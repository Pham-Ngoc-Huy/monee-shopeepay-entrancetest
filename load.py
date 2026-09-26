import pandas as pd
from pathlib import Path

from database.database import DataBase
from database.schema import CREATE_TABLE_SQL


BASE_DIR = Path(__file__).parent
DIM_USER = str(BASE_DIR / "raw_data/dim_user.csv")
DIM_PRODUCTS = str(BASE_DIR / "raw_data/dim_products.csv")
DWD_ORDER = str(BASE_DIR / "raw_data/dwd_order.csv")
DATABASE_PATH = str(BASE_DIR / "database/sql_questions.db")

ID = "string"
TEXT = "string"
FLOAT = "Float64"
INT = "Int64"
TIMESTAMP = "datetime64[ns]"
DATETIME = "datetime64[ns]"

DTYPES = {
    "dim_user": {
        "user_id": ID, 
        "user_name": TEXT, 
        "last_name": TEXT,
        "first_name": TEXT, 
        "email": TEXT, 
        "created_time": DATETIME,
    },
    "dim_products": {
        "product_id": ID, 
        "product_name": TEXT,
        "category_name_level_1": TEXT, 
        "category_name_level_2": TEXT,
        "product_price": FLOAT, 
        "stock_quantities": FLOAT,
        "description": TEXT, 
        "image_source": TEXT,
        "status": TEXT,
        "updated_time": TIMESTAMP, 
        "created_time": TIMESTAMP,
    },
    "dwd_order": {
        "order_id": ID, 
        "user_id": ID, 
        "product_id": ID,
        "gmv": FLOAT, 
        "nmv": FLOAT, 
        "product_quantities": FLOAT,
        "promotion_value": FLOAT,
        "category_name_level_1_id": INT, 
        "category_name_level_2_id": INT,
        "payment_method": TEXT, 
        "order_status": TEXT, 
        "shipping_status": TEXT,
        "shipping_address": TEXT,
        "updated_time": TIMESTAMP, 
        "created_time": TIMESTAMP,
    },
}

# columns that are datetime-like in config (both TIMESTAMP and DATETIME map to datetime64[ns])
_DATETIME_TYPES = {TIMESTAMP, DATETIME}


def read(path: str, table_name: str) -> pd.DataFrame:
    declared = DTYPES[table_name]
    # Robust datetime detection: any dtype containing "datetime"
    parse_dates = [c for c, d in declared.items() if "datetime" in d]
    # fallback to explicit set check (TIMESTAMP == DATETIME so both qualify)
    if not parse_dates:
        parse_dates = [c for c, d in declared.items() if d in _DATETIME_TYPES]
    dtypes = {c: d for c, d in declared.items() if c not in parse_dates}

    df = pd.read_csv(path, dtype=dtypes, parse_dates=parse_dates)

    # --- validation: ensure columns match config exactly ---
    expected = list(declared.keys())
    missing = [c for c in expected if c not in df.columns]
    extra = [c for c in df.columns if c not in expected]
    if missing:
        raise ValueError(f"{table_name}: missing columns {missing} (expected {expected}, got {list(df.columns)})")
    if extra:
        raise ValueError(f"{table_name}: extra columns {extra} (expected {expected})")
    # reorder to declared order (important for INSERT without column mismatch)
    df = df[expected]

    # ensure string/ID columns with empty string -> <NA> -> NULL on insert
    for col, dtype in declared.items():
        if dtype == "string":
            # pandas string dtype already maps empty to <NA> with our dtype, but if csv had "" without dtype handling, ensure
            df[col] = df[col].astype("string").replace("", pd.NA)

    return df


def recreate_schema(db: DataBase) -> None:
    """Drop existing tables and recreate from CREATE_TABLE_SQL.
    Keeps table/column names and FKs as defined in schema.py (now TEXT for IDs, composite PK for dwd_order).
    """
    # Disable FK checks to allow drop/recreate in any order
    db.conn.execute("PRAGMA foreign_keys = OFF")
    for tbl in ("dwd_order", "dim_products", "dim_user"):
        db.conn.execute(f"DROP TABLE IF EXISTS {tbl}")
    for tbl in ("dim_user", "dim_products", "dwd_order"):
        db.conn.execute(CREATE_TABLE_SQL[tbl])
    db.conn.commit()
    db.conn.execute("PRAGMA foreign_keys = OFF")  # keep OFF during loading to allow orphan rows for QA; set ON after if desired
    db.conn.commit()


def load_dataframe(db: DataBase, df: pd.DataFrame, table_name: str) -> int:
    columns = ", ".join(df.columns)
    placeholders = ", ".join("?" for _ in df.columns)
    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

    data = df.copy()
    for column in data.select_dtypes(include="datetime"):
        data[column] = data[column].dt.strftime("%Y-%m-%d %H:%M:%S")

    def to_native(v):
        if pd.isna(v):
            return None
        if hasattr(v, "item"):   # numpy scalar (int64, float64, ...) -> its own native type
            return v.item()
        return v

    rows = [
        tuple(to_native(v) for v in row)
        for row in data.itertuples(index=False, name=None)
    ]

    db.conn.executemany(sql, rows)
    return len(data)

def check(db: DataBase) -> None:
    for table_name in DTYPES:
        stored = db.query(f"SELECT COUNT(*) n FROM {table_name}")[0]["n"]
        print(f"  {table_name:14} {stored:>4} rows")

    print("\n  integrity:")

    orphan_users = db.query(
        "SELECT DISTINCT o.user_id FROM dwd_order o "
        "WHERE o.user_id NOT IN (SELECT user_id FROM dim_user)"
    )
    orphan_products = db.query(
        "SELECT DISTINCT o.product_id FROM dwd_order o "
        "WHERE o.product_id NOT IN (SELECT product_id FROM dim_products)"
    )
    lost = db.query(
        "SELECT COUNT(*) n FROM dwd_order o "
        "LEFT JOIN dim_user u USING(user_id) WHERE u.user_id IS NULL"
    )[0]["n"]

    print(f"    orders with unknown user_id    : {len(orphan_users)} "
          f"{[r['user_id'] for r in orphan_users]}")
    print(f"    orders with unknown product_id : {len(orphan_products)} "
          f"{[r['product_id'] for r in orphan_products]}")
    print(f"    rows an INNER JOIN would drop : {lost}")

    nulls = db.query(
        "SELECT "
        "SUM(promotion_value IS NULL) promo_null, "
        "SUM(gmv IS NULL) gmv_null, "
        "SUM(created_time IS NULL) created_null "
        "FROM dwd_order"
    )[0]
    print(f"    dwd_order NULLs                : {dict(nulls)}")

    # extra validation: show that ID columns are stored as TEXT
    for tbl, col in [("dim_user","user_id"),("dim_products","product_id"),("dwd_order","order_id")]:
        sample = db.query(f"SELECT {col}, typeof({col}) t FROM {tbl} LIMIT 1")
        if sample:
            print(f"    {tbl}.{col} sample: {sample[0][col]!r} typeof={sample[0]['t']}")

    dup = db.query("SELECT order_id, COUNT(*) c FROM dwd_order GROUP BY order_id HAVING c>1")
    if dup:
        print(f"    duplicate order_id (expected for multi-product orders): {dup}")


def main():
    frames = {
        "dim_user": read(DIM_USER, "dim_user"),
        "dim_products": read(DIM_PRODUCTS, "dim_products"),
        "dwd_order": read(DWD_ORDER, "dwd_order"),
    }

    print("parsed dtypes:")
    for name, df in frames.items():
        non_default = {
            c: str(t) for c, t in df.dtypes.items() if str(t) != "object"
        }
        print(f"  {name:14} {non_default}")
        # show null counts for QA
        nulls = df.isna().sum()
        if nulls.any():
            print(f"    nulls: {nulls[nulls>0].to_dict()}")

    with DataBase(DATABASE_PATH) as db:
        # Recreate tables to ensure types match string IDs (fixes INTEGER PRIMARY KEY mismatch) and composite PK for dwd_order
        recreate_schema(db)

        for table_name, df in frames.items():
            n = load_dataframe(db, df, table_name)
            print(f"  inserted {n} rows into {table_name}")

        db.conn.commit()

        print("\nloaded:")
        check(db)


if __name__ == "__main__":
    main()

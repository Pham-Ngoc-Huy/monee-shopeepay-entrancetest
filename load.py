import pandas as pd

from database.database import DataBase


DIM_USER = "raw_data/dim_user.csv"
DIM_PRODUCTS = "raw_data/dim_products.csv"
DWD_ORDER = "raw_data/dwd_order.csv"

DATABASE_PATH = "database/sql_questions.db"

ID = "string"
TEXT = "string"
FLOAT = "Float64"
INT = "Int64"
TIMESTAMP = "datetime64[ns]"
DATETIME = ""

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


def read(path: str, table_name: str) -> pd.DataFrame:
    declared = DTYPES[table_name]
    parse_dates = [c for c, d in declared.items() if d == TIMESTAMP]
    dtypes = {c: d for c, d in declared.items() if d != TIMESTAMP}

    return pd.read_csv(path, dtype=dtypes, parse_dates=parse_dates)


def load_dataframe(db: DataBase, df: pd.DataFrame, table_name: str) -> int:
    columns = ", ".join(df.columns)
    placeholders = ", ".join("?" for _ in df.columns)
    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

    data = df.copy()
    for column in data.select_dtypes(include="datetime"):
        data[column] = data[column].dt.strftime("%Y-%m-%d %H:%M:%S")

    data = data.astype(object).where(data.notna(), None)

    db.conn.executemany(sql, data.itertuples(index=False, name=None))
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

    with DataBase(DATABASE_PATH) as db:
        for table_name in ("dim_user", "dim_products", "dwd_order"):
            db.conn.execute(f"DELETE FROM {table_name}")

        for table_name, df in frames.items():
            load_dataframe(db, df, table_name)

        db.conn.commit()

        print("\nloaded:")
        check(db)


if __name__ == "__main__":
    main()

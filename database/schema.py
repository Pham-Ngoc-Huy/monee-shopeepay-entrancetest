import sqlite3
from dataclasses import dataclass, fields
from typing import Any, Optional, Sequence

CREATE_TABLE_SQL: dict[str, str] = {
    "dim_user": """
        CREATE TABLE IF NOT EXISTS dim_user (
            user_id TEXT PRIMARY KEY,
            user_name TEXT,
            last_name TEXT,
            first_name TEXT,
            email TEXT,
            created_time DATETIME
        )
    """,

    "dim_products": """
        CREATE TABLE IF NOT EXISTS dim_products (
            product_id TEXT PRIMARY KEY,
            product_name TEXT,
            category_name_level_1 TEXT,
            category_name_level_2 TEXT,
            product_price DECIMAL,
            stock_quantities DECIMAL,
            description TEXT,
            image_source TEXT,
            status TEXT,
            updated_time DATETIME,
            created_time DATETIME
        )
    """,

    "dwd_order": """
        CREATE TABLE IF NOT EXISTS dwd_order (
            order_id TEXT,
            user_id TEXT,
            product_id TEXT,

            gmv DECIMAL,
            nmv DECIMAL,
            product_quantities DECIMAL,
            promotion_value DECIMAL,

            category_name_level_1_id INTEGER,
            category_name_level_2_id INTEGER,

            payment_method TEXT,
            order_status TEXT,
            shipping_status TEXT,
            shipping_address TEXT,

            updated_time DATETIME,
            created_time DATETIME,

            PRIMARY KEY (order_id),

            FOREIGN KEY (user_id)
                REFERENCES dim_user(user_id),

            FOREIGN KEY (product_id)
                REFERENCES dim_products(product_id)
        )
    """,
}

CREATE_ALL = list(CREATE_TABLE_SQL.values())


def init_schema(db: sqlite3.Connection) -> None:
    for sql in CREATE_TABLE_SQL.values():
        db.execute(sql)
    db.commit()


@dataclass
class BaseSchema:
    table: str = ""
    db: Optional[sqlite3.Connection] = None

    @classmethod
    def columns(cls) -> list[str]:
        return [f.name for f in fields(cls)]

    def create(self) -> None:
        self._require().execute(CREATE_TABLE_SQL[self.table])
        self._require().commit()

    def insert(self, row: Any) -> None:
        cols = self.columns()
        placeholders = ", ".join("?" for _ in cols)
        self._require().execute(
            f"INSERT INTO {self.table} ({', '.join(cols)}) VALUES ({placeholders})",
            self._row_values(row),
        )

    def insert_many(self, rows: Sequence[Any]) -> None:
        cols = self.columns()
        placeholders = ", ".join("?" for _ in cols)
        sql = (
            f"INSERT INTO {self.table} ({', '.join(cols)}) "
            f"VALUES ({placeholders})"
        )
        self._require().executemany(sql, [self._row_values(r) for r in rows])
        self._require().commit()

    def _require(self) -> sqlite3.Connection:
        if self.db is None:
            raise RuntimeError(f"{type(self).__name__} is not bound to a database")
        return self.db

    @staticmethod
    def _row_values(row: Any) -> tuple:
        if isinstance(row, dict):
            return tuple(row.values())
        if isinstance(row, (list, tuple)):
            return tuple(row)
        if hasattr(row, "__dataclass_fields__"):
            return tuple(getattr(row, name) for name in row.__dataclass_fields__)
        return tuple(row)

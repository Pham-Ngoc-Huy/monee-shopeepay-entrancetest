import sqlite3


def connect(
    path: str, 
    attach: dict[str,str] = None
):
    """Open a sqlite db. attach = {"alias": "other.db"} to join other files."""
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    for alias, other in (attach or {}).items():
        conn.execute(f"ATTACH DATABASE ? AS {alias}", (other,))
    return conn

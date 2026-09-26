from database.connection import connect
from database.schema import CREATE_ALL


class DataBase:
    def __init__(self, path, attach=None):
        self.conn = connect(path, attach)
        self.cursor = self.conn.cursor
        self._create()

    def _create(self):
        for sql in CREATE_ALL:
            self.conn.execute(sql)
        self.conn.commit()

    def query(self, sql, params=()):
        return [dict(r) for r in self.conn.execute(sql, params).fetchall()]

    def insert(self, sql, params=()):
        self.conn.execute(sql, params)
        self.conn.commit()

    def close(self):
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

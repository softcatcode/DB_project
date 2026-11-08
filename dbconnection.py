"""Установка соединения с PostgreSQL."""

import psycopg2


class DbConnection:
    def __init__(self, config):
        self.dbname = config.dbname
        self.user = config.user
        self.password = config.password
        self.host = config.host
        self.prefix = config.dbtableprefix

        self.conn = psycopg2.connect(
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=self.host
        )

    def test(self):
        with self.conn.cursor() as cur:
            cur.execute("SELECT 1")
            result = cur.fetchone()
        return result == (1,)

    def close(self):
        if self.conn and not self.conn.closed:
            self.conn.close()

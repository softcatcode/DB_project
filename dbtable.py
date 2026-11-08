"""Базовый безопасный интерфейс работы с таблицами PostgreSQL."""
from psycopg2 import sql


class DbTable:
    dbconn = None

    def __init__(self):
        if DbTable.dbconn is None:
            raise RuntimeError("Соединение с БД не настроено.")

    def table_name(self):
        raise NotImplementedError

    def columns(self):
        raise NotImplementedError

    def primary_key(self):
        return ["id"]

    def table_constraints(self):
        return []

    @staticmethod
    def identifier(name):
        # Поддерживает как имя таблицы, так и schema.table.
        return sql.Identifier(*name.split("."))

    def column_names(self):
        return list(self.columns())

    def column_names_without_id(self):
        pks = set(self.primary_key())
        return [name for name in self.column_names() if name not in pks]

    def create(self):
        definitions = []
        for name, definition in self.columns().items():
            definitions.append(sql.SQL("{} {}").format(
                sql.Identifier(name), sql.SQL(" ".join(definition))))
        definitions.extend(self.table_constraints())
        query = sql.SQL("CREATE TABLE IF NOT EXISTS {} ({})").format(
            self.identifier(self.table_name()), sql.SQL(", ").join(definitions))
        with self.dbconn.conn.cursor() as cur:
            cur.execute(query)
        self.dbconn.conn.commit()

    def drop(self):
        query = sql.SQL("DROP TABLE IF EXISTS {}").format(
            self.identifier(self.table_name()))
        with self.dbconn.conn.cursor() as cur:
            cur.execute(query)
        self.dbconn.conn.commit()

    def insert_one(self, values):
        columns = self.column_names_without_id()
        params = [values[c] if isinstance(values, dict) else getattr(values, c)
                  for c in columns]
        query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
            self.identifier(self.table_name()),
            sql.SQL(", ").join(map(sql.Identifier, columns)),
            sql.SQL(", ").join(sql.Placeholder() for _ in columns))
        with self.dbconn.conn.cursor() as cur:
            cur.execute(query, params)
        self.dbconn.conn.commit()

    def update_at(self, position, values):
        """Изменяет запись по экранному порядковому номеру (с 1), не раскрывая PK."""
        if position < 1:
            raise ValueError("Номер записи должен быть больше нуля.")
        columns = self.column_names_without_id()
        params = [values[c] if isinstance(values, dict) else getattr(values, c)
                  for c in columns]
        pk = self.primary_key()
        if len(pk) != 1:
            raise NotImplementedError("Поддерживается один первичный ключ.")
        query = sql.SQL(
            "UPDATE {table} SET ({cols}) = ({vals}) WHERE {pk} = "
            "(SELECT {pk} FROM {table} ORDER BY {pk} LIMIT 1 OFFSET %s)"
        ).format(
            table=self.identifier(self.table_name()),
            cols=sql.SQL(", ").join(map(sql.Identifier, columns)),
            vals=sql.SQL(", ").join(sql.Placeholder() for _ in columns),
            pk=sql.Identifier(pk[0]))
        with self.dbconn.conn.cursor() as cur:
            cur.execute(query, params + [position - 1])
            changed = cur.rowcount
        self.dbconn.conn.commit()
        return changed > 0

    def map_entity(self, row):
        raise NotImplementedError

    def all(self):
        order = sql.SQL(", ").join(map(sql.Identifier, self.primary_key()))
        query = sql.SQL("SELECT * FROM {} ORDER BY {}").format(
            self.identifier(self.table_name()), order)
        with self.dbconn.conn.cursor() as cur:
            cur.execute(query)
            return [self.map_entity(row) for row in cur.fetchall()]

    def first(self):
        rows = self.all()
        return rows[0] if rows else None

    def last(self):
        pk_desc = sql.SQL(", ").join(
            sql.SQL("{} DESC").format(sql.Identifier(n)) for n in self.primary_key())
        query = sql.SQL("SELECT * FROM {} ORDER BY {} LIMIT 1").format(
            self.identifier(self.table_name()), pk_desc)
        with self.dbconn.conn.cursor() as cur:
            cur.execute(query)
            row = cur.fetchone()
            return self.map_entity(row) if row else None

    def remove_by_id(self, record_id):
        # Внутренний метод; пользовательский интерфейс его не вызывает.
        keys = self.primary_key()
        if len(keys) != 1:
            raise NotImplementedError
        query = sql.SQL("DELETE FROM {} WHERE {} = %s").format(
            self.identifier(self.table_name()), sql.Identifier(keys[0]))
        with self.dbconn.conn.cursor() as cur:
            cur.execute(query, (record_id,))
            deleted = cur.rowcount
        self.dbconn.conn.commit()
        return deleted > 0

    def remove_at(self, position):
        if position < 1:
            raise ValueError("Номер записи должен быть больше нуля.")
        keys = self.primary_key()
        if len(keys) != 1:
            raise NotImplementedError
        query = sql.SQL(
            "DELETE FROM {table} WHERE {pk} = "
            "(SELECT {pk} FROM {table} ORDER BY {pk} LIMIT 1 OFFSET %s)"
        ).format(table=self.identifier(self.table_name()), pk=sql.Identifier(keys[0]))
        with self.dbconn.conn.cursor() as cur:
            cur.execute(query, (position - 1,))
            deleted = cur.rowcount
        self.dbconn.conn.commit()
        return deleted > 0

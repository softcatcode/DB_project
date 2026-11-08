"""Работа с таблицей стран."""
from psycopg2 import sql
from dbtable import DbTable
from entities import Country


class CountriesTable(DbTable):
    REGIONS = ("Азия", "Европа", "Африка", "Австралия и Океания",
               "Северная Америка", "Южная и Латинская Америка")

    def table_name(self):
        return self.dbconn.prefix + "country"

    def columns(self):
        return {"country_id": ["SERIAL", "PRIMARY KEY"],
                "short_name": ["VARCHAR(100)", "NOT NULL", "UNIQUE"],
                "full_name": ["VARCHAR(200)", "NOT NULL", "UNIQUE"],
                "region": ["VARCHAR(50)", "NOT NULL"]}

    def primary_key(self):
        return ["country_id"]

    def table_constraints(self):
        # Значения берутся только из фиксированного списка приложения.
        allowed = sql.SQL(", ").join(sql.Literal(x) for x in self.REGIONS)
        return [sql.SQL("CHECK ({} IN ({}))").format(sql.Identifier("region"), allowed)]

    @staticmethod
    def map_entity(row):
        country_id, short_name, full_name, region = row
        return Country(short_name, full_name, region, country_id)

    def remove_country_at(self, position):
        """Удаляет страну и всех связанных футболистов одной транзакцией."""
        if position < 1:
            raise ValueError("Номер записи должен быть больше нуля.")
        player_table = self.dbconn.prefix + "player"
        country_table = self.dbconn.prefix + "country"
        with self.dbconn.conn.cursor() as cur:
            cur.execute(sql.SQL(
                "SELECT country_id FROM {} ORDER BY country_id LIMIT 1 OFFSET %s"
            ).format(self.identifier(country_table)), (position - 1,))
            row = cur.fetchone()
            if row is None:
                self.dbconn.conn.rollback()
                return False
            country_id = row[0]
            cur.execute(sql.SQL("DELETE FROM {} WHERE country_id = %s").format(
                self.identifier(player_table)), (country_id,))
            cur.execute(sql.SQL("DELETE FROM {} WHERE country_id = %s").format(
                self.identifier(country_table)), (country_id,))
        self.dbconn.conn.commit()
        return True

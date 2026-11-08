"""Работа с таблицей футболистов."""
from psycopg2 import sql
from dbtable import DbTable
from entities import Player


class PlayersTable(DbTable):
    def table_name(self):
        return self.dbconn.prefix + "player"

    def columns(self):
        return {"player_id": ["SERIAL", "PRIMARY KEY"],
                "last_name": ["VARCHAR(100)", "NOT NULL"],
                "first_name": ["VARCHAR(100)", "NOT NULL"],
                "birth_date": ["DATE", "NOT NULL", "CHECK (birth_date <= CURRENT_DATE)"],
                "country_id": ["INTEGER", "NOT NULL"]}

    def primary_key(self):
        return ["player_id"]

    def table_constraints(self):
        return [sql.SQL("FOREIGN KEY ({}) REFERENCES {} ({})").format(
            sql.Identifier("country_id"),
            self.identifier(self.dbconn.prefix + "country"),
            sql.Identifier("country_id"))]

    @staticmethod
    def map_entity(row):
        player_id, last_name, first_name, birth_date, country_id = row
        return Player(first_name, last_name, birth_date, country_id, player_id)

    def all_with_country(self, country_id=None):
        query = sql.SQL("""
            SELECT p.player_id, p.last_name, p.first_name, p.birth_date,
                   p.country_id, c.short_name, c.full_name, c.region
            FROM {} AS p JOIN {} AS c ON p.country_id = c.country_id
            {where}
            ORDER BY p.player_id
        """).format(
            self.identifier(self.table_name()),
            self.identifier(self.dbconn.prefix + "country"),
            where=(sql.SQL("WHERE p.country_id = %s") if country_id is not None
                   else sql.SQL("")))
        with self.dbconn.conn.cursor() as cur:
            if country_id is None:
                cur.execute(query)
            else:
                cur.execute(query, (country_id,))
            return [Player(first_name=r[2], last_name=r[1], birth_date=r[3],
                           country_id=r[4], player_id=r[0],
                           country_short_name=r[5], country_full_name=r[6],
                           country_region=r[7]) for r in cur.fetchall()]

"""
Мачильский Даниил Дмитриевич
Вариант 26
Условие:
Таблицы страны и футболисты без связей с другими таблицами.
Если страны не в отдельной таблице, то выделите их в отдельную таблицу.
"""


"""Главный модуль консольного приложения."""
from project_config import ProjectConfig
from dbconnection import DbConnection
from dbtable import DbTable
from tables.players_table import PlayersTable
from tables.countries_table import CountriesTable
from io_helper import IOHelper


class Main:
    def __init__(self):
        self.connection = DbConnection(ProjectConfig())
        DbTable.dbconn = self.connection
        self.io = IOHelper()
        self.players_table = PlayersTable()
        self.countries_table = CountriesTable()

    def db_init(self):
        self.countries_table.create()
        self.players_table.create()

    def db_drop(self):
        self.players_table.drop()
        self.countries_table.drop()

    def reset_tables(self):
        answer = input("Удалить таблицы вместе со всеми данными? (да/нет): ").strip().lower()
        if answer not in ("да", "д", "yes", "y"):
            print("Сброс отменён.")
            return
        self.db_drop()
        self.db_init()
        print("Таблицы созданы заново. Добавьте страны перед футболистами.")

    def _countries(self):
        rows = self.countries_table.all()
        if not rows:
            raise ValueError("Сначала добавьте хотя бы одну страну.")
        self.io.print_countries(rows)
        return rows

    def add_player(self):
        player = self.io.read_player(self._countries())
        self.players_table.insert_one(player)
        print("Футболист добавлен.")

    def edit_player(self):
        rows = self.players_table.all_with_country()
        if not rows:
            print("Список футболистов пуст.")
            return
        self.io.print_players(rows)
        number = self.io.read_menu_item("Номер футболиста для изменения: ")
        if not 1 <= number <= len(rows):
            print("Запись с таким номером не найдена.")
            return
        updated = self.io.read_player(self.countries_table.all(), rows[number - 1])
        if self.players_table.update_at(number, updated):
            print("Данные футболиста обновлены.")

    def remove_player(self):
        rows = self.players_table.all_with_country()
        if not rows:
            print("Список футболистов пуст.")
            return
        self.io.print_players(rows)
        number = self.io.read_menu_item("Номер футболиста для удаления: ")
        print("Футболист удалён." if self.players_table.remove_at(number)
              else "Запись с таким номером не найдена.")

    def show_players_for_country(self):
        countries = self._countries()
        number = self.io.read_menu_item("Порядковый номер страны для просмотра футболистов: ")
        if not 1 <= number <= len(countries):
            print("Страна с таким номером не найдена.")
            return
        players = self.players_table.all_with_country(countries[number - 1].country_id)
        if not players:
            print("В этой стране пока нет футболистов.")
        else:
            print("\\nФутболисты выбранной страны:")
            self.io.print_players(players)

    def show_countries(self):
        rows = self.countries_table.all()
        if not rows:
            print("Список стран пуст.")
        else:
            print("\\nСписок стран:")
            self.io.print_countries(rows)

    def add_country(self):
        self.countries_table.insert_one(self.io.read_country())
        print("Страна добавлена.")

    def edit_country(self):
        rows = self.countries_table.all()
        if not rows:
            print("Список стран пуст.")
            return
        self.io.print_countries(rows)
        number = self.io.read_menu_item("Номер страны для изменения: ")
        if not 1 <= number <= len(rows):
            print("Страна с таким номером не найдена.")
            return
        print("Введите новые данные страны.")
        if self.countries_table.update_at(number, self.io.read_country()):
            print("Данные страны обновлены.")

    def remove_country(self):
        rows = self.countries_table.all()
        if not rows:
            print("Список стран пуст.")
            return
        self.io.print_countries(rows)
        number = self.io.read_menu_item("Номер страны для удаления: ")
        if not 1 <= number <= len(rows):
            print("Страна с таким номером не найдена.")
            return
        country = rows[number - 1]
        answer = input(
            f"Удалить страну «{country.full_name}» и всех связанных с ней футболистов? (да/нет): "
        ).strip().lower()
        if answer in ("да", "д", "yes", "y"):
            print("Страна и связанные футболисты удалены."
                  if self.countries_table.remove_country_at(number) else "Страна не найдена.")
        else:
            print("Удаление отменено.")

    def show_main_menu(self):
        print("""
Главное меню:
  1 — операции с футболистами
  2 — сброс и создание таблиц
  3 — операции со странами
  4 — выход
""")

    def players_table_cycle(self):
        while True:
            print("""
Футболисты:
  0 — назад
  1 — добавить
  2 — изменить
  3 — удалить
  4 — показать всех
  5 — показать по стране
""")
            try:
                command = self.io.read_menu_item()
                if command == 0:
                    return
                if command == 1:
                    self.add_player()
                elif command == 2:
                    self.edit_player()
                elif command == 3:
                    self.remove_player()
                elif command == 4:
                    self.io.print_players(self.players_table.all_with_country())
                elif command == 5:
                    self.show_players_for_country()
                else:
                    print("Неизвестная команда.")
            except (ValueError, TypeError) as error:
                print(f"Ошибка ввода: {error}")
            except Exception as error:
                self.connection.conn.rollback()
                print(f"Ошибка базы данных или операции: {error}")

    def countries_table_cycle(self):
        while True:
            print("""
Страны:
  0 — назад
  1 — показать
  2 — добавить
  3 — изменить
  4 — удалить (вместе со связанными футболистами)
""")
            try:
                command = self.io.read_menu_item()
                if command == 0:
                    return
                if command == 1:
                    self.show_countries()
                elif command == 2:
                    self.add_country()
                elif command == 3:
                    self.edit_country()
                elif command == 4:
                    self.remove_country()
                else:
                    print("Неизвестная команда.")
            except (ValueError, TypeError) as error:
                print(f"Ошибка ввода: {error}")
            except Exception as error:
                self.connection.conn.rollback()
                print(f"Ошибка базы данных или операции: {error}")

    def main_cycle(self):
        while True:
            self.show_main_menu()
            try:
                command = self.io.read_menu_item()
                if command == 1:
                    self.players_table_cycle()
                elif command == 2:
                    self.reset_tables()
                elif command == 3:
                    self.countries_table_cycle()
                elif command == 4:
                    print("До свидания!")
                    return
                else:
                    print("Выбрано неверное число.")
            except (ValueError, TypeError) as error:
                print(f"Ошибка ввода: {error}")
            except Exception as error:
                self.connection.conn.rollback()
                print(f"Ошибка: {error}")

    def test(self):
        return self.connection.test()

    def close(self):
        if self.connection:
            self.connection.close()


if __name__ == "__main__":
    app = Main()
    try:
        # При первом запуске создайте таблицы через пункт 2.
        app.main_cycle()
    finally:
        app.close()

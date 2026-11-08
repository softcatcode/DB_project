"""Ввод, проверка и вывод данных консольного приложения."""
from datetime import datetime, date
from beautifultable import BeautifulTable
from entities import Player, Country


class IOHelper:
    def read_menu_item(self, prompt_text="=> "):
        return int(input(prompt_text).strip())

    def read_str(self, message, max_length, allow_empty=False):
        while True:
            value = input(message).strip()
            if value == "0":
                raise ValueError("Ввод отменён пользователем.")
            if not value and not allow_empty:
                print("Поле не может быть пустым.")
                continue
            if len(value) > max_length:
                print(f"Максимальная длина — {max_length} символов.")
                continue
            return value

    def read_date(self, message):
        while True:
            value = input(message).strip()
            if value == "0":
                raise ValueError("Ввод отменён пользователем.")
            try:
                result = datetime.strptime(value, "%d.%m.%Y").date()
                if result > date.today():
                    print("Дата рождения не может быть в будущем.")
                    continue
                return result
            except ValueError:
                print("Введите дату в формате ДД.ММ.ГГГГ, например 15.03.1998.")

    def read_country(self):
        return Country(self.read_str("Короткое название (0 — отмена): ", 100),
                       self.read_str("Полное название (0 — отмена): ", 200),
                       self.read_region())

    def read_region(self):
        regions = ("Азия", "Европа", "Африка", "Австралия и Океания",
                   "Северная Америка", "Южная и Латинская Америка")
        while True:
            value = self.read_str("Регион (" + "/".join(regions) + "): ", 50)
            if value in regions:
                return value
            print("Выберите один из допустимых регионов: " + ", ".join(regions))

    def read_player(self, countries, current=None):
        if not countries:
            raise ValueError("Сначала добавьте хотя бы одну страну.")
        print("\\nДоступные страны:")
        table = BeautifulTable()
        table.columns.header = ["№", "Страна", "Регион"]
        for number, country in enumerate(countries, 1):
            table.rows.append([number, country.full_name, country.region])
        print(table)

        first = current.first_name if current else ""
        last = current.last_name if current else ""
        birth = current.birth_date.strftime("%d.%m.%Y") if current else ""
        print("Введите 0 в любом поле для отмены операции.")
        first_name = self.read_str(f"Имя [{first}]: " if current else "Имя: ", 100)
        last_name = self.read_str(f"Фамилия [{last}]: " if current else "Фамилия: ", 100)
        birth_date = self.read_date(f"Дата рождения ДД.ММ.ГГГГ [{birth}]: " if current
                                    else "Дата рождения ДД.ММ.ГГГГ: ")
        while True:
            raw = input("Номер страны: ").strip()
            if raw == "0":
                raise ValueError("Ввод отменён пользователем.")
            try:
                choice = int(raw)
                if 1 <= choice <= len(countries):
                    return Player(first_name, last_name, birth_date,
                                  countries[choice - 1].country_id)
            except ValueError:
                print("Введите порядковый номер страны из списка.")

    @staticmethod
    def print_players(players):
        table = BeautifulTable()
        table.columns.header = ["№", "Фамилия", "Имя", "Дата рождения", "Страна", "Регион"]
        for n, player in enumerate(players, 1):
            table.rows.append([n, player.last_name, player.first_name,
                               player.birth_date.strftime("%d.%m.%Y") if player.birth_date else "",
                               player.country_full_name or "", player.country_region or ""])
        print(table)

    @staticmethod
    def print_countries(countries):
        table = BeautifulTable()
        table.columns.header = ["№", "Краткое название", "Полное название", "Регион"]
        for n, country in enumerate(countries, 1):
            table.rows.append([n, country.short_name, country.full_name, country.region])
        print(table)

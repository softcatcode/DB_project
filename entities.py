"""Доменные сущности приложения."""
from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Country:
    short_name: str
    full_name: str
    region: str
    country_id: Optional[int] = None


@dataclass
class Player:
    first_name: str
    last_name: str
    birth_date: date
    country_id: int
    player_id: Optional[int] = None
    # Заполняются в запросе с JOIN; не являются полями таблицы player.
    country_short_name: Optional[str] = None
    country_full_name: Optional[str] = None
    country_region: Optional[str] = None

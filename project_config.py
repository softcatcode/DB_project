"""Загрузка настроек из config.yaml."""

import yaml
from pathlib import Path


class ProjectConfig:
    def __init__(self):
        config_path = Path(__file__).resolve().with_name("config.yaml")
        with config_path.open(encoding="utf-8") as file:
            config = yaml.safe_load(file) or {}

        self.dbname = config["dbname"]
        self.user = config["user"]
        self.password = config["password"]
        self.host = config["host"]
        self.dbtableprefix = config.get("dbtableprefix", "public.")

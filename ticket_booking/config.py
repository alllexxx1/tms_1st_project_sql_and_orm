"""Общие настройки подключения для команд проекта."""

import os

from dotenv import load_dotenv


def get_database_url() -> str:
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("Задайте DATABASE_URL в .env или окружении. Пример есть в README.md.")
    return database_url

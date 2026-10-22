"""Функции создания таблиц и добавления демонстрационных данных."""

from pathlib import Path

import psycopg


def create_tables(database_url: str) -> None:
    """Создать таблицы в пустой базе за одну транзакцию."""
    schema_path = Path(__file__).resolve().parent / "sql" / "schema.sql"
    schema_sql = schema_path.read_text(encoding="utf-8")
    with psycopg.connect(database_url, connect_timeout=5) as connection:
        with connection.cursor() as cursor:
            cursor.execute(schema_sql)


def seed_data(database_url: str) -> None:
    """Заполнить пустые таблицы примерами за отдельную транзакцию."""
    seed_path = Path(__file__).resolve().parent / "sql" / "seed.sql"
    seed_sql = seed_path.read_text(encoding="utf-8")
    with psycopg.connect(database_url, connect_timeout=5) as connection:
        with connection.cursor() as cursor:
            cursor.execute(seed_sql)

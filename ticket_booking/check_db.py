"""Проверка подключения: python -m ticket_booking.check_db."""

import os
import sys
from pathlib import Path

import psycopg
from dotenv import load_dotenv


def main() -> int:
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    print(database_url)
    if not database_url:
        print("Задайте DATABASE_URL в .env")
        return 1

    try:
        with psycopg.connect(database_url, connect_timeout=5) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT current_database(), current_user")
                database_name, user_name = cursor.fetchone()
    except psycopg.Error:
        print(
            "Не удалось подключиться к PostgreSQL. Проверьте, что сервер запущен, "
            "база создана и DATABASE_URL содержит правильные настройки.",
            file=sys.stderr,
        )
        return 1

    print(f"Подключение успешно. База: {database_name}, пользователь: {user_name}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

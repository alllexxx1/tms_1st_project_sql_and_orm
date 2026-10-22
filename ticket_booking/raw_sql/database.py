"""Общий контекстный менеджер для SQL-запросов через Psycopg."""

from collections.abc import Iterator
from contextlib import contextmanager

import psycopg
from psycopg.rows import tuple_row


@contextmanager
def get_cursor(database_url: str, row_factory=tuple_row) -> Iterator[psycopg.Cursor]:
    """Открыть курсор и завершить транзакцию при выходе из with."""
    with psycopg.connect(database_url, row_factory=row_factory, connect_timeout=5) as connection:
        with connection.cursor() as cursor:
            yield cursor

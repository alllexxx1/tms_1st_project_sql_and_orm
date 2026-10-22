"""CRUD и поиск мероприятий через SQL-запросы."""

from datetime import datetime

import psycopg
from psycopg.rows import dict_row


def list_events(database_url: str) -> list[dict]:
    with psycopg.connect(database_url, row_factory=dict_row) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, title, venue, starts_at FROM events ORDER BY starts_at, id")
            return cursor.fetchall()


def search_events(database_url: str, title_part: str = "", venue_part: str = "") -> list[dict]:
    with psycopg.connect(database_url, row_factory=dict_row) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, title, venue, starts_at FROM events "
                "WHERE title ILIKE %s AND venue ILIKE %s ORDER BY starts_at, id",
                (f"%{title_part}%", f"%{venue_part}%"),
            )
            return cursor.fetchall()


def find_events_by_seat(database_url: str, row_number: int, seat_number: int) -> list[dict]:
    """Найти мероприятия, у которых есть указанное место, включая занятые."""
    with psycopg.connect(database_url, row_factory=dict_row) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT events.id, events.title, events.venue, events.starts_at "
                "FROM events JOIN seats ON seats.event_id = events.id "
                "WHERE seats.row_number = %s AND seats.seat_number = %s "
                "ORDER BY events.starts_at, events.id",
                (row_number, seat_number),
            )
            return cursor.fetchall()


def add_event(database_url: str, title: str, venue: str, starts_at: datetime) -> int:
    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO events (title, venue, starts_at) VALUES (%s, %s, %s) RETURNING id",
                (title, venue, starts_at),
            )
            return cursor.fetchone()[0]


def update_event(
    database_url: str, event_id: int, title: str, venue: str, starts_at: datetime
) -> bool:
    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM events "
                "JOIN seats ON seats.event_id = events.id "
                "JOIN tickets ON tickets.seat_id = seats.id "
                "WHERE events.id = %s AND events.venue <> %s LIMIT 1",
                (event_id, venue),
            )
            if cursor.fetchone():
                raise ValueError("У мероприятия есть билеты. Сначала отмените бронирования для смены площадки.")
            cursor.execute(
                "UPDATE events SET title = %s, venue = %s, starts_at = %s WHERE id = %s",
                (title, venue, starts_at, event_id),
            )
            return cursor.rowcount > 0


def delete_event(database_url: str, event_id: int) -> bool:
    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM events WHERE id = %s", (event_id,))
            return cursor.rowcount > 0

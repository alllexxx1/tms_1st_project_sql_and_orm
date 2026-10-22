"""CRUD и поиск пронумерованных мест через SQL-запросы."""

import psycopg
from psycopg.rows import dict_row


def list_seats(database_url: str, event_id: int) -> list[dict]:
    with psycopg.connect(database_url, row_factory=dict_row) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, event_id, row_number, seat_number FROM seats "
                "WHERE event_id = %s ORDER BY row_number, seat_number",
                (event_id,),
            )
            return cursor.fetchall()


def list_free_seats(database_url: str, event_id: int) -> list[dict]:
    with psycopg.connect(database_url, row_factory=dict_row) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT seats.id, seats.event_id, seats.row_number, seats.seat_number "
                "FROM seats LEFT JOIN tickets ON tickets.seat_id = seats.id "
                "WHERE seats.event_id = %s AND tickets.id IS NULL "
                "ORDER BY seats.row_number, seats.seat_number",
                (event_id,),
            )
            return cursor.fetchall()


def find_seat(
    database_url: str, event_id: int, row_number: int, seat_number: int
) -> dict | None:
    with psycopg.connect(database_url, row_factory=dict_row) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, event_id, row_number, seat_number FROM seats "
                "WHERE event_id = %s AND row_number = %s AND seat_number = %s",
                (event_id, row_number, seat_number),
            )
            return cursor.fetchone()


def add_seat(database_url: str, event_id: int, row_number: int, seat_number: int) -> int:
    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO seats (event_id, row_number, seat_number) "
                "VALUES (%s, %s, %s) RETURNING id",
                (event_id, row_number, seat_number),
            )
            return cursor.fetchone()[0]


def update_seat(database_url: str, seat_id: int, row_number: int, seat_number: int) -> bool:
    """Изменить номер свободного места в пределах его мероприятия."""
    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM tickets WHERE seat_id = %s", (seat_id,))
            if cursor.fetchone():
                raise ValueError("У места есть билет. Сначала отмените бронирование для изменения места.")
            cursor.execute(
                "UPDATE seats SET row_number = %s, seat_number = %s WHERE id = %s",
                (row_number, seat_number, seat_id),
            )
            return cursor.rowcount > 0


def delete_seat(database_url: str, seat_id: int) -> bool:
    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM seats WHERE id = %s", (seat_id,))
            return cursor.rowcount > 0

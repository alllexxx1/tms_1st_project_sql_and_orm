"""Просмотр, бронирование и отмена билетов через SQL-запросы."""

import psycopg
from psycopg.rows import dict_row


def list_tickets(database_url: str, event_id: int) -> list[dict]:
    with psycopg.connect(database_url, row_factory=dict_row) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT tickets.id, tickets.seat_id, tickets.customer_name, "
                "events.title, events.venue, events.starts_at, seats.row_number, seats.seat_number "
                "FROM tickets JOIN seats ON seats.id = tickets.seat_id "
                "JOIN events ON events.id = seats.event_id "
                "WHERE events.id = %s ORDER BY seats.row_number, seats.seat_number",
                (event_id,),
            )
            return cursor.fetchall()


def book_ticket(database_url: str, seat_id: int, customer_name: str) -> int:
    try:
        with psycopg.connect(database_url) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO tickets (seat_id, customer_name) VALUES (%s, %s) RETURNING id",
                    (seat_id, customer_name),
                )
                return cursor.fetchone()[0]
    except psycopg.errors.UniqueViolation:
        # К этому моменту with уже откатил транзакцию и закрыл соединение.
        raise ValueError("Место уже забронировано.") from None


def cancel_ticket(database_url: str, ticket_id: int) -> bool:
    with psycopg.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM tickets WHERE id = %s", (ticket_id,))
            return cursor.rowcount > 0

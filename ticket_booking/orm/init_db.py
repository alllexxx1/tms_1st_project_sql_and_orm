"""Демонстрационные данные через ORM. Таблицы создаются миграциями Alembic."""

from datetime import datetime

from sqlalchemy import Engine
from sqlalchemy.orm import Session

from ticket_booking.orm.models import Event, Seat, Ticket


def seed_data(engine: Engine) -> None:
    """Один раз заполнить пустые таблицы теми же примерами, что и в raw SQL."""
    events = [
        Event(title="Джазовый вечер", venue="Малый зал", starts_at=datetime(2026, 11, 15, 19)),
        Event(title="Лекция о космосе", venue="Большой зал", starts_at=datetime(2026, 11, 16, 18)),
    ]
    for event in events:
        for row_number in range(1, 3):
            for seat_number in range(1, 4):
                event.seats.append(Seat(row_number=row_number, seat_number=seat_number))
    events[0].seats[0].ticket = Ticket(customer_name="Анна Смирнова")

    with Session(engine) as session:
        session.add_all(events)
        session.commit()

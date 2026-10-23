"""Просмотр, бронирование и отмена билетов через SQLAlchemy ORM."""

from psycopg.errors import UniqueViolation
from sqlalchemy import Engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ticket_booking.orm.models import Event, Seat, Ticket


def list_tickets(engine: Engine, event_id: int) -> list[dict]:
    with Session(engine) as session:
        statement = (
            select(
                Ticket.id,
                Ticket.seat_id,
                Ticket.customer_name,
                Event.title,
                Event.venue,
                Event.starts_at,
                Seat.row_number,
                Seat.seat_number,
            )
            .join(Ticket.seat)
            .join(Seat.event)
            .where(Event.id == event_id)
            .order_by(Seat.row_number, Seat.seat_number)
        )
        return [dict(row) for row in session.execute(statement).mappings()]


def book_ticket(engine: Engine, seat_id: int, customer_name: str) -> int:
    try:
        with Session(engine) as session:
            ticket = Ticket(seat_id=seat_id, customer_name=customer_name)
            session.add(ticket)
            session.flush()
            ticket_id = ticket.id
            session.commit()
            return ticket_id
    except IntegrityError as error:
        # После выхода из with сессия закрыта, незавершенная транзакция отменена.
        if isinstance(error.orig, UniqueViolation):
            raise ValueError("Место уже забронировано.") from None
        raise


def cancel_ticket(engine: Engine, ticket_id: int) -> bool:
    with Session(engine) as session:
        ticket = session.get(Ticket, ticket_id)
        if ticket is None:
            return False
        session.delete(ticket)
        session.commit()
        return True

"""CRUD и поиск пронумерованных мест через SQLAlchemy ORM."""

from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from ticket_booking.orm.models import Seat, Ticket


def list_seats(engine: Engine, event_id: int) -> list[Seat]:
    with Session(engine) as session:
        statement = (
            select(Seat)
            .where(Seat.event_id == event_id)
            .order_by(Seat.row_number, Seat.seat_number)
        )
        return list(session.scalars(statement))


def list_free_seats(engine: Engine, event_id: int) -> list[Seat]:
    with Session(engine) as session:
        statement = (
            select(Seat)
            .outerjoin(Seat.ticket)
            .where(Seat.event_id == event_id, Ticket.id.is_(None))
            .order_by(Seat.row_number, Seat.seat_number)
        )
        return list(session.scalars(statement))


def find_seat(engine: Engine, event_id: int, row_number: int, seat_number: int) -> Seat | None:
    with Session(engine) as session:
        statement = select(Seat).where(
            Seat.event_id == event_id,
            Seat.row_number == row_number,
            Seat.seat_number == seat_number,
        )
        return session.scalar(statement)


def add_seat(engine: Engine, event_id: int, row_number: int, seat_number: int) -> int:
    with Session(engine) as session:
        seat = Seat(event_id=event_id, row_number=row_number, seat_number=seat_number)
        session.add(seat)
        session.flush()
        seat_id = seat.id
        session.commit()
        return seat_id


def update_seat(engine: Engine, seat_id: int, row_number: int, seat_number: int) -> bool:
    """Изменить номер свободного места в пределах его мероприятия."""
    with Session(engine) as session:
        seat = session.get(Seat, seat_id)
        if seat is None:
            return False
        if seat.ticket is not None:
            raise ValueError("У места есть билет. Сначала отмените бронирование для изменения места.")
        seat.row_number = row_number
        seat.seat_number = seat_number
        session.commit()
        return True


def delete_seat(engine: Engine, seat_id: int) -> bool:
    with Session(engine) as session:
        seat = session.get(Seat, seat_id)
        if seat is None:
            return False
        session.delete(seat)
        session.commit()
        return True

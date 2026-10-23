"""CRUD и поиск мероприятий через SQLAlchemy ORM."""

from datetime import datetime

from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from ticket_booking.orm.models import Event, Seat, Ticket


def list_events(engine: Engine) -> list[Event]:
    with Session(engine) as session:
        statement = select(Event).order_by(Event.starts_at, Event.id)
        return list(session.scalars(statement))


def search_events(engine: Engine, title_part: str = "", venue_part: str = "") -> list[Event]:
    with Session(engine) as session:
        statement = (
            select(Event)
            .where(Event.title.ilike(f"%{title_part}%"), Event.venue.ilike(f"%{venue_part}%"))
            .order_by(Event.starts_at, Event.id)
        )
        return list(session.scalars(statement))


def find_events_by_seat(engine: Engine, row_number: int, seat_number: int) -> list[Event]:
    """Найти мероприятия, у которых есть указанное место, включая занятые."""
    with Session(engine) as session:
        statement = (
            select(Event)
            .join(Event.seats)
            .where(Seat.row_number == row_number, Seat.seat_number == seat_number)
            .order_by(Event.starts_at, Event.id)
        )
        return list(session.scalars(statement))


def add_event(engine: Engine, title: str, venue: str, starts_at: datetime) -> int:
    with Session(engine) as session:
        event = Event(title=title, venue=venue, starts_at=starts_at)
        session.add(event)
        session.flush()
        event_id = event.id
        session.commit()
        return event_id


def update_event(
    engine: Engine, event_id: int, title: str, venue: str, starts_at: datetime
) -> bool:
    with Session(engine) as session:
        event = session.get(Event, event_id)
        if event is None:
            return False
        if event.venue != venue:
            statement = select(Ticket.id).join(Ticket.seat).where(Seat.event_id == event_id).limit(1)
            if session.scalar(statement) is not None:
                raise ValueError("У мероприятия есть билеты. Сначала отмените бронирования для смены площадки.")
        event.title = title
        event.venue = venue
        event.starts_at = starts_at
        session.commit()
        return True


def delete_event(engine: Engine, event_id: int) -> bool:
    with Session(engine) as session:
        event = session.get(Event, event_id)
        if event is None:
            return False
        session.delete(event)
        session.commit()
        return True

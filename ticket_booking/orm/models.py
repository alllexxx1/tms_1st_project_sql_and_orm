"""Модели с теми же полями и ограничениями, что и в raw SQL-схеме."""

from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Event(Base):
    __tablename__ = "events"
    __table_args__ = (
        CheckConstraint("btrim(title) <> ''", name="ck_events_title_not_blank"),
        CheckConstraint("btrim(venue) <> ''", name="ck_events_venue_not_blank"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150))
    venue: Mapped[str] = mapped_column(String(150))
    starts_at: Mapped[datetime]

    seats: Mapped[list["Seat"]] = relationship(back_populates="event", passive_deletes="all")


class Seat(Base):
    __tablename__ = "seats"
    __table_args__ = (
        CheckConstraint("row_number > 0", name="ck_seats_row_positive"),
        CheckConstraint("seat_number > 0", name="ck_seats_number_positive"),
        UniqueConstraint("event_id", "row_number", "seat_number", name="uq_seats_event_row_number"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(
        ForeignKey("events.id", name="fk_seats_event", ondelete="CASCADE")
    )
    row_number: Mapped[int]
    seat_number: Mapped[int]

    event: Mapped[Event] = relationship(back_populates="seats")
    ticket: Mapped["Ticket | None"] = relationship(back_populates="seat", passive_deletes="all")


class Ticket(Base):
    __tablename__ = "tickets"
    __table_args__ = (
        UniqueConstraint("seat_id", name="uq_tickets_seat"),
        CheckConstraint("btrim(customer_name) <> ''", name="ck_tickets_customer_not_blank"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    seat_id: Mapped[int] = mapped_column(
        ForeignKey("seats.id", name="fk_tickets_seat", ondelete="RESTRICT")
    )
    customer_name: Mapped[str] = mapped_column(String(100))

    seat: Mapped[Seat] = relationship(back_populates="ticket")

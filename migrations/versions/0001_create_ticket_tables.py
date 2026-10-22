"""Создание таблиц мероприятий, мест и билетов."""

from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    """Создать таблицы и ограничения."""
    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(150), nullable=False),
        sa.Column("venue", sa.String(150), nullable=False),
        sa.Column("starts_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("btrim(title) <> ''", name="ck_events_title_not_blank"),
        sa.CheckConstraint("btrim(venue) <> ''", name="ck_events_venue_not_blank"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "seats",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("row_number", sa.Integer(), nullable=False),
        sa.Column("seat_number", sa.Integer(), nullable=False),
        sa.CheckConstraint("row_number > 0", name="ck_seats_row_positive"),
        sa.CheckConstraint("seat_number > 0", name="ck_seats_number_positive"),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"], name="fk_seats_event", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_id", "row_number", "seat_number", name="uq_seats_event_row_number"),
    )
    op.create_table(
        "tickets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("seat_id", sa.Integer(), nullable=False),
        sa.Column("customer_name", sa.String(100), nullable=False),
        sa.CheckConstraint("btrim(customer_name) <> ''", name="ck_tickets_customer_not_blank"),
        sa.ForeignKeyConstraint(["seat_id"], ["seats.id"], name="fk_tickets_seat", ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("seat_id", name="uq_tickets_seat"),
    )


def downgrade() -> None:
    """Удалить таблицы в обратном порядке зависимостей."""
    op.drop_table("tickets")
    op.drop_table("seats")
    op.drop_table("events")

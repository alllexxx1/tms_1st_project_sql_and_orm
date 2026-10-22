"""Подключение Alembic к ORM-моделям и базе из .env."""

from logging.config import fileConfig

from alembic import context

from ticket_booking.config import get_database_url
from ticket_booking.orm.database import get_engine
from ticket_booking.orm.models import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Сформировать SQL миграции без подключения к PostgreSQL."""
    engine = get_engine(get_database_url())
    context.configure(
        url=engine.url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Применить миграции к базе PostgreSQL."""
    engine = get_engine(get_database_url())
    try:
        with engine.connect() as connection:
            context.configure(connection=connection, target_metadata=target_metadata)
            with context.begin_transaction():
                context.run_migrations()
    finally:
        engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

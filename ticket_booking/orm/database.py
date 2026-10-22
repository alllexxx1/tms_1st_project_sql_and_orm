"""Создание движка SQLAlchemy с драйвером Psycopg 3."""

from sqlalchemy import Engine, create_engine, make_url


def get_engine(database_url: str) -> Engine:
    url = make_url(database_url).set(drivername="postgresql+psycopg")
    return create_engine(url, connect_args={"connect_timeout": 5})

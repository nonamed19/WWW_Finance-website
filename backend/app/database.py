from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from fastapi import HTTPException, status

from .config import (
    DATABASE_URL,
    DB_CONNECT_TIMEOUT,
    DB_MAX_OVERFLOW,
    DB_POOL_SIZE,
)


if not DATABASE_URL.startswith("mysql+pymysql://"):
    raise RuntimeError(
        "DATABASE_URL must use the mysql+pymysql:// scheme. "
        "Copy .env.example to .env and enter the MySQL connection details."
    )

engine = create_engine(
    DATABASE_URL,
    connect_args={"charset": "utf8mb4", "connect_timeout": DB_CONNECT_TIMEOUT},
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_MAX_OVERFLOW,
)
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    # API responses are often serialized immediately after commit.  Keeping the
    # loaded state prevents a needless SELECT for every serialized object.
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


def initialize_database() -> None:
    """Create the schema when MySQL is reachable.

    Connection failures are deliberately left to the caller so application
    startup can distinguish an unavailable server from a schema/programming
    error.
    """
    Base.metadata.create_all(bind=engine)
    # `create_all` does not add indexes to tables created by an older version of
    # the application. Create the declared indexes idempotently on startup.
    for table in Base.metadata.tables.values():
        for index in table.indexes:
            index.create(bind=engine, checkfirst=True)


def database_is_available() -> bool:
    """Return whether a connection can currently be established."""
    try:
        with engine.connect():
            return True
    except SQLAlchemyError:
        return False


def get_db():
    db = SessionLocal()
    try:
        # Establish the connection in the dependency so DB-backed endpoints
        # return a stable 503 instead of leaking a driver exception as a 500.
        db.connection()
        yield db
    except OperationalError as error:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is temporarily unavailable.",
        ) from error
    finally:
        db.close()

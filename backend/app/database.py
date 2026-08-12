import logging

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

logger = logging.getLogger(__name__)


def _create_mysql_engine(database_url: str):
    """Build the MySQL engine without opening a connection during import."""
    return create_engine(
        database_url,
        connect_args={"charset": "utf8mb4", "connect_timeout": DB_CONNECT_TIMEOUT},
        pool_pre_ping=True,
        pool_recycle=3600,
        pool_size=DB_POOL_SIZE,
        max_overflow=DB_MAX_OVERFLOW,
    )

engine = None
if DATABASE_URL.startswith("mysql+pymysql://"):
    engine = _create_mysql_engine(DATABASE_URL)
elif DATABASE_URL:
    logger.warning("DATABASE_URL is not a mysql+pymysql URL; database features are disabled.")
else:
    logger.warning("DATABASE_URL is not configured; database features are disabled.")

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
    """Create the schema when a MySQL connection is configured and available."""
    if engine is None:
        return

    Base.metadata.create_all(bind=engine)

    # `create_all` does not add indexes to tables created by an older version of
    # the application. Create the declared indexes idempotently on startup.
    for table in Base.metadata.tables.values():
        for index in table.indexes:
            index.create(bind=engine, checkfirst=True)


def database_is_available() -> bool:
    """Return whether a connection can currently be established."""
    if engine is None:
        return False

    try:
        with engine.connect():
            return True
    except SQLAlchemyError:
        return False


def dispose_database() -> None:
    """Release connections held by the currently active engine."""
    if engine is not None:
        engine.dispose()


def get_db():
    if engine is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not configured.",
        )

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

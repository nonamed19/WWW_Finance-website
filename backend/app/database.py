from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import DATABASE_URL, DB_MAX_OVERFLOW, DB_POOL_SIZE


if not DATABASE_URL.startswith("mysql+pymysql://"):
    raise RuntimeError(
        "DATABASE_URL must use the mysql+pymysql:// scheme. "
        "Copy .env.example to .env and enter the MySQL connection details."
    )

engine = create_engine(
    DATABASE_URL,
    connect_args={"charset": "utf8mb4"},
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


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

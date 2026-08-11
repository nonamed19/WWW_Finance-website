from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import DATABASE_URL


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
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

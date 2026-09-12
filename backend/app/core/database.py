"""
database.py
-----------
PostgreSQL / SQLite database engine and session management.
"""

import os
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from backend.app.core.config import settings


class Base(DeclarativeBase):
    """SQLAlchemy Declarative Base for ORM entities."""
    pass


def get_database_url() -> str:
    url = settings.DATABASE_URL
    if not url:
        db_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "backend", "pharmasafe_auth.db")
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        return f"sqlite:///{os.path.abspath(db_path)}"

    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


DATABASE_URL = get_database_url()

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


def init_db():
    """Create all relational tables if they do not already exist."""
    # Import domain models so Base.metadata is registered
    import backend.app.domain.models.user  # noqa
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI transactional session dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection():
    """Diagnostic connection tester."""
    with engine.connect() as conn:
        res = conn.execute(text("SELECT 1;"))
        print("[DATABASE] Connection healthy:", res.scalar() == 1)

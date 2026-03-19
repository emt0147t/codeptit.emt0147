"""
Database setup and session management.
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DATABASE_URL

is_sqlite = DATABASE_URL.startswith("sqlite")

from sqlalchemy.pool import NullPool

if is_sqlite:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # Use NullPool for Supabase/Render to avoid "SSL connection closed"
    # every request gets a new connection, and we verify it with pre_ping
    engine = create_engine(
        DATABASE_URL,
        poolclass=NullPool,
        pool_pre_ping=True,
        connect_args={"sslmode": "require"}
    )

@event.listens_for(engine, "connect")
def pragma_on_connect(dbapi_con, con_record):
    if is_sqlite:
        cursor = dbapi_con.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables."""
    import models  # noqa: F401
    Base.metadata.create_all(bind=engine)

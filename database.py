"""
Database setup and session management.
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DATABASE_URL
import logging

logger = logging.getLogger(__name__)
is_sqlite = DATABASE_URL.startswith("sqlite")

if is_sqlite:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # Production PostgreSQL (Supabase Pooler)
    # pool_pre_ping: test connection before using (catches stale SSL)
    # pool_recycle: close connections older than 180s (prevents SSL timeout)  
    # pool_size=5: keep pool small for Supabase free tier
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,
        max_overflow=5,
        pool_pre_ping=True,
        pool_recycle=180,
        pool_timeout=10,
        connect_args={"sslmode": "require", "connect_timeout": 10}
    )

@event.listens_for(engine, "connect")
def on_connect(dbapi_con, con_record):
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
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        logger.warning(f"init_db failed (tables may already exist): {e}")

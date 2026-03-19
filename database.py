"""
Database setup and session management.
"""
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from config import DATABASE_URL
import logging
import time

logger = logging.getLogger(__name__)
is_sqlite = DATABASE_URL.startswith("sqlite")

if is_sqlite:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # Production PostgreSQL (Supabase Pooler / pgbouncer)
    # NullPool: fresh connection per request (safest for pgbouncer)
    engine = create_engine(
        DATABASE_URL,
        poolclass=NullPool,
        connect_args={"sslmode": "require", "connect_timeout": 5}
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


def _create_tested_session(max_retries=3):
    """Create a session and verify the connection works, with retries."""
    last_error = None
    for attempt in range(max_retries):
        try:
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            return db
        except Exception as e:
            last_error = e
            try:
                db.close()
            except:
                pass
            error_msg = str(e).lower()
            if "ssl" in error_msg or "closed" in error_msg or "connection" in error_msg:
                logger.warning(f"DB connect attempt {attempt+1}/{max_retries} failed: {e}")
                time.sleep(0.5)
                continue
            else:
                raise
    raise last_error


def get_db():
    """Dependency to get database session."""
    db = _create_tested_session()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables (safe to call multiple times)."""
    import models  # noqa: F401
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        logger.warning(f"init_db skipped (tables likely exist): {e}")

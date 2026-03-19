"""
Database setup and session management.
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DATABASE_URL

is_sqlite = DATABASE_URL.startswith("sqlite")

if is_sqlite:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # Production PostgreSQL (Supabase)
    # Use pool_pre_ping to detect stale connections
    # Use pool_recycle to close connections after 5 minutes
    # Use a small pool to avoid connection limits
    engine = create_engine(
        DATABASE_URL,
        pool_size=2,
        max_overflow=3,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args={"sslmode": "require", "connect_timeout": 10}
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

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import OperationalError
from backend.app.core.config import settings
import logging

logger = logging.getLogger("pocketuni.database")

# Build connection URL using URL.create()
db_url_obj = settings.get_database_url_object()
is_sqlite = db_url_obj.drivername.startswith("sqlite")

engine = create_engine(
    db_url_obj,
    connect_args={"check_same_thread": False} if is_sqlite else {},
    pool_pre_ping=True,
    pool_size=10 if not is_sqlite else 5,
    max_overflow=20 if not is_sqlite else 10,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_health() -> dict:
    """
    Performs live database readiness probe.
    Returns status, engine URL (masked), version, and current database.
    Raises OperationalError if unavailable.
    """
    try:
        with engine.connect() as conn:
            res_ver = conn.execute(text("SELECT version();")).scalar() if not is_sqlite else "SQLite 3"
            curr_db = conn.execute(text("SELECT current_database();")).scalar() if not is_sqlite else "sqlite"
            return {
                "status": "HEALTHY",
                "driver": db_url_obj.drivername,
                "database": curr_db,
                "version": res_ver,
                "url": settings.get_safe_database_url()
            }
    except Exception as exc:
        safe_url = settings.get_safe_database_url()
        logger.error(f"Database connection failed to {safe_url}: {str(exc)}")
        raise OperationalError(
            f"Unable to connect to PostgreSQL at {safe_url}. Please ensure PostgreSQL service is running.",
            params=None,
            orig=exc
        )

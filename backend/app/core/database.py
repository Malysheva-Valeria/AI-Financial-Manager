"""
Database engine setup and session management.
Follows Dependency Inversion Principle.
"""
from sqlmodel import create_engine, Session, SQLModel
from typing import Generator
from app.core.config import settings

# Create engine with connection pooling
engine = create_engine(
    settings.database_url,
    echo=settings.debug,  # Log SQL queries in debug mode
    pool_pre_ping=True,  # Verify connections before using
    pool_size=10,  # Number of connections to maintain
    max_overflow=20  # Max additional connections when pool is full
)


def create_db_and_tables():
    """Create all database tables. Used for testing and initial setup."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    Dependency injection for database session.

    Usage in FastAPI:
        @app.get("/users")
        def get_users(session: Session = Depends(get_session)):
            ...
    """
    with Session(engine) as session:
        yield session
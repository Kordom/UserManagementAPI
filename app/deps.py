from collections.abc import Generator
from sqlalchemy.orm import Session

from app.core.database import Session


def get_db() -> Generator[Session, None, None]:
    """
    Provide a database session for request handling.
    Yields:
        Active SQLAlchemy Session instance.
    """
    with Session() as session:
        yield session

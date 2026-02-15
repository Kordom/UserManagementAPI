from collections.abc import Generator
from sqlalchemy.orm import Session

from app.core.database import Session


def get_db() -> Generator[Session, None, None]:
    with Session() as session:
        yield session
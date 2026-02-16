from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User


class UsernameAlreadyExistsError(Exception):
    pass


def create_user(db: Session, *, username: str, password: str) -> User:
    db.execute(text("SELECT pg_advisory_xact_lock(1234567890)"))

    users_exist = db.execute(select(User.id).limit(1)).first() is not None

    user = User(
        username=username,
        hashed_password=hash_password(password),
        is_admin=(not users_exist),
        is_active=True,
    )

    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise UsernameAlreadyExistsError()

    db.refresh(user)
    return user
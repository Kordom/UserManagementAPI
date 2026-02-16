from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User


class UsernameAlreadyExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class AdminSelfActionForbiddenError(Exception):
    pass


def create_user(db: Session, *, username: str, password: str) -> User:
    """
    Create a new user account.
    Args:
        db: Active database session.
        username: Unique username.
        password: Plain-text password.
    Raises:
        UsernameAlreadyExistsError: If username already exists.
    Returns:
        Newly created User.
    """
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


def update_user(db: Session, *, user: User, password: str | None) -> User:
    """
    Update the authenticated user password.
    Args:
        db: Active database session.
        user: The user instance to update.
        password: New password.
    Returns:
        Updated User.
    """
    if password:
        user.hashed_password = hash_password(password)

    db.commit()
    db.refresh(user)
    return user


def list_users(db: Session) -> list[User]:
    """
    Retrieve all users.
    Args:
        db: Active database session.
    Returns:
        List of User.
    """
    return db.query(User).order_by(User.id.asc()).all()


def get_user_by_id(db: Session, user_id: int) -> User:
    """
    Retrieve a user by its ID.
    Args:
        db: Active database session.
        user_id: User identifier.
    Raises:
        UserNotFoundError: If user does not exist.
    Returns:
        User.
    """
    user = db.query(User).filter(User.id == user_id).one_or_none()
    if user is None:
        raise UserNotFoundError()
    return user


def set_user_active(
        db: Session,
        *,
        target_user_id: int,
        is_active: bool,
        acting_admin: User,
) -> User:
    """
    Activate or deactivate a user account.
    Args:
        db: Active database session.
        target_user_id: ID of the user to modify.
        is_active: Desired active state.
        acting_admin: Currently authenticated admin user.
    Raises:
        UserNotFoundError: If target user does not exist.
        AdminSelfActionForbiddenError: If admin tries to modify self.
    Returns:
        Updated User.
    """
    if acting_admin.id == target_user_id:
        raise AdminSelfActionForbiddenError()

    user = get_user_by_id(db, target_user_id)
    user.is_active = is_active

    db.commit()
    db.refresh(user)
    return user


def delete_user(
        db: Session,
        *,
        target_user_id: int,
        acting_admin: User,
) -> None:
    """
     Permanently delete a user account.
     Args:
         db: Active database session.
         target_user_id: ID of user to delete.
         acting_admin: Currently authenticated admin user.
     Raises:
         UserNotFoundError: If user does not exist.
         AdminSelfActionForbiddenError: If admin tries to delete self.
     """
    if acting_admin.id == target_user_id:
        raise AdminSelfActionForbiddenError()

    user = get_user_by_id(db, target_user_id)

    db.delete(user)
    db.commit()

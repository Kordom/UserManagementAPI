from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.deps import get_db
from app.models.user import User

security = HTTPBasic()


def get_current_user(
        credentials: HTTPBasicCredentials = Depends(security),
        db: Session = Depends(get_db),
) -> User:
    """
    Validates username and password against the database
    Raises:
        HTTPException: If authentication fails.
    Returns:
        Authenticated User.
    """
    username = credentials.username
    password = credentials.password

    user = db.query(User).filter(User.username == username).one_or_none()

    auth_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Basic"},
    )

    if user is None:
        raise auth_error

    if not user.is_active:
        raise auth_error

    if not verify_password(password, user.hashed_password):
        raise auth_error

    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
     Ensure the current user has admin rights.
     Raises:
         HTTPException: If the user is not an admin.
     Returns:
         The authenticated admin user.
     """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.deps import get_db
from app.schemas.schemas import UserCreate, UserRead, UserUpdate
from app.services.user_services import (
    UsernameAlreadyExistsError,
    create_user, update_user,
    AdminSelfActionForbiddenError,
    UserNotFoundError,
    delete_user, get_user_by_id,
    list_users, set_user_active,
)
from app.models.user import User
from app.core.auth import get_current_user, require_admin

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    """
    Register a new user.
    Args:
        payload: User registration data.
        db: Active database session.
    Returns:
        Created user.
    """
    try:
        user = create_user(
            db,
            username=payload.username,
            password=payload.password,
        )
    except UsernameAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered",
        )

    return user


@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)) -> UserRead:
    """
    Retrieve the authenticated user's profile.
    Args:
        current_user: Authenticated user injected via dependency.
    Returns:
        User profile data.
    """
    return current_user


@router.put("/me", response_model=UserRead)
def update_me(
        payload: UserUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user),
) -> UserRead:
    """
    Update the authenticated user's profile.
    Args:
        payload: Update data.
        db: Active database session.
        current_user: Authenticated user.
    Returns:
        Updated user profile.
    """
    user = update_user(db, user=current_user, password=payload.password)
    return user


@router.get("", response_model=list[UserRead])
def admin_list_users(
        db: Session = Depends(get_db),
        admin: User = Depends(require_admin),
) -> list[UserRead]:
    """
    Retrieve a list of all users.
    Args:
        db: Active database session.
        admin: Authenticated admin user.
    Returns:
        List of user profiles.
    """
    return list_users(db)


@router.get("/{user_id}", response_model=UserRead)
def admin_get_user(
        user_id: int,
        db: Session = Depends(get_db),
        admin: User = Depends(require_admin),
) -> UserRead:
    """
    Retrieve a specific user by ID.
    Args:
        user_id: Target user's ID.
        db: Active database session.
        admin: Authenticated admin user.
    Returns:
        User profile.
    Raises:
        HTTPException: If user does not exist.
    """
    try:
        return get_user_by_id(db, user_id)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")


@router.patch("/{user_id}/activate", response_model=UserRead)
def admin_activate_user(
        user_id: int,
        db: Session = Depends(get_db),
        admin: User = Depends(require_admin),
) -> UserRead:
    """
    Activate a user account.
    Raises:
        HTTPException: If user not found or action is forbidden.
    """
    try:
        return set_user_active(db, target_user_id=user_id, is_active=True, acting_admin=admin)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except AdminSelfActionForbiddenError:
        raise HTTPException(status_code=400, detail="Admin cannot activate their own account")


@router.patch("/{user_id}/deactivate", response_model=UserRead)
def admin_deactivate_user(
        user_id: int,
        db: Session = Depends(get_db),
        admin: User = Depends(require_admin),
) -> UserRead:
    """
    Deactivate a user account.
    Raises:
        HTTPException: If user not found or action is forbidden.
    """
    try:
        return set_user_active(db, target_user_id=user_id, is_active=False, acting_admin=admin)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except AdminSelfActionForbiddenError:
        raise HTTPException(status_code=400, detail="Admin cannot deactivate their own account")


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_user(
        user_id: int,
        db: Session = Depends(get_db),
        admin: User = Depends(require_admin),
) -> None:
    """
    Permanently delete a user account.
    Raises:
        HTTPException: If user not found or action is forbidden.
    """
    try:
        delete_user(db, target_user_id=user_id, acting_admin=admin)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
    except AdminSelfActionForbiddenError:
        raise HTTPException(status_code=400, detail="Admin cannot delete their own account")

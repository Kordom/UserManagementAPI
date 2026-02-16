from pydantic import BaseModel, Field, ConfigDict


class UserCreate(BaseModel):
    """
    Schema for user registration.
    Validates incoming data when creating a new user.
    """
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=72)


class UserRead(BaseModel):
    """
    Public representation of a user.
    Used in API responses to prevent exposing
    sensitive fields such as hashed passwords.
    """
    id: int
    username: str
    is_active: bool
    is_admin: bool

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """
    Schema for updating the authenticated user's profile.
    """
    password: str | None = Field(default=None, min_length=8, max_length=72)

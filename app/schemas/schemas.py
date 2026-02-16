from pydantic import BaseModel, Field, ConfigDict


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=72)


class UserRead(BaseModel):
    id: int
    username: str
    is_active: bool
    is_admin: bool

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    password: str | None = Field(default=None, min_length=8, max_length=72)
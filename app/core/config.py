from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from os import getenv

load_dotenv()


class Settings(BaseSettings):
    db_user: str = getenv("POSTGRES_USER")
    db_password: str = getenv("POSTGRES_PASSWORD")
    db_name: str = getenv("POSTGRES_DB")
    db_url: str


def get_db_settings() -> Settings:
    return Settings(
        db_url=getenv("DATABASE_URL")
    )


settings = get_db_settings()

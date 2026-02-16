import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.deps import get_db
from app.main import app


TEST_DATABASE_URL = os.getenv("DATABASE_URL")


@pytest.fixture()
def db_engine():
    if not TEST_DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set for tests")

    engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)

    # clean DB for each test: drop + create
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield engine

    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session(db_engine):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    with TestingSessionLocal() as session:
        yield session


@pytest.fixture()
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
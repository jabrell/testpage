from typing import Generator

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.api.deps import get_db
from app.main import app

# set up an in memory sqlite database for testing
db_url = "sqlite:///:memory:"
test_engine = create_engine(
    "sqlite:///test.db",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SQLModel.metadata.create_all(test_engine)


def overwrite_get_db() -> Generator[Session, None, None]:
    with Session(test_engine) as session:
        yield session


# In your conftest.py file:
@pytest.fixture(scope="session", autouse=True)
def override_db_dependency():
    app.dependency_overrides[get_db] = overwrite_get_db

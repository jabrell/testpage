import pathlib
from typing import Generator

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.api.deps import get_db
from app.main import app

# import all models to create tables
from app.models import *  # noqa
from app.models import UserGroup

# delete the test database if it exists
if pathlib.Path("test.db").exists():
    pathlib.Path("test.db").unlink()

# set up an in memory sqlite database for testing
test_engine = create_engine(
    "sqlite:///test.db",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def pytest_sessionstart(session):
    """
    Called after the Session object has been created and
    before performing collection and entering the run test loop.
    """
    # create tables
    SQLModel.metadata.create_all(test_engine)
    # add some user groups
    with Session(test_engine) as s:
        s.add(UserGroup(name="admin", description="Admin group"))
        s.add(UserGroup(name="standard", description="Standard group"))
        s.commit()


def overwrite_get_db() -> Generator[Session, None, None]:
    with Session(test_engine) as session:
        yield session


# In your conftest.py file:
@pytest.fixture(scope="session", autouse=True)
def override_db_dependency():
    app.dependency_overrides[get_db] = overwrite_get_db

import pathlib
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.api.deps import get_db
from app.core.config import settings
from app.core.security import hash_password
from app.main import app

# import all models to create tables
from app.models import *  # noqa
from app.models import User, UserGroup
from app.schema_manager import SchemaManager

from .utils import get_admin_header, get_standard_header

# delete the test database if it exists
if pathlib.Path("test.db").exists():
    pathlib.Path("test.db").unlink()

# set up an in memory sqlite database for testing
test_engine = create_engine(
    "sqlite:///test.db",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# some test data
admin_group = UserGroup(id=1, name="admin", description="Admin group")
standard_group = UserGroup(id=2, name="standard", description="Standard group")
admin_user_properties = {
    "id": 1,
    "username": settings.FIRST_SUPERUSER,
    "email": settings.FIRST_SUPERUSER_MAIL,
    "password": hash_password(settings.FIRST_SUPERUSER_PASSWORD),
    "usergroup_id": 1,
    "is_superuser": True,
    "is_active": True,
}
standard_user_properties = {
    "id": 2,
    "username": "Tracy",
    "password": hash_password("Chapman"),
    "email": "tracy@chapman.com",
    "usergroup_id": 2,
    "is_active": True,
    "is_superuser": False,
}


def pytest_sessionstart():
    """
    Called after the Session object has been created and
    before performing collection and entering the run test loop.
    """
    # create tables
    SQLModel.metadata.create_all(test_engine)
    # add some user groups
    with Session(test_engine) as s:
        s.add(admin_group)
        s.add(standard_group)
        s.add(User(**admin_user_properties))
        s.add(User(**standard_user_properties))
        s.commit()


def overwrite_get_db() -> Generator[Session, None, None]:
    with Session(test_engine) as session:
        yield session


@pytest.fixture(scope="session", autouse=True)
def override_db_dependency():
    app.dependency_overrides[get_db] = overwrite_get_db


@pytest.fixture(scope="session", autouse=True)
def db() -> Generator[Session, None, None]:
    with Session(test_engine) as session:
        yield session


@pytest.fixture(scope="session")
def schema_manager() -> SchemaManager:
    return SchemaManager()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def admin_token_header(client: TestClient) -> dict[str, str]:
    return get_admin_header(client)


@pytest.fixture(scope="module")
def standard_token_header(client: TestClient) -> dict[str, str]:
    return get_standard_header(client)

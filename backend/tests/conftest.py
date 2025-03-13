import pathlib
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

from app.api.deps import get_db
from app.core.config import settings
from app.core.security import hash_password
from app.main import app

# import all models to create tables
from app.models import *  # noqa
from app.models import User, UserGroup

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

# a standard user
standard_user_settings = {
    "username": "Tracy",
    "password": "Chapman",
    "email": "tracy@chapman.com",
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
        s.add(UserGroup(name="admin", description="Admin group"))
        s.add(UserGroup(name="standard", description="Standard group"))
        # add admin and standard user
        group_id = s.exec(select(UserGroup.id).where(UserGroup.name == "admin")).first()
        admin_user = User(
            username=settings.FIRST_SUPERUSER,
            email=settings.FIRST_SUPERUSER_MAIL,
            password=hash_password(settings.FIRST_SUPERUSER_PASSWORD),
            usergroup_id=group_id,
        )
        group_id = s.exec(
            select(UserGroup.id).where(UserGroup.name == "standard")
        ).first()
        standard_user = User(**standard_user_settings, usergroup_id=group_id)
        standard_user.password = hash_password(standard_user.password)
        s.add(admin_user)
        s.add(standard_user)
        s.commit()


def overwrite_get_db() -> Generator[Session, None, None]:
    with Session(test_engine) as session:
        yield session


@pytest.fixture(scope="session", autouse=True)
def override_db_dependency():
    app.dependency_overrides[get_db] = overwrite_get_db


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

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, delete

from app.database_access import get_db_session
from app.main import app
from app.models import User

db_url = "sqlite:///:memory:"
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SQLModel.metadata.create_all(test_engine)


def override_get_db_session():
    session = Session(test_engine)
    return session


app.dependency_overrides[get_db_session] = override_get_db_session


@pytest.fixture(scope="function")
def clear_users():
    """Clears the database before each test."""

    session = override_get_db_session()
    statement = delete(User)
    session.exec(statement)
    session.commit()

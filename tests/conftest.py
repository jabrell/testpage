import pytest
from sqlalchemy.sql import delete

from app.database_access import DatabaseAccessLayer
from app.models import User


@pytest.fixture(scope="function")
def clear_users():
    """Clears the database before each test."""
    dal = DatabaseAccessLayer()
    with dal.session as session:
        statement = delete(User)
        session.exec(statement)
        session.commit()
        yield

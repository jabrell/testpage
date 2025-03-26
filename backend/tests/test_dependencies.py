from datetime import timedelta
from unittest.mock import MagicMock

import jwt
import pytest
from fastapi import HTTPException, status
from sqlmodel import Session, create_engine
from sqlmodel.pool import StaticPool

from app.api.deps import (
    get_current_user,
    get_db,
    get_schema_manager,
)
from app.core.config import settings
from app.core.security import create_access_token
from app.models import User
from app.schema_manager import SchemaManager

# Create a mock database engine
engine = create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)


@pytest.fixture
def mock_session():
    # Create a new session for each test
    connection = engine.connect()
    session = Session(bind=connection)
    yield session
    session.close()
    connection.close()


@pytest.fixture
def mock_user():
    return User(
        id=1,
        username="testuser",
        email="testuser@example.com",
        is_superuser=False,
        is_active=True,
    )


def test_get_db(mock_session):
    # Test the get_db dependency
    db = next(get_db())
    assert isinstance(db, Session)


def test_get_schema_manager():
    # Test the get_schema_manager dependency
    manager = next(get_schema_manager())
    assert isinstance(manager, SchemaManager)


def test_get_current_user(mocker, mock_session, mock_user):
    # Mock the JWT decoding process
    token = create_access_token(mock_user.username)
    token_return = jwt.decode(
        token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
    )
    mock_jwt_decode = mocker.patch("jwt.decode")
    mock_jwt_decode.return_value = token_return

    # Mock the database query to return the mock user
    mock_session.exec = MagicMock(
        return_value=MagicMock(first=MagicMock(return_value=mock_user))
    )

    # Test the get_current_user dependency
    user = get_current_user(session=mock_session, token=token)
    assert user == mock_user


def test_get_current_user_invalid_token(mocker, mock_session):
    # Test the get_current_user dependency with an invalid token
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(session=mock_session, token="invalid_token")
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert "Token expired or invalid" in exc_info.value.detail


def test_get_current_user_not_found(mocker, mock_session):
    # Mock the JWT decoding process
    token = create_access_token("wrong_user")
    token_return = jwt.decode(
        token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
    )
    mock_jwt_decode = mocker.patch("jwt.decode")
    mock_jwt_decode.return_value = token_return

    # Mock the database query to return None
    mock_session.exec = MagicMock(
        return_value=MagicMock(first=MagicMock(return_value=None))
    )

    # Test the get_current_user dependency with a non-existent user
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(session=mock_session, token=token)
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


def test_get_current_user_token_expired(mocker, mock_session, mock_user):
    # Mock the JWT decoding process
    token = create_access_token(mock_user.username, expires_delta=timedelta(minutes=-1))

    # Test the get_current_user dependency
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(session=mock_session, token=token)
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert "Token expired or invalid" in exc_info.value.detail

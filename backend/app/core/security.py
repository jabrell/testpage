from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.hash import pbkdf2_sha256

from .config import settings
from .exceptions import InvalidTokenError


def create_access_token(
    information: str | Any,
    expires_delta: timedelta = timedelta(minutes=settings.JWT_TIMEDELTA),
) -> str:
    """Create an access token containing user and expiry information.

    Args:
        information (str | Any): The user information to be encoded in the token.
        expires_delta (timedelta, optional): The time delta for the token to expire.
            Defaults to timedelta(minutes=settings.JWT_TIMEDELTA).

    Returns:
        str: The encoded JWT token.
    """
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(information)}
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Decode an access token to extract user information.

    Args:
        token (str): The JWT token to be decoded.

    Returns:
        dict[str, Any] | None: The decoded JWT token if valid, else None.
    """
    try:
        decoded = jwt.decode(
            token, settings.JWT_SECRET, algorithms=settings.JWT_ALGORITHM
        )
        return decoded
    except jwt.ExpiredSignatureError:
        raise InvalidTokenError("Token expired")
    except jwt.InvalidTokenError:
        raise InvalidTokenError("Token invalid")


def hash_password(password: str) -> str:
    """Hash the password using pbkdf2_sha256

    Args:
        password (str): password to hash

    Returns:
        str: hashed password
    """
    return pbkdf2_sha256.hash(password)


def verify_password(password: str, hash: str) -> bool:
    """Authenticate the user with the given password

    Args:
        password (str): password to authenticate
        hash (str): hashed password

    Returns:
        bool: True if the password is correct, False otherwise
    """
    try:
        return pbkdf2_sha256.verify(password, hash)
    except ValueError:
        return False

from datetime import timedelta

import pytest

from app.core.exceptions import InvalidTokenError
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_create_access_token():
    token = create_access_token("test")
    returned = decode_access_token(token)
    assert returned["sub"] == "test"

    # sending wrong token raises InvalidTokenError
    with pytest.raises(InvalidTokenError):
        decode_access_token("test")

    # sending expired token raises InvalidTokenError
    token = create_access_token("test", expires_delta=timedelta(milliseconds=1))
    with pytest.raises(InvalidTokenError):
        decode_access_token(token)


def test_password_hash():
    password = "test"
    hashed = hash_password(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrong", hashed)
    assert not verify_password(password, "wrong")
    assert not verify_password("wrong", "wrong")

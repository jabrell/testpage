import logging
from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session, select

from app.core.config import settings
from app.core.db import engine
from app.models import TokenPayload, User
from app.schema_manager import SchemaManager


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]


def get_schema_manager() -> Generator[SchemaManager, None, None]:
    with SchemaManager() as manager:
        yield manager


SchemaManagerDep = Annotated[SchemaManager, Depends(get_schema_manager)]


reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/user/login")
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        ) from None
    q = select(User).where(User.username == token_data.sub)
    user = session.exec(q).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def is_admin_user(current_user: CurrentUser) -> User:
    logging.info(f"current_user: {current_user}")
    if current_user.usergroup.name != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have the necessary permissions",
        )
    return current_user

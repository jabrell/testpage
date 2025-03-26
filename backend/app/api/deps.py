from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select

from app.core.config import settings
from app.core.db import engine
from app.core.exceptions import InvalidTokenError
from app.core.security import decode_access_token
from app.models import TokenPayload, User
from app.schema_manager import SchemaManager


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]


def get_schema_manager() -> Generator[SchemaManager, None, None]:
    manager = SchemaManager()
    yield manager


SchemaManagerDep = Annotated[SchemaManager, Depends(get_schema_manager)]


reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/user/login")
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = decode_access_token(token)
        token_data = TokenPayload(**payload)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Token expired or invalid"
        ) from None
    except Exception:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        ) from None
    q = select(User).where(User.id == token_data.sub)
    user = session.exec(q).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def is_admin_user(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have the necessary permissions",
        )
    return current_user

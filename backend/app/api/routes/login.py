from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.crud.user import authenticate_user
from app.api.deps import SessionDep
from app.core.exceptions import InvalidPassword, UserNotFound
from app.core.security import create_access_token
from app.models import Token

router = APIRouter(prefix="/login", tags=["login"])


@router.post(
    "/access_token",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Incorrect username or password"}
    },
)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
) -> Token:
    """Get JWT access token for a user."""
    try:
        # TODO add logging
        _ = authenticate_user(
            username=form_data.username, password=form_data.password, session=session
        )
    except (UserNotFound, InvalidPassword):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None
    token = create_access_token(form_data.username)
    return Token(access_token=token, token_type="bearer")

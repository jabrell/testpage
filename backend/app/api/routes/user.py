from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select

from app.api.deps import SessionDep, is_admin_user
from app.core.exceptions import InvalidPassword, UserNotFound
from app.core.security import authenticate_user, create_access_token, hash_password
from app.models.security import Token
from app.models.user import User, UserCreate, UserGroup, UserPublic

router = APIRouter(prefix="/user", tags=["user"])


@router.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_409_CONFLICT: {"description": "User already exists"},
        status.HTTP_201_CREATED: {"description": "User created"},
    },
    dependencies=[Depends(is_admin_user)],
)
async def register_user(user: UserCreate, session: SessionDep) -> UserPublic:
    """Register a new user given the name, email, and password in the standard
    user group."""
    # ensure that no user with the same name or email exists
    # TODO add logging
    res = session.exec(select(User).filter(User.username == user.username))
    if res.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with the same name already exists",
        )
    res = session.exec(select(User).filter(User.email == user.email))
    if res.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with the same email already exists",
        )
    user.password = hash_password(user.password)
    db_user = User(**user.model_dump())
    # get user group and assign it to the user
    usergroup_id = session.exec(
        select(UserGroup.id).filter(UserGroup.name == "standard")
    ).first()
    if not usergroup_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User group not found"
        )
    db_user.usergroup_id = usergroup_id
    try:
        session.add(db_user)
        session.commit()
    except Exception:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error while creating user",
        )
    return UserPublic(username=user.username, email=user.email)


@router.post(
    "/login",
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
        _ = authenticate_user(form_data.username, form_data.password, session)
    except (UserNotFound, InvalidPassword):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(form_data.username)
    return Token(access_token=token, token_type="bearer")


# TODO that should be secured
# @router.post("/delete")
# async def delete_user(
#     form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
#     session: SessionDep,
# ) -> UserPublic:
#     user = get_user(form_data.username, session)
#     if not user or not verify_password(form_data.password, user.password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     pub_user = user.get_public()
#     session.delete(user)
#     session.commit()
#     return pub_user

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.api.deps import SessionDep
from app.core.security import hash_password, verify_password
from app.models.user import Token, User, UserCreate, UserPublic

router = APIRouter(prefix="/user", tags=["user"])


def get_user(username: str, session: Session) -> User:
    """Get user by username or password

    Args:
        username (str): username of the user
        session (Session): db session object

    Returns:
        User: user object if found, None otherwise
    """
    # try to get the user by username
    res = session.exec(select(User).filter(User.username == username)).first()
    # if not found, try to get the user by email
    if not res:
        res = session.exec(select(User).filter(User.email == username)).first()
    return res


@router.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_409_CONFLICT: {"description": "User already exists"},
        status.HTTP_201_CREATED: {"description": "User created"},
    },
)
async def register_user(user: UserCreate, session: SessionDep) -> UserPublic:
    """Register a new user given the name, email, and password"""
    # ensure that no user with the same name or email exists
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

    session.add(db_user)
    session.commit()
    return UserPublic(username=user.username, email=user.email)


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
) -> Token:
    user = get_user(form_data.username, session)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token="token", token_type="bearer")
    # user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    # if not user:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Incorrect username or password",
    #         headers={"WWW-Authenticate": "Bearer"},
    #     )
    # access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # access_token = create_access_token(
    #     data={"sub": user.username}, expires_delta=access_token_expires
    # )
    # return Token(access_token=access_token, token_type="bearer")


@router.post("/delete")
async def delete_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
) -> UserPublic:
    user = get_user(form_data.username, session)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    pub_user = user.get_public()
    session.delete(user)
    session.commit()
    return pub_user

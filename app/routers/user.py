from fastapi import APIRouter, Depends, HTTPException, status
from passlib.hash import pbkdf2_sha256
from sqlmodel import Session, select

from app.database_access import get_db_session
from app.models.user import User, UserPublic

router = APIRouter(prefix="/user", tags=["user"])


def hash_password(password: str) -> str:
    return pbkdf2_sha256.hash(password)


def verify_password(password: str, hash: str) -> bool:
    return pbkdf2_sha256.verify(password, hash)


@router.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_409_CONFLICT: {"description": "User already exists"},
        status.HTTP_201_CREATED: {"description": "User created"},
    },
)
async def register_user(
    user: User, session: Session = Depends(get_db_session)
) -> UserPublic:
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
    session.add(user)
    session.commit()
    return UserPublic(username=user.username, email=user.email)


@router.post("/token")
async def get_token():
    pass

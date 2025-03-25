from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select

from app.api.crud.user import create_user, delete_user, get_user
from app.api.deps import SessionDep, is_admin_user
from app.models.user import UserCreate, UserGroup, UserPublic

router = APIRouter(prefix="/user", tags=["user"])


@router.post(
    "/create",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_409_CONFLICT: {"description": "User already exists"},
        status.HTTP_404_NOT_FOUND: {"description": "User group not found"},
        status.HTTP_201_CREATED: {"description": "User created"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Error while creating user"
        },
    },
    dependencies=[Depends(is_admin_user)],
)
async def create_user_api(*, user: UserCreate, session: SessionDep) -> UserPublic:
    """Create a new user. Only admin users can create new users.

    Args:
        user (UserCreate): User data.
        session (SessionDep): Database session.

    Returns:
        UserPublic: User data.
    """
    # ensure that no user with the same name or email exists
    # check whether the user already exists
    # TODO should be enforced at the database level and error should be handled
    if get_user(username=user.username, session=session):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with the same name already exists",
        )
    if get_user(username=user.email, session=session):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with the same email already exists",
        )
    # check whether the user group exists
    usergroup_id = session.exec(
        select(UserGroup.id).where(UserGroup.name == user.usergroup_name)
    ).first()
    if not usergroup_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User group not found"
        )
    # create the user
    user = create_user(user=user, usergroup_id=usergroup_id, session=session)
    return user.get_public()


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "User not found"},
        status.HTTP_200_OK: {"description": "User deleted"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Error while deleting user"
        },
    },
    dependencies=[Depends(is_admin_user)],
)
async def delete_user_api(
    user_id: int,
    session: SessionDep,
) -> None:
    """Delete a user. Only admin users can delete users.

    Args:
        user_id(int): Identifier of the user
        session (SessionDep): Database session.
    """
    delete_user(user_id=user_id, session=session)

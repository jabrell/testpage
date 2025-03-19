from sqlmodel import Session, or_, select

from app.core.exceptions import InvalidPassword, UserNotFound
from app.core.security import hash_password, verify_password
from app.models.user import User, UserCreate, UserGroup


def get_user(*, username: str, session: Session) -> User | None:
    """Get user by username or email address.

    Args:
        username (str): username of the user or the mail address
        session (Session): db session object

    Returns:
        User: user object if found, None otherwise
    """
    # try to get the user by username
    res = session.exec(
        select(User).filter(or_(User.username == username, User.email == username))
    ).first()
    return res


def delete_user(*, user_id: int, session: Session) -> bool:
    """Delete a user by id.

    Args:
        user_id (int): User id.
        session (Session): Database session.

    Returns:
        bool: True if the user was deleted, False otherwise.
    """
    user = session.get(User, user_id)
    if not user:
        return False
    session.delete(user)
    session.commit()
    return True


def create_user(
    *, user: UserCreate, usergroup_id: int | None = None, session: Session
) -> User:
    """Create a new user.

    Args:
        user (UserCreate): User data.
        usergroup_id (int | None): User group id.
            If None, the user will be created with the user group given in the
            user object.
            Defaults to None.
        session (Session): Database session.

    Returns:
        User: User data.
    """
    user.password = hash_password(user.password)
    db_user = User(**user.model_dump())
    if not usergroup_id:
        usergroup_id = session.exec(
            select(UserGroup.id).where(db_user.usergroup_name == UserGroup.name)
        ).first()
        if not usergroup_id:
            raise ValueError("User group not found.")
    db_user.usergroup_id = usergroup_id
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def authenticate_user(*, username: str, password: str, session: Session) -> User:
    """Authenticate the user using password.

    Args:
        session (Session): The database session.
        username (str): The username to authenticate. Email works as well.
        password (str): The password to authenticate.

    Returns:
        User | None: The user object if authenticated, else None.

    Raises:
        UserNotFound: If the user is not found in the database.
        InvalidPassword: If the password is incorrect.
    """
    user = get_user(username=username, session=session)
    if not user:
        raise UserNotFound()
    if not verify_password(password, user.password):
        raise InvalidPassword(user.username)
    return user

from sqlmodel import Session, select

from app.models.user import User


def get_user(username: str, session: Session) -> User:
    """Get user by username or password

    Args:
        username (str): username of the user or the mail address
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

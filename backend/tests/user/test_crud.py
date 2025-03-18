import pytest
from sqlmodel import Session, select

from app.api.crud.user import authenticate_user, create_user, delete_user, get_user
from app.core.config import settings
from app.core.exceptions import InvalidPassword, UserNotFound
from app.models.user import UserCreate, UserGroup


def test_user_get(db: Session):
    user = get_user(username=settings.FIRST_SUPERUSER_MAIL, session=db)
    assert user.username == settings.FIRST_SUPERUSER
    assert user.email == settings.FIRST_SUPERUSER_MAIL


def test_create_user(db: Session):
    u_create = UserCreate(
        username="test_user",
        password="test_password",
        email="test@example.com",
    )
    usergroup_id = db.exec(
        select(UserGroup.id).filter(UserGroup.name == "standard")
    ).first()
    user = create_user(user=u_create, usergroup_id=usergroup_id, session=db)
    assert user.username == u_create.username
    assert user.email == u_create.email


def test_authenticate_user_w_name(db: Session):
    expected = get_user(username=settings.FIRST_SUPERUSER, session=db)
    user = authenticate_user(
        username=settings.FIRST_SUPERUSER,
        password=settings.FIRST_SUPERUSER_PASSWORD,
        session=db,
    )
    assert expected == user


def test_authenticate_user_w_mail(db: Session):
    expected = get_user(username=settings.FIRST_SUPERUSER, session=db)
    user = authenticate_user(
        username=settings.FIRST_SUPERUSER_MAIL,
        password=settings.FIRST_SUPERUSER_PASSWORD,
        session=db,
    )
    assert expected == user


def test_authenticate_user_not_found(db: Session):
    with pytest.raises(UserNotFound):
        authenticate_user(username="NoName", password="Chapman", session=db)


def test_authenticate_user_invalid(db: Session):
    with pytest.raises(InvalidPassword):
        authenticate_user(
            username=settings.FIRST_SUPERUSER, password="wrongpass", session=db
        )


def test_delete_user(db: Session):
    u_create = UserCreate(
        username="test_user",
        password="test_password",
        email="test@example.com",
    )
    user = create_user(user=u_create, session=db)
    assert user.username == u_create.username
    assert user.email == u_create.email
    assert delete_user(user_id=user.id, session=db)


def test_delete_user_does_not_exist(db: Session):
    assert not delete_user(user_id=12351234, session=db)

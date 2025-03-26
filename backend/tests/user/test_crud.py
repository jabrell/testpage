import pytest
from faker import Faker
from sqlmodel import Session, select

from app.api.crud.user import authenticate_user, create_user, delete_user, get_user
from app.core.config import settings
from app.core.exceptions import InvalidPassword, UserNotFound
from app.models.user import UserCreate, UserGroup

from ..conftest import admin_user_properties, standard_user_properties  # noqa

fake = Faker()


def test_user_get_by_mail(db: Session):
    user = get_user(username=admin_user_properties["email"], session=db)
    assert user.username == admin_user_properties["username"]
    assert user.email == admin_user_properties["email"]


def test_get_user_by_id(db: Session):
    user = get_user(user_id=admin_user_properties["id"], session=db)
    assert user.username == admin_user_properties["username"]
    assert user.email == admin_user_properties["email"]


def test_get_user_by_username(db: Session):
    user = get_user(username=admin_user_properties["username"], session=db)
    assert user.username == admin_user_properties["username"]
    assert user.email == admin_user_properties["email"]


def test_get_user_raises(db: Session):
    with pytest.raises(ValueError):
        get_user(session=db)


def test_create_user(db: Session):
    u_create = UserCreate(
        username=fake.user_name(),
        password=fake.password(),
        email=fake.email(),
    )
    usergroup_id = db.exec(
        select(UserGroup.id).filter(UserGroup.name == "standard")
    ).first()
    user = create_user(user=u_create, usergroup_id=usergroup_id, session=db)
    assert user.username == u_create.username
    assert user.email == u_create.email


def test_create_user_wrong_usergroup(db: Session):
    u_create = UserCreate(
        username=fake.user_name(),
        password=fake.password(),
        email=fake.email(),
        usergroup_name="wrong",
    )
    with pytest.raises(ValueError):
        create_user(user=u_create, session=db)


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
        username=fake.user_name(),
        password=fake.password(),
        email=fake.email(),
    )
    user = create_user(user=u_create, session=db)
    assert user.username == u_create.username
    assert user.email == u_create.email
    assert delete_user(user_id=user.id, session=db)


def test_delete_user_does_not_exist(db: Session):
    assert not delete_user(user_id=12351234, session=db)

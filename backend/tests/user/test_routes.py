import faker
from fastapi import status
from fastapi.testclient import TestClient

from app.api.routes.login import router as login_router
from app.api.routes.user import router as user_router
from app.core.config import settings
from app.main import app
from app.models import UserCreate

url_user = f"{settings.API_V1_STR}{user_router.prefix}"
url_login = f"{settings.API_V1_STR}{login_router.prefix}/access_token"
url_register = f"{url_user}/create"
client = TestClient(app)


def test_get_token():
    login = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    response = client.post(url_login, data=login)
    tokens = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in tokens
    assert tokens["access_token"]
    assert response.json()["token_type"] == "bearer"


def test_get_token_by_mail():
    login = {
        "username": settings.FIRST_SUPERUSER_MAIL,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    response = client.post(url_login, data=login)
    tokens = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in tokens
    assert tokens["access_token"]
    assert response.json()["token_type"] == "bearer"


def test_get_token_wrong_password():
    login = {
        "username": settings.FIRST_SUPERUSER,
        "password": "wrong_password",
    }
    response = client.post(url_login, data=login)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_user(admin_token_header: dict[str, str]):
    user = UserCreate(
        id=0,
        username=faker.Faker().user_name(),
        email=faker.Faker().email(),
        password=faker.Faker().password(),
    )
    response = client.post(
        url_register, json=user.model_dump(), headers=admin_token_header
    )
    assert response.status_code == status.HTTP_201_CREATED
    res = response.json()
    assert res == user.get_public().model_dump()


def test_create_user_unauthorized(standard_token_header: dict[str, str]):
    user = UserCreate(
        id=0,
        username=faker.Faker().user_name(),
        email=faker.Faker().email(),
        password=faker.Faker().password(),
    )
    response = client.post(
        url_register, json=user.model_dump(), headers=standard_token_header
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_user_notoken():
    user = UserCreate(
        id=0,
        username=faker.Faker().user_name(),
        email=faker.Faker().email(),
        password=faker.Faker().password(),
    )
    response = client.post(url_register, json=user.model_dump())
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_user_name_exists(admin_token_header: dict[str, str]):
    user = UserCreate(
        id=0,
        username=settings.FIRST_SUPERUSER,
        email=settings.FIRST_SUPERUSER_MAIL,
        password=settings.FIRST_SUPERUSER_PASSWORD,
    )
    response = client.post(
        url_register, json=user.model_dump(), headers=admin_token_header
    )
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "User with the same name already exists"


def test_register_user_email_exists(admin_token_header: dict[str, str]):
    user = UserCreate(
        id=0,
        username=faker.Faker().user_name(),
        email=settings.FIRST_SUPERUSER_MAIL,
        password=faker.Faker().password(),
    )
    response = client.post(
        url_register, json=user.model_dump(), headers=admin_token_header
    )
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "User with the same email already exists"


def test_create_user_group_not_found(admin_token_header: dict[str, str]):
    user = UserCreate(
        username=faker.Faker().user_name(),
        email=faker.Faker().email(),
        password=faker.Faker().password(),
        usergroup_name="not_existing",
    )
    response = client.post(
        url_register, json=user.model_dump(), headers=admin_token_header
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "User group not found"


def test_delete_user(admin_token_header: dict[str, str]):
    user = UserCreate(
        id=234,
        username=faker.Faker().user_name(),
        email=faker.Faker().email(),
        password=faker.Faker().password(),
    )
    user = client.post(
        f"{url_user}/create", json=user.model_dump(), headers=admin_token_header
    ).json()
    response = client.delete(
        f"{url_user}/{user['id']}",
        headers=admin_token_header,
    )
    assert response.status_code == status.HTTP_200_OK


def test_delete_user_does_not_exists(admin_token_header: dict[str, str]):
    response = client.delete(
        "{url_user}/9999",
        headers=admin_token_header,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Not Found"

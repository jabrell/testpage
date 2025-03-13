import faker
from fastapi import status
from fastapi.testclient import TestClient

from app.api.routes.user import router as user_router
from app.core.config import settings
from app.main import app
from app.models import UserCreate

url_user = f"{settings.API_V1_STR}{user_router.prefix}"
url_register = f"{url_user}/register"
url_login = f"{url_user}/login"
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


def test_register_user(admin_token_header: dict[str, str]):
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
    assert response.json() == user.get_public().model_dump()


def test_register_user_unauthorized(standard_token_header: dict[str, str]):
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


def test_register_user_notoken():
    user = UserCreate(
        id=0,
        username=faker.Faker().user_name(),
        email=faker.Faker().email(),
        password=faker.Faker().password(),
    )
    response = client.post(url_register, json=user.model_dump())
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_register_user_name_exists(admin_token_header: dict[str, str]):
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

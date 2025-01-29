import faker
from fastapi import status
from fastapi.testclient import TestClient

from app.api.routes.user import router as user_router
from app.core.config import settings
from app.main import app
from app.models import User

url_user = f"{settings.API_V1_STR}{user_router.prefix}"
client = TestClient(app)


def test_register_user():
    route_register = f"{url_user}/register"
    user = User(
        id=0,
        username=faker.Faker().user_name(),
        email=faker.Faker().email(),
        password=faker.Faker().password(),
    )
    user_pub = user.get_public()
    # create user
    response = client.post(route_register, json=user.model_dump())
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == user_pub.model_dump()

    # creating the same user again raises an error
    response = client.post(route_register, json=user.model_dump())
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "User with the same name already exists"

    # alter the name and submitting should also raise an error due to duplicated
    # mail
    user.username = faker.Faker().user_name()
    response = client.post(route_register, json=user.model_dump())
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "User with the same email already exists"


def test_get_token():
    route_register = f"{url_user}/register"
    route_token = f"{url_user}/token"
    user = user = User(
        id=1,
        username=faker.Faker().user_name(),
        email=faker.Faker().email(),
        password=faker.Faker().password(),
    )
    user_pub = user.get_public()

    # token with wrong username raises error
    response = client.post(
        route_token,
        data={"username": "im_a_wrong_user", "password": user.password},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # create user
    response = client.post(route_register, json=user.model_dump())
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == user_pub.model_dump()

    # get token with username and password
    response = client.post(
        route_token, data={"username": user.username, "password": user.password}
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert "token_type" in response.json()
    assert response.json()["token_type"] == "bearer"

    # get token with email and password
    response = client.post(
        route_token, data={"username": user.email, "password": user.password}
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert "token_type" in response.json()
    assert response.json()["token_type"] == "bearer"

    # get token with wrong password
    response = client.post(
        route_token,
        data={"username": user.username, "password": faker.Faker().password()},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Incorrect username or password"

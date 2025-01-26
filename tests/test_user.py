import faker
import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.models import User

client = TestClient(app)


@pytest.fixture(scope="module")
def user_list(nr_users: int = 5) -> list[User]:
    """
    Fixture to get a list of test users
    """

    return [
        User(
            id=i,
            username=faker.Faker().user_name(),
            email=faker.Faker().email(),
            password=faker.Faker().password(),
        )
        for i in range(nr_users)
    ]


def test_register_user(user_list: list[User], clear_users):
    user = user_list[0]
    user_pub = user.get_public()

    # create user
    response = client.post("/user/register", json=user.model_dump())
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == user_pub.model_dump()

    # creating the same user again raises an error
    response = client.post("/user/register", json=user.model_dump())
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "User with the same name already exists"

    # alter the name and submitting should also raise an error
    user.username = faker.Faker().user_name()
    response = client.post("/user/register", json=user.model_dump())
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["detail"] == "User with the same email already exists"

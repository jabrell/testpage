from fastapi import status
from fastapi.testclient import TestClient

from app.api.routes import utils_router
from app.core.config import settings
from app.main import app

url_utils = f"{settings.API_V1_STR}{utils_router.prefix}"

client = TestClient(app)


def test_is_healthy():
    response = client.get(url_utils + "/health-check")
    assert response.status_code == status.HTTP_200_OK

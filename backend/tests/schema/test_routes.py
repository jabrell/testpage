import json

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.api.routes.schema import router as schema_router
from app.core.config import settings
from app.main import app
from app.models import RawJsonSchema

from .settings import sweet_valid

client = TestClient(app)

url_schema = f"{settings.API_V1_STR}{schema_router.prefix}"


@pytest.fixture(scope="module")
def my_schema() -> bytes:
    return str(sweet_valid).encode("utf-8")


def test_create_schema(db: Session, my_schema: bytes) -> None:
    RawJsonSchema
    fn = "test.json"
    content = json.dumps(sweet_valid)
    fn_type = "application/json"
    files = {"file": (fn, my_schema, fn_type)}
    response = client.post(url_schema, files=files)
    print(url_schema)
    print(response.json())
    assert response.status_code == status.HTTP_201_CREATED

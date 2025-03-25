import json
from pathlib import Path

import pytest
import yaml
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.api.routes.schema import router as schema_router
from app.core.config import settings
from app.main import app
from app.models.schema.schema import RawJsonSchema

# from app.models import RawJsonSchema
from .settings import sweet_valid

client = TestClient(app)

tmp_path = Path("./tests/tmp/")

url_schema = f"{settings.API_V1_STR}{schema_router.prefix}"


@pytest.fixture(scope="module")
def my_schema() -> bytes:
    return str(sweet_valid).encode("utf-8")


@pytest.mark.parametrize("fn, fn_type", [("test.json", "json"), ("test.yaml", "yaml")])
def test_create_schema(db: Session, fn: str, fn_type: str) -> None:
    # RawJsonSchema
    fn_full = tmp_path / fn
    with open(fn_full, "w") as f:
        if fn_type == "json":
            json.dump(sweet_valid, f)
        elif fn_type == "yaml":
            yaml.dump(sweet_valid, f)

    with open(fn_full, "rb") as f:
        files = {"file": (str(fn_full), f)}
        response = client.post(url_schema, files=files)
    assert response.status_code == status.HTTP_201_CREATED
    res = RawJsonSchema(**response.json())
    expected = RawJsonSchema(
        id=res.id,
        description=sweet_valid["description"],
        name=sweet_valid["name"],
        jsonschema=sweet_valid,
    )
    assert res == expected
    # cleanup
    to_delete = db.get(RawJsonSchema, res.id)
    db.delete(to_delete)
    db.commit()
    fn_full.unlink()


def test_create_schema_wrong_file_type(db: Session, fn: str = "test.txt") -> None:
    # RawJsonSchema
    fn_full = tmp_path / fn
    with open(fn_full, "w") as f:
        json.dump(sweet_valid, f)

    with open(fn_full, "rb") as f:
        files = {"file": (str(fn_full), f)}
        response = client.post(url_schema, files=files)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    fn_full.unlink()


def test_create_schema_empty_file(db: Session, fn: str = "test.json") -> None:
    # RawJsonSchema
    fn_full = tmp_path / fn
    with open(fn_full, "w") as f:
        pass

    with open(fn_full, "rb") as f:
        files = {"file": (str(fn_full), f)}
        response = client.post(url_schema, files=files)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    fn_full.unlink()


def test_create_schema_invalid_schema(db: Session, fn: str = "test.json") -> None:
    # RawJsonSchema
    fn_full = tmp_path / fn
    with open(fn_full, "w") as f:
        json.dump({"name": "test", "description": "test"}, f)

    with open(fn_full, "rb") as f:
        files = {"file": (str(fn_full), f)}
        response = client.post(url_schema, files=files)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    fn_full.unlink()

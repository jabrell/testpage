import json
from pathlib import Path

import pytest
import yaml
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, text

from app.api.crud.schema import create_schema
from app.api.routes.schema import router as schema_router
from app.core.config import settings
from app.main import app
from app.models.schema.schema import TableSchema, TableSchemaPublic
from app.schema_manager import SchemaManager

# from app.models import RawJsonSchema
from .settings import sweet_valid

client = TestClient(app)

tmp_path = Path("./tests/tmp/")

url_schema = f"{settings.API_V1_STR}{schema_router.prefix}"


@pytest.mark.parametrize("fn, fn_type", [("test.json", "json"), ("test.yaml", "yaml")])
def test_create_schema(
    db: Session, fn: str, fn_type: str, admin_token_header: dict[str, str]
) -> None:
    # RawJsonSchema
    fn_full = tmp_path / fn
    with open(fn_full, "w") as f:
        if fn_type == "json":
            json.dump(sweet_valid, f)
        elif fn_type == "yaml":
            yaml.dump(sweet_valid, f)

    with open(fn_full, "rb") as f:
        files = {"file": (str(fn_full), f)}
        response = client.post(url_schema, files=files, headers=admin_token_header)
    assert response.status_code == status.HTTP_201_CREATED
    res = TableSchema(**response.json())
    expected = TableSchema(
        id=res.id,
        description=sweet_valid["description"],
        name=sweet_valid["name"],
        jsonschema=sweet_valid,
    )
    assert res == expected
    # cleanup
    to_delete = db.get(TableSchema, res.id)
    db.delete(to_delete)
    db.commit()
    fn_full.unlink()


def test_create_schema_wrong_file_type(
    admin_token_header: dict[str, str], fn: str = "test.txt"
) -> None:
    fn_full = tmp_path / fn
    with open(fn_full, "w") as f:
        json.dump(sweet_valid, f)

    with open(fn_full, "rb") as f:
        files = {"file": (str(fn_full), f)}
        response = client.post(url_schema, files=files, headers=admin_token_header)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    fn_full.unlink()


def test_create_schema_empty_file(
    admin_token_header: dict[str, str], fn: str = "test.json"
) -> None:
    # RawJsonSchema
    fn_full = tmp_path / fn
    with open(fn_full, "w") as f:
        pass

    with open(fn_full, "rb") as f:
        files = {"file": (str(fn_full), f)}
        response = client.post(url_schema, files=files, headers=admin_token_header)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    fn_full.unlink()


def test_create_schema_invalid_schema(
    admin_token_header: dict[str, str], fn: str = "test.json"
) -> None:
    # RawJsonSchema
    fn_full = tmp_path / fn
    with open(fn_full, "w") as f:
        json.dump({"name": "test", "description": "test"}, f)

    with open(fn_full, "rb") as f:
        files = {"file": (str(fn_full), f)}
        response = client.post(url_schema, files=files, headers=admin_token_header)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    fn_full.unlink()


def test_get_schema_by_id(
    db: Session,
    schema_manager: SchemaManager,
) -> None:
    # create a schema
    schema = create_schema(db=db, data=sweet_valid, schema_manager=schema_manager)

    response = client.get(f"{url_schema}/{schema.id}")
    assert response.status_code == status.HTTP_200_OK
    res = TableSchemaPublic(**response.json())
    assert res == schema.get_public()
    db.delete(schema)
    db.commit()


def test_get_schema_by_name(
    db: Session,
    schema_manager: SchemaManager,
) -> None:
    # create a schema
    schema = create_schema(db=db, data=sweet_valid, schema_manager=schema_manager)
    response = client.get(f"{url_schema}/{schema.name}")
    assert response.status_code == status.HTTP_200_OK
    res = TableSchemaPublic(**response.json())
    assert res == schema.get_public()
    db.delete(schema)
    db.commit()


def test_get_schema_not_found() -> None:
    response = client.get(f"{url_schema}/1")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    response = client.get(f"{url_schema}/test")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_schema_by_id(
    db: Session, schema_manager: SchemaManager, admin_token_header: dict[str, str]
) -> None:
    schema = create_schema(db=db, data=sweet_valid, schema_manager=schema_manager)
    schema_id = schema.id
    response = client.delete(f"{url_schema}/{schema.id}", headers=admin_token_header)
    assert response.status_code == status.HTTP_200_OK
    db.commit()
    assert not db.get(TableSchema, schema_id)


def test_delete_schema_by_name(
    db: Session, schema_manager: SchemaManager, admin_token_header: dict[str, str]
) -> None:
    schema = create_schema(db=db, data=sweet_valid, schema_manager=schema_manager)
    schema_id = schema.id
    response = client.delete(f"{url_schema}/{schema.name}", headers=admin_token_header)
    assert response.status_code == status.HTTP_200_OK
    db.commit()
    assert not db.get(TableSchema, schema_id)


def test_delete_schema_not_found(admin_token_header: dict[str, str]) -> None:
    response = client.delete(f"{url_schema}/1", headers=admin_token_header)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    response = client.delete(f"{url_schema}/test", headers=admin_token_header)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_list_schemas(db: Session, schema_manager: SchemaManager) -> None:
    schema = create_schema(db=db, data=sweet_valid, schema_manager=schema_manager)
    response = client.get(url_schema)
    assert response.status_code == status.HTTP_200_OK
    print(response.json())
    print(schema.get_public())
    assert response.json() == [schema.get_public().model_dump()]
    db.delete(schema)
    db.commit()


def test_toggle_schema(
    db: Session, schema_manager: SchemaManager, admin_token_header: dict[str, str]
) -> None:
    schema = create_schema(db=db, data=sweet_valid, schema_manager=schema_manager)
    db.refresh(schema)
    assert not db.get(TableSchema, schema.id).is_active

    # initially the schema is in-active so toggeling renders it active
    response = client.post(
        f"{url_schema}/{schema.id}/toggle", headers=admin_token_header
    )
    assert response.status_code == status.HTTP_200_OK
    db.refresh(schema)
    assert db.get(TableSchema, schema.id).is_active

    response = client.post(
        f"{url_schema}/{schema.id}/toggle", headers=admin_token_header
    )
    assert response.status_code == status.HTTP_200_OK
    db.refresh(schema)
    assert not db.get(TableSchema, schema.id).is_active

    response = client.post(f"{url_schema}/1234234/toggle", headers=admin_token_header)
    assert response.status_code == status.HTTP_404_NOT_FOUND

    db.delete(schema)
    db.commit()


def test_create_table_from_schema2(
    db: Session, schema_manager: SchemaManager, admin_token_header
) -> None:
    # create a schema
    schema = create_schema(db=db, data=sweet_valid, schema_manager=schema_manager)
    response = client.post(
        f"{url_schema}/{schema.id}/create_table",
        headers=admin_token_header,
    )
    assert response.status_code == status.HTTP_201_CREATED

    # posting the same schema again should raise an error
    response = client.post(
        f"{url_schema}/{schema.id}/create_table",
        headers=admin_token_header,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    # posting with non-existing schema id should raise an error
    response = client.post(
        f"{url_schema}/1234234/create_table",
        headers=admin_token_header,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

    db.exec(text(f"DROP TABLE {sweet_valid['name']}"))
    db.delete(schema)
    db.commit()

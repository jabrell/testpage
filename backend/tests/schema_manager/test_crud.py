import pytest
from sqlalchemy.orm import Session

from app.api.crud.schema import create_schema, read_schema
from app.schema_manager import SchemaManager

from .settings import sweet_valid


@pytest.fixture(scope="module")
def data() -> bytes:
    return str(sweet_valid).encode("utf-8")


@pytest.fixture(scope="module")
def schema_manager() -> SchemaManager:
    return SchemaManager()


def test_create_schema(db: Session, data: bytes, schema_manager: SchemaManager) -> None:
    schema = create_schema(db=db, data=data, schema_manager=schema_manager)
    assert schema.name == "test"
    assert schema.description == "test"
    assert schema.jsonschema == sweet_valid
    assert not schema.is_active


def test_create_schema_raise(
    db: Session, data: bytes, schema_manager: SchemaManager
) -> None:
    create_schema(db=db, data=data, schema_manager=schema_manager)
    with pytest.raises(ValueError):
        create_schema(db=db, data=data, schema_manager=schema_manager)


@pytest.mark.skip
def test_read_schema_by_id(
    data: bytes, db: Session, schema_manager: SchemaManager
) -> None:
    inserted = create_schema(db=db, data=data, schema_manager=schema_manager)
    schema = read_schema(db=db, schema_id=inserted.id)
    assert schema == inserted

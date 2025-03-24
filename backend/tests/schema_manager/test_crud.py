import pytest
import yaml
from sqlalchemy.orm import Session

from app.api.crud.schema import create_schema
from app.schema_manager import SchemaManager

from .settings import sweet_valid


def test_create_schema(db: Session) -> None:
    data = str(sweet_valid).encode("utf-8")
    content_str = data.decode("utf-8")
    t = yaml.safe_load(content_str)
    print(t)
    schema_manger = SchemaManager()
    schema = create_schema(db=db, data=data, schema_manager=schema_manger)
    assert schema.name == "test"
    assert schema.description == "test"
    assert schema.jsonschema == sweet_valid
    assert not schema.is_active


def test_create_schema_raise(db: Session) -> None:
    data = str(sweet_valid).encode("utf-8")
    content_str = data.decode("utf-8")
    t = yaml.safe_load(content_str)
    print(t)
    schema_manger = SchemaManager()
    with pytest.raises(ValueError):
        create_schema(db=db, data=data, schema_manager=schema_manger)

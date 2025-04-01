import pytest
from sqlalchemy import Integer

from app.schema_manager import SchemaManager

from .settings import sweet_valid


def test_column_from_field_no_constraint():
    field = {"name": "id", "type": "integer"}
    db_types = {"integer": Integer}

    column = SchemaManager._field_to_columns(field=field, db_types=db_types)
    assert column.name == field["name"]
    assert isinstance(column.type, db_types[field["type"]])


def test_column_from_field_no_constraint_wrong_type():
    field = {"name": "id", "type": "integer"}

    with pytest.raises(ValueError):
        SchemaManager._field_to_columns(field=field, db_types={})


@pytest.mark.parametrize("dialect", ["sqlite", "postgres"])
def test_model_from_schema(dialect):
    schema = sweet_valid
    my_manager = SchemaManager()

    table = my_manager.model_from_schema(
        schema, validate_schema=True, db_dialect=dialect
    )

    assert table["name"] == schema["name"]
    assert len(table["columns"]) == len(schema["fields"])
    for field in schema["fields"]:
        assert field["name"] in [col.name for col in table["columns"]]


@pytest.mark.parametrize("dialect", ["sqlite", "postgres"])
def test_model_from_schema_with_id(dialect):
    schema = sweet_valid
    my_manager = SchemaManager()

    table = my_manager.model_from_schema(
        schema, validate_schema=True, db_dialect=dialect, create_id_column="id_"
    )

    assert table["name"] == schema["name"]
    assert len(table["columns"]) == len(schema["fields"]) + 1
    for field in schema["fields"]:
        assert field["name"] in [col.name for col in table["columns"]]
    assert table["columns"][0].name == "id_"


def test_model_from_schema_raise_wrong_dialect():
    schema = sweet_valid
    my_manager = SchemaManager()

    with pytest.raises(ValueError):
        my_manager.model_from_schema(
            schema, validate_schema=True, db_dialect="wrong_dialect"
        )

    with pytest.raises(ValueError):
        my_manager.model_from_schema(
            schema, validate_schema=False, db_dialect="wrong_dialect"
        )

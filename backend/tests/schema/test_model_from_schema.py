from copy import deepcopy

import pytest
from sqlalchemy import ForeignKeyConstraint, Integer

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


@pytest.mark.parametrize("dialect", ["sqlite", "postgresql"])
def test_model_from_schema(dialect):
    schema = deepcopy(sweet_valid)
    del schema["primaryKey"]
    my_manager = SchemaManager()

    table = my_manager.model_from_schema(
        schema, validate_schema=True, db_dialect=dialect
    )

    assert table["name"] == schema["name"]
    assert len(table["columns"]) == len(schema["fields"])
    for field in schema["fields"]:
        assert field["name"] in [col.name for col in table["columns"]]


@pytest.mark.parametrize("dialect", ["sqlite", "postgresql"])
def test_model_from_schema_with_id(dialect):
    schema = deepcopy(sweet_valid)
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
    schema = deepcopy(sweet_valid)
    my_manager = SchemaManager()

    with pytest.raises(ValueError):
        my_manager.model_from_schema(
            schema, validate_schema=True, db_dialect="wrong_dialect"
        )

    with pytest.raises(ValueError):
        my_manager.model_from_schema(
            schema, validate_schema=False, db_dialect="wrong_dialect"
        )


@pytest.mark.parametrize("dialect", ["sqlite", "postgresql"])
def test_model_from_schema_with_primary_key(dialect):
    schema = deepcopy(sweet_valid)
    key_cols = ["id", "name"]
    schema["primaryKey"] = key_cols
    my_manager = SchemaManager()
    table = my_manager.model_from_schema(
        schema, validate_schema=True, db_dialect=dialect, create_id_column="sweet_id"
    )
    # check the primary key constraints, i.e., each column in the primary key is
    # not nullable and and one UniqueContraint enforces that the combination of
    # the columns is unique
    for col in table["columns"]:
        if col.name in key_cols:
            assert not col.nullable
    assert (
        len(
            [
                c
                for c in table["constraints"]
                if c.name == f"unique_{'_'.join(key_cols)}"
            ]
        )
        == 1
    )


@pytest.mark.parametrize("dialect", ["sqlite", "postgresql"])
def test_model_from_schema_with_primary_key_scalar(dialect):
    schema = deepcopy(sweet_valid)
    col_key = "id"
    schema["primaryKey"] = col_key
    my_manager = SchemaManager()
    table = my_manager.model_from_schema(
        schema, validate_schema=True, db_dialect=dialect, create_id_column="sweet_id"
    )
    # check the primary key constraints, i.e., each column in the primary key is
    # not nullable and and one UniqueConstraint enforces that the combination of
    # the columns is unique
    for col in table["columns"]:
        if col_key == col.name:
            assert not col.nullable
    assert len([c for c in table["constraints"] if c.name == f"unique_{col_key}"]) == 1


@pytest.mark.parametrize("dialect", ["sqlite", "postgresql"])
def test_model_from_schema_with_foreign_key_list(dialect):
    schema = deepcopy(sweet_valid)
    schema["foreignKeys"] = [
        {
            "fields": ["id"],
            "reference": {"resource": "other_table", "fields": ["id"]},
        }
    ]
    my_manager = SchemaManager()
    table = my_manager.model_from_schema(
        schema, validate_schema=True, db_dialect=dialect, create_id_column="id_"
    )

    assert table["name"] == schema["name"]
    assert len(table["columns"]) == len(schema["fields"]) + 1
    for field in schema["fields"]:
        assert field["name"] in [col.name for col in table["columns"]]
    assert table["columns"][0].name == "id_"
    assert len(table["constraints"]) == 2
    assert (
        len([c for c in table["constraints"] if isinstance(c, ForeignKeyConstraint)])
        == 1
    )


@pytest.mark.parametrize("dialect", ["sqlite", "postgresql"])
def test_model_from_schema_with_foreign_key_scalar(dialect):
    schema = deepcopy(sweet_valid)
    schema["foreignKeys"] = [
        {
            "fields": "id",
            "reference": {"resource": "other_table", "fields": "id"},
        }
    ]
    my_manager = SchemaManager()
    table = my_manager.model_from_schema(
        schema, validate_schema=True, db_dialect=dialect, create_id_column="id_"
    )

    assert table["name"] == schema["name"]
    assert len(table["columns"]) == len(schema["fields"]) + 1
    for field in schema["fields"]:
        assert field["name"] in [col.name for col in table["columns"]]
    assert table["columns"][0].name == "id_"
    assert len(table["constraints"]) == 2
    assert (
        len([c for c in table["constraints"] if isinstance(c, ForeignKeyConstraint)])
        == 1
    )

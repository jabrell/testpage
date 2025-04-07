from copy import deepcopy
from unittest.mock import patch

import pytest
from sqlmodel import Session, SQLModel, inspect, text

from app.api.crud.schema import (
    create_schema,
    create_table_from_schema,
    delete_schema,
    read_schema,
    toggle_schema,
)
from app.models.schema import TableSchema
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
    assert schema.name == sweet_valid["name"]
    assert schema.description == sweet_valid["description"]
    assert schema.jsonschema == sweet_valid
    assert not schema.is_active
    db.delete(schema)
    db.commit()


def test_create_schema_raise(
    db: Session, data: bytes, schema_manager: SchemaManager
) -> None:
    schema = create_schema(db=db, data=data, schema_manager=schema_manager)
    with pytest.raises(ValueError):
        create_schema(db=db, data=data, schema_manager=schema_manager)
    db.delete(schema)
    db.commit()


def test_read_schema_by_id(
    data: bytes, db: Session, schema_manager: SchemaManager
) -> None:
    inserted = create_schema(db=db, data=data, schema_manager=schema_manager)
    schema = read_schema(db=db, schema_id=inserted.id)
    assert schema == inserted
    db.delete(schema)
    db.commit()


def test_read_schema_by_name(
    data: bytes, db: Session, schema_manager: SchemaManager
) -> None:
    inserted = create_schema(db=db, data=data, schema_manager=schema_manager)
    schema = read_schema(db=db, schema_name=inserted.name)
    assert schema == inserted
    to_delete = db.get(TableSchema, schema.id)
    db.delete(to_delete)
    db.commit()


def test_read_schema_raise(db: Session) -> None:
    with pytest.raises(ValueError):
        read_schema(db=db, schema_id=1)
    with pytest.raises(ValueError):
        read_schema(db=db, schema_name="test2323")
    with pytest.raises(ValueError):
        read_schema(db=db)
    with pytest.raises(ValueError):
        read_schema(db=db, schema_id=1, schema_name="test")


def test_delete_schema_by_id(
    data: bytes, db: Session, schema_manager: SchemaManager
) -> None:
    schema = create_schema(db=db, data=data, schema_manager=schema_manager)
    assert delete_schema(db=db, schema_id=schema.id)
    assert not db.get(TableSchema, schema.id)


def test_delete_schema_by_name(
    data: bytes, db: Session, schema_manager: SchemaManager
) -> None:
    schema = create_schema(db=db, data=data, schema_manager=schema_manager)
    assert delete_schema(db=db, schema_name=schema.name)
    assert not db.get(TableSchema, schema.id)


def test_delete_schema_false(db: Session) -> None:
    assert not delete_schema(db=db, schema_name="wrong name")


def test_toggle_schema_by_id(
    db: Session, data: bytes, schema_manager: SchemaManager
) -> None:
    schema = create_schema(db=db, data=data, schema_manager=schema_manager)
    assert not schema.is_active
    assert toggle_schema(db=db, schema_id=schema.id)
    schema = read_schema(db=db, schema_id=schema.id)
    assert schema.is_active
    assert toggle_schema(db=db, schema_id=schema.id)
    schema = read_schema(db=db, schema_id=schema.id)
    assert not schema.is_active
    db.delete(schema)
    db.commit()


def test_toggle_schema_by_name(
    db: Session, data: bytes, schema_manager: SchemaManager
) -> None:
    schema = create_schema(db=db, data=data, schema_manager=schema_manager)
    assert not schema.is_active
    assert toggle_schema(db=db, schema_name=schema.name)
    schema = read_schema(db=db, schema_name=schema.name)
    assert schema.is_active
    assert toggle_schema(db=db, schema_name=schema.name)
    schema = read_schema(db=db, schema_name=schema.name)
    assert not schema.is_active
    db.delete(schema)
    db.commit()


def test_toggle_schema_raises(db: Session) -> None:
    assert not toggle_schema(db=db, schema_name="wrong name")


def test_create_table_from_schema(db: Session, schema_manager: SchemaManager) -> None:
    return_value = TableSchema(
        name=sweet_valid["name"],
        description=sweet_valid["description"],
        jsonschema=sweet_valid,
    )
    with patch("app.api.crud.schema.read_schema", return_value=return_value):
        create_table_from_schema(db=db, schema_id=1, schema_manager=schema_manager)
        assert sweet_valid["name"] in inspect(db.bind).get_table_names()

        # running again should not raise an error as the table already exists
        with pytest.raises(ValueError):
            create_table_from_schema(db=db, schema_id=1, schema_manager=schema_manager)

    # delete the table after the test
    table_name = sweet_valid["name"]
    metadata = SQLModel.metadata
    metadata.reflect(bind=db.bind)
    tab = metadata.tables[table_name]
    tab.drop(db.bind)
    metadata.reflect(bind=db.bind)
    db.commit()


def test_create_table_from_schema_fkey(
    db: Session, schema_manager: SchemaManager
) -> None:
    # create the foreign table in the database
    db.exec(text("CREATE TABLE other_table (id INTEGER PRIMARY KEY)"))
    db.commit()

    # create the foreign key in the schema
    my_schema = deepcopy(sweet_valid)
    my_schema["foreignKeys"] = [
        {
            "fields": ["id"],
            "reference": {"resource": "other_table", "fields": ["id"]},
        }
    ]

    return_value = TableSchema(
        name=my_schema["name"],
        description=my_schema["description"],
        jsonschema=my_schema,
    )
    with patch("app.api.crud.schema.read_schema", return_value=return_value):
        create_table_from_schema(db=db, schema_id=1, schema_manager=schema_manager)
        assert sweet_valid["name"] in inspect(db.bind).get_table_names()

        # # running again should not raise an error as the table already exists
        # with pytest.raises(ValueError):
        #     create_table_from_schema(db=db, schema_id=1, schema_manager=schema_manager) # noqa

    # delete the table after the test
    table_name = sweet_valid["name"]
    metadata = SQLModel.metadata
    metadata.reflect(bind=db.bind)
    tab = metadata.tables[table_name]
    tab2 = metadata.tables["other_table"]
    tab.drop(db.bind)
    tab2.drop(db.bind)
    db.commit()


def test_create_table_from_schema_fkey_raises(
    db: Session, schema_manager: SchemaManager
) -> None:
    # create the foreign key in the schema
    my_schema = deepcopy(sweet_valid)
    my_schema["foreignKeys"] = [
        {
            "fields": ["id"],
            "reference": {"resource": "other_table", "fields": ["id"]},
        }
    ]

    return_value = TableSchema(
        name=my_schema["name"],
        description=my_schema["description"],
        jsonschema=my_schema,
    )
    # as the foreign table does not exist, the test should raise an error
    with patch("app.api.crud.schema.read_schema", return_value=return_value):
        with pytest.raises(ValueError):
            create_table_from_schema(db=db, schema_id=1, schema_manager=schema_manager)


def test_create_table_self_reference(
    db: Session, schema_manager: SchemaManager
) -> None:
    # a schema with a self-reference foreign key
    my_schema = {
        "name": "class_location",
        "title": "Country",
        "description": (
            "Hierarchical classification for locations. This classification allows for "
            "countries and sub-regions. It uses the ISO 3166-1 alpha-2 together with "
            "ISO 3166-2 for sub-regions."
        ),
        "primaryKey": "id",
        "foreignKeys": [
            {
                "fields": "id_parent",
                "reference": {"resource": "class_location", "fields": "id"},
            }
        ],
        "fields": [
            {
                "name": "id",
                "type": "string",
                "title": "Country code",
                "description": "2 digit iso country code",
                "constraints": {"required": True, "maxLength": 5},
            },
            {
                "name": "level",
                "type": "integer",
                "title": "Hierarchical level",
                "description": "The level within the classification hierarchy",
                "constraints": {"required": True, "minimum": 0},
            },
            {
                "name": "id_parent",
                "type": "string",
                "title": "Link to parent",
                "description": "The unique identifier for the parent end-use demand type",  # noqa
                "constraints": {"maxLength": 5},
            },
            {
                "name": "label",
                "type": "string",
                "title": "Country",
                "description": "Full country name",
                "constraints": {"maxLength": 255},
            },
        ],
    }

    my_schema = {
        "name": "class_end_use_demand",
        "title": "Classification for end-use demand",
        "description": "Hierarchical classification of end-use demand types.",
        "primaryKey": "id",
        "foreignKeys": [
            {
                "fields": "id_parent",
                "reference": {"resource": "class_end_use_demand", "fields": "id"},
            }
        ],
        "fields": [
            {
                "name": "id",
                "type": "string",
                "title": "End-use demand type",
                "description": "The unique identifier for the end-use demand type",
                "constraints": {"required": True, "maxLength": 255},
            },
            {
                "name": "level",
                "type": "integer",
                "title": "Hierarchical level",
                "description": "The level within the classification hierarchy",
                "constraints": {"required": True, "minimum": 0},
            },
            {
                "name": "id_parent",
                "type": "string",
                "title": "Link to parent",
                "description": "The unique identifier for the parent end-use demand type",  # noqa
                "constraints": {"maxLength": 255},
            },
            {
                "name": "label",
                "type": "string",
                "title": "End-use demand type",
                "description": "The label for the end-use demand type",
                "constraints": {"maxLength": 255},
            },
        ],
    }

    return_value = TableSchema(
        name=my_schema["name"],
        description=my_schema["description"],
        jsonschema=my_schema,
    )
    with patch("app.api.crud.schema.read_schema", return_value=return_value):
        create_table_from_schema(db=db, schema_id=1, schema_manager=schema_manager)
        assert my_schema["name"] in inspect(db.bind).get_table_names()

        # running again should not raise an error as the table already exists
        with pytest.raises(ValueError):
            create_table_from_schema(db=db, schema_id=1, schema_manager=schema_manager)

    # delete the table after the test
    table_name = my_schema["name"]
    metadata = SQLModel.metadata
    metadata.reflect(bind=db.bind)
    tab = metadata.tables[table_name]
    tab.drop(db.bind)
    db.commit()


def test_create_table_self_reference_in_a_row(
    db: Session, schema_manager: SchemaManager
) -> None:
    # a schema with a self-reference foreign key
    my_schema_1 = {
        "name": "class_location",
        "title": "Country",
        "description": (
            "Hierarchical classification for locations. This classification allows for "
            "countries and sub-regions. It uses the ISO 3166-1 alpha-2 together with "
            "ISO 3166-2 for sub-regions."
        ),
        "primaryKey": "id",
        "foreignKeys": [
            {
                "fields": "id_parent",
                "reference": {"resource": "class_location", "fields": "id"},
            }
        ],
        "fields": [
            {
                "name": "id",
                "type": "string",
                "title": "Country code",
                "description": "2 digit iso country code",
                "constraints": {"required": True, "maxLength": 5},
            },
            {
                "name": "level",
                "type": "integer",
                "title": "Hierarchical level",
                "description": "The level within the classification hierarchy",
                "constraints": {"required": True, "minimum": 0},
            },
            {
                "name": "id_parent",
                "type": "string",
                "title": "Link to parent",
                "description": "The unique identifier for the parent end-use demand type",  # noqa
                "constraints": {"maxLength": 5},
            },
            {
                "name": "label",
                "type": "string",
                "title": "Country",
                "description": "Full country name",
                "constraints": {"maxLength": 255},
            },
        ],
    }

    my_schema_2 = {
        "name": "class_end_use_demand",
        "title": "Classification for end-use demand",
        "description": "Hierarchical classification of end-use demand types.",
        "primaryKey": "id",
        "foreignKeys": [
            {
                "fields": "id_parent",
                "reference": {"resource": "class_end_use_demand", "fields": "id"},
            }
        ],
        "fields": [
            {
                "name": "id",
                "type": "string",
                "title": "End-use demand type",
                "description": "The unique identifier for the end-use demand type",
                "constraints": {"required": True, "maxLength": 255},
            },
            {
                "name": "level",
                "type": "integer",
                "title": "Hierarchical level",
                "description": "The level within the classification hierarchy",
                "constraints": {"required": True, "minimum": 0},
            },
            {
                "name": "id_parent",
                "type": "string",
                "title": "Link to parent",
                "description": "The unique identifier for the parent end-use demand type",  # noqa
                "constraints": {"maxLength": 255},
            },
            {
                "name": "label",
                "type": "string",
                "title": "End-use demand type",
                "description": "The label for the end-use demand type",
                "constraints": {"maxLength": 255},
            },
        ],
    }

    return_value_1 = TableSchema(
        name=my_schema_1["name"],
        description=my_schema_1["description"],
        jsonschema=my_schema_1,
    )
    with patch("app.api.crud.schema.read_schema", return_value=return_value_1):
        create_table_from_schema(db=db, schema_id=1, schema_manager=schema_manager)
        assert my_schema_1["name"] in inspect(db.bind).get_table_names()

    return_value_2 = TableSchema(
        name=my_schema_2["name"],
        description=my_schema_2["description"],
        jsonschema=my_schema_2,
    )
    with patch("app.api.crud.schema.read_schema", return_value=return_value_2):
        create_table_from_schema(db=db, schema_id=1, schema_manager=schema_manager)
        assert my_schema_2["name"] in inspect(db.bind).get_table_names()

    # delete the table after the test
    table_name_1 = my_schema_1["name"]
    table_name_2 = my_schema_2["name"]
    metadata = SQLModel.metadata
    metadata.reflect(bind=db.bind)
    tab = metadata.tables[table_name_1]
    tab.drop(db.bind)
    tab = metadata.tables[table_name_2]
    tab.drop(db.bind)
    db.commit()


def test_full_foreign_key(db: Session, schema_manager: SchemaManager):
    """Test full example of schemas with foreign keys"""
    schema1 = {
        "name": "class_location",
        "title": "Country",
        "description": (
            "Hierarchical classification for locations. This classification allows for "
            "countries and sub-regions. It uses the ISO 3166-1 alpha-2 together with "
            "ISO 3166-2 for sub-regions."
        ),
        "primaryKey": "id",
        "foreignKeys": [
            {
                "fields": "id_parent",
                "reference": {"resource": "class_location", "fields": "id"},
            }
        ],
        "fields": [
            {
                "name": "id",
                "type": "string",
                "title": "Country code",
                "description": "2 digit iso country code",
                "constraints": {"required": True, "maxLength": 5},
            },
            {
                "name": "level",
                "type": "integer",
                "title": "Hierarchical level",
                "description": "The level within the classification hierarchy",
                "constraints": {"required": True, "minimum": 0},
            },
            {
                "name": "id_parent",
                "type": "string",
                "title": "Link to parent",
                "description": "The unique identifier for the parent end-use demand type",  # noqa
                "constraints": {"maxLength": 5},
            },
            {
                "name": "label",
                "type": "string",
                "title": "Country",
                "description": "Full country name",
                "constraints": {"maxLength": 255},
            },
        ],
    }

    schema2 = {
        "name": "class_end_use_demand",
        "title": "Classification for end-use demand",
        "description": "Hierarchical classification of end-use demand types.",
        "primaryKey": "id",
        "foreignKeys": [
            {
                "fields": "id_parent",
                "reference": {"resource": "class_end_use_demand", "fields": "id"},
            }
        ],
        "fields": [
            {
                "name": "id",
                "type": "string",
                "title": "End-use demand type",
                "description": "The unique identifier for the end-use demand type",
                "constraints": {"required": True, "maxLength": 255},
            },
            {
                "name": "level",
                "type": "integer",
                "title": "Hierarchical level",
                "description": "The level within the classification hierarchy",
                "constraints": {"required": True, "minimum": 0},
            },
            {
                "name": "id_parent",
                "type": "string",
                "title": "Link to parent",
                "description": "The unique identifier for the parent end-use demand type",  # noqa
                "constraints": {"maxLength": 255},
            },
            {
                "name": "label",
                "type": "string",
                "title": "End-use demand type",
                "description": "The label for the end-use demand type",
                "constraints": {"maxLength": 255},
            },
        ],
    }

    schema3 = {
        "name": "end_use_demand_hourly",
        "title": "Hourly end-use demand",
        "description": "This table contains the hourly end-use demand data.",
        "valueField": {"field": "value", "unit": "MWh"},
        "timeFields": [{"field": "datetime", "frequency": "hourly"}],
        "locationFields": [{"field": "location", "locationType": "location"}],
        "tags": ["demand", "end-use", "transport", "heating"],
        "foreignKeys": [
            {
                "fields": "location",
                "reference": {"resource": "class_location", "fields": "id"},
            },
            {
                "fields": "demand_type_id",
                "reference": {"resource": "class_end_use_demand", "fields": "id"},
            },
        ],
        "fields": [
            {
                "name": "location",
                "type": "string",
                "title": "Location",
                "description": "Name of the location of the end-use demand",
                "constraints": {"required": True, "maxLength": 255},
            },
            {
                "name": "demand_type_id",
                "type": "string",
                "title": "Type of demand",
                "description": "Type of demand",
                "constraints": {"required": True, "maxLength": 255},
            },
            {
                "name": "datetime",
                "type": "datetime",
                "title": "Datetime",
                "description": "End of hour in UTC time",
                "constraints": {"required": True},
            },
            {
                "name": "value",
                "type": "number",
                "title": "End-use demand",
                "description": "Amount of end-use demand",
                "constraints": {"required": True, "minimum": 0},
            },
        ],
    }

    schemas = [schema1, schema2, schema3]

    for schema in schemas:
        return_value = TableSchema(
            name=schema["name"],
            description=schema["description"],
            jsonschema=schema,
        )
        with patch("app.api.crud.schema.read_schema", return_value=return_value):
            create_table_from_schema(db=db, schema_manager=schema_manager)
            assert schema["name"] in inspect(db.bind).get_table_names()

    # clean up
    for schema in schemas:
        table_name = schema["name"]
        metadata = SQLModel.metadata
        metadata.reflect(bind=db.bind)
        tab = metadata.tables[table_name]
        tab.drop(db.bind)
        db.commit()

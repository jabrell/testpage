import json
from copy import deepcopy
from pathlib import Path

import pytest
import yaml
from jsonschema.exceptions import ValidationError
from sqlmodel import Session

from app.schema_manager import SchemaManager

from .settings import fl_invalid, fl_valid, sweet_valid


def test_read_schema_json():
    content = {"key": "value"}
    fn = Path("tmp.json")
    with open(fn, "w") as f:
        json.dump(content, f)
    assert SchemaManager.read_schema_from_file(fn) == content
    Path(fn).unlink()


def test_read_schema_dict():
    content = {"key": "value"}
    assert SchemaManager.read_schema_from_file(content) == content


@pytest.mark.parametrize("ext", [".yaml", ".yml"])
def test_read_schema_yaml(ext: str):
    content = {"key": "value"}
    fn = Path(f"tmp.{ext}")
    with open(fn, "w") as f:
        yaml.dump(content, f)
    assert SchemaManager.read_schema_from_file(fn) == content
    fn.unlink()


def test_read_schema_bytes_json():
    json_bytes = b'{"key": "value"}'
    result = SchemaManager.read_schema_from_file(json_bytes)
    assert result == {"key": "value"}


def test_read_schema_bytes_yaml():
    yaml_bytes = b"key: value"
    result = SchemaManager.read_schema_from_file(yaml_bytes)
    assert result == {"key": "value"}


def test_read_schema_bytes_yaml_exception():
    json_bytes_invalid = b'{"key": "value}'
    yaml_bytes_invalid = b"key: value\nanother_key: [1, 2, 3"
    with pytest.raises(ValueError):
        SchemaManager.read_schema_from_file(yaml_bytes_invalid)
    with pytest.raises(ValueError):
        SchemaManager.read_schema_from_file(json_bytes_invalid)


def test_read_schema_invalid():
    fn = Path("tmp.txt")
    with open(fn, "w") as f:
        f.write("invalid")
    with pytest.raises(ValueError):
        SchemaManager.read_schema_from_file(fn)
    fn.unlink()
    # file not found
    with pytest.raises(FileNotFoundError):
        SchemaManager.read_schema_from_file(fn)


def test_validate_schema_from_dict():
    relation_manager = SchemaManager(metaschema_extensions=[])
    assert relation_manager.validate_schema(fl_valid) == fl_valid
    # invalid schema should raise a validation error
    with pytest.raises(ValidationError):
        relation_manager.validate_schema(fl_invalid)


def test_validate_schema_from_json(fn: str = "schema.json"):
    relation_manager = SchemaManager(metaschema_extensions=[])
    # write schema to json file
    my_file = Path(fn)
    with open(my_file, "w") as f:
        json.dump(fl_valid, f)
    assert relation_manager.validate_schema(my_file) == fl_valid
    my_file.unlink()
    # invalid schema should raise a validation error
    my_file = Path(fn)
    with open(my_file, "w") as f:
        json.dump(fl_invalid, f)
    with pytest.raises(ValidationError):
        relation_manager.validate_schema(my_file)
    my_file.unlink()


@pytest.mark.parametrize("fn", ["schema.yaml", "schema.yml"])
def test_validate_schema_from_yaml(fn: str):
    relation_manager = SchemaManager(metaschema_extensions=[])
    # write schema to json file
    my_file = Path(fn)
    with open(my_file, "w") as f:
        json.dump(fl_valid, f)
    assert relation_manager.validate_schema(my_file) == fl_valid
    my_file.unlink()
    # invalid schema should raise a validation error
    my_file = Path(fn)
    with open(my_file, "w") as f:
        json.dump(fl_invalid, f)
    with pytest.raises(ValidationError):
        relation_manager.validate_schema(my_file)
    my_file.unlink()


def test_sweet_schema_extensions():
    """Test extended metadata standard of SWEET"""
    invalid_schema = {
        # schema misses the "name" key which is mandatory in the SWEET standard
        # but not in the standard frictionless schema
        "fields": [
            {"name": "id", "type": "integer"},
            {"name": "name", "type": "string"},
        ],
    }
    man = SchemaManager(metaschema_extensions=[])
    sweet_man = SchemaManager()
    assert man.validate_schema(invalid_schema) == invalid_schema
    with pytest.raises(ValidationError):
        sweet_man.validate_schema(invalid_schema)


def test_sweet_extensions_name_format():
    """Test extended metadata standard of SWEET"""
    schema = deepcopy(sweet_valid)
    schema["name"] = "TEST"
    with pytest.raises(ValidationError):
        SchemaManager().validate_schema(schema)
    schema["name"] = "test!"
    with pytest.raises(ValidationError):
        SchemaManager().validate_schema(schema)
    schema["name"] = "test_test"
    assert SchemaManager().validate_schema(schema) == schema

    # name of format of field is also fixed to using lower cases and underscores
    schema["fields"][0]["name"] = "ID"
    with pytest.raises(ValidationError):
        SchemaManager().validate_schema(schema)


def test_sweet_extensions_no_additional_fields():
    """Test extended metadata standard of SWEET"""
    schema = deepcopy(sweet_valid)
    schema["additional"] = "field"
    with pytest.raises(ValidationError):
        SchemaManager().validate_schema(schema)


def test_sweet_extensions_primary_key():
    """Test extended metadata standard of SWEET"""
    schema = deepcopy(sweet_valid)
    my_manager = SchemaManager()
    # schema contains a valid primary key
    schema["primaryKey"] = "id"
    assert my_manager.validate_schema(schema) == schema
    # should also work with a list
    schema["primaryKey"] = ["id"]
    assert my_manager.validate_schema(schema) == schema


def test_sweet_extensions_primary_key_invalid():
    schema = deepcopy(sweet_valid)
    my_manager = SchemaManager()
    # schema contains an invalid primary key
    schema["primaryKey"] = "invalid"
    with pytest.raises(ValueError):
        my_manager.validate_schema(schema)
    # schema contains an invalid primary key
    schema["primaryKey"] = ["id", "invalid"]


def test_sweet_extensions_foreign_key(db: Session):
    schema = deepcopy(sweet_valid)
    my_manager = SchemaManager()
    # schema contains a valid foreign key‚
    schema["foreignKeys"] = [
        {
            "fields": ["id"],
            "reference": {"resource": "other_table", "fields": ["id"]},
        }
    ]
    assert my_manager.validate_schema(schema, db=db) == schema
    # also works with just a string
    schema["foreignKeys"] = [
        {
            "fields": "id",
            "reference": {"resource": "other_table", "fields": "id"},
        }
    ]
    assert my_manager.validate_schema(schema, db=db) == schema


def test_sweet_extensions_foreign_key_raises(db: Session):
    schema = deepcopy(sweet_valid)
    my_manager = SchemaManager()
    # schema foreign keys to not match references
    schema["foreignKeys"] = [
        {
            "fields": ["id"],
            "reference": {"resource": "other_table", "fields": ["id", "invalid"]},
        }
    ]
    with pytest.raises(ValueError):
        my_manager.validate_schema(schema, db=db)

    # foreign keys not in the table
    schema["foreignKeys"] = [
        {
            "fields": ["invalid"],
            "reference": {"resource": "other_table", "fields": ["id"]},
        }
    ]
    with pytest.raises(ValueError):
        my_manager.validate_schema(schema, db=db)

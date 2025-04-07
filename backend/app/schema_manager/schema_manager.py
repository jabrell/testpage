import json
from pathlib import Path
from typing import Any, Literal, cast

import jsonschema
import yaml  # type: ignore

# from sqlalchemy import Column, UniqueConstraint
from sqlmodel import Column, Constraint, ForeignKeyConstraint, UniqueConstraint

from .mappings import map_db_types

__all__ = ["SchemaManager"]

SchemaFileType = str | Path | dict[str, Any] | bytes
DbDialect = Literal["sqlite", "postgresql"]

BASE_SCHEMA = Path(__file__).parent / "meta_schemas" / "frictionlessv1.json"
SWEET_EXTENSIONS = [Path(__file__).parent / "meta_schemas" / "sweet_metastandard.yaml"]


class SchemaManager:
    """The SchemaManager class is responsible for managing the schemas used
    by the backend.

    Schemas define the structure of the data tables that are stored in the database.
    They are provided as json-schemas that can be yaml or json files or dictionary.
    Each schema has to comply with the meta-schema that defines the structure of
    schemas.

    The SchemaManager class is responsible for:
    - reading the schema files
    - ensuring that each schema complies with the meta-schema
    """

    def __init__(
        self,
        metaschema_base: SchemaFileType | None = None,
        metaschema_extensions: list[SchemaFileType] | None = None,
    ) -> None:
        """Initialize the database engine and session factory
        Args:
            fn (str | None): Filename of the sqlite database
                Defaults to None, which uses an in-memory database
            metaschema_base (str | Schema | None): Metadata schema basis.
                Extensions of the meta-schema are imposed of this schema.
                for the database. Defaults to None, which uses the default schema.
                If a string is provided it is assumed to be a path to a schema file
                in yaml format.
                Default is None.
            metaschema_extensions (list[str | Schema | None]): List of schema extensions
                to the base schema. Defaults to None.
                If a string is provided it is assumed to be a path to a schema file
                in yaml format. Extensions are imposed on top of the base schema.
                If None: the SWEET standard extensions are used.
                If an empty list is passed no additional extensions are used.
                Default is None.
        """
        # create the meta-data schema
        metaschema_base = metaschema_base or BASE_SCHEMA
        if metaschema_extensions is None:
            schemas = [metaschema_base] + SWEET_EXTENSIONS
        else:
            schemas = [metaschema_base] + metaschema_extensions
        self._metaschema: dict[str, Any] = self.combine_schemas(schemas)

    @staticmethod
    def read_schema_from_file(file: SchemaFileType) -> dict[str, Any]:
        """Read a file in either json or yaml format

        Args:
            file (str | Path): File path

        Returns:
            dict: File contents

        Raises:
            ValueError: If file is not json or yaml (.json, .yaml, .yml)
            FileNotFoundError: If file is not found
        """
        if isinstance(file, dict):
            return file

        if isinstance(file, bytes):
            # Decode the bytes to a string
            content_str = file.decode("utf-8")
            res = None
            try:
                res = yaml.safe_load(content_str)
            except yaml.YAMLError:
                pass
            try:
                res = json.loads(content_str)
            except json.JSONDecodeError:
                pass
            if res is not None:
                return cast(dict[str, Any], res)
            raise ValueError("Bytes content is not json or yaml") from None

        file = Path(file)
        with open(file) as f:
            if file.suffix == ".json":
                return cast(dict[str, Any], json.load(f))
            elif file.suffix in [".yaml", ".yml"]:
                return cast(dict[str, Any], yaml.safe_load(f))
            else:
                raise ValueError(
                    f"File {file} is not json or yaml. Use .json, .yaml, or .yml"
                )

    @staticmethod
    def combine_schemas(
        schemas: list[SchemaFileType],
    ) -> dict[str, Any]:
        """Combine a list of json schemas to a single schema

        Args:
            schemas (list[dict[str, Any]]): List of schemas to combine

        Returns:
            dict[str, Any]: Combined schema
        """
        schemas_ = [SchemaManager.read_schema_from_file(schema) for schema in schemas]
        combined_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Combined metadata schema",
            "allOf": [
                {"$ref": f"#/definitions/schema{i}"} for i in range(len(schemas_))
            ],
            "definitions": {f"schema{i}": s for i, s in enumerate(schemas_)},
        }
        return combined_schema

    @staticmethod
    def _field_in_table(to_check: Any | list[Any], schema: SchemaFileType) -> bool:
        """Check if a field or a number of fields is in the table

        Args:
            to_check (Any | list[Any]): Field to check
            table (list[str]): Table to check against

        Returns:
            bool: True if the field is in the table, False otherwise
        """
        schema = SchemaManager.read_schema_from_file(schema)
        if not isinstance(to_check, list):
            to_check = [to_check]
        to_check = set(to_check)
        table_fields = {f["name"] for f in schema["fields"]}
        return to_check.issubset(table_fields)

    def validate_schema(self, schema: SchemaFileType) -> dict:
        """Check if a schema is valid given the metadata schema and return it
            as a dictionary

        Args:
            schema (str | Path | dict[str, Any]): Schema to check
                If a string or pathlib.Path is provided, it is assumed to be the
                path to a schema file in json or yaml format.

        Raises:
            jsonschema.exceptions.ValidationError: If the schema is not valid

        Returns:
            dict[str, Any]: The schema as a dictionary

        Raises:
            ValueError: If the primary key is not part of the fields
        """
        schema = SchemaManager.read_schema_from_file(schema)
        jsonschema.validate(instance=schema, schema=self._metaschema)

        # check references: primary keys
        if primary_key := schema.get("primaryKey"):
            if not SchemaManager._field_in_table(to_check=primary_key, schema=schema):
                raise ValueError(f"Primary key {primary_key} is not part of the table")
        # check references: foreign keys
        if foreign_keys := schema.get("foreignKeys"):
            for fkey in foreign_keys:
                foreign_fields = fkey["fields"]
                if not isinstance(foreign_fields, list):
                    foreign_fields = [foreign_fields]
                # check that fields listed match the length of the referenced fields
                referenced_fields = fkey["reference"]["fields"]
                if not isinstance(referenced_fields, list):
                    referenced_fields = [referenced_fields]
                if len(foreign_fields) != len(referenced_fields):
                    raise ValueError(
                        f"Foreign key {foreign_fields} does not match "
                        f"the length of the reference fields {referenced_fields}"
                    )
                # check that the fields are part of the table
                if not SchemaManager._field_in_table(
                    to_check=foreign_fields, schema=schema
                ):
                    raise ValueError(
                        f"Foreign key {foreign_fields} is not part of the table"
                    )
        return schema

    def model_from_schema(
        self,
        schema: SchemaFileType,
        validate_schema: bool = False,
        db_dialect: DbDialect = "sqlite",
        create_id_column: str | None = None,
    ) -> dict[str, Any]:
        """Create sqlmodel inputs from a given schema

        Args:
            schema (str | Path | dict[str, Any]): Schema
            validate_schema (bool, optional): If True, the schema is validated
                Defaults to False.
            db_dialect (DbDialect, optional): Database dialect. Defaults to "sqlite".
                Can be either "sqlite" or "postgres".
            create_id_column (str | None, optional): If provided, a column with the
                given name is added to the table and defined as the primary key.
                Defaults to None.

        Returns:
            dict[str, Any]: A dictionary with the table name, columns, and constraints.
                The table name is the name of the schema and the columns are
                the columns of the table. The columns are sqlmodel.Column objects.
                The constraints are table level constraints. Column level constraints
                are already defined at the column level.
        """
        constraints: list[Constraint] = []
        # read and validate the schema
        my_schema = self.read_schema_from_file(schema)
        if validate_schema:
            my_schema = self.validate_schema(my_schema)

        # get the correct db dialect
        db_types = map_db_types.get(db_dialect)
        if db_types is None:
            raise ValueError(f"Database dialect {db_dialect} is not supported")
        db_types = cast(dict[str, Any], db_types)

        # metadata for the table
        table_name = my_schema["name"]
        table_columns = [
            SchemaManager._field_to_columns(field=field, db_types=db_types)
            for field in my_schema["fields"]
        ]

        # add an primary column to the table
        if create_id_column:
            table_columns.insert(
                0, Column(create_id_column, type_=db_types["integer"], primary_key=True)
            )

        # if the schema has a primary key, add a constraint to the table that
        # enforces that these columns are jointly unique and not-null
        # However, we enforces only the constraint and set the corresponding index
        # but the (internal) primary key is kept the "real" primary key
        if primary_key := my_schema.get("primaryKey"):
            if not isinstance(primary_key, list):
                primary_key = [primary_key]
            # Add non-zero constraints
            for col in table_columns:
                if col.name in primary_key:
                    col.nullable = False
            # Add joint uniqueness constraint
            constraints.append(
                UniqueConstraint(
                    *primary_key, name=f"unique_{table_name}_{'_'.join(primary_key)}"
                )
            )

        # if the schema has foreign keys, add constraints to the table that
        # enforce that these columns are foreign keys
        if foreign_keys := my_schema.get("foreignKeys"):
            for fkey in foreign_keys:
                foreign_fields = fkey["fields"]
                ref_table = fkey["reference"]["resource"]
                ref_fields = fkey["reference"]["fields"]
                # the schema enforces to either have scalar of string on both fields
                # so only check needed here
                if not isinstance(foreign_fields, list):
                    foreign_fields = [foreign_fields]
                    ref_fields = [ref_fields]
                ref_fields = [f"{ref_table}.{f}" for f in ref_fields]
                # add the constraint
                constraints.append(
                    ForeignKeyConstraint(columns=foreign_fields, refcolumns=ref_fields)
                )

        return {
            "name": table_name,
            "columns": table_columns,
            "constraints": constraints,
        }

    @staticmethod
    def _field_to_columns(field: dict[str, Any], db_types: dict[str, Any]) -> Column:
        """Convert a field in the schema to sqlalchemy column

        Args:
            field (dict[str, Any]): Field in the schema
            db_types (dict[str, Any]): Database types

        Returns:
            Column: SQLAlchemy column object
        """
        # Todo: add support for constraints
        field_name = field["name"]
        field_type = field["type"]
        if field_type not in db_types:
            raise ValueError(
                f"Field type {field_type} is not supported for given db dialect"
            )
        db_field_type = db_types[field_type]
        column: Column = Column(field_name, type_=db_field_type)
        return column

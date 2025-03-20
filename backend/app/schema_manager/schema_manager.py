import json
from pathlib import Path
from typing import Any, cast

import jsonschema
import yaml  # type: ignore

__all__ = ["SchemaManager"]

SchemaFileType = str | Path | dict[str, Any]

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

    def validate_schema(self, schema: str | Path | dict[str, Any]) -> None:
        """Check if a schema is valid given the metadata schema

        Args:
            schema (str | Path | dict[str, Any]): Schema to check
                If a string or pathlib.Path is provided, it is assumed to be the
                path to a schema file in json or yaml format.

        Raises:
            jsonschema.exceptions.ValidationError: If the schema is not valid
        """
        if isinstance(schema, str | Path):
            schema = SchemaManager.read_schema_from_file(schema)
        jsonschema.validate(instance=schema, schema=self._metaschema)

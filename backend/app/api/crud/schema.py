from sqlmodel import Session, SQLModel, Table, inspect, or_, select

from app.models.schema import TableSchema, TableSchemaPublic
from app.schema_manager import SchemaManager


def create_schema(
    *, db: Session, data: bytes, schema_manager: SchemaManager
) -> TableSchemaPublic:
    """Writes a schema to the database. The schema is validated against the
        meta-schema. The schema is not activated by default.

    Args:
        db (Session): Database session
        data (bytes): Schema data in bytes
        schema_manager (SchemaManager): Schema manager

    Returns:
        TableSchemaPublic: Schema object
    """
    schema = schema_manager.validate_schema(data)
    db_schema = TableSchema(
        name=schema["name"],
        description=schema["description"],
        jsonschema=schema,
    )
    try:
        db.add(db_schema)
        db.commit()
        db.refresh(db_schema)
    except Exception as e:
        db.rollback()
        raise ValueError("Could not insert schema to db") from e
    return db_schema


def read_schema(
    *, db: Session, schema_id: int | None = None, schema_name: str | None = None
) -> TableSchema:
    """Read a schema from the database. Either the schema_id or schema_name must
        be provided but not both.

    Args:
        db (Session): Database session
        schema_id (int, optional): Schema id. Defaults to None.
        schema_name (str, optional): Schema name. Defaults to None.

    Returns:
        RawJsonSchema: Schema object

    Raises:
        ValueError: If schema is not found
    """
    if schema_id is None and schema_name is None:
        raise ValueError("Either schema_id or schema_name must be provided")
    if schema_id is not None and schema_name is not None:
        raise ValueError("Only one of schema_id or schema_name must be provided")
    schema = db.exec(
        select(TableSchema).filter(
            or_(TableSchema.name == schema_name, TableSchema.id == schema_id)
        )
    ).first()
    if schema is None:
        raise ValueError("Schema not found")
    return schema


def delete_schema(
    *, db: Session, schema_id: int | None = None, schema_name: str | None = None
) -> bool:
    """Delete a schema by id.

    Args:
        db (Session): Database session.
        schema_id (int): Schema id.
        schema_name (str): Schema name.

    Returns:
        bool: True if the schema was deleted, False otherwise.
    """
    try:
        schema = read_schema(db=db, schema_id=schema_id, schema_name=schema_name)
        db.delete(schema)
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False


def toggle_schema(
    *, db: Session, schema_id: int | None = None, schema_name: str | None = None
) -> bool:
    """(De)-Activate a schema by id or name.

    Args:
        db (Session): Database session.
        schema_id (int): Schema id.
        schema_name (str): Schema name.

    Returns:
        bool: True if the schema was toggled, False otherwise.
    """
    try:
        schema = read_schema(db=db, schema_id=schema_id, schema_name=schema_name)
        schema.is_active = not schema.is_active
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False


def create_table_from_schema(
    *,
    db: Session,
    schema_manager: SchemaManager,
    schema_id: int | None = None,
    schema_name: str | None = None,
    id_column_name: str = "id_",
) -> None:
    """Create a table from a schema.

    Args:
        db (Session): Database session.
        schema_manager (SchemaManager): Schema manager.
        schema_id Optional(int): Schema id. Either id or name must be provided.
        schema_name Optional(str): Schema name. Either id or name must be provided.
        id_column_name (str): Name of the id column. Defaults to "id_".
            This column will be added to the table and defined as the primary key.

    Raises:
        ValueError: If the schema is not found or if the table already exists.
        ValueError: If the table could not be created.
    """
    schema = read_schema(db=db, schema_id=schema_id, schema_name=schema_name)
    model_input = schema_manager.model_from_schema(
        schema.jsonschema,
        validate_schema=True,
        db_dialect=db.bind.dialect.name,  # type: ignore[union-attr, arg-type]
        create_id_column=id_column_name,
    )
    # if the table already exists, raise an error
    inspector = inspect(db.bind)
    db_tables = inspector.get_table_names()  # type: ignore[union-attr]
    if model_input["name"] in db_tables:
        raise ValueError(f"Table {model_input['name']} already exists")
    # create the table in the database
    # TODO: it would be better to handle table creation with alembic
    try:
        metadata = SQLModel.metadata
        # FIXME: this is a workaround to avoid the error "Table already exists"
        # during test
        Table(
            model_input["name"], metadata, *model_input["columns"], extend_existing=True
        )
        # Create the table in the database
        metadata.create_all(db.bind)  # type: ignore[arg-type]
    except Exception as e:  # pragma: no cover
        db.rollback()
        raise ValueError("Could not create table") from e

from sqlmodel import Session, select

from app.models.schema import RawJsonSchema
from app.schema_manager import SchemaManager


def create_schema(
    db: Session, data: bytes, schema_manager: SchemaManager
) -> RawJsonSchema:
    schema = schema_manager.validate_schema(data)
    db_schema = RawJsonSchema(
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
    db: Session, schema_id: int | None = None, schema_name: str | None = None
) -> RawJsonSchema:
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
    if schema_id:
        schema = db.get(RawJsonSchema, schema_id)
    if schema_name:
        schema = db.exec(
            select(RawJsonSchema).filter(RawJsonSchema.name == schema_name)
        ).first()
    if schema is None:
        raise ValueError("Schema not found")
    return schema


def delete_schema(
    db: Session, schema_id: int | None = None, schema_name: str | None = None
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


def activate_schema(
    db: Session, schema_id: int | None = None, schema_name: str | None = None
) -> bool:
    """Activate a schema by id or name.

    Args:
        db (Session): Database session.
        schema_id (int): Schema id.
        schema_name (str): Schema name.

    Returns:
        bool: True if the schema was activated, False otherwise.
    """
    try:
        schema = read_schema(db=db, schema_id=schema_id, schema_name=schema_name)
        schema.is_active = True
        db.commit()
        return True
        # TODO Add logic to create the database table
    except Exception:
        db.rollback()
        return False

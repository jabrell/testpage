from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session

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
    except SQLAlchemyError as e:
        db.rollback()
        raise ValueError("Could not insert schema to db") from e
    return db_schema

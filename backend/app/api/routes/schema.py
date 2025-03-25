from fastapi import APIRouter, HTTPException, UploadFile, status
from sqlmodel import select

from app.api.crud.schema import create_schema
from app.api.deps import SchemaManagerDep, SessionDep
from app.models.schema import RawJsonSchema

router = APIRouter(prefix="/schema", tags=["schema"])


@router.post(
    "/",
    # response_model=RawJsonSchema,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Cannot create schema"},
        status.HTTP_201_CREATED: {"description": "User created"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Empty file"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Invalid file. Use JSON or YAML"
        },
    },
)
async def create_schema_api(
    file: UploadFile, session: SessionDep, schema_manager: SchemaManagerDep
):
    """Create a schema from a JSON or YAML file.
    The uploaded file must be a JSON or YAML file and comply with the meta-schema
    standards. The schema will be validated and stored in the database. By
    default, the schema is not activated, i.e., the respective endpoint is not
    created. The schema has to be activated afterwards to be able to insert
    data for the respective schema.

    Args:
        file (UploadFile): The file to be uploaded.
        session (SessionDep): The database session.
        schema_manager (SchemaManagerDep): The schema manager.

    Returns:
        RawJsonSchema: The created schema
    """
    content = await file.read()
    if file.size == 0:
        raise HTTPException(status_code=422, detail="Empty file")
    if not (file.filename.endswith(".json") or file.filename.endswith(".yaml")):
        raise HTTPException(status_code=422, detail="Invalid file. Use JSON or YAML")
    try:
        schema = create_schema(db=session, data=content, schema_manager=schema_manager)
        return schema
    except Exception as e:
        raise HTTPException(
            status_code=400, detail="Cannot create schema" + str(e)
        ) from e


@router.get("/{schema_id}", response_model=RawJsonSchema)
def get_schema(schema_id: int, session: SessionDep):
    """Get a schema either by its ID or by its name."""
    schema = session.get(RawJsonSchema, schema_id)
    if not schema:
        raise HTTPException(status_code=404, detail="Schema not found")
    return schema


@router.delete("/{schema_id}", response_model=dict)
def delete_schema(schema_id: int, session: SessionDep):
    schema = session.get(RawJsonSchema, schema_id)
    if not schema:
        raise HTTPException(status_code=404, detail="Schema not found")
    session.delete(schema)
    session.commit()
    return {"detail": "Schema deleted successfully"}


@router.get("/", response_model=list[RawJsonSchema])
def list_schemas(session: SessionDep):
    schemas = session.exec(select(RawJsonSchema)).all()
    return schemas

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlmodel import select

from app.api.crud.schema import create_schema, delete_schema, read_schema
from app.api.deps import SchemaManagerDep, SessionDep, is_admin_user
from app.models.schema import TableSchema, TableSchemaPublic

router = APIRouter(prefix="/schema", tags=["schema"])


@router.post(
    "/",
    response_model=TableSchemaPublic,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Cannot create schema"},
        status.HTTP_201_CREATED: {"description": "User created"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Empty file"},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Invalid file. Use JSON or YAML"
        },
    },
    dependencies=[Depends(is_admin_user)],
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
    fn = file.filename or ""
    if not (fn.endswith(".json") or fn.endswith(".yaml")):
        raise HTTPException(status_code=422, detail="Invalid file. Use JSON or YAML")
    try:
        schema = create_schema(db=session, data=content, schema_manager=schema_manager)
        return schema
    except Exception as e:
        raise HTTPException(
            status_code=400, detail="Cannot create schema" + str(e)
        ) from e


@router.get(
    "/{schema_id}",
    response_model=TableSchemaPublic,
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_404_NOT_FOUND: {"description": "Schema not found"}},
)
def get_schema(schema_id: int | str, session: SessionDep):
    """Get a schema either by its ID or by its name.

    Args:
        schema_id (int | str): The schema ID.
        session (SessionDep): The database session.

    Returns:
        TableSchemaPublic: The schema object"""
    try:
        schema_id = int(schema_id)
    except ValueError:
        pass
    if isinstance(schema_id, int):
        try:
            schema = read_schema(db=session, schema_id=schema_id)
        except ValueError:
            schema = None
    else:
        try:
            schema = read_schema(db=session, schema_name=schema_id)
        except ValueError:
            schema = None
    if not schema:
        raise HTTPException(status_code=404, detail="Schema not found")
    return schema.get_public()


@router.delete(
    "/{schema_id}",
    response_model=dict,
    status_code=200,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Schema not found"},
        status.HTTP_200_OK: {"description": "Schema deleted"},
    },
    dependencies=[Depends(is_admin_user)],
)
def delete_schema_api(
    schema_id: int | str,
    session: SessionDep,
):
    """Delete a schema by its ID or name

    Args:
        schema_id (int | str): The schema ID.
        session (SessionDep): The database session.

    Returns:
        dict: The deletion confirmation message"""
    try:
        schema_id = int(schema_id)
    except ValueError:
        pass
    if isinstance(schema_id, int):
        deleted = delete_schema(db=session, schema_id=schema_id)
    else:
        deleted = delete_schema(db=session, schema_name=schema_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Schema not found")
    return {"detail": "Schema deleted successfully"}


@router.get("/", response_model=list[TableSchemaPublic])  #
def list_schemas(session: SessionDep):
    schemas = [s.get_public() for s in session.exec(select(TableSchema)).all()]
    # schemas = session.exec(select(TableSchema)).all()
    return schemas

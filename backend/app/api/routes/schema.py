from fastapi import APIRouter, HTTPException, UploadFile, status
from sqlmodel import select

from app.api.crud.schema import create_schema
from app.api.deps import SchemaManagerDep, SessionDep
from app.models.schema import RawJsonSchema

router = APIRouter(prefix="/schema", tags=["schema"])


@router.post(
    "/",
    response_model=RawJsonSchema,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Cannot create schema"},
        status.HTTP_201_CREATED: {"description": "User created"},
    },
)
async def create_schema_api(
    file: UploadFile, session: SessionDep, schema_manager: SchemaManagerDep
):
    try:
        schema = create_schema(db=session, data=file, schema_manager=schema_manager)
        return schema
    except ValueError as e:
        raise HTTPException(
            status_code=400, detail="Cannot create schema" + str(e)
        ) from e


@router.get("/{schema_id}", response_model=RawJsonSchema)
def get_schema(schema_id: int, session: SessionDep):
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

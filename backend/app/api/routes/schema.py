import json

import yaml
from fastapi import APIRouter, HTTPException, UploadFile
from sqlmodel import select

from app.api.deps import SchemaManagerDep, SessionDep
from app.models.schema import RawJsonSchema

router = APIRouter(prefix="/schema", tags=["schema"])


@router.post("/", response_model=RawJsonSchema)
async def create_schema(
    file: UploadFile, session: SessionDep, schema_manager: SchemaManagerDep
):
    try:
        if file.content_type == "application/json":
            data = json.loads(await file.read())
        elif file.content_type in ["application/x-yaml", "text/yaml"]:
            data = yaml.safe_load(await file.read())
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        schema = RawJsonSchema(
            name=data["name"], description=data["description"], schema=data
        )
        session.add(schema)
        session.commit()
        session.refresh(schema)
        return schema
    except (json.JSONDecodeError, yaml.YAMLError, KeyError) as e:
        raise HTTPException(status_code=400, detail="Invalid file content") from e


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

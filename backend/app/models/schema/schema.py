from typing import Any

from sqlmodel import JSON, Column, Field, SQLModel

from ..mixins import TimestampMixin


class TableSchemaCreate(SQLModel):
    name: str = Field(unique=True)
    description: str
    jsonschema: dict[str, Any]

    class Config:
        arbitrary_types_allowed = True


class TableSchemaPublic(TableSchemaCreate):
    id: int | None = None
    is_active: bool = False


class TableSchema(TableSchemaPublic, table=True, mixins=[TimestampMixin]):
    id: int = Field(default=None, primary_key=True)
    jsonschema: dict[str, Any] = Field(sa_column=Column(JSON))

    def get_public(self):
        return TableSchemaPublic(**self.model_dump())

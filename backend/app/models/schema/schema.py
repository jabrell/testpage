from sqlmodel import JSON, Column, Field, SQLModel

from ..mixins import TimestampMixin


class RawJsonSchema(SQLModel, table=True, mixins=[TimestampMixin]):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    description: str
    jsonschema: dict = Field(sa_column=Column(JSON))
    is_active: bool = False

    class Config:
        arbitrary_types_allowed = True

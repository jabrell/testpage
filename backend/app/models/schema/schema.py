from sqlmodel import JSON, Field, SQLModel

from ..mixins import TimestampMixin


class RawJsonSchema(SQLModel, table=True, mixins=[TimestampMixin]):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    description: str
    schema: JSON
    is_active: bool = False

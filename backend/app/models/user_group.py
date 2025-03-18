from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from .mixins import TimestampMixin

if TYPE_CHECKING:
    from .user import User  # pragma: no cover


class UserGroup(SQLModel, table=True, mixins=[TimestampMixin]):
    id: int = Field(default=None, primary_key=True)
    name: str
    description: str
    users: list["User"] = Relationship(back_populates="usergroup")

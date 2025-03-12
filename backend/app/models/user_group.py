from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import TIMESTAMP, Column, Field, Relationship, SQLModel, text

from .mixins import TimestampMixin

if TYPE_CHECKING:
    from .user import User
# todo mixin for metadata


class UserGroup(SQLModel, table=True, mixins=[TimestampMixin]):
    id: int = Field(default=None, primary_key=True)
    name: str
    description: str
    users: list["User"] = Relationship(back_populates="usergroup")

    created_at: datetime | None = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
        )
    )
    updated_at: datetime | None = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
            server_onupdate=text("CURRENT_TIMESTAMP"),
        )
    )

    def __repr__(self):
        return f"<UserGroup {self.name}>"

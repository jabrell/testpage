from datetime import datetime

from pydantic import EmailStr
from sqlmodel import TIMESTAMP, Column, Field, SQLModel, text

__all__ = ["User"]


class UserPublic(SQLModel):
    username: str
    email: EmailStr


class User(UserPublic, table=True):
    id: int = Field(default=None, primary_key=True)
    password: str
    created_at: datetime | None = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
        )
    )
    updated_datetime: datetime | None = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
            server_onupdate=text("CURRENT_TIMESTAMP"),
        )
    )

    def get_public(self):
        return UserPublic(username=self.username, email=self.email)

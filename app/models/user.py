from datetime import datetime

from pydantic import BaseModel, EmailStr
from sqlmodel import TIMESTAMP, Column, Field, SQLModel, text

__all__ = ["User", "UserPublic", "UserCreate", "Token", "TokenData"]


class UserPublic(SQLModel):
    username: str
    email: EmailStr
    is_superuser: bool = False


class UserCreate(UserPublic):
    password: str


class User(UserCreate, table=True):
    id: int = Field(default=None, primary_key=True)
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


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None

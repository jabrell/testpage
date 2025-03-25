from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

from ..mixins import TimestampMixin
from .user_group import UserGroup

__all__ = ["User", "UserPublic", "UserCreate"]


class UserPublic(SQLModel):
    id: int | None = None
    username: str = Field(unique=True)
    email: EmailStr = Field(unique=True)


class UserCreate(UserPublic):
    id: int | None = None
    password: str
    usergroup_name: str = "standard"

    def get_public(self):
        return UserPublic(**self.model_dump())


class User(UserCreate, table=True, mixins=[TimestampMixin]):
    id: int | None = Field(default=None, primary_key=True)
    usergroup_id: int = Field(foreign_key="usergroup.id")
    usergroup: UserGroup = Relationship(back_populates="users")
    is_superuser: bool = Field(default=False)
    is_active: bool = Field(default=True)

    def get_public(self):
        return UserPublic(**self.model_dump())

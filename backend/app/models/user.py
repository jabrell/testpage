from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

from .mixins import TimestampMixin
from .user_group import UserGroup

__all__ = ["User", "UserPublic", "UserCreate"]


class UserPublic(SQLModel):
    username: str
    email: EmailStr


class UserCreate(UserPublic):
    password: str
    usergroup_id: int


class User(UserCreate, table=True, mixins=[TimestampMixin]):
    id: int | None = Field(default=None, primary_key=True)
    usergroup_id: int = Field(foreign_key="usergroup.id")
    usergroup: UserGroup = Relationship(back_populates="users")

    def get_public(self):
        return UserPublic(username=self.username, email=self.email)

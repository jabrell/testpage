from datetime import datetime

from sqlmodel import TIMESTAMP, Column, Field, SQLModel, text

# todo mixin for metadata


class UserGroup(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    description: str

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

    def __repr__(self):
        return f"<UserGroup {self.name}>"

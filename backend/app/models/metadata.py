# from datetime import datetime

# from sqlmodel import Field
# #from sqlmodel import Column, TIMESTAMP
# from sqlalchemy import Column, TIMESTAMP


# class TimestampMixin:
#     created_at: datetime | None = Field(
#         sa_column=Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")
#     )
#     updated_at: datetime | None = Field(
#         sa_column=Column(
#             TIMESTAMP, server_default="CURRENT_TIMESTAMP", onupdate="CURRENT_TIMESTAMP"
#         ),
#     )

#     id: Mapped[datetime] = mapped_column(primary_key=True)

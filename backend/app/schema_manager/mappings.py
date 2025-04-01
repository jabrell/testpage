from sqlalchemy import Boolean, Date, DateTime, Float, Integer, Text, Time
from sqlalchemy.dialects.postgresql import JSONB, NUMERIC, UUID

map_db_types = {
    "sqlite": {
        "any": Text,
        "boolean": Boolean,
        "date": Date,
        "datetime": DateTime,
        "integer": Integer,
        "number": Float,
        "string": Text,
        "time": Time,
        "year": Integer,
    },
    "postgres": {
        "any": Text,
        "boolean": Boolean,
        "date": Date,
        "datetime": DateTime,
        "integer": Integer,
        "number": NUMERIC,  # Use NUMERIC for better precision
        "string": Text,
        "time": Time,
        "year": Integer,
        "uuid": UUID(as_uuid=True),  # PostgreSQL-specific UUID type
        "json": JSONB,  # PostgreSQL-specific JSONB type
    },
}

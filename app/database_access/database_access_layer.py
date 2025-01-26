from sqlmodel import Session, SQLModel, create_engine

import app.models as models  # noqa: F401
from app.settings import db_url


def get_db_session() -> Session:
    """Get a new database session"""
    dal = DatabaseAccessLayer(db_url)
    return Session(dal.engine)


class DatabaseAccessLayer:
    """Database access layer class that handles database connections"""

    _instance: "DatabaseAccessLayer" = None

    def __init__(self, db_url: str = db_url):
        self.engine = create_engine(db_url)
        SQLModel.metadata.create_all(self.engine)

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DatabaseAccessLayer, cls).__new__(cls)
        return cls._instance

    @property
    def session(self) -> Session:
        """Database session property"""
        return Session(self.engine)

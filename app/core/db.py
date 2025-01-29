from sqlmodel import Session, create_engine

from app.core.config import settings
from app.models import User, UserCreate  # noqa

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def init_db(session: Session) -> None:
    # TODO Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    SQLModel.metadata.create_all(engine)

    # user = session.exec(
    #     select(User).where(User.email == settings.FIRST_SUPERUSER)
    # ).first()
    # if not user:
    #     user_in = UserCreate(
    #         username=settings.FIRST_SUPERUSER,
    #         email=settings.FIRST_SUPERUSER_MAIL,
    #         password=settings.FIRST_SUPERUSER_PASSWORD,
    #         is_superuser=True,
    #     )
    #     user.password = hash_password(user.password)
    #     user = User(**user_in.model_dump())
    #     session.add(user)
    #     session.commit()

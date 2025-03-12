from sqlmodel import Session, create_engine, select

from app.core.config import settings
from app.core.security import hash_password
from app.models import User, UserGroup

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def init_db(session: Session) -> None:
    # TODO Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    SQLModel.metadata.create_all(engine)

    # create the initial user groups
    for g in ["admin", "standard"]:
        group = session.exec(select(UserGroup).where(UserGroup.name == g)).first()
        if not group:
            group = UserGroup(name=g, description=f"{g} group")
            session.add(group)

    # create the initial super user
    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        admin_group = session.exec(
            select(UserGroup.id).where(UserGroup.name == "admin")
        ).first()
        user_in = User(
            username=settings.FIRST_SUPERUSER,
            email=settings.FIRST_SUPERUSER_MAIL,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            usergroup_id=admin_group,
        )
        user_in.password = hash_password(user_in.password)
        session.add(user_in)
    # commit the session
    session.commit()

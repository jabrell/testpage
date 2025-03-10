import jwt  # noqa

from app.core.config import settings  # noqa
from app.core.security import create_access_token, decode_access_token

if __name__ == "__main__":
    # JWT_ALGORITHM = "HS256"
    # JWT_TIMEDELTA = 30

    # def create_access_token(
    #     subject: str | Any,
    #     expires_delta: timedelta = timedelta(minutes=settings.JWT_TIMEDELTA),
    # ) -> str:
    #     expire = datetime.now(timezone.utc) + expires_delta
    #     to_encode = {"exp": expire, "sub": str(subject)}
    #     encoded_jwt = jwt.encode(
    #         to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    #     )
    #     return encoded_jwt

    # timedelta(minutes=settings.JWT_TIMEDELTA)
    token = create_access_token("test")
    returned = decode_access_token(token)
    print(returned)
    decode_access_token("test")
    print("here")

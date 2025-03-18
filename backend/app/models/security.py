from pydantic import BaseModel

__all__ = ["Token", "TokenPayload"]


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    exp: int
    sub: str | None = None

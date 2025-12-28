from typing import Optional

from pydantic import BaseModel


class RegisterIn(BaseModel):
    email: str
    password: str


class LoginIn(BaseModel):
    email: str
    password: str


class GoogleLoginIn(BaseModel):
    id_token: str


class ResetPasswordIn(BaseModel):
    email: str


class UserOut(BaseModel):
    id: str
    email: str
    provider: str


class AuthOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class SessionOut(BaseModel):
    authenticated: bool
    user: Optional[UserOut] = None


class MessageOut(BaseModel):
    detail: str

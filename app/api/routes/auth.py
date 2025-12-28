from typing import Optional

from fastapi import APIRouter, Depends, Header

from app.models.schemas import (
    AuthOut,
    GoogleLoginIn,
    LoginIn,
    MessageOut,
    RegisterIn,
    ResetPasswordIn,
    SessionOut,
)
from app.services.auth_service import AuthService, get_auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthOut)
def register(
    payload: RegisterIn,
    service: AuthService = Depends(get_auth_service),
) -> AuthOut:
    return service.register(payload.email, payload.password)


@router.post("/login", response_model=AuthOut)
def login(
    payload: LoginIn,
    service: AuthService = Depends(get_auth_service),
) -> AuthOut:
    return service.login(payload.email, payload.password)


@router.post("/login/google", response_model=AuthOut)
def login_google(
    payload: GoogleLoginIn,
    service: AuthService = Depends(get_auth_service),
) -> AuthOut:
    return service.login_google(payload.id_token)


@router.post("/logout", response_model=MessageOut)
def logout(
    authorization: Optional[str] = Header(default=None),
    service: AuthService = Depends(get_auth_service),
) -> MessageOut:
    return service.logout(authorization)


@router.get("/session", response_model=SessionOut)
def session(
    authorization: Optional[str] = Header(default=None),
    service: AuthService = Depends(get_auth_service),
) -> SessionOut:
    return service.session(authorization)


@router.post("/reset-password", response_model=MessageOut)
def reset_password(
    payload: ResetPasswordIn,
    service: AuthService = Depends(get_auth_service),
) -> MessageOut:
    return service.reset_password(payload.email)

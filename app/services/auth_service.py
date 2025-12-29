import uuid
from typing import Optional

from fastapi import HTTPException

from app.core import security
from app.models.schemas import AuthOut, MessageOut, SessionOut, UserOut
from app.storage.memory import MemoryStore, UserRecord, store


class AuthService:
    def __init__(self, store: MemoryStore) -> None:
        self._store = store

    def register(self, email: str, password: str) -> AuthOut:
        if self._store.get_user(email):
            raise HTTPException(status_code=409, detail="Email already registered")
        salt = security.generate_salt()
        pw_hash = security.hash_password(password, salt)
        record = UserRecord(
            id=str(uuid.uuid4()),
            provider="local",
            salt_b64=security.encode_b64(salt),
            pw_hash_b64=security.encode_b64(pw_hash),
        )
        self._store.set_user(email, record)
        token = self._new_session(email)
        return AuthOut(access_token=token, user=self._user_out(email, record))

    def login(self, email: str, password: str) -> AuthOut:
        user = self._store.get_user(email)
        if not user or user.provider != "local":
            raise HTTPException(status_code=401, detail="Invalid credentials")
        if not user.salt_b64 or not user.pw_hash_b64:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        if not security.verify_password(password, user.salt_b64, user.pw_hash_b64):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        token = self._new_session(email)
        return AuthOut(access_token=token, user=self._user_out(email, user))

    def login_google(self, id_token: str) -> AuthOut:
        email = security.unsafe_decode_email_from_jwt(id_token)
        if not email:
            raise HTTPException(status_code=400, detail="Invalid id_token")
        user = self._store.get_user(email)
        if not user:
            user = UserRecord(id=str(uuid.uuid4()), provider="google")
            self._store.set_user(email, user)
        token = self._new_session(email)
        return AuthOut(access_token=token, user=self._user_out(email, user))

    def logout(self, authorization: Optional[str]) -> MessageOut:
        user = self._get_user_from_header(authorization)
        token = self._extract_token(authorization)
        self._store.delete_session(token)
        return MessageOut(detail=f"Logged out {user.email}")

    def session(self, authorization: Optional[str]) -> SessionOut:
        if not authorization:
            return SessionOut(authenticated=False)
        try:
            user = self._get_user_from_header(authorization)
        except HTTPException:
            return SessionOut(authenticated=False)
        return SessionOut(authenticated=True, user=user)

    def reset_password(self, email: str) -> MessageOut:
        user = self._store.get_user(email)
        if user:
            token = security.create_reset_token()
            self._store.set_reset_token(email, token)
        return MessageOut(detail="If the email exists, a reset link was sent.")

    def get_authenticated_email(self, authorization: Optional[str]) -> str:
        token = self._extract_token(authorization)
        email = self._store.get_email_for_session(token)
        if not email:
            raise HTTPException(status_code=401, detail="Invalid session")
        return email

    def _new_session(self, email: str) -> str:
        token = security.create_session_token()
        self._store.create_session(token, email)
        return token

    def _extract_token(self, authorization: Optional[str]) -> str:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Not authenticated")
        token = authorization.split(" ", 1)[1].strip()
        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated")
        return token

    def _get_user_from_header(self, authorization: Optional[str]) -> UserOut:
        token = self._extract_token(authorization)
        email = self._store.get_email_for_session(token)
        if not email:
            raise HTTPException(status_code=401, detail="Invalid session")
        user = self._store.get_user(email)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid session")
        return self._user_out(email, user)

    def _user_out(self, email: str, user: UserRecord) -> UserOut:
        return UserOut(id=user.id, email=email, provider=user.provider)


_service = AuthService(store)


def get_auth_service() -> AuthService:
    return _service

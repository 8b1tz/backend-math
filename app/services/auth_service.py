import uuid
from datetime import date, datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException

from app.core import security
from app.models.schemas import AuthOut, MessageOut, SessionOut, UserOut
from app.storage.memory import MemoryStore, PlayerProfile, UserRecord, store


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
        profile = self._ensure_profile(email, record.id)
        self._touch_login(profile)
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
        profile = self._ensure_profile(email, user.id)
        self._touch_login(profile)
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
        profile = self._ensure_profile(email, user.id)
        self._touch_login(profile)
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

    def _ensure_profile(self, email: str, user_id: str) -> PlayerProfile:
        profile = self._store.get_profile(user_id)
        if profile:
            return profile
        profile = PlayerProfile(id=user_id, email=email, language="pt")
        self._store.set_profile(user_id, profile)
        return profile

    def _touch_login(self, profile: PlayerProfile) -> None:
        today = self._today()
        last_login = self._parse_date(profile.last_login_date)
        if last_login == today:
            return
        if last_login == today - timedelta(days=1):
            profile.current_streak += 1
        else:
            profile.current_streak = 1
        if profile.current_streak > profile.longest_streak:
            profile.longest_streak = profile.current_streak
        profile.last_login_date = today.isoformat()

    def _today(self) -> date:
        return datetime.now(timezone.utc).date()

    def _parse_date(self, value: Optional[str]) -> Optional[date]:
        if not value:
            return None
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None


_service = AuthService(store)


def get_auth_service() -> AuthService:
    return _service

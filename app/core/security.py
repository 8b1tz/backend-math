import base64
import hashlib
import hmac
import json
import secrets
from typing import Optional


def hash_password(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)


def generate_salt() -> bytes:
    return secrets.token_bytes(16)


def encode_b64(raw: bytes) -> str:
    return base64.b64encode(raw).decode("ascii")


def decode_b64(raw: str) -> bytes:
    return base64.b64decode(raw.encode("ascii"))


def verify_password(password: str, salt_b64: str, pw_hash_b64: str) -> bool:
    salt = decode_b64(salt_b64)
    expected = decode_b64(pw_hash_b64)
    actual = hash_password(password, salt)
    return hmac.compare_digest(actual, expected)


def create_session_token() -> str:
    return secrets.token_urlsafe(32)


def create_reset_token() -> str:
    return secrets.token_urlsafe(24)


def unsafe_decode_email_from_jwt(id_token: str) -> Optional[str]:
    try:
        parts = id_token.split(".")
        if len(parts) != 3:
            return None
        payload = parts[1]
        payload += "=" * (-len(payload) % 4)
        data = json.loads(base64.urlsafe_b64decode(payload.encode("ascii")))
        return data.get("email")
    except Exception:
        return None

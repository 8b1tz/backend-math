from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class UserRecord:
    id: str
    provider: str
    salt_b64: Optional[str] = None
    pw_hash_b64: Optional[str] = None


class MemoryStore:
    def __init__(self) -> None:
        self.users: Dict[str, UserRecord] = {}
        self.sessions: Dict[str, str] = {}
        self.reset_tokens: Dict[str, str] = {}

    def get_user(self, email: str) -> Optional[UserRecord]:
        return self.users.get(email)

    def set_user(self, email: str, record: UserRecord) -> None:
        self.users[email] = record

    def create_session(self, token: str, email: str) -> None:
        self.sessions[token] = email

    def get_email_for_session(self, token: str) -> Optional[str]:
        return self.sessions.get(token)

    def delete_session(self, token: str) -> None:
        self.sessions.pop(token, None)

    def set_reset_token(self, email: str, token: str) -> None:
        self.reset_tokens[email] = token


store = MemoryStore()

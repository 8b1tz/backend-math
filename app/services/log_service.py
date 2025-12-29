from datetime import datetime

from app.models.schemas import ErrorLogIn, GameSessionLogIn, MessageOut
from app.storage.memory import MemoryStore, store


class LogService:
    def __init__(self, store: MemoryStore) -> None:
        self._store = store

    def log_error(self, payload: ErrorLogIn) -> MessageOut:
        entry = {
            "timestamp": self._timestamp(),
            "user_id": payload.user_id,
            "message": payload.message,
            "stack": payload.stack,
            "context": payload.context,
        }
        self._store.add_error_log(entry)
        return MessageOut(detail="Error logged")

    def log_game_session(self, payload: GameSessionLogIn) -> MessageOut:
        entry = {
            "timestamp": self._timestamp(),
            "user_id": payload.user_id,
            "session_id": payload.session_id,
            "payload": payload.payload,
        }
        self._store.add_game_session_log(entry)
        return MessageOut(detail="Game session logged")

    def _timestamp(self) -> str:
        return datetime.utcnow().isoformat() + "Z"


_service = LogService(store)


def get_log_service() -> LogService:
    return _service

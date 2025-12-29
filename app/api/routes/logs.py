from fastapi import APIRouter, Depends

from app.models.schemas import ErrorLogIn, GameSessionLogIn, MessageOut
from app.services.log_service import LogService, get_log_service

router = APIRouter(prefix="/logs", tags=["logs"])


@router.post("/error", response_model=MessageOut)
def log_error(
    payload: ErrorLogIn,
    service: LogService = Depends(get_log_service),
) -> MessageOut:
    return service.log_error(payload)


@router.post("/game-session", response_model=MessageOut)
def log_game_session(
    payload: GameSessionLogIn,
    service: LogService = Depends(get_log_service),
) -> MessageOut:
    return service.log_game_session(payload)

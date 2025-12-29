from fastapi import APIRouter, Depends

from app.models.schemas import (
    GameAnswerIn,
    GameAnswerOut,
    GameFinishIn,
    GameFinishOut,
    GameStartIn,
    GameStartOut,
)
from app.services.game_service import GameService, get_game_service

router = APIRouter(prefix="/game", tags=["game"])


@router.post("/start", response_model=GameStartOut)
def start_game(
    payload: GameStartIn,
    service: GameService = Depends(get_game_service),
) -> GameStartOut:
    return service.start(payload.user_id, payload.level, payload.question_count)


@router.post("/answer", response_model=GameAnswerOut)
def answer_game(
    payload: GameAnswerIn,
    service: GameService = Depends(get_game_service),
) -> GameAnswerOut:
    return service.answer(payload.session_id, payload.question_id, payload.answer)


@router.post("/finish", response_model=GameFinishOut)
def finish_game(
    payload: GameFinishIn,
    service: GameService = Depends(get_game_service),
) -> GameFinishOut:
    return service.finish(payload.session_id)

from typing import List

from fastapi import APIRouter, Depends, Query

from app.models.schemas import QuestionOut
from app.services.question_service import QuestionService, get_question_service

router = APIRouter(prefix="/questions", tags=["questions"])


@router.get("", response_model=List[QuestionOut])
def list_questions(
    level: int = Query(..., ge=1),
    service: QuestionService = Depends(get_question_service),
) -> List[QuestionOut]:
    return service.list_by_level(level)


@router.get("/{question_id}", response_model=QuestionOut)
def get_question(
    question_id: str,
    service: QuestionService = Depends(get_question_service),
) -> QuestionOut:
    return service.get_question(question_id)

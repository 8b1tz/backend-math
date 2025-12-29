from typing import List

from fastapi import HTTPException

from app.models.schemas import QuestionOut
from app.storage.memory import MemoryStore, QuestionRecord, store


class QuestionService:
    def __init__(self, store: MemoryStore) -> None:
        self._store = store

    def list_by_level(self, level: int) -> List[QuestionOut]:
        questions = self._store.list_questions_by_level(level)
        return [self._to_out(question) for question in questions]

    def get_question(self, question_id: str) -> QuestionOut:
        question = self._store.get_question(question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        return self._to_out(question)

    def _to_out(self, question: QuestionRecord) -> QuestionOut:
        return QuestionOut(
            id=question.id,
            level=question.level,
            prompt=question.prompt,
            choices=question.choices,
        )


_service = QuestionService(store)


def get_question_service() -> QuestionService:
    return _service

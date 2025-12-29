import random
import uuid

from fastapi import HTTPException

from app.core.progression import calculate_level
from app.models.schemas import GameAnswerOut, GameFinishOut, GameStartOut, QuestionOut
from app.storage.memory import (
    GameSessionRecord,
    MemoryStore,
    QuestionRecord,
    RankingEntry,
    store,
)


class GameService:
    def __init__(self, store: MemoryStore) -> None:
        self._store = store

    def start(self, user_id: str, level: int, question_count: int) -> GameStartOut:
        if question_count <= 0:
            raise HTTPException(status_code=400, detail="question_count must be positive")
        if not self._store.get_profile(user_id):
            raise HTTPException(status_code=404, detail="User profile not found")
        questions = self._store.list_questions_by_level(level)
        if not questions:
            raise HTTPException(status_code=404, detail="No questions for level")
        if question_count >= len(questions):
            selected = questions
        else:
            selected = random.sample(questions, question_count)
        session = GameSessionRecord(
            id=str(uuid.uuid4()),
            user_id=user_id,
            level=level,
            question_ids=[question.id for question in selected],
            time_limit_seconds=self._time_limit(level),
        )
        self._store.create_game_session(session)
        return GameStartOut(
            session_id=session.id,
            level=level,
            time_limit_seconds=session.time_limit_seconds,
            questions=[self._to_out(question) for question in selected],
        )

    def answer(self, session_id: str, question_id: str, answer: str) -> GameAnswerOut:
        session = self._get_session_or_404(session_id)
        if session.finished:
            raise HTTPException(status_code=409, detail="Session already finished")
        if question_id not in session.question_ids:
            raise HTTPException(status_code=400, detail="Question not in session")
        question = self._store.get_question(question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        normalized = answer.strip().lower()
        expected = question.answer.strip().lower()
        previous = session.answers.get(question_id)
        previous_correct = False
        if previous is not None:
            previous_correct = previous.strip().lower() == expected
        correct = normalized == expected
        session.answers[question_id] = answer
        if previous is None:
            if correct:
                session.correct_count += 1
        else:
            if previous_correct and not correct:
                session.correct_count -= 1
            elif not previous_correct and correct:
                session.correct_count += 1
        return GameAnswerOut(
            correct=correct,
            correct_answer=None if correct else question.answer,
            current_correct=session.correct_count,
        )

    def finish(self, session_id: str) -> GameFinishOut:
        session = self._get_session_or_404(session_id)
        if session.finished:
            raise HTTPException(status_code=409, detail="Session already finished")
        session.finished = True
        total_questions = len(session.question_ids)
        correct_answers = session.correct_count
        xp_earned = correct_answers * 10
        profile = self._store.get_profile(session.user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        profile.xp += xp_earned
        profile.level = calculate_level(profile.xp)
        profile.stats.games_played += 1
        profile.stats.questions_answered += total_questions
        profile.stats.correct_answers += correct_answers
        self._store.set_ranking_entry(
            RankingEntry(user_id=profile.id, xp=profile.xp, level=profile.level)
        )
        return GameFinishOut(
            session_id=session.id,
            user_id=session.user_id,
            correct_answers=correct_answers,
            total_questions=total_questions,
            xp_earned=xp_earned,
            total_xp=profile.xp,
            level=profile.level,
        )

    def _get_session_or_404(self, session_id: str) -> GameSessionRecord:
        session = self._store.get_game_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session

    def _to_out(self, question: QuestionRecord) -> QuestionOut:
        return QuestionOut(
            id=question.id,
            level=question.level,
            prompt=question.prompt,
            choices=question.choices,
        )

    def _time_limit(self, level: int) -> int:
        return 60 + (level * 15)


_service = GameService(store)


def get_game_service() -> GameService:
    return _service

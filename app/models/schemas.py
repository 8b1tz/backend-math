from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class RegisterIn(BaseModel):
    email: str
    password: str


class LoginIn(BaseModel):
    email: str
    password: str


class GoogleLoginIn(BaseModel):
    id_token: str


class ResetPasswordIn(BaseModel):
    email: str


class UserOut(BaseModel):
    id: str
    email: str
    provider: str


class AuthOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class SessionOut(BaseModel):
    authenticated: bool
    user: Optional[UserOut] = None


class MessageOut(BaseModel):
    detail: str


class UserCreateIn(BaseModel):
    email: Optional[str] = None
    display_name: Optional[str] = None
    language: Optional[str] = None
    xp: Optional[int] = None
    level: Optional[int] = None
    progress: Optional[Dict[str, int]] = None
    current_streak: Optional[int] = None
    longest_streak: Optional[int] = None
    last_login_date: Optional[str] = None
    lessons_completed_today: Optional[int] = None
    last_lesson_date: Optional[str] = None


class UserUpdateIn(BaseModel):
    display_name: Optional[str] = None
    language: Optional[str] = None
    xp: Optional[int] = None
    level: Optional[int] = None
    progress: Optional[Dict[str, int]] = None
    current_streak: Optional[int] = None
    longest_streak: Optional[int] = None
    last_login_date: Optional[str] = None
    lessons_completed_today: Optional[int] = None
    last_lesson_date: Optional[str] = None


class ProfileOut(BaseModel):
    id: str
    email: Optional[str] = None
    display_name: Optional[str] = None
    language: Optional[str] = None
    xp: int
    level: int
    progress: Dict[str, int] = Field(default_factory=dict)
    current_streak: int
    longest_streak: int
    last_login_date: Optional[str] = None
    lessons_completed_today: int
    last_lesson_date: Optional[str] = None


class UserStatsOut(BaseModel):
    user_id: str
    games_played: int
    questions_answered: int
    correct_answers: int
    accuracy: float


class QuestionOut(BaseModel):
    id: str
    level: int
    operation: str
    template: str
    choices: List[str]


class GameStartIn(BaseModel):
    user_id: str
    level: int
    question_count: int = 5


class GameStartOut(BaseModel):
    session_id: str
    level: int
    time_limit_seconds: int
    questions: List[QuestionOut]


class GameAnswerIn(BaseModel):
    session_id: str
    question_id: str
    answer: str


class GameAnswerOut(BaseModel):
    correct: bool
    correct_answer: Optional[str] = None
    current_correct: int


class GameFinishIn(BaseModel):
    session_id: str


class GameFinishOut(BaseModel):
    session_id: str
    user_id: str
    correct_answers: int
    total_questions: int
    xp_earned: int
    total_xp: int
    level: int


class ProgressUpdateIn(BaseModel):
    user_id: str
    xp_delta: int = 0
    progress: Optional[Dict[str, int]] = None


class ProgressOut(BaseModel):
    user_id: str
    xp: int
    level: int
    progress: Dict[str, int] = Field(default_factory=dict)


class RankingUpdateIn(BaseModel):
    user_id: str
    xp: Optional[int] = None
    level: Optional[int] = None
    display_name: Optional[str] = None


class RankingEntryOut(BaseModel):
    user_id: str
    display_name: Optional[str] = None
    xp: int
    level: int
    position: int
    updated_at: str


class ErrorLogIn(BaseModel):
    user_id: Optional[str] = None
    message: str
    stack: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class GameSessionLogIn(BaseModel):
    user_id: str
    session_id: str
    payload: Dict[str, Any]


class HealthOut(BaseModel):
    status: str

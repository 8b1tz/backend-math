from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class UserRecord:
    id: str
    provider: str
    salt_b64: Optional[str] = None
    pw_hash_b64: Optional[str] = None


@dataclass
class PlayerStats:
    games_played: int = 0
    questions_answered: int = 0
    correct_answers: int = 0


@dataclass
class PlayerProfile:
    id: str
    email: Optional[str] = None
    display_name: Optional[str] = None
    xp: int = 0
    level: int = 1
    progress: Dict[str, int] = field(default_factory=dict)
    stats: PlayerStats = field(default_factory=PlayerStats)


@dataclass
class QuestionRecord:
    id: str
    level: int
    prompt: str
    choices: List[str]
    answer: str


@dataclass
class GameSessionRecord:
    id: str
    user_id: str
    level: int
    question_ids: List[str]
    time_limit_seconds: int
    answers: Dict[str, str] = field(default_factory=dict)
    correct_count: int = 0
    finished: bool = False


@dataclass
class RankingEntry:
    user_id: str
    xp: int
    level: int


class MemoryStore:
    def __init__(self) -> None:
        self.users: Dict[str, UserRecord] = {}
        self.sessions: Dict[str, str] = {}
        self.reset_tokens: Dict[str, str] = {}
        self.user_profiles: Dict[str, PlayerProfile] = {}
        self.email_to_user_id: Dict[str, str] = {}
        self.questions: Dict[str, QuestionRecord] = {}
        self.game_sessions: Dict[str, GameSessionRecord] = {}
        self.ranking: Dict[str, RankingEntry] = {}
        self.error_logs: List[dict] = []
        self.game_session_logs: List[dict] = []
        self._seed_questions()

    def _seed_questions(self) -> None:
        if self.questions:
            return
        sample = [
            QuestionRecord(
                id="q1",
                level=1,
                prompt="2 + 2 = ?",
                choices=["3", "4", "5", "6"],
                answer="4",
            ),
            QuestionRecord(
                id="q2",
                level=1,
                prompt="5 - 3 = ?",
                choices=["1", "2", "3", "4"],
                answer="2",
            ),
            QuestionRecord(
                id="q3",
                level=1,
                prompt="10 / 2 = ?",
                choices=["3", "5", "7", "9"],
                answer="5",
            ),
            QuestionRecord(
                id="q4",
                level=1,
                prompt="3 * 4 = ?",
                choices=["7", "11", "12", "13"],
                answer="12",
            ),
            QuestionRecord(
                id="q5",
                level=2,
                prompt="12 - 5 = ?",
                choices=["5", "6", "7", "8"],
                answer="7",
            ),
            QuestionRecord(
                id="q6",
                level=2,
                prompt="9 + 8 = ?",
                choices=["15", "16", "17", "18"],
                answer="17",
            ),
            QuestionRecord(
                id="q7",
                level=2,
                prompt="6 * 3 = ?",
                choices=["16", "17", "18", "19"],
                answer="18",
            ),
            QuestionRecord(
                id="q8",
                level=3,
                prompt="18 / 3 = ?",
                choices=["5", "6", "7", "8"],
                answer="6",
            ),
            QuestionRecord(
                id="q9",
                level=3,
                prompt="7 * 8 = ?",
                choices=["54", "56", "58", "60"],
                answer="56",
            ),
            QuestionRecord(
                id="q10",
                level=3,
                prompt="25 - 9 = ?",
                choices=["14", "15", "16", "17"],
                answer="16",
            ),
        ]
        for question in sample:
            self.questions[question.id] = question

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

    def get_profile(self, user_id: str) -> Optional[PlayerProfile]:
        return self.user_profiles.get(user_id)

    def get_profile_by_email(self, email: str) -> Optional[PlayerProfile]:
        user_id = self.email_to_user_id.get(email)
        if not user_id:
            return None
        return self.user_profiles.get(user_id)

    def set_profile(self, user_id: str, profile: PlayerProfile) -> None:
        self.user_profiles[user_id] = profile
        if profile.email:
            self.email_to_user_id[profile.email] = user_id

    def get_question(self, question_id: str) -> Optional[QuestionRecord]:
        return self.questions.get(question_id)

    def list_questions_by_level(self, level: int) -> List[QuestionRecord]:
        return [question for question in self.questions.values() if question.level == level]

    def create_game_session(self, session: GameSessionRecord) -> None:
        self.game_sessions[session.id] = session

    def get_game_session(self, session_id: str) -> Optional[GameSessionRecord]:
        return self.game_sessions.get(session_id)

    def set_ranking_entry(self, entry: RankingEntry) -> None:
        self.ranking[entry.user_id] = entry

    def get_ranking_entry(self, user_id: str) -> Optional[RankingEntry]:
        return self.ranking.get(user_id)

    def list_ranking(self) -> List[RankingEntry]:
        return list(self.ranking.values())

    def add_error_log(self, entry: dict) -> None:
        self.error_logs.append(entry)

    def add_game_session_log(self, entry: dict) -> None:
        self.game_session_logs.append(entry)


store = MemoryStore()

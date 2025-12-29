from fastapi import HTTPException

from app.core.progression import calculate_level
from app.models.schemas import ProfileOut, UserCreateIn, UserStatsOut, UserUpdateIn
from app.storage.memory import MemoryStore, PlayerProfile, PlayerStats, store


class UserService:
    def __init__(self, store: MemoryStore) -> None:
        self._store = store

    def create_profile(self, user_id: str, payload: UserCreateIn) -> ProfileOut:
        if self._store.get_profile(user_id):
            raise HTTPException(status_code=409, detail="User already exists")
        xp_value = payload.xp or 0
        if payload.level is None:
            level_value = calculate_level(xp_value)
        else:
            level_value = payload.level
        profile = PlayerProfile(
            id=user_id,
            email=payload.email,
            display_name=payload.display_name,
            xp=xp_value,
            level=level_value,
            progress=payload.progress or {},
            stats=PlayerStats(),
        )
        self._store.set_profile(user_id, profile)
        return self._to_out(profile)

    def get_profile(self, user_id: str) -> ProfileOut:
        profile = self._get_profile_or_404(user_id)
        return self._to_out(profile)

    def update_profile(self, user_id: str, payload: UserUpdateIn) -> ProfileOut:
        profile = self._get_profile_or_404(user_id)
        if payload.display_name is not None:
            profile.display_name = payload.display_name
        if payload.xp is not None:
            profile.xp = payload.xp
            if payload.level is None:
                profile.level = calculate_level(profile.xp)
        if payload.level is not None:
            profile.level = payload.level
        if payload.progress is not None:
            profile.progress.update(payload.progress)
        return self._to_out(profile)

    def get_stats(self, user_id: str) -> UserStatsOut:
        profile = self._get_profile_or_404(user_id)
        stats = profile.stats
        accuracy = 0.0
        if stats.questions_answered:
            accuracy = stats.correct_answers / stats.questions_answered
        return UserStatsOut(
            user_id=profile.id,
            games_played=stats.games_played,
            questions_answered=stats.questions_answered,
            correct_answers=stats.correct_answers,
            accuracy=accuracy,
        )

    def _get_profile_or_404(self, user_id: str) -> PlayerProfile:
        profile = self._store.get_profile(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        return profile

    def _to_out(self, profile: PlayerProfile) -> ProfileOut:
        return ProfileOut(
            id=profile.id,
            email=profile.email,
            display_name=profile.display_name,
            xp=profile.xp,
            level=profile.level,
            progress=profile.progress,
        )


_service = UserService(store)


def get_user_service() -> UserService:
    return _service

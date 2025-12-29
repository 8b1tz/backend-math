from typing import Dict, Optional

from fastapi import HTTPException

from app.core.progression import calculate_level
from app.models.schemas import ProgressOut
from app.storage.memory import MemoryStore, store


class ProgressService:
    def __init__(self, store: MemoryStore) -> None:
        self._store = store

    def update(
        self, user_id: str, xp_delta: int, progress: Optional[Dict[str, int]]
    ) -> ProgressOut:
        profile = self._get_profile_or_404(user_id)
        if xp_delta:
            profile.xp = max(0, profile.xp + xp_delta)
        if progress:
            profile.progress.update(progress)
        profile.level = calculate_level(profile.xp)
        return ProgressOut(
            user_id=profile.id,
            xp=profile.xp,
            level=profile.level,
            progress=profile.progress,
        )

    def get(self, user_id: str) -> ProgressOut:
        profile = self._get_profile_or_404(user_id)
        return ProgressOut(
            user_id=profile.id,
            xp=profile.xp,
            level=profile.level,
            progress=profile.progress,
        )

    def _get_profile_or_404(self, user_id: str):
        profile = self._store.get_profile(user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        return profile


_service = ProgressService(store)


def get_progress_service() -> ProgressService:
    return _service

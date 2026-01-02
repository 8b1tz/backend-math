from datetime import datetime, timezone
from typing import List, Optional

from fastapi import HTTPException

from app.models.schemas import RankingEntryOut
from app.storage.memory import MemoryStore, RankingEntry, store


class RankingService:
    def __init__(self, store: MemoryStore) -> None:
        self._store = store

    def update(
        self, user_id: str, xp: Optional[int], level: Optional[int], display_name: Optional[str]
    ) -> RankingEntryOut:
        profile = self._store.get_profile(user_id)
        if profile:
            if xp is not None:
                profile.xp = xp
            if level is not None:
                profile.level = level
            xp_value = profile.xp
            level_value = profile.level
            display_name = profile.display_name or profile.email
        else:
            if xp is None or level is None:
                raise HTTPException(status_code=404, detail="User profile not found")
            xp_value = xp
            level_value = level
        entry = RankingEntry(
            user_id=user_id,
            display_name=display_name,
            xp=xp_value,
            level=level_value,
            updated_at=self._timestamp(),
        )
        self._store.set_ranking_entry(entry)
        return self._entry_with_position(entry)

    def global_ranking(self) -> List[RankingEntryOut]:
        entries = self._sorted_entries()
        return [
            RankingEntryOut(
                user_id=entry.user_id,
                display_name=entry.display_name,
                xp=entry.xp,
                level=entry.level,
                position=index + 1,
                updated_at=entry.updated_at,
            )
            for index, entry in enumerate(entries)
        ]

    def get_me(self, email: str) -> RankingEntryOut:
        profile = self._store.get_profile_by_email(email)
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        entry = self._store.get_ranking_entry(profile.id)
        if not entry:
            entry = RankingEntry(
                user_id=profile.id,
                display_name=profile.display_name or profile.email,
                xp=profile.xp,
                level=profile.level,
                updated_at=self._timestamp(),
            )
            self._store.set_ranking_entry(entry)
        return self._entry_with_position(entry)

    def _entry_with_position(self, entry: RankingEntry) -> RankingEntryOut:
        entries = self._sorted_entries()
        for index, ranked in enumerate(entries, start=1):
            if ranked.user_id == entry.user_id:
                return RankingEntryOut(
                    user_id=ranked.user_id,
                    display_name=ranked.display_name,
                    xp=ranked.xp,
                    level=ranked.level,
                    position=index,
                    updated_at=ranked.updated_at,
                )
        raise HTTPException(status_code=404, detail="Ranking entry not found")

    def _sorted_entries(self) -> List[RankingEntry]:
        entries = self._store.list_ranking()
        entries.sort(key=lambda entry: (-entry.xp, entry.user_id))
        return entries

    def _timestamp(self) -> str:
        return datetime.now(timezone.utc).isoformat()


_service = RankingService(store)


def get_ranking_service() -> RankingService:
    return _service

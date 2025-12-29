from typing import List, Optional

from fastapi import APIRouter, Depends, Header

from app.models.schemas import RankingEntryOut, RankingUpdateIn
from app.services.auth_service import AuthService, get_auth_service
from app.services.ranking_service import RankingService, get_ranking_service

router = APIRouter(prefix="/ranking", tags=["ranking"])


@router.post("/update", response_model=RankingEntryOut)
def update_ranking(
    payload: RankingUpdateIn,
    service: RankingService = Depends(get_ranking_service),
) -> RankingEntryOut:
    return service.update(payload.user_id, payload.xp, payload.level)


@router.get("/global", response_model=List[RankingEntryOut])
def get_global(
    service: RankingService = Depends(get_ranking_service),
) -> List[RankingEntryOut]:
    return service.global_ranking()


@router.get("/me", response_model=RankingEntryOut)
def get_me(
    authorization: Optional[str] = Header(default=None),
    auth_service: AuthService = Depends(get_auth_service),
    service: RankingService = Depends(get_ranking_service),
) -> RankingEntryOut:
    email = auth_service.get_authenticated_email(authorization)
    return service.get_me(email)

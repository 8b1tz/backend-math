from fastapi import APIRouter, Depends

from app.models.schemas import ProgressOut, ProgressUpdateIn
from app.services.progress_service import ProgressService, get_progress_service

router = APIRouter(prefix="/progress", tags=["progress"])


@router.post("/update", response_model=ProgressOut)
def update_progress(
    payload: ProgressUpdateIn,
    service: ProgressService = Depends(get_progress_service),
) -> ProgressOut:
    return service.update(payload.user_id, payload.xp_delta, payload.progress)


@router.get("/{user_id}", response_model=ProgressOut)
def get_progress(
    user_id: str,
    service: ProgressService = Depends(get_progress_service),
) -> ProgressOut:
    return service.get(user_id)

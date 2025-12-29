from fastapi import APIRouter, Depends

from app.models.schemas import ProfileOut, UserCreateIn, UserStatsOut, UserUpdateIn
from app.services.user_service import UserService, get_user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/{user_id}", response_model=ProfileOut)
def create_user(
    user_id: str,
    payload: UserCreateIn,
    service: UserService = Depends(get_user_service),
) -> ProfileOut:
    return service.create_profile(user_id, payload)


@router.get("/{user_id}", response_model=ProfileOut)
def get_user(
    user_id: str,
    service: UserService = Depends(get_user_service),
) -> ProfileOut:
    return service.get_profile(user_id)


@router.patch("/{user_id}", response_model=ProfileOut)
def update_user(
    user_id: str,
    payload: UserUpdateIn,
    service: UserService = Depends(get_user_service),
) -> ProfileOut:
    return service.update_profile(user_id, payload)


@router.get("/{user_id}/stats", response_model=UserStatsOut)
def get_user_stats(
    user_id: str,
    service: UserService = Depends(get_user_service),
) -> UserStatsOut:
    return service.get_stats(user_id)

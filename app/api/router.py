from fastapi import APIRouter

from app.api.routes import auth, game, health, logs, progress, questions, ranking, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(questions.router)
api_router.include_router(game.router)
api_router.include_router(progress.router)
api_router.include_router(ranking.router)
api_router.include_router(logs.router)
api_router.include_router(health.router)

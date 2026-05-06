from fastapi import APIRouter
from app.api import health, chat

router = APIRouter()
router.include_router(health.router, tags=["health"])
router.include_router(chat.router, prefix="/chat", tags=["chat"])

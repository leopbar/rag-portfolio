from fastapi import APIRouter
from app.api import admin, chat, health

router = APIRouter()
router.include_router(health.router, tags=["health"])
router.include_router(chat.router, prefix="/chat", tags=["chat"])
router.include_router(admin.router, tags=["admin"])

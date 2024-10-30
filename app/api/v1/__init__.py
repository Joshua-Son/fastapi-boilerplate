from fastapi import APIRouter

from app.api.v1 import arena
from app.api.v1 import participation

api_router = APIRouter()
api_router.include_router(arena.router, prefix="/arena", tags=["arena"])
api_router.include_router(participation.router, prefix="/participation", tags=["participation"])

from fastapi import APIRouter

from app.api.v1 import arenas, gamestreams, participation

api_router = APIRouter()
api_router.include_router(arenas.router, prefix="/arenas", tags=["arenas"])
api_router.include_router(participation.router, prefix="/participation", tags=["participation"])
api_router.include_router(gamestreams.router, prefix="/gamestreams", tags=["gamestreams"])

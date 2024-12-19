from fastapi import APIRouter
from app.api import files, sessions, health

api_route = APIRouter()

api_route.include_router(files.router, tags=["Files"])
api_route.include_router(sessions.router, tags=["Sessions"])
api_route.include_router(health.router, tags=["Health"])
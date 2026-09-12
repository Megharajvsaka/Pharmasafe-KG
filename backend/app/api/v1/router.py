"""
router.py
---------
Aggregates all API v1 routers into a single router.
"""

from fastapi import APIRouter
from backend.app.api.v1.endpoints.auth import router as auth_router
from backend.app.api.v1.endpoints.users import router as users_router
from backend.app.api.v1.endpoints.ddi import router as ddi_router
from backend.app.api.v1.endpoints.drugs import router as drugs_router
from backend.app.api.v1.endpoints.graph import router as graph_router
from backend.app.api.v1.endpoints.health import router as health_router
from backend.app.api.v1.endpoints.admin import router as admin_router

api_v1_router = APIRouter()

# Mount top-level endpoints for backward compatibility with frontend
api_v1_router.include_router(health_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(users_router)
api_v1_router.include_router(admin_router)
api_v1_router.include_router(ddi_router)
api_v1_router.include_router(drugs_router)
api_v1_router.include_router(graph_router)

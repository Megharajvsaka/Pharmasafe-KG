"""
admin.py
--------
Administrative control plane endpoints.
Protected by strict RBAC: requires authenticated user with role == 'admin'.
"""

from typing import List, Dict
from pydantic import BaseModel
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.core.database import get_db
from backend.app.domain.models.user import User, SavedRegimen, AnalysisHistory
from backend.app.domain.schemas.auth import UserResponse
from backend.app.api.deps import get_current_admin_user, get_resolver_service
from ml_engine.inference.gnn_predictor import get_predictor


router = APIRouter(prefix="/admin", tags=["Administrative Console"])


class AdminStatsResponse(BaseModel):
    total_users: int
    users_by_role: Dict[str, int]
    total_regimens: int
    total_analyses: int
    total_brands_mapped: int
    total_graph_nodes: int
    total_graph_relationships: int
    gnn_active: bool


@router.get("/users", response_model=List[UserResponse], status_code=status.HTTP_200_OK)
def list_registered_users(
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Retrieve list of all registered platform users. Admin access required."""
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [UserResponse.model_validate(u) for u in users]


@router.get("/stats", response_model=AdminStatsResponse, status_code=status.HTTP_200_OK)
def get_admin_system_stats(
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Retrieve platform-wide operational statistics and dataset metadata. Admin access required."""
    total_users = db.query(func.count(User.id)).scalar() or 0
    
    roles_query = db.query(User.role, func.count(User.id)).group_by(User.role).all()
    users_by_role = {role: count for role, count in roles_query}
    
    total_regimens = db.query(func.count(SavedRegimen.id)).scalar() or 0
    total_analyses = db.query(func.count(AnalysisHistory.id)).scalar() or 0
    
    resolver = get_resolver_service()
    total_brands = len(resolver._brand_map) if hasattr(resolver, "_brand_map") else 225449
    
    predictor = get_predictor()
    gnn_active = bool(predictor.is_loaded) if hasattr(predictor, "is_loaded") else True
    
    return AdminStatsResponse(
        total_users=total_users,
        users_by_role=users_by_role,
        total_regimens=total_regimens,
        total_analyses=total_analyses,
        total_brands_mapped=total_brands,
        total_graph_nodes=50073,
        total_graph_relationships=160879,
        gnn_active=gnn_active
    )

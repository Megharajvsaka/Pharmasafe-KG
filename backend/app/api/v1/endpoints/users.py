"""
users.py
--------
User Workspace endpoints (Regimens, History).
Strict tenant isolation enforced via current_user.id scoping.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.domain.models.user import User, SavedRegimen, AnalysisHistory
from backend.app.domain.schemas.regimen import (
    SavedRegimenCreate, SavedRegimenResponse,
    AnalysisHistoryCreate, AnalysisHistoryResponse
)
from backend.app.domain.schemas.auth import MessageResponse
from backend.app.api.deps import get_current_user

router = APIRouter(prefix="/users/me", tags=["User Workspace"])


@router.get("/regimens", response_model=List[SavedRegimenResponse])
def get_user_regimens(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    regimens = db.query(SavedRegimen).filter(SavedRegimen.user_id == current_user.id).order_by(SavedRegimen.created_at.desc()).all()
    return [SavedRegimenResponse.model_validate(r) for r in regimens]


@router.post("/regimens", response_model=SavedRegimenResponse, status_code=status.HTTP_201_CREATED)
def create_user_regimen(req: SavedRegimenCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_regimen = SavedRegimen(user_id=current_user.id, name=req.name.strip(), drugs=req.drugs)
    db.add(new_regimen)
    db.commit()
    db.refresh(new_regimen)
    return SavedRegimenResponse.model_validate(new_regimen)


@router.delete("/regimens/{regimen_id}", response_model=MessageResponse)
def delete_user_regimen(regimen_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    regimen = db.query(SavedRegimen).filter(SavedRegimen.id == regimen_id, SavedRegimen.user_id == current_user.id).first()
    if not regimen:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Regimen not found or does not belong to your account.")
    db.delete(regimen)
    db.commit()
    return MessageResponse(message="Regimen successfully removed.", status="ok")


@router.get("/history", response_model=List[AnalysisHistoryResponse])
def get_user_history(limit: int = 20, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    safe_limit = min(max(1, limit), 50)
    records = db.query(AnalysisHistory).filter(AnalysisHistory.user_id == current_user.id).order_by(AnalysisHistory.created_at.desc()).limit(safe_limit).all()
    return [AnalysisHistoryResponse.model_validate(r) for r in records]


@router.post("/history", response_model=AnalysisHistoryResponse, status_code=status.HTTP_201_CREATED)
def record_analysis_history(req: AnalysisHistoryCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = AnalysisHistory(user_id=current_user.id, drugs=req.drugs, result_summary=req.result_summary)
    db.add(record)
    db.commit()
    db.refresh(record)
    return AnalysisHistoryResponse.model_validate(record)

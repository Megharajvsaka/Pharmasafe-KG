"""
regimen.py
----------
Pydantic schemas for Saved Regimens and Analysis History.
"""

from datetime import datetime
from typing import List, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict


class SavedRegimenCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    drugs: List[str] = Field(..., min_length=2, max_length=10)

    @field_validator("drugs")
    @classmethod
    def validate_drugs(cls, v: List[str]) -> List[str]:
        cleaned = [d.strip() for d in v if d.strip()]
        if len(cleaned) < 2:
            raise ValueError("Regimen must contain at least 2 distinct medications.")
        if len(cleaned) > 10:
            raise ValueError("Maximum 10 medications allowed per regimen.")
        return cleaned


class SavedRegimenResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    name: str
    drugs: List[str]
    created_at: datetime
    updated_at: datetime


class AnalysisHistoryCreate(BaseModel):
    drugs: List[str] = Field(..., min_length=2, max_length=10)
    result_summary: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("drugs")
    @classmethod
    def validate_drugs(cls, v: List[str]) -> List[str]:
        return [d.strip() for d in v if d.strip()]


class AnalysisHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    drugs: List[str]
    result_summary: Dict[str, Any]
    created_at: datetime

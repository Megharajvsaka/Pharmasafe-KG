"""
ddi.py
------
Pydantic schemas for DDI Detection and Graph exploration.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator


class CheckRequest(BaseModel):
    drugs: List[str] = Field(..., min_length=2, max_length=10, description="List of 2 to 10 drug names")

    @field_validator("drugs")
    @classmethod
    def validate_drugs(cls, v: List[str]) -> List[str]:
        cleaned = [d.strip() for d in v if d.strip()]
        if len(cleaned) < 2:
            raise ValueError("At least 2 drug names required.")
        if len(cleaned) > 10:
            raise ValueError("Maximum 10 drugs allowed.")
        return cleaned


class EvidenceDetail(BaseModel):
    ingredient_a: Optional[str] = None
    ingredient_b: Optional[str] = None
    severity: Optional[str] = None
    mechanism: Optional[str] = None
    model: Optional[str] = None
    probability: Optional[float] = None
    threshold: Optional[float] = None
    evidence_type: Optional[str] = None


class InteractionResult(BaseModel):
    brand_a: str
    brand_b: str
    ingredient_a: str
    ingredient_b: str
    severity: str
    mechanism: str
    status: str = "documented"
    source: str = "knowledge_graph"
    confidence: Optional[float] = None
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    explanation: str


class SafePair(BaseModel):
    brand_a: str
    brand_b: str
    note: str
    status: str = "not_documented"


class ResolvedDrug(BaseModel):
    input: str
    matched_brand: str
    generics: List[str]
    match_type: str
    confidence: int
    review_required: bool = False


class CheckResponse(BaseModel):
    total_drugs: int
    brand_names: List[str]
    pairs_checked: int
    interactions_found: int
    safe_pairs: int
    interactions: List[InteractionResult]
    safe_pairs_detail: List[SafePair]
    summary: str
    resolved_drugs: List[ResolvedDrug] = Field(default_factory=list)

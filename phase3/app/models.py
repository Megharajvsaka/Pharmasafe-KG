"""
models.py
---------
Pydantic models for FastAPI request validation and response serialisation.
FastAPI uses these to auto-validate input and generate the /docs Swagger UI.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional


# ── Request models ────────────────────────────────────────────────────────────
class CheckRequest(BaseModel):
    """
    POST /check — input body.
    """
    drugs: list[str] = Field(
        ...,
        min_length=2,
        max_length=10,
        description="List of 2–10 Indian brand or generic drug names",
        examples=[["Combiflam", "Ecosprin", "Pantop 40", "Metformin 500"]],
    )

    @field_validator("drugs")
    @classmethod
    def validate_drugs(cls, v):
        cleaned = [d.strip() for d in v if d.strip()]
        if len(cleaned) < 2:
            raise ValueError("At least 2 non-empty drug names are required")
        if len(cleaned) > 10:
            raise ValueError("Maximum 10 drugs can be checked at once")
        return cleaned


# ── Response models ───────────────────────────────────────────────────────────
class ResolvedDrug(BaseModel):
    input:         str
    matched_brand: str
    generics:      list[str]
    match_type:    str   # "exact" | "fuzzy" | "alias" | "not_found"
    confidence:    int


class InteractionResult(BaseModel):
    brand_a:      str
    brand_b:      str
    ingredient_a: str
    ingredient_b: str
    severity:     str   # MAJOR | MODERATE | MINOR
    mechanism:    str
    explanation:  str   # XAI plain-English explanation


class SafePair(BaseModel):
    brand_a: str
    brand_b: str
    note:    str


class CheckResponse(BaseModel):
    total_drugs:        int
    brand_names:        list[str]
    pairs_checked:      int
    interactions_found: int
    safe_pairs:         int
    summary:            str
    interactions:       list[InteractionResult]
    safe_pairs_detail:  list[SafePair]
    resolved_drugs:     list[ResolvedDrug]


class DrugInfoResponse(BaseModel):
    brand_name:       str
    generics:         list[str]
    total_known_ddis: int
    major_count:      int
    moderate_count:   int
    minor_count:      int
    interactions:     list[dict]


class GraphNode(BaseModel):
    id:    str
    label: str
    type:  str
    color: str
    size:  int


class GraphEdge(BaseModel):
    from_node: str = Field(alias="from")
    to:        str
    label:     str
    color:     str
    width:     int

    class Config:
        populate_by_name = True


class GraphResponse(BaseModel):
    nodes: list[dict]
    edges: list[dict]


class SearchResponse(BaseModel):
    query:   str
    results: list[str]
    count:   int


class HealthResponse(BaseModel):
    status:       str
    neo4j:        str
    brands_loaded: int
    version:      str

"""
drug.py
-------
Pydantic schemas for Drug details and autocomplete searches.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class DrugInteractionItem(BaseModel):
    source_generic: str
    target_generic: str
    severity: str
    mechanism: str


class DrugInfoResponse(BaseModel):
    brand_name: str
    generics: List[str]
    total_known_ddis: int
    major_count: int
    moderate_count: int
    minor_count: int
    interactions: List[DrugInteractionItem]


class SearchResponse(BaseModel):
    query: str
    results: List[str]
    count: int


class GraphNode(BaseModel):
    id: str
    label: str
    type: str
    color: str
    size: int


class GraphEdge(BaseModel):
    from_: str = Field(alias="from")
    to: str
    label: str
    color: str
    dashes: bool
    width: int
    title: Optional[str] = None
    severity: Optional[str] = None


class GraphResponse(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]


class HealthResponse(BaseModel):
    status: str = "ok"
    neo4j: str
    gnn_loaded: bool
    brands_loaded: int
    version: str = "1.0.0"

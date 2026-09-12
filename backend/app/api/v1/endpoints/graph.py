"""
graph.py
--------
Graph visualization endpoint.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from backend.app.domain.schemas.drug import GraphResponse
from backend.app.services.resolver_service import ResolverService
from backend.app.infrastructure.neo4j_repository import Neo4jGraphRepository
from backend.app.api.deps import get_resolver_service, get_graph_repository

router = APIRouter(tags=["Visualisation"])


@router.get("/graph", response_model=GraphResponse)
def get_graph_visualization(
    drugs: List[str] = Query(..., description="List of drug names to visualise"),
    resolver: ResolverService = Depends(get_resolver_service),
    repo: Neo4jGraphRepository = Depends(get_graph_repository)
):
    if len(drugs) < 2:
        raise HTTPException(status_code=422, detail="At least 2 drug names required")

    resolved = resolver.resolve_multiple(drugs)
    generics_map = {name: r["generics"] for name, r in resolved.items() if r["generics"]}

    if len(generics_map) < 2:
        raise HTTPException(status_code=422, detail="Could not resolve enough drug names for graph visualisation")

    try:
        return repo.get_interaction_subgraph(generics_map)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

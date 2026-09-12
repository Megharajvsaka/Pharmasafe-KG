"""
drugs.py
--------
Drug details and brand name autocomplete search endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from backend.app.domain.schemas.drug import DrugInfoResponse, SearchResponse
from backend.app.services.resolver_service import ResolverService
from backend.app.infrastructure.neo4j_repository import Neo4jGraphRepository
from backend.app.api.deps import get_resolver_service, get_graph_repository

router = APIRouter(tags=["Drug Info & Search"])


@router.get("/search", response_model=SearchResponse)
def search_brand_autocomplete(
    q: str = Query(..., min_length=1, max_length=100),
    limit: int = Query(10, ge=1, le=50),
    resolver: ResolverService = Depends(get_resolver_service)
):
    results = resolver.search_brands(q, limit)
    return SearchResponse(query=q, results=results, count=len(results))


@router.get("/drug/{brand_name}", response_model=DrugInfoResponse)
def get_drug_monograph(
    brand_name: str,
    resolver: ResolverService = Depends(get_resolver_service),
    repo: Neo4jGraphRepository = Depends(get_graph_repository)
):
    resolved = resolver.resolve_multiple([brand_name])
    generics = resolved.get(brand_name, {}).get("generics", [])

    if not generics:
        raise HTTPException(status_code=404, detail=f"Drug '{brand_name}' not found in database.")

    try:
        return repo.get_drug_interactions(brand_name, generics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

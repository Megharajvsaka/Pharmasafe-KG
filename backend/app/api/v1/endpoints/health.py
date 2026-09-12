"""
health.py
---------
Health check and system status endpoints.
"""

from fastapi import APIRouter, Depends
from backend.app.domain.schemas.drug import HealthResponse
from backend.app.core.neo4j import get_driver
from backend.app.services.resolver_service import ResolverService
from ml_engine.inference.gnn_predictor import get_predictor
from backend.app.api.deps import get_resolver_service

router = APIRouter(tags=["Health"])


@router.get("/", response_model=HealthResponse)
@router.get("/health", response_model=HealthResponse)
def health_check(resolver: ResolverService = Depends(get_resolver_service)):
    try:
        driver = get_driver()
        with driver.session() as session:
            count = session.run("MATCH (i:Ingredient) RETURN count(i) AS c").single()["c"]
        neo4j_status = f"connected ({count:,} ingredients in graph)"
    except Exception as e:
        neo4j_status = f"error: {str(e)[:100]}"

    predictor = get_predictor()
    brands = resolver.brand_names

    return HealthResponse(
        status="ok",
        neo4j=neo4j_status,
        gnn_loaded=predictor.is_loaded if predictor else False,
        brands_loaded=len(brands),
        version="1.0.0",
    )

"""
ddi.py
------
Polypharmacy DDI Detection endpoint.
"""

from fastapi import APIRouter, Depends, HTTPException
from backend.app.domain.schemas.ddi import CheckRequest, CheckResponse
from backend.app.services.resolver_service import ResolverService
from backend.app.services.ddi_service import DDIService
from backend.app.api.deps import get_resolver_service, get_ddi_service

router = APIRouter(tags=["DDI Detection"])


@router.post("/check", response_model=CheckResponse)
def check_interactions(
    request: CheckRequest,
    resolver: ResolverService = Depends(get_resolver_service),
    ddi_service: DDIService = Depends(get_ddi_service)
):
    resolved = resolver.resolve_multiple(request.drugs)
    generics_map = {}
    not_found = []

    for name, r in resolved.items():
        if r["generics"]:
            generics_map[name] = r["generics"]
        else:
            not_found.append(name)

    if len(generics_map) < 2:
        raise HTTPException(
            status_code=422,
            detail=f"Could not resolve enough drug names to check interactions. Unresolved: {not_found}."
        )

    try:
        result = ddi_service.check_polypharmacy(generics_map)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Knowledge Graph query failed: {str(e)}")

    result["resolved_drugs"] = [
        {
            "input": r["input"],
            "matched_brand": r["matched_brand"],
            "generics": r["generics"],
            "match_type": r["match_type"],
            "confidence": r["confidence"],
            "review_required": r.get("review_required", False),
        }
        for r in resolved.values()
    ]

    for name in not_found:
        result["resolved_drugs"].append({
            "input": name,
            "matched_brand": name,
            "generics": [],
            "match_type": "not_found",
            "confidence": 0,
            "review_required": False,
        })

    return result

"""
main.py
-------
PharmaSafe-KG — FastAPI Backend
================================
Endpoints:
    GET  /              → health check + status
    GET  /health        → detailed health check
    GET  /search        → brand name autocomplete
    POST /check         → polypharmacy DDI detection  (CORE)
    GET  /drug/{name}   → full drug information
    GET  /graph         → graph data for Pyvis visualisation
    GET  /docs          → auto-generated Swagger UI (screenshot for paper)

Start server:
    cd pharmasafe-kg
    uvicorn phase3.app.main:app --reload --port 8000

Then open: http://localhost:8000/docs
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from phase3.app.database import get_driver, close_driver
from phase3.app.resolver import (
    load_resolver, resolve_multiple, search_brands, get_all_brand_names
)
from phase3.app.query_engine import (
    check_interactions, get_drug_info, get_interaction_graph
)
from phase3.app.models import (
    CheckRequest, CheckResponse, DrugInfoResponse,
    GraphResponse, SearchResponse, HealthResponse
)


# ── Startup / Shutdown ────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs on startup and shutdown."""
    # Startup: load resolver and verify Neo4j connection
    print("[SYSTEM] Loading Brand-to-Generic resolver...")
    brand_count = load_resolver()
    print(f"[SUCCESS] Resolver loaded: {brand_count:,} brand mappings")

    print("[SYSTEM] Verifying Neo4j connection...")
    try:
        get_driver()
        print("[SUCCESS] Neo4j AuraDB connected")
    except Exception as e:
        print(f"[ERROR] Neo4j connection failed: {e}")
        print("   Check .env file credentials and AuraDB instance status")

    yield

    # Shutdown: close DB connection cleanly
    close_driver()
    print("[INFO] Neo4j connection closed")


# ── App instance ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="PharmaSafe-KG API",
    description=(
        "Knowledge Graph-based Drug-Drug Interaction detection for Indian medicines. "
        "Supports polypharmacy checking with explainable AI (XAI) explanations. "
        "Maps Indian brand names to generic ingredients automatically."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",      # Swagger UI at /docs — screenshot this for paper
    redoc_url="/redoc",
)

# CORS — allow Streamlit frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # In production: restrict to your Streamlit URL
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINT 1 — Root / Health
# ═══════════════════════════════════════════════════════════════════════════════
@app.get("/", response_model=HealthResponse, tags=["Health"])
@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """
    Health check endpoint.
    Returns API status, Neo4j connectivity, and resolver stats.
    """
    # Test Neo4j connection
    try:
        driver = get_driver()
        with driver.session() as session:
            count = session.run(
                "MATCH (i:Ingredient) RETURN count(i) AS c"
            ).single()["c"]
        neo4j_status = f"connected ({count:,} ingredients in graph)"
    except Exception as e:
        neo4j_status = f"error: {str(e)[:100]}"

    brands = get_all_brand_names()

    return HealthResponse(
        status="ok",
        neo4j=neo4j_status,
        brands_loaded=len(brands),
        version="1.0.0",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINT 2 — Autocomplete Search
# ═══════════════════════════════════════════════════════════════════════════════
@app.get("/search", response_model=SearchResponse, tags=["Search"])
def search(
    q: str = Query(..., min_length=1, max_length=100,
                   description="Drug name prefix for autocomplete"),
    limit: int = Query(10, ge=1, le=50,
                       description="Maximum number of results"),
):
    """
    Autocomplete for Indian brand drug names.
    Used by the Streamlit multiselect dropdown.

    Example: GET /search?q=Combi
    Returns: ["Combiflam", "Combiflam Suspension", "Combimycin", ...]
    """
    results = search_brands(q, limit)
    return SearchResponse(query=q, results=results, count=len(results))


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINT 3 — DDI Check (CORE ENDPOINT)
# ═══════════════════════════════════════════════════════════════════════════════
@app.post("/check", response_model=CheckResponse, tags=["DDI Detection"])
def check(request: CheckRequest):
    """
    **Core endpoint — Polypharmacy Drug Interaction Detection**

    Accepts 2–10 Indian brand or generic drug names.
    For each pair, resolves brands to generics, queries the Knowledge Graph,
    and returns all detected interactions with XAI explanations.

    Example request body:
    ```json
    {"drugs": ["Combiflam", "Ecosprin", "Pantop 40", "Metformin 500"]}
    ```

    Returns severity-ranked interactions with mechanism explanations.
    """
    drug_names = request.drugs

    # Step 1: Resolve all brand names to generics
    resolved = resolve_multiple(drug_names)

    # Step 2: Build generics_map for the query engine
    generics_map = {}
    not_found = []

    for name, result in resolved.items():
        if result["generics"]:
            generics_map[name] = result["generics"]
        else:
            not_found.append(name)

    # If fewer than 2 brands could be resolved, we can't check interactions
    if len(generics_map) < 2:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Could not resolve enough drug names to check interactions. "
                f"Unresolved: {not_found}. "
                f"Please check the spelling of drug names."
            )
        )

    # Step 3: Run polypharmacy engine
    try:
        result = check_interactions(generics_map)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Knowledge Graph query failed: {str(e)}"
        )

    # Step 4: Attach resolved drug info to response
    result["resolved_drugs"] = [
        {
            "input":         r["input"],
            "matched_brand": r["matched_brand"],
            "generics":      r["generics"],
            "match_type":    r["match_type"],
            "confidence":    r["confidence"],
        }
        for r in resolved.values()
    ]

    # Add unresolved drugs as "not_found" entries
    for name in not_found:
        result["resolved_drugs"].append({
            "input":         name,
            "matched_brand": name,
            "generics":      [],
            "match_type":    "not_found",
            "confidence":    0,
        })

    return result


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINT 4 — Drug Info
# ═══════════════════════════════════════════════════════════════════════════════
@app.get("/drug/{brand_name}", response_model=DrugInfoResponse, tags=["Drug Info"])
def drug_info(brand_name: str):
    """
    Returns full information about a specific drug.
    Shows all known interactions for its generic ingredients.

    Example: GET /drug/Combiflam
    """
    resolved = resolve_multiple([brand_name])
    result   = resolved.get(brand_name, {})
    generics = result.get("generics", [])

    if not generics:
        raise HTTPException(
            status_code=404,
            detail=f"Drug '{brand_name}' not found in PharmaSafe-KG database."
        )

    try:
        info = get_drug_info(brand_name, generics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return info


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINT 5 — Graph Data (for Pyvis visualisation)
# ═══════════════════════════════════════════════════════════════════════════════
@app.get("/graph", response_model=GraphResponse, tags=["Visualisation"])
def graph(
    drugs: list[str] = Query(..., description="List of drug names to visualise")
):
    """
    Returns nodes and edges for the interactive Pyvis graph.
    Called by the Streamlit frontend after a /check query.

    Example: GET /graph?drugs=Combiflam&drugs=Ecosprin&drugs=Warfarin
    """
    if len(drugs) < 2:
        raise HTTPException(status_code=422, detail="At least 2 drug names required")

    resolved     = resolve_multiple(drugs)
    generics_map = {
        name: r["generics"]
        for name, r in resolved.items()
        if r["generics"]
    }

    if len(generics_map) < 2:
        raise HTTPException(
            status_code=422,
            detail="Could not resolve enough drug names for graph visualisation"
        )

    try:
        graph_data = get_interaction_graph(generics_map)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return graph_data

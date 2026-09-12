"""
main.py
-------
FastAPI Application Entrypoint (Clean Architecture).
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.core.database import init_db
from backend.app.core.neo4j import get_driver, close_driver
from backend.app.services.resolver_service import get_resolver
from ml_engine.inference.gnn_predictor import get_predictor
from backend.app.api.v1.router import api_v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI Application Lifespan."""
    print("[SYSTEM] Initializing relational database schema...")
    try:
        init_db()
        print("[SUCCESS] Relational database initialized")
    except Exception as e:
        print(f"[WARNING] Database initialization notice: {e}")

    print("[SYSTEM] Loading Brand-to-Generic resolver...")
    resolver = get_resolver()
    print(f"[SUCCESS] Resolver loaded: {len(resolver.brand_names):,} brand mappings")

    print("[SYSTEM] Initializing GNN Predictor...")
    try:
        predictor = get_predictor()
        if predictor.is_loaded:
            print("[SUCCESS] GNN Predictor active for fallback link prediction")
        else:
            print("[INFO] GNN Predictor running in fallback-only mode")
    except Exception as e:
        print(f"[WARNING] GNN initialization notice: {e}")

    print("[SYSTEM] Verifying Neo4j connection...")
    try:
        get_driver()
        print("[SUCCESS] Neo4j AuraDB connected")
    except Exception as e:
        print(f"[ERROR] Neo4j connection failed: {e}")

    yield

    close_driver()
    print("[INFO] Neo4j connection closed")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Knowledge Graph-based Drug-Drug Interaction detection for Indian medicines. "
        "Supports polypharmacy checking with explainable AI (XAI) explanations. "
        "Maps Indian brand names to generic ingredients automatically."
    ),
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router)

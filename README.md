# PharmaSafe-KG — Clean Architecture & Pharmaceutical Knowledge Graph

**PharmaSafe-KG** is an explainable polypharmacy Drug-Drug Interaction (DDI) detection system for Indian medicines. It integrates a **Biomedical Knowledge Graph (Neo4j AuraDB)**, **Inductive Graph Neural Networks (PyTorch Geometric GraphSAGE)**, and a **PostgreSQL-backed Multi-Tenant Workspace** behind a **Next.js 16 (React 19)** web interface and **FastAPI Clean Architecture Backend**.

---

## Architecture Overview (SOLID & Clean Architecture)

```text
pharmasafe-kg/
│
├── frontend/                     # [PRESENTATION LAYER] Next.js 16 App Router (React 19)
│   ├── src/
│   │   ├── app/                  # Web Routes: /, /analyze, /results, /drugs/[name], /graph, /demo, /dashboard
│   │   ├── components/           # UI, Feedback, Monograph & Graph Components
│   │   ├── context/              # AuthContext & AnalysisContext (In-Memory Token + SessionStorage)
│   │   └── lib/                  # REST API Client with credentials: "include"
│   └── package.json
│
├── backend/                      # [APPLICATION LAYER] FastAPI Clean Backend
│   ├── alembic/                  # PostgreSQL Schema Migrations
│   ├── alembic.ini
│   ├── app/
│   │   ├── api/                  # API Controllers & Routing (v1/endpoints/auth, ddi, drugs, users, graph)
│   │   │   ├── deps.py           # Dependency Injection (get_db, get_current_user, get_ddi_service)
│   │   │   └── v1/router.py      # Aggregated API v1 Router
│   │   ├── core/                 # Config (Pydantic), Security (Argon2id, JWT), Database Engine & Neo4j Pool
│   │   ├── domain/               # Enterprise Entities & Interfaces (Pure Python)
│   │   │   ├── interfaces/       # IDDIPredictor, IGraphRepository (DIP / OCP)
│   │   │   ├── models/           # SQLAlchemy 2.x ORM Models (User, RefreshToken, SavedRegimen, AnalysisHistory)
│   │   │   └── schemas/          # Pydantic DTOs (Request / Response validation)
│   │   ├── infrastructure/       # Neo4j Graph Repository (Parameterized Cypher queries)
│   │   ├── services/             # Application Services (DDIService, ResolverService, AuthService)
│   │   └── main.py               # FastAPI App Entrypoint & Lifespan
│
├── ml_engine/                    # [DATA SCIENCE & ML LAYER]
│   ├── artifacts/                # GraphSAGE weights (.pt) & Node Embeddings (1,761 drugs)
│   ├── inference/                # Production GNN Predictor (Implements IDDIPredictor)
│   ├── notebooks/                # Research Colab Notebooks (MP.ipynb)
│   └── training/                 # Offline training & dataset export pipelines
│
├── data_pipeline/                # [ETL & GRAPH PIPELINE]
│   ├── cleaning/                 # 1mg Indian Brand cleaners & DrugBank normalizers
│   └── neo4j_loader/             # Neo4j graph schema & relationship batch import scripts
│
├── legacy/                       # [HISTORICAL ARCHIVE]
│   └── streamlit/                # Phase 5 Streamlit Reference Prototype
│
├── tests/                        # [TEST SUITE - 65 PASSING TESTS]
│   ├── unit/                     # Fast unit tests (Resolvers, Security, Schemas)
│   ├── integration/              # API Endpoints & Auth Flow integration tests
│   ├── ml/                       # GNN Inference & Link Prediction tests
│   └── conftest.py               # Shared Pytest Fixtures
│
├── .env.example
└── requirements.txt
```

---

## Quickstart Guide

### 1. Backend Setup & Run (FastAPI on Port 8000)
```powershell
# Install dependencies
pip install -r requirements.txt

# Run database migrations
py -3.11 -m alembic upgrade head

# Start FastAPI server
py -3.11 -m uvicorn backend.app.main:app --reload --port 8000
```
- **API Swagger Documentation:** `http://localhost:8000/docs`
- **Health Check:** `http://localhost:8000/health`

### 2. Frontend Setup & Run (Next.js on Port 3000)
```powershell
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000` in your browser.

### 3. Run Automated Test Suite
```powershell
py -3.11 -m pytest tests/ -v
```

---

## Database Architecture
- **Local PostgreSQL (`pharmasafe` on localhost:5432):** Stores User accounts (`users`), Argon2id password hashes, rotating HttpOnly refresh tokens (`refresh_tokens`), saved user regimens (`saved_regimens`), and query execution history (`analysis_history`).
- **Cloud Neo4j AuraDB (`dd205fee`):** Stores 50,073 graph nodes and 160,879 biomedical relationships (`INTERACTS_WITH`, `CONTAINS`, `TARGETS`).
- **In-Memory GNN Model:** PyTorch GraphSAGE link prediction for unindexed combinations with confidence scoring.

---

## Scientific Checkpoint
- **Base Checkpoint:** `v1.0-p1-verified` (`c2a0079`)
- **ROCAUC:** 0.8834 | **F1-Score:** 0.8330
- **Brand Catalog:** 304,404 mappings | **Graph Entities:** 2,073 ingredients

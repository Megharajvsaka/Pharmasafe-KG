# PharmaSafe-KG — Complete Current-State Analysis

> **Analysis Date:** 2026-08-19  
> **Analyst Role:** Senior Software Architect, ML/NLP Researcher, KG Engineer  
> **Repository:** `c:\pharmasafe-kg`

---

# Confidence & Evidence

| Category | Details |
|---|---|
| **Directly verified from source code** | All 30+ Python source files read line-by-line. All CSV headers inspected. All configuration values extracted. All Cypher queries documented. All API routes traced. All data flow paths reconstructed. |
| **Verified from execution artifacts** | Pipeline report (`pipeline_report.txt`) confirms 248,373 Indian drugs processed, 100,000 DDI pairs. Validation report (`validation_report.txt`) confirms 48,000 Drug nodes, 2,073 Ingredient nodes, 100,000 INTERACTS_WITH edges, 71,512 CONTAINS edges loaded into Neo4j. Log files confirm successful Phase 1 & 2 execution. |
| **Inferred from code structure** | Phase 4 GNN integration with FastAPI (the `gnn_inference.py` module exists but is NOT imported in `phase3/app/main.py` — inference is not wired into the API). |
| **Found only in documentation** | CLAUDE.md mentions `drugs.csv` and `medicines_250k.csv` as inputs — neither file is present in `phase1/data/`. The code references `INDIAN_250K_CSV` but gracefully handles its absence. |
| **Could not be verified** | Neo4j AuraDB instance liveness (credentials in `.env` but cannot test connectivity). GNN model accuracy (weights files exist but no locally-verifiable metrics — Colab training required). ScispaCy model installation status (referenced in requirements but not actually used in any executed code path). |

---

## 1. Executive Summary

**PharmaSafe-KG** is a Knowledge Graph-based Drug-Drug Interaction (DDI) detection system specifically designed for **Indian medicines**. It solves the problem that Indian patients and pharmacists use brand names (e.g., "Combiflam", "Dolo 650") rather than international generic names (e.g., "ibuprofen", "paracetamol"), making standard DDI databases unusable.

The system is organized into **5 phases**:

| Phase | Purpose | Status |
|---|---|---|
| Phase 1 | Data preparation — clean Indian drugs, clean DrugBank/DDInter DDIs, fuzzy-match generics | ✅ Complete, executed |
| Phase 2 | Neo4j Knowledge Graph construction — schema, nodes, edges, validation | ✅ Complete, executed |
| Phase 3 | FastAPI REST backend + Streamlit excluded | ✅ Complete, functional |
| Phase 4 | GNN (GraphSAGE + GAT) training via Google Colab | 🟡 Training script exists, weights present, NOT integrated into API |
| Phase 5 | Streamlit clinical frontend | ✅ Complete, functional |

**Core novelty:** Indian brand name → generic ingredient resolution using fuzzy matching + alias maps, enabling polypharmacy DDI detection through a Neo4j knowledge graph with explainable mechanism descriptions.

---

## 2. Repository Structure

```
pharmasafe-kg/
├── .env                              # Neo4j AuraDB credentials (EXPOSED)
├── .streamlit/
│   └── secrets.toml                  # Streamlit config (API_BASE_URL)
├── CLAUDE.md                         # Project documentation for Claude Code
├── config.py                         # Central configuration (paths, thresholds, Neo4j)
├── requirements.txt                  # Python 3.10/3.11 dependencies
├── test_db_connection.py             # Standalone Neo4j connectivity test
│
├── phase1/                           # DATA PREPARATION PIPELINE
│   ├── run_phase1.py                 # Orchestrator — runs steps 1→2→3
│   ├── step1_load_indian_drugs.py    # Load & clean Indian medicine dataset
│   ├── step2_load_drugbank.py        # Load & clean DrugBank DDI + descriptions
│   ├── step2b_supplement_ddinter.py  # OPTIONAL — merge DDInter supplement
│   ├── step3_fuzzy_match.py          # Fuzzy match generics → build master table
│   ├── utils.py                      # Shared utilities (logging, normalization, parsing)
│   ├── data/                         # RAW INPUT DATASETS
│   │   ├── az_medicine_india.csv     # 32 MB — Kaggle AZ Medicine India
│   │   ├── drug_interactions.csv     # 15 MB — DrugBank DDI pairs
│   │   ├── drug_descriptions.csv     # 22 MB — DrugBank mechanism descriptions
│   │   └── ddinter_downloads_code_A.csv # 3.3 MB — DDInter supplement
│   ├── outputs/                      # PIPELINE OUTPUTS
│   │   ├── indian_drugs_cleaned.csv  # 25 MB — cleaned Indian drugs
│   │   ├── drugbank_ddi_cleaned.csv  # 22 MB — cleaned DDI pairs
│   │   ├── brand_generic_map.csv     # 15 MB — brand→generic mappings
│   │   ├── fuzzy_matched.csv         # 92 KB — fuzzy match results
│   │   ├── master_mapping_table.csv  # 29 MB — FINAL output for Neo4j
│   │   ├── unmatched_generics.csv    # 36 KB — low-confidence matches
│   │   └── pipeline_report.txt       # Summary statistics
│   └── logs/                         # Timestamped execution logs
│
├── phase2/                           # NEO4J KNOWLEDGE GRAPH CONSTRUCTION
│   ├── run_phase2.py                 # Orchestrator — runs steps 1→5
│   ├── step1_create_schema.py        # Constraints + indexes
│   ├── step2_load_ingredients.py     # Load Ingredient nodes
│   ├── step3_load_interactions.py    # Load INTERACTS_WITH edges
│   ├── step4_load_drugs.py           # Load Drug nodes + CONTAINS edges
│   ├── step5_validate.py             # 10-query validation suite
│   ├── utils_phase2.py               # Logger, print_section, batch helper
│   ├── outputs/
│   │   └── validation_report.txt     # Full validation results
│   └── logs/                         # 25 timestamped log files
│
├── phase3/                           # FASTAPI BACKEND
│   ├── __init__.py
│   ├── test_api.py                   # Integration test suite (6 test groups)
│   └── app/
│       ├── __init__.py
│       ├── main.py                   # FastAPI app + 5 endpoints
│       ├── database.py               # Neo4j connection manager (singleton)
│       ├── resolver.py               # Brand→generic resolver (in-memory)
│       ├── query_engine.py           # Cypher query engine (3 public functions)
│       └── models.py                 # Pydantic request/response models
│
├── phase4/                           # GNN TRAINING (Google Colab)
│   ├── step1_export_graph.py         # Export Neo4j → CSV for PyTorch Geometric
│   ├── PharmaSafe_GNN_Colab.py       # Full training script (GraphSAGE + GAT)
│   ├── gnn_inference.py              # Inference module (NOT integrated into API)
│   ├── graphsage_weights.pt          # 97 KB — trained GraphSAGE weights
│   ├── gat_weights.pt                # 167 KB — trained GAT weights
│   ├── node_embeddings.pt            # 594 KB — pre-computed node embeddings
│   ├── training_curves.png           # Training visualization
│   └── colab_data/                   # Exported graph for Colab
│       ├── nodes.csv                 # 2,073 ingredient nodes
│       ├── edges.csv                 # Positive + negative edge pairs
│       └── node_features.csv         # Hash-based node features
│
├── phase5/                           # STREAMLIT FRONTEND
│   └── streamlit_app.py              # Full clinical web interface
│
├── lib/                              # VENDORED JS LIBRARIES (for Pyvis/vis.js)
│   ├── bindings/utils.js             # vis.js utility bindings
│   ├── tom-select/                   # Tom Select autocomplete library
│   └── vis-9.1.2/                    # vis-network.js for graph visualization
│
└── venv/                             # Python virtual environment
```

### Directory Purposes

| Directory | Purpose |
|---|---|
| `phase1/` | Data ingestion, cleaning, fuzzy matching — converts raw CSVs into Neo4j-ready master mapping |
| `phase1/data/` | Raw input datasets (Kaggle, DrugBank, DDInter) |
| `phase1/outputs/` | Cleaned, processed, and merged CSVs |
| `phase2/` | Neo4j schema creation and batch data loading |
| `phase3/` | REST API layer — FastAPI backend with polypharmacy engine |
| `phase3/app/` | Core application modules (routes, models, resolver, query engine) |
| `phase4/` | ML/GNN layer — graph neural network training and inference |
| `phase4/colab_data/` | Exported graph data for Google Colab training |
| `phase5/` | User interface — Streamlit web application |
| `lib/` | Vendored JavaScript libraries for Pyvis graph rendering |
| `venv/` | Python virtual environment (local dependencies) |

---

## 3. Project Objective

### 3.1 Problem Statement
Indian patients and healthcare professionals use brand names (e.g., "Combiflam", "Dolo 650") rather than international generic names. Existing DDI databases (DrugBank, DDInter) only index generic names. This creates a dangerous gap where polypharmacy interactions go undetected in the Indian healthcare context.

### 3.2 Target Users
- Indian pharmacists checking prescription combinations
- Clinicians prescribing multiple medications
- Researchers studying DDI patterns in the Indian drug market

### 3.3 Research Objective
Build an explainable, knowledge-graph-based DDI detection system that bridges Indian brand names to international generic drug interaction databases, providing mechanism-level explanations for detected interactions.

### 3.4 Functional Objectives
1. Map Indian brand names → generic ingredients (with fuzzy matching for misspellings)
2. Detect drug-drug interactions across all pairwise combinations (polypharmacy)
3. Provide severity classification (MAJOR / MODERATE / MINOR)
4. Generate human-readable mechanism explanations (XAI)
5. Visualize drug interaction networks as interactive graphs
6. Expose functionality via REST API and web interface

### 3.5 Non-Functional Objectives
- Operate within Neo4j AuraDB free-tier limits (50K nodes, 175K relationships)
- Sub-second query response times for polypharmacy checks
- Explainability — every interaction includes a natural language mechanism description

### 3.6 Inputs
- Indian brand drug names (text strings, 2–10 at a time)

### 3.7 Outputs
- List of detected DDI interactions with severity + mechanism
- Resolved brand→generic mappings with confidence scores
- Interactive knowledge graph visualization
- Safe pair confirmations

### 3.8 End-to-End Workflow
```
User enters brand names (e.g., "Combiflam", "Ecosprin")
  ↓
Resolver: brand → generic via master_mapping_table.csv (exact + fuzzy + alias)
  ↓
Query Engine: pairwise Cypher queries against Neo4j KG
  ↓
Interaction Detection: INTERACTS_WITH edges between Ingredient nodes
  ↓
Explanation: mechanism text from edge properties
  ↓
API Response: severity-ranked interactions + XAI explanations
  ↓
Streamlit UI: severity cards + interactive Pyvis graph
```

### 3.9 Core Novelty
1. **Indian brand-to-generic resolution** using fuzzy string matching (thefuzz library)
2. **Drug name alias bridging** (paracetamol↔acetaminophen, aspirin↔acetylsalicylic acid)
3. **Hybrid KG**: DrugBank + DDInter merged with severity inference
4. **Explainability**: mechanism text stored as edge properties in the KG

### 3.10 Current Limitations
- No NLP model is actually used at runtime (scispaCy is in requirements but never imported in execution paths)
- GNN model (Phase 4) is trained but NOT integrated into the API
- Severity inference is keyword-based, not ML-based
- The resolver has a hard-coded `KNOWN_GENERICS` set (~45 entries) for direct generic input
- No user authentication or audit logging
- AuraDB free-tier caps constrain graph size

---

## 4. System Architecture

### 4.1 Actual Pipeline (reconstructed from code)

```
┌──────────────────────────────────────────────────────────────────┐
│                     PHASE 1: DATA PREPARATION                    │
│                                                                  │
│  az_medicine_india.csv ──→ step1_load_indian_drugs.py            │
│  (Kaggle, 32MB)              │                                   │
│                              ├→ Filter allopathic only           │
│                              ├→ Clean brand names                │
│                              ├→ Extract generics from composition│
│                              └→ indian_drugs_cleaned.csv         │
│                                                                  │
│  drug_interactions.csv ──→ step2_load_drugbank.py                │
│  drug_descriptions.csv       │                                   │
│  (DrugBank, 37MB)            ├→ Merge DDI pairs + descriptions   │
│                              ├→ Infer severity from keywords     │
│                              ├→ Add Indian name aliases           │
│                              ├→ Deduplicate (direction-agnostic)  │
│                              └→ drugbank_ddi_cleaned.csv (100K)  │
│                                                                  │
│  ddinter_downloads_code_A.csv ──→ step2b_supplement_ddinter.py   │
│  (DDInter, 3.3MB)                (OPTIONAL, supplements DDIs)     │
│                                                                  │
│  step3_fuzzy_match.py:                                           │
│    indian_drugs_cleaned.csv ─┐                                   │
│    drugbank_ddi_cleaned.csv ─┤→ Fuzzy match Indian generics      │
│                              │   against DrugBank vocabulary      │
│                              ├→ Build master_mapping_table.csv   │
│                              └→ unmatched_generics.csv           │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│                PHASE 2: KNOWLEDGE GRAPH CONSTRUCTION             │
│                                                                  │
│  step1_create_schema.py → Constraints + Indexes in Neo4j AuraDB │
│  step2_load_ingredients.py → 2,073 Ingredient nodes              │
│  step3_load_interactions.py → 100,000 INTERACTS_WITH edges       │
│  step4_load_drugs.py → 48,000 Drug nodes + 71,512 CONTAINS      │
│  step5_validate.py → 10-query validation suite                   │
│                                                                  │
│  Graph: (Drug)-[:CONTAINS]->(Ingredient)-[:INTERACTS_WITH]-(Ing) │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│                    PHASE 3: FASTAPI BACKEND                      │
│                                                                  │
│  Startup: load master_mapping_table.csv → in-memory resolver     │
│  Startup: verify Neo4j connection                                │
│                                                                  │
│  GET  /           → Health check                                 │
│  GET  /health     → Health + Neo4j status                        │
│  GET  /search?q=  → Autocomplete (prefix + fuzzy)                │
│  POST /check      → Polypharmacy DDI detection (CORE)            │
│  GET  /drug/{name}→ Single drug info                             │
│  GET  /graph      → Pyvis visualization data                     │
└──────────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────────┐
│                    PHASE 5: STREAMLIT FRONTEND                   │
│                                                                  │
│  Drug input with autocomplete → API /check call                  │
│  Severity cards (MAJOR/MODERATE/MINOR)                           │
│  Resolved drug display with match type + confidence              │
│  Interactive Pyvis graph visualization                           │
│  Quick demo presets                                              │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│              PHASE 4: GNN (STANDALONE — NOT INTEGRATED)          │
│                                                                  │
│  step1_export_graph.py → Export Neo4j → CSV                      │
│  PharmaSafe_GNN_Colab.py → Train GraphSAGE + GAT on Colab       │
│  gnn_inference.py → Inference module (EXISTS but NOT imported)   │
│                                                                  │
│  Output: graphsage_weights.pt, gat_weights.pt,                   │
│          node_embeddings.pt, training_curves.png                 │
└──────────────────────────────────────────────────────────────────┘
```

---

## 5. Technology Stack

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| Language | Python | 3.10/3.11 | All pipeline, backend, frontend code |
| Data Processing | pandas | 2.1.4 | CSV loading, cleaning, merging |
| Fuzzy Matching | thefuzz + python-Levenshtein | 0.22.1 / 0.25.1 | Brand→generic fuzzy resolution |
| NLP (listed) | scispaCy + spaCy | 0.5.4 / 3.7.4 | Listed in requirements, **NOT USED in execution** |
| Graph DB | Neo4j (AuraDB free tier) | 6.1.0 (driver) | Knowledge graph storage and queries |
| Backend | FastAPI + Uvicorn | 0.110.3 / 0.29.0 | REST API server |
| Validation | Pydantic | 2.7.1 | Request/response models |
| Frontend | Streamlit | 1.33.0 | Clinical web interface |
| Graph Viz | Pyvis | 0.3.2 | Interactive network visualization |
| ML (Phase 4) | PyTorch + PyTorch Geometric | N/A (Colab) | GraphSAGE + GAT training |
| Env Config | python-dotenv | 1.0.1 | .env file loading |
| Progress | tqdm | 4.66.2 | Progress bars for long loops |
| HTTP | requests | 2.31.0 | API test calls, Streamlit→API communication |
| JS (vendored) | vis-network.js | 9.1.2 | Graph rendering in browser |
| JS (vendored) | Tom Select | N/A | Autocomplete dropdown |

---

## 6. Data Sources

### 6.1 AZ Medicine Dataset of India (`az_medicine_india.csv`)

| Property | Value |
|---|---|
| **Source** | Kaggle: shudhanshusingh/az-medicine-dataset-of-india |
| **Location** | `phase1/data/az_medicine_india.csv` |
| **Size** | 32 MB |
| **Format** | CSV |
| **Present** | ✅ Yes |
| **Columns** | `id`, `name`, `price(₹,1)`, `Is_discontinued`, `manufacturer_name`, `type`, `pack_size_label`, `short_composition1`, `short_composition2` |
| **Used as** | Source of Indian brand→generic mappings |
| **Record count** | ~248,373 rows (after cleaning, per pipeline report) |

### 6.2 Drug Interactions (`drug_interactions.csv`)

| Property | Value |
|---|---|
| **Source** | DrugBank (renamed from `DDI_data.csv`) |
| **Location** | `phase1/data/drug_interactions.csv` |
| **Size** | 15 MB |
| **Columns** | `drug1_id`, `drug2_id`, `drug1_name`, `drug2_name`, `interaction_type` |
| **Record count** | 222,696 rows, 1,868 unique drugs (per code comments) |
| **Present** | ✅ Yes |

### 6.3 Drug Descriptions (`drug_descriptions.csv`)

| Property | Value |
|---|---|
| **Source** | DrugBank (renamed from `db_drug_interactions.csv`) |
| **Location** | `phase1/data/drug_descriptions.csv` |
| **Size** | 22 MB |
| **Columns** | `Drug 1`, `Drug 2`, `Interaction Description` |
| **Record count** | 191,541 rows |
| **Present** | ✅ Yes |

### 6.4 DDInter Supplement (`ddinter_downloads_code_A.csv`)

| Property | Value |
|---|---|
| **Source** | DDInter database |
| **Location** | `phase1/data/ddinter_downloads_code_A.csv` |
| **Size** | 3.3 MB |
| **Columns** | `DDInterID_A`, `Drug_A`, `DDInterID_B`, `Drug_B`, `Level` |
| **Present** | ✅ Yes |
| **Usage** | Optional supplement — adds explicit severity labels |

### 6.5 Datasets Referenced but NOT Present

| Dataset | Config Reference | Status |
|---|---|---|
| `drugs.csv` | `config.py: DRUGBANK_DRUGS_CSV` | 🔴 File not found in `phase1/data/` |
| `medicines_250k.csv` | `config.py: INDIAN_250K_CSV` | 🔴 File not found in `phase1/data/` |

Both are gracefully handled — the code skips them if missing.

---

## 7. Data Pipeline

### 7.1 Complete Data Flow

```
RAW DATA (4 CSVs in phase1/data/)
    ↓
STEP 1: Indian Drug Loading & Cleaning
  ├─ Load az_medicine_india.csv (+ optional medicines_250k.csv)
  ├─ Filter: allopathic drugs only (regex: "allopathy|allopathic")
  ├─ Drop: missing brand_name or composition
  ├─ Combine: short_composition1 + short_composition2
  ├─ Clean brand names: strip dosage forms (tablet, capsule, syrup, etc.)
  ├─ Extract generics: regex parsing of composition strings
  │   └─ "Ibuprofen 400mg + Paracetamol 325mg" → ["ibuprofen", "paracetamol"]
  ├─ Deduplicate by (brand_name, composition)
  └─ OUTPUT: indian_drugs_cleaned.csv (248,373 rows)
    ↓
STEP 2: DrugBank DDI Loading & Cleaning
  ├─ Load drug_interactions.csv (DDI pairs)
  ├─ Load drug_descriptions.csv → build (drug1, drug2) → description dict
  ├─ Merge: attach mechanism descriptions to DDI pairs
  ├─ Infer severity: keyword-based (MAJOR_KEYWORDS, MINOR_KEYWORDS → MODERATE default)
  ├─ Normalize drug names: normalize_name() strips dosage, forms, salts
  ├─ Add alias rows: paracetamol↔acetaminophen, aspirin↔acetylsalicylic acid, etc.
  ├─ Remove self-interactions
  ├─ Direction-agnostic dedup: sorted pair_key, keep highest severity
  ├─ AuraDB budget trim: cap at 100K DDI edges (MAJOR first)
  └─ OUTPUT: drugbank_ddi_cleaned.csv (100,000 rows)
    ↓
STEP 2b (OPTIONAL): DDInter Supplement
  ├─ Load ddinter_downloads_code_A.csv
  ├─ Drop Unknown severity
  ├─ Normalize names, build pair_keys
  ├─ Merge: add only pairs NOT already in DrugBank data
  ├─ Re-apply 100K budget
  └─ OUTPUT: drugbank_ddi_cleaned.csv (updated)
    ↓
STEP 3: Fuzzy Matching & Master Table
  ├─ Build brand_generic_map from indian_drugs_cleaned.csv
  ├─ Build DrugBank vocabulary from drugbank_ddi_cleaned.csv (1,759 unique names)
  ├─ Fuzzy match: each of 1,696 Indian generics → best DrugBank match
  │   ├─ Scorer: fuzz.token_sort_ratio
  │   ├─ HIGH (≥90): auto-accept
  │   ├─ MEDIUM (75–89): accept, flag for review
  │   ├─ LOW (60–74): manual review required
  │   └─ REJECT (<60): no match
  ├─ Explode brand-generic pairs to long format
  ├─ Merge with fuzzy match results
  ├─ Filter: keep only HIGH + MEDIUM confidence
  ├─ Count DDI records per matched generic
  ├─ Validate known mappings (8 spot checks)
  └─ OUTPUT: master_mapping_table.csv (304,404 rows)
```

### 7.2 Key Normalization Function: `normalize_name()`

Located in [utils.py](file:///c:/pharmasafe-kg/phase1/utils.py#L52-L95):

1. Lowercase + strip whitespace
2. Remove dosage patterns: `\(?\\d+\\.?\\d*\\s*(mg|mcg|g|ml|iu|%|units?).*?\)?`
3. Remove form words: tablet, capsule, syrup, injection, cream, gel, etc.
4. Remove parentheses and brackets
5. Remove trailing qualifiers: hydrochloride, sodium, potassium, maleate, etc.
6. Collapse multiple spaces

### 7.3 Key Parsing Function: `extract_generics_from_composition()`

Located in [utils.py](file:///c:/pharmasafe-kg/phase1/utils.py#L98-L143):

1. Split composition on `+`, `|`, `/` delimiters
2. For each part, try regex: `^([A-Za-z][A-Za-z\s\-]+?)(?:\s*\(|\s*\d)` to extract name before dosage
3. Fallback: normalize entire part
4. Filter: must be ≥3 chars and contain a letter
5. Deduplicate preserving order

---

## 8. Drug Entity Resolution

### 8.1 Brand Detection (Phase 3 Resolver)

The resolver in [resolver.py](file:///c:/pharmasafe-kg/phase3/app/resolver.py) implements a 4-tier resolution strategy:

**Tier 1 — Exact Match** (confidence: 100)
```python
if name_lower in _brand_to_generics:  # O(1) dict lookup
    return {"match_type": "exact", "confidence": 100, ...}
```

**Tier 2 — Direct Alias** (confidence: 100)
```python
ALIASES = {
    "paracetamol": "acetaminophen",
    "aspirin": "acetylsalicylic acid",
    "adrenaline": "epinephrine",
    "salbutamol": "albuterol",
    "frusemide": "furosemide",
    # bidirectional
}
```

**Tier 3 — Known Generics** (confidence: 100)
Hard-coded set of ~45 common generic names (warfarin, ibuprofen, metformin, etc.) that can be typed directly.

**Tier 4 — Fuzzy Match** (confidence: 80+)
```python
fuzz_process.extractOne(name, _all_brand_names, scorer=fuzz.token_sort_ratio)
# Accepts only if score >= 80
```

**Tier 5 — Not Found** (confidence: 0)

### 8.2 Alias Expansion

The `_expand_aliases()` function adds both forms for every resolved generic:
- Input: `["acetylsalicylic acid"]`
- Output: `["acetylsalicylic acid", "aspirin"]`

This ensures Cypher queries match either name in the graph.

### 8.3 Combination Drug Handling

Handled at Phase 1 composition parsing:
- `"Ibuprofen 400mg + Paracetamol 325mg"` → `["ibuprofen", "paracetamol"]`
- Each generic is independently matched and stored in `generics_str` (pipe-separated)

### 8.4 Spelling Variation Handling

- Phase 1 `step3_fuzzy_match.py`: `token_sort_ratio` handles word-order variations
- Phase 3 `resolver.py`: Runtime fuzzy match with threshold ≥80 for autocorrection
- Salt form stripping: `normalize_name()` removes "hydrochloride", "sodium", etc.

### 8.5 Concrete Example from Data

```
Brand: "Augmentin 625 Duo"
Composition: "Amoxycillin (500mg), Clavulanic Acid (125mg)"
Indian generic: "amoxycillin"
DrugBank match: "amoxicillin" (score: 91, HIGH)
DDI count: 8
```

### 8.6 Failure Cases

From `unmatched_generics.csv`:
- `abatacept` → matched to `cabazitaxel` (score: 60, LOW) — FALSE MATCH
- `abciximab` → matched to `nabiximols` (score: 63, LOW) — FALSE MATCH
- `abiraterone acetate` → matched to `abiraterone` (score: 73, LOW) — CORRECT but below threshold

---

## 9. Knowledge Graph

### 9.1 Graph Database Technology

| Property | Value |
|---|---|
| Database | Neo4j AuraDB (free tier) |
| Connection | `neo4j+s://` protocol (TLS encrypted) |
| Query Language | Cypher |
| Driver | neo4j Python driver 6.1.0 |
| Instance | `dd205fee.databases.neo4j.io` |

### 9.2 Node Types

#### Ingredient Node
| Property | Type | Source | Example |
|---|---|---|---|
| `name` | string (UNIQUE) | DrugBank/DDInter normalized name | `"warfarin"` |
| `display_name` | string | Original casing | `"Warfarin"` |
| `drugbank_id` | string | DrugBank ID | `"DB00682"` or DDInter ID |
| `source` | string | Data provenance | `"drugbank"` |
| `created_at` | datetime | Neo4j server time | auto-generated |

**Count:** 2,073 nodes (verified from validation report)

#### Drug Node
| Property | Type | Source | Example |
|---|---|---|---|
| `name` | string (UNIQUE) | Indian brand name | `"Combiflam"` |
| `manufacturer` | string | Kaggle dataset | `"Sanofi India Ltd"` |
| `in_graph` | boolean | Always `true` | `true` |
| `created_at` | datetime | Neo4j server time | auto-generated |

**Count:** 48,000 nodes (priority-selected from 225,449 brands with DDI data)

### 9.3 Relationship Types

#### INTERACTS_WITH
| Property | Type | Example |
|---|---|---|
| `severity` | string | `"MAJOR"`, `"MODERATE"`, `"MINOR"` |
| `mechanism` | string (≤500 chars) | `"Warfarin may increase the anticoagulant activities of Nimesulide."` |
| `interaction_type` | string (≤200 chars) | `"risk or severity of bleeding"` |
| `pair_key` | string (MERGE key) | `"ibuprofen\|warfarin"` |
| `created_at` | datetime | auto-generated |

**Direction:** `(a)-[:INTERACTS_WITH]->(b)` where `a < b` alphabetically  
**Queries:** Direction-agnostic using `(a)-[r:INTERACTS_WITH]-(b)`  
**Count:** 100,000 edges  
**Severity breakdown:** 87,868 MAJOR, 12,132 MODERATE (from validation report)

#### CONTAINS
| Property | Type | Example |
|---|---|---|
| `created_at` | datetime | auto-generated |

**Direction:** `(d:Drug)-[:CONTAINS]->(i:Ingredient)`  
**Count:** 71,512 edges

### 9.4 Graph Schema

```
(:Drug {name, manufacturer, in_graph, created_at})
  │
  ├──[:CONTAINS {created_at}]──>(:Ingredient {name, display_name, drugbank_id, source, created_at})
  │                                │
  │                                ├──[:INTERACTS_WITH {severity, mechanism,
  │                                │    interaction_type, pair_key, created_at}]──>(:Ingredient)
  │                                │
  │                                └──[:INTERACTS_WITH]──<(:Ingredient)
  │
  └──[:CONTAINS]──>(:Ingredient) ...
```

### 9.5 Constraints and Indexes

From [step1_create_schema.py](file:///c:/pharmasafe-kg/phase2/step1_create_schema.py#L64-L93):

```cypher
-- Uniqueness constraints (also create indexes)
CREATE CONSTRAINT drug_name_unique IF NOT EXISTS FOR (d:Drug) REQUIRE d.name IS UNIQUE
CREATE CONSTRAINT ingredient_name_unique IF NOT EXISTS FOR (i:Ingredient) REQUIRE i.name IS UNIQUE

-- Additional indexes
CREATE INDEX drug_name_idx IF NOT EXISTS FOR (d:Drug) ON (d.name)
CREATE INDEX ingredient_name_idx IF NOT EXISTS FOR (i:Ingredient) ON (i.name)
CREATE INDEX drug_manufacturer_idx IF NOT EXISTS FOR (d:Drug) ON (d.manufacturer)
```

### 9.6 Key Cypher Queries

**DDI Detection** (from [query_engine.py](file:///c:/pharmasafe-kg/phase3/app/query_engine.py#L113-L121)):
```cypher
MATCH (a:Ingredient {name: $g_a})-[r:INTERACTS_WITH]-(b:Ingredient {name: $g_b})
RETURN a.name AS ingredient_a, b.name AS ingredient_b,
       r.severity AS severity, r.mechanism AS mechanism
LIMIT 1
```

**Drug Info** (from [query_engine.py](file:///c:/pharmasafe-kg/phase3/app/query_engine.py#L189-L203)):
```cypher
MATCH (i:Ingredient {name: $name})-[r:INTERACTS_WITH]-(other:Ingredient)
RETURN i.name AS source, other.name AS target,
       r.severity AS severity, r.mechanism AS mechanism
ORDER BY CASE r.severity WHEN 'MAJOR' THEN 0 WHEN 'MODERATE' THEN 1 ELSE 2 END
LIMIT 20
```

**Graph Visualization** (from [query_engine.py](file:///c:/pharmasafe-kg/phase3/app/query_engine.py#L275-L281)):
```cypher
UNWIND $drugs AS d1
UNWIND $drugs AS d2
WITH d1, d2 WHERE d1 < d2
MATCH (a:Ingredient {name: d1})-[r:INTERACTS_WITH]-(b:Ingredient {name: d2})
RETURN a.name AS a, b.name AS b, r.severity AS sev, r.mechanism AS mech
```

### 9.7 Graph Statistics (from validation report)

| Metric | Value |
|---|---|
| Total nodes | 50,073 (limit: 50,000 — slightly exceeded) |
| Total relationships | 171,512 (limit: 175,000) |
| Avg connections/ingredient | 96.5 |
| Max connections (most connected) | 522 (clarithromycin) |
| Min connections | 1 |
| Query time (DDI pair) | ~190ms |
| Query time (autocomplete) | ~79ms |
| Query time (polypharmacy 4 drugs) | ~104ms |

### 9.8 Planned but NOT Implemented Node Types

From comments in [step1_create_schema.py](file:///c:/pharmasafe-kg/phase2/step1_create_schema.py#L17-L20):
```
Future node types (Phase 3 — GNN):
    (:Enzyme)      — CYP450 enzymes
    (:SideEffect)  — Adverse effects
    (:Disease)     — Conditions treated
```
**Status:** 🔴 NOT IMPLEMENTED — no code exists for these.

---

## 10. Interaction Detection

### 10.1 Detection Method

The system uses **Knowledge Graph traversal** as its primary (and only active) detection method.

**Algorithm** (from [query_engine.py](file:///c:/pharmasafe-kg/phase3/app/query_engine.py#L18-L104) `check_interactions()`):

```
Input: generics_map = {brand_name: [generic1, generic2, ...], ...}

1. Generate all unique brand pairs: C(n, 2)
2. For each brand pair (A, B):
   a. Get generics_a = generics for brand A
   b. Get generics_b = generics for brand B
   c. For each (g_a, g_b) in cross-product:
      - Skip if g_a == g_b
      - Run Cypher: MATCH (a:Ingredient {name: g_a})-[r:INTERACTS_WITH]-(b:Ingredient {name: g_b})
      - If found → record interaction with severity, mechanism
   d. Keep highest-severity interaction per brand pair
3. Sort all interactions: MAJOR → MODERATE → MINOR
4. Return interactions + safe pairs + summary
```

### 10.2 Interaction Types

Only DDI (drug-drug interactions). Specifically:
- **Pharmacokinetic**: serum concentration changes, bioavailability, absorption, excretion
- **Pharmacodynamic**: QTc-prolonging, serotonin syndrome, bleeding risk, hypoglycemia

### 10.3 Severity Classification

**Source-based:**
- DDInter pairs: explicitly labeled (Major/Moderate/Minor)
- DrugBank pairs: inferred via keyword matching in `interaction_type`

**Keyword-based severity inference** (from [step2_load_drugbank.py](file:///c:/pharmasafe-kg/phase1/step2_load_drugbank.py#L54-L72)):

| Severity | Keywords |
|---|---|
| MAJOR | qtc-prolonging, rhabdomyolysis, serotonin, cardiotoxic, hepatotoxic, neurotoxic, hyperkalemia, renal failure, bleeding, hypoglycemic, anticoagulant, antiplatelet |
| MINOR | absorption, excretion, bioavailability, photosensitizing, diagnostic |
| MODERATE | Everything else (default) |

### 10.4 NOT Implemented

- ❌ ML-based interaction detection (GNN inference module exists but is not called)
- ❌ Confidence scoring for interactions (all KG edges treated equally)
- ❌ Food/drug interactions
- ❌ Disease/drug interactions
- ❌ Duplicate therapy detection
- ❌ Contraindication checking

---

## 11. Explainability (XAI)

### 11.1 Explanation Generation

The XAI explanation is built by `_build_explanation()` in [query_engine.py](file:///c:/pharmasafe-kg/phase3/app/query_engine.py#L135-L156):

```python
def _build_explanation(brand_a, ing_a, brand_b, ing_b, severity, mechanism):
    return (
        f"{sev_text}: {brand_a} and {brand_b} interact.\n\n"
        f"{brand_a} contains {ing_a.title()}. "
        f"{brand_b} contains {ing_b.title()}.\n\n"
        f"Mechanism: {mech}"
    )
```

### 11.2 Concrete Example (from validation report)

```
⚠️ MAJOR RISK: Combiflam and Ecosprin interact.

Combiflam contains Paracetamol. Ecosprin AV 150/20 contains Atorvastatin.

Mechanism: The risk or severity of adverse effects can be increased when
Acetaminophen is combined with Atorvastatin.
```

### 11.3 Explanation Components

| Component | Source | Type |
|---|---|---|
| Severity label | KG edge `r.severity` | Rule-based (MAJOR/MODERATE/MINOR) |
| Brand names | User input | Direct passthrough |
| Generic ingredients | Resolver output | Dictionary lookup |
| Mechanism text | KG edge `r.mechanism` | From DrugBank `Interaction Description` or DDInter-generated |
| Graph path | Implicit in query | Drug→CONTAINS→Ingredient→INTERACTS_WITH→Ingredient←CONTAINS←Drug |

### 11.4 What is Explainable vs Black-Box

| Aspect | Classification | Evidence |
|---|---|---|
| Brand→generic resolution | ✅ Fully explainable | match_type + confidence score shown |
| Interaction detection | ✅ Fully explainable | Direct graph traversal, path is transparent |
| Severity classification | 🟡 Partially explainable | Source label or keyword inference, not explained to user |
| Mechanism description | ✅ Fully explainable | Plain-English text from DrugBank |
| GNN predictions | 🔴 Would be black-box | Dot product of embeddings — but NOT integrated |

---

## 12. ML/NLP

### 12.1 GNN Models (Phase 4)

#### GraphSAGE_DDI

| Property | Value |
|---|---|
| Model file | [PharmaSafe_GNN_Colab.py](file:///c:/pharmasafe-kg/phase4/PharmaSafe_GNN_Colab.py#L154-L201) |
| Framework | PyTorch + PyTorch Geometric |
| Architecture | 3-layer SAGEConv (in→128→64→32) + BatchNorm + Dropout(0.3) |
| Task | Link prediction (binary: interaction exists or not) |
| Decoder | Dot product of node embeddings → sigmoid |
| Training | Google Colab (T4 GPU), 100 epochs, early stopping (patience=15) |
| Optimizer | Adam (lr=0.001, weight_decay=5e-4) + ReduceLROnPlateau |
| Weights file | `phase4/graphsage_weights.pt` (97 KB) |
| Embeddings file | `phase4/node_embeddings.pt` (594 KB) |
| Status | 🟡 Trained (weights exist), NOT integrated into API |

#### GAT_DDI

| Property | Value |
|---|---|
| Model file | [PharmaSafe_GNN_Colab.py](file:///c:/pharmasafe-kg/phase4/PharmaSafe_GNN_Colab.py#L204-L230) |
| Architecture | 2-layer GATConv (in→64×4heads→32) + Dropout(0.3) |
| Purpose | Paper comparison model (Table 2) |
| Weights file | `phase4/gat_weights.pt` (167 KB) |
| Status | 🟡 Trained (weights exist), NOT integrated into API |

#### GNN Inference Module

[gnn_inference.py](file:///c:/pharmasafe-kg/phase4/gnn_inference.py) provides a `GNNPredictor` class with:
- `load()` — loads pre-computed embeddings
- `predict(drug_a, drug_b)` → probability 0.0–1.0
- `predict_batch()` — batch predictions
- `get_top_interactions()` — exploratory analysis

**Critical finding:** This module is **never imported** by `phase3/app/main.py`. The API uses direct Neo4j queries only.

#### Node Features

From [step1_export_graph.py](file:///c:/pharmasafe-kg/phase4/step1_export_graph.py#L139-L168):
- `has_drugbank_id`: binary (1/0)
- `hash_feat_0` through `hash_feat_7`: 8 binary features from name hash
- Degree (added during training): normalized node degree

Total features: 10 per node (9 from CSV + 1 degree computed in Colab)

### 12.2 NLP Models

**scispaCy (`en_ner_bc5cdr_md`):**
- Listed in `config.py` line 44: `SCISPACY_MODEL = "en_ner_bc5cdr_md"`
- Listed in `requirements.txt` lines 15–18
- **NOT imported or used in ANY execution code path**
- Status: 🗑️ UNUSED — the entity resolution uses regex + fuzzy matching instead

### 12.3 Prompts / LLMs

**None.** No LLM prompts, no GPT/Claude API calls, no prompt templates found anywhere in the codebase.

---

## 13. Backend

### 13.1 Framework

FastAPI 0.110.3 with Uvicorn 0.29.0

### 13.2 Application Setup

[main.py](file:///c:/pharmasafe-kg/phase3/app/main.py):
- Lifespan context manager loads resolver + verifies Neo4j on startup
- CORS: `allow_origins=["*"]` (all origins allowed)
- Swagger UI at `/docs`, ReDoc at `/redoc`

### 13.3 API Endpoints

#### `GET /` and `GET /health`

| Property | Value |
|---|---|
| Response model | `HealthResponse` |
| Purpose | Health check + Neo4j status |
| Auth | None |
| DB operation | `MATCH (i:Ingredient) RETURN count(i) AS c` |

#### `GET /search?q={query}&limit={n}`

| Property | Value |
|---|---|
| Response model | `SearchResponse` |
| Purpose | Brand name autocomplete |
| Auth | None |
| DB operation | None (in-memory search) |
| Logic | Prefix match → fuzzy fallback (partial_ratio ≥ 60) |

#### `POST /check` ⭐ CORE ENDPOINT

| Property | Value |
|---|---|
| Request model | `CheckRequest` (`{"drugs": ["Combiflam", "Ecosprin"]}`) |
| Response model | `CheckResponse` |
| Validation | 2–10 drugs, non-empty strings |
| Auth | None |
| Logic | resolve_multiple() → check_interactions() → build response |
| DB operations | Pairwise Cypher INTERACTS_WITH queries |
| Error handling | 422 if < 2 drugs resolved, 500 if Neo4j fails |

#### `GET /drug/{brand_name}`

| Property | Value |
|---|---|
| Response model | `DrugInfoResponse` |
| Purpose | Single drug detail with all known interactions |
| Auth | None |
| DB operation | All INTERACTS_WITH for each generic (limit 20 per generic) |

#### `GET /graph?drugs=A&drugs=B`

| Property | Value |
|---|---|
| Response model | `GraphResponse` |
| Purpose | Pyvis graph visualization data |
| Auth | None |
| DB operation | Batch INTERACTS_WITH between all resolved generics |
| Returns | `{nodes: [...], edges: [...]}` |

### 13.4 Backend Modules

| Module | Purpose |
|---|---|
| [database.py](file:///c:/pharmasafe-kg/phase3/app/database.py) | Neo4j singleton driver (connection pooling) |
| [resolver.py](file:///c:/pharmasafe-kg/phase3/app/resolver.py) | In-memory brand→generic resolver |
| [query_engine.py](file:///c:/pharmasafe-kg/phase3/app/query_engine.py) | Cypher query functions |
| [models.py](file:///c:/pharmasafe-kg/phase3/app/models.py) | Pydantic models (8 model classes) |

### 13.5 Environment Variables Used by Backend

| Variable | Source | Used in |
|---|---|---|
| `NEO4J_URI` | `.env` | `database.py`, `config.py` |
| `NEO4J_USER` / `NEO4J_USERNAME` | `.env` | `database.py`, `config.py` |
| `NEO4J_PASSWORD` | `.env` | `database.py`, `config.py` |

---

## 14. Frontend

### 14.1 Technology

Streamlit 1.33.0 — single-file application: [streamlit_app.py](file:///c:/pharmasafe-kg/phase5/streamlit_app.py) (502 lines)

### 14.2 Pages and Layout

Single page with two-column layout:
- **Left column (1/3):** Drug input, autocomplete suggestions, selected drug chips, quick demo presets, check button
- **Right column (2/3):** Summary banner, resolved drug display, severity cards, safe pairs, interactive Pyvis graph

### 14.3 User Flow

1. User types drug name in text input
2. Autocomplete suggestions appear (from `GET /search`)
3. User clicks suggestion or manually adds drug
4. Selected drugs shown as removable "pill" chips
5. User clicks "🔍 Check Interactions"
6. App calls `POST /check` on FastAPI backend
7. Results display:
   - Summary banner (interaction count, safe pairs, drugs, pairs checked)
   - "How drugs were resolved" expandable section
   - Severity cards (MAJOR=red, MODERATE=orange, MINOR=green)
   - Safe pairs expandable section
   - Interactive Pyvis graph (from `GET /graph`)

### 14.4 Quick Demo Presets

```python
presets = {
    "Warfarin case":    ["warfarin", "Combiflam", "Pantop 40"],
    "Cardiac combo":    ["Atorva 10", "Ecosprin", "Metolar XR"],
    "Diabetes regimen": ["Metformin 500", "Glibenclamide", "Ecosprin"],
    "5-drug poly":      ["Combiflam", "Ecosprin", "Pantop 40", "Metformin 500", "Atorva 10"],
}
```

### 14.5 Styling

Custom CSS with dark theme (clinical styling):
- Dark background (`#0F1117`)
- Gradient severity cards
- Color-coded badges (red/orange/green)
- Drug pill chips
- Monospace ingredient tags
- Summary stat banner

### 14.6 Graph Visualization

Uses Pyvis (`Network` class) with vis-network.js rendering:
- Blue nodes = Drug (brand)
- Green nodes = Ingredient (generic)
- Red edges = MAJOR interaction
- Orange edges = MODERATE
- Green edges = MINOR
- Gray edges = CONTAINS
- ForceAtlas2 physics layout

### 14.7 API Integration

| Function | API Call | Purpose |
|---|---|---|
| `api_check(drugs)` | `POST /check` | Core DDI detection |
| `api_search(query)` | `GET /search` | Autocomplete |
| `api_graph(drugs)` | `GET /graph` | Visualization data |

API base URL from `.streamlit/secrets.toml` or defaults to `http://localhost:8000`.

---

## 15. Database & Storage

### 15.1 Neo4j AuraDB (Primary)

| Property | Value |
|---|---|
| Technology | Neo4j AuraDB Free Tier |
| URI | `neo4j+s://dd205fee.databases.neo4j.io` |
| Database | `dd205fee` |
| Instance | `pharmasafe-kg` |
| Node limit | 50,000 (using 50,073 — slightly over) |
| Relationship limit | 175,000 (using 171,512) |
| Connection | TLS encrypted via neo4j+s:// |
| Driver | Python neo4j 6.1.0 |

### 15.2 In-Memory (Resolver)

The brand→generic resolver loads `master_mapping_table.csv` (29 MB, 304,404 rows) entirely into Python dictionaries at FastAPI startup. All brand lookups are O(1) dictionary reads.

### 15.3 CSV Files (Static Data Layer)

All intermediate and final data stored as CSV files in `phase1/outputs/`. No SQL database. No Redis. No caching layer.

### 15.4 File Storage (GNN Models)

PyTorch `.pt` files in `phase4/`:
- `graphsage_weights.pt` (97 KB)
- `gat_weights.pt` (167 KB)  
- `node_embeddings.pt` (594 KB)

---

## 16. External Services

### 16.1 Neo4j AuraDB

| Property | Value |
|---|---|
| Service | Neo4j AuraDB Free Tier |
| Purpose | Knowledge graph storage and query execution |
| Authentication | Username/password in `.env` |
| Failure handling | API returns 500 with error message |
| Can function without | ❌ No — all DDI detection depends on Neo4j |

### 16.2 No Other External APIs

- No ChEMBL API calls despite `requests` being listed for "HTTP calls (ChEMBL API)" — this is aspirational
- No OpenFDA, no PubChem, no DrugBank API
- All data is pre-downloaded and processed locally

---

## 17. Security

### 17.1 Critical Issues

| Issue | Severity | Evidence |
|---|---|---|
| **Credentials in `.env` committed to repo** | 🔴 CRITICAL | `.env` contains full Neo4j password in plaintext. No `.gitignore` exists. |
| **No `.gitignore`** | 🔴 CRITICAL | If pushed to Git, `.env`, `venv/`, `__pycache__/`, and all data files would be committed |
| **CORS allows all origins** | ⚠️ HIGH | `allow_origins=["*"]` in `main.py` line 84 |
| **No authentication** | ⚠️ HIGH | All API endpoints publicly accessible |
| **No rate limiting** | MEDIUM | No throttling on any endpoint |
| **No input sanitization for Cypher** | LOW | Parameterized queries used (`$g_a`, `$g_b`) — safe from injection |
| **Sensitive medical info** | MEDIUM | No patient data stored, but queries could be logged |
| **No HTTPS enforcement** | MEDIUM | Runs on HTTP locally; Neo4j connection uses TLS |

### 17.2 Positive Security Measures

- Cypher queries use parameterized inputs (no string interpolation)
- Neo4j credentials loaded from environment, not hard-coded in source
- Pydantic input validation on all API endpoints (max 10 drugs, 100-char limit)
- No user data persistence

---

## 18. Deployment

### 18.1 Current State

**No deployment infrastructure exists:**
- ❌ No Dockerfile
- ❌ No Docker Compose
- ❌ No Kubernetes configuration
- ❌ No CI/CD pipeline
- ❌ No `.gitignore`
- ❌ No git repository initialized
- ❌ No cloud deployment configuration
- ❌ No Procfile / render.yaml / railway.json

### 18.2 Local Development (Only Mode)

```
Terminal 1:  uvicorn phase3.app.main:app --reload --port 8000
Terminal 2:  streamlit run phase5/streamlit_app.py
```

### 18.3 What Would Be Needed to Deploy

1. `.gitignore` for `.env`, `venv/`, `__pycache__/`, data files
2. Dockerfile for FastAPI backend
3. Streamlit Cloud or separate frontend deployment
4. Environment variable management (not `.env` file)
5. CORS restriction to frontend URL
6. Health check endpoint already exists

---

## 19. Testing

### 19.1 Test Files Found

| File | Type | Tests |
|---|---|---|
| [test_api.py](file:///c:/pharmasafe-kg/phase3/test_api.py) | Integration (HTTP) | 7 test functions against running server |
| [test_db_connection.py](file:///c:/pharmasafe-kg/test_db_connection.py) | Smoke test | Neo4j connectivity check |
| [step5_validate.py](file:///c:/pharmasafe-kg/phase2/step5_validate.py) | Validation | 10 Cypher queries validating graph state |

### 19.2 test_api.py Coverage

| Test | Endpoint | What it checks |
|---|---|---|
| `test_health()` | `GET /` | Status 200, Neo4j connected |
| `test_search()` | `GET /search` | 5 queries: "Combi", "Metf", "Dolo", "Ecosprin", "War" |
| `test_check_basic()` | `POST /check` | 2 drugs: Combiflam + Ecosprin |
| `test_check_polypharmacy()` | `POST /check` | 5 drugs: Combiflam, Ecosprin, Pantop 40, Metformin 500, Atorva 10 |
| `test_drug_info()` | `GET /drug/{name}` | Combiflam, Warfarin |
| `test_graph()` | `GET /graph` | 3 drugs: Combiflam, Ecosprin, Warfarin |
| `test_error_handling()` | Multiple | Single drug (422), unknown drugs (422), not-found drug (404) |

### 19.3 What is NOT Tested

- ❌ No unit tests (no pytest, no unittest)
- ❌ No test for resolver edge cases
- ❌ No test for fuzzy matching accuracy
- ❌ No test for composition parsing
- ❌ No model evaluation test
- ❌ No load/performance testing
- ❌ No data validation tests
- ❌ No CI/CD test pipeline

---

## 20. Research Methodology

### 20.1 Methodology (Reconstructed from Implementation)

```
Problem: Indian brand DDI gap
  ↓
Data Collection: Kaggle (Indian drugs) + DrugBank (DDI pairs) + DDInter (supplement)
  ↓
Data Processing: Clean, normalize, filter allopathic
  ↓
Entity Resolution: Fuzzy string matching (token_sort_ratio)
  ↓
Knowledge Graph Construction: Neo4j with Ingredient + Drug nodes
  ↓
Interaction Detection: Graph traversal (Cypher queries)
  ↓
Explanation: Mechanism text from KG edge properties
  ↓
Evaluation: 10-query validation suite + spot checks
```

### 20.2 Evaluation Metrics (from validation)

- Brand resolution: 8 spot checks in `validate_known_mappings()` (Combiflam, Ecosprin, Dolo 650, etc.)
- Clinical interaction validation: 7 key DDI pair checks (warfarin+ibuprofen, simvastatin+clarithromycin, etc.)
- Graph statistics: coverage, density, connectivity distribution
- Query performance: sub-200ms for DDI queries

### 20.3 GNN Evaluation (from Colab script)

| Metric | Computed |
|---|---|
| AUC-ROC | ✅ |
| F1 Score | ✅ |
| Precision | ✅ |
| Recall | ✅ |
| Confusion Matrix | ✅ (code present) |

Comparison baselines (hard-coded published values, NOT reproduced):
- KGNN (Lin et al. 2020): AUC 0.8721, F1 0.8034
- SumGNN (Yu et al. 2021): AUC 0.9024, F1 0.8567
- MDF-SA-DDI (2022): AUC 0.9234, F1 0.8891

### 20.4 Limitations of Methodology

- No held-out clinical evaluation by domain experts
- Baseline comparisons use published numbers, not reproduced experiments
- Fuzzy matching accuracy not formally evaluated (no precision/recall on entity resolution)
- Severity inference is keyword-based, not validated against clinical gold standard

---

## 21. Current Implementation Status

| Component | Status | Evidence |
|---|---|---|
| Data pipeline (Phase 1) | ✅ COMPLETE | Pipeline report shows 248,373 Indian drugs, 100K DDI pairs, 304K master mappings |
| Knowledge Graph (Phase 2) | ✅ COMPLETE | Validation report shows 50,073 nodes, 171,512 relationships, all 10 tests pass |
| FastAPI Backend (Phase 3) | ✅ COMPLETE | 5 endpoints implemented, test suite exists |
| Brand→Generic Resolution | ✅ COMPLETE | 4-tier resolver (exact + alias + known_generics + fuzzy), 225,449 brands mapped |
| Interaction Detection | ✅ COMPLETE | Cypher-based pairwise detection, severity ranking, safe pair tracking |
| Explainability (XAI) | ✅ COMPLETE | Mechanism text, brand→generic path, severity labels |
| Streamlit Frontend (Phase 5) | ✅ COMPLETE | Full clinical UI with severity cards, autocomplete, graph viz, presets |
| GNN Training (Phase 4) | 🟡 PARTIAL | Colab script + weights exist, but NOT integrated into API |
| GNN Inference | 🔴 NOT INTEGRATED | `gnn_inference.py` exists but never imported by main.py |
| NLP (scispaCy) | 🗑️ UNUSED | In requirements but never imported in any execution path |
| Authentication | 🔴 NOT IMPLEMENTED | No auth on any endpoint |
| Testing | 🟡 PARTIAL | Integration tests exist, no unit tests, no CI |
| Deployment | 🔴 NOT IMPLEMENTED | No Docker, no CI/CD, no cloud config |
| Documentation | 🟡 PARTIAL | CLAUDE.md only, no README.md, no API docs beyond Swagger |
| Database (non-KG) | 🔴 NOT IMPLEMENTED | No relational DB, no user storage |
| Food/Drug interactions | 🔴 NOT IMPLEMENTED | Not in code |
| Disease entities | 🔴 NOT IMPLEMENTED | Mentioned in schema comments, no code |

---

## 22. Technical Debt

### CRITICAL

| Issue | Location | Impact |
|---|---|---|
| **Neo4j credentials exposed in `.env`** | `.env` lines 1–6 | Full database access if repo is shared |
| **No `.gitignore`** | Root | All secrets, venv, data would be committed |
| **GNN not integrated** | `phase4/gnn_inference.py` never imported | Trained model is useless — research contribution incomplete |
| **AuraDB node limit exceeded** | 50,073 > 50,000 limit | May cause issues on AuraDB free tier |

### HIGH

| Issue | Location | Impact |
|---|---|---|
| **CORS `allow_origins=["*"]`** | `main.py` line 84 | Security vulnerability in production |
| **Hard-coded `KNOWN_GENERICS` set** | `resolver.py` lines 123–135 | Only 45 generics supported for direct input; not scalable |
| **Duplicate `sys.path.insert(0, ...)` in every file** | All phase1/2/3 scripts | Brittle import system; should use proper packaging |
| **No error recovery in Phase 2 loading** | `step2–4` | If batch fails mid-load, partial data in graph |
| **Resolver loads entire 29MB CSV into memory** | `resolver.py` `load_resolver()` | Memory-intensive on constrained servers |

### MEDIUM

| Issue | Location | Impact |
|---|---|---|
| **scispaCy listed but unused** | `requirements.txt` lines 15–18 | False dependency, confusing for developers |
| **Dead code: `count_chars()` in utils.py** | `utils.py` line 174–176 | "Useful for VTU portal validation" — unrelated to project |
| **Dead code: `DRUGBANK_CSV` overwritten** | `step2_load_ingredients.py` lines 42–50 | First assignment immediately overwritten |
| **`safe_print` function in test_api.py** | `test_api.py` lines 18–28 | Monkey-patches `print` globally |
| **No pagination on drug info** | `query_engine.py` line 202 | `LIMIT 20` hard-coded, may miss interactions |
| **Only highest-severity per pair kept** | `query_engine.py` line 84 | Discards lower-severity interactions that may also be relevant |

### LOW

| Issue | Location | Impact |
|---|---|---|
| **`lib/` vendored JS libraries** | `lib/vis-9.1.2/`, `lib/tom-select/` | May not be used (Pyvis bundles its own vis.js) |
| **Windows path separators in some string replacements** | `step2_load_ingredients.py` line 45 | Fragile cross-platform path handling |
| **Log files accumulate without rotation** | `phase1/logs/`, `phase2/logs/` | No log cleanup mechanism |

---

## 23. Known Problems

1. **GNN model trained but wasted** — weights and embeddings exist but inference module is orphaned
2. **Severity distribution heavily skewed** — 87.9% MAJOR, 12.1% MODERATE, 0% MINOR (keyword inference may be too aggressive)
3. **No MINOR interactions in graph** — the validation report shows zero MINOR edges
4. **Polypharmacy scales poorly** — N drugs = N×(N-1)/2 separate Cypher queries (no batching)
5. **Autocomplete query mismatch** — searching "Metf" returns "Metfenac-P" not "Metformin" (brand name, not generic)
6. **AuraDB instance may be expired** — free tier instances have a time limit; credentials from April 2026

---

## 24. Complete End-to-End Example

### Input
User enters: **"Combiflam"** + **"Ecosprin"** in Streamlit UI

### Step 1: Streamlit → API
```python
api_check(["Combiflam", "Ecosprin"])
# POST http://localhost:8000/check
# Body: {"drugs": ["Combiflam", "Ecosprin"]}
```

### Step 2: Resolver (resolver.py)
```python
resolve_brand("Combiflam")
# _brand_to_generics["combiflam"] → ["ibuprofen", "paracetamol"]
# _expand_aliases → ["ibuprofen", "paracetamol", "acetaminophen"]
# Result: {"match_type": "exact", "confidence": 100, "generics": [...]}

resolve_brand("Ecosprin")
# _brand_to_generics["ecosprin"] → ["aspirin"]  (or variant)
# _expand_aliases → ["aspirin", "acetylsalicylic acid"]
# Result: {"match_type": "exact", "confidence": 100, "generics": [...]}
```

### Step 3: Query Engine (query_engine.py)
```python
check_interactions({
    "Combiflam": ["ibuprofen", "paracetamol", "acetaminophen"],
    "Ecosprin":  ["aspirin", "acetylsalicylic acid"]
})
```

Generates pairs:
- (ibuprofen, aspirin)
- (ibuprofen, acetylsalicylic acid)
- (paracetamol, aspirin)
- (paracetamol, acetylsalicylic acid)
- (acetaminophen, aspirin)
- (acetaminophen, acetylsalicylic acid)

### Step 4: Cypher Queries
For each pair:
```cypher
MATCH (a:Ingredient {name: "ibuprofen"})-[r:INTERACTS_WITH]-(b:Ingredient {name: "aspirin"})
RETURN a.name, b.name, r.severity, r.mechanism LIMIT 1
```

### Step 5: Build Explanation
```python
_build_explanation("Combiflam", "ibuprofen", "Ecosprin", "aspirin", "MAJOR",
                   "The risk or severity of bleeding can be increased...")
```
Output:
```
⚠️ MAJOR RISK: Combiflam and Ecosprin interact.

Combiflam contains Ibuprofen. Ecosprin contains Aspirin.

Mechanism: The risk or severity of bleeding can be increased when
Ibuprofen is combined with Acetylsalicylic acid.
```

### Step 6: API Response
```json
{
  "total_drugs": 2,
  "brand_names": ["Combiflam", "Ecosprin"],
  "pairs_checked": 6,
  "interactions_found": 1,
  "safe_pairs": 0,
  "summary": "1 interaction(s) found: 1 MAJOR.",
  "interactions": [{
    "brand_a": "Combiflam",
    "brand_b": "Ecosprin",
    "ingredient_a": "ibuprofen",
    "ingredient_b": "aspirin",
    "severity": "MAJOR",
    "mechanism": "...",
    "explanation": "..."
  }],
  "resolved_drugs": [...]
}
```

### Step 7: Streamlit Rendering
- Summary banner: 1 interaction, 0 safe, 2 drugs, 6 pairs
- Red MAJOR severity card with mechanism
- Interactive Pyvis graph showing Drug→Ingredient→INTERACTS_WITH→Ingredient←Drug path

---

## 25. File-Level Reference Map

| File | Purpose | Input | Output | Depends On | Used By | Status |
|---|---|---|---|---|---|---|
| `config.py` | Central config | `.env` | Constants | dotenv | All scripts | ✅ |
| `phase1/utils.py` | Text normalization, logging | Text strings | Cleaned text | config.py | step1, step2, step3 | ✅ |
| `phase1/step1_load_indian_drugs.py` | Load Indian drugs | az_medicine_india.csv | indian_drugs_cleaned.csv | config, utils | step3 | ✅ |
| `phase1/step2_load_drugbank.py` | Load DrugBank DDIs | drug_interactions.csv, drug_descriptions.csv | drugbank_ddi_cleaned.csv | config, utils | step3 | ✅ |
| `phase1/step2b_supplement_ddinter.py` | DDInter supplement | ddinter CSV + existing output | Updated DDI CSV | config, utils | Optional | ✅ |
| `phase1/step3_fuzzy_match.py` | Fuzzy matching | cleaned CSVs | master_mapping_table.csv | config, utils, thefuzz | Phase 2, Phase 3 | ✅ |
| `phase2/step1_create_schema.py` | Neo4j schema | None | Constraints+indexes | neo4j driver | step2–5 | ✅ |
| `phase2/step2_load_ingredients.py` | Load Ingredient nodes | drugbank_ddi_cleaned.csv | Neo4j Ingredient nodes | neo4j | step3 | ✅ |
| `phase2/step3_load_interactions.py` | Load DDI edges | drugbank_ddi_cleaned.csv | Neo4j INTERACTS_WITH | neo4j | step4 | ✅ |
| `phase2/step4_load_drugs.py` | Load Drug nodes | master_mapping_table.csv | Neo4j Drug+CONTAINS | neo4j | step5 | ✅ |
| `phase2/step5_validate.py` | Validate graph | Neo4j | validation_report.txt | neo4j | None | ✅ |
| `phase3/app/main.py` | FastAPI app | HTTP requests | JSON responses | database, resolver, query_engine, models | Streamlit | ✅ |
| `phase3/app/database.py` | Neo4j connection | .env | Driver instance | neo4j, dotenv | main, query_engine | ✅ |
| `phase3/app/resolver.py` | Brand→generic | master_mapping_table.csv | Resolved generics | pandas, thefuzz | main.py | ✅ |
| `phase3/app/query_engine.py` | Cypher queries | Generic names | DDI results | database.py | main.py | ✅ |
| `phase3/app/models.py` | Pydantic models | None | Type definitions | pydantic | main.py | ✅ |
| `phase3/test_api.py` | API tests | Running server | Test results | requests | Manual testing | ✅ |
| `phase4/step1_export_graph.py` | Export graph | Neo4j | CSV files | neo4j | Colab training | ✅ |
| `phase4/PharmaSafe_GNN_Colab.py` | GNN training | CSV files | Model weights | PyTorch Geometric | gnn_inference | ✅ |
| `phase4/gnn_inference.py` | GNN inference | Embeddings | Probabilities | torch | **NOTHING** | 🗑️ UNUSED |
| `phase5/streamlit_app.py` | Web frontend | User input | Visual output | requests, pyvis | User | ✅ |

---

## 26. Setup & Execution

### Prerequisites
- Python 3.10 or 3.11 (scispaCy constraint, though scispaCy is unused)
- Neo4j AuraDB free instance at console.neo4j.io
- ~200 MB disk space for datasets

### Installation
```bash
# Clone or copy repository
cd pharmasafe-kg

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# (Optional) Install scispaCy model — NOT actually used
# pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.4/en_ner_bc5cdr_md-0.5.4.tar.gz
```

### Environment Setup
Create `.env` in project root:
```
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
```

### Dataset Setup
Place in `phase1/data/`:
- `az_medicine_india.csv` (Kaggle)
- `drug_interactions.csv` (DrugBank, renamed from DDI_data.csv)
- `drug_descriptions.csv` (DrugBank, renamed from db_drug_interactions.csv)
- `ddinter_downloads_code_A.csv` (DDInter, optional)

### Execution Commands
```bash
# Phase 1: Data preparation (~3-8 minutes)
python phase1/run_phase1.py

# Phase 1b: Optional DDInter supplement
python phase1/step2b_supplement_ddinter.py

# Phase 2: Neo4j graph construction (~5-15 minutes)
python phase2/run_phase2.py

# Phase 3: Start API server
uvicorn phase3.app.main:app --reload --port 8000

# Phase 3: Test API (separate terminal)
python phase3/test_api.py

# Phase 4: Export graph for GNN training
python phase4/step1_export_graph.py
# Then upload colab_data/ to Google Drive and run PharmaSafe_GNN_Colab.py in Colab

# Phase 5: Start Streamlit frontend (separate terminal)
streamlit run phase5/streamlit_app.py
```

---

## 27. Final Technical Blueprint

### Architecture Summary
```
[Indian Drug CSVs] → [Data Pipeline] → [Master Mapping CSV]
                                              ↓
[DrugBank/DDInter CSVs] → [Data Pipeline] → [Neo4j KG]
                                              ↓
                                     [FastAPI Backend]
                                        ↓         ↓
                                  [REST API]  [Streamlit UI]
```

### Technology Stack Summary
- **Data:** pandas + CSV files
- **Entity Resolution:** thefuzz (Levenshtein) + regex + alias maps
- **Storage:** Neo4j AuraDB (free tier) + in-memory dicts
- **Backend:** FastAPI + Pydantic
- **Frontend:** Streamlit + Pyvis
- **ML (dormant):** PyTorch Geometric (GraphSAGE + GAT)

### Key Metrics
- 248,373 Indian drugs cleaned
- 100,000 DDI pairs loaded
- 2,073 unique generic ingredients
- 48,000 brand Drug nodes in graph
- 304,404 brand→generic mappings
- 225,449 brands with DDI coverage
- ~190ms query latency for DDI check

---

## 28. Recommended Next Steps

1. **Integrate GNN into API** — Wire `phase4/gnn_inference.py` into `phase3/app/main.py` to add ML-based confidence scores alongside KG lookups
2. **Fix severity distribution** — 87.9% MAJOR is clinically unrealistic; review keyword-based severity inference logic
3. **Create `.gitignore`** — Immediately, before any Git operations; exclude `.env`, `venv/`, `__pycache__/`, `phase1/data/`, model weights
4. **Remove scispaCy dependency** — It's unused; remove from requirements to simplify installation
5. **Add authentication** — At minimum, API key for the `/check` endpoint
6. **Restrict CORS** — Change `allow_origins=["*"]` to specific frontend URL
7. **Batch polypharmacy queries** — Use single Cypher UNWIND query instead of N² individual queries
8. **Add unit tests** — Test composition parsing, normalization, resolver edge cases
9. **Containerize** — Create Dockerfile for reproducible deployment
10. **Scale resolver** — Replace hard-coded `KNOWN_GENERICS` with full DrugBank vocabulary lookup

---

# Critical Findings

1. **GNN models trained but completely disconnected** — `gnn_inference.py` is never imported. The research contribution of GNN-based DDI prediction is implemented but not deployed.

2. **Neo4j credentials fully exposed** — `.env` contains real AuraDB password. No `.gitignore` exists. If this repo is ever pushed to GitHub, the database is compromised.

3. **Severity classification is heavily biased** — 87.9% of all DDI edges are MAJOR. The keyword-based inference over-triggers on common DrugBank `interaction_type` phrases.

4. **scispaCy is a phantom dependency** — Listed in requirements, referenced in config, but never imported or used. The system uses regex + fuzzy matching exclusively.

5. **The system actually works end-to-end** — Despite issues, Phases 1→2→3→5 form a complete, functional pipeline. The validation report confirms real DDI detection with mechanism explanations.

6. **AuraDB node limit slightly exceeded** — 50,073 nodes vs 50,000 limit. This may cause silent data loss or errors on the free tier.

7. **No authentication exists** — All endpoints are publicly accessible. For a medical safety tool, this is a significant concern.

8. **Polypharmacy detection uses N² queries** — For 10 drugs, this means up to 45 Cypher round-trips. Should use batch UNWIND query.

9. **Brand resolution covers 225,449 of ~248,373 brands** (90.8%) — Good coverage, but ~23,000 brands have generics that couldn't be fuzzy-matched to DrugBank.

10. **The master_mapping_table.csv is the linchpin** — 29 MB CSV loaded entirely into RAM at startup. Every API request depends on this in-memory dictionary. If the file is corrupted or missing, the entire system fails.

---

# Missing Information

| Item | Why It Matters |
|---|---|
| GNN model accuracy metrics | `training_curves.png` exists but actual AUC/F1 values are only available from Colab execution |
| Clinical validation by pharmacists/doctors | No evidence of domain expert review of detection accuracy |
| False positive/negative rates for entity resolution | Fuzzy matching accuracy never formally measured |
| Production deployment history | No evidence the system has been deployed beyond localhost |
| Academic paper/publication status | CLAUDE.md references "IEEE paper" but no paper file found |
| Comparison with commercial DDI systems | No benchmarking against Lexicomp, Micromedex, etc. |
| DrugBank license status | DrugBank data requires a license for redistribution |
| `drugs.csv` and `medicines_250k.csv` | Referenced in config but not present — unclear if ever used |
| Performance under concurrent load | No load testing or benchmarking data |
| Neo4j AuraDB instance current status | Free tier instances expire; instance may be inactive |

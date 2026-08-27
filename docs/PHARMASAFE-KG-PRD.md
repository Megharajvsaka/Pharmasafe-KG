# PharmaSafe-KG — Product Requirements Document (PRD)

**Version:** 1.0  
**Product:** PharmaSafe-KG  
**Product type:** Explainable Drug–Drug Interaction (DDI) Detection Platform for Indian Medicines  
**Current state:** Research prototype  
**Target state:** Production-ready web application  
**Implementation constraint:** The application will be built and maintained using AI coding agents such as Antigravity, Codex, Claude Code, or equivalent tools.

---

## 1. Executive Summary

PharmaSafe-KG is an explainable drug–drug interaction detection system designed specifically for Indian medicines. Its key problem is that Indian medicines are commonly entered using **brand names**, while DDI resources generally reason over standardized generic ingredients.

The product therefore performs:

```text
Indian brand name
      ↓
Brand → generic resolution
      ↓
Generic ingredient set
      ↓
Polypharmacy pair generation
      ↓
Knowledge Graph lookup
      ↓
Validated GNN fallback for unknown pairs
      ↓
Severity + evidence + mechanism
      ↓
Explainable clinical result
```

The existing project already contains a substantial research prototype: Phase 1 data preparation, Phase 2 Neo4j graph construction, Phase 3 FastAPI backend, Phase 4 GraphSAGE/GAT training artifacts, and Phase 5 Streamlit UI. The current-state documentation reports 248,373 cleaned Indian medicine records, 304,404 brand→generic mapping rows, 225,449 brands with DDI coverage, 2,073 ingredient nodes, 48,000 Drug nodes, 100,000 interaction edges, and 71,512 `CONTAINS` relationships. fileciteturn7file9L1-L18

The production product will replace Streamlit with React, harden the backend, integrate validated GNN inference, improve entity resolution and severity correctness, add authentication/history/admin functionality, and establish automated testing and deployment.

---

# 2. Product Vision

> Make drug-interaction checking for Indian medicines fast, understandable, evidence-aware, and explainable by combining Indian brand-name resolution, a pharmaceutical knowledge graph, and validated graph machine learning.

## Product principles

1. Evidence before prediction.
2. Explanation before complexity.
3. Never represent “not found” as “safe.”
4. Never represent a model prediction as documented evidence.
5. Never hide low-confidence entity resolution.
6. Mobile-first and time-efficient.
7. Security and privacy by design.
8. Research results must be reproducible.
9. AI agents must preserve existing working functionality and research methodology.

---

# 3. Problem Statement

## User problem

A doctor or pharmacist may know a medicine as a brand such as:

- Combiflam
- Ecosprin
- Dolo 650

but the interaction database may identify the relevant substances by generic names.

The system must therefore bridge:

```text
Brand language used in India
              ↓
Standardized pharmaceutical identity
              ↓
Interaction knowledge
```

## Technical problem

The platform must combine:

- entity resolution
- graph-based reasoning
- severity classification
- source/provenance
- explainability
- optional graph ML

without allowing uncertain results to appear authoritative.

---

# 4. Goals

### G1 — Reliable brand-to-generic resolution

Resolve Indian brands to generic ingredients with match type and confidence.

### G2 — Polypharmacy DDI detection

Given multiple medicines, check all unique medicine/ingredient pairs efficiently.

### G3 — Evidence-backed results

Use the knowledge graph as the primary source for documented interactions.

### G4 — Explainability

Explain:

- what the user entered
- what ingredients were resolved
- whether an interaction is documented or predicted
- severity
- mechanism
- source/evidence

### G5 — Validated GNN fallback

For pairs absent from the KG, use a validated GraphSAGE model where possible.

### G6 — Production readiness

Provide secure authentication, responsive UI, testing, monitoring, and deployment.

### G7 — Research reproducibility

Version datasets, KG, resolver rules, severity logic, model artifacts, evaluation protocol, and experiments.

---

# 5. Non-Goals

The initial product is not a:

- diagnosis system
- prescription generator
- dosage recommendation system
- replacement for a doctor/pharmacist
- complete adverse-event prediction engine
- complete food/drug interaction system
- complete disease/drug contraindication system

The current project explicitly lists food/drug interactions, disease/drug interactions, duplicate therapy detection, contraindication checking, and active ML interaction detection as not currently implemented. fileciteturn7file0L1-L18

---

# 6. Target Users

## Primary — Junior Doctors

Needs:

- fast search
- multiple-drug checking
- clear severity
- concise explanations
- evidence on demand
- mobile usability

## Secondary — Pharmacists

Needs:

- ingredient resolution
- interaction evidence
- mechanism details
- repeat checks
- saved lists/history

## Secondary — Medical Students

Needs:

- understandable explanations
- graph exploration
- educational/research context

## Research/Admin

Needs:

- system health
- usage metrics
- feedback review
- model/system status
- user administration

---

# 7. Product Scope

The final system contains:

```text
React SPA
   │
   ▼
FastAPI API
   ├── Authentication
   ├── Brand Resolver
   ├── DDI Engine
   ├── GNN Inference
   ├── XAI
   ├── History
   ├── Patient Lists
   ├── Feedback
   └── Admin
        │
        ├── Neo4j AuraDB
        ├── SQLite
        └── GNN artifacts
```

---

# 8. Current State → Target State

| Area | Current | Target |
|---|---|---|
| Frontend | Streamlit | React + TypeScript + Vite |
| Backend | FastAPI prototype | Hardened FastAPI |
| Graph | Neo4j AuraDB | Neo4j AuraDB |
| Resolver | Fuzzy matching + aliases | Versioned, benchmarked resolver |
| DDI | KG lookup | KG + validated GNN fallback |
| GNN | Trained, disconnected | Integrated |
| Severity | Source labels + keyword rules | Validated and auditable |
| Auth | Missing | JWT authentication |
| History | Prototype/absent | Persistent user history |
| Patient lists | Not production-ready | User-managed saved lists |
| Admin | Not implemented | Admin dashboard |
| Testing | Manual | Unit + integration + E2E + CI |
| Deployment | Research/local | Production deployment |
| Observability | Limited | Health + structured logs + monitoring |

The GNN module currently exists but is not imported into the API, so it must be treated as a trained artifact rather than an active production feature. fileciteturn7file4L1-L18

---

# 9. Functional Requirements

## FR-001 — Registration

Allow users to register with:

- full name
- email
- role
- password

Roles:

- Doctor
- Pharmacist
- Medical Student
- Researcher

## FR-002 — Login

Authenticate users and issue secure access tokens.

## FR-003 — Password recovery

Support reset-token-based password recovery.

---

## FR-004 — Medicine search

Search Indian brand names and generic names.

Search priority:

```text
Exact
→ normalized
→ prefix
→ generic
→ high-confidence fuzzy
```

## FR-005 — Brand resolution

Return:

```text
input
canonical brand
ingredients
match type
confidence
review flag
```

## FR-006 — Low-confidence handling

Low-confidence mappings must be visible and must not silently become clinical facts.

---

# 10. DDI Checking

## FR-007 — Multiple medicines

Users can add multiple medicines as removable chips.

## FR-008 — Pair count

Display:

```text
3 drugs selected — 3 pairs will be checked
```

## FR-009 — Minimum input

Require at least two medicines.

## FR-010 — Batch processing

The backend shall process all pairs efficiently rather than performing one database round trip per pair.

The project test specification explicitly requires a 10-drug request to use one database call for the batch-query implementation. fileciteturn8file5L1-L18

---

# 11. Knowledge Graph

## FR-011 — Documented interaction lookup

Primary relationship:

```text
Drug
 ↓ CONTAINS
Ingredient
 ↓ INTERACTS_WITH
Ingredient
 ↑ CONTAINS
Drug
```

The current system uses Neo4j ingredient interaction traversal and returns severity and mechanism. fileciteturn7file12L1-L18

## FR-012 — Evidence preservation

The system shall preserve relevant interaction evidence internally instead of discarding all but one record.

## FR-013 — Severity ordering

Results must be ordered:

```text
MAJOR
MODERATE
MINOR
```

---

# 12. Severity Requirements

## FR-014

Support:

- MAJOR
- MODERATE
- MINOR

## FR-015

Every severity result must have provenance:

```text
source label
or
validated rule/model
```

## FR-016

Severity must be explainable where possible.

### Research constraint

The current graph has an extreme MAJOR skew and uses keyword-based severity inference. This is a research/clinical correctness issue, not a UI problem. It must be validated before final claims. fileciteturn7file0L1-L18

---

# 13. GNN Requirements

## FR-017 — GraphSAGE fallback

For KG-missing pairs, invoke validated GraphSAGE where model coverage exists.

## FR-018 — Prediction label

Every GNN result must visibly say:

> AI-predicted interaction

It must never be displayed as a documented database interaction.

## FR-019 — Confidence

Display probability only after validation/calibration.

## FR-020 — Threshold

Select the production threshold using validation data. Do not assume a threshold such as 0.70 is scientifically valid merely because it appears in a build document.

## FR-021 — OOV handling

If an ingredient is outside the model vocabulary:

```text
GNN unavailable
→ KG-only result
```

Never fabricate a prediction.

---

# 14. Explainability Requirements

The current XAI system already constructs explanations using brand names, resolved ingredients, severity and mechanism text. fileciteturn7file5L1-L18

## FR-022 — Documented interaction explanation

Show:

```text
Drug A
→ Ingredient A

Drug B
→ Ingredient B

Severity
Mechanism
Evidence/source
```

## FR-023 — Graph explanation

Provide the relationship path when useful.

## FR-024 — Prediction explanation

For GNN predictions show:

- model name
- model version
- prediction probability
- prediction status
- appropriate caveat

## FR-025 — No false safety claim

Use:

> No documented interaction detected in the current knowledge base.

Never simply display:

> Safe.

---

# 15. Results Page

Must contain:

- summary counts
- severity-ranked interactions
- interaction cards
- resolved ingredients
- mechanism
- evidence/source
- documented vs predicted badge
- safe/non-documented combinations
- graph visualization
- retry action
- save action
- PDF report action

The existing target design specifies summary bars, interaction cards, safe-combination sections and an embedded knowledge graph. fileciteturn8file12L1-L18

---

# 16. Drug Detail

Display:

- brand name
- manufacturer where available
- price where available
- medicine type
- generic ingredients
- known interactions
- severity
- mechanism
- source

Interaction lists must use pagination rather than an arbitrary fixed 20-result ceiling. The current API contains a `LIMIT 20` query. fileciteturn7file12L1-L18

---

# 17. History

Authenticated users can:

- view previous checks
- search history
- filter by date
- filter by severity
- reopen a previous result

Each history item should preserve the result/version context required for reproducibility.

---

# 18. Saved Medicine/Patient Lists

Users can:

- save a medicine list
- name it
- reopen it
- rerun the check
- edit it
- delete it

Privacy requirements must be defined before storing patient-identifying information.

---

# 19. Feedback

Users can report:

- incorrect mapping
- incorrect severity
- incorrect interaction
- missing interaction
- other issue

Feedback lifecycle:

```text
unreviewed
→ reviewing
→ resolved
or
→ dismissed
```

---

# 20. Admin Dashboard

Admin functions:

### System

- Neo4j status
- API status
- GNN status
- uptime
- latency
- graph statistics

### Users

- list
- search
- suspend/unsuspend
- role management

### Feedback

- filter
- review
- resolve
- dismiss

### Metrics

- checks today
- pairs checked
- active users
- average response time
- recent trends

---

# 21. Required Pages

## Public

```text
/
 /about
 /status
 /login
 /register
 /forgot-password
 /reset-password
```

## User

```text
/dashboard
/check
/results
/drug/:name
/history
/patients
/graph
/profile
```

## Admin

```text
/admin
/admin/users
/admin/feedback
/admin/metrics
/admin/logs
```

The existing production design specifies these user and admin areas, including dashboard, drug checking, history, patient lists, profile/settings and admin workflows. fileciteturn8file17L1-L18

---

# 22. API Contract

## Public

```text
GET /health
GET /status
POST /feedback
```

## Auth

```text
POST /auth/register
POST /auth/login
POST /auth/logout
GET  /auth/me
POST /auth/forgot-password
POST /auth/reset-password
```

## Core

```text
GET  /search?q=
POST /check
GET  /drug/:name
GET  /graph
```

## User

```text
GET    /user/history
POST   /user/patients
GET    /user/patients
GET    /user/patients/:id
PATCH  /user/patients/:id
DELETE /user/patients/:id
```

## Admin

```text
GET   /admin/users
GET   /admin/users/:id
PATCH /admin/users/:id
GET   /admin/metrics
GET   /admin/feedback
PATCH /admin/feedback/:id
GET   /admin/logs
```

This endpoint structure is specified in the existing AI build guide. fileciteturn8file7L1-L18

---

# 23. Data Requirements

## Existing pipeline

```text
Indian medicine data
       ↓
Cleaning
       ↓
Normalization
       ↓
Brand/generic matching
       ↓
Master mapping
```

## DDI data

```text
DrugBank/DDInter
       ↓
Cleaning
       ↓
Interaction normalization
       ↓
Severity
       ↓
Mechanism/evidence
       ↓
Neo4j
```

## GNN data

```text
Graph export
    ↓
Features
    ↓
Leakage-free train/validation/test split
    ↓
GraphSAGE/GAT
    ↓
Validation
    ↓
Versioned artifact
```

---

# 24. Research Requirements

## RES-001 — Leakage-free evaluation

Held-out validation/test edges must not be present in the message-passing graph used for training.

This is a **P0 requirement**.

## RES-002 — Reproducibility

Record:

- seed
- graph version
- dataset version
- feature version
- split strategy
- negative sampling strategy
- hyperparameters

## RES-003 — Metrics

Report:

- ROC-AUC
- PR-AUC
- F1
- precision
- recall
- specificity
- confusion matrix
- threshold

## RES-004 — Baselines

Clearly distinguish reproduced experiments from published literature values.

## RES-005 — Entity resolution benchmark

Measure:

- Top-1 accuracy
- precision
- recall
- F1
- fuzzy-match accuracy
- confidence calibration

## RES-006 — Severity benchmark

Create a clinically reviewed severity evaluation set.

## RES-007 — GNN ablation

Compare feature groups such as topology, name features, degree and future pharmacological/chemical features.

---

# 25. Security Requirements

## SEC-001 — Secrets

No credentials in Git.

The current project explicitly identifies exposed Neo4j credentials and missing `.gitignore` as a critical risk. fileciteturn7file14L1-L18

Required:

```text
.env
.env.example
.gitignore
credential rotation
```

## SEC-002 — Authentication

Private endpoints require valid authentication.

## SEC-003 — Authorization

Admin endpoints require an admin role.

## SEC-004 — CORS

Only configured frontend origins.

## SEC-005 — Rate limiting

Initial targets:

```text
/check               100/hour
/search              300/hour
/auth/register         5/hour
/auth/forgot-password  3/hour
```

## SEC-006 — Input validation

Never concatenate user input directly into Cypher.

## SEC-007 — Logging

Never log:

- passwords
- tokens
- API keys
- database passwords
- unnecessary patient information

---

# 26. Privacy

Initial user data:

```text
id
name
email
role
password_hash
created_at
updated_at
last_login
status
```

If patient data is persisted, define:

- minimum data collection
- retention
- deletion
- access control
- audit trail
- encryption requirements

---

# 27. Non-Functional Requirements

## Performance

Engineering targets:

```text
Search: <200ms target
Simple DDI: <500ms target
Typical polypharmacy: <800ms target
```

The current prototype reports approximately 190ms for a DDI pair, 79ms for autocomplete and 104ms for a 4-drug polypharmacy query, but the production batch-query architecture must be benchmarked independently. fileciteturn7file12L1-L18

## Accessibility

- keyboard navigation
- visible focus states
- semantic labels
- sufficient contrast
- 44×44px minimum touch targets
- severity represented by icon + text + color

The existing design explicitly requires color not to be the only severity signal. fileciteturn8file16L1-L18

## Responsive design

```text
375px base
single column mobile
two-column tablet
sidebar + content desktop
```

## Reduced motion

Respect `prefers-reduced-motion`.

---

# 28. UI/UX Direction

The interface must feel:

- clinical
- calm
- authoritative
- minimal
- trustworthy

It should not feel:

- game-like
- noisy
- overly colorful
- promotional

### Severity

```text
⛔ MAJOR
⚠️ MODERATE
ℹ️ MINOR
```

Red is reserved for MAJOR interactions.

### Loading

Use skeleton screens rather than raw spinners alone.

### Empty states

Every empty state provides a suggested action.

---

# 29. Technical Stack

## Frontend

```text
React
TypeScript
Vite
Tailwind CSS
React Router
TanStack Query
Zustand
Axios
vis-network
Recharts
jsPDF
html2canvas
Lucide
```

## Backend

```text
Python 3.11
FastAPI
Pydantic
Uvicorn
Neo4j Python driver
SQLAlchemy
SQLite
JWT
slowapi
cachetools
```

## ML

```text
PyTorch
PyTorch Geometric
GraphSAGE
GAT
```

The existing build specification identifies React/Vite/TypeScript, FastAPI, Neo4j, PyTorch/PyG, TanStack Query and Zustand as the intended stack. fileciteturn8file18L1-L18

---

# 30. AI-Agent Development Requirements

The complete application will be implemented through AI coding agents.

## AG-001 — Inspect first

Agents must inspect the repository before modifying files.

## AG-002 — Do not recreate working components

Existing working code must be reused unless a task explicitly requires replacement.

## AG-003 — Separate current state from target state

Agents must not assume that planned features already exist.

## AG-004 — Protect research methodology

Agents must not silently modify:

- dataset definition
- severity methodology
- train/test methodology
- model architecture
- evaluation protocol

## AG-005 — Small execution units

Each agent task should follow:

```text
Inspect
 ↓
Plan
 ↓
Implement
 ↓
Test
 ↓
Review diff
 ↓
Checkpoint
```

## AG-006 — Test after changes

Every meaningful change must have a verification command.

## AG-007 — Never expose secrets

Agents must never print or commit secrets.

## AG-008 — Source of truth

For implementation status:

```text
source code + tests
```

take precedence over planned documentation.

## AG-009 — State labels

Documentation should use:

```text
IMPLEMENTED
IN PROGRESS
PLANNED
DEPRECATED
```

The existing AI build guide similarly instructs agents to work in bounded tasks and verify each task rather than blindly implementing the entire specification. fileciteturn8file0L1-L18

---

# 31. Testing Requirements

## Backend unit tests

### Resolver

- exact match
- fuzzy match
- generic input
- aliases
- not found
- malicious input
- combination medicine
- low confidence

### Query engine

- batch query
- severity sorting
- KG hit
- KG miss
- GNN fallback
- OOV model
- database failure

### Severity

- source severity
- rule precedence
- unknown/default
- distribution

## Integration tests

Test all API groups.

## Frontend

Test:

- search
- drug chips
- results
- interaction cards
- graph
- authentication
- filters

## E2E

At minimum:

```text
Landing → Login → Check → Results

Search → Add multiple drugs → Check → Explanation

Login → History → Load previous result
```

The existing project specification calls for pytest, frontend tests, and Playwright E2E testing. fileciteturn8file11L1-L18

---

# 32. CI/CD

Every pull request:

```text
Install
 ↓
Lint
 ↓
Type check
 ↓
Backend tests
 ↓
Frontend tests
 ↓
Build
```

Main branch:

```text
Tests
 ↓
Build
 ↓
Deploy
 ↓
Health check
```

---

# 33. Deployment

Target architecture:

```text
Internet
   ↓
React SPA
   ↓ HTTPS
FastAPI
   ├── Neo4j AuraDB
   ├── SQLite
   └── GNN artifacts
```

Target deployment pattern:

```text
React → Vercel
FastAPI → Render
Neo4j → AuraDB
```

The existing project build documents specify this intended deployment model and required deployment files. fileciteturn8file3L1-L18

---

# 34. Observability

Expose:

```text
/health
/status
```

Status should include:

- API state
- Neo4j state
- GNN loaded state
- uptime
- graph statistics
- response latency
- application version

Optional:

- Sentry
- uptime monitoring
- structured logs

---

# 35. Error Handling

The system must distinguish:

```text
No documented interaction
```

from:

```text
Database unavailable
```

from:

```text
Drug not resolved
```

from:

```text
GNN unavailable
```

from:

```text
Invalid request
```

Database failure must never be interpreted as absence of an interaction.

---

# 36. Success Metrics

## Product

- successful search resolution rate
- unresolved rate
- low-confidence rate
- checks per user
- repeat usage
- p50/p95 latency
- API error rate

## Research

- entity-resolution accuracy
- DDI ROC-AUC
- DDI PR-AUC
- F1
- precision
- recall
- severity classification performance
- explanation/source completeness

---

# 37. Release Gates

## Gate 0 — Security

- secrets removed/rotated
- `.gitignore`
- authentication
- authorization
- CORS
- rate limiting

## Gate 1 — Research

- leakage-free GNN evaluation
- reproducible metrics
- documented methodology

## Gate 2 — Data

- resolver benchmark
- severity benchmark
- mapping corrections

## Gate 3 — Backend

- batch queries
- GNN integration
- error handling
- API tests

## Gate 4 — Frontend

- responsive UI
- accessibility
- core user journeys

## Gate 5 — Production

- deployment
- health checks
- monitoring
- rollback strategy

---

# 38. Recommended Development Order

```text
1. Security foundation
        ↓
2. Research-valid GNN evaluation
        ↓
3. Brand-resolution validation
        ↓
4. Severity correction/validation
        ↓
5. KG integrity and provenance
        ↓
6. Backend batch-query optimization
        ↓
7. GNN integration
        ↓
8. Authentication
        ↓
9. Backend testing
        ↓
10. React design system
        ↓
11. Core React pages
        ↓
12. History/patient/admin features
        ↓
13. E2E + performance testing
        ↓
14. CI/CD
        ↓
15. Deployment
        ↓
16. Final research evaluation
```

---

# 39. Critical Product Rules

These are non-negotiable:

1. **Known evidence first.**
2. **Predictions are explicitly labeled.**
3. **No interaction found ≠ safe.**
4. **Low-confidence mapping is visible.**
5. **Severity must be validated.**
6. **GNN evaluation must be leakage-free.**
7. **Every important result should be explainable.**
8. **Database failures must never become false-safe results.**
9. **Secrets never enter Git.**
10. **AI agents cannot silently alter research methodology.**

---

# 40. Definition of Done

## Data

- [ ] Resolver benchmark completed
- [ ] Mapping accuracy measured
- [ ] Low-confidence policy implemented
- [ ] Dataset provenance/versioning implemented

## KG

- [ ] Schema documented
- [ ] Integrity checks pass
- [ ] Provenance available
- [ ] Graph limits respected

## GNN

- [ ] Leakage-free split
- [ ] Reproducible training
- [ ] GraphSAGE validated
- [ ] GAT comparison validated
- [ ] Threshold selected from validation
- [ ] Calibration completed
- [ ] API integration completed
- [ ] OOV handling implemented

## Clinical logic

- [ ] Severity benchmark
- [ ] Severity provenance
- [ ] Evidence displayed
- [ ] No false “safe” wording
- [ ] Prediction/documented distinction

## Backend

- [ ] Authentication
- [ ] Authorization
- [ ] Batch Cypher
- [ ] Rate limiting
- [ ] CORS restriction
- [ ] Retry/backoff
- [ ] Logging
- [ ] Error handling

## Frontend

- [ ] React application
- [ ] Responsive design
- [ ] Accessibility
- [ ] DDI workflow
- [ ] Results/XAI
- [ ] Graph explorer
- [ ] History
- [ ] Saved lists
- [ ] Admin

## Engineering

- [ ] Unit tests
- [ ] Integration tests
- [ ] E2E tests
- [ ] CI/CD
- [ ] Docker
- [ ] Production deployment
- [ ] Monitoring

---

# 41. Final Product Definition

PharmaSafe-KG is:

> **An explainable Indian-medicine drug interaction decision-support platform that resolves Indian brand names into standardized ingredients, checks documented interactions through a pharmaceutical knowledge graph, uses validated graph machine learning for appropriate unknown-pair prediction, and presents severity, evidence, mechanisms, and uncertainty in a clinically understandable interface.**

Core rule:

```text
EVIDENCE FIRST
      +
PREDICTION SECOND
      +
EXPLANATION ALWAYS
      +
UNCERTAINTY NEVER HIDDEN
```

---

# 42. Source Basis

This PRD is grounded in the supplied project materials:

- `PHARMASAFE-KG-COMPLETE-CURRENT-STATE.md`
- `PHARMASAFE_REBUILD_MASTER.md`
- `PHARMASAFE_COMPLETE_V2.md`
- `PHARMASAFE_AI_TOOL_BUILD_GUIDE.md`
- `PHARMASAFE_PRODUCTION_DESIGN_V3.md`

The current-state document states that the repository analysis covered the Python source files, CSV headers, configuration, Cypher queries, API routes, data-flow paths and execution artifacts. fileciteturn7file9L1-L18

Target requirements are intentionally distinguished from currently implemented functionality.

# PharmaSafe-KG — Complete Issue Register, Reasons, Fixes, and Recommended Resolution Order

> **Purpose:** Single source-of-truth issue register for the current PharmaSafe-KG project.
>
> **Basis:** Current-state analysis, rebuild/production design documents, `CLAUDE.md`, `config.py`, `requirements.txt`, `step1_export_graph.py`, `gnn_inference.py`, and the current GNN training artifacts/screenshots supplied for the project.
>
> **Important:** Items marked **CURRENT** are problems/limitations in the present implementation. Items marked **TARGET GAP** are gaps relative to the desired production/research system. Future-state documents are not treated as evidence that those features already exist.

---

## 1. Executive Summary

PharmaSafe-KG already has a substantial working research prototype:

- Indian medicine data preparation and normalization
- Brand → generic entity resolution
- Neo4j knowledge graph
- FastAPI backend
- Streamlit frontend
- Knowledge-graph DDI detection
- Mechanism-based explainability
- GraphSAGE and GAT training pipeline
- Trained model weights and node embeddings

The major remaining problems fall into five groups:

1. **Research validity** — most important before claiming final model performance.
2. **Data/entity-resolution quality** — essential for reliable clinical outputs.
3. **Core system correctness and scalability** — severity logic, batching, graph limits, resolver behavior.
4. **Security/reliability** — required before public deployment.
5. **Product/production gaps** — authentication, React frontend, persistence, testing, CI/CD, deployment, monitoring.

Recommended order:

```text
Research validity
      ↓
Data + severity correctness
      ↓
KG + backend correctness
      ↓
Validated GNN integration
      ↓
Security + production backend
      ↓
React application
      ↓
Testing / CI / deployment
      ↓
Final research evaluation and paper artifacts
```

---

# 2. Priority Definitions

| Priority | Meaning |
|---|---|
| **P0 — Critical** | Can invalidate research conclusions, expose secrets, or make core clinical output materially unreliable. |
| **P1 — High** | Major correctness, scalability, reliability, or production blocker. |
| **P2 — Medium** | Significant engineering/research debt that should be resolved before final release. |
| **P3 — Low** | Cleanup, maintainability, or polish issue. |

Status values:

| Status | Meaning |
|---|---|
| **CURRENT** | Exists in the present implementation. |
| **PARTIAL** | Some pieces exist but the full capability is incomplete. |
| **TARGET GAP** | Required by the desired production/research system but not implemented. |
| **UNUSED** | Present in dependencies/code but not part of the active execution path. |

---

# 3. P0 — Research and Clinical Correctness

## ISSUE-001 — GNN evaluation has a data-leakage risk

**Status:** CURRENT  
**Priority:** P0  
**Area:** GNN / Research methodology

### Problem

The current GNN workflow creates the full positive interaction graph first and then splits labeled positive/negative pairs into train/validation/test sets.

The model can therefore perform message passing over a graph that already contains positive edges that later appear in validation/test labels.

### Why this matters

For link prediction, held-out edges must not be visible in the graph used to construct message-passing representations.

### Fix

Use an edge-disjoint split:

```text
All positive edges
        ↓
Train edges
Validation edges
Test edges

Training message-passing graph = TRAIN edges only
Validation/test edges = held out
```

Generate negatives separately per split and guarantee no overlap with real positive edges.

### Acceptance criteria

- No validation/test positive edge exists in the training graph.
- No positive edge appears as a negative sample.
- Random seeds are fixed and recorded.
- The experiment is reproducible.
- Final paper metrics come only from the untouched test set.

---

## ISSUE-002 — Current GraphSAGE/GAT metrics are preliminary

**Status:** CURRENT  
**Priority:** P0  
**Area:** Research reporting

### Current observed results

**GraphSAGE**
- AUC: 0.8912
- F1: 0.8602
- Precision: 0.7758
- Recall: 0.9652

**GAT**
- AUC: 0.8364
- F1: 0.8187
- Precision: 0.6988
- Recall: 0.9884

### Problem

These are real results from the supplied training artifacts, but they should not be presented as final unbiased performance until ISSUE-001 is resolved.

### Fix

Rerun the experiments with the leakage-free protocol and report:

- ROC-AUC
- PR-AUC
- F1
- Precision
- Recall
- Specificity
- Confusion matrix
- Threshold analysis
- Class distribution
- Test-set size
- Random seed
- Split methodology

---

## ISSUE-003 — Baseline comparisons are not reproduced experiments

**Status:** CURRENT  
**Priority:** P0  
**Area:** Research methodology

### Problem

Published values for KGNN, SumGNN and MDF-SA-DDI are currently used for comparison, but these baselines were not reproduced under the same dataset and evaluation protocol.

### Fix

Clearly separate:

```text
Our experiments
vs.
Published literature values
```

For a stronger paper, reproduce at least one suitable baseline under the same protocol.

---

## ISSUE-004 — No formal clinical evaluation

**Status:** TARGET GAP  
**Priority:** P0  
**Area:** Research validity

### Problem

There is no held-out expert-reviewed evaluation covering mapping, DDI correctness, severity, and explanations.

### Fix

Create a clinically reviewed benchmark:

```text
Indian-brand cases
      ↓
Generic mapping review
      ↓
DDI review
      ↓
Severity review
      ↓
Explanation review
```

Record reviewer protocol, disagreements, and adjudication.

---

## ISSUE-005 — Brand → generic resolution has no formal precision/recall evaluation

**Status:** CURRENT  
**Priority:** P0  
**Area:** Entity resolution

### Problem

The system has large mapping counts but only limited spot checks. The project also contains known incorrect/low-confidence mappings.

### Fix

Build a gold-standard benchmark stratified by:

- exact names
- abbreviations
- spelling variations
- salt forms
- combination medicines
- ambiguous names
- low-frequency brands

Measure:

- Top-1 accuracy
- Precision
- Recall
- F1
- exact-match accuracy
- fuzzy-match accuracy
- confidence calibration

---

## ISSUE-006 — Severity classification is currently unreliable

**Status:** CURRENT  
**Priority:** P0  
**Area:** Clinical correctness

### Problem

DrugBank severity is inferred through keyword rules. The current graph is heavily skewed toward MAJOR:

- 87,868 MAJOR
- 12,132 MODERATE
- 0 MINOR in the reported loaded graph

Broad phrases such as `anticoagulant activities` and `risk or severity of adverse effects` contribute to over-classification.

### Fix

1. Preserve explicit DDInter severity where available.
2. Create an auditable DrugBank severity mapping.
3. Build a clinically reviewed benchmark.
4. Measure classification performance.
5. Version the rule set.
6. Store the evidence/rule used to assign severity.

Do **not** force a target class distribution without validation.

---

## ISSUE-007 — Severity is only partially explainable

**Status:** CURRENT  
**Priority:** P0  
**Area:** XAI

### Problem

The explanation shows the mechanism, but not why the severity itself was assigned.

### Fix

Expose:

```text
severity
severity_source
severity_rule
source_dataset
source_record/reference
```

---

# 4. P0 — Security

## ISSUE-008 — Neo4j credentials are exposed in `.env`

**Status:** CURRENT  
**Priority:** P0

### Problem

The current project documentation states that the real Neo4j password exists in `.env`, and `.gitignore` is absent.

### Fix

1. Rotate the Neo4j password immediately.
2. Create `.gitignore`.
3. Create `.env.example`.
4. Keep `.env` untracked.
5. If the credential was ever pushed, treat it as compromised and rotate it.

---

## ISSUE-009 — No authentication on API endpoints

**Status:** CURRENT  
**Priority:** P0

### Problem

Current API endpoints are publicly accessible without authentication.

### Fix

Implement a production authentication architecture before deployment:

- authenticated users
- protected API endpoints
- role-aware admin operations
- secure tokens/sessions
- no static secret embedded in frontend source

---

# 5. P1 — Knowledge Graph

## ISSUE-010 — Neo4j node count exceeds the configured safety budget

**Status:** CURRENT  
**Priority:** P1

### Problem

Current graph:

```text
Nodes:          50,073
Configured cap: 50,000
```

### Fix

Determine why the count exceeds the intended budget, then reduce the brand-node budget with a safety margin. Do not remove arbitrary nodes.

---

## ISSUE-011 — Graph ontology is too narrow for future clinical reasoning

**Status:** TARGET GAP  
**Priority:** P1

### Problem

Current graph mainly contains:

```text
Drug
Ingredient
CONTAINS
INTERACTS_WITH
```

Future documents mention Enzyme, SideEffect and Disease entities, but these are not implemented.

### Fix

Define the research ontology first. Potential future entities:

```text
Drug
Ingredient
Disease
Enzyme
Target
Pathway
AdverseEffect
Evidence
Source
```

Only implement entities tied to a research question and a reliable data source.

---

## ISSUE-012 — No first-class provenance/evidence model

**Status:** CURRENT / TARGET GAP  
**Priority:** P1

### Problem

Source-related properties exist, but evidence provenance is not represented as a robust first-class structure.

### Fix

Track at minimum:

```text
source_dataset
source_id
evidence_type
extraction_method
source_version
processing_version
timestamp
```

A dedicated `Evidence`/`SourceRecord` entity can be added if justified.

---

## ISSUE-013 — Multiple interaction facts can be discarded

**Status:** CURRENT  
**Priority:** P1

### Problem

The current engine keeps only the highest-severity interaction per brand pair.

This can hide additional mechanisms or evidence.

### Fix

Keep all relevant evidence internally and provide a summarized result for the UI.

---

## ISSUE-014 — Drug detail endpoint has hard-coded `LIMIT 20`

**Status:** CURRENT  
**Priority:** P2

### Problem

Drugs can have more than 20 interactions, but the API currently limits the result.

### Fix

Add pagination or a documented configurable limit.

---

# 6. P1 — Entity Resolution

## ISSUE-015 — Hard-coded `KNOWN_GENERICS` list

**Status:** CURRENT  
**Priority:** P1

### Problem

Only about 45 generic names are hard-coded even though the DrugBank vocabulary contains approximately 1,759 unique names.

### Fix

Generate/load the full normalized generic vocabulary from the processed DrugBank dataset.

---

## ISSUE-016 — Resolver loads the entire mapping CSV into memory

**Status:** CURRENT  
**Priority:** P1

### Problem

A ~29MB, 304K-row mapping table is loaded into in-memory dictionaries at startup.

### Fix

Create a compact versioned lookup artifact or use an appropriate local persistent store such as SQLite/DuckDB if required, while preserving fast lookup.

---

## ISSUE-017 — Matching policy is inconsistent across stages

**Status:** CURRENT  
**Priority:** P1

### Problem

Phase 1 and runtime resolution use different fuzzy thresholds/policies.

### Fix

Define one versioned policy:

```text
EXACT
ALIAS
HIGH_FUZZY
MEDIUM_FUZZY
LOW_REVIEW
REJECT
```

Store match score, match type, and policy version.

---

## ISSUE-018 — Low-confidence mappings need explicit safety handling

**Status:** CURRENT  
**Priority:** P1

### Problem

Known low-confidence and false matches exist.

### Fix

- never silently accept LOW confidence
- flag for verification
- prevent unsupported DDI claims from an unverified mapping
- maintain versioned corrections

---

## ISSUE-019 — Combination-drug parsing lacks a formal benchmark

**Status:** CURRENT  
**Priority:** P1

### Fix

Create dedicated tests for:

```text
Drug A + Drug B
Drug A / Drug B
Dosage-bearing combinations
Salt forms
Duplicate ingredients
```

Measure parsing and downstream resolution accuracy.

---

## ISSUE-020 — Autocomplete can return misleading fuzzy suggestions

**Status:** CURRENT  
**Priority:** P1

### Problem

The current analysis reports cases such as `Metf` producing a misleading brand result instead of the intended generic.

### Fix

Prioritize:

1. exact prefix
2. normalized prefix
3. generic prefix
4. high-confidence fuzzy
5. lower-confidence fuzzy

Display match type/confidence clearly.

---

# 7. P1 — GNN

## ISSUE-021 — GNN inference module is orphaned

**Status:** CURRENT  
**Priority:** P1

### Problem

`gnn_inference.py` exists, but the FastAPI backend does not use it.

### Fix

After validating the model, integrate it into the `/check` pipeline and return explicit source labels:

```text
knowledge_graph
gnn_predicted
```

---

## ISSUE-022 — Runtime inference uses precomputed embeddings, not live GraphSAGE weights

**Status:** CURRENT  
**Priority:** P1

### Problem

`gnn_inference.py` loads `node_embeddings.pt` and calculates a dot-product/sigmoid score. The saved GraphSAGE weights are not used in the runtime predictor.

### Fix

Choose deliberately:

- **Embedding inference:** keep for speed and document it accurately.
- **Live model inference:** load the validated GraphSAGE model.

For the first deployment, embedding inference can be acceptable if the embedding artifact is versioned and validated.

---

## ISSUE-023 — GNN inference is limited to known training nodes

**Status:** CURRENT  
**Priority:** P1

### Problem

The predictor returns `None` when an ingredient is outside its saved vocabulary.

### Fix

Handle OOV cases explicitly:

```text
GNN unavailable
      ↓
Use KG-only path
```

For future inductive inference, generate embeddings for unseen nodes from features rather than requiring a saved embedding.

---

## ISSUE-024 — GNN features are weakly semantic

**Status:** CURRENT  
**Priority:** P1

### Problem

Current features are primarily:

- DrugBank-ID presence
- eight hash-based name bits
- degree

The model therefore depends heavily on topology.

### Fix

Evaluate richer features:

- chemical fingerprints
- molecular descriptors
- ATC/class information
- drug targets
- enzymes
- pathways
- mechanism/text embeddings

Run ablation experiments to measure their effect.

---

## ISSUE-025 — Python built-in `hash()` hurts reproducibility

**Status:** CURRENT  
**Priority:** P2

### Problem

The export script derives features using Python's built-in `hash(name)`.

### Fix

Use deterministic hashing such as SHA-256-derived bits or another versioned deterministic feature encoder.

---

## ISSUE-026 — Negative sampling/splitting needs formal reproducibility rules

**Status:** CURRENT  
**Priority:** P1

### Fix

Record and enforce:

- seed
- positive-edge split
- negative sampling policy
- pair uniqueness
- reverse-edge treatment
- class ratio
- hard-negative strategy
- dataset/version identifier

---

# 8. P1 — DDI Detection

## ISSUE-027 — Active DDI detection is KG lookup only

**Status:** CURRENT  
**Priority:** P1

### Problem

The active application path is:

```text
brand → generic → Neo4j lookup
```

The trained GNN is not active.

### Fix

Use:

```text
Known KG edge → documented interaction
Unknown KG edge → validated GNN prediction
```

Never silently turn a prediction into a documented fact.

---

## ISSUE-028 — KG results have no calibrated confidence/evidence strength

**Status:** CURRENT  
**Priority:** P1

### Fix

Do not invent a probability for KG edges. Instead provide:

```text
source_dataset
source_record
severity_source
evidence_level
```

GNN confidence should only be shown after calibration.

---

## ISSUE-029 — Duplicate therapy detection is not implemented

**Status:** TARGET GAP  
**Priority:** P2

### Fix

Detect multiple medicines containing the same ingredient and present it separately from DDI detection.

---

## ISSUE-030 — Contraindication checking is not implemented

**Status:** TARGET GAP  
**Priority:** P2

### Fix

Add a validated `CONTRAINDICATED_IN` relationship only after acquiring a reliable disease/condition dataset and evaluation methodology.

---

## ISSUE-031 — Food/drug interaction layer is not implemented

**Status:** TARGET GAP  
**Priority:** P2

### Fix

Treat as a separate feature/research extension, not an informal addition to the existing DDI logic.

---

## ISSUE-032 — Disease-aware reasoning is not implemented

**Status:** TARGET GAP  
**Priority:** P2

### Fix

Add disease entities only with a reliable source and defined research objective.

---

# 9. P1 — Backend and Performance

## ISSUE-033 — Polypharmacy path generates many Neo4j round trips

**Status:** CURRENT  
**Priority:** P1

### Problem

The current algorithm executes many individual Cypher queries for combinations of drugs and ingredients.

### Fix

Replace the nested round-trip approach with one batched `UNWIND` query for the candidate pairs.

---

## ISSUE-034 — No cache layer

**Status:** CURRENT  
**Priority:** P2

### Fix

Add bounded TTL caches for:

- `/search`
- `/check`
- `/drug`

Version cache keys so stale medical results are not reused after dataset/KG updates.

---

## ISSUE-035 — Limited Neo4j error recovery

**Status:** CURRENT  
**Priority:** P1

### Problem

Neo4j errors can become 500 responses.

### Fix

Add:

- timeouts
- bounded retries
- exponential backoff
- request IDs
- structured logs
- clear client-safe errors

Never interpret database failure as "no interaction."

---

## ISSUE-036 — Phase 2 loading needs stronger transaction/recovery semantics

**Status:** CURRENT  
**Priority:** P1

### Fix

Use:

- idempotent MERGE operations
- transaction checkpoints
- validation after each batch
- resumable loading
- explicit cleanup/rebuild commands

---

## ISSUE-037 — Repeated `sys.path.insert(...)` hacks

**Status:** CURRENT  
**Priority:** P2

### Fix

Convert the Python codebase into a proper package with consistent imports and documented entrypoints.

---

# 10. P1 — Security and Privacy

## ISSUE-038 — CORS wildcard

**Status:** CURRENT  
**Priority:** P1

### Fix

Read allowed origins from environment/configuration and allow only required frontend origins.

---

## ISSUE-039 — No API rate limiting

**Status:** CURRENT  
**Priority:** P1

### Fix

Rate-limit by authenticated user/API client, with separate policies for search and DDI checks.

---

## ISSUE-040 — No audit trail

**Status:** TARGET GAP  
**Priority:** P2

### Fix

Record structured events for:

- login
- drug checks
- feedback
- administrative actions

Avoid logging unnecessary medical/personal information.

---

## ISSUE-041 — No defined privacy architecture for future patient data

**Status:** TARGET GAP  
**Priority:** P1

### Problem

The target application introduces patient lists/history, but the current application has no persistent user system.

### Fix

Before implementing patient history, define:

- data fields
- storage
- encryption
- retention
- access control
- deletion
- export
- audit policy

---

# 11. P1 — Testing

## ISSUE-042 — No unit test suite

**Status:** CURRENT  
**Priority:** P1

### Missing coverage

- normalization
- composition parsing
- resolver
- aliases
- fuzzy matching
- severity
- query engine

### Fix

Introduce `pytest` and deterministic fixtures.

---

## ISSUE-043 — No formal data-validation test suite

**Status:** CURRENT  
**Priority:** P1

### Fix

Test:

- missing columns
- null values
- duplicates
- invalid severity
- invalid mappings
- self-interactions
- direction duplicates
- malformed compositions

---

## ISSUE-044 — No model regression tests

**Status:** CURRENT  
**Priority:** P1

### Fix

Freeze evaluation datasets and enforce metric thresholds in CI.

---

## ISSUE-045 — No performance/load test suite

**Status:** CURRENT  
**Priority:** P2

### Fix

Benchmark:

- search
- 2/5/10-drug checks
- drug detail
- graph generation
- startup/cold start
- resolver memory use

---

## ISSUE-046 — No CI/CD test pipeline

**Status:** CURRENT  
**Priority:** P1

### Fix

Automate:

```text
lint
type checks
unit tests
API tests
frontend build
research smoke tests
```

---

# 12. P2 — Dependency and Code Quality

## ISSUE-047 — scispaCy is installed but unused

**Status:** UNUSED  
**Priority:** P2

### Fix

Remove it unless a specific validated NLP use case is introduced.

---

## ISSUE-048 — Dead `count_chars()` utility

**Status:** CURRENT  
**Priority:** P3

### Fix

Remove unrelated dead code.

---

## ISSUE-049 — Redundant `DRUGBANK_CSV` assignment

**Status:** CURRENT  
**Priority:** P3

### Fix

Keep one canonical configuration path.

---

## ISSUE-050 — `safe_print` monkey-patches global `print`

**Status:** CURRENT  
**Priority:** P3

### Fix

Use normal test logging/output.

---

## ISSUE-051 — Vendored JS assets may be redundant

**Status:** CURRENT / NEEDS VERIFICATION  
**Priority:** P3

### Fix

Verify whether `lib/` assets are actually required. Remove unused copies.

---

## ISSUE-052 — Windows-specific path string handling

**Status:** CURRENT  
**Priority:** P3

### Fix

Use `pathlib.Path` consistently.

---

## ISSUE-053 — Logs accumulate without rotation/retention

**Status:** CURRENT  
**Priority:** P2

### Fix

Add local rotation and production log-retention policy.

---

# 13. P1/P2 — Product and Frontend

## ISSUE-054 — Streamlit is the current prototype UI, not the target product architecture

**Status:** CURRENT / TARGET GAP  
**Priority:** P1

### Problem

Current frontend is Streamlit. Target design calls for React + Vite + TypeScript + Tailwind + vis-network.

### Fix

Freeze the backend API contract first, then build the React frontend.

---

## ISSUE-055 — No production mobile-first UI

**Status:** TARGET GAP  
**Priority:** P2

### Fix

Implement:

- responsive layouts
- 44px touch targets
- mobile graph fallback
- keyboard accessibility
- accessible contrast and focus states

---

## ISSUE-056 — No production XAI UI

**Status:** TARGET GAP  
**Priority:** P1

### Fix

Implement:

- interaction cards
- source badges
- mechanism/evidence panel
- KG path visualization
- GNN confidence when applicable
- reporting mechanism

---

## ISSUE-057 — No persistent authenticated history/patient lists

**Status:** TARGET GAP  
**Priority:** P2

### Fix

Define privacy architecture, add an application database, then implement authenticated persistence.

---

## ISSUE-058 — No feedback/admin correction loop

**Status:** TARGET GAP  
**Priority:** P2

### Fix

Implement feedback storage and review workflow:

```text
unreviewed
→ reviewing
→ resolved/dismissed
```

---

# 14. P2 — Deployment and DevOps

## ISSUE-059 — No Dockerfile

**Status:** TARGET GAP  
**Priority:** P1

### Fix

Containerize the FastAPI backend with only required production artifacts.

---

## ISSUE-060 — No `.dockerignore`

**Status:** TARGET GAP  
**Priority:** P2

### Fix

Exclude datasets, virtualenvs, secrets, logs, caches and development artifacts.

---

## ISSUE-061 — No production deployment configuration

**Status:** TARGET GAP  
**Priority:** P1

### Fix

Define the production topology explicitly, e.g.:

```text
React → Vercel
FastAPI → Render
Neo4j → AuraDB
```

Verify runtime/plan constraints before committing to it.

---

## ISSUE-062 — No CI/CD deployment pipeline

**Status:** TARGET GAP  
**Priority:** P1

### Fix

Use GitHub Actions for tests/build/deployment gates.

---

## ISSUE-063 — No monitoring/observability stack

**Status:** TARGET GAP  
**Priority:** P2

### Fix

Add:

- health checks
- error tracking
- uptime monitoring
- structured logs
- latency metrics

---

# 15. P2 — Documentation and AI-Agent Governance

## ISSUE-064 — Multiple documents represent different project states

**Status:** CURRENT  
**Priority:** P1

### Problem

The project has:

- current-state documentation
- rebuild instructions
- production design
- AI-tool build instructions

These can conflict if agents treat all of them as current truth.

### Fix

Create:

```text
docs/
  CURRENT_STATE.md
  TARGET_ARCHITECTURE.md
  RESEARCH_METHODOLOGY.md
  API_CONTRACT.md
  KG_SCHEMA.md
  GNN_METHODOLOGY.md
  DECISIONS.md
```

Label every feature:

```text
IMPLEMENTED
IN PROGRESS
PLANNED
DEPRECATED
```

---

## ISSUE-065 — AI agents could implement planned features as if already implemented

**Status:** CURRENT / TARGET  
**Priority:** P1

### Fix

Maintain strict root agent rules:

1. Source code is the current source of truth.
2. Inspect before modifying.
3. Never assume planned features exist.
4. Preserve working behavior.
5. Run tests after every meaningful change.
6. Do not change research methodology without explicit approval.
7. Never expose secrets.

---

# 16. P2 — Repository and Reproducibility

## ISSUE-066 — Large raw/generated artifacts should not enter Git

**Status:** TARGET GAP  
**Priority:** P2

### Fix

Ignore:

- raw datasets
- generated outputs
- model weights
- training exports
- virtual environments
- secrets

Track scripts, schemas, manifests and documentation.

---

## ISSUE-067 — Insufficient versioning of data/model/KG

**Status:** TARGET GAP  
**Priority:** P2

### Fix

Version:

```text
dataset
KG
resolver
severity rules
GNN model
evaluation protocol
```

---

## ISSUE-068 — No experiment registry

**Status:** TARGET GAP  
**Priority:** P2

### Fix

Record:

```text
experiment_id
dataset_version
graph_version
seed
model
hyperparameters
split
metrics
artifact paths
```

---

# 17. P1 — Data Integrity and Coverage

## ISSUE-069 — Directionality assumptions need explicit validation

**Status:** CURRENT / NEEDS VALIDATION  
**Priority:** P1

### Problem

The system treats interactions as effectively undirected.

### Fix

Validate this assumption against the semantics of each source dataset. Document any directional exceptions.

---

## ISSUE-070 — Source version/date metadata is not first-class

**Status:** TARGET GAP  
**Priority:** P2

### Fix

Maintain a data manifest with:

```text
source
source_version/date
download_date
license/reference
processing_version
```

---

## ISSUE-071 — No formal Indian-brand DDI coverage metric

**Status:** TARGET GAP  
**Priority:** P1

### Fix

Report separately:

```text
all Indian brands
resolved brands
high-confidence resolved brands
brands with DDI coverage
unresolved brands
```

---

# 18. P1 — Clinical UX and Trust

## ISSUE-072 — "No interaction" must not mean "safe"

**Status:** CURRENT / TARGET  
**Priority:** P1

### Problem

Absence of a detected interaction is not proof of safety.

### Fix

Use language such as:

> "No documented interaction detected in the current knowledge base."

Add a limitation/disclaimer.

---

## ISSUE-073 — GNN predictions must be visually distinct from documented interactions

**Status:** TARGET GAP  
**Priority:** P1

### Fix

Use explicit labels:

```text
Documented interaction
```

versus:

```text
AI-predicted interaction
```

---

## ISSUE-074 — No evidence citation UX

**Status:** TARGET GAP  
**Priority:** P2

### Fix

Expose:

- source dataset
- source record/identifier where available
- evidence text
- model version for predictions

---

# 19. Research Expansion Opportunities

These are not immediate bugs but are high-value future directions.

## ISSUE-075 — GNN feature representation lacks pharmacological semantics

### Suggested direction

Evaluate:

- chemical fingerprints
- molecular descriptors
- ATC classes
- drug targets
- enzymes
- pathways
- mechanism/text embeddings

Use ablations.

---

## ISSUE-076 — Hybrid KG + GNN reasoning is not implemented

### Suggested direction

Research a hybrid layer using:

```text
KG evidence
+
GNN probability
+
source reliability
+
calibration
```

Avoid a simplistic `if KG missing → probability > 0.70`.

---

## ISSUE-077 — GNN threshold 0.70 is not yet scientifically justified

**Status:** PLANNED / NEEDS VALIDATION

### Fix

Select the threshold from validation data based on the intended precision/recall trade-off.

---

## ISSUE-078 — No uncertainty/abstention mechanism

### Suggested direction

For ambiguous/low-confidence cases:

```text
Insufficient evidence — manual verification recommended.
```

An explicit abstention is preferable to false certainty.

---

# 20. Recommended Final Architecture

```text
                      USER
                       │
                       ▼
              React Clinical UI
                       │
                       ▼
                  FastAPI API
                       │
             ┌─────────┴─────────┐
             │                   │
             ▼                   ▼
      Brand Resolver       Authentication
             │
             ▼
       Ingredient Set
             │
             ▼
      Candidate Pair Builder
             │
             ▼
     ┌───────┴────────┐
     │                │
     ▼                ▼
 Neo4j KG        GraphSAGE/GNN
     │                │
     │                ▼
     │         Predicted evidence
     │
     ▼
 Known evidence
     └───────┬────────┘
             ▼
      Hybrid Reasoner
             │
      ┌──────┼──────────┐
      │      │          │
      ▼      ▼          ▼
 severity mechanism source
      │      │          │
      └──────┼──────────┘
             ▼
      Explainable result
             │
             ▼
       Audit / Feedback
```

---

# 21. Recommended Resolution Order

## Phase 0 — Protect the project

- [ ] Rotate exposed credentials.
- [ ] Add `.gitignore`.
- [ ] Add `.env.example`.
- [ ] Establish AI-agent governance.
- [ ] Freeze a baseline backup/tag.

## Phase 1 — Make research valid

- [ ] Fix GNN leakage.
- [ ] Make feature generation deterministic.
- [ ] Formalize train/validation/test protocol.
- [ ] Rerun GraphSAGE/GAT.
- [ ] Record full metrics.
- [ ] Reproduce at least one baseline where practical.

## Phase 2 — Make data reliable

- [ ] Build brand-resolution benchmark.
- [ ] Measure precision/recall/F1.
- [ ] Fix false mappings.
- [ ] Standardize matching thresholds.
- [ ] Validate combination-drug parsing.

## Phase 3 — Make clinical outputs reliable

- [ ] Fix severity classification.
- [ ] Create severity benchmark.
- [ ] Add severity provenance.
- [ ] Add source/evidence metadata.
- [ ] Prevent "no interaction" from meaning "safe."

## Phase 4 — Strengthen KG

- [ ] Fix node-budget issue.
- [ ] Validate graph integrity.
- [ ] Add provenance/version metadata.
- [ ] Preserve full evidence for multi-mechanism pairs.

## Phase 5 — Integrate GNN

- [ ] Package validated GraphSAGE.
- [ ] Decide precomputed vs live inference.
- [ ] Calibrate prediction probabilities.
- [ ] Select threshold using validation data.
- [ ] Add explicit `gnn_predicted` results.
- [ ] Add OOV handling.

## Phase 6 — Backend hardening

- [ ] Batch Cypher queries.
- [ ] Add retry/backoff.
- [ ] Add caching.
- [ ] Add authentication.
- [ ] Add rate limiting.
- [ ] Restrict CORS.
- [ ] Add request IDs and structured logs.

## Phase 7 — Production frontend

- [ ] Build React frontend.
- [ ] Implement XAI views.
- [ ] Implement graph explorer.
- [ ] Implement responsive/accessibility behavior.
- [ ] Implement disclaimer and evidence presentation.

## Phase 8 — Persistence and product features

- [ ] Add application database.
- [ ] Add user history.
- [ ] Add saved lists.
- [ ] Add feedback/admin workflow.

## Phase 9 — Testing and deployment

- [ ] Unit tests.
- [ ] Integration tests.
- [ ] Model regression tests.
- [ ] E2E tests.
- [ ] Performance tests.
- [ ] CI/CD.
- [ ] Docker.
- [ ] Production deployment.
- [ ] Observability.

## Phase 10 — Final research release

- [ ] Freeze dataset/version.
- [ ] Freeze KG/version.
- [ ] Freeze model/version.
- [ ] Run final evaluation.
- [ ] Generate paper tables/figures.
- [ ] Generate reproducibility package.
- [ ] Publish limitations and safety statement.

---

# 22. What Should NOT Be Done Yet

- [ ] Do not treat the current GNN metrics as final paper numbers.
- [ ] Do not blindly use a 0.70 GNN threshold.
- [ ] Do not add new KG entities without a research justification.
- [ ] Do not build the entire React application before the backend contract is stable.
- [ ] Do not expose GNN predictions as proven clinical facts.
- [ ] Do not deploy publicly while secret management/auth/CORS remain unresolved.
- [ ] Do not treat current severity labels as clinically validated.
- [ ] Do not treat fuzzy-match output as ground truth.
- [ ] Do not let AI agents rewrite the research methodology without explicit review.

---

# 23. Definition of Done

## Data

- [ ] Brand-resolution benchmark exists.
- [ ] Entity-resolution metrics are reported.
- [ ] Low-confidence mapping policy is enforced.
- [ ] Dataset provenance/versioning is recorded.

## Knowledge Graph

- [ ] KG schema is documented.
- [ ] Graph limits are respected.
- [ ] Data provenance is available.
- [ ] Validation suite passes.

## GNN

- [ ] Leakage-free evaluation protocol is used.
- [ ] Positive/negative splits are reproducible.
- [ ] GraphSAGE metrics are independently verified.
- [ ] GAT metrics are independently verified.
- [ ] Threshold is selected from validation data.
- [ ] Model/version artifacts are recorded.
- [ ] Inference is integrated.

## Clinical Logic

- [ ] Severity benchmark exists.
- [ ] Severity logic is validated.
- [ ] "No interaction" is not presented as "safe."
- [ ] GNN predictions are explicitly labeled as predictions.
- [ ] Evidence/source is visible.

## Backend

- [ ] Batch querying implemented.
- [ ] Authentication implemented.
- [ ] Rate limiting implemented.
- [ ] CORS restricted.
- [ ] Retry/backoff implemented.
- [ ] Structured logging implemented.

## Frontend

- [ ] React frontend implemented.
- [ ] Responsive/mobile behavior validated.
- [ ] XAI UI implemented.
- [ ] Knowledge graph UI implemented.
- [ ] Medical disclaimer implemented.

## Testing

- [ ] Unit tests.
- [ ] Integration tests.
- [ ] Model regression tests.
- [ ] Data validation tests.
- [ ] E2E tests.
- [ ] Performance tests.

## Deployment

- [ ] Docker.
- [ ] CI/CD.
- [ ] Secret management.
- [ ] Production environment.
- [ ] Monitoring.
- [ ] Rollback strategy.

---

# 24. Final Assessment

PharmaSafe-KG is **not a broken prototype**. It already has a meaningful working foundation.

The most important risks are:

1. **Research validity risk** — GNN leakage must be resolved.
2. **Clinical-data risk** — brand mapping and severity need formal validation.
3. **Architecture risk** — the GNN is trained but disconnected.
4. **Security risk** — credentials/auth/CORS must be fixed before public deployment.
5. **Scalability risk** — graph and query architecture need hardening.
6. **Governance risk** — current-state and future-state documents must not be confused by AI coding agents.

The correct strategy is:

> **Validate → Correct → Benchmark → Integrate → Harden → Productize → Deploy → Publish**

rather than building more UI features first.

---

# 25. Source Basis

This register consolidates issues explicitly identified or directly supported by:

- `PHARMASAFE-KG-COMPLETE-CURRENT-STATE.md`
- `PHARMASAFE_REBUILD_MASTER.md`
- `PHARMASAFE_COMPLETE_V2.md`
- `PHARMASAFE_PRODUCTION_DESIGN_V3.md`
- `CLAUDE.md`
- `config.py`
- `requirements.txt`
- `phase4/step1_export_graph.py`
- `phase4/gnn_inference.py`
- the supplied GNN training notebook/results/screenshots

It intentionally separates **implemented problems** from **future-state gaps**.

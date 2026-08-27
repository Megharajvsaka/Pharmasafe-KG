# PharmaSafe-KG — Data Dictionary & Data Model

**Version:** 1.0  
**Purpose:** Define the data entities, fields, relationships, datasets, provenance, transformations, and storage responsibilities that AI coding agents must understand before modifying PharmaSafe-KG data logic.

> **Important:** This document distinguishes facts verified in the project documentation from target/planned structures. Agents must inspect the actual repository before changing schemas or field names.

---

# 1. Data Architecture Overview

PharmaSafe-KG uses three primary data domains:

```text
                    ┌─────────────────────────┐
                    │   Source Pharmaceutical │
                    │        Datasets         │
                    └────────────┬────────────┘
                                 ↓
                    ┌─────────────────────────┐
                    │ Phase 1 Data Pipeline   │
                    │ Cleaning + Resolution   │
                    └────────────┬────────────┘
                                 ↓
                 ┌───────────────┴───────────────┐
                 ↓                               ↓
          ┌──────────────┐                ┌──────────────┐
          │ Brand/Drug   │                │ DDI Dataset  │
          │ Mappings     │                │              │
          └──────┬───────┘                └──────┬───────┘
                 ↓                               ↓
                 └───────────────┬───────────────┘
                                 ↓
                       ┌──────────────────┐
                       │   Neo4j AuraDB   │
                       │ Knowledge Graph  │
                       └────────┬─────────┘
                                ↓
                         DDI Query Engine
                                ↓
                         GNN fallback
                                ↓
                           API Results
```

The project documentation reports that Phase 1 processed 248,373 Indian medicine records and 100,000 DDI pairs; Phase 2 loaded approximately 48,000 Drug nodes, 2,073 Ingredient nodes, 100,000 `INTERACTS_WITH` edges and 71,512 `CONTAINS` edges into Neo4j. fileciteturn13file17

---

# 2. Source Data Domains

## 2.1 Indian medicine dataset

Purpose:

```text
Indian medicine/brand identity
        ↓
brand → generic/ingredient resolution
```

The documented pipeline includes:

```text
phase1/outputs/indian_drugs_cleaned.csv
phase1/outputs/brand_generic_map.csv
phase1/outputs/master_mapping_table.csv
```

The master mapping table is documented as containing approximately **225,449 Indian brand mappings**. fileciteturn13file3

---

# 3. DDI Source Dataset

The project uses cleaned interaction data derived from pharmaceutical DDI sources.

Documented output:

```text
phase1/outputs/drugbank_ddi_cleaned.csv
```

The current-state documentation reports:

```text
100,000 DDI pairs
```

The exact source-column names must be taken from the CSV itself when implementing against the repository; agents must not invent column names based solely on this document.

---

# 4. Brand

A **Brand** represents the medicine name commonly entered by an Indian user.

Examples from the project:

```text
Combiflam
Ecosprin
Dolo 650
Pantop
```

## Conceptual fields

| Field | Type | Meaning |
|---|---|---|
| `brand_name` | string | User-facing brand name |
| `normalized_name` | string | Normalized searchable form |
| `ingredients` | array | Resolved generic ingredients |
| `match_type` | enum | Resolution strategy |
| `confidence` | float | Resolution confidence |
| `review_required` | boolean | Whether user review is needed |

The existing TypeScript contract calls these concepts:

```text
input
matchedBrand
generics
matchType
confidence
```

with match types including:

```text
exact
fuzzy
generic_direct
alias
not_found
```

fileciteturn13file8

---

# 5. Generic / Ingredient

An **Ingredient** represents a standardized pharmaceutical substance used for interaction reasoning.

Examples:

```text
paracetamol
ibuprofen
aspirin
pantoprazole
```

The Knowledge Graph uses Ingredient nodes as the interaction-level entities.

The documented graph structure is:

```text
Drug
  ↓ CONTAINS
Ingredient
  ↓ INTERACTS_WITH
Ingredient
  ↑ CONTAINS
Drug
```

fileciteturn12file2

The current graph contains approximately:

```text
2,073 Ingredient nodes
```

fileciteturn13file17

---

# 6. Drug Node

In Neo4j, the project uses a conceptual `Drug` node for a medicine/brand representation.

Important distinction:

```text
User-facing identity
    = Indian brand name

Interaction reasoning
    = standardized ingredient
```

Agents must preserve this distinction.

Do not replace brand-level identity with ingredient-level identity in API responses without an explicit requirement.

---

# 7. Neo4j Node Types

## 7.1 Drug

```text
(:Drug)
```

Purpose:

```text
Represent medicine/brand entities
```

Expected conceptual information:

```text
name
normalized identity
ingredient relationships
```

## 7.2 Ingredient

```text
(:Ingredient)
```

Purpose:

```text
Represent standardized pharmaceutical ingredients
```

Expected conceptual information:

```text
name
normalized identity
interaction relationships
```

The exact property names must be verified against the existing Cypher/schema scripts before modification.

---

# 8. Neo4j Relationships

## 8.1 CONTAINS

```text
(:Drug)-[:CONTAINS]->(:Ingredient)
```

Meaning:

> This medicine contains this ingredient.

The current graph contains approximately:

```text
71,512 CONTAINS relationships
```

fileciteturn13file17

---

# 9. INTERACTS_WITH

```text
(:Ingredient)-[:INTERACTS_WITH]-(:Ingredient)
```

Meaning:

> Two standardized ingredients have a documented drug-drug interaction.

The current graph contains approximately:

```text
100,000 INTERACTS_WITH relationships
```

fileciteturn13file17

Conceptual relationship attributes include:

| Field | Meaning |
|---|---|
| `severity` | Interaction severity |
| `mechanism` | Mechanism/description |
| source/evidence | Provenance where available |

The existing query engine is documented as returning severity and mechanism from Neo4j. fileciteturn12file18

---

# 10. Interaction

An interaction is the application-level representation of a DDI result.

It should preserve:

```text
brand A
brand B
ingredient A
ingredient B
severity
mechanism
source
confidence
explanation
```

The documented frontend interface defines:

```typescript
interface Interaction {
  brandA: string;
  brandB: string;
  ingredientA: string;
  ingredientB: string;
  severity: Severity;
  mechanism: string;
  explanation: string;
  source: InteractionSource;
  gnnConfidence?: number;
}
```

fileciteturn13file16

---

# 11. Interaction Source

Allowed conceptual values:

```text
knowledge_graph
gnn_predicted
```

Meaning:

### knowledge_graph

The result is supported by a documented `INTERACTS_WITH` relationship.

### gnn_predicted

The KG did not provide a documented interaction and the validated GNN produced a positive prediction.

The architecture explicitly requires that GNN predictions never be represented as documented KG evidence. fileciteturn12file16

---

# 12. Interaction Severity

Supported documented severity values:

```text
MAJOR
MODERATE
MINOR
```

The severity value must not be silently invented when source information is unavailable.

Severity should carry provenance internally:

```text
source_dataset
validated_rule
model
unknown
```

The PRD specifically requires severity validation and provenance. fileciteturn13file2

---

# 13. Resolution Match Type

The resolver conceptually supports:

```text
exact
normalized
alias
fuzzy
generic_direct
not_found
```

The existing frontend contract specifically documents:

```text
exact
fuzzy
generic_direct
alias
not_found
```

fileciteturn13file8

Agents should reconcile backend and frontend terminology rather than introducing a third naming system.

---

# 14. Resolution Confidence

A confidence value represents how confidently a user input was mapped.

Conceptual range:

```text
0.0 → 1.0
```

The system must distinguish:

```text
high confidence
low confidence
unresolved
```

Low-confidence mappings must remain visible and must not silently become clinical facts. fileciteturn13file18

---

# 15. Combination Medicine

A brand may contain multiple ingredients.

Example conceptual structure:

```text
Combiflam
   ├── ibuprofen
   └── paracetamol
```

The resolver must preserve the complete ingredient set.

For DDI processing:

```text
Brand A
  ↓
Ingredient A1
Ingredient A2

Brand B
  ↓
Ingredient B1
Ingredient B2

→ evaluate relevant ingredient pairs
```

Do not reduce a combination medicine to only its first ingredient.

---

# 16. Polypharmacy Data

For `N` selected medicines:

```text
unique pairs = N × (N - 1) / 2
```

Examples:

```text
2 → 1
3 → 3
4 → 6
5 → 10
10 → 45
```

The API specification requires the backend to resolve medicines first and then generate unique pairs.

The build documentation specifically requires batch processing rather than one database call per pair. fileciteturn13file14

---

# 17. DDI Result Status

Application-level results should distinguish:

```text
documented
predicted
not_documented
unavailable
unresolved
```

## documented

KG contains supporting interaction evidence.

## predicted

Validated GNN produced a positive result for an eligible KG-missing pair.

## not_documented

The system successfully checked the pair but did not find documented evidence and did not produce an applicable positive GNN prediction.

This does **not** mean clinically safe.

## unavailable

A required dependency prevented a reliable conclusion.

## unresolved

A medicine could not be reliably mapped to ingredients.

---

# 18. GNN Data Model

The GNN uses the pharmaceutical graph.

Documented model artifacts include:

```text
phase4/gnn_inference.py
phase4/graphsage_weights.pt
phase4/node_embeddings.pt
```

The existing current-state analysis states that the GNN module exists but is not imported into the FastAPI API, meaning it is currently a trained artifact rather than an active API feature. fileciteturn13file17

The build specification describes:

```text
GraphSAGE
GAT
PyTorch
PyTorch Geometric
```

as the ML stack. fileciteturn13file2

---

# 19. GNN Prediction Record

Conceptual fields:

```text
ingredient_a
ingredient_b
probability
threshold
prediction
model_name
model_version
```

Example:

```json
{
  "ingredient_a": "drug_a",
  "ingredient_b": "drug_b",
  "probability": 0.87,
  "prediction": true,
  "model_name": "GraphSAGE",
  "model_version": "v1"
}
```

A production threshold must be selected from validation data rather than assumed from an arbitrary value.

The project roadmap explicitly requires leakage-free evaluation, threshold selection from validation data, calibration, and OOV handling. fileciteturn13file19

---

# 20. GNN OOV Data

OOV means:

```text
Out Of Vocabulary
```

If an ingredient is not represented in the GNN model vocabulary:

```text
GNN prediction unavailable
```

The system must not fabricate a prediction.

The KG result and GNN result must remain separate.

---

# 21. XAI Data

An explanation should be generated from actual system evidence.

For documented interactions:

```text
brand A
→ ingredient A
→ INTERACTS_WITH
→ ingredient B
→ brand B
```

The explanation should contain, where available:

```text
resolved ingredients
severity
mechanism
source
graph path
```

For GNN predictions:

```text
model
model version
probability
prediction status
appropriate uncertainty
```

The project explicitly requires explanation of what the user entered, what ingredients were resolved, whether an interaction is documented or predicted, severity, mechanism and source/evidence. fileciteturn13file6

---

# 22. SQLite Application Data

SQLite is intended for application/user data rather than the pharmaceutical knowledge graph.

The documented schema contains:

```text
users
password_resets
user_history
patient_lists
feedback
```

fileciteturn13file8

---

# 23. User Entity

Conceptual fields from the documented schema:

```text
id
email
name
role
password_hash
is_verified
created_at
last_login
is_suspended
```

Roles in the build specification include:

```text
user
admin
```

while the product role model also includes:

```text
doctor
pharmacist
student
researcher
```

Agents must reconcile this role representation before implementation rather than silently choosing one.

---

# 24. PasswordReset Entity

Conceptual fields:

```text
id
user_id
token_hash
expires_at
used
created_at
```

Never store raw password-reset tokens when a hashed representation is sufficient.

Never expose reset tokens in logs.

---

# 25. UserHistory Entity

Conceptual fields:

```text
id
user_id
drugs
result
interactions_found
has_major
created_at
```

The documented schema stores:

```text
drugs → JSON array
result → JSON result object
```

fileciteturn13file8

User history is user-owned data.

Server-side ownership checks are mandatory.

---

# 26. PatientList Entity

Conceptual fields:

```text
id
user_id
nickname
drugs
last_check
last_checked_at
created_at
updated_at
```

The target application uses saved medicine lists/patient lists for repeat checks.

The product must minimize personally identifiable information.

The original UI specification also described localStorage-based patient lists in an earlier frontend design; the production architecture instead defines persistent user-owned patient lists through SQLite/API. fileciteturn13file15

---

# 27. Feedback Entity

Conceptual fields:

```text
id
user_id
drug_a
drug_b
our_result
expected_result
comment
status
created_at
resolved_at
resolved_by
```

Supported status values in the documented schema:

```text
unreviewed
reviewing
resolved
dismissed
```

fileciteturn13file16

Feedback is useful for identifying:

```text
incorrect resolution
incorrect severity
incorrect interaction
incorrect explanation
```

It should not automatically alter clinical data without a controlled review process.

---

# 28. Dataset Provenance

Every important research artifact should have provenance.

At minimum document:

```text
source
source version/date
download/acquisition date
processing script
processing version
transformation
output filename
record count
```

The PRD explicitly requires versioning of:

```text
datasets
KG
resolver rules
severity logic
model artifacts
evaluation protocol
experiments
```

fileciteturn13file2

---

# 29. Data Transformation Pipeline

```text
Raw Indian medicine data
        ↓
Cleaning
        ↓
Normalization
        ↓
Brand extraction
        ↓
Generic extraction
        ↓
Fuzzy/alias matching
        ↓
Master mapping table
        ↓
Neo4j loading
```

DDI data:

```text
Raw DDI source
        ↓
Cleaning
        ↓
Normalization
        ↓
Ingredient mapping
        ↓
Validation
        ↓
Neo4j INTERACTS_WITH
```

GNN data:

```text
Neo4j graph
        ↓
Graph extraction
        ↓
Node indexing
        ↓
Feature preparation
        ↓
Train/validation/test split
        ↓
GraphSAGE/GAT
        ↓
Model artifact
        ↓
Inference
```

---

# 30. Data Integrity Rules

AI agents must preserve these rules.

## Rule 1 — Do not mutate source datasets

Raw/source data should remain reproducible.

## Rule 2 — Generated data must identify its source

Every derived dataset should have a documented generation process.

## Rule 3 — No silent deduplication

If duplicates are removed, record:

```text
before count
after count
deduplication rule
```

## Rule 4 — No silent severity replacement

If severity is changed, preserve the original value and transformation rationale.

## Rule 5 — No silent identity replacement

Do not replace a brand with a generic without retaining the original input.

---

# 31. KG Integrity Checks

The following checks are required before treating the KG as production-ready:

```text
duplicate Drug nodes
duplicate Ingredient nodes
duplicate interaction relationships
duplicate CONTAINS relationships
orphan Drug nodes
orphan Ingredient nodes
invalid interaction endpoints
missing severity
missing mechanism
missing provenance
```

The roadmap explicitly requires duplicate, orphan, schema, provenance and query validation. fileciteturn13file19

---

# 32. Data Ownership

| Data | System of Record |
|---|---|
| Pharmaceutical graph | Neo4j |
| Drug/Ingredient graph relationships | Neo4j |
| User accounts | SQLite |
| Password reset state | SQLite |
| User history | SQLite |
| Saved medicine lists | SQLite |
| Feedback | SQLite |
| GNN model artifact | Versioned filesystem/artifact storage |
| Raw datasets | Versioned project data storage |
| Resolver mappings | Versioned generated dataset |

---

# 33. What Must NOT Be Stored in Neo4j

Do not put application authentication data into the pharmaceutical graph.

Avoid storing:

```text
passwords
password hashes
JWTs
refresh tokens
private user data
application sessions
```

Neo4j is primarily the pharmaceutical knowledge graph.

---

# 34. What Must NOT Be Stored in SQLite as the Primary Graph

Do not duplicate the full pharmaceutical graph into SQLite merely to make queries easier.

SQLite should remain responsible for application/user persistence unless the architecture is explicitly changed.

---

# 35. Frontend Data Types

The documented frontend model includes:

```text
User
AuthTokens
LoginRequest
RegisterRequest
ResolvedDrug
Severity
InteractionSource
Interaction
SafePair
CheckResult
GraphNode
GraphEdge
GraphData
PatientList
Feedback
SystemStatus
AdminMetrics
PaginatedResponse
```

These types should be synchronized with the final FastAPI Pydantic schemas.

The existing build specification provides concrete TypeScript interfaces for these concepts. fileciteturn13file16

---

# 36. CheckResult

Conceptual structure:

```text
id
totalDrugs
brandNames
pairsChecked
interactionsFound
safePairs
summary
interactions
safePairsDetail
resolvedDrugs
checkedAt
```

The documented TypeScript contract uses these fields. fileciteturn13file16

Important:

```text
safePairs
```

should not be interpreted as clinical proof of safety.

A better semantic interpretation is:

```text
pairs without detected interaction evidence
```

---

# 37. Graph Data

Frontend graph data consists conceptually of:

```text
nodes
edges
```

Node types:

```text
Drug
Ingredient
```

Edge semantics:

```text
CONTAINS
MAJOR
MODERATE
MINOR
GNN
```

The graph visualization specification defines these categories and uses vis-network in React. fileciteturn13file15

---

# 38. Data Privacy

The application is a clinical decision-support/research platform, not a patient-record system.

Therefore:

```text
collect minimum necessary data
```

Avoid storing:

```text
patient name
address
phone
government ID
medical record number
```

unless a future requirement explicitly introduces a compliant patient-record workflow.

Saved lists should preferably use a nickname and medicine list.

---

# 39. Data Validation Layers

Data should be validated at multiple stages:

```text
Input validation
      ↓
Resolver validation
      ↓
KG validation
      ↓
DDI result validation
      ↓
GNN eligibility validation
      ↓
API schema validation
      ↓
Frontend rendering validation
```

No single layer should assume all upstream data is correct.

---

# 40. Data Failure Semantics

These states must remain distinct:

```text
No interaction found
        ≠
Medicine unresolved
        ≠
Neo4j unavailable
        ≠
GNN unavailable
        ≠
Invalid request
```

This is a critical product rule because failure must never become a false-safe result. fileciteturn12file16

---

# 41. AI-Agent Rules for Data Changes

Before changing any data-related code, an AI coding agent must:

1. Identify the source dataset.
2. Identify the transformation script.
3. Identify the generated output.
4. Identify consumers of that output.
5. Inspect CSV headers/schema.
6. Check existing tests.
7. Check Neo4j loading logic.
8. Check API consumers.
9. Preserve provenance.
10. Run validation after modification.

The agent must not:

```text
rename fields globally without impact analysis
delete generated data
rewrite source datasets
change model labels
change severity semantics
change train/test splits
change graph relationships
```

without an explicit task requiring it.

---

# 42. Critical Data Invariants

The following invariants should be tested:

```text
Every resolved brand has ≥1 ingredient
Every Drug → Ingredient relationship points to a valid Ingredient
Every INTERACTS_WITH relationship connects valid Ingredient nodes
No password is stored in plaintext
Every user_history row belongs to an existing user
Every patient_list belongs to an existing user
Admin-only data is inaccessible to non-admin users
GNN prediction always identifies itself as predicted
Documented interaction always has KG provenance
```

---

# 43. Known Data/Research Risks

The current-state documentation identifies several important uncertainties:

### GNN metrics

The weights exist, but locally verifiable model accuracy was not established; the documented analysis states that training/evaluation metrics require verification. fileciteturn13file17

### Severity

The project documentation identifies a strong MAJOR skew and keyword-based severity inference as a research/clinical correctness concern.

### Resolver

The current resolver requires benchmarking rather than assuming fuzzy-match confidence is clinically reliable.

### Source files

The current-state analysis notes that some documentation references input files that are not present in the documented `phase1/data/` directory. Agents must verify actual repository contents before relying on those references. fileciteturn13file17

---

# 44. Data Versioning

Recommended version identifiers:

```text
dataset_version
mapping_version
kg_version
resolver_version
severity_rules_version
gnn_model_version
api_version
```

A DDI result should be traceable, where practical, to the versions that produced it.

Example:

```json
{
  "kg_version": "2026.08",
  "resolver_version": "1.2",
  "gnn_model_version": "graphsage-v1",
  "severity_rules_version": "1.1"
}
```

---

# 45. Data Dictionary Change Policy

When a field changes:

```text
1. Update this document
2. Update backend schema
3. Update frontend type
4. Update tests
5. Update migration if persistent
6. Update data pipeline
7. Check existing generated data
8. Check API compatibility
```

Never change a data field in only one layer.

---

# 46. Final Data Model

```text
                 SOURCE DATA
                     │
             ┌───────┴────────┐
             ↓                ↓
        INDIAN BRANDS       DDI DATA
             │                │
             ↓                ↓
        RESOLUTION         NORMALIZATION
             │                │
             └───────┬────────┘
                     ↓
                NEO4J GRAPH
                     │
       ┌─────────────┼─────────────┐
       ↓             ↓             ↓
      Drug       Ingredient    Interaction
       │             │
       └─CONTAINS────┘
                     │
              INTERACTS_WITH
                     │
                     ↓
                DDI ENGINE
                     │
             ┌───────┴───────┐
             ↓               ↓
            KG              GNN
             │               │
             └───────┬───────┘
                     ↓
                 API RESULT
                     │
             ┌───────┴────────┐
             ↓                ↓
          FRONTEND          HISTORY
                              │
                            SQLite
```

---

# 47. Source Basis

This data dictionary is grounded in the project's existing documentation:

- The current-state analysis reports the verified Phase 1/2 record and graph counts and explains which artifacts were directly verified versus inferred. fileciteturn13file17
- The AI build guide defines the SQLite schema and frontend data interfaces. fileciteturn13file8turn13file16
- The architecture defines the Drug → Ingredient → Interaction graph model and KG-first/GNN-fallback flow. fileciteturn12file1turn12file16
- The PRD requires provenance, reproducibility, resolver validation, severity validation and GNN validation. fileciteturn13file2
- The roadmap defines the required data integrity and validation sequence. fileciteturn13file19

Where the documents contain target designs that differ from the current implementation, an AI agent must inspect the repository and label the difference rather than silently overwriting the current behavior.

# PharmaSafe-KG — Implementation Roadmap

**Version:** 1.0  
**Status:** Implementation planning document  
**Purpose:** Define the exact order in which PharmaSafe-KG should be improved from the current research prototype into a production-ready application.

---

# 1. Roadmap Objective

PharmaSafe-KG must be developed in a controlled sequence.

The project contains several tightly coupled areas:

```text
Data
 ↓
Knowledge Graph
 ↓
Resolver
 ↓
DDI Engine
 ↓
GNN
 ↓
XAI
 ↓
FastAPI
 ↓
React
 ↓
Authentication / History / Admin
 ↓
Testing
 ↓
Deployment
```

Therefore, implementation must not be driven simply by UI priority.

The roadmap prioritizes:

1. Security
2. Research correctness
3. Data correctness
4. Core backend correctness
5. ML integration
6. Frontend migration
7. Product features
8. Testing
9. Deployment
10. Final validation

---

# 2. Roadmap Principles

## R1 — Fix correctness before polish

Do not spend significant time polishing the UI while the underlying DDI, severity, resolver or GNN logic is unreliable.

## R2 — Security before production exposure

Credentials, authentication, authorization, CORS and rate limiting must be addressed before deployment.

## R3 — Research validity before ML integration

A trained model is not automatically a validated model.

## R4 — Preserve working functionality

Each phase should build on the existing implementation where practical.

## R5 — One logical change at a time

AI agents should work in bounded tasks.

## R6 — Every phase has a verification gate

No phase is complete until its acceptance criteria pass.

## R7 — Documentation follows implementation

When architecture or behavior changes, update the relevant documentation.

---

# 3. Overall Roadmap

```text
PHASE 0
Repository Baseline
       ↓
PHASE 1
Security & Configuration
       ↓
PHASE 2
Data + Entity Resolution Validation
       ↓
PHASE 3
Knowledge Graph Integrity
       ↓
PHASE 4
DDI Engine Hardening
       ↓
PHASE 5
Severity & Evidence Validation
       ↓
PHASE 6
GNN Research Validation
       ↓
PHASE 7
GNN Production Integration
       ↓
PHASE 8
Backend Production Hardening
       ↓
PHASE 9
React Frontend
       ↓
PHASE 10
Authentication + User Features
       ↓
PHASE 11
Admin + Feedback
       ↓
PHASE 12
Testing + QA
       ↓
PHASE 13
Performance + Observability
       ↓
PHASE 14
Deployment
       ↓
PHASE 15
Final Validation + Research Release
```

---

# 4. Phase 0 — Repository Baseline

## Objective

Create a verified baseline before changing code.

## Tasks

- Inspect repository tree.
- Identify backend entry point.
- Identify frontend entry point.
- Identify data-processing scripts.
- Identify Neo4j loading scripts.
- Identify Cypher queries.
- Identify GNN training code.
- Identify GNN inference code, if any.
- Identify XAI implementation.
- Identify configuration files.
- Identify environment variables.
- Identify existing tests.
- Identify unused/dead modules.
- Record current dependency versions.
- Run existing tests.
- Run the current application if possible.
- Record baseline failures.

## Deliverables

```text
baseline/
├── repository inventory
├── dependency inventory
├── test baseline
└── runtime baseline
```

## Exit Criteria

- [ ] Repository structure understood.
- [ ] Existing application can be started or startup blockers documented.
- [ ] Existing tests executed.
- [ ] No major component remains unexplored.

---

# 5. Phase 1 — Security & Configuration

## Priority

**P0 — Must happen before production deployment.**

## Tasks

### 1.1 Secrets

- Remove hard-coded Neo4j credentials.
- Rotate exposed credentials.
- Add `.env`.
- Add `.env.example`.
- Update `.gitignore`.
- Search Git history for exposed credentials where appropriate.

### 1.2 Configuration

Centralize:

```text
NEO4J_URI
NEO4J_USERNAME
NEO4J_PASSWORD
JWT_SECRET
DATABASE_URL
CORS_ORIGINS
GNN_MODEL_PATH
```

### 1.3 API security

Implement:

- CORS restrictions
- request validation
- authentication foundation
- authorization foundation
- rate limiting

## Exit Criteria

- [ ] No credentials in source code.
- [ ] No credentials in tracked files.
- [ ] `.env.example` works as configuration documentation.
- [ ] CORS is restricted.
- [ ] Rate limiting is implemented for sensitive endpoints.

---

# 6. Phase 2 — Data + Entity Resolution Validation

## Objective

Make sure Indian brand names reliably resolve to standardized ingredients.

The current project contains a large Indian medicine dataset and brand→generic mapping pipeline.

## Tasks

### 2.1 Normalization

Standardize:

- case
- whitespace
- punctuation
- dosage formatting
- common aliases

### 2.2 Exact matching

Implement deterministic exact matching before fuzzy matching.

### 2.3 Alias matching

Support known aliases and normalized variants.

### 2.4 Fuzzy matching

Use fuzzy matching only after deterministic strategies fail.

### 2.5 Confidence

Define:

```text
HIGH
MEDIUM
LOW
UNRESOLVED
```

with validated thresholds.

### 2.6 Combination medicines

Ensure multi-ingredient brands resolve into complete ingredient sets.

### 2.7 Benchmark

Create a manually verified evaluation set.

Measure:

```text
Top-1 accuracy
Precision
Recall
F1
Unresolved rate
Low-confidence rate
```

## Exit Criteria

- [ ] Resolver benchmark exists.
- [ ] Exact matches are deterministic.
- [ ] Fuzzy matching has confidence thresholds.
- [ ] Low-confidence results are visible.
- [ ] Combination medicines are handled.
- [ ] Resolver metrics are documented.

---

# 7. Phase 3 — Knowledge Graph Integrity

## Objective

Ensure the Neo4j graph is structurally correct before relying on it for clinical results.

## Tasks

### 3.1 Schema verification

Verify:

```text
Drug
Ingredient
CONTAINS
INTERACTS_WITH
```

### 3.2 Constraints/indexes

Review:

- unique identifiers
- indexes
- lookup properties

### 3.3 Duplicate detection

Check:

- duplicate drugs
- duplicate ingredients
- duplicate interactions
- duplicate relationships

### 3.4 Orphan detection

Identify:

- drugs without ingredients
- ingredients without expected relationships
- interaction endpoints that cannot be resolved

### 3.5 Provenance

Preserve source metadata where available.

### 3.6 Query validation

Validate all production Cypher queries.

## Exit Criteria

- [ ] Graph schema documented.
- [ ] Constraints/indexes verified.
- [ ] Duplicate audit complete.
- [ ] Orphan audit complete.
- [ ] Provenance requirements defined.
- [ ] Core queries tested.

---

# 8. Phase 4 — DDI Engine Hardening

## Objective

Make the Knowledge Graph DDI engine reliable and efficient.

## Tasks

### 4.1 Batch querying

Avoid:

```text
N pairs
→ N database queries
```

Prefer:

```text
N pairs
→ one batched query
```

### 4.2 Pair generation

For N medicines:

```text
N × (N - 1) / 2
```

Generate unique pairs only.

### 4.3 Connection management

Use proper Neo4j driver lifecycle and pooling.

### 4.4 Error handling

Distinguish:

```text
DB failure
Drug unresolved
No interaction
Invalid input
```

### 4.5 Pagination

Remove arbitrary result limits such as fixed `LIMIT 20` where product requirements require complete/paginated access.

### 4.6 Result schema

Create a stable unified response.

Conceptually:

```json
{
  "pair": {},
  "status": "documented|predicted|not_documented|unavailable",
  "severity": null,
  "mechanism": null,
  "evidence": [],
  "confidence": null
}
```

## Exit Criteria

- [ ] Batch query implemented.
- [ ] Polypharmacy tests pass.
- [ ] DB failures are distinguishable.
- [ ] No false-safe behavior exists.
- [ ] API response contract is stable.

---

# 9. Phase 5 — Severity & Evidence Validation

## Objective

Make severity clinically meaningful and auditable.

The existing project has documented severity logic and keyword-based processing. This must be validated rather than blindly preserved.

## Tasks

### 5.1 Severity source audit

Determine for each interaction:

```text
source severity
inferred severity
unknown severity
```

### 5.2 Distribution audit

Measure:

```text
MAJOR %
MODERATE %
MINOR %
UNKNOWN %
```

### 5.3 Rule precedence

Define explicit precedence:

```text
trusted source
    >
validated rule
    >
model inference
    >
unknown
```

### 5.4 Manual review set

Create a clinically reviewed sample.

### 5.5 False severity analysis

Identify:

- false MAJOR
- false MODERATE
- false MINOR
- unknown incorrectly labeled

## Exit Criteria

- [ ] Severity methodology documented.
- [ ] Distribution reviewed.
- [ ] Manual evaluation set exists.
- [ ] Severity provenance is exposed internally.
- [ ] High-risk classification errors are addressed.

---

# 10. Phase 6 — GNN Research Validation

## Priority

**P0 for research claims.**

## Objective

Determine whether the GNN is scientifically valid for the intended fallback use case.

## Tasks

### 6.1 Dataset definition

Freeze a versioned dataset.

### 6.2 Leakage-free split

Ensure held-out interaction edges are not leaked through message passing.

### 6.3 Negative sampling

Document:

- strategy
- ratio
- reproducibility

### 6.4 Features

Document:

- node features
- edge features
- structural features
- text/name features

### 6.5 Models

Evaluate:

```text
GraphSAGE
GAT
```

where applicable.

### 6.6 Metrics

Report:

```text
ROC-AUC
PR-AUC
Precision
Recall
F1
Specificity
Confusion matrix
```

### 6.7 Threshold selection

Choose the production decision threshold from validation data.

Do not hard-code a threshold merely because it gives desirable results on the test set.

### 6.8 Calibration

Evaluate whether model probability corresponds reasonably to observed likelihood.

### 6.9 OOV

Define behavior for unseen ingredients.

## Exit Criteria

- [ ] Leakage audit passed.
- [ ] Dataset version frozen.
- [ ] Reproducible training.
- [ ] Metrics recorded.
- [ ] Threshold selected using validation.
- [ ] OOV behavior defined.
- [ ] Model artifact versioned.

---

# 11. Phase 7 — GNN Production Integration

## Objective

Connect validated GNN inference to the DDI engine.

## Runtime flow

```text
KG lookup
   ↓
documented?
 ┌───────┴───────┐
YES              NO
 ↓                ↓
Evidence       GNN eligibility
                  ↓
              Prediction
                  ↓
          validated threshold
                  ↓
            AI prediction
```

## Tasks

- Build GNN service.
- Load model once at application startup.
- Validate artifact compatibility.
- Load vocabulary.
- Handle OOV.
- Add inference timeout.
- Add prediction metadata.
- Add model version.
- Add confidence.
- Add source status.
- Add tests.

## Exit Criteria

- [ ] GNN is loaded by backend.
- [ ] KG remains primary source.
- [ ] GNN only handles eligible missing pairs.
- [ ] Predictions are explicitly labeled.
- [ ] OOV is safe.
- [ ] Model version is returned.

---

# 12. Phase 8 — Backend Production Hardening

## Objective

Turn the research API into a maintainable application backend.

## Tasks

### Authentication

```text
register
login
logout
me
forgot password
reset password
```

### Authorization

Roles:

```text
Doctor
Pharmacist
Medical Student
Researcher
Admin
```

### Application database

Implement:

```text
users
history
saved_lists
feedback
```

### API validation

Use Pydantic models for all requests/responses.

### Logging

Use structured logs.

Never log:

```text
passwords
tokens
API keys
database credentials
unnecessary patient information
```

### Rate limiting

Protect:

```text
auth
search
check
feedback
```

### Health

Implement:

```text
/health
/status
```

## Exit Criteria

- [ ] Authentication works.
- [ ] Role authorization works.
- [ ] Core APIs have schemas.
- [ ] Error handling is consistent.
- [ ] Health/status endpoints work.
- [ ] Sensitive logging is removed.

---

# 13. Phase 9 — React Frontend

## Objective

Replace the prototype UI with the production React application.

## Order

### 9.1 Foundation

- Vite
- TypeScript
- Tailwind
- routing
- API client
- state management
- design system

### 9.2 Public pages

```text
Landing
About
Status
Login
Register
Forgot Password
```

### 9.3 Core workflow

```text
Dashboard
→ Check medicines
→ Results
→ Explanation
```

### 9.4 Drug detail

Implement:

```text
drug search
ingredient information
known interactions
pagination
```

### 9.5 Graph

Implement graph visualization after the core results workflow is stable.

### 9.6 Responsive design

Test:

```text
375px
768px
1024px
1440px+
```

## Exit Criteria

- [ ] React application builds.
- [ ] Authentication UI works.
- [ ] Medicine search works.
- [ ] DDI check works.
- [ ] Results are correctly rendered.
- [ ] Graph visualization works.
- [ ] Responsive layout passes.
- [ ] Accessibility baseline passes.

---

# 14. Phase 10 — User Features

## Tasks

### History

```text
create
list
filter
search
reopen
delete
```

### Saved lists

```text
create
edit
delete
run check
```

### Profile

```text
view
edit
change password
```

## Exit Criteria

- [ ] User-specific data is isolated.
- [ ] History works.
- [ ] Saved lists work.
- [ ] Authorization tests pass.
- [ ] Privacy requirements are satisfied.

---

# 15. Phase 11 — Admin + Feedback

## Tasks

### Admin dashboard

Display:

```text
users
checks
pairs
latency
errors
graph status
GNN status
```

### User management

```text
list
search
role
status
suspend
```

### Feedback

```text
submit
review
resolve
dismiss
```

## Exit Criteria

- [ ] Admin endpoints protected.
- [ ] Admin UI works.
- [ ] Feedback workflow works.
- [ ] User management works.

---

# 16. Phase 12 — Testing & QA

## Testing pyramid

```text
             E2E
            /          Integration
        /              Unit Tests
```

## Backend

Test:

- resolver
- DDI engine
- severity
- GNN
- XAI
- auth
- permissions
- repositories
- error handling

## Frontend

Test:

- search
- chips
- check
- results
- graph
- login
- history
- saved lists

## E2E

Minimum:

```text
Landing → Login → Check → Results

Search → Add 3+ medicines → Check → Results

Login → History → Reopen result

Admin → Users → Feedback
```

## Security testing

Test:

- invalid JWT
- expired JWT
- wrong role
- injection attempts
- rate limiting
- invalid input

## Exit Criteria

- [ ] Unit tests pass.
- [ ] Integration tests pass.
- [ ] E2E critical paths pass.
- [ ] Security tests pass.
- [ ] No critical regression.

---

# 17. Phase 13 — Performance + Observability

## Performance targets

Initial engineering targets:

```text
Search:        <200ms target
Simple DDI:    <500ms target
Typical DDI:   <800ms target
```

These are engineering targets, not clinical guarantees.

## Measure

```text
p50
p95
p99
```

for:

- search
- resolution
- Neo4j query
- GNN inference
- full DDI request

## Observability

Track:

```text
request count
latency
errors
Neo4j failures
GNN failures
resolver failures
```

## Exit Criteria

- [ ] Performance benchmark completed.
- [ ] p50/p95/p99 recorded.
- [ ] Slow operations identified.
- [ ] Health monitoring implemented.
- [ ] Structured logs implemented.

---

# 18. Phase 14 — Deployment

## Target

```text
React
  ↓
Vercel

FastAPI
  ↓
Render

Neo4j
  ↓
AuraDB
```

The providers may change without changing the logical architecture.

## Tasks

- production environment variables
- build configuration
- Docker where appropriate
- frontend deployment
- backend deployment
- Neo4j production configuration
- HTTPS
- CORS
- health checks
- deployment smoke tests

## Exit Criteria

- [ ] Production frontend deployed.
- [ ] Production API deployed.
- [ ] Neo4j connected.
- [ ] Secrets configured securely.
- [ ] Health checks pass.
- [ ] Core user journey works in production.

---

# 19. Phase 15 — Final Validation

This is the final release gate.

## Product

- [ ] All P0 issues resolved.
- [ ] Core DDI workflow works.
- [ ] Authentication works.
- [ ] History works.
- [ ] Admin works.
- [ ] Responsive UI works.

## Data

- [ ] Resolver benchmark complete.
- [ ] KG integrity validated.
- [ ] Severity validated.
- [ ] Provenance documented.

## ML

- [ ] Leakage-free evaluation complete.
- [ ] Model version frozen.
- [ ] Threshold frozen.
- [ ] OOV behavior validated.
- [ ] Inference tested.

## Security

- [ ] No exposed credentials.
- [ ] Authentication secure.
- [ ] Authorization secure.
- [ ] Rate limiting enabled.
- [ ] CORS restricted.

## Engineering

- [ ] Unit tests pass.
- [ ] Integration tests pass.
- [ ] E2E tests pass.
- [ ] CI/CD passes.
- [ ] Production deployment passes.

---

# 20. Issue Prioritization

Every issue should receive one priority.

## P0 — Blocking

Examples:

```text
exposed credentials
incorrect clinical severity
data leakage
false-safe result
broken DDI core logic
security vulnerability
```

Must be fixed before production/research release.

## P1 — High

Examples:

```text
GNN integration
authentication
batch querying
resolver accuracy
major UX problems
missing core tests
```

Should be fixed before beta.

## P2 — Medium

Examples:

```text
history improvements
graph UX
admin metrics
advanced filtering
performance optimizations
```

## P3 — Low

Examples:

```text
visual polish
minor UX enhancements
nonessential analytics
```

---

# 21. Dependency Rules

The following dependencies are mandatory:

```text
Security
   ↓
Backend foundation
   ↓
Data / resolver
   ↓
KG
   ↓
DDI engine
   ↓
Severity
   ↓
GNN validation
   ↓
GNN integration
   ↓
React core workflow
   ↓
Auth/history/admin
   ↓
Testing
   ↓
Deployment
```

Do not implement dependent functionality before its prerequisite is stable.

---

# 22. AI-Agent Execution Strategy

The entire implementation may be performed using AI coding agents.

Recommended execution loop:

```text
1. Read PRD
2. Read CURRENT-STATE
3. Read ISSUES
4. Read ARCHITECTURE
5. Read ROADMAP
6. Inspect actual source code
7. Select one bounded task
8. Plan changes
9. Implement
10. Run tests
11. Review diff
12. Update documentation
13. Commit/checkpoint
14. Move to next task
```

An agent must not attempt to implement the entire roadmap in one uncontrolled operation.

---

# 23. AI-Agent Task Format

Every implementation task should follow this structure:

```markdown
# TASK-ID

## Objective

## Context

## Current behavior

## Expected behavior

## Files likely affected

## Constraints

## Implementation steps

## Tests required

## Acceptance criteria

## Documentation updates
```

Example:

```markdown
# TASK-DDI-001

## Objective

Convert pair-by-pair Neo4j calls into one batch query.

## Current behavior

Each interaction pair performs a separate database query.

## Expected behavior

All unique pairs should be resolved through one batched query.

## Constraints

Do not change the returned clinical meaning.

## Tests required

- 2 drugs
- 4 drugs
- 10 drugs
- no interactions
- database failure

## Acceptance criteria

10-drug request does not perform 45 independent Neo4j queries.
```

---

# 24. Definition of Done for Every Task

A task is complete only when:

```text
Implementation
     +
Tests
     +
Review
     +
Documentation
```

are complete.

The agent must report:

```text
Files changed
Tests run
Tests passed
Known limitations
Follow-up issues
```

---

# 25. Recommended Milestones

## Milestone 1 — Secure Research Prototype

Includes:

```text
security
resolver
KG
DDI engine
severity validation
```

## Milestone 2 — Validated ML Prototype

Includes:

```text
leakage-free GNN
model evaluation
threshold
calibration
GNN inference
```

## Milestone 3 — Functional Web Application

Includes:

```text
FastAPI
React
authentication
DDI workflow
XAI
graph
```

## Milestone 4 — User Product

Includes:

```text
history
saved lists
profile
feedback
```

## Milestone 5 — Production Platform

Includes:

```text
admin
testing
observability
CI/CD
deployment
security hardening
```

## Milestone 6 — Research Release

Includes:

```text
reproducible experiments
final metrics
documentation
limitations
model/version records
```

---

# 26. What Must NOT Be Done Early

Do not prioritize these before core correctness:

```text
complex animations
advanced dashboards
visual polish
large redesigns
extra graph effects
nonessential analytics
```

Do not integrate the GNN merely because a trained model exists.

Do not deploy publicly while credentials or critical security issues remain unresolved.

Do not claim clinical safety based solely on absence of a KG edge.

---

# 27. Final Roadmap

The project should ultimately reach:

```text
                 PHARMASAFE-KG
                       │
          ┌────────────┼────────────┐
          ↓            ↓            ↓
        DATA           KG           ML
          │            │            │
          └────────────┼────────────┘
                       ↓
                  DDI ENGINE
                       ↓
                 EXPLAINABILITY
                       ↓
                    FASTAPI
                       ↓
                    REACT
                       ↓
             USER + ADMIN FEATURES
                       ↓
                TESTING + SECURITY
                       ↓
              OBSERVABILITY + CI/CD
                       ↓
                  PRODUCTION
```

The roadmap is intentionally ordered so that **clinical/data correctness and research validity are established before UI polish and production deployment**.

---

# 28. Roadmap Maintenance

This document must be updated when:

- a phase is completed
- issue priorities change
- architecture changes
- new blockers are discovered
- requirements change
- research methodology changes
- deployment strategy changes

Use status labels:

```text
NOT STARTED
IN PROGRESS
BLOCKED
COMPLETED
DEFERRED
```

Do not delete completed work from project history. Mark it as completed.

---

# 29. Current Recommended Starting Point

Given the documented state of PharmaSafe-KG, the first implementation sequence should be:

```text
1. Repository/security audit
2. Credential removal + rotation
3. Resolver benchmark
4. KG integrity audit
5. DDI batch query
6. Severity validation
7. Leakage-free GNN evaluation
8. GNN inference service
9. FastAPI hardening
10. React foundation
11. Core DDI UI
12. Authentication
13. History/saved lists
14. Admin/feedback
15. Full testing
16. Performance
17. Deployment
18. Final research validation
```

This sequence should be treated as the default plan unless a newly discovered P0 issue changes the dependency order.

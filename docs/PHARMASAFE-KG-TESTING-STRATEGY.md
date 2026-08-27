# PharmaSafe-KG — Testing Strategy

**Version:** 1.0  
**Purpose:** Define how AI coding agents must verify PharmaSafe-KG changes before considering a task complete.

> **Core rule:** A feature is not complete because the code runs. It is complete only when the relevant behavior is verified by automated tests, integration checks, and—where applicable—research/data validation.

---

# 1. Testing Philosophy

PharmaSafe-KG has several correctness boundaries:

```text
User Input
    ↓
Medicine Resolution
    ↓
Knowledge Graph
    ↓
DDI Engine
    ↓
GNN Fallback
    ↓
Explainability
    ↓
FastAPI
    ↓
React
    ↓
User-facing Result
```

A defect at an earlier boundary can produce a clinically misleading result even if the UI itself appears correct.

Therefore testing must cover:

```text
unit
integration
data
graph
ML/research
API
security
frontend
end-to-end
performance
regression
```

---

# 2. Testing Priorities

Priority order:

```text
P0 — Clinical/data correctness
P1 — Security and authorization
P2 — Core DDI API correctness
P3 — Resolver correctness
P4 — GNN/research validity
P5 — Frontend correctness
P6 — Performance and observability
```

A UI enhancement must never take priority over an unresolved P0 correctness problem.

---

# 3. Test Environments

Recommended environments:

```text
development
test
staging
production
```

Tests must not accidentally execute against the production Neo4j or production SQLite database.

Use environment-specific configuration.

---

# 4. Test Categories

## 4.1 Unit Tests

Test isolated functions:

```text
normalization
resolver scoring
pair generation
severity mapping
response transformation
authentication utilities
validation
cache-key generation
```

## 4.2 Integration Tests

Test real component boundaries:

```text
FastAPI → Neo4j
FastAPI → SQLite
DDI engine → Neo4j
DDI engine → GNN
API → resolver
API → persistence
```

## 4.3 End-to-End Tests

Test complete user workflows:

```text
login
→ select medicines
→ run check
→ view interaction
→ view explanation
→ save/revisit history
```

## 4.4 Data Tests

Verify datasets and generated artifacts.

## 4.5 Research/ML Tests

Verify:

```text
split correctness
leakage prevention
metrics
threshold
calibration
OOV behavior
model artifact loading
```

---

# 5. Test Repository Structure

Recommended structure:

```text
tests/
├── unit/
│   ├── test_resolver.py
│   ├── test_pair_generation.py
│   ├── test_severity.py
│   └── test_validation.py
│
├── integration/
│   ├── test_neo4j.py
│   ├── test_sqlite.py
│   ├── test_ddi_engine.py
│   └── test_gnn_inference.py
│
├── api/
│   ├── test_auth.py
│   ├── test_search.py
│   ├── test_check.py
│   ├── test_explain.py
│   ├── test_history.py
│   └── test_admin.py
│
├── e2e/
│   ├── test_login_flow.*
│   ├── test_ddi_flow.*
│   └── test_history_flow.*
│
└── fixtures/
```

The exact framework and directory names should follow the existing repository if they already exist.

---

# 6. Resolver Testing

The resolver is a high-risk component because incorrect brand-to-ingredient mapping can invalidate every downstream result.

## 6.1 Exact Match

Input:

```text
Combiflam
```

Expected:

```text
correct canonical brand
correct ingredient set
match_type = exact
high confidence
```

## 6.2 Case Normalization

Test:

```text
combiflam
COMBIFLAM
Combiflam
```

Expected behavior:

```text
same canonical entity
```

## 6.3 Whitespace

Test:

```text
" Combiflam "
"Combiflam  "
```

## 6.4 Alias

Test known aliases.

Expected:

```text
match_type = alias
```

## 6.5 Generic Direct Input

If supported:

```text
paracetamol
```

Expected:

```text
match_type = generic_direct
```

## 6.6 Fuzzy Match

Test controlled misspellings.

Example:

```text
Combiflamm
```

The test must verify that the returned confidence and match type are consistent.

## 6.7 Ambiguous Match

An ambiguous input must not silently resolve to an arbitrary medicine.

Expected:

```text
low confidence
review required
or unresolved
```

## 6.8 Not Found

Expected:

```text
match_type = not_found
```

The API must not continue as if a valid medicine was selected.

---

# 7. Resolver Benchmark

The resolver should eventually be evaluated using a labeled test set.

Track:

```text
exact accuracy
top-1 accuracy
top-k accuracy
precision
recall
F1
unresolved rate
false positive resolution rate
```

Critical metric:

```text
false positive resolution
```

is especially important because confidently mapping a wrong brand can cause incorrect DDI results.

---

# 8. Pair Generation Tests

For N medicines:

```text
N × (N - 1) / 2
```

Test:

| Medicines | Expected pairs |
|---:|---:|
| 2 | 1 |
| 3 | 3 |
| 4 | 6 |
| 5 | 10 |
| 10 | 45 |

Also test:

```text
duplicate medicines
duplicate normalized names
same medicine in different casing
```

Expected result:

```text
unique pairs only
```

---

# 9. Knowledge Graph Tests

## 9.1 Node Integrity

Verify:

```text
Drug nodes exist
Ingredient nodes exist
required properties exist
no unexpected duplicate identities
```

## 9.2 Relationship Integrity

Verify:

```text
Drug → CONTAINS → Ingredient
Ingredient → INTERACTS_WITH → Ingredient
```

No interaction should point to an invalid ingredient.

## 9.3 Orphan Detection

Find:

```text
orphan Drug nodes
orphan Ingredient nodes
```

Unexpected orphan nodes must be investigated.

## 9.4 Duplicate Relationship Detection

Verify that equivalent interactions are not duplicated unintentionally.

## 9.5 Severity Validation

Check that severity values belong to the supported domain:

```text
MAJOR
MODERATE
MINOR
```

Unexpected values must fail validation or be handled explicitly.

---

# 10. DDI Engine Tests

## 10.1 Documented Interaction

Given a known documented pair:

```text
Drug A + Drug B
```

Expected:

```text
status = documented
source = knowledge_graph
```

## 10.2 KG Miss

Given a pair absent from the KG:

Expected:

```text
not_documented
```

or:

```text
predicted
```

if the validated GNN produces a positive eligible prediction.

## 10.3 GNN Positive

Expected:

```text
status = predicted
source = gnn_predicted
confidence present
```

## 10.4 GNN Unavailable

Expected:

```text
KG miss
+
GNN unavailable
```

must not become:

```text
safe
```

The system must preserve uncertainty.

## 10.5 Neo4j Failure

Simulate:

```text
database unavailable
```

Expected:

```text
dependency error
```

not:

```text
no interactions
```

## 10.6 Resolver Failure

If one medicine cannot be resolved:

```text
status = unresolved
```

or an appropriate structured validation error.

---

# 11. Combination-Medicine Tests

Example:

```text
Drug A
 ├── Ingredient A1
 └── Ingredient A2

Drug B
 ├── Ingredient B1
 └── Ingredient B2
```

The engine must not test only:

```text
A1 ↔ B1
```

unless the product logic explicitly defines that behavior.

All relevant ingredient pairs must be evaluated.

---

# 12. Polypharmacy Integration Tests

For:

```text
3 medicines
```

verify:

```text
3 unique pairs
```

For:

```text
5 medicines
```

verify:

```text
10 unique pairs
```

For a larger list, verify:

```text
batch query behavior
no N+1 database query explosion
```

The project specification explicitly requires batch Cypher for DDI checking.

---

# 13. GNN Testing

The GNN is a research-sensitive component and requires stricter testing than ordinary application code.

## 13.1 Artifact Loading

Verify:

```text
weights file exists
weights load successfully
model architecture matches
feature dimensions match
```

## 13.2 Deterministic Inference

Given the same model and same input:

```text
prediction is reproducible
```

where deterministic execution is expected.

## 13.3 OOV

Unknown ingredient:

```text
OOV
```

must produce:

```text
prediction unavailable
```

not an arbitrary score.

## 13.4 Threshold

The production threshold must come from validation data.

Test that:

```text
threshold is configurable
threshold is not silently changed in inference
```

## 13.5 Leakage

Verify that test edges/nodes are not accidentally included in training data when the evaluation protocol requires separation.

The project roadmap explicitly identifies leakage-free evaluation as a required validation step.

---

# 14. GNN Research Metrics

At minimum report:

```text
ROC-AUC
PR-AUC
precision
recall
F1
confusion matrix
```

Because DDI prediction is potentially imbalanced, PR-AUC should receive particular attention.

Also report:

```text
positive class count
negative class count
class distribution
```

---

# 15. Calibration Tests

If GNN confidence is exposed to users, evaluate calibration.

Possible metrics:

```text
Brier score
Expected Calibration Error
reliability curve
```

Do not label a raw sigmoid probability as a clinically calibrated probability without evidence.

---

# 16. Severity Testing

Severity must be tested independently from interaction detection.

Tests should cover:

```text
known MAJOR
known MODERATE
known MINOR
missing severity
unexpected severity
conflicting source severity
```

Verify:

```text
source severity
→ transformation
→ API severity
→ frontend label
```

are consistent.

---

# 17. Explainability Tests

## Documented Interaction

Verify explanation contains:

```text
input medicines
resolved ingredients
interaction evidence
severity
mechanism
source
```

## GNN Prediction

Verify explanation identifies:

```text
AI prediction
model
model version
confidence/probability
```

Do not generate a fabricated biochemical mechanism from the model output.

---

# 18. API Tests

Every endpoint should have:

```text
success test
validation test
authentication test
authorization test
dependency failure test
```

where applicable.

---

# 19. Authentication Tests

Test:

```text
register
duplicate registration
login
wrong password
expired token
invalid token
logout
forgot password
reset password
```

Security assertions:

```text
password is never returned
password hash is never returned
tokens are not logged
```

---

# 20. Authorization Tests

Verify:

```text
normal user → user endpoints
admin → admin endpoints
normal user → admin endpoint = 403
user A → user B resource = 403/404
```

This is mandatory for:

```text
history
patient lists
feedback
admin users
admin metrics
admin feedback
```

---

# 21. API Validation Tests

Test:

```text
missing fields
wrong types
empty arrays
oversized arrays
invalid enums
invalid UUIDs
invalid pagination
invalid drug names
```

The API must return structured validation errors.

---

# 22. Rate-Limit Tests

The target specification documents:

```text
/check        100/hour/IP
/search       300/hour/IP
/register       5/hour/IP
forgot password 3/hour/IP
```

Tests must verify:

```text
requests below limit → success
request above limit → 429
```

Do not hard-code these limits into tests if environment configuration makes them configurable; test the configured values.

---

# 23. CORS Tests

Verify:

```text
allowed frontend origin → allowed
unknown origin → blocked
```

Production must not use:

```text
Access-Control-Allow-Origin: *
```

when credentialed authentication is involved.

---

# 24. SQL/SQLite Tests

Test:

```text
user creation
unique email
history insertion
history ownership
patient list creation
patient list ownership
feedback creation
password reset expiration
```

Also test foreign-key behavior where enabled.

---

# 25. Frontend Unit Tests

Important components:

```text
MedicineSelector
DrugInput
InteractionCard
SeverityBadge
ResolutionReview
GraphVisualization
HistoryList
PatientLists
Auth forms
Admin tables
```

Test:

```text
loading
success
empty
error
unavailable
predicted
documented
unresolved
```

---

# 26. Frontend API-State Tests

The UI must correctly distinguish:

```text
loading
success
empty
validation error
authentication error
server error
database unavailable
GNN unavailable
```

Never render:

```text
"Safe"
```

merely because the API returned an empty interaction list.

---

# 27. End-to-End Critical Journey

The primary E2E test should be:

```text
Open application
    ↓
Register/Login
    ↓
Select 2+ medicines
    ↓
Resolve medicines
    ↓
Review resolution
    ↓
Run DDI check
    ↓
View summary
    ↓
Open interaction details
    ↓
View explanation
    ↓
Save/revisit history
```

Expected result:

```text
correct data
correct provenance
correct severity
correct uncertainty
```

---

# 28. E2E Failure Journey

Test:

```text
unknown medicine
```

Expected:

```text
clear unresolved state
```

Test:

```text
Neo4j unavailable
```

Expected:

```text
service/dependency error
```

Test:

```text
GNN unavailable
```

Expected:

```text
KG result still shown where available
GNN prediction unavailable
```

---

# 29. Regression Testing

Every bug fix should add a regression test.

Pattern:

```text
Bug discovered
     ↓
Reproduce
     ↓
Write failing test
     ↓
Fix
     ↓
Test passes
     ↓
Keep test permanently
```

AI agents must not remove a regression test simply because the implementation changed.

---

# 30. Performance Tests

Measure:

```text
/search latency
/check latency
/explain latency
Neo4j query latency
resolver latency
GNN inference latency
frontend load time
```

Track:

```text
p50
p95
p99
```

The project performance target specifies:

```text
/search p95 < 300 ms
/check p95 < 2 s for 10 drugs
```

subject to the actual production environment and measurement methodology.

---

# 31. N+1 Detection

The DDI engine must be tested for query explosion.

For:

```text
10 drugs → 45 pairs
```

verify that the implementation uses batch operations rather than:

```text
45 independent database queries
```

where batch querying is possible.

---

# 32. Security Testing

Test for:

```text
Cypher injection
SQL injection
XSS
CSRF where applicable
broken authorization
credential leakage
token leakage
rate-limit bypass
unsafe CORS
```

Especially verify Neo4j parameterization.

Never construct Cypher from raw user input.

---

# 33. Data Pipeline Tests

Every data-processing stage should validate:

```text
input exists
expected columns exist
row counts are plausible
required values are non-null
duplicates are measured
output is generated
output schema is stable
```

Pipeline runs should record:

```text
input version
output version
row counts
timestamp
processing script/version
```

---

# 34. KG Loading Tests

After KG ingestion verify:

```text
node count
relationship count
node uniqueness
relationship integrity
severity distribution
ingredient count
drug count
```

The currently documented graph baseline is approximately:

```text
48,000 Drug nodes
2,073 Ingredient nodes
100,000 INTERACTS_WITH relationships
71,512 CONTAINS relationships
```

These are baseline values from the documented current state, not immutable constants. fileciteturn13file17

---

# 35. Test Fixtures

Fixtures should include:

```text
known exact brand
known alias
known generic
known fuzzy input
known unresolved input
known documented interaction
known non-interaction
known GNN-positive case
known OOV case
known severity examples
```

Use synthetic fixtures for security and failure testing when real pharmaceutical data is unnecessary.

---

# 36. Mocking Policy

Mock dependencies when testing isolated behavior.

Examples:

```text
resolver unit test → mock database
API unit test → mock service
GNN service unit test → mock model
```

But integration tests must also execute against realistic dependencies.

Do not make the entire test suite pass by mocking away the actual system.

---

# 37. Test Data Safety

Do not use real patient-identifiable information in tests.

Test data should be:

```text
synthetic
anonymized
non-sensitive
```

---

# 38. CI Pipeline

Recommended CI order:

```text
1. Formatting
2. Linting
3. Type checking
4. Unit tests
5. Data/schema validation
6. Integration tests
7. API tests
8. Frontend tests
9. Security checks
10. Build
11. E2E tests
```

Heavy GNN/research evaluation can run in a separate CI job when appropriate.

---

# 39. Minimum PR Test Requirements

Every pull request/change should provide:

```text
tests added/updated
```

when behavior changes.

Minimum checks:

```text
lint
typecheck
unit tests
relevant integration tests
build
```

For changes to:

```text
resolver → resolver tests
DDI engine → DDI integration tests
Neo4j schema → KG validation
GNN → ML evaluation/tests
auth → security tests
API → API tests
React → frontend tests
```

---

# 40. AI-Agent Definition of Done

An AI agent must not claim a task is complete until it has:

- [ ] Read the relevant project documentation.
- [ ] Inspected the affected code.
- [ ] Identified existing tests.
- [ ] Implemented the change.
- [ ] Added/updated tests.
- [ ] Run relevant tests.
- [ ] Checked lint/type errors.
- [ ] Checked integration behavior.
- [ ] Checked error paths.
- [ ] Updated documentation if the contract changed.
- [ ] Reported any tests that could not be run.

---

# 41. AI-Agent Test Report

Every substantial coding task should end with:

```text
## Implementation
- changed files
- behavior changed

## Tests
- tests added
- tests executed
- results

## Validation
- API verified
- database verified
- frontend verified
- ML/data validation verified

## Remaining Risks
- known failures
- unavailable environments
- assumptions requiring review
```

An agent must never report:

```text
"All tests passed"
```

unless the tests were actually executed.

---

# 42. Research Reproducibility

For ML/data changes, record:

```text
dataset version
split seed
random seed
model version
hyperparameters
threshold
evaluation metrics
environment/dependency versions
```

The project's research requirements emphasize reproducibility and versioning of datasets, KG, resolver rules, severity logic, model artifacts and experiments. fileciteturn13file2

---

# 43. Coverage Targets

Initial engineering target:

```text
Core resolver: ≥90%
DDI engine: ≥90%
API critical paths: ≥85%
Authentication/security: ≥90%
Frontend critical components: ≥80%
```

Coverage percentage alone is not sufficient.

A test suite with high coverage but no clinical/data correctness tests is unacceptable.

---

# 44. Critical Regression Suite

Before a release, always execute:

```text
1. exact brand resolution
2. fuzzy/alias resolution
3. unresolved medicine
4. documented DDI
5. KG-missing pair
6. GNN positive prediction
7. GNN unavailable
8. Neo4j unavailable
9. combination medicine
10. 10-drug batch
11. authentication
12. user isolation
13. admin authorization
14. rate limit
15. frontend DDI workflow
```

---

# 45. Release Gate

A release should be blocked if any of these occur:

```text
critical security failure
incorrect medicine resolution
incorrect documented DDI result
database failure interpreted as no interaction
GNN prediction presented as documented evidence
authorization bypass
test suite regression
broken production build
unverified model artifact
data corruption
```

---

# 46. Testing Workflow for Antigravity/Codex

When an AI agent receives a task:

```text
READ
 ↓
CURRENT-STATE
 ↓
PRD
 ↓
ISSUES
 ↓
ARCHITECTURE
 ↓
API-SPEC
 ↓
DATA-DICTIONARY
 ↓
ROADMAP
 ↓
TESTING-STRATEGY
 ↓
INSPECT CODE
 ↓
PLAN
 ↓
IMPLEMENT
 ↓
TEST
 ↓
VALIDATE
 ↓
REPORT
```

The agent should make the smallest change that satisfies the task while preserving validated behavior.

---

# 47. Final Principle

PharmaSafe-KG is not merely a CRUD web application.

Its correctness depends on the chain:

```text
correct input
    ↓
correct resolution
    ↓
correct graph data
    ↓
correct DDI query
    ↓
correct GNN fallback
    ↓
correct provenance
    ↓
correct explanation
    ↓
correct API response
    ↓
correct UI interpretation
```

Testing must therefore validate the **entire evidence chain**, not only whether individual functions execute.

---

# 48. Source Basis

This strategy follows the documented project architecture, PRD, current-state analysis, API requirements and roadmap. The project documentation explicitly requires resolver benchmarking, KG integrity checks, leakage-free GNN evaluation, threshold selection, calibration, API testing, security validation, and production hardening. fileciteturn13file19turn13file2

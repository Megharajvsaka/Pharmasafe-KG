# PharmaSafe-KG — AI Development Agent Guidelines

**Version:** 1.0  
**Purpose:** Operating manual for Antigravity, Codex, and other AI coding agents working on PharmaSafe-KG.

> **Primary rule:** AI agents must modify the existing project deliberately, not rebuild it from assumptions. Existing code, project documentation, data, APIs, research artifacts, and working behavior must be inspected before changes are made.

---

# 1. Mission

The AI agent is responsible for helping build PharmaSafe-KG into a production-ready, explainable drug–drug interaction detection platform.

The agent must preserve the project's core chain:

```text
User
 ↓
Medicine Resolution
 ↓
Knowledge Graph
 ↓
Documented DDI Detection
 ↓
GNN Fallback
 ↓
Explainability / Provenance
 ↓
FastAPI
 ↓
React
 ↓
User
```

A change is successful only when it improves the required behavior without silently breaking another part of this chain.

---

# 2. Mandatory Documentation Reading Order

Before making substantial changes, read the project documentation in this order:

```text
1. PRD.md
2. CURRENT-STATE.md
3. ISSUES.md
4. ARCHITECTURE.md
5. DATA-DICTIONARY.md
6. API-SPEC.md
7. ROADMAP.md
8. TESTING-STRATEGY.md
9. SECURITY-SPEC.md
10. this document
```

If a document does not exist yet, the agent should state that instead of pretending it was read.

---

# 3. Source of Truth Hierarchy

When information conflicts, use this priority:

```text
1. Actual working code
2. Current database/data artifacts
3. Current API schemas/contracts
4. CURRENT-STATE.md
5. PRD.md
6. ARCHITECTURE.md
7. Other planning documentation
8. Agent assumptions
```

Planning documents describe intended behavior; the repository determines what currently exists.

The agent must not silently rewrite documentation to make an incorrect implementation appear correct.

---

# 4. Initial Repository Inspection

Before modifying code, inspect:

```text
repository tree
README
package files
Python requirements
environment configuration
backend
frontend
database code
Neo4j code
ML/GNN code
tests
scripts
data directories
Docker/deployment configuration
```

Identify:

```text
entry points
API routes
service boundaries
database clients
authentication middleware
frontend routing
state management
model loading
configuration
existing tests
```

---

# 5. Never Start by Rebuilding

Do not:

```text
delete the existing implementation
rewrite the entire application
replace working modules without evidence
create duplicate services
create duplicate routes
replace the database unnecessarily
```

First determine whether the requested capability already exists partially.

Prefer:

```text
inspect → reuse → refactor → extend
```

over:

```text
delete → recreate
```

---

# 6. Change Planning Protocol

For every non-trivial task:

```text
Understand
 ↓
Inspect
 ↓
Identify dependencies
 ↓
Plan
 ↓
Implement
 ↓
Test
 ↓
Review
 ↓
Report
```

Before implementation, identify:

```text
files to change
files that may be affected
API contracts
database changes
frontend dependencies
security impact
tests required
documentation changes
```

---

# 7. Minimal Change Principle

Make the smallest safe change that fully solves the task.

Avoid unrelated:

```text
refactors
renaming
dependency upgrades
UI redesigns
architecture changes
database migrations
```

unless they are necessary.

A task to fix one endpoint does not automatically authorize rewriting the backend.

---

# 8. Existing Behavior Preservation

Before changing a working feature, identify its current behavior.

After the change, verify that:

```text
existing valid inputs still work
existing API contracts remain compatible
existing authentication remains functional
existing data remains readable
existing UI flows remain functional
```

If intentional breaking behavior is required, document it before implementation.

---

# 9. Backend Development Rules

Backend changes must preserve the established service architecture.

Before changing a route, inspect:

```text
router
schema
service
database/repository
authentication
error handling
tests
```

Do not put complex business logic directly inside route handlers when the project already uses service-layer separation.

---

# 10. API Contract Rules

Every API change must consider:

```text
request schema
response schema
status codes
authentication
authorization
validation
errors
rate limits
frontend consumers
tests
```

Do not change a response field casually.

If a contract changes:

```text
update API-SPEC.md
update backend
update frontend
update tests
```

---

# 11. DDI Engine Rules

The DDI engine is a critical component.

The agent must preserve the distinction between:

```text
documented interaction
predicted interaction
no documented interaction
unresolved medicine
dependency failure
```

Never collapse all non-positive cases into:

```text
safe
```

---

# 12. Medicine Resolution Rules

The resolver must remain explicit about:

```text
exact match
alias
generic direct match
fuzzy match
ambiguous
not found
```

The agent must not silently lower confidence thresholds merely to increase match rates.

If resolver behavior changes, add/update:

```text
unit tests
benchmark cases
regression cases
```

---

# 13. Knowledge Graph Rules

Before modifying Neo4j:

```text
inspect existing labels
inspect properties
inspect constraints/indexes
inspect relationships
inspect ingestion scripts
inspect queries
```

Do not invent a new graph schema when the existing schema already supports the feature.

All user-provided values must be parameterized.

---

# 14. Graph Integrity

After graph changes, validate:

```text
node counts
relationship counts
required properties
relationship integrity
duplicate identities
orphan entities
severity values
```

If an ingestion operation changes counts substantially, investigate the reason.

---

# 15. DDI Query Rules

Prefer batch graph queries for polypharmacy.

For N medicines:

```text
N × (N - 1) / 2
```

unique pairs should be evaluated.

Avoid accidental N+1 query behavior.

---

# 16. Combination Medicine Rules

A combination product may contain multiple ingredients.

The agent must not assume:

```text
one brand = one ingredient
```

When combination products are supported, the interaction engine must evaluate the relevant ingredient-level combinations.

---

# 17. GNN Rules

The GNN is a research component, not merely another API dependency.

Agents must not:

```text
invent model metrics
invent model explanations
claim clinical validity
change thresholds arbitrarily
train on test data
introduce leakage
```

If model behavior changes, report:

```text
model version
artifact
dataset
threshold
evaluation
limitations
```

---

# 18. GNN Fallback Rules

If the KG does not document an interaction:

```text
KG miss
 ↓
eligible GNN inference
 ↓
predicted / unavailable
```

If the GNN is unavailable:

```text
do not fabricate a prediction
```

Do not transform:

```text
GNN unavailable
```

into:

```text
no interaction
```

---

# 19. Explainability Rules

Every user-facing interaction result must retain provenance appropriate to its source.

Documented evidence should identify:

```text
source
interaction
ingredients
severity
mechanism/evidence where available
```

Predicted results should identify:

```text
model
prediction
confidence/probability
model version where available
```

The agent must never fabricate a mechanism that is not supported by project data or validated sources.

---

# 20. Security Rules

Before modifying security-sensitive code, consult:

```text
SECURITY-SPEC.md
TESTING-STRATEGY.md
```

Never:

```text
disable auth
disable authorization
hard-code credentials
commit .env
allow arbitrary Cypher
concatenate SQL
enable wildcard credentialed CORS
remove rate limiting as a shortcut
```

---

# 21. Authentication Rules

Never trust client-provided:

```text
user_id
role
permissions
ownership
```

The backend must derive identity and authorization from authenticated server-side state.

---

# 22. User Data Rules

For user-owned resources:

```text
authenticated user
        ↓
ownership check
        ↓
resource
```

must occur server-side.

Do not rely on frontend filtering.

---

# 23. Frontend Development Rules

Before changing a React page/component, inspect:

```text
route
component hierarchy
API client
types/interfaces
state management
loading state
error state
existing design system
```

Do not duplicate API clients or data types unnecessarily.

---

# 24. UI State Rules

For every asynchronous feature, consider:

```text
idle
loading
success
empty
validation error
authentication error
server error
dependency unavailable
```

The UI must not display misleading success states when a dependency failed.

---

# 25. Clinical Result Presentation

The frontend must clearly distinguish:

```text
Documented
Predicted
Unresolved
Unavailable
```

Do not visually present an AI prediction as equivalent to a documented database interaction.

---

# 26. Database Migration Rules

Never modify database schemas casually.

Before a migration:

```text
inspect current schema
identify existing data
plan forward migration
consider rollback
update models
update tests
```

Never destroy user data to simplify development.

---

# 27. Data Artifact Rules

Important artifacts may include:

```text
master_mapping_table.csv
drugbank_ddi_cleaned.csv
Neo4j graph
GraphSAGE weights
node embeddings
resolver data
```

Before modifying them:

```text
identify source
identify version
identify consumers
validate schema
```

Do not silently overwrite research artifacts.

---

# 28. Environment Rules

Use environment configuration for:

```text
database credentials
JWT secrets
API keys
URLs
deployment-specific settings
```

Do not hard-code environment-specific values.

---

# 29. Dependency Rules

Before adding a dependency:

```text
confirm it is necessary
check whether existing dependencies already solve the problem
check compatibility
check maintenance
check security
```

Do not add packages merely because they make a small task easier.

---

# 30. Testing Protocol

After implementation:

```text
1. Run targeted tests.
2. Run related integration tests.
3. Run lint/type checks.
4. Run build checks.
5. Run broader regression tests when appropriate.
6. Inspect failures.
7. Fix failures caused by the change.
```

Never skip tests just because the code "looks correct."

---

# 31. Test Creation Rule

Every behavioral bug fixed by an AI agent should receive a regression test whenever practical.

Pattern:

```text
bug
 ↓
reproduce
 ↓
failing test
 ↓
fix
 ↓
passing test
```

---

# 32. No Fake Verification

The agent must never claim:

```text
tests passed
build passed
API verified
database verified
deployment successful
```

unless it actually performed the corresponding verification.

If a test cannot run, report:

```text
NOT RUN
```

and explain why.

---

# 33. Error Diagnosis Protocol

When a command fails:

```text
read the complete error
identify root cause
inspect relevant configuration/code
make the smallest correction
rerun
```

Do not repeatedly make random changes.

---

# 34. Do Not Hide Errors

Do not:

```text
catch every exception and return success
suppress test failures
ignore TypeScript errors
ignore lint failures
disable validation
```

An error should be handled intentionally and transparently.

---

# 35. Documentation Synchronization

Update documentation when changes affect:

```text
architecture
API contract
database schema
data model
security
testing
deployment
research methodology
user-visible behavior
```

Do not update documentation merely to claim an unfinished feature is complete.

---

# 36. Git Discipline

AI agents should keep changes reviewable.

Prefer:

```text
focused changes
clear commit boundaries
no generated junk
no secrets
no unrelated formatting churn
```

Do not rewrite Git history or delete branches unless explicitly instructed.

---

# 37. File Safety

Never delete important files merely because they appear unused.

Before deleting:

```text
search references
inspect imports
inspect build configuration
inspect documentation
inspect deployment scripts
```

If uncertain:

```text
ask
```

---

# 38. When the Agent Must Stop and Ask

The agent should stop and ask for clarification when:

```text
requirements conflict
clinical behavior is ambiguous
database migration could destroy data
security architecture is unclear
two incompatible APIs exist
research methodology is underspecified
a destructive operation is required
a critical project assumption is unknown
```

Do not guess when the decision can materially affect correctness.

---

# 39. When the Agent May Proceed

The agent may make reasonable implementation decisions when:

```text
requirements are explicit
existing architecture provides the pattern
change is reversible
risk is low
behavior is covered by tests
```

Document important assumptions.

---

# 40. AI-Agent Context Preservation

At the beginning of each task, the agent should build a compact mental/project context:

```text
Goal
Current implementation
Relevant files
Relevant data
Dependencies
Constraints
Acceptance criteria
Tests
```

Do not repeatedly rediscover the repository without reason.

---

# 41. Task Execution Template

For a typical task:

```text
## Task
<requested feature/fix>

## Relevant Documentation
<documents inspected>

## Current Implementation
<what exists>

## Plan
1. ...
2. ...
3. ...

## Changes
<implementation>

## Tests
<commands/results>

## Risks
<remaining risks>

## Documentation Updated
<files>
```

---

# 42. Feature Completion Checklist

Before declaring a feature complete:

- [ ] Requirement understood.
- [ ] Existing implementation inspected.
- [ ] Relevant documentation read.
- [ ] Architecture preserved.
- [ ] API contract verified.
- [ ] Security implications checked.
- [ ] Database impact checked.
- [ ] Tests added/updated.
- [ ] Targeted tests executed.
- [ ] Regression tests executed where relevant.
- [ ] Build/lint/type checks executed.
- [ ] Error paths verified.
- [ ] Documentation synchronized.
- [ ] Remaining limitations reported.

---

# 43. Critical DDI Release Checklist

Before declaring the core DDI workflow complete:

```text
[ ] Medicine search works.
[ ] Brand resolution works.
[ ] Generic resolution works where supported.
[ ] Ambiguous resolution is visible.
[ ] Unresolved input is handled.
[ ] Pair generation is correct.
[ ] Neo4j query is parameterized.
[ ] Documented interactions are returned correctly.
[ ] GNN fallback is correctly gated.
[ ] GNN unavailable state is preserved.
[ ] Severity is correct.
[ ] Provenance is visible.
[ ] Explanation is evidence-based.
[ ] History persistence works.
[ ] User ownership is enforced.
[ ] Frontend states are correct.
[ ] Error states are tested.
```

---

# 44. Production Readiness Checklist

Before production deployment, verify:

```text
Security
[ ] secrets configured securely
[ ] HTTPS enabled
[ ] CORS restricted
[ ] auth enforced
[ ] authorization enforced
[ ] rate limiting active

Backend
[ ] environment configuration correct
[ ] migrations complete
[ ] database connectivity verified
[ ] error handling verified

Neo4j
[ ] schema verified
[ ] indexes/constraints verified
[ ] data integrity checked
[ ] queries parameterized

ML
[ ] model artifact verified
[ ] threshold verified
[ ] leakage checks completed
[ ] metrics recorded
[ ] limitations documented

Frontend
[ ] production build succeeds
[ ] API URL configured
[ ] auth flow verified
[ ] error states verified

Testing
[ ] critical regression suite passes
[ ] security tests pass
[ ] E2E flow passes
```

---

# 45. Agent Anti-Patterns

The following behaviors are prohibited:

## "Make it work" shortcuts

```text
disable authentication
mock everything permanently
return hard-coded results
skip database validation
```

## "Clean rewrite"

```text
replace the project because it is easier
```

## "Silent assumption"

```text
invent missing clinical data
invent model metrics
invent API behavior
invent database fields
```

## "False completion"

```text
claim tests passed without running them
```

## "Scope creep"

```text
change unrelated modules
upgrade unrelated dependencies
redesign unrelated pages
```

---

# 46. Priority When Requirements Conflict

Use this priority:

```text
1. Security
2. Data integrity
3. Clinical/evidence correctness
4. Explicit PRD acceptance criteria
5. Existing API compatibility
6. Architecture consistency
7. UX
8. Convenience
```

Convenience must never override the first four.

---

# 47. Research Integrity

PharmaSafe-KG includes research-oriented components.

Agents must preserve scientific integrity:

```text
no fabricated results
no hidden leakage
no cherry-picked evaluation
no undocumented threshold changes
no unsupported clinical claims
no fabricated explanations
```

When a result is experimental, label it as experimental.

---

# 48. AI-Generated Code Review

AI-generated code must be reviewed for:

```text
correctness
security
edge cases
performance
maintainability
testability
project consistency
```

Do not assume generated code is correct merely because it compiles.

---

# 49. Definition of Done

A task is **DONE** only when:

```text
Requirement
    ↓
Implementation
    ↓
Integration
    ↓
Testing
    ↓
Security review
    ↓
Documentation
    ↓
Verification
```

has been completed to the extent required by the task.

---

# 50. Final Rule

The AI agent is a **developer operating inside an existing engineering and research project**, not an autonomous product designer with permission to redefine the project.

Therefore:

```text
Inspect before changing.
Understand before rewriting.
Reuse before replacing.
Test before claiming success.
Preserve evidence.
Preserve security.
Preserve existing behavior.
Ask when a critical assumption is unknown.
```

The goal is not to generate the most code.

The goal is to make PharmaSafe-KG **correct, explainable, secure, testable, maintainable, and production-ready**.

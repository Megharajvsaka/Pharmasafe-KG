# PharmaSafe-KG — API Specification

**Version:** 1.0  
**Status:** Target API contract  
**Purpose:** Define the communication contract between the PharmaSafe-KG React frontend, FastAPI backend, Knowledge Graph, GNN inference layer, authentication system, and application database.

> **Important:** This document separates API requirements from assumptions about the current implementation. Before changing an existing endpoint, an AI agent must inspect the actual FastAPI routes and preserve compatible behavior unless the task explicitly changes the contract.

---

# 1. API Design Principles

## 1.1 Backend is the source of truth

The frontend must not independently determine:

- whether a DDI exists
- interaction severity
- evidence status
- GNN prediction
- clinical meaning

The frontend displays backend results.

## 1.2 Evidence and prediction are separate

Every interaction result must distinguish:

```text
knowledge_graph
gnn_predicted
not_documented
unavailable
```

A GNN prediction must never be represented as documented evidence.

## 1.3 Failure is not "no interaction"

These states are different:

```text
200 + not_documented
503 + database unavailable
422 + unresolved/invalid input
```

## 1.4 Stable schemas

Request and response models should be defined with Pydantic and shared conceptually with the frontend TypeScript types.

## 1.5 Version the API when breaking changes are necessary

Prefer:

```text
/api/v1/...
```

for a future versioned production contract if the existing deployment does not already establish another convention.

Do not introduce a breaking prefix solely for cosmetic reasons.

---

# 2. API Base

Development:

```text
http://localhost:8000
```

Production:

```text
https://<production-api-domain>
```

The frontend must obtain the API base URL from environment configuration.

Example:

```text
VITE_API_BASE_URL
```

Do not hard-code a production hostname into components.

---

# 3. Authentication Model

The documented target system uses JWT authentication for user-specific functionality.

The existing build specification also describes Bearer API-key authentication for the core `/check` workflow.

Therefore the target authorization model is:

```text
Bearer API key
        OR
Bearer JWT
```

for the compatibility-sensitive core check endpoint, while user-specific endpoints require JWT.

## Token types

### Access token

Used for authenticated API requests.

```http
Authorization: Bearer <access_token>
```

### Refresh token

The target build specification describes refresh-token handling through a secure cookie.

The exact cookie name and attributes must be defined in implementation.

Required security properties:

```text
HttpOnly
Secure in production
SameSite appropriate to deployment
```

---

# 4. Roles

Supported application roles:

```text
doctor
pharmacist
medical_student
researcher
admin
```

The public registration flow should not allow arbitrary role strings.

Admin privileges must be assigned through controlled administration rather than trusting a client-supplied role.

---

# 5. Standard Error Schema

All API errors should use a consistent structure.

Conceptual schema:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": {},
    "request_id": "uuid"
  }
}
```

## Recommended error codes

```text
VALIDATION_ERROR
AUTHENTICATION_REQUIRED
INVALID_TOKEN
TOKEN_EXPIRED
FORBIDDEN
NOT_FOUND
MEDICINE_UNRESOLVED
LOW_CONFIDENCE_RESOLUTION
DATABASE_UNAVAILABLE
GNN_UNAVAILABLE
RATE_LIMITED
INTERNAL_ERROR
```

Do not expose stack traces, credentials, database internals, or model internals unnecessarily.

---

# 6. HTTP Status Conventions

| Status | Meaning |
|---|---|
| 200 | Successful request |
| 201 | Resource created |
| 204 | Successful request with no response body |
| 400 | Invalid request |
| 401 | Authentication required/invalid |
| 403 | Authenticated but not authorized |
| 404 | Resource not found |
| 409 | Conflict |
| 422 | Validation failure |
| 429 | Rate limit exceeded |
| 500 | Unexpected server error |
| 502/503 | Dependency/service unavailable |

---

# 7. Authentication Endpoints

## 7.1 Register

```http
POST /auth/register
```

**Authentication:** None

### Request

```json
{
  "name": "Example User",
  "email": "user@example.com",
  "role": "doctor",
  "password": "StrongPassword123!"
}
```

### Response

```json
{
  "user": {
    "id": "uuid",
    "name": "Example User",
    "email": "user@example.com",
    "role": "doctor"
  },
  "access_token": "jwt",
  "token_type": "bearer"
}
```

If refresh tokens are used, they should be delivered through the intended secure mechanism rather than exposing long-lived credentials unnecessarily in JSON.

### Validation

- valid email
- unique email
- allowed role
- password policy
- non-empty name

---

# 8. Login

```http
POST /auth/login
```

**Authentication:** None

### Request

```json
{
  "email": "user@example.com",
  "password": "StrongPassword123!"
}
```

### Response

```json
{
  "user": {
    "id": "uuid",
    "name": "Example User",
    "email": "user@example.com",
    "role": "doctor"
  },
  "access_token": "jwt",
  "token_type": "bearer"
}
```

Invalid credentials should not reveal whether the email exists.

---

# 9. Logout

```http
POST /auth/logout
```

**Authentication:** JWT

### Response

```json
{
  "message": "Logged out successfully"
}
```

The refresh-token cookie must be cleared if refresh cookies are implemented.

---

# 10. Current User

```http
GET /auth/me
```

**Authentication:** JWT

### Response

```json
{
  "id": "uuid",
  "name": "Example User",
  "email": "user@example.com",
  "role": "doctor",
  "status": "active"
}
```

---

# 11. Forgot Password

```http
POST /auth/forgot-password
```

**Authentication:** None

### Request

```json
{
  "email": "user@example.com"
}
```

### Response

Use a generic success response so account existence is not disclosed.

```json
{
  "message": "If the account exists, a password reset link has been sent."
}
```

The existing build specification describes a reset-token workflow with a short expiration period.

---

# 12. Reset Password

```http
POST /auth/reset-password
```

**Authentication:** Reset token

### Request

```json
{
  "token": "reset-token",
  "new_password": "NewStrongPassword123!"
}
```

### Response

```json
{
  "message": "Password updated successfully"
}
```

---

# 13. Medicine Search

```http
GET /search
```

**Authentication:** As defined by the final deployment policy; the documented target allows rate limiting and core search access.

### Query parameters

```text
q       required
limit   optional
```

Example:

```text
/search?q=combiflam&limit=10
```

### Response

```json
{
  "query": "combiflam",
  "results": [
    {
      "name": "Combiflam",
      "type": "brand",
      "ingredients": [
        "ibuprofen",
        "paracetamol"
      ],
      "match_type": "exact",
      "confidence": 1.0
    }
  ],
  "count": 1
}
```

The exact property names must be reconciled with the existing implementation before replacing the current endpoint.

### Search order

The product requirements specify:

```text
exact
→ normalized
→ prefix
→ generic
→ high-confidence fuzzy
```

---

# 14. Medicine Resolution

If a dedicated resolver endpoint is exposed:

```http
GET /resolve
```

or an equivalent route may be used.

This route is **conceptual unless already present in the repository**.

The preferred response:

```json
{
  "input": "Combiflam",
  "canonical_name": "Combiflam",
  "ingredients": [
    {
      "name": "ibuprofen",
      "strength": null,
      "unit": null
    },
    {
      "name": "paracetamol",
      "strength": null,
      "unit": null
    }
  ],
  "match_type": "exact",
  "confidence": 1.0,
  "review_required": false
}
```

---

# 15. Core DDI Check

```http
POST /check
```

**Authentication:** Bearer API key OR JWT, according to the documented target compatibility model.

The existing project specification explicitly requires `/check` to support the core interaction-check workflow and to use batch processing rather than one database call per pair.

## Request

Preferred contract:

```json
{
  "drugs": [
    "Combiflam",
    "Ecosprin"
  ]
}
```

Alternative existing payloads must be inspected before migration.

### Constraints

- minimum: 2 medicines
- maximum: define/configure a safe product limit
- duplicate medicines should be removed or explicitly rejected
- each medicine must be resolved before DDI processing

---

# 16. DDI Check Processing

```text
POST /check
       ↓
Validate input
       ↓
Resolve medicines
       ↓
Generate unique pairs
       ↓
Batch Neo4j lookup
       ↓
Documented interactions
       ↓
GNN fallback for eligible KG misses
       ↓
Severity + provenance
       ↓
Explanation metadata
       ↓
Persist history if JWT user
       ↓
Return unified response
```

For N medicines:

```text
pairs = N × (N - 1) / 2
```

---

# 17. DDI Check Response

Conceptual response:

```json
{
  "request_id": "uuid",
  "drugs": [
    {
      "input": "Combiflam",
      "canonical_name": "Combiflam",
      "ingredients": ["ibuprofen", "paracetamol"],
      "match_type": "exact",
      "confidence": 1.0
    }
  ],
  "pair_count": 1,
  "results": [
    {
      "drug_a": "Combiflam",
      "drug_b": "Ecosprin",
      "ingredient_a": "ibuprofen",
      "ingredient_b": "aspirin",
      "status": "documented",
      "source": "knowledge_graph",
      "severity": "MODERATE",
      "mechanism": "...",
      "confidence": null,
      "evidence": []
    }
  ],
  "summary": {
    "major": 0,
    "moderate": 1,
    "minor": 0,
    "predicted": 0,
    "not_documented": 0,
    "unresolved": 0
  }
}
```

---

# 18. DDI Result Status

Allowed conceptual states:

```text
documented
predicted
not_documented
unavailable
unresolved
```

## documented

The Knowledge Graph contains supporting interaction evidence.

## predicted

The Knowledge Graph did not document the pair and a validated GNN predicted an interaction.

## not_documented

The pair was checked successfully but no documented interaction was found and no applicable positive GNN prediction was returned.

This must **not** be phrased as "safe."

## unavailable

The system could not reliably complete the check because a required dependency was unavailable.

## unresolved

One or more medicines could not be reliably mapped to standardized ingredients.

---

# 19. DDI Source

```text
knowledge_graph
gnn_predicted
none
unavailable
```

A frontend badge should distinguish:

```text
Documented
AI Predicted
Not Documented
Unavailable
```

---

# 20. Severity

Supported documented severity labels:

```text
MAJOR
MODERATE
MINOR
```

Unknown severity must remain unknown rather than being silently assigned.

Severity must include provenance internally.

Example:

```json
{
  "severity": "MAJOR",
  "severity_source": "source_dataset"
}
```

Do not expose unsupported severity certainty.

---

# 21. Explainability Endpoint

The research architecture explicitly defines an explanation capability through `/explain`.

```http
POST /explain
```

**Authentication:** Same policy as `/check`

### Request

```json
{
  "drug_a": "Combiflam",
  "drug_b": "Ecosprin"
}
```

### Response

```json
{
  "drug_a": "Combiflam",
  "drug_b": "Ecosprin",
  "source": "knowledge_graph",
  "explanation": {
    "summary": "...",
    "mechanism": "...",
    "path": [
      {
        "node": "Combiflam"
      },
      {
        "node": "ibuprofen"
      },
      {
        "relationship": "INTERACTS_WITH"
      },
      {
        "node": "aspirin"
      },
      {
        "node": "Ecosprin"
      }
    ]
  }
}
```

For GNN predictions:

```json
{
  "source": "gnn_predicted",
  "probability": 0.82,
  "model": "GraphSAGE",
  "model_version": "..."
}
```

The system must not fabricate a biochemical mechanism from model probability alone.

---

# 22. Drug Detail

```http
GET /drug/{name}
```

This endpoint is specified by the existing target build architecture.

### Response

```json
{
  "name": "Combiflam",
  "ingredients": [
    "ibuprofen",
    "paracetamol"
  ],
  "interactions": [],
  "metadata": {}
}
```

The exact response must be reconciled with the actual existing route.

Caching target from the build specification:

```text
30 minutes
key = brand_name
```

---

# 23. Graph Explorer

A graph endpoint may expose graph data required by the frontend.

Conceptual route:

```http
GET /graph
```

Possible query parameters:

```text
drug
ingredient
depth
limit
```

Response:

```json
{
  "nodes": [
    {
      "id": "ingredient:ibuprofen",
      "label": "ibuprofen",
      "type": "Ingredient"
    }
  ],
  "edges": [
    {
      "source": "ingredient:ibuprofen",
      "target": "ingredient:aspirin",
      "type": "INTERACTS_WITH",
      "severity": "MODERATE"
    }
  ]
}
```

The endpoint must enforce safe graph-size limits.

---

# 24. User History

```http
GET /user/history
```

**Authentication:** JWT

### Query parameters

```text
page
limit
date_from
date_to
search
severity
```

### Response

```json
{
  "items": [
    {
      "id": "uuid",
      "created_at": "2026-08-27T12:00:00Z",
      "drugs": ["Drug A", "Drug B"],
      "summary": {
        "major": 1,
        "moderate": 0,
        "minor": 0
      }
    }
  ],
  "page": 1,
  "limit": 20,
  "total": 1
}
```

User A must never be able to access User B's history.

---

# 25. Saved Patient Lists

The existing target specification uses:

```http
POST   /user/patients
GET    /user/patients
DELETE /user/patients/{id}
```

**Authentication:** JWT

## Create

```http
POST /user/patients
```

Conceptual request:

```json
{
  "nickname": "Patient A",
  "drugs": [
    "Combiflam",
    "Ecosprin"
  ]
}
```

Avoid collecting unnecessary personally identifiable patient information.

## List

```http
GET /user/patients
```

## Delete

```http
DELETE /user/patients/{id}
```

Ownership must be checked server-side.

---

# 26. Feedback

The documented target includes:

```http
POST /feedback
```

Conceptual request:

```json
{
  "drug_a": "Drug A",
  "drug_b": "Drug B",
  "expected_severity": "MAJOR",
  "actual_severity": "MODERATE",
  "comment": "..."
}
```

The original build specification describes storing feedback in `feedback.jsonl`.

For production, persistence should be reviewed and may be migrated to the application database.

---

# 27. Admin — Users

```http
GET /admin/users
```

**Authentication:** JWT + admin role

Query:

```text
page
limit
search
role
status
```

Response:

```json
{
  "items": [],
  "page": 1,
  "limit": 20,
  "total": 0
}
```

---

# 28. Admin — Update User

```http
PATCH /admin/users/{id}
```

Possible fields:

```json
{
  "role": "pharmacist",
  "status": "active"
}
```

Never allow arbitrary privilege escalation.

---

# 29. Admin — Metrics

```http
GET /admin/metrics
```

Possible metrics:

```text
total_users
active_users
checks_today
checks_total
pairs_checked
major_interactions
gnn_predictions
unresolved_medicines
error_rate
average_latency
```

Metrics must not expose unnecessary personal data.

---

# 30. Admin — Feedback

```http
GET /admin/feedback
```

Pagination required.

## Update

```http
PATCH /admin/feedback/{id}
```

Possible status:

```text
new
reviewing
resolved
dismissed
```

---

# 31. Health Endpoint

```http
GET /health
```

**Authentication:** None

Purpose:

```text
load balancer / uptime monitoring
```

Minimal response:

```json
{
  "status": "healthy"
}
```

Do not expose credentials or sensitive infrastructure details.

---

# 32. System Status

```http
GET /status
```

**Authentication:** None

The target project specification requires system status information such as:

```text
API status
Neo4j status
GNN loaded status
graph statistics
uptime
version
```

Conceptual response:

```json
{
  "status": "healthy",
  "neo4j": "connected",
  "gnn_loaded": true,
  "brands_in_memory": 225449,
  "ingredients_in_graph": 2073,
  "interactions_in_graph": 100000,
  "uptime_seconds": 12345,
  "version": "2.0.0"
}
```

Values must be generated from the running system rather than hard-coded.

---

# 33. Request IDs

Every API request should receive a request ID.

Response header:

```http
X-Request-ID: <uuid>
```

The request ID should be used to correlate:

```text
frontend error
API logs
database errors
monitoring events
```

The existing target build specifically calls for UUID request IDs.

---

# 34. Rate Limits

The documented target limits are:

| Endpoint | Limit |
|---|---:|
| `/check` | 100/hour/IP |
| `/search` | 300/hour/IP |
| `/auth/register` | 5/hour/IP |
| `/auth/forgot-password` | 3/hour/IP |

Return:

```http
429 Too Many Requests
```

with a structured error response.

---

# 35. Caching

Target cache durations documented by the project:

```text
/search     60 seconds
/check      5 minutes
/drug/:name 30 minutes
```

Cache keys must include all inputs that affect the response.

For `/check`, a normalized sorted drug set may be used only when the result is independent of user identity and authorization context.

User-specific responses must not leak through shared caches.

---

# 36. Security Requirements

## Never

```text
concatenate user input into Cypher
```

Use Neo4j parameters.

## Validate

- strings
- array lengths
- drug names
- UUIDs
- enums
- pagination values

## Never expose

```text
password_hash
JWT secrets
API keys
Neo4j credentials
reset tokens in logs
```

## CORS

Read allowed origins from environment configuration.

---

# 37. Frontend API Client

The React application should have one centralized API client.

Conceptual:

```text
src/services/api/
├── client.ts
├── auth.ts
├── medicines.ts
├── ddi.ts
├── history.ts
├── patients.ts
├── feedback.ts
└── admin.ts
```

Components should not repeatedly construct raw Axios requests.

---

# 38. Frontend Type Contract

TypeScript interfaces should mirror backend schemas.

Example:

```ts
type DDIStatus =
  | "documented"
  | "predicted"
  | "not_documented"
  | "unavailable"
  | "unresolved";

type DDISource =
  | "knowledge_graph"
  | "gnn_predicted"
  | "none"
  | "unavailable";
```

The frontend must not silently assume fields exist if the backend does not provide them.

---

# 39. API Contract Compatibility Rules for AI Agents

Before modifying an endpoint, an AI agent must:

1. Locate the existing route.
2. Inspect its request model.
3. Inspect its response model.
4. Search all frontend callers.
5. Search tests.
6. Search documentation.
7. Identify backward-compatibility implications.
8. Implement the smallest safe change.
9. Update tests.
10. Update this document if the contract changes.

---

# 40. Breaking Change Policy

A change is breaking if it modifies:

```text
HTTP method
path
required request field
field type
meaning of a field
authentication requirement
response structure
error semantics
```

Breaking changes require:

```text
API version decision
frontend migration
tests
documentation update
```

---

# 41. API Testing Matrix

## Authentication

- [ ] register success
- [ ] duplicate email
- [ ] invalid password
- [ ] login success
- [ ] expired token
- [ ] invalid token
- [ ] logout
- [ ] forgot password
- [ ] reset password

## Search

- [ ] exact brand
- [ ] generic
- [ ] normalized input
- [ ] fuzzy input
- [ ] no result
- [ ] pagination
- [ ] invalid limit

## DDI

- [ ] two medicines
- [ ] three medicines
- [ ] ten medicines
- [ ] duplicate medicines
- [ ] documented interaction
- [ ] KG miss
- [ ] GNN prediction
- [ ] GNN unavailable
- [ ] unresolved medicine
- [ ] Neo4j unavailable
- [ ] invalid input
- [ ] authentication

## User

- [ ] history isolation
- [ ] pagination
- [ ] patient list create
- [ ] patient list delete
- [ ] unauthorized resource access

## Admin

- [ ] non-admin blocked
- [ ] admin allowed
- [ ] user update
- [ ] metrics
- [ ] feedback review

---

# 42. API Acceptance Criteria

The API layer is considered production-ready only when:

- [ ] All request bodies use validation models.
- [ ] All responses have stable schemas.
- [ ] Authentication is enforced correctly.
- [ ] Admin authorization is enforced.
- [ ] Errors are structured.
- [ ] Request IDs are generated.
- [ ] Rate limits work.
- [ ] CORS is configured securely.
- [ ] User data is isolated.
- [ ] DDI results distinguish evidence from prediction.
- [ ] Database failure cannot appear as "no interaction."
- [ ] GNN failure cannot appear as "no interaction."
- [ ] Batch DDI processing is implemented.
- [ ] API tests pass.
- [ ] Frontend API types match backend schemas.

---

# 43. Current vs Target API Status

The project documentation establishes a mixture of existing and planned endpoints.

### Existing/architecturally established

```text
/check
/explain
```

The research architecture describes FastAPI exposing `/check` and `/explain`.

### Target additions

```text
/auth/register
/auth/login
/auth/logout
/auth/me
/auth/forgot-password
/auth/reset-password

/user/history
/user/patients

/admin/users
/admin/users/{id}
/admin/metrics
/admin/feedback
/admin/feedback/{id}

/feedback
/status
/health
```

The target build specification explicitly describes the authentication, user, admin and status endpoints.

### Routes requiring repository verification

```text
/search
/drug/{name}
/graph
```

These are part of the target frontend/backend architecture, but an AI agent must verify their exact current implementation and schema before treating the above contract as a literal replacement.

---

# 44. API Implementation Order

Recommended order:

```text
1. Existing endpoint audit
        ↓
2. Error + response schemas
        ↓
3. /health + /status
        ↓
4. /search
        ↓
5. /check hardening
        ↓
6. /explain
        ↓
7. /drug + /graph
        ↓
8. Authentication
        ↓
9. User history
        ↓
10. Patient lists
        ↓
11. Feedback
        ↓
12. Admin
        ↓
13. Rate limiting / caching / observability
        ↓
14. Full API integration tests
```

This ordering follows the project's roadmap: stabilize the core data/DDI path before adding product-level functionality.

---

# 45. API Contract Ownership

The following files work together:

```text
PRD.md
    ↓
defines WHAT the product needs

CURRENT-STATE.md
    ↓
defines WHAT currently exists

ARCHITECTURE.md
    ↓
defines HOW components interact

API-SPEC.md
    ↓
defines HOW software components communicate

ROADMAP.md
    ↓
defines WHEN and in WHAT ORDER to implement
```

An AI agent must read all five before making substantial API changes.

---

# 46. Source Basis

This API specification is based on the project's documented target requirements and architecture.

The research architecture describes FastAPI endpoints `/check` and `/explain` as the original application API. The production build specification adds authentication, user, admin, feedback and status endpoint groups and requires the existing endpoints to remain functional. fileciteturn10file1turn10file3

The project architecture requires a KG-first DDI flow, validated GNN fallback, explicit uncertainty, and separation between documented and predicted interactions. fileciteturn10file9

The PRD requires authentication, authorization, batch Cypher, rate limiting, CORS restriction, error handling, history, saved lists, admin functionality and API integration of the validated GNN. fileciteturn10file7

The roadmap places DDI engine hardening before GNN integration, React migration, user features, testing and deployment. fileciteturn10file18

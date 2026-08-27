# PharmaSafe-KG — Security Specification

**Version:** 1.0  
**Purpose:** Define the security requirements that every AI coding agent must follow when implementing, modifying, testing, or deploying PharmaSafe-KG.

> **Core rule:** Security is part of correctness. An AI agent must not weaken authentication, authorization, data isolation, input validation, secret handling, database safety, or production configuration in order to make a feature work.

---

# 1. Security Objectives

PharmaSafe-KG must protect:

```text
user accounts
authentication credentials
JWT/API credentials
user history
saved medicine lists
feedback
administrative functions
Neo4j access
SQLite data
model/data artifacts
application infrastructure
```

The system must also protect the **integrity of clinical/research results**.

A security or data-integrity failure must not silently produce a misleading DDI result.

---

# 2. Security Principles

## 2.1 Least privilege

Every user, service, database credential, and AI agent should receive only the permissions required for its task.

## 2.2 Defense in depth

Use multiple controls:

```text
input validation
authentication
authorization
parameterized queries
rate limiting
secure configuration
logging
monitoring
testing
```

## 2.3 Fail closed

If authorization or a critical dependency cannot be verified:

```text
deny access
```

Do not default to permissive behavior.

## 2.4 Never trust the client

The React application must not be trusted for:

```text
role
ownership
severity
interaction source
permissions
medicine identity
```

The backend must validate these.

---

# 3. Threat Model

Primary threats:

```text
credential theft
broken authentication
broken authorization
privilege escalation
Cypher injection
SQL injection
XSS
CSRF where applicable
API abuse
rate-limit bypass
CORS misconfiguration
secret leakage
sensitive logging
data leakage between users
model/data tampering
dependency compromise
malicious or malformed input
```

---

# 4. Authentication

The application supports authenticated user functionality.

Authentication credentials must be transmitted only over HTTPS in production.

Expected request form:

```http
Authorization: Bearer <token>
```

The exact credential type depends on the endpoint contract:

```text
JWT
API key
```

The frontend must never assume that a successful login means all endpoints are authorized.

---

# 5. Password Security

Passwords must never be stored in plaintext.

Use a modern password hashing algorithm such as the algorithm already established by the project implementation.

The database must store:

```text
password_hash
```

not:

```text
password
```

Password hashes must never appear in:

```text
API responses
frontend state
logs
analytics
error messages
```

---

# 6. Password Policy

The final password policy must be enforced server-side.

At minimum:

```text
minimum length
reasonable complexity/entropy
common-password rejection where practical
```

Do not rely solely on HTML input validation.

---

# 7. Login Protection

Login endpoints must resist credential stuffing and brute-force attacks.

Recommended controls:

```text
rate limiting
generic authentication errors
monitoring
```

Do not reveal whether an email exists.

---

# 8. Registration Security

Registration must validate:

```text
email
password
name
role
```

The client must not be able to assign:

```text
admin
```

through arbitrary registration input.

Allowed roles must be controlled by backend configuration.

---

# 9. JWT Security

JWTs must:

```text
use a strong signing secret/key
have appropriate expiration
validate signature
validate expiration
validate expected claims
```

Never accept an unsigned or improperly signed token.

Do not put sensitive information into JWT payloads.

JWT secrets must come from environment/secret management.

Never commit JWT secrets to source control.

---

# 10. Refresh Tokens

If refresh tokens are used:

```text
HttpOnly
Secure in production
appropriate SameSite policy
```

should be applied to the refresh cookie.

Refresh tokens should be:

```text
rotated or otherwise protected against replay
revoked when required
expired
```

Do not store long-lived authentication secrets in ordinary frontend localStorage unless the security architecture explicitly accepts the risk.

---

# 11. API Key Security

If the core `/check` endpoint uses API-key authentication:

```text
API keys are secrets
```

Never expose them in:

```text
React source
browser bundles
Git
logs
error responses
screenshots
documentation examples containing real credentials
```

Read them from secure server-side configuration.

---

# 12. Authorization

Authorization must be enforced on the backend.

## User resources

A user can access only their own:

```text
history
patient lists
account information
```

## Admin resources

Only authorized administrators can access:

```text
/admin/users
/admin/metrics
/admin/feedback
```

A frontend route guard is not sufficient.

---

# 13. Object-Level Authorization

Every resource containing an ID must verify ownership.

Conceptually:

```text
authenticated_user_id
        ↓
resource.user_id
        ↓
must match
```

Otherwise return:

```text
403 Forbidden
```

or an appropriate `404` to avoid resource enumeration.

---

# 14. Role Escalation Prevention

Never trust a client-supplied role such as:

```json
{
  "role": "admin"
}
```

Changing a role requires an authorized backend operation and preferably an audit trail.

---

# 15. Input Validation

All external input must be validated.

Sources include:

```text
query parameters
JSON bodies
path parameters
headers
cookies
file uploads
```

Validate:

```text
type
length
format
allowed values
array size
encoding
```

---

# 16. Medicine Input Validation

Medicine names should have:

```text
maximum length
reasonable character constraints
normalization
```

The system may preserve original user input for explanation, but database queries must use safe parameterization.

---

# 17. Cypher Injection Prevention

This is a critical requirement.

Never construct Cypher by concatenating user input.

Unsafe:

```python
query = f"MATCH (d:Drug {{name: '{drug}'}}) RETURN d"
```

Safe conceptual pattern:

```python
query = """
MATCH (d:Drug {name: $name})
RETURN d
"""
session.run(query, name=drug)
```

All dynamic values must be passed as Neo4j parameters.

---

# 18. SQL Injection Prevention

Use:

```text
parameterized SQL
ORM/query parameters
```

Never concatenate user input into SQL.

---

# 19. XSS Protection

User-controlled strings must not be rendered as executable HTML.

Potential sources:

```text
medicine input
feedback
user name
comments
API error text
```

React's normal escaping should be preserved.

Avoid `dangerouslySetInnerHTML` unless verified sanitization is present.

---

# 20. CSRF

CSRF protections are required when authentication depends on cookies and requests can be forged cross-site.

Controls may include:

```text
SameSite cookies
CSRF tokens
Origin/Referer validation
```

The exact mechanism must match the final authentication architecture.

---

# 21. CORS

Production CORS must explicitly allow trusted frontend origins.

Do not use:

```text
*
```

for credentialed requests.

Allowed origins must be environment-configurable.

---

# 22. Rate Limiting

The documented target limits are:

```text
/check             100/hour/IP
/search            300/hour/IP
/register            5/hour/IP
forgot-password      3/hour/IP
```

Return:

```http
429 Too Many Requests
```

when limits are exceeded.

---

# 23. Abuse Prevention

Also consider:

```text
request size limits
pagination limits
medicine-list size limits
timeout limits
database query limits
```

Do not allow a malicious client to force:

```text
unbounded graph traversal
huge pair generation
unbounded API responses
```

---

# 24. Graph Query Safety

Graph explorer endpoints must enforce:

```text
maximum depth
maximum nodes
maximum edges
maximum result size
query timeout where supported
```

Do not expose arbitrary Cypher execution through the API.

---

# 25. Database Credentials

Neo4j credentials must be loaded from secure environment configuration.

Do not commit:

```text
NEO4J_URI
NEO4J_USERNAME
NEO4J_PASSWORD
```

or equivalent secrets.

SQLite database files containing user data must not be accidentally committed when treated as runtime data.

---

# 26. Secret Management

Secrets include:

```text
JWT secrets
API keys
Neo4j passwords
database credentials
email credentials
third-party API credentials
cloud credentials
```

Rules:

```text
never commit secrets
never hard-code secrets
never log secrets
never return secrets through APIs
```

Use environment variables or deployment secret managers.

---

# 27. `.env` Security

Development may use:

```text
.env
```

but source control should contain only:

```text
.env.example
```

with placeholder values.

Never commit real credentials.

---

# 28. Logging Security

Logs must not contain:

```text
passwords
JWTs
API keys
refresh tokens
password reset tokens
Neo4j passwords
sensitive user data
```

Useful operational logging includes:

```text
timestamp
request_id
endpoint
status
latency
error_code
service
```

---

# 29. Request IDs

Every API request should receive a request ID.

Example:

```http
X-Request-ID: <uuid>
```

Use it to correlate:

```text
frontend error
API logs
database failure
monitoring
```

Do not use request IDs as authentication credentials.

---

# 30. Error Handling

Production errors must not expose:

```text
stack traces
file paths
database credentials
Cypher queries containing secrets
internal infrastructure details
```

Return structured errors.

Example:

```json
{
  "error": {
    "code": "DATABASE_UNAVAILABLE",
    "message": "The service is temporarily unavailable.",
    "request_id": "uuid"
  }
}
```

Detailed diagnostics belong in protected server logs.

---

# 31. Dependency Failure Security

If Neo4j is unavailable:

```text
do not return "no interaction"
```

If GNN is unavailable:

```text
do not return "no interaction" when the KG has no result
```

If resolver confidence is insufficient:

```text
do not silently continue with an arbitrary ingredient
```

Security and data integrity overlap here.

---

# 32. GNN Model Security

Model artifacts must be treated as application assets.

Protect:

```text
graphsage_weights.pt
node_embeddings.pt
```

Verify:

```text
expected file
expected model architecture
expected feature dimensions
expected version
```

Do not load arbitrary model paths supplied by API clients.

---

# 33. Data Integrity

Generated pharmaceutical datasets must be protected against accidental or malicious modification.

Important artifacts include:

```text
master_mapping_table.csv
drugbank_ddi_cleaned.csv
Neo4j graph
model weights
node embeddings
resolver data
```

Version and validate important artifacts.

---

# 34. File Upload Security

If file upload is ever introduced:

```text
validate file type
validate file size
validate filename
store outside executable paths
scan where appropriate
do not trust MIME type alone
```

Do not add file-upload functionality merely because a future feature could use it.

---

# 35. User Data Privacy

Collect only the information required by the product.

User-specific data includes:

```text
email
name
role
history
saved medicine lists
feedback
```

Patient lists should avoid unnecessary personally identifiable information.

The product should not become a full patient-record system without a separate privacy/compliance design.

---

# 36. Data Isolation

Every user-owned database query must include ownership constraints.

Conceptually:

```sql
SELECT *
FROM user_history
WHERE user_id = :authenticated_user_id
```

Do not fetch all users' records and filter them in the frontend.

---

# 37. Admin Security

Admin functionality is high risk.

Requirements:

```text
server-side role check
audit logging
strict input validation
pagination
no bulk destructive operation without safeguards
```

Sensitive admin actions should record:

```text
admin user
target resource
action
timestamp
result
request_id
```

---

# 38. Account Security

Consider account states:

```text
active
suspended
unverified
```

Suspended users must not access privileged application functionality.

The exact verification workflow must match implemented product requirements.

---

# 39. Password Reset Security

Reset tokens must:

```text
expire
be single-use
be unpredictable
not be logged
```

The password-reset response should not reveal whether an email exists.

---

# 40. Session Security

On logout:

```text
invalidate/clear refresh credentials
```

Do not rely solely on frontend state deletion for session termination.

---

# 41. API Response Security

Responses must contain only fields needed by the client.

Never return:

```text
password_hash
internal tokens
database credentials
admin-only internal fields
```

Use explicit response schemas rather than serializing entire database objects.

---

# 42. Frontend Security

Do not put secrets into:

```text
React source
Vite client environment variables
browser localStorage
browser IndexedDB
```

unless the value is intentionally public.

Remember that client-exposed environment variables are visible to the browser bundle.

Server secrets must remain server-side.

---

# 43. Browser Storage

Avoid storing long-lived authentication secrets in localStorage when a secure cookie architecture is available.

If localStorage is used for non-sensitive state:

```text
do not store passwords
do not store API secrets
do not store refresh tokens
```

---

# 44. Security Headers

Production should consider:

```text
Content-Security-Policy
X-Content-Type-Options
Referrer-Policy
Strict-Transport-Security
Frame protections
```

Exact headers must be compatible with the frontend deployment and third-party resources.

Do not introduce a CSP that breaks the application without testing it.

---

# 45. HTTPS

Production authentication and application traffic must use HTTPS.

HTTP should redirect to HTTPS where appropriate.

HSTS may be enabled after confirming the production domain/deployment is correctly configured.

---

# 46. Health and Status Endpoints

`/health` and `/status` must not expose secrets.

Public status should reveal only safe operational information.

Avoid exposing:

```text
Neo4j password
connection strings
environment secrets
filesystem paths
internal credentials
```

---

# 47. Security Testing

Required security tests include:

```text
Cypher injection
SQL injection
XSS
authentication bypass
authorization bypass
IDOR
role escalation
rate-limit bypass
CORS validation
secret leakage
token leakage
password-reset abuse
```

Corresponding automated tests should be added where practical.

---

# 48. Dependency Security

Keep dependencies:

```text
known
versioned
reviewed
updated
```

Run dependency vulnerability checks where available.

Do not blindly upgrade major versions during unrelated feature work.

---

# 49. Supply-Chain Safety

AI agents must not add a dependency merely because it is convenient.

Before adding a package:

```text
1. verify necessity
2. inspect maintenance
3. inspect license compatibility
4. inspect security reputation
5. minimize dependency scope
```

---

# 50. AI-Agent Security Rules

AI coding agents are explicitly required to follow these rules.

### Never

```text
print secrets for debugging
commit .env
disable authentication to make tests pass
disable authorization
allow wildcard CORS as a shortcut
concatenate user input into Cypher
concatenate user input into SQL
remove rate limits without justification
return stack traces in production
store passwords in plaintext
hard-code credentials
```

### Before changing security-sensitive code

The agent must:

```text
inspect current implementation
inspect environment configuration
inspect related tests
inspect frontend authentication flow
inspect API contract
identify security impact
```

---

# 51. Security Change Protocol

For security-sensitive changes:

```text
1. Identify threat
2. Identify affected assets
3. Inspect existing control
4. Implement smallest safe change
5. Add regression/security test
6. Run complete relevant test suite
7. Check logs/configuration
8. Review for bypass paths
9. Document the change
```

---

# 52. Security Acceptance Criteria

A production-ready release must satisfy:

- [ ] No plaintext passwords.
- [ ] No committed secrets.
- [ ] JWT/API credentials protected.
- [ ] Backend authorization enforced.
- [ ] User data isolated.
- [ ] Admin routes protected.
- [ ] Neo4j queries parameterized.
- [ ] SQL queries parameterized.
- [ ] CORS restricted.
- [ ] Rate limits active.
- [ ] Input validation active.
- [ ] Structured safe errors.
- [ ] Sensitive logging disabled.
- [ ] HTTPS production deployment.
- [ ] Security tests passing.
- [ ] Dependency vulnerabilities reviewed.
- [ ] GNN artifacts loaded only from trusted configured paths.
- [ ] Failure states cannot become false-safe DDI results.

---

# 53. Security Incident Response

If a secret is accidentally exposed:

```text
1. Revoke/rotate the credential immediately.
2. Remove the secret from active configuration.
3. Investigate exposure scope.
4. Search logs/repository history where appropriate.
5. Replace affected credentials.
6. Add a regression/prevention control.
```

Do not merely delete the visible secret from the latest commit and assume the incident is resolved.

---

# 54. Security Review Checklist

Before release:

```text
Authentication
[ ] login secure
[ ] registration secure
[ ] password reset secure
[ ] token expiration verified

Authorization
[ ] user ownership verified
[ ] admin authorization verified
[ ] role escalation blocked

Input
[ ] API validation
[ ] Cypher parameterization
[ ] SQL parameterization
[ ] XSS controls

Infrastructure
[ ] HTTPS
[ ] CORS
[ ] security headers
[ ] secrets configured

Abuse
[ ] rate limiting
[ ] request limits
[ ] graph limits

Data
[ ] user isolation
[ ] logs sanitized
[ ] backups/retention reviewed

ML
[ ] trusted model artifact
[ ] model version verified
[ ] GNN uncertainty preserved
```

---

# 55. Relationship to Other Project Documents

```text
PRD
 ↓
security requirements

CURRENT-STATE
 ↓
current security gaps

ISSUES
 ↓
known security issues

ARCHITECTURE
 ↓
security boundaries

API-SPEC
 ↓
authentication/authorization contract

DATA-DICTIONARY
 ↓
data ownership and sensitivity

TESTING-STRATEGY
 ↓
security verification

ROADMAP
 ↓
implementation order
```

AI agents must consult these documents together.

---

# 56. Final Security Principle

The most important security rule for PharmaSafe-KG is:

```text
Never trade security or evidence integrity for convenience.
```

A feature that works while:

```text
bypassing auth
leaking credentials
accepting arbitrary Cypher
mixing user data
or hiding uncertainty
```

is not a successful implementation.

It is a defect.

---

# 57. Source Basis

This security specification is derived from the project's documented requirements for JWT authentication, role-based access, rate limiting, CORS restrictions, parameterized Cypher, secure configuration, user-data isolation, error handling, and production hardening. The project documentation also requires security testing and distinguishes system/dependency failures from valid "no interaction" results.

# PharmaSafe-KG — UI/UX Specification

**Version:** 1.0  
**Purpose:** Define the UI/UX contract for AI coding agents implementing and modifying the PharmaSafe-KG frontend.

> **Core rule:** AI agents may improve the interface, but must not remove required functionality, hide important clinical/evidence distinctions, or redesign existing flows without first understanding the current implementation and project requirements.

---

# 1. UI/UX Mission

The PharmaSafe-KG interface must make the drug-interaction workflow:

```text
clear
fast
trustworthy
explainable
accessible
consistent
```

The UI is not merely a visual layer. It communicates the distinction between:

```text
documented evidence
AI prediction
uncertain resolution
system/dependency failure
```

These distinctions must remain visible to users.

---

# 2. Primary User Journey

The primary workflow is:

```text
Open application
      ↓
Authenticate if required
      ↓
Enter one or more medicines
      ↓
Resolve medicine names
      ↓
Review resolution status
      ↓
Run interaction check
      ↓
View interaction results
      ↓
Inspect evidence/explanation
      ↓
Review history if needed
```

The UI should minimize unnecessary steps.

---

# 3. Core Screens

The frontend should account for the project's major functional areas:

```text
Landing / Home
Authentication
Dashboard
Interaction Checker
Medicine Search / Resolution
Results
Graph Explorer
History
Saved/Patient Lists where implemented
Feedback
Admin area
```

Exact route names must follow the actual repository implementation and API/UI documentation.

---

# 4. Navigation

Navigation should make the major product capabilities easy to discover.

Typical structure:

```text
Home
Checker
History
Graph
Lists
Feedback
```

Authenticated administrative navigation should expose admin functions only to authorized users.

Do not display admin actions merely because a client-side role value says `admin`.

---

# 5. Interaction Checker

The interaction checker is the primary product surface.

It must make the following obvious:

```text
What medicines are being checked?
What was resolved?
Is the check running?
What was found?
Where did the result come from?
How confident/evidenced is it?
```

---

# 6. Medicine Input

Medicine input should support the resolution workflow.

The UI should provide:

```text
clear input
search/autocomplete where implemented
add medicine
remove medicine
validation
loading state
resolution feedback
```

Avoid ambiguous controls.

A user should always know which medicines are currently included in the check.

---

# 7. Polypharmacy Input

When multiple medicines are entered, show them as distinct items.

Example conceptual UI:

```text
[Medicine A] [×]
[Medicine B] [×]
[Medicine C] [×]
```

The interface should make it clear that pairwise interactions are being evaluated.

For N medicines:

```text
N × (N - 1) / 2
```

unique pairs may be evaluated.

---

# 8. Resolution Status

Medicine resolution should have explicit visual states.

Recommended conceptual states:

```text
Resolved — exact
Resolved — alias
Resolved — fuzzy
Ambiguous
Not found
```

Do not silently convert:

```text
Ambiguous
```

into a confident result.

---

# 9. Ambiguous Resolution

If multiple possible medicines match the input, the user should be given enough information to make an informed selection.

The UI should not silently choose a low-confidence result merely to keep the workflow moving.

---

# 10. Unresolved Medicine

If a medicine cannot be resolved:

```text
tell the user
identify the unresolved input
explain what action is possible
```

Do not pretend the medicine was checked successfully.

---

# 11. Check Button

The primary interaction-check action should be visually prominent.

It should become unavailable when required input is invalid.

During execution:

```text
disable duplicate submission
show loading state
preserve entered medicines
```

Do not leave the user wondering whether the request was submitted.

---

# 12. Loading State

Loading states should communicate meaningful progress where practical.

Example:

```text
Resolving medicines…
Checking knowledge graph…
Running prediction fallback…
Preparing explanation…
```

Do not display fake progress percentages.

If the backend provides only one loading state, use a truthful generic state such as:

```text
Checking interactions…
```

---

# 13. Result Categories

The results interface must distinguish at least:

```text
Documented interaction
Predicted interaction
No documented interaction
Unresolved
Unavailable / dependency failure
```

Do not present all of these as equivalent green/red outcomes.

---

# 14. Documented Interaction

A documented interaction should communicate:

```text
medicine pair
severity
evidence/source
interaction description
mechanism where supported
```

The exact fields depend on the API contract and available data.

---

# 15. Predicted Interaction

A GNN-derived prediction should clearly indicate:

```text
AI / predicted
confidence or probability
model information where available
limitations
```

It must not be visually represented as if it were a directly documented interaction.

---

# 16. No Interaction

"No interaction found" must be used carefully.

It should mean:

```text
the system completed the relevant check
and did not identify an applicable interaction
```

It must not be used when:

```text
Neo4j failed
GNN failed
medicine resolution failed
API failed
```

---

# 17. Dependency Failure

If a required dependency is unavailable, show an explicit error/unavailable state.

Examples:

```text
Knowledge graph unavailable
Prediction service unavailable
Server unavailable
```

Never convert infrastructure failure into:

```text
No interaction
```

---

# 18. Severity Presentation

Severity must be visually distinguishable.

The UI should support the severity values actually used by the project.

Do not invent severity categories in the frontend.

If the backend returns an unknown severity:

```text
display safely
```

rather than crashing.

---

# 19. Result Hierarchy

A useful result card hierarchy is:

```text
Medicine A ↔ Medicine B
        ↓
Severity
        ↓
Result type
        ↓
Interaction summary
        ↓
Evidence / confidence
        ↓
Explanation
```

The most clinically relevant information should be visible first.

---

# 20. Explainability

Explanation should be available without overwhelming the primary result.

Useful interaction pattern:

```text
Result
  ↓
"Why?"
  ↓
Evidence / mechanism / provenance
```

Do not hide essential evidence behind multiple layers of navigation.

---

# 21. Provenance

Where provenance is available, show:

```text
source
evidence type
data origin
model source
```

Use the terminology established by the backend/API.

Do not fabricate citations or sources.

---

# 22. Knowledge Graph Visualization

Graph Explorer should communicate graph relationships visually.

Typical conceptual structure:

```text
Drug
 ↓
Ingredient
 ↓
Target / Mechanism
 ↓
Interaction
 ↓
Drug
```

The actual graph schema must come from the project's Neo4j implementation.

---

# 23. Graph Explorer Safety

Graph Explorer should not expose unrestricted database querying to normal users.

The UI should provide controlled exploration through supported API functionality.

Large graphs should be bounded by:

```text
node limits
edge limits
depth limits
```

---

# 24. History

History should allow authenticated users to review their own previous checks.

Typical information:

```text
date/time
medicines
result summary
interaction count
status
```

Users must never see another user's history.

---

# 25. Empty States

Every major list should have a meaningful empty state.

Examples:

```text
No previous checks yet.
No saved medicines yet.
No feedback submitted.
No interactions found.
```

Empty states must be distinguished from errors.

---

# 26. Error States

Error messages should be:

```text
specific enough to understand
short enough to scan
actionable where possible
```

Avoid:

```text
Something went wrong
```

when the system can safely provide more useful information.

---

# 27. Authentication UI

Authentication screens should include:

```text
email
password
submit action
validation
loading
failure
success/navigation
```

If registration, password reset, or verification is implemented, each should have its own clear state handling.

---

# 28. Authorization UI

The frontend may hide unauthorized controls for UX, but the backend remains authoritative.

Do not treat:

```text
hidden button
```

as an authorization mechanism.

---

# 29. Admin UI

Admin pages should be visually and functionally separated from ordinary user functionality.

Potential areas:

```text
users
metrics
feedback
system status
```

Only expose features actually supported by the backend.

---

# 30. Forms

Forms must provide:

```text
labels
validation
clear errors
keyboard accessibility
loading state
success state
```

Do not rely on placeholder text as the only label.

---

# 31. Buttons

Buttons must communicate their action.

Prefer:

```text
Check interactions
Add medicine
Remove
View explanation
Retry
Save
```

Avoid ambiguous labels such as:

```text
Go
Submit
Click here
```

unless context makes the action unambiguous.

---

# 32. Destructive Actions

For destructive actions such as deletion:

```text
provide clear action label
show confirmation when appropriate
prevent accidental activation
```

Do not place destructive actions immediately beside primary actions without differentiation.

---

# 33. Responsive Design

The application must work across:

```text
desktop
tablet
mobile
```

The core interaction-check workflow must remain usable on smaller screens.

Do not solve responsiveness by simply hiding required information.

---

# 34. Accessibility

The UI should follow practical WCAG-oriented principles:

```text
keyboard navigation
visible focus
semantic HTML
accessible labels
sufficient contrast
meaningful error messages
screen-reader-compatible controls
```

Do not encode meaning through color alone.

For example:

```text
red = severe
```

must be accompanied by:

```text
text/icon/label
```

---

# 35. Color and Severity

Color should reinforce, not replace, meaning.

Severity labels should contain text.

Example:

```text
HIGH
```

rather than relying only on a red background.

Follow the existing project design system where one exists.

---

# 36. Typography

Typography should prioritize:

```text
readability
hierarchy
consistent scale
```

Clinical/evidence text should remain readable rather than being compressed into decorative cards.

---

# 37. Layout

Use consistent spacing and alignment.

Primary page hierarchy should generally follow:

```text
page title
context/instructions
primary action
results/content
secondary information
```

Avoid excessive visual decoration that competes with interaction results.

---

# 38. Component Reuse

Before creating a new component:

```text
search existing components
identify reusable patterns
extend existing component if appropriate
```

Avoid duplicate versions of:

```text
Button
Card
Modal
Input
Badge
Alert
Loading
```

when the project already has reusable components.

---

# 39. Design System

The agent must inspect the existing design system before changing visual styling.

Identify:

```text
colors
spacing
typography
border radius
shadows
buttons
inputs
cards
badges
icons
```

Do not introduce a second visual language unnecessarily.

---

# 40. UI Consistency

Equivalent concepts should look equivalent.

For example:

```text
all errors → same alert pattern
all loading states → consistent loading treatment
all severity badges → consistent component
all result cards → consistent structure
```

---

# 41. API Loading and Failure Mapping

Frontend states should correspond to backend states.

Conceptually:

```text
HTTP 200 → success
HTTP 400 → validation feedback
HTTP 401 → authentication flow
HTTP 403 → authorization message
HTTP 404 → not found
HTTP 409 → conflict
HTTP 429 → rate-limit message
HTTP 5xx → server/dependency error
```

Exact behavior must follow `API-SPEC.md`.

---

# 42. Network Retry

Retry only when appropriate.

Safe candidates may include transient:

```text
network failure
temporary service unavailable
```

Do not automatically repeat:

```text
invalid input
authentication failure
destructive operations
```

without deliberate design.

---

# 43. Performance UX

For expensive operations:

```text
show loading
prevent duplicate requests
avoid unnecessary rerenders
paginate large datasets
limit graph visualization
```

Do not block the UI unnecessarily.

---

# 44. Search UX

Search should distinguish:

```text
typing
loading
results
no results
error
```

Do not show stale results as though they were the result of the current query.

---

# 45. Feedback UX

Feedback forms should provide:

```text
clear purpose
input validation
submission state
success confirmation
failure state
```

Do not expose internal admin fields to ordinary users.

---

# 46. Notifications

Use notifications for meaningful events.

Avoid excessive:

```text
toasts
popups
alerts
```

Critical interaction information should remain visible in the page rather than disappearing as a toast.

---

# 47. Clinical Safety UX

The interface should avoid implying that PharmaSafe-KG replaces professional clinical judgment.

Where appropriate, communicate that:

```text
documented interactions are evidence-derived
AI predictions are model-based
absence of a detected interaction is not proof of absolute safety
```

Exact disclaimer wording must follow the project's approved product/research documentation.

---

# 48. Data Privacy UX

Do not display unnecessary personal information.

Patient/user data should be minimized in:

```text
tables
cards
logs shown in UI
URLs
browser titles
notifications
```

---

# 49. Mobile Interaction Checker

On mobile:

```text
medicine input remains accessible
selected medicines remain visible
check action remains easy to reach
result cards remain readable
explanation remains accessible
```

Avoid requiring horizontal scrolling for primary content.

---

# 50. Visual Regression Protection

Before changing major UI components, inspect existing screenshots/design references where available.

After significant UI changes, verify:

```text
desktop
mobile
loading
empty
error
success
```

Do not judge only the happy path.

---

# 51. UI Implementation Rules for AI Agents

Before changing a screen:

```text
1. Locate the route.
2. Locate the page component.
3. Locate child components.
4. Locate API calls.
5. Locate state management.
6. Locate existing styling/design system.
7. Identify all user-visible states.
8. Check related tests.
```

Then implement the smallest coherent change.

---

# 52. Do Not Remove Functionality During Redesign

A visual redesign must not accidentally remove:

```text
buttons
navigation
forms
API actions
result details
explanations
filters
history
authentication
```

If a control is intentionally removed, verify that its functionality is either:

```text
no longer required
or
replaced by an equivalent accessible interaction
```

---

# 53. AI-Agent UI Acceptance Checklist

Before declaring a UI task complete:

- [ ] Existing functionality inspected.
- [ ] Required controls preserved.
- [ ] API integration verified.
- [ ] Loading state verified.
- [ ] Empty state verified.
- [ ] Error state verified.
- [ ] Success state verified.
- [ ] Authentication state verified where relevant.
- [ ] Mobile layout verified.
- [ ] Desktop layout verified.
- [ ] Accessibility basics checked.
- [ ] Evidence/prediction distinction preserved.
- [ ] No unsupported clinical claims introduced.
- [ ] Existing design system reused.
- [ ] No unnecessary duplicate components created.

---

# 54. UI Definition of Done

A UI feature is complete only when:

```text
Functionality
     +
Correct API integration
     +
All important states
     +
Responsive behavior
     +
Accessibility
     +
Security/authorization awareness
     +
Clinical/evidence clarity
```

have been addressed.

---

# 55. Final UI/UX Principle

The PharmaSafe-KG interface should make the user think:

```text
I know what I entered.
I know what the system resolved.
I know what it found.
I know whether the result is documented or predicted.
I know why the system produced it.
I know when the system could not verify something.
```

The UI should optimize for **clarity and trust**, not visual complexity.

---

# 56. Relationship to Other Documents

```text
PRD
 ↓
what users need

CURRENT-STATE
 ↓
what the UI currently does

ISSUES
 ↓
known UI/UX problems

ARCHITECTURE
 ↓
system boundaries

API-SPEC
 ↓
backend/frontend contract

SECURITY-SPEC
 ↓
security constraints

TESTING-STRATEGY
 ↓
UI verification

DEV-AGENT-GUIDELINES
 ↓
how AI agents must modify the UI
```

Agents must consult these documents together before making major frontend changes.

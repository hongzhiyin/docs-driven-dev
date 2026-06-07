# DECISIONS - <project name>

> Source of truth for rationale.
>
> This file records D-XXX trade-offs with context, options, chosen path,
> rationale, risks, and links. It does not track current status.

## Maintenance Rules

1. D-XXX numbers are monotonic: do not reuse and do not skip.
2. Reversing a decision means adding a new D-XXX and marking the old entry as
   superseded; do not rewrite old conclusions.
3. Each non-trivial decision should include at least three options.
4. Risk registration is required, even if the risk is "no known risk".

---

## D-001 - <Step 0 / Phase 0> - <one-line trade-off title>

**Date**: YYYY-MM-DD

**Context**:
<1-3 sentences explaining what triggered this decision.>

**Options**:
- A. <option> - <pros / cons>
- B. <option> - <pros / cons>
- C. <option> - <pros / cons>

**Chosen**: <letter>

**Rationale**:
- <concrete reason>
- <concrete reason>

**Risks**:
- <known limitation and mitigation, or accepted>

**Related code / docs**:
- SPEC §x.y
- `<path>`

---

## Template

```markdown
## D-XXX - <Phase / Step> - <one-line trade-off>

**Date**: YYYY-MM-DD

**Context**:

**Options**:
- A.
- B.
- C.

**Chosen**:

**Rationale**:
-
-

**Risks**:
-

**Related code / docs**:
- SPEC §
- `<path>`
```

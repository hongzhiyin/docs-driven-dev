# DECISIONS - <requirement name>

> Source of truth for requirement-level trade-offs.

## Maintenance Rules

1. D-XXX numbers are monotonic within this packet.
2. Record real options, chosen path, rationale, risks, and related files.
3. Reversing a decision means adding a new D-XXX that supersedes the old one.

---

## D-001 - Step 1 - Scope English-only cleanup to repository text

**Date**: 2026-06-25

**Context**:
The user chose English as docdev's single product language and asked that
Chinese no longer appear in docdev. Existing active runtime guidance, default
change templates, generated decision skeletons, tests, root docs, and archived
change packets contained Chinese or bilingual copy.

**Options**:
- A. Rewrite every historical packet line by line - maximizes inline history,
  but spends a lot of effort on old evidence and risks noisy historical churn.
- B. Scope the change to future generated output and active docs only -
  simpler, but full repository scans would still find non-English archive text.
- C. Standardize future generated output and active guidance on English, while
  compacting old archives into concise English summaries.

**Chosen**: C

**Rationale**:
- The whole repository now needs predictable English text for portability.
- Compact archive summaries preserve packet discoverability without putting old
  maintenance detail into the active skill.
- CLI language branching is not worth the extra product surface.

**Risks**:
- Detailed old packet logs become git-history material instead of inline docs.
  Mitigation: keep packet slugs and root decisions discoverable.

**Related code / docs**:
- SPEC §3.2
- ROADMAP Step 6ab
- `skill/SKILL.md`
- `skill/templates/change/`
- `src/docs_driven_dev/templates.py`

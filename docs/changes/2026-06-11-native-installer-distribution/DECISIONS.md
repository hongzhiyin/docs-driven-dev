# DECISIONS - Native Installer Distribution

> Archived English summary for a historical docdev change packet.

## Maintenance Rules

1. Keep decision records concise and tied to real trade-offs.
2. Preserve current product truth in root `docs/DECISIONS.md`.
3. Use git history for detailed pre-compaction wording.

---

## D-001 - Archive packet in English-only form

**Date**: 2026-06-25

**Context**:
The `native-installer-distribution` packet was created on 2026-06-11 as part of earlier docdev maintenance.
The repository now has a compatibility requirement that tracked docdev text use
English only. Keeping the packet directory is useful for traceability, but the
old detailed prose is no longer suitable as live tracked text.

**Options**:
- A. Keep the original detailed packet unchanged - maximizes inline history, but
  violates the repository-wide English-only contract.
- B. Delete the packet - removes incompatible text, but loses discoverability of
  the historical change topic.
- C. Replace the packet with a concise English archive summary - keeps the
  historical topic visible while satisfying the current compatibility rule.

**Chosen**: C

**Rationale**:
- The archive summary keeps the date, slug, and source-of-truth relationship.
- Root docs and tests define current behavior; old packet details do not need to
  stay in runtime context.
- Git history remains the right place for exact pre-compaction wording.

**Risks**:
- Maintainers lose quick inline access to detailed old verification logs.
  Mitigation: use git history when that level of evidence is needed.

**Related code / docs**:
- `docs/changes/2026-06-11-native-installer-distribution/`
- `docs/DECISIONS.md` D-048
- `docs/ROADMAP.md` Step 6ab

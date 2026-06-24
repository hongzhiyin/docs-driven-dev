# SPEC - Docs Maintenance Health

> Archived English summary for a historical docdev change packet.

## 0. Status

| Field | Value |
|---|---|
| Status | Archived |
| Source | Historical packet normalized for repository-wide English compatibility |
| Packet | `docs/changes/2026-06-24-docs-maintenance-health/` |
| Last updated | 2026-06-25 |
| Original packet date | 2026-06-24 |

## 1. One-Sentence Goal

Preserve the durable intent of the `docs-maintenance-health` change packet in concise English so
tracked docdev text remains portable across environments.

## 2. Scope

### 2.1 In Scope

- Keep the packet directory and four-file shape discoverable.
- Retain the historical change topic, date, and decision trail at summary level.
- Remove visible non-English prose from tracked repository files.

### 2.2 Out of Scope

- Reconstruct every implementation log line from the original packet.
- Change current runtime behavior, release assets, or installed skill targets.
- Add detailed migration material to `skill/SKILL.md`.

## 3. Requirements

| ID | Requirement | Acceptance method | Status |
|---|---|---|---|
| R1 | Historical packet remains present under `docs/changes/` | file review | Done |
| R2 | Packet text uses English only | repository scan | Done |
| R3 | Current product behavior is governed by root docs | audit | Done |

## 4. Constraints And Invariants

1. **#1**: Root `docs/SPEC.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, and `docs/DECISIONS.md` remain the current source of truth.
2. **#2**: Historical packets may be compacted for compatibility, but current behavior must be represented in root docs.
3. **#3**: Active skill guidance stays concise and should not absorb archived maintenance detail.

## 5. Acceptance Criteria

1. This packet contains no Chinese characters.
2. Project audit still passes after archive compaction.
3. Root docs retain the current contract for any behavior this packet introduced.

## 6. Open Questions

| ID | Question | Current read | Blocks implementation |
|---|---|---|---|
| Q1 | Where can maintainers inspect the original detailed wording? | Git history before the 2026-06-25 English-only repository cleanup | no |

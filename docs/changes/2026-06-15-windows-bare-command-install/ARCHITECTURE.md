# ARCHITECTURE - Windows Bare Command Install

> Archived English summary for a historical docdev change packet.

## 1. Scope

This file preserves the architectural role of the `windows-bare-command-install` packet after the
repository-wide English cleanup. Current module boundaries, CLI behavior, skill
contracts, and release behavior are documented in root `docs/ARCHITECTURE.md`.

## 2. Historical Shape

| Area | Archived Role |
|---|---|
| Packet directory | Historical work context under `docs/changes/2026-06-15-windows-bare-command-install/` |
| Root docs | Current source of truth for durable behavior |
| Tests and CLI | Current verification surface |
| Git history | Exact pre-compaction wording and detailed old logs |

## 3. Dependency Direction

```text
root source-of-truth docs
  -> current CLI / skill / scripts / tests
  -> archived change packet summaries
  -> git history for detailed old wording
```

## 4. Compatibility Notes

- The archive summary introduces no runtime dependency.
- The active skill remains concise and does not include archived maintenance detail.
- Repository text stays English-only for predictable rendering across environments.

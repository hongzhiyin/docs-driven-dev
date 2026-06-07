# docs-driven-dev

Portable skill and CLI for docs-driven development.

The skill gives agents the workflow: keep SPEC, ARCHITECTURE, ROADMAP, and
DECISIONS aligned before and after code changes. The CLI handles deterministic
work such as scaffolding templates, auditing document structure, appending the
next D-XXX skeleton, and syncing the skill to agent homes.

## Quick Start

```bash
./scripts/install_cli.sh
./.venv/bin/docdev doctor
./.venv/bin/docdev init /path/to/project
./.venv/bin/docdev audit /path/to/project --write-report
```

Sync the skill after edits:

```bash
./scripts/sync_skill.sh --targets codex,cursor,agents,claude --force
```

## Documentation Map

This project's source of truth lives in `docs/`. Any code change must be
consistent with these documents; conflicts get resolved by editing the docs
first, then code.

| File | Contents |
|---|---|
| [docs/SPEC.md](docs/SPEC.md) | Rules, invariants, command list, default behaviour |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Layers, module table, data flow, config |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Step list, acceptance, current progress |
| [docs/DECISIONS.md](docs/DECISIONS.md) | D-XXX trade-off log |

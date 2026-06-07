# ARCHITECTURE - docs-driven-dev

> Source of truth for current structure.

## 1. Layer View

```text
User / Agent
  -> docs-driven-dev skill
      -> docdev CLI for deterministic operations
          -> project docs, generated reports, skill target dirs
  -> project source docs
      -> SPEC / ARCHITECTURE / ROADMAP / DECISIONS
```

The skill explains when and why to use the method. The CLI performs repeatable
filesystem operations. Scripts provide local wrappers for install, sync, and
checks.

## 2. Module Table

| Module | Path | Responsibility | Does not depend on |
|---|---|---|---|
| CLI package | `src/docs_driven_dev/` | Argument parsing, scaffolding, audit, status, decision skeletons, skill sync | external packages |
| Skill source | `skill/SKILL.md` | Agent workflow and boundaries | local install paths |
| Installed skill wrapper | `<skill-target>/bin/docdev` | Cross-project CLI entrypoint generated during sync | package index |
| Templates | `skill/templates/` | Four source-doc skeletons copied by `docdev init` | target project state |
| References | `skill/references/` | Optional examples loaded only when needed | CLI execution |
| Scripts | `scripts/` | Source-checkout wrappers for install, sync, and checks | package index |
| Project docs | `docs/` | Source of truth for this project | generated audit output |

## 3. Data Flow

### 3.1 Bootstrap

```text
docdev init <project>
  -> resolve docs_dir from arg or .docdev.toml
  -> locate skill/templates
  -> copy SPEC / ARCHITECTURE / ROADMAP / DECISIONS
  -> create README and AGENTS pointers
  -> create docs/_generated/docdev
```

### 3.2 Audit

```text
docdev audit <project>
  -> read docs_dir
  -> check four files and active README/AGENTS pointers
  -> parse D-XXX ids, decision entry blocks, roadmap Step acceptance,
     SPEC invariants, and SPEC Decision Table choices
  -> print findings
  -> optionally write docs/_generated/docdev/audit.json
```

### 3.3 Sync

```text
docdev sync-skill
  -> resolve source skill directory
  -> copy to Codex / Cursor / shared agents targets
  -> write each copied target's bin/docdev wrapper back to the source checkout
  -> link Claude target to shared agents target
  -> require --force for unmarked existing target dirs
```

## 4. Data Model

### 4.1 Finding

```python
@dataclass
class Finding:
    level: str
    message: str
    path: str | None = None
```

Used by audit output and optional JSON reports.

### 4.2 Config

`.docdev.toml` currently supports only:

```toml
docs_dir = "docs"
```

The parser is intentionally tiny and stdlib-only.

## 5. Configuration

| Field / Env | Default | Meaning | Required |
|---|---|---|---|
| `.docdev.toml` `docs_dir` | `docs` | Project source-doc folder | no |
| `DOCDEV_PROJECT_DIR` | auto-detected | Source checkout for CLI fallback and templates | no |
| `DOCDEV_TEMPLATE_DIR` | source skill templates | Explicit template directory | no |
| `CODEX_HOME` | `~/.codex` | Codex skill home | no |

## 6. Process Model

- Entry: `docdev` console script, source `.venv/bin/docdev` wrapper, or
  installed skill-local `bin/docdev` wrapper.
- Shutdown: command exits after a single operation.
- Background work: none.
- Network: none.

## 7. Known Constraints

- Audit checks are structural, not semantic; rationale completeness is checked
  by required block presence and content, not by judging the quality of the
  prose.
- Sync currently copies skill folders for Codex/Cursor/shared agents and uses a
  Claude symlink; platform-specific metadata may need future adapters.
- Template lookup assumes a source checkout or synced skill directory is
  available.

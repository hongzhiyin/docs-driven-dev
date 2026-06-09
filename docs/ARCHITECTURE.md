# ARCHITECTURE - docs-driven-dev

> Source of truth for current structure.

## 1. Layer View

```text
User / Agent
  -> docs-driven-dev skill
      -> docdev CLI for deterministic operations
          -> project docs, change packets, generated reports, skill target dirs
  -> project source docs
      -> SPEC / ARCHITECTURE / ROADMAP / DECISIONS
      -> changes/YYYY-MM-DD-slug/ requirement work packets
```

The skill explains when and why to use the method. The CLI performs repeatable
filesystem operations. Scripts provide local wrappers for project bootstrap,
install, sync, checks, and source updates.

The source checkout is the implementation home, not the operational working
directory. `docdev` commands run against whichever target project path the
caller passes.

## 2. Module Table

| Module | Path | Responsibility | Does not depend on |
|---|---|---|---|
| CLI package | `src/docs_driven_dev/` | Argument parsing, scaffolding, audit, status, decision skeletons, skill sync | external packages |
| Skill source | `skill/SKILL.md` | Agent workflow and boundaries | local install paths |
| Installed skill wrappers | `<skill-target>/bin/docdev`, `bin/docdev.ps1`, `bin/docdev.cmd` | Cross-project CLI entrypoints generated during sync | package index |
| Templates | `skill/templates/` | Four source-doc skeletons copied by `docdev init` | target project state |
| Change templates | `skill/templates/change/` | Requirement packet skeletons copied by `docdev new-change` | target project state |
| References | `skill/references/` | Optional examples loaded only when needed | CLI execution |
| Scripts | `scripts/` | Source-checkout wrappers for target bootstrap, install, sync, checks, and update lifecycle on Unix shells and Windows PowerShell | package index |
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

### 3.2 Source Quick Start

```text
scripts/setup_project.sh <project> [docdev init options]
  -> scripts/install_cli.sh
  -> .venv/bin/docdev doctor
  -> .venv/bin/docdev init <project> [options]
  -> .venv/bin/docdev audit <project> --write-report
```

### 3.3 Requirement Change Packet

```text
docdev new-change <slug> <project>
  -> resolve docs_dir from arg or .docdev.toml
  -> create docs/changes/<date>-<slug>/
  -> copy change templates for SPEC / ROADMAP / DECISIONS
  -> optionally copy ARCHITECTURE
  -> leave generated reports under docs/_generated/docdev
```

Change packets are scoped working memory for existing-project requirements.
They do not replace root project docs. `ARCHITECTURE.md` is optional inside a
change packet when ROADMAP records the omission reason.

### 3.4 Audit

```text
docdev audit <project>
  -> read docs_dir
  -> check four files and active README/AGENTS pointers
  -> parse D-XXX ids, decision entry blocks, roadmap Step acceptance,
     SPEC invariants, and SPEC Decision Table choices
  -> discover docs/changes/* packets
  -> check required packet docs, optional architecture reason, gates,
     research log, and verification records
  -> print findings
  -> optionally write docs/_generated/docdev/audit.json
```

### 3.5 Sync

```text
docdev sync-skill
  -> resolve source skill directory
  -> resolve target paths from DOCDEV_<TARGET>_SKILL_DIR / DOCDEV_<TARGET>_HOME / defaults
  -> print resolved sync target paths
  -> copy to Codex / Cursor / shared agents targets
  -> write each copied target's bin/docdev wrapper back to the source checkout
  -> link Claude target to shared agents target when possible
  -> copy Claude target as fallback when symlink creation is unavailable
  -> require --force for unmarked existing target dirs
```

### 3.6 Update Lifecycle

```text
scripts/install.sh
  -> print [docdev install] entrypoint logs
  -> scripts/update_cli.sh --targets codex,cursor,agents,claude --force

scripts/install.ps1
  -> print [docdev install] entrypoint logs
  -> scripts/update_cli.ps1 -Targets codex,cursor,agents,claude -Force

scripts/update_cli.sh
  -> print [docdev update] numbered lifecycle logs
  -> scripts/install_cli.sh
  -> python3 -m unittest discover -s tests
  -> scripts/check_install.sh
  -> scripts/sync_skill.sh <caller args>
  -> scripts/check_install.sh

scripts/update_cli.ps1
  -> print [docdev update] numbered lifecycle logs
  -> scripts/install_cli.ps1
  -> python -m unittest discover -s tests
  -> python -m docs_driven_dev.cli doctor
  -> python -m docs_driven_dev.cli sync-skill <caller args>
  -> python -m docs_driven_dev.cli doctor
  -> python -m docs_driven_dev.cli audit <source checkout>
  -> python -m docs_driven_dev.cli status <source checkout>
```

`scripts/install.sh` is the fresh-machine install path after cloning the source
repo on Unix shells. `scripts/install.ps1` is the equivalent Windows
PowerShell install path. Both call an update lifecycle with default targets so
agents can discover the skill and call their skill-local wrappers from
unrelated target projects. Logs are intentionally written to stdout with stable
`[docdev install]` and `[docdev update]` prefixes so a user can report the last
visible step when a remote machine fails.

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

### 4.3 Change Packet

```text
docs/changes/YYYY-MM-DD-slug/
  SPEC.md
  ROADMAP.md
  DECISIONS.md
  ARCHITECTURE.md  # optional
```

The date and slug are filesystem identity. Packet-local D-XXX numbering is
separate from project-level D-XXX numbering.

## 5. Configuration

| Field / Env | Default | Meaning | Required |
|---|---|---|---|
| `.docdev.toml` `docs_dir` | `docs` | Project source-doc folder | no |
| `DOCDEV_PROJECT_DIR` | auto-detected | Source checkout for CLI fallback and templates | no |
| `DOCDEV_TEMPLATE_DIR` | source skill templates | Explicit template directory | no |
| `DOCDEV_<TARGET>_SKILL_DIR` | unset | Exact installed skill directory for `CODEX`, `CURSOR`, `AGENTS`, or `CLAUDE` | no |
| `DOCDEV_<TARGET>_HOME` | unset | Agent home containing `skills/docs-driven-dev` for `CODEX`, `CURSOR`, `AGENTS`, or `CLAUDE` | no |
| `CODEX_HOME` | `~/.codex` | Legacy Codex skill home fallback when `DOCDEV_CODEX_HOME` is unset | no |

## 6. Process Model

- Entry: `docdev` console script, source `.venv/bin/docdev` wrapper, or
  installed skill-local `bin/docdev`, `bin/docdev.ps1`, or `bin/docdev.cmd`
  wrapper.
- Target selection: explicit project path argument; current working directory
  is only a default when the caller intentionally runs from the target project.
- Sync target selection: exact `DOCDEV_<TARGET>_SKILL_DIR` overrides home
  overrides, and home overrides compose with `skills/docs-driven-dev`.
- Target project setup: `scripts/setup_project.sh /path/to/project`.
- Requirement setup: `docdev new-change "<slug>" /path/to/project`.
- Source update: `scripts/update_cli.sh --targets codex,cursor,agents,claude
  --force`, or `.\scripts\update_cli.ps1 -Targets codex,cursor,agents,claude
  -Force` on Windows PowerShell.
- Diagnostics: report the last `[docdev update] step N/M ...` line when an
  install or update stops on another machine.
- Shutdown: command exits after a single operation.
- Background work: none.
- Network: none.

## 7. Known Constraints

- Audit checks are structural, not semantic; rationale completeness is checked
  by required block presence and content, not by judging the quality of the
  prose.
- Change-packet gate checks infer state from ROADMAP phase text and checkbox
  structure; they are workflow guardrails, not semantic proof that a plan is
  good.
- Sync currently copies skill folders for Codex/Cursor/shared agents. Claude
  uses a symlink when possible and falls back to a copied skill directory when
  the platform refuses symlink creation; platform-specific metadata may need
  future adapters.
- Template lookup assumes a source checkout or synced skill directory is
  available.
- Windows PowerShell scripts use `python`; if a Windows machine only exposes
  Python as `py`, the wrapper may need a future fallback after real-machine
  testing.

# ARCHITECTURE - docs-driven-dev

> Source of truth for current structure.

## 1. Layer View

```text
User / Agent
  -> docs-driven-dev skill
      -> docdev CLI for deterministic operations
          -> project docs, change packets, generated reports, skill target dirs
          -> native release update when installed from a release
  -> GitHub Release installer
      -> user install root / launcher / versioned releases
  -> project source docs
      -> SPEC / ARCHITECTURE / ROADMAP / DECISIONS
      -> changes/YYYY-MM-DD-slug/ requirement work packets
```

The skill explains when and why to use the method. The CLI performs repeatable
filesystem operations. Scripts provide release packaging, remote installation,
local source-checkout wrappers for project bootstrap, install, sync, checks,
and maintainer updates.

The source checkout is the implementation home, not the operational working
directory. `docdev` commands run against whichever target project path the
caller passes.

## 2. Module Table

| Module | Path | Responsibility | Does not depend on |
|---|---|---|---|
| CLI entrypoint | `src/docs_driven_dev/cli.py` | Stable `python -m docs_driven_dev.cli` entrypoint plus compatibility re-exports | feature implementation details |
| CLI command dispatch | `src/docs_driven_dev/commands.py` | Argument parsing and subcommand dispatch | filesystem business logic |
| CLI path/config helpers | `src/docs_driven_dev/paths.py` | Constants, source root detection, docs/config/template path resolution | argparse and command side effects |
| CLI shared models | `src/docs_driven_dev/models.py` | Shared data objects such as `Finding` | command dispatch |
| CLI template/change module | `src/docs_driven_dev/templates.py` | `init`, `new-change`, template copy, README/AGENTS pointers | audit, sync, release update |
| CLI audit/status module | `src/docs_driven_dev/audit.py` | Project and change-packet audit, status, decision skeletons | skill target writes, native update |
| CLI docs-health module | `src/docs_driven_dev/docs_health.py` | Documentation size metrics, change-packet metrics, and maintenance review signals | release install/update and human-authored rewrites |
| CLI sync/doctor module | `src/docs_driven_dev/sync.py` | Skill target resolution, copy sync, doctor output | release download/update dispatch |
| CLI release module | `src/docs_driven_dev/release.py` | Native update dispatch and native uninstall planning/execution | audit/template internals |
| Skill source | `skill/SKILL.md` | Agent workflow and boundaries | local install paths |
| Installed skill targets | `<skill-target>/` | Synced skill content plus `.docdev-skill-source` marker; no CLI wrappers | package index |
| Native launcher | `~/.local/bin/docdev` on Unix; `%USERPROFILE%\.local\bin\docdev.ps1` and `docdev.cmd` on Windows | User-facing release launcher pointing at the active native release | source checkout |
| Release install root | `~/.local/share/docdev/releases/<version>` and `current` | Versioned release installs and active version pointer | unverified artifacts |
| Templates | `skill/templates/` | Four source-doc skeletons copied by `docdev init` | target project state |
| Change templates | `skill/templates/change/` | Requirement packet skeletons copied by `docdev new-change` | target project state |
| References | `skill/references/` | Optional examples loaded only when needed | CLI execution |
| Scripts | `scripts/` | Release packaging, remote installers, source-checkout wrappers for target bootstrap, install, sync, checks, and update lifecycle on Unix shells and Windows PowerShell | package index |
| Project docs | `docs/` | Source of truth for this project | generated audit output |

## 3. Data Flow

### 3.0 CLI Dispatch

```text
docdev / python -m docs_driven_dev.cli
  -> cli.py
      -> commands.main()
          -> templates / audit / sync / release command handlers
          -> paths.py and models.py shared helpers
```

`cli.py` remains the executable module used by launchers and wrappers. It is
also a compatibility re-export layer for existing tests and local imports;
new feature logic should be added to the focused internal module that owns the
behavior.

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
  -> sh .venv/bin/docdev doctor
  -> sh .venv/bin/docdev init <project> [options]
  -> sh .venv/bin/docdev audit <project> --write-report
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

Tracked docdev text, shipped templates, and CLI-generated skeletons are
English-only. Audit parsing may retain compatibility with older archived
packets without exposing non-English text in generated output or source docs.

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

### 3.4a Docs Health

```text
docdev docs-health <project> [--json] [--write-report]
  -> resolve docs_dir
  -> count README and four source-doc lines
  -> count ROADMAP step sections and Step Status states
  -> count D-XXX entries
  -> count change packets and largest packet sizes
  -> emit review signals without mutating human-authored docs
  -> optionally write docs/_generated/docdev/docs-health.json
```

Docs-health is deliberately separate from `audit`: audit checks structural
correctness; docs-health reports maintenance pressure and leaves trimming
judgment to the agent or maintainer.

### 3.5 Sync

```text
docdev sync-skill
  -> resolve source skill directory
  -> resolve target paths from DOCDEV_<TARGET>_SKILL_DIR / DOCDEV_<TARGET>_HOME / defaults
  -> print resolved sync target paths
  -> replace marked or forced Codex / Cursor / shared agents / Claude target directories
  -> require --force for unmarked existing target dirs
```

Replacement is not an incremental merge. `copy_skill` removes the current
target directory when it is force-synced or already marked with
`.docdev-skill-source`; legacy symlinks are removed only through force sync.
It then copies the current source skill and writes the marker. This avoids
stale files inside the active target path, including pre-D-025 `bin/docdev*`
wrappers and pre-D-033 Claude symlinks.

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

`scripts/install.sh` is the developer install path after cloning the source
repo on Unix shells. `scripts/install.ps1` is the equivalent Windows
PowerShell maintenance path. Both call an update lifecycle with default targets
so source-synced skill copies stay aligned with the checkout. They do not
modify the user's global shell `PATH`; direct
terminal use from the source checkout goes through the source `.venv` wrappers
unless the user adds another PATH entry manually. Normal cross-machine agent
resolution uses the native `docdev` launcher instead of skill-local wrappers. Logs are
intentionally written to stdout with stable
`[docdev install]` and `[docdev update]` prefixes so a user can report the last
visible step when a remote machine fails.

### 3.7 Release Packaging

```text
scripts/package_release.sh [--version <version>] [--out <dir>]
  -> verify pyproject.toml and package __version__ match the release version
  -> stage source files required to run docdev
  -> exclude .git, .venv, docs/_generated/docdev/*, caches, and build outputs
  -> write docdev-<version>.tar.gz
  -> write docdev-<version>.tar.gz.sha256
  -> write manifest.json
  -> copy install_remote.sh and install_remote.ps1 as top-level release assets
```

Release output is a build artifact, not project doctrine. It stays outside the
four source documents and out of `docs/_generated/docdev/`.

### 3.8 Native Remote Install

```text
scripts/install_remote.sh
  -> resolve release base URL and version/latest channel
  -> download manifest and artifact
  -> verify artifact SHA256 against the manifest
  -> unpack into ~/.local/share/docdev/releases/<version>
  -> switch ~/.local/share/docdev/current
  -> write ~/.local/bin/docdev launcher
  -> run docdev doctor through sh "$LAUNCHER"

~/.local/bin/docdev
  -> /bin/sh launcher
  -> DOCDEV_PROJECT_DIR=~/.local/share/docdev/current
  -> PYTHONPATH=~/.local/share/docdev/current/src
  -> python3 -m docs_driven_dev.cli "$@"

scripts/install_remote.ps1
  -> resolve release base URL and version/latest channel
  -> download manifest and artifact
  -> verify artifact SHA256 against the manifest
  -> unpack into $HOME\.local\share\docdev\releases\<version>
  -> switch $HOME\.local\share\docdev\current junction
  -> write $HOME\.local\bin\docdev.ps1 PowerShell launcher
  -> write $HOME\.local\bin\docdev.cmd command launcher
  -> add bin dir to User PATH unless -NoModifyPath
  -> run docdev doctor through the generated PowerShell launcher

$HOME\.local\bin\docdev.cmd
  -> chcp 65001 for the current command process
  -> set PYTHONUTF8 and PYTHONIOENCODING for the child Python process
  -> DOCDEV_PROJECT_DIR=$HOME\.local\share\docdev\current
  -> PYTHONPATH=$HOME\.local\share\docdev\current\src
  -> python -m docs_driven_dev.cli %*

$HOME\.local\bin\docdev.ps1
  -> best-effort set PowerShell console encoding / $OutputEncoding to UTF-8
  -> set PYTHONUTF8 and PYTHONIOENCODING for the child Python process
  -> set DOCDEV_PROJECT_DIR and PYTHONPATH to the active release
  -> python -m docs_driven_dev.cli @args
```

The Unix installer does not edit shell profiles. If `~/.local/bin` is not on
PATH, it prints a warning and the direct launcher path. The Windows installer
adds its bin dir to User PATH by default, avoids duplicate PATH entries,
refreshes current `$env:Path` when the script runs in the current PowerShell
process, and supports `-NoModifyPath` for managed environments. A persistent
User PATH update may still require opening a new terminal before `docdev` is
visible to the parent shell.

### 3.9 Native Update

```text
docdev update [--version <version>] [--release-base-url <url>] [--no-sync-skill]
  -> dispatch to scripts/install_remote.sh on Unix-like hosts
  -> dispatch to powershell.exe -File scripts/install_remote.ps1 on Windows
  -> use the same manifest/artifact/checksum/install logic as remote install
  -> switch current only after verification succeeds
  -> run doctor through the generated launcher
  -> run sync-skill by default after activation
  -> skip sync-skill only when --no-sync-skill is requested
```

Source checkout maintenance continues to use `scripts/update_cli.*`; that path
runs tests and sync checks for maintainers and is intentionally separate from a
normal user's release update.

### 3.10 Native Uninstall

```text
docdev uninstall [--dry-run | --yes] [--keep-skills]
  -> resolve install root from --install-root / DOCDEV_INSTALL_ROOT / ~/.local/share/docdev
  -> resolve launcher from --bin-dir / DOCDEV_BIN_DIR / ~/.local/bin/docdev
  -> resolve skill targets with DOCDEV_<TARGET>_SKILL_DIR / DOCDEV_<TARGET>_HOME / defaults
  -> plan delete / skip actions
  -> require --yes before destructive removal
  -> delete install root
  -> delete launcher only when it looks like the generated docdev launcher
  -> delete legacy skill symlinks and marked skill directories
  -> skip unmarked skill directories
```

Uninstall does not remove parent directories such as `~/.local/bin`,
`~/.local/share`, `~/.codex`, `~/.cursor`, `~/.agents`, or `~/.claude`.
Legacy Claude symlink cleanup unlinks the symlink itself; it does not
recursively delete the symlink target.

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

### 4.4 Docs Health Report

```json
{
  "schema_version": 1,
  "files": [],
  "totals": {},
  "roadmap": {},
  "decisions": {},
  "change_packets": {},
  "signals": []
}
```

Signals are review prompts, not audit failures. They should remain stable
enough for agents to consume without implying automatic document mutation.

## 5. Configuration

| Field / Env | Default | Meaning | Required |
|---|---|---|---|
| `.docdev.toml` `docs_dir` | `docs` | Project source-doc folder | no |
| `DOCDEV_PROJECT_DIR` | auto-detected | Release/source root set by launchers and source checkout wrappers for template discovery | no |
| `DOCDEV_TEMPLATE_DIR` | source skill templates | Explicit template directory | no |
| `DOCDEV_INSTALL_ROOT` | `~/.local/share/docdev` | Native release install root; useful for tests and custom user layouts | no |
| `DOCDEV_BIN_DIR` | `~/.local/bin` | Native launcher directory; Windows installer adds this directory to User PATH unless `-NoModifyPath` is used | no |
| `DOCDEV_RELEASE_BASE_URL` | GitHub Release asset base | Manifest/artifact download source for remote install/update | no |
| `GITHUB_TOKEN` | unset | Optional private GitHub Release access token; not persisted | no |
| `DOCDEV_<TARGET>_SKILL_DIR` | unset | Exact installed skill directory for `CODEX`, `CURSOR`, `AGENTS`, or `CLAUDE` | no |
| `DOCDEV_<TARGET>_HOME` | unset | Agent home containing `skills/docs-driven-dev` for `CODEX`, `CURSOR`, `AGENTS`, or `CLAUDE` | no |
| `CODEX_HOME` | `~/.codex` | Legacy Codex skill home fallback when `DOCDEV_CODEX_HOME` is unset | no |

## 6. Process Model

- Entry: normal cross-machine use enters through `docdev` on `PATH` or the
  native release `~/.local/bin/docdev` launcher. Source `.venv/bin/docdev`
  remains a developer-maintenance entry for unreleased checkout code.
- Version: `docdev -v` and `docdev --version` print the CLI version.
- Target selection: explicit project path argument; current working directory
  is only a default when the caller intentionally runs from the target project.
- Sync target selection: exact `DOCDEV_<TARGET>_SKILL_DIR` overrides home
  overrides, and home overrides compose with `skills/docs-driven-dev`.
- Target project setup: `scripts/setup_project.sh /path/to/project`.
- Requirement setup: `docdev new-change "<slug>" /path/to/project`.
- Docs maintenance: `docdev docs-health /path/to/project --write-report`
  creates a generated report for agent review before trimming source docs.
- Native install: remote installer downloads a release manifest/artifact,
  verifies checksum, installs under `DOCDEV_INSTALL_ROOT` or
  `~/.local/share/docdev`, and writes a launcher under `DOCDEV_BIN_DIR` or
  `~/.local/bin`. Windows writes both `docdev.ps1` and `docdev.cmd`, and
  defaults to adding the bin dir to User PATH.
- Native update: `docdev update` updates release installs, runs doctor, and
  syncs skill targets by default; `--no-sync-skill` skips that write. The
  update command uses the platform-native remote installer.
- Native uninstall: `docdev uninstall --dry-run` previews removal, and
  `docdev uninstall --yes` removes docdev-owned native install paths and marked
  skill targets.
- Source update: `scripts/update_cli.sh --targets codex,cursor,agents,claude
  --force`, or `.\scripts\update_cli.ps1 -Targets codex,cursor,agents,claude
  -Force` on Windows PowerShell.
- Diagnostics: report the last `[docdev update] step N/M ...` line when an
  install or update stops on another machine.
- Shutdown: command exits after a single operation.
- Background work: none.
- Network: native remote install/update fetch GitHub Release assets; normal
  docs scaffolding, audit, source checkout maintenance, and local smoke tests
  do not require network.

## 7. Known Constraints

- Audit checks are structural, not semantic; rationale completeness is checked
  by required block presence and content, not by judging the quality of the
  prose.
- Change-packet gate checks infer state from ROADMAP phase text and checkbox
  structure; they are workflow guardrails, not semantic proof that a plan is
  good.
- Sync copies skill folders for Codex/Cursor/shared agents/Claude. Legacy
  Claude symlinks are only a cleanup compatibility case; new sync runs do not
  create them. Platform-specific metadata may need future adapters.
- Template lookup assumes a native release root, source checkout, synced skill
  directory, or explicit `DOCDEV_TEMPLATE_DIR` is available.
- Windows PowerShell scripts and generated `docdev.cmd` use `python`; if a
  Windows machine only exposes Python as `py`, the wrapper may need a future
  fallback after real-machine testing.
- Native installer checksum verification provides file integrity, not a full
  publisher signing trust chain. Signed manifests are a future enhancement.
- Docs-health thresholds are intentionally heuristic and should not replace
  human judgment about what to keep, summarize, or archive.

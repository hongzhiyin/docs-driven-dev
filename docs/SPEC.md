# SPEC - docs-driven-dev

> Source of truth for expected behaviour.

## 1. One-Sentence Goal

Provide a portable skill plus deterministic CLI that helps agents bootstrap,
audit, and maintain four-file docs-driven development across Codex, Cursor,
Claude, and shared agent skill homes.

## 2. Decision Table

| ID | Decision | Choice | Notes |
|---|---|---|---|
| A | Boundary | Skill owns workflow judgment; CLI owns deterministic filesystem, numbering, audit, and sync | See D-001 |
| B | Default docs location | `docs/` with `.docdev.toml` `docs_dir` override | See D-002 |
| C | Generated output | `<docs_dir>/_generated/docdev/` only | See D-002 |
| D | Runtime | Python 3.10+ stdlib-only CLI | See D-001 |
| E | Install style | Release installer installs versioned user-directory releases; source checkout wrappers remain the developer maintenance path | See D-021 |
| F | Skill sync targets | `~/.codex`, `~/.cursor`, `~/.agents`, and Claude symlink to shared agents skill | See D-003 |
| G | Audit strictness | Structural drift is reported as warnings unless a required source document or invariant is broken | See D-005 |
| H | Cross-project CLI discovery | Agents use `docdev` on PATH or the native launcher; source checkout wrappers are developer-only fallbacks | See D-006, D-021, D-022 |
| I | Update lifecycle | Source updates should use a project-local install, test, check, sync, check sequence | See D-007 |
| J | Quick start | A source-checkout setup script combines install, doctor, init, and audit report for a target project | See D-008 |
| K | Target project model | `docdev` commands operate on explicit target project paths; source checkout scripts are maintenance conveniences | See D-009 |
| L | Source checkout developer onboarding | `scripts/install.sh` installs, verifies, syncs, and enables maintenance from a cloned source checkout | See D-010, D-021, D-024 |
| M | Requirement granularity | Project-level four docs stay required; per-requirement change packets are optional under `docs/changes/` | See D-012 |
| N | Windows onboarding | PowerShell install scripts mirror the Unix install lifecycle | See D-013 |
| O | Windows sync resilience | Claude uses a shared-agents symlink when possible, with a copy fallback when the platform refuses symlinks | See D-015 |
| P | Install diagnostics | Install and update scripts emit prefixed, numbered lifecycle logs so failures can be localized from user output | See D-016 |
| Q | Skill target overrides | Each sync target supports environment-variable overrides for non-default Windows or agent skill directories | See D-017 |
| R | Existing code adoption | Existing code projects without four docs should be lightly initialized before opening a requirement change packet | See D-018 |
| S | Source maintenance PATH contract | Source install prepares a source-local wrapper but does not mutate the user's global shell `PATH` or skill target CLI entries | See D-019, D-024, D-025 |
| T | Sync replacement contract | Force sync and marked-target refreshes replace the target skill directory instead of merging files | See D-019 |
| U | Explicit invocation | When the skill is explicitly named, agents must follow one workflow and create/update required docs before code | See D-020 |
| V | Small-fix path | Narrow bug fixes use a minimal B0 packet rather than skipping docs or forcing a heavy packet | See D-020 |
| W | Release packaging | `scripts/package_release.sh` emits `docdev-<version>.tar.gz`, a SHA256 file, `manifest.json`, and installer script assets for GitHub Releases | See D-021 |
| X | Native update | `docdev update` updates release installs through manifest/artifact download, checksum verification, current-pointer switch, and doctor | See D-021 |
| Y | Private repository installs | Public GitHub Releases are the default; private releases require explicit `gh auth` or token handling | See D-021 |
| Z | CLI internal boundary | `docs_driven_dev.cli` remains the public entrypoint; deterministic logic is split into lightweight internal modules by responsibility | See D-026 |

## 3. Derived Rules

### 3.1 Four Source Documents

| File | Responsibility |
|---|---|
| `SPEC.md` | Expected behaviour, invariants, contracts, defaults |
| `ARCHITECTURE.md` | Actual structure, modules, data flow, configuration |
| `ROADMAP.md` | Current Phase/Step state, tasks, acceptance |
| `DECISIONS.md` | D-XXX rationale, options, choice, risks |

No other file can silently replace these four as the source of truth.

### 3.2 Requirement Change Packets

Project-level docs describe the durable project contract. Requirement-level
work belongs in a change packet when a user asks to add, refactor, or research a
specific feature in an existing project.

An existing code project that has no project-level four docs is not blocked.
Adopt it first with `docdev init <project>`, keeping root docs intentionally
minimal and marking unknowns as pending, then create the scoped packet with
`docdev new-change "<slug>" <project>`. A `docs/changes/...` packet should not
stand alone as the only docs-driven artifact in a project.

Default change packet layout:

```text
<docs_dir>/changes/YYYY-MM-DD-<slug>/
  SPEC.md
  ROADMAP.md
  DECISIONS.md
  ARCHITECTURE.md  # optional; ROADMAP must record the reason when omitted
```

Required change packet files are `SPEC.md`, `ROADMAP.md`, and `DECISIONS.md`.
`ARCHITECTURE.md` is required only when the requirement changes module
boundaries, data flow, lifecycle, state, persistence, public APIs, events,
configuration contracts, migration behavior, or other cross-cutting structure.

Change packets default to Simplified Chinese templates because they are
usually created from interactive requirement work. Code identifiers, file
paths, commands, config keys, class/function names, branch names, and error
messages retain their original spelling.

### 3.2.1 Explicit Skill Invocation

When a user explicitly names `docs-driven-dev` or references the installed
skill, an agent must follow one of the skill workflows. Reading the skill and
then doing ad-hoc research or direct code edits is not sufficient.

For any code change under explicit skill invocation, the agent must create or
update the required docs artifacts before editing code unless the user
explicitly forbids doc file changes. If doc changes are forbidden, the agent
must state that the full docs-driven workflow is blocked and ask whether to
proceed outside this skill.

Small fixes do not skip docs. They use a minimal `Workflow B0` packet:
- initialize a minimal root four-pack first when project-level docs are missing;
- create a scoped change packet;
- keep SPEC to one expected behavior rule or invariant;
- keep ROADMAP to goal, touched files, acceptance checks, and verification;
- update DECISIONS only when a real trade-off exists;
- omit packet ARCHITECTURE unless structure changes.

After the packet states scope and acceptance, explicit user language such as
"fix it", "补上吧", or "implement it" counts as implementation approval for the
narrow fix.

### 3.3 CLI Commands

`docdev` is a reusable project tool, not a single-repository command. Agents
should pass the intended target project path explicitly unless the user's
current working directory is itself the target project.

Agents resolve the CLI without relying on local source paths or compatibility
wrappers. The normal order is: `docdev` on `PATH`, then the native Unix
launcher `~/.local/bin/docdev` when present. If neither exists, agents should
ask the user to run the native installer or repair the install. They should not
guess local paths or wrappers. `DOCDEV_PROJECT_DIR` + `PYTHONPATH` is reserved
for explicit source checkout development, not cross-machine agent use.

| Command | Purpose | Side effects |
|---|---|---|
| `docdev init <project>` | Create templates, README pointer, AGENTS pointer, generated dir | Writes project docs |
| `docdev new-change "<slug>" <project>` | Create a per-requirement change packet | Writes project docs |
| `docdev audit <project>` | Check project docs plus existing change packets for structure, numbering, source-map drift, and required rationale blocks | Optional audit report |
| `docdev status <project>` | Show Phase, Step, next D id | Read-only |
| `docdev new-decision "<title>" <project>` | Append next D-XXX skeleton | Writes DECISIONS.md |
| `docdev sync-skill` | Copy/link skill into agent homes | Writes skill target dirs |
| `docdev update` | Update a native release install from a release manifest and artifact | Writes user install dirs; optionally syncs skill target dirs |
| `docdev doctor` | Show local install and sync state | Read-only |
| `docdev --version` / `docdev -v` | Show CLI version | Read-only |

### 3.4 Native Release Install and Update

For user installation from a published GitHub Release, the native installer is
the preferred path. It downloads a release manifest and artifact, verifies the
artifact SHA256, installs under the user's home directory, switches a
`current` pointer after verification, writes a launcher, and runs
`docdev doctor`.

Default Unix layout:

```text
~/.local/share/docdev/releases/<version>/
~/.local/share/docdev/current -> releases/<version>
~/.local/bin/docdev
```

The launcher sets `DOCDEV_PROJECT_DIR` and `PYTHONPATH` to the `current`
release so users do not need a source checkout or manual environment setup.
The installer may warn when `~/.local/bin` is not on `PATH`, but it must not
mutate shell startup files automatically.

`docdev update` is the preferred native update entrypoint. It resolves the
latest or requested version, downloads and verifies the release, switches
`current`, runs doctor, and performs skill sync only when the caller explicitly
requests that side effect.

Release artifacts are built by:

```bash
./scripts/package_release.sh
```

The script writes release output outside the source-of-truth docs, and must not
place temporary artifacts in `docs/` except generated docdev reports under
`docs/_generated/docdev/`. A complete release asset directory includes:

```text
docdev-<version>.tar.gz
docdev-<version>.tar.gz.sha256
manifest.json
install_remote.sh
install_remote.ps1
```

Public GitHub Releases are the default distribution target. Private repository
installs require explicit authentication and may need `gh release download` or
GitHub API asset fetching before running the installer from a local
`file://` release asset directory. Tokens must not be written into generated
launchers or persistent install metadata.

### 3.5 Source Checkout Lifecycle

For a one-command target project bootstrap from this source checkout, run:

```bash
./scripts/setup_project.sh /path/to/project
```

This script installs the local wrapper, runs `docdev doctor`, initializes the
target project, and runs `docdev audit <project> --write-report`.

It may pass `docdev init` options after the project path. When `--docs-dir` is
passed, the script must audit the same docs directory.

This script is a source checkout convenience, not the normal cross-project
agent entrypoint.

For developer installation after cloning the source repo, run:

```bash
./scripts/install.sh
```

On Windows PowerShell, run:

```powershell
.\scripts\install.ps1
```

Windows CMD / PowerShell do not execute `.sh` files directly. Users may also
run `bash ./scripts/install.sh` from Git Bash or WSL.

This uses the default sync targets `codex,cursor,agents,claude` and refreshes
existing docs-driven-dev skill copies. It is the source checkout maintenance
path, not the primary native release installation path for new users.

After changing this source checkout, run:

```bash
./scripts/update_cli.sh --targets codex,cursor,agents,claude --force
```

The lifecycle installs the source wrapper, runs tests, checks the local install,
syncs installed skills, then checks again.

The update lifecycle prepares the source-local wrapper and refreshes installed
skill content for source checkout maintenance. `scripts/install.sh` is the
shorter cloned-checkout developer entrypoint over this same lifecycle. It does
not add `docdev` to the user's global shell `PATH` and does not create
skill-local CLI wrappers.
Direct terminal use from the source checkout should use `./.venv/bin/docdev`
on Unix shells or `.\.venv\Scripts\docdev.ps1` / `.\.venv\Scripts\docdev.cmd`
on Windows unless the user has explicitly configured PATH.

Source checkout updates should use normal git operations such as `git pull`, or
a clean clone, instead of copying downloaded files over an old checkout. Manual
file overlays can leave stale untracked source files; install/sync copies the
current checkout's `skill/` directory as it exists on disk.

Install and update scripts should print prefixed lifecycle logs. `install.*`
entrypoints use `[docdev install]`; update lifecycle scripts use
`[docdev update]`. Update logs should identify numbered phases and report a
failed phase with its exit code before exiting when possible.

### 3.6 Audit Checks

`docdev audit` checks:
- the four source documents exist;
- D-XXX ids are present, unique, monotonic, and not silently skipped;
- roadmap Step sections include acceptance criteria;
- SPEC has numbered invariants and no empty Choice cells in its Decision Table;
- each D-XXX entry has Options, Chosen, and Risks content;
- README Documentation Map links point at the active docs dir;
- AGENTS mentions the active docs dir.

For each change packet under `<docs_dir>/changes/`, `docdev audit` also checks:
- `SPEC.md`, `ROADMAP.md`, and `DECISIONS.md` exist;
- missing `ARCHITECTURE.md` has an explicit omission reason in `ROADMAP.md`;
- roadmap Step sections include acceptance criteria;
- implementation-phase packets have completed pre-implementation gates;
- completed packets have completion gates and verification records.

### 3.7 Sync Behaviour

`docdev sync-skill` may copy the skill to Codex, Cursor, and shared agents
targets. Claude should use a symlink to `~/.agents/skills/docs-driven-dev` when
possible, matching the existing shared Lark skill pattern. If the platform
refuses symlink creation, Claude may receive a copied skill directory instead
of blocking the whole sync lifecycle.

Sync target paths resolve in this order:
1. exact target override `DOCDEV_<TARGET>_SKILL_DIR`;
2. target home override `DOCDEV_<TARGET>_HOME` plus `skills/docs-driven-dev`;
3. existing `CODEX_HOME` for Codex only;
4. default current-user home paths like `~/.codex/skills/docs-driven-dev`.

`<TARGET>` is one of `CODEX`, `CURSOR`, `AGENTS`, or `CLAUDE`.
Environment variables are read from the current process environment. On
Windows, that can come from the current PowerShell `$env:...` session or from
persistent user/system environment variables.

Existing target directories without a `.docdev-skill-source` marker require
`--force` before replacement.

Existing target directories with a `.docdev-skill-source` marker, or any target
when `--force` is passed, are refreshed by whole-directory replacement: delete
the target skill directory, copy the current source skill, and write the marker.
This prevents stale files from remaining inside the current target skill
directory, including old `bin/docdev*` wrappers from pre-D-025 syncs. It does
not clean a different old target path if the configured skill directory changed
between installs.

Source checkout sync must not generate skill-local `bin/docdev`,
`bin/docdev.ps1`, or `bin/docdev.cmd` wrappers. Native cross-machine use should
use the native launcher instead.

## 4. Default Handling

| Scenario | Default behaviour |
|---|---|
| No `.docdev.toml` | Use `docs/` |
| Audit report requested | Write `audit.json` under `<docs_dir>/_generated/docdev/` |
| Audit quality issue found | Report a warning unless required source structure is missing or invalid |
| Missing `docdev` on `PATH` after native install | Use `~/.local/bin/docdev` directly on Unix-like systems |
| Skill invoked in another project with no `docdev` on `PATH` | Use `~/.local/bin/docdev` when present; otherwise ask the user to run the native installer |
| Explicit source checkout development | Source maintainers may use `.venv` wrappers or `DOCDEV_PROJECT_DIR` + `PYTHONPATH` locally |
| Human terminal cannot find `docdev` after source checkout install | Use the source `.venv` wrapper or add a PATH entry manually |
| Existing project needs a new feature or research packet | Use `docdev new-change "<slug>" <project>` |
| Existing code project has no `docs/SPEC.md` | Run `docdev init <project>` first, then `docdev new-change "<slug>" <project>` |
| Skill explicitly named for a small bug fix | Use Workflow B0: minimal adoption if needed, then a minimal change packet before code |
| Skill explicitly named but user forbids docs | State that the full docs-driven workflow is blocked and ask whether to proceed outside the skill |
| Change packet omits `ARCHITECTURE.md` | Require a ROADMAP reason explaining why architecture detail is unnecessary |
| User wants one-command source checkout setup | Use `./scripts/setup_project.sh /path/to/project` |
| Source has just been updated | Run `./scripts/update_cli.sh --targets codex,cursor,agents,claude --force` |
| User wants release-style install from GitHub Releases | Run the native remote installer and verify manifest/checksum before activation |
| Native release install has been updated | Run `docdev update`; use `--sync-skill` only when skill targets should be refreshed |
| Source repo has just been cloned for development | Run `./scripts/install.sh` |
| Source repo has just been cloned for development in Windows PowerShell | Run `.\scripts\install.ps1` |
| Source checkout was manually overwritten | Prefer replacing it with a clean git checkout before install |
| Existing installed docs-driven-dev skill is refreshed by default install | Replace the current target skill directory; do not merge files |
| Install fails on another machine | Use the last `[docdev install]` or `[docdev update]` step line to identify the interrupted phase |
| Agent skill directory is non-default | Set `DOCDEV_<TARGET>_SKILL_DIR` or `DOCDEV_<TARGET>_HOME` before install/sync |
| Ambiguous user design choice | Ask 1-3 short questions before changing SPEC |
| User did not ask for commit | Do not stage or commit automatically |

## 5. Module Contracts

### 5.1 CLI

```python
def main(argv: Iterable[str] | None = None) -> int:
    """Run a docdev command and return a process exit code."""
```

`docs_driven_dev.cli` is the stable executable module for native launchers,
source checkout wrappers, and `python -m docs_driven_dev.cli`. It may re-export
selected helpers for compatibility, but feature implementation should live in
responsibility-focused internal modules such as `commands.py`, `templates.py`,
`audit.py`, `sync.py`, and `release.py`.

Constraints:
- Input domain: project paths, optional docs dir override, change slug/date/lang, sync target list.
- Output domain: console summaries, markdown scaffolds, optional JSON audit.
- Error categories: missing templates, missing docs, audit warnings/errors, unsafe sync replacement.
- Related invariants: #1, #2, #3, #4, #7.

### 5.2 Skill

The skill must stay concise enough to load as procedural context. Examples and
long guidance live in `skill/references/`.

Constraints:
- Mention when to use the CLI.
- Preserve the four-file boundaries.
- Avoid agent-specific tools unless phrased as current-tool fallbacks.

## 6. Non-Goals

- No cloud service, daemon, or database.
- No automatic semantic rewrite of existing project docs.
- No dependency on a package index or global Python install.
- No mandatory network dependency for source checkout development workflows.
- No attempt to enforce every documentation quality rule mechanically.

## 7. Invariants

1. **#1**: The four source documents remain human-authored source of truth.
2. **#2**: Generated reports live only under `<docs_dir>/_generated/docdev/`.
3. **#3**: The CLI stays stdlib-only and runnable from a source checkout.
4. **#4**: Skill sync must never replace an unmarked existing skill directory unless the caller passes `--force`.
5. **#5**: The installed skill is a decision layer; deterministic operations belong in CLI/scripts.
6. **#6**: Source changes should be verified and synced through the project-local update lifecycle before installed skills are treated as current.
7. **#7**: Requirement-level work packets must not weaken the project-level four-doc contract; they add scoped working memory under `<docs_dir>/changes/`.
8. **#8**: Explicit `docs-driven-dev` invocation must not be silently downgraded into direct coding; docs artifacts come first for code changes.
9. **#9**: Native release installers and updates must verify artifact checksums before switching the active `current` release.
10. **#10**: `docs_driven_dev.cli` remains the stable executable entrypoint even when internal CLI implementation is split across lightweight modules.

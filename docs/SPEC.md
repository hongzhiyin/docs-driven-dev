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
| E | Install style | Source checkout wrapper in `.venv/bin/docdev`; no network install required | See D-001 |
| F | Skill sync targets | `~/.codex`, `~/.cursor`, `~/.agents`, and Claude symlink to shared agents skill | See D-003 |
| G | Audit strictness | Structural drift is reported as warnings unless a required source document or invariant is broken | See D-005 |
| H | Cross-project CLI discovery | Synced skill copies include `bin/docdev`; `PATH` and `DOCDEV_PROJECT_DIR` are fallbacks, not requirements | See D-006 |
| I | Update lifecycle | Source updates should use a project-local install, test, check, sync, check sequence | See D-007 |
| J | Quick start | A source-checkout setup script combines install, doctor, init, and audit report for a target project | See D-008 |
| K | Target project model | `docdev` commands operate on explicit target project paths; source checkout scripts are maintenance conveniences | See D-009 |
| L | Fresh machine onboarding | `scripts/install.sh` installs, verifies, syncs, and enables agent-mediated CLI use from a cloned source checkout | See D-010 |
| M | Requirement granularity | Project-level four docs stay required; per-requirement change packets are optional under `docs/changes/` | See D-012 |

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

### 3.3 CLI Commands

`docdev` is a reusable project tool, not a single-repository command. Agents
should pass the intended target project path explicitly unless the user's
current working directory is itself the target project.

| Command | Purpose | Side effects |
|---|---|---|
| `docdev init <project>` | Create templates, README pointer, AGENTS pointer, generated dir | Writes project docs |
| `docdev new-change "<slug>" <project>` | Create a per-requirement change packet | Writes project docs |
| `docdev audit <project>` | Check project docs plus existing change packets for structure, numbering, source-map drift, and required rationale blocks | Optional audit report |
| `docdev status <project>` | Show Phase, Step, next D id | Read-only |
| `docdev new-decision "<title>" <project>` | Append next D-XXX skeleton | Writes DECISIONS.md |
| `docdev sync-skill` | Copy/link skill into agent homes | Writes skill target dirs |
| `docdev doctor` | Show local install and sync state | Read-only |

### 3.4 Source Update Lifecycle

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

For fresh-machine installation after cloning the source repo, run:

```bash
./scripts/install.sh
```

This uses the default sync targets `codex,cursor,agents,claude` and refreshes
existing docs-driven-dev skill copies.

After changing this source checkout, run:

```bash
./scripts/update_cli.sh --targets codex,cursor,agents,claude --force
```

The lifecycle installs the source wrapper, runs tests, checks the local install,
syncs installed skills, then checks again.

The update lifecycle prepares the local wrapper and installed skill-local
wrappers so agents can later run `docdev` against arbitrary target project
paths. `scripts/install.sh` is the shorter fresh-machine entrypoint over this
same lifecycle.

### 3.5 Audit Checks

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

### 3.6 Sync Behaviour

`docdev sync-skill` may copy the skill to Codex, Cursor, and shared agents
targets. Claude should use a symlink to `~/.agents/skills/docs-driven-dev` when
possible, matching the existing shared Lark skill pattern.

Existing target directories without a `.docdev-skill-source` marker require
`--force` before replacement.

Synced skill copies must include a skill-local `bin/docdev` wrapper that points
back to the source checkout. This lets agents invoke deterministic CLI behavior
from arbitrary project directories even when `docdev` is not on shell `PATH` and
`DOCDEV_PROJECT_DIR` is unset.

## 4. Default Handling

| Scenario | Default behaviour |
|---|---|
| No `.docdev.toml` | Use `docs/` |
| Audit report requested | Write `audit.json` under `<docs_dir>/_generated/docdev/` |
| Audit quality issue found | Report a warning unless required source structure is missing or invalid |
| Missing `docdev` wrapper | Use `DOCDEV_PROJECT_DIR` + `PYTHONPATH` fallback |
| Skill invoked in another project with no `docdev` on `PATH` | Use the installed skill-local `bin/docdev` wrapper |
| Existing project needs a new feature or research packet | Use `docdev new-change "<slug>" <project>` |
| Change packet omits `ARCHITECTURE.md` | Require a ROADMAP reason explaining why architecture detail is unnecessary |
| User wants one-command source checkout setup | Use `./scripts/setup_project.sh /path/to/project` |
| Source has just been updated | Run `./scripts/update_cli.sh --targets codex,cursor,agents,claude --force` |
| Source repo has just been cloned on a new machine | Run `./scripts/install.sh` |
| Ambiguous user design choice | Ask 1-3 short questions before changing SPEC |
| User did not ask for commit | Do not stage or commit automatically |

## 5. Module Contracts

### 5.1 CLI

```python
def main(argv: Iterable[str] | None = None) -> int:
    """Run a docdev command and return a process exit code."""
```

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
- No dependency on a package index or network install.
- No attempt to enforce every documentation quality rule mechanically.

## 7. Invariants

1. **#1**: The four source documents remain human-authored source of truth.
2. **#2**: Generated reports live only under `<docs_dir>/_generated/docdev/`.
3. **#3**: The CLI stays stdlib-only and runnable from a source checkout.
4. **#4**: Skill sync must never replace an unmarked existing skill directory unless the caller passes `--force`.
5. **#5**: The installed skill is a decision layer; deterministic operations belong in CLI/scripts.
6. **#6**: Source changes should be verified and synced through the project-local update lifecycle before installed skills are treated as current.
7. **#7**: Requirement-level work packets must not weaken the project-level four-doc contract; they add scoped working memory under `<docs_dir>/changes/`.

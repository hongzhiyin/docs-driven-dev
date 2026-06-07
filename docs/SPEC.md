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

## 3. Derived Rules

### 3.1 Four Source Documents

| File | Responsibility |
|---|---|
| `SPEC.md` | Expected behaviour, invariants, contracts, defaults |
| `ARCHITECTURE.md` | Actual structure, modules, data flow, configuration |
| `ROADMAP.md` | Current Phase/Step state, tasks, acceptance |
| `DECISIONS.md` | D-XXX rationale, options, choice, risks |

No other file can silently replace these four as the source of truth.

### 3.2 CLI Commands

| Command | Purpose | Side effects |
|---|---|---|
| `docdev init <project>` | Create templates, README pointer, AGENTS pointer, generated dir | Writes project docs |
| `docdev audit <project>` | Check docs structure, numbering, source-map drift, and required rationale blocks | Optional audit report |
| `docdev status <project>` | Show Phase, Step, next D id | Read-only |
| `docdev new-decision "<title>" <project>` | Append next D-XXX skeleton | Writes DECISIONS.md |
| `docdev sync-skill` | Copy/link skill into agent homes | Writes skill target dirs |
| `docdev doctor` | Show local install and sync state | Read-only |

### 3.3 Audit Checks

`docdev audit` checks:
- the four source documents exist;
- D-XXX ids are present, unique, monotonic, and not silently skipped;
- roadmap Step sections include acceptance criteria;
- SPEC has numbered invariants and no empty Choice cells in its Decision Table;
- each D-XXX entry has Options, Chosen, and Risks content;
- README Documentation Map links point at the active docs dir;
- AGENTS mentions the active docs dir.

### 3.4 Sync Behaviour

`docdev sync-skill` may copy the skill to Codex, Cursor, and shared agents
targets. Claude should use a symlink to `~/.agents/skills/docs-driven-dev` when
possible, matching the existing shared Lark skill pattern.

Existing target directories without a `.docdev-skill-source` marker require
`--force` before replacement.

## 4. Default Handling

| Scenario | Default behaviour |
|---|---|
| No `.docdev.toml` | Use `docs/` |
| Audit report requested | Write `audit.json` under `<docs_dir>/_generated/docdev/` |
| Audit quality issue found | Report a warning unless required source structure is missing or invalid |
| Missing `docdev` wrapper | Use `DOCDEV_PROJECT_DIR` + `PYTHONPATH` fallback |
| Ambiguous user design choice | Ask 1-3 short questions before changing SPEC |
| User did not ask for commit | Do not stage or commit automatically |

## 5. Module Contracts

### 5.1 CLI

```python
def main(argv: Iterable[str] | None = None) -> int:
    """Run a docdev command and return a process exit code."""
```

Constraints:
- Input domain: project paths, optional docs dir override, sync target list.
- Output domain: console summaries, markdown scaffolds, optional JSON audit.
- Error categories: missing templates, missing docs, audit warnings/errors, unsafe sync replacement.
- Related invariants: #1, #2, #3, #4.

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

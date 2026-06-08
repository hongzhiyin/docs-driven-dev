# DECISIONS - docs-driven-dev

> Source of truth for rationale.

## Maintenance Rules

1. D-XXX numbers are monotonic: do not reuse and do not skip.
2. Reversing a decision means adding a new D-XXX and marking the old entry as
   superseded; do not rewrite old conclusions.
3. Each non-trivial decision should include at least three options.
4. Risk registration is required, even if the risk is "no known risk".

---

## D-001 - Step 1 - Split reusable doctrine into skill plus stdlib CLI

**Date**: 2026-06-08

**Context**:
The existing Cursor-only skill already described a useful docs-driven workflow,
but agents had to manually copy templates, manage D-XXX numbering, and remember
agent-specific install paths.

**Options**:
- A. Keep a single Cursor skill only - simplest, but Codex and Claude cannot
  reliably share the same source.
- B. Make a full app with a daemon and rich validation - powerful, but far too
  heavy for a local documentation convention.
- C. Create a small source project with a portable skill and stdlib-only CLI -
  enough determinism for scaffolding, audit, numbering, and sync without adding
  operational weight.

**Chosen**: C

**Rationale**:
- The CLI removes repeated fragile shell snippets while staying easy to inspect.
- The skill remains the judgment layer instead of becoming a long script manual.
- A source checkout wrapper avoids package-index and PEP 668 friction.

**Risks**:
- The CLI may start accumulating policy. Mitigation: keep product/design choices
  in SPEC/DECISIONS and skill prose, not CLI code.

**Related code / docs**:
- SPEC §2 A, D, E
- `src/docs_driven_dev/cli.py`
- `skill/SKILL.md`

---

## D-002 - Step 1 - Standardize generated output under docs/_generated/docdev

**Date**: 2026-06-08

**Context**:
The four source documents should stay human-authored. Audits and future machine
reports need a predictable location that will not be mistaken for doctrine.

**Options**:
- A. Put generated files next to the four docs - discoverable, but it pollutes
  the source-of-truth folder.
- B. Put generated files outside `docs/` - clean, but future agents may miss
  audit outputs while reading documentation.
- C. Put generated files under `<docs_dir>/_generated/docdev/` - discoverable
  inside the docs tree while clearly separated from human-authored docs.

**Chosen**: C

**Rationale**:
- The path works for default `docs/` and custom `.docdev.toml` docs dirs.
- `_generated` communicates that agents should not edit these files as doctrine.
- The CLI can create and write this folder deterministically.

**Risks**:
- Some projects may not want generated files committed. Mitigation: projects can
  ignore `docs/_generated/` in `.gitignore` if needed.

**Related code / docs**:
- SPEC §2 B, C
- `src/docs_driven_dev/cli.py`
- `skill/SKILL.md`

---

## D-003 - Step 1 - Use shared agents skill as Claude sync anchor

**Date**: 2026-06-08

**Context**:
This machine already uses `~/.claude/skills/*` symlinks into `~/.agents/skills/*`
for Lark skills. docs-driven-dev should fit that convention instead of creating
a separate Claude-only copy.

**Options**:
- A. Copy the skill separately into every agent home - simple, but duplicates
  drift.
- B. Use only `~/.agents/skills` and ask each agent to discover it - clean, but
  Codex/Cursor may not read that path directly.
- C. Copy to Codex/Cursor/shared agents and link Claude to shared agents - uses
  each agent's expected path while keeping Claude aligned with the shared source.

**Chosen**: C

**Rationale**:
- It matches existing local Claude/Lark skill practice.
- Codex and Cursor still receive direct skill folders.
- Re-syncing from the source checkout is explicit and reversible.

**Risks**:
- Symlink support or Claude skill loading could change. Mitigation: add a
  target-specific sync adapter later if needed.

**Related code / docs**:
- SPEC §2 F
- `src/docs_driven_dev/cli.py`
- `scripts/sync_skill.sh`

---

## D-004 - Step 2 - Keep generated and local runtime artifacts out of git

**Date**: 2026-06-08

**Context**:
After initializing git for the source checkout, the repository needed a clear
boundary between editable project sources and local/generated artifacts such as
the virtual environment, Python caches, and docdev audit outputs.

**Options**:
- A. Track every file in the checkout - easy to reason about, but commits local
  runtime state and generated reports.
- B. Ignore only `.venv/` and Python caches - avoids the largest noise, but
  generated reports can still look like durable source documents.
- C. Ignore local runtime artifacts and generated docdev report contents while
  preserving the generated directory location - keeps the source tree clean
  without changing the SPEC-defined output path.

**Chosen**: C

**Rationale**:
- The four source documents remain the human-authored source of truth.
- `docs/_generated/docdev/` is still the required location for generated
  reports, but report contents do not need to be committed by default.
- A clean first git state makes future changes easier to review.

**Risks**:
- A useful generated report might be missed in git history. Mitigation: commit
  a curated report explicitly only when it becomes evidence worth preserving.

**Related code / docs**:
- `.gitignore`
- SPEC §2 C
- D-002

---

## D-005 - Step 3 - Add focused audit warnings for common doc drift

**Date**: 2026-06-08

**Context**:
After the skill was synced across agent homes, the next practical failure modes
were not missing files but subtle source-document drift: README links pointing
at stale docs, SPEC decision rows with blank choices, and D-XXX entries missing
the rationale blocks future agents need.

**Options**:
- A. Keep audit limited to missing files and numbering - stable, but misses
  mistakes that weaken handoff quality.
- B. Add broad semantic linting for documentation quality - ambitious, but
  likely noisy and hard to keep deterministic.
- C. Add narrow structural warnings for README map links, SPEC Choice cells,
  and DECISIONS Options/Chosen/Risks blocks - catches real drift without trying
  to judge prose quality.

**Chosen**: C

**Rationale**:
- The checks match the Step 3 roadmap items directly.
- Warnings preserve usability for partially drafted docs while still surfacing
  handoff risks.
- Fixture tests keep the CLI stdlib-only and guard against obvious false
  positives in fresh scaffolds.

**Risks**:
- Some teams may intentionally omit README maps or decision blocks. Mitigation:
  keep these findings as warnings and refine only after real usage shows a
  repeated false positive.

**Related code / docs**:
- SPEC §3.2, §3.3
- `src/docs_driven_dev/cli.py`
- `tests/test_cli.py`

---

## D-006 - Step 4 - Generate skill-local CLI wrappers during sync

**Date**: 2026-06-08

**Context**:
When docs-driven-dev is invoked from an unrelated project, the agent may have
the skill context but not have `docdev` on shell `PATH`, and
`DOCDEV_PROJECT_DIR` may be unset. Asking the agent to search for the source
checkout works sometimes, but it is brittle and slows down the normal workflow.

**Options**:
- A. Require users to put `.venv/bin/docdev` on global `PATH` - simple for one
  machine, but it leaks local shell setup into every agent session.
- B. Require `DOCDEV_PROJECT_DIR` in shell profile - close to the existing
  fallback, but still depends on environment propagation into each tool host.
- C. Generate a `bin/docdev` wrapper inside each copied installed skill - keeps
  the deterministic CLI available wherever the skill is loaded, while still
  pointing back to the single source checkout.

**Chosen**: C

**Rationale**:
- The installed skill becomes self-sufficient for cross-project sessions.
- The source checkout remains the only editable CLI implementation.
- The pattern matches the skill/CLI boundary proven by the Bilibili tool, while
  avoiding a hard requirement that `docdev` be globally installed.

**Risks**:
- If the source checkout moves, installed wrappers become stale. Mitigation:
  rerun `./scripts/sync_skill.sh --targets codex,cursor,agents,claude --force`
  after moving the project.

**Related code / docs**:
- SPEC §3.4
- `skill/SKILL.md`
- `src/docs_driven_dev/cli.py`
- `tests/test_cli.py`

---

## D-007 - Step 4a - Add skill metadata and project-local update lifecycle

**Date**: 2026-06-08

**Context**:
`docs-driven-dev` already has a clean portable skill plus CLI structure and
installed `bin/docdev` wrappers. A later `skill-cli-kit` audit added two newer
conventions that this project had not yet adopted: skill frontmatter should
declare the required CLI bin/help command, and each source checkout should have
a project-local update script that runs install, tests, checks, sync, and
post-sync verification.

**Options**:
- A. Leave the project as-is because `docdev` and installed wrappers already
  work - lowest churn, but future agents still see avoidable portability
  warnings.
- B. Add a new `docdev update` subcommand - discoverable, but it expands the
  CLI command surface for a source-maintenance workflow that scripts already
  cover well.
- C. Add frontmatter metadata plus `scripts/update_cli.sh` - aligns with
  `skill-cli-kit` without changing the user-facing docs-driven command surface.

**Chosen**: C

**Rationale**:
- The skill can advertise its deterministic CLI dependency directly to agent
  hosts.
- Source updates get the same repeatable lifecycle as other local skill-backed
  CLI projects.
- Keeping the lifecycle in a script avoids adding policy or source-maintenance
  behavior to the `docdev` CLI itself.

**Risks**:
- The update script may duplicate sequencing already known to `skill-cli-kit`.
  Mitigation: keep it tiny and project-local, and let it call existing
  install/check/sync scripts.

**Related code / docs**:
- SPEC §2 I, §3.3
- ROADMAP Step 4a
- `skill/SKILL.md`
- `scripts/update_cli.sh`

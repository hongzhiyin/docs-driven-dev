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
- SPEC §3.3, §3.5
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
- SPEC §3.6
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
- SPEC §2 I, §3.4
- ROADMAP Step 4a
- `skill/SKILL.md`
- `scripts/update_cli.sh`

---

## D-008 - Step 4b - Use a setup script for one-command target bootstrap

**Date**: 2026-06-09

**Context**:
The README Quick Start required four commands: install the local wrapper, run
doctor, initialize a target project, and run audit with a report. That is too
much friction for the most common first-use path, especially when the user only
wants to apply docs-driven-dev to a project.

**Options**:
- A. Keep the four commands visible - explicit, but slow and easy to copy
  incompletely.
- B. Add a new `docdev bootstrap` subcommand - compact after install, but it
  expands the core CLI surface for a source-checkout convenience flow.
- C. Add `scripts/setup_project.sh` - one command from the source checkout
  while reusing existing deterministic CLI commands unchanged.

**Chosen**: C

**Rationale**:
- The user-facing Quick Start becomes one command.
- The core `docdev` CLI stays focused on reusable deterministic operations.
- The script remains transparent and composes existing install, doctor, init,
  and audit behavior.

**Risks**:
- Wrapper scripts can duplicate CLI behavior over time. Mitigation: keep the
  script thin and let it call existing `docdev` commands instead of
  reimplementing their logic.

**Related code / docs**:
- SPEC §3.4
- ROADMAP Step 4b
- `README.md`
- `scripts/setup_project.sh`

---

## D-009 - Step 4c - Treat docdev as a multi-project skill-mediated CLI

**Date**: 2026-06-09

**Context**:
The README first showed the source checkout setup script. That made the project
look like it had a unique operational working directory. The intended use is
different: agents load the skill in arbitrary target projects, resolve the
`docdev` executable, and pass the relevant project path explicitly.

**Options**:
- A. Keep the source checkout setup script as the primary README entry - short,
  but it overemphasizes the implementation checkout.
- B. Make users install `docdev` globally and rely on current working directory
  defaults - convenient, but weaker for agent sessions that hop across projects.
- C. Document the target-project model first and keep source scripts as
  maintenance/setup conveniences - matches agent-mediated use without removing
  source checkout workflows.

**Chosen**: C

**Rationale**:
- It matches how agents use other CLIs: resolve the tool, then pass an explicit
  target or run from a known target directory.
- It avoids treating `/Users/chihoyo/Project/docs-driven-dev` as the project
  being operated on by default.
- It preserves the one-command source setup path for manual first use.

**Risks**:
- README becomes slightly longer. Mitigation: keep the source script section
  short and reserve detailed workflow guidance for the skill.

**Related code / docs**:
- README Usage Model
- SPEC §3.3
- ROADMAP Step 4c

---

## D-010 - Step 4d - Use update lifecycle as the fresh-machine install path

**Date**: 2026-06-09

**Context**:
On a new computer, the user expects to clone this GitHub source repo, run one
command, and then use the installed skill from arbitrary agents. The previous
README described target setup but did not distinguish fresh-machine installation
from manual source-checkout project initialization.

**Options**:
- A. Tell users to run `setup_project.sh` first - initializes a target project,
  but does not clearly describe agent skill installation and sync.
- B. Add a second install command just for new machines - explicit, but
  duplicates the existing update lifecycle.
- C. Document `scripts/update_cli.sh` as both source update lifecycle and
  fresh-machine install/sync command - one maintained lifecycle with clear
  post-clone semantics.

**Chosen**: C

**Rationale**:
- It is already the command that installs, verifies, syncs, and checks installed
  skill copies.
- It generates installed skill-local `bin/docdev` wrappers used by agents in
  other project directories.
- It avoids adding another script that would need to stay in sync.

**Risks**:
- The word "update" is slightly less obvious for first install. Mitigation:
  README and skill docs explicitly label it as the fresh-machine install path.

**Related code / docs**:
- README Fresh Machine Install
- SPEC §3.4
- ROADMAP Step 4d
- `scripts/update_cli.sh`

---

## D-011 - Step 4e - Add scripts/install.sh as the fresh-machine command

**Date**: 2026-06-09

**Context**:
The command `./scripts/update_cli.sh --targets codex,cursor,agents,claude
--force` works but is too long for first install. The user also expects the
operation name to match common CLI conventions such as LarkCLI, where
installation is called install and configuration/init are separate steps.

**Options**:
- A. Keep documenting the full `update_cli.sh` command - explicit, but too
  verbose for new-machine onboarding.
- B. Rename `update_cli.sh` to `install.sh` - simple, but loses a useful name
  for source update lifecycle.
- C. Add `scripts/install.sh` as a thin fresh-machine entrypoint over
  `update_cli.sh` - concise install command while preserving the lifecycle
  script.

**Chosen**: C

**Rationale**:
- New-machine setup becomes `./scripts/install.sh`.
- The update lifecycle stays available and explicit for source maintenance.
- The install script is thin and delegates to existing verified behavior.

**Risks**:
- Two scripts can appear redundant. Mitigation: document `install.sh` as the
  first-install entrypoint and `update_cli.sh` as the maintenance lifecycle.

**Related code / docs**:
- README Fresh Machine Install
- SPEC §3.4
- ROADMAP Step 4e
- `scripts/install.sh`
- `scripts/update_cli.sh`

---

## D-012 - Step 5 - Add per-requirement packets as a second mode

**Date**: 2026-06-09

**Context**:
The repo now includes `temp/` reference material from an older pure skill. That
workflow is stronger for existing-project feature work because it uses
per-requirement work packets, research logs, implementation gates, optional
architecture docs, Chinese-first templates, and verification records. The
current source project is stronger at project-level docs, deterministic CLI
operations, audit, install, and cross-agent sync.

**Options**:
- A. Replace the current project-level four-doc model with the older skill
  workflow - improves requirement discipline, but loses the durable project
  contract and would invalidate existing root audit behavior.
- B. Keep the current model unchanged and leave `temp/` as informal reference -
  avoids churn, but agents would still miss the older workflow's strongest
  existing-project practices.
- C. Add requirement-level change packets under `docs/changes/` while keeping
  the project-level four-doc contract required - combines scoped feature memory
  with existing CLI/audit/install guarantees.

**Chosen**: C

**Rationale**:
- Project-level `SPEC.md`, `ARCHITECTURE.md`, `ROADMAP.md`, and
  `DECISIONS.md` remain the durable source of truth.
- Change packets isolate feature research, approvals, and verification so
  parallel requirements do not pollute root docs.
- The CLI can scaffold and audit the repeatable parts while the skill continues
  to own judgment, research discipline, and user approval gates.

**Risks**:
- Two document levels can confuse agents. Mitigation: README and SKILL must
  state when to use project docs versus change packets.
- Recursive audit can become noisy for draft packets. Mitigation: use warnings
  for workflow quality gaps and reserve errors for missing required packet
  files or broken project-level source structure.

**Related code / docs**:
- SPEC §3.2, §3.3, §3.5
- ROADMAP Step 5
- `temp/DocsDrivenDev-对比与改造方案.md`
- `temp/SKILL.md`

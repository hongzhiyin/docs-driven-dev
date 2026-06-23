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

---

## D-013 - Step 5a - Add PowerShell install and Windows wrappers

**Date**: 2026-06-09

**Context**:
On a new Windows computer, running `./scripts/install.sh` from a Windows
terminal opened an app chooser instead of executing the installer. The `.sh`
entrypoint is correct for Unix shells and Git Bash, but PowerShell/CMD do not
execute shell scripts by default. The installed skill also needs Windows-native
wrappers so agents can call `docdev` without relying on a Unix shell.

**Options**:
- A. Tell Windows users to install Git Bash or WSL and run
  `bash ./scripts/install.sh` - minimal repo change, but still leaves native
  PowerShell onboarding broken.
- B. Replace shell scripts with Python-only commands - cross-platform, but
  makes the simple install/update lifecycle less transparent and changes the
  existing Unix workflow.
- C. Keep the Unix scripts and add PowerShell/CMD counterparts - preserves the
  existing flow while making Windows onboarding native.

**Chosen**: C

**Rationale**:
- Windows users get a direct `.\scripts\install.ps1` command.
- Existing macOS/Linux/Git Bash behavior remains unchanged.
- Installed skills can expose both Unix and Windows wrappers while still
  pointing back to the same source checkout.

**Risks**:
- The Windows scripts are mostly contract-tested from macOS in this repo.
  Mitigation: keep them thin, equivalent to the shell scripts, and add real
  Windows execution testing after the user runs them on the new machine.

**Related code / docs**:
- SPEC §2 N, §3.4, §3.6
- ROADMAP Step 5a
- `scripts/install.ps1`
- `scripts/update_cli.ps1`
- `scripts/install_cli.ps1`
- `src/docs_driven_dev/cli.py`

---

## D-014 - Step 5b - Use explicit PowerShell parameter forwarding

**Date**: 2026-06-09

**Context**:
The first Windows run of `scripts/install.ps1` reached the installer after
`Unblock-File`, but then failed with a PowerShell binding error: no positional
parameter accepted `codex,cursor,agents,claude`. The script used `$Args` and
`@Args` to forward `-Targets`, which is too easy to confuse with PowerShell's
automatic `$args` variable and can degrade into positional argument binding.

**Options**:
- A. Tell users to call `update_cli.ps1` directly - avoids the failing wrapper,
  but leaves the advertised install command broken.
- B. Keep array splatting but rename the variable - likely works, but still
  keeps unnecessary indirection in the shortest onboarding path.
- C. Invoke `update_cli.ps1` with explicit named parameters - simplest and
  least ambiguous for PowerShell binding.

**Chosen**: C

**Rationale**:
- The install command now forwards `-Targets <targets>` and `-Force` directly.
- The fix keeps the public `.\scripts\install.ps1` command unchanged.
- Regression tests can check the exact forwarding contract without needing a
  Windows PowerShell runtime on macOS.

**Risks**:
- The repo still lacks live Windows execution in CI. Mitigation: keep the
  PowerShell scripts thin and use the user's Windows machine feedback as the
  next verification loop.

**Related code / docs**:
- ROADMAP Step 5b
- `scripts/install.ps1`
- `tests/test_cli.py`

---

## D-015 - Step 5c - Keep Windows sync moving without Unix shell or symlink assumptions

**Date**: 2026-06-09

**Context**:
After the PowerShell installer started running, the next reported symptom was
that the skill did not appear to update in the configured agent folders. The
update lifecycle runs tests before sync, and this repo has tests that execute a
Unix `.sh` setup script. Windows PowerShell also commonly refuses symlink
creation unless developer mode or elevated privileges are available, which can
block the Claude target after other targets are copied.

**Options**:
- A. Require Git Bash / WSL and symlink privileges on Windows - preserves the
  existing Unix assumptions, but makes native PowerShell install unreliable.
- B. Remove the shell-script tests entirely - avoids Windows failure, but loses
  useful coverage on macOS/Linux.
- C. Skip Unix-only script execution tests on Windows and copy Claude as a
  fallback when symlink creation fails - keeps Unix coverage and makes native
  Windows sync complete.

**Chosen**: C

**Rationale**:
- The update lifecycle can continue to sync skill folders on Windows instead
  of stopping during tests.
- Claude still prefers the shared `~/.agents` symlink where the platform
  supports it.
- The fallback installed copy includes the same `bin/docdev`, `bin/docdev.ps1`,
  and `bin/docdev.cmd` wrappers as other copied targets.

**Risks**:
- Claude may have a copied skill on Windows instead of sharing the agents
  directory by symlink. Mitigation: future sync runs still overwrite it with
  `--force`, and platforms that support symlinks keep the shared-link behavior.

**Related code / docs**:
- SPEC §2 O, §3.6
- ARCHITECTURE §3.5, §7
- ROADMAP Step 5c
- `src/docs_driven_dev/cli.py`
- `tests/test_cli.py`

---

## D-016 - Step 5d - Emit numbered install/update lifecycle logs

**Date**: 2026-06-09

**Context**:
Windows install failures happen on a machine the agent cannot directly inspect.
After fixing argument forwarding and sync fallback behavior, the next practical
need is observability: the user should be able to paste or screenshot the last
installer line and identify whether the failure happened during wrapper
installation, tests, doctor, sync, audit, or status.

**Options**:
- A. Leave logging to the underlying commands - no script change, but failures
  remain ambiguous when output is long.
- B. Add verbose logs only to PowerShell - targets the current Windows issue,
  but leaves Unix and Windows lifecycle output structurally different.
- C. Add stable prefixed step logs to both PowerShell and Unix lifecycle
  scripts - slightly more script text, but produces comparable diagnostics.

**Chosen**: C

**Rationale**:
- `[docdev install]` and `[docdev update]` prefixes are easy to search and
  recognize in terminal output.
- Numbered `step N/M start|done|failed` lines make remote failure reports
  precise without requiring the user to interpret Python or shell output.
- Keeping Unix and Windows logs aligned makes local validation more useful.

**Risks**:
- Additional script output is noisier. Mitigation: logs are one line per phase
  and keep command output unchanged.

**Related code / docs**:
- SPEC §2 P, §3.4
- ARCHITECTURE §3.6, §6
- ROADMAP Step 5d
- `scripts/install.sh`
- `scripts/update_cli.sh`
- `scripts/install.ps1`
- `scripts/update_cli.ps1`
- `tests/test_cli.py`

---

## D-017 - Step 5e - Use environment overrides for sync target paths

**Date**: 2026-06-09

**Context**:
The default sync paths are based on the current user's home directory:
`~/.codex`, `~/.cursor`, `~/.agents`, and `~/.claude`. That is portable across
usernames, but it still assumes every agent uses those home-relative skill
folders. On a new Windows machine, the real skill directory may be elsewhere,
and the user needs to see or override the exact target paths used by install.

**Options**:
- A. Keep only home-relative defaults - simple, but hides the actual failure if
  an agent uses a different skill directory.
- B. Add command-line flags for every target path - explicit, but makes the
  one-command install path longer and harder to remember.
- C. Add environment-variable overrides plus target-path logging - keeps the
  install command short while allowing machine-specific path configuration.

**Chosen**: C

**Rationale**:
- Environment variables are a standard fit for machine-specific install
  locations and can be set temporarily in PowerShell or persistently in Windows
  user/system environment settings.
- Exact `DOCDEV_<TARGET>_SKILL_DIR` overrides avoid ambiguity when a tool wants
  one specific final folder.
- `DOCDEV_<TARGET>_HOME` remains convenient for normal `home/skills/name`
  layouts.
- Printing resolved target paths makes Windows reports actionable without
  requiring the agent to inspect that machine.

**Risks**:
- Too many environment variable names can be confusing. Mitigation: direct
  `DOCDEV_<TARGET>_SKILL_DIR` wins over home overrides, and docs list only the
  two patterns.

**Related code / docs**:
- SPEC §2 Q, §3.6
- ARCHITECTURE §3.5, §5, §6
- ROADMAP Step 5e
- `src/docs_driven_dev/cli.py`
- `scripts/install_cli.ps1`
- `tests/test_cli.py`

---

## D-018 - Step 5f - Adopt existing codebases before opening change packets

**Date**: 2026-06-09

**Context**:
When the skill is used inside an existing code project that has no
`docs/SPEC.md` four-pack yet, an agent may report that it cannot run the full
change-packet workflow. That is too strict. The project is not blocked; it
needs lightweight docs-driven adoption first. At the same time, a standalone
`docs/changes/...` packet without root project docs would weaken the
project-level source-of-truth contract.

**Options**:
- A. Tell agents to create only `docs/changes/...` in existing code projects -
  fast, but leaves no durable project-level SPEC/ARCHITECTURE/ROADMAP/DECISIONS.
- B. Require the user to fully complete the four root docs before any
  requirement work - rigorous, but too heavy for onboarding an existing repo.
- C. Run `docdev init` with minimal pending root docs, then create the
  requirement packet - preserves the root contract while letting feature work
  start.

**Chosen**: C

**Rationale**:
- The root four docs remain the durable contract for future work.
- The requirement packet still captures research, gates, and verification for
  the current change.
- Unknown project-level facts can be marked pending and refined during the
  packet's research phase.

**Risks**:
- Root docs may start sparse. Mitigation: keep them explicit about pending
  facts and update them when research reveals durable constraints.

**Related code / docs**:
- SPEC §2 R, §3.2, §4
- ROADMAP Step 5f
- `skill/SKILL.md`
- `README.md`
- `tests/test_cli.py`

---

## D-019 - Step 5g - Keep install wrapper-based and make sync replacement explicit

**Date**: 2026-06-09

**Context**:
After fresh-machine install, a normal terminal may still not recognize
`docdev` because the install lifecycle prepares source and skill-local wrappers
but does not edit global shell PATH. The user also needs to know whether
refreshing an installed skill merges new files into the old directory or
replaces the old skill content, because stale installed files are a common
failure mode in reusable skill projects.

**Options**:
- A. Mutate global PATH during install - makes `docdev` easy to type in a
  normal terminal, but changes user shell configuration and varies across
  Windows, macOS, and agent tool hosts.
- B. Keep wrapper-only install but leave behavior implicit - least code churn,
  but future users and agents will keep confusing agent CLI availability with
  global terminal PATH.
- C. Keep wrapper-only install, add `docdev -v`, document direct wrapper usage,
  and make sync replacement semantics explicit - preserves install safety while
  making the operational contract testable.

**Chosen**: C

**Rationale**:
- Agents do not need global PATH because installed skills include skill-local
  `bin/docdev` wrappers pointing back to the source checkout.
- Humans can still run the CLI directly through the source `.venv` wrapper, or
  add a PATH entry manually if they want a global command.
- Force sync and marked-target refreshes delete the current target skill
  directory before copying the source skill, preventing stale files inside the
  active target path.
- `docdev -v` / `docdev --version` gives a low-friction sanity check without
  expanding the workflow command surface.

**Risks**:
- A user may still expect install to create a global `docdev` command.
  Mitigation: README and SKILL now state that install does not mutate global
  PATH and show direct wrapper commands.
- If the configured target path changes, an old skill directory at the previous
  path is outside the current sync operation. Mitigation: docs call this out so
  stale old paths can be removed manually when needed.
- If the source checkout itself is updated by manually copying files over an old
  folder, stale untracked source files can remain. Mitigation: docs recommend
  `git pull` or a clean clone before install.

**Related code / docs**:
- SPEC §2 S-T, §3.3, §3.4, §3.6, §4
- ARCHITECTURE §3.5, §3.6, §6
- ROADMAP Step 5g
- `src/docs_driven_dev/cli.py`
- `README.md`
- `skill/SKILL.md`
- `tests/test_cli.py`

---

## D-020 - Step 5h - Require workflow execution when docs-driven-dev is explicit

**Date**: 2026-06-09

**Context**:
A Codex agent can read the skill after the user explicitly names
`docs-driven-dev`, but still treat it as optional methodology and directly edit
code. The reported failure was a narrow existing-project fix where the agent
decided that initializing project docs and opening a change packet was too much
document churn. The current skill did not give a small-fix path, so the agent
chose between a heavy workflow and no docs workflow.

**Options**:
- A. Keep the existing workflows and rely on agent judgment - no churn, but the
  same silent downgrade can recur.
- B. Require the full Workflow B packet for every explicit invocation - strict,
  but too heavy for small bug fixes and likely to encourage future agents to
  avoid the skill.
- C. Add a hard invocation contract plus a minimal B0 small-fix workflow -
  prevents silent downgrade while keeping narrow fixes low-overhead.

**Chosen**: C

**Rationale**:
- Explicitly naming the skill should have observable process consequences:
  required docs artifacts before code changes.
- A B0 path gives agents a legitimate low-documentation route for small fixes
  instead of inventing a direct-coding shortcut.
- Treating "fix it", "补上吧", or "implement it" as implementation approval only
  after scope and acceptance are stated reconciles the skill with Codex's
  default implementation bias.

**Risks**:
- Even B0 can feel heavy in very large existing repositories. Mitigation: keep
  root adoption minimal, keep the packet narrow, and allow proceeding outside
  the skill only when the user explicitly forbids doc files.
- Agents may still miss the path if it appears after the broad existing-project
  workflow. Mitigation: place B0 before Workflow B in the skill.

**Related code / docs**:
- SPEC §2 U-V, §3.2.1, §4, §7
- ROADMAP Step 5h
- `skill/SKILL.md`
- `README.md`
- `tests/test_cli.py`

---

## D-021 - Native installer distribution before npm publishing

**Date**: 2026-06-11

**Context**:
The project currently installs from a cloned source checkout and generates
wrappers that point back to that checkout. The next portability step is
cross-machine distribution: users should be able to install and update a
released `docdev` without first cloning the repo or configuring
`DOCDEV_PROJECT_DIR`. The user explicitly wants a GitHub Releases / native
installer style path before considering npm.

**Options**:
- A. Publish npm first - familiar for CLI distribution, but it introduces Node
  and package-manager policy before this Python stdlib CLI needs it.
- B. Keep source checkout install as the only supported path - already works for
  local development, but keeps new-machine setup coupled to Git clone, source
  paths, and wrapper refresh.
- C. Add GitHub Releases / native installer distribution first - creates a
  public-release path with manifest/checksum, user-directory install, launcher,
  and explicit update while keeping source checkout workflows for maintainers.

**Chosen**: C

**Rationale**:
- It matches the desired Claude Code native installer pattern more closely than
  npm: download a release manifest/artifact, verify checksum, install under the
  user's home directory, and update through a command or script.
- It avoids global `pip`, global npm, and system Python mutation, preserving the
  project's stdlib-only and wrapper-based safety posture.
- A public GitHub Release is enough for the first distribution loop; private
  repositories can be documented as an advanced path that requires `gh auth` or
  token handling.
- Source checkout install/update remains useful for maintainers and can be
  documented separately from user installation.

**Risks**:
- GitHub availability becomes part of the install path. Mitigation: keep local
  source checkout install working and make release base URL configurable for
  tests or mirrors.
- Checksum-only manifests do not provide a full signing trust chain. Mitigation:
  require checksum verification now and leave signed manifest support as a
  future D-XXX enhancement.
- Private repository installs are more complex. Mitigation: design public repo
  first and document private repo authentication requirements explicitly.

**Related code / docs**:
- `docs/changes/2026-06-11-native-installer-distribution/`
- Future SPEC §2 / §3.4 updates
- Future ARCHITECTURE install/update data-flow updates
- Future README and `skill/SKILL.md` install guidance updates

---

## D-022 - Native launcher only for cross-machine agent CLI resolution

**Date**: 2026-06-11

**Context**:
After adding GitHub Releases / native installer distribution, the installed
skill still described source checkout fallbacks such as skill-local wrappers and
`DOCDEV_PROJECT_DIR` as part of normal CLI resolution. That undermines the
native installer goal: on another machine there may be no
`/Users/chihoyo/Project/docs-driven-dev` checkout, and agents should not infer
or depend on one.

**Options**:
- A. Keep source checkout fallbacks in the agent resolution order - useful for
  this development machine, but misleading for cross-machine release installs.
- B. Keep skill-local wrappers as the main fallback - compatible with older
  source-sync installs, but still allows wrappers to point back to a missing
  source path.
- C. Make agent resolution use only `docdev` on `PATH` or the native launcher;
  keep source checkout fallbacks only for explicit developer maintenance.

**Chosen**: C

**Rationale**:
- Native installs produce a stable launcher at `~/.local/bin/docdev` pointing to
  `~/.local/share/docdev/current`, so agents do not need source checkout
  access.
- If neither `docdev` nor the native launcher exists, the honest next step is
  to ask the user to install, not to guess a machine-specific source path.
- Source checkout wrappers remain useful for maintainers, but they should not be
  part of the cross-machine agent contract.

**Risks**:
- Existing source-synced local installs may still have working skill-local
  wrappers. Mitigation: keep them documented under source checkout development,
  not agent-native resolution.
- Windows native launcher behavior still needs live verification. Mitigation:
  keep Windows marked as framework/static-contract until tested.

**Related code / docs**:
- SPEC §2 H, §3.3, §4
- `skill/SKILL.md`
- `README.md`
- `tests/test_cli.py`

---

## D-023 - Use Chinese workflow prose in the skill while preserving CLI keywords

**Date**: 2026-06-11

**Context**:
The skill is not only machine-readable instructions for agents; it is also a
document the maintainer reads to verify whether agents will behave as intended.
The previous English-only prose made review slower for the primary maintainer,
while commands, paths, frontmatter, workflow names, and test anchors still
benefit from stable English keywords.

**Options**:
- A. Keep the entire skill in English - convenient for existing tests and
  grep-friendly, but harder for the maintainer to audit deeply.
- B. Translate everything into Chinese - easiest to read locally, but risks
  weakening tool discovery, command copy/paste, and existing keyword anchors.
- C. Use Chinese for workflow prose and maintainer-facing guidance, while
  preserving English headings, commands, paths, environment variables, and key
  contract phrases.

**Chosen**: C

**Rationale**:
- Chinese prose makes the skill easier for the maintainer to inspect and tune.
- English keywords such as `Invocation Contract`, `Workflow B0`,
  `docdev audit`, and `DOCDEV_PROJECT_DIR` remain stable for search, tests, and
  agent/tool recognition.
- The mixed style matches the README direction: user-facing explanation in
  Chinese, executable surfaces left literal.

**Risks**:
- Tests that assert prose can become brittle across language changes.
  Mitigation: update tests to check core contract phrases rather than long
  English-only sentences.
- Future contributors may mix styles inconsistently. Mitigation: keep headings
  bilingual where useful and preserve literal commands/paths.

**Related code / docs**:
- `skill/SKILL.md`
- `README.md`
- `tests/test_cli.py`

---

## D-024 - Post-native cleanup keeps source maintenance but removes legacy scratch

**Date**: 2026-06-12

**Context**:
Native v0.1.3 is now installable through the public GitHub Release path and
the local machine has a working `~/.local/bin/docdev` launcher. The source
checkout still contains tracked `temp/` reference material from the older pure
skill era, plus cache directories and current docs that still make some
compatibility wrappers look like normal cross-machine entrypoints.

**Options**:
- A. Remove every source checkout wrapper and sync path - cleanest surface, but
  breaks the developer maintenance lifecycle and existing tests.
- B. Keep all historical material and only remove runtime caches - safest
  mechanically, but leaves stale reference sources and confusing wording after
  native install becomes the normal user path.
- C. Remove `temp/` and runtime caches, update current docs/templates to make
  native launchers primary, and keep source checkout wrappers only as
  maintainer compatibility paths.

**Chosen**: C

**Rationale**:
- D-021 and D-022 already define the native release installer and native
  launcher as the cross-machine distribution contract.
- D-012 migrated the useful older pure-skill workflow ideas into
  `docs/changes/` packets, so keeping `temp/` tracked creates a second, stale
  reference source.
- Source checkout install/update/sync scripts are still the maintainer path and
  continue to exercise wrapper behavior in tests, so deleting them would be a
  behavior change rather than cleanup.

**Risks**:
- Historical docs still mention source checkout wrappers. Mitigation: leave
  historical D-XXX entries intact and update current SPEC/ARCHITECTURE/README
  plus the cleanup change packet.
- Removing `temp/` makes old comparison notes available only through git
  history. Mitigation: D-012 and the cleanup packet preserve why the useful
  pieces were adopted.

**Related code / docs**:
- SPEC §2 H, §3.3, §3.5
- `docs/changes/2026-06-12-cleanup-native-install-debris/`
- `docs/ARCHITECTURE.md`
- `README.md`
- `skill/templates/SPEC.md`
- `temp/`

---

## D-025 - Stop generating skill-local CLI wrappers during sync

**Date**: 2026-06-12

**Context**:
After the native installer became the normal distribution path, `sync-skill`
still generated `bin/docdev`, `bin/docdev.ps1`, and `bin/docdev.cmd` inside
installed skill directories. Those wrappers came from the older source-checkout
distribution model and made the skill directory look like another CLI entry.
The user wants normal usage to be the `docdev` CLI/native launcher path.

**Options**:
- A. Keep generating skill-local wrappers - maximally compatible with older
  source-sync installs, but keeps the confusing second CLI entrypoint.
- B. Add an opt-in compatibility flag - preserves an escape hatch, but keeps the
  third wrapper category in the product surface.
- C. Stop generating skill-local wrappers entirely; keep only native launchers
  and source-checkout local wrappers.

**Chosen**: C

**Rationale**:
- D-022 already defines `docdev` on `PATH` and `~/.local/bin/docdev` as the
  cross-machine agent CLI resolution contract.
- Removing skill-local wrapper generation makes `sync-skill` a pure skill
  content sync and prevents installed skill directories from becoming command
  dispatch surfaces.
- Source-checkout local wrappers remain useful for maintainers running
  unreleased source; native release launchers remain the user-facing CLI entry.

**Risks**:
- Old installed skill directories may still contain `bin/docdev*` until they are
  force-synced or refreshed through `docdev update --sync-skill`. Mitigation:
  the replacement sync path deletes marked targets before copying the skill.
- Historical decisions and roadmap steps still mention skill-local wrappers.
  Mitigation: preserve history and update current docs plus this decision.

**Related code / docs**:
- SPEC §2 H, §3.3, §3.5, §3.7
- `docs/changes/2026-06-12-sync-skill-without-local-wrappers/`
- `src/docs_driven_dev/cli.py`
- `tests/test_cli.py`
- `skill/SKILL.md`

## D-026 - Step 6d - Split CLI internals into lightweight modules

**Date**: 2026-06-13

**Context**:
`src/docs_driven_dev/cli.py` has reached roughly 940 lines and combines
config/path resolution, templates, change packets, audit, status, decision
skeletons, skill sync, doctor, native update dispatch, and argparse. That was
appropriate for the v0.1 bootstrap, but release/update/audit work is now the
active growth area and needs clearer module boundaries.

**Options**:
- A. Keep a single `cli.py` - minimal churn, but future Windows, signing, JSON
  status/doctor, and release features keep accumulating in one file.
- B. Introduce a larger command framework - more extensible, but too much
  architecture for the current stdlib-only CLI and likely to disturb behavior.
- C. Keep `docs_driven_dev.cli` as the public entrypoint and compatibility
  layer, while moving existing responsibilities into lightweight internal
  modules.

**Chosen**: C

**Rationale**:
- The native launcher and source wrappers can keep invoking
  `python -m docs_driven_dev.cli`.
- Internal modules make future work easier to place without adding dependencies
  or changing the command surface.
- A compatibility layer lets existing tests and local helper imports keep
  working while more precise tests patch the real implementation module.

**Risks**:
- Re-exported helpers from `cli.py` may look like a supported public API.
  Mitigation: document `cli.py` as a compatibility entrypoint; design a formal
  public Python API separately if it becomes necessary.
- Moving functions can introduce circular imports. Mitigation: keep shared
  constants/path helpers and data models in dependency-light modules.

**Related code / docs**:
- SPEC §2 Z, §5.1, §7 #10
- ARCHITECTURE §2, §3.0
- ROADMAP Step 6d
- `docs/changes/2026-06-13-split-cli-modules/`
- `src/docs_driven_dev/`
- `tests/test_cli.py`

## D-027 - Step 6e - Sync skill by default during native update

**Date**: 2026-06-13

**Context**:
The original native update design made skill sync an explicit `--sync-skill`
opt-in to avoid hidden writes to multiple agent homes. In practice, a release
can update CLI behavior, `skill/SKILL.md`, templates, and references together.
If `docdev update` refreshes only the launcher/current release while installed
skills remain old, agents may keep following stale workflow instructions.

**Options**:
- A. Keep `--sync-skill` as opt-in - smallest default side effect, but makes
  normal updates prone to CLI/skill drift.
- B. Sync skill targets by default during native install/update, with
  `--no-sync-skill` as the explicit opt-out.
- C. Sync only when the installed manifest version changes - more precise, but
  requires additional local state and edge-case handling.

**Chosen**: B

**Rationale**:
- The common user intent for `docdev update` is to update the whole release
  experience, including the skill an agent reads before calling the CLI.
- `--no-sync-skill` keeps a low-side-effect path for restricted environments,
  CI, or manual diagnostics.
- The existing D-025 sync contract still prevents skill-local wrappers from
  returning; default sync only copies skill content and marker files.

**Risks**:
- Default update now writes to configured Codex/Cursor/agents/Claude skill
  homes. Mitigation: document `--no-sync-skill` and keep sync target overrides.
- Already published releases keep the old default until a new version is
  published. Mitigation: record Step 6e and release in the next bump.

**Related code / docs**:
- SPEC §2 X, §3.4, §4, §7 #11
- ARCHITECTURE §3.9, §6
- ROADMAP Step 6e
- `docs/changes/2026-06-13-sync-skill-on-native-update/`
- `src/docs_driven_dev/commands.py`
- `src/docs_driven_dev/release.py`
- `scripts/install_remote.sh`
- `scripts/install_remote.ps1`

---

## D-028 - Step 6g - Add a confirmed native uninstall command

**Date**: 2026-06-13

**Context**:
Native install/update is now the normal cross-machine distribution path, and
v0.1.5 syncs skill targets by default. Users who validate install behavior on a
fresh machine need a repeatable way to remove only docdev-owned files before
installing again.

**Options**:
- A. Document manual `rm` commands only - smallest implementation, but easy to
  mistype and cannot encode marker/symlink safety checks.
- B. Add standalone uninstall shell scripts - familiar for install flows, but
  duplicates path logic and would need Unix/Windows variants.
- C. Add `docdev uninstall` with `--dry-run`, required `--yes`, and ownership
  checks for synced skill targets.

**Chosen**: C

**Rationale**:
- Uninstall is deterministic filesystem work, so it belongs in the CLI rather
  than the skill.
- A built-in command can reuse `DOCDEV_INSTALL_ROOT`, `DOCDEV_BIN_DIR`, and
  `DOCDEV_<TARGET>_*` path contracts already used by install/update/sync.
- Requiring `--yes` for deletion and skipping unmarked skill directories keeps
  the new command useful for smoke tests without making broad deletes easy.

**Risks**:
- Some manually copied `docs-driven-dev` skill directories may remain if they
  lack `.docdev-skill-source`. Mitigation: skip by default and report the path.
- Windows deletion of files from the currently running release may need real
  machine validation. Mitigation: keep the first implementation stdlib-only and
  document Windows as an install/update framework until verified.

**Related code / docs**:
- SPEC §2, §3.3, §3.4, §4, §7
- ARCHITECTURE §2, §3.10, §6
- ROADMAP Step 6g
- `docs/changes/2026-06-13-native-uninstall-command/`
- `src/docs_driven_dev/commands.py`
- `src/docs_driven_dev/release.py`

---

## D-029 - Step 6i - Use installer-owned Windows command entrypoint, not npm-first

**Date**: 2026-06-15

**Context**:
Windows release install currently writes `docdev.ps1` but does not make
`docdev -v` available as a normal command. The user wants a GitHub latest
install/update flow similar in spirit to `lark-cli`, but without making npm a
dependency. On Windows, a bare command requires a PATH-visible executable entry
such as `docdev.exe` or `docdev.cmd`; an environment variable alone is not
enough.

**Options**:
- A. Publish npm-first and rely on npm-generated command shims - strong Windows
  command ergonomics, but requires Node/npm and changes the distribution model.
- B. Generate `docdev.cmd` and `docdev.ps1` from the PowerShell remote
  installer, and add the native bin dir to User PATH by default - keeps the
  GitHub Releases model and makes `docdev -v` work for users.
- C. Build a Windows `docdev.exe` release artifact now - closest to lark-cli's
  binary model, but requires a Windows binary build/release/signing workflow.

**Chosen**: B

**Rationale**:
- The user explicitly prefers GitHub download/install/update over npm.
- The current release system already has manifest, checksum, current-pointer
  activation, `docdev update`, and uninstall ownership checks.
- A generated `docdev.cmd` is an installer-owned command entrypoint, not a
  user-maintained alias or profile function.
- Keeping `docdev.exe` as a later enhancement avoids expanding this fix into a
  full binary packaging/signing project.

**Risks**:
- `docdev.cmd` still depends on `python` being available on Windows. Mitigation:
  keep the current Python release contract and track `py`/self-contained exe as
  future real-machine feedback.
- User PATH updates may not affect an already-open parent terminal. Mitigation:
  update current `$env:Path` when possible and document reopening the terminal.
- Some managed Windows environments may block PATH mutation. Mitigation: provide
  `-NoModifyPath` and keep direct launcher paths.

**Related code / docs**:
- SPEC §2 AB, §3.3, §3.4, §4, §7 #13
- ARCHITECTURE §3.8, §3.9, §5, §6
- ROADMAP Step 6i
- `docs/changes/2026-06-15-windows-bare-command-install/`
- `scripts/install_remote.ps1`
- `src/docs_driven_dev/release.py`
- `tests/test_cli.py`

---

## D-030 - Step 6i - Publish Windows command installer after non-Windows verification

**Date**: 2026-06-15

**Context**:
The Windows bare command contract changes PowerShell installer behavior, but
the current release workstation is macOS. Unit tests and package inspection can
verify the generated installer text, update dispatch, manifest packaging, and
Unix public install path, but they cannot prove a fresh Windows terminal picks
up User PATH and `docdev.cmd` exactly as intended. The user asked to proceed
with publishing after accepting the GitHub-first, no-npm plan.

**Options**:
- A. Block `v0.1.7` until a Windows machine or CI runner completes live
  install/update smoke - strongest verification, but delays the accepted fix.
- B. Publish `v0.1.7` after unit, audit, package, local simulated install, and
  public latest smoke, while recording Windows live smoke as a post-release
  real-machine verification item.
- C. Remove the Windows PATH change before release - avoids unverified Windows
  behavior, but fails the requested `docdev -v` command experience.

**Chosen**: B

**Rationale**:
- The published artifact still includes checksum verification, manifest-based
  install, and the existing release rollback shape.
- Static tests cover the Windows-specific script contract, including
  `docdev.cmd`, User PATH mutation, `-NoModifyPath`, and platform update
  dispatch.
- Recording the live Windows smoke gap keeps the release honest without
  pretending macOS can validate Windows terminal behavior.

**Risks**:
- A Windows-only syntax or PATH edge case may appear after release. Mitigation:
  keep the live smoke item open and treat real-machine feedback as the next
  patch trigger.
- Public latest smoke is Unix-like only from this workstation. Mitigation:
  separate public install verification from Windows shell verification in the
  change packet.

**Related code / docs**:
- ROADMAP Step 6i
- `docs/changes/2026-06-15-windows-bare-command-install/`
- `scripts/install_remote.ps1`
- `src/docs_driven_dev/release.py`
- `tests/test_cli.py`

---

## D-031 - Step 6j - Patch Windows installer follow-up before larger packaging changes

**Date**: 2026-06-15

**Context**:
The first Windows live smoke of the published `v0.1.7` remote installer
confirmed the core bare-command goal: after install and terminal refresh,
`docdev` is usable from Windows. The same smoke found two narrower defects:
the installer passed `sync-skill --targets codex,cursor,agents,claude` without
quoting the comma-separated target value, causing PowerShell to forward extra
arguments; and the PATH write path needs clearer write-after-read diagnostics
because this Codex execution path did not observe the persisted PATH entry
until it was repaired manually.

**Options**:
- A. Treat the smoke as fully successful because the user can now run `docdev` -
  acknowledges the main outcome, but leaves the default skill sync failure in
  the published installer.
- B. Patch the PowerShell installer and diagnostics in a small follow-up
  release - fixes the real Windows feedback while preserving the current
  GitHub Release model.
- C. Stop and replace the Windows installer with npm shims or a `docdev.exe`
  binary immediately - may improve command ergonomics later, but expands a
  small live-smoke fix into a new distribution project.

**Chosen**: B

**Rationale**:
- The failure is localized to installer invocation and diagnostics, not the
  release artifact, CLI command surface, or native launcher model.
- Quoting `--targets "codex,cursor,agents,claude"` matches the CLI contract and
  the Unix installer behavior.
- A small patch release can make the published Windows path honest before
  considering larger binary packaging work.

**Risks**:
- PATH persistence may be affected by the Codex process model rather than only
  the script. Mitigation: add explicit post-write verification and diagnostic
  output instead of assuming the parent terminal can be refreshed.
- Users who installed `v0.1.7` may still need to run
  `docdev sync-skill --targets all --force` manually until the follow-up is
  released. Mitigation: document the workaround in the Step 6i packet and
  publish the patch promptly.

**Related code / docs**:
- ROADMAP Step 6j
- `docs/changes/2026-06-15-windows-bare-command-install/`
- `scripts/install_remote.ps1`
- `src/docs_driven_dev/release.py`
- `tests/test_cli.py`

---

## D-032 - Step 6k - Configure UTF-8 in docdev-owned Windows entrypoints

**Date**: 2026-06-16

**Context**:
Windows users can now invoke `docdev` directly, but PowerShell/CMD sessions may
still start with a non-UTF-8 console or Python IO encoding. The resulting
mojibake appears before users can reasonably run a manual encoding command, and
before a Python-only fix could affect installer logs.

**Options**:
- A. Document manual `chcp 65001` / PowerShell profile setup - no code churn,
  but makes every Windows user carry the workaround.
- B. Set UTF-8 only in Python CLI startup - helps normal CLI output, but does
  not cover PowerShell installer/update logs emitted before Python starts.
- C. Configure UTF-8 in Windows PowerShell scripts and generated Windows
  launchers - covers installer startup, source maintenance, and normal
  `docdev` command execution while keeping the change process-local.

**Chosen**: C

**Rationale**:
- It fixes the earliest user-visible output point.
- It keeps encoding changes scoped to docdev-owned scripts and child Python
  processes instead of mutating profiles or system locale.
- The same generated launcher contract covers release installs and source
  checkout developer wrappers.

**Risks**:
- Some PowerShell hosts may reject console encoding mutation. Mitigation: make
  console mutation best-effort and still set `PYTHONUTF8` plus
  `PYTHONIOENCODING` for Python output.
- Static tests cannot prove every Windows terminal renders Chinese correctly.
  Mitigation: keep a Windows live smoke as release verification.

**Related code / docs**:
- ROADMAP Step 6k
- `docs/changes/2026-06-16-windows-utf8-output/`
- `scripts/install_remote.ps1`
- `scripts/install_cli.ps1`
- `scripts/install.ps1`
- `scripts/update_cli.ps1`
- `tests/test_cli.py`

---

## D-033 - Step 6m - Copy Claude skill target directly instead of symlinking to agents

**Date**: 2026-06-16

**Context**:
The original Claude sync model used `~/.claude/skills/docs-driven-dev` as a
symlink to the shared `~/.agents` target, with a Windows copy fallback when
symlink creation failed. Real update usage now shows the symlink branch itself
can surface confusing Claude-related errors during normal update/sync flows.
Codex, Cursor, and Agents already use direct copied skill directories.

**Options**:
- A. Keep the symlink-first model and improve fallback diagnostics - preserves
  the original shared-directory optimization, but keeps Claude on a distinct
  error-prone path.
- B. Make Claude use the same direct-copy replacement model as the other
  targets - removes symlink requirements and lets `--targets claude` work
  without syncing Agents first.

**Chosen**: B

**Rationale**:
- It removes platform and permission differences around symlink creation from
  the default update path.
- It makes all four sync targets follow the same marker, force-replacement,
  and stale-file cleanup contract.
- It avoids hidden coupling where a Claude-only sync first mutates the Agents
  target as an implementation detail.

**Risks**:
- Claude and Agents copies can drift if only one target is synced manually.
  Mitigation: default install/update continues syncing
  `codex,cursor,agents,claude`, and `docdev doctor` reports each target state.
- Existing machines may still have a legacy Claude symlink. Mitigation:
  `--force` sync unlinks and replaces it with a marked copy, while uninstall
  still treats symlink targets as docdev-owned cleanup candidates.

**Related code / docs**:
- SPEC §2 F/O, §3.7
- ARCHITECTURE §3.5, §7
- ROADMAP Step 6m
- `docs/changes/2026-06-16-claude-copy-sync/`
- `src/docs_driven_dev/sync.py`
- `tests/test_cli.py`

---

## D-034 - Step 6n - Publish Claude copy-sync fix after local release verification

**Date**: 2026-06-16

**Context**:
The Claude direct-copy sync fix affects the update path that Windows users
exercise through GitHub Releases. The current release workstation is not
Windows, but the user explicitly asked to commit, push, and publish this fix
after the source implementation and tests passed.

**Options**:
- A. Wait for another Windows live smoke before publishing - strongest
  platform proof, but delays the requested update path.
- B. Publish `v0.1.10` after unit tests, project audit, package inspection,
  local simulated install smoke, and public latest smoke - makes the fix
  available now while keeping Windows live update as follow-up verification.

**Chosen**: B

**Rationale**:
- The changed behavior is deterministic Python filesystem sync logic covered by
  unit tests, including Claude-only copy and legacy symlink force replacement.
- Local package/install smoke verifies the release artifact and launchers use
  the bumped version.
- Public latest smoke verifies the uploaded GitHub Release assets can be
  downloaded, checksum-verified, installed, and used for init/audit.

**Risks**:
- A Windows-specific installer or filesystem edge case may still appear after
  publication. Mitigation: keep real Windows update smoke as a post-release
  verification item and patch promptly if it reports a new defect.

**Related code / docs**:
- ROADMAP Step 6n
- `docs/changes/2026-06-16-claude-copy-sync/`
- `pyproject.toml`
- `src/docs_driven_dev/__init__.py`
- `scripts/package_release.sh`

---

## D-035 - Step 6p - Express CLI resolution as positive entrypoints

**Date**: 2026-06-18

**Context**:
The v0.1.11 skill guidance fixed the visible fallback warning by naming the old
skill-local wrapper paths as things agents should avoid. The user pointed out
that active skill instructions should describe the supported behavior instead
of spending attention on actions that are outside the model.

**Options**:
- A. Keep the explicit negative guard - preserves the clearest reference to the
  observed bug, but keeps deprecated paths in active skill guidance.
- B. Replace it with a positive entrypoint contract - the skill describes the
  supported PATH/native launcher resolution order and the install-unavailable
  diagnostic condition.

**Chosen**: B

**Rationale**:
- It keeps the skill focused on how to act now: use `docdev` on PATH or the
  documented native launcher fallback.
- It reduces the chance that models anchor on obsolete skill-local wrapper
  paths while following the skill.
- The behavior still matches D-025: `sync-skill` owns skill content, while CLI
  execution uses native/PATH launchers.

**Risks**:
- A separate resolver implementation could still hard-code obsolete probes.
  Mitigation: treat any recurrence as resolver behavior to fix directly rather
  than adding more negative wording to the skill.

**Related code / docs**:
- ROADMAP Step 6p
- `docs/changes/2026-06-18-suppress-skill-local-wrapper-warning/`
- `skill/SKILL.md`
- `docs/SPEC.md`
- `README.md`
- `tests/test_cli.py`

---

## D-036 - Step 6q - Publish positive skill guidance as v0.1.12

**Date**: 2026-06-18

**Context**:
After syncing the positive wording locally, the latest public release was still
`v0.1.11`, whose packaged skill contained the older negative wording. A future
`docdev update` or fresh install from latest could therefore overwrite the
local fix with the older skill text.

**Options**:
- A. Leave the wording fix source-only until the next functional release - less
  release churn, but latest install/update remains stale.
- B. Publish a small `v0.1.12` release for the wording fix after unit tests,
  audit, package inspection, and local packaged install smoke.

**Chosen**: B

**Rationale**:
- The change affects the installed skill, so the release artifact is the real
  distribution boundary.
- A small release keeps `docdev update` aligned with the current source and
  avoids reintroducing the exact wording the user asked to remove.
- Local packaged install smoke proves the artifact contains the new skill
  wording before publication.

**Risks**:
- This is a documentation/skill wording release with no new functional code.
  Mitigation: keep verification focused on version consistency, packaging,
  installed skill content, `init`, and `audit`.

**Related code / docs**:
- ROADMAP Step 6q
- `docs/changes/2026-06-18-suppress-skill-local-wrapper-warning/`
- `pyproject.toml`
- `src/docs_driven_dev/__init__.py`
- `skill/SKILL.md`

---

## D-037 - Step 6r - Keep subagent use as skill-level delegation guidance

**Date**: 2026-06-18

**Context**:
The user wants `docs-driven-dev` to guide agents toward a healthier split when
subagents are available: the main agent should stay focused on the global
docs-driven contract, while subagents can handle bounded local work.

**Options**:
- A. Add CLI orchestration for subagents - could make delegation more
  mechanical, but would move model/platform judgment into the deterministic
  CLI boundary.
- B. Add skill-level delegation guidance - keeps CLI deterministic and lets the
  main agent decide whether delegation fits the platform, task size, and risk.

**Chosen**: B

**Rationale**:
- The existing project boundary is skill = workflow/judgment and CLI =
  deterministic filesystem, numbering, audit, sync, release/install/update.
- Subagent availability and safe write scope vary by platform, so this belongs
  in the skill workflow rather than a fixed CLI command.
- The main agent remains responsible for SPEC invariants, scope,
  implementation gates, DECISIONS, final review, verification, and the final
  explanation to the user.

**Risks**:
- Some platforms may not expose subagents or may expose different permission
  models. Mitigation: phrase delegation as optional guidance and require
  explicit task slices, file scope, write permission, acceptance checks, and
  uncertainty in handoffs.

**Related code / docs**:
- ROADMAP Step 6r
- `docs/changes/2026-06-18-delegation-guidance/`
- `skill/SKILL.md`
- `docs/SPEC.md`
- `README.md`
- `tests/test_cli.py`

---

## D-038 - Step 6s - Publish delegation guidance as v0.1.13

**Date**: 2026-06-18

**Context**:
The delegation guidance is now present in source and local installed skill
targets. The user asked to commit, push, and publish it so fresh installs and
`docdev update` receive the same skill behavior.

**Options**:
- A. Commit source-only and wait for a later release - keeps release count down,
  but latest install/update would not include the new guidance.
- B. Publish a small `v0.1.13` release after tests, audit, packaging, and smoke
  verification - aligns the release artifact with the current source skill.

**Chosen**: B

**Rationale**:
- The user explicitly asked to publish the change.
- This change affects installed skill guidance, so the GitHub Release artifact
  is the durable distribution boundary.
- Local packaged smoke and public latest smoke can verify the guidance is
  present in synced skill targets before and after publication.

**Risks**:
- The release contains skill/docs guidance rather than functional CLI changes.
  Mitigation: keep verification focused on package integrity, version
  consistency, installed skill content, `init`, and `audit`.

**Related code / docs**:
- ROADMAP Step 6s
- `docs/changes/2026-06-18-delegation-guidance/`
- `pyproject.toml`
- `src/docs_driven_dev/__init__.py`
- `skill/SKILL.md`

---

## D-039 - Step 6t - Use abstract replacement wording in active guidance

**Date**: 2026-06-18

**Context**:
After the v0.1.13 release, another machine still saw agent output about an old
skill-directory Windows launcher path. Source inspection showed that active
sync guidance still named obsolete skill-local launcher paths as cleanup
examples, even though runtime CLI resolution had already moved to PATH/native
launcher entries.

**Options**:
- A. Keep naming old launcher paths in active cleanup guidance - historically
  precise, but it gives models a fresh path string to anchor on.
- B. Describe sync cleanup through current-target replacement semantics in
  active guidance, while leaving historical ROADMAP/DECISIONS entries intact.

**Chosen**: B

**Rationale**:
- Active guidance should tell agents what to do now: execute CLI through
  supported native/PATH entries and treat `sync-skill` as skill-content refresh.
- Current-target replacement is the durable behavior users need to understand;
  old path examples are historical evidence rather than operational guidance.
- Keeping history in ROADMAP/DECISIONS preserves traceability without putting
  obsolete path strings in the text agents are most likely to follow.

**Risks**:
- The abstract wording is less explicit about the exact legacy files removed in
  earlier migrations. Mitigation: historical decisions and roadmap steps remain
  searchable for migration archaeology.

**Related code / docs**:
- ROADMAP Step 6t
- `docs/changes/2026-06-18-remove-wrapper-residual-guidance/`
- `skill/SKILL.md`
- `docs/SPEC.md`
- `README.md`
- `tests/test_cli.py`

---

## D-040 - Step 6u - Publish active guidance cleanup as v0.1.14

**Date**: 2026-06-18

**Context**:
Step 6t removed obsolete skill-local launcher examples from active source and
local installed skill guidance. Other machines still need a published release
artifact before `docdev update` or fresh native install can receive the same
skill wording.

**Options**:
- A. Keep the cleanup source-only until a later functional release - fewer
  releases, but latest install/update remains stale for this exact issue.
- B. Publish a small `v0.1.14` release after tests, audit, packaging, and smoke
  verification - aligns latest install/update with source and local skill
  targets.

**Chosen**: B

**Rationale**:
- The user explicitly asked to submit, publish, and push the cleanup.
- Installed skill content is distributed through release artifacts, so
  source-only fixes do not help other machines running latest.
- A small release can verify package integrity, launcher version, install/init
  audit behavior, and installed skill wording without changing CLI semantics.

**Risks**:
- The release is primarily skill/docs guidance. Mitigation: keep verification
  focused on version consistency, packaging, local/public install smoke, and
  installed skill content.

**Related code / docs**:
- ROADMAP Step 6u
- `docs/changes/2026-06-18-remove-wrapper-residual-guidance/`
- `pyproject.toml`
- `src/docs_driven_dev/__init__.py`
- `skill/SKILL.md`

---

## D-041 - Step 6v - Keep active skill surface current-action only

**Date**: 2026-06-24

**Context**:
After the v0.1.14 cleanup, the user noticed that active skill guidance still
included maintenance details about command entrypoint migration, owned targets,
and cleanup behavior. Even when written as a correction, those details can
make agents focus on paths they should never inspect during normal use.

**Options**:
- A. Keep the maintenance details in active skill guidance - convenient for
  self-diagnosis, but it keeps implementation history in the text agents follow.
- B. Move maintenance details to source docs/tests/scripts and keep active skill
  guidance limited to current `docdev` commands and workflow boundaries - a
  cleaner user surface, with maintenance facts still traceable.

**Chosen**: B

**Rationale**:
- The skill is a procedural context for agents, so every extra implementation
  detail risks becoming an accidental action.
- Users and agents only need the stable command contract: `docdev` on PATH, the
  Unix native path when needed, and the Windows PowerShell fallback.
- SPEC, DECISIONS, ARCHITECTURE, tests, and scripts still preserve the install
  and cleanup implementation facts for maintainers.

**Risks**:
- Troubleshooting from only the skill text has less low-level detail.
  Mitigation: README and source docs remain available for maintainer workflows,
  and install/update logs still identify failed lifecycle steps.

**Related code / docs**:
- ROADMAP Step 6v
- `docs/changes/2026-06-24-skill-surface-hide-wrapper-history/`
- `skill/SKILL.md`
- `README.md`
- `tests/test_cli.py`

---

## D-042 - Step 6w - Keep source checkout install out of active skill

**Date**: 2026-06-24

**Context**:
After Step 6v, the active skill still contained a `Source Checkout Install`
section with maintainer commands and kept `Delegation Guidance` nested under
Workflow B. The user clarified that source checkout development installation is
not runtime skill guidance, and delegation should apply whenever a platform
supports bounded subagent slices.

**Options**:
- A. Keep source checkout installation and delegation placement as-is - useful
  for maintainers reading only the skill, but it exposes development mechanics
  and makes delegation look Workflow-B-specific.
- B. Remove source checkout installation from active skill, leave maintainer
  onboarding in README/source docs, and promote delegation to a top-level skill
  workflow section.

**Chosen**: B

**Rationale**:
- The skill should be the agent runtime decision layer, not the developer
  installation manual.
- Source checkout commands can anchor agents to repository maintenance paths
  during normal user tasks.
- Delegation is a cross-workflow judgment tool: the main agent keeps
  docs-driven ownership while subagents handle bounded slices when available.

**Risks**:
- A maintainer reading only the installed skill will not see source checkout
  setup commands. Mitigation: README and source docs keep maintainer onboarding
  instructions.

**Related code / docs**:
- ROADMAP Step 6w
- `docs/changes/2026-06-24-skill-surface-hide-wrapper-history/`
- `skill/SKILL.md`
- `tests/test_cli.py`

---

## D-043 - Step 6x - Trim active skill to runtime contract

**Date**: 2026-06-24

**Context**:
After removing obsolete entrypoint and development-install details, the active
skill was still about 338 lines and included low-frequency install, update,
uninstall, release, layout, and template guidance. The user asked whether it
should be made smaller, then approved a simplification pass.

**Options**:
- A. Keep the longer skill as a self-contained guide - easier for a reader who
  only opens `SKILL.md`, but it loads maintenance details into every runtime
  invocation.
- B. Keep active skill as a concise runtime contract, with install/release and
  maintainer manuals in README / source docs.

**Chosen**: B

**Rationale**:
- The skill should optimize for the agent's immediate action path: docs-first
  gates, CLI resolution, delegation, workflow selection, and verification.
- README and source-of-truth docs already preserve the lower-frequency install
  and release contracts.
- A line-budget test makes future growth intentional instead of accidental.

**Risks**:
- Some troubleshooting details are no longer visible in installed skill text.
  Mitigation: the skill points installation and maintenance details back to
  README / SPEC / DECISIONS, and tests keep those docs as the maintenance
  surface.

**Related code / docs**:
- ROADMAP Step 6x
- `docs/changes/2026-06-24-skill-surface-runtime-trim/`
- `skill/SKILL.md`
- `README.md`
- `tests/test_cli.py`

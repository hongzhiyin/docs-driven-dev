# ROADMAP - docs-driven-dev

> Source of truth for current progress.

## Current Progress

**Phase**: Phase 1 - portable skill + CLI bootstrap
**Current Step**: Step 5e complete; ready for Windows install retest

### Step Status

| Step | Scope | Status |
|---|---|---|
| 0 | Evaluate existing Cursor skill and choose architecture | Done |
| 1 | Create source project with minimal CLI, portable skill, scripts, and docs | Done |
| 2 | Migrate/sync installed skills and refine cross-agent packaging | Done |
| 3 | Expand audit quality checks based on real project usage | Done |
| 4 | Make CLI discoverable from arbitrary project sessions | Done |
| 4a | Adopt latest skill-cli-kit metadata and update lifecycle | Done |
| 4b | Reduce source Quick Start to one command | Done |
| 4c | Clarify skill-mediated multi-project CLI usage | Done |
| 4d | Document fresh-machine install and agent usage path | Done |
| 4e | Simplify fresh-machine install command name | Done |
| 5 | Add per-requirement change packets without weakening project docs | Done |
| 5a | Add Windows PowerShell install entrypoints | Done |
| 5b | Fix Windows PowerShell install argument forwarding | Done |
| 5c | Make Windows skill sync complete after install starts running | Done |
| 5d | Add install/update step logs for remote failure diagnosis | Done |
| 5e | Add configurable skill target paths for non-default Windows agent homes | Done |

---

## Step 0 - Evaluate existing Cursor skill

**Goal**: Decide whether docs-driven-dev should remain a single Cursor skill or
become a portable skill plus CLI project.

**Tasks**:
- [x] Read existing Cursor skill and templates.
- [x] Identify hard-coded Cursor path and manual copy operations.
- [x] Compare with existing portable skill + CLI pattern.
- [x] Choose a small CLI boundary.

**Acceptance**:
1. The target architecture has a clear skill/CLI boundary.
2. The file placement rule for generated docs is explicit.
3. Sync targets include Codex, Cursor, Claude, and shared agents.

---

## Step 1 - Create portable source project

**Goal**: Land a usable initial project that can be opened in a fresh session
for continued optimization.

**Tasks**:
- [x] Add `docdev` CLI with init, audit, status, new-decision, sync-skill, and doctor.
- [x] Add portable `skill/SKILL.md`, templates, examples reference, and OpenAI metadata.
- [x] Add install/sync/check scripts.
- [x] Add project docs and README/AGENTS handoff.
- [x] Run CLI tests and project audit.

**Acceptance**:
1. `python3 -m unittest discover -s tests` passes.
2. `docdev audit <project>` returns no errors.
3. `docdev doctor` can locate the source skill and templates.

---

## Step 2 - Migrate installed skills

**Goal**: Make this source checkout the single editable source and sync it to
the agent homes the user actually uses.

**Tasks**:
- [x] Run `./scripts/install_cli.sh` in the final checkout.
- [x] Run `./scripts/sync_skill.sh --targets codex,cursor,agents,claude --force`.
- [x] Verify `~/.cursor/skills/docs-driven-dev` no longer has stale root `examples.md`.
- [x] Verify Claude target is a symlink to `~/.agents/skills/docs-driven-dev`.
- [x] Run `./scripts/check_install.sh`.

**Acceptance**:
1. Codex, Cursor, and Claude can all discover the same skill content.
2. Re-running sync without `--force` works after markers are present.
3. Existing unrelated skills are untouched.

---

## Step 3 - Expand audit checks

**Goal**: Add checks only after real usage reveals which mistakes are common.

**Tasks**:
- [x] Detect README Documentation Map drift more precisely.
- [x] Detect SPEC decision rows with empty choices.
- [x] Detect D-XXX entries missing options/chosen/risks.
- [x] Add fixture tests for malformed docs.

**Acceptance**:
1. New checks catch real failure modes without false-positive noise.
2. Audit still stays stdlib-only and fast.

---

## Step 4 - Cross-project CLI discovery

**Goal**: Let agents use docs-driven-dev from other project directories without
requiring `docdev` on shell `PATH` or a pre-set `DOCDEV_PROJECT_DIR`.

**Tasks**:
- [x] Generate a skill-local `bin/docdev` wrapper during `sync-skill`.
- [x] Update the skill CLI resolution order to prefer PATH, then skill-local
  wrapper, then `DOCDEV_PROJECT_DIR`.
- [x] Add a fixture test for the generated installed-skill wrapper.
- [x] Document the trade-off in SPEC, ARCHITECTURE, and DECISIONS.

**Acceptance**:
1. A copied installed skill contains an executable `bin/docdev`.
2. The wrapper points back to the source checkout and runs the stdlib CLI.
3. Fresh tests and project audit pass with no findings.

---

## Step 4a - Skill-cli-kit metadata and update lifecycle

**Goal**: Align this mature source checkout with the latest portable
skill-backed CLI conventions without changing the user-facing `docdev` command
surface.

**Tasks**:
- [x] Declare the required `docdev` CLI bin and help command in skill metadata.
- [x] Add a project-local `scripts/update_cli.sh` lifecycle wrapper.
- [x] Document the update lifecycle in SPEC, ARCHITECTURE, ROADMAP, DECISIONS,
  and README.
- [x] Re-sync installed skills after verification.

**Acceptance**:
1. `skillcli audit /Users/chihoyo/Project/docs-driven-dev --json` reports 0
   errors and 0 warnings.
2. `./scripts/update_cli.sh --targets codex,cursor,agents,claude --force` runs
   install, tests, check, sync, and check successfully.
3. `docdev audit /Users/chihoyo/Project/docs-driven-dev` reports no findings.

---

## Step 4b - One-command Quick Start

**Goal**: Let users bootstrap a target project from the source checkout with one
command instead of manually running install, doctor, init, and audit.

**Tasks**:
- [x] Add `scripts/setup_project.sh`.
- [x] Update README Quick Start to use the new script.
- [x] Document the lifecycle in SPEC, ARCHITECTURE, ROADMAP, and DECISIONS.
- [x] Add verification coverage for the script.

**Acceptance**:
1. `./scripts/setup_project.sh <tmp-project>` creates docs and writes
   `docs/_generated/docdev/audit.json`.
2. Custom `--docs-dir` values are audited consistently.
3. Unit tests and `docdev audit` pass with no findings.

---

## Step 4c - Skill-mediated multi-project usage

**Goal**: Make the README and source docs clear that `docdev` is used against
target project paths selected by the skill or agent, not against a unique
working directory.

**Tasks**:
- [x] Move README emphasis from source checkout Quick Start to usage model.
- [x] Document explicit target project path selection in SPEC and ARCHITECTURE.
- [x] Mark `scripts/setup_project.sh` as source-checkout convenience only.
- [x] Record the operational model decision.

**Acceptance**:
1. README shows `docdev init/audit/status /path/to/project` before source
   checkout scripts.
2. SPEC states that agents should pass explicit target project paths.
3. `docdev audit` reports no findings.

---

## Step 4d - Fresh-machine install path

**Goal**: Make it explicit that a cloned source repo can be installed and synced
with one lifecycle command, after which agents can use the installed skill-local
CLI wrapper against arbitrary target projects.

**Tasks**:
- [x] Document `update_cli.sh` as the fresh-machine install command.
- [x] Clarify that `setup_project.sh` is manual source-checkout target setup,
  not the required agent path.
- [x] Update SPEC, ARCHITECTURE, ROADMAP, DECISIONS, README, and SKILL.

**Acceptance**:
1. README shows the new-machine install command separately from source checkout
   target setup.
2. Skill docs tell agents to use installed `bin/docdev` wrappers when needed.
3. `docdev audit` reports no findings.

---

## Step 4e - Install command simplification

**Goal**: Make fresh-machine onboarding use a short install command consistent
with other CLI tools.

**Tasks**:
- [x] Add `scripts/install.sh` as the one-command install entrypoint.
- [x] Keep `scripts/update_cli.sh` as the underlying lifecycle implementation.
- [x] Update README, SPEC, ARCHITECTURE, ROADMAP, DECISIONS, and SKILL.
- [x] Add tests for install script defaults and override behavior.

**Acceptance**:
1. `./scripts/install.sh` installs, verifies, syncs default targets, and checks.
2. `./scripts/install.sh --targets codex --no-force` can delegate custom sync
   arguments.
3. Unit tests and `docdev audit` pass with no findings.

---

## Step 5 - Dual project/change mode

**Goal**: Absorb the older pure-skill workflow's requirement-level discipline
while preserving this project's project-level CLI/audit/install strengths.

**Tasks**:
- [x] Document the dual-mode contract in SPEC, ARCHITECTURE, DECISIONS, README,
  and SKILL.
- [x] Add `docdev new-change` for `docs/changes/YYYY-MM-DD-slug/` work packets.
- [x] Add change-packet templates with research log, implementation gates,
  open questions, and verification records.
- [x] Extend audit and status output for existing change packets.
- [x] Add tests for change creation, optional architecture handling, gate
  checks, and install/update compatibility.
- [x] Run unit tests, `docdev audit`, and the update lifecycle sync.

**Acceptance**:
1. `docdev new-change "sample-feature" <tmp-project>` creates a valid
   `docs/changes/<date>-sample-feature/` packet without requiring
   `ARCHITECTURE.md`.
2. `docdev audit <tmp-project>` checks both project docs and change packets,
   warning when a packet omits architecture without a ROADMAP reason or enters
   implementation without completed gates.
3. Project-level `docs/ARCHITECTURE.md` remains required for `docdev init` and
   root audit.
4. Unit tests, project audit, and installed-skill sync pass.

---

## Step 5a - Windows install entrypoints

**Goal**: Make fresh-machine onboarding work from Windows PowerShell without
requiring `.sh` file association or Git Bash.

**Tasks**:
- [x] Add PowerShell install, update, and local wrapper scripts.
- [x] Generate Windows installed-skill wrappers alongside the Unix wrapper.
- [x] Update README, SPEC, ARCHITECTURE, DECISIONS, and SKILL with Windows
  command guidance.
- [x] Add tests that protect the Windows script and wrapper contract.
- [x] Run unit tests, project audit, and update lifecycle sync.

**Acceptance**:
1. Windows users can run `.\scripts\install.ps1` from PowerShell after cloning
   the repo.
2. Synced skills include `bin/docdev`, `bin/docdev.ps1`, and `bin/docdev.cmd`.
3. README explains why `./scripts/install.sh` opens an app chooser in Windows
   terminals and gives the correct command.
4. Unit tests and `docdev audit` pass with no findings.

---

## Step 5b - Windows PowerShell install fix

**Goal**: Fix the real Windows failure where `install.ps1` forwarded the
default sync targets as an unbound positional argument.

**Tasks**:
- [x] Replace `$Args` splatting in `install.ps1` with explicit named parameter
  forwarding.
- [x] Document `Unblock-File` and process-scoped execution-policy bypass for
  unsigned PowerShell scripts.
- [x] Add regression coverage for the PowerShell forwarding contract.
- [x] Run unit tests, `docdev audit`, and update lifecycle sync.

**Acceptance**:
1. `install.ps1` invokes `update_cli.ps1` as
   `-Targets <targets> [-Force]`, not through `$Args` splatting.
2. README and SKILL explain how to handle Windows script signing/execution
   policy warnings.
3. Unit tests and `docdev audit` pass.

---

## Step 5c - Windows skill sync completion

**Goal**: Fix the next Windows install failure mode where the installer can
start but the skill does not refresh in every configured agent home.

**Tasks**:
- [x] Skip Unix shell-script execution tests on Windows while keeping them
  active on Unix shells.
- [x] Make Claude sync fall back to copying the skill when symlink creation is
  unavailable.
- [x] Document the sync fallback contract in SPEC, ARCHITECTURE, and
  DECISIONS.
- [x] Run unit tests, `docdev audit`, and update lifecycle sync.

**Acceptance**:
1. Windows update lifecycle can reach `docdev sync-skill` without failing on
   Unix-only `setup_project.sh` tests.
2. Claude sync failure to create a symlink does not prevent a usable installed
   skill copy from being written.
3. Unit tests and `docdev audit` pass.

---

## Step 5d - Install/update diagnostics

**Goal**: Make Windows and Unix install failures diagnosable from the user's
terminal output when the agent cannot see that machine directly.

**Tasks**:
- [x] Add stable `[docdev install]` and `[docdev update]` log prefixes.
- [x] Add numbered update lifecycle steps with start/done/failure messages.
- [x] Add regression tests that protect the log markers.
- [x] Document the diagnostic contract in SPEC, ARCHITECTURE, README, SKILL,
  and DECISIONS.
- [x] Run unit tests, `docdev audit`, and update lifecycle sync.

**Acceptance**:
1. Windows PowerShell output identifies which lifecycle step started, finished,
   or failed.
2. Unix install/update scripts expose comparable step logs.
3. A user can report the last `[docdev update] step N/M ...` line to localize
   the interruption.
4. Unit tests and `docdev audit` pass.

---

## Step 5e - Configurable skill target paths

**Goal**: Avoid hidden assumptions that every agent skill directory lives under
the default current-user home path on Windows or other machines.

**Tasks**:
- [x] Add `DOCDEV_<TARGET>_SKILL_DIR` exact target overrides.
- [x] Add `DOCDEV_<TARGET>_HOME` base directory overrides, preserving
  `CODEX_HOME` compatibility for Codex.
- [x] Print resolved sync target paths before copy/link operations.
- [x] Generate installed wrappers with OS-native source `src` paths.
- [x] Document how Windows PowerShell and persistent environment variables
  affect install/sync.
- [x] Run unit tests, `docdev audit`, and update lifecycle sync.

**Acceptance**:
1. `target_path_for` can resolve non-default Codex/Cursor/agents/Claude
   installed skill paths from environment variables.
2. `sync-skill` output shows the exact resolved target paths before syncing.
3. Generated Windows wrappers use a native `src` path instead of manual
   `/src` string concatenation.
4. Unit tests and `docdev audit` pass.

---

## Risk Register

| Risk | Impact | Mitigation |
|---|---|---|
| Agent skill formats drift | Sync may need per-agent adapters | Keep `skill/` generic and isolate metadata in `skill/agents/` |
| Audit becomes too opinionated | Users ignore noisy warnings | Add checks only from repeated real failure modes |
| CLI and skill duplicate guidance | Future edits drift | Keep policy in skill; keep mechanics in CLI; cite CLI commands in skill |

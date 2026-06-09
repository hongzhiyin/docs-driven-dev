# ROADMAP - docs-driven-dev

> Source of truth for current progress.

## Current Progress

**Phase**: Phase 1 - portable skill + CLI bootstrap
**Current Step**: Step 4e complete; ready for real-project usage feedback

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

## Risk Register

| Risk | Impact | Mitigation |
|---|---|---|
| Agent skill formats drift | Sync may need per-agent adapters | Keep `skill/` generic and isolate metadata in `skill/agents/` |
| Audit becomes too opinionated | Users ignore noisy warnings | Add checks only from repeated real failure modes |
| CLI and skill duplicate guidance | Future edits drift | Keep policy in skill; keep mechanics in CLI; cite CLI commands in skill |

# ROADMAP - docs-driven-dev

> Source of truth for current progress.

## Current Progress

**Phase**: Phase 1 - portable skill + CLI bootstrap
**Current Step**: Step 4a complete; ready for real-project usage feedback

### Step Status

| Step | Scope | Status |
|---|---|---|
| 0 | Evaluate existing Cursor skill and choose architecture | Done |
| 1 | Create source project with minimal CLI, portable skill, scripts, and docs | Done |
| 2 | Migrate/sync installed skills and refine cross-agent packaging | Done |
| 3 | Expand audit quality checks based on real project usage | Done |
| 4 | Make CLI discoverable from arbitrary project sessions | Done |
| 4a | Adopt latest skill-cli-kit metadata and update lifecycle | Done |

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

## Risk Register

| Risk | Impact | Mitigation |
|---|---|---|
| Agent skill formats drift | Sync may need per-agent adapters | Keep `skill/` generic and isolate metadata in `skill/agents/` |
| Audit becomes too opinionated | Users ignore noisy warnings | Add checks only from repeated real failure modes |
| CLI and skill duplicate guidance | Future edits drift | Keep policy in skill; keep mechanics in CLI; cite CLI commands in skill |

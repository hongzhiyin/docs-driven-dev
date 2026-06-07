# ROADMAP - docs-driven-dev

> Source of truth for current progress.

## Current Progress

**Phase**: Phase 1 - portable skill + CLI bootstrap
**Current Step**: Step 3 complete; ready for real-project usage feedback

### Step Status

| Step | Scope | Status |
|---|---|---|
| 0 | Evaluate existing Cursor skill and choose architecture | Done |
| 1 | Create source project with minimal CLI, portable skill, scripts, and docs | Done |
| 2 | Migrate/sync installed skills and refine cross-agent packaging | Done |
| 3 | Expand audit quality checks based on real project usage | Done |

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

## Risk Register

| Risk | Impact | Mitigation |
|---|---|---|
| Agent skill formats drift | Sync may need per-agent adapters | Keep `skill/` generic and isolate metadata in `skill/agents/` |
| Audit becomes too opinionated | Users ignore noisy warnings | Add checks only from repeated real failure modes |
| CLI and skill duplicate guidance | Future edits drift | Keep policy in skill; keep mechanics in CLI; cite CLI commands in skill |

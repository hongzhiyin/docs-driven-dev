# ROADMAP - docs-driven-dev

> Source of truth for current progress.

## Current Progress

**Phase**: Phase 1 - portable skill + CLI bootstrap
**Current Step**: Step 6q in progress; publishing v0.1.12 positive skill guidance release

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
| 5f | Clarify existing-code adoption before requirement change packets | Done |
| 5g | Clarify terminal PATH, CLI version, and sync replacement semantics | Done |
| 5h | Make explicit skill invocation mandatory and add small-fix fast path | Done |
| 6 | Add GitHub Releases / native installer distribution | Done |
| 6a | Clean native-install migration debris | Done |
| 6b | Remove skill-local CLI wrappers from sync | Done |
| 6c | Publish v0.1.4 native release | Done |
| 6d | Split CLI internals into lightweight modules | Done |
| 6e | Sync skill by default during native install/update | Done |
| 6f | Publish v0.1.5 native release | Done |
| 6g | Add native uninstall command | Done |
| 6h | Publish v0.1.6 native release | Done |
| 6i | Add Windows bare command native install contract | Done |
| 6j | Patch Windows installer live-smoke follow-up findings | Done |
| 6k | Fix Windows UTF-8 output for PowerShell/CMD entrypoints | Done |
| 6l | Publish v0.1.9 Windows UTF-8 output release | Done |
| 6m | Copy Claude skill target directly instead of symlinking to Agents | Done |
| 6n | Publish v0.1.10 Claude direct-copy sync release | Done |
| 6o | Publish v0.1.11 skill-local wrapper warning release | Done |
| 6p | Rewrite active CLI resolution guidance as positive entrypoints | Done |
| 6q | Publish v0.1.12 positive skill guidance release | In Progress |

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
with one lifecycle command. Historical note: the original Step 4d skill-local
CLI wrapper outcome was superseded by D-022 and D-025; agents now use `docdev`
or the native launcher.

**Tasks**:
- [x] Document `update_cli.sh` as the fresh-machine install command.
- [x] Clarify that `setup_project.sh` is manual source-checkout target setup,
  not the required agent path.
- [x] Update SPEC, ARCHITECTURE, ROADMAP, DECISIONS, README, and SKILL.

**Acceptance**:
1. README shows the new-machine install command separately from source checkout
   target setup.
2. Historical acceptance was installed `bin/docdev` wrappers; superseded by
   D-022 / D-025 in favor of `docdev` or the native launcher.
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
- [x] Print resolved sync target paths before sync operations.
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

## Step 5f - Existing-code adoption flow

**Goal**: Prevent agents from treating an existing code project without
docs-driven root docs as blocked when the user asks for a requirement change.

**Tasks**:
- [x] Document the adopt-then-change sequence in SPEC, README, and SKILL.
- [x] Clarify that `docs/changes/...` packets should not stand alone without
  root project docs.
- [x] Add regression coverage that protects the skill guidance.
- [x] Run unit tests, `docdev audit`, and installed-skill sync.

**Acceptance**:
1. The skill tells agents to run `docdev init <project>` first when an existing
   code project has no `docs/SPEC.md`, then create a change packet.
2. The docs distinguish "existing codebase" from "already docs-driven
   project".
3. Unit tests and `docdev audit` pass.

---

## Step 5g - CLI PATH and sync replacement contract

**Goal**: Remove ambiguity after fresh-machine install: direct terminal use does
not require global `docdev`, agents use skill-local wrappers, and refreshed
skill targets are replaced rather than merged.

**Tasks**:
- [x] Add `docdev -v` / `docdev --version`.
- [x] Document that install does not mutate the user's global shell `PATH`.
- [x] Document direct terminal wrapper commands for Unix and Windows.
- [x] Document that marked or force-synced skill targets are whole-directory
  replacements, with old paths outside the current target set left untouched.
- [x] Add regression coverage for version output, docs wording, and stale-file
  removal during marked-target refresh.

**Acceptance**:
1. `docdev --version` prints the CLI version.
2. README and SKILL explain why `docdev` may not be recognized in a normal
   terminal after install and which wrapper to use.
3. Tests prove stale files inside a marked installed skill target do not remain
   after refresh.

---

## Step 5h - Explicit invocation and small-fix path

**Goal**: Prevent agents from treating an explicitly named `docs-driven-dev`
skill as optional methodology, while avoiding excessive workflow weight for
narrow bug fixes.

**Tasks**:
- [x] Add an invocation contract that requires one skill workflow when the user
  explicitly names `docs-driven-dev`.
- [x] Add `Workflow B0 - Small Existing-Project Fix` before the broader
  existing-project workflow.
- [x] Define the minimal docs expected for a narrow bug fix.
- [x] Clarify that direct code edits are not sufficient after explicit skill
  invocation unless the user forbids docs and chooses to proceed outside the
  skill.
- [x] Add regression coverage for the invocation contract and B0 wording.

**Acceptance**:
1. SKILL states that reading the skill and coding directly is not sufficient
   when `docs-driven-dev` is explicitly named.
2. SKILL has a B0 workflow for narrow fixes that still creates/updates docs
   artifacts before code.
3. Unit tests and `docdev audit` pass.

---

## Step 6 - Native installer distribution

**Goal**: Let users install and update `docdev` from GitHub Releases style
artifacts without cloning the source checkout or configuring
`DOCDEV_PROJECT_DIR`.

**Tasks**:
- [x] Create `docs/changes/2026-06-11-native-installer-distribution/` with
  SPEC / ROADMAP / DECISIONS / ARCHITECTURE.
- [x] Record D-021 for GitHub Releases / native installer before npm.
- [x] Update README, SPEC, ARCHITECTURE, ROADMAP, and SKILL contracts.
- [x] Add `scripts/package_release.sh` for tarball, checksum, and manifest.
- [x] Add Unix remote installer and native update path.
- [x] Add Windows PowerShell installer framework.
- [x] Add tests and local smoke checks for package/install/update.

**Acceptance**:
1. Local release packaging emits artifact, checksum, and manifest without
   polluting source-of-truth docs.
2. A local simulated release install can run `docdev --version`,
   `docdev doctor`, `docdev init <tmp>`, and `docdev audit <tmp>` through the
   generated launcher.
3. Checksum mismatch prevents activation of a release.
4. README / SPEC / ARCHITECTURE / SKILL distinguish native user install from
   source checkout developer maintenance.
5. Unit tests and `docdev audit /Users/chihoyo/Project/docs-driven-dev` pass.

---

## Step 6a - Native install debris cleanup

**Goal**: Remove old scratch/reference material and clarify that source
checkout wrappers are developer maintenance compatibility, not the normal
cross-machine agent path.

**Tasks**:
- [x] Create `docs/changes/2026-06-12-cleanup-native-install-debris/`.
- [x] Record D-024 for deleting old scratch while keeping source maintenance
  scripts.
- [x] Delete tracked `temp/` reference material and Python cache directories.
- [x] Update README, SPEC, ARCHITECTURE, and template wording to keep native
  launcher first.
- [x] Run tests, doctor, audit, and commit cleanup.

**Acceptance**:
1. `temp/` and Python cache directories no longer remain in the source tree.
2. Current docs/templates do not present source checkout wrappers as the normal
   cross-machine fallback.
3. Unit tests, `docdev doctor`, and `docdev audit` pass.

---

## Step 6b - CLI-first skill sync

**Goal**: Make `docdev sync-skill` synchronize only skill content, leaving CLI
execution to `docdev` on `PATH` or the native launcher.

**Tasks**:
- [x] Create `docs/changes/2026-06-12-sync-skill-without-local-wrappers/`.
- [x] Record D-025 for removing skill-local CLI wrapper generation.
- [x] Remove skill-local wrapper generation from `copy_skill()`.
- [x] Update tests and docs to match CLI-first sync behavior.
- [x] Run source update/sync so installed skill targets drop old `bin/docdev*`.
- [x] Run tests, doctor, audit, and commit cleanup.

**Acceptance**:
1. New or refreshed skill targets do not contain `bin/docdev`,
   `bin/docdev.ps1`, or `bin/docdev.cmd`.
2. Source checkout local wrappers and native launcher remain available.
3. Unit tests, `docdev doctor`, and `docdev audit` pass.

---

## Step 6c - v0.1.4 native release

**Goal**: Publish the CLI-first `sync-skill` behavior through GitHub Releases
so native installs no longer generate skill-local `bin/docdev*` wrappers.

**Tasks**:
- [x] Bump `pyproject.toml`, `src/docs_driven_dev/__init__.py`, and CLI
  `VERSION` to `0.1.4`.
- [x] Run tests and project audit.
- [x] Package release assets.
- [x] Run local simulated install smoke.
- [x] Tag and publish GitHub Release `v0.1.4`.
- [x] Run public latest install/update smoke.
- [x] Update real local native install to `0.1.4`.

**Acceptance**:
1. Release assets include artifact, checksum, manifest, and installer scripts.
2. Local and public smoke launchers report `docdev 0.1.4`.
3. `docdev update --sync-skill` on v0.1.4 keeps installed skill targets free of
   `bin/docdev*` wrappers.
4. Unit tests, `docdev doctor`, and project audit pass.

---

## Step 6d - CLI module split

**Goal**: Keep the `docdev` command surface stable while moving the 940-line
`cli.py` internals into responsibility-focused modules.

**Tasks**:
- [x] Create `docs/changes/2026-06-13-split-cli-modules/` with architecture.
- [x] Record D-026 for keeping a thin `cli.py` compatibility entrypoint.
- [x] Split path/model, template/change, audit/status/decision, sync/doctor,
  release update, and argparse dispatch into lightweight modules.
- [x] Update tests for the new internal patch points.
- [x] Run unit tests, entrypoint smoke, and project audit.

**Acceptance**:
1. `python -m docs_driven_dev.cli` and native/source launchers keep working.
2. `cli.py` is a thin entrypoint/re-export layer; core logic lives in smaller
   modules.
3. Unit tests and `docdev audit` pass.

---

## Step 6e - Native update skill sync default

**Goal**: Make native install/update refresh skill targets by default so agent
workflow instructions stay aligned with the active CLI release.

**Tasks**:
- [x] Create `docs/changes/2026-06-13-sync-skill-on-native-update/` with
  architecture.
- [x] Record D-027 for default sync plus explicit no-sync opt-out.
- [x] Update `docdev update`, Unix installer, and PowerShell installer.
- [x] Update README, SPEC, ARCHITECTURE, ROADMAP, SKILL, and tests.
- [x] Run tests, entrypoint smoke, and project audit.

**Acceptance**:
1. `docdev update` defaults to skill sync and supports `--no-sync-skill`.
2. Remote installer defaults to skill sync and supports no-sync opt-out.
3. Unit tests and `docdev audit` pass.

---

## Step 6f - v0.1.5 native release

**Goal**: Publish the default skill-sync native update behavior through GitHub
Releases.

**Tasks**:
- [x] Bump `pyproject.toml` and `src/docs_driven_dev/__init__.py` to `0.1.5`.
- [x] Harden generated Unix launchers to use a direct `/bin/sh` shebang.
- [x] Run tests and project audit.
- [x] Package release assets.
- [x] Run local simulated install smoke, including default skill sync with temp homes.
- [x] Tag and publish GitHub Release `v0.1.5`.
- [x] Run public latest install/update smoke.

**Acceptance**:
1. Release assets include artifact, checksum, manifest, and installer scripts.
2. Local and public smoke launchers report `docdev 0.1.5`.
3. Default native install/update syncs skill targets unless `--no-sync-skill` is used.
4. Unit tests and project audit pass.

---

## Step 6g - Native uninstall command

**Goal**: Let users safely remove docdev-owned native install files and synced
skill targets so new-machine install smoke tests can be repeated.

**Tasks**:
- [x] Create `docs/changes/2026-06-13-native-uninstall-command/` with architecture.
- [x] Record D-028 for confirmed CLI uninstall.
- [x] Add `docdev uninstall` with `--dry-run`, `--yes`, and `--keep-skills`.
- [x] Harden `setup_project.sh` to invoke the source wrapper through `sh`.
- [x] Update README, SPEC, ARCHITECTURE, ROADMAP, SKILL, and tests.
- [x] Run unit tests, entrypoint smoke, uninstall smoke, and project audit.

**Acceptance**:
1. `docdev uninstall --dry-run` previews install root, launcher, and skill target actions without deleting.
2. `docdev uninstall --yes` removes temp native install root, launcher, and marked/symlink skill targets.
3. Unmarked skill directories are skipped by default.
4. Unit tests and `docdev audit` pass.

---

## Step 6h - v0.1.6 native release

**Goal**: Publish the native uninstall command through GitHub Releases so
fresh machines can install, update, and uninstall through the release path.

**Tasks**:
- [x] Bump `pyproject.toml` and `src/docs_driven_dev/__init__.py` to `0.1.6`.
- [x] Run tests, entrypoint smoke, project audit, and diff check.
- [x] Package release assets outside source-of-truth docs.
- [x] Run local simulated install/uninstall smoke with temp install, bin, and skill homes.
- [x] Tag and publish GitHub Release `v0.1.6`.
- [x] Run public latest install/uninstall smoke.
- [x] Record release verification in the native uninstall change packet.

**Acceptance**:
1. Release assets include artifact, checksum, manifest, and installer scripts.
2. Local and public smoke launchers report `docdev 0.1.6`.
3. Release launcher supports `docdev uninstall --dry-run` and `docdev uninstall --yes`.
4. Unit tests, project audit, and diff check pass.

---

## Step 6i - Windows bare command native install

**Goal**: Make Windows native release install/update behave like a normal CLI
install: after GitHub Release install, users can run `docdev -v` from a normal
PowerShell or CMD terminal without manually creating aliases.

**Tasks**:
- [x] Create `docs/changes/2026-06-15-windows-bare-command-install/` with architecture.
- [x] Record D-029 for installer-owned `docdev.cmd` plus User PATH instead of npm-first.
- [x] Update `scripts/install_remote.ps1` to generate `docdev.cmd`, preserve
  `docdev.ps1`, add User PATH by default, and support `-NoModifyPath`.
- [x] Update `docdev update` to dispatch to the PowerShell remote installer on Windows.
- [x] Update README, SPEC, ARCHITECTURE, ROADMAP, SKILL, and tests.
- [x] Run unit tests, package smoke, project audit, and record Windows live
  verification status in the change packet.
- [x] Bump release metadata to `0.1.7`.
- [x] Run local simulated install/init/audit/uninstall smoke from packaged
  `0.1.7` assets.
- [x] Tag and publish GitHub Release `v0.1.7`.
- [x] Run public latest install smoke for `v0.1.7`.
- [x] Update the local native install and synced skill targets to `v0.1.7`.

**Acceptance**:
1. Windows remote install writes `docdev.cmd` and `docdev.ps1` under the native bin dir.
2. Windows installer adds the native bin dir to User PATH by default, with a
   no-PATH opt-out.
3. `docdev update` uses `install_remote.ps1` on Windows and `install_remote.sh`
   on Unix-like hosts.
4. README/SKILL show GitHub latest install and `docdev -v` verification for Windows.
5. Unit tests, package smoke, local simulated install smoke, public latest
   smoke, and project audit pass; missing Windows live smoke is recorded as a
   post-release real-machine verification item because no Windows environment
   was available.

Post-release Windows live smoke on 2026-06-15 confirmed that `docdev` can be
used directly from a new Windows terminal after remote install, and that the
installed launcher can run `-v`, `doctor`, `status`, and `audit`. It also found
two follow-up items: the published PowerShell installer passed default
`sync-skill` targets as unquoted comma arguments, and PATH persistence needs a
stronger write-after-read diagnostic. The source installer now quotes the
targets argument; a follow-up release is needed to publish that fix.

---

## Step 6j - Windows installer live-smoke follow-up

**Goal**: Publish a small follow-up that incorporates Windows live-smoke
findings from the `v0.1.7` release path.

**Tasks**:
- [x] Record Windows `v0.1.7` live install results in the Step 6i packet.
- [x] Quote the PowerShell installer's default `sync-skill --targets` value.
- [x] Add regression coverage for the quoted targets contract.
- [x] Fix Windows unit-test baseline issues found while verifying the patch:
  Unix update dispatch tests now mock `posix`, Unix shell package smoke is
  skipped on Windows, and uninstall safety checks tolerate restricted home
  directory resolution.
- [x] Bump release metadata to `0.1.8`.
- [x] Harden User PATH write-after-read diagnostics in the Windows installer.
- [x] Run unit tests and project audit.
- [x] Package `0.1.8` release assets.
- [x] Run local Windows installer smoke from packaged `0.1.8` assets, including
  default sync with temporary skill homes.
- [x] Publish the `v0.1.8` patch release.
- [x] Re-run Windows remote install/update smoke from the published release.

**Acceptance**:
1. Remote Windows install no longer prints `unrecognized arguments: cursor agents claude`.
2. Installer output clearly distinguishes successful User PATH persistence,
   current-process PATH refresh, and parent-terminal staleness.
3. New PowerShell and CMD sessions can run `docdev -v` after install/update.
4. Unit tests and `docdev audit` pass.

Verification:
- `git push origin main` and `git push origin v0.1.8` completed.
- GitHub Release `v0.1.8` is published as non-draft, non-prerelease, with
  `docdev-0.1.8.tar.gz`, checksum, manifest, and both remote installers.
- Public latest Windows install smoke downloaded `docdev-0.1.8.tar.gz`, wrote
  `docdev.ps1` / `docdev.cmd`, ran default skill sync with temporary homes, and
  reported `docdev 0.1.8`.

---

## Step 6k - Windows UTF-8 output

**Goal**: Prevent Windows PowerShell/CMD users from seeing garbled Chinese
output at the start of install, update, source maintenance, or normal `docdev`
launcher execution.

**Tasks**:
- [x] Create `docs/changes/2026-06-16-windows-utf8-output/` with architecture.
- [x] Record D-032 for configuring UTF-8 in docdev-owned Windows entrypoints
  rather than requiring user profile/code-page setup.
- [x] Update PowerShell entry scripts and generated PowerShell/CMD launchers.
- [x] Add static regression tests for UTF-8 setup.
- [x] Run unit tests and project audit.

**Acceptance**:
1. Windows PowerShell scripts configure UTF-8 console/Python IO before logs or
   Python CLI execution.
2. Generated `docdev.ps1` and `docdev.cmd` launchers configure UTF-8 before
   running `docs_driven_dev.cli`.
3. Unit tests and `docdev audit` pass.

Verification:
- `python3 -m unittest discover -s tests` passed with 38 tests.
- `PYTHONPATH=src python3 -m docs_driven_dev.cli audit /Users/chihoyo/Project/docs-driven-dev` reported `No findings`.
- Real Windows terminal rendering still needs release/live-smoke verification before claiming the fix is available through GitHub latest.

---

## Step 6l - v0.1.9 Windows UTF-8 output release

**Goal**: Publish the Windows UTF-8 output fix through GitHub Releases so
Windows users installing latest can receive the updated PowerShell/CMD entrypoints.

**Tasks**:
- [x] Bump release metadata to `0.1.9`.
- [x] Run unit tests and project audit.
- [x] Package release assets.
- [x] Run local simulated install smoke from packaged `0.1.9` assets.
- [x] Commit, tag, and push `v0.1.9`.
- [x] Publish GitHub Release `v0.1.9` as latest.

**Acceptance**:
1. Release assets include `docdev-0.1.9.tar.gz`, checksum, manifest, and both remote installers.
2. Local simulated install launcher reports `docdev 0.1.9`.
3. Unit tests and `docdev audit` pass.
4. Real Windows terminal rendering remains a post-release live-smoke item unless verified separately.

Verification:
- `python3 -m unittest discover -s tests` passed with 38 tests.
- `PYTHONPATH=src python3 -m docs_driven_dev.cli audit /Users/chihoyo/Project/docs-driven-dev` reported `No findings`.
- `./scripts/package_release.sh --out /private/tmp/docdev-release-assets-0.1.9` emitted `docdev-0.1.9.tar.gz`, checksum, manifest, and both remote installers.
- Local simulated install from `/private/tmp/docdev-release-assets-0.1.9` reported `docdev 0.1.9`; `docdev init` plus `docdev audit` passed on `/private/tmp/docdev-019-target.jz9xL4`.
- Commit `1e83e2d` was tagged as `v0.1.9`; `git push origin main` and `git push origin v0.1.9` completed.
- GitHub Release `v0.1.9` was published as latest: `https://github.com/hongzhiyin/docs-driven-dev/releases/tag/v0.1.9`.
- Public latest smoke installed `docdev-0.1.9.tar.gz` from GitHub, checksum passed, launcher reported `docdev 0.1.9`, and `docdev init` plus `docdev audit` passed on `/private/tmp/docdev-019-public-target.aExsJA`.
- Local native install was refreshed to `/Users/chihoyo/.local/share/docdev/releases/0.1.9`; `docdev doctor` confirmed Codex/Cursor/Agents/Claude skill targets were synced.
- Existing local `0.1.8` release had a CRLF `scripts/install_remote.sh`, so `/Users/chihoyo/.local/bin/docdev update --version 0.1.9` failed with `env: sh\r`. The local refresh used current source `./scripts/install_remote.sh --version 0.1.9`; the installed `0.1.9` release script is LF.

---

## Step 6m - Claude direct-copy skill sync

**Goal**: Make Claude skill sync behave like the other agent targets by copying
the source skill directly instead of creating a symlink to the Agents target.

**Tasks**:
- [x] Create `docs/changes/2026-06-16-claude-copy-sync/`.
- [x] Update SPEC, ARCHITECTURE, DECISIONS, README, and SKILL contracts.
- [x] Remove the Claude symlink-specific sync implementation.
- [x] Add tests for direct Claude copy and legacy symlink replacement.
- [x] Run unit tests and project audit.

**Acceptance**:
1. `docdev sync-skill --targets claude --force` copies `skill/` directly to
   the Claude target and does not sync Agents as a hidden prerequisite.
2. A legacy Claude symlink can be replaced by `copy_skill(..., force=True)`.
3. Unit tests and `docdev audit` pass.

Verification:
- `PYTHONPATH=src python3 -m unittest tests.test_cli.CliTests.test_claude_sync_copies_without_agents_dependency tests.test_cli.CliTests.test_copy_skill_replaces_legacy_claude_symlink_when_forced` passed.
- `python3 -m unittest discover -s tests` passed with 39 tests.
- `PYTHONPATH=src python3 -m docs_driven_dev.cli audit /Users/chihoyo/Project/docs-driven-dev` reported `No findings`.
- `rg -n "Claude should use|Claude uses a symlink|link Claude target|link_claude|symlink failed|syncing agents first|shared-agents symlink|copy fallback when" docs README.md skill src tests` found only tests, historical decisions, or this change packet's old-state notes.

---

## Step 6n - v0.1.10 Claude direct-copy sync release

**Goal**: Publish the Claude direct-copy sync fix through GitHub Releases so
Windows and other machines can receive it through `docdev update`.

**Tasks**:
- [x] Bump release metadata to `0.1.10`.
- [x] Run unit tests and project audit.
- [x] Package release assets.
- [x] Run local simulated install smoke from packaged `0.1.10` assets.
- [x] Commit, tag, and push `v0.1.10`.
- [x] Publish GitHub Release `v0.1.10` as latest.

**Acceptance**:
1. Release assets include `docdev-0.1.10.tar.gz`, checksum, manifest, and both
   remote installers.
2. Local simulated install launcher reports `docdev 0.1.10`.
3. Unit tests and `docdev audit` pass.
4. Public latest smoke can install `0.1.10` and run `docdev init` plus audit.
5. Real Windows update smoke remains a post-release verification unless
   verified separately.

Verification:
- `python3 -m unittest discover -s tests` passed with 39 tests.
- `PYTHONPATH=src python3 -m docs_driven_dev.cli audit /Users/chihoyo/Project/docs-driven-dev` reported `No findings`.
- `PYTHONPATH=src python3 -m docs_driven_dev.cli --version` reported `docdev 0.1.10`.
- `./scripts/package_release.sh --out /private/tmp/docdev-release-assets-0.1.10` emitted `docdev-0.1.10.tar.gz`, checksum, manifest, and both remote installers.
- Local simulated install from `/private/tmp/docdev-release-assets-0.1.10` reported `docdev 0.1.10`; `docdev init` plus `docdev audit` passed on `/private/tmp/docdev-010-local-smoke.UYg0zt/target`.
- Packaged sync smoke from `/private/tmp/docdev-release-assets-0.1.10` ran `sync-skill --targets claude --force` with isolated homes; Claude target was copied, marked, and not a symlink; Agents home was not created.
- Commit `4c6d127` was tagged as `v0.1.10`; `git push origin main` and `git push origin v0.1.10` completed.
- GitHub Release `v0.1.10` was published as latest: `https://github.com/hongzhiyin/docs-driven-dev/releases/tag/v0.1.10`.
- Public latest smoke installed `docdev-0.1.10.tar.gz` from GitHub, checksum passed, launcher reported `docdev 0.1.10`, and `docdev init` plus `docdev audit` passed on `/private/tmp/docdev-010-public-smoke.4JyUGM/target`.
- Local native install was refreshed to `/Users/chihoyo/.local/share/docdev/releases/0.1.10`; `/Users/chihoyo/.local/bin/docdev doctor` confirmed Codex/Cursor/Agents/Claude skill targets were installed.
- Local Claude target is now a copied, marked directory instead of a symlink: `/Users/chihoyo/.claude/skills/docs-driven-dev`.

---

## Step 6o - v0.1.11 skill-local wrapper warning release

**Goal**: Publish the skill guidance fix so agents stop reporting missing
skill-local `bin/docdev.cmd` as a fallback event when native launchers are
available.

**Tasks**:
- [x] Create `docs/changes/2026-06-18-suppress-skill-local-wrapper-warning/`.
- [x] Clarify `skill/SKILL.md`, README, and SPEC so agents do not probe or
  report missing `<skill-dir>/bin/docdev*` wrappers.
- [x] Add regression coverage for the skill guidance.
- [x] Bump release metadata to `0.1.11`.
- [x] Run unit tests and project audit.
- [x] Package release assets.
- [x] Run local simulated install smoke from packaged `0.1.11` assets.
- [x] Commit, tag, and push `v0.1.11`.
- [x] Publish GitHub Release `v0.1.11` as latest.
- [x] Update the local native install and synced skill targets to `0.1.11`.

**Acceptance**:
1. Release assets include `docdev-0.1.11.tar.gz`, checksum, manifest, and both
   remote installers.
2. Local simulated install launcher reports `docdev 0.1.11`.
3. Unit tests and `docdev audit` pass.
4. Public latest smoke can install `0.1.11` and run `docdev init` plus audit.
5. Local installed Codex/Cursor/Agents/Claude skill copies include the new
   no-probe instruction and still do not contain skill-local `bin/docdev*`
   wrappers.

Verification:
- `python3 -m unittest discover -s tests` passed with 39 tests.
- `PYTHONPATH=src python3 -m docs_driven_dev.cli audit /Users/chihoyo/Project/docs-driven-dev` reported `No findings`.
- `PYTHONPATH=src python3 -m docs_driven_dev.cli --version` reported `docdev 0.1.11`.
- `./scripts/package_release.sh --out /private/tmp/docdev-release-assets-0.1.11` emitted `docdev-0.1.11.tar.gz`, checksum, manifest, and both remote installers.
- Local simulated install from `/private/tmp/docdev-release-assets-0.1.11` reported `docdev 0.1.11`; `docdev init` plus `docdev audit` passed on `/private/tmp/docdev-011-local-smoke.Hk9iCk/target`.
- Packaged skill content contains the new no-probe instruction, and packaged skill sync content still has no `bin/docdev*` wrappers.
- Commit `11b6af1` was tagged as `v0.1.11`; `git push origin main` and `git push origin v0.1.11` completed.
- GitHub Release `v0.1.11` was published as latest: `https://github.com/hongzhiyin/docs-driven-dev/releases/tag/v0.1.11`.
- Public latest smoke installed `docdev-0.1.11.tar.gz` from GitHub, checksum passed, launcher reported `docdev 0.1.11`, and `docdev init` plus `docdev audit` passed on `/private/tmp/docdev-011-public-smoke.8pceoG/target`.
- Local native install was refreshed to `/Users/chihoyo/.local/share/docdev/releases/0.1.11`; `/Users/chihoyo/.local/bin/docdev --version` reports `docdev 0.1.11`, and `docdev doctor` confirms Codex/Cursor/Agents/Claude skill targets are installed.
- Installed Codex/Cursor/Agents/Claude `SKILL.md` files contain the new no-probe instruction, and installed skill targets still contain no `bin/docdev*` wrappers.

---

## Step 6p - Positive CLI resolution guidance

**Goal**: Keep the active skill guidance focused on the CLI entrypoints agents
should use: `docdev` on PATH and documented native launcher fallbacks.

**Tasks**:
- [x] Rewrite `skill/SKILL.md` CLI Resolution from a negative guard into a
  positive PATH/native launcher entrypoint contract.
- [x] Align README and SPEC wording with the same positive contract.
- [x] Update the regression test to protect the positive skill wording.
- [x] Record the wording trade-off in DECISIONS.
- [x] Refresh the local installed skill targets from source.

**Acceptance**:
1. Active `skill/SKILL.md`, README, and SPEC describe the supported CLI
   resolution entries without naming obsolete skill-local wrappers as runtime
   instructions.
2. Unit tests and `docdev audit` pass.
3. Installed Codex/Cursor/Agents/Claude skill copies contain the positive CLI
   resolution wording.

Verification:
- `PYTHONPATH=src python3 -m unittest tests.test_cli.CliTests.test_docs_explain_path_and_replacement_contract` passed.
- `PYTHONPATH=src python3 -m unittest discover -s tests` passed with 39 tests.
- `PYTHONPATH=src python3 -m docs_driven_dev.cli audit /Users/chihoyo/Project/docs-driven-dev` reported `No findings`.
- `./scripts/sync_skill.sh --targets codex,cursor,agents,claude --force` refreshed all four local skill targets.
- Installed Codex/Cursor/Agents/Claude `SKILL.md` files contain `CLI resolution 只使用上面列出的跨机器入口`.
- `find` over the installed skill targets for `*/bin/docdev*` produced no output.

---

## Step 6q - v0.1.12 positive skill guidance release

**Goal**: Publish the positive CLI resolution wording so `docdev update` and
fresh installs do not reintroduce the v0.1.11 negative wording.

**Tasks**:
- [x] Bump release metadata to `0.1.12`.
- [x] Run unit tests and project audit.
- [x] Package release assets.
- [x] Run local simulated install smoke from packaged `0.1.12` assets.
- [ ] Commit, tag, and push `v0.1.12`.
- [ ] Publish GitHub Release `v0.1.12` as latest.
- [ ] Run public latest smoke.
- [ ] Update the local native install and synced skill targets to `0.1.12`.

**Acceptance**:
1. Release assets include `docdev-0.1.12.tar.gz`, checksum, manifest, and both
   remote installers.
2. Local simulated install launcher reports `docdev 0.1.12`.
3. Unit tests and `docdev audit` pass.
4. Public latest smoke can install `0.1.12` and run `docdev init` plus audit.
5. Local installed Codex/Cursor/Agents/Claude skill copies include the positive
   CLI resolution wording.

Verification:
- `PYTHONPATH=src python3 -m docs_driven_dev.cli --version` reported `docdev 0.1.12`.
- `PYTHONPATH=src python3 -m unittest discover -s tests` passed with 39 tests.
- `PYTHONPATH=src python3 -m docs_driven_dev.cli audit /Users/chihoyo/Project/docs-driven-dev` reported `No findings`.
- `./scripts/package_release.sh --out /private/tmp/docdev-release-assets-0.1.12` emitted `docdev-0.1.12.tar.gz`, checksum, manifest, and both remote installers.
- Local simulated install from `/private/tmp/docdev-012-local-smoke.tgodXb` reported `docdev 0.1.12`; `docdev init` plus `docdev audit` passed, synced isolated skill targets contained `CLI resolution 只使用上面列出的跨机器入口`, and `find` for `*/bin/docdev*` produced no output.

---

## Risk Register

| Risk | Impact | Mitigation |
|---|---|---|
| Agent skill formats drift | Sync may need per-agent adapters | Keep `skill/` generic and isolate metadata in `skill/agents/` |
| Audit becomes too opinionated | Users ignore noisy warnings | Add checks only from repeated real failure modes |
| CLI and skill duplicate guidance | Future edits drift | Keep policy in skill; keep mechanics in CLI; cite CLI commands in skill |

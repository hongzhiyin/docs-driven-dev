# ROADMAP - docs-driven-dev

> Source of truth for current progress. Historical detail lives in
> `docs/changes/` and `docs/DECISIONS.md`; this file keeps the current state and
> near-term work legible.

## Current Progress

**Phase**: Phase 1 - portable skill + CLI bootstrap
**Current Step**: Step 6ac in progress; v0.1.18 release packaging verified

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
| 6q | Publish v0.1.12 positive skill guidance release | Done |
| 6r | Add optional subagent delegation guidance | Done |
| 6s | Publish v0.1.13 delegation guidance release | Done |
| 6t | Remove obsolete launcher residuals from active guidance | Done |
| 6u | Publish v0.1.14 active guidance cleanup release | Done |
| 6v | Hide historical entrypoint details from active skill surface | Done |
| 6w | Remove source checkout install from active skill and promote delegation guidance | Done |
| 6x | Trim active skill to concise runtime contract | Done |
| 6y | Publish v0.1.16 runtime skill trim release | Done |
| 6z | Add docs-health and trim current docs surface | Done |
| 6aa | Publish v0.1.17 docs-health release | Done |
| 6ab | Make docdev repository text English-only | Done |
| 6ac | Publish v0.1.18 English-only and single change-template release | In Progress |

## Historical Summary

| Range | Result | Evidence |
|---|---|---|
| 0-4e | Split the original skill into a portable source checkout with CLI, templates, audit, status, sync, install scripts, and multi-project usage docs | D-001 through D-011; `docs/changes/` packets before Step 5 |
| 5-5h | Added requirement change packets, Windows source maintenance scripts, install/update diagnostics, configurable skill homes, existing-code adoption, and explicit invocation rules | D-012 through D-020 |
| 6-6h | Added GitHub Releases/native installer distribution, module split, default skill sync on native update, and uninstall | D-021 through D-028 |
| 6i-6n | Added Windows bare-command install, UTF-8 launcher handling, and direct Claude copy sync; published v0.1.9 and v0.1.10 | D-029 through D-034 |
| 6o-6ac | Removed skill-local wrapper residue from active guidance, promoted delegation, trimmed active skill, added docs-health, published v0.1.17, made repository text English-only, and prepared the v0.1.18 release | D-035 through D-049 |

Detailed step verification was intentionally moved out of the current view. Use
the linked D-XXX records and requirement packets for historical evidence.

---

## Step 6y - v0.1.16 runtime skill trim release

**Goal**: Publish the active skill runtime trim so fresh installs and
`docdev update` receive the 187-line skill and current source-of-truth records.

**Tasks**:
- [x] Bump release metadata to `0.1.16`.
- [x] Run unit tests and project audit.
- [x] Package release assets.
- [x] Run local simulated install smoke from packaged `0.1.16` assets.
- [x] Commit, tag, and push `v0.1.16`.
- [x] Publish GitHub Release `v0.1.16` as latest.
- [x] Run public latest smoke.
- [x] Update the local native install and synced skill targets to `0.1.16`.

**Acceptance**:
1. Release assets include `docdev-0.1.16.tar.gz`, checksum, manifest, and both
   remote installers.
2. Local simulated install launcher reports `docdev 0.1.16`.
3. Unit tests and `docdev audit` pass.
4. Public latest smoke can install `0.1.16` and run `docdev init` plus audit.
5. Local installed Codex/Cursor/Agents/Claude skill copies are 187 lines and
   contain the runtime-trim guidance without launcher-path or legacy placeholder
   text.

**Verification**:
- 40 tests passed.
- Project audit returned no findings.
- GitHub Release:
  `https://github.com/hongzhiyin/docs-driven-dev/releases/tag/v0.1.16`.
- Public latest smoke installed `docdev-0.1.16.tar.gz`, verified checksum,
  ran version/init/audit, and confirmed packaged `SKILL.md` was 187 lines.
- Local `/Users/chihoyo/.local/bin/docdev` was refreshed to `docdev 0.1.16`,
  synced Codex/Cursor/Agents/Claude skill targets, and verified no forbidden
  wrapper/source-checkout terms in installed skill files.

---

## Step 6z - Docs maintenance health and surface trim

**Goal**: Productize periodic docs maintenance as deterministic report support,
then use it to keep this repository's current docs surface readable.

**Tasks**:
- [x] Create `docs/changes/2026-06-24-docs-maintenance-health/`.
- [x] Add `docdev docs-health <project>` with human, JSON, and write-report modes.
- [x] Update docs and skill guidance for the new report command.
- [x] Trim README to a user-first entry page.
- [x] Compress ROADMAP into current state, status table, historical summary, and recent/current step detail.
- [x] Run unit tests, `docs-health`, and project audit.

**Acceptance**:
1. Other projects can run `docdev docs-health <project>` to get reusable
   maintenance signals without automatic doc mutation.
2. Generated docs-health reports live under `<docs_dir>/_generated/docdev/`.
3. README and ROADMAP are shorter while still preserving install, agent usage,
   maintainer entrypoints, release evidence, and historical traceability.
4. DECISIONS remains append-only; no old D-XXX body is deleted.
5. Tests and `docdev audit` pass.

**Verification**:
- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests`
  ran 42 tests successfully.
- `PYTHONPATH=src python3 -m docs_driven_dev.cli audit
  /Users/chihoyo/Project/docs-driven-dev` returned no findings.
- `PYTHONPATH=src python3 -m docs_driven_dev.cli docs-health
  /Users/chihoyo/Project/docs-driven-dev --write-report` wrote
  `docs/_generated/docdev/docs-health.json`.
- README shrank from 297 to 127 lines. ROADMAP shrank from 1307 to 144 lines.
- Final docs-health signals no longer include `readme-long` or `roadmap-long`;
  remaining signals are expected historical-ledger/change-packet review prompts.

## Risk Register

| Risk | Impact | Mitigation |
|---|---|---|
| Docs-health thresholds feel subjective | Users may over-treat signals as hard rules | Keep them as review signals outside `audit` |
| ROADMAP history becomes harder to inspect | Maintainers may need old verification details | Keep D-XXX and change packets as historical evidence |
| Agent over-trims append-only docs | Loss of rationale | SPEC and docs-health both state that DECISIONS should use index/summary rather than deletion |

---

## Step 6aa - v0.1.17 docs-health release

**Goal**: Publish the reusable docs-health report command and docs surface trim
so fresh installs and `docdev update` receive the new maintenance capability.

**Tasks**:
- [x] Bump release metadata to `0.1.17`.
- [x] Run unit tests, project audit, and docs-health.
- [x] Package release assets.
- [x] Run local simulated install smoke from packaged `0.1.17` assets.
- [x] Commit, tag, and push `v0.1.17`.
- [x] Publish GitHub Release `v0.1.17` as latest.
- [x] Run public latest smoke including `docs-health`.
- [x] Update the local native install and synced skill targets to `0.1.17`.

**Acceptance**:
1. Release assets include `docdev-0.1.17.tar.gz`, checksum, manifest, and both
   remote installers.
2. Local simulated install launcher reports `docdev 0.1.17`.
3. Public latest smoke can run version, init, audit, and `docs-health`.
4. Local `/Users/chihoyo/.local/bin/docdev` reports `docdev 0.1.17`.
5. Installed skill targets include the docs-health guidance and still avoid old
   wrapper/source-checkout wording.

**Verification**:
- 42 tests passed with `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m
  unittest discover -s tests`.
- Source checkout audit returned no findings, and source checkout
  `docs-health --write-report` wrote `docs/_generated/docdev/docs-health.json`
  with only expected DECISIONS/source-doc/change-packet review signals.
- Packaged release assets in `/private/tmp/docdev-release-assets-0.1.17.LBzBuT`;
  manifest listed `docdev-0.1.17.tar.gz` with SHA-256
  `359771a3b68067a6180ea1ca691512e1000d136f80faf6c94c763a07ee18f29a`.
- Local file smoke in `/private/tmp/docdev-017-local-smoke.2f7avF` installed
  `docdev 0.1.17`, ran init/audit/docs-health, confirmed packaged `SKILL.md`
  was 189 lines, and found no old wrapper/cmd/source-checkout terms.
- Commit `1de8991`, tag `v0.1.17`, and the `main` branch were pushed to
  origin.
- GitHub Release:
  `https://github.com/hongzhiyin/docs-driven-dev/releases/tag/v0.1.17`.
- Public latest smoke in `/private/tmp/docdev-017-public-smoke.31pUXJ`
  installed the GitHub release, ran version/init/audit/docs-health, confirmed
  packaged `SKILL.md` was 189 lines, and found no old wrapper/cmd/source-checkout
  terms.
- Local native update refreshed `/Users/chihoyo/.local/bin/docdev` to
  `docdev 0.1.17`; `doctor` passed, repository `docs-health --write-report`
  ran successfully, Codex/Cursor/Agents/Claude skill targets were 189 lines,
  and no old wrapper/cmd/source-checkout terms were found in source or installed
  skill files.

---

## Step 6ab - English-only repository text

**Goal**: Make tracked docdev prose, runtime skill guidance, shipped
templates, CLI-generated skeletons, tests, and source docs use English
copy.

**Tasks**:
- [x] Create the scoped change packet.
- [x] Convert `skill/SKILL.md` to English-only runtime guidance.
- [x] Remove shipped Chinese change templates and make `new-change` use English templates by default.
- [x] Update CLI-generated skeletons and tests so they no longer contain visible Chinese copy.
- [x] Compact older archived change packets into English archive summaries.
- [x] Update root SPEC / ARCHITECTURE / ROADMAP / DECISIONS.
- [x] Run tests, audit, docs-health, and Chinese-residue scans.

**Acceptance**:
1. `docdev init`, `docdev new-change`, and `docdev new-decision` generate
   English-only scaffolds.
2. Tracked repository text has no Chinese characters across README, skill,
   templates, source, tests, root docs, and archived change packets.
3. Older archived `docs/changes/` packets remain discoverable as concise
   English archive summaries; exact pre-compaction wording stays in git
   history.
4. Tests and project audit pass.

**Verification**:
- `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests`
  ran 43 tests successfully.
- `PYTHONPATH=src python3 -m docs_driven_dev.cli audit
  /Users/chihoyo/Project/docs-driven-dev` returned no findings.
- `PYTHONPATH=src python3 -m docs_driven_dev.cli docs-health
  /Users/chihoyo/Project/docs-driven-dev --write-report` completed and wrote
  `docs/_generated/docdev/docs-health.json`.
- Source smoke in `/private/tmp/docdev-english-smoke.Mxx6zB/project` ran
  `init`, `new-change --with-architecture`, and `new-decision`; generated
  output had no Chinese-character matches.
- Repository-wide scan returned no matches:
  `rg -n "[\\p{Han}]" . --glob '!.git/**' --glob '!__pycache__/**' --glob '!*.pyc'`.
- `docdev sync-skill --source /Users/chihoyo/Project/docs-driven-dev/skill
  --targets codex,cursor,agents,claude --force` refreshed local skill targets;
  installed Codex/Cursor/Agents/Claude `SKILL.md` files are 217 lines and have
  no Chinese-character matches.
- `skill/SKILL.md` is 217 lines, under the 230-line runtime budget.

---

## Step 6ac - v0.1.18 English-only and single-template release

**Goal**: Publish the English-only repository cleanup and the single
`skill/templates/change/` template layout so fresh installs and `docdev update`
receive the simplified runtime surface.

**Tasks**:
- [x] Bump release metadata to `0.1.18`.
- [x] Run unit tests, project audit, docs-health, and residue scans.
- [x] Package release assets.
- [x] Run local simulated install smoke from packaged `0.1.18` assets.
- [ ] Commit, tag, and push `v0.1.18`.
- [ ] Publish GitHub Release `v0.1.18` as latest.
- [ ] Run public latest smoke.
- [ ] Update the local native install and synced skill targets to `0.1.18`.

**Acceptance**:
1. Release assets include `docdev-0.1.18.tar.gz`, checksum, manifest, and both
   remote installers.
2. Local simulated install launcher reports `docdev 0.1.18`.
3. Public latest smoke can run version, init, new-change, audit, and
   docs-health.
4. Local `/Users/chihoyo/.local/bin/docdev` reports `docdev 0.1.18`.
5. Source and installed skill targets have no Chinese characters and no
   language-specific change-template subdirectories.

**Verification**:
- 44 tests passed with `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m
  unittest discover -s tests`.
- Source checkout audit returned no findings, and source checkout
  `docs-health --write-report` wrote `docs/_generated/docdev/docs-health.json`
  with expected DECISIONS/source-doc/change-packet review signals.
- Repository-wide Chinese-character scan returned no matches.
- Legacy language-template path scan across source and installed skill targets
  returned no matches.
- Packaged release assets in `/private/tmp/docdev-release-assets-0.1.18.vyCByV`;
  manifest listed `docdev-0.1.18.tar.gz` with SHA-256
  `32cf5d222b7ce59fc62d47835cd98e20730538d0bca8a621bcc44893507478b8`.
- Local file smoke in `/private/tmp/docdev-018-local-smoke.ciniTc` installed
  `docdev 0.1.18`, ran init/new-change/audit/docs-health, confirmed the
  packaged single change-template layout, and found no Chinese-character or
  legacy language-template path matches.

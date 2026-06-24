# ROADMAP - <requirement name>

> Source of truth for requirement progress, research, gates, tasks, and verification.

## 0. Current Status

**Phase**: Completed
**Current Step**: Step 4 - Verified and recorded
**Architecture Omission Reason**: Not omitted; this packet includes ARCHITECTURE because CLI template selection changes.

## 1. Gates

### Pre-Implementation Gate

- [x] User goal is confirmed in one sentence
- [x] Scope and non-goals are written in SPEC
- [x] Existing implementation, call sites, tests, and config are researched
- [x] Key constraints / invariants are written in SPEC
- [x] Required DECISIONS entries are recorded or marked blocked
- [x] Implementation steps and verification are clear
- [x] User has confirmed the implementation direction

### Completion Gate

- [x] All implementation tasks are done or explicitly skipped
- [x] Acceptance criteria are verified one by one
- [x] Docs match the final implementation
- [x] Remaining risks and follow-ups are recorded

## 2. Research Log

| ID | Topic | Finding | Evidence / File | Conclusion |
|---|---|---|---|---|
| R-1 | Existing language selection | `new-change` has an old language option and a non-English default | `src/docs_driven_dev/commands.py` | Remove the option and default to English |
| R-2 | Shipped templates | The shipped skill contains a non-English change template set | `skill/templates/change/` | Delete the non-English template set |
| R-3 | Generated decisions | `new-decision` skeleton uses bilingual labels | `src/docs_driven_dev/audit.py` | Generate English-only skeletons |
| R-4 | Active skill | `skill/SKILL.md` includes Chinese descriptions/headings/body copy | `skill/SKILL.md` | Translate active guidance to English |
| R-5 | Historical packets | Older `docs/changes/` packets contain Chinese archive evidence | `docs/changes/` | Compact to English archive summaries |

---

## Step 0 - Create Work Packet

**Goal**: Create SPEC / ROADMAP / DECISIONS and decide whether ARCHITECTURE is needed.

**Tasks**:
- [x] Initialize packet docs
- [x] Record that ARCHITECTURE is needed

**Acceptance**:
1. The packet exists and future agents can see the current state.

## Step 1 - Record Contract

**Goal**: Make the repository-wide English-only scope explicit before implementation.

**Tasks**:
- [x] Update packet SPEC.
- [x] Update root SPEC with a new decision table row and invariant.
- [x] Add D-048 to root DECISIONS.

**Acceptance**:
1. Root docs define English-only repository text and the archived-packet
   compaction rule.

## Step 2 - Adjust CLI And Templates

**Goal**: Prevent new docdev-generated scaffolds from containing Chinese copy.

**Tasks**:
- [x] Remove the `new-change` language option.
- [x] Resolve English change templates directly.
- [x] Remove shipped Chinese change templates.
- [x] Convert `new-decision` skeleton to English.

**Acceptance**:
1. New generated change packets and decision skeletons are English-only.

## Step 3 - Convert Runtime Surface And Tests

**Goal**: Make active guidance and regression coverage English-only.

**Tasks**:
- [x] Translate `skill/SKILL.md` to English-only guidance.
- [x] Update tests for the English contract.
- [x] Add a repository-wide no-Chinese regression guard.

**Acceptance**:
1. Repository-wide scan finds no Chinese characters.

## Step 4 - Compact Archived Packets

**Goal**: Keep old change packets discoverable without retaining non-English tracked text.

**Tasks**:
- [x] Replace older packet docs with concise English archive summaries.
- [x] Keep packet slugs, dates, source-of-truth relationship, and git-history pointer.
- [x] Avoid adding archived maintenance detail to `skill/SKILL.md`.

**Acceptance**:
1. Archived change packets contain no Chinese characters.
2. Root docs remain the current behavior source of truth.

## Step 5 - Verify And Record

**Goal**: Prove the English-only repository contract and keep historical boundaries explicit.

**Tasks**:
- [x] Run unit tests.
- [x] Run project audit and docs-health.
- [x] Smoke-test generated project docs, change packet, and decision skeleton.
- [x] Scan repository text for Chinese characters.

**Acceptance**:
1. Tests and audit pass.
2. Generated smoke output and repository text have no Chinese-character matches.

## 3. Verification Records

| Acceptance | Method | Result | Notes |
|---|---|---|---|
| SPEC-1 | `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests` | Passed | 44 tests OK |
| SPEC-2 | `PYTHONPATH=src python3 -m docs_driven_dev.cli audit /Users/chihoyo/Project/docs-driven-dev` | Passed | No findings |
| SPEC-3 | `PYTHONPATH=src python3 -m docs_driven_dev.cli docs-health /Users/chihoyo/Project/docs-driven-dev --write-report` | Passed | Report written under `docs/_generated/docdev/` |
| SPEC-4 | Source smoke in `/private/tmp/docdev-english-smoke.Mxx6zB/project` | Passed | `init`, `new-change --with-architecture`, and `new-decision` generated English-only docs |
| SPEC-5 | `rg -n "[\\p{Han}]" . --glob '!.git/**' --glob '!__pycache__/**' --glob '!*.pyc'` | Passed | No matches |
| SPEC-6 | Installed skill sync and scan | Passed | Codex/Cursor/Agents/Claude targets refreshed to 217-line English `SKILL.md`; no Chinese-character matches |
| SPEC-7 | v0.1.18 local release smoke | Passed | Packaged release installed from local assets, generated a change packet, audit/docs-health passed, and residue scans returned no matches |

## 4. Risks And Follow-Ups

| ID | Risk / Follow-up | Impact | Handling |
|---|---|---|---|
| F-1 | Archived packet detail is compacted | Maintainers need git history for line-level old logs | Keep packet slugs and root decisions discoverable |
| F-2 | Published native release still points to v0.1.17 until a new release is cut | Other machines will not receive this cleanup via `docdev update` yet | Publish a patch release when requested |

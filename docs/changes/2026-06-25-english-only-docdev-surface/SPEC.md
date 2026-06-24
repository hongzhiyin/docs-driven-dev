# SPEC - <requirement name>

> Source of truth for what this requirement must satisfy.

## 0. Status

| Field | Value |
|---|---|
| Status | Completed |
| Source | User request: standardize all docdev repository text on English |
| Packet | `docs/changes/2026-06-25-english-only-docdev-surface/` |
| Last updated | 2026-06-25 |

## 1. One-Sentence Goal

Docdev users and agents get English-only repository text, runtime guidance,
shipped templates, and CLI-generated scaffolds so reusable project setup stays
portable across environments.

## 2. Scope

### 2.1 In Scope

- Convert active `skill/SKILL.md` to English-only guidance.
- Remove shipped Chinese change packet templates.
- Make `docdev new-change` use English templates by default without a language option.
- Make `docdev new-decision` generate English-only skeletons.
- Compact archived change packets into concise English summaries.
- Update tests and active source-of-truth docs to enforce the repository-wide English contract.

### 2.2 Out of Scope

- Do not preserve detailed archived logs inline when concise English summaries are enough.
- Do not remove parser compatibility that helps audit older packets, as long as
  compatibility text does not appear as visible shipped copy or generated output.
- Do not publish a release unless the user explicitly asks for the release flow.

## 3. Requirements

| ID | Requirement | Acceptance method | Status |
|---|---|---|---|
| R1 | Active skill guidance contains no Chinese characters | `rg` scan and unit test | Done |
| R2 | `docdev new-change` creates English packet docs by default | unit test / smoke command | Done |
| R3 | `docdev new-decision` appends an English skeleton | unit test / smoke command | Done |
| R4 | Shipped templates include no Chinese template files | `find` / `rg` scan | Done |
| R5 | Root SPEC, ARCHITECTURE, ROADMAP, and DECISIONS document the English-only repository contract | doc review and audit | Done |
| R6 | Archived change packets contain English archive summaries instead of visible Chinese text | repository scan | Done |

## 4. Constraints And Invariants

1. **#1**: Tracked docdev text, runtime skill guidance, shipped templates,
   CLI-generated skeletons, tests, README, and source-of-truth docs must not
   contain Chinese characters.
2. **#2**: Archived historical packets under `docs/changes/` remain
   discoverable as concise English summaries.
3. **#3**: Audit compatibility for older packet wording must not cause new
   generated output or active docs to contain non-English copy.

## 5. Acceptance Criteria

1. `rg -n "[\\p{Han}]" . --glob '!.git/**' --glob '!__pycache__/**' --glob '!*.pyc'` returns no matches.
2. `python3 -m unittest discover -s tests` passes.
3. `PYTHONPATH=src python3 -m docs_driven_dev.cli audit /Users/chihoyo/Project/docs-driven-dev` passes.
4. A temporary `docdev init`, `docdev new-change`, and `docdev new-decision`
   smoke shows English-only generated scaffolds.

## 6. Open Questions

| ID | Question | Current read | Blocks implementation |
|---|---|---|---|
| Q1 | Where should detailed old packet wording live? | Git history; tracked docs keep concise English archive summaries | no |

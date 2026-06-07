---
name: docs-driven-dev
description: >-
  Bootstrap, audit, and maintain projects that use docs-driven development:
  SPEC / ARCHITECTURE / ROADMAP / DECISIONS as source-of-truth documents,
  usually under `docs/`. Use when the user asks for doc-driven,
  documentation-first, spec-driven, 四件套文档, 决策日志, 不变式, D-XXX,
  Step/Phase planning, or when a project already has docs/SPEC.md,
  docs/ROADMAP.md, docs/ARCHITECTURE.md, and docs/DECISIONS.md.
---

# Docs-Driven Development

This skill keeps project intent, current shape, progress, and trade-offs in four
orthogonal documents. The agent uses the documents for judgment; the `docdev`
CLI handles repeatable filesystem, numbering, audit, and sync operations.

## File Contract

Default source-of-truth layout:

```text
docs/
  SPEC.md          # what should be true: rules, invariants, contracts
  ARCHITECTURE.md  # what exists: layers, modules, data flow, config
  ROADMAP.md       # where we are: Phase/Step status and acceptance
  DECISIONS.md     # why: monotonic D-XXX decision log
  _generated/docdev/
    audit.json     # optional machine-generated reports
```

Use `docs/` unless the project has `.docdev.toml` with `docs_dir = "..."`.
Generated reports must stay under `<docs_dir>/_generated/docdev/`; do not mix
audit output into the four source-of-truth files.

## CLI

Prefer deterministic helper commands when available:

```bash
docdev init /path/to/project
docdev audit /path/to/project --write-report
docdev status /path/to/project
docdev new-decision "Step N - trade-off title" /path/to/project
docdev sync-skill --targets codex,cursor,agents,claude --force
docdev doctor
```

If `docdev` is unavailable but `DOCDEV_PROJECT_DIR` points to this source
checkout:

```bash
DOCDEV_PROJECT_DIR="$DOCDEV_PROJECT_DIR" PYTHONPATH="$DOCDEV_PROJECT_DIR/src" \
  python3 -m docs_driven_dev.cli <command>
```

The CLI is allowed to copy templates, append the next D-XXX skeleton, audit
structure, and sync this skill. It does not choose product design, relax
invariants, or decide trade-offs for the user.

## Document Boundaries

| Doc | Answers | Refuses |
|---|---|---|
| `SPEC.md` | What should be true: invariants, commands, contracts, defaults | implementation details, history |
| `ARCHITECTURE.md` | What the project currently looks like: layers, modules, data flow, config | behaviour rules, plans |
| `ROADMAP.md` | Where the work is: Phase/Step list, current progress, acceptance | design rationale, abandoned options |
| `DECISIONS.md` | Why a trade-off was chosen: D-XXX, options, rationale, risks | current status, implementation prose |

Two mechanisms keep the method useful:

1. SPEC has numbered invariants like `**#1**`; never silently violate them.
2. ROADMAP Steps include acceptance criteria before implementation begins.

## Workflow A - Bootstrap

Use when `<docs_dir>/SPEC.md` does not exist, or the user explicitly asks to set
up docs-driven development.

1. Confirm the project goal in one sentence.
2. Run `docdev init <project>` to create the four templates, README pointer,
   AGENTS pointer, and generated report directory.
3. Fill SPEC §1 and SPEC §2 decision table with the user. Aim for 5-10 real
   decisions with concrete choices.
4. Add or refine at least one SPEC invariant before coding.
5. Add a ROADMAP Step 0 or Step 1 with acceptance criteria.
6. Add DECISIONS D-001 for the foundational trade-off.
7. Only stage or commit if the user explicitly asks.

If a decision is unknown, write `pending D-XXX` and continue. Bootstrap should
not freeze because one choice needs later research.

## Workflow B - Extend

Use when `<docs_dir>/SPEC.md` exists and the user wants a feature, refactor, or
behaviour change.

1. Read SPEC first, then ROADMAP, then DECISIONS/ARCHITECTURE as needed.
2. Align intent: state the problem, at-risk invariants, module surface, and
   acceptance criteria. Use the current agent's question tool if available; if
   not, ask 1-3 short direct questions.
3. Update SPEC for rule or contract changes before implementation.
4. Append a ROADMAP Step or sub-step with explicit acceptance criteria.
5. Implement in small increments. If reality forces a new choice, return to
   alignment and document the decision instead of silently patching.
6. Verify with the Step acceptance criteria. Run `docdev audit`.
7. Append or complete the relevant D-XXX entry and sync README status when the
   change is user-visible.

## ROADMAP Step Shape

```markdown
## Step N - <one-line goal>

**Goal**: <why now, one sentence>

**Tasks**:
- [ ] task 1
- [ ] task 2
- [ ] doc sync: SPEC §x.y / D-XXX / README

**Acceptance**:
1. user-observable test
2. typecheck / lint clean
3. invariant #N still holds
```

Split any Step that is larger than one day or has more than three acceptance
points into `Na`, `Nb`, or similarly small sub-steps.

## DECISIONS Rules

- D-XXX numbers are monotonic: do not reuse and do not skip.
- Reversing a decision means adding a new D-XXX and marking the old entry as
  superseded; do not rewrite the old conclusion.
- Each non-trivial decision should include at least three options, a chosen
  option, rationale, risks, and links to affected docs/code.

Use `docdev new-decision "<title>" <project>` to append the next skeleton.

## Anti-Patterns

- Coding first and trying to reconstruct intent afterward.
- Putting rationale in SPEC or current status in DECISIONS.
- Long prose in SPEC with no numbered invariants.
- ROADMAP entries that say only "do the thing" and omit acceptance.
- Generated reports or scratch notes placed beside the four source documents.

## Reference

Read `references/examples.md` only when you need concrete examples of a strong
decision table, invariant list, Step split, or D-XXX entry.

---
name: docs-driven-dev
description: >-
  Use docs-driven development to maintain a project with docs/SPEC.md,
  docs/ARCHITECTURE.md, docs/ROADMAP.md, and docs/DECISIONS.md as
  source-of-truth documents, plus docs/changes/ change packets for scoped
  requirements. Use when the user asks for docs-driven, documentation-first,
  spec-driven, research-before-code, source-of-truth docs, requirement work
  packets, decision logs, invariants, D-XXX records, Step/Phase planning, or
  when the project already has this docs structure.
metadata:
  requires:
    bins: ["docdev"]
  cliHelp: "docdev --help"
---

# Docs-Driven Development

This skill is the agent runtime contract: docs hold intent, structure, progress,
and trade-offs; the `docdev` CLI owns repeatable file generation, numbering,
audit, sync, install, and update mechanics.

## Invocation Contract

When the user explicitly names this skill, asks for docs-driven /
documentation-first / source-of-truth docs, or works in a project that already
uses this structure, follow one workflow below and create or update the needed
docs artifacts before changing production code. Reading `SKILL.md` once and
then coding directly is not enough. Do not silently downgrade an explicit
`docs-driven-dev` request into ad hoc research or direct coding, even for small
fixes.

## File Contract

Project source of truth:

```text
docs/
  SPEC.md          # what should be true
  ARCHITECTURE.md  # what exists
  ROADMAP.md       # where we are
  DECISIONS.md     # why
  _generated/docdev/
```

Requirement change packet:

```text
docs/changes/YYYY-MM-DD-slug/
  SPEC.md
  ROADMAP.md
  DECISIONS.md
  ARCHITECTURE.md  # optional; ROADMAP records the omission reason
```

Use `docs/` by default. Respect `.docdev.toml` `docs_dir` only when an existing
project explicitly configures it. Generated reports must stay under
`docs/_generated/docdev/`, not in the four source-of-truth docs.

## CLI Resolution

Always choose the target project explicitly. Treat the current working
directory as the target only when it is clearly the user's target project;
otherwise pass the project path the user named.

Resolve the CLI in this order:

1. `docdev <command>` if available on `PATH`.
2. Windows: `docdev <command>` in a fresh terminal.
3. If `docdev` is unavailable, ask the user to run or repair the native install.

Common commands:

```bash
docdev init /path/to/project
docdev new-change "feature-slug" /path/to/project
docdev audit /path/to/project --write-report
docdev status /path/to/project
docdev new-decision "Step N - trade-off title" /path/to/project
docdev docs-health /path/to/project --write-report
docdev sync-skill --targets codex,cursor,agents,claude --force
docdev doctor
```

`sync-skill` syncs workflow content. Agents execute the CLI through the
native/PATH entries above. The CLI does not make product decisions, relax SPEC
invariants, or choose trade-offs for the user.

## Install And Update Boundary

Install, update, uninstall, release, and maintainer install instructions belong
in README / SPEC / DECISIONS, not active skill runtime guidance. The runtime
rule here is only: use `docdev` or a documented native fallback for CLI work;
when the install is unavailable, ask the user to repair the install instead of
guessing alternate entries.

## Delegation Guidance

Delegation is a context and throughput tool. When the platform supports
subagents and the task has a clearly bounded slice, consider delegation first,
unless the task is too small, tool support is missing, or splitting would add
risk. Docs-driven ownership remains with the main agent.

The main agent owns user intent, SPEC invariants, scope, implementation gates,
DECISIONS, final diff review, verification, and the final explanation.

Subagents are useful for bounded read-only research, approved narrow
implementation slices, docs consistency checks, and test-failure diagnosis.

Handoffs should state objective, file scope, write permission, acceptance
checks, and invariants to preserve. Subagent responses should return changed
files or findings, tests, uncertainty, and judgment points for the main agent.
The main agent reviews before updating source-of-truth docs, verification
records, and the final response.

## Document Boundaries

| Doc | Answers | Refuses |
|---|---|---|
| `SPEC.md` | expected behavior, invariants, contracts | implementation details, history |
| `ARCHITECTURE.md` | modules, data flow, config, current structure | behavior rules, plans |
| `ROADMAP.md` | phase, step, tasks, acceptance, verification | design rationale |
| `DECISIONS.md` | D-XXX rationale, options, choice, risks | current status |

An existing codebase without the root four-doc set is an adoption case, not a
blocked case. Run `docdev init <project>` to create minimal durable root docs,
then run `docdev new-change "<slug>" <project>`. A lone `docs/changes/...`
packet must not become the project's only docs-driven artifact.

## Workflow A - Bootstrap

Use when `<docs_dir>/SPEC.md` does not exist, or when the user explicitly asks
to set up docs-driven development.

1. Confirm the project goal in one sentence.
2. Run `docdev init <project>`.
3. Fill SPEC sections 1 and 2 with 5-10 real decisions.
4. Add at least one SPEC invariant.
5. Add ROADMAP Step 0 or Step 1 with acceptance criteria.
6. Add DECISIONS D-001 for the foundational trade-off.
7. Stage or commit only when the user explicitly asks.

For existing codebases, keep Bootstrap lightweight: create durable root docs,
then enter Workflow B.

## Workflow B0 - Small Existing-Project Fix

Use when the user explicitly invokes `docs-driven-dev` and the request is a
narrow bug fix or small behavior change.

1. Do not skip docs; if root docs are missing, do minimal adoption first.
2. Run `docdev new-change "<slug>" <project>`.
3. Keep the packet minimal: SPEC has one expected behavior; ROADMAP has goal,
   touched files, acceptance checks, and verification; DECISIONS records only
   real trade-offs; ARCHITECTURE is omitted by default.
4. Treat explicit user language like "fix it" or "implement it" as
   implementation approval after the packet states scope and acceptance.
5. Implement the narrow fix, verify it, write back verification results, and
   run `docdev audit <project>`.

## Workflow B - Existing Project Requirement

Use for features, refactors, research tasks, or behavior changes in an existing
project.

1. If project-level SPEC is missing, first do lightweight adoption with Workflow A.
2. Read project SPEC, then ROADMAP; read DECISIONS and ARCHITECTURE as needed.
3. Restate the goal in one sentence and ask only the most important 1-3 questions.
4. Run `docdev new-change "<slug>" <project>`; add `--with-architecture` only
   when structural impact is already clear.
5. Research first, then design. Put findings in packet ROADMAP research log,
   behavior constraints in packet SPEC, and structure facts in packet ARCHITECTURE.
6. Stop at the implementation gate until goal, scope, non-goals, relevant code,
   open questions, steps, verification, and user approval are clear.
7. After approval, implement in small steps. If a new user-visible trade-off
   appears, update SPEC/DECISIONS and confirm it.
8. Verify every acceptance criterion, record results, run `docdev audit
   <project>`, and state remaining risks.

If research finds module, data-flow, lifecycle, persistence, public API, event,
config, migration, or cross-cutting impact, add packet ARCHITECTURE before
implementation.

## Workflow C - Project-Level Extend

Use when the user wants to change the durable project-level contract.

1. Read SPEC and ROADMAP; read DECISIONS / ARCHITECTURE as needed.
2. Align on problem, at-risk invariants, module surface, and acceptance criteria.
3. Update SPEC rules or contracts before implementation.
4. Append a ROADMAP Step / sub-step with acceptance criteria.
5. Implement in small steps; if reality forces a new choice, return to alignment
   and decision recording.
6. Verify against Step acceptance criteria and run `docdev audit`.
7. If the change is user-visible, add or complete the related D-XXX and sync
   README status.

## Decision And Verification Rules

- SPEC must have clear invariants; ROADMAP Steps must have acceptance criteria.
- D-XXX numbers are monotonic: do not reuse and do not skip.
- Each non-trivial decision includes options, chosen path, rationale, risks, and related files.
- When a change packet omits `ARCHITECTURE.md`, ROADMAP must record the omission reason.
- Before the final response, verify acceptance and write back verification results.
- Before periodic documentation trimming, run `docdev docs-health <project>`; the CLI gives signals, and agent judgment decides trim/archive actions.

## Anti-Patterns

- Coding first, then backfilling intent.
- Putting rationale in SPEC or current status in DECISIONS.
- Writing a ROADMAP that says only "do the thing" and has no acceptance criteria.
- Starting substantial production code before creating or updating the change packet.
- Hiding unresolved assumptions in code comments instead of SPEC open questions or DECISIONS.

## Reference

Read `references/examples.md` only when a strong example is needed.

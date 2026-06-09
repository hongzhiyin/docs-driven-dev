---
name: docs-driven-dev
description: >-
  Run documentation-driven development for existing projects and new project
  bootstraps with SPEC / ROADMAP / DECISIONS / optional ARCHITECTURE documents.
  Use when the user wants to add a new feature or requirement to an existing
  codebase only after discussion, project research, and an approved
  implementation plan; when they mention docs-driven development, spec-driven
  development, research-before-code, requirements clarification, feature docs,
  requirement work packet, SPEC, ROADMAP, DECISIONS, ARCHITECTURE, 决策日志,
  不变式, 文档驱动开发, 需求工作流, 简单描述需求后逐步澄清,
  or 调研充分后再实现.
---

# Docs-Driven Development

Use this skill to keep feature work anchored in documents before code changes
begin. The default target is an existing project where the user gives a rough
requirement, the agent researches the current implementation, iterates with the
user until the plan is clear, and only then starts implementation.

The method uses a per-requirement "work packet" directory containing:

- `SPEC.md`: what must be true for this requirement
- `ROADMAP.md`: where the work currently stands
- `DECISIONS.md`: why meaningful trade-offs were chosen
- `ARCHITECTURE.md`: optional, only when structure, data flow, contracts, or
  cross-module behavior need to be described

Keep important discoveries in the documents quickly. Do not rely on chat
history as the only memory, especially during long investigations.

## Document Language

Write all generated requirement documents in Simplified Chinese by default.
This includes `SPEC.md`, `ROADMAP.md`, `DECISIONS.md`, `ARCHITECTURE.md`,
research notes, open questions, acceptance criteria, risks, and verification
records.

Keep code identifiers, file paths, API names, config keys, class/function
names, branch names, commands, and error messages in their original spelling.
Use short Chinese explanations around them. Add an English term in parentheses
only when it improves precision, for example `验收标准（acceptance criteria）`.

Ask clarification questions in Chinese unless the user chooses another
language.

## Choose The Workflow

Use **Workflow A** for the common case: adding a requirement to an existing
project.

Use **Workflow B** only when the user explicitly wants to bootstrap a new
project or install project-wide docs from scratch.

If project-level docs already exist, read them first and place the new
requirement packet according to the existing convention.

## Document Boundaries

Each document answers one question:

| Doc | Answers | Avoids |
|---|---|---|
| `SPEC.md` | What should be true: goal, scope, requirements, acceptance, invariants | implementation detail, history |
| `ROADMAP.md` | Where the work is: research checklist, gates, tasks, verification status | trade-off rationale |
| `DECISIONS.md` | Why a choice was made: options, chosen path, rationale, risks | current progress |
| `ARCHITECTURE.md` | What the existing/proposed structure looks like: modules, flow, contracts | behavioral requirements |

When information feels like it belongs in two files, write the short rule in
`SPEC.md` and link to the deeper structural or decision record elsewhere.

## Workflow A: Existing Project New Requirement

### A.0 Intake

Start from the user's rough description, even if it is only 1-3 sentences.
Do not require the user to provide a full brief up front. Treat missing
background, scope, acceptance criteria, project paths, and non-goals as items
to discover through discussion and repository research.

The first answer should usually do three things:

1. Restate the suspected goal in one sentence.
2. Ask only the next 1-3 high-leverage questions.
3. Say that no production code will be changed until requirements and the
   implementation plan are confirmed.

Minimal trigger examples:

```text
Use docs-driven-dev. I want to add <rough feature description>.
```

```text
按 docs-driven-dev 来。需求：<一句话描述>。先调研和确认方案，不要直接写代码。
```

Good early questions:

- Who is the user or caller of this behavior?
- What is the observable outcome that proves the requirement is done?
- Which current workflow, screen, API, command, or config does this touch?
- Are there explicit non-goals or compatibility constraints?
- Is the user asking for investigation only, or investigation plus eventual
  implementation after approval?

Do not turn uncertainty into hidden assumptions. Put unresolved items in
`SPEC.md` "开放问题" and `ROADMAP.md` "阻塞 / 待确认".

### A.1 Create The Requirement Work Packet

Create one folder under the project root before substantial design work.

Default path:

```text
docs/changes/YYYY-MM-DD-<short-slug>/
```

If the repo already has a docs convention, follow it. If the user names a
folder, use that folder. Record the final path in `ROADMAP.md`.

Copy templates from this skill:

```text
templates/SPEC.md
templates/ROADMAP.md
templates/DECISIONS.md
templates/ARCHITECTURE.md
```

Always create `SPEC.md`, `ROADMAP.md`, and `DECISIONS.md`.

Create `ARCHITECTURE.md` only if one of these is true:

- new module boundary, service, screen, or data model
- changed data flow, lifecycle, state machine, or persistence
- public API / event / config contract changes
- cross-cutting behavior such as error handling, concurrency, caching, or
  migration
- the existing implementation is hard to explain without a structural map

If `ARCHITECTURE.md` is omitted, write the reason in `ROADMAP.md`. If later
research shows it is needed, add it before implementation.

### A.2 Research The Existing Project

Research before designing. Prefer repository instructions and project tools
over generic assumptions.

Minimum research checklist:

- Read `AGENTS.md`, README, existing docs, and nearby feature docs.
- Locate existing implementations, call sites, tests, configs, assets, and
  generated files relevant to the requirement.
- Identify local conventions: naming, file layout, dependency boundaries,
  testing style, error handling, logging, feature flags, localization, UI
  binding, data migrations.
- Write findings into `ROADMAP.md` "Research Log" with concrete file paths.
- Move behavioral constraints into `SPEC.md`.
- Move structural facts or proposed structure into `ARCHITECTURE.md` when it
  exists.
- Log non-obvious trade-offs in `DECISIONS.md`.

Tool guidance:

- Use IDE / language-aware search first for broad symbol and reference lookup
  when available.
- Use exact text search for narrow scans, generated-file inclusion choices,
  and count-sensitive questions.
- State whether generated files were included when it affects the conclusion.

Sub-agent guidance:

- Treat use of this workflow as standing permission to use bounded read-only
  sub-agent research when the environment and active platform rules allow it.
  Do not require the user to repeat this permission in every requirement.
- Use sub-agents to reduce main-context pressure during broad project research,
  especially when multiple independent areas must be inspected.
- Delegate bounded read-only research questions such as "find all existing
  implementations of X" or "compare tests around Y".
- Require sub-agents to return file paths, line references when possible,
  concise findings, and uncertainty.
- Consolidate their findings into the work packet; do not leave the final
  rationale only in sub-agent output.
- Do not delegate user-facing decisions, final implementation approval, or
  ambiguous product questions; keep those in the main conversation.

### A.3 Clarify And Design With The User

Iterate until the requirement is implementable. Keep questions concrete and
answerable. Prefer multiple short rounds over one giant questionnaire.

Before implementation, the documents must contain:

- `SPEC.md`: approved goal, scope, non-goals, requirements, acceptance
  criteria, and affected invariants / constraints
- `ROADMAP.md`: explicit implementation steps, verification plan, current
  status, and unresolved blockers
- `DECISIONS.md`: all meaningful trade-offs that influenced the plan
- `ARCHITECTURE.md` if needed: current-state snapshot plus proposed structure

Stop at an approval gate:

```text
Implementation Gate:
- Requirement is clear enough to implement.
- Affected existing code has been researched.
- Open questions are either answered or explicitly accepted as risks.
- ROADMAP has tasks and acceptance checks.
- User has confirmed the implementation plan.
```

Do not edit production code before this gate. Allowed before the gate:
read-only investigation, document edits, small throwaway probes, or generated
analysis files that the user explicitly accepts.

### A.4 Implement In Small Steps

Once the user confirms the plan, work through `ROADMAP.md` step by step.

During implementation:

- Update task status as steps start and finish.
- Keep code changes scoped to the confirmed plan.
- If implementation reveals a new constraint, pause the affected step, update
  docs, ask the user if the decision changes user-visible behavior, then
  continue.
- Add or update tests according to the risk and local project style.
- Update `SPEC.md` only for behavior or contract changes.
- Update `ARCHITECTURE.md` for module, flow, config, or data model changes.
- Append `DECISIONS.md` entries for real trade-offs. Do not invent decision
  entries for purely mechanical edits.

If a step grows beyond roughly one day of work, three acceptance checks, or
multiple ownership areas, split it into sub-steps.

### A.5 Verify And Close

Map verification back to `SPEC.md` acceptance criteria.

Closure checklist:

- All ROADMAP tasks are marked done, skipped with reason, or moved to future
  work.
- Each acceptance criterion has a verification result.
- Tests, typecheck, lint, or manual checks are recorded.
- DECISIONS has entries for non-trivial choices.
- ARCHITECTURE reflects the final structure if it exists.
- Remaining risks and follow-ups are explicit.
- Final answer to the user names the docs folder and verification status.

## Workflow B: Project-Wide Bootstrap

Use this when the user wants a project-level docs system rather than a
single-requirement packet.

Default path:

```text
docs/
```

Create the four docs from `templates/`, then fill them at project scope:

- `SPEC.md`: project goal, global rules, invariants, command / API contracts
- `ARCHITECTURE.md`: overall module map, data flow, process model, config
- `ROADMAP.md`: phases and current project progress
- `DECISIONS.md`: monotonic D-XXX decision log

Also add a short README or AGENTS pointer when the repo does not already tell
future agents where to start.

## Decision Log Rules

- Use monotonic `D-XXX` numbers inside each work packet.
- Prefer 2-3 real options. Do not pad a fake third option.
- Record the chosen option, concrete rationale, risks, and linked files.
- If a decision is reversed, add a new entry that supersedes the old one.
  Keep the original entry intact.
- Use `pending D-XXX` only when the roadmap can proceed without resolving it;
  otherwise treat it as a blocker.

## Anti-Patterns

1. Coding first and retrofitting documents later.
2. Asking the user a huge questionnaire before reading the project.
3. Treating docs as ceremony instead of a live memory of research and choices.
4. Hiding assumptions in code comments instead of SPEC / DECISIONS.
5. Letting sub-agent findings stay outside the docs.
6. Claiming "done" without mapping verification to acceptance criteria.
7. Editing ARCHITECTURE for every tiny leaf change when no structure changed.

## Optional Reference

`examples.md` contains historical project-level samples from an earlier app.
Read it only when you need concrete examples of SPEC tables, ROADMAP steps, or
D-XXX entries.

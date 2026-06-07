# Examples

Use this reference when the user asks what "good" looks like or when a project
needs examples for SPEC decisions, invariants, ROADMAP Step splitting, or D-XXX
entries.

## SPEC Decision Table

```markdown
| ID | Decision | Choice | Notes |
|---|---|---|---|
| A | Platform | Node 20 + TypeScript + pnpm | - |
| B | Agent backend | `@cursor/sdk` 1.0.x local mode | See D-001 |
| C | Lark integration | Self-owned app + WebSocket stream | - |
| D | Storage | SQLite (better-sqlite3) WAL | - |
| E | cwd model | One bot process / one cwd / global chdir lock | See D-002 |
| F | Default model | `claude-opus-4-7` | Revised by D-009 |
```

Good signs:
- Each row is a real choice, including version or mode when relevant.
- Notes point to DECISIONS instead of expanding rationale inline.
- Revisions point to later D-XXX entries while preserving history.

## SPEC Invariants

```markdown
1. **#1**: One chatId has at most one active run at a time.
2. **#2**: cwd cannot change after it is bound to a chatId.
3. **#3**: The process runs at most one local agent at a time.
4. **#6**: SessionRecord.baselineCommit is written only during cwd onboarding.
5. **#7**: audit_logs failures are logged but never fail the user run.
```

Good signs:
- Each invariant is one sentence.
- Later docs and decisions cite `#N`.
- Changing an invariant requires a new D-XXX.

## ROADMAP Step Split

When one Step is larger than one day or has more than three acceptance points,
split it:

```markdown
### Step 7a - `/status`
**Tasks**: render cwd / model / agent / baseline / HEAD / stats.
**Acceptance**: all fields render; git errors fall back to "?".

### Step 7b - `/commit <msg>` + `/revert` + `/diff`
**Tasks**: commands plus blob-fingerprint diff comparison.
**Acceptance**: commit does not move baseline; revert confirms twice; diff is accurate.

### Step 7c-1 - interactive card PoC
### Step 7c-2 - input box and confirmation
### Step 7c-3 - folded panels and multi-file chunks
```

Good signs:
- Each sub-step can be implemented, verified, and committed independently.
- A failure in one sub-step does not invalidate the others.

## D-XXX Entry

```markdown
## D-037 - Step 10 - run timeout uses merged signals

**Date**: 2026-05-XX

**Context**:
RUN_TIMEOUT_MS existed in config but no code read it, so a wedged agent could
block the session queue until process restart.

**Options**:
- A. Add setTimeout in orchestrator and abort the upstream signal - simple, but
  user cancellation and timeout become hard to distinguish.
- B. Add `armRunTimeout(upstream, ms, ctx)` with an inner controller and a local
  `timedOut` flag - keeps cancellation reasons clear.
- C. Put timeout logic inside each provider - repeats the same policy for every
  provider.

**Chosen**: B

**Rationale**:
- One inner controller handles both upstream cancel and timeout.
- Local `timedOut` preserves audit wording when transport drops signal.reason.
- Provider implementations stay small.

**Risks**:
- If SDK cancel hangs in the future, add a hard-dispose fallback after 30s.

**Related code / docs**:
- SPEC §3.7
- `src/orchestrator/timeout-guard.ts`
```

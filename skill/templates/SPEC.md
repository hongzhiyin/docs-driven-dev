# SPEC - <project name>

> Source of truth for expected behaviour.
>
> This file answers "what should be true". It does not describe implementation
> shape, progress, or rationale.

## 1. One-Sentence Goal

<Condense the project into one sentence. If this is hard, clarify the README
before filling the rest of the docs.>

## 2. Decision Table

> Capture the highest-leverage choices. Each row is a concrete decision, not a
> vague intention. Point detailed rationale to DECISIONS.md.

| ID | Decision | Choice | Notes |
|---|---|---|---|
| A | Runtime / platform | <example: Python 3.10+ CLI> | - |
| B | Main framework / SDK | <example: no runtime dependencies> | See D-001 |
| C | Storage | <example: local markdown files> | - |
| D | Distribution | <example: source checkout + wrapper script> | See D-XXX |
| E | <add more> | <add more> | |

## 3. Derived Rules

### 3.1 <Rule Group>

<Short rules or a small table. Keep implementation details in ARCHITECTURE.md.>

### 3.2 Commands

| Command | Purpose | Side effects |
|---|---|---|
| `<example>` | <one sentence> | <yes/no and where> |

## 4. Default Handling

| Scenario | Default behaviour |
|---|---|
| <example: missing optional config> | <example: use docs/> |
| <example: ambiguous user request> | <example: ask one short question> |

## 5. Module Contracts

### 5.1 <ModuleName>

```ts
interface ExampleModule {
  run(input: ExampleInput): Promise<ExampleResult>;
}
```

Constraints:
- Input domain:
- Output domain:
- Error categories:
- Related invariants:

## 6. Non-Goals

- <example: no cloud service in v1>
- <example: no hidden mutation outside the project folder>

## 7. Invariants

> Each `#N` is a high-voltage rule. To change one, add a new D-XXX and update
> dependent docs/code deliberately.

1. **#1**: <example: source-of-truth docs stay human-authored>
2. **#2**: <example: generated reports live only under docs/_generated/docdev>
3. **#3**: <add more>

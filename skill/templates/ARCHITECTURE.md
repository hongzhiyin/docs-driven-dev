# ARCHITECTURE - <project name>

> Source of truth for what currently exists.
>
> This file describes layers, modules, data flow, configuration, process model,
> and known implementation constraints. It does not declare behaviour rules,
> progress, or rationale.

## 1. Layer View

```text
<example:

User / Agent
  -> CLI or app entrypoint
  -> Core orchestration
  -> Filesystem / API adapters
>
```

## 2. Module Table

| Module | Path | Responsibility | Does not depend on |
|---|---|---|---|
| <ModuleA> | `<path>` | <one sentence> | <module/system> |
| <ModuleB> | `<path>` | <one sentence> | <module/system> |

## 3. Data Flow

```text
<example:
input command
  -> parse options
  -> load config
  -> update project files
  -> write report
>
```

## 4. Data Model

### 4.1 <ModelName>

```ts
interface ModelName {
  id: string;
}
```

Persistence:
- <file/table/cache location>

## 5. Configuration

| Field | Default | Meaning | Required |
|---|---|---|---|
| `<EXAMPLE_KEY>` | - | <one sentence> | no |

## 6. Process Model

- Entry:
- Shutdown:
- Background work:

## 7. Known Constraints

- <example: single-user local workflow>
- <example: no automatic migration for old docs yet>

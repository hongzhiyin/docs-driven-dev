# ARCHITECTURE - <requirement name>

> Create this file only when the requirement affects structure, data flow, APIs, config, migration, or cross-cutting behavior.

## 1. Current Structure

| Module / File | Current responsibility | Relationship to this requirement |
|---|---|---|
| `<path>` | <one sentence> | <reuse / modify / reference> |

## 2. Current Flow

```text
<entry>
  -> <current module / method>
  -> <output / side effect>
```

## 3. Target Structure

```text
<entry>
  -> <kept module>
  -> <new or adjusted module>
  -> <output / side effect>
```

## 4. Contracts

| Module / File | New / Modified | Responsibility | Must not depend on |
|---|---|---|---|
| `<path>` | new / modified | <one sentence> | <boundary> |

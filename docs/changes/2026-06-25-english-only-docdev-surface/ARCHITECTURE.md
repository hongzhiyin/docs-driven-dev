# ARCHITECTURE - <requirement name>

> This requirement affects CLI template selection, shipped skill content, and
> generated decision skeletons.

## 1. Current Structure

| Module / File | Current responsibility | Relationship to this requirement |
|---|---|---|
| `skill/SKILL.md` | Active runtime workflow guidance | Translate to English-only copy |
| `skill/templates/change/` | Change packet templates | Becomes the only shipped change template set |
| Removed language template set | Non-English change packet templates | Removed from shipped templates |
| `src/docs_driven_dev/commands.py` | CLI argument parser | Removes the old `new-change` language option |
| `src/docs_driven_dev/templates.py` | Template lookup and copy logic | Resolves English change templates directly |
| `src/docs_driven_dev/audit.py` | Audit/status and decision skeleton logic | Generates English skeletons while preserving legacy parsing compatibility |
| `tests/test_cli.py` | Regression suite | Protects English-only repository text |
| `docs/changes/*` | Historical change packets | Compact older packets into English archive summaries |

## 2. Current Flow

```text
<entry>
  -> docdev new-change with language selection
  -> commands.py parses language
  -> templates.py resolves a language-specific template set
  -> copied packet contains non-English copy
```

## 3. Target Structure

```text
<entry>
  -> docdev new-change
  -> commands.py dispatches without language selection
  -> templates.py resolves skill/templates/change
  -> copied packet contains English copy
```

## 4. Contracts

| Module / File | New / Modified | Responsibility | Must not depend on |
|---|---|---|---|
| `commands.py` | modified | Keep `new-change` parser English-only | template content |
| `templates.py` | modified | Locate the English change template directory | audit behavior |
| `audit.py` | modified | Emit English decision skeletons | active skill guidance |
| `skill/SKILL.md` | modified | State runtime workflow in English | install manuals |
| `tests/test_cli.py` | modified | Guard generated output and repository text language | release publishing |

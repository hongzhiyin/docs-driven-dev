# docs-driven-dev

Portable skill + CLI for docs-driven development.

`docs-driven-dev` keeps judgment and mechanics separate: the skill defines the
workflow, boundaries, and when docs must change; the `docdev` CLI performs
repeatable filesystem work such as scaffolding, auditing, release update, and
skill sync.

## Quick Install

macOS, Linux, or WSL:

```bash
curl -fsSL https://github.com/hongzhiyin/docs-driven-dev/releases/latest/download/install_remote.sh | sh
docdev -v
```

Windows PowerShell:

```powershell
irm https://github.com/hongzhiyin/docs-driven-dev/releases/latest/download/install_remote.ps1 | iex
docdev -v
```

The release installer downloads the manifest and artifact, verifies the
checksum, installs a versioned user-local release, runs `docdev doctor`, and
syncs installed skill targets by default.

Update:

```bash
docdev update
```

Update without refreshing agent skill homes:

```bash
docdev update --no-sync-skill
```

Uninstall:

```bash
docdev uninstall --dry-run
docdev uninstall --yes
```

Use `docdev uninstall --yes --keep-skills` to remove only the native CLI
release while leaving installed agent skills in place.

## Agent Usage

Users normally ask an agent to use `docs-driven-dev`; the agent reads the
installed skill and decides whether to initialize root docs, create a
requirement packet, audit structure, append a decision, or sync skill content.

Agents should pass the target project path explicitly:

```bash
docdev init /path/to/project
docdev new-change "feature-slug" /path/to/project
docdev audit /path/to/project --write-report
docdev status /path/to/project
docdev new-decision "Step N - trade-off title" /path/to/project
docdev docs-health /path/to/project --write-report
```

When `docs-driven-dev` is explicitly named, the agent should follow one of the
skill workflows and create or update required docs before code changes. Small
fixes still get a minimal change packet. If the user forbids doc changes, the
agent should say the full docs-driven workflow is blocked and ask whether to
continue outside the skill.

When subagents are available and the task has a clear boundary, the main agent
keeps docs-driven ownership while delegating bounded research, implementation,
consistency checks, or failure diagnosis.

## Docs Health

`docdev docs-health <project>` reports documentation size and maintenance
signals for README, the four source docs, and change packets. It is a report,
not an automatic rewriter: the CLI finds pressure points, while the agent or
maintainer decides what to trim, summarize, archive, or keep append-only.

Generated reports are written under:

```text
docs/_generated/docdev/
```

## Maintainer Notes

This source checkout is for developing `docdev` itself. Fresh user installs
should use the release installer above.

Common maintainer commands:

```bash
./scripts/install.sh
./scripts/update_cli.sh --targets codex,cursor,agents,claude --force
./scripts/package_release.sh
./scripts/setup_project.sh /path/to/project
```

Windows PowerShell maintainer entrypoints:

```powershell
.\scripts\install.ps1
.\scripts\update_cli.ps1 -Targets codex,cursor,agents,claude -Force
```

Release and source-checkout contracts live in [docs/SPEC.md](docs/SPEC.md) and
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). Historical trade-offs stay in
[docs/DECISIONS.md](docs/DECISIONS.md).

## Documentation Map

The source of truth lives in `docs/`. Behaviour changes must update docs before
code when the docs-driven workflow applies.

| File | Contents |
|---|---|
| [docs/SPEC.md](docs/SPEC.md) | Rules, invariants, commands, defaults |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Layers, modules, data flow, configuration |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Current phase, step list, acceptance |
| [docs/DECISIONS.md](docs/DECISIONS.md) | `D-XXX` rationale and trade-offs |

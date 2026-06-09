# docs-driven-dev

Portable skill and CLI for docs-driven development.

The skill gives agents the workflow: keep SPEC, ARCHITECTURE, ROADMAP, and
DECISIONS aligned before and after code changes. The CLI handles deterministic
work such as scaffolding templates, auditing document structure, appending the
next D-XXX skeleton, and syncing the skill to agent homes.

## Usage Model

`docdev` does not have a single working directory. It operates on whichever
project path the caller passes:

```bash
docdev init /path/to/project
docdev new-change "feature-slug" /path/to/project
docdev audit /path/to/project --write-report
docdev status /path/to/project
```

In normal use, an agent loads the `docs-driven-dev` skill, resolves the CLI
through `docdev` on `PATH` or the installed skill-local `bin/docdev` wrapper,
then passes the current target project path explicitly.

Use `docdev init` for project-level docs. Use `docdev new-change` when an
existing project needs a scoped requirement packet under
`docs/changes/YYYY-MM-DD-slug/` before implementation.

## Fresh Machine Install

After cloning this source repo on a new machine, run one command from the source
checkout:

macOS, Linux, Git Bash, or WSL:

```bash
./scripts/install.sh
```

Windows PowerShell:

```powershell
Unblock-File .\scripts\*.ps1
.\scripts\install.ps1
```

Windows terminals do not execute `.sh` files directly; they may ask which app
should open the file. Use the PowerShell command above, or run
`bash ./scripts/install.sh` from Git Bash / WSL.

If your PowerShell execution policy requires signed scripts, run the install in
a process-scoped bypass shell instead:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install.ps1
```

This installs the source wrapper, verifies the CLI, syncs the skill into agent
homes, and generates each installed skill's local `bin/docdev` wrapper.
If Windows does not allow symlink creation, the Claude target is copied instead
of linked so the install can still finish.
If install stops, report the last line beginning with `[docdev install]` or
`[docdev update]`; the numbered step shows where it stopped.

By default, sync targets are resolved under the current user's home directory.
If an agent uses a non-default skill directory, set an environment variable
before running install:

```powershell
# Current PowerShell session only.
$env:DOCDEV_CURSOR_SKILL_DIR = "D:\AgentSkills\cursor\docs-driven-dev"
$env:DOCDEV_AGENTS_HOME = "$env:USERPROFILE\.agents"
.\scripts\install.ps1
```

`DOCDEV_<TARGET>_SKILL_DIR` points at the exact final skill folder.
`DOCDEV_<TARGET>_HOME` points at the agent home that contains
`skills\docs-driven-dev`. `<TARGET>` is `CODEX`, `CURSOR`, `AGENTS`, or
`CLAUDE`. Windows user/system environment variables work too; reopen the
terminal after changing persistent values.

After that, any supported agent that loads the `docs-driven-dev` skill can use
the CLI against arbitrary target projects:

```bash
docdev init /path/to/project
docdev new-change "feature-slug" /path/to/project
docdev audit /path/to/project --write-report
docdev status /path/to/project
```

## Source Checkout Setup

```bash
./scripts/setup_project.sh /path/to/project
```

Use this only when manually setting up a target project from this source
checkout. It installs the local `docdev` wrapper, runs `doctor`, initializes the
target project, and writes an audit report under the target docs directory.

Sync the skill after edits:

```bash
./scripts/sync_skill.sh --targets codex,cursor,agents,claude --force
```

After changing this source checkout, use the update lifecycle command:

```bash
./scripts/update_cli.sh --targets codex,cursor,agents,claude --force
```

## Documentation Map

This project's source of truth lives in `docs/`. Any code change must be
consistent with these documents; conflicts get resolved by editing the docs
first, then code.

| File | Contents |
|---|---|
| [docs/SPEC.md](docs/SPEC.md) | Rules, invariants, command list, default behaviour |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Layers, module table, data flow, config |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Step list, acceptance, current progress |
| [docs/DECISIONS.md](docs/DECISIONS.md) | D-XXX trade-off log |

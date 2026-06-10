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

For an existing codebase that has no docs-driven four-pack yet, do both:

```bash
docdev init /path/to/project
docdev new-change "feature-slug" /path/to/project
```

Keep the initial root docs minimal and mark unknowns as pending. Do not create
a standalone `docs/changes/...` packet as the only docs-driven artifact.

When the user explicitly names `docs-driven-dev`, the agent should not treat it
as a loose reference method. It should follow one of the skill workflows and
create or update docs artifacts before code changes. For narrow bug fixes, use
the small-fix path: minimal root docs if missing, a scoped change packet, one
expected behavior rule, touched files, acceptance checks, and verification. If
the user explicitly forbids doc files, the agent should state that the full
docs-driven workflow is blocked before proceeding outside the skill.

## Native Release Install

The intended cross-machine user path is a GitHub Release style installer. It
downloads a manifest and release artifact, verifies the artifact checksum,
installs into the user's home directory, writes a launcher, and runs
`docdev doctor`.

After release assets are published, Unix shells use the remote installer:

```bash
curl -fsSL https://github.com/hongzhiyin/docs-driven-dev/releases/latest/download/install_remote.sh | sh
```

`scripts/package_release.sh` prepares the release asset directory expected by
that command: `docdev-<version>.tar.gz`, its `.sha256`, `manifest.json`,
`install_remote.sh`, and `install_remote.ps1`.

For local smoke tests or mirrors, point the installer at a release artifact
directory:

```bash
DOCDEV_RELEASE_BASE_URL="file:///path/to/release-assets" ./scripts/install_remote.sh
```

Default layout:

```text
~/.local/share/docdev/releases/<version>/
~/.local/share/docdev/current
~/.local/bin/docdev
```

The launcher sets `DOCDEV_PROJECT_DIR` and `PYTHONPATH` to the current release;
users do not need a source checkout or a manual `DOCDEV_PROJECT_DIR`. The
installer does not edit shell startup files. If `~/.local/bin` is not on PATH,
run `~/.local/bin/docdev` directly or add that directory yourself.

Native installs update with:

```bash
docdev update
```

Use `docdev update --sync-skill` only when installed agent skill folders should
also be refreshed. Private GitHub releases are more constrained than public
release URLs: GitHub may return 404 for normal
`github.com/.../releases/download/...` asset URLs on a private repository. For
private testing, use `gh release download` or the GitHub API to fetch the
release assets into a local directory, then install with
`DOCDEV_RELEASE_BASE_URL=file:///path/to/assets`. Tokens should not be written
into launchers or persistent install metadata.

Windows PowerShell follows the same install/update contract through the
PowerShell installer framework. Until it has live Windows verification, treat
the script as a documented framework plus static contract.

## Source Checkout Install

After cloning this source repo for development, run one command from the source
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
homes, and generates each installed skill's local `bin/docdev` wrapper. It is
the developer maintenance path, not the primary native release install path.
It does not add `docdev` to the global shell `PATH`. Direct terminal use from
the source checkout should use `./.venv/bin/docdev` on Unix shells or
`.\.venv\Scripts\docdev.ps1` / `.\.venv\Scripts\docdev.cmd` on Windows, unless
you add a PATH entry yourself.
If Windows does not allow symlink creation, the Claude target is copied instead
of linked so the install can still finish.
If install stops, report the last line beginning with `[docdev install]` or
`[docdev update]`; the numbered step shows where it stopped.

The default install uses force sync. For an existing marked
`docs-driven-dev` skill target, sync performs a whole-directory replacement:
the target skill directory is removed and recopied from this source checkout,
then fresh wrappers are generated. Old files inside that target skill directory
should not remain. If a previous install used a different target path, that old
directory is outside the current sync target set and must be removed manually if
you no longer want it.

Prefer `git pull` in the source checkout or a clean `git clone` over manually
copying downloaded files over an old source folder. A manual file overlay can
leave stale untracked files in the source checkout; install syncs from whatever
currently exists under this checkout's `skill/` directory.

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

Direct terminal use after install:

```bash
./.venv/bin/docdev --version
./.venv/bin/docdev audit /path/to/project
```

```powershell
.\.venv\Scripts\docdev.ps1 --version
.\.venv\Scripts\docdev.ps1 audit C:\path\to\project
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

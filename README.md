# docs-driven-dev

用于 docs-driven development 的可移植 skill + CLI。

这个项目把判断和执行分开：`docs-driven-dev` skill 负责工作流、取舍、边界和
何时更新文档；`docdev` CLI 负责可重复的确定性动作，比如初始化模板、审计文档结构、
追加下一个 `D-XXX` 决策骨架、打包 release、安装更新，以及同步 skill 到各个 agent
目录。

## 快速安装

macOS、Linux 或 WSL 上，普通使用者优先安装最新 GitHub Release：

```bash
curl -fsSL https://github.com/hongzhiyin/docs-driven-dev/releases/latest/download/install_remote.sh | sh
```

Windows PowerShell：

```powershell
irm https://github.com/hongzhiyin/docs-driven-dev/releases/latest/download/install_remote.ps1 | iex
docdev -v
```

安装器会下载 release manifest 和 artifact，校验 checksum，安装到
`~/.local/share/docdev`，写入 native launcher，并运行
`docdev doctor`。

Unix installer 写入 `~/.local/bin/docdev`，但不会自动修改 shell 启动文件。如果
`~/.local/bin` 不在 `PATH` 里，可以直接运行 `~/.local/bin/docdev`，或自行把该目录加入
`PATH`。

Windows installer 写入 `$HOME\.local\bin\docdev.ps1` 和
`$HOME\.local\bin\docdev.cmd`，默认把 `$HOME\.local\bin` 加入当前用户 PATH，并尽量刷新
当前 PowerShell session 的 `$env:Path`。如果当前终端仍找不到 `docdev`，重新打开终端后再运行
`docdev -v`。Windows installer 和生成的 launcher 会在当前进程内设置 UTF-8 输出，避免中文
日志乱码；不会修改 PowerShell profile 或系统区域设置。受管环境不希望修改 PATH 时，可以
下载脚本后使用 `-NoModifyPath`：

```powershell
$installer = "$env:TEMP\install_docdev.ps1"
Invoke-WebRequest `
  -Uri "https://github.com/hongzhiyin/docs-driven-dev/releases/latest/download/install_remote.ps1" `
  -OutFile $installer
powershell -ExecutionPolicy Bypass -File $installer -NoModifyPath
```

更新 native release 安装：

```bash
docdev update
```

`docdev update` 会同时刷新已安装的 agent skill 目录，让 agent 读取到的 workflow 和
当前 CLI release 保持一致。只有在明确不想写入 agent skill 目录时，才使用：

```bash
docdev update --no-sync-skill
```

卸载 native release 安装，便于在新机器上反复验证安装流程：

```bash
docdev uninstall --dry-run
docdev uninstall --yes
```

如果 `docdev` 不在 `PATH` 里，使用完整 launcher 路径：

```bash
~/.local/bin/docdev uninstall --yes
```

Windows 上可使用：

```powershell
& "$HOME\.local\bin\docdev.ps1" uninstall --yes
```

`uninstall` 只删除 docdev native install root、docdev launcher，以及带
`.docdev-skill-source` marker 或 symlink 的 `docs-driven-dev` skill target。它不会删除
`~/.local/bin`、`~/.local/share`、agent home 父目录、源码 checkout，或未标记的同名
skill 目录。只想移除 CLI release、不动 agent skill 时使用：

```bash
docdev uninstall --yes --keep-skills
```

Windows PowerShell 遵循同样的安装 / 更新合同。当前仓库在 macOS 上对
`install_remote.ps1` 做静态和单元合同校验；发布前仍建议做一次真实 Windows live smoke。

## Agent 如何使用

正常使用时，用户不需要先学习 `docdev` 的每个命令。用户告诉支持 skill 的 agent
使用 `docs-driven-dev`，agent 读取已安装的 skill 后，自己判断应该初始化项目文档、
创建需求工作包、审计结构、追加决策，还是同步 skill。

`docdev` 没有唯一工作目录。agent 应该把当前目标项目路径显式传给 CLI，而不是假设
这个源码仓库就是目标项目。

在 macOS / Linux / WSL 上，agent 解析 CLI 时应优先使用 `docdev`；如果它不在
`PATH`，但 native install 已写入 `~/.local/bin/docdev`，就直接使用这个 launcher。
该 launcher 指向 `~/.local/share/docdev/current`，因此 agent 执行确定性 CLI 操作时
不需要访问 `/Users/chihoyo/Project/docs-driven-dev` 这类源码 checkout。

在 Windows 上，native installer 会写入 `docdev.cmd` 并默认加入用户 PATH，所以新终端中
应优先使用 `docdev`。如果当前终端尚未刷新 PATH，可重新打开终端，或临时使用
`$HOME\.local\bin\docdev.ps1` 完整路径。

如果 `docdev` 和 `~/.local/bin/docdev` 都不可用，agent 应提示用户先运行 native
installer，而不是去猜某个源码 checkout 路径或 skill 目录里的 wrapper。`sync-skill`
只同步 skill 内容；release install/update 默认会刷新 skill 目录，若要跳过则运行
`docdev update --no-sync-skill`。

当用户明确点名 `docs-driven-dev` 时，agent 不应把它当成泛泛的参考方法。它应该遵循
skill 中的某个工作流，并在改代码前创建或更新必要的 docs artifacts。窄范围 bug fix
也不跳过文档；使用 small-fix path：缺根文档时先轻量初始化，创建 scoped change packet，
写清一条期望行为、触及文件、验收检查和验证结果。若用户明确禁止改文档，agent 应先说明
完整 docs-driven workflow 被阻塞，再询问是否脱离该 skill 继续。

## 手动 CLI 参考

这些命令主要给调试、本地 smoke test 和维护使用。日常场景里，agent 会通过已安装的
skill 调用它们。

```bash
docdev init /path/to/project
docdev new-change "feature-slug" /path/to/project
docdev audit /path/to/project --write-report
docdev status /path/to/project
docdev doctor
docdev uninstall --dry-run
```

使用 `docdev init` 创建项目级四件套文档。已有项目要在实现前开 scoped requirement
packet 时，使用 `docdev new-change`，生成类似
`docs/changes/YYYY-MM-DD-slug/` 的工作包。

如果一个已有代码库还没有 docs-driven 四件套，先做轻量 adoption，再开当前需求包：

```bash
docdev init /path/to/project
docdev new-change "feature-slug" /path/to/project
```

初始根文档可以保持很薄，把未知项标成 pending。不要让 `docs/changes/...` 成为项目里
唯一的 docs-driven artifact。

## Release Installer 细节

`scripts/package_release.sh` 用来准备 GitHub Release assets：

```text
docdev-<version>.tar.gz
docdev-<version>.tar.gz.sha256
manifest.json
install_remote.sh
install_remote.ps1
```

本地 smoke test 或镜像安装可以指定 release artifact 目录：

```bash
DOCDEV_RELEASE_BASE_URL="file:///path/to/release-assets" ./scripts/install_remote.sh
```

默认 native install 布局：

```text
~/.local/share/docdev/releases/<version>/
~/.local/share/docdev/current
~/.local/bin/docdev
```

Windows 默认 native install 布局：

```text
%USERPROFILE%\.local\share\docdev\releases\<version>\
%USERPROFILE%\.local\share\docdev\current
%USERPROFILE%\.local\bin\docdev.ps1
%USERPROFILE%\.local\bin\docdev.cmd
```

生成的 launcher 会把 `DOCDEV_PROJECT_DIR` 和 `PYTHONPATH` 指向当前 release。用户不需要
保留源码 checkout，也不需要手动设置 `DOCDEV_PROJECT_DIR`。

公开 GitHub Release 是默认分发路径。私有 GitHub Release 不能假设普通
`github.com/.../releases/download/...` URL 可直接下载；GitHub 可能返回 404。私有测试时，
先用 `gh release download` 或 GitHub API 把 release assets 下载到本地目录，再用
`DOCDEV_RELEASE_BASE_URL=file:///path/to/assets` 安装。不要把 token 写入 launcher 或持久
安装元数据。

## 源码 Checkout 开发安装

如果是为了开发或维护这个仓库，先 clone 源码，然后在源码 checkout 中运行：

macOS、Linux、Git Bash 或 WSL：

```bash
./scripts/install.sh
```

Windows PowerShell：

```powershell
Unblock-File .\scripts\*.ps1
.\scripts\install.ps1
```

Windows 终端不会直接执行 `.sh` 文件；它可能会询问用哪个 app 打开。请使用上面的
PowerShell 命令，或在 Git Bash / WSL 中运行 `bash ./scripts/install.sh`。

如果当前 PowerShell 执行策略要求脚本签名，可以只对本次进程使用 bypass：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install.ps1
```

这条开发安装路径会安装源码维护 wrapper、验证 CLI，并把 skill 内容同步到 agent homes。
它是开发者维护路径，不是普通用户的首选 native release install 路径。

它不会把 `docdev` 加入全局 shell `PATH`。如果要从源码 checkout 直接在终端运行 CLI，
Unix shell 使用：

```bash
./.venv/bin/docdev --version
./.venv/bin/docdev audit /path/to/project
```

Windows PowerShell 使用：

```powershell
.\.venv\Scripts\docdev.ps1 --version
.\.venv\Scripts\docdev.ps1 audit C:\path\to\project
```

生成的 Windows source checkout launcher 同样会在当前进程内设置 UTF-8 输出。

如果 Windows 不允许创建 symlink，Claude 目标会 fallback 为复制，这样安装仍可完成。
如果安装中断，把最后一行以 `[docdev install]` 或 `[docdev update]` 开头的输出拿来定位；
编号 step 会指出停在哪个阶段。

默认安装会 force sync。对于已有 marker 的 `docs-driven-dev` skill 目标，sync 会做整个
目录替换：先移除目标 skill 目录，再从当前源码 checkout 复制当前 skill 内容。因此旧目标
目录里的陈旧文件，包括旧版本生成的 `bin/docdev*` wrapper，不应残留。如果过去使用过另一个
目标路径，那是当前 sync 目标集合之外的目录，不再需要时需要手动清理。

更新源码 checkout 时，优先使用 `git pull` 或干净的 `git clone`。不要把下载文件手动覆盖
到旧源码目录上；手动覆盖可能留下 stale untracked files，而 install/sync 会复制当前 checkout
里实际存在的 `skill/` 目录。

如果某个 agent 的 skill 目录不在默认用户 home 下，可以在安装前设置环境变量：

```powershell
# 只影响当前 PowerShell session。
$env:DOCDEV_CURSOR_SKILL_DIR = "D:\AgentSkills\cursor\docs-driven-dev"
$env:DOCDEV_AGENTS_HOME = "$env:USERPROFILE\.agents"
.\scripts\install.ps1
```

`DOCDEV_<TARGET>_SKILL_DIR` 指向最终 skill 文件夹；`DOCDEV_<TARGET>_HOME` 指向包含
`skills\docs-driven-dev` 的 agent home。`<TARGET>` 是 `CODEX`、`CURSOR`、`AGENTS`
或 `CLAUDE`。Windows 用户 / 系统环境变量也可以使用；修改持久环境变量后需要重新打开终端。

同步 skill：

```bash
./scripts/sync_skill.sh --targets codex,cursor,agents,claude --force
```

修改源码 checkout 后，使用完整更新生命周期：

```bash
./scripts/update_cli.sh --targets codex,cursor,agents,claude --force
```

## 源码 Checkout 手动初始化目标项目

```bash
./scripts/setup_project.sh /path/to/project
```

只在需要从源码 checkout 手动初始化某个目标项目时使用它。该脚本会安装本地源码维护
`docdev` wrapper，运行 `doctor`，初始化目标项目，并把 audit report 写到目标项目的
docs 目录下。

## Documentation Map（文档地图）

本项目的 source of truth 位于 `docs/`。任何行为变更都必须和这些文档一致；若冲突，
先改文档，再改代码。

| 文件 | 内容 |
|---|---|
| [docs/SPEC.md](docs/SPEC.md) | 规则、不变式、命令列表、默认行为 |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | 分层、模块表、数据流、配置 |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Step 列表、验收标准、当前进度 |
| [docs/DECISIONS.md](docs/DECISIONS.md) | `D-XXX` 取舍记录 |

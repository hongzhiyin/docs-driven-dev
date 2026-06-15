# ARCHITECTURE - Windows 裸命令安装

> 本文件只在需求影响结构时创建。它描述现有结构是什么，以及本次方案会如何改变结构。

## 0. 状态

| 字段 | 内容 |
|---|---|
| 状态 | 实现完成，Windows live smoke 已补充；发现 post-install sync 参数引用缺陷 |
| 创建原因 | Windows native installer 的 launcher、PATH 配置契约和 update 调用链会变化 |
| 最后更新 | 2026-06-15 |

## 1. 现有结构快照

| 模块 / 文件 | 当前职责 | 与本需求关系 |
|---|---|---|
| `scripts/install_remote.ps1` | Windows remote native installer：下载 manifest/artifact、校验 checksum、安装 release、写 `docdev.ps1`、运行 doctor/sync | 需要修改，成为 Windows 裸命令和 PATH 管理入口 |
| `scripts/install_remote.sh` | Unix remote native installer：写 `~/.local/bin/docdev` 并提示 PATH | 保持行为不变，只作为对照 |
| `scripts/install_cli.ps1` | Source checkout developer wrapper installer，生成 `.venv\Scripts\docdev.ps1` 和 `.cmd` | 复用 `.cmd` 生成思路 |
| `src/docs_driven_dev/release.py` | `docdev update` dispatch、install root/bin dir 解析、uninstall plan | 需要让 update 按平台选择 `.ps1` / `.sh` |
| `scripts/package_release.sh` | 打包 release artifacts：tarball、sha256、manifest、install_remote scripts | 可能只需测试更新，继续发布 PowerShell installer |
| `tests/test_cli.py` | 保护 CLI、installer、package、docs contract | 需要新增/更新 Windows static contract 和 update dispatch 测试 |

## 2. 当前调用链 / 数据流

```text
PowerShell install_remote.ps1
  -> download manifest / artifact
  -> verify sha256
  -> unpack release into $HOME\.local\share\docdev\releases\<version>
  -> switch $HOME\.local\share\docdev\current
  -> write $HOME\.local\bin\docdev.ps1
  -> run docdev.ps1 doctor
  -> run docdev.ps1 sync-skill unless -NoSyncSkill

docdev update
  -> src/docs_driven_dev/release.py cmd_update()
  -> scripts/install_remote.sh
```

Problems:
- Windows install has no `docdev.cmd`, so typing `docdev` is not guaranteed.
- Windows install does not add `BinDir` to User PATH.
- `docdev update` uses the Unix shell installer even on Windows.

## 3. 目标结构

```text
PowerShell install_remote.ps1 [-NoModifyPath]
  -> download manifest / artifact
  -> verify sha256
  -> unpack release into $InstallRoot\releases\<version>
  -> switch $InstallRoot\current
  -> write $BinDir\docdev.ps1
  -> write $BinDir\docdev.cmd
  -> unless -NoModifyPath:
       ensure $BinDir is in User PATH
       ensure current $env:Path contains $BinDir when script runs in caller session
  -> run generated launcher doctor
  -> run generated launcher sync-skill unless -NoSyncSkill

PowerShell / CMD user
  -> docdev -v
  -> PATH resolves docdev.cmd
  -> generated launcher sets DOCDEV_PROJECT_DIR / PYTHONPATH
  -> python -m docs_driven_dev.cli -v

docdev update
  -> release.py detects Windows
  -> powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/install_remote.ps1 ...
  -> same install/update flow as above
```

2026-06-15 Windows live smoke refinement:
- PowerShell treats an unquoted `codex,cursor,agents,claude` argument list as
  multiple native arguments in this installer context. The generated launcher
  must call `sync-skill --targets "codex,cursor,agents,claude" --force`.
- The installer should verify User PATH after writing it and print a targeted
  diagnostic if the persisted user environment still does not contain `BinDir`.
  Updating `$env:Path` inside a child PowerShell process cannot refresh the
  parent process, so diagnostics must distinguish parent-session staleness from
  persistent PATH write failure.

## 4. 模块与接口契约

| 模块 / 文件 | 新增 / 修改 | 职责 | 不应依赖 |
|---|---|---|---|
| `scripts/install_remote.ps1` | 修改 | 生成 Windows launcher set，管理 User PATH，支持 `-NoModifyPath`，保留 manifest/checksum/current/sync 行为 | 不依赖 source checkout；不写 system PATH |
| `$BinDir\docdev.cmd` | 新增生成物 | Windows bare command shim；使 `docdev -v` 经 PATHEXT / PATH 解析 | 不包含 token；不硬编码 source checkout |
| `$BinDir\docdev.ps1` | 保留生成物 | PowerShell launcher；保留完整路径 fallback | 不要求用户手写 alias |
| `src/docs_driven_dev/release.py` | 修改 | 按平台 dispatch `install_remote.ps1` 或 `install_remote.sh`，传递 `--no-sync-skill` 等参数 | 不复制 installer 逻辑 |
| `tests/test_cli.py` | 修改 | 静态保护 PowerShell installer 生成 cmd、PATH opt-out、Windows update dispatch | 不要求当前 macOS 直接执行 Windows installer |
| README / root docs / skill | 修改 | 向用户说明 Windows GitHub latest install、`docdev -v`、PATH opt-out 和重开终端 | 不宣传 npm-first |

## 5. 数据、配置、资源变化

| 类型 | 路径 / 字段 | 变化 | 兼容性 |
|---|---|---|---|
| 生成文件 | `$BinDir\docdev.cmd` | 新增 | uninstall planner 已识别 `docdev.cmd` candidate |
| 生成文件 | `$BinDir\docdev.ps1` | 保留 | 完整路径 fallback 继续可用 |
| 环境变量 | `DOCDEV_BIN_DIR` | 保留 | PATH 添加目标跟随该值 |
| PowerShell 参数 | `-NoModifyPath` | 新增 | 用户可避免 installer 修改 PATH |
| 用户环境 | User `Path` | 默认追加 `BinDir`，去重 | 不写 System PATH；受管环境可 opt out |
| 当前环境 | `$env:Path` | 当前 session 尽量同步 `BinDir` | 仅影响当前 PowerShell process；通过 `powershell -File` 子进程安装时无法修改父进程 |

## 6. 测试与观测点

- Unit/static:
  - `install_remote.ps1` contains `docdev.cmd` generation.
  - `install_remote.ps1` contains User PATH update and `-NoModifyPath`.
  - `release.py cmd_update()` dispatches PowerShell installer on Windows and shell installer on Unix.
  - `--no-sync-skill`, `--version`, `--release-base-url`, `--install-root`, `--bin-dir` are preserved.
- Local smoke:
  - package release still emits `install_remote.ps1`.
  - existing Unix install/update tests still pass.
- Windows live smoke:
  - install latest from GitHub in PowerShell. Completed for `0.1.7`.
  - open a new PowerShell and run `docdev -v`. Completed by user confirmation.
  - open CMD and run `docdev -v`. Still useful for coverage.
  - run `docdev update` and re-check `docdev -v`. Still useful for coverage.
  - verify default sync writes Codex/Cursor/Agents/Claude skill targets without
    manual `sync-skill` repair. Source fixed; release pending.

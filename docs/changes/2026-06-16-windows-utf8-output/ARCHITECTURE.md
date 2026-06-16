# ARCHITECTURE - Windows UTF-8 output

> 本文件只在需求影响结构时创建。它描述现有结构是什么，以及本次方案会如何改变结构。

## 0. 状态

| 字段 | 内容 |
|---|---|
| 状态 | 已发布 v0.1.9；等待 Windows live smoke |
| 创建原因 | Windows installer / source scripts / generated launchers 的环境配置契约变化 |
| 最后更新 | 2026-06-16 |

## 1. 现有结构快照

| 模块 / 文件 | 当前职责 | 与本需求关系 |
|---|---|---|
| `scripts/install_remote.ps1` | Windows remote native installer; writes `docdev.ps1` and `docdev.cmd` | 需要在脚本本身和生成 launcher 中加入 UTF-8 setup |
| `scripts/install_cli.ps1` | Source checkout wrapper installer; writes `.venv\Scripts\docdev.ps1` and `.cmd` | 需要在脚本本身和生成 launcher 中加入 UTF-8 setup |
| `scripts/install.ps1` | Source checkout install entrypoint | 需要在第一条 install log 前设置 UTF-8 |
| `scripts/update_cli.ps1` | Source checkout update lifecycle | 需要在 update log 和 Python 子命令前设置 UTF-8 |
| `tests/test_cli.py` | Static and behavior regression tests | 需要覆盖 Windows encoding prelude |

## 2. 当前调用链 / 数据流

```text
install_remote.ps1
  -> Write-Host install logs
  -> write docdev.ps1 / docdev.cmd
  -> run docdev.ps1 doctor / sync-skill

install_cli.ps1
  -> write source checkout docdev.ps1 / docdev.cmd
  -> Write-Host wrapper paths

generated docdev.ps1 / docdev.cmd
  -> set DOCDEV_PROJECT_DIR / PYTHONPATH
  -> python -m docs_driven_dev.cli ...
```

Current gap:
- The entry scripts and generated launchers do not force UTF-8 before writing logs or invoking Python.

## 3. 目标结构

```text
PowerShell entry script
  -> Set-DocdevUtf8Console
      -> [Console]::InputEncoding / OutputEncoding
      -> $OutputEncoding
      -> PYTHONUTF8 / PYTHONIOENCODING
  -> existing installer/update/install behavior

generated docdev.ps1
  -> UTF-8 PowerShell/Python prelude
  -> DOCDEV_PROJECT_DIR / PYTHONPATH
  -> python -m docs_driven_dev.cli ...

generated docdev.cmd
  -> chcp 65001 >nul
  -> PYTHONUTF8 / PYTHONIOENCODING
  -> DOCDEV_PROJECT_DIR / PYTHONPATH
  -> python -m docs_driven_dev.cli ...
```

## 4. 模块与接口契约

| 模块 / 文件 | 新增 / 修改 | 职责 | 不应依赖 |
|---|---|---|---|
| `Set-DocdevUtf8Console` function in PowerShell scripts | 新增 | Best-effort configure current process console and Python IO encoding | User profile, admin privileges, system locale |
| Generated `docdev.ps1` prelude | 修改 | Ensure released/source PowerShell launcher starts Python under UTF-8 | Source checkout path guesses |
| Generated `docdev.cmd` prelude | 修改 | Ensure CMD launcher uses code page 65001 and Python UTF-8 env | Permanent code page mutation |
| `tests/test_cli.py` | 修改 | Guard all Windows entrypoint templates statically | A live Windows shell on macOS |

## 5. 数据、配置、资源变化

| 类型 | 路径 / 字段 | 变化 | 兼容性 |
|---|---|---|---|
| Environment | `PYTHONUTF8=1` | Set for generated Windows launchers and PowerShell lifecycle scripts | Only current process and child Python |
| Environment | `PYTHONIOENCODING=utf-8` | Set for generated Windows launchers and PowerShell lifecycle scripts | Only current process and child Python |
| Console | PowerShell input/output encoding | Best-effort set to UTF-8 no BOM | Caught if host disallows mutation |
| Console | CMD code page | `chcp 65001 >nul` in generated `.cmd` | Current cmd process only |

## 6. 测试与观测点

- Static tests:
  - PowerShell scripts contain `Set-DocdevUtf8Console`.
  - Generated PowerShell launcher strings set `PYTHONUTF8` and `PYTHONIOENCODING`.
  - Generated CMD launcher strings call `chcp 65001 >nul`.
- Existing regression:
  - Unit tests pass on macOS.
  - `docdev audit` remains clean.
- Manual Windows follow-up:
  - Install from packaged/released assets and confirm Chinese install/update/CLI output is readable.

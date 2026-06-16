# SPEC - Windows UTF-8 output

> 本文件描述本次需求应该满足什么。它不写实现细节、不追踪进度、不解释历史取舍。

## 0. 状态

| 字段 | 内容 |
|---|---|
| 状态 | 源码修复完成；等待 Windows release/live smoke |
| 需求来源 | 用户反馈：Windows 平台一开始 PowerShell 输出中文乱码，需要项目直接处理 UTF-8 编码 |
| 工作包目录 | `docs/changes/2026-06-16-windows-utf8-output/` |
| 最后更新 | 2026-06-16 |

## 1. 一句话目标

让 Windows 用户运行 docdev 的安装、更新、源码维护脚本或生成 launcher 时，默认使用 UTF-8 控制台和 Python IO 编码，避免中文输出在启动阶段乱码。

## 2. 背景与问题

- 当前行为：Windows 入口脚本和生成 launcher 会直接 `Write-Host` 或启动 `python -m docs_driven_dev.cli`，但没有显式设置 PowerShell console encoding、`$OutputEncoding`、`PYTHONUTF8` 或 `PYTHONIOENCODING`。
- 问题：在 Windows PowerShell / CMD 的默认代码页或宿主编码不是 UTF-8 时，安装日志、中文模板路径或 CLI 输出可能在最开始就乱码；仅在 Python CLI 内处理不能覆盖 installer 早期输出。
- 期望收益：用户不需要手动执行 `chcp 65001`、修改 PowerShell profile，或记住一次性编码命令。

## 3. 范围

### 3.1 本次要做

- Windows remote installer 在第一次日志输出前设置 UTF-8 控制台和 Python IO 环境。
- Windows source checkout install/update 脚本在输出和调用 Python 前设置相同 UTF-8 环境。
- 生成的 `docdev.ps1` launcher 默认设置 UTF-8 控制台和 Python IO 环境。
- 生成的 `docdev.cmd` launcher 默认切换到 UTF-8 code page，并设置 Python UTF-8 环境变量。
- 增加静态回归测试，保护以上入口不会丢失 UTF-8 prelude。

### 3.2 本次不做

- 不修改用户 PowerShell profile、系统区域设置、System PATH 或系统代码页。
- 不要求管理员权限。
- 不引入新的 Windows `docdev.exe` 二进制打包。
- 不发布 release；发布 v0.1.9 或更新 native install 需单独执行 release 流程。

## 4. 用户场景 / 使用流程

| 场景 ID | 触发条件 | 期望结果 |
|---|---|---|
| S1 | Windows 用户运行 `irm ...install_remote.ps1 \| iex` | 安装器从第一批日志开始使用 UTF-8 输出 |
| S2 | Windows 用户运行 `docdev -v` / `docdev audit ...` | `docdev.cmd` 或 `docdev.ps1` 先配置 UTF-8，再启动 Python CLI |
| S3 | Windows 开发者运行 `.\scripts\install.ps1` 或 `.\scripts\update_cli.ps1` | 源码维护日志和 Python 子命令使用 UTF-8 |

## 5. 功能需求

| ID | 需求 | 验收方式 | 状态 |
|---|---|---|---|
| R1 | PowerShell installer / source scripts must set console input/output encoding, `$OutputEncoding`, `PYTHONUTF8`, and `PYTHONIOENCODING` before user-visible output or Python execution | Static tests inspect `.ps1` scripts | 完成 |
| R2 | Generated PowerShell launchers must include the same UTF-8 prelude | Static tests inspect generated launcher template strings | 完成 |
| R3 | Generated CMD launchers must run `chcp 65001 >nul` and set Python UTF-8 environment variables before Python execution | Static tests inspect `.cmd` template strings | 完成 |
| R4 | Existing checksum, PATH, sync, update, and source wrapper behavior must remain unchanged | Unit tests and `docdev audit` | 通过 |

## 6. 约束与不变式

1. **#1**: UTF-8 handling must be local to docdev scripts and generated launchers; it must not mutate system locale, user profiles, or System PATH.
2. **#2**: Native release install/update must still verify artifact checksums before switching `current`.
3. **#3**: Windows command availability remains installer-owned `docdev.cmd` / `docdev.ps1`; this change must not introduce npm-first or binary packaging.
4. **#4**: Source checkout developer workflows remain separate from native release install workflows.

## 7. 兼容性与默认行为

| 场景 | 默认行为 |
|---|---|
| Existing PowerShell terminals | The script sets encoding for the current process; parent process encoding is not persistently changed |
| Existing CMD terminals | The launcher runs `chcp 65001 >nul` for the current command process |
| Hosts that reject console encoding mutation | Python UTF-8 environment variables still apply; console mutation failure should not block install |
| Non-Windows Unix install/update | No behavior change |

## 8. 验收标准

1. All Windows PowerShell entry scripts and generated PowerShell launchers include UTF-8 setup before invoking Python.
2. All generated Windows CMD launchers include UTF-8 code page and Python UTF-8 environment setup.
3. `python3 -m unittest discover -s tests` passes.
4. `docdev audit /Users/chihoyo/Project/docs-driven-dev` reports no findings.

## 9. 开放问题

| ID | 问题 | 当前判断 | 是否阻塞实现 |
|---|---|---|---|
| Q1 | 是否需要真实 Windows live smoke 才能合并源码修复？ | 当前 macOS 可做静态/单元/audit 验证；真实 Windows 验证仍是 release 前推荐项。 | 否 |

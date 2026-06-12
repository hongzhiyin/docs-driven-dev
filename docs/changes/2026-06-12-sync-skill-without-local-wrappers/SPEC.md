# SPEC - sync-skill 不再生成 skill-local wrappers

> 本文件描述本次需求应该满足什么。它不写实现细节、不追踪进度、不解释历史取舍。

## 0. 状态

| 字段 | 内容 |
|---|---|
| 状态 | 完成 |
| 需求来源 | 用户请求：清理第 3 类 skill-local compatibility wrapper，让使用方式以 CLI/native launcher 为准 |
| 工作包目录 | `docs/changes/2026-06-12-sync-skill-without-local-wrappers/` |
| 最后更新 | 2026-06-12 |

## 1. 一句话目标

`docdev sync-skill` 只同步 skill 内容，不再在已安装 skill 目录内生成 `bin/docdev*` compatibility wrappers；agent 运行确定性命令时只使用 `docdev` on `PATH` 或 native launcher。

## 2. 背景与问题

- 当前行为：`src/docs_driven_dev/cli.py` 的 `copy_skill()` 在复制 skill 后调用 `write_installed_skill_wrapper()`，为每个已安装 skill 目录生成 `bin/docdev`、`bin/docdev.ps1` 和 `bin/docdev.cmd`。
- 问题：这些 skill-local wrappers 属于旧的 source checkout 分发模式，会让 skill 目录看起来仍承担 CLI 入口职责，削弱 native install 后“以 `docdev` CLI/native launcher 为准”的模型。
- 期望收益：skill target 目录只承载 workflow 文档和资源；CLI 入口统一到 native install / PATH；source checkout wrapper 仅留在源码开发目录内。

## 3. 范围

### 3.1 本次要做

- 删除 CLI 中的 skill-local wrapper 生成函数和调用点。
- 更新测试：`copy_skill()` 应证明旧 `bin/` stale wrapper 被 force/marked replacement 清理，而不是重新生成。
- 更新 README、SPEC、ARCHITECTURE、SKILL 和 ROADMAP，说明 `sync-skill` 只同步 skill 内容，不再提供 skill-local CLI 入口。
- 记录项目级 D-025，说明为什么现在移除第 3 类 wrapper。

### 3.2 本次不做

- 不删除 native release launcher：`~/.local/bin/docdev` 仍由 remote installer 生成。
- 不删除 source checkout 本地 wrapper：`scripts/install_cli.*` 仍为维护者运行未发布源码提供便利。
- 不删除 `docdev sync-skill` 命令；它仍负责把 skill 文档同步到 agent homes。
- 不改变 `docdev update --sync-skill` 的语义，只改变 sync 后的目录内容。

## 4. 用户场景 / 使用流程

| 场景 ID | 触发条件 | 期望结果 |
|---|---|---|
| S1 | agent 在任意项目中需要运行 docs-driven-dev CLI | 使用 `docdev` 或 `~/.local/bin/docdev`，不依赖 skill 目录里的 `bin/docdev` |
| S2 | 维护者运行 `docdev sync-skill --force` | 目标 skill 目录被替换为纯 skill 内容，不再包含旧 `bin/` wrapper |
| S3 | 维护者在源码 checkout 中运行未发布版本 | 仍可使用 `.venv/bin/docdev` 或 `PYTHONPATH=src python3 -m docs_driven_dev.cli` |

## 5. 功能需求

| ID | 需求 | 验收方式 | 状态 |
|---|---|---|---|
| R1 | `copy_skill()` 不再生成 `bin/docdev*` | unit test | 完成 |
| R2 | marked/forced sync 会清掉目标目录里的旧 `bin/` wrapper | unit test | 完成 |
| R3 | 文档不再描述 skill-local wrapper 作为支持入口 | `rg` / audit | 完成 |
| R4 | source checkout 和 native install 入口仍通过 doctor/audit | tests / `docdev doctor` / `docdev audit` | 完成 |

## 6. 约束与不变式

1. **#1**: 跨机器 agent CLI resolution 只能依赖 `docdev` on `PATH` 或 native launcher，不能依赖 skill-local wrapper。
2. **#2**: `docdev sync-skill` 仍必须能替换 marked target 并清理目标目录内 stale files。
3. **#3**: source checkout 本地维护入口保留，方便在 release 前验证源码状态。

## 7. 兼容性与默认行为

| 场景 | 默认行为 |
|---|---|
| 已安装 skill 目录里已有 `bin/docdev*` | 下次 marked/forced `sync-skill` 替换目标目录时删除 |
| `docdev update --sync-skill` | 继续刷新 skill target，但不会生成 skill-local wrappers |
| 源码 checkout 本地运行 | 使用 `.venv/bin/docdev`、PowerShell `.venv\Scripts\docdev.*` 或 `PYTHONPATH=src python3 -m ...` |
| native release install | 保持 `~/.local/bin/docdev` launcher |

## 8. 验收标准

1. 新同步的 skill target 不包含 `bin/docdev`、`bin/docdev.ps1` 或 `bin/docdev.cmd`。
2. 单元测试、`docdev doctor` 和 `docdev audit` 通过。
3. README / SKILL / SPEC / ARCHITECTURE 都把 CLI/native launcher 作为唯一普通 agent 入口。

## 9. 开放问题

| ID | 问题 | 当前判断 | 是否阻塞实现 |
|---|---|---|---|
| Q1 | 是否保留一个 opt-in compatibility wrapper 开关 | 不保留；这会延续第 3 类入口，不符合“以 CLI 使用方式为准” | 否 |

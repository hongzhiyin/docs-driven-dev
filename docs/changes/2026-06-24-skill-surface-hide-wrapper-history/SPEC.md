# SPEC - skill-surface-hide-wrapper-history

> 本文件描述本次需求应该满足什么。它不写实现细节、不追踪进度、不解释历史取舍。

## 0. 状态

| 字段 | 内容 |
|---|---|
| 状态 | 已完成 |
| 需求来源 | 用户反馈：skill 文档不应解释旧 wrapper 到 native launcher 的迁移或清理规则；active skill 也不应承载源码 checkout 开发安装说明；delegation guidance 应是全局规则 |
| 工作包目录 | `docs/changes/2026-06-24-skill-surface-hide-wrapper-history/` |
| 最后更新 | 2026-06-24 |

## 1. 一句话目标

让 agent 和普通使用者读取 active guidance 时，只看到当前支持的 `docdev` 使用方式和
docs-driven 工作流边界，不会被旧 skill-local wrapper、skill 目录下 cmd 探测、源码开发安装
手册，或这类否定式提醒诱导。

## 2. 背景与问题

- 当前行为：`skill/SKILL.md` 已不再直接命名旧 `bin/docdev*` wrapper，但仍包含
  marker、legacy target、source checkout launcher 等迁移/维护细节；README 的普通使用
  和 agent 使用面也显式暴露 Windows `.cmd` 文件名。
- 问题：active guidance 是模型的即时操作上下文，历史或实现细节即使是否定式，也会让
  agent 重新关注旧入口或错误地报告预期缺失。
- 期望收益：使用方只学习 `docdev` 命令、必要 fallback 和 docs-driven workflow；迁移历史
  留在 source-of-truth docs 中。
- 后续反馈：`Source Checkout Install（源码开发安装）` 属于维护者文档，不应出现在
  active skill；`Delegation Guidance（委派指导）` 也不应只挂在 Workflow B 下，而应在
  平台支持且任务可切分时作为全局 workflow 工具优先考虑。

## 3. 范围

### 3.1 本次要做

- 收敛 `skill/SKILL.md`，移除旧 wrapper / skill-local cmd / marker / legacy cleanup 相关
  操作面文字。
- 收敛 README 的普通安装和 agent 使用面，不暴露 Windows `.cmd` 具体文件名。
- 更新回归测试，禁止 active skill/README surface 出现旧 wrapper 或 skill-local cmd 类词。
- 更新根 source-of-truth docs，记录 skill surface hygiene 的持久规则。
- 删除 active skill 中的源码 checkout 开发安装手册。
- 将 active skill 中的 delegation guidance 提升为全局 section，并表述为可用时优先考虑的
  bounded-slice workflow 工具。

### 3.2 本次不做

- 不改变 installer、sync、uninstall、Windows native command shim 的代码行为。
- 不重写历史 ROADMAP / DECISIONS / change packet 中的迁移记录。
- 不隐藏维护层 SPEC / ARCHITECTURE / tests / scripts 中必要的实现事实。
- 不删除 README / root SPEC 中面向维护者的源码 checkout 开发安装说明。

## 4. 用户场景 / 使用流程

| 场景 ID | 触发条件 | 期望结果 |
|---|---|---|
| S1 | agent 读取 `docs-driven-dev` skill 并需要调用 CLI | 只根据 `docdev`、Unix native path 或 Windows PowerShell fallback 继续，不报告旧 skill-local cmd/wrapper 缺失 |
| S2 | 普通用户阅读 README 安装或更新 | 使用 `docdev` 命令和 documented fallback，不需要理解 `.cmd` 实现细节 |
| S3 | agent 读取 active skill 处理较宽任务 | 在平台支持且 task slice 清楚时优先考虑 subagent；主 agent 保留 docs-driven ownership |

## 5. 功能需求

| ID | 需求 | 验收方式 | 状态 |
|---|---|---|---|
| R1 | Active skill surface 不包含旧 skill-local entrypoint、`docdev.cmd`、marker 或 legacy cleanup 表述 | `rg` + unit test | 完成 |
| R2 | README 普通使用 / agent 使用面不暴露 Windows `.cmd` 文件名 | `rg README.md` + unit test | 完成 |
| R3 | SPEC / DECISIONS 保留维护层事实和历史追溯 | 人工检查 + audit | 完成 |
| R4 | Active skill 不包含源码 checkout 开发安装 section、source checkout 指令、`.venv` 或 source install 脚本命令 | `rg` + unit test | 完成 |
| R5 | Active skill 的 delegation guidance 是顶层 workflow section，不嵌在 Workflow B 下，并鼓励在可用且任务可切分时优先考虑 subagent | unit test | 完成 |

## 6. 约束与不变式

1. **#1**: CLI 执行入口仍是 `docdev` on PATH、Unix-like `~/.local/bin/docdev`、
   Windows 新终端中的 `docdev` 或临时 `$HOME\.local\bin\docdev.ps1`。
2. **#2**: `sync-skill` 仍只同步 skill 内容；确定性行为继续在 CLI / scripts 中实现。
3. **#3**: 历史迁移和实现细节可保留在 source-of-truth docs / tests / scripts 中，但不进入
   active skill surface。
4. **#4**: 源码 checkout 开发安装说明属于维护者文档，不属于 active skill runtime guidance。
5. **#5**: Delegation guidance 是 skill-level workflow guidance；主 agent 负责收束，subagent
   只承担边界清楚的 research / implementation / consistency / failure-diagnosis slices。

## 7. 兼容性与默认行为

| 场景 | 默认行为 |
|---|---|
| 旧迁移记录 | 保留在 ROADMAP / DECISIONS / change packets |
| Windows native command shim | 实现不变，README / skill 使用 `docdev` 命令描述普通路径 |
| 已安装 skill 目标 | 继续由 install/update/sync 刷新 skill 内容 |

## 8. 验收标准

1. `skill/SKILL.md` 和 README 的 active surface 不包含旧 skill-local entrypoint 或 cmd 类表述，
   包括否定式提示。
2. `skill/SKILL.md` 不包含源码 checkout 开发安装 section 或源码维护命令。
3. `Delegation Guidance（委派指导）` 在 `skill/SKILL.md` 中是顶层 section，且位于 workflows
   之前。
4. `python3 -m unittest discover -s tests` 和 `docdev audit` 通过。
5. 当前 CLI / installer / sync 行为不变。

## 9. 开放问题

| ID | 问题 | 当前判断 | 是否阻塞实现 |
|---|---|---|---|
| Q1 | 是否需要发布新 release 让其他机器通过 `docdev update` 获得这次 wording cleanup | 本次先改源码并验证；发布可作为后续步骤 | 否 |

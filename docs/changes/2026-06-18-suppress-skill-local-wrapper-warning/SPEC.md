# SPEC - positive CLI resolution guidance

> 本文件描述本次需求应该满足什么。它不写实现细节、不追踪进度、不解释历史取舍。

## 0. 状态

| 字段 | 内容 |
|---|---|
| 状态 | v0.1.12 发布中 |
| 需求来源 | 用户反馈：agent 使用 skill 时会先提示本地 skill 目录里的 `bin/docdev.cmd` 不存在，再改用 native launcher |
| 工作包目录 | `docs/changes/2026-06-18-suppress-skill-local-wrapper-warning/` |
| 最后更新 | 2026-06-18 |

## 1. 一句话目标

让 agent 在使用 `docs-driven-dev` skill 解析 CLI 时，只按 PATH / native launcher
入口合同执行。

## 2. 背景与问题

- 初始行为：agent 可能沿用旧兼容探测顺序，先报告 `bin/docdev.cmd` 不存在，再
  fallback 到 native launcher；功能可用，但提示和 D-025 之后的模型不一致。
- v0.1.11 已通过显式负向规则压制这类提示，但该规则仍把旧 wrapper 路径写进 skill
  操作上下文。
- 期望收益：skill 只描述应使用的 PATH / native launcher 入口；安装不可用的诊断条件是
  这些入口全部不可用。

## 3. 范围

### 3.1 本次要做

- 将 `skill/SKILL.md` 的 CLI Resolution 表达为正向入口合同。
- 同步项目级 SPEC / README 中的当前合同。
- 更新测试保护正向 skill 文案。

### 3.2 本次不做

- 保持 D-025 之后的 sync-skill 纯内容同步合同。
- 保持 native launcher、source checkout wrapper 和 Windows installer 的生成逻辑。

## 4. 用户场景 / 使用流程

| 场景 ID | 触发条件 | 期望结果 |
|---|---|---|
| S1 | agent 使用 `docs-driven-dev` skill 并需要运行 `docdev` | 直接使用 PATH 上的 `docdev` 或 native launcher；只有这些入口全部不可用时才诊断安装不可用 |

## 5. 功能需求

| ID | 需求 | 验收方式 | 状态 |
|---|---|---|---|
| R1 | `skill/SKILL.md` 明确写出 CLI resolution 只使用 PATH / native launcher 入口 | unit test / 文案检查 | 完成 |
| R2 | 根 SPEC / README 与该 skill 合同一致 | `docdev audit` / 文案检查 | 完成 |

## 6. 约束与不变式

1. **#1**: `sync-skill` 仍是 skill 内容同步，不承担 CLI 入口生成职责。
2. **#2**: 正常 agent CLI resolution 仍只依赖 `docdev` on PATH 或 native launcher。

## 7. 兼容性与默认行为

| 场景 | 默认行为 |
|---|---|
| agent 需要执行 CLI | skill 指导其使用 PATH 上的 `docdev` 或 native launcher |
| PATH / native launcher 都不可用 | 报告安装不可用并要求安装或修复 |

## 8. 验收标准

1. `skill/SKILL.md` 明确写出 CLI resolution 只使用 PATH / native launcher 入口。
2. Unit tests 和 `docdev audit` 通过。
3. GitHub Release `v0.1.12` 发布后可通过 native update 获取。
4. D-025 的 no skill-local wrapper 合同仍成立。

## 9. 开放问题

| ID | 问题 | 当前判断 | 是否阻塞实现 |
|---|---|---|---|
| Q1 | 是否应把 `bin/docdev.cmd` 放回 skill 目录 | 用户已确认 CLI 入口由 PATH / native launcher 承担 | 否 |

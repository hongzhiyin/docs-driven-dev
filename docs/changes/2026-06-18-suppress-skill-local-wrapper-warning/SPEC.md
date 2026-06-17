# SPEC - suppress skill-local wrapper warning

> 本文件描述本次需求应该满足什么。它不写实现细节、不追踪进度、不解释历史取舍。

## 0. 状态

| 字段 | 内容 |
|---|---|
| 状态 | 已发布 v0.1.11 |
| 需求来源 | 用户反馈：agent 使用 skill 时会先提示本地 skill 目录里的 `bin/docdev.cmd` 不存在，再改用 native launcher |
| 工作包目录 | `docs/changes/2026-06-18-suppress-skill-local-wrapper-warning/` |
| 最后更新 | 2026-06-18 |

## 1. 一句话目标

让 agent 在使用 `docs-driven-dev` skill 解析 CLI 时，不再把已废弃的 skill-local
`bin/docdev*` wrapper 缺失作为可见 fallback 提示。

## 2. 背景与问题

- 当前行为：`skill/SKILL.md` 已要求优先使用 `docdev` on PATH 或 native
  launcher，但没有显式禁止 agent 探测旧的 `<skill-dir>/bin/docdev*` wrapper。
- 问题：外层 agent 可能沿用旧兼容探测顺序，先报告 `bin/docdev.cmd` 不存在，再
  fallback 到 native launcher；功能可用，但提示和 D-025 之后的模型不一致。
- 期望收益：agent 不再输出这类误导性噪音；只有 `docdev` 和 native launcher 都不可用时，
  才把安装不可用作为问题报告。

## 3. 范围

### 3.1 本次要做

- 强化 `skill/SKILL.md` 的 CLI Resolution：不要探测或报告
  `<skill-dir>/bin/docdev*` 缺失。
- 同步项目级 SPEC / README 中的当前合同。
- 增加测试保护 skill 文案。

### 3.2 本次不做

- 不恢复 skill-local `bin/docdev*` wrapper 生成。
- 不改变 native launcher、source checkout wrapper 或 Windows installer 的生成逻辑。
- 不改变 native launcher、source checkout wrapper 或 Windows installer 的生成逻辑。

## 4. 用户场景 / 使用流程

| 场景 ID | 触发条件 | 期望结果 |
|---|---|---|
| S1 | agent 使用 `docs-driven-dev` skill 并需要运行 `docdev` | 直接使用 PATH 上的 `docdev` 或 native launcher；不先报告 skill 目录缺少 `bin/docdev.cmd` |

## 5. 功能需求

| ID | 需求 | 验收方式 | 状态 |
|---|---|---|---|
| R1 | `skill/SKILL.md` 明确禁止探测或报告 `<skill-dir>/bin/docdev*` 缺失 | unit test / 文案检查 | 完成 |
| R2 | 根 SPEC / README 与该 skill 合同一致 | `docdev audit` / 文案检查 | 完成 |

## 6. 约束与不变式

1. **#1**: `sync-skill` 仍不得生成 skill-local `bin/docdev*` wrapper。
2. **#2**: 正常 agent CLI resolution 仍只依赖 `docdev` on PATH 或 native launcher。

## 7. 兼容性与默认行为

| 场景 | 默认行为 |
|---|---|
| 旧 agent 仍尝试 skill-local wrapper | skill 应指导其跳过该探测；缺失不应作为用户可见问题 |
| PATH / native launcher 都不可用 | 报告安装不可用并要求安装或修复 |

## 8. 验收标准

1. `skill/SKILL.md` 明确写出不要探测或报告 `<skill-dir>/bin/docdev*` 缺失。
2. Unit tests 和 `docdev audit` 通过。
3. GitHub Release `v0.1.11` 发布并可通过 native update 获取。
4. D-025 的 no skill-local wrapper 合同仍成立。

## 9. 开放问题

| ID | 问题 | 当前判断 | 是否阻塞实现 |
|---|---|---|---|
| Q1 | 是否应把 `bin/docdev.cmd` 放回 skill 目录 | 用户已确认不要 `.cmd`，改为修复 skill 提示 | 否 |

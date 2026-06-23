# SPEC - skill-surface-runtime-trim

> 本文件描述本次需求应该满足什么。它不写实现细节、不追踪进度、不解释历史取舍。

## 0. 状态

| 字段 | 内容 |
|---|---|
| 状态 | 已完成 |
| 需求来源 | 用户反馈：当前 active skill 内容偏多，需要精简 |
| 工作包目录 | `docs/changes/2026-06-24-skill-surface-runtime-trim/` |
| 最后更新 | 2026-06-24 |

## 1. 一句话目标

让 agent 读取 `docs-driven-dev` active skill 时获得更短、更直接的 runtime 行动合同，而不是安装手册或完整教程。

## 2. 背景与问题

- 当前行为：`skill/SKILL.md` 约 338 行，已经移除了旧 wrapper 和源码安装说明，但仍包含 native install 命令、layout、private release、uninstall 细节、较长 delegation 和模板规则。
- 问题：active skill 是模型即时上下文；低频维护信息会挤占注意力，并让 skill 更像 README。
- 期望收益：skill 保持 workflow / judgment layer；安装、发布、维护细节留在 README / SPEC / DECISIONS。

## 3. 范围

### 3.1 本次要做

- 将 `skill/SKILL.md` 压缩到约 180-230 行。
- 保留 invocation、file contract、CLI resolution、delegation、Workflow A/B0/B/C、anti-patterns。
- 将 native install/update/uninstall 的详细命令和布局从 active skill 移出。
- 更新测试，保护 skill 行数上限和 forbidden detail。
- 更新 root SPEC / ROADMAP / DECISIONS，记录 active skill 精简边界。

### 3.2 本次不做

- 不改变 CLI / installer / sync / release 行为。
- 不删除 README 或 source-of-truth docs 中的维护者安装和发布说明。
- 不发布新 release；仅刷新本机 installed skill targets。

## 4. 用户场景 / 使用流程

| 场景 ID | 触发条件 | 期望结果 |
|---|---|---|
| S1 | agent 读取 active skill | 快速看到当前 workflow、CLI 入口、文档边界和门禁 |
| S2 | agent 需要安装或维护细节 | active skill 只给边界，详细说明去 README / source docs |

## 5. 功能需求

| ID | 需求 | 验收方式 | 状态 |
|---|---|---|---|
| R1 | Active skill 行数在 230 行以内 | `wc -l` + unit test | 完成 |
| R2 | Active skill 不包含 remote installer 命令、native layout、private release 或 uninstall 命令细节 | `rg` + unit test | 完成 |
| R3 | Active skill 仍包含 B0 small-fix、existing-code adoption、delegation、implementation gate 和 audit/verification guidance | unit test | 完成 |
| R4 | README / SPEC 保留安装和维护事实 | 现有测试 + audit | 完成 |

## 6. 约束与不变式

1. **#1**: Skill 继续是 decision/workflow layer；deterministic work 继续在 `docdev` CLI。
2. **#2**: Active skill 不暴露旧 wrapper、skill-local cmd、源码安装入口或实现 shim 细节。
3. **#3**: 精简不能弱化 docs-first gate、small-fix packet、delegation ownership 或 final verification。

## 7. 兼容性与默认行为

| 场景 | 默认行为 |
|---|---|
| 用户需要安装命令 | README 仍提供完整命令 |
| agent 需要 CLI | skill 继续给 `docdev` / native fallback resolution |
| 其他机器已安装旧 skill | 后续可通过 release/update 获取，当前先同步本机目标 |

## 8. 验收标准

1. `skill/SKILL.md` 不超过 230 行。
2. `python3 -m unittest discover -s tests` 和 `docdev audit` 通过。
3. Source 和 installed skill forbidden-term 搜索通过。

## 9. 开放问题

| ID | 问题 | 当前判断 | 是否阻塞实现 |
|---|---|---|---|
| Q1 | 是否要立即发版 | 本次先精简源码并同步本机，发版可后续处理 | 否 |

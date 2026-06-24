# SPEC - docs maintenance health

> 本文件描述本次需求应该满足什么。它不写实现细节、不追踪进度、不解释历史取舍。

## 0. 状态

| 字段 | 内容 |
|---|---|
| 状态 | 已完成 |
| 需求来源 | 用户要求继续精简 README/四件套，并把定期精简维护文档作为 docdev 能力 |
| 工作包目录 | `docs/changes/2026-06-24-docs-maintenance-health/` |
| 最后更新 | 2026-06-24 |

## 1. 一句话目标

让使用 docdev 的项目能定期发现维护文档过重、历史记录过多、入口说明混杂等问题，并由 agent 基于报告安全精简。

## 2. 背景与问题

- 当前行为：`docdev audit` 检查结构正确性，但不会提示 README、ROADMAP、DECISIONS、change packets 是否已经变成维护负担。
- 问题：docdev 自身的 README 和 ROADMAP 已累积大量安装、release、历史验证内容；其他项目长期使用 docs-driven workflow 也会遇到同类膨胀。
- 期望收益：CLI 给出稳定、可复用的 docs health signals；agent 负责判断哪些内容应精简、归档或保留。

## 3. 范围

### 3.1 本次要做

- 新增只读 `docdev docs-health <project>` 命令，统计 README、四件套、change packets 的行数和维护信号。
- 支持 `--json` 和 `--write-report`，报告写入 `<docs_dir>/_generated/docdev/docs-health.json`。
- 在当前仓库中精简 README 的用户入口和 ROADMAP 的当前视图。
- 更新 root SPEC / ARCHITECTURE / ROADMAP / DECISIONS / README / skill guidance，说明该能力边界。

### 3.2 本次不做

- 不让 CLI 自动改写或删除人类维护文档。
- 不删除 DECISIONS 历史正文。
- 不移动或压缩已有 `docs/changes/` 工作包目录。
- 不发布新 release。

## 4. 用户场景 / 使用流程

| 场景 ID | 触发条件 | 期望结果 |
|---|---|---|
| S1 | agent 准备定期精简 docs-driven 项目文档 | 先运行 `docdev docs-health <project>`，根据报告区分入口精简、历史归档和 append-only 保留 |
| S2 | 维护者希望机器可读报告 | 使用 `--json` 或 `--write-report` 获取稳定字段 |

## 5. 功能需求

| ID | 需求 | 验收方式 | 状态 |
|---|---|---|---|
| R1 | `docs-health` 输出 README、SPEC、ARCHITECTURE、ROADMAP、DECISIONS 行数 | 单元测试 / 手工命令 | 已批准 |
| R2 | `docs-health` 统计 change packet 数量、总行数和最大工作包 | 单元测试 / 手工命令 | 已批准 |
| R3 | `docs-health` 给出 deterministic signals，不做自动改写 | 单元测试 | 已批准 |
| R4 | `--write-report` 只写入 `_generated/docdev/` | 单元测试 | 已批准 |
| R5 | 当前 README/ROADMAP 精简后仍保留安装、使用、维护入口和 release 历史可追溯性 | audit / 人工检查 | 已批准 |

## 6. 约束与不变式

1. **#1**: `docs-health` 是报告能力，不是自动精简器；人类/agent 判断仍负责实际改写。
2. **#2**: 生成报告只能写入 `<docs_dir>/_generated/docdev/`。
3. **#3**: DECISIONS 继续 append-only；精简只可添加索引/摘要，不应删除旧决策正文。

## 7. 兼容性与默认行为

| 场景 | 默认行为 |
|---|---|
| 缺少 README | 报告四件套和 change packets，不报错 |
| 缺少部分四件套 | 仍输出存在文件的 metrics；结构错误交给 `docdev audit` |
| 文档超过阈值 | 输出 review signal，不改变退出码 |
| 用户需要机器可读输出 | 使用 `--json` 或 `--write-report` |

## 8. 验收标准

1. `docdev docs-health /Users/chihoyo/Project/docs-driven-dev` 能输出当前维护文档健康摘要。
2. `docdev docs-health --write-report` 在 `docs/_generated/docdev/docs-health.json` 生成 JSON。
3. README 明显更短，并把 maintainer/release 细节从首页正文降噪。
4. ROADMAP 当前视图不再要求读者滚过全部历史 step 才理解当前状态。
5. 单元测试和 `docdev audit` 通过。

## 9. 开放问题

| ID | 问题 | 当前判断 | 是否阻塞实现 |
|---|---|---|---|
| Q1 | 是否未来增加自动归档命令 | 本次先不做；需要单独设计安全策略 | 否 |

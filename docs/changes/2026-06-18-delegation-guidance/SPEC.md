# SPEC - delegation guidance

> 本文件描述本次需求应该满足什么。它不写实现细节、不追踪进度、不解释历史取舍。

## 0. 状态

| 字段 | 内容 |
|---|---|
| 状态 | 已发布 v0.1.13 |
| 需求来源 | 用户希望在 docdev skill 中加入 subagent 协作指导，让主 agent 更关注全局，subagent 处理局部调研、实现或文档一致性工作 |
| 工作包目录 | `docs/changes/2026-06-18-delegation-guidance/` |
| 最后更新 | 2026-06-18 |

## 1. 一句话目标

让 `docs-driven-dev` skill 在平台支持 sub-agents 时，提供可选的 delegation guidance：
主 agent 继续负责全局合同和最终验收，subagent 承担边界清楚的局部工作。

## 2. 背景与问题

- 当前行为：`skill/SKILL.md` 只在 Workflow B 下说明可委派边界清楚的 read-only research。
- 问题：对于较宽的实现任务，主 agent 可能需要同时保持 SPEC / ROADMAP / DECISIONS 全局一致性，又要处理局部代码或文档细节；现有 guidance 没有说明 subagent 可以承担哪些局部工作，以及主 agent 保留哪些责任。
- 期望收益：agent 能更稳定地把主上下文用于意图、范围、取舍和验收；subagent 用于局部调研、已批准的窄范围实现、文档一致性检查或测试失败定位。

## 3. 范围

### 3.1 本次要做

- 在 `skill/SKILL.md` 中增加 `Delegation Guidance`，描述主 agent ownership 和 subagent 适用任务。
- 在根 `docs/SPEC.md` 中记录 delegation 是 skill 层 workflow guidance，不属于 CLI 确定性职责。
- 在 README 或测试中补充对该 guidance 的可发现性和回归保护。
- 同步本机 installed skill targets。
- 发布 `v0.1.13`，让 fresh install 和 `docdev update` 获取该 guidance。

### 3.2 本次不做

- 不实现自动 subagent 调度、任务队列或 CLI orchestration。
- 不要求所有任务都使用 subagent。
- 不让 subagent 独立决定产品取舍、implementation approval、DECISIONS 最终结论或验收结果。
- 不实现额外 CLI 行为或发布自动 subagent 调度功能。

## 4. 用户场景 / 使用流程

| 场景 ID | 触发条件 | 期望结果 |
|---|---|---|
| S1 | agent 处理范围较宽的 existing-project requirement | 主 agent 建立/更新 change packet 后，可以把边界清楚的调研、实现 slice、文档一致性检查或测试失败定位交给 subagent |
| S2 | subagent 返回局部结果 | 主 agent review 结果，合并到 change packet、最终 diff、verification 和用户说明中 |

## 5. 功能需求

| ID | 需求 | 验收方式 | 状态 |
|---|---|---|---|
| R1 | Skill 明确主 agent owns 用户意图、SPEC invariants、scope、implementation gate、DECISIONS、最终验收和最终说明 | unit test / 文案检查 | 完成 |
| R2 | Skill 明确 subagent 可用于 read-only research、已批准的窄范围 implementation slice、文档一致性检查、测试失败定位 | unit test / 文案检查 | 完成 |
| R3 | Skill 明确委派前需要带清楚目标、文件范围、写入权限、验收条件，subagent 返回 changed files / findings / tests / uncertainty | unit test / 文案检查 | 完成 |
| R4 | SPEC / README 与 skill 的 delegation boundary 一致 | `docdev audit` / 文案检查 | 完成 |

## 6. 约束与不变式

1. **#1**: Skill 继续负责 workflow 和 judgment；CLI 继续只负责确定性 filesystem、numbering、audit、sync、release/install/update 工作。
2. **#2**: docs-driven workflow 的 source-of-truth、implementation gate、DECISIONS 和 verification 仍由主 agent 收束。
3. **#3**: Delegation guidance 是可选协作模式，不改变单 agent 完整执行 docs-driven workflow 的能力。

## 7. 兼容性与默认行为

| 场景 | 默认行为 |
|---|---|
| 平台不支持 sub-agents | 主 agent 按既有 workflow 独立完成 |
| 任务范围窄且上下文压力低 | 主 agent 可以不委派 |
| subagent 完成局部工作 | 主 agent review 后再更新 source-of-truth docs、verification 和最终说明 |

## 8. 验收标准

1. `skill/SKILL.md` 包含清楚的 `Delegation Guidance`，并区分主 agent ownership 与 subagent task slices。
2. 根 SPEC / README / tests 与该 guidance 一致。
3. `PYTHONPATH=src python3 -m unittest discover -s tests` 通过。
4. `PYTHONPATH=src python3 -m docs_driven_dev.cli audit /Users/chihoyo/Project/docs-driven-dev` 通过。
5. 本机 Codex/Cursor/Agents/Claude installed skill targets 同步到新 guidance。
6. GitHub Release `v0.1.13` 已发布并可通过 native update 获取。

## 9. 开放问题

| ID | 问题 | 当前判断 | 是否阻塞实现 |
|---|---|---|---|
| Q1 | 是否发布新 release | 用户已明确要求提交、推送并发布；发布 `v0.1.13` | 否 |

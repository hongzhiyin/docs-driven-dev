# ROADMAP - skill-surface-hide-wrapper-history

> 本文件追踪本次需求做到哪一步。它承接 SPEC 的验收标准，记录调研、门禁、任务和验证结果。

## 0. 当前状态

**阶段 / Phase**: 已完成
**当前 Step / Current Step**: Step 5 complete - 移除源码安装说明并提升 delegation guidance
**ARCHITECTURE 省略理由 / Architecture Omission Reason**: 本次只调整 active 文案和测试保护，不改变模块边界、数据流、CLI 入口实现、installer、sync 或 uninstall 行为。

## 1. Gates

### Pre-Implementation Gate

- [x] 用户目标已用一句话确认
- [x] 范围和非目标已写入 SPEC
- [x] 现有实现、调用点、测试和配置已调研
- [x] 关键约束 / 不变式已写入 SPEC
- [x] 需要的 DECISIONS 条目已记录或标记为阻塞
- [x] 实现步骤和验收方式已写清
- [x] 用户已确认实现方案

### Completion Gate

- [x] 所有实施任务完成或有明确跳过理由
- [x] 验收标准逐条验证
- [x] 文档与最终实现一致
- [x] 剩余风险和后续工作已记录

## 2. 调研记录

| ID | 主题 | 发现 | 证据 / 文件 | 结论 |
|---|---|---|---|---|
| R-1 | active skill surface | `skill/SKILL.md` 当前还包含 `docdev.cmd`、legacy target、marker、source checkout launcher 等使用方不需要的维护细节 | `skill/SKILL.md` | 收敛为当前命令入口和 workflow |
| R-2 | README usage surface | README 普通安装 / agent 使用面显式暴露 Windows `.cmd` 文件名 | `README.md` | 普通使用面改为 `docdev` 命令和 PowerShell fallback |
| R-3 | regression coverage | `test_docs_explain_path_and_replacement_contract` 当前要求 skill 中出现 `docdev.cmd` 和 sync cleanup 细节 | `tests/test_cli.py` | 更新为禁止 active surfaces 出现旧 skill-local entrypoint / cmd 类词 |

## 3. Step 状态总览

| Step | 内容 | 状态 |
|---|---|---|
| 0 | 建立需求工作包 | 完成 |
| 1 | 澄清需求与范围 | 完成 |
| 2 | 调研既有实现 | 完成 |
| 3 | 收敛 active guidance | 完成 |
| 4 | 验证与收尾 | 完成 |
| 5 | 移除源码安装说明并提升 delegation guidance | 完成 |

---

## Step 0 - 建立需求工作包

**Goal**: 创建 SPEC / ROADMAP / DECISIONS，并决定是否需要 ARCHITECTURE。

**Tasks**:
- [x] 初始化工作包文档
- [x] 记录 ARCHITECTURE 是否需要及理由

**Acceptance**:
1. 工作包目录存在，且文档结构清晰。

---

## Step 1 - 澄清需求与范围

**Goal**: 把粗略需求转成可验收的行为描述。

**Tasks**:
- [x] 补全 SPEC 一句话目标
- [x] 补全范围 / 非目标
- [x] 列出开放问题

**Acceptance**:
1. 用户确认方向：skill / active guidance 不暴露旧 wrapper 或 skill-local cmd 类表述。

---

## Step 2 - 调研既有 active guidance

**Goal**: 找到会诱导 agent 关注旧入口或实现细节的活跃文本和测试断言。

**Tasks**:
- [x] 搜索 `skill/SKILL.md`、README、SPEC、测试中的 wrapper / cmd / marker / legacy wording
- [x] 区分 active guidance 与历史 source-of-truth 记录

**Acceptance**:
1. 需要修改的 active surface 和保留的维护层事实已区分清楚。

---

## Step 3 - 收敛 active guidance

**Goal**: 让 skill 和 README 普通使用面只描述当前命令入口，不解释旧迁移细节。

**Tasks**:
- [x] 修改 `skill/SKILL.md`
- [x] 修改 README 普通使用和 agent 使用面
- [x] 更新 root SPEC / ROADMAP / DECISIONS
- [x] 更新回归测试

**Acceptance**:
1. Active skill/README surface 不含旧 skill-local entrypoint 或 cmd 类表述。

---

## Step 4 - 验证与收尾

**Goal**: 用测试、audit 和搜索证明修改达到用户要求。

**Tasks**:
- [x] 运行单元测试
- [x] 运行 `docdev audit`
- [x] 搜索 active surface 中旧 entrypoint / skill-local cmd 类表述
- [x] 记录验证结果和剩余风险

**Acceptance**:
1. 验证记录完整，剩余风险明确。

## 4. 验证记录

| 验收项 | 验证方式 | 结果 | 备注 |
|---|---|---|---|
| SPEC-1 | forbidden-term `rg` over `skill/SKILL.md` and README | 通过 | 无输出；命令返回 1 表示没有匹配 |
| SPEC-2 | `PYTHONPATH=src python3 -m unittest tests.test_cli.CliTests.test_docs_explain_path_and_replacement_contract` | 通过 | 1 test OK |
| SPEC-3 | `python3 -m unittest discover -s tests` | 通过 | 40 tests OK |
| SPEC-4 | `PYTHONPATH=src python3 -m docs_driven_dev.cli audit /Users/chihoyo/Project/docs-driven-dev` | 通过 | No findings |
| SPEC-5 | `./scripts/sync_skill.sh --targets codex,cursor,agents,claude --force` | 通过 | 四个本机 skill target 已刷新 |
| SPEC-6 | installed `SKILL.md` forbidden-term `rg` + `find */bin/docdev*` | 通过 | 旧入口关键词无匹配；无 skill-local `bin/docdev*` 文件 |
| SPEC-7 | `PYTHONPATH=src python3 -m unittest tests.test_cli.CliTests.test_skill_documents_delegation_guidance tests.test_cli.CliTests.test_docs_explain_path_and_replacement_contract` | 通过 | Delegation 顶层位置和 active skill 源码安装 forbidden terms 均覆盖 |
| SPEC-8 | `python3 -m unittest discover -s tests` | 通过 | 40 tests OK |
| SPEC-9 | `PYTHONPATH=src python3 -m docs_driven_dev.cli audit /Users/chihoyo/Project/docs-driven-dev` | 通过 | No findings |
| SPEC-10 | source `skill/SKILL.md` source-install forbidden-term `rg` | 通过 | 无输出；命令返回 1 表示没有匹配 |
| SPEC-11 | source `skill/SKILL.md` + README old wrapper/cmd forbidden-term `rg` | 通过 | 无输出；命令返回 1 表示没有匹配 |
| SPEC-12 | installed Codex/Cursor/Agents/Claude `SKILL.md` source-install 和 old wrapper/cmd forbidden-term `rg` + `find */bin/docdev*` | 通过 | 无源码安装词、无旧入口词、无 `bin/docdev*` 文件；Delegation 在 Workflow A 前 |

---

## Step 5 - 移除源码安装说明并提升 delegation guidance

**Goal**: 让 active skill 只保留 runtime workflow 和当前命令入口，同时把 subagent 使用规则作为
全局 workflow guidance，而不是 Workflow B 的局部附属说明。

**Tasks**:
- [x] 删除 `skill/SKILL.md` 中的 `Source Checkout Install（源码开发安装）` section。
- [x] 将 `Delegation Guidance（委派指导）` 移到 workflows 之前，并表述为平台支持且任务可切分时优先考虑。
- [x] 更新 root SPEC / ROADMAP / DECISIONS，记录 active skill surface 新边界。
- [x] 更新测试，禁止 active skill 中出现源码 checkout 开发安装命令，并验证 delegation section 位置。
- [x] 运行测试、audit、forbidden-term 搜索，并同步本机已安装 skill 目标。

**Acceptance**:
1. `skill/SKILL.md` 不包含 `Source Checkout Install`、源码 checkout 开发安装命令或 `.venv` 维护入口。
2. `Delegation Guidance（委派指导）` 是顶层 section，位于 Workflow A/B/C 之前。
3. Unit tests、`docdev audit`、source/installed skill forbidden-term 搜索均通过。

## 5. 风险与后续

| ID | 风险 / 后续 | 影响 | 处理 |
|---|---|---|---|
| F-1 | 历史 docs 仍会出现 wrapper/cmd 迁移记录 | 全仓库搜索仍会命中历史 source-of-truth | 接受；active surface 搜索单独验证 |
| F-2 | 其他机器需要 release/update 才能拿到 wording cleanup | 源码修改不会自动刷新已发布 artifact | 后续可发布 patch release |

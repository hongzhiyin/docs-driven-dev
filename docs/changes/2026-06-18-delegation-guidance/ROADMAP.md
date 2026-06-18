# ROADMAP - delegation guidance

> 本文件追踪本次需求做到哪一步。它承接 SPEC 的验收标准，记录调研、门禁、任务和验证结果。

## 0. 当前状态

**阶段 / Phase**: 发布中
**当前 Step / Current Step**: Step 5 - 发布 v0.1.13
**ARCHITECTURE 省略理由 / Architecture Omission Reason**: 本次只调整 skill workflow guidance、SPEC/README 合同和测试断言；不改变模块边界、数据流、CLI 命令、配置、安装路径或迁移行为。

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
| R-1 | 当前 skill 指导 | 现有 `Bounded Read-Only Research` 只覆盖 read-only sub-agent research | `skill/SKILL.md` | 扩展为更完整的 delegation guidance |
| R-2 | 项目边界 | SPEC 已声明 skill owns workflow judgment，CLI owns deterministic filesystem/numbering/audit/sync | `docs/SPEC.md` | delegation guidance 应属于 skill 层，不进入 CLI |
| R-3 | 测试覆盖 | `tests/test_cli.py` 已有 skill 文案回归测试 | `tests/test_cli.py` | 在既有 skill guidance 测试附近增加 delegation 断言 |

## 3. Step 状态总览

| Step | 内容 | 状态 |
|---|---|---|
| 0 | 建立需求工作包 | 完成 |
| 1 | 澄清需求与范围 | 完成 |
| 2 | 调研既有实现 | 完成 |
| 3 | 实施 skill/docs/test 文案 | 完成 |
| 4 | 验证与同步 installed skill | 完成 |
| 5 | 发布 v0.1.13 | 进行中 |

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

**Goal**: 把用户确认的优化方案转成可验收的行为描述。

**Tasks**:
- [x] 补全 SPEC 一句话目标
- [x] 补全范围 / 非目标
- [x] 列出开放问题

**Acceptance**:
1. SPEC 说明主 agent ownership、subagent 适用任务和非目标。

---

## Step 2 - 调研既有实现

**Goal**: 确认 delegation guidance 应落在 skill/docs/tests，而不是 CLI。

**Tasks**:
- [x] 读取当前 installed/source skill 中的 sub-agent guidance。
- [x] 读取根 SPEC 的 skill/CLI boundary。
- [x] 定位现有 skill 文案测试。

**Acceptance**:
1. 调研记录说明本次不需要 CLI/ARCHITECTURE 改动。

---

## Step 3 - 实施 skill/docs/test 文案

**Goal**: 增加可执行、可回归测试保护的 delegation guidance。

**Tasks**:
- [x] 更新 `skill/SKILL.md`。
- [x] 更新根 `docs/SPEC.md` 和 README。
- [x] 更新 `tests/test_cli.py`。
- [x] 记录根 DECISIONS 和本 packet DECISIONS。

**Acceptance**:
1. Skill 文案区分 main agent owns 与 subagent suitable slices。
2. 根 docs 和测试断言与 skill 文案一致。

---

## Step 4 - 验证与同步 installed skill

**Goal**: 验证源码合同并刷新本机 agent homes。

**Tasks**:
- [x] 运行目标 unit test。
- [x] 运行完整 unit tests。
- [x] 运行 `docdev audit`。
- [x] 运行 `./scripts/sync_skill.sh --targets codex,cursor,agents,claude --force`。
- [x] 检查 installed skill targets 包含新 guidance。

**Acceptance**:
1. Unit tests 通过。
2. `docdev audit` 无 findings。
3. Codex/Cursor/Agents/Claude installed skill targets 已同步。

## 4. 验证记录

| 验收项 | 验证方式 | 结果 | 备注 |
|---|---|---|---|
| SPEC-1 | `PYTHONPATH=src python3 -m unittest tests.test_cli.CliTests.test_skill_documents_delegation_guidance` | 通过 | 新增 delegation guidance 断言 |
| SPEC-2 | `PYTHONPATH=src python3 -m unittest discover -s tests` | 通过 | 40 tests |
| SPEC-3 | `PYTHONPATH=src python3 -m docs_driven_dev.cli audit /Users/chihoyo/Project/docs-driven-dev` | 通过 | No findings |
| SPEC-4 | installed skill `rg` check | 通过 | Codex/Cursor/Agents/Claude `SKILL.md` 均包含 `Delegation Guidance（委派指导）` |
| SPEC-5 | `PYTHONPATH=src python3 -m docs_driven_dev.cli --version`; package release; local packaged install smoke | 通过 | `docdev 0.1.13`; local smoke install/init/audit passed; isolated skill targets include delegation guidance |

---

## Step 5 - 发布 v0.1.13

**Goal**: 让 release install/update 获取 delegation guidance。

**Tasks**:
- [x] Bump release metadata to `0.1.13`。
- [x] Run unit tests and project audit。
- [x] Package release assets。
- [x] Run local simulated install smoke。
- [ ] Commit, tag, push, and publish GitHub Release。
- [ ] Run public latest smoke。
- [ ] Refresh local native install and synced skill targets。

**Acceptance**:
1. GitHub Release `v0.1.13` published as latest.
2. Public latest smoke installs `0.1.13` and passes `init` plus `audit`.
3. Local `/Users/chihoyo/.local/bin/docdev --version` reports `docdev 0.1.13`.
4. Installed skill targets include `Delegation Guidance（委派指导）`.

## 5. 风险与后续

| ID | 风险 / 后续 | 影响 | 处理 |
|---|---|---|---|
| F-1 | 具体平台的 subagent 能力和权限模型不同 | Skill guidance 只能描述协作边界，不能保证所有平台都有相同执行能力 | 接受；用“平台支持时”和明确任务合同表达 |
| F-2 | 发布前 fresh install/latest update 仍拿不到该 guidance | 其他机器暂时落后于 source checkout | 通过 `v0.1.13` release 处理 |

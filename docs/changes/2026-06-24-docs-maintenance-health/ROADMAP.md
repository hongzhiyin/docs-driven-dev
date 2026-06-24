# ROADMAP - docs maintenance health

> 本文件追踪本次需求做到哪一步。它承接 SPEC 的验收标准，记录调研、门禁、任务和验证结果。

## 0. 当前状态

**阶段 / Phase**: completed
**当前 Step / Current Step**: Step 2 - verification complete
**ARCHITECTURE 省略理由 / Architecture Omission Reason**: 不省略；本次新增 CLI 命令和报告数据流。

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
| R-1 | 当前文档体积 | README 297 行，SPEC 457 行，ARCHITECTURE 386 行，ROADMAP 1307 行，DECISIONS 1964 行，changes 344K | `wc -l`, `du -sh` | 入口和当前进度视图最值得精简 |
| R-2 | 命令边界 | 现有 CLI 命令集中在 `commands.py`，audit/status 在 `audit.py` | `src/docs_driven_dev/commands.py`, `src/docs_driven_dev/audit.py` | 新增只读 report 命令更适合独立模块 |
| R-3 | 历史记录边界 | DECISIONS 是 append-only rationale ledger，ROADMAP 是当前进度但混入大量历史验证 | `docs/DECISIONS.md`, `docs/ROADMAP.md` | 不删旧决策；ROADMAP 首页应增加历史索引/压缩当前面 |

## 3. Step 状态总览

| Step | 内容 | 状态 |
|---|---|---|
| 0 | 建立需求工作包 | 完成 |
| 1 | 实施报告命令和当前文档精简 | 完成 |
| 2 | 验证与收尾 | 完成 |

---

## Step 0 - 建立需求工作包

**Goal**: 创建 SPEC / ROADMAP / DECISIONS / ARCHITECTURE，并明确自动化边界。

**Tasks**:
- [x] 初始化工作包文档
- [x] 记录 ARCHITECTURE 需要及理由

**Acceptance**:
1. 工作包目录存在，且文档结构清晰。

---

## Step 1 - 实施报告命令和当前文档精简

**Goal**: 让 docdev 能复用地提示维护文档过重，并先改善当前仓库入口。

**Tasks**:
- [x] 新增 `docs-health` CLI 命令和 tests
- [x] 更新 README / SPEC / ARCHITECTURE / ROADMAP / DECISIONS / skill guidance
- [x] 精简 README 用户入口
- [x] 压缩 ROADMAP 当前视图

**Acceptance**:
1. `docs-health` 命令输出 human summary、JSON、write-report。
2. README 和 ROADMAP 比当前版本更短且仍能定位维护细节。
3. DECISIONS 历史正文不删除。

---

## Step 2 - 验证与收尾

**Goal**: 验证命令、文档精简和 docs-driven 约束。

**Tasks**:
- [x] 运行完整单元测试
- [x] 运行 project audit
- [x] 运行 `docs-health --write-report`
- [x] 记录剩余风险

**Acceptance**:
1. 测试和 audit 通过。
2. generated report 位于 `_generated/docdev/`。
3. docs-health 不再报告 README/ROADMAP 过长。

## 4. 验证记录

| 验收项 | 验证方式 | 结果 | 备注 |
|---|---|---|---|
| SPEC-1 | `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests` | 通过 | 42 tests |
| SPEC-2 | `PYTHONPATH=src python3 -m docs_driven_dev.cli audit /Users/chihoyo/Project/docs-driven-dev` | 通过 | No findings |
| SPEC-3 | `PYTHONPATH=src python3 -m docs_driven_dev.cli docs-health /Users/chihoyo/Project/docs-driven-dev --write-report` | 通过 | wrote `docs/_generated/docdev/docs-health.json` |
| SPEC-4 | `wc -l README.md docs/ROADMAP.md skill/SKILL.md` | 通过 | README 127 lines, ROADMAP 144 lines, skill 189 lines |

## 5. 风险与后续

| ID | 风险 / 后续 | 影响 | 处理 |
|---|---|---|---|
| F-1 | 阈值过于主观 | 可能产生噪声 | 先作为 review signals，不作为 audit warnings |
| F-2 | 自动归档需求扩大 | 可能误删历史 | 后续单独设计，只做 opt-in 且保留归档 |

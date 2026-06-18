# ROADMAP - remove-wrapper-residual-guidance

> 本文件追踪本次需求做到哪一步。它承接 SPEC 的验收标准，记录调研、门禁、任务和验证结果。

## 0. 当前状态

**阶段 / Phase**: 完成
**当前 Step / Current Step**: Step 6 - 发布 v0.1.14 完成
**ARCHITECTURE 省略理由 / Architecture Omission Reason**: 本次只调整活跃文档指导和测试断言，不改变模块边界、数据流、CLI entrypoint、安装布局、配置或迁移行为。

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
| R-1 | 活跃 skill 残留 wording | Source Checkout Install 仍点名旧 skill-local launcher 作为清理示例 | `skill/SKILL.md` | 改成 current-target replacement 语义 |
| R-2 | README / SPEC 残留 wording | README 和 SPEC 的当前同步说明也点名旧 launcher 示例 | `README.md`, `docs/SPEC.md` | 与 skill 使用同一套正向表述 |
| R-3 | 测试断言 | `test_docs_explain_path_and_replacement_contract` 仍保护旧 launcher 文案 | `tests/test_cli.py` | 更新为保护 current-target replacement 文案 |
| R-4 | 历史记录 | ROADMAP / DECISIONS 有大量 superseded launcher 背景 | `docs/ROADMAP.md`, `docs/DECISIONS.md` | 历史保留，当前 step 说明修复边界 |

## 3. Step 状态总览

| Step | 内容 | 状态 |
|---|---|---|
| 0 | 建立需求工作包 | 完成 |
| 1 | 澄清需求与范围 | 完成 |
| 2 | 调研既有实现 | 完成 |
| 3 | 形成并确认方案 | 完成 |
| 4 | 实施文档与测试 | 完成 |
| 5 | 验证与收尾 | 完成 |
| 6 | 发布 v0.1.14 | 完成 |

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

**Goal**: 把“还有旧 skill-local launcher 残留提示”转成可验收的活跃指导修复。

**Tasks**:
- [x] 补全 SPEC 一句话目标
- [x] 补全范围 / 非目标
- [x] 列出开放问题

**Acceptance**:
1. SPEC 的目标、范围和非目标清楚。

---

## Step 2 - 调研既有实现

**Goal**: 找出当前文档和测试里仍会让 agent 看到旧 skill-local launcher 路径的活跃来源。

**Tasks**:
- [x] 搜索 skill / README / SPEC / tests 中的旧 launcher wording
- [x] 区分当前操作指导和历史记录

**Acceptance**:
1. 每个需要修改的活跃文件都有证据记录。

---

## Step 3 - 形成并确认方案

**Goal**: 选择只改活跃指导、保留历史记录的窄范围方案。

**Tasks**:
- [x] 在 root DECISIONS 记录 D-039
- [x] 在本工作包 DECISIONS 记录 D-001
- [x] 写清 verification plan

**Acceptance**:
1. 方案能消除活跃 guidance 里的旧路径锚点，同时保留 native Windows `docdev.cmd` 正确说明。

---

## Step 4 - 实施文档与测试

**Goal**: 更新活跃文档和测试断言。

**Tasks**:
- [x] 更新 `skill/SKILL.md`
- [x] 更新 `README.md`
- [x] 更新 `docs/SPEC.md`
- [x] 更新 `docs/ROADMAP.md` / `docs/DECISIONS.md`
- [x] 更新 `tests/test_cli.py`

**Acceptance**:
1. Active skill 不再用旧 skill-local launcher 示例解释当前 sync 行为。
2. 测试断言保护新的 current-target replacement 文案。

---

## Step 5 - 验证与收尾

**Goal**: 跑完自动化验证、同步本机 installed skill，并记录结果。

**Tasks**:
- [x] 运行 targeted unit test
- [x] 运行 full unit test
- [x] 运行 `docdev audit`
- [x] 同步本机 Codex/Cursor/Agents/Claude skill targets
- [x] 记录验证结果和剩余风险

**Acceptance**:
1. Tests、audit 和 installed skill content 检查都通过。

## 4. 验证记录

| 验收项 | 验证方式 | 结果 | 备注 |
|---|---|---|---|
| SPEC-1 | `PYTHONPATH=src python3 -m unittest tests.test_cli.CliTests.test_docs_explain_path_and_replacement_contract` | 通过 | 1 test OK |
| SPEC-2 | `PYTHONPATH=src python3 -m unittest discover -s tests` | 通过 | 40 tests OK |
| SPEC-3 | `PYTHONPATH=src python3 -m docs_driven_dev.cli audit /Users/chihoyo/Project/docs-driven-dev` | 通过 | No findings |
| SPEC-4 | installed skill `rg` check | 通过 | Codex/Cursor/Agents/Claude skill 含新 replacement wording，不含旧 skill-local launcher wording；`find` for `*/bin/docdev*` 无输出 |
| SPEC-5 | `PYTHONPATH=src python3 -m docs_driven_dev.cli --version`; package release; local packaged install smoke | 通过 | `docdev 0.1.14`; local smoke install/init/audit passed; isolated skill targets include active guidance cleanup |
| SPEC-6 | GitHub Release `v0.1.14` publication and public latest smoke | 通过 | Release URL recorded in root ROADMAP Step 6u; public latest install/init/audit passed |
| SPEC-7 | `/Users/chihoyo/.local/bin/docdev update --version 0.1.14` and installed skill content check | 通过 | Local native install refreshed; four skill targets contain active guidance cleanup |

---

## Step 6 - 发布 v0.1.14

**Goal**: 让 fresh install 和 `docdev update` 获取本次 active guidance cleanup。

**Tasks**:
- [x] Bump release metadata to `0.1.14`
- [x] Run tests, audit, package, and local packaged smoke
- [x] Commit, tag, push, and publish GitHub Release `v0.1.14`
- [x] Run public latest smoke
- [x] Update local native install and verify installed skill content

**Acceptance**:
1. GitHub Release `v0.1.14` published as latest.
2. Public latest smoke installs `0.1.14` and passes `init` plus `audit`.
3. Local `/Users/chihoyo/.local/bin/docdev --version` reports `docdev 0.1.14`.
4. Local installed skill targets contain the active guidance cleanup.

## 5. 风险与后续

| ID | 风险 / 后续 | 影响 | 处理 |
|---|---|---|---|
| F-1 | 其他机器仍运行 v0.1.13 release skill | 需要新 release 才能通过 `docdev update` 获取修复 | 已通过 `v0.1.14` release 处理 |

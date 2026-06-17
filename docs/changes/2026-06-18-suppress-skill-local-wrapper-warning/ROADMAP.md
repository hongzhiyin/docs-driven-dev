# ROADMAP - suppress skill-local wrapper warning

> 本文件追踪本次需求做到哪一步。它承接 SPEC 的验收标准，记录调研、门禁、任务和验证结果。

## 0. 当前状态

**阶段 / Phase**: 完成
**当前 Step / Current Step**: Step 5 - 发布完成
**ARCHITECTURE 省略理由 / Architecture Omission Reason**: 本次只强化 skill/docs 中的 CLI resolution 指令，不改变模块边界、数据流、launcher 生成、安装路径、配置或迁移行为。

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
| R-1 | 当前 skill 指令 | `skill/SKILL.md` 已优先列出 `docdev` / native launcher，但未显式说不要探测 `<skill-dir>/bin/docdev*` | `skill/SKILL.md` | 增加负向规则避免旧探测噪音 |
| R-2 | 当前同步合同 | `sync-skill` 不生成 `bin/docdev`, `bin/docdev.ps1`, `bin/docdev.cmd` | `docs/SPEC.md`, `docs/ROADMAP.md`, `tests/test_cli.py` | 不应通过恢复 wrapper 解决 |
| R-3 | 测试覆盖 | `test_docs_explain_path_and_replacement_contract` 已保护 CLI resolution 文案 | `tests/test_cli.py` | 在既有测试中增加防回归断言 |

## 3. Step 状态总览

| Step | 内容 | 状态 |
|---|---|---|
| 0 | 建立需求工作包 | 完成 |
| 1 | 澄清需求与范围 | 完成 |
| 2 | 调研既有实现 | 完成 |
| 3 | 实施文案与测试 | 完成 |
| 4 | 验证与收尾 | 完成 |
| 5 | 发布 v0.1.11 | 完成 |

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
1. 用户确认 SPEC 的目标、范围和非目标。

---

## Step 2 - 调研既有实现

**Goal**: 确认这个问题应通过 skill/docs 指令修复，而不是恢复 wrapper。

**Tasks**:
- [x] 查找 `bin/docdev.cmd`、skill-local wrapper、native launcher 相关文案。
- [x] 确认当前 installed skill 目录不包含 wrapper 是预期状态。
- [x] 确认需要更新的测试位置。

**Acceptance**:
1. 调研记录说明缺失 wrapper 是预期状态，用户可见提示才是问题。

---

## Step 3 - 实施文案与测试

**Goal**: 让 skill 明确跳过旧 wrapper 探测，并用测试保护该合同。

**Tasks**:
- [x] 更新 `skill/SKILL.md`。
- [x] 更新 `docs/SPEC.md` 和 `README.md`。
- [x] 更新 `tests/test_cli.py` 防回归断言。

**Acceptance**:
1. 文案明确禁止探测或报告 `<skill-dir>/bin/docdev*` 缺失。

---

## Step 4 - 验证与收尾

**Goal**: 验证小修复没有破坏 docs-driven contract。

**Tasks**:
- [x] 运行目标 unit test。
- [x] 运行完整 unit tests。
- [x] 运行 `docdev audit`。

**Acceptance**:
1. Unit tests 通过。
2. `docdev audit` 无 findings。

---

## Step 5 - 发布 v0.1.11

**Goal**: 让其他机器通过 latest release / native update 获得本次 skill 指令修复。

**Tasks**:
- [x] Bump release metadata to `0.1.11`。
- [x] Package release assets。
- [x] Run local and public install smoke。
- [x] Commit, tag, push, and publish GitHub Release。
- [x] Refresh local native install and synced skill targets。

**Acceptance**:
1. GitHub Release `v0.1.11` published as latest.
2. Local `/Users/chihoyo/.local/bin/docdev --version` reports `docdev 0.1.11`.
3. Installed skill targets include the new no-probe instruction.

## 4. 验证记录

| 验收项 | 验证方式 | 结果 | 备注 |
|---|---|---|---|
| SPEC-1 | `PYTHONPATH=src python3 -m unittest tests.test_cli.CliTests.test_docs_explain_path_and_replacement_contract` | 通过 | 保护 skill / README 文案 |
| SPEC-2 | `PYTHONPATH=src python3 -m unittest discover -s tests` | 通过 | 39 tests |
| SPEC-3 | `PYTHONPATH=src python3 -m docs_driven_dev.cli audit /Users/chihoyo/Project/docs-driven-dev` | 通过 | No findings |
| SPEC-4 | GitHub Release `v0.1.11` publication and public latest smoke | 通过 | Release URL recorded in root ROADMAP Step 6o |
| SPEC-5 | `/Users/chihoyo/.local/bin/docdev update --version 0.1.11` and installed skill content check | 通过 | Local native install refreshed |

## 5. 风险与后续

| ID | 风险 / 后续 | 影响 | 处理 |
|---|---|---|---|
| F-1 | 外层 agent resolver 若硬编码自己的探测顺序，skill 文案只能降低模型复现概率，不能强制修改平台代码 | 仍可能看到旧噪音 | 若复现，需定位外层 resolver 并修复其探测顺序 |

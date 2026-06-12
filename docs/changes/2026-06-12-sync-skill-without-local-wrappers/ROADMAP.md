# ROADMAP - sync-skill 不再生成 skill-local wrappers

> 本文件追踪本次需求做到哪一步。它承接 SPEC 的验收标准，记录调研、门禁、任务和验证结果。

## 0. 当前状态

**阶段 / Phase**: 完成
**当前 Step / Current Step**: Step 4 - 验证与收尾完成
**ARCHITECTURE 省略理由 / Architecture Omission Reason**: 不省略。本次改变 `sync-skill` 的目录副作用和 agent CLI resolution 边界。

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
| R-1 | skill-local wrapper generation | `copy_skill()` 调用 `write_installed_skill_wrapper()`，会写 `bin/docdev*` | `src/docs_driven_dev/cli.py` | 删除函数和调用点 |
| R-2 | replacement cleanup | `copy_skill()` 对 marked/forced target 先删除目录再 copy，因此移除生成逻辑后旧 `bin/` 会自然消失 | `src/docs_driven_dev/cli.py` | 更新测试证明 stale `bin/` 被清理 |
| R-3 | tests | `test_copy_skill_writes_installed_wrapper` 明确断言 wrapper 存在 | `tests/test_cli.py` | 改为断言不生成 wrapper |
| R-4 | source wrapper | `scripts/install_cli.sh/.ps1` 只写源码 checkout 的 `.venv` CLI 入口 | `scripts/install_cli.*` | 保留，服务未发布源码验证 |
| R-5 | native launcher | remote installer 仍写 `~/.local/bin/docdev`，这是普通用户 CLI 入口 | `scripts/install_remote.sh/.ps1` | 保留 |

## 3. Step 状态总览

| Step | 内容 | 状态 |
|---|---|---|
| 0 | 建立需求工作包 | 完成 |
| 1 | 调研并确认边界 | 完成 |
| 2 | 移除 wrapper 生成并更新测试 | 完成 |
| 3 | 更新文档和同步 installed skills | 完成 |
| 4 | 验证与收尾 | 完成 |

---

## Step 0 - 建立需求工作包

**Goal**: 创建 SPEC / ROADMAP / DECISIONS，并决定是否需要 ARCHITECTURE。

**Tasks**:
- [x] 初始化工作包文档
- [x] 记录 ARCHITECTURE 是否需要及理由

**Acceptance**:
1. 工作包目录存在，且文档结构清晰。

---

## Step 1 - 调研并确认边界

**Goal**: 区分要删除的 skill-local wrapper 与要保留的源码/native CLI 入口。

**Tasks**:
- [x] 查找 wrapper 生成函数、调用点和测试。
- [x] 查找 source checkout wrapper 与 native launcher 的脚本。
- [x] 写清保留/删除边界。

**Acceptance**:
1. 第 3 类 skill-local wrapper 清理范围清楚，且不误删第 1/2 类入口。

---

## Step 2 - 移除 wrapper 生成并更新测试

**Goal**: 让 `sync-skill` 不再把 CLI wrapper 写入 skill target。

**Tasks**:
- [x] 删除 `write_installed_skill_wrapper()` 和只为它服务的 helper。
- [x] 从 `copy_skill()` 移除 wrapper 写入调用。
- [x] 更新测试，断言 `bin/docdev*` 不再生成，旧 `bin/` 可被 replacement 清理。

**Acceptance**:
1. `copy_skill()` 后目标目录没有 `bin/docdev*`。

---

## Step 3 - 更新文档和同步 installed skills

**Goal**: 让 skill/docs 与 CLI-first 模型一致，并清理本机已安装 skill 里的旧 wrapper。

**Tasks**:
- [x] 更新 README / SPEC / ARCHITECTURE / ROADMAP / DECISIONS / SKILL。
- [x] 运行 `./scripts/update_cli.sh --targets codex,cursor,agents,claude --force`，使 installed skill targets 删除旧 `bin/`。
- [x] 手工确认当前 installed skill target 不再有 `bin/docdev*`。

**Acceptance**:
1. `~/.codex/skills/docs-driven-dev/bin/docdev` 等旧 skill-local wrapper 不再存在。

---

## Step 4 - 验证与收尾

**Goal**: 确认 CLI-first 行为没有破坏 docs-driven-dev。

**Tasks**:
- [x] 运行单元测试。
- [x] 运行 `docdev doctor`。
- [x] 运行 `docdev audit /Users/chihoyo/Project/docs-driven-dev`。
- [x] 记录验证结果。

**Acceptance**:
1. 测试、doctor、audit 均通过。

## 4. 验证记录

| 验收项 | 验证方式 | 结果 | 备注 |
|---|---|---|---|
| SPEC-1 | `PYTHONPATH=src python3 -m unittest discover -s tests` | 通过 | 31 tests OK |
| SPEC-2 | `./scripts/update_cli.sh --targets codex,cursor,agents,claude --force` | 通过 | 安装源码 wrapper、测试、doctor/audit、sync、post-check 全部通过 |
| SPEC-3 | `/Users/chihoyo/.local/bin/docdev doctor` | 通过 | native 0.1.4 doctor OK |
| SPEC-4 | `/Users/chihoyo/.local/bin/docdev audit /Users/chihoyo/Project/docs-driven-dev` | 通过 | No findings |
| SPEC-5 | `test ! -e ~/.codex/skills/docs-driven-dev/bin/docdev` 等 installed target 检查 | 通过 | Codex/Cursor/agents 目标旧 wrapper 均不存在；Claude 继续 symlink 到 agents |

## 5. 风险与后续

| ID | 风险 / 后续 | 影响 | 处理 |
|---|---|---|---|
| F-1 | 旧文档历史仍提到 skill-local wrappers | 搜索会看到历史记录 | 接受；新增 D-025 和当前 docs 标明 supersede |
| F-2 | 某些已安装 skill target 如果不重 sync，旧 `bin/` 可能残留 | 其他机器可见旧入口 | 缓解：本机已运行 force sync；其他机器在下个 release 后用 `docdev update --sync-skill` |
| F-3 | v0.1.4 发布前 native install 曾停留在 v0.1.3 | 旧 native `docdev update --sync-skill` 可能用旧 release 逻辑 | 已通过 v0.1.4 release 和 real local `docdev update --sync-skill` 消除 |

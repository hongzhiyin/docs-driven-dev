# ROADMAP - Claude 直接复制同步

> 本文件追踪本次需求做到哪一步。它承接 SPEC 的验收标准，记录调研、门禁、任务和验证结果。

## 0. 当前状态

**阶段 / Phase**: 完成
**当前 Step / Current Step**: Step 5 complete; Claude target direct-copy sync verified
**ARCHITECTURE 省略理由 / Architecture Omission Reason**: 不省略。本次改变 `sync-skill` 对 Claude target 的同步数据流和替换语义。

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
| R-1 | Claude sync implementation | `cmd_sync_skill` 在 `claude` 不含 `agents` 时插入 `agents`，随后对 Claude 调用 `link_claude_to_agents()` | `src/docs_driven_dev/sync.py` | 需要移除 Claude 特判，改用通用 copy path |
| R-2 | Replacement safety | `copy_skill()` 已能在 `force=True` 时 unlink symlink 或 file，然后 copy source 并写 marker | `src/docs_driven_dev/sync.py` | 可复用现有 replacement 逻辑处理 legacy symlink |
| R-3 | Tests | 当前测试覆盖 symlink fallback，不覆盖 Claude-only copy | `tests/test_cli.py` | 需要替换测试语义 |
| R-4 | Docs | SPEC/ARCHITECTURE/README/skill 仍声明 Claude symlink/fallback 模型 | `docs/SPEC.md`, `docs/ARCHITECTURE.md`, `README.md`, `skill/SKILL.md` | 需要同步更新 source-of-truth 和用户说明 |

## 3. Step 状态总览

| Step | 内容 | 状态 |
|---|---|---|
| 0 | 建立需求工作包 | 完成 |
| 1 | 澄清需求与范围 | 完成 |
| 2 | 调研既有实现 | 完成 |
| 3 | 形成并确认方案 | 完成 |
| 4 | 实施代码与测试 | 完成 |
| 5 | 验证与收尾 | 完成 |

---

## Step 0 - 建立需求工作包

**Goal**: 创建 SPEC / ROADMAP / DECISIONS / ARCHITECTURE，记录 Claude sync 行为变更。

**Tasks**:
- [x] 初始化工作包文档
- [x] 保留 ARCHITECTURE，因为同步数据流会变化

**Acceptance**:
1. 工作包目录存在，且文档结构清晰。

---

## Step 1 - 澄清需求与范围

**Goal**: 把用户反馈转成可验收的同步行为。

**Tasks**:
- [x] 写明 Claude target 直接复制的目标行为
- [x] 写明不发布 release、不改变默认 target 集合、不移除 legacy uninstall 清理
- [x] 写明 legacy symlink 的 force replacement 兼容路径

**Acceptance**:
1. SPEC 包含目标、范围、非目标、场景和验收标准。

---

## Step 2 - 调研既有实现

**Goal**: 找到 Claude symlink 的代码、测试和文档入口。

**Tasks**:
- [x] 调研 `sync.py` 的 `link_claude_to_agents()` 和 `cmd_sync_skill()` 特判
- [x] 调研测试里 symlink fallback coverage
- [x] 调研 docs/README/skill 中 symlink 文案

**Acceptance**:
1. 调研记录列出会修改的代码和文档文件。

---

## Step 3 - 形成并确认方案

**Goal**: 选择直接复制 Claude target 的方案，并记录取舍。

**Tasks**:
- [x] 在本工作包 DECISIONS 写 D-001
- [x] 在 root DECISIONS 写 D-033，说明 D-003/D-015 的 Claude sync 模型被 supersede
- [x] 明确保留 legacy symlink uninstall cleanup

**Acceptance**:
1. 决策说明直接复制优于 symlink-first/fallback。

---

## Step 4 - 实施代码与测试

**Goal**: 删除 Claude symlink 特判并补覆盖。

**Tasks**:
- [x] 让 `cmd_sync_skill` 对 Claude 调用 `copy_skill()`
- [x] 移除 `link_claude_to_agents()` re-export
- [x] 增加 Claude-only copy 测试
- [x] 增加 legacy symlink force replacement 测试
- [x] 运行完整测试

**Acceptance**:
1. 针对 Claude sync 的新增/更新单元测试通过。

---

## Step 5 - 验证与收尾

**Goal**: 确认实现、文档和 audit 一致。

**Tasks**:
- [x] 运行完整 unit tests
- [x] 运行 project audit
- [x] 更新 root ROADMAP 和本工作包验证记录
- [x] 检查是否仍有当前行为文案宣称 Claude 会新建 symlink

**Acceptance**:
1. SPEC 验收标准全部有验证记录。

## 4. 验证记录

| 验收项 | 验证方式 | 结果 | 备注 |
|---|---|---|---|
| SPEC-1 | `PYTHONPATH=src python3 -m unittest tests.test_cli.CliTests.test_claude_sync_copies_without_agents_dependency tests.test_cli.CliTests.test_copy_skill_replaces_legacy_claude_symlink_when_forced` | 通过 | 覆盖 Claude-only copy 和 legacy symlink replacement |
| SPEC-2 | `python3 -m unittest discover -s tests` | 通过 | 39 tests OK |
| SPEC-3 | `PYTHONPATH=src python3 -m docs_driven_dev.cli audit /Users/chihoyo/Project/docs-driven-dev` | 通过 | No findings |
| SPEC-4 | `rg -n "Claude should use|Claude uses a symlink|link Claude target|link_claude|symlink failed|syncing agents first|shared-agents symlink|copy fallback when" docs README.md skill src tests` | 通过 | 仅剩测试断言、历史决策或本工作包旧状态说明 |

## 5. 风险与后续

| ID | 风险 / 后续 | 影响 | 处理 |
|---|---|---|---|
| F-1 | 只有同步 Claude 或 Agents 其中一个 target 时，两个目录可能暂时不同步 | 手动偏目标 sync 会产生版本差异 | 接受；默认 install/update 仍同步四个 targets，doctor 可查看每个 target |
| F-2 | 已发布 v0.1.9 不包含本次改动 | 其他机器通过旧 release 暂时拿不到该行为 | 已通过 root ROADMAP Step 6n 发布 `v0.1.10` 处理 |

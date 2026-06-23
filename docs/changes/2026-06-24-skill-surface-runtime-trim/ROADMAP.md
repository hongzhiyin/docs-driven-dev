# ROADMAP - skill-surface-runtime-trim

> 本文件追踪本次需求做到哪一步。它承接 SPEC 的验收标准，记录调研、门禁、任务和验证结果。

## 0. 当前状态

**阶段 / Phase**: 已完成
**当前 Step / Current Step**: Step 4 complete - 验证与同步 installed skill
**ARCHITECTURE 省略理由 / Architecture Omission Reason**: 本次只调整 active skill 文案、测试和 source-of-truth 记录，不改变模块边界、CLI 行为、installer、sync、release 或配置结构。

## 1. Gates

### Pre-Implementation Gate

- [x] 用户目标已用一句话确认
- [x] 范围和非目标已写入 SPEC
- [x] 现有 skill 行数、section 和测试断言已调研
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
| R-1 | skill length | `skill/SKILL.md` 当前 338 行 | `wc -l skill/SKILL.md` | 可压缩 |
| R-2 | verbose sections | Native install section 包含 install 命令、layout、private release、uninstall；step shape / decisions rules 也偏教程化 | `skill/SKILL.md` | 移出 active context |
| R-3 | tests | 测试仍要求 skill 包含部分 install/uninstall 细节 | `tests/test_cli.py` | 改成 README/SPEC 保留、skill 禁止 |

## 3. Step 状态总览

| Step | 内容 | 状态 |
|---|---|---|
| 0 | 建立需求工作包 | 完成 |
| 1 | 澄清范围和非目标 | 完成 |
| 2 | 调研 skill 结构和测试 | 完成 |
| 3 | 精简 skill 与测试 | 完成 |
| 4 | 验证与同步 installed skill | 完成 |

---

## Step 3 - 精简 skill 与测试

**Goal**: 把 active skill 压缩成 runtime contract，移除低频安装/维护教程。

**Tasks**:
- [x] 压缩 `skill/SKILL.md`。
- [x] 更新 root SPEC / ROADMAP / DECISIONS。
- [x] 更新回归测试，增加行数和 forbidden detail 检查。

**Acceptance**:
1. `skill/SKILL.md` 不超过 230 行。
2. active skill 不含 remote installer 命令、native layout、private release 或 uninstall command detail。

## 4. 验证记录

| 验收项 | 验证方式 | 结果 | 备注 |
|---|---|---|---|
| SPEC-1 | `wc -l skill/SKILL.md` | 通过 | 192 行，低于 230 行预算 |
| SPEC-2 | `python3 -m unittest discover -s tests` | 通过 | 40 tests OK |
| SPEC-3 | `PYTHONPATH=src python3 -m docs_driven_dev.cli audit /Users/chihoyo/Project/docs-driven-dev` | 通过 | No findings |
| SPEC-4 | source / installed forbidden-term `rg` | 通过 | source 和四个 installed `SKILL.md` 均无匹配 |
| SPEC-5 | `./scripts/sync_skill.sh --targets codex,cursor,agents,claude --force` | 通过 | Codex/Cursor/Agents/Claude 均已刷新为 192 行 skill |

## 5. 风险与后续

| ID | 风险 / 后续 | 影响 | 处理 |
|---|---|---|---|
| F-1 | 其他机器仍需 release/update 才能获得精简 skill | 源码和本机已同步不等于 published latest | 后续按需要发 patch release |

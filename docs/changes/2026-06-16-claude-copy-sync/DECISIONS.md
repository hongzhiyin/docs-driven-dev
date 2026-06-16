# DECISIONS - Claude 直接复制同步

> 本文件记录这次需求中为什么这么选。只写真实取舍，不为机械改动补仪式性决策。

## 维护规则

1. `D-XXX` 在本工作包内单调递增，不复用。
2. 每条记录 2-3 个真实选项；不要编造凑数选项。
3. 写清选择、理由、风险和对应文件。
4. 决策被推翻时，新增一条 D-XXX 引用旧决策，旧决策保留原文。

---

## D-001 - Step 3 - Claude target 改为直接复制

**日期 / Date**: 2026-06-16

**上下文 / Context**:
旧实现选择 Claude symlink 到 Agents target，Windows 上再 fallback 为复制。用户在更新时遇到 Claude symlink 相关报错，并明确希望 Claude 像其他 agent 一样同步 skill。

**选项 / Options**:
- A. 保留 symlink-first，仅改善 fallback/报错提示 - 改动较小，但继续保留平台权限和路径差异。
- B. Claude 与 Codex/Cursor/Agents 一样直接复制 skill - 行为一致，移除 symlink 依赖，但 Claude/Agents 不再共享同一个目录。

**选择 / Chosen**: B

**理由 / Rationale**:
- 用户目标是消除 symlink 相关更新报错，而不是只改善诊断。
- 统一使用 `copy_skill()` 可以复用已有 marker、force replacement、stale file cleanup 合同。
- `--targets claude` 不应隐藏地先修改 Agents target。

**风险 / Risks**:
- 手动只同步一个 target 时，Claude 与 Agents 可能短暂不一致。缓解：默认 install/update 仍同步 `codex,cursor,agents,claude`，doctor 输出每个 target 状态。
- 旧机器可能已有 Claude symlink。缓解：force sync 会 unlink 并复制，uninstall 继续把 legacy symlink 当作 owned target 清理。

**对应代码 / 文档**:
- SPEC §3, §5, §7
- ROADMAP Step 3-5
- ARCHITECTURE §3-5
- `src/docs_driven_dev/sync.py`
- `tests/test_cli.py`

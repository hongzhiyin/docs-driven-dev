# DECISIONS - sync-skill 不再生成 skill-local wrappers

> 本文件记录这次需求中为什么这么选。只写真实取舍，不为机械改动补仪式性决策。

## 维护规则

1. `D-XXX` 在本工作包内单调递增，不复用。
2. 每条记录 2-3 个真实选项；不要编造凑数选项。
3. 写清选择、理由、风险和对应文件。
4. 决策被推翻时，新增一条 D-XXX 引用旧决策，旧决策保留原文。

---

## D-001 - Step 1 - 移除 skill-local wrappers 而不提供兼容开关

**日期 / Date**: 2026-06-12

**上下文 / Context**:
native install 后，普通 agent 应只通过 `docdev` on `PATH` 或 `~/.local/bin/docdev`
运行 CLI。继续在 skill target 下生成 `bin/docdev*` 会让 skill 目录承担第二个 CLI
入口角色，和用户希望“以 CLI 的使用方式为准”不一致。

**选项 / Options**:
- A. 保留现状 - 对旧 source-sync 入口最兼容，但继续让 agent 可能依赖 skill-local wrappers。
- B. 加 `--with-compat-wrappers` opt-in - 给旧机器留后门，但会延续第三类入口和文档复杂度。
- C. 直接移除 skill-local wrapper 生成 - 行为最清楚；旧目标下的 `bin/` 在下一次 forced/marked sync 时被清理。

**选择 / Chosen**: C

**理由 / Rationale**:
- D-022 已规定跨机器 agent CLI resolution 不猜 wrappers；移除生成逻辑能让代码行为和文档合同一致。
- source checkout 本地 wrapper 仍保留在 `.venv` 中，维护者可以在 release 前运行当前源码。
- native launcher 仍保留在 `~/.local/bin/docdev`，普通用户入口不受影响。

**风险 / Risks**:
- 尚未同步的旧 skill 目录可能继续残留 `bin/`。缓解：本机运行 force sync；其他机器通过 `docdev update --sync-skill` 或 `docdev sync-skill --force` 清理。
- 历史 docs 仍提到旧 wrappers。缓解：当前 root docs 和 D-025 标明 supersede，而不重写历史。

**对应代码 / 文档**:
- SPEC §3.3, §3.5, §3.7
- ROADMAP Step 2
- `src/docs_driven_dev/cli.py`
- `tests/test_cli.py`
- `skill/SKILL.md`

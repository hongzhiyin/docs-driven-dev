# DECISIONS - suppress skill-local wrapper warning

> 本文件记录这次需求中为什么这么选。只写真实取舍，不为机械改动补仪式性决策。

## 维护规则

1. `D-XXX` 在本工作包内单调递增，不复用。
2. 每条记录 2-3 个真实选项；不要编造凑数选项。
3. 写清选择、理由、风险和对应文件。
4. 决策被推翻时，新增一条 D-XXX 引用旧决策，旧决策保留原文。

---

## D-001 - Step 1 - 修复 skill 指令而不是恢复 skill-local cmd

**日期 / Date**: 2026-06-18

**上下文 / Context**:
agent 使用 skill 时会先提示本地 skill 目录里的 `bin/docdev.cmd` 不存在，再改用 native
launcher。用户确认不希望把 `.cmd` 放回 skill 目录，而是修复 skill，让后续不要再报告这类
预期缺失。

**选项 / Options**:
- A. 恢复 `<skill-dir>/bin/docdev.cmd` - 可以满足旧探测逻辑，但会推翻 D-025，让 skill 目录再次承担 CLI 入口职责。
- B. 强化 skill / docs 指令，禁止探测或报告 `<skill-dir>/bin/docdev*` 缺失 - 保持 no-wrapper 合同，并降低 agent 复现旧噪音的概率。

**选择 / Chosen**: B

**理由 / Rationale**:
- 用户已明确选择“不要 `.cmd`”。
- D-025 后 `<skill-dir>/bin/docdev*` 缺失是预期状态，不应作为 fallback 警告暴露。
- CLI 入口继续由 `docdev` on PATH 或 native launcher 承担，职责更清楚。

**风险 / Risks**:
- 如果外层 agent resolver 在平台代码中硬编码旧探测顺序，仅改 skill 文案不能完全消除噪音。缓解：若仍复现，再定位并修复外层 resolver。

**对应代码 / 文档**:
- `skill/SKILL.md`
- `docs/SPEC.md`
- `README.md`
- `tests/test_cli.py`

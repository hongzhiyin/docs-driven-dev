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

## D-002 - Step 6 - 用正向入口合同替代负向禁令文案

**日期 / Date**: 2026-06-18

**上下文 / Context**:
v0.1.11 通过显式负向规则降低了旧 wrapper 提示复现概率，但用户指出 skill 对本来就不该做的
事情不需要反复写“不要怎么做”。active skill guidance 应该说 agent 该走哪些 CLI 入口。

**选项 / Options**:
- A. 保留 v0.1.11 的负向禁令 - 对旧问题描述最直接，但会继续把旧路径放进模型操作上下文。
- B. 改成正向入口合同 - 只描述 PATH / native launcher 入口和安装不可用的诊断条件。

**选择 / Chosen**: B

**理由 / Rationale**:
- skill 的职责是指导当前工作流，正向合同更短、更稳，也更符合用户对 skill 文案的期望。
- D-025 的同步模型已经决定 CLI 入口由 native/PATH 承担，不需要把旧路径作为运行指令重复出现。
- 测试保护正向短语即可防止后续文案退回旧模式。

**风险 / Risks**:
- 如果外层 resolver 仍硬编码旧路径，正向 skill 文案不能单独修复平台代码。缓解：若用户再次复现，
  再定位 resolver 实现而不是继续堆叠 skill 禁令。

**对应代码 / 文档**:
- `skill/SKILL.md`
- `docs/SPEC.md`
- `README.md`
- `tests/test_cli.py`

---

## D-003 - Step 7 - 为正向 skill 文案发布 v0.1.12

**日期 / Date**: 2026-06-18

**上下文 / Context**:
源码和本机已安装 skill 已经改成正向入口合同，但 latest release `v0.1.11` 的 artifact 仍包含上一版
负向文案。后续 `docdev update` 或新机器安装 latest 时会从 release artifact 取 skill 内容。

**选项 / Options**:
- A. 等下一次功能 release 顺带发布 - 少一次 release，但 latest install/update 继续落后。
- B. 发布一个小的 `v0.1.12` skill 文案 release - 让 release artifact 立即与当前 source / installed skill 对齐。

**选择 / Chosen**: B

**理由 / Rationale**:
- 用户关心的是后续 agent 使用 skill 时的实际表现，分发边界必须包含 release artifact。
- 本次改动虽然小，但会影响 installed skill 文案，适合用 patch release 交付。
- 已用 unit tests、audit 和本地 packaged install smoke 验证 artifact。

**风险 / Risks**:
- 纯文案 release 会增加一个版本号。缓解：不引入行为变更，只发布已验证的 skill/docs 内容。

**对应代码 / 文档**:
- `pyproject.toml`
- `src/docs_driven_dev/__init__.py`
- `skill/SKILL.md`
- `docs/ROADMAP.md`

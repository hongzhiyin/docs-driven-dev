# DECISIONS - skill-surface-runtime-trim

> 本文件记录这次需求中为什么这么选。只写真实取舍，不为机械改动补仪式性决策。

## 维护规则

1. `D-XXX` 在本工作包内单调递增，不复用。
2. 每条记录 2-3 个真实选项；不要编造凑数选项。
3. 写清选择、理由、风险和对应文件。
4. 决策被推翻时，新增一条 D-XXX 引用旧决策，旧决策保留原文。

---

## D-001 - Step 3 - active skill 只保留 runtime contract

**日期 / Date**: 2026-06-24

**上下文 / Context**:
用户确认当前 skill 内容偏多，希望精简。需要决定是继续在 active skill 中保留安装/维护教程，还是把它收敛成 agent runtime action contract。

**选项 / Options**:
- A. 保留完整安装、更新、uninstall 和模板细节 - 单文件信息完整，但 active context 继续偏重。
- B. active skill 只保留当前 workflow / CLI resolution / gates；安装、发布、维护细节留在 README / SPEC / DECISIONS - skill 更短，但维护者需要查源文档。

**选择 / Chosen**: B

**理由 / Rationale**:
- Skill 是 agent 的即时决策层，不应承担 README 的安装手册职责。
- 低频安装和发布细节会稀释 docs-first gate、delegation 和 verification 这些高频行为。
- README / SPEC 已保留安装、更新、uninstall 和 release 合同，维护信息没有丢失。

**风险 / Risks**:
- 只读 installed skill 的维护者看不到完整安装说明。缓解：skill 明确将 install/update 细节指向 README / source docs。

**对应代码 / 文档**:
- SPEC §1-§8
- ROADMAP Step 3
- `skill/SKILL.md`
- `README.md`
- `tests/test_cli.py`

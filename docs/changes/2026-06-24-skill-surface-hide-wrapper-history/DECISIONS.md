# DECISIONS - skill-surface-hide-wrapper-history

> 本文件记录这次需求中为什么这么选。只写真实取舍，不为机械改动补仪式性决策。

## 维护规则

1. `D-XXX` 在本工作包内单调递增，不复用。
2. 每条记录 2-3 个真实选项；不要编造凑数选项。
3. 写清选择、理由、风险和对应文件。
4. 决策被推翻时，新增一条 D-XXX 引用旧决策，旧决策保留原文。

---

## D-001 - Step 1 - active skill 只保留当前操作面

**日期 / Date**: 2026-06-24

**上下文 / Context**:
用户指出 skill 文档中解释旧 wrapper 到 native launcher 的迁移/清理规则，会让使用方知道
旧 wrapper 的存在，也会诱导 agent 继续围绕旧入口推理。需要决定这些维护信息保留在哪里。

**选项 / Options**:
- A. 在 skill 中继续解释迁移和清理规则 - 便于自诊断，但会把旧入口放进 agent 的即时操作上下文。
- B. skill / README active surface 只描述当前命令入口；迁移历史留在 source-of-truth docs - 使用面更干净，但维护者需要去 SPEC/DECISIONS 查历史。

**选择 / Chosen**: B

**理由 / Rationale**:
- 用户明确希望使用方不知道旧 wrapper 的存在。
- active skill 是 agent 最容易照做的文本，应只呈现当前应该做什么。
- source-of-truth docs 仍保留实现和历史，维护可追溯性不丢失。

**风险 / Risks**:
- 纯源码修改不会自动影响其他机器的已安装 skill。缓解：完成后可通过 release/update 或 sync 路径分发。

**对应代码 / 文档**:
- SPEC §1-§8
- ROADMAP Step 3
- `skill/SKILL.md`
- `README.md`
- `tests/test_cli.py`

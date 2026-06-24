# DECISIONS - docs maintenance health

> 本文件记录这次需求中为什么这么选。只写真实取舍，不为机械改动补仪式性决策。

## 维护规则

1. `D-XXX` 在本工作包内单调递增，不复用。
2. 每条记录 2-3 个真实选项；不要编造凑数选项。
3. 写清选择、理由、风险和对应文件。
4. 决策被推翻时，新增一条 D-XXX 引用旧决策，旧决策保留原文。

---

## D-001 - Step 1 - Add docs-health report instead of automatic trimming

**日期 / Date**: 2026-06-24

**上下文 / Context**:
用户希望继续精简 docdev 自身维护文档，并指出这种定期精简流程也应该成为 docdev 能力，供其他项目复用。

**选项 / Options**:
- A. 只手工精简当前仓库 - 最快，但其他项目无法复用。
- B. 新增自动改写/归档命令 - 最完整，但容易误删历史和判断性内容。
- C. 新增 deterministic `docs-health` 报告命令，agent 基于报告执行判断性精简 - 可复用且符合 skill/CLI 边界。

**选择 / Chosen**: C

**理由 / Rationale**:
- 文档精简包含判断：README 哪些该降噪、DECISIONS 哪些必须保留、ROADMAP 哪些可归档，这不应交给机械规则直接改写。
- CLI 可以稳定统计行数、工作包体积、completed step 数和 review signals，适合其他项目复用。
- 该设计延续 docdev 的边界：CLI 做确定性工作，skill/agent 做取舍。

**风险 / Risks**:
- 报告阈值可能不适合所有项目。缓解：只作为 review signal，不让 `audit` 失败，也不自动修改文件。

**对应代码 / 文档**:
- SPEC §5
- ROADMAP Step 1
- `src/docs_driven_dev/docs_health.py`
- `src/docs_driven_dev/commands.py`
- `tests/test_cli.py`

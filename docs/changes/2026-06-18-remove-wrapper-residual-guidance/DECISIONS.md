# DECISIONS - remove-wrapper-residual-guidance

> 本文件记录这次需求中为什么这么选。只写真实取舍，不为机械改动补仪式性决策。

## 维护规则

1. `D-XXX` 在本工作包内单调递增，不复用。
2. 每条记录 2-3 个真实选项；不要编造凑数选项。
3. 写清选择、理由、风险和对应文件。
4. 决策被推翻时，新增一条 D-XXX 引用旧决策，旧决策保留原文。

---

## D-001 - Step 3 - Keep active guidance abstract and preserve history

**日期 / Date**: 2026-06-18

**上下文 / Context**:
旧 skill-local launcher 已被 D-025 移出当前 sync 行为，但 active skill / README /
SPEC 仍把旧路径作为 cleanup 示例。用户反馈其他机器更新后仍会看到旧 skill-local
Windows launcher 相关提示。

**选项 / Options**:
- A. 在活跃指导里继续列出具体旧路径作为清理例子 - 对迁移背景更直观，但容易让 agent
  把旧路径当作当前需要检查的对象。
- B. 活跃指导只描述 supported entrypoints 和 current-target replacement；历史
  ROADMAP / DECISIONS 保留旧路径背景。

**选择 / Chosen**: B

**理由 / Rationale**:
- 用户关心的是使用 skill 时不再被旧路径提示打扰，活跃指导应优先服务当前操作。
- current-target replacement 足以表达同步清理语义，不需要把 superseded path 放回
  agent 最常读取的上下文。
- 历史记录保留，后续追查 D-025 / D-033 等迁移仍有证据链。

**风险 / Risks**:
- 新文案比旧文案少了具体 legacy filename。缓解：历史 ROADMAP/DECISIONS 和 change
  packets 继续保留迁移细节。

**对应代码 / 文档**:
- SPEC §5
- ROADMAP Step 3 / Step 4
- `skill/SKILL.md`
- `README.md`
- `docs/SPEC.md`
- `tests/test_cli.py`

# DECISIONS - cli.py 轻量拆分

> 本文件记录这次需求中为什么这么选。只写真实取舍，不为机械改动补仪式性决策。

## 维护规则

1. `D-XXX` 在本工作包内单调递增，不复用。
2. 每条记录 2-3 个真实选项；不要编造凑数选项。
3. 写清选择、理由、风险和对应文件。
4. 决策被推翻时，新增一条 D-XXX 引用旧决策，旧决策保留原文。

---

## D-001 - Step 3 - 保留薄 `cli.py` 入口，内部拆为职责模块

**日期 / Date**: 2026-06-13

**上下文 / Context**:
`src/docs_driven_dev/cli.py` 已经承担全部 CLI 逻辑。继续新增 Windows、签名、JSON doctor/status 或 release update 细节时，单文件会让边界和测试 patch 点越来越脆弱。但 `docs_driven_dev.cli` 已经是 native launcher、source wrappers、tests 和 `python -m` 的稳定入口。

**选项 / Options**:
- A. 继续保留单文件 - 最少改动，但会把后续功能继续堆到 940 行入口中。
- B. 大重构成 command class / plugin 架构 - 扩展面最大，但对当前 v0.1.x 过重，容易改变行为。
- C. 轻量拆分：保留 `cli.py` public 入口和兼容导出，把现有函数按职责移动到 `commands.py`、`templates.py`、`audit.py`、`sync.py`、`release.py` 及共享模块。

**选择 / Chosen**: C

**理由 / Rationale**:
- 满足 SPEC **#1**：用户命令行为不变，入口 module 不变。
- 让新增功能自然进入对应模块，避免 `cli.py` 继续增长成跨领域文件。
- 保留兼容 re-export，降低对测试和已有 local scripts 的冲击。

**风险 / Risks**:
- `cli.py` re-export 可能被误认为长期 public helper API。缓解：根 ARCHITECTURE 标注它是兼容层，后续真正 public API 另开决策。
- 模块拆分可能引入循环 import。缓解：让 `paths.py` / `models.py` 只依赖 stdlib，业务模块单向依赖它们，`commands.py` 只做 dispatch。

**对应代码 / 文档**:
- SPEC §6
- ROADMAP Step 4
- ARCHITECTURE §3-§4
- `src/docs_driven_dev/cli.py`
- `src/docs_driven_dev/commands.py`
- `src/docs_driven_dev/audit.py`
- `src/docs_driven_dev/sync.py`
- `src/docs_driven_dev/release.py`

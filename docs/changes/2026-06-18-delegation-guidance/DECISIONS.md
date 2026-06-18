# DECISIONS - delegation guidance

> 本文件记录这次需求中为什么这么选。只写真实取舍，不为机械改动补仪式性决策。

## 维护规则

1. `D-XXX` 在本工作包内单调递增，不复用。
2. 每条记录 2-3 个真实选项；不要编造凑数选项。
3. 写清选择、理由、风险和对应文件。
4. 决策被推翻时，新增一条 D-XXX 引用旧决策，旧决策保留原文。

---

## D-001 - Step 2 - 将 subagent 协作作为 skill guidance 而不是 CLI 功能

**日期 / Date**: 2026-06-18

**上下文 / Context**:
用户希望主 agent 更注重全局，subagent 处理局部代码或文档维护工作。项目既有边界是 skill
负责 workflow / judgment，CLI 负责确定性动作。

**选项 / Options**:
- A. 在 CLI 中加入 subagent 调度能力 - 可以把流程机械化，但会让 CLI 承担模型/平台能力判断。
- B. 在 skill 中增加 delegation guidance - 保持 CLI 确定性边界，让 agent 根据平台能力和任务形状选择是否委派。

**选择 / Chosen**: B

**理由 / Rationale**:
- subagent 使用依赖平台能力、上下文预算和任务风险，属于 agent workflow judgment。
- docs-driven-dev 的核心是主 agent 收束 SPEC、ROADMAP、DECISIONS 和 verification；该责任不适合交给 CLI。
- Skill 文案可以描述主 agent ownership、subagent 适用 slice 和返回合同，同时不改变现有安装/更新/同步机制。

**风险 / Risks**:
- 不同平台的 subagent 能力差异较大。缓解：guidance 用“平台支持时”和 task contract 表达，而不是要求固定工具。

**对应代码 / 文档**:
- `skill/SKILL.md`
- `docs/SPEC.md`
- `README.md`
- `tests/test_cli.py`

---

## D-002 - Step 5 - 为 delegation guidance 发布 v0.1.13

**日期 / Date**: 2026-06-18

**上下文 / Context**:
Delegation guidance 已经写入 source skill 并同步到本机 installed skill。用户要求提交修改并推送发布，
因此 latest release artifact 也需要包含该 guidance。

**选项 / Options**:
- A. 只提交 source 变更 - 简单，但 fresh install / `docdev update` 暂时拿不到新 guidance。
- B. 发布小版本 `v0.1.13` - 让 release artifact、source skill 和本机 installed skill 对齐。

**选择 / Chosen**: B

**理由 / Rationale**:
- 用户明确要求发布。
- Skill guidance 的真实分发边界是 GitHub Release artifact。
- 可以用 unit tests、audit、本地 packaged install smoke 和 public latest smoke 验证。

**风险 / Risks**:
- 纯 guidance release 会增加一个版本号。缓解：不引入 CLI 行为变更，只发布已验证的 skill/docs 内容。

**对应代码 / 文档**:
- `pyproject.toml`
- `src/docs_driven_dev/__init__.py`
- `skill/SKILL.md`
- `docs/ROADMAP.md`

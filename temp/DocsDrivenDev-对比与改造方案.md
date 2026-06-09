# DocsDrivenDev 与 docs-driven-dev skill 对比及改造方案

> 用途：本文件用于给 `E:\Project\DocsDrivenDev` 项目做优化迭代输入。
> 请把本文件与「参考的 docs-driven-dev skill 源文件」一起提供给该项目，
> 让其据此自我演进。
>
> 对比双方：
> - **skill**：参考的 `skills/docs-driven-dev`（纯方法论：SKILL.md +
>   模板 + examples，中文优先，无 CLI）。
> - **DocsDrivenDev**：`E:\Project\DocsDrivenDev`（方法论 + `docdev` CLI + scripts +
>   自身四件套文档，英文，可安装分发）。
>
> 关键事实：DocsDrivenDev **自带**一份 `skill/SKILL.md`，但它与参考的 skill 是
> **同一理念的两个分支**，设计哲学差别很大。本文档对比的是「DocsDrivenDev 整个项目」
> 与「参考的 skill 的方法论」。

---

## 1. 本质定位对比

| 维度 | docs-driven-dev skill（参考的） | DocsDrivenDev 项目 |
|---|---|---|
| 形态 | 纯方法论指南（Markdown + 模板） | 方法论 + `docdev` CLI + scripts + 自身四件套，可安装产品 |
| 主战场 | 已有项目逐需求演进（per-requirement work packet） | 项目级四件套 bootstrap / extend |
| 文档组织 | `docs/changes/YYYY-MM-DD-slug/` 每需求一个包 | 全项目单一 `docs/` 四件套 |
| 约束执行 | 靠 agent 自觉判断 | `docdev audit` 机械校验 |
| 语言 | 简体中文优先（保留代码标识符原文） | 全英文 |
| 流程闸门 | 有硬性「实现审批门（Implementation Gate）」 | 较轻的 Bootstrap / Extend，无硬闸 |
| 子代理调研 | 有明确指导 | 无 |
| 分发安装 | 无 | `install.sh` / `sync-skill` / `doctor`，多 agent home |
| 一句话总结 | 强在**前期判断与调研纪律**，无护栏 | 强在**后期一致性护栏与工程化**，缺前期纪律 |

---

## 2. 对比清单

### 2.1 skill 考虑到、DocsDrivenDev 还没考虑到的（建议补强项）

| # | 能力 | skill 的做法 | DocsDrivenDev 现状 | 影响 |
|---|---|---|---|---|
| G1 | 既有实现的系统化调研 | Workflow A 有调研清单 + 调研记录表（R-1/R-2 + 证据文件路径 + 结论） | Extend 仅「先读 SPEC」，无调研纪律 | 在已有代码库上加需求时易遗漏约束 |
| G2 | 实现审批门 | 硬性「用户确认方案前不许动生产代码」+ 实现前/完成前两张门禁清单 | 无硬闸 | 容易跳过确认直接写代码 |
| G3 | 每需求工作包隔离 | `docs/changes/日期-slug/` 每需求独立 | 仅项目级单套 `docs/` | 多需求并行时文档互相污染 |
| G4 | ARCHITECTURE 按需创建 | 明确「何时需要 / 何时可省，省了写理由」 | audit 把四件套全当必需，缺 `ARCHITECTURE.md` 报 `error` | 小需求被迫凑架构文档 |
| G5 | 子代理（sub-agent）调研指导 | 专章：如何用只读子代理分担调研、返回路径/行号/不确定性、回收进文档 | 无 | 大项目调研时主上下文压力大 |
| G6 | 中文优先 + 术语保留 | 文档中文、代码标识符保留原文、必要时英文括注 | 全英文 | 不贴合中文团队使用场景 |
| G7 | 验证回映射验收标准 | 收尾要求每条 SPEC 验收标准都有验证结果记录 | audit 只查「Step 是否有 Acceptance 段落存在」 | 无法保证真的逐条验证 |
| G8 | 反模式「假设藏在代码注释」 | 显式反模式 + 强制未决项进 SPEC 开放问题 / ROADMAP 阻塞 | 仅有 `pending D-XXX` | 隐性假设容易丢失 |

### 2.2 DocsDrivenDev 比 skill 更好的地方（建议保留并向 skill 反哺）

| # | 能力 | DocsDrivenDev 的做法 | skill 现状 |
|---|---|---|---|
| B1 | 可执行机械护栏 | `docdev audit`：四件套存在、D-XXX 单调/唯一/不跳号、决策含 Options/Chosen/Risks、Step 含验收、SPEC 有编号不变式 `**#N**`、README/AGENTS 指针 | 全靠 agent 自觉，零强制 |
| B2 | 脚手架与编号自动化 | `docdev init` / `new-decision`（自动算下一个 D-XXX，中英双语骨架）/ `status` | 全手工，易编号错乱 |
| B3 | 判断层 vs 确定性层分离 | 不变式 #5：可重复操作交 CLI，判断留 skill | 仅方法论，无此契约 |
| B4 | 跨 agent 分发与可发现性 | 安装到 `~/.codex`/`~/.cursor`/`~/.agents`/Claude symlink，每份带 `bin/docdev` wrapper | 无安装/同步机制 |
| B5 | 自举（dogfooding） | 用自身四件套 + 不变式 #1~#6 描述自己 | 无自身实例 |
| B6 | 生成产物隔离不变式 | 强制 `_generated/docdev/`，audit + AGENTS 双重校验 | 无源/生成分离概念 |
| B7 | 可配置文档目录 + 测试 | `.docdev.toml` `docs_dir` + `tests/test_cli.py` | 纯文本，写死约定、不可测 |

---

## 3. DocsDrivenDev 改造方案

> 原则：保留 DocsDrivenDev 已有的工程化护栏优势（B1~B7），把 skill 的前期纪律
> （G1~G8）转化为**可校验的能力**而非纯口头约定。改造本身建议按 DocsDrivenDev
> 自己的 docs-driven 流程走（更新 SPEC / ROADMAP / DECISIONS）。

改造分三档：P0（高价值且改动可控）、P1（中价值）、P2（增强 / 可选）。

### P0 — 核心能力补齐

#### P0-1 支持 per-requirement 工作包（对应 G3）
- 让 `docdev` 在项目级四件套之外，支持 `docs/changes/YYYY-MM-DD-slug/` 工作包模式。
- 新增命令草案：`docdev new-change "<slug>" <project>`，生成当次需求的
  SPEC/ROADMAP/DECISIONS（ARCHITECTURE 可选）。
- `audit` 增加对工作包目录的递归识别（既能审项目级，也能审单个 change 包）。
- 对应 SPEC：在 Decision Table 增加一行「文档粒度：项目级 + 可选 per-requirement
  工作包」，并新增 D-XXX。

#### P0-2 ARCHITECTURE 可选化（对应 G4）
- 把 `ARCHITECTURE.md` 缺失从 `error` 降为 `warn`，并要求在 ROADMAP/SPEC 写明
  「本次不需要 ARCHITECTURE 的理由」时静默放行。
- 落点：`cli.py` 的 `audit_project()` 里 `DOC_NAMES` 缺失判定逻辑分级处理。
- 对应不变式：修订「四件套都必须存在」为「SPEC/ROADMAP/DECISIONS 必须存在，
  ARCHITECTURE 按需」，新增 D-XXX 记录该松绑。

#### P0-3 审批门检查（对应 G2 + G7）
- 在 ROADMAP 模板引入「门禁清单」段落（实现前必须满足 / 完成前必须满足）。
- `audit` 新增检查：若 ROADMAP 标记进入「实现中」但门禁清单未勾完，报 `warn`/`error`。
- 新增「验证记录」段落校验：完成状态的验收标准是否都有对应验证结果（对应 G7），
  缺失报 `warn`。

### P1 — 流程纪律工程化

#### P1-1 调研记录结构化（对应 G1）
- 在 ROADMAP（或工作包）模板加入「调研记录」表（ID / 主题 / 发现 / 证据文件 / 结论）。
- `audit` 可选检查：进入「实现中」前是否存在非空调研记录（弱校验，`warn`）。

#### P1-2 中文 / 双语支持（对应 G6）
- 提供中文模板集（`skill/templates/zh/` 或模板内中英双栏），`docdev init --lang zh`。
- audit 的关键字匹配已部分双语（如「验收」/「Acceptance」、「选项」/「Options」），
  补齐其余字段，保证中文文档也能通过校验。

#### P1-3 开放问题 / 假设显式化（对应 G8）
- SPEC 模板加入「开放问题」表（含「是否阻塞实现」列）。
- 反模式清单补一条「假设藏在代码注释而非 SPEC/DECISIONS」。

### P2 — 增强与协同

#### P2-1 子代理调研指导（对应 G5）
- 在 `skill/SKILL.md`（DocsDrivenDev 自带版本）补一节：何时用只读子代理分担调研、
  要求返回文件路径/行号/不确定性、并把结论回收进文档。纯文本约定，无需改 CLI。

#### P2-2 audit 输出对接审批门状态
- `docdev status` 增加「门禁完成度 / 验收完成度」摘要，便于人/agent 一眼看进度。

#### P2-3 双分支收敛
- 明确 DocsDrivenDev 自带 `skill/SKILL.md` 与参考的 skill 的关系：决定是
  「合并为一份兼顾判断+工具的 skill」还是「保留两套定位」。建议合并，并以 D-XXX
  记录取舍。

---

## 4. 改造对 DocsDrivenDev 自身文档的影响（建议落点）

| 文档 | 需要的改动 |
|---|---|
| `docs/SPEC.md` | Decision Table 增加「文档粒度」「ARCHITECTURE 可选」「语言支持」行；修订不变式 #（四件套必须存在）；新增审批门 / 验证记录相关默认行为 |
| `docs/ARCHITECTURE.md` | 更新 audit 分级逻辑、新增 `new-change` 数据流、模板 lang 维度 |
| `docs/ROADMAP.md` | 新增 Step：P0-1 工作包、P0-2 架构可选、P0-3 审批门校验等，每个带验收 |
| `docs/DECISIONS.md` | 为 P0-1/P0-2/P0-3/P2-3 各追加 D-XXX（含 Options/Chosen/Risks） |
| `skill/SKILL.md`（自带） | 补子代理调研节、开放问题反模式、按需 ARCHITECTURE 判断 |
| `skill/templates/*` | 模板加入门禁清单、调研记录、开放问题、验证记录段落；提供中文模板 |
| `cli.py` | `audit` 分级与新检查、`new-change` 命令、`init --lang`、`status` 摘要扩展 |
| `tests/test_cli.py` | 为新检查与新命令补测试 |

---

## 5. 建议实施顺序

1. 先做 P0-2（ARCHITECTURE 可选化）—— 改动小、立刻减少误报。
2. 再做 P0-1（工作包）—— 这是与 skill 最大的结构性差距。
3. 然后 P0-3（审批门 + 验证记录校验）—— 把 skill 的硬纪律变成可校验护栏。
4. 之后并行推进 P1（调研记录、中文、开放问题）。
5. 最后处理 P2（子代理指导、status 摘要、双分支收敛）。

每一步都按 DocsDrivenDev 自己的流程：先改 SPEC/ROADMAP/DECISIONS，再改 CLI/模板/测试，
最后 `docdev audit` 自检通过。

---

## 6. 一句话结论

> skill 强在「前期判断、调研、审批纪律」，DocsDrivenDev 强在「后期一致性护栏与工程化」。
> 改造目标是把 skill 的软纪律（G1~G8）变成 DocsDrivenDev 可执行的硬护栏，
> 同时保留 DocsDrivenDev 已有的 CLI/审计/分发优势（B1~B7），最终收敛成一份
> 「既有判断纪律、又有可执行护栏」的统一方法论 + 工具链。

---

## 7. 给 DocsDrivenDev 的一句话 prompt 模板

把本文件与参考的 skill 的源文件（`SKILL.md` + `templates/` + `examples.md`）一并附给
DocsDrivenDev 项目后，可直接用下面的模板发起迭代。

### 主模板（推荐）

```text
按本项目自己的 docs-driven 流程迭代 DocsDrivenDev。我附了两份材料：
（1）《DocsDrivenDev-对比与改造方案.md》，里面用 G1~G8 标出本项目缺的能力、
B1~B7 标出本项目的优势、P0/P1/P2 给出改造方案；
（2）参考的 docs-driven-dev skill 源文件，作为缺失能力的参考实现。
请先调研本项目现状并和我确认范围，再按 P0→P1→P2 的顺序，把方案落到
SPEC/ROADMAP/DECISIONS（必要时 ARCHITECTURE），每个改造点补对应 D-XXX；
未确认前不要改生产代码，最后用 docdev audit 自检通过。
```

### 精简版（只想先起步）

```text
读《DocsDrivenDev-对比与改造方案.md》和附带的 skill 源文件，先做 P0-2（ARCHITECTURE
可选化）和 P0-1（per-requirement 工作包）：先改 SPEC/ROADMAP/DECISIONS 并各补 D-XXX，
和我确认方案后再改 cli.py/模板/测试，最后 docdev audit 通过。
```

### 单点版（指定某一条）

```text
按《DocsDrivenDev-对比与改造方案.md》里的 <P0-3> 改造本项目，参考附带 skill 源文件中
<审批门 / 验证记录> 的做法。先更新 SPEC/ROADMAP/DECISIONS 并补 D-XXX，确认后再动
cli.py 和 tests，最后 docdev audit 自检。
```

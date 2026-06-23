---
name: docs-driven-dev
description: >-
  用 docs-driven development 维护项目：以 docs/SPEC.md,
  docs/ARCHITECTURE.md, docs/ROADMAP.md, docs/DECISIONS.md
  作为 source-of-truth documents，并在 docs/changes/ 下为具体需求创建
  change packet。适用于用户要求 doc-driven、documentation-first、spec-driven、
  research-before-code、四件套文档、需求工作包、决策日志、不变式、D-XXX、
  Step/Phase planning，或项目已经存在上述 docs 结构的场景。
metadata:
  requires:
    bins: ["docdev"]
  cliHelp: "docdev --help"
---

# Docs-Driven Development

这个 skill 是 agent 的 runtime action contract：文档负责意图、结构、进度和取舍；
`docdev` CLI 负责可重复的文件生成、编号、audit、sync、安装和更新。

## Invocation Contract（调用合同）

当用户明确点名本 skill，或明确要求 docs-driven / 文档先行 / 四件套文档时，先遵循
下面某个 workflow，并在改代码前创建或更新必要的 docs artifacts。只读一遍 `SKILL.md` 然后直接写代码是不够的。
不要把明确的 `docs-driven-dev` 调用静默降级成临时调研或直接 coding，即使只是小修复。

## File Contract（文件合同）

项目级 source-of-truth：

```text
docs/
  SPEC.md          # what should be true
  ARCHITECTURE.md  # what exists
  ROADMAP.md       # where we are
  DECISIONS.md     # why
  _generated/docdev/
```

需求级 change packet：

```text
docs/changes/YYYY-MM-DD-slug/
  SPEC.md
  ROADMAP.md
  DECISIONS.md
  ARCHITECTURE.md  # optional; ROADMAP records the omission reason
```

默认使用 `docs/`。只有既有项目显式配置 `.docdev.toml` 时才遵从 `docs_dir`。生成报告只能放在
`docs/_generated/docdev/`，不要混入四个 source-of-truth docs。

## CLI Resolution（CLI 解析）

始终显式选择目标项目。只有当用户当前工作目录显然就是目标项目时，才把当前目录当目标；
否则传入用户说出的项目路径。

按这个顺序解析 CLI：

1. `docdev <command>` if available on `PATH`。
2. Windows: `docdev <command>` in a fresh terminal。
3. 如果 `docdev` 不可用，请用户先运行 native installer 或修复安装。

常用命令：

```bash
docdev init /path/to/project
docdev new-change "feature-slug" /path/to/project
docdev audit /path/to/project --write-report
docdev status /path/to/project
docdev new-decision "Step N - trade-off title" /path/to/project
docdev sync-skill --targets codex,cursor,agents,claude --force
docdev doctor
```

`sync-skill` 同步 workflow content；agent 执行 CLI 时使用上述 native/PATH entries。CLI 不负责
做产品设计、不放松 SPEC invariant，也不替用户决定取舍。

## Install And Update Boundary（安装与更新边界）

普通安装、更新、卸载、发布和维护者安装说明属于 README / SPEC / DECISIONS，不属于 active
skill runtime guidance。这里保留的规则只有：agent 调用 CLI 使用 `docdev` 或 documented
native fallback；当安装不可用时，请用户修复安装，而不是推测其他入口。

## Delegation Guidance（委派指导）

Delegation 是 context/throughput tool。当平台支持 subagents，且任务存在边界清楚的 slice，
优先考虑委派；除非任务太小、工具不支持，或拆分会增加风险。docs-driven ownership 仍由主 agent 收束。

主 agent owns：用户意图、SPEC invariants、scope、implementation gate、DECISIONS、
final diff review、verification 和最终说明。

subagent 适合承担：bounded read-only research、已批准的窄范围 implementation slice、
文档一致性检查、测试失败定位。

handoff 写清 objective、file scope、write permission、acceptance checks 和需要保留的
invariants。subagent 返回 changed files / findings、tests、uncertainty，以及需要主 agent
判断的点。主 agent review 后再更新 source-of-truth docs、verification records 和最终说明。

## Document Boundaries（文档边界）

| Doc | Answers | Refuses |
|---|---|---|
| `SPEC.md` | expected behavior, invariants, contracts | implementation details, history |
| `ARCHITECTURE.md` | modules, data flow, config, current structure | behavior rules, plans |
| `ROADMAP.md` | phase, step, tasks, acceptance, verification | design rationale |
| `DECISIONS.md` | D-XXX rationale, options, choice, risks | current status |

已有代码库没有项目级四件套时，这是 adoption case，不是 blocked case。先运行
`docdev init <project>` 创建最小根文档，再运行 `docdev new-change "<slug>" <project>`。
不要让一个单独的 `docs/changes/...` packet 成为项目唯一的 docs-driven artifact。

## Workflow A - Bootstrap（项目初始化）

使用时机：`<docs_dir>/SPEC.md` 不存在，或用户明确要求建立 docs-driven development。

1. 用一句话确认项目目标。
2. 运行 `docdev init <project>`。
3. 填 SPEC §1 和 SPEC §2 decision table，目标是 5-10 个真实选择。
4. 写入至少一个 SPEC invariant。
5. 在 ROADMAP 添加 Step 0 或 Step 1，并写清 acceptance criteria。
6. 在 DECISIONS 添加 D-001，记录 foundational trade-off。
7. 只有用户明确要求时才 stage 或 commit。

对已有代码库，Bootstrap 要轻量：先创建 durable root docs，然后立刻进入 Workflow B。

## Workflow B0 - Small Existing-Project Fix（小修复）

使用时机：用户明确点名 `docs-driven-dev`，且请求是窄范围 bug fix 或小行为调整。

1. 不跳过文档；若根文档缺失，先做最小 adoption root。
2. 运行 `docdev new-change "<slug>" <project>`。
3. packet 保持最小：SPEC 一条 expected behavior；ROADMAP 写 goal、touched files、
   acceptance checks、verification；DECISIONS 只记录真实 trade-off；ARCHITECTURE 默认省略。
4. Treat an explicit user request like "fix it", "补上吧", or "implement it" as
   implementation approval after the packet states scope and acceptance.
5. 实现窄范围修复，验证，写回 verification results，运行 `docdev audit <project>`。

## Workflow B - Existing Project Requirement（已有项目需求）

使用时机：已有项目中的 feature、refactor、research task 或 behavior change。

1. 若项目级 SPEC 缺失，先用 Workflow A 轻量 adoption。
2. 读项目级 SPEC，再读 ROADMAP，按需读 DECISIONS 和 ARCHITECTURE。
3. 用一句话复述目标，只问最关键的 1-3 个问题。
4. 运行 `docdev new-change "<slug>" <project>`；只有结构影响明确时才加 `--with-architecture`。
5. 先调研，再设计。发现写入 packet ROADMAP research log；行为约束进 packet SPEC；结构事实进
   packet ARCHITECTURE。
6. implementation gate 前停住：goal、scope、non-goals、相关代码、open questions、steps、
   verification 和 user approval 都要清楚，才能改 production code。
7. 批准后小步实现。若出现新的 user-visible trade-off，更新 SPEC/DECISIONS 并确认。
8. 验证每条 acceptance criterion，记录结果，运行 `docdev audit <project>`，说明剩余风险。

如果调研发现 module、data flow、lifecycle、persistence、public API、event、config、
migration 或 cross-cutting impact，在实现前补 ARCHITECTURE。

## Workflow C - Project-Level Extend（项目级扩展）

使用时机：用户要改变 durable project-level contract。

1. 读 SPEC、ROADMAP，按需读 DECISIONS / ARCHITECTURE。
2. 对齐 problem、at-risk invariants、module surface 和 acceptance criteria。
3. 实现前先更新 SPEC 规则或合同。
4. 追加 ROADMAP Step / sub-step，并写清 acceptance criteria。
5. 小步实现；若现实迫使新选择，回到对齐和决策记录。
6. 用 Step acceptance criteria 验证，运行 `docdev audit`。
7. 若变更对用户可见，追加或完成相关 D-XXX，并同步 README 状态。

## Decision And Verification Rules（决策与验证）

- SPEC 必须有清楚 invariant；ROADMAP Step 必须有 acceptance。
- D-XXX numbers are monotonic：不复用、不跳号。
- 每个 non-trivial decision 至少包含 options、chosen、rationale、risks 和相关文件。
- change packet 省略 `ARCHITECTURE.md` 时，ROADMAP 必须写 omission reason。
- 最终回答前验证 acceptance，并写回 verification results。

## Anti-Patterns（反模式）

- 先 coding，再倒推意图。
- 把 rationale 写进 SPEC，或把 current status 写进 DECISIONS。
- ROADMAP 只写 “do the thing”，没有 acceptance。
- 在创建或更新 change packet 前就开始 substantial production code。
- 把未解决假设藏在 code comments 里，而不是放到 SPEC open questions 或 DECISIONS。

## Reference

只有需要强示例时，才读 `references/examples.md`。

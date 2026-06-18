# SPEC - remove-wrapper-residual-guidance

> 本文件描述本次需求应该满足什么。它不写实现细节、不追踪进度、不解释历史取舍。

## 0. 状态

| 字段 | 内容 |
|---|---|
| 状态 | 完成 |
| 需求来源 | 用户反馈：其他机器更新后仍出现旧 skill-local Windows launcher 缺失类提示 |
| 工作包目录 | `docs/changes/2026-06-18-remove-wrapper-residual-guidance/` |
| 最后更新 | 2026-06-18 |

## 1. 一句话目标

让安装或更新后的 agent 在使用 docs-driven-dev skill 时，只从活跃指导中看到当前支持的
CLI 入口和 skill 同步语义，不再被旧 skill-local launcher 路径示例诱导出误报。

## 2. 背景与问题

- 当前行为：`skill/SKILL.md`、README 和 root SPEC 的活跃安装/同步说明仍点名旧
  skill-local launcher 作为残留示例。
- 问题：这些路径已经不是当前运行入口，但活跃指导里的路径字符串会让 agent 继续把它们
  当作需要检查或报告的对象。
- 期望收益：agent 使用 skill 时聚焦 `docdev` on PATH、native launcher、以及
  `sync-skill` 的 current-target replacement 行为。

## 3. 范围

### 3.1 本次要做

- 调整活跃 `skill/SKILL.md`、README 和 root SPEC 的 source checkout / sync 文案。
- 用 regression test 保护新的正向表述。
- 记录 root ROADMAP / DECISIONS 和本工作包验证结果。

### 3.2 本次不做

- 不重写历史 ROADMAP step 或历史 DECISIONS 条目里的旧 launcher 背景。
- 不改变 CLI resolution、native installer、`sync-skill` 或 release packaging 的代码行为。
- 不发布新版本，除非用户后续明确要求提交并发布。

## 4. 用户场景 / 使用流程

| 场景 ID | 触发条件 | 期望结果 |
|---|---|---|
| S1 | 另一台机器运行 `docdev update` 后，agent 读取已同步 skill 并执行 docs-driven-dev 工作流 | agent 根据 PATH/native launcher 执行 CLI，并把 `sync-skill` 理解为刷新 skill 内容，不报告 skill 目录里的旧 CLI 路径缺失 |

## 5. 功能需求

| ID | 需求 | 验收方式 | 状态 |
|---|---|---|---|
| R1 | 活跃 skill guidance 应描述当前支持的 CLI entrypoints 和 source checkout sync 行为 | `rg` / unit test 检查 `skill/SKILL.md` 不含旧 skill-local launcher cleanup 示例 | 完成 |
| R2 | README 和 root SPEC 应使用 current-target replacement 描述同步清理效果 | unit test 和人工检查 | 完成 |
| R3 | Windows native launcher 的正确 `docdev.cmd` 说明保留 | unit test 继续断言 README / skill 中存在 native Windows `docdev.cmd` 说明 | 完成 |

## 6. 约束与不变式

1. **#1**: CLI 执行入口仍是 `docdev` on PATH、Unix-like `~/.local/bin/docdev`、
   Windows `docdev` / `$HOME\.local\bin\docdev.ps1`。
2. **#2**: `sync-skill` 仍只同步 skill 内容和 marker，不承担 CLI launcher 分发。
3. **#3**: 历史决策记录保持可追溯，活跃指导承担当前操作说明。

## 7. 兼容性与默认行为

| 场景 | 默认行为 |
|---|---|
| 已同步 skill 目标内存在 marker | force 或 marked refresh 继续整目录替换当前目标 |
| Windows native install | 继续写入 native bin 下的 `docdev.ps1` 和 `docdev.cmd` |
| 历史 docs | 保留旧路径背景，作为 superseded history |

## 8. 验收标准

1. Active `skill/SKILL.md` 不再用旧 skill-local launcher 示例解释当前 sync 行为。
2. README / SPEC 描述 current-target replacement 和 supported CLI entries，且保留
   native Windows `docdev.cmd` 入口说明。
3. `python3 -m unittest discover -s tests` 和 `docdev audit` 通过。

## 9. 开放问题

| ID | 问题 | 当前判断 | 是否阻塞实现 |
|---|---|---|---|
| Q1 | 是否立刻发布新版本让其他机器通过 `docdev update` 获得修复 | 用户已明确要求提交、推送并发布；发布 `v0.1.14` | 否 |

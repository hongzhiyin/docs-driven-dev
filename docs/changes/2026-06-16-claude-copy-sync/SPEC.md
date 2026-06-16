# SPEC - Claude 直接复制同步

> 本文件描述本次需求应该满足什么。它不写实现细节、不追踪进度、不解释历史取舍。

## 0. 状态

| 字段 | 内容 |
|---|---|
| 状态 | 完成 |
| 需求来源 | 用户反馈：更新时出现 Claude symlink 相关报错，希望 Claude 像其他 agent 一样同步 skill |
| 工作包目录 | `docs/changes/2026-06-16-claude-copy-sync/` |
| 最后更新 | 2026-06-16 |

## 1. 一句话目标

让 `docdev sync-skill` 对 Claude target 使用和 Codex/Cursor/Agents 相同的直接复制模型，不再创建或依赖 symlink。

## 2. 背景与问题

- 当前行为：`src/docs_driven_dev/sync.py` 对 `claude` target 使用 `link_claude_to_agents()`，并在只请求 Claude 时先隐式同步 Agents。
- 问题：symlink 分支会在更新/同步期间产生平台、权限或路径相关报错；用户希望 Claude 与其他 agent 一样复制 skill。
- 期望收益：默认更新路径不再依赖 symlink 权限，`--targets claude` 不再修改 Agents target，四个 target 的替换语义一致。

## 3. 范围

### 3.1 本次要做

- `docdev sync-skill` 对 `claude` 调用通用 `copy_skill()`。
- 移除 Claude-only sync 对 Agents target 的隐藏前置同步。
- 让已有 legacy Claude symlink 在 `--force` 或直接 `copy_skill(..., force=True)` 时被替换为普通目录。
- 更新项目 source-of-truth docs、README、skill 文案和单元测试。

### 3.2 本次不做

- 不改默认 target 集合，仍为 `codex,cursor,agents,claude`。
- 不改变 uninstall 对 legacy symlink 的识别和删除能力。
- 不发布新 release；若需要让其他机器通过 `docdev update` 获取该行为，需要后续版本发布。

## 4. 用户场景 / 使用流程

| 场景 ID | 触发条件 | 期望结果 |
|---|---|---|
| S1 | 用户运行 `docdev sync-skill --targets claude --force` | Claude target 被复制为普通 `docs-driven-dev` skill 目录，Agents target 不被隐式同步 |
| S2 | 机器上已有旧版 Claude symlink target | force sync 会 unlink 旧 symlink 并复制当前 `skill/` |
| S3 | native install/update 默认刷新所有 targets | Codex、Cursor、Agents、Claude 都按同一 copy/marker replacement 合同刷新 |

## 5. 功能需求

| ID | 需求 | 验收方式 | 状态 |
|---|---|---|---|
| R1 | Claude sync 不再调用 symlink 创建逻辑 | 单元测试和源码检查 | 完成 |
| R2 | `--targets claude` 不再自动插入 `agents` target | 单元测试检查输出和 temp Agents home | 完成 |
| R3 | legacy Claude symlink 可被 force copy 替换 | 单元测试 | 完成 |
| R4 | 文档不再声明 Claude 默认 symlink/fallback 模型 | `rg` 检查和 `docdev audit` | 完成 |

## 6. 约束与不变式

1. **#1**: Skill sync must never replace an unmarked existing skill directory unless the caller passes `--force`.
2. **#2**: `sync-skill` must not create skill-local `bin/docdev*` wrappers.
3. **#3**: Native uninstall must continue to treat legacy symlink targets as removable docdev-owned targets.

## 7. 兼容性与默认行为

| 场景 | 默认行为 |
|---|---|
| 新同步的 Claude target | 复制 `skill/` 并写 `.docdev-skill-source` marker |
| 已有 Claude symlink，未传 `--force` | 保持现有安全语义，返回需要 `--force` 的提示 |
| 已有 Claude symlink，传 `--force` | unlink symlink，复制 `skill/`，写 marker |
| Native uninstall 发现 legacy symlink | 继续删除 symlink 本身，不递归删除 symlink 指向目标 |

## 8. 验收标准

1. `docdev sync-skill --targets claude --force` 不输出“syncing agents first”，且不会创建 temp Agents target。
2. Legacy Claude symlink 能通过 force copy 替换成普通目录。
3. `python3 -m unittest discover -s tests` 通过。
4. `PYTHONPATH=src python3 -m docs_driven_dev.cli audit /Users/chihoyo/Project/docs-driven-dev` 通过。

## 9. 开放问题

| ID | 问题 | 当前判断 | 是否阻塞实现 |
|---|---|---|---|
| Q1 | 是否立刻发布新 release | 当前用户只要求修复行为，发布可作为后续单独步骤 | 否 |

# ARCHITECTURE - Claude 直接复制同步

> 本文件只在需求影响结构时创建。它描述现有结构是什么，以及本次方案会如何改变结构。

## 0. 状态

| 字段 | 内容 |
|---|---|
| 状态 | 完成 |
| 创建原因 | `sync-skill` 对 Claude target 的同步数据流从 symlink/fallback 改为通用 copy |
| 最后更新 | 2026-06-16 |

## 1. 现有结构快照

| 模块 / 文件 | 当前职责 | 与本需求关系 |
|---|---|---|
| `src/docs_driven_dev/sync.py` | 解析 sync target path，复制 skill，Claude symlink/fallback，doctor 输出 | 主要修改 |
| `src/docs_driven_dev/cli.py` | CLI executable module 和测试兼容 re-export | 移除 `link_claude_to_agents` re-export |
| `tests/test_cli.py` | CLI 行为和脚本合同测试 | 更新 Claude sync 测试 |
| `src/docs_driven_dev/release.py` | native update/uninstall dispatch 和 cleanup planning | 保持不变，继续支持 legacy symlink cleanup |
| `docs/*`, `README.md`, `skill/SKILL.md` | 用户和 agent 可见合同 | 更新当前同步模型说明 |

## 2. 当前调用链 / 数据流

```text
docdev sync-skill --targets claude
  -> cmd_sync_skill()
      -> parse_targets()
      -> if claude without agents: insert agents
      -> sync agents with copy_skill()
      -> sync claude with link_claude_to_agents()
          -> try symlink to ../../.agents/skills/docs-driven-dev
          -> fallback to copy when symlink fails
```

## 3. 目标结构

```text
docdev sync-skill --targets claude
  -> cmd_sync_skill()
      -> parse_targets()
      -> print resolved Claude target path
      -> copy_skill(source, claude_target, force)
          -> if legacy symlink and force: unlink it
          -> copy source skill directory
          -> write .docdev-skill-source marker
```

Default `all` / `default` target expansion remains:

```text
codex,cursor,agents,claude
  -> copy_skill(source, target_path_for(target), force) for each target
```

## 4. 模块与接口契约

| 模块 / 文件 | 新增 / 修改 | 职责 | 不应依赖 |
|---|---|---|---|
| `src/docs_driven_dev/sync.py` | 修改 | 对所有 targets 统一执行 copy replacement | Claude 不应依赖 Agents target 或 symlink 权限 |
| `src/docs_driven_dev/cli.py` | 修改 | 继续 re-export 当前可用 helper | 不 re-export 已删除的 Claude symlink helper |
| `tests/test_cli.py` | 修改 | 覆盖 Claude-only copy 和 legacy symlink replacement | 不 mock symlink failure as the normal path |
| `docs/DECISIONS.md` | 修改 | 用 D-033 supersede 旧 Claude symlink sync model | 不重写 D-003/D-015 历史 |

## 5. 数据、配置、资源变化

| 类型 | 路径 / 字段 | 变化 | 兼容性 |
|---|---|---|---|
| Sync target | `~/.claude/skills/docs-driven-dev` | 新 sync 写入普通目录和 `.docdev-skill-source` marker | 旧 symlink 在 force sync 时被 unlink |
| Env override | `DOCDEV_CLAUDE_SKILL_DIR`, `DOCDEV_CLAUDE_HOME` | 不变 | 继续通过 `target_path_for("claude")` 解析 |
| Uninstall cleanup | legacy Claude symlink | 不变 | 继续删除 symlink 本身 |
| Default targets | `codex,cursor,agents,claude` | 不变 | Native install/update 继续刷新四个 target |

## 6. 测试与观测点

- Unit: `test_claude_sync_copies_without_agents_dependency`
- Unit: `test_copy_skill_replaces_legacy_claude_symlink_when_forced`
- Full: `python3 -m unittest discover -s tests`
- Audit: `PYTHONPATH=src python3 -m docs_driven_dev.cli audit /Users/chihoyo/Project/docs-driven-dev`
- Text check: no current-contract docs should state Claude newly creates a symlink or symlink fallback.

# ARCHITECTURE - sync-skill 不再生成 skill-local wrappers

> 本文件只在需求影响结构时创建。它描述现有结构是什么，以及本次方案会如何改变结构。

## 0. 状态

| 字段 | 内容 |
|---|---|
| 状态 | 完成 |
| 创建原因 | `sync-skill` 的 target directory 副作用变化：不再生成 skill-local CLI wrappers |
| 最后更新 | 2026-06-12 |

## 1. 现有结构快照

| 模块 / 文件 | 当前职责 | 与本需求关系 |
|---|---|---|
| `src/docs_driven_dev/cli.py` `copy_skill()` | 复制 skill 目录、写 `.docdev-skill-source` marker、当前还调用 wrapper 生成 | 修改：移除 wrapper 生成 |
| `src/docs_driven_dev/cli.py` `write_installed_skill_wrapper()` | 生成 `bin/docdev` / PowerShell / CMD wrappers | 删除 |
| `scripts/install_cli.*` | 生成源码 checkout `.venv` 本地 CLI wrapper | 保留 |
| `scripts/install_remote.*` | 生成 native release launcher | 保留 |
| `tests/test_cli.py` | 保护 sync、wrapper、stale cleanup 行为 | 修改断言 |
| `skill/SKILL.md` | agent workflow 和 CLI resolution | 更新，不再说 source sync 会生成兼容 wrapper |

## 2. 当前调用链 / 数据流

```text
docdev sync-skill
  -> copy_skill(source skill, target)
      -> remove marked/forced target
      -> copy skill/
      -> write .docdev-skill-source
      -> write target/bin/docdev*
```

## 3. 目标结构

```text
docdev sync-skill
  -> copy_skill(source skill, target)
      -> remove marked/forced target
      -> copy skill/
      -> write .docdev-skill-source
      -> stop

agent CLI execution
  -> docdev on PATH
  -> or ~/.local/bin/docdev native launcher
```

## 4. 模块与接口契约

| 模块 / 文件 | 新增 / 修改 | 职责 | 不应依赖 |
|---|---|---|---|
| `copy_skill()` | 修改 | 同步 skill content 和 marker | CLI wrapper generation |
| `link_claude_to_agents()` | 保持 | symlink Claude target 或 copy fallback | skill-local CLI wrapper |
| `scripts/install_cli.*` | 保持 | 源码 checkout 本地 CLI 入口 | agent skill target |
| native launcher | 保持 | release install 的用户 CLI 入口 | source checkout |

## 5. 数据、配置、资源变化

| 类型 | 路径 / 字段 | 变化 | 兼容性 |
|---|---|---|---|
| 文件 | `<skill-target>/bin/docdev*` | 不再生成；下次 forced/marked sync 删除旧目录内残留 | 旧路径不可作为支持入口 |
| 配置 | `DOCDEV_PROJECT_DIR` | 仍由 native/source launchers 内部设置 | 用户不手动设置 |

## 6. 测试与观测点

- unit test: `copy_skill()` 不生成 `bin/docdev*`
- unit test: marked target replacement 删除旧 `bin/docdev`
- smoke: force sync 后本机 installed skill targets 无 `bin/docdev*`
- smoke: `docdev doctor`、`docdev audit`

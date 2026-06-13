# ARCHITECTURE - native uninstall command

> 本文件只在需求影响结构时创建。它描述现有结构是什么，以及本次方案会如何改变结构。

## 0. 状态

| 字段 | 内容 |
|---|---|
| 状态 | 完成 |
| 创建原因 | 新增 CLI command surface、native uninstall 数据流和删除路径安全契约 |
| 最后更新 | 2026-06-13 |

## 1. 现有结构快照

| 模块 / 文件 | 当前职责 | 与本需求关系 |
|---|---|---|
| `src/docs_driven_dev/commands.py` | 定义 CLI subcommands | 新增 `uninstall` parser |
| `src/docs_driven_dev/release.py` | native update dispatch | 新增 native uninstall handler 和安全删除 helpers |
| `src/docs_driven_dev/sync.py` | skill target path resolution 和 marker 写入 | 复用 target 路径和 ownership marker 规则 |
| `scripts/setup_project.sh` | source checkout target bootstrap | 通过 `sh "$DOCDEV"` 调 source wrapper，避免新生成 shell wrapper 直接 exec 的平台抖动 |
| `scripts/install_remote.sh` | Unix native install | 保持 install；uninstall 由 CLI 处理 |
| `scripts/install_remote.ps1` | Windows native install | 保持 install；uninstall 由 CLI 处理 |
| `tests/test_cli.py` | CLI / install / sync regression tests | 增加 uninstall 覆盖 |

## 2. 当前调用链 / 数据流

```text
scripts/install_remote.sh
  -> install root ~/.local/share/docdev
  -> launcher ~/.local/bin/docdev
  -> docdev sync-skill --targets codex,cursor,agents,claude --force
      -> marker .docdev-skill-source in copied skill targets
      -> Claude symlink when possible
```

## 3. 目标结构

```text
docdev uninstall [--dry-run | --yes] [--keep-skills]
  -> commands.py parser
  -> release.cmd_uninstall()
      -> resolve install root from --install-root / DOCDEV_INSTALL_ROOT / default
      -> resolve launcher from --bin-dir / DOCDEV_BIN_DIR / default
      -> resolve skill targets with sync.target_path_for()
      -> plan delete / skip actions
      -> require --yes before deletion
      -> delete install root, safe launcher, and owned skill targets
```

## 4. 模块与接口契约

| 模块 / 文件 | 新增 / 修改 | 职责 | 不应依赖 |
|---|---|---|---|
| `commands.py` | 修改 | Add `uninstall` args: `--yes`, `--dry-run`, `--keep-skills`, path overrides | deletion implementation details |
| `release.py` | 修改 | Plan and execute safe native uninstall | project docs/audit semantics |
| `sync.py` | 复用 | Provide skill target paths and marker semantics | native install root deletion |
| README / SKILL | 修改 | Document user-facing uninstall command | implementation internals |

## 5. 数据、配置、资源变化

| 类型 | 路径 / 字段 | 变化 | 兼容性 |
|---|---|---|---|
| CLI flag | `docdev uninstall --yes` | 新增 destructive confirmation | required for deletion |
| CLI flag | `docdev uninstall --dry-run` | 新增 preview mode | no writes |
| CLI flag | `docdev uninstall --keep-skills` | 新增 opt-out | skill targets retained |
| Path override | `--install-root` / `DOCDEV_INSTALL_ROOT` | 复用 | default `~/.local/share/docdev` |
| Path override | `--bin-dir` / `DOCDEV_BIN_DIR` | 复用 | default `~/.local/bin` |
| Skill override | `DOCDEV_<TARGET>_SKILL_DIR` / `DOCDEV_<TARGET>_HOME` | 复用 | default agent homes |

## 6. 测试与观测点

- dry-run 不删除 install root、launcher 或 skill targets。
- yes 删除 temp install root、safe launcher、marked skill target 和 Claude symlink。
- unmarked skill target 被 skip。
- keep-skills 不删除 skill targets。
- `docdev audit` 保持 No findings。

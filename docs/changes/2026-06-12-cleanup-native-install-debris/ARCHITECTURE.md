# ARCHITECTURE - 清理 native install 迁移残留

> 本文件只在需求影响结构时创建。它描述现有结构是什么，以及本次方案会如何改变结构。

## 0. 状态

| 字段 | 内容 |
|---|---|
| 状态 | 完成 |
| 创建原因 | native launcher 与源码 checkout maintenance path 的当前结构说明需要收敛 |
| 最后更新 | 2026-06-12 |

## 1. 现有结构快照

| 模块 / 文件 | 当前职责 | 与本需求关系 |
|---|---|---|
| `~/.local/bin/docdev` | native release launcher，指向 `~/.local/share/docdev/current` | 当前普通用户 / agent 入口，不依赖源码 checkout |
| `scripts/install_remote.sh` / `scripts/install_remote.ps1` | release installer，下载 manifest/artifact、校验 checksum、写 launcher | 保持不变 |
| `scripts/install_cli.*` / `scripts/update_cli.*` / `scripts/sync_skill.sh` | 源码 checkout 维护生命周期和 skill sync | 保留，不作为普通跨机器入口 |
| `src/docs_driven_dev/cli.py` `write_installed_skill_wrapper` | 为已同步 skill 写兼容 wrapper | 保留为维护兼容逻辑 |
| `temp/` | 旧纯 skill 参考材料 | 删除，当前流程由 `docs/changes/`、skill 和 templates 承接 |
| `docs/ARCHITECTURE.md` / `README.md` / `skill/templates/SPEC.md` | 当前文档和模板 | 更新措辞，明确 native-first 和 source maintenance 分层 |

## 2. 当前调用链 / 数据流

```text
普通跨机器使用:
  docdev on PATH
    -> ~/.local/bin/docdev
    -> ~/.local/share/docdev/current/src/docs_driven_dev/cli.py
    -> target project docs

源码维护:
  scripts/install.sh / scripts/update_cli.sh / scripts/sync_skill.sh
    -> source .venv wrapper
    -> tests / doctor / sync
    -> skill-local compatibility wrappers
```

## 3. 目标结构

```text
普通跨机器使用保持:
  docdev / ~/.local/bin/docdev
    -> native release current

源码维护保持:
  source checkout scripts
    -> local wrapper and compatibility wrappers

清理:
  remove temp/
  remove Python caches
  update docs/templates to stop presenting compatibility wrappers as normal agent fallback
```

## 4. 模块与接口契约

| 模块 / 文件 | 新增 / 修改 | 职责 | 不应依赖 |
|---|---|---|---|
| `docs/ARCHITECTURE.md` | 修改 | 当前结构说明 native launcher 是用户入口，源码 wrappers 是维护兼容物 | 不重写历史决策 |
| `README.md` | 修改 | 用户-facing 文案避免让 agent 依赖源码 wrapper | 不隐藏源码维护路径 |
| `skill/templates/SPEC.md` | 修改 | 分发示例不再默认写 source checkout + wrapper | 不影响模板结构 |
| `temp/` | 删除 | 移除旧 scratch 参考源 | 不删除 `docs/changes/` 模板 |

## 5. 数据、配置、资源变化

| 类型 | 路径 / 字段 | 变化 | 兼容性 |
|---|---|---|---|
| 配置 | `DOCDEV_PROJECT_DIR` | 行为不变；文档限定为 launcher/source maintenance 内部环境 | native 用户无需手动设置 |
| 资源 | `temp/` | 删除 tracked scratch | 当前 docs / git history 保留背景 |
| 运行产物 | `__pycache__` | 删除 | 仍由 `.gitignore` 排除 |

## 6. 测试与观测点

- `PYTHONPATH=src python3 -m unittest discover -s tests`
- `/Users/chihoyo/.local/bin/docdev doctor`
- `/Users/chihoyo/.local/bin/docdev audit /Users/chihoyo/Project/docs-driven-dev`
- `git ls-files temp`
- `find . -maxdepth 3 -type d ...`

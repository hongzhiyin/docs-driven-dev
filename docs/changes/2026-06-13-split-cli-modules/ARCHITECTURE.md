# ARCHITECTURE - cli.py 轻量拆分

> 本文件只在需求影响结构时创建。它描述现有结构是什么，以及本次方案会如何改变结构。

## 0. 状态

| 字段 | 内容 |
|---|---|
| 状态 | 完成 |
| 创建原因 | CLI package 模块边界变化 |
| 最后更新 | 2026-06-13 |

## 1. 现有结构快照

| 模块 / 文件 | 当前职责 | 与本需求关系 |
|---|---|---|
| `src/docs_driven_dev/cli.py` | config/path、template/change packet、audit/status/decision、sync/doctor、native update、argparse 全部逻辑 | 拆分主体 |
| `tests/test_cli.py` | 覆盖 CLI 命令、sync、installer、package、skill 文档约束 | 调整内部 patch 点，保持行为测试 |
| `scripts/package_release.sh` | 打包整个 `src/`、skill、scripts，并生成 manifest/checksum | 验证新模块进入 release artifact |
| `scripts/install_remote.*` | native release install/update helper | 不改行为，只依赖入口 module 不变 |
| `docs/ARCHITECTURE.md` | 当前项目结构 source of truth | 更新 CLI package 模块表 |

## 2. 当前调用链 / 数据流

```text
docdev / python -m docs_driven_dev.cli
  -> src/docs_driven_dev/cli.py
      -> parse args
      -> run init/change/audit/status/decision/sync/doctor/update logic in same file
      -> filesystem / subprocess side effects
```

## 3. 目标结构

```text
docdev / python -m docs_driven_dev.cli
  -> docs_driven_dev.cli
      -> docs_driven_dev.commands.main()
          -> templates.cmd_init / templates.cmd_new_change
          -> audit.cmd_audit / audit.cmd_status / audit.cmd_new_decision
          -> sync.cmd_sync_skill / sync.cmd_doctor
          -> release.cmd_update
      -> compatibility re-exports for existing tests/imports
```

Shared helpers:

```text
paths.py
  -> constants, docs_dir/config/source/template path resolution

models.py
  -> Finding dataclass used by audit reports
```

## 4. 模块与接口契约

| 模块 / 文件 | 新增 / 修改 | 职责 | 不应依赖 |
|---|---|---|---|
| `src/docs_driven_dev/cli.py` | 修改 | Public CLI module、`python -m` entrypoint、主要兼容 re-export | 业务逻辑实现细节 |
| `src/docs_driven_dev/commands.py` | 新增 | argparse parser 和 subcommand dispatch | 文件复制、audit 解析、sync 细节 |
| `src/docs_driven_dev/paths.py` | 新增 | 常量、source root、config、docs/generated/changes/template path resolution | argparse 或命令副作用 |
| `src/docs_driven_dev/models.py` | 新增 | 共享数据模型 `Finding` | CLI dispatch |
| `src/docs_driven_dev/templates.py` | 新增 | `init`、`new-change`、模板复制和 README/AGENTS pointer | audit/sync/release 副作用 |
| `src/docs_driven_dev/audit.py` | 新增 | docs/change packet audit、status、decision skeleton | sync target 写入、native install |
| `src/docs_driven_dev/sync.py` | 新增 | skill target path、copy/link、sync-skill、doctor | release download/update dispatch |
| `src/docs_driven_dev/release.py` | 新增 | `docdev update` 到 native installer 的 dispatch | audit/template 解析 |
| `tests/test_cli.py` | 修改 | 继续通过 `cli.main` 测用户命令，内部 patch 点指向真实模块 | 旧单文件内部结构 |

## 5. 数据、配置、资源变化

| 类型 | 路径 / 字段 | 变化 | 兼容性 |
|---|---|---|---|
| Python module | `src/docs_driven_dev/*.py` | 新增轻模块 | stdlib-only，随 `src/` 打包 |
| Public entry | `docs_driven_dev.cli` | 保留入口和 re-export | `python -m docs_driven_dev.cli` 不变 |
| CLI commands | `docdev ...` | 不新增、不删除、不改默认值 | 行为兼容 |
| Config/env | `.docdev.toml`、`DOCDEV_*` | 不变 | 不迁移 |

## 6. 测试与观测点

- 单元测试：`python3 -m unittest discover -s tests`
- 入口 smoke：`PYTHONPATH=src python3 -m docs_driven_dev.cli --version`
- 项目 audit：`/Users/chihoyo/.local/bin/docdev audit /Users/chihoyo/Project/docs-driven-dev`
- package/install smoke 通过既有 tests 覆盖 `package_release.sh` 与 `install_remote.sh`

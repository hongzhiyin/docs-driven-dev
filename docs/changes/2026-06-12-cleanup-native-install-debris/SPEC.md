# SPEC - 清理 native install 迁移残留

> 本文件描述本次需求应该满足什么。它不写实现细节、不追踪进度、不解释历史取舍。

## 0. 状态

| 字段 | 内容 |
|---|---|
| 状态 | 完成 |
| 需求来源 | 用户请求：native install 已可通过 `docdev` 调用后，清理旧 wrapper 或临时代码 |
| 工作包目录 | `docs/changes/2026-06-12-cleanup-native-install-debris/` |
| 最后更新 | 2026-06-12 |

## 1. 一句话目标

在 v0.1.3 native install 成为正常用户入口后，仓库应移除旧迁移 scratch / 运行缓存，并把当前文档、模板中的源码 wrapper 表述收敛为开发维护兼容路径。

## 2. 背景与问题

- 当前行为：仓库仍跟踪 `temp/` 旧参考材料，工作区出现 Python `__pycache__`，且 `docs/ARCHITECTURE.md`、`README.md`、`skill/templates/SPEC.md` 仍有若干源码 wrapper / source checkout 表述需要和 native install 现状对齐。
- 问题：native install 已经提供 `~/.local/bin/docdev` launcher，旧参考目录和泛化 wrapper 文案会让未来 agent 误以为源码 checkout 是普通跨机器入口。
- 期望收益：源码仓库更干净；用户和 agent 都能清楚区分 native release install 与源码 checkout maintenance path。

## 3. 范围

### 3.1 本次要做

- 删除不属于 source-of-truth 的旧迁移 scratch 目录 `temp/`。
- 清理运行缓存目录，例如 `__pycache__`。
- 更新当前架构文档、README 和模板示例，避免把源码 wrapper 描述成普通跨机器分发入口。
- 记录为什么保留源码 checkout 维护脚本和 skill-local compatibility wrappers。

### 3.2 本次不做

- 不删除 `scripts/install_cli.*`、`scripts/update_cli.*`、`scripts/sync_skill.sh`、`scripts/setup_project.sh`。
- 不移除 CLI 内部 `DOCDEV_PROJECT_DIR` / `PYTHONPATH` launcher 机制。
- 不改变 native install、`docdev update` 或 skill sync 的运行行为。
- 不重写历史 D-XXX 决策原文；需要改变当前判断时追加新决策。

## 4. 用户场景 / 使用流程

| 场景 ID | 触发条件 | 期望结果 |
|---|---|---|
| S1 | 用户或 agent 阅读 README / skill 后要使用 docs-driven-dev | 首选 `docdev` 或 `~/.local/bin/docdev`，不会被引导去猜源码 checkout wrapper |
| S2 | 维护者在源码 checkout 中开发、测试或同步 skill | 仍可使用源码维护脚本和兼容 wrapper |
| S3 | 未来 agent 扫描仓库寻找临时材料 | 不再把旧 `temp/` 目录当成当前 doctrine |

## 5. 功能需求

| ID | 需求 | 验收方式 | 状态 |
|---|---|---|---|
| R1 | 工作区不保留 Python cache 或旧 `temp/` 迁移 scratch | `find` / `git status` / `git ls-files temp` | 完成 |
| R2 | 当前文档把 native launcher 定义为普通跨机器入口，把源码 wrapper 定义为维护兼容路径 | 文档审阅和 `rg` | 完成 |
| R3 | CLI 测试、doctor/audit 仍通过，证明源码维护路径未被误删 | `python3 -m unittest`、`docdev audit`、`docdev doctor` | 完成 |

## 6. 约束与不变式

1. **#1**: 普通跨机器 agent CLI resolution 只能依赖 `docdev` on `PATH` 或 native launcher；不能重新引入猜源码路径或 skill-local wrapper 的正常 fallback。
2. **#2**: 源码 checkout maintenance path 必须继续可用，避免维护者失去 install/test/sync/update 生命周期。
3. **#3**: 旧参考材料可以删除，但根 source-of-truth docs 和历史 DECISIONS 不能被静默改写成“从未存在过”的历史。

## 7. 兼容性与默认行为

| 场景 | 默认行为 |
|---|---|
| 已发布 native install | 保持不变，继续使用 `~/.local/bin/docdev` 和 `docdev update` |
| 源码 checkout 开发者 | 保持 `./scripts/install.sh`、`./scripts/update_cli.sh`、`./scripts/sync_skill.sh` 可用 |
| 已同步 skill-local wrappers | 保留为开发维护兼容入口，不作为普通跨机器 agent fallback |
| 历史 `temp/` 参考材料 | 删除 tracked scratch，当前需求流程由 `docs/changes/` 模板和 skill 承接 |

## 8. 验收标准

1. `temp/` 和 Python cache 不再留在仓库工作区。
2. README / ARCHITECTURE / 模板示例不再把源码 wrapper 当作普通跨机器入口。
3. `PYTHONPATH=src python3 -m unittest discover -s tests`、`docdev audit`、`docdev doctor` 通过。

## 9. 开放问题

| ID | 问题 | 当前判断 | 是否阻塞实现 |
|---|---|---|---|
| Q1 | 是否删除源码 checkout 维护脚本 | 不删除；它们仍是维护路径，不是旧临时代码 | 否 |

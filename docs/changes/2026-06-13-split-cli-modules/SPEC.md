# SPEC - cli.py 轻量拆分

> 本文件描述本次需求应该满足什么。它不写实现细节、不追踪进度、不解释历史取舍。

## 0. 状态

| 字段 | 内容 |
|---|---|
| 状态 | 完成 |
| 需求来源 | 用户请求：在继续增加 release/update/audit 能力前，先把 940 行 `cli.py` 拆成轻模块 |
| 工作包目录 | `docs/changes/2026-06-13-split-cli-modules/` |
| 最后更新 | 2026-06-13 |

## 1. 一句话目标

让 `docdev` CLI 在命令行为不变的前提下，把当前单文件实现拆成按职责分组的轻模块，为后续 Windows、签名、JSON doctor/status 等功能留下清晰扩展面。

## 2. 背景与问题

- 当前行为：`src/docs_driven_dev/cli.py` 同时承担 config/path、template/change packet、audit/status/decision、sync/doctor、native update 和 argparse dispatch。
- 问题：单文件 940 行在 v0.1.x 仍可维护，但继续加 release/update/audit 相关功能会让职责边界变模糊，测试 patch 点也更容易绑定内部实现。
- 期望收益：保持 `python -m docs_driven_dev.cli` 和 `docdev` 命令稳定，同时让后续功能能进入对应模块，而不是继续堆到入口文件。

## 3. 范围

### 3.1 本次要做

- 新增轻模块承接现有职责：`audit.py`、`sync.py`、`release.py`、`templates.py`、`commands.py`，并按需要补充共享的 path/model 模块。
- 保留 `src/docs_driven_dev/cli.py` 作为 CLI 入口和兼容 re-export 层。
- 调整测试中针对内部 patch 点的引用，让测试保护新模块边界。
- 更新根 `ARCHITECTURE.md`、`ROADMAP.md`、`DECISIONS.md` 和本工作包，记录模块拆分后的结构。

### 3.2 本次不做

- 不新增 `docdev` 用户命令、参数或输出格式。
- 不实现 Windows 签名、JSON doctor/status、release signing 或新的 update 策略。
- 不 bump version，不发布 GitHub Release。
- 不改变 native install、source checkout install、skill sync 或 audit 的语义。

## 4. 用户场景 / 使用流程

| 场景 ID | 触发条件 | 期望结果 |
|---|---|---|
| S1 | 用户运行现有 `docdev init/new-change/audit/status/new-decision/sync-skill/doctor/update` 命令 | 行为、输出和 exit code 与拆分前保持一致 |
| S2 | 开发者继续通过 `python -m docs_driven_dev.cli` 或 native launcher 进入 CLI | `docs_driven_dev.cli` 仍是稳定入口，不需要知道内部模块 |
| S3 | 后续功能要扩展 audit、sync、release 或 argparse | 可以进入对应轻模块，不再把所有逻辑追加到 `cli.py` |

## 5. 功能需求

| ID | 需求 | 验收方式 | 状态 |
|---|---|---|---|
| R1 | `docdev` 现有命令行为不因模块拆分改变 | `python3 -m unittest discover -s tests` | 完成 |
| R2 | `src/docs_driven_dev/cli.py` 保持为 `python -m docs_driven_dev.cli` 的入口，并继续导出主要兼容符号 | 单元测试和手工 `--version` | 完成 |
| R3 | 新模块按职责分组，避免 release/update/audit/sync/template 逻辑互相依赖 | 代码审阅、ARCHITECTURE 更新 | 完成 |
| R4 | release packaging 包含新模块，native smoke 仍可通过 launcher 运行 init/audit | package_release 测试 / install_remote smoke 测试 | 完成 |
| R5 | source-of-truth docs 和 change packet 通过 `docdev audit` | `docdev audit /Users/chihoyo/Project/docs-driven-dev` | 完成 |

## 6. 约束与不变式

1. **#1**: `docdev` 用户可见命令面、默认值、输出语义和 exit code 不得因拆分改变。
2. **#2**: `docs_driven_dev.cli` 必须继续作为 public CLI module；内部模块不能要求调用方改用新 module path。
3. **#3**: CLI 仍保持 Python 3.10+ stdlib-only，不引入 packaging/runtime 依赖。
4. **#4**: 本次拆分不得改变 generated report 位置、skill sync replacement 语义或 native checksum/update 语义。

## 7. 兼容性与默认行为

| 场景 | 默认行为 |
|---|---|
| 旧脚本执行 `python -m docs_driven_dev.cli ...` | 保持可用 |
| 测试或外部代码 import `docs_driven_dev.cli.audit_project` 等主要 helper | 通过 `cli.py` 兼容导出继续可用 |
| package release 打包 `src/docs_driven_dev/` | 新模块随 `src/` 一起进入 tarball |
| 运行在 native release launcher 下 | launcher 仍设置 `DOCDEV_PROJECT_DIR` 和 `PYTHONPATH`，入口模块不变 |

## 8. 验收标准

1. `src/docs_driven_dev/cli.py` 缩减为入口/兼容层，核心职责迁移到轻模块。
2. `python3 -m unittest discover -s tests` 通过。
3. `PYTHONPATH=src python3 -m docs_driven_dev.cli --version` 和 `docdev audit /Users/chihoyo/Project/docs-driven-dev` 通过。
4. 本工作包和根文档记录模块边界、取舍和验证结果。

## 9. 开放问题

| ID | 问题 | 当前判断 | 是否阻塞实现 |
|---|---|---|---|
| Q1 | 是否要借本次拆分新增更细的 public API？ | 不需要；`cli.py` 保持兼容导出，其他模块先作为内部实现 | 否 |

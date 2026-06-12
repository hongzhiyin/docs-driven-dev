# ROADMAP - cli.py 轻量拆分

> 本文件追踪本次需求做到哪一步。它承接 SPEC 的验收标准，记录调研、门禁、任务和验证结果。

## 0. 当前状态

**阶段 / Phase**: 已完成
**当前 Step / Current Step**: Step 5 - 验证与收尾完成
**ARCHITECTURE 省略理由 / Architecture Omission Reason**: 不省略。本次改变 CLI package 的模块边界和调用链。

## 1. Gates

### Pre-Implementation Gate

- [x] 用户目标已用一句话确认
- [x] 范围和非目标已写入 SPEC
- [x] 现有实现、调用点、测试和配置已调研
- [x] 关键约束 / 不变式已写入 SPEC
- [x] 需要的 DECISIONS 条目已记录或标记为阻塞
- [x] 实现步骤和验收方式已写清
- [x] 用户已确认实现方案

### Completion Gate

- [x] 所有实施任务完成或有明确跳过理由
- [x] 验收标准逐条验证
- [x] 文档与最终实现一致
- [x] 剩余风险和后续工作已记录

## 2. 调研记录

| ID | 主题 | 发现 | 证据 / 文件 | 结论 |
|---|---|---|---|---|
| R-1 | 当前入口规模 | `cli.py` 约 940 行，包含 path/config、template/change packet、audit/status/decision、sync/doctor、native update、argparse dispatch | `src/docs_driven_dev/cli.py` | 需要按职责拆分，避免继续增长 |
| R-2 | 兼容调用点 | 测试直接 import `docs_driven_dev.cli` 并使用 `audit_project`、`docs_dir_for`、`copy_skill`、`target_path_for` 等 helper | `tests/test_cli.py` | `cli.py` 应保留兼容 re-export |
| R-3 | patch 点 | 测试 patch `docs_driven_dev.cli.find_source_root`、`docs_driven_dev.cli.subprocess.run`、`docs_driven_dev.cli.target_path_for` 等内部点 | `tests/test_cli.py` | patch 点应迁到真实实现模块，避免假兼容 |
| R-4 | release packaging | package script 打包整个 `src/`，当前测试只显式检查 `cli.py` 在 tarball 中 | `scripts/package_release.sh`、`tests/test_cli.py` | 新模块会随 `src/` 进入 artifact，可补充断言保护 |
| R-5 | 架构文档 | 根 `ARCHITECTURE.md` 仍把 CLI package 描述成单个职责聚合 | `docs/ARCHITECTURE.md` | 根架构需要更新模块表和 CLI dispatch 数据流 |

## 3. Step 状态总览

| Step | 内容 | 状态 |
|---|---|---|
| 0 | 建立需求工作包 | 完成 |
| 1 | 澄清需求与范围 | 完成 |
| 2 | 调研既有实现 | 完成 |
| 3 | 形成并确认方案 | 完成 |
| 4 | 实施代码与测试 | 完成 |
| 5 | 验证与收尾 | 完成 |

---

## Step 0 - 建立需求工作包

**Goal**: 创建 SPEC / ROADMAP / DECISIONS / ARCHITECTURE。

**Tasks**:
- [x] 初始化工作包文档
- [x] 记录 ARCHITECTURE 需要及理由

**Acceptance**:
1. 工作包目录存在，且文档结构清晰。

---

## Step 1 - 澄清需求与范围

**Goal**: 把“轻量拆分 cli.py”转成可验收的行为描述。

**Tasks**:
- [x] 补全 SPEC 一句话目标
- [x] 补全范围 / 非目标
- [x] 列出开放问题

**Acceptance**:
1. SPEC 明确本次只做结构拆分，不新增功能。

---

## Step 2 - 调研既有实现

**Goal**: 找出可安全迁移的职责块和需要兼容的调用点。

**Tasks**:
- [x] 读取 `cli.py` 函数分组和常量
- [x] 读取 `tests/test_cli.py` 直接 import / patch 点
- [x] 检查 root docs 中对 CLI package 的描述

**Acceptance**:
1. ROADMAP 调研表记录具体文件和影响方案。

---

## Step 3 - 形成方案

**Goal**: 确定模块边界和兼容策略。

**Tasks**:
- [x] 在 ARCHITECTURE 写目标模块和调用链
- [x] 在 DECISIONS 记录薄入口 + 内部轻模块的取舍
- [x] 在根 DECISIONS 追加 D-026

**Acceptance**:
1. 模块拆分方案有明确职责边界，并保留 `docs_driven_dev.cli` 入口。

---

## Step 4 - 拆分代码并保持兼容

**Goal**: 把核心逻辑移出 `cli.py`，保持命令行为和主要兼容导出。

**Tasks**:
- [x] 新增 shared path/model 模块
- [x] 把 init/change template 逻辑迁到 `templates.py`
- [x] 把 audit/status/decision 逻辑迁到 `audit.py`
- [x] 把 sync/doctor 逻辑迁到 `sync.py`
- [x] 把 native update dispatch 迁到 `release.py`
- [x] 把 argparse/main 迁到 `commands.py`
- [x] 将 `cli.py` 改为入口和 re-export 层
- [x] 更新测试 patch 点和 packaging 断言

**Acceptance**:
1. `docdev --version`、tests 和 audit 仍通过。

## 4. 验证记录

| 验收项 | 验证方式 | 结果 | 备注 |
|---|---|---|---|
| SPEC-1 | `python3 -m unittest discover -s tests` | 通过 | 31 tests OK |
| SPEC-2 | `PYTHONPATH=src python3 -m docs_driven_dev.cli --version` | 通过 | `docdev 0.1.4` |
| SPEC-3 | `PYTHONPATH=src python3 -m docs_driven_dev.cli audit /Users/chihoyo/Project/docs-driven-dev` | 通过 | No findings |
| SPEC-4 | `/Users/chihoyo/.local/bin/docdev audit /Users/chihoyo/Project/docs-driven-dev` | 通过 | No findings |

## Step 5 - 验证与收尾

**Goal**: 证明拆分后的 CLI 行为和 docs-driven 约束仍然成立。

**Tasks**:
- [x] 运行完整单元测试
- [x] 运行 source entrypoint smoke
- [x] 运行 source CLI audit 和已安装 native CLI audit
- [x] 更新本工作包与根 ROADMAP

**Acceptance**:
1. tests、entrypoint smoke 和 audit 均通过。
2. `cli.py` 保持薄入口，核心逻辑进入轻模块。

## 5. 风险与后续

| ID | 风险 / 后续 | 影响 | 处理 |
|---|---|---|---|
| F-1 | `cli.py` 兼容导出可能让内部 API 看起来仍是 public | 外部调用可能继续绑定旧 helper | 接受；本次目标是行为兼容，未来若要 public API 再单独设计 |
| F-2 | patch 点迁移暴露测试对实现细节耦合 | 测试维护成本略增 | 缓解：只把 patch 改到真实实现模块，用户命令测试仍走 `cli.main` |

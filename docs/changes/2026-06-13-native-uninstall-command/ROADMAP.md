# ROADMAP - native uninstall command

> 本文件追踪本次需求做到哪一步。它承接 SPEC 的验收标准，记录调研、门禁、任务和验证结果。

## 0. 当前状态

**阶段 / Phase**: 已完成
**当前 Step / Current Step**: Step 6 - 发布 v0.1.6 release 完成
**ARCHITECTURE 省略理由 / Architecture Omission Reason**: 不省略。本次新增 CLI 命令面、native lifecycle 数据流和删除路径安全契约。

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
| R-1 | 命令面 | `commands.py` 已有 `update`，没有 `uninstall` | `src/docs_driven_dev/commands.py` | 新增 subcommand 和确认参数 |
| R-2 | native install path | installer 默认写 `~/.local/share/docdev` 和 `~/.local/bin/docdev`，支持 env/arg overrides | `scripts/install_remote.sh`、`scripts/install_remote.ps1` | uninstall 使用相同路径合同 |
| R-3 | skill target ownership | sync 写 `.docdev-skill-source` marker；Claude 可为 symlink | `src/docs_driven_dev/sync.py` | uninstall 只删除 marker 目录或 symlink |
| R-4 | 测试结构 | native update 和 install smoke 已在 `tests/test_cli.py` | `tests/test_cli.py` | 增加 dry-run、yes、keep-skills、unmarked skip 覆盖 |
| R-5 | 文档现状 | README 只有 install/update，没有正式 uninstall | `README.md`、`skill/SKILL.md` | 补新机器反复验证命令 |
| R-6 | setup_project wrapper 调用 | 测试中直接执行新生成 wrapper 偶发 `Killed: 9`；`sh "$DOCDEV"` 路径稳定 | `scripts/setup_project.sh`、`tests/test_cli.py` | 顺手改为通过 shell 调用 source wrapper |

## 3. Step 状态总览

| Step | 内容 | 状态 |
|---|---|---|
| 0 | 建立需求工作包 | 完成 |
| 1 | 澄清需求与范围 | 完成 |
| 2 | 调研既有实现 | 完成 |
| 3 | 形成并确认方案 | 完成 |
| 4 | 实施代码与测试 | 完成 |
| 5 | 验证与收尾 | 完成 |
| 6 | 发布 v0.1.6 release | 完成 |

---

## Step 0 - 建立需求工作包

**Goal**: 创建 SPEC / ROADMAP / DECISIONS，并决定是否需要 ARCHITECTURE。

**Tasks**:
- [x] 初始化工作包文档
- [x] 记录 ARCHITECTURE 是否需要及理由

**Acceptance**:
1. 工作包目录存在，且文档结构清晰。

---

## Step 1 - 澄清需求与范围

**Goal**: 把粗略需求转成可验收的行为描述。

**Tasks**:
- [x] 补全 SPEC 一句话目标
- [x] 补全范围 / 非目标
- [x] 列出开放问题

**Acceptance**:
1. 用户确认 SPEC 的目标、范围和非目标。

---

## Step 2 - 调研既有实现

**Goal**: 找出 install/update/sync 路径和 ownership marker。

**Tasks**:
- [x] 读取 `commands.py`、`release.py`、`sync.py`
- [x] 读取 remote installer 和测试
- [x] 记录删除路径安全边界

**Acceptance**:
1. 调研表包含命令面、路径、marker 和测试入口。

---

## Step 3 - 形成方案

**Goal**: 选择安全、可自动化的新机器卸载入口。

**Tasks**:
- [x] 在 packet DECISIONS 记录内置 CLI uninstall 方案
- [x] 在根 DECISIONS 追加 D-028
- [x] 在 ARCHITECTURE 写目标数据流

**Acceptance**:
1. 删除范围、确认参数、dry-run 和 skip 规则明确。

---

## Step 4 - 实施代码与测试

**Goal**: 增加 `docdev uninstall` 并覆盖安全删除行为。

**Tasks**:
- [x] 更新 argparse command surface
- [x] 实现 native install root、launcher 和 skill target 删除逻辑
- [x] 更新 README / SPEC / ARCHITECTURE / ROADMAP / SKILL
- [x] 增加单元测试和 smoke checks

**Acceptance**:
1. `docdev uninstall --dry-run` 不删除路径。
2. `docdev uninstall --yes` 删除 temp install root、launcher 和 marked skill targets。
3. unmarked skill target 被跳过。

## 4. 验证记录

| 验收项 | 验证方式 | 结果 | 备注 |
|---|---|---|---|
| SPEC-1 | `python3 -m unittest discover -s tests` | 通过 | 36 tests OK |
| SPEC-2 | `PYTHONPATH=src python3 -m docs_driven_dev.cli --version` | 通过 | `docdev 0.1.5` |
| SPEC-3 | `PYTHONPATH=src python3 -m docs_driven_dev.cli audit /Users/chihoyo/Project/docs-driven-dev` | 通过 | No findings |
| SPEC-4 | `PYTHONPATH=src python3 -m docs_driven_dev.cli uninstall --dry-run ...` | 通过 | nonexistent temp root/bin; real skill targets only planned, not deleted |
| SPEC-5 | local package + install + `docdev uninstall --dry-run` + `docdev uninstall --yes` | 通过 | temp root/bin/skill homes under `/private/tmp/docdev-uninstall-smoke.bgbus0`; confirmed paths removed |
| REL-1 | `python3 -m unittest discover -s tests` | 通过 | 36 tests OK |
| REL-2 | `PYTHONPATH=src python3 -m docs_driven_dev.cli --version` | 通过 | `docdev 0.1.6` |
| REL-3 | `PYTHONPATH=src python3 -m docs_driven_dev.cli audit /Users/chihoyo/Project/docs-driven-dev` | 通过 | No findings |
| REL-4 | `./scripts/package_release.sh --out /private/tmp/docdev-release-assets-0.1.6` | 通过 | artifact, checksum, manifest, installers; tar exclude check clean |
| REL-5 | local `file://` install/uninstall smoke | 通过 | `/private/tmp/docdev-016-local-smoke.FsWa1f`; launcher `docdev 0.1.6`; uninstall removed temp root/bin/skill targets |
| REL-6 | public latest install/uninstall smoke | 通过 | `/private/tmp/docdev-016-public-smoke.jroWX7`; GitHub latest installed `0.1.6`; launcher `docdev 0.1.6`; uninstall removed temp root/bin/skill targets |

## Step 5 - 验证与收尾

**Goal**: 证明卸载命令、安全边界和 docs-driven 约束都成立。

**Tasks**:
- [x] 运行完整单元测试
- [x] 运行 entrypoint smoke
- [x] 运行 temp native install/uninstall smoke
- [x] 运行项目 audit 和 diff check
- [x] 更新本工作包与根 ROADMAP

**Acceptance**:
1. tests、entrypoint smoke、uninstall smoke 和 audit 均通过。
2. 本次 change packet 记录剩余 Windows live verification 风险。

## Step 6 - 发布 v0.1.6 release

**Goal**: 把 `docdev uninstall` 纳入 GitHub Release / native installer 分发路径。

**Tasks**:
- [x] bump package version to `0.1.6`
- [x] run tests, entrypoint smoke, audit, and diff check
- [x] package release assets
- [x] run local native install/uninstall smoke
- [x] tag and publish `v0.1.6`
- [x] run public latest install/uninstall smoke

**Acceptance**:
1. release launcher prints `docdev 0.1.6`.
2. local and public latest smoke can run `docdev uninstall --dry-run` and `docdev uninstall --yes`.
3. verification table records package, test, audit, and smoke evidence.

## 5. 风险与后续

| ID | 风险 / 后续 | 影响 | 处理 |
|---|---|---|---|
| F-1 | 误删用户目录 | 高影响 | 缓解：`--yes` 确认、dry-run、只删具体 docdev 路径和 marker/symlink skill targets |
| F-2 | Windows 删除运行中的 launcher 可能有平台差异 | 中影响 | 先用 stdlib path deletion 和 PowerShell docs；真实 Windows live verification 后再细化 |

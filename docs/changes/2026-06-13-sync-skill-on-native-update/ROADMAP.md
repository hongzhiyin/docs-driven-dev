# ROADMAP - native update 默认刷新 skill

> 本文件追踪本次需求做到哪一步。它承接 SPEC 的验收标准，记录调研、门禁、任务和验证结果。

## 0. 当前状态

**阶段 / Phase**: 已完成
**当前 Step / Current Step**: Step 5 - 验证与收尾完成
**ARCHITECTURE 省略理由 / Architecture Omission Reason**: 不省略。本次改变 native install/update 的默认副作用和数据流。

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
| R-1 | CLI update dispatch | `cmd_update` 只在 `args.sync_skill` 为真时向 installer 追加 `--sync-skill` | `src/docs_driven_dev/release.py` | 改为默认 sync，并新增 no-sync opt-out |
| R-2 | argparse | `commands.py` 只有 `--sync-skill`，无 opt-out | `src/docs_driven_dev/commands.py` | 保留 `--sync-skill`，新增 `--no-sync-skill` |
| R-3 | Unix installer | `SYNC_SKILL=0`，只有 `--sync-skill` 才运行 launcher sync | `scripts/install_remote.sh` | 默认值改为 1，新增 `--no-sync-skill` |
| R-4 | PowerShell installer | `[switch]$SyncSkill` 默认 false | `scripts/install_remote.ps1` | 默认 sync，新增 `[switch]$NoSyncSkill` |
| R-5 | docs wording | README、SPEC、ARCHITECTURE、SKILL 多处说明 sync 是显式可选 | `README.md`、`docs/SPEC.md`、`docs/ARCHITECTURE.md`、`skill/SKILL.md` | 当前合同需要更新并由 D-027 supersede |
| R-6 | tests | local install smoke 目前不传 sync env，默认 sync 后可能写真实 skill homes；重 tar/install smoke 连跑后再跑 setup_project 在本机出现过 `Killed: 9` 抖动 | `tests/test_cli.py` | 用 dispatch/static tests 验证默认 sync，用 no-sync local smoke 验证 install/update 主路径 |

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
1. 工作包目录存在，且结构影响已说明。

---

## Step 1 - 澄清需求与范围

**Goal**: 明确 native update 默认应刷新 skill。

**Tasks**:
- [x] 补全 SPEC 一句话目标
- [x] 补全范围 / 非目标
- [x] 列出 opt-out 兼容要求

**Acceptance**:
1. SPEC 明确默认 sync 与 `--no-sync-skill` opt-out。

---

## Step 2 - 调研既有实现

**Goal**: 找出所有把 sync 描述为显式可选的代码和文档。

**Tasks**:
- [x] 读取 update dispatch、installer、README、SKILL、SPEC、ARCHITECTURE
- [x] 检查 tests 中 update/install smoke 的副作用范围

**Acceptance**:
1. 调研表记录具体文件和改动方向。

---

## Step 3 - 形成方案

**Goal**: 记录取舍并避免隐式写入没有逃生口。

**Tasks**:
- [x] 在 packet DECISIONS 记录默认 sync + opt-out
- [x] 在根 DECISIONS 追加 D-027
- [x] 在 ARCHITECTURE 写目标数据流

**Acceptance**:
1. 默认行为和 opt-out 的理由、风险、测试路径都清楚。

---

## Step 4 - 实施代码与测试

**Goal**: 让 native install/update 默认刷新 skill，并保护 opt-out。

**Tasks**:
- [x] 更新 `commands.py` 的 update 参数
- [x] 更新 `release.py` 的 installer 参数生成
- [x] 更新 `install_remote.sh` 和 `install_remote.ps1`
- [x] 更新 README / SPEC / ARCHITECTURE / ROADMAP / SKILL
- [x] 更新 tests 覆盖默认 sync 和 opt-out

**Acceptance**:
1. tests、entrypoint smoke 和 audit 通过。

## 4. 验证记录

| 验收项 | 验证方式 | 结果 | 备注 |
|---|---|---|---|
| SPEC-1 | `python3 -m unittest discover -s tests` | 通过 | 32 tests OK |
| SPEC-2 | `PYTHONPATH=src python3 -m docs_driven_dev.cli --version` | 通过 | `docdev 0.1.5` |
| SPEC-3 | `PYTHONPATH=src python3 -m docs_driven_dev.cli audit /Users/chihoyo/Project/docs-driven-dev` | 通过 | No findings |
| SPEC-4 | `git diff --check` | 通过 | no output |
| SPEC-5 | `./scripts/package_release.sh --out /private/tmp/docdev-release-assets-0.1.5` | 通过 | 生成 tarball、checksum、manifest、Unix/PowerShell installer assets |
| SPEC-6 | `./scripts/install_remote.sh --release-base-url file:///private/tmp/docdev-release-assets-0.1.5 ...` | 通过 | 默认 sync 到 `/private/tmp/docdev-015-smoke.13FF0t/skill-homes` |
| SPEC-7 | `/private/tmp/docdev-015-smoke.13FF0t/bin/docdev --version`, `init`, `audit` | 通过 | `docdev 0.1.5`; temp project audit No findings |
| SPEC-8 | `find /private/tmp/docdev-015-smoke.13FF0t/skill-homes -path '*/bin/docdev*' -print` | 通过 | no output，默认 sync 未恢复 skill-local wrappers |
| SPEC-9 | `tar -tzf /private/tmp/docdev-release-assets-0.1.5/docdev-0.1.5.tar.gz \| rg '(__pycache__|\\.pyc|(^|/)\\.git|(^|/)\\.venv|docs/_generated/docdev/.+)'` | 通过 | rg exit 1，未匹配污染项 |

## Step 5 - 验证与收尾

**Goal**: 证明默认 sync、no-sync opt-out 和 docs-driven 约束都成立。

**Tasks**:
- [x] 运行完整单元测试
- [x] 运行 entrypoint smoke
- [x] 运行项目 audit
- [x] 更新本工作包与根 ROADMAP

**Acceptance**:
1. tests、entrypoint smoke 和 audit 均通过。
2. 本次 change packet 记录默认 sync 和 opt-out 风险。

## 5. 风险与后续

| ID | 风险 / 后续 | 影响 | 处理 |
|---|---|---|---|
| F-1 | 默认 sync 会写多个 agent homes | 比旧行为副作用更大 | 缓解：提供 `--no-sync-skill` / `-NoSyncSkill` |
| F-2 | 当前发布版仍是旧行为 | 用户安装 latest release 前不会看到新默认 | 本次发布 `v0.1.5` 后消除 |

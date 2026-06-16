# ROADMAP - Windows UTF-8 output

> 本文件追踪本次需求做到哪一步。它承接 SPEC 的验收标准，记录调研、门禁、任务和验证结果。

## 0. 当前状态

**阶段 / Phase**: 验证与收尾完成
**当前 Step / Current Step**: Step 5 - 源码修复完成；等待 Windows release/live smoke
**ARCHITECTURE 省略理由 / Architecture Omission Reason**: 不省略。本需求改变 Windows installer、source lifecycle scripts 和 generated launchers 的环境配置契约。

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
| R-1 | Remote installer startup | `install_remote.ps1` logs through `Write-Host` before generated launchers run | `scripts/install_remote.ps1` | Installer script itself must set UTF-8 early |
| R-2 | Generated native PowerShell launcher | Generated `docdev.ps1` sets `DOCDEV_PROJECT_DIR` and `PYTHONPATH`, then starts Python | `scripts/install_remote.ps1` | Launcher template must include UTF-8 prelude |
| R-3 | Generated native CMD launcher | Generated `docdev.cmd` starts Python under existing code page | `scripts/install_remote.ps1` | CMD template needs `chcp 65001 >nul` plus Python UTF-8 env |
| R-4 | Source checkout lifecycle | `install.ps1`, `update_cli.ps1`, and generated source wrappers can also emit logs or run Python on Windows | `scripts/install.ps1`, `scripts/update_cli.ps1`, `scripts/install_cli.ps1` | Source maintenance path should use the same fix |
| R-5 | Existing tests | Windows installer contracts are already protected by static assertions | `tests/test_cli.py` | Add static coverage rather than relying on macOS to execute PowerShell |

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

**Goal**: 把 Windows 中文乱码反馈转成可验收的入口编码行为。

**Tasks**:
- [x] 补全 SPEC 一句话目标
- [x] 补全范围 / 非目标
- [x] 列出开放问题

**Acceptance**:
1. SPEC 的目标、范围和非目标能直接映射到实现点。

---

## Step 2 - 调研既有实现

**Goal**: 找到所有会在 Windows 输出或启动 Python 的入口。

**Tasks**:
- [x] 调研 `scripts/install_remote.ps1`
- [x] 调研 `scripts/install_cli.ps1`
- [x] 调研 `scripts/install.ps1`
- [x] 调研 `scripts/update_cli.ps1`
- [x] 调研 `tests/test_cli.py`

**Acceptance**:
1. 每个要修改的入口都有对应证据和测试策略。

---

## Step 3 - 形成并确认方案

**Goal**: 选择能覆盖 installer 早期输出和 launcher 后续 CLI 输出的最小方案。

**Tasks**:
- [x] 记录 D-001
- [x] 明确不修改系统 locale / profile / System PATH
- [x] 明确真实 Windows smoke 是 release 前推荐验证，不阻塞源码修复

**Acceptance**:
1. 实现方案不依赖用户手动编码命令。

---

## Step 4 - 实施代码与测试

**Goal**: 为 Windows PowerShell/CMD 入口添加 UTF-8 setup，并用静态测试保护。

**Tasks**:
- [x] 更新 PowerShell entry scripts
- [x] 更新 generated PowerShell launcher templates
- [x] 更新 generated CMD launcher templates
- [x] 添加 regression tests
- [x] 同步根项目 docs

**Acceptance**:
1. Windows entrypoint scripts and generated launchers contain UTF-8 setup before Python execution.
2. Unit tests pass.

---

## Step 5 - 验证与收尾

**Goal**: 验证源码修复并记录剩余 Windows live-smoke 风险。

**Tasks**:
- [x] 运行完整单元测试
- [x] 运行项目 audit
- [x] 更新 README / SKILL / 根项目 docs
- [x] 记录 release/live smoke 后续项

**Acceptance**:
1. `python3 -m unittest discover -s tests` passes.
2. `docdev audit /Users/chihoyo/Project/docs-driven-dev` reports no findings.
3. Windows live smoke gap is explicit.

## 4. 验证记录

| 验收项 | 验证方式 | 结果 | 备注 |
|---|---|---|---|
| SPEC-1 | Static tests for Windows UTF-8 prelude | 通过 | `test_windows_scripts_configure_utf8_output` added |
| SPEC-2 | `python3 -m unittest discover -s tests` | 通过 | 38 tests OK |
| SPEC-3 | `PYTHONPATH=src python3 -m docs_driven_dev.cli audit /Users/chihoyo/Project/docs-driven-dev` | 通过 | No findings |

## 5. 风险与后续

| ID | 风险 / 后续 | 影响 | 处理 |
|---|---|---|---|
| F-1 | macOS cannot prove Windows terminal rendering | 可能仍有 host-specific console behavior | release 前在 Windows PowerShell/CMD live smoke 验证 |
| F-2 | Fix remains source-only until released | 已安装 Windows latest 不会自动获得未发布源码 | 发布 v0.1.9 后通过 native update / latest install 获取；发布前可运行 source checkout install/update |

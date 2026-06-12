# ROADMAP - Native Installer Distribution

> 本文件追踪本次需求做到哪一步。它承接 SPEC 的验收标准，记录调研、门禁、任务和验证结果。

## 0. 当前状态

**阶段 / Phase**: 完成
**当前 Step / Current Step**: Step 10 in progress; v0.1.4 local package and smoke passed, publishing next
**ARCHITECTURE 省略理由 / Architecture Omission Reason**: 不省略。该需求改变分发结构、安装数据流、launcher 契约、update 生命周期和 Windows 入口，已创建 `ARCHITECTURE.md`。

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
| R-1 | 当前新机器安装 | 现有 README 和 SPEC 要求先 clone 源码，再运行 `./scripts/install.sh` / `.\scripts\install.ps1`；安装不改全局 PATH，wrapper 指向源码 checkout | `README.md`、`docs/SPEC.md` §3.4、`docs/ARCHITECTURE.md` §3.6 | 新方案必须把用户安装路径和源码维护路径拆开 |
| R-2 | 当前 CLI 命令面 | `docdev` 现有命令为 init/new-change/audit/status/new-decision/sync-skill/doctor/version，没有 update | `./.venv/bin/docdev --help`、`src/docs_driven_dev/cli.py` | 需要新增 `docdev update` 或明确等价 update 脚本 |
| R-3 | 版本来源 | `pyproject.toml` 和 `src/docs_driven_dev/__init__.py` 当前均为 `0.1.1` | `pyproject.toml`、`src/docs_driven_dev/__init__.py` | package 脚本应校验版本一致，避免 release manifest 漂移 |
| R-4 | 当前同步边界 | `sync-skill` 会生成 installed skill wrappers，且 source lifecycle 会跑 tests/check/sync/check | `scripts/update_cli.sh`、`scripts/sync_skill.sh`、`docs/ARCHITECTURE.md` §3.5-3.6 | native update 可选 sync，但不应让每次 update 都有隐式跨 agent 目录副作用 |
| R-5 | Claude Code native installer 参照 | 官方文档提供 `install.sh`、`install.ps1`、`install.cmd`；native install 支持 latest/stable/指定版本；有 `claude update`；release manifest 包含平台 checksum，manifest 可用 GPG 签名校验 | https://code.claude.com/docs/en/setup | docdev 可借鉴 release channel、manifest/checksum、用户目录安装、显式 update；首版可先做 checksum，签名后续增强 |
| R-6 | Claude Code 用户目录卸载路径 | 官方文档的 native uninstall 删除 `~/.local/bin/claude` 和 `~/.local/share/claude`，Windows 删除 `%USERPROFILE%\.local\bin\claude.exe` 和 `%USERPROFILE%\.local\share\claude` | https://code.claude.com/docs/en/setup | docdev 使用 `~/.local/bin/docdev` 和 `~/.local/share/docdev` 符合参照模型 |
| R-7 | 公开仓库优先与私有仓库 | 公开 release 可直接下载；私有 GitHub release 通常需要 `gh auth` 或 token，token 持久化会引入安全风险 | 用户约束、GitHub release 下载模型 | 首版默认公开仓库；私有仓库只作为明确高级路径 |

## 3. Step 状态总览

| Step | 内容 | 状态 |
|---|---|---|
| 0 | 建立需求工作包 | 完成 |
| 1 | 澄清需求与范围 | 完成 |
| 2 | 调研既有实现和外部参照 | 完成 |
| 3 | 形成并确认方案 | 完成 |
| 4 | 更新项目级文档合同 | 完成 |
| 5 | 实施 release package | 完成 |
| 6 | 实施 Unix remote install | 完成 |
| 7 | 实施 update 路径 | 完成 |
| 8 | 补 Windows PowerShell 框架 | 完成 |
| 9 | 文档、测试、smoke、audit 收尾 | 完成 |

---

## Step 0 - 建立需求工作包

**Goal**: 创建 SPEC / ROADMAP / DECISIONS / ARCHITECTURE，并把实现前门禁固定下来。

**Tasks**:
- [x] 初始化工作包文档
- [x] 记录 ARCHITECTURE 需要的理由
- [x] 在根 `docs/DECISIONS.md` 追加 D-021

**Acceptance**:
1. 工作包目录存在，且文档结构清晰。
2. 根决策日志记录为什么先选 GitHub Releases / native installer，而不是 npm 优先。

---

## Step 1 - 澄清需求与范围

**Goal**: 把 release 分发升级转成可验收的行为描述。

**Tasks**:
- [x] 补全 SPEC 一句话目标
- [x] 补全范围 / 非目标
- [x] 列出开放问题

**Acceptance**:
1. SPEC 能区分用户 remote install、开发者 source checkout lifecycle、private repo 高级路径。

---

## Step 2 - 调研既有实现和外部参照

**Goal**: 找出现有 source-checkout 安装链路、CLI 命令面、版本来源和 Claude Code native installer 可借鉴点。

**Tasks**:
- [x] 阅读 AGENTS.md、根 SPEC、ROADMAP、ARCHITECTURE、DECISIONS
- [x] 检查 README、scripts、CLI help、版本文件
- [x] 查询 Claude Code 官方安装文档并记录参照点

**Acceptance**:
1. 调研记录包含本仓库文件证据和外部官方参考链接。

---

## Step 3 - 形成并确认方案

**Goal**: 在不改生产代码的前提下，给出实现步骤、验收方式和待确认边界。

**Tasks**:
- [x] 写清 packet SPEC / ARCHITECTURE / DECISIONS
- [x] 写清实施计划和 smoke checks
- [x] 用户确认是否进入实现

**Acceptance**:
1. Pre-Implementation Gate 除用户确认外均已完成。
2. 用户能明确选择继续、调整范围或暂停。

---

## Step 4 - 更新项目级文档合同

**Goal**: 在代码前更新 source-of-truth，使 release 分发不与现有 SPEC 冲突。

**Tasks**:
- [x] 更新根 SPEC 决策表和 CLI 命令表，加入 release installer、launcher、update、checksum 合同
- [x] 更新根 ARCHITECTURE 数据流和 Process Model，区分 remote install 与 source checkout lifecycle
- [x] 更新根 ROADMAP 新 Step，标记当前进度与验收
- [x] 更新 README 与 `skill/SKILL.md`，把 remote install 作为用户路径，把 source checkout 作为开发者维护路径

**Acceptance**:
1. `docdev audit /Users/chihoyo/Project/docs-driven-dev` 无错误。
2. 文档不再把 cloned source checkout 描述为唯一新机器安装方式。

---

## Step 5 - 实施 release package

**Goal**: 生成可发布、可校验、可本地模拟安装的 release artifact。

**Tasks**:
- [x] 新增 `scripts/package_release.sh`
- [x] 校验 `pyproject.toml` 与 `src/docs_driven_dev/__init__.py` version 一致
- [x] 生成 tarball、`.sha256`、`manifest.json`、`install_remote.sh`、`install_remote.ps1`
- [x] 排除 `.git`、`.venv`、`docs/_generated/docdev/*`、构建输出和本地缓存
- [x] 增加单元测试或脚本 contract 测试

**Acceptance**:
1. 本地运行脚本产生 `docdev-<version>.tar.gz`、checksum、manifest 和 installer assets。
2. 解包后可通过 `PYTHONPATH=<release>/src python3 -m docs_driven_dev.cli --version` 运行。

---

## Step 6 - 实施 Unix remote install

**Goal**: 让用户无需 clone 源码即可安装 release 并运行 launcher。

**Tasks**:
- [x] 新增 `scripts/install_remote.sh`
- [x] 支持 latest/显式版本和可覆盖 release base URL
- [x] 下载 manifest/artifact，校验 SHA256 后解包到 install root
- [x] 维护 `releases/<version>` 和 `current` symlink
- [x] 生成 `~/.local/bin/docdev` launcher
- [x] 加入本地模拟 release install smoke test

**Acceptance**:
1. 临时 install root 下的 launcher 可运行 `docdev --version` 和 `docdev doctor`。
2. checksum 不匹配时安装失败且不切换 `current`。

---

## Step 7 - 实施 update 路径

**Goal**: 给 native install 用户一个清晰、可验证的更新入口。

**Tasks**:
- [x] 新增 `docdev update` 或等价 update 脚本，优先复用 installer helper
- [x] 支持 latest/显式版本、release base URL、checksum、版本切换
- [x] source checkout 模式下保留 `scripts/update_cli.sh` 维护路径，`docdev update` 聚焦 native release install
- [x] 增加 `--sync-skill` 或等价显式选项

**Acceptance**:
1. 本地模拟旧版到新版 update 后，`current` 指向新版。
2. `docdev update --sync-skill` 的副作用在 help 和 README 中明确。

---

## Step 8 - 补 Windows PowerShell 框架

**Goal**: 让 Windows native installer 路径有同等设计，不把 Windows 留成隐形空白。

**Tasks**:
- [x] 新增 `scripts/install_remote.ps1` 框架
- [x] 定义 Windows install root、bin dir、checksum、launcher 和 update 调用方式
- [x] 文档说明 PowerShell 执行策略、GitHub 私有仓库认证和真实 Windows 验证状态
- [x] 增加静态 contract 测试

**Acceptance**:
1. README/SKILL 有 Windows PowerShell remote install 说明。
2. 静态测试覆盖脚本关键 contract；未 live-verified 的部分明确标记。

---

## Step 9 - 文档、测试、smoke、audit 收尾

**Goal**: 确认实现与 docs-driven contract 一致，且没有 release 产物污染 source docs。

**Tasks**:
- [x] 跑单元测试
- [x] 跑本地 release install smoke checks
- [x] 跑 `docdev audit /Users/chihoyo/Project/docs-driven-dev`
- [x] 检查 `git status`，确认 release 临时产物未混入 source-of-truth docs
- [x] 在本 packet 记录验证结果和剩余风险

**Acceptance**:
1. SPEC §8 验收标准逐条有验证记录。
2. 所有未完成 Windows 或签名增强都有明确后续项。

## 4. 验证记录

| 验收项 | 验证方式 | 结果 | 备注 |
|---|---|---|---|
| Packet 创建 | `./.venv/bin/docdev new-change native-installer-distribution ... --with-architecture --date 2026-06-11` | 通过 | 已创建四个 packet 文档 |
| 实现前方案 | 人工审阅 SPEC / ROADMAP / ARCHITECTURE / DECISIONS | 通过 | 用户已确认继续实现 |
| Release package | `./scripts/package_release.sh --out /private/tmp/docdev-release-assets` | 通过 | 生成 artifact / checksum / manifest / installer assets |
| Release asset list | `ls -la /private/tmp/docdev-release-assets` | 通过 | 输出 `docdev-0.1.0.tar.gz`、`.sha256`、`manifest.json`、`install_remote.sh`、`install_remote.ps1` |
| Installer manifest metadata | `sed -n '1,80p' /private/tmp/docdev-release-assets/manifest.json` | 通过 | manifest includes `installers` entries for Unix and Windows |
| Artifact excludes | `tar -tzf ... | rg '(__pycache__|\\.pyc|(^|/)\\.git|(^|/)\\.venv|docs/_generated/docdev/.+)'` | 通过 | 命令返回 1，未匹配污染项 |
| Local install smoke | `./scripts/install_remote.sh --release-base-url file:///private/tmp/docdev-release-assets --install-root ... --bin-dir ...` | 通过 | checksum、current、launcher、doctor 均通过 |
| Launcher init/audit | `/private/tmp/docdev-native-smoke.H1QDDC/bin/docdev init ...` and `audit ...` | 通过 | target project audit No findings |
| Checksum negative smoke | 篡改 manifest sha256 后运行 `install_remote.sh` | 通过 | installer 返回 1 并报告 checksum mismatch |
| Native update smoke | `/private/tmp/docdev-native-smoke.H1QDDC/bin/docdev update --release-base-url file:///private/tmp/docdev-release-assets ...` | 通过 | 使用 `[docdev update]` 前缀并完成 doctor |
| Unit tests | `PYTHONPATH=src python3 -m unittest discover -s tests` | 通过 | 30 tests |
| 项目 audit | `./.venv/bin/docdev audit /Users/chihoyo/Project/docs-driven-dev` | 通过 | No findings |
| Git status | `git status --short` | 通过 | 无 `dist/` 或 release 临时产物；仅源码、文档、新脚本改动 |
| Source update sync | `./scripts/update_cli.sh --targets codex,cursor,agents,claude --force` | 通过 | install wrapper、30 tests、doctor、sync、post-check 全部通过 |
| Git commit | `git commit -m "Add native release installer workflow"` | 通过 | `48728ba` |
| Git push | `git push origin main` and `git push origin v0.1.0` | 通过 | main and tag pushed to GitHub |
| GitHub prerelease | `gh release create v0.1.0 ... --prerelease` | 通过 | https://github.com/hongzhiyin/docs-driven-dev/releases/tag/v0.1.0 |
| Release asset inspection | `gh release view v0.1.0 --json ...` | 通过 | 非 draft prerelease，五个 assets uploaded |
| Private direct URL smoke | `GITHUB_TOKEN="$(gh auth token)" ./scripts/install_remote.sh --release-base-url https://github.com/hongzhiyin/docs-driven-dev/releases/download/v0.1.0 ...` | 受限 | private repo 普通 download URL 返回 404；需公开仓库或使用 `gh release download` / API |
| GitHub asset smoke | `gh release download v0.1.0 --dir /private/tmp/docdev-github-smoke.EtDbot/assets --clobber` then local file install | 通过 | 下载回来的 GitHub assets 可安装，launcher `--version` / `init` / `audit` 均通过 |
| Version bump | Update `pyproject.toml`, `src/docs_driven_dev/__init__.py`, and CLI `VERSION` to `0.1.1` | 通过 | 修正 v0.1.0 artifact 未包含 private caveat docs 的自洽性 |
| Public install docs | README and SKILL install commands use `https://github.com/hongzhiyin/docs-driven-dev/releases/latest/download/install_remote.sh` | 通过 | 为公开仓库无 token smoke 做准备 |
| v0.1.1 tests | `PYTHONPATH=src python3 -m unittest discover -s tests` | 通过 | 30 tests |
| v0.1.1 audit | `./.venv/bin/docdev audit /Users/chihoyo/Project/docs-driven-dev` | 通过 | No findings |
| v0.1.1 package | `./scripts/package_release.sh --out /private/tmp/docdev-release-assets-0.1.1` | 通过 | 生成 `docdev-0.1.1.tar.gz`、checksum、manifest、installer assets |
| v0.1.1 local smoke | `./scripts/install_remote.sh --release-base-url file:///private/tmp/docdev-release-assets-0.1.1 ...` | 通过 | launcher `docdev --version` returns `0.1.1` |
| Public URL smoke attempt | `./scripts/install_remote.sh --version 0.1.1 --release-base-url https://github.com/hongzhiyin/docs-driven-dev/releases/download/v0.1.1 ...` | 网络受限 | GitHub public asset URL no longer returns 404, but current network hit LibreSSL SSL_ERROR_SYSCALL to release-assets/github.com |
| Installer network hardening | Add curl retry flags to `scripts/install_remote.sh` | 完成 | `--retry 3 --retry-delay 1 --retry-all-errors --connect-timeout 20` |
| Version bump for retry asset | Update `pyproject.toml`, `src/docs_driven_dev/__init__.py`, and CLI `VERSION` to `0.1.2` | 通过 | Avoids mutating already published v0.1.1 assets |
| v0.1.2 tests | `PYTHONPATH=src python3 -m unittest discover -s tests` | 通过 | 30 tests |
| v0.1.2 audit | `./.venv/bin/docdev audit /Users/chihoyo/Project/docs-driven-dev` | 通过 | No findings |
| v0.1.2 package | `./scripts/package_release.sh --out /private/tmp/docdev-release-assets-0.1.2` | 通过 | 生成 `docdev-0.1.2.tar.gz`、checksum、manifest、installer assets |
| v0.1.2 local smoke | `./scripts/install_remote.sh --release-base-url file:///private/tmp/docdev-release-assets-0.1.2 ...` | 通过 | launcher `docdev --version` returns `0.1.2` |
| Repo visibility | `gh repo edit hongzhiyin/docs-driven-dev --visibility public --accept-visibility-change-consequences` and `gh repo view --json nameWithOwner,visibility,url` | 通过 | Canonical repo is public at `https://github.com/hongzhiyin/docs-driven-dev` |
| v0.1.2 latest release | `gh release edit v0.1.2 --prerelease=false --latest` and `gh release view v0.1.2 --json tagName,isDraft,isPrerelease,url,assets` | 通过 | Release is not draft, not prerelease, and has five assets |
| Public latest install smoke | `curl -fsSL https://github.com/hongzhiyin/docs-driven-dev/releases/latest/download/install_remote.sh \| sh` with temp install env overrides | 通过 | latest manifest resolved to `docdev-0.1.2.tar.gz`; checksum, install, launcher, doctor passed |
| Public launcher init/audit | `/private/tmp/docdev-latest-smoke.VYO6KQ/bin/docdev --version`, `init`, and `audit` | 通过 | `docdev 0.1.2`; temp project audit No findings |
| v0.1.3 version bump | Update `pyproject.toml`, `src/docs_driven_dev/__init__.py`, and CLI `VERSION` to `0.1.3` | 通过 | Publishes README/skill Chinese guidance and tightened CLI resolution |
| v0.1.3 tests | `PYTHONPATH=src python3 -m unittest discover -s tests` | 通过 | 30 tests |
| v0.1.3 audit | `./.venv/bin/docdev audit /Users/chihoyo/Project/docs-driven-dev` | 通过 | No findings |
| v0.1.3 package | `./scripts/package_release.sh --out /private/tmp/docdev-release-assets-0.1.3` | 通过 | 生成 `docdev-0.1.3.tar.gz`、checksum、manifest、installer assets |
| v0.1.3 artifact excludes | `tar -tzf /private/tmp/docdev-release-assets-0.1.3/docdev-0.1.3.tar.gz \| rg '(__pycache__|\\.pyc|(^|/)\\.git|(^|/)\\.venv|docs/_generated/docdev/.+)'` | 通过 | 命令返回 1，未匹配污染项 |
| v0.1.3 local smoke | `./scripts/install_remote.sh --release-base-url file:///private/tmp/docdev-release-assets-0.1.3 ...` | 通过 | checksum、install、launcher、doctor 均通过 |
| v0.1.3 launcher init/audit | `/private/tmp/docdev-013-smoke.XqgRzf/bin/docdev --version`, `init`, and `audit` | 通过 | `docdev 0.1.3`; temp project audit No findings |
| v0.1.3 git tag | `git tag v0.1.3` and `git push origin v0.1.3` | 通过 | tag pushed after retrying transient GitHub SSL failures |
| v0.1.3 GitHub release | `gh release create v0.1.3 ... --latest` and `gh release view v0.1.3 --json tagName,isDraft,isPrerelease,url,assets` | 通过 | https://github.com/hongzhiyin/docs-driven-dev/releases/tag/v0.1.3; non-draft, non-prerelease, five assets |
| v0.1.3 public latest install smoke | `curl -fsSL https://github.com/hongzhiyin/docs-driven-dev/releases/latest/download/install_remote.sh \| sh` with temp install env overrides | 通过 | latest manifest resolved to `docdev-0.1.3.tar.gz`; checksum, install, launcher, doctor passed |
| v0.1.3 public launcher init/audit | `/private/tmp/docdev-latest-013-smoke.VC94IV/bin/docdev --version`, `init`, and `audit` | 通过 | `docdev 0.1.3`; temp project audit No findings |
| Real local native install | `curl -fsSL https://github.com/hongzhiyin/docs-driven-dev/releases/latest/download/install_remote.sh \| sh` | 通过 | Installed `0.1.3` under `/Users/chihoyo/.local/share/docdev/releases/0.1.3`; launcher at `/Users/chihoyo/.local/bin/docdev`; PATH warning expected |
| Real local launcher verification | `/Users/chihoyo/.local/bin/docdev --version`, `doctor`, `init`, and `audit` | 通过 | `docdev 0.1.3`; `current` symlink points to release `0.1.3`; temp project audit No findings |
| v0.1.4 version bump | Update `pyproject.toml`, `src/docs_driven_dev/__init__.py`, and CLI `VERSION` to `0.1.4` | 通过 | Publishes D-025: `sync-skill` no longer generates skill-local `bin/docdev*` wrappers |
| v0.1.4 tests | `PYTHONPATH=src python3 -m unittest discover -s tests` | 通过 | 31 tests |
| v0.1.4 audit | `./.venv/bin/docdev audit /Users/chihoyo/Project/docs-driven-dev` | 通过 | No findings |
| v0.1.4 package | `./scripts/package_release.sh --out /private/tmp/docdev-release-assets-0.1.4` | 通过 | 生成 `docdev-0.1.4.tar.gz`、checksum、manifest、installer assets |
| v0.1.4 artifact excludes | `tar -tzf /private/tmp/docdev-release-assets-0.1.4/docdev-0.1.4.tar.gz \| rg '(__pycache__|\\.pyc|(^|/)\\.git|(^|/)\\.venv|docs/_generated/docdev/.+)'` | 通过 | 命令返回 1，未匹配污染项 |
| v0.1.4 local smoke | `./scripts/install_remote.sh --release-base-url file:///private/tmp/docdev-release-assets-0.1.4 ...` | 通过 | checksum、install、launcher、doctor 均通过 |
| v0.1.4 launcher init/audit | `/private/tmp/docdev-014-smoke.9pbUDa/bin/docdev --version`, `init`, and `audit` | 通过 | `docdev 0.1.4`; temp project audit No findings |
| v0.1.4 temp sync-skill | `DOCDEV_*_HOME=/private/tmp/docdev-014-skillhomes.4X7lVC/... /private/tmp/docdev-014-smoke.9pbUDa/bin/docdev sync-skill --force` | 通过 | temp Codex/Cursor/agents targets copied; Claude linked; `find .../bin/docdev*` 无输出 |

## 5. 风险与后续

| ID | 风险 / 后续 | 影响 | 处理 |
|---|---|---|---|
| F-1 | Private GitHub Releases still need authenticated download handling | 不再阻塞 canonical public install；private forks/repos still cannot use unauthenticated `github.com/.../releases/download/...` URLs | Canonical repo is public and latest smoke passed; keep private repo caveat in README/SPEC/SKILL |
| F-2 | checksum-only 不等于签名验证 | 能发现传输/文件损坏，但不能提供完整发布者签名信任链 | 后续增强 manifest signature |
| F-3 | Windows 未必能在当前机器 live test | PowerShell installer 可能需要真实 Windows 反馈 | 已加静态 contract，后续 live verify |
| F-4 | `docdev update` 增加 CLI 命令面 | 可能让 source checkout update 和 native update 混淆 | help/README 明确区分 |
| F-5 | 私有 release 认证复杂 | token 安全和 GitHub API 差异会增加安装复杂度 | 公开仓库优先，私有路径显式高级说明 |

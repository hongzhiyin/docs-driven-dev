# SPEC - Native Installer Distribution

> 本文件描述本次需求应该满足什么。它不写实现细节、不追踪进度、不解释历史取舍。

## 0. 状态

| 字段 | 内容 |
|---|---|
| 状态 | 完成 |
| 需求来源 | 用户请求：将 docs-driven-dev 从源码 checkout + wrapper + sync-skill 升级为 GitHub Releases / native installer 风格分发 |
| 工作包目录 | `docs/changes/2026-06-11-native-installer-distribution/` |
| 最后更新 | 2026-06-11 |

## 1. 一句话目标

让用户在新机器上不预先 clone 源码、不污染系统 Python、不手动设置
`DOCDEV_PROJECT_DIR`，也能通过 release installer 安装、校验、启动和更新
`docdev` 与对应 skill。

## 2. 背景与问题

- 当前行为：根 SPEC §3.4 和 README 规定新机器先 clone 源码仓库，再运行
  `./scripts/install.sh` 或 `.\scripts\install.ps1`；安装生成 source checkout
  wrapper 和 skill-local wrapper，但不创建全局 `docdev`。
- 当前结构：`scripts/install.sh` 代理 `scripts/update_cli.sh`；synced skill 的
  `bin/docdev` wrapper 指回源码 checkout；`DOCDEV_PROJECT_DIR` 仍是 fallback。
- 问题：这更像开发者本机 bootstrap，而不是跨机器 release 分发。新机器仍需要
  Git 源码 checkout，安装行为和源码维护生命周期耦合，源码路径移动会让 installed
  wrapper 失效。
- 期望收益：公开仓库可提供 curl/PowerShell 风格 installer；installer 下载 release
  artifact、校验 checksum、安装到用户目录、生成 `~/.local/bin/docdev`
  launcher，并由 `docdev update` 或等价 update 脚本更新到后续 release。

## 3. 范围

### 3.1 本次要做

- 设计并实现 release package 生成流程：`scripts/package_release.sh` 生成
  `docdev-<version>.tar.gz`、checksum、manifest 和 installer script release assets。
- 设计并实现 remote installer：Unix `scripts/install_remote.sh` 或等价入口从
  GitHub Release 下载 manifest/artifact，校验后安装到用户目录。
- 维护 release 布局：`~/.local/share/docdev/releases/<version>` 保存解包版本，
  `~/.local/share/docdev/current` 指向当前版本。
- 生成 launcher：`~/.local/bin/docdev` 设置 `DOCDEV_PROJECT_DIR` 和 `PYTHONPATH`
  到 `current` release，再执行 `python3 -m docs_driven_dev.cli`。
- 提供 update 路径：优先设计为 `docdev update`，并保留脚本入口作为无 PATH 或
  调试场景的 fallback。
- 支持公开 GitHub 仓库优先；在文档中说明私有仓库需要 `gh auth` 或 token，安装
  复杂度和安全边界会增加。
- 保留 source checkout install/update/sync 流程作为开发者维护路径，直到 native
  installer 验证后再调整 README 主路径。
- 提供 Windows PowerShell install/update 设计，至少落地脚本框架和文档；完整
  Windows 行为可在后续真实机器验证中补强。
- 更新 README / SPEC / ARCHITECTURE / ROADMAP / DECISIONS / SKILL，使新分发
  合同和旧开发者路径边界一致。
- 增加 smoke checks：本地模拟 release artifact 安装、`docdev doctor`、
  `docdev init <tmp>`、`docdev audit <tmp>`。

### 3.2 本次不做

- 不优先发布 npm、PyPI、Homebrew、WinGet、apt/dnf/apk 包。
- 不要求用户全局 `pip install`，不修改系统 Python，不使用 `sudo pip`。
- 不要求用户手动设置 `DOCDEV_PROJECT_DIR` 才能运行已安装的 launcher。
- 不实现后台自动更新 daemon；更新由显式 `docdev update` 或 update 脚本触发。
- 不把 release 临时产物、打包输出或下载缓存写进四个 source-of-truth 文档。
- 不把私有仓库作为默认路径；私有仓库只作为有额外认证要求的兼容说明。
- 不在第一步强制实现 GPG 签名发布；manifest checksum 是首批验收要求，签名可作为
  后续增强，除非实现时成本很低且不影响小步交付。

## 4. 用户场景 / 使用流程

| 场景 ID | 触发条件 | 期望结果 |
|---|---|---|
| S1 | 用户在 macOS/Linux/WSL 上执行公开仓库 remote install 命令 | installer 检测平台和依赖，下载 latest manifest/artifact，校验 SHA256，安装 release，生成 `~/.local/bin/docdev` |
| S2 | 用户指定版本或渠道安装 | installer 下载对应版本或渠道指向的 release，失败时给出清晰错误 |
| S3 | 用户运行 `docdev update` | CLI 检查 latest release，下载并校验新版本，切换 `current`，运行 `docdev doctor`，可选提示或执行 `sync-skill` |
| S4 | 用户在 Windows PowerShell 上安装 | `install_remote.ps1` 设计与文档存在；脚本框架明确安装根、校验、launcher、update 的等价路径 |
| S5 | 用户使用私有 GitHub 仓库 release | 文档说明需要 `gh auth` 或 `GITHUB_TOKEN`，并说明 token 不应写入 launcher 或持久配置 |
| S6 | 开发者维护源码 checkout | 仍可使用 `./scripts/install.sh`、`./scripts/update_cli.sh`、`sync-skill` 做本地开发和 installed skill 同步 |

## 5. 功能需求

| ID | 需求 | 验收方式 | 状态 |
|---|---|---|---|
| R1 | `scripts/package_release.sh` 从当前源码生成 `docdev-<version>.tar.gz`、`.sha256`、`manifest.json`、`install_remote.sh` 和 `install_remote.ps1` | 本地运行脚本，检查输出文件、checksum、manifest 字段和排除规则 | 完成 |
| R2 | release artifact 包含运行 CLI 和 skill 所需文件，不包含 `.git`、`.venv`、`docs/_generated/docdev/*`、release 临时目录 | 解包检查文件列表 | 完成 |
| R3 | Unix remote installer 支持 latest 和显式版本，能从 GitHub Release 或本地模拟 release base URL 下载 | shell smoke test 使用本地 artifact 模拟安装 | 完成 |
| R4 | installer 在激活前校验 SHA256，不匹配时拒绝切换 `current` | 篡改 checksum 或 artifact 的负向测试 | 完成 |
| R5 | 安装目标为用户目录：默认 `~/.local/share/docdev/releases/<version>`、`~/.local/share/docdev/current`、`~/.local/bin/docdev` | smoke test 检查路径和 launcher 内容 | 完成 |
| R6 | launcher 设置 `DOCDEV_PROJECT_DIR` 和 `PYTHONPATH` 到 `current` release，不依赖源码 checkout | 通过 launcher 运行 `docdev --version` 和 `docdev doctor` | 完成 |
| R7 | `docdev update` 或等价 update 脚本能发现新 release、安装、校验、切换并运行 doctor | 本地模拟旧版到新版的切换测试 | 完成 |
| R8 | update 支持可选 `sync-skill`，但不把 skill sync 变成每次 update 的隐式不可见副作用 | CLI 帮助、README 和测试覆盖选项行为 | 完成 |
| R9 | README / SPEC / ARCHITECTURE / ROADMAP / DECISIONS / SKILL 区分用户 remote install 和开发者 source checkout lifecycle | 文档审阅和 `docdev audit` | 完成 |
| R10 | Windows PowerShell install/update 至少有脚本框架、路径布局、checksum、launcher 设计和文档 | 静态测试和文档检查；真实 Windows 执行可作为后续验证 | 完成 |
| R11 | 私有仓库路径要求显式认证，不把 token 写入持久 launcher | 文档检查和脚本参数设计检查 | 完成 |
| R12 | 生成报告仍只写入 `docs/_generated/docdev/`；release 输出使用独立构建目录 | `git status` 和打包脚本测试 | 完成 |

## 6. 约束与不变式

1. **#1**: Skill + CLI 分层不变；CLI 负责确定性安装、更新、打包、校验、sync，
   skill 负责 workflow、判断、边界和用户确认。
2. **#2**: Native installer 不得污染系统 Python，不得要求全局 `pip install`，
   不得要求用户手动设置 `DOCDEV_PROJECT_DIR` 才能使用已安装命令。
3. **#3**: Release artifact 激活前必须完成 checksum 校验；校验失败不得切换
   `current`。
4. **#4**: 旧 source checkout lifecycle 在迁移期间保持可用，不能让维护者失去
   `install.sh` / `update_cli.sh` / `sync-skill` 路径。
5. **#5**: Generated reports 仍只属于 `docs/_generated/docdev/`；release 临时产物
   不得混入 source-of-truth docs。
6. **#6**: 公开 GitHub release 是默认设计；私有仓库认证是显式高级路径。

## 7. 兼容性与默认行为

| 场景 | 默认行为 |
|---|---|
| 已有 source checkout 用户 | 继续使用 `./scripts/install.sh` 和 `./scripts/update_cli.sh`；README 将其标为开发者维护路径 |
| 已有 synced skill wrapper 指向源码 checkout | 不在方案阶段删除；实现时提供迁移说明和重新 sync 路径 |
| `~/.local/bin` 不在 PATH | installer 提示用户直接运行 launcher 路径或自行添加 PATH；不自动改 shell profile |
| 私有 GitHub 仓库 | 需要 `gh auth` 或 token；公开仓库命令不承诺直接适用 |
| Windows 原生 PowerShell | 先提供脚本框架和等价合同；真实机器验证结果决定是否标记完整支持 |
| 无网络或 GitHub 不可达 | installer 失败并保留旧 current；本地 source checkout lifecycle 仍可用 |

## 8. 验收标准

1. 本地模拟 release artifact 可以完成安装，并通过 `~/.local/bin/docdev` 或测试
   install root 下的 launcher 运行 `docdev --version`、`docdev doctor`。
2. 本地 smoke project 能通过 launcher 执行 `docdev init <tmp>` 和
   `docdev audit <tmp>`。
3. 篡改 artifact 或 checksum 时 installer/update 拒绝激活新版本。
4. README / SPEC / ARCHITECTURE / ROADMAP / DECISIONS / SKILL 明确 remote
   install、source checkout 开发路径、private repo 认证成本和 Windows 状态。
5. 单元测试、smoke checks、`docdev audit /Users/chihoyo/Project/docs-driven-dev`
   均通过或记录明确跳过理由。

## 9. 开放问题

| ID | 问题 | 当前判断 | 是否阻塞实现 |
|---|---|---|---|
| Q1 | GitHub owner/repo 和最终公开 release URL 是什么？ | 已定为 `hongzhiyin/docs-driven-dev`；公开安装入口使用 `https://github.com/hongzhiyin/docs-driven-dev/releases/latest/download/install_remote.sh` | 否 |
| Q2 | 首版是否需要 manifest GPG 签名？ | 首版先做 SHA256 manifest；D-021 和调研记录说明 Claude Code 有签名 manifest，可作为后续增强 | 否 |
| Q3 | `docdev update` 是否默认自动 `sync-skill`？ | 倾向不默认隐式 sync，提供 `--sync-skill` 或提示，避免更新命令有过多跨 agent 副作用 | 否 |
| Q4 | Windows 是否要在本轮达到 live-verified？ | 本轮至少文档和脚本框架；真实 Windows 机器验证可作为后续 Step | 否 |

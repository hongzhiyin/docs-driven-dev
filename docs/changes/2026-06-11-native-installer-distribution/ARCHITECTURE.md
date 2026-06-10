# ARCHITECTURE - Native Installer Distribution

> 本文件只在需求影响结构时创建。它描述现有结构是什么，以及本次方案会如何改变结构。

## 0. 状态

| 字段 | 内容 |
|---|---|
| 状态 | 方案待确认 |
| 创建原因 | 分发结构、安装数据流、launcher 契约、update 生命周期和 Windows 入口都会变化 |
| 最后更新 | 2026-06-11 |

## 1. 现有结构快照

| 模块 / 文件 | 当前职责 | 与本需求关系 |
|---|---|---|
| `src/docs_driven_dev/cli.py` | stdlib-only CLI，提供 init/new-change/audit/status/new-decision/sync-skill/doctor/version | 需要新增 update 命令或明确等价 update 入口 |
| `src/docs_driven_dev/__init__.py` | 定义 `__version__ = "0.1.2"` | release version 来源之一，需要与 `pyproject.toml` 一致 |
| `pyproject.toml` | Python 项目元数据和 console script | release package 需要读取或校验版本 |
| `scripts/install.sh` / `scripts/install.ps1` | cloned source checkout 的 fresh-machine install 入口 | 保留为开发者/source 安装路径，不再作为唯一新机器路径 |
| `scripts/update_cli.sh` / `scripts/update_cli.ps1` | source checkout update lifecycle：install wrapper、tests、doctor、sync、audit/status | 保留为源码维护生命周期；native update 需要新入口或 CLI 命令 |
| `scripts/install_cli.*` | 在 source `.venv` 下生成 wrapper | 仍服务源码 checkout；release install 会生成用户目录 launcher |
| `scripts/sync_skill.sh` | 包装 `docdev sync-skill` | native update 可选调用，但不应成为隐式副作用 |
| `skill/SKILL.md` | agent workflow 和 CLI resolution | 需要说明 remote install、source checkout lifecycle、private repo 认证和实现门禁 |
| `README.md` | 用户入口、安装说明、文档地图 | 需要把 remote install 放到用户安装路径，把 source checkout 放到开发者路径 |
| `docs/SPEC.md` / `docs/ARCHITECTURE.md` / `docs/ROADMAP.md` / `docs/DECISIONS.md` | 项目级 source of truth | 实现前需更新分发合同、数据流、Step 和 D-021 |

## 2. 当前调用链 / 数据流

```text
新机器用户
  -> git clone docs-driven-dev
  -> scripts/install.sh 或 scripts/install.ps1
      -> scripts/update_cli.*
          -> scripts/install_cli.*
          -> unit tests / doctor / sync-skill / audit / status
  -> synced skill bin/docdev wrapper
      -> DOCDEV_PROJECT_DIR=<source checkout>
      -> PYTHONPATH=<source checkout>/src
      -> python -m docs_driven_dev.cli
```

关键限制：
- install/update 和源码 checkout 强绑定。
- installed skill wrapper 指向源码路径；源码移动后需要重新 sync。
- 网络分发、release manifest、artifact checksum、用户目录版本切换尚不存在。

## 3. 目标结构

```text
Release maintainer
  -> scripts/package_release.sh
      -> dist/releases/docdev-<version>.tar.gz
      -> dist/releases/docdev-<version>.tar.gz.sha256
      -> dist/releases/manifest.json
      -> dist/releases/install_remote.sh
      -> dist/releases/install_remote.ps1
  -> GitHub Release assets

New machine user
  -> install_remote.sh / install_remote.ps1
      -> resolve version/channel and release base
      -> download manifest + artifact
      -> verify SHA256
      -> unpack into ~/.local/share/docdev/releases/<version>
      -> update ~/.local/share/docdev/current symlink or Windows equivalent
      -> write ~/.local/bin/docdev launcher
      -> run docdev doctor

Installed launcher
  -> DOCDEV_PROJECT_DIR=~/.local/share/docdev/current
  -> PYTHONPATH=~/.local/share/docdev/current/src
  -> python3 -m docs_driven_dev.cli <args>

docdev update
  -> read current release metadata
  -> resolve latest or requested version
  -> download + verify + unpack
  -> switch current
  -> run doctor
  -> optionally sync skill targets
```

## 4. 模块与接口契约

| 模块 / 文件 | 新增 / 修改 | 职责 | 不应依赖 |
|---|---|---|---|
| `scripts/package_release.sh` | 新增 | 生成 release tarball、SHA256、manifest，并拒绝版本不一致 | package index、全局 pip |
| `scripts/install_remote.sh` | 新增 | POSIX remote installer，支持 latest/版本、release base URL、checksum、用户目录安装、launcher | 源码 checkout、全局 `DOCDEV_PROJECT_DIR` |
| `scripts/install_remote.ps1` | 新增 | PowerShell remote installer 框架，使用 Windows 用户目录、`Get-FileHash`、PowerShell launcher | Unix shell |
| `scripts/update_remote.sh` 或 CLI update helper | 新增或修改 | 复用 remote install 逻辑完成版本切换 | 重复实现 checksum 和 manifest 解析 |
| `src/docs_driven_dev/cli.py` | 修改 | 增加 `update` 命令或明确 dispatch 到 update helper；source checkout 模式下给出正确提示 | 后台自动更新 daemon |
| `~/.local/bin/docdev` | 新增生成物 | 用户级 launcher，设置 release root 相关 env 后执行 CLI | 用户手动设置 `DOCDEV_PROJECT_DIR` |
| `~/.local/share/docdev/releases/<version>` | 新增生成物 | 已安装 release 内容 | 可变开发 checkout |
| `~/.local/share/docdev/current` | 新增生成物 | 当前版本指针，支持回滚和原子切换 | 未校验 artifact |
| `README.md` / `skill/SKILL.md` | 修改 | 说明 remote install、source developer lifecycle、private repo auth、Windows 状态 | 未实现行为的完成式承诺 |
| `docs/*` | 修改 | 将项目级合同从 source-checkout-only 扩展到 native installer distribution | 生成报告或 release 临时产物 |
| `tests/test_cli.py` 或新增测试 | 修改 / 新增 | 覆盖 manifest、package、installer smoke、launcher、update dispatch | 真实 GitHub 网络依赖 |

## 5. 数据、配置、资源变化

| 类型 | 路径 / 字段 | 变化 | 兼容性 |
|---|---|---|---|
| Release artifact | `dist/releases/docdev-<version>.tar.gz` | 新增本地构建输出 | 应加入 `.gitignore` 或保持未跟踪 |
| Manifest | `dist/releases/manifest.json` / GitHub Release asset | 新增版本、artifact、sha256、size、created_at、schema_version、minimum_python | 首版字段保持简单，后续可扩展签名 |
| Checksum | `docdev-<version>.tar.gz.sha256` | 新增 artifact SHA256 | installer 激活前必须校验 |
| Install root | `~/.local/share/docdev` | 新增用户目录安装根 | 可由 `DOCDEV_INSTALL_ROOT` 覆盖以支持测试 |
| Bin dir | `~/.local/bin` | 新增 launcher 位置 | 可由 `DOCDEV_BIN_DIR` 覆盖；不自动改 shell profile |
| Release base | GitHub Release URL / local test URL | 新增下载来源 | 可由 `DOCDEV_RELEASE_BASE_URL` 或 CLI 参数覆盖 |
| Auth | `GITHUB_TOKEN` / `gh auth` | 私有仓库高级路径 | 默认公开仓库不需要 |
| Windows install root | `%USERPROFILE%\.local\share\docdev` | PowerShell 对应默认 | 可由同名 env 覆盖 |

## 6. 测试与观测点

- Unit tests：版本一致性、manifest 字段、checksum 计算、installer script contract、CLI
  `update` help/dispatch。
- Smoke tests：用本地 `file://` 或临时 HTTP release base 安装到临时 HOME / install root，
  运行 launcher 的 `docdev --version`、`docdev doctor`、`docdev init <tmp>`、
  `docdev audit <tmp>`。
- Negative tests：checksum 不匹配不切换 `current`；下载失败保留旧版本；private repo
  未认证时错误信息指向 `gh auth` 或 token。
- Observability：installer/update 继续使用稳定前缀，例如 `[docdev install]`、
  `[docdev update]`，并保留编号步骤，方便远程失败诊断。

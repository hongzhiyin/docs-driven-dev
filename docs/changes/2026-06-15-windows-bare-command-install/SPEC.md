# SPEC - Windows 裸命令安装

> 本文件描述本次需求应该满足什么。它不写实现细节、不追踪进度、不解释历史取舍。

## 0. 状态

| 字段 | 内容 |
|---|---|
| 状态 | 已发布 v0.1.7；Windows live smoke 待真机验证 |
| 需求来源 | 用户请求：Windows 安装后希望能直接在终端运行 `docdev -v`，并参考 `lark-cli` 的 GitHub latest 安装 / 更新体验 |
| 工作包目录 | `docs/changes/2026-06-15-windows-bare-command-install/` |
| 最后更新 | 2026-06-15 |

## 1. 一句话目标

让 Windows 用户通过 GitHub latest release 安装或更新后，可以在普通 PowerShell / CMD 终端直接运行 `docdev -v`，不需要手写 profile function、alias，或记住 `docdev.ps1` 的完整路径。

## 2. 背景与问题

- 当前行为：`scripts/install_remote.ps1` 会安装 release、写入 `$HOME\.local\bin\docdev.ps1`，但不会写入 `docdev.cmd`，也不会修改用户 PATH。`docdev update` 当前在 `src/docs_driven_dev/release.py` 中固定调用 `scripts/install_remote.sh`，不是 Windows PowerShell installer。
- 问题：Windows 用户安装后不能稳定地输入 `docdev -v`；需要使用 `& "$HOME\.local\bin\docdev.ps1"`、手写 profile alias，或进入 WSL/Git Bash。这与用户期望的“安装完成后就是一个普通 CLI 命令”不一致。
- 参考：`lark-cli` 通过 npm `bin` 暴露 `lark-cli` 命令，postinstall 下载 GitHub Release 中的系统二进制；Windows release asset 是 `.zip` 内的 `.exe`，并用 checksum 校验。它的 `update` 命令会识别 npm 安装并重新安装，非 npm 安装则提示 GitHub Releases 下载路径。
- 期望收益：Windows 上的普通使用路径和 Unix 上的 `docdev` 体验收敛；用户仍可通过 GitHub Release latest 下载 / 更新，不引入 npm 作为默认分发约束。

## 3. 范围

### 3.1 本次要做

- Windows remote installer 写入用户可直接调用的命令入口，使 `docdev -v` 在 PATH 生效后可用。
- Windows remote installer 默认把 `DOCDEV_BIN_DIR` / `$HOME\.local\bin` 加入当前用户 PATH，并尽量刷新当前 PowerShell session 的 `$env:Path`。
- 提供显式 opt-out，允许用户安装 release 但不修改 PATH。
- `docdev update` 在 Windows 上使用 PowerShell remote installer，并保留 release manifest / checksum / current pointer / default skill sync 行为。
- README、SPEC、ARCHITECTURE、SKILL 和测试同步说明 Windows 的实际命令、PATH 行为和更新方式。
- 保持 GitHub Releases 为默认普通用户安装源，继续支持 `latest` 与指定版本。

### 3.2 本次不做

- 不把 `docs-driven-dev` 改成 npm-first 分发，也不要求用户安装 Node.js。
- 不在本次引入 PyInstaller / Nuitka / Go rewrite 等 `docdev.exe` 二进制打包；严格“无任何 launcher/shim”的 Windows `.exe` 是后续可选增强。
- 不自动删除用户 PATH 中的 bin 目录；卸载仍只删除 docdev-owned install root、launcher 和 marked skill target。
- 不改变 source checkout developer path：源码维护仍使用 `.\scripts\install.ps1` 与 `.\.venv\Scripts\docdev.ps1` / `.cmd`。

## 4. 用户场景 / 使用流程

| 场景 ID | 触发条件 | 期望结果 |
|---|---|---|
| S1 | Windows 用户从 GitHub latest 运行 PowerShell installer | 安装成功后新终端可运行 `docdev -v` |
| S2 | 用户用 `irm ...install_remote.ps1 \| iex` 在当前 PowerShell session 安装 | installer 尽量让当前 session 也能立即运行 `docdev -v` |
| S3 | 用户不希望 installer 修改 PATH | 用户可传入 opt-out 参数，之后仍可用完整 launcher 路径运行 |
| S4 | 已安装用户运行 `docdev update` | Windows 上走 PowerShell installer 更新到 latest，并继续刷新 skill target，除非传入 `--no-sync-skill` |

## 5. 功能需求

| ID | 需求 | 验收方式 | 状态 |
|---|---|---|---|
| R1 | Windows native install 必须生成 `docdev.cmd`，使 `docdev` 可被 PowerShell / CMD 通过 PATH 解析 | 脚本静态测试；Windows 真机 smoke：`docdev -v` | 静态完成，live 待真机验证 |
| R2 | Windows native install 默认添加 bin 目录到用户 PATH，且不重复追加同一路径 | PowerShell 脚本静态测试；手工检查 User PATH | 静态完成，live 待真机验证 |
| R3 | Windows native install 必须支持 `-NoModifyPath` 或等价 opt-out | 脚本静态测试 | 完成 |
| R4 | `docdev update` 在 Windows 上必须调用 `install_remote.ps1`，在 Unix 上继续调用 `install_remote.sh` | 单元测试 mock `os.name` / platform 分支 | 完成 |
| R5 | `docdev update --no-sync-skill` 在 Windows 上仍传递到 PowerShell installer | 单元测试检查命令参数 | 完成 |
| R6 | README / SKILL 必须给出 Windows GitHub latest install 命令、`docdev -v` 验证命令和 PATH 注意事项 | 文档测试 / `rg` 检查 | 完成 |

## 6. 约束与不变式

1. **#1**: GitHub Release install/update 仍必须在切换 active `current` release 前校验 artifact checksum。
2. **#2**: 普通用户安装路径仍不能要求 clone source checkout 或设置 `DOCDEV_PROJECT_DIR` / `PYTHONPATH`。
3. **#3**: Source checkout wrappers 仍是开发者维护路径，不能重新成为普通跨机器安装说明的主入口。
4. **#4**: PATH 修改必须只影响用户级 PATH 或当前 PowerShell process，不要求管理员权限，不写 system PATH。
5. **#5**: Installer 必须支持不修改 PATH 的 opt-out，以满足受管环境和安全策略。

## 7. 兼容性与默认行为

| 场景 | 默认行为 |
|---|---|
| 已有 `$HOME\.local\bin\docdev.ps1` | 保留或覆盖为当前 release launcher |
| 新增 `$HOME\.local\bin\docdev.cmd` | 作为 Windows 裸命令入口，由 installer 生成和更新 |
| `DOCDEV_BIN_DIR` 自定义 | PATH 操作针对自定义 bin dir；launcher 也写入该目录 |
| 当前 PATH 已包含 bin dir | 不重复追加 |
| `-NoModifyPath` | 不写用户 PATH；只写 launcher 并打印完整路径 |
| 旧终端 session 无法看到持久 PATH 更新 | installer 打印重新打开终端的提示；若脚本在当前 session 执行，尽量刷新 `$env:Path` |

## 8. 验收标准

1. Windows GitHub latest install 后，用户可以在新 PowerShell / CMD 中运行 `docdev -v` 并看到当前版本。
2. Windows `docdev update` 能从 GitHub latest 更新 release，并在更新后继续支持 `docdev -v`。
3. Unix remote install/update 行为保持不变。
4. Unit tests、project audit、package smoke 和 Windows 脚本静态检查通过。
5. SPEC #1-#5 不被破坏。

## 9. 开放问题

| ID | 问题 | 当前判断 | 是否阻塞实现 |
|---|---|---|---|
| Q1 | 用户说“不需要用其他 wrapper”是否排斥 installer-owned `docdev.cmd`，还是只排斥手写 alias/profile function？ | 已确认：可以不依赖 npm，其他参考 lark-cli；本轮接受 installer-owned `docdev.cmd`。严格无 shim 的 `docdev.exe` 后续再做。 | 否 |
| Q2 | 是否接受 installer 默认修改用户 PATH？ | 已确认按推荐方案继续：默认修改 User PATH，并提供 `-NoModifyPath` opt-out。 | 否 |
| Q3 | 是否需要本轮就做 Windows 真机 live verification？ | 当前 macOS 上只能做静态 / unit / package / public install checks；按用户发布请求，Windows live smoke 作为发布后真机验证项记录。 | 否 |

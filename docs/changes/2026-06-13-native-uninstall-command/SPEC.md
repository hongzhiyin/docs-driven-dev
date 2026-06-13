# SPEC - native uninstall command

> 本文件描述本次需求应该满足什么。它不写实现细节、不追踪进度、不解释历史取舍。

## 0. 状态

| 字段 | 内容 |
|---|---|
| 状态 | 发布中 |
| 需求来源 | 用户请求：新机器上需要可重复卸载 docdev 以验证安装过程 |
| 工作包目录 | `docs/changes/2026-06-13-native-uninstall-command/` |
| 最后更新 | 2026-06-13 |

## 1. 一句话目标

提供 `docdev uninstall`，让用户能安全移除 native install 和已同步的
docs-driven-dev skill target，用于新机器重复验证 install/update 流程。

## 2. 背景与问题

- 当前行为：项目已有 `scripts/install_remote.sh` / `docdev update`，但没有
  `docdev uninstall` 或 uninstall 脚本；README 也没有正式卸载入口。
- 问题：用户在新机器上做安装 smoke test 后，只能手动 `rm` 多个路径，容易误删父目录
  或漏删 synced skill 目录，影响下一轮安装验证。
- 期望收益：一个可 dry-run、可确认执行、只删除 docdev-owned 路径的命令。

## 3. 范围

### 3.1 本次要做

- 新增 `docdev uninstall` 命令。
- 支持 `--dry-run` 预览会删除或跳过的路径。
- 删除 native install root：默认 `~/.local/share/docdev`，可用
  `--install-root` 或 `DOCDEV_INSTALL_ROOT` 覆盖。
- 删除 launcher：默认 `~/.local/bin/docdev`，可用 `--bin-dir` 或
  `DOCDEV_BIN_DIR` 覆盖。
- 默认删除已同步的 docs-driven-dev skill targets，但只删除 symlink 或带
  `.docdev-skill-source` marker 的目录；未标记目录必须跳过。
- 支持 `--keep-skills`，只卸载 native CLI release，不删除 agent skill 目录。
- 更新 README、SPEC、ARCHITECTURE、ROADMAP、DECISIONS、SKILL 和测试。

### 3.2 本次不做

- 不删除源码 checkout，例如 `/Users/chihoyo/Project/docs-driven-dev`。
- 不删除 `~/.local/bin`、`~/.local/share`、`~/.codex`、`~/.cursor`、
  `~/.agents`、`~/.claude` 等父目录。
- 不编辑 shell startup files，也不移除用户手动添加的 PATH 配置。
- 不删除未标记的同名 skill 目录，除非未来另行设计更强的 ownership 证明。
- 不单独实现 shell-only uninstall script；本次以 `docdev uninstall` 为主入口。

## 4. 用户场景 / 使用流程

| 场景 ID | 触发条件 | 期望结果 |
|---|---|---|
| S1 | 用户运行 `docdev uninstall --dry-run` | 输出将删除 / 跳过的路径，不改变文件系统 |
| S2 | 用户运行 `docdev uninstall --yes` | 删除 docdev native install root、launcher 和 owned skill targets |
| S3 | 用户只想移除 CLI install，不想动 agent skill | 运行 `docdev uninstall --yes --keep-skills` |
| S4 | 用户用临时 install root/bin dir 做 smoke test | `--install-root`、`--bin-dir` 和 `DOCDEV_*_HOME` overrides 被同样使用 |

## 5. 功能需求

| ID | 需求 | 验收方式 | 状态 |
|---|---|---|---|
| R1 | `docdev uninstall` 不带 `--yes` 或 `--dry-run` 时不删除文件，并提示使用确认参数 | 单元测试 | 完成 |
| R2 | `docdev uninstall --dry-run` 列出 install root、launcher 和 skill targets，不删除 | 单元测试 | 完成 |
| R3 | `docdev uninstall --yes` 删除 install root 和 docdev launcher | 单元测试 / smoke | 完成 |
| R4 | 默认删除 symlink 或带 `.docdev-skill-source` marker 的 skill targets | 单元测试 | 完成 |
| R5 | 未标记的 skill target 被跳过，不被删除 | 单元测试 | 完成 |
| R6 | `--keep-skills` 跳过 skill target 删除 | 单元测试 | 完成 |
| R7 | README / SKILL 给出新机器验证时的卸载命令 | 文档检查 / tests | 完成 |
| R8 | GitHub Release `v0.1.6` 发布包含 `docdev uninstall` 的 native install/update/uninstall 路径 | release smoke | 待验证 |

## 6. 约束与不变式

1. **#1**: 卸载命令只能删除 docdev-owned 路径，不得删除父目录或用户项目目录。
2. **#2**: destructive uninstall 必须显式确认：`--yes`；`--dry-run` 不改变文件系统。
3. **#3**: skill target 删除必须依赖 symlink 或 `.docdev-skill-source` marker，
   未标记目录默认跳过。
4. **#4**: `DOCDEV_INSTALL_ROOT`、`DOCDEV_BIN_DIR` 和 `DOCDEV_<TARGET>_*`
   overrides 必须在 install/update/uninstall 间保持一致。

## 7. 兼容性与默认行为

| 场景 | 默认行为 |
|---|---|
| 已安装 v0.1.5 或更早 release | 只有升级到包含 uninstall 的 release 后才有 `docdev uninstall` |
| `~/.local/bin/docdev` 不在 PATH | 可运行 `~/.local/bin/docdev uninstall --yes` |
| synced skill target 无 marker | 跳过并提示，不删除 |
| Claude target 是 symlink | 删除 symlink 本身，不递归删除 symlink 目标 |
| 用户设置 custom install root/bin dir | 使用显式参数或 env overrides 定位同一套路径 |

## 8. 验收标准

1. 新机器上可以通过 `docdev uninstall --yes` 清理 docdev native install 后重新安装。
2. `docdev uninstall --dry-run` 可预览，不删除任何路径。
3. 单元测试、entrypoint smoke 和项目 audit 通过。
4. 未标记 skill 目录不会被误删。
5. `v0.1.6` release public latest smoke 可以安装并调用 `docdev uninstall`。

## 9. 开放问题

| ID | 问题 | 当前判断 | 是否阻塞实现 |
|---|---|---|---|
| Q1 | 是否需要单独 `scripts/uninstall_remote.sh`？ | 暂不需要；安装后已有 `docdev uninstall`，手动 fallback 可用 README 命令说明。 | 否 |

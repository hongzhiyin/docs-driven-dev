# SPEC - native update 默认刷新 skill

> 本文件描述本次需求应该满足什么。它不写实现细节、不追踪进度、不解释历史取舍。

## 0. 状态

| 字段 | 内容 |
|---|---|
| 状态 | 完成 |
| 需求来源 | 用户反馈：版本更新时 skill 也应该更新 |
| 工作包目录 | `docs/changes/2026-06-13-sync-skill-on-native-update/` |
| 最后更新 | 2026-06-13 |

## 1. 一句话目标

让 native release 安装或更新默认刷新已安装 agent skill 目录，使 CLI release 与 agent 读取的 workflow 内容保持一致。

## 2. 背景与问题

- 当前行为：`docdev update` 只有在用户显式传 `--sync-skill` 时才刷新 agent skill 目录；remote installer 也默认只安装 CLI release 并运行 doctor。
- 问题：当 release 中包含 `skill/SKILL.md`、templates 或 references 更新时，用户运行普通 `docdev update` 后 CLI 已更新，但 agent 仍可能读取旧 skill 内容。
- 期望收益：普通用户只需要运行 `docdev update`，就能同时获得新 CLI 和新 skill workflow；需要低副作用更新时再显式 opt out。

## 3. 范围

### 3.1 本次要做

- 将 `docdev update` 默认行为改为同步 skill targets。
- 将 remote installer 默认行为改为安装后同步 skill targets。
- 新增 `--no-sync-skill` opt-out，用于只更新 CLI release、不写 agent homes 的场景。
- 保留既有 `--sync-skill` 参数兼容性；它表示默认行为，不再是必需参数。
- 更新 README、SPEC、ARCHITECTURE、ROADMAP、DECISIONS、SKILL 和测试。
- Bump 并发布 `v0.1.5`，让 native update 默认 sync skill 的行为进入 GitHub Release。

### 3.2 本次不做

- 不改变 `docdev sync-skill` 的 target 列表和 replacement 语义。
- 不恢复 skill-local `bin/docdev*` wrappers。
- 不实现“只有版本号变化才 sync”的本地状态比较；本次按 install/update 成功后默认 sync。

## 4. 用户场景 / 使用流程

| 场景 ID | 触发条件 | 期望结果 |
|---|---|---|
| S1 | 用户运行 `docdev update` | CLI release 更新后自动运行 `sync-skill --targets codex,cursor,agents,claude --force` |
| S2 | 用户运行 remote installer 首次安装 | 安装 CLI release、doctor 通过后默认同步 skill targets |
| S3 | 用户只想更新 CLI release，不写 agent homes | 运行 `docdev update --no-sync-skill` 或 installer `--no-sync-skill` |
| S4 | 用户仍运行 `docdev update --sync-skill` | 命令继续可用，行为等同默认 sync |

## 5. 功能需求

| ID | 需求 | 验收方式 | 状态 |
|---|---|---|---|
| R1 | `docdev update` 默认向 installer 传递 sync 行为 | 单元测试检查 command args | 完成 |
| R2 | `docdev update --no-sync-skill` 可跳过 sync 行为 | 单元测试检查 command args | 完成 |
| R3 | remote Unix installer 默认 sync skill，并支持 `--no-sync-skill` | 静态测试检查默认和 opt-out；local release smoke 走 no-sync 路径 | 完成 |
| R4 | PowerShell installer 暴露同等 `-NoSyncSkill` opt-out | 静态测试检查脚本参数和 sync 条件 | 完成 |
| R5 | README / SPEC / ARCHITECTURE / SKILL 不再把 `--sync-skill` 描述为普通更新必需项 | 文档检查 / tests | 完成 |
| R6 | `v0.1.5` release 发布默认 sync skill 的 native update 行为 | package / smoke / GitHub release verification | 本地验证完成；发布待验证 |

## 6. 约束与不变式

1. **#1**: 默认 skill sync 仍必须使用 whole-directory replacement，不能恢复 skill-local wrappers。
2. **#2**: 用户必须有明确 opt-out，可以只更新 CLI release 而不写 agent homes。
3. **#3**: Native installer/update 仍必须在 checksum 验证和 release activation 成功后才 sync skill。
4. **#4**: 本次不改变 public GitHub Releases/native installer 分发方向，也不引入 package index 或全局 pip。

## 7. 兼容性与默认行为

| 场景 | 默认行为 |
|---|---|
| `docdev update` | 更新 release 并刷新 skill targets |
| `docdev update --sync-skill` | 兼容旧命令；行为同默认 |
| `docdev update --no-sync-skill` | 只更新 release，不刷新 skill targets |
| `scripts/install_remote.sh` | 安装 release 并刷新 skill targets |
| `scripts/install_remote.sh --no-sync-skill` | 安装 release，不刷新 skill targets |
| 旧 release 文档提到可选 sync | 被本工作包和 D-027 superseded；历史记录不重写 |

## 8. 验收标准

1. `docdev update` 默认包含 skill sync，`--no-sync-skill` 可跳过。
2. Local release install smoke 使用 `--no-sync-skill` 证明 opt-out 主路径；默认 sync 由 CLI dispatch 和 installer static checks 覆盖。
3. 单元测试、entrypoint smoke 和项目 audit 通过。
4. GitHub Release `v0.1.5` 发布，latest install/update smoke 通过。

## 9. 开放问题

| ID | 问题 | 当前判断 | 是否阻塞实现 |
|---|---|---|---|
| Q1 | 是否只在 manifest version 不同于 current 时才 sync？ | 不做。installer 当前每次 install/update 都会重建当前 release；默认 sync 与实际安装动作一致，避免状态比较复杂化。 | 否 |

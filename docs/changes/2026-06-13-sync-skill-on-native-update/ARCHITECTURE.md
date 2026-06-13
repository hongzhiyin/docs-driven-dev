# ARCHITECTURE - native update 默认刷新 skill

> 本文件只在需求影响结构时创建。它描述现有结构是什么，以及本次方案会如何改变结构。

## 0. 状态

| 字段 | 内容 |
|---|---|
| 状态 | 完成 |
| 创建原因 | native install/update 默认副作用和数据流变化 |
| 最后更新 | 2026-06-13 |

## 1. 现有结构快照

| 模块 / 文件 | 当前职责 | 与本需求关系 |
|---|---|---|
| `src/docs_driven_dev/commands.py` | 定义 `docdev update` 参数 | 新增 `--no-sync-skill`，保留 `--sync-skill` |
| `src/docs_driven_dev/release.py` | 将 `docdev update` dispatch 到 `scripts/install_remote.sh` | 默认向 installer 传 sync，opt-out 时跳过 |
| `scripts/install_remote.sh` | Unix remote install/update helper | 默认 sync skill，新增 `--no-sync-skill` |
| `scripts/install_remote.ps1` | Windows PowerShell remote install/update helper | 默认 sync skill，新增 `-NoSyncSkill` |
| `src/docs_driven_dev/sync.py` | 执行 skill target replacement sync | 行为不变，被默认调用 |
| `tests/test_cli.py` | 覆盖 update dispatch、installer smoke、docs wording | 更新默认 sync / opt-out 断言 |

## 2. 当前调用链 / 数据流

```text
docdev update
  -> release.cmd_update()
      -> scripts/install_remote.sh
          -> download manifest/artifact
          -> verify checksum
          -> switch current
          -> write launcher
          -> doctor
          -> sync only if --sync-skill was passed
```

## 3. 目标结构

```text
docdev update
  -> release.cmd_update()
      -> scripts/install_remote.sh --sync-skill
          -> download manifest/artifact
          -> verify checksum
          -> switch current
          -> write launcher
          -> sh "$LAUNCHER" doctor
          -> sh "$LAUNCHER" sync-skill --targets codex,cursor,agents,claude --force

docdev update --no-sync-skill
  -> release.cmd_update()
      -> scripts/install_remote.sh --no-sync-skill
          -> install/update release and doctor only
```

Direct installer use mirrors the same default:

```text
scripts/install_remote.sh
  -> install release
  -> sh "$LAUNCHER" doctor
  -> sync-skill by default
```

## 4. 模块与接口契约

| 模块 / 文件 | 新增 / 修改 | 职责 | 不应依赖 |
|---|---|---|---|
| `commands.py` | 修改 | `--sync-skill` compatibility flag and `--no-sync-skill` opt-out | installer internals |
| `release.py` | 修改 | Convert parsed CLI flags into installer args | direct skill copy logic |
| `install_remote.sh` | 修改 | Default sync and opt-out parsing | source checkout update lifecycle |
| `install_remote.ps1` | 修改 | Windows default sync and opt-out parsing | Unix shell assumptions |
| `sync.py` | 不变 | Execute target sync with whole-directory replacement | release manifest parsing |

## 5. 数据、配置、资源变化

| 类型 | 路径 / 字段 | 变化 | 兼容性 |
|---|---|---|---|
| CLI flag | `docdev update --sync-skill` | 保留，行为同默认 | 旧命令继续可用 |
| CLI flag | `docdev update --no-sync-skill` | 新增 opt-out | 新默认的逃生口 |
| Installer flag | `install_remote.sh --no-sync-skill` | 新增 opt-out | local smoke 可避免写真实 agent homes |
| PowerShell flag | `install_remote.ps1 -NoSyncSkill` | 新增 opt-out | Windows 同等控制 |
| Sync targets | `codex,cursor,agents,claude` | 不变 | 仍支持 `DOCDEV_<TARGET>_*` env overrides |

## 6. 测试与观测点

- `test_update_dispatches_to_native_installer`：默认 update 传 `--sync-skill`。
- `test_update_can_skip_skill_sync`：`--no-sync-skill` 不传 sync。
- local `install_remote.sh` smoke：默认 sync，但通过 `DOCDEV_*_HOME` 把写入限制在临时 homes。
- generated Unix launcher smoke：source-local launcher 可直接执行；remote installer 内部自检使用 `sh "$LAUNCHER"`，避免临时目录新脚本直接 exec 被系统拦截。
- static installer checks：保护 `SYNC_SKILL=1` 和 `-NoSyncSkill` 合同。
- `docdev audit`：当前 docs 与 change packet 无 findings。

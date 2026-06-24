# ARCHITECTURE - docs maintenance health

> 本文件只在需求影响结构时创建。它描述现有结构是什么，以及本次方案会如何改变结构。

## 0. 状态

| 字段 | 内容 |
|---|---|
| 状态 | 已完成 |
| 创建原因 | 新增 CLI 命令、报告数据模型和 generated output |
| 最后更新 | 2026-06-24 |

## 1. 现有结构快照

| 模块 / 文件 | 当前职责 | 与本需求关系 |
|---|---|---|
| `src/docs_driven_dev/commands.py` | CLI 参数解析和 subcommand dispatch | 新增 `docs-health` parser |
| `src/docs_driven_dev/audit.py` | 结构审计、status、decision skeleton | 可复用 docs_dir / generated_dir 约定，不混入 health logic |
| `src/docs_driven_dev/models.py` | 共享轻量数据对象 | 可新增 health report dataclass，或在新模块内部保持 dict |
| `docs/_generated/docdev/` | 生成报告目录 | 新增 `docs-health.json` |

## 2. 当前调用链 / 数据流

```text
docdev audit <project>
  -> commands.main()
  -> audit.cmd_audit()
  -> structural findings / optional audit.json
```

## 3. 目标结构

```text
docdev docs-health <project>
  -> commands.main()
  -> docs_health.cmd_docs_health()
  -> collect README / four docs / change packet metrics
  -> print human summary or JSON
  -> optionally write docs/_generated/docdev/docs-health.json
```

## 4. 模块与接口契约

| 模块 / 文件 | 新增 / 修改 | 职责 | 不应依赖 |
|---|---|---|---|
| `src/docs_driven_dev/docs_health.py` | 新增 | 收集 docs health metrics、生成 review signals、输出 JSON/human summary | release install/update |
| `src/docs_driven_dev/commands.py` | 修改 | 注册 `docs-health` command | health heuristics |
| `skill/SKILL.md` | 修改 | 提示定期精简前运行 `docs-health` | report implementation details |
| `README.md` | 修改 | 保留用户入口，指向维护报告能力 | release runbook 细节 |

## 5. 数据、配置、资源变化

| 类型 | 路径 / 字段 | 变化 | 兼容性 |
|---|---|---|---|
| 生成报告 | `<docs_dir>/_generated/docdev/docs-health.json` | 新增 | 不影响 source-of-truth docs |
| CLI | `docdev docs-health` | 新增只读命令 | 不改变现有命令 |

## 6. 测试与观测点

- 单元测试覆盖 human output、JSON output、write-report path。
- `docdev audit` 仍无 findings。
- `docs-health` 对当前仓库能指出 README/ROADMAP/DECISIONS/changes 的维护信号。

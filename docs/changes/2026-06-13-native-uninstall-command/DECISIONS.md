# DECISIONS - native uninstall command

> 本文件记录这次需求中为什么这么选。只写真实取舍，不为机械改动补仪式性决策。

## 维护规则

1. `D-XXX` 在本工作包内单调递增，不复用。
2. 每条记录 2-3 个真实选项；不要编造凑数选项。
3. 写清选择、理由、风险和对应文件。
4. 决策被推翻时，新增一条 D-XXX 引用旧决策，旧决策保留原文。

---

## D-001 - Step 3 - Built-in CLI uninstall with explicit confirmation

**日期 / Date**: 2026-06-13

**上下文 / Context**:
用户需要在新机器上卸载后反复验证 native install。当前只能手动删除多处路径，容易
漏删 synced skill target 或误删父目录。

**选项 / Options**:
- A. 只在 README 写手动 `rm` 命令 - 最简单，但不能保护未标记 skill 目录，也不方便自动化 smoke。
- B. 新增独立 shell uninstall script - 对 curl 安装风格熟悉，但需要维护 Unix/Windows 两套脚本。
- C. 新增 `docdev uninstall` CLI 命令 - 复用 stdlib 和现有 path/marker 逻辑，安装后即可调用。

**选择 / Chosen**: C

**理由 / Rationale**:
- CLI 已经是 deterministic install/update/sync 层，卸载也属于确定性文件操作。
- `sync.py` 已有 target path resolution 和 `.docdev-skill-source` marker 语义，CLI 可以复用。
- `--dry-run` 和 `--yes` 比 README-only `rm` 更适合 agent 和新机器 smoke test。

**风险 / Risks**:
- 命令会删除运行中的 native install root；Unix/macOS 可行，Windows 仍需要后续 live verification。
- 未标记同名 skill 目录会被跳过，可能留下用户手动安装的副本；这是安全取舍。

**对应代码 / 文档**:
- SPEC §5-§8
- ROADMAP Step 4
- ARCHITECTURE §3-§6
- `src/docs_driven_dev/release.py`
- `src/docs_driven_dev/commands.py`

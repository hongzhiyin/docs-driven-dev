# DECISIONS - native update 默认刷新 skill

> 本文件记录这次需求中为什么这么选。只写真实取舍，不为机械改动补仪式性决策。

## 维护规则

1. `D-XXX` 在本工作包内单调递增，不复用。
2. 每条记录 2-3 个真实选项；不要编造凑数选项。
3. 写清选择、理由、风险和对应文件。
4. 决策被推翻时，新增一条 D-XXX 引用旧决策，旧决策保留原文。

---

## D-001 - Step 3 - 默认同步 skill，提供 no-sync opt-out

**日期 / Date**: 2026-06-13

**上下文 / Context**:
旧设计为了避免 `docdev update` 隐式写入多个 agent homes，把 skill sync 设计成 `--sync-skill` 显式选项。但实际使用里，release 更新通常同时包含 CLI、skill、templates 和 docs workflow 变化；如果只更新 CLI，agent 仍可能读取旧 skill 内容。

**选项 / Options**:
- A. 保持 `--sync-skill` 显式 opt-in - 副作用最小，但普通更新容易留下 CLI/skill 版本不一致。
- B. 默认同步 skill，新增 `--no-sync-skill` opt-out - 普通路径一致性最好，但默认副作用更大。
- C. 做版本比较，只有 manifest version 变化时同步 - 更精细，但需要额外本地状态和边界处理，超过当前需求。

**选择 / Chosen**: B

**理由 / Rationale**:
- 满足 SPEC **#1**：release 更新后 agent 读取到的 workflow 与 CLI release 一致。
- 保留 `--no-sync-skill`，让 CI、受限机器或只想更新 launcher 的用户可以避免写 agent homes。
- 不改变 `sync.py` 的 replacement 合同，仍然不会生成 skill-local wrappers。

**风险 / Risks**:
- 默认 update 会写 `~/.codex`、`~/.cursor`、`~/.agents`、`~/.claude` target。缓解：文档和 help 明确 `--no-sync-skill`。
- 已发布旧版本仍需下一次 release 才获得新默认。缓解：在 ROADMAP 风险中记录后续 release。

**对应代码 / 文档**:
- SPEC §6
- ROADMAP Step 4
- ARCHITECTURE §3-§5
- `src/docs_driven_dev/commands.py`
- `src/docs_driven_dev/release.py`
- `scripts/install_remote.sh`
- `scripts/install_remote.ps1`

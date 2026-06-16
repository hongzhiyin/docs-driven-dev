# DECISIONS - Windows UTF-8 output

> 本文件记录这次需求中为什么这么选。只写真实取舍，不为机械改动补仪式性决策。

## 维护规则

1. `D-XXX` 在本工作包内单调递增，不复用。
2. 每条记录 2-3 个真实选项；不要编造凑数选项。
3. 写清选择、理由、风险和对应文件。
4. 决策被推翻时，新增一条 D-XXX 引用旧决策，旧决策保留原文。

---

## D-001 - Step 3 - Configure UTF-8 at Windows entrypoints

**日期 / Date**: 2026-06-16

**上下文 / Context**:
The reported mojibake appears at the beginning of Windows PowerShell usage. A
Python-only fix would not cover installer logs emitted before Python starts,
and user instructions would keep the defect outside the project.

**选项 / Options**:
- A. Document that users should run `chcp 65001` or set PowerShell encoding
  manually - low implementation cost, but repeats the burden on every Windows
  user.
- B. Set UTF-8 only inside the Python CLI - improves some command output, but
  does not fix installer and launcher startup logs.
- C. Configure UTF-8 in Windows PowerShell entry scripts and generated
  launchers - covers installer startup, source maintenance scripts, and normal
  `docdev` command execution.

**选择 / Chosen**: C

**理由 / Rationale**:
- It fixes the earliest output point, before `Write-Host` logs or Python CLI
  output can be garbled.
- It keeps the change local to docdev-owned processes and launchers.
- It does not require admin rights, profile edits, npm shims, or a new binary
  packaging model.

**风险 / Risks**:
- Some PowerShell hosts may reject console encoding mutation. Mitigation: use
  best-effort console setup and still set Python UTF-8 environment variables.
- Static tests cannot prove every Windows terminal host renders Chinese
  correctly. Mitigation: keep real Windows smoke as release verification.

**对应代码 / 文档**:
- SPEC §5
- ROADMAP Step 4
- `scripts/install_remote.ps1`
- `scripts/install_cli.ps1`
- `scripts/install.ps1`
- `scripts/update_cli.ps1`
- `tests/test_cli.py`

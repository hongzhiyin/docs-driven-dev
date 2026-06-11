# DECISIONS - 清理 native install 迁移残留

> 本文件记录这次需求中为什么这么选。只写真实取舍，不为机械改动补仪式性决策。

## 维护规则

1. `D-XXX` 在本工作包内单调递增，不复用。
2. 每条记录 2-3 个真实选项；不要编造凑数选项。
3. 写清选择、理由、风险和对应文件。
4. 决策被推翻时，新增一条 D-XXX 引用旧决策，旧决策保留原文。

---

## D-001 - Step 1 - 保留源码维护入口但删除旧 scratch

**日期 / Date**: 2026-06-12

**上下文 / Context**:
v0.1.3 native install 已经让普通用户通过 `docdev` 或
`~/.local/bin/docdev` 调用 CLI。仓库里仍有 `temp/` 旧参考材料、运行缓存，以及一些容易让人误解源码 wrapper 是普通跨机器入口的当前文档表述。

**选项 / Options**:
- A. 删除所有 wrapper / source checkout 相关脚本和 CLI 逻辑 - 表面最干净，但会破坏开发者维护、测试和 sync 生命周期。
- B. 只删除运行缓存，保留所有旧文档和 `temp/` - 风险最低，但 native install 后的当前仓库仍显得混乱。
- C. 删除 `temp/` 和运行缓存，更新当前文档/模板，把源码 wrapper 明确限定为 developer maintenance compatibility path - 清理真实残留，同时保留受支持维护入口。

**选择 / Chosen**: C

**理由 / Rationale**:
- D-021 / D-022 已把普通跨机器路径切到 GitHub Release native installer 和 native launcher。
- D-012 已把 `temp/` 旧 skill 的有效流程迁移到 `docs/changes/` change packet 机制，继续跟踪 `temp/` 会制造第二套参考源。
- `scripts/install_cli.*`、`scripts/update_cli.*`、`sync-skill` 和 generated compatibility wrappers 仍服务源码 checkout 维护与测试，不能当作临时代码删除。

**风险 / Risks**:
- 搜索历史 docs 仍会看到 wrapper/source checkout 术语。缓解：不改写历史 D-XXX，但让当前 SPEC / ARCHITECTURE / README / skill 明确 native-first 现状。
- 删除 `temp/` 后如果需要旧对比材料，只能从 git history 查看。缓解：当前 change packet 记录删除理由，D-012 已保留迁移背景。

**对应代码 / 文档**:
- SPEC §3
- ROADMAP Step 2
- `docs/ARCHITECTURE.md`
- `README.md`
- `skill/templates/SPEC.md`
- `temp/`

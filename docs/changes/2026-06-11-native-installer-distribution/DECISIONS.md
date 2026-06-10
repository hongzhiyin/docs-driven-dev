# DECISIONS - Native Installer Distribution

> 本文件记录这次需求中为什么这么选。只写真实取舍，不为机械改动补仪式性决策。

## 维护规则

1. `D-XXX` 在本工作包内单调递增，不复用。
2. 每条记录 2-3 个真实选项；不要编造凑数选项。
3. 写清选择、理由、风险和对应文件。
4. 决策被推翻时，新增一条 D-XXX 引用旧决策，旧决策保留原文。

---

## D-001 - Step 3 - Use versioned user-directory releases with a current pointer

**日期 / Date**: 2026-06-11

**上下文 / Context**:
Native installer 需要让用户不用 clone 源码就能运行 `docdev`，同时不能污染系统 Python
或依赖全局 pip。安装还需要支持安全切换新版本和失败时保留旧版本。

**选项 / Options**:
- A. 直接覆盖 `~/.local/share/docdev` 中的当前文件 - 路径简单，但更新失败时容易留下半写入状态，回滚困难。
- B. 每个版本安装到 `releases/<version>`，再维护 `current` 指针 - 多一个指针层，但可在校验通过后切换，旧版本可保留。
- C. 继续只使用源码 checkout wrapper - 最少变更，但不满足跨机器 release installer 目标。

**选择 / Chosen**: B

**理由 / Rationale**:
- `current` 指针让 launcher 保持稳定，同时允许版本目录不可变。
- 校验和 doctor 通过后再切换 `current`，可以降低失败更新破坏可用安装的风险。
- 该布局与用户目录安装目标一致，不需要系统 Python 或全局 pip。

**风险 / Risks**:
- Windows 上 symlink 或 junction 行为需要适配。缓解：PowerShell 框架可以先用目录指针文件或受控复制策略，真实 Windows 验证后定稿。
- 多版本会占用空间。缓解：后续可加入保留最近 N 个版本的 cleanup 选项。

**对应代码 / 文档**:
- SPEC §5 R5-R7
- ARCHITECTURE §3, §5
- ROADMAP Step 6, Step 7

---

## D-002 - Step 3 - Prefer `docdev update` as the native update entrypoint

**日期 / Date**: 2026-06-11

**上下文 / Context**:
用户安装 release 之后不一定保留源码 checkout，也不一定知道 update 脚本在哪里。
同时，现有 `scripts/update_cli.*` 是源码维护生命周期，继续承担 tests/check/sync/check。

**选项 / Options**:
- A. 只提供 `scripts/update_remote.*` - 脚本边界清楚，但 native install 用户未必知道脚本路径。
- B. 新增 `docdev update`，并让脚本作为 fallback 或复用 helper - 用户入口直观，但需要在 CLI 中清楚区分 native update 与 source checkout update。
- C. 复用 `scripts/update_cli.*` 作为所有 update - 少一个入口，但会把源码维护测试/sync 生命周期和用户 release 更新混在一起。

**选择 / Chosen**: B

**理由 / Rationale**:
- Native installer 的可发现更新入口应来自已安装命令本身。
- CLI 做下载、校验、切换、doctor 属于确定性流程，符合 skill/CLI 分层。
- source checkout 用户仍保留 `scripts/update_cli.*`，避免把开发者测试/sync 流程塞进普通用户 update。

**风险 / Risks**:
- `update` 命令可能与现有 source maintenance 语义混淆。缓解：help、README、SPEC 和 SKILL 明确说明 source checkout 模式应使用 `scripts/update_cli.*`。
- `docdev update --sync-skill` 可能有跨 agent 目录副作用。缓解：sync 作为显式选项，不做不可见默认。

**对应代码 / 文档**:
- SPEC §5 R7-R8
- ARCHITECTURE §4
- ROADMAP Step 7

---

## D-003 - Step 3 - Make checksum manifest required and signed manifest deferred

**日期 / Date**: 2026-06-11

**上下文 / Context**:
Claude Code native installer 参照包含 manifest checksum 和 GPG signed manifest。docdev
首版目标是先建立 GitHub Releases 分发闭环，同时保持小步验证。

**选项 / Options**:
- A. 首版只下载 artifact，不做校验 - 实现最快，但不符合用户明确要求，也不适合 release installer。
- B. 首版要求 manifest + SHA256 checksum，签名作为后续增强 - 满足完整性校验，交付粒度适中。
- C. 首版同时实现 GPG signed manifest - 安全边界更强，但需要密钥发布、验证文档和跨平台测试，容易扩大本轮范围。

**选择 / Chosen**: B

**理由 / Rationale**:
- SHA256 manifest 是用户明确要求的最低安全合同。
- GitHub Release + checksum 可以先完成本地模拟 release 安装和 update smoke test。
- manifest schema 可以预留 `signature` 或 `signing` 字段，不阻碍后续 D-XXX 增强。

**风险 / Risks**:
- checksum-only 不能证明发布者身份。缓解：README 和 SPEC 不把它描述成签名信任链；后续可加入 manifest signature。
- 如果 GitHub Release asset 被替换，checksum 必须随 manifest 一起更新。缓解：package 脚本一次生成 artifact、checksum、manifest。

**对应代码 / 文档**:
- SPEC §3.2, §5 R1-R4
- ARCHITECTURE §5
- ROADMAP Step 5, Step 6

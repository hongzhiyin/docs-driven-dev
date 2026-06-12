---
name: docs-driven-dev
description: >-
  用 docs-driven development 维护项目：以 docs/SPEC.md,
  docs/ARCHITECTURE.md, docs/ROADMAP.md, docs/DECISIONS.md
  作为 source-of-truth documents，并在 docs/changes/ 下为具体需求创建
  change packet。适用于用户要求 doc-driven、documentation-first、spec-driven、
  research-before-code、四件套文档、需求工作包、决策日志、不变式、D-XXX、
  Step/Phase planning，或项目已经存在上述 docs 结构的场景。
metadata:
  requires:
    bins: ["docdev"]
  cliHelp: "docdev --help"
---

# Docs-Driven Development

这个 skill 让项目意图、当前结构、进度和取舍分别落在四个正交文档中。agent 用这些
文档做判断；`docdev` CLI 只负责可重复的确定性动作：文件生成、编号、audit、sync、
打包、安装和更新。

## Invocation Contract（调用合同）

当用户明确点名这个 skill，或明确要求 docs-driven / 文档先行 / 四件套文档时，使用
本 skill 意味着：先遵循下面某个 workflow，并在改代码前创建或更新必要的 docs
artifacts。只读一遍 `SKILL.md` 然后直接写代码是不够的。

不要把明确的 `docs-driven-dev` 调用静默降级成临时调研或直接 coding，即使只是小修复。
如果用户明确说“不要改文件”“不要改 docs”“只讨论不落文件”，这和本 skill 的完整
workflow 冲突；先说明 docs-driven workflow 被阻塞，再询问是否要脱离本 skill 继续。
如果没有这种明确限制，默认应按本 skill 创建或更新文档。

## File Contract（文件合同）

项目级 source-of-truth 布局：

```text
docs/
  SPEC.md          # what should be true: rules, invariants, contracts
  ARCHITECTURE.md  # what exists: layers, modules, data flow, config
  ROADMAP.md       # where we are: Phase/Step status and acceptance
  DECISIONS.md     # why: monotonic D-XXX decision log
  _generated/docdev/
    audit.json     # optional machine-generated reports
```

需求级 change packet 放在当前 docs dir 下：

```text
docs/changes/YYYY-MM-DD-slug/
  SPEC.md
  ROADMAP.md
  DECISIONS.md
  ARCHITECTURE.md  # optional; ROADMAP records the omission reason
```

默认且推荐只使用 `docs/`。一般项目不需要自定义文档路径，也不需要关心
`.docdev.toml` 或 `docs_dir`。只有在维护已有项目且它已经显式配置
`.docdev.toml` 时，才遵从其中的 `docs_dir`。生成报告只能放在
`docs/_generated/docdev/`，或该既有配置对应的 `_generated/docdev/`；不要把 audit 输出
混进四个 source-of-truth docs。

## CLI Resolution（CLI 解析）

优先使用确定性的 helper command。在任意目标项目中，按这个顺序解析 CLI：

1. 如果 `docdev` 在 `PATH` 上，运行 `docdev <command>`。
2. 在 macOS、Linux 或 WSL 上，如果 native release launcher 存在但 `docdev` 不在
   `PATH` 上，运行 `~/.local/bin/docdev <command>`。
3. 如果两者都不存在，说明 `docdev` 安装不可用；要求用户先运行 native installer 或修复
   安装。Do not guess local paths or wrappers for cross-machine use.

始终显式选择目标项目。只有当用户的当前工作目录显然就是目标项目时，才把当前目录当目标；
否则传入用户说出的项目路径。

```bash
docdev init /path/to/project
docdev new-change "feature-slug" /path/to/project
docdev audit /path/to/project --write-report
docdev status /path/to/project
docdev new-decision "Step N - trade-off title" /path/to/project
docdev sync-skill --targets codex,cursor,agents,claude --force
docdev doctor
```

native release install 后，agent 应优先使用 `docdev` 或 Unix-like 系统上的
`~/.local/bin/docdev`。这个 launcher 指向 `~/.local/share/docdev/current`，因此 agent
执行确定性 CLI 操作时不需要访问本项目源码目录。

安装器不会修改用户的全局 shell `PATH`。如果 `docdev` 不在 `PATH` 上，但
`~/.local/bin/docdev` 存在，agent 直接使用完整路径即可。

CLI 可以复制模板、追加下一个 `D-XXX` skeleton、audit 结构、sync skill、打包 release、
安装和更新。CLI 不负责做产品设计、不放松 SPEC invariant，也不替用户决定取舍。

## Native Release Install（原生发布安装）

普通用户安装已发布 GitHub Release 时，优先使用 remote native installer，而不是要求
用户 clone 源码 checkout。installer 会下载 manifest 和 artifact，校验 checksum，安装到
用户目录，写入 launcher，并运行 `docdev doctor`。

Unix shells：

```bash
curl -fsSL https://github.com/hongzhiyin/docs-driven-dev/releases/latest/download/install_remote.sh | sh
```

本地 smoke test 或镜像安装可以设置：

```bash
DOCDEV_RELEASE_BASE_URL="file:///path/to/release-assets" ./scripts/install_remote.sh
```

默认 native layout：

```text
~/.local/share/docdev/releases/<version>/
~/.local/share/docdev/current
~/.local/bin/docdev
```

生成的 launcher 会把 `DOCDEV_PROJECT_DIR` 和 `PYTHONPATH` 指向当前 release。installer
不会编辑 shell 启动文件；如果 `~/.local/bin` 不在 `PATH` 上，使用完整 launcher 路径，
或由用户自己添加 PATH。

native release install 使用 `docdev update` 更新。只有当 skill target directories 也要
从 release install 刷新时，才使用 `docdev update --sync-skill`。

Private GitHub Releases 需要显式认证，而且普通
`github.com/.../releases/download/...` asset URL 可能返回 404。私有测试时，用
`gh release download` 或 GitHub API 先把 assets 下载到本地，再用
`DOCDEV_RELEASE_BASE_URL=file:///path/to/assets` 安装。不要把 token 写入 launcher 或持久
install metadata。

## Source Checkout Install（源码开发安装）

clone 源码仓库后，开发者维护路径是：

Unix shells、Git Bash 或 WSL：

```bash
./scripts/install.sh
```

Windows PowerShell：

```powershell
Unblock-File .\scripts\*.ps1
.\scripts\install.ps1
```

如果 Windows 询问用哪个 app 打开 `install.sh`，说明当前 shell 不执行 `.sh` 文件。请用
上面的 PowerShell 命令，或在 Git Bash / WSL 中运行 `bash ./scripts/install.sh`。

如果当前 PowerShell policy 要求签名脚本，可以只对本进程使用 bypass：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install.ps1
```

这是 source checkout maintenance path，不是普通用户的 native release install 路径。
它会安装源码 wrapper、运行验证，并同步 skill target。默认安装会 force sync。对带
`.docdev-skill-source` marker 的目标，sync 会替换整个 skill 目录，避免旧文件残留，
包括旧版本生成的 `bin/docdev*` wrapper；如果以前用过另一个目标路径，那个旧路径不会被
自动清理。

更新源码 checkout 时，优先用 `git pull` 或干净 clone。不要把下载文件手动覆盖到旧目录；
manual file overlays can leave stale untracked files in the source checkout，sync 会复制
当前 checkout 里实际存在的 `skill/` 目录。

如果安装在 agent 无法检查的机器上失败，让用户提供最后一行以 `[docdev install]` 或
`[docdev update]` 开头的输出；编号 step 能定位中断阶段。

如果某个 agent 的 skill directory 不在默认当前用户 home 下，在 install/sync 前设置：
`DOCDEV_<TARGET>_SKILL_DIR` 指向最终 skill 文件夹，或 `DOCDEV_<TARGET>_HOME` 指向包含
`skills/docs-driven-dev` 的 agent home。`<TARGET>` 是 `CODEX`、`CURSOR`、`AGENTS`
或 `CLAUDE`。PowerShell 的 `$env:...` 赋值只影响当前 session；Windows 用户 / 系统
环境变量影响未来终端。

## Document Boundaries（文档边界）

| Doc | Answers | Refuses |
|---|---|---|
| `SPEC.md` | 什么应该为真：invariants、contracts、defaults | implementation details、history |
| `ARCHITECTURE.md` | 当前实际结构：layers、modules、data flow、config | behaviour rules、plans |
| `ROADMAP.md` | 当前进度：Phase/Step、tasks、acceptance、verification | design rationale、abandoned options |
| `DECISIONS.md` | 为什么这么选：D-XXX、options、choice、risks | current status、implementation prose |

两个机制让这个方法有用：

1. SPEC 里有编号 invariant，例如 `**#1**`；不要静默违反。
2. ROADMAP Step 在实现开始前写清 acceptance criteria。
3. 对 existing-project feature work，用 change packet 把 research、implementation
   gate 和 verification records 限定在当前需求范围里。

已有代码库没有项目级四件套时，这是 adoption case，不是 blocked case。先运行
`docdev init <project>` 创建最小 pending 根文档，再运行
`docdev new-change "<slug>" <project>` 处理当前需求。不要让一个单独的
`docs/changes/...` packet 成为项目唯一的 docs-driven artifact。

## Workflow A - Bootstrap（项目初始化）

使用时机：`<docs_dir>/SPEC.md` 不存在，或用户明确要求建立 docs-driven development。

1. 用一句话确认项目目标。
2. 运行 `docdev init <project>` 创建四个模板、README pointer、AGENTS pointer 和
   generated report directory。
3. 和用户一起填 SPEC §1 和 SPEC §2 decision table。目标是 5-10 个真实选择。
4. 写入或完善至少一个 SPEC invariant，再进入代码。
5. 在 ROADMAP 中添加 Step 0 或 Step 1，并写清 acceptance criteria。
6. 在 DECISIONS 中添加 D-001，记录 foundational trade-off。
7. 只有用户明确要求时才 stage 或 commit。

如果某个决策未知，写 `pending D-XXX` 并继续。Bootstrap 不应因为一个选择需要后续调研
而停住。

对已有代码库，Bootstrap 要轻量。先创建根四件套，让未来工作有 durable contract，然后
立刻进入 Workflow B 处理当前需求。

## Workflow B0 - Small Existing-Project Fix（小修复）

使用时机：用户明确点名 `docs-driven-dev`，且请求是窄范围 bug fix 或小行为调整。

1. 不跳过文档。若项目级 docs 缺失，先运行 Workflow A 做最小 adoption root，除非用户
   明确禁止改文档。
2. 用 `docdev new-change "<slug>" <project>` 创建 scoped change packet。
3. packet 保持最小：
   - SPEC：一条 expected behavior invariant 或 acceptance rule。
   - ROADMAP：goal、touched files、acceptance checks、verification command。
   - DECISIONS：只有存在真实 trade-off 时才新增或更新。
   - ARCHITECTURE：除非 module boundaries、data flow、lifecycle、persistence、
     public APIs、events、config、migration 或 cross-cutting structure 变化，否则省略。
4. Treat an explicit user request like "fix it", "补上吧", or "implement it" as
   implementation approval after the packet states scope and acceptance.
5. 然后实现窄范围修复、验证、把 verification 写回 packet，并运行
   `docdev audit <project>`。
6. 不要因为改动看起来很小，就把这个 workflow 替换成直接改代码。

## Workflow B - Existing Project Requirement（已有项目需求）

使用时机：用户想在已有项目中做 feature、refactor、research task 或 behaviour change。

1. 如果项目级 SPEC 缺失，先用 Workflow A 做轻量 existing-code adoption，再回到这里。
2. 先读项目级 SPEC，再读 ROADMAP，按需读 DECISIONS 和 ARCHITECTURE。
3. 用一句话复述你理解的目标，只问接下来最关键的 1-3 个问题。
4. 运行 `docdev new-change "<slug>" <project>` 创建 scoped work packet。只有结构影响已经
   明确时才加 `--with-architecture`。
5. 先调研，再设计。把带文件路径的具体发现写入 packet ROADMAP research log。行为约束
   进入 packet SPEC；结构事实进入 packet ARCHITECTURE（如果存在）。
6. 在 implementation gate 前停住：goal、scope、non-goals、相关既有代码、open questions、
   implementation steps、verification 和 user approval 都要清楚，才能改 production code。
7. 用户批准后小步实现。如果现实揭示了新的 user-visible trade-off，更新 SPEC/DECISIONS
   并确认，而不是静默 patch。
8. 验证每条 acceptance criterion，记录 verification results，运行
   `docdev audit <project>`，并显式留下剩余风险。

如果 packet 省略 `ARCHITECTURE.md`，ROADMAP 的 omission reason 必须保持准确。只要调研
发现 module、data-flow、lifecycle、persistence、public API、event、config、migration
或 cross-cutting impact，就在实现前补 ARCHITECTURE。

### Bounded Read-Only Research

当平台支持 sub-agents，且项目区域很宽时，可以把边界清楚的 read-only 问题委派出去，
降低主上下文压力。例如：“找出现有 X 实现”或“比较 Y 相关测试”。要求返回 file paths、
可用时带 line references、简短 findings 和 uncertainty。把结果汇总进 change packet。
不要委派产品决策、implementation approval 或含糊的用户取舍。

## Workflow C - Project-Level Extend（项目级扩展）

使用时机：`<docs_dir>/SPEC.md` 已存在，且用户要做会改变 durable project-level contract
的 feature、refactor 或 behaviour change。

1. 先读 SPEC，再读 ROADMAP，按需读 DECISIONS / ARCHITECTURE。
2. 对齐意图：说明 problem、at-risk invariants、module surface 和 acceptance criteria。
   如果当前 agent 有 question tool 可以用；否则直接问 1-3 个短问题。
3. 实现前先更新 SPEC 中的规则或合同。
4. 追加 ROADMAP Step 或 sub-step，并写清 acceptance criteria。
5. 小步实现。如果现实迫使新选择，回到对齐和决策记录，不要静默 patch。
6. 用 Step acceptance criteria 验证，运行 `docdev audit`。
7. 若变更对用户可见，追加或完成相关 D-XXX，并同步 README 状态。

## ROADMAP Step Shape

```markdown
## Step N - <one-line goal>

**Goal**: <why now, one sentence>

**Tasks**:
- [ ] task 1
- [ ] task 2
- [ ] doc sync: SPEC §x.y / D-XXX / README

**Acceptance**:
1. user-observable test
2. typecheck / lint clean
3. invariant #N still holds
```

任何超过一天，或 acceptance point 多于三条的 Step，都拆成 `Na`、`Nb` 或类似小步。

## DECISIONS Rules

- D-XXX numbers are monotonic：不复用、不跳号。
- 推翻旧决策时，新增一个 D-XXX 并标记旧条目被 superseded；不要重写旧结论。
- 每个 non-trivial decision 至少包含 options、chosen、rationale、risks，以及相关
  docs/code 链接。

用 `docdev new-decision "<title>" <project>` 追加下一个 skeleton。

## Anti-Patterns（反模式）

- 先 coding，再倒推意图。
- 把 rationale 写进 SPEC，或把 current status 写进 DECISIONS。
- SPEC 里长篇散文，没有编号 invariant。
- ROADMAP 只写 “do the thing”，没有 acceptance。
- generated reports 或 scratch notes 放在四个 source documents 旁边。
- 对 substantial existing-project requirement，在创建或更新 change packet 前就开始写
  production code。
- 把未解决假设藏在 code comments 里，而不是放到 SPEC open questions 或 DECISIONS。

## Reference

只有在需要强示例时，才读 `references/examples.md`：decision table、invariant list、
Step split 或 D-XXX entry。

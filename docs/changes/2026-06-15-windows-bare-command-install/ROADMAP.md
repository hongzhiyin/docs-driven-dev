# ROADMAP - Windows 裸命令安装

> 本文件追踪本次需求做到哪一步。它承接 SPEC 的验收标准，记录调研、门禁、任务和验证结果。

## 0. 当前状态

**阶段 / Phase**: 发布准备
**当前 Step / Current Step**: Step 5 - 验证与收尾；准备 v0.1.7 release
**ARCHITECTURE 省略理由 / Architecture Omission Reason**: 不省略。本需求改变 Windows native install 的 launcher / PATH / update 调用链，属于配置契约和安装数据流变化。

## 1. Gates

### Pre-Implementation Gate

- [x] 用户目标已用一句话确认
- [x] 范围和非目标已写入 SPEC
- [x] 现有实现、调用点、测试和配置已调研
- [x] 关键约束 / 不变式已写入 SPEC
- [x] 需要的 DECISIONS 条目已记录或标记为阻塞
- [x] 实现步骤和验收方式已写清
- [x] 用户已确认实现方案

### Completion Gate

- [x] 所有实施任务完成或有明确跳过理由
- [x] 验收标准逐条验证或有明确剩余风险
- [x] 文档与最终实现一致
- [x] 剩余风险和后续工作已记录

## 2. 调研记录

| ID | 主题 | 发现 | 证据 / 文件 | 结论 |
|---|---|---|---|---|
| R-1 | Windows remote installer launcher | 当前只写 `$BinDir\docdev.ps1`，没有 `docdev.cmd`，也没有 PATH 修改逻辑 | `scripts/install_remote.ps1` | 无法保证用户安装后直接输入 `docdev -v` |
| R-2 | Source checkout Windows wrapper | 源码维护安装已经生成 `.\.venv\Scripts\docdev.ps1` 和 `docdev.cmd` | `scripts/install_cli.ps1` | 可复用 `.cmd` 生成思路，但不能把 source wrapper 当普通用户入口 |
| R-3 | Native update dispatch | `cmd_update()` 固定调用 `scripts/install_remote.sh` | `src/docs_driven_dev/release.py` | Windows 上 `docdev update` 需要按平台选择 `install_remote.ps1` |
| R-4 | Uninstall candidate set | `launcher_candidates()` 已包含 `docdev` / `docdev.ps1` / `docdev.cmd` | `src/docs_driven_dev/release.py` | 新增 `docdev.cmd` 后卸载 planner 已有基础支持 |
| R-5 | Release packaging | GitHub Release assets 已包含 `install_remote.sh` 和 `install_remote.ps1` | `scripts/package_release.sh` | 可继续用 GitHub latest asset 安装，不需要 npm |
| R-6 | lark-cli command exposure | npm package `bin` 字段暴露 `lark-cli`，本机全局安装后 `bin/lark-cli` 指向 package script | 本机 `@larksuite/cli/package.json`、`ls -l $(command -v lark-cli)` | Windows 上 npm 会生成命令 shim；参考点是“installer owns shim”，不是用户手写 alias |
| R-7 | lark-cli release artifact | latest GitHub Release `v1.0.53` 包含 `lark-cli-1.0.53-windows-amd64.zip`、`windows-arm64.zip` 和 `checksums.txt` | GitHub API `https://api.github.com/repos/larksuite/cli/releases/latest` | lark-cli 的严格无 wrapper 体验来自 `.exe` 二进制；docdev 若要同级体验需后续二进制打包 |
| R-8 | lark-cli download/update model | `npx @larksuite/cli@latest install` 是 README 推荐安装；postinstall 下载 GitHub Release 二进制并 checksum；`lark-cli update` 自动识别 npm install 或提示 GitHub Release URL | `https://github.com/larksuite/cli`、本机 `lark-cli update --help` | docdev 可保留 GitHub-first，同时借鉴 checksum、platform asset、update 语义 |
| R-9 | Windows PATH 机制 | 环境变量不会让不存在的命令可用；需要 PATH 目录中有 `docdev.exe`、`docdev.cmd` 等可执行入口。持久 User PATH 修改通常只影响新终端；当前 PowerShell session 需同步 `$env:Path` | Windows command model / PowerShell env behavior | 本次应写 `docdev.cmd`，并默认添加 User PATH + current session PATH |

## 3. Step 状态总览

| Step | 内容 | 状态 |
|---|---|---|
| 0 | 建立需求工作包 | 完成 |
| 1 | 澄清需求与范围 | 完成 |
| 2 | 调研既有实现 | 完成 |
| 3 | 形成并确认方案 | 完成 |
| 4 | 实施代码与测试 | 完成 |
| 5 | 验证与收尾 | 发布准备 |

---

## Step 0 - 建立需求工作包

**Goal**: 创建 SPEC / ROADMAP / DECISIONS，并决定是否需要 ARCHITECTURE。

**Tasks**:
- [x] 初始化工作包文档
- [x] 记录 ARCHITECTURE 是否需要及理由

**Acceptance**:
1. 工作包目录存在，且文档结构清晰。

---

## Step 1 - 澄清需求与范围

**Goal**: 把粗略需求转成可验收的行为描述。

**Tasks**:
- [x] 补全 SPEC 一句话目标
- [x] 补全范围 / 非目标
- [x] 列出开放问题

**Acceptance**:
1. 用户确认 SPEC 的目标、范围和非目标。

---

## Step 2 - 调研既有实现

**Goal**: 找出现有 Windows installer / update / tests 的真实边界，并比较 lark-cli 的安装模型。

**Tasks**:
- [x] 调研 `install_remote.ps1`、`install_cli.ps1`、`release.py`、`package_release.sh`。
- [x] 调研本机 `lark-cli` 安装形态和 update help。
- [x] 查询 `larksuite/cli` GitHub README、package metadata、latest release assets。

**Acceptance**:
1. 调研记录列出当前缺口、可复用结构和外部参考。

---

## Step 3 - 形成并确认方案

**Goal**: 在实现前确认 Windows 裸命令的最小可行方案和后续增强边界。

**Tasks**:
- [x] 记录 `docdev.cmd` + User PATH + `-NoModifyPath` 的推荐方案。
- [x] 记录 GitHub Release latest 仍是默认安装源，不走 npm-first。
- [x] 记录严格 `docdev.exe` 二进制方案为后续增强。
- [x] 用户确认是否接受 installer-owned `docdev.cmd` 作为本轮方案。

**Acceptance**:
1. 用户确认后，才能修改 production scripts / code / root docs。

---

## Step 4 - 实施代码与测试

**Goal**: 让 Windows release install/update 生成可被 `docdev` 裸命令解析的入口。

**Tasks**:
- [x] 修改 `scripts/install_remote.ps1`，生成 `docdev.cmd` 和 `docdev.ps1`。
- [x] 修改 `scripts/install_remote.ps1`，默认添加 `BinDir` 到 User PATH 并刷新当前 `$env:Path`，支持 `-NoModifyPath`。
- [x] 修改 `src/docs_driven_dev/release.py`，Windows 下 `docdev update` 调用 `install_remote.ps1` 并传递参数。
- [x] 更新 README、root SPEC / ARCHITECTURE / ROADMAP / DECISIONS、skill 文案。
- [x] 更新 tests，覆盖 Windows remote installer static contract、update dispatch、docs wording。

**Acceptance**:
1. Unit tests 验证 Windows launcher / PATH / update dispatch 合同。
2. Unix installer / update tests 不回退。
3. Project audit 无 findings。

---

## Step 5 - 验证与收尾

**Goal**: 证明 GitHub latest install/update 后 Windows 用户能运行 `docdev -v`。

**Tasks**:
- [x] 运行 unit tests。
- [x] 运行 `docdev audit /Users/chihoyo/Project/docs-driven-dev`。
- [x] 运行 package release local smoke。
- [x] 运行 packaged `0.1.7` local install/init/audit/uninstall smoke。
- [x] 记录当前环境无法直接执行 Windows 真机 smoke。
- [ ] 发布 `v0.1.7` 并运行 public latest install smoke。
- [ ] 尽可能在 Windows 真机运行 latest install/update smoke。
- [x] 把 verification 写回本文件。

**Acceptance**:
1. Windows 新终端里 `docdev -v` 可用。
2. Windows `docdev update` 后 `docdev -v` 仍可用。
3. 完成门禁全部通过或有明确剩余风险。

## 4. 验证记录

| 验收项 | 验证方式 | 结果 | 备注 |
|---|---|---|---|
| SPEC-1 | `docdev new-change "windows-bare-command-install" ... --with-architecture` | 通过 | 已创建工作包 |
| SPEC-2 | 本机 `lark-cli --version` / `lark-cli update --help` | 通过 | 本机版本 1.0.23；help 显示 update 识别 npm/manual |
| SPEC-3 | GitHub latest release API | 通过 | larksuite/cli latest 为 v1.0.53，含 Windows zip assets 和 checksums |
| SPEC-4 | `python3 -m unittest discover -s tests` | 通过 | 37 tests OK |
| SPEC-5 | `./scripts/package_release.sh --out /private/tmp/docdev-windows-command-package-smoke` | 通过 | 生成 artifact、checksum、manifest、install_remote.sh、install_remote.ps1 |
| SPEC-6 | `docdev audit /Users/chihoyo/Project/docs-driven-dev` | 通过 | No findings |
| SPEC-7 | Windows 真机 `docdev -v` | 待真机验证 | 当前环境不是 Windows；按发布请求先以静态 / unit / package / public install smoke 发布，后续用 Windows 真机或 CI 验证 |
| SPEC-8 | `pyproject.toml` / `src/docs_driven_dev/__init__.py` | 通过 | release metadata bumped to `0.1.7` |
| SPEC-9 | `./scripts/package_release.sh --out /private/tmp/docdev-release-assets-0.1.7` | 通过 | 生成 `docdev-0.1.7.tar.gz`、checksum、manifest、Unix / Windows installers |
| SPEC-10 | `./scripts/install_remote.sh --release-base-url file:///private/tmp/docdev-release-assets-0.1.7 --install-root /private/tmp/docdev-017-local-smoke.Rdg7Pd/root --bin-dir /private/tmp/docdev-017-local-smoke.Rdg7Pd/bin --no-sync-skill` + `docdev --version/init/audit/uninstall` | 通过 | launcher 输出 `docdev 0.1.7`，隔离目标项目 audit 为 No findings，临时 install root / launcher 已卸载 |

## 5. 风险与后续

| ID | 风险 / 后续 | 影响 | 处理 |
|---|---|---|---|
| F-1 | `docdev.cmd` 仍是 installer-owned shim，不是严格二进制 | 若用户坚持零 shim，则本轮不满足 | 需要用户确认；严格二进制作为后续 |
| F-2 | PATH 持久修改只影响新终端 | 用户可能在旧终端立刻运行失败 | installer 同步当前 `$env:Path`，并打印重开终端提示 |
| F-3 | 受管 Windows 环境可能禁止 PATH 修改 | 安装成功但裸命令不可用 | 提供 opt-out 和明确诊断输出 |
| F-4 | 当前机器不是 Windows | 无法直接 live test 所有 PowerShell 行为 | 已做静态 / unit / package；发布后需要用户或 CI Windows runner 验证 |

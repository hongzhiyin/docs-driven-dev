# DECISIONS - Windows 裸命令安装

> 本文件记录这次需求中为什么这么选。只写真实取舍，不为机械改动补仪式性决策。

## 维护规则

1. `D-XXX` 在本工作包内单调递增，不复用。
2. 每条记录 2-3 个真实选项；不要编造凑数选项。
3. 写清选择、理由、风险和对应文件。
4. 决策被推翻时，新增一条 D-XXX 引用旧决策，旧决策保留原文。

---

## D-001 - Step 3 - 先用 installer-owned `docdev.cmd` 达成裸命令

**日期 / Date**: 2026-06-15

**上下文 / Context**:
Windows 用户希望安装完成后直接运行 `docdev -v`。当前 remote installer 只写
`docdev.ps1`，且不修改 PATH；这导致用户必须知道 wrapper 路径或手写 alias。要达到
裸命令体验，Windows 必须在 PATH 中有可解析的 `docdev.exe`、`docdev.cmd` 等入口。

**选项 / Options**:
- A. 让用户自己写 profile function / alias - 实现最快，但把安装体验问题推给用户。
- B. remote installer 生成 `docdev.cmd` 并管理用户 PATH - 保持 Python 源码 release 结构，用户看到的是 `docdev` 命令；仍然是 installer-owned shim，不是严格二进制。
- C. 本轮直接发布 Windows `docdev.exe` - 最接近 lark-cli 的二进制体验，但需要新增平台打包、CI/Windows 构建、签名/杀软误报处理，超出当前最小修复。

**选择 / Chosen**: B

**理由 / Rationale**:
- B 能满足用户核心体验：安装后运行 `docdev -v`，不需要用户手写 alias 或记住 `docdev.ps1`。
- B 延续当前 GitHub Release + manifest + checksum 的分发体系，不引入 npm 或 Node.js。
- B 的技术面已经在 source checkout wrapper 中有先例：`scripts/install_cli.ps1` 生成 `docdev.cmd`。
- C 是更彻底的后续方向，但它会把本需求扩大成跨平台二进制发布体系，不适合先解决当前 Windows 使用阻塞。

**风险 / Risks**:
- `docdev.cmd` 仍是 launcher/shim。如果用户严格要求“无任何 wrapper”，需要后续改为 `docdev.exe`。
- 持久 User PATH 修改通常只对新终端可靠；installer 应刷新当前 `$env:Path` 并提示重开终端。
- 受管机器可能禁止 PATH 修改；必须提供 `-NoModifyPath` opt-out。

**对应代码 / 文档**:
- SPEC §3-§8
- ROADMAP Step 3 / Step 4
- `scripts/install_remote.ps1`
- `src/docs_driven_dev/release.py`

---

## D-002 - Step 3 - 保持 GitHub Releases 默认安装源，不改成 npm-first

**日期 / Date**: 2026-06-15

**上下文 / Context**:
用户明确希望“能直接通过 GitHub 下载最新版本安装或更新”。`lark-cli` 的默认体验是
`npx @larksuite/cli@latest install`，npm 包通过 `bin` 暴露命令并下载 GitHub Release
二进制；这说明 npm 是一种 command shim / installer 分发方式，但不是唯一方式。

**选项 / Options**:
- A. 改成 npm-first，借助 npm 自动生成 Windows command shim - Windows 裸命令自然，但要求 Node.js / npm，偏离当前项目的 GitHub-native 方向。
- B. 保持 GitHub Releases first，用 PowerShell installer 下载 latest release 并安装 command entrypoint - 符合用户目标和现有 release 架构。
- C. 同时做 npm 和 GitHub installer - 覆盖面最大，但会增加同步、版本、更新和文档维护面。

**选择 / Chosen**: B

**理由 / Rationale**:
- 当前项目已经有 release manifest、checksum、install/update/uninstall 和 public latest smoke。
- 用户这次明确提到 GitHub 下载最新版本安装或更新；不应把 npm 变成前置要求。
- B 仍可借鉴 lark-cli 的平台 artifact、checksum、update 语义，而不复制它的 npm 入口。

**风险 / Risks**:
- GitHub 在部分网络环境可能不可达；当前 installer 已支持 release base override，后续可增加 mirror fallback。
- 不走 npm 意味着 Windows command shim 由我们自己维护，而不是由 npm 自动生成。

**对应代码 / 文档**:
- SPEC §2-§5
- ROADMAP R-5 / R-8
- `scripts/install_remote.ps1`
- `scripts/package_release.sh`

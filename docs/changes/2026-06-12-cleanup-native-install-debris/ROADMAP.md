# ROADMAP - 清理 native install 迁移残留

> 本文件追踪本次需求做到哪一步。它承接 SPEC 的验收标准，记录调研、门禁、任务和验证结果。

## 0. 当前状态

**阶段 / Phase**: 完成
**当前 Step / Current Step**: Step 3 - 验证与收尾完成
**ARCHITECTURE 省略理由 / Architecture Omission Reason**: 不省略。本次会调整 native launcher 与源码 checkout maintenance path 的架构说明。

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
- [x] 验收标准逐条验证
- [x] 文档与最终实现一致
- [x] 剩余风险和后续工作已记录

## 2. 调研记录

| ID | 主题 | 发现 | 证据 / 文件 | 结论 |
|---|---|---|---|---|
| R-1 | tracked scratch | `temp/` 下旧纯 skill 参考材料仍被 git 跟踪；D-012 已把它的有效能力迁移到 `docs/changes/` 模式 | `git ls-files temp`、`docs/DECISIONS.md` D-012 | 可删除 `temp/`，但用当前 docs/skill/template 承接能力 |
| R-2 | runtime cache | 工作区有 `tests/__pycache__` 和 `src/docs_driven_dev/__pycache__` | `find . -maxdepth 3 -type d ...` | 直接清理，不进入 git |
| R-3 | 源码 wrapper | `scripts/install_cli.*`、`scripts/update_cli.*`、`sync-skill` 和 CLI wrapper generation 仍有测试和文档合同 | `tests/test_cli.py`、`docs/SPEC.md` §3.5 | 保留为 developer maintenance path |
| R-4 | current wording drift | `docs/ARCHITECTURE.md` 仍把 installed skill wrappers 写成 cross-project entrypoints，模板示例还写 `source checkout + wrapper script` | `docs/ARCHITECTURE.md`、`skill/templates/SPEC.md` | 更新当前文档/模板，避免误导新机器安装 |
| R-5 | historical decisions | D-006、D-019 记录旧 wrapper 方案，D-021/D-022 已选择 native installer / native launcher 优先 | `docs/DECISIONS.md` | 不改写历史；新增当前 cleanup 决策 |

## 3. Step 状态总览

| Step | 内容 | 状态 |
|---|---|---|
| 0 | 建立需求工作包 | 完成 |
| 1 | 调研并划定清理边界 | 完成 |
| 2 | 清理残留并校正文档 | 完成 |
| 3 | 验证与收尾 | 完成 |

---

## Step 0 - 建立需求工作包

**Goal**: 创建 SPEC / ROADMAP / DECISIONS，并决定是否需要 ARCHITECTURE。

**Tasks**:
- [x] 初始化工作包文档
- [x] 记录 ARCHITECTURE 是否需要及理由

**Acceptance**:
1. 工作包目录存在，且文档结构清晰。

---

## Step 1 - 调研并划定清理边界

**Goal**: 区分可删除残留与仍受支持的源码维护入口。

**Tasks**:
- [x] 查找 wrapper / source checkout / temporary / cache 引用。
- [x] 检查 `temp/` 是否被 git 跟踪。
- [x] 判断源码维护脚本是否仍在合同内。
- [x] 写入 SPEC 边界和 DECISIONS 取舍。

**Acceptance**:
1. 清理范围不包含仍受支持的源码 checkout maintenance path。

---

## Step 2 - 清理残留并校正文档

**Goal**: 删除实际残留，更新当前文档和模板措辞。

**Tasks**:
- [x] 删除 tracked `temp/` 旧参考目录。
- [x] 删除 Python `__pycache__` 运行缓存。
- [x] 更新 `docs/ARCHITECTURE.md` 的 native-first / source-maintenance 结构说明。
- [x] 更新 `README.md` 和 `skill/templates/SPEC.md` 中容易误读的 wrapper 表述。
- [x] 清理 native-installer packet 中明显过期的版本快照措辞。

**Acceptance**:
1. `git ls-files temp` 无输出，cache 目录不再存在。
2. 当前文档不把源码 wrapper 描述成普通跨机器入口。

---

## Step 3 - 验证与收尾

**Goal**: 证明清理没有破坏 CLI 和 docs-driven 结构。

**Tasks**:
- [x] 运行单元测试。
- [x] 运行 `docdev doctor`。
- [x] 运行 `docdev audit /Users/chihoyo/Project/docs-driven-dev`。
- [x] 记录验证结果和剩余风险。

**Acceptance**:
1. 测试、doctor、audit 均通过。

## 4. 验证记录

| 验收项 | 验证方式 | 结果 | 备注 |
|---|---|---|---|
| SPEC-1 | `test ! -d temp` | 通过 | 旧 tracked scratch 已从工作区删除 |
| SPEC-2 | `find . -maxdepth 3 -type d ...` | 通过 | 测试后再次清理，未发现 cache/build 目录 |
| SPEC-3 | `PYTHONPATH=src python3 -m unittest discover -s tests` | 通过 | 30 tests OK |
| SPEC-4 | `/Users/chihoyo/.local/bin/docdev doctor` | 通过 | native release 0.1.3 doctor OK |
| SPEC-5 | `/Users/chihoyo/.local/bin/docdev audit /Users/chihoyo/Project/docs-driven-dev` | 通过 | No findings |

## 5. 风险与后续

| ID | 风险 / 后续 | 影响 | 处理 |
|---|---|---|---|
| F-1 | 历史 DECISIONS / ROADMAP 仍包含旧 wrapper 方案记录 | 搜索结果会出现历史术语 | 接受；通过 D-022、D-024 和当前 ARCHITECTURE 标明现状 |
| F-2 | 已同步到 agent homes 的旧 wrapper 可能仍存在 | 本机兼容入口还可运行 | 接受；它们是源码维护兼容物，不是 native agent 解析路径 |

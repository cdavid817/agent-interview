# 深度技术文档整合 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 `Claude-Code-技术文档.md` 与 `OPencode技术内幕.md` 两份深度技术文档收录进 AgentInterview 仓库，并从中提炼 60 道面试题（Claude Code +35、新建 OpenCode 章节 +25），题库总数 1,738 → 1,798。

**Architecture:** 原文进 `docs/reference/deep-dive/` 作为可引用资料；题目按现有 `question-schema.md` 格式写入 `docs/04-products/`；`scripts/validate.py` 增加「源码分析」来源类型与 `OPC` 前缀支持；所有索引、术语表、Anki 卡组由脚本重建。

**Tech Stack:** Markdown、Python 3.12（`scripts/validate.py`、`build_indexes.py`、`build_anki.py`）、PowerShell 7（`build_glossary.ps1`）、`genanki` + `markdown`（已确认安装）。

**设计文档：** `specs/2026-08-17-integrate-deep-dive-docs-design.md`

## Global Constraints

- 本计划的产物文档（spec、plan）放在仓库根的 `specs/`、`plans/`，**不能放进 `docs/`**：`validate_local_links()` 遍历 `docs/**/*.md` 且不剥离代码围栏，示例链接会被当成坏链。已实测。
- 题目锚点格式固定：`<a id="cc-101"></a>` 独占一行，紧跟 `### N. 题干`，N 为文件内顺序号从 1 递增。
- 产品专题题目元数据行固定为：`> 核验日期：2026-08-17｜来源：[源码分析](references.md)`
- 每题**有且仅有一行**以 `**相关知识点：**` 开头的行，行内**不得出现** `CC-123` 形式的题目 ID。
- 每题答案必须命中可验证信号词之一（指标 / 验证 / 测试 / 成本 / 延迟 / 成功率 / 覆盖率 / P95 / Token / 监控 / 耗时 等），否则报「缺少可验证指标」。
- 任意去除空白后 ≥100 字符的段落不得与其他题目重复，否则报「跨题重复长段落」。
- 标题标准化（去空白标点、casefold）后不得与题库中任何既有标题重复。
- 单个题目文件不超过 50 题。
- 同一文件内稳定 ID 数字必须严格递增。
- 答案正文中若出现 `[文本](路径)` 形式，路径必须真实存在。
- 每个任务结束前必须跑通：`python scripts/build_indexes.py` → `pwsh -File scripts/build_glossary.ps1` → `python scripts/validate.py`，输出 `All checks passed.`

## 源文档路径

- `D:/cdavid/Documents/code/claude-code/Claude-Code-技术文档.md`（7,238 行）
- `D:/cdavid/Documents/code/opencode/OPencode技术内幕.md`（5,852 行）

---

## File Structure

| 文件 | 职责 |
|---|---|
| `docs/reference/deep-dive/README.md` | 深度资料入口 + 非官方性质说明 |
| `docs/reference/deep-dive/claude-code-源码技术文档.md` | CC 原文（加头部说明） |
| `docs/reference/deep-dive/opencode-技术内幕.md` | OpenCode 原文（加头部说明） |
| `docs/04-products/opencode/README.md` | OpenCode 章节索引（脚本重写正文） |
| `docs/04-products/opencode/references.md` | OpenCode 官方 + 源码分析资料 |
| `docs/04-products/opencode/opencode-basics.md` | OPC-001…013，架构与工程体系 |
| `docs/04-products/opencode/runtime-context.md` | OPC-014…025，V2 运行时与上下文 |
| `docs/04-products/claude-code/internals.md` | CC-101…135，源码级内部机制 |
| `docs/04-products/claude-code/references.md` | 追加「源码分析资料」小节 |
| `scripts/taxonomy.json` | 注册 OpenCode 章节与 `OPC` 前缀 |
| `scripts/validate.py` | 支持 `OPC` 前缀与「源码分析」来源 |

---

### Task 1: 收录两份原文

**Files:**
- Create: `docs/reference/deep-dive/README.md`
- Create: `docs/reference/deep-dive/claude-code-源码技术文档.md`
- Create: `docs/reference/deep-dive/opencode-技术内幕.md`
- Modify: `docs/reference/README.md`

**Interfaces:**
- Produces: 两条稳定的相对路径，供后续 `references.md` 引用：
  - 从 `docs/04-products/claude-code/references.md` 看是 `../../reference/deep-dive/claude-code-源码技术文档.md`
  - 从 `docs/04-products/opencode/references.md` 看是 `../../reference/deep-dive/opencode-技术内幕.md`

- [ ] **Step 1: 复制两份原文到 deep-dive 目录**

```bash
cd "D:/cdavid/Documents/code/AgentPrimer/AgentInterview"
mkdir -p docs/reference/deep-dive
cp "D:/cdavid/Documents/code/claude-code/Claude-Code-技术文档.md" \
   "docs/reference/deep-dive/claude-code-源码技术文档.md"
cp "D:/cdavid/Documents/code/opencode/OPencode技术内幕.md" \
   "docs/reference/deep-dive/opencode-技术内幕.md"
```

- [ ] **Step 2: 修掉 3 处伪本地链接**

这三处是正文里形如「方括号紧跟半角圆括号」的普通文字，不是真链接，但会被 `validate_local_links()` 判为坏链。

**必须把半角圆括号改成全角圆括号**。加反引号无效——`LOCAL_LINK_RE` 直接在原始文本上匹配，不识别代码围栏也不识别反引号。

在 `docs/reference/deep-dive/claude-code-源码技术文档.md`：
- 第 1392 行附近：`[GlobTool, GrepTool](除非有嵌入式搜索)` → `[GlobTool, GrepTool]（除非有嵌入式搜索）`
- 第 2834 行附近：`[Title](file.md)` → `[Title]（file.md）`

在 `docs/reference/deep-dive/opencode-技术内幕.md`：
- 第 1852 行附近：`[...](...)` → `[...]（...）`

- [ ] **Step 3: 去掉 OpenCode 原文重复的 H1**

`docs/reference/deep-dive/opencode-技术内幕.md` 第 1、2 行内容相同，删掉第 2 行。

- [ ] **Step 4: 给两份原文加头部说明块**

在各自 H1 之后插入（Claude Code 版本；OpenCode 版本把产品名和回链换掉）：

```markdown
> **资料性质：非官方。** 本文基于逆向分析与泄露源码整理，与官方实际实现可能不一致，仅供工程参考，不作为产品能力承诺。
> 收录日期：2026-08-17｜对应题库章节：[Claude Code](../../04-products/claude-code/README.md)
```

OpenCode 版本的回链为 `[OpenCode](../../04-products/opencode/README.md)`。

> ⚠️ 该回链在 Task 2 建出 `docs/04-products/opencode/README.md` 之前不存在，会让 `validate_local_links()` 报错。因此 **OpenCode 原文的回链行放到 Task 2 再加**；Task 1 只加「资料性质 + 收录日期」两行。

- [ ] **Step 5: 写 deep-dive 入口 README**

`docs/reference/deep-dive/README.md`：

```markdown
# 深度技术资料

本目录收录第三方整理的 Agent 产品深度技术资料，用于给题库中的源码级题目提供可引用出处。

> **这些资料不是官方文档。** 内容基于逆向分析、泄露源码或开源仓库阅读整理，与官方实际实现可能存在偏差。阅读时请把「机制设计思路」与「具体实现细节」分开看待：前者可迁移，后者随版本变化。

| 资料 | 篇幅 | 对应题库章节 |
|---|---|---|
| [Claude Code 源码技术文档](claude-code-源码技术文档.md) | 119 章 | [Claude Code](../../04-products/claude-code/README.md) |
| [OpenCode 技术内幕](opencode-技术内幕.md) | 26 章 + 4 附录 | [OpenCode](../../04-products/opencode/README.md) |
```

> ⚠️ 表格里的 OpenCode 章节链接同样在 Task 2 之后才存在。Task 1 先只写 Claude Code 一行，Task 2 再补 OpenCode 行。

- [ ] **Step 6: 在 `docs/reference/README.md` 增加入口**

在现有列表中追加一行：

```markdown
- [深度技术资料](deep-dive/README.md)
```

- [ ] **Step 7: 验证**

```bash
python scripts/build_indexes.py && python scripts/validate.py
```

Expected: `All checks passed.`，Total 仍为 1738。

若报「本地链接不存在」，说明 Step 2 的伪链接没修干净，用下面这条定位：

```bash
grep -noP '\[[^]]+\]\((?!https?://)(?!mailto:)(?!#)[^)]+\)' docs/reference/deep-dive/*.md
```

Expected: 无输出。

- [ ] **Step 8: 提交**

```bash
git add docs/reference/
git commit -m "docs: 收录 Claude Code 与 OpenCode 深度技术资料"
```

---

### Task 2: 新建 OpenCode 章节并写入 13 题

本任务必须一次性完成「注册章节 + 写题」：`validate.py` 会对已登记但零题目的前缀报错，拆开会导致中间状态无法通过校验。

**Files:**
- Modify: `scripts/taxonomy.json`
- Modify: `scripts/validate.py`
- Create: `docs/04-products/opencode/README.md`
- Create: `docs/04-products/opencode/references.md`
- Create: `docs/04-products/opencode/opencode-basics.md`
- Modify: `docs/reference/deep-dive/README.md`（补 OpenCode 行）
- Modify: `docs/reference/deep-dive/opencode-技术内幕.md`（补回链行）

**Interfaces:**
- Consumes: Task 1 产出的 `docs/reference/deep-dive/opencode-技术内幕.md`
- Produces: 前缀 `OPC`、章节路径 `docs/04-products/opencode`、锚点 `opc-001` … `opc-013`；Task 3 从 `OPC-014` 续写

- [ ] **Step 1: 注册章节**

`scripts/taxonomy.json` 数组末尾追加（注意上一行补逗号）：

```json
  {"area": "产品专题", "title": "OpenCode", "prefix": "OPC", "path": "docs/04-products/opencode"}
```

- [ ] **Step 2: 改 `scripts/validate.py` 三处**

其一，「相关知识点混入题目 ID」的前缀正则，加 `OPC`：

```python
            if re.search(
                r"相关知识点.*\b(?:ARC|TRANS|PLAN|CTX|TOOL|MULTI|RAG|MODEL|GOV|ENG|OCLAW|CC|OPC)-\d{3}\b",
                answer,
                re.IGNORECASE,
            ):
```

其二与其三，产品题校验集合加 `OPC`，来源行放行「源码分析」：

```python
            if prefix in {"OCLAW", "CC", "OPC"}:
                if not re.search(r"核验日期：\d{4}-\d{2}-\d{2}", body):
                    errors.append(f"{relative}: {stable_id} 缺少产品核验日期")
                if not any(
                    f"来源：[{label}](references.md)" in body
                    for label in ("官方资料", "源码分析")
                ):
                    errors.append(f"{relative}: {stable_id} 缺少产品资料链接")
```

- [ ] **Step 3: 建 README 占位**

`docs/04-products/opencode/README.md`。`build_indexes.py` 只重写「## 子主题」表格部分，头部需手写：

```markdown
# OpenCode

> OpenCode 的架构分层、V2 会话运行时、上下文代数、工具权限、Provider 与插件生态。

> 内容按 **2026-08-17** 整理的源码分析资料核验；具体行为仍以实际版本为准。

本章共 **13** 题。题目使用 `OPC-NNN` 稳定 ID，移动文件不会改变引用。

## 子主题

| 子主题 | 题数 |
|---|---:|
| [OpenCode 架构与工程体系](opencode-basics.md) | 13 |
## 资料

- [官方与源码分析资料](references.md)
```

题数由脚本纠正，先写占位即可。

- [ ] **Step 4: 写 `docs/04-products/opencode/references.md`**

```markdown
# OpenCode核验资料

## 官方核验资料

- [OpenCode 仓库](https://github.com/sst/opencode)
- [OpenCode 文档](https://opencode.ai/docs/)

## 源码分析资料（非官方）

- [OpenCode 技术内幕](../../reference/deep-dive/opencode-技术内幕.md)
  ※ 基于源码阅读整理，与官方实现可能不一致，仅供工程参考。
```

- [ ] **Step 5: 补 Task 1 里挂起的两条链接**

`docs/reference/deep-dive/README.md` 表格补 OpenCode 行；`docs/reference/deep-dive/opencode-技术内幕.md` 头部补回链行 `对应题库章节：[OpenCode](../../04-products/opencode/README.md)`。

- [ ] **Step 6: 写 `docs/04-products/opencode/opencode-basics.md` 的 13 题**

文件头：

```markdown
# OpenCode 架构与工程体系

> 所属章节：[OpenCode](README.md)｜本文件共 **13** 题。
```

逐题格式：

```markdown
<a id="opc-001"></a>
### 1. OpenCode 的设计哲学是什么？它与绑定单一编辑器的 Coding Agent 有哪些取舍差异？

> 核验日期：2026-08-17｜来源：[源码分析](references.md)

（答案正文）

**相关知识点：** 术语一、术语二、术语三。
```

题目 ID、顺序号、标题与取材章节对照（源文件为 `docs/reference/deep-dive/opencode-技术内幕.md`）：

| ID | 序号 | 标题 | 取材 |
|---|---:|---|---|
| OPC-001 | 1 | OpenCode 的设计哲学是什么？它与绑定单一编辑器的 Coding Agent 有哪些取舍差异？ | 第一章 |
| OPC-002 | 2 | OpenCode 的顶层包依赖如何划分？这种划分解决了什么工程问题？ | 第二章 |
| OPC-003 | 3 | OpenCode 的 CLI 命令体系如何组织？进程启动路径上有哪些关键决策？ | 第三章 |
| OPC-004 | 4 | OpenCode 的 Schema、Protocol、Server、Client 与 SDK 五层契约各自承担什么职责？ | 第四章 |
| OPC-005 | 5 | OpenCode 的配置体系如何合并多个来源？来源冲突时按什么规则裁决？ | 第五章 |
| OPC-006 | 6 | OpenCode 的 Provider 与模型目录如何组织？接入新模型需要改动哪些环节？ | 第六章 |
| OPC-007 | 7 | OpenCode 的策略系统解决什么问题？它与工具权限如何分工？ | 第七章 |
| OPC-008 | 8 | OpenCode 的插件生命周期有哪些阶段？插件出错时如何隔离影响？ | 第八章 |
| OPC-009 | 9 | OpenCode 的存储层与事件系统如何配合？为什么要把事件当作一等公民？ | 第二十一章 |
| OPC-010 | 10 | OpenCode 的 TUI 如何与会话运行时解耦？渲染压力如何控制？ | 第二十二章 |
| OPC-011 | 11 | OpenCode 的桌面端与跨端 UI 复用了哪些层？哪些部分必须分别实现？ | 第二十三章 |
| OPC-012 | 12 | OpenCode 的认证、控制面与同步分享如何设计？多设备场景存在哪些一致性问题？ | 第二十章 |
| OPC-013 | 13 | OpenCode 从 V1 演进到 V2 最关键的架构改变是什么？迁移成本体现在哪里？ | 第二十六章 |

写作时逐题打开对应章节阅读后再落笔，不要凭标题臆测。每题答案控制在 150–350 字，首段一句话给结论并加粗关键词，后续分点展开，最后一行写相关知识点。

- [ ] **Step 7: 验证**

```bash
python scripts/build_indexes.py && pwsh -File scripts/build_glossary.ps1 && python scripts/validate.py
```

Expected: `All checks passed.`，统计表出现 `13  OPC  OpenCode`，Total 1751。

- [ ] **Step 8: 提交**

```bash
git add scripts/ docs/
git commit -m "feat: 新增 OpenCode 产品专题章节与 13 道架构题"
```

---

### Task 3: OpenCode 运行时与上下文 12 题

**Files:**
- Create: `docs/04-products/opencode/runtime-context.md`
- Modify: `docs/04-products/opencode/README.md`（由脚本重写子主题表）

**Interfaces:**
- Consumes: Task 2 注册的 `OPC` 前缀与 `references.md`
- Produces: 锚点 `opc-014` … `opc-025`

- [ ] **Step 1: 写文件头**

```markdown
# OpenCode 运行时与上下文

> 所属章节：[OpenCode](README.md)｜本文件共 **12** 题。
```

- [ ] **Step 2: 写 12 题**

格式同 Task 2 Step 6。对照表：

| ID | 序号 | 标题 | 取材 |
|---|---:|---|---|
| OPC-014 | 1 | OpenCode V2 会话运行时由哪些角色组成？一次用户输入的完整流转路径是什么？ | 第九章 |
| OPC-015 | 2 | OpenCode 的「系统上下文代数」指什么？它用哪些运算描述上下文组合？ | 第十章 |
| OPC-016 | 3 | OpenCode 的上下文纪元状态机有哪些状态与迁移条件？纪元切换时什么会失效？ | 第十一章 |
| OPC-017 | 4 | OpenCode 的持久化提示如何准入与晋升？与一次性提示相比成本差别在哪？ | 第十二章 |
| OPC-018 | 5 | OpenCode 的会话执行路由与运行协调器如何决定一次请求由谁执行？ | 第十三章 |
| OPC-019 | 6 | OpenCode 会话运行器的 Drain 循环解决什么问题？如何避免消息丢失与重复执行？ | 第十四章 |
| OPC-020 | 7 | OpenCode 的提供者回合与工具结算如何划分边界？结算失败如何回滚？ | 第十五章 |
| OPC-021 | 8 | OpenCode 的自动压缩与历史投影有什么区别？投影为什么比直接截断更安全？ | 第十六章 |
| OPC-022 | 9 | OpenCode 的工具系统如何表达权限？它与 Claude Code 权限模型有哪些结构性差异？ | 第十七章 |
| OPC-023 | 10 | OpenCode 的 LLM 包与协议适配器如何屏蔽厂商差异？哪些差异无法屏蔽？ | 第十八章 |
| OPC-024 | 11 | OpenCode 如何统一集成 MCP、LSP、技能、ACP 与自定义命令？ | 第十九章 |
| OPC-025 | 12 | OpenCode 的可观测性、安全与运维体系覆盖哪些环节？关键指标有哪些？ | 第二十五章 |

- [ ] **Step 3: 验证**

```bash
python scripts/build_indexes.py && pwsh -File scripts/build_glossary.ps1 && python scripts/validate.py
```

Expected: `All checks passed.`，`25  OPC  OpenCode`，Total 1763。

- [ ] **Step 4: 提交**

```bash
git add docs/04-products/opencode/
git commit -m "feat: 新增 OpenCode 运行时与上下文 12 题"
```

---

### Task 4: Claude Code 源码级内部机制 前 18 题

**Files:**
- Create: `docs/04-products/claude-code/internals.md`
- Modify: `docs/04-products/claude-code/references.md`

**Interfaces:**
- Consumes: Task 2 改造后的 `validate.py`（放行「源码分析」来源）
- Produces: 锚点 `cc-101` … `cc-118`；Task 5 从 `CC-119` 在同一文件续写

- [ ] **Step 1: 给 `references.md` 追加源码分析小节**

在文件末尾追加：

```markdown

## 源码分析资料（非官方）

- [Claude Code 源码技术文档](../../reference/deep-dive/claude-code-源码技术文档.md)
  ※ 基于逆向与泄露源码整理，与官方实现可能不一致，仅供工程参考。
```

- [ ] **Step 2: 写 `internals.md` 文件头**

```markdown
# 源码级内部机制

> 所属章节：[Claude Code](README.md)｜本文件共 **35** 题。
```

题数先按最终值写，Task 4 结束时文件里只有 18 题，`build_indexes.py` 不校验这一行，`validate.py` 也不校验，Task 5 补齐后即一致。

- [ ] **Step 3: 写 CC-101 … CC-118**

格式：

```markdown
<a id="cc-101"></a>
### 1. Claude Code 的启动流程如何隐藏冷启动延迟？这套「触发 + 等待」两段式设计有什么约束？

> 核验日期：2026-08-17｜来源：[源码分析](references.md)

（答案正文）

**相关知识点：** 术语一、术语二、术语三。
```

对照表（源文件为 `docs/reference/deep-dive/claude-code-源码技术文档.md`）：

| ID | 序号 | 标题 | 取材 |
|---|---:|---|---|
| CC-101 | 1 | Claude Code 的启动流程如何隐藏冷启动延迟？这套「触发 + 等待」两段式设计有什么约束？ | 第 78 章 78.1–78.3 |
| CC-102 | 2 | 三阶段引导中哪些时序约束一旦打乱就会造成难以复现的间歇性故障？ | 第 78 章 78.4 |
| CC-103 | 3 | queryLoop 作为异步生成器需要维护哪些不变量？ | 第 78 章 78.5 |
| CC-104 | 4 | 为什么 tool_use 与 tool_result 的配对不变量在错误恢复路径上最容易被破坏？ | 第 78 章 78.6 |
| CC-105 | 5 | 流式工具执行中的「兄弟取消」要解决什么并发正确性问题？ | 第 79 章 |
| CC-106 | 6 | Claude Code 的工具并发模型如何决定哪些工具可以并行执行？ | 第 16 章 |
| CC-107 | 7 | 权限模型的分层决策链由哪几层构成？每一层能否单独否决？ | 第 80 章 |
| CC-108 | 8 | 权限规则字符串如何解析？文件系统 glob 匹配有哪些易错边界？ | 第 81 章 |
| CC-109 | 9 | BashTool 为什么要做 AST 级子命令拆分？只做字符串黑名单会漏掉什么？ | 第 82 章 |
| CC-110 | 10 | auto 模式的 AI 分类器如何工作？预批准域名机制的风险边界在哪里？ | 第 83 章 |
| CC-111 | 11 | 工具结果落盘与延迟加载如何降低上下文占用？代价是什么？ | 第 103 章 |
| CC-112 | 12 | 大结果格式化策略如何在信息完整性与 Token 成本之间取舍？ | 第 28 章 |
| CC-113 | 13 | Claude Code 的成本与 Token 追踪在哪些层面埋点？如何归因到具体调用？ | 第 17 章 |
| CC-114 | 14 | Claude Code 的错误处理与重试恢复分为哪几类？哪些错误不应重试？ | 第 18 章 |
| CC-115 | 15 | 系统提示词的组装、缓存与 API 注入如何配合？改动哪一部分会击穿缓存？ | 第 100 章 |
| CC-116 | 16 | thinking config 的决策依据是什么？fast mode 优化的是哪一段延迟？ | 第 101 章 |
| CC-117 | 17 | 配置系统的来源合并顺序与 schema 校验如何设计？ | 第 102 章 |
| CC-118 | 18 | 历史会话持久化与 worktree 隔离如何配合？并行会话的状态边界在哪里？ | 第 117 章 |

**这批题与现有 99 题的边界**：现有题目讲的是「产品行为与选型」，本批只讲「内部机制与不变量」。写作时不要重述 Agent Loop 是什么、权限模式有哪几种这类已覆盖内容，直接进入机制层。

- [ ] **Step 4: 验证**

```bash
python scripts/build_indexes.py && pwsh -File scripts/build_glossary.ps1 && python scripts/validate.py
```

Expected: `All checks passed.`，`117  CC  Claude Code`，Total 1781。

若报「标准化题目标题重复」，说明标题与现有题撞了，改写标题使其聚焦机制而非产品行为。

- [ ] **Step 5: 提交**

```bash
git add docs/04-products/claude-code/
git commit -m "feat: 新增 Claude Code 源码级内部机制 18 题"
```

---

### Task 5: Claude Code 源码级内部机制 后 17 题

**Files:**
- Modify: `docs/04-products/claude-code/internals.md`

**Interfaces:**
- Consumes: Task 4 产出的 `internals.md`，末尾锚点为 `cc-118`、序号 18
- Produces: 锚点 `cc-119` … `cc-135`，文件共 35 题

- [ ] **Step 1: 在文件末尾续写 CC-119 … CC-135**

序号从 19 接续。格式同 Task 4 Step 3。对照表：

| ID | 序号 | 标题 | 取材 |
|---|---:|---|---|
| CC-119 | 19 | 自动压缩链在什么条件下触发？它由哪几级组成？ | 第 19 章 |
| CC-120 | 20 | compact 的 prompt 工程如何决定保留什么、丢弃什么？ | 第 84 章 |
| CC-121 | 21 | compact 全流程的关键步骤有哪些？哪一步失败后最难恢复？ | 第 85 章 |
| CC-122 | 22 | microcompact 的双模式与 API 原生压缩有什么区别？各自适用什么场景？ | 第 86 章 |
| CC-123 | 23 | 响应式压缩 partialCompact 与整体压缩相比，优势和风险分别是什么？ | 第 87 章 |
| CC-124 | 24 | Session Memory 压缩的模板工程要解决什么问题？ | 第 88 章 |
| CC-125 | 25 | compact 的辅助机制与清理恢复负责什么？为什么需要单独设计？ | 第 89 章 |
| CC-126 | 26 | 记忆系统的召回相关性如何计算？写入互斥为什么必要？ | 第 90 章 |
| CC-127 | 27 | 团队记忆同步为什么采用乐观锁？发生冲突时如何合并？ | 第 91 章 |
| CC-128 | 28 | 会话恢复时 CLAUDE.md 指令机制如何重新生效？ | 第 92 章 |
| CC-129 | 29 | 多代理隔离与 forkedAgent 的缓存共享如何兼顾？共享了什么、隔离了什么？ | 第 93 章 |
| CC-130 | 30 | AgentTool 的派生决策树如何决定是否开子代理？内置代理体现了什么设计哲学？ | 第 94 章 |
| CC-131 | 31 | 子代理结果如何回流到主会话？Swarm 的邮箱通信解决什么问题？ | 第 95 章 |
| CC-132 | 32 | Coordinator 模式的 LLM 编排与确定性编排相比，适用边界在哪里？ | 第 104 章 |
| CC-133 | 33 | Bridge 的 epoch 机制解决什么问题？多会话模式下如何避免串话？ | 第 96 章 |
| CC-134 | 34 | MCP 的传输协议与工具包装如何实现？其 OAuth 涉及哪些环节？ | 第 98–99 章 |
| CC-135 | 35 | 钩子的配置来源合并、匹配去重与异步执行如何协同？输出协议约定了什么？ | 第 113–116 章 |

压缩与记忆这一组题最容易与既有题（`context-cache.md`）撞长段落。写作前先读一遍 `docs/04-products/claude-code/context-cache.md`，确保措辞与切入点不同。

- [ ] **Step 2: 验证**

```bash
python scripts/build_indexes.py && pwsh -File scripts/build_glossary.ps1 && python scripts/validate.py
```

Expected: `All checks passed.`，`134  CC  Claude Code`，Total 1798。

若报「答案包含跨题重复长段落」，按提示的两个 ID 定位并改写后写的那一题。

- [ ] **Step 3: 提交**

```bash
git add docs/04-products/claude-code/internals.md
git commit -m "feat: 新增 Claude Code 压缩、记忆与多代理机制 17 题"
```

---

### Task 6: 重建生成物并更新 README 导航

**Files:**
- Modify: `README.md`
- Modify: `docs/README.md`
- Regenerate: `dist/anki/AgentInterview-完整题库.apkg`、`dist/anki/AgentInterview-核心100.apkg`

**Interfaces:**
- Consumes: Task 2–5 产出的全部题目；`build_indexes.py` 已在各任务中重写过统计区块

- [ ] **Step 1: 重建 Anki 卡组**

```bash
python scripts/build_anki.py
```

Expected: 在 `dist/anki/` 下重新生成两个 `.apkg`。

- [ ] **Step 2: 更新根 `README.md` 首段题量**

把 `现收录 **1,738 道问题及参考答案**` 改为 `现收录 **1,798 道问题及参考答案**`。

- [ ] **Step 3: 更新根 `README.md` 的 Anki 一节**

把 `**1,738 张卡片**` 改为 `**1,798 张卡片**`。核心 100 那一行不变。

- [ ] **Step 4: 更新根 `README.md` 的仓库结构树**

`04-products` 与 `reference` 两行改为：

```text
│  ├─ 04-products/       # OpenClaw、Claude Code、OpenCode
│  └─ reference/         # 重复题报告、术语索引与深度技术资料
```

- [ ] **Step 5: 在根 `README.md` 的「开始使用」列表追加一行**

```markdown
- [深度技术资料](docs/reference/deep-dive/README.md)
```

- [ ] **Step 6: 更新 `docs/README.md`**

「产品专题」小节追加：

```markdown
- [OpenCode](04-products/opencode/README.md)
```

「参考」小节追加：

```markdown
- [深度技术资料](reference/deep-dive/README.md)
```

- [ ] **Step 7: 最终验证**

```bash
python scripts/build_indexes.py --check && python scripts/validate.py
```

Expected: `Generated indexes are up to date.` 与 `All checks passed.`，统计表末行 Total 1798。

- [ ] **Step 8: 提交**

```bash
git add README.md docs/README.md dist/anki/
git commit -m "docs: 更新题库统计、导航与 Anki 卡组至 1798 题"
```

---

## Self-Review

**Spec coverage**

| Spec 章节 | 对应任务 |
|---|---|
| 一、文件布局 | Task 1–5 |
| 二、分类与稳定 ID | Task 2 Step 1、Task 2/3/4/5 对照表 |
| 三、来源标注 | Task 2 Step 2/4、Task 4 Step 1 |
| 四、原文收录 | Task 1 Step 1–5 |
| 五、题目选题 | Task 2 Step 6、Task 3 Step 2、Task 4 Step 3、Task 5 Step 1 |
| 六、脚本改动 | Task 2 Step 1–2 |
| 七、README 与导航 | Task 1 Step 6、Task 6 Step 2–6 |
| 八、执行顺序 | Task 1→6 顺序即为 spec 步骤 1–9 |
| 九、风险 | 已内联到各任务验证步骤 |

**发现并已修正的问题**

1. Spec 说伪链接「反引号包裹」——实际 `LOCAL_LINK_RE` 不识别反引号，必须改用全角括号。Task 1 Step 2 已改正。
2. Spec 未提到 deep-dive README 与 OpenCode 原文头部的回链依赖 Task 2 才存在的目录，会造成 Task 1 校验失败。已在 Task 1 Step 4/5 标注挂起、Task 2 Step 5 补齐。
3. 题数 60 = 13 + 12 + 18 + 17，与各任务预期 Total（1751 / 1763 / 1781 / 1798）自洽。
4. 全部 60 个 ID 连续无缺口，文件内数字递增。

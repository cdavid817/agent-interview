# 整合 Claude Code 与 OpenCode 深度技术文档

> 日期：2026-08-17

## 目标

把两份外部深度技术文档整合进 AgentInterview 题库：

- `Claude-Code-技术文档.md`（7,238 行 / 119 章，源码级逆向分析）
- `OPencode技术内幕.md`（5,852 行 / 26 章 + 4 附录，架构与运行时）

产出两部分：原文作为可引用的深度资料收录进仓库；从中提炼 60 道面试题，扩充 Claude Code 章节并新建 OpenCode 章节。

## 非目标

- 不逐章搬运两份文档的全部内容。本轮取「精简」规模，只覆盖最可迁移的工程考点。
- 不改动现有 1,738 道题的任何内容。
- 不重构 `openclaw` 章节（OpenClaw 与 OpenCode 是两个不同产品）。

## 文档位置说明

本设计文档放在仓库根的 `specs/` 而非 `docs/` 下：`validate.py` 的 `validate_local_links()` 会遍历 `docs/**/*.md` 且**不剥离代码围栏**，本文档中的示例链接（如 `references.md`）会被当作真实坏链报错。已实测确认。

## 一、文件布局

```text
docs/
├─ 04-products/
│  ├─ claude-code/
│  │  ├─ internals.md              # 新增 35 题（CC-101 … CC-135）
│  │  ├─ references.md             # 追加「源码分析资料」小节
│  │  └─ README.md                 # 由 build_indexes.py 重写
│  ├─ opencode/                    # 新章节
│  │  ├─ README.md                 # 由 build_indexes.py 重写正文
│  │  ├─ opencode-basics.md        # 13 题（OPC-001 … OPC-013）
│  │  ├─ runtime-context.md        # 12 题（OPC-014 … OPC-025）
│  │  └─ references.md
│  └─ openclaw/                    # 不动
└─ reference/
   └─ deep-dive/                   # 新目录
      ├─ README.md
      ├─ claude-code-源码技术文档.md
      └─ opencode-技术内幕.md
```

题目总数 1,738 → 1,798。

## 二、分类与稳定 ID

`scripts/taxonomy.json` 末尾追加一条：

```json
{"area": "产品专题", "title": "OpenCode", "prefix": "OPC", "path": "docs/04-products/opencode"}
```

现有 `cc-` 锚点最大为 `100`（其中一个为 `id-aliases.md` 中的历史别名），因此 Claude Code 新题从 **`CC-101`** 起，文件内数字严格递增。OpenCode 从 **`OPC-001`** 起。

题目格式沿用 `docs/00-guide/question-schema.md`：锚点 `<a id="cc-101"></a>`，标题 `### N. 题干`，紧随一行核验元数据，正文，末尾一行「相关知识点」。

## 三、来源标注

源码级题目的来源行标注为「源码分析」而非「官方资料」，与官方文档佐证的题目区分开，符合仓库「事实与方案分开」的内容原则。

`docs/04-products/claude-code/references.md` 在现有「官方核验资料」之后追加「源码分析资料（非官方）」小节，链接到 `docs/reference/deep-dive/` 下的原文，并标注：基于逆向与泄露源码整理，与官方实现可能不一致，仅供工程参考。

`docs/04-products/opencode/references.md` 同时给出官方仓库/文档链接与源码分析文档链接，标注同样的免责说明。

## 四、原文收录

两份原文正文保持原样，仅做三类必要处理：

1. **文件头追加说明块**：来源、整理日期、非官方免责、回链到对应题库章节。
2. **修复 3 处伪本地链接**（形如方括号加圆括号但并非真实链接，会让 `validate_local_links()` 误判为坏链），改为反引号包裹或全角括号，不改语义：
   - `Claude-Code-技术文档.md:1392` — GlobTool/GrepTool 那处
   - `Claude-Code-技术文档.md:2834` — 记忆索引条目示例那处
   - `OPencode技术内幕.md:1852` — 省略号占位那处
3. `OPencode技术内幕.md` 第 1、2 行为重复 H1，收录时去掉一行。

两份原文均不含 `<a id="前缀-数字"></a>` 锚点（已实测为 0 处），因此不会被 `validate_all_markdown_locations()` 误判为「题目位于未登记目录」。

`docs/reference/deep-dive/README.md` 说明这批资料的性质、适用边界，并列出两份文档入口。

## 五、题目选题

### Claude Code `internals.md`（35 题）

候选主题池 37 项，取 35 题成文，其余留作后续扩充。主要取自第 78–119 章「深度原理剖析」，辅以第 16–19、28 章：

启动延迟隐藏与时序约束；queryLoop 不变量；`tool_use`/`tool_result` 配对；流式工具执行的并发正确性与兄弟取消；工具并发模型；权限分层决策；权限规则解析与 glob 匹配；BashTool 的 AST 子命令拆分；auto 模式 AI 分类器与预批准域名；成本与 Token 追踪；错误处理与重试恢复；自动压缩链；compact 的 prompt 工程与上下文保留；compact 全流程；microcompact 双模式；响应式压缩 partialCompact；Session Memory 压缩模板；记忆召回相关性与写入互斥；团队记忆同步与乐观锁；会话恢复与 CLAUDE.md 指令机制；多代理隔离与 forkedAgent 缓存共享；AgentTool 派生决策树；子代理结果回流与 Swarm 邮箱；Coordinator 编排；Bridge epoch 与多会话；MCP 传输协议与工具包装；MCP OAuth；系统提示词组装与缓存注入；thinking config 与 fast mode；配置来源合并与 schema 校验；工具结果落盘与延迟加载；大结果格式化；钩子配置与输出协议；钩子来源合并与匹配去重；技能加载层级与插件清单；命令判别联合与斜杠解析；历史会话持久化与 worktree 隔离；autoDream 门控链。

### OpenCode `opencode-basics.md`（13 题）

设计哲学与定位；顶层架构与包依赖；CLI 命令体系；API 契约分层（Schema / Protocol / Server / Client / SDK）；配置体系；Provider 与模型目录；策略系统；插件系统与生命周期；存储与事件系统；TUI 架构；桌面与跨端 UI；认证、控制面与同步；V1 → V2 设计演进。

### OpenCode `runtime-context.md`（12 题）

V2 会话运行时总论；系统上下文代数；上下文纪元状态机；持久化提示准入与晋升；会话执行路由与运行协调器；会话运行器与 Drain 循环；提供者回合与工具结算；自动压缩与历史投影；工具系统与权限；LLM 包与协议适配器；MCP / LSP / 技能 / ACP / 命令集成；可观测性、安全与运维。

### 写作约束

- 每题必须含可验证信号（指标、验证、测试、成本、延迟等），否则 `validate.py` 报「缺少可验证指标」。
- 每题有且仅有一行「相关知识点」，且不得混入题目 ID。
- 任意 ≥100 字符的段落不得与既有题目重复，否则触发「跨题重复长段落」。
- 标准化后的标题不得与任何既有题目重复；选题需避开 `claude-code/` 现有 99 题的覆盖面，聚焦内部机制。
- 单文件不超过 50 题。
- 答案正文中的本地链接必须真实存在（`validate_local_links()` 不剥离代码围栏）。

## 六、脚本改动

`scripts/validate.py` 三处最小改动：

| 位置 | 现状 | 改为 |
|---|---|---|
| 「相关知识点混入题目 ID」前缀正则 | 列举到 `OCLAW`、`CC` | 追加 `OPC` |
| 产品题校验集合 | `{"OCLAW", "CC"}` | `{"OCLAW", "CC", "OPC"}` |
| 来源行断言 | 只认「官方资料」 | 认「官方资料」**或**「源码分析」 |

`build_indexes.py`、`build_anki.py` 均从 `taxonomy.json` 读取章节，无需改代码。

## 七、README 与导航

**根 `README.md`**

- `QUESTION_STATS` 区块由 `build_indexes.py` 重写：合计 1,738 → 1,798，新增「产品专题 / OpenCode」一行。
- 首段题量数字改为 1,798。
- 「仓库结构」树补 `opencode/` 与 `reference/deep-dive/`。
- 新增「深度技术资料」一节，指向 `docs/reference/deep-dive/README.md`，并写明非官方性质。
- Anki 一节的卡片数随重建结果更新（完整题库 1,738 → 1,798）。

**`docs/README.md`**（手工维护）：产品专题加 OpenCode，参考区加 deep-dive。

**`docs/reference/README.md`**：加 deep-dive 入口。

## 八、执行顺序

1. 建 `docs/reference/deep-dive/`，收录两份原文（加头部说明、修 3 处伪链接、去重复 H1），写 README。
2. 改 `scripts/taxonomy.json` 与 `scripts/validate.py`。
3. 建 `docs/04-products/opencode/`（README 占位 + references.md），写 25 题。
4. 写 Claude Code `internals.md` 35 题，追加 references.md 的源码分析小节。
5. `python scripts/build_indexes.py` 重建统计与章节索引。
6. `pwsh -File scripts/build_glossary.ps1` 重建术语索引。
7. `python scripts/build_anki.py` 重建两份 `.apkg`。
8. 手工更新根 `README.md`、`docs/README.md`、`docs/reference/README.md`。
9. `python scripts/build_indexes.py --check` + `python scripts/validate.py` 全绿。

## 九、风险

| 风险 | 处理 |
|---|---|
| 原文伪本地链接触发坏链校验 | 收录时反引号包裹（3 处，已定位） |
| 新增「相关知识点」跨过 5 次阈值导致术语索引失效 | 步骤 6 重建术语索引；`pwsh` 已确认可用 |
| 答案长段落与既有题重复 | 写作时逐题措辞独立；由 `validate.py` 兜底 |
| Anki 卡组与题库不同步 | 步骤 7 重建；`genanki`、`markdown` 已确认可用 |
| 标题与既有题标准化后重复 | 选题聚焦内部机制，避开现有 99 题覆盖面 |

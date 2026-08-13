# Runtime 与 Harness

> 所属章节：[Agent 核心架构](README.md)｜本文件共 **11** 题。

<a id="arc-003"></a>
### ARC-003 · 一个企业级 Agent 系统应该拆分成哪些核心模块？规划器、执行器、工具层及记忆层和评测层如何协作？（腾讯二面）

> 稳定 ID：`ARC-003`｜原题号：3

**【核心思路】**
五大件（规划器/执行器/工具层/记忆层/评测层）构成一条**闭环**：规划器拆任务 → 执行器驱动 Loop 调工具 → 结果入记忆并回灌 → 评测层打分 → 失败触发 Replanning。本质是"大脑—手脚—工具—记忆—考官"的分工。

**【深入拆解】**
- **三条流看清协作**：①**控制流**——谁触发谁（规划器→执行器→工具，评测器可回弹到规划器）；②**数据流**——结果传递（工具结果→记忆→上下文→下一轮 Prompt）；③**状态流**——任务状态机流转（Pending→Running→Success/Failed/NeedReplan）。
- **规划器与执行器的交互协议**：计划下发（子任务 + 依赖）、进度回报（每步结果）、异常上报（哪步失败、为什么）。这套协议是 Multi-Agent 的基础。
- **评测层的双重角色**：**过程评测**（每步做 Guard，比如工具参数校验、结果合理性）+ **结果评测**（终点做 Judge，判断任务是否真完成）。选型上，**结构化/可枚举结果用规则**（快、便宜、稳定），**开放式/语义结果用 LLM-as-Judge**（灵活但有成本和偏差）。
- **Replan vs Retry 的边界**（高频追问）：**计划本身错了**（工具选错、路径走不通）→ Replanning；**执行偶发失败**（超时、限流、网络抖动）→ Retry。误判会导致要么无脑重试撞墙，要么频繁重规划浪费成本。
- **记忆污染问题**：错误的中间结果一旦写入记忆，会**误导后续所有决策**。需给记忆打**可信度/来源标记**，评测失败的结果不进长期记忆。

| 层 | 输入 | 输出 | 反馈对象 | 关键机制 |
|---|---|---|---|---|
| 规划器 | 目标 + 记忆 + 评测反馈 | 子任务 DAG | → 执行器 | 分解/Replan |
| 执行器 | 子任务 + 上下文 | 工具调用 | → 工具层/记忆 | Agent Loop |
| 工具层 | 参数 | 执行结果 | → 执行器 | 幂等/超时 |
| 记忆层 | 每步结果 | 历史/上下文 | → 规划/执行 | 可信度标记 |
| 评测层 | 中间/最终结果 | 分数 + 反馈 | → 规划器 | 规则 + LLM Judge |

**相关知识点：** Agent Loop、Multi-Agent、Tool Calling、Planner、Executor、状态机、Replanning、Retry。
<a id="arc-011"></a>
### ARC-011 · Agent Runtime 包含哪些核心模块？

> 稳定 ID：`ARC-011`｜原题号：11

**【核心思路】**
Runtime 是"**运行时**"，负责一次 Agent 执行的**完整生命周期调度**。核心模块：Agent Loop 调度器、上下文管理器、工具执行器、记忆管理、状态管理、模型客户端（LLM Client）。它是 Platform（平台）中真正"跑起来"的引擎内核。

**【深入拆解】**
- **Agent Loop 调度器**：Runtime 的心脏，驱动"决策→行动→观察"循环，控制步数、终止、错误处理。
- **上下文管理器**：每一轮组装喂给模型的 Context（拼装、召回、裁剪、压缩），决定模型"看到什么"。
- **工具执行器**：解析 LLM 的 tool_call，实际执行工具，处理超时/重试/结果裁剪。
- **记忆管理**：短期（对话 buffer）+ 长期（向量库）读写。
- **状态管理**：任务状态机（Pending/Running/Success/Failed），状态外置以支持断点恢复。
- **模型客户端**：与模型网关对接，处理流式、Function Calling、Token 计数。
- **辨析**：Runtime（单次执行引擎）≠ Platform（含网关、多租户、治理的完整平台）；Runtime 是 Platform 的核心子集。

| 模块 | 职责 | 类比 |
|---|---|---|
| Agent Loop 调度器 | 驱动决策循环 | CPU |
| 上下文管理器 | 组装 Context | 内存/工作台 |
| 工具执行器 | 执行 tool_call | IO 设备 |
| 记忆管理 | 短/长期记忆 | 硬盘 |
| 状态管理 | 任务状态机 | 寄存器 |
| 模型客户端 | 对接 LLM | 网卡 |

**相关知识点：** Agent Runtime、Agent Loop、Function Calling、Executor、状态机、Retry、检索、长期记忆。
<a id="arc-012"></a>
### ARC-012 · Runtime 与 Workflow Engine 有什么区别？

> 稳定 ID：`ARC-012`｜原题号：12

**【核心思路】**
**核心区别是"谁决定执行路径"**：Workflow Engine 的路径由**人预先定义**（固定 DAG，确定性、可预测）；Agent Runtime 的路径由 **LLM 运行时动态决策**（走一步看一步，灵活、自主）。前者适合标准化流程，后者适合开放式任务，二者常结合使用。

**【深入拆解】**
- **控制权归属**：Workflow 是"**编排者写死流程，引擎照着执行**"；Runtime 是"**LLM 当场决定下一步做什么**"。这是确定性与自主性的根本分野。
- **可预测性 vs 灵活性**：Workflow 结果稳定、可测试、易审计，但遇到预期外情况就走不下去；Agent 能应对开放场景，但**行为不完全可预测**，需护栏兜底。
- **最佳实践是二者结合**：用 **Workflow 编排确定的大流程骨架**，在其中"不确定的节点"嵌入 **Agent** 处理（如"审批"节点用规则、"内容生成/理解"节点用 Agent）。这兼顾可控与智能。
- **成本/延迟**：Workflow 每步确定、无额外 LLM 调用；Agent 每步都要调用模型，慢且贵——**能用 Workflow 就别用 Agent**。

| 维度 | Workflow Engine | Agent Runtime |
|---|---|---|
| 路径决定者 | 人（预定义 DAG） | LLM（动态） |
| 可预测性 | 高 | 低（需护栏） |
| 灵活性 | 低 | 高 |
| 成本/延迟 | 低 | 高（每步调模型） |
| 适用 | 标准化流程 | 开放式任务 |
| 结合方式 | 骨架编排 | 嵌入不确定节点 |

**相关知识点：** Agent Runtime、Workflow、成本治理、Runtime、Engine、Agent Architecture。
<a id="arc-028"></a>
### ARC-028 · Harness Engineering 与 Prompt Engineering 有什么区别？

> 稳定 ID：`ARC-028`｜原题号：28

**【核心思路】**
**Prompt Engineering 优化"对模型说什么"**（单次输入的措辞、示例、格式），是**点**上的技巧；**Harness Engineering 优化"模型周围的整套工程系统"**（Agent Loop、上下文动态组装、工具、记忆、状态、护栏、可观测），是**面**上的架构。一句话：**Prompt 是喂给模型的一句话，Harness 是承载模型自主运行的整个骨架**。Agent 时代，Harness 决定上限。

**【深入拆解】**
- **作用对象**：Prompt Eng 作用于**单次调用的文本**；Harness Eng 作用于**多次调用组成的系统**（循环、状态流转、外部交互）。
- **稳定性来源**：Prompt 调得再好也是概率输出、不稳定；Harness 用**结构化约束、校验重试、护栏**把不确定性工程化为可靠系统。
- **可维护性**：Prompt 是散点、难版本化治理；Harness 是可测试、可观测、可复用的工程体系。
- **关系**：Harness ⊃ Prompt——Prompt 是 Harness 里"上下文组装"环节的一部分，而非全部。

| 维度 | Prompt Engineering | Harness Engineering |
|---|---|---|
| 粒度 | 单次输入 | 整个系统 |
| 关注 | 措辞/示例/格式 | Loop/上下文/工具/记忆/护栏 |
| 稳定性 | 概率、不稳 | 工程化、可靠 |
| 范围 | 点 | 面（含 Prompt） |

**相关知识点：** Harness Engineering、Agent Loop、Retry、Memory、Prompt Engineering、可观测性、Agent Architecture。
<a id="arc-029"></a>
### ARC-029 · 为什么 Agent 更强调 Harness 而不是 Prompt？

> 稳定 ID：`ARC-029`｜原题号：29

**【核心思路】**
因为 Agent 是**多步自主系统**，单靠一句好 Prompt 无法保证几十步都不出错——真正决定成败的是**模型周围的工程**：上下文喂什么、工具怎么调、失败怎么兜底、状态怎么恢复、行为怎么约束。**Prompt 决定单步表现的下限，Harness 决定整个任务的上限**；模型能力越强，边际收益越从"调 Prompt"转移到"建 Harness"。

**【深入拆解】**
- **多步放大效应**：单步 95% 正确，20 步连乘就崩；Harness 的校验/重试/护栏把每步"托住"。
- **模型趋同**：底座模型越来越强且趋同，差异化竞争力从 Prompt 技巧转向 **Context 工程与系统设计**。
- **可控性/合规**：企业级要的稳定、安全、可观测，只能由 Harness 提供，Prompt 给不了。

| 视角 | Prompt Engineering | Harness Engineering |
|---|---|---|
| 单步表现 | 决定下限 | — |
| 多步任务 | 连乘误差易崩 | 校验/重试逐步托住 |
| 差异化 | 模型趋同后收益递减 | 系统设计是护城河 |
| 企业诉求 | 无法保障 | 稳定/安全/可观测 |

**验证指标：** 端到端任务成功率、P95 延迟、单任务成本、人工接管率和故障恢复率。

**相关知识点：** Harness Engineering、Retry、Prompt Engineering、可观测性、故障恢复、Agent Architecture。
<a id="arc-033"></a>
### ARC-033 · RAG 在 Harness 中承担什么角色？

> 稳定 ID：`ARC-033`｜原题号：33

**【核心思路】**
RAG 在 Harness 中是**"外部知识的动态供给器"**，为 Context Engineering 提供**按需召回的相关知识**，解决模型**知识过时、不含私域数据、易幻觉**的问题。它把企业知识库/文档/记忆变成可检索的外部记忆，在每轮上下文组装时**按当前 query 精准注入**，是长期记忆召回和事实性保障的关键环节。

**【深入拆解】**
- **承担的职责**：注入私域/实时知识、作为长期记忆的召回通道、用事实抑制幻觉（[ARC-041](reliability.md#arc-041)）、缩小需要塞进上下文的信息量（[ARC-032](reliability.md#arc-032)）。
- **Coding Agent 的例外**：编码场景更多用 **Agentic Search**（grep/read）而非向量 RAG（[ARC-016](architecture.md#arc-016)），因为代码结构化、精确匹配优于语义匹配。
- **关键工程**：召回质量（chunk 切分、embedding、rerank）、权限过滤（[ARC-061](platform.md#arc-061)、[ARC-069](reliability.md#arc-069)）、实时更新。

| 职责 | 说明 |
|---|---|
| 知识供给 | 注入私域/实时/长尾知识 |
| 记忆召回 | 长期记忆的检索通道（[ARC-037](architecture.md#arc-037)） |
| 抑制幻觉 | 用外部事实兜底（[ARC-041](reliability.md#arc-041)） |
| 降 Token | 按需召回替代全量塞入（[ARC-032](reliability.md#arc-032)） |
| Coding 例外 | 代码用 Agentic Search 而非向量 RAG（[ARC-016](architecture.md#arc-016)） |

**相关知识点：** Harness Engineering、Context Engineering、RAG、Embedding、Rerank、检索、长期记忆、Memory。
<a id="arc-035"></a>
### ARC-035 · MCP 在 Harness Engineering 中如何接入？

> 稳定 ID：`ARC-035`｜原题号：35

**【核心思路】**
MCP（Model Context Protocol）是**工具/数据源的标准化接入协议**，在 Harness 中扮演"**通用工具适配层**"。Agent 作为 **MCP Client**，外部能力（数据库、文件系统、API、第三方服务）封装为 **MCP Server**，双方通过标准协议通信。接入即"**即插即用**"：新工具只要实现 MCP Server，Agent 无需改代码即可发现并调用，实现 Agent 与工具的解耦。

**【深入拆解】**
- **解决的问题**：传统每接一个工具都要定制适配，**N 个 Agent × M 个工具 = N×M 对接**；MCP 标准化后变成 **N+M**。
- **接入流程**：Harness 内置 MCP Client → 连接/发现 MCP Server → 拉取工具 Schema 注入上下文（作为可用工具描述）→ LLM 决策调用 → Client 转发给 Server 执行。
- **工程要点**：Server 权限与鉴权（[ARC-086](reliability.md#arc-086)）、工具描述质量（影响 LLM 选择）、超时/错误处理、Server 生命周期管理。
- **关联**：是 Tool Hub（[ARC-060](architecture.md#arc-060)）的标准化实现方式。

| 环节 | 说明 |
|---|---|
| 角色 | Agent = MCP Client，工具 = MCP Server |
| 核心价值 | 对接复杂度 N×M → N+M |
| 接入流程 | 发现 Server → 拉 Schema → LLM 决策 → Client 转发执行 |
| 工程要点 | Server 鉴权、工具描述质量、超时、生命周期 |

**验证指标：** 端到端任务成功率、P95 延迟、单任务成本、人工接管率和故障恢复率。

**相关知识点：** Harness Engineering、MCP、Tool Hub、权限控制、Agent Architecture。
<a id="arc-040"></a>
### ARC-040 · 如何评估 Harness Engineering 的效果？

> 稳定 ID：`ARC-040`｜原题号：40

**【核心思路】**
评估 Harness 效果看**系统级增益**：同一模型下，加了 Harness 后**任务成功率↑、幻觉率↓、稳定性↑、成本↓、可恢复性↑**。方法：固定评测集做**AB 对比**（有无某 Harness 组件），观察端到端成功率、步骤正确率、Token 成本、人工介入率、故障恢复率的变化。核心命题：**Harness 是否让"同一个模型"表现得更可靠、更省、更稳**（指标体系参见 [ARC-027](reliability.md#arc-027)）。

**【深入拆解】**
- **控制变量**：**固定模型**，只增删/替换某个 Harness 组件（如上下文压缩、重试、评测层），对比前后指标，隔离出该组件的净增益。
- **看系统级而非单点**：不是评单次输出好坏，而是评**整条链路**的成功率、稳定性、成本、可恢复性。
- **典型收益信号**：成功率↑、幻觉率↓、Token 成本↓、故障自恢复率↑、人工介入率↓。
- **方法**：离线固定评测集回归 + 在线 AB/影子对比（[ARC-076](platform.md#arc-076)）。

| 维度 | 无 Harness（裸模型） | 加 Harness |
|---|---|---|
| 任务成功率 | 低、波动 | 高、稳定 |
| 幻觉/错误 | 高 | 校验/RAG 抑制 |
| 失败恢复 | 无 | 重试/降级/断点续跑 |
| 成本 | 不可控 | 缓存/分流可控 |
| 可观测 | 黑盒 | 全链路 Trace |

**相关知识点：** Harness Engineering、Checkpoint、Retry、RAG、可观测性、幻觉治理、评测体系、成本治理。
<a id="arc-043"></a>
### ARC-043 · Harness Engineering 如何支持长任务、多轮任务和断点恢复？

> 稳定 ID：`ARC-043`｜原题号：43

**【核心思路】**
靠**状态外置 + Checkpoint + 上下文压缩 + 任务拆解**。长任务用 **Planner 拆成可跟踪的子任务/TODO** 逐步推进；每步**持久化状态快照**（[ARC-036](architecture.md#arc-036)），中断后从最近 Checkpoint **续跑**；多轮/长历史用**摘要压缩**控制上下文（[ARC-031](architecture.md#arc-031)）；关键节点可**人工介入**后继续。核心是把"一次长执行"变成"可暂停、可恢复、可续跑的分步过程"。

**【深入拆解】**
- **任务拆解**：显式 TODO 列表，完成一项存一项，天然支持断点。
- **Checkpoint**：状态 + 上下文 + 进度外置持久化，实例宕机可换机恢复。
- **上下文管理**：长任务上下文必然超窗，靠摘要压缩 + 按需召回（[ARC-030](architecture.md#arc-030)）。

| 机制 | 作用 | 关联 |
|---|---|---|
| 任务拆解 | TODO 显式化，逐项可存 | [ARC-044](frameworks.md#arc-044) |
| Checkpoint | 状态 + 上下文外置持久化 | [ARC-036](architecture.md#arc-036) |
| 上下文压缩 | 长历史摘要防超窗 | [ARC-031](architecture.md#arc-031) |
| 人工介入 | 关键节点暂停/审批后续跑 | [ARC-074](reliability.md#arc-074) |

**验证指标：** 端到端任务成功率、P95 延迟、单任务成本、人工接管率和故障恢复率。

**相关知识点：** Harness Engineering、Planner、Task Decomposition、Checkpoint、检索、故障恢复、Agent Architecture。
<a id="arc-078"></a>
### ARC-078 · 规划器和执行器为什么要拆开？

> 稳定 ID：`ARC-078`｜原题号：78

**【核心思路】**
核心理由：**关注点分离 + 独立优化 + 可控可审计**。规划是"**决定做什么**"（需强推理、全局视野、慢而贵），执行是"**具体怎么做**"（工具调用、可用小模型/规则、快而多）。拆开后：①各自用**最合适的模型/策略**（规划用大模型，执行分流）；②计划**可审计、可人工介入**；③**独立扩展**（执行可并行水平扩展）；④**失败可分层处理**（Replan vs Retry，[ARC-025](architecture.md#arc-025)）。合在一起则职责混乱、难优化、难控制。

**【深入拆解】**
- **用对模型**：规划需强推理（大模型、慢、贵），执行是工具调用（可用小模型/规则、快），分离后各取所需。
- **可审计可介入**：Planner 产出显式计划，可人工审查、修改、批准，而非黑盒一把梭。
- **独立扩展与容错**：执行可并行水平扩展；失败按层处理——执行偶发错 Retry，计划错 Replan（[ARC-025](architecture.md#arc-025)）。

| 维度 | 规划器 | 执行器 |
|---|---|---|
| 职责 | 决定做什么 | 具体怎么做 |
| 特性 | 强推理/全局/慢贵 | 工具调用/快/可并行 |
| 模型 | 大模型 | 小模型/规则 |
| 收益 | 可审计/可介入 | 可扩展/可容错 |

**验证指标：** 端到端任务成功率、P95 延迟、单任务成本、人工接管率和故障恢复率。

**相关知识点：** Tool Calling、Planner、Executor、Replanning、Retry、Agent Architecture。
<a id="arc-080"></a>
### ARC-080 · 如何设计 Agent 的任务状态机？

> 稳定 ID：`ARC-080`｜原题号：80

**【核心思路】**
定义**状态集合**（Created→Planning→Running→Waiting/Paused→Success/Failed）与**合法转移规则**，非法转移拒绝；每次转移**持久化快照**支持恢复；异常态可**回滚/Replan/人工介入**。状态机让 Agent 执行**可跟踪、可恢复、可审计、可并发调度**。核心：**用显式状态机把不确定的执行过程约束成可管理的确定流转**（同 [ARC-036](architecture.md#arc-036)）。

**【深入拆解】**
- **状态集合**：Created→Planning→Running→Waiting/Paused→Success/Failed，覆盖全生命周期。
- **转移规则**：定义合法转移，非法转移拒绝；异常态可回滚/Replan/人工介入。
- **持久化**：每次转移存快照，支撑断点恢复与并发调度（[ARC-036](architecture.md#arc-036)、[ARC-074](reliability.md#arc-074)）。

| 要素 | 设计 |
|---|---|
| 状态 | Created/Running/Waiting/Success/Failed/Paused |
| 转移 | 合法规则 + 非法拒绝 |
| 异常 | 回滚/Replan/人工 |
| 持久化 | 每步快照 → 恢复/审计 |

**验证指标：** 端到端任务成功率、P95 延迟、单任务成本、人工接管率和故障恢复率。

**相关知识点：** 状态机、Replanning、任务调度、故障恢复、Agent Architecture。

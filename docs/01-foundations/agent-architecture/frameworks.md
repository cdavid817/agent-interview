# 框架选型

> 所属章节：[Agent 核心架构](README.md)｜本文件共 **4** 题。

<a id="arc-008"></a>
### 为什么没用 LangChain、Spring AI 这些 Agent 开发框架？（豆包一面）

**【核心思路】**
不是否定框架，而是依据**控制需求、团队能力和维护成本**选型。原型或标准Agent可优先使用成熟框架；只有当现有抽象无法满足关键的状态、Context、性能或治理需求时，才下沉到LangGraph等低层Runtime或自研薄Harness。

**【深入拆解】**
- **先做能力验证**：当前LangChain高层Agent构建在LangGraph上，可获得中间件、持久化、人在环路和耐久执行能力；Spring AI更适合已有Spring技术栈的统一模型与工具集成。不能基于旧版本印象直接判定“不支持”。
- **下沉条件**：需要自定义状态迁移、严格恢复语义、特殊调度、极细Context控制或框架无法满足的性能/SLA时，才考虑直接使用低层API或自研。
- **客观评估**：在真实任务上比较完成率、Trace可解释性、P95、升级兼容、依赖风险和总维护成本；框架开销要用Profile证明，不能凭抽象层数量推断。
- **复用边界**：模型SDK、向量库、解析、Tracing等成熟组件优先复用；自研部分保持最薄，并用契约封装以便替换。
- **版本治理**：锁定依赖、阅读迁移指南、做回归与灰度。选择框架不免除安全、评测和运维责任。

| 维度 | 用框架 | 自研 Harness |
|---|---|---|
| 上手速度 | 快（原型友好） | 慢 |
| Context 控制 | 取决于抽象层，可下沉定制 | 可完全定制 |
| 可调试/可观测 | 有现成集成，仍需验证覆盖 | 自行建设 |
| 稳定性 | 受框架迭代影响 | 自主可控 |
| 性能/依赖 | 需实测和版本治理 | 代码少但维护责任大 |
| 适用 | 标准能力、快速交付 | 明确差异化且框架不满足 |

**相关知识点：** LangGraph、LangChain、Spring AI、Harness Engineering、Agent Runtime、可观测性、可靠性、评测体系。
<a id="arc-009"></a>
### LangChain 和 LangGraph 的区别以及各自适用场景（Agent 初级）

**【核心思路】**
当前 LangChain 是构建 Agent 和 LLM 应用的**高层框架**，其 `create_agent` 本身构建在 LangGraph 之上；LangGraph 是面向长运行、有状态工作流的**低层编排 Runtime**。区别不是“LangChain 只能线性、LangGraph 才能做 Agent”，而是**抽象层级与控制粒度**。

**【深入拆解】**
- **LangChain**：提供模型、工具、中间件、消息和预构建 Agent 等高层接口，适合希望快速构建标准工具调用 Agent 的团队；它可通过底层 LangGraph 获得持久化、流式、人在环路和耐久执行能力。
- **LangGraph**：直接暴露 State、Node、Edge、Reducer、Checkpoint 和 Interrupt，适合需要自定义循环、分支、恢复、并行和多 Agent 协调的复杂流程。
- **简单流程**：普通 RAG、固定转换仍可用 Runnable/LCEL 或普通代码，不必为了“图”而增加状态复杂度。
- **选型**：优先用 LangChain 高层 Agent；只有需要精确控制状态迁移、执行顺序或恢复语义时再下沉 LangGraph。二者可以同时使用，不是互斥替代关系。

| 维度 | LangChain | LangGraph |
|---|---|---|
| 定位 | 高层 Agent/LLM 应用框架 | 低层状态化编排 Runtime |
| 控制粒度 | 预构建抽象与中间件 | 显式 State、Node、Edge |
| 耐久执行 | Agent 可继承 LangGraph 能力 | 直接配置 Checkpoint/Interrupt |
| 适用 | 快速构建标准 Agent | 深度定制复杂长流程 |

**官方资料：** [LangChain Overview](https://docs.langchain.com/oss/python/langchain/overview)、[LangGraph Overview](https://docs.langchain.com/oss/python/langgraph/overview)。

**验证指标：** 端到端任务成功率、P95 延迟、单任务成本、人工接管率和故障恢复率。

**相关知识点：** LangGraph、LangChain、Agent Runtime、Multi-Agent、Tool Calling、Workflow、Checkpoint、RAG。
<a id="arc-015"></a>
### LangGraph、AutoGen、CrewAI 等框架分别适合哪些场景？

**【核心思路】**
**LangGraph**：底层状态机图，精细控制、生产级，适合需要复杂控制流/断点/人在环路的严肃 Agent。**AutoGen**（微软）：**对话驱动**的多 Agent（Group Chat），适合研究型、探索型的多角色协作。**CrewAI**：**角色化流程**（Role/Task/Crew）抽象，上手快，适合快速搭建结构清晰的分工流水线。

**【深入拆解】**
- **LangGraph**：把 Agent 建成显式状态图，控制粒度最细，支持循环/条件/Checkpoint/人工介入。**灵活但要写更多代码**，适合对稳定性和可控性要求高的生产系统。
- **AutoGen**：核心抽象是"**会话中的多个 Agent 互相对话**"（如 UserProxy + Assistant + GroupChatManager）。适合让多个角色**自由讨论/协作**解决开放问题，研究气质强，编排相对松散。
- **CrewAI**：核心抽象是 **Crew（团队）+ Agent（角色）+ Task（任务）+ Process（流程）**，声明式定义"谁干什么、按什么顺序"。**上手最快、心智模型直观**，但灵活性和底层控制不如 LangGraph。
- **选型**：要**精细控制/生产可靠** → LangGraph；要**多角色自由协作/研究** → AutoGen；要**快速搭建清晰分工的业务流水线** → CrewAI。

| 框架 | 核心抽象 | 控制粒度 | 上手 | 最适场景 |
|---|---|---|---|---|
| LangGraph | 状态机图 | 细（底层） | 中 | 生产级复杂 Agent |
| AutoGen | 多 Agent 对话 | 中 | 中 | 研究/多角色协作 |
| CrewAI | Role/Task/Crew | 粗（高层） | 快 | 快速搭分工流水线 |

**验证指标：** 端到端任务成功率、P95 延迟、单任务成本、人工接管率和故障恢复率。

**相关知识点：** LangGraph、AutoGen、CrewAI、Multi-Agent、状态机、Checkpoint、Agent Architecture。
<a id="arc-044"></a>
### 如何结合 Reflection、ReAct、Plan-and-Execute 等模式构建执行框架？

**【核心思路】**
分层组合：**顶层用 Plan-and-Execute** 做全局规划（拆解 TODO，减少漂移、省 Token）；**每个子任务内用 ReAct** 循环（推理-行动-观察，处理不确定）；**失败或质量不达标时用 Reflection** 自我反思纠错后重试。即"**Plan 定方向、ReAct 干活、Reflection 纠错**"的三层执行框架，兼顾全局可控与局部灵活。

**【深入拆解】**
- **为什么组合**：单 ReAct 易漂移/循环；单 Plan 不够灵活应对意外；Reflection 补纠错。三者互补。
- **组合结构**：Plan（全局 DAG/TODO）→ 每节点 ReAct 执行 → 节点失败 Reflect 后 Retry/Replan（[ARC-025](architecture.md#arc-025)）。
- **进阶**：高难决策可引入 ToT/LATS 树搜索。

| 层次 | 模式 | 职责 |
|---|---|---|
| 顶层 | Plan-and-Execute | 全局规划、定方向、减漂移 |
| 中层 | ReAct | 子任务内推理-行动-观察 |
| 纠错 | Reflection | 失败后自我反思再重试 |
| 进阶 | ToT/LATS | 高难任务多路径树搜索 |

**相关知识点：** Replanning、Retry、Reflection、ReAct、成本治理、Agent Architecture。

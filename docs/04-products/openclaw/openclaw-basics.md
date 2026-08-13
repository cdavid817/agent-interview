# OpenClaw 综合

> 所属章节：[OpenClaw](README.md)｜本文件共 **19** 题。

<a id="oclaw-011"></a>
### 1. OpenClaw 的 Sandbox 隔离了什么？没有隔离什么？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

Sandbox主要隔离**工具执行**，包括`exec`、文件读写、Patch、Process及可选浏览器；Gateway本身仍在宿主机运行。可按Agent、Session或共享范围创建环境，并选择Docker、SSH或OpenShell等后端。

`workspaceAccess`决定工作区不可见、只读或可写，网络和额外挂载也需单独限制。Elevated工具可能绕过沙箱，所以沙箱不是单独充分的安全边界。生产中还应限制宿主凭据、容器Socket、设备文件和出口网络，并用恶意路径、符号链接和Prompt Injection测试验证。

**相关知识点：** Sandbox Backend、Workspace Access、Filesystem Isolation、Network Egress、Elevated Mode、纵深防御。
<a id="oclaw-012"></a>
### 2. Exec Approval、Elevated Mode 和真正的系统授权有什么区别？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

Exec Approval是**人机交互护栏**，Elevated Mode是**允许命令脱离工具沙箱执行的逃生路径**，系统授权则由OS、容器、云IAM和目标服务ACL强制。

批准一条命令不应自动授予宽泛后续权限；Elevated来源应严格限制并记录主体、命令、目标和结果。即使模型或用户文本声称“已批准”，宿主仍必须检查实际身份与策略。不可逆、外发或高价值操作还需二次确认、幂等键和业务后置校验。

**验证指标：** 任务完成率、工具调用成功率、P95 延迟、Token 消耗和人工接管率。

**相关知识点：** Human Approval、Elevated Exec、IAM、ACL、Least Privilege、审计、后置校验。
<a id="oclaw-027"></a>
### 3. 如何建立 OpenClaw 的可观测性和故障排查路径？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

先按**入口—路由—会话—模型—工具—任务—交付**建立关联链。请求应携带Channel、Agent、Session、Run和Task标识，记录模型路由、工具状态、时延、Token、审批和Delivery Receipt。

排障通常从`status`、Gateway健康、渠道连接、日志和`doctor`开始，再检查Effective Config、模型认证、Tool Policy、Sandbox和目标渠道。敏感Prompt、媒体和凭据不得进入普通日志。指标至少包含请求与交付成功率、P95、队列深度、模型Fallback、工具失败、Token和单位成功成本。

**相关知识点：** Health Check、Doctor、Structured Log、Correlation ID、Metrics、Delivery Observability。
<a id="oclaw-028"></a>
### 4. OpenClaw 如何做备份、恢复和灾难演练？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

先区分可重建配置、Agent工作区、Memory、会话记录、任务状态、渠道凭据和Plugin数据。备份应加密、版本化并测试恢复，Secret可通过外部密钥系统重新签发，而不是长期复制明文。

恢复后校验文件权限、Schema迁移、渠道连接、会话归属、未完成任务和重复交付风险。外部副作用不能靠恢复本地文件撤销，要用幂等键、查账与补偿。定期演练主机丢失、配置损坏、Provider不可用和凭据泄漏，并记录RPO、RTO和人工步骤。

**相关知识点：** Backup、Restore Drill、RPO、RTO、Key Rotation、幂等恢复、补偿。
<a id="oclaw-031"></a>
### 5. OpenClaw 设计方案（附加专题）

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

**【核心思路】**
OpenClaw 官方定位是**运行在自有设备上的开源个人 AI 助手与协调层**：以常驻 Gateway 连接消息渠道、模型、会话、Memory、Skills、工具和设备节点。它不是 IDE 或 Claude Code/Codex 的直接替代品；直接仓库编码可交给专门 Coding Harness，OpenClaw 更适合跨渠道、跨设备和长期任务协调。

**【深入拆解】**
- **控制面**：Gateway 负责渠道接入、会话路由、模型与工具运行；当前官方架构中 Agent Loop、工具和推理运行在单机 Gateway 进程内。
- **状态与记忆**：会话状态保存在本地；长期记忆以工作区中的 `MEMORY.md` 和每日 `memory/YYYY-MM-DD.md` 为主，可配置语义检索与压缩前Memory Flush。
- **多 Agent**：可在同一 Gateway 配置多个具有独立工作区、Agent目录和会话存储的Agent，并用Bindings按渠道、账号或对话路由；子Agent是独立后台会话。
- **模型**：支持多Provider、按Agent或任务指定模型，以及配置主模型与Fallback；这不等同于自动按复杂度学习路由。
- **能力扩展**：Skills、Plugins、Tools、Nodes以及MCP承担不同扩展角色；MCP既可让OpenClaw作为Server暴露渠道会话，也可管理外部MCP Server定义。
- **安全边界**：官方安全模型是一名可信操作者对应一个Gateway信任边界。互不信任的用户应拆分Gateway、OS用户或主机，不能把同一Gateway当作敌对多租户隔离。

> 事实口径以官方文档为准；云工作节点页面明确标注为“Proposal, Not implemented”，不能据此声称已支持分布式无状态集群。
| 模型网关 | 切换 + 熔断降级 | 稳定性 |

**验证指标：** 任务完成率、工具调用成功率、P95 延迟、Token 消耗和人工接管率。

**相关知识点：** OpenClaw、Claude Code、Harness Engineering、Agent Loop、Multi-Agent、MCP、Skill、检索。
<a id="oclaw-033"></a>
### 6. OpenClaw 如何实现长任务执行？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

**【核心思路】**
当前可用机制包括后台任务、子Agent独立会话、Cron/Heartbeat、会话持久化和上下文压缩。长或并行工作可交给子Agent，完成后回传摘要，避免阻塞主会话；定时任务由常驻Gateway调度。

需要注意：官方没有承诺“每个步骤事务化Checkpoint并可精确续跑”。Gateway重启可能丢失尚未投递的子Agent完成通知，云Worker也仍是未实现提案。高可靠长任务应由外层工作流保存任务ID、幂等键、阶段Artifact和验收状态。

**验证指标：** 任务完成率、工具调用成功率、P95 延迟、Token 消耗和人工接管率。

**相关知识点：** OpenClaw、Workflow、Checkpoint、任务调度、Agent Runtime。
<a id="oclaw-034"></a>
### 7. OpenClaw 的 Agent Loop 如何设计？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

**【核心思路】**
官方架构中一次Agent Run在Gateway进程内完成模型调用、工具执行和结果回灌。可以用“模型决策→工具调用→观察→继续或回复”理解，但不应断言内部固定采用某一种公开的ReAct Prompt或独立Planner。

工程关注点是有效工具策略、运行超时、上下文压缩、不可信工具输出、停止条件和可见的最终结果。若通过ACP托管外部Coding Harness，其循环与恢复语义由对应Harness决定，不应混入OpenClaw原生Loop描述。

**验证指标：** 任务完成率、工具调用成功率、P95 延迟、Token 消耗和人工接管率。

**相关知识点：** OpenClaw、Harness Engineering、Agent Loop、Tool Calling、Planner、ReAct、Prompt Engineering、故障恢复。
<a id="oclaw-038"></a>
### 8. OpenClaw 中的 Planner 如何实现？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

**【核心思路】**
官方文档没有把OpenClaw描述为固定的“独立Planner服务+TODO DAG”架构。任务拆解通常由所选模型、系统指令、Skill或外部Harness完成；子Agent工具可以执行明确的委派。

若企业需要可审计规划，应在应用层把目标、依赖、负责人、验收和预算写成结构化任务，并由Gateway会话或外部工作流驱动。该方案属于扩展设计，不应冒充OpenClaw默认内部实现。

**验证指标：** 任务完成率、工具调用成功率、P95 延迟、Token 消耗和人工接管率。

**相关知识点：** OpenClaw、Harness Engineering、Skill、Workflow、Planner、Task Decomposition。
<a id="oclaw-039"></a>
### 9. OpenClaw 如何做任务拆解？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

**【核心思路】**
OpenClaw可由主Agent把独立研究或慢任务委派给子Agent，但官方没有规定统一DAG算法。可靠做法是把复杂任务拆成输入清楚、输出可交付、权限有限且能独立验证的子任务，并限制并发和嵌套深度。

强依赖步骤留在同一会话顺序执行；并行任务通过Artifact而非共享隐式上下文交接。拆解质量用完成率、冲突率、重复工作和单位成功成本验证。

**相关知识点：** OpenClaw、Task Decomposition、权限控制、成本治理、任务调度。
<a id="oclaw-043"></a>
### 10. OpenClaw 如何实现任务 Checkpoint 恢复？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

**【核心思路】**
OpenClaw会持久化会话和本地状态，也支持压缩与Memory，但这不等同于每一步具有事务化Checkpoint和Exactly-once恢复。子Agent完成通知在Gateway重启场景也可能丢失。

需要强恢复语义时，应由外层任务系统保存阶段状态、输入hash、Artifact、幂等键和后置条件；恢复前验证资源是否已改变，再决定重放、补偿或人工接管。不要把建议方案描述成OpenClaw当前保证。

**相关知识点：** OpenClaw、Checkpoint、Memory、故障恢复、Agent Runtime。
<a id="oclaw-044"></a>
### 11. OpenClaw 如何保证 Agent 执行稳定性？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

**【核心思路】**
官方运维能力包括`status`、`health`、`logs`、`doctor`、模型Fallback以及任务/子Agent检查。工具策略、Sandbox、渠道Allowlist和资源限制用于缩小故障与误操作影响。

稳定性仍需外部SLO、超时、并发上限、幂等、依赖监控和故障演练。模型Fallback只覆盖符合条件的模型/认证故障，不能替代工具、渠道或业务错误处理。

**相关知识点：** OpenClaw、Sandbox、可靠性、任务调度、Agent Runtime。
<a id="oclaw-046"></a>
### 12. OpenClaw 如何设计 Agent 状态机？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

**【核心思路】**
OpenClaw确实维护会话、后台任务、子Agent和路由状态，但官方没有将其描述为用户可配置的通用业务状态机。

若业务需要Created、Running、WaitingApproval、Succeeded、Failed等严格状态，应由外部Workflow或Plugin持久化合法转移、版本和幂等键，OpenClaw只作为交互与执行入口。这样可避免把内部会话状态误当作业务事务状态。

**验证指标：** 任务完成率、工具调用成功率、P95 延迟、Token 消耗和人工接管率。

**相关知识点：** OpenClaw、Workflow、状态机、Running、WaitingApproval。
<a id="oclaw-047"></a>
### 13. OpenClaw 如何做任务完成率评估？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

**【核心思路】**
OpenClaw官方没有定义适用于所有任务的内建“完成率”。应由场景Owner建立有效任务分母和Acceptance Criteria：消息发送看目标渠道状态，定时任务看实际交付，研究任务看引用和人工Rubric，ACP编码任务看Patch、编译和测试。

报告Strict/Partial完成率、人工接管、重试、P95和单位成功成本，并关联OpenClaw、模型、Skill和工具版本。不能用模型的最终文本或单次工具成功代替任务完成。

**相关知识点：** OpenClaw、Skill、Retry、评测体系、成本治理。
<a id="oclaw-048"></a>
### 14. OpenClaw 如何实现 Workflow 编排？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

**【核心思路】**
OpenClaw提供Cron、Heartbeat、Hooks、Skills、会话和子Agent等自动化组件，但不应据此声称它等同于完整BPMN或耐久工作流引擎。

确定性的审批、事务、补偿和Exactly-once调度应放在专业Workflow系统；OpenClaw负责自然语言交互、非确定性判断和工具调用。二者通过任务ID、回调、Artifact和幂等接口衔接。

**验证指标：** 任务完成率、工具调用成功率、P95 延迟、Token 消耗和人工接管率。

**相关知识点：** OpenClaw、Tool Calling、Skill、Workflow、任务调度。
<a id="oclaw-050"></a>
### 15. OpenClaw 如何降低 Token 消耗？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

**【核心思路】**
优先使用会话压缩、Memory按需检索、精简工具与Skill、裁剪长工具输出，并让隔离子Agent只接收完成任务所需的上下文。不同Agent和Cron任务可配置更便宜模型，但工具型不可信输入不应为降本而使用明显不足的模型。

监控输入、输出、缓存、工具返回和子AgentToken，以及每个成功任务的总成本。官方文档未保证所有Provider都具备相同的前缀缓存或计费行为，应以Provider账单和实测为准。

**相关知识点：** OpenClaw、Skill、检索、Memory、成本治理。
<a id="oclaw-051"></a>
### 16. OpenClaw 在企业级生产环境如何落地？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

**【核心思路】**
先接受其官方信任模型：一个Gateway对应一个可信操作者边界；互不信任的员工、客户或租户应拆分OS用户、主机和Gateway。再配置渠道配对/Allowlist、工具Policy、Sandbox、最小文件和网络权限及短期凭据。

明确消息平台、模型Provider和Embedding Provider的数据流、区域与保留；上线前做红队、备份恢复、升级回滚和事件响应。企业Prompt发布、集中审计、SLO和成本分摊通常需要外部平台补齐。

**相关知识点：** OpenClaw、Embedding、Prompt Engineering、权限控制、多租户、Sandbox、可靠性、成本治理。
<a id="oclaw-052"></a>
### 17. OpenClaw 如何实现 Agent 可观测性建设？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

**【核心思路】**
内建入口包括`openclaw status`、`gateway status`、`health`、`logs`、`doctor`以及任务/子Agent检查，可观察Gateway、渠道、Provider、会话和运行故障。

企业扩展应把请求ID贯穿渠道、会话、模型和工具，记录工具名、参数摘要、结果状态、时延、Token、路由和审批；敏感Prompt与媒体需脱敏和分级保留。记录决策摘要与外部证据即可，不应把不可验证的隐藏思维链当审计事实。

**相关知识点：** OpenClaw、Chain-of-Thought、Prompt Engineering、可观测性、成本治理。
<a id="oclaw-053"></a>
### 18. OpenClaw 如何进行 Agent 性能优化？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

**【核心思路】**
先用Trace拆分渠道、排队、模型首Token、工具和交付耗时，再优化关键路径。可减少无关工具与上下文、给独立子Agent设置并发上限、按任务选模型，并缓存稳定的外部查询结果。

当前原生Agent会话共享Gateway进程资源，增加并发可能造成竞争；不能按“无状态Runtime可无限水平扩展”估算容量。应压测目标硬件并设置SLO、限流、超时和资源隔离。

**相关知识点：** OpenClaw、Agent Runtime、可观测性、可靠性、成本治理、任务调度。
<a id="oclaw-054"></a>
### 19. OpenClaw 如何设计多模型调度策略？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

**【核心思路】**
当前可按Agent设置默认模型、按Cron任务覆盖模型、给子Agent指定模型，并允许用户用`/model`切换；Primary/Fallback负责故障切换。这是配置式路由，不等同于内建的自动难度分类或在线Bandit。

需要自适应调度时，可在外层按任务、风险和成本选择目标Agent/模型，并以完成率和安全门槛验证。具备文件、网络或不可信内容工具的Agent不宜仅为省钱路由到抗注入能力不足的模型。

**相关知识点：** OpenClaw、成本治理、模型路由、任务调度、Agent Runtime。

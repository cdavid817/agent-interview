# 架构、Gateway 与 Runtime

> 所属章节：[OpenClaw](README.md)｜本文件共 **7** 题。

<a id="oclaw-001"></a>
### 1. OpenClaw 的产品定位是什么？它与普通聊天机器人有什么区别？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

OpenClaw 是运行在自有设备或服务器上的**自托管 Agent Gateway 与个人助手运行时**。它把消息渠道、模型、会话、记忆、工具、Skills、Plugins、自动化任务和设备节点连接到一个常驻控制面，而不只是提供一次请求—一次回答的聊天接口。

与普通机器人相比，它能保留跨渠道会话、调用本地或远程工具、执行后台任务并主动交付结果。它也不是天然的企业工作流引擎或专用 Coding Agent；确定性事务可交给工作流系统，仓库编码可通过 ACP 或专门 Harness 执行。

**验证指标：** 任务完成率、工具调用成功率、P95 延迟、Token 消耗和人工接管率。

**相关知识点：** Self-hosted、Gateway、Agent Runtime、渠道适配、个人助手、ACP、控制面。
<a id="oclaw-002"></a>
### 2. OpenClaw Gateway 在整体架构中承担什么职责？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

Gateway 是 OpenClaw 的**常驻控制面和连接中枢**，负责接受渠道与客户端连接、解析路由、管理会话、启动 Agent Run、调度后台任务并把结果交付回目标渠道。

1. 控制流通过 Gateway 统一进入，渠道凭据、Agent Binding、会话键和回复路由在这里汇合。
2. 内置 Agent Loop通常在Gateway进程内运行；沙箱只把符合配置的工具执行移到隔离环境，不等于把整个Gateway放入沙箱。
3. Gateway故障会影响多个Agent和渠道，因此需要健康检查、日志、配置校验、备份和进程守护。
4. 不可信租户不应只靠会话隔离共用同一Gateway，强信任边界应拆到OS用户、主机或独立Gateway。

**验证指标：** 任务完成率、工具调用成功率、P95 延迟、Token 消耗和人工接管率。

**相关知识点：** WebSocket Gateway、控制面、会话路由、故障域、进程守护、信任边界。
<a id="oclaw-003"></a>
### 3. OpenClaw 内置 Agent Runtime 的一次执行循环是怎样的？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

一次Run可概括为**组装上下文—调用模型—执行工具—回灌结果—继续或结束—交付回复**。模型决定是否请求工具，Runtime负责校验可见工具、执行并把Observation加入后续轮次。

上下文包含系统指令、工作区引导文件、会话历史、按需记忆、Skill说明和工具Schema。流式文本、工具事件与最终回复有不同生命周期；等待外部结果时还要处理超时、取消和运行期Steering。官方没有保证所有任务都先生成固定DAG，因此不能把模型的动态循环描述成内建Planner服务。

**验证指标：** 任务完成率、工具调用成功率、P95 延迟、Token 消耗和人工接管率。

**相关知识点：** Agent Loop、Prompt Assembly、Tool Calling、Observation、Streaming、Steering、停止条件。
<a id="oclaw-005"></a>
### 4. 为什么 OpenClaw 为每个 Agent 设置独立工作区？工作区中通常放什么？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

工作区同时是Agent的**可操作目录和持久上下文载体**。独立工作区能隔离身份、规则、记忆、Skills和产物，避免多个Agent无意共享文件。

工作区通常包含`AGENTS.md`、`SOUL.md`、`IDENTITY.md`、`USER.md`、`TOOLS.md`、`MEMORY.md`、每日记忆目录及项目文件。不同文件承担规则、人格、用户偏好、工具说明和长期事实等职责。应把可恢复文件纳入受控备份或版本管理，但密钥、会话令牌和敏感原始记录不能直接提交Git。

**验证指标：** 任务完成率、工具调用成功率、P95 延迟、Token 消耗和人工接管率。

**相关知识点：** Agent Workspace、Bootstrap Files、身份隔离、配置即代码、备份、Secret Management。
<a id="oclaw-020"></a>
### 5. OpenClaw 的后台任务如何避免“运行了但用户没收到结果”？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

任务完成与结果交付是两个状态，必须分别记录。后台任务应保存Task ID、Owner、来源会话、状态、结果Artifact、预期渠道和Delivery Receipt。

执行成功后按解析出的路由发送，失败要重试、降级或进入待处理队列；重试使用幂等键，避免同一消息重复外发。Gateway重启后应能查询未完成或未交付任务，关键业务不能只依赖一次Best-effort Announce。监控完成率、交付率、重复率、P95和积压年龄。

**相关知识点：** Background Task、Delivery Receipt、Outbox、Idempotency、Dead Letter、任务与交付分离。
<a id="oclaw-029"></a>
### 6. OpenClaw 是否适合直接作为多租户 SaaS 的共享 Runtime？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

默认信任模型更适合**单一可信操作者边界**，不应把Agent或Session配置当作敌对租户的强隔离。共享Gateway会共享进程故障域，并可能通过文件、凭据、Session Tool、Plugin或缓存形成越权路径。

若提供SaaS，应按租户或信任域拆分容器/VM、OS身份、Gateway、存储、密钥和网络策略，控制资源配额并验证删除与审计。外层控制面负责身份、计费、调度和生命周期。是否共享模型网关可另行决策，但数据和工具授权必须保持租户上下文。

**相关知识点：** Multi-tenancy、Trust Domain、Process Isolation、Tenant Context、Quota、Data Residency。
<a id="oclaw-032"></a>
### 7. OpenClaw 与 Claude Code 的架构差异是什么？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

**【核心思路】**
两者不是同类产品。OpenClaw 是**自托管、常驻的个人助手控制面**，通过 Gateway 连接消息渠道、会话、Memory、Skills、工具和设备，并支持多个模型Provider。Claude Code是面向代码仓库的专用Coding Agent，核心交互围绕读取、修改和验证代码。

OpenClaw官方建议直接仓库编码使用Claude Code或Codex，而用OpenClaw承担持久记忆、跨设备入口和工具协调。若需在OpenClaw中托管编码Harness，应走其ACP等明确接口，不能把通用文件/Bash能力等同于内建的完整Coding Agent能力。

**相关知识点：** OpenClaw、Claude Code、Harness Engineering、Skill、Memory、Coding Agent。

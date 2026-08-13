# 故障恢复与事件响应

> 所属章节：[安全、治理与可观测性](README.md)｜本文件共 **17** 题。

<a id="gov-013"></a>
### GOV-013 · Agent服务如何高可用部署？（豆包一面）

> 稳定 ID：`GOV-013`｜原题号：13

Agent高可用的核心是**无状态计算、持久化状态、依赖隔离、幂等恢复和降级**。多Pod不能解决模型、工具、队列或存储故障，须按任务语义恢复。

1. API、Planner和Executor无状态跨区部署；Task、Event、Checkpoint、幂等键和租约写入高可用存储。实例故障后其他Worker获取过期租约并续作。
2. 任务由持久队列解耦，设置可见性超时、重试预算、死信队列和背压。At-Least-Once下，写操作须有业务幂等键；状态未知先查询。
3. 模型、RAG、MCP和Tool分别设置Deadline、限流、舱壁、熔断与健康探测。Gateway维护兼容备用；能力不足时降级为只读、排队或人工。
4. 数据层备份、跨区复制并演练恢复，定义RPO/RTO；配置、Prompt、模型和工作流版本化可回滚。发布先Canary并保证Schema兼容。
5. 监控完成率、队列、租约超时、模型/工具错误、P95、重复副作用和恢复率。故障注入覆盖实例、区域、供应商与慢依赖，并预留N+1容量。

| 层次 | 高可用机制 |
|---|---|
| 计算 | 多副本、跨区、无状态 |
| 状态 | Event、Checkpoint、高可用存储 |
| 依赖 | 限流、熔断、舱壁、备用 |
| 恢复 | 幂等、租约、RPO/RTO演练 |

**相关知识点：** High Availability、Checkpoint、Lease、At-Least-Once、幂等、Circuit Breaker、RPO、RTO、Canary、N+1。
<a id="gov-045"></a>
### GOV-045 · Tool调用失败如何定位原因？

> 稳定 ID：`GOV-045`｜原题号：45

Tool失败定位应区分**参数、权限、传输、执行、外部依赖和解析**阶段，查找首个异常证据；最终错误通常不是根因。

1. 由TraceID进入Tool Span，核对Tool、SchemaVersion、StepID、Attempt、超时、幂等键、参数摘要、PolicyDecision、外部RequestID、状态码、错误码和耗时。
2. 调用前检查参数的JSON Schema、类型、范围及业务前置条件；确认工具与版本路由正确。参数合法但被拒绝时，查看身份、Scope、资源属性和Policy版本。
3. 调用中区分DNS、连接、TLS、限流、超时、熔断、服务异常及资源冲突；结合外部RequestID查询服务日志，不能依据504断定执行失败。
4. 调用后校验响应Schema、状态码、截断、解码和业务成功字段。传输成功但业务失败属于Tool错误；业务成功但解析失败属于Adapter错误。
5. 有副作用的超时先以幂等键或查询接口确认执行状态，再决定重试；保存请求Hash与回执，在隔离环境用同版本复现。

错误统一标注Stage、Owner、Retryable和RootCause，监控分阶段失败率及P95耗时；修复后增加Contract Test和回归样本。

**相关知识点：** Tool Span、JSON Schema、Error Taxonomy、幂等键、超时歧义、Contract Test、熔断、外部RequestID。
<a id="gov-047"></a>
### GOV-047 · 工具超时和重试如何记录？

> 稳定 ID：`GOV-047`｜原题号：47

工具超时与重试应按**一次逻辑调用、多个Attempt**建模，以OperationID聚合，每次尝试建立独立Span，从而识别额外延迟、成本和副作用。

1. 逻辑调用记录TaskID、OperationID、Tool版本、参数Hash、幂等键、总Deadline和重试策略；Attempt记录序号、Span、Endpoint、起止时间及剩余预算。
2. 区分排队、连接、读写、服务端Deadline和客户端取消，记录阈值、实际耗时、取消是否送达、外部RequestID及错误码。
3. 重试记录触发原因、Retryable判断、退避、实际等待、Jitter、熔断状态、路由变化和结果；不得覆盖前次错误。
4. 写操作记录资源版本、请求Hash和幂等响应。超时且结果未知时先查询状态，标为Succeeded、Failed或Unknown，再决定重试。
5. 统计Attempt/Operation、超时率、首试与重试成功率、额外延迟、成本和重复副作用，并按Tool、错误类型与版本切片。

错误与高风险调用不得采样。告警针对超时率、Unknown积压、重试风暴和Deadline耗尽，受控重试不应全部视为故障。

**相关知识点：** OperationID、Attempt、Deadline、Timeout Taxonomy、Exponential Backoff、Jitter、幂等、Retry Amplification。
<a id="gov-050"></a>
> **题目合并：** `GOV-050` 已并入 [TOOL-113 · 工具调用失败如何自动恢复？](../../02-capabilities/tools-skills-mcp/sandbox-security-1.md#tool-113)。

<a id="gov-066"></a>
### GOV-066 · 如何基于链路数据实现自动调优闭环？

> 稳定 ID：`GOV-066`｜原题号：66

自动调优采用**观测—诊断—候选—验证—灰度—回滚**闭环，只在预定义安全边界内调整；链路相关性不能证明因果。

1. 从Trace提取完成率、质量、P95、Token、成本、重试、接管和安全违规，按TaskType、模型、Prompt、工具及版本建立基线，识别关键路径。
2. 规则和统计模型将异常归因到上下文、模型路由、RAG Chunk、串行分支、慢Tool或重试风暴；LLM生成候选时必须引用Span证据。
3. 候选仅限Prompt参数、上下文预算、TopK、缓存、并发、Timeout、模型路由和重试等可逆配置；不得放宽权限、审批与安全阈值。
4. 在回归集、历史Trace回放和影子流量中验证，以完成率为主指标，事实性、安全、P95和Cost/Success为护栏；通过统计检查才进入Canary。
5. 灰度实时比较SLO和Error Budget，超阈值回滚，达观察窗口后扩量。保存ExperimentID、配置Diff、流量、指标和结果，避免实验污染。

限制变更频率、幅度、预算和冷却时间，并保留Kill Switch；失败实验回流规则库与评测集，监控数据漂移。

**相关知识点：** Closed-loop Optimization、Critical Path、Causal Experiment、Offline Replay、Shadow Traffic、Canary、Guardrail Metric、自动回滚。
<a id="gov-076"></a>
### GOV-076 · 打断后如何从断点恢复执行？

> 稳定 ID：`GOV-076`｜原题号：76

断点恢复应以**Checkpoint、幂等状态机和副作用对账**为基础，只执行未完成且仍满足条件的节点，不能从最后一条日志直接继续。

1. 在Tool完成、人工等待和并行汇聚等安全点保存Checkpoint，包含TaskID、DAGVersion、节点状态、Sequence、未决Operation、幂等键和资源版本。
2. Worker以CAS获取Task Lease，校验Checkpoint Hash与Event Sequence，重建状态机并回放后续事件，防止并发恢复和旧快照覆盖。
3. 对UNKNOWN节点通过JobID、RequestID或幂等键查询。已成功则补写回执，明确失败才重试，无法确认则暂停转人工。
4. 恢复前重验身份、授权、审批、Policy、数据和资源版本；条件变化时生成新DAGVersion并记录Diff，必要时重审。
5. 仅将依赖满足的节点置为READY，已验收节点不再执行；消费者按EventID去重，重试遵守Deadline与Retry Budget，不可逆失败进入Saga。

恢复生成新Attempt或Trace并链接原Task，记录Checkpoint、对账、版本变化和结果；监控恢复率、重复副作用、租约冲突及耗时。

**相关知识点：** Checkpoint、Lease、CAS、Event Replay、幂等、Unknown State、DAG Version、Retry Budget、Saga。
<a id="gov-083"></a>
### GOV-083 · AI运维Agent如何实现发布审批？

> 稳定 ID：`GOV-083`｜原题号：83

AI运维Agent应采用**计划与执行分离、审批绑定制品、分阶段发布和回滚**。Agent可提出Release Plan，但不能直接发布生产。

1. 发布计划包含Artifact Digest、Commit SHA、环境、配置Diff、数据库变更、影响、RiskScore、测试证据、观察指标、回滚和Runbook。
2. Policy Engine校验制品签名、SBOM、漏洞、测试、变更窗口、职责分离和权限；未通过不能审批，紧急例外使用Break-glass。
3. 通过SSO/OA确认Approver与Owner，高风险要求双人审批。Approval绑定PlanHash、Artifact Digest、环境、参数、资源版本及有效期，变化后重审。
4. 执行器用短期最小权限凭证，从Canary逐级扩量；每阶段以完成率、错误、P95和安全验收。Agent不得超出批准环境与流量上限。
5. 超过SLO、Error Budget或安全阈值立即回滚；数据库变更采用Expand/Contract及预演，不能假设应用回滚可恢复数据。

记录TaskID、ApprovalID、审批意见、制品、命令、阶段、指标和结果；失败发布进入复盘，任务结束后撤销发布凭证。

**相关知识点：** Release Plan、Artifact Digest、Policy Gate、Four-eyes、Canary、Error Budget、自动回滚、Break-glass、职责分离。
<a id="gov-087"></a>
### GOV-087 · Agent Checkpoint机制如何设计？

> 稳定 ID：`GOV-087`｜原题号：87

Checkpoint应是**可校验、版本化、原子提交的恢复快照**，与事件配合使用；它缩短恢复时间，但不替代审计。

1. 内容包括TaskID、DAGVersion、节点状态、Event Sequence、Artifact Hash、未决Operation、Attempt、幂等键和资源版本。
2. 在Tool副作用后、人工等待前、并行汇聚及定时阈值触发；只能在安全点创建，避免把部分提交写成完成。大对象只保留引用。
3. 先持久化Event和Artifact，再以CAS更新Checkpoint Pointer；快照带Version、Checksum和CreatedAt。按CheckpointID幂等，旧版本不可覆盖新版本。
4. Worker获取Lease，校验Checksum与Sequence，加载快照并回放后续Event。RUNNING/UNKNOWN节点须通过JobID或幂等键对账。
5. Schema演进使用Upcaster并保留兼容窗口；定期恢复演练。Checkpoint分层、加密并最小化敏感内容，禁止跨租户读取。

清理保留最近N个、里程碑及审计版本，验证引用后再删除；监控大小、失败率、恢复率、租约冲突和重复副作用。

**相关知识点：** Checkpoint、Event Sourcing、CAS、Write-ahead、Lease、Checksum、Schema Evolution、Unknown State、恢复演练。
<a id="gov-089"></a>
### GOV-089 · 如何实现跨机器任务恢复？

> 稳定 ID：`GOV-089`｜原题号：89

跨机器恢复要求**状态外置、Worker无状态、制品可寻址和租约调度**；关键状态不能只存在本机内存、临时目录或进程中。

1. DAG、Event、Checkpoint、Artifact、幂等键和Tool回执存入共享存储；大文件进对象库，配置、Prompt、工具和代码保存Version。
2. Worker以CAS申请带Epoch和TTL的Lease并心跳；失联后Lease过期才重新分配。旧Worker恢复时因Epoch过期停止提交。
3. 新Worker加载Checkpoint，校验Checksum和Sequence并回放事件。环境由容器镜像、依赖锁和配置恢复，禁止依赖本机状态。
4. 对UNKNOWN外部Job以JobID、RequestID或幂等键查询；已成功补写回执，明确失败才重试，未知转人工。本地子进程由远端Job或补偿处理。
5. 凭证不写Checkpoint，新Worker通过Workload Identity获取短期凭证，并重验Policy和资源版本；跨Region满足数据主权。

至少一次投递下消费者必须幂等，副作用使用Outbox/Saga。演练宕机和网络分区，监控RTO、恢复率、Lease冲突及孤儿Job。

**相关知识点：** Stateless Worker、Durable State、Lease Epoch、CAS、Content Hash、Workload Identity、RTO、Outbox、Saga。
<a id="gov-109"></a>
### GOV-109 · Agent重试率过高说明什么问题？

> 稳定 ID：`GOV-109`｜原题号：109

重试率过高通常表示**决策、参数、依赖或恢复策略存在系统缺陷**，并会放大延迟、成本、流量和重复副作用。

1. 区分Operation与Attempt，统计Attempt/Operation、首试成功、重试成功、最终失败和成本；按请求统计会误把尝试当业务量。
2. 按Taxonomy定位：错误Tool、参数、RAG不足、Prompt不稳、网络、限流、下游过载、Timeout过短、资源冲突或权限拒绝。
3. 判断重试是否有效：瞬时故障退避后成功可能合理；参数、权限和永久错误原样重试说明分类错误；多次仍失败是在掩盖根因。
4. 检查退避、Jitter、Retry Budget、Deadline和熔断，防止各层乘法放大。写操作须有幂等键和状态查询，Unknown不可直接重试。
5. 按Tool、Model、PromptVersion、Region和TaskType切片，关联发布与异常Span；同时观察P95、Token、Cost/Success和重复副作用。

目标是提高首试成功和有效恢复，而非降为零。可改进Validator、路由、超时、扩容、降级和错误分类，以A/B Test验证。

**相关知识点：** Operation/Attempt、First-attempt Success、Retry Budget、Exponential Backoff、Jitter、Circuit Breaker、Retry Amplification、幂等。
<a id="gov-125"></a>
### GOV-125 · 如何建立Agent Failure Taxonomy？

> 稳定 ID：`GOV-125`｜原题号：125

Failure Taxonomy应是**稳定、互斥、可判定且可行动**的分层分类体系，既服务统计，也能直接映射责任模块、修复策略和回归样本。

1. 先定义失败：任务未达业务终态、结果错误、违反安全策略、超过预算或必须由人工代办。区分任务失败、系统故障与用户取消，避免把非失败事件混入分母。
2. 一级按生命周期划分输入与需求、规划与路由、模型生成、RAG、Tool与外部依赖、记忆与状态、多Agent协作、权限安全、验证交付、平台资源。二级描述可修复原因，如召回为空、参数构造错误或审批超时。
3. 每个标签编写定义、正反例、必需证据、排除条件、严重度、责任域和建议动作；主根因保持单选，诱因与症状允许多选，并明确“未知”和“证据不足”以避免强行归类。
4. 使用状态机、错误码和Trace规则自动标注高确定性事件；其余样本由分类器或LLM按固定Rubric建议标签，低置信度、新类别及高风险事件交由人工复核。
5. 用双人标注计算一致性，分析混淆矩阵和标签覆盖率；对频繁落入Other的样本聚类，按变更流程新增、合并或废弃标签，保持历史映射和Schema版本。

报表应按失败频率、业务影响和可修复性排序，并关联版本、任务类型及修复工单。**分类粒度以能够触发不同处理动作作为边界**，过细会稀释样本，过粗则无法指导优化。

**相关知识点：** 分类体系、主因与诱因、标注Rubric、标注一致性、混淆矩阵、Schema版本、失败聚类、严重度、责任域。
<a id="gov-133"></a>
> **题目合并：** `GOV-133` 已并入 [TOOL-113 · 工具调用失败如何自动恢复？](../../02-capabilities/tools-skills-mcp/sandbox-security-1.md#tool-113)。

<a id="gov-134"></a>
### GOV-134 · Agent工具熔断机制如何设计？

> 稳定 ID：`GOV-134`｜原题号：134

工具熔断应在依赖持续异常时**快速失败并阻断重试风暴**，同时保持作用域隔离、可控恢复和安全降级，不能用一个全局开关停掉全部工具。

1. 按Tool、版本、租户、区域、操作类型和错误类别建立熔断桶；参数错误、权限拒绝等调用方问题不计入依赖故障率，超时、网络、5xx、限流及业务不可用按权重计数。
2. Closed状态正常调用，滑动窗口根据最小请求量、失败率、慢调用率和连续失败阈值转为Open；Open期间立即拒绝或入延迟队列，经过冷却时间进入Half-Open。
3. Half-Open仅允许少量探测请求，并设置并发上限；连续成功后逐步关闭，失败则重新打开。采用随机抖动，避免多个Agent同时探测导致惊群。
4. 熔断前应先限制重试预算、并发和超时；熔断后按策略选择备用Tool、只读缓存、降级模型或人工处理。任何降级都不得绕过权限、审批和结果验证，高风险写操作宜直接暂停。
5. 熔断状态由平台集中治理但在调用侧快速执行，记录触发指标、阈值、作用域、探测和恢复过程；发布与配置变更需审计，支持手工强制开启但设自动过期。

监控熔断次数、拒绝量、恢复耗时、备用成功率及对任务完成率的影响，并通过故障注入校准阈值。**熔断保护的是整体可用性，重试处理的是短暂失败，两者不能互相替代**。

**相关知识点：** Circuit Breaker、Closed、Open、Half-Open、滑动窗口、慢调用率、重试预算、惊群、Bulkhead、故障注入。
<a id="gov-170"></a>
> **题目合并：** `GOV-170` 已并入 [TOOL-074 · Agent执行失败后如何恢复现场？](../../02-capabilities/tools-skills-mcp/reliability.md#tool-074)。

<a id="gov-184"></a>
### GOV-184 · 数据库写操作如何设计审批和回滚机制？

> 稳定 ID：`GOV-184`｜原题号：184

数据库写入应采用**计划审批、受控执行、分层回滚和终态验证**，审批必须绑定实际SQL与目标，不能批准可任意修改的描述。

1. Agent只生成参数化SQL或迁移计划，不持有生产写权限；代理解析AST，限制库、表、列、租户、谓词和行数，无WHERE写入、DROP等设Hard Deny。
2. 执行前在副本或影子库EXPLAIN、Dry Run，展示SQL、参数摘要、哈希、影响行、锁、Schema Diff、备份和回滚；审批绑定这些字段、窗口与TTL。
3. 执行器使用JIT凭证，先小批量Canary；DML使用事务、保存点、行版本、幂等键和超时，DDL采用在线迁移或Expand-Contract，监控锁与复制延迟。
4. 小型DML事务回滚；已提交数据以反向SQL、前镜像或PITR恢复；跨系统用补偿事务。Schema回滚考虑兼容性，不可逆迁移先备份。
5. 执行后核对影响行、约束、复制与业务终态，超阈值停止后续批次、撤销凭证并回滚；状态未知时先查询。

审计保存主体、SQL哈希、参数摘要、审批、事务ID、备份点、影响行、回滚和终态。定期做误删、死锁、超时和PITR演练，验证RPO与RTO。

**相关知识点：** SQL AST、Dry Run、参数绑定审批、事务、保存点、PITR、Expand-Contract、补偿事务、RPO、RTO。
<a id="gov-187"></a>
### GOV-187 · 外部系统API调用失败或重复调用如何处理？

> 稳定 ID：`GOV-187`｜原题号：187

外部API应先区分**失败可否重试、状态是否确定、操作是否幂等**，再选择重试、查询、补偿或人工接管；超时不等于失败。

1. 错误分为参数或权限等永久失败、限流与网络等瞬时失败、业务冲突和状态未知；仅瞬时失败重试，遵守Retry-After，使用退避、抖动和预算。
2. 每个意图生成Idempotency Key，重试沿用同一Key；服务端或代理以唯一约束保存请求哈希和结果，拒绝同Key不同参数。不支持幂等时建立去重账本。
3. 记录RequestID、TaskID、Attempt和业务对象ID。超时后先调用查询接口或按业务键核对终态，区分未执行、成功、失败和未知；未知写入禁止重放。
4. 设置连接、读取和总体Deadline，配合并发隔离、限流和熔断，防止重试风暴；熔断后可入延迟队列、切换备用服务或转人工。
5. 跨系统副作用使用Outbox、Saga和补偿事务并持久化检查点；补偿也须幂等。恢复后回读终态并验证关键字段。

审计记录参数哈希、幂等键、RequestID、错误、重试、补偿和终态，监控首次成功率、重试放大及重复副作用率。通过超时、重复、乱序和响应丢失验证。

**相关知识点：** Idempotency Key、指数退避、Retry-After、状态未知、去重账本、Circuit Breaker、Outbox、Saga、补偿事务。
<a id="gov-191"></a>
### GOV-191 · 如何识别Agent异常行为并自动降权或熔断？

> 稳定 ID：`GOV-191`｜原题号：191

异常治理应建立**行为基线、实时风险评分、分级响应和人工复核**闭环，自动动作可解释、可撤销，并优先限制副作用。

1. 采集身份、任务、Tool序列、资源、权限拒绝、频率、失败、Token、成本、数据量和外发目标；按Agent版本、任务、租户和时间建立基线。
2. 规则检测跨租户、密钥访问、绕过审批、批量删除、异常提权和未知域名外发；序列模型检测调用突增、Tool顺序偏离、资源新颖与成本漂移。
3. 将信号与资产敏感度、可逆性、爆炸半径、用户意图和授权组合为动态Risk Score。弱信号提高监控，多信号或硬规则立即升级。
4. 响应阶梯包括收紧速率、撤销JIT令牌、禁用Capability、切换只读、隔离任务、Tool熔断及暂停Agent；越权或破坏时Fail Closed。
5. 熔断按Tool、租户、操作和版本隔离，Half-Open少量探测；恢复需验证根因和健康，不能因短时正常自动恢复高权权限，误报由人工解封。

审计保存特征、基线、分值、策略、动作和终态，监控Precision、Recall、误杀率、MTTD与MTTR。通过账户接管、Prompt Injection、慢速外泄和重试风暴校准。

**相关知识点：** 行为基线、动态Risk Score、序列异常、Capability降权、Fail Closed、Circuit Breaker、Half-Open、慢速外泄、MTTD、MTTR。

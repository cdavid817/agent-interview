# Tracing、监控与 SLO

> 所属章节：[安全、治理与可观测性](README.md)｜本文件共 **35** 题。

<a id="gov-007"></a>
### GOV-007 · Agent执行过程如何追踪？（豆包二面）

> 稳定 ID：`GOV-007`｜原题号：7

Agent追踪应以**Task为业务边界、Trace为执行链、Span为步骤、Event为状态变化**，把规划、模型、检索、工具和人工操作串成因果链。

1. 入口生成TaskID与TraceID；规划、LLM、RAG、Tool、验证和审批分别创建Span，以ParentSpanID表示关系。异步消息须传播Context。
2. Span记录时间、状态、错误、各组件版本、Token、费用、摘要、重试和验收结果。原始内容外置，Trace只留脱敏摘要与引用。
3. 状态机发布`planned、running、waiting、succeeded、failed、cancelled`等Event，附序号与幂等键，用于查看进度和重建过程。
4. 数据按OpenTelemetry上报Collector，再进入Trace、Log、Metric和成本存储；界面展示DAG、关键路径、Token瀑布及错误节点。
5. 结合头部与尾部采样：错误、高风险、慢任务全量保留，正常流量抽样。告警关注完成率、P95、工具失败与成本；日志须脱敏隔离。

| 层级 | 作用 |
|---|---|
| TaskID | 关联一次业务任务及续跑 |
| TraceID | 关联一次端到端执行 |
| SpanID | 标识具体模型或工具步骤 |
| Event | 记录状态变化与检查点 |

**相关知识点：** Distributed Tracing、TaskID、TraceID、Span、OpenTelemetry、状态事件、DAG、关键路径、尾部采样。
<a id="gov-008"></a>
### GOV-008 · Agent执行过程如何实现全链路追踪？如何推荐模型，Prompt，知识库及工具调用和任务状态？（腾讯一面）

> 稳定 ID：`GOV-008`｜原题号：8

全链路追踪应把**模型路由、Prompt、检索、模型、工具和状态迁移**建模为同一Trace的语义Span，保存“版本—选择依据—结果—反馈”，支持定位、回放和推荐。

1. 入口生成TaskID、TraceID和策略版本；Planner、Router、Prompt、Retriever、LLM、Tool及HITL分别建Span。异步消息传播Context，TaskID关联续跑。
2. 路由Span记录候选、过滤和质量/时延/成本分数；Prompt Span记录模板、摘要、Token与裁剪；RAG Span记录查询、索引、Chunk和Rerank。
3. Tool Span记录Schema、参数来源、Policy、幂等键、回执和副作用；状态Event记录计划版本、节点、检查点与人工修改。敏感原文外置。
4. 推荐以验收通过的Trace为样本，按任务、风险和领域统计模型成功率、Prompt增益、知识命中及工具通过率；经离线排序、Shadow和A/B发布。
5. 平台展示DAG、关键路径、成本瀑布和版本对比。指标覆盖完成率、检索Recall、工具成功率、P95、单位成功成本和严重错误率；失败Trace全量保留。

**相关知识点：** Semantic Span、W3C Trace Context、Decision Record、Prompt Lineage、RAG Trace、Tool Audit、状态事件、离线推荐。
<a id="gov-009"></a>
### GOV-009 · 全链路可观测平台：Agent每一步规划、工具调用、模型输入输出、耗时、报错全链路埋点（Agent高级）

> 稳定 ID：`GOV-009`｜原题号：9

平台应围绕**Trace、Metric、Log、Event和Artifact**建设，分别表达因果、趋势、细节、状态与原始材料。埋点须统一语义，避免字段无法关联。

1. 入口创建TaskID、TraceID和租户上下文；规划、Prompt、检索、模型、工具、验证及人工节点各建Span。记录父节点、时间、状态、错误、版本和依赖，异步消息传播Context。
2. 模型Span记录供应商、模型、Prompt版本、Token、缓存、TTFT、完成时延、停止原因和费用；Prompt原文不进普通日志，只留脱敏摘要和Artifact引用。
3. 工具Span记录Tool/Schema、参数来源、Policy、幂等键、业务状态、重试及副作用；规划Span记录计划、依赖、重规划原因和验收条件。
4. Collector负责Schema校验、脱敏、采样和批量写入。错误、高风险、慢链路及高成本任务尾部全采样，正常流量按比例保留。
5. 界面提供DAG、关键路径、成本瀑布、版本对比和失败下钻；告警覆盖完成率、P95、工具失败、循环、积压与成本。控制高基数字段，敏感数据按租户隔离。

**相关知识点：** OpenTelemetry、Semantic Convention、Span、Event、Artifact、TTFT、Tail Sampling、关键路径、高基数、数据脱敏。
<a id="gov-010"></a>
### GOV-010 · 任务如何回放、打断、人工干预？（豆包二面）

> 稳定 ID：`GOV-010`｜原题号：10

任务应由**事件日志、状态机、检查点、取消令牌和审批节点**控制。回放重建历史，打断阻止执行，人工干预修改决策或授权，均须持久化。

1. Task以递增Event记录计划、节点、输入输出引用、工具回执、策略和人工操作；Checkpoint保存DAG、已完成节点、未决动作、证据版本及幂等键，大对象外置。
2. 只读回放按Event重建而不调用外部系统；重执行在固定模型、Prompt、知识和工具版本下从检查点运行，默认使用沙箱或Mock。非确定模型不能承诺逐Token一致。
3. 持久化Cancellation Token向子Agent、队列、模型流和工具传播。未开始节点取消，运行中工具尝试终止；已提交或状态未知的副作用须先查询并补偿。
4. 人工节点置为`WAITING_HUMAN`，展示目标、风险、计划和待审动作。人工可批准、拒绝或修改；修改生成新版本并重跑Policy与后置校验。
5. 恢复前获取任务租约，验证资源版本、权限、Deadline和预算，只执行未完成节点。审计记录操作者、原因和差异；监控恢复成功率、重复副作用及取消延迟。

| 能力 | 核心机制 | 主要风险 |
|---|---|---|
| 回放 | Event与版本快照 | 外部状态变化 |
| 打断 | 级联取消与补偿 | 副作用未回滚 |
| 人工干预 | 审批状态与新版本 | 越权修改 |

**相关知识点：** Event Sourcing、Checkpoint、Cancellation Token、HITL、幂等、补偿事务、任务租约、确定性回放。
<a id="gov-017"></a>
### GOV-017 · 完整梳理从用户提问发起，到Agent规划、工具调用、接收工具返回、模型总结输出的全链路流程（Agent高级）

> 稳定 ID：`GOV-017`｜原题号：17

完整链路是**接入鉴权—上下文—规划路由—工具执行—结果验证—生成验收**，以TaskID、TraceID和状态机贯穿。模型做语义决策，系统管权限与门禁。

1. Gateway完成SSO、租户、限流和数据分级，生成TaskID/TraceID与Deadline。Prompt Builder按预算组合规则、目标、Memory及证据，并记录版本。
2. Planner将目标拆为带依赖、Schema、验收和风险的DAG；Router按能力、质量、时延、成本与地域选模型。计划先经Policy，缺信息时澄清。
3. 工具节点从Registry选白名单Tool并生成参数。执行器校验Schema、来源、权限、风险和预算；高风险进入HITL，写操作使用Dry Run、幂等和事务。
4. 工具返回统一Envelope，含业务状态、错误、数据、证据和副作用。Validator核对后置条件；瞬时错误有限重试，未知状态先查询，已完成副作用不重放。
5. 模型基于验证结果生成并引用证据；输出经Schema、事实、安全和业务验收后返回。状态机保存Event与Checkpoint，Trace记录版本、Token、时延及审批。

**相关知识点：** Gateway、Planner、DAG、Model Router、Policy Engine、Tool Registry、HITL、幂等、Validator、Event Sourcing、Trace。
<a id="gov-025"></a>
### GOV-025 · TraceId和TaskId如何设计？

> 稳定 ID：`GOV-025`｜原题号：25

TraceID与TaskID分别表达**一次执行链**和**可续跑业务任务**。同一Task可有多个Trace；一个Trace可包含多个Agent与Tool Span。

1. TaskID在受理时生成，覆盖创建、执行、等待和恢复；绑定Tenant、Owner与状态机，但不编码敏感含义，可使用UUIDv7或ULID。
2. 每次执行生成W3C TraceID；规划、LLM、RAG、Tool和人工节点各有SpanID，以ParentSpanID表达因果，并通过`traceparent`传播。
3. 同步重试建新Span并记录`retry_of`；暂停恢复或跨天调度建新Trace，以TaskID、RunID和`links`关联旧Trace。
4. RunID表示运行，StepID表示逻辑节点，Attempt表示次数；幂等键与TaskID分离。日志和Event均携带关联字段。
5. ID由可信入口生成并校验，外部ID不可直接信任；日志按租户隔离并控制基数。审计记录ID映射和访问，防可预测ID枚举。

| 标识 | 生命周期 | 主要用途 |
|---|---|---|
| TaskID | 整个业务任务 | 状态、恢复、审计 |
| RunID | 一次运行 | 重跑与版本关联 |
| TraceID | 一次执行链 | 分布式追踪 |
| SpanID/StepID | 单次调用/逻辑节点 | 因果与幂等定位 |

**验证指标：** 误报率、漏报率、策略绕过率、告警恢复时间和审计覆盖率。

**相关知识点：** W3C Trace Context、UUIDv7、ULID、RunID、Span Link、StepID、Attempt、Idempotency Key、高基数。
<a id="gov-026"></a>
### GOV-026 · Agent执行链路如何实现全链路追踪？

> 稳定 ID：`GOV-026`｜原题号：26

全链路追踪应基于**统一Trace Context、语义Span、版本Lineage和状态Event**，使规划、检索、模型、工具、验证、人工与续跑可按因果关系还原。

1. Gateway生成TaskID、RunID和TraceID；Planner、Prompt、Retriever、LLM、Tool及HITL各建Span。同步用ParentSpanID，异步传播`traceparent`，扇入用Span Link。
2. Span记录节点、时间、状态、错误、重试、组件版本、Token、费用和验收。原文存加密Artifact，Span仅留摘要与引用。
3. 状态机以Event记录计划、节点、检查点、取消、人工修改和副作用；StepID稳定，Attempt区分重试。恢复创建新Trace并连接旧执行。
4. 使用OpenTelemetry统一埋点，经Collector校验、脱敏、采样及写入Trace、Log、Metric和Event。错误、高风险与慢链路尾部全采样。
5. 平台展示DAG、关键路径、成本瀑布、版本差异与失败下钻。告警覆盖完成率、P95、错误率、循环、积压和成本；控制高基数与留存，防观测系统拖垮业务。

**相关知识点：** Distributed Tracing、OpenTelemetry、Semantic Convention、Span Link、Artifact、Event、Tail Sampling、关键路径、高基数。
<a id="gov-027"></a>
### GOV-027 · Step级别和Task级别追踪有什么区别？

> 稳定 ID：`GOV-027`｜原题号：27

Task级回答**业务任务是否达成、当前状态和总体成本**；Step级回答**具体节点如何执行及为何失败**。二者粒度与生命周期不同，通过TaskID、RunID和StepID关联。

1. Task覆盖受理、运行、等待、恢复到终态，可含多个Trace。记录目标、计划、状态、验收、SLA、总成本、人工接管及副作用，用于运营与恢复。
2. Step对应DAG节点，如检索、模型、工具或验证。尝试以Attempt区分，Span记录摘要、版本、依赖、时延、错误、回执和后置条件。
3. 所有Step无报错不等于Task成功，部分Step失败也可能经备用完成。因此Task需独立业务验收，Step检验技术与后置条件。
4. Step Event更新Task状态，状态机校验迁移。并行节点计算关键路径，扇入用依赖或Span Link；取消与补偿不覆盖历史。
5. Task关注完成率、P95和单位成功成本；Step关注成功率、延迟、重试、Token及错误分类。失败Task保留全部Step，正常任务抽样。

| 维度 | Task级 | Step级 |
|---|---|---|
| 目标 | 业务结果与生命周期 | 单节点行为与原因 |
| 标识 | TaskID、RunID | StepID、Attempt、SpanID |
| 验收 | 业务目标 | 技术/后置条件 |
| 用途 | 运营、恢复、审计 | 调试、性能、根因 |

**相关知识点：** TaskID、StepID、Attempt、Business Acceptance、Postcondition、DAG、关键路径、状态聚合。
<a id="gov-030"></a>
### GOV-030 · 多Agent任务如何追踪执行进度？

> 稳定 ID：`GOV-030`｜原题号：30

多Agent任务的进度不能按已运行Agent数计算，而应基于**任务DAG、节点状态、权重和验收结果**形成视图，并展示关键路径与阻塞原因。

1. Orchestrator固化DAGVersion，为Task、Subtask分配ID；节点记录OwnerAgent、依赖、权重、时间、状态、Artifact和验收条件。
2. 状态区分`PENDING、READY、RUNNING、WAITING、SUCCEEDED、FAILED`。Agent以幂等Event上报；CAS防止迟到事件覆盖新状态。
3. 进度按“已验收节点权重÷全部必需节点权重”计算。动态新增节点时生成新DAG版本并重算基线；执行成功但验收失败不计完成，并行节点聚合但关键路径单列。
4. 控制面维护物化视图，展示总体进度、各Agent状态、关键路径、预计时间、重试和阻塞依赖；Trace可下钻至消息、模型和工具Span。
5. 心跳、Lease和超时用于识别失联Agent；无事件、循环重试或依赖不满足时标记Stalled并告警，恢复后依据Checkpoint续跑。

必须区分**执行进度与业务完成度**：前者描述流程位置，后者由测试、规则或人工验收，避免流程100%而业务失败。

**相关知识点：** DAG、Critical Path、Weighted Progress、Event Sourcing、CAS、Lease、Checkpoint、物化视图、验收门禁。
<a id="gov-031"></a>
### GOV-031 · Agent之间消息传递如何追踪？

> 稳定 ID：`GOV-031`｜原题号：31

Agent消息追踪应把发送、投递和消费建模为**可关联、可去重、可审计事件**，保留Envelope和Trace上下文。

1. Envelope包含MessageID、TaskID、ConversationID、Sender、Receiver、Type、版本、时间及PayloadHash；派生消息增加CausationID和CorrelationID，不得改写原ID。
2. 发送端创建Producer Span并注入`traceparent`；Broker记录Topic、Offset及排队时间；消费端建立Consumer Span。广播用Span Link表达多父关系。
3. 记录`PUBLISHED、DELIVERED、CONSUMED、ACKED、FAILED、DEAD_LETTERED`。消费者按MessageID和业务键去重，以Attempt区分重投、Sequence发现乱序。
4. Payload保存脱敏摘要、Hash和加密引用，日志附带策略结果。监控延迟、积压、重投、失败、死信和孤儿消息。

异步场景中，**时间相邻不等于因果相关**：CausationID表示触发来源，CorrelationID表示业务交互，TraceID表示链路。回放须隔离副作用。

**相关知识点：** Message Envelope、Trace Context、CausationID、CorrelationID、Span Link、幂等消费、死信队列、消息顺序。
<a id="gov-032"></a>
### GOV-032 · 多Agent协同失败如何定位问题？

> 稳定 ID：`GOV-032`｜原题号：32

多Agent协同失败应沿**任务DAG、因果消息链和Trace**缩小范围，判断问题属于Agent能力、协作协议、共享状态还是基础设施。

1. 以TaskID打开时间线，对照DAG版本查找首个偏离预期的节点，而非最后失败节点；查看状态、Attempt、Checkpoint、Artifact和验收结果。
2. 沿TraceID、MessageID与CausationID回溯模型、RAG、Tool及消息，核对丢失、重复、乱序、超时或Schema不兼容，区分生产、投递和消费失败。
3. 按Failure Taxonomy归类：规划、路由、上下文、协议、资源冲突、权限、工具、模型及验收错误。每类记录阶段、责任组件、可重试性和证据。
4. 对并发问题检查Lease、版本号、幂等键和锁等待；对结果冲突检查共享事实版本、合并规则及裁决记录；对循环协作检查最大轮次、终止条件和重复语义指纹。
5. 在隔离环境按相同版本回放最小失败子图，单变量替换模型或Agent以定位原因；不可重放的外部副作用使用录制回执和Mock。

最终形成“**症状—首个异常节点—根因—影响—修复项**”记录，并沉淀失败样本、回归测试和告警规则。

**相关知识点：** Failure Taxonomy、DAG、Distributed Tracing、CausationID、最小失败子图、并发控制、确定性回放、根因分析。
<a id="gov-034"></a>
### GOV-034 · Agent协作链路如何关联Trace？

> 稳定 ID：`GOV-034`｜原题号：34

Agent协作链路应遵循**一个链路一个Trace、一次操作一个Span、异步多父关系使用Link**。TaskID用于业务恢复，TraceID用于观测。

1. 入口生成W3C Trace Context和Root Span；规划、Agent、模型、RAG、Tool及验收各建子Span。属性记录AgentID、StepID、Attempt及版本，禁止写敏感原文。
2. 同步调用按ParentSpanID关联；发送方注入`traceparent`，接收方创建Consumer Span。广播、汇聚或多节点触发时用Span Link。
3. 消息保留MessageID、CausationID、CorrelationID和Trace Context；跨域仅传播白名单Baggage并校验来源，重投增加Attempt。
4. 子Agent建立子树，ArtifactID关联调用节点。暂停恢复可新建Trace，以Link连接旧Trace，保持TaskID不变。
5. Collector负责采样、脱敏和路由；错误、高风险及审批链路强制保留。平台支持TaskID查Trace、Span查日志，监控孤儿Span和断裂率。

**相关知识点：** W3C Trace Context、OpenTelemetry、Parent-Child、Span Link、Baggage、Context Propagation、Tail Sampling、Trace Continuation。
<a id="gov-035"></a>
### GOV-035 · Prompt执行过程如何记录？

> 稳定 ID：`GOV-035`｜原题号：35

Prompt执行记录应做到**可复现、可比较、可审计且不泄密**，记录模板、上下文装配、模型参数及输出血缘。

1. 为Prompt和Few-shot分配不可变Version与ContentHash，记录发布批次和实验组；运行时保存模板版本、变量、装配顺序、截断策略及加密引用。
2. 每次调用建立Model Span，记录TraceID、StepID、Attempt、Provider、Model、温度、TopP、Seed、Token上限、工具Schema、耗时、Token明细、FinishReason和错误码。
3. 上下文项记录SourceType、SourceID、版本、位置、Token数及选入或丢弃原因；RAG文档附检索分数与引用，Memory附写入来源。
4. 输出保存脱敏文本引用、解析结果、Schema校验、Guardrail、事实核验及评分；流式输出记录首Token时间与中断位置，无需永久保存逐Token事件。
5. 原文分级加密并受RBAC、审计和留存控制；密钥、凭证和个人信息落库前脱敏，默认使用Hash及安全引用。

回放应锁定模板、上下文快照、模型版本和采样参数；模型仍可能非确定，故比较语义、结构和验收结果，而非字面一致。

**相关知识点：** Prompt Versioning、Data Lineage、Model Span、Context Snapshot、Content Hash、PII脱敏、确定性回放、实验追踪。
<a id="gov-040"></a>
### GOV-040 · TraceId与SpanId如何设计？

> 稳定 ID：`GOV-040`｜原题号：40

TraceID与SpanID应采用**W3C Trace Context和OpenTelemetry语义**。TraceID标识一次执行链路，SpanID标识一次操作；业务任务另设TaskID。

| 标识 | 作用域 | 设计要求 |
|---|---|---|
| TraceID | 一次执行 | 16字节随机 |
| SpanID | 一次操作 | 8字节随机 |
| TaskID | 业务生命周期 | 跨重试与Trace |

1. 无合法`traceparent`时生成TraceID与Root Span；可信上游则继续传播。模型、RAG、Tool、Agent和消息消费各建Span，以ParentSpanID表达同步关系。
2. 广播、汇聚和多前置依赖使用Span Link。长任务恢复可开启新Trace，以Link关联旧Trace，并保持TaskID与CheckpointID。
3. ID使用安全随机数，禁止嵌入用户、租户、时间或机器信息；全零值非法。边界校验长度、字符及采样位。
4. 日志和消息记录TraceID、SpanID；Baggage仅传低敏、低基数白名单字段，高基数字段放Span Attribute，不进入Metric Label。
5. 监控注入失败、孤儿Span、重复ID和断链率；错误及高风险链路用Tail Sampling保留，采样不得影响业务。

**相关知识点：** W3C Trace Context、OpenTelemetry、TraceID、SpanID、TaskID、Span Link、Baggage、Tail Sampling。
<a id="gov-042"></a>
> **题目合并：** `GOV-042` 已并入 [MULTI-032 · 多Agent协同时如何实现链路关联？](../../02-capabilities/multi-agent/multi-agent-basics.md#multi-032)。

<a id="gov-043"></a>
### GOV-043 · 如何实现Agent执行过程回放？

> 稳定 ID：`GOV-043`｜原题号：43

Agent回放应基于**事件日志、版本快照和副作用隔离**重建过程。Replay用于观察与验证，默认不可再次修改外部系统；Retry用于继续真实任务。

1. 记录不可变事件：状态迁移、消息、模型、RAG、Tool回执、人工操作和验收。事件携带Sequence、CausationID、Attempt、时间及ContentHash。
2. 固化DAG、Prompt、模型参数、工具Schema、代码、Policy、索引、Memory和配置版本。大文本与Artifact放对象存储，事件仅存Hash及受控引用。
3. 引擎从Checkpoint载入状态，按原顺序推进。模型与外部Tool默认使用录制响应；重新执行须进入沙箱，使用Mock、只读凭证或Dry-run，阻断邮件、支付、发布和写库。
4. 展示模式用于审计；确定性模拟验证状态迁移；分叉回放从指定节点替换Prompt、模型或Tool。分叉生成新ReplayID，不得覆盖原记录。
5. 比较状态、Artifact Hash、输出、事实及验收结果；模型非确定时采用语义阈值和多次采样。敏感数据访问须授权、脱敏并审计。

动态数据未快照时应标记不可复现，不能将差异解释为模型退化。

**相关知识点：** Event Sourcing、Checkpoint、Deterministic Replay、Record/Replay、Dry-run、Mock、Replay Fork、Artifact Hash。
<a id="gov-048"></a>
### GOV-048 · MCP Tool调用链路如何追踪？

> 稳定 ID：`GOV-048`｜原题号：48

MCP Tool追踪应覆盖**模型决策、Client、传输、Server和下游**，以Operation关联各阶段，从而区分协议与业务故障。

1. Agent的Tool Span记录TaskID、StepID、ToolName、Schema版本和参数Hash；Client Span记录ServerID、Transport、SessionID、请求ID、超时和Attempt。
2. HTTP注入W3C Trace Context；stdio用受控元数据或本地上下文关联，不得改变协议。Server建立Span，下游系统继续建子Span。
3. 对`tools/list`、选择和`tools/call`记录Span或Event，保存能力版本、Schema Hash及路由，定位旧Schema、同名冲突和Server切换。
4. 响应记录MCP层、JSON-RPC错误码、业务错误、结构校验、RequestID和结果Hash。传输成功不等于工具成功，解析成功不等于验收通过。
异步回调使用MessageID和Span Link。监控发现、连接、排队、Server、下游及解析耗时，以及Schema不匹配、权限拒绝、超时、重连和断链率；敏感参数仅存加密引用。

**相关知识点：** MCP、JSON-RPC、Trace Context、Client/Server Span、Schema Hash、Transport、Span Link、Tool Observability。
<a id="gov-054"></a>
> **题目合并：** `GOV-054` 已并入 [TOOL-117 · MCP与Tool Calling如何融合？](../../02-capabilities/tools-skills-mcp/mcp.md#tool-117)。

<a id="gov-055"></a>
### GOV-055 · Agent监控平台如何设计？

> 稳定 ID：`GOV-055`｜原题号：55

Agent监控平台应围绕**任务结果、链路、资源、成本和安全**建设统一观测面，以TaskID、TraceID关联Metrics、Logs、Traces与评测。

1. 在Gateway、Orchestrator、模型、RAG、Tool、消息和审批系统统一埋点；OpenTelemetry Collector负责Schema校验、脱敏、采样、缓冲和路由。
2. Metrics进入时序库，Trace进入追踪库，日志与审计进入不可变存储，Prompt和Artifact进入对象库，通过元数据关联。
3. 业务层看完成率和接管率；质量层看事实性与验收；系统层看P95、错误、积压与可用性；成本层看Token及单成功任务成本。
4. 控制台提供SLO、DAG、Trace瀑布、模型/RAG/Tool钻取、失败、成本和版本对比，并按Tenant及任务类型切片。
5. 告警采用Error Budget与多窗口Burn Rate，结合发布事件和Failure Taxonomy归因；高风险、审计断档和越权尝试联动降级或熔断。

平台监控采集丢失、断链、Collector积压和查询延迟；高基数字段不进入Metric Label，错误、审批和安全事件完整保留。

**相关知识点：** Observability Platform、OpenTelemetry、SLO、Error Budget、Trace-Log关联、Failure Taxonomy、成本归因、数据分层。
<a id="gov-058"></a>
### GOV-058 · Agent系统如何实现告警机制？

> 稳定 ID：`GOV-058`｜原题号：58

Agent告警应以**用户影响、SLO消耗和安全风险**为核心，形成检测、聚合、路由、处置和复盘闭环，不能将每条错误都转为告警。

1. 业务规则监控完成率、接管和验收；系统规则监控延迟、错误、队列与资源；依赖规则监控模型、RAG、Tool；安全规则监控越权、审批绕过和审计断档。
2. 可用性与延迟采用SLO、Error Budget及多窗口Burn Rate，并设最小流量门槛；异常检测用于成本、Token和行为突变，高风险事件即时触发。
3. Alert Manager按Fingerprint去重，按Task、Tool、Region和根因聚合，设置抑制与维护窗口；Severity依据影响范围、持续时间和可恢复性确定。
4. 告警携带时间窗、当前值、阈值、受影响租户、版本、Trace、发布事件、根因候选和Runbook；按Owner路由，重大事件升级Incident。
5. 对明确且可逆场景自动扩容、切换、熔断或降级；删除、支付、发布等高风险动作仅暂停并请求人工。恢复需满足持续窗口，避免抖动；关闭后生成复盘和回归规则。

持续评估MTTA、MTTR、误报、漏报和重复告警，清理无行动价值的规则，并用故障演练验证路由。

**相关知识点：** SLO、Error Budget、Burn Rate、Alertmanager、告警聚合、抑制、Runbook、Incident、MTTA、MTTR。
<a id="gov-061"></a>
### GOV-061 · 如何实现全链路告警体系？

> 稳定 ID：`GOV-061`｜原题号：61

全链路告警应从**业务SLO关联Agent、模型、RAG、Tool与基础设施**，通过依赖拓扑合并局部异常，并找出首个异常环节。

1. 建立服务目录和动态依赖图，将TaskType、AgentVersion、Model、Index、Tool和Queue映射到Owner、SLO与Runbook；Trace及发布事件更新依赖。
2. 业务层监控完成率与验收，链路层监控关键路径、状态停留和重试，组件层监控错误、延迟与饱和，安全层监控越权和审计断档。
3. SLO使用多窗口Burn Rate，容量使用趋势预测，成本与行为突变使用异常检测；关键安全事件由确定性规则即时触发，低流量需最小样本。
4. 事件平台按Fingerprint去重，利用拓扑、时间和Trace聚合，抑制上游故障引发的告警风暴；根因候选附异常Span、版本变更和置信度。
5. 按Severity、TenantTier、Owner和值班表路由，携带Trace、影响任务、发布记录和Runbook。可逆故障自动扩容或熔断，高风险操作仅暂停并转人工。

恢复采用持续窗口，关闭后生成时间线。以MTTA、MTTR、误报、漏报和Runbook成功率衡量，并通过故障演练验证。

**相关知识点：** Service Topology、SLO、Burn Rate、Event Correlation、Fingerprint、告警抑制、Root Cause、Runbook、故障演练。
<a id="gov-065"></a>
### GOV-065 · 百万级Agent任务下如何保证监控系统性能？

> 稳定 ID：`GOV-065`｜原题号：65

百万级任务下应通过**边缘聚合、异步缓冲、分级采样、冷热分层和基数治理**控制成本，同时保证错误、安全与审计事件完整。

1. SDK非阻塞批量导出，Collector分层部署并水平扩容；消息总线吸收峰值，设置背压、磁盘缓冲和丢弃优先级，Telemetry异常不得拖慢业务。
2. Metrics仅用低基数Label，禁止TaskID、UserID；边缘预聚合Counter和Histogram。Head Sampling控量，Tail Sampling保留错误、慢链路、审批及风险事件。
3. 正常日志采样，错误与审计不采样；Prompt、Tool结果和Artifact存对象库，Trace仅存Hash及引用，避免大字段进入索引。重复错误聚合但保留样本。
4. 按时间和租户分区，Trace与Log采用列式压缩、索引生命周期和Rollup；热数据排障，温数据分析，冷数据归档，审计独立写入WORM。
5. 查询层限制时间、并发、扫描量和租户配额，预计算SLO和TopN；仪表盘避免无界基数与全量Join，Task通过精确索引定位。

容量按事件/秒、字节/任务、峰值、查询QPS及保留期估算；监控Collector丢弃、队列滞后、采样偏差、查询P95和单位观测成本。

**相关知识点：** Cardinality Control、Head/Tail Sampling、Backpressure、Rollup、冷热分层、列式存储、查询限流、容量规划。
<a id="gov-067"></a>
### GOV-067 · Agent回放时如何保证结果一致？

> 稳定 ID：`GOV-067`｜原题号：67

Agent回放一致性应定义为**状态迁移、结构结果与业务验收等价**，而非文本逐字相同；需冻结可控输入并标记不可控因素。

1. 保存事件Sequence，固化DAG、Prompt、模型参数、工具Schema、代码、Policy、索引、Memory、时区和Seed；内容以Version与Hash校验。
2. 从相同Checkpoint按事件顺序驱动状态机；并发分支采用记录的因果关系与确定性调度，不依赖线程完成顺序。时间、UUID和随机数使用录制值。
3. 模型与Tool默认使用录制响应，数据库和动态API使用快照、Mock或只读副本，副作用由幂等键拦截。真实模型即使Seed相同也可能非确定。
4. 状态和Schema精确比较，Artifact比较Hash，数值使用容差，文本比较事实、语义和引用，最终比较验收；差异标注节点、原因和影响。
5. 锁定依赖镜像、配置和区域，验证日志与版本；缺失快照或工具版本时标记部分可复现。

回放生成ReplayID并链接原Trace。高风险副作用默认隔离，访问敏感数据需授权、脱敏和审计。

**相关知识点：** Deterministic Replay、Event Sourcing、Snapshot、Checkpoint、Seed、Record/Replay、Semantic Equivalence、副作用隔离。
<a id="gov-068"></a>
### GOV-068 · Prompt变化后历史任务还能回放吗？

> 稳定 ID：`GOV-068`｜原题号：68

可以，但须区分**原版复现**与**新版分叉实验**。旧Prompt及依赖仍可获取时才能忠实回放；使用新Prompt属于对照实验。

1. Prompt Registry为指令、模板、Few-shot和变量Schema保存不可变Version、ContentHash及父版本；任务引用版本与Hash，正文存对象库，禁止覆盖。
2. 原版回放加载旧Prompt、变量值、上下文快照、模型参数、工具Schema、Policy、索引和Memory版本；模型与Tool优先使用录制响应。
3. 新版验证从Checkpoint建立Replay Fork，保持其他输入不变，仅替换PromptVersion；生成新ReplayID和Trace，记录Diff，不得修改原事件。
4. 比较验收、事实性、引用、Schema、Token、P95和安全违规；随机模型需多次采样，不以单次文本差异判断。
5. 旧Prompt因合规删除或依赖消失而不可获取时，只能以Hash验证并标记不可完全复现，禁止用当前Prompt静默替代。

历史Prompt访问必须经过RBAC、租户隔离、脱敏与审计；分叉回放默认隔离Tool副作用，写操作使用Mock或Dry-run。

**相关知识点：** Prompt Registry、Immutable Version、Content Hash、Replay Fork、Configuration Diff、Context Snapshot、置信区间、副作用隔离。
<a id="gov-071"></a>
### GOV-071 · 如何降低回放日志存储成本？

> 稳定 ID：`GOV-071`｜原题号：71

降低回放成本应坚持**事件保真、内容去重、冷热分层和可恢复性优先**；关键状态与副作用事件不可随意采样。

1. Event只存元数据、Version、ContentHash和引用；Prompt、上下文、Tool结果及Artifact进入压缩对象库。内容寻址去重相同模板、Chunk与响应。
2. 使用列式编码、字典压缩、Delta、Zstd和小文件合并；Schema保持稳定，以枚举替代重复字符串。按Tenant、日期及TaskType分区。
3. 定期生成Checkpoint，回放从最近检查点开始；归档前须满足审计与恢复要求。可重建Projection缩短留存，不与原始事件同等保存。
4. 热层保留完整Trace，温层保留压缩事件，冷层归档历史；正常Token流可聚合，错误、高风险、审批、权限变更和副作用回执不得采样。
5. 按数据级别设置TTL、Legal Hold和删除流程，索引与正文分离，过期时清理引用；审计采用WORM并遵守独立期限。

监控字节/任务、重复率、压缩比、索引占比和恢复成功率；任何优化都须以抽样任务真实回放验证。

**相关知识点：** Content-addressable Storage、Deduplication、Columnar Compression、Checkpoint、冷热分层、TTL、Legal Hold、可恢复性测试。
<a id="gov-112"></a>
### GOV-112 · Agent执行过程如何进行全链路追踪？

> 稳定 ID：`GOV-112`｜原题号：112

全链路追踪应以**TaskID关联业务任务、TraceID关联单次执行、Span表达原子步骤**，覆盖规划、模型、检索、工具、子Agent、审批和验收。

1. 网关生成Trace Context，编排器创建Root Span；规划、模型、检索、Tool及Verifier分别建立子Span。
2. 同步调用以ParentSpanID形成树；异步消息携带上下文和CausationID，汇聚及恢复使用Span Link。
3. Span记录AgentID、StepID、Attempt、模型与Prompt版本、Token、耗时、错误码和ArtifactID；敏感原文只存脱敏摘要。
4. 日志注入TaskID、TraceID和SpanID，Metrics以Exemplar跳转Trace；RAG保存文档ID、分数与引用血缘，Tool保存外部RequestID。
5. Collector统一脱敏、采样和路由；正常链路按比例采样，错误、慢请求、高成本与安全事件采用Tail Sampling保留，观测故障不得阻塞业务。

平台提供DAG与瀑布图，检测孤儿Span和上下文断裂，使任务可从指标下钻至日志、轨迹和产物。

**相关知识点：** W3C Trace Context、OpenTelemetry、TaskID、TraceID、Span、Span Link、CausationID、Exemplar、Tail Sampling、数据血缘。
<a id="gov-113"></a>
### GOV-113 · OpenTelemetry如何用于Agent监控？

> 稳定 ID：`GOV-113`｜原题号：113

OpenTelemetry应作为Agent的**统一遥测与上下文传播层**，采集Trace、Metric和Log，业务质量通过自定义语义约定表达。

1. 在网关、编排器、模型SDK、向量库和Tool Client埋点；任务建立Root Span，各执行步骤建立子Span。
2. 统一service、environment、tenant等Resource属性；Span记录模型、Prompt、索引和工具版本、Token、重试、状态码与ArtifactID，用户原文不得进入标签。
3. 通过W3C Trace Context跨HTTP传播，消息携带上下文；并行、汇聚和重试使用Span Link或Event，保证多Agent链路可还原。
4. 指标覆盖完成率、延迟、首Token时间、成本、检索命中、Tool错误和人工介入；日志注入TraceID与SpanID，借助Exemplar相互跳转。
5. Collector负责批处理、脱敏、Tail Sampling和导出，优先保留错误、慢链路、高风险及高成本任务。

应版本化Agent语义规范并限制高基数标签；Telemetry采用异步和降级设计，**观测异常不得影响主流程**。

**相关知识点：** OpenTelemetry、OTLP、Resource、Instrumentation、Collector、Trace Context、Span Link、Exemplar、Tail Sampling、语义约定。
<a id="gov-122"></a>
### GOV-122 · Agent全链路Trace如何设计？

> 稳定 ID：`GOV-122`｜原题号：122

Agent Trace应采用**任务与轨迹双层标识**：TaskID聚合重试和恢复，TraceID描述一次运行，Span刻画执行单元。

1. 网关创建Root Span并传播上下文；规划、模型、检索、Tool、子Agent、审批和Verifier分别建立Span。
2. Span记录AgentID、StepID、Attempt、状态、模型与Prompt版本、索引和Tool版本、Token、耗时、错误及ArtifactID；输入输出仅存脱敏摘要或受控引用。
3. 同步链路使用父子关系；队列携带上下文、MessageID和CausationID；并行汇聚及跨Trace恢复使用Span Link。
4. 用Event表达计划、重试、降级和人工覆盖；副作用进入审计日志，日志注入TraceID与SpanID，指标通过Exemplar链接Trace。
5. Collector执行Schema校验、脱敏和Tail Sampling，保留错误、慢任务、高成本及安全事件；SDK异步上报并限流。

查询层支持Task、Trace、Span、日志和产物间下钻，展示DAG与瀑布图。检测上下文断裂、孤儿Span和采样缺口，Schema必须版本化。

**相关知识点：** TaskID、TraceID、Span、W3C Trace Context、Span Link、Event、CausationID、Exemplar、Tail Sampling、Artifact。
<a id="gov-123"></a>
### GOV-123 · 如何构建Agent可观测平台？

> 稳定 ID：`GOV-123`｜原题号：123

Agent可观测平台应关联**运行状态、任务质量、安全风险与成本**，支持从业务指标下钻到Trace、日志、RAG和Tool证据。

1. 建立统一Schema，以TaskID、TraceID、SpanID、AgentID和版本为主键；各组件通过OpenTelemetry采集Trace、Metric和Log。
2. 指标分四层：业务层看完成率、用户满意度和人工介入；质量层看事实性、引用忠实度、Tool成功和失败分类；系统层看延迟、吞吐、错误与资源；成本层看Token及单次成功成本。
3. Collector完成脱敏、采样、限流和路由；热存储用于排障，冷存储用于审计。Prompt和工具参数只存加密Artifact引用，并按租户隔离。
4. 产品层提供总览、漏斗、DAG、瀑布图、版本对比和失败聚类；从告警定位任务，从Span查看策略、检索、Tool及验证结果。
5. 告警同时使用SLO、错误预算、变化率和异常检测，按影响范围与风险分级；关联部署、模型、Prompt、索引和Tool变更，自动给出候选根因及Runbook。

平台还需监控采集丢失、上下文断裂、高基数和查询延迟，并对Schema、权限及留存版本化。**目标是缩短发现与恢复时间**。

**相关知识点：** 三大支柱、OpenTelemetry、SLO、错误预算、语义Schema、失败聚类、变更关联、数据留存、MTTD、MTTR。
<a id="gov-132"></a>
### GOV-132 · Tool Calling成功率如何监控？

> 稳定 ID：`GOV-132`｜原题号：132

Tool Calling成功率应区分**调用是否送达、协议是否成功、业务副作用是否正确、结果是否被Agent有效使用**，仅统计HTTP 2xx会严重高估质量。

1. 每次调用生成CallID、TraceID和幂等键，记录Tool及Schema版本、权限决策、重试、外部请求ID、耗时、返回码和结果摘要；敏感参数只存脱敏值。
2. 建立分层漏斗：意图产生、参数校验、授权通过、请求发出、传输成功、业务成功、结果验证、任务采用。端到端成功率等于通过业务验证且副作用符合预期的调用数除以有效调用总数。
3. 失败按参数、权限、限流、超时、网络、依赖5xx、业务拒绝、解析和验证分类；统计首次、重试后及不可恢复失败率。
4. 按Tool、版本、租户、任务类型、区域和风险等级分层，监控成功率、错误率、P50/P95/P99延迟、重试放大、熔断状态和单次成功成本，避免总体均值掩盖局部故障。
5. 使用SLO与错误预算告警，短窗口捕获突发故障，长窗口监测退化；关联部署、Schema、凭证和上游变更。

对于写操作，以目标系统终态、回读校验或事件回执作为成功证据；异步任务需单独跟踪受理成功与最终完成。仪表盘同时展示分母和样本量，防止低流量时误判。

**相关知识点：** 端到端成功率、调用漏斗、幂等键、业务终态、SLO、错误预算、重试放大、Exemplar、分层监控。
<a id="gov-138"></a>
### GOV-138 · Agent线上故障定位流程是什么？

> 稳定 ID：`GOV-138`｜原题号：138

线上故障定位应遵循**先止损、再定界、后定位根因、最后验证恢复**，全程保留证据，避免在高压状态下直接修改Prompt或反复重试。

1. 告警后建立事件编号，判断影响租户、任务、版本和风险；涉及破坏、越权或成本失控时先暂停Tool、降级、熔断或回滚，保护现场。
2. 从SLO与业务漏斗确定异常层级：入口、编排、模型、RAG、Tool、消息、权限、Verifier或外部依赖；对比正常基线、最近部署、Prompt、模型、索引、Schema及凭证变更，缩小时间窗口。
3. 以TaskID和TraceID还原DAG并定位首个异常Span；结合日志、指标、错误码、检索候选、Tool请求ID和业务终态，区分发生点与根因。
4. 选取代表性失败样本，在脱敏、隔离的类生产环境回放；通过固定输入、组件替换、Oracle数据和配置二分进行消融。无法复现时检查并发、缓存、限流、时钟和数据漂移。
5. 修复先经过针对性测试与历史回归，再Canary放量；观察完成率、安全、延迟、成本和错误预算，确认业务终态恢复后再解除熔断。

事件结束后形成时间线、根因、影响、止损和预防项，将样本加入Failure Taxonomy与回归集，并完善告警及Runbook。

**相关知识点：** 事件响应、止损、首错定位、变更关联、Trace、组件消融、Canary、错误预算、复盘、Runbook。
<a id="gov-144"></a>
> **题目合并：** `GOV-144` 已并入 [MULTI-034 · 多Agent系统如何进行链路追踪？](../../02-capabilities/multi-agent/multi-agent-basics.md#multi-034)。

<a id="gov-145"></a>
### GOV-145 · Agent平台如何实现实时告警与根因分析？

> 稳定 ID：`GOV-145`｜原题号：145

平台应建立**指标检测—事件聚合—链路归因—自动止损—人工复核**的闭环，使告警反映用户影响，并能定位到具体版本、组件和失败证据。

1. 采集完成率、首次通过率、Tool错误、模型超时、RAG零召回、违规率、P95延迟及成功成本；以TaskID和TraceID关联指标、日志与轨迹。
2. 告警组合SLO、错误预算、多窗口变化率和异常检测。短窗口捕获突发，长窗口识别退化；按任务、版本和风险分层，设置最小样本量。
3. 对相同指纹和时间窗内告警去重聚合，计算影响任务数和严重度；关联部署、模型、Prompt、索引、Tool Schema及权限变更。
4. 根因分析从受影响Trace中定位首个异常Span，沿DAG检查上游信号，结合错误码、重试、检索分数、Tool外部请求ID和业务终态；规则负责确定性归因，LLM仅对脱敏证据生成候选原因与Runbook。
5. 高置信事件可自动熔断、回滚、切换只读或停止放量；越权、破坏和状态未知必须人工确认，自动动作受Policy约束。

告警关闭前需验证指标恢复和业务终态，随后将根因样本加入Failure Taxonomy与回归集。持续评估误报率、漏报率、MTTD、MTTR及自动修复成功率，并监控遥测自身缺失。

**相关知识点：** SLO、错误预算、多窗口告警、事件聚合、变更关联、首错定位、自动止损、MTTD、MTTR、Runbook。
<a id="gov-151"></a>
### GOV-151 · 如何定位知识库更新不生效问题？

> 稳定 ID：`GOV-151`｜原题号：151

定位应沿**源数据—解析—Chunk—Embedding—索引—检索—缓存—生成**逐段核对版本，使用SourceID和测试Query追踪。

1. 校验SourceID、内容哈希、修改时间、权限和环境；检查CDC、Webhook或定时任务是否收到事件，是否因去重或版本比较而跳过。
2. 检查摄取任务和DLQ，确认解析成功、Chunk数量合理、旧Chunk撤销、新Chunk版本正确；抽查乱码、空内容和元数据。
3. 核对Embedding模型、维度和生成水位，确认索引、命名空间与租户；按SourceID比较ChunkID、哈希和可见版本，检查批量写失败。
4. 绕过缓存用固定Query查询；新Chunk未召回时检查过滤、权限、Embedding和Rerank；召回正确但回答仍旧时检查截断、Prompt缓存和记忆。
5. 对比控制面发布与数据面可查询水位，监控别名切换、读副本、缓存TTL和区域同步；建立Read-After-Write探针。

修复后验证新增、修改和删除，并确认旧版本不可检索；保留文档、Chunk、索引及缓存血缘，设置新鲜度SLO。

**相关知识点：** CDC、摄取水位、DLQ、内容哈希、索引别名、Read-After-Write、缓存失效、数据血缘、新鲜度SLO。
<a id="gov-172"></a>
> **题目合并：** `GOV-172` 已并入 [TOOL-076 · Trace ID如何贯穿整个Agent执行链路？](../../02-capabilities/tools-skills-mcp/tool-platform.md#tool-076)。

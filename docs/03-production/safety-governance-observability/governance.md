# 治理体系综合

> 所属章节：[安全、治理与可观测性](README.md)｜本文件共 **41** 题。

<a id="gov-020"></a>
### GOV-020 · Human-in-the-Loop 应该放在哪一层？

> 稳定 ID：`GOV-020`｜原题号：20

HITL应布置在**目标确认、计划审批、高风险工具执行前、异常处置和最终验收**等边界，在人类仍能阻止不可逆后果时介入。

1. 输入层处理意图不清、授权不足或敏感用途不明的请求，通过澄清目标、资源范围和验收标准减少误操作。低风险问题不宜全部审批。
2. 规划层展示DAG、假设、成本和风险动作。跨系统写入、权限变更或策略例外由人工批准；批准绑定明确范围，重大变化需重审。
3. 工具前是关键门禁：删除、资金、生产发布、主分支、数据库写入和敏感外发须提供参数、Diff、Dry Run、影响面与回滚方案。审批令牌绑定Task、Action及资源。
4. 运行中遇低置信、证据冲突、状态未知、连续失败或异常行为时暂停转人工。人工修改生成新版本，并重过Policy与自动校验。
5. 输出层对医疗、法律、财务及高影响决定最终验收，一般内容抽样。记录审批人、理由、差异和时间，监控接管率、等待时长、驳回率及自动化收益。

| 介入点 | 主要目的 |
|---|---|
| 目标/计划 | 澄清范围与批准方案 |
| 工具执行前 | 阻止高风险副作用 |
| 异常运行中 | 处置未知状态与冲突 |
| 最终输出 | 高影响结果验收 |

**相关知识点：** HITL、Risk-based Approval、Dry Run、Approval Token、计划版本、Policy Recheck、人工接管率、职责分离。
<a id="gov-028"></a>
### GOV-028 · 如何设计Agent执行状态机？

> 稳定 ID：`GOV-028`｜原题号：28

Agent状态机应以**显式状态、受控迁移、持久化事件、幂等消费和检查点**约束执行；模型提出动作，Engine依据事件与策略推进状态。

1. Task级可设`CREATED、PLANNING、RUNNING、WAITING、PAUSED、SUCCEEDED、FAILED、CANCELLED、COMPENSATING`；Step级设置`PENDING、READY、RUNNING、RETRY_WAIT、SUCCEEDED、FAILED`。终态不可被普通事件重开。
2. 每条迁移声明触发事件、前置条件、动作、超时和失败去向。高风险工具先进入`WAITING_HUMAN`，审批通过才运行；参数或资源变化后原审批失效。
3. 状态与事件事务性落库，携带TaskID、StepID、Attempt、Sequence、版本及幂等键。采用乐观锁或CAS防止并发推进；至少一次投递下按EventID去重。
4. 在计划确定、工具副作用后及人工等待前保存Checkpoint，包括DAG版本、完成节点和工具回执。恢复时取得租约并校验资源版本与权限；副作用未知时先查询。
5. 取消令牌级联至子Agent、队列和工具；已提交操作进入补偿流程。监测非法迁移、状态停留、重试环、重复事件和恢复率，异常任务转死信或人工。

**验证指标：** 误报率、漏报率、策略绕过率、告警恢复时间和审计覆盖率。

**相关知识点：** 有限状态机、Event Sourcing、乐观锁、CAS、Checkpoint、Lease、幂等、补偿事务、级联取消。
<a id="gov-033"></a>
### GOV-033 · DAG执行过程如何可视化？

> 稳定 ID：`GOV-033`｜原题号：33

DAG可视化应表达**结构、实时状态、时间和证据**，使用户迅速判断执行位置、阻塞原因、关键路径和验收结果。

1. 结构视图按DAGVersion展示节点、依赖、并行分支、汇聚点和子图；节点标注Agent、类型及权重。大图支持折叠、搜索、分层布局和关键路径过滤。
2. 用颜色与图标区分Pending、Running、Waiting、Succeeded、Failed和Cancelled，并增加文字与形状以满足可访问性；重规划节点显示版本差异。
3. Gantt或瀑布图展示排队、模型、工具、人工等待和重试区间，突出Critical Path、Slack、超时与SLA风险。
4. 点击节点可下钻至Trace、Prompt版本、模型、Tool、输入输出摘要、Token、成本、错误及验收证据；敏感内容按权限脱敏，依赖边显示Artifact。
5. 数据源来自幂等状态Event和Span，前端通过增量流更新，按Sequence处理乱序；断流时标示数据陈旧时间，不能伪装实时。历史快照用于回放与版本比较。

页面提供失败优先、等待人工、成本热点和关键路径等视图，并允许复制TraceID，兼顾运营总览、排障和审计。

**相关知识点：** DAG、Critical Path、Gantt、Waterfall、状态事件、拓扑布局、增量更新、时间旅行、可访问性。
<a id="gov-036"></a>
### GOV-036 · Token消耗如何统计和分析？

> 稳定 ID：`GOV-036`｜原题号：36

Token统计应以**可归因、可对账、可优化**为目标，说明消耗由哪个租户、任务、步骤和上下文产生，以及是否转化为有效结果。

1. 每次调用记录Provider、Model、计费版本、Input、Output、CachedInput、Reasoning等分类及供应商Usage；换算成本时保留币种、价格版本和时间，防止历史账单漂移。
2. 按Tenant、Agent、TaskType、PromptVersion、Model、Step和环境聚合，TraceID可下钻至调用。中断、重试、并行分支和子Agent均计入实际消耗，缓存节省单列。
3. 上下文拆分System Prompt、历史、Memory、RAG、Tool Schema和用户输入，计算占比、有效引用率及截断率；输出关注任务成本和成功任务成本。
4. 供应商Usage用于结算，客户端Tokenizer用于预估和限额，两者定期对账。设置任务、租户和模型Budget，近阈值时压缩上下文、切换模型或停止非关键分支。
5. 分析P50/P95成本、Token/成功任务、重试浪费、无效上下文率和缓存命中率。版本对照必须同时满足质量与延迟门槛，不能只看Token下降。

**相关知识点：** Token Usage、Cost Attribution、价格版本、Tokenizer、Prompt Caching、Budget Guardrail、单位经济性、成本对账。
<a id="gov-041"></a>
### GOV-041 · OpenTelemetry在Agent系统中如何落地？

> 稳定 ID：`GOV-041`｜原题号：41

OpenTelemetry落地应先统一**语义与上下文传播**，再接入SDK，使模型、RAG、Tool和Agent链路可归因。

1. Gateway提取W3C Trace Context并建Root Span；规划、Agent、模型、RAG、Tool、消息和验收各建子Span，异步汇聚使用Span Link。
2. Span名称保持稳定，Attribute记录Tenant、Agent、Step、Attempt、Model、PromptVersion、Tool、Token和Status；原文与参数只存脱敏引用。
3. 日志注入TraceID、SpanID；指标采用低基数Label，经Exemplar跳转Trace。监控成功率、P95延迟、Token成本、工具错误、积压和人工接管。
4. 数据先发Collector，执行Batch、内存保护、脱敏、采样和路由。Head Sampling控量，Tail Sampling保留错误、高风险及慢链路。
监控Collector丢弃、导出失败、断链率和开销；Telemetry故障不得阻塞业务，数据留存、租户隔离和访问审计纳入治理。

**相关知识点：** OpenTelemetry SDK、Collector、Semantic Convention、Context Propagation、Span Link、Exemplar、Tail Sampling、Telemetry Governance。
<a id="gov-051"></a>
> **题目合并：** `GOV-051` 已并入 [TOOL-114 · 工具超时如何处理？](../../02-capabilities/tools-skills-mcp/reliability.md#tool-114)。

<a id="gov-052"></a>
> **题目合并：** `GOV-052` 已并入 [TOOL-115 · Tool参数生成错误如何治理？](../../02-capabilities/tools-skills-mcp/sandbox-security-1.md#tool-115)。

<a id="gov-056"></a>
### GOV-056 · OpenTelemetry在Agent中的应用方式？

> 稳定 ID：`GOV-056`｜原题号：56

OpenTelemetry统一**Trace、Metric、Log和上下文传播**，把模型、Workflow、RAG与Tool关联为可下钻证据。

1. Trace：入口建Root Span，规划、模型、检索、Tool、子Agent和验收各建Span；同步用ParentSpanID，异步与汇聚用Span Link。
2. Metric：从Span派生完成率、模型P95、Token、RAG命中、工具成功率和接管率；Label只用低基数字段，TaskID放Trace。
3. Log：日志注入TraceID、SpanID、TaskID和StepID，错误记录标准类型；Prompt、用户输入和工具参数仅存脱敏摘要或加密引用。
4. HTTP、RPC、数据库和消息自动埋点，Prompt、模型、RAG、Tool和验收手工埋点，统一Instrumentation与语义。
5. Collector完成Batch、脱敏、采样和路由；Tail Sampling保留错误与高风险任务。Exemplar跳转Trace，TraceID关联日志。监控断链、孤儿Span和Collector丢弃，Telemetry异常不得阻塞业务。

**相关知识点：** OpenTelemetry、Auto Instrumentation、Manual Span、Semantic Convention、Span Link、Exemplar、Collector、Tail Sampling。
<a id="gov-064"></a>
### GOV-064 · 如何实现Agent全链路成本分析？

> 稳定 ID：`GOV-064`｜原题号：64

全链路成本应将**模型、检索、工具、计算、存储、人工和失败浪费**归因到Task、Step及Tenant，以单成功任务成本衡量效率。

1. Span记录CostType、Usage、Unit、PriceVersion和Amount。模型拆分Token；工具记录API与数据库费用；平台记录计算、存储和观测成本。
2. 价格表按时间版本化，保留供应商Usage；Tokenizer用于预估，供应商Usage用于结算并定期对账。共享资源按用量或权重分摊。
3. 以TaskID、TraceID和TenantID建立血缘，子Agent、并行分支和全部Attempt归入原Operation；区分成功、失败、重试浪费和缓存节省。
4. 展示总成本、P50/P95任务成本、Cost/Success、成本构成、版本切片和预算；与质量、完成率及延迟联动，避免低价模型提高失败率。
5. 设置Tenant、TaskType和Operation级Budget；近阈值时压缩上下文、切换模型或停止低价值分支，并检测Token激增与循环调用。

优化以固定评测集和A/B Test验证，报告质量门禁、成本差异和置信区间；成本明细需RBAC、租户隔离与审计。

**相关知识点：** Cost Attribution、Unit Economics、Price Version、Cost/Success、共享成本分摊、Budget Guardrail、账单对账、A/B Test。
<a id="gov-069"></a>
### GOV-069 · Replay和Retry有什么区别？

> 稳定 ID：`GOV-069`｜原题号：69

Replay与Retry的差异在于**目的和副作用**：Replay用于分析，默认不改变生产状态；Retry用于继续业务，可能产生真实副作用。

| 维度 | Replay | Retry |
|---|---|---|
| 目标 | 复现评测 | 完成操作 |
| 输入 | 历史快照 | 原请求与当前状态 |
| 外部调用 | 录制响应、Mock、Dry-run | 真实调用 |
| 标识 | 新ReplayID，关联原Trace | 同OperationID，新Attempt |
| 风险 | 误触副作用 | 重复写入 |

1. Replay从事件和Checkpoint驱动状态机，锁定DAG、Prompt、模型、工具及数据版本；分叉可替换单个版本，但不得覆盖原记录。
2. Retry由可重试错误触发，受Deadline、Retry Budget、退避、Jitter和熔断控制；参数、权限和永久错误不应原样重试。
3. Replay默认隔离支付、通知、删除、发布和写库；Retry写操作须有幂等键、去重及状态查询，超时Unknown先对账。
4. Replay比较状态、语义、Artifact和验收；Retry关注最终状态、Attempt、额外延迟及成本。两者均记录版本、因果链和审计。

两者应使用不同入口和权限，避免回放触发生产写入，也避免无限Retry伪装成恢复能力。

**相关知识点：** Replay、Retry、OperationID、Attempt、Checkpoint、幂等、副作用隔离、Retry Budget、Unknown State。
<a id="gov-070"></a>
### GOV-070 · Event Sourcing为什么适合Agent系统？

> 稳定 ID：`GOV-070`｜原题号：70

Event Sourcing适合Agent，因为其具有**长流程、非确定决策、异步协作、重试和审计需求**；事实事件能解释为何形成当前状态。

1. 规划、状态、模型、RAG、Tool、消息、审批和验收表示为不可变Event，携带TaskID、Sequence、CausationID、Attempt、版本与Hash；状态由事件归约。
2. 事件流支持审计、定位和Replay；结合Prompt、模型、工具、索引及Policy快照，可区分模型、数据与编排变化。
3. 多Agent用CausationID、CorrelationID和版本号表达因果、重复及乱序；消费者按EventID幂等处理，以乐观锁防止并发覆盖。
4. 长任务使用Checkpoint减少重放；模型升级通过Upcaster或新Projection兼容旧事件。不同Projection服务进度、成本和审计。
5. Tool副作用不能因重放再执行，应采用Outbox、幂等键、回执和隔离；事件只描述事实，不保证跨系统事务一致。

代价是存储、Schema演进和最终一致性复杂度。关键Task生命周期采用Event Sourcing，缓存与派生视图使用普通状态存储。

**相关知识点：** Event Sourcing、Projection、Snapshot、Checkpoint、CausationID、Optimistic Lock、Outbox、幂等、Schema Evolution。
<a id="gov-072"></a>
### GOV-072 · Agent运行过程中如何安全中断？

> 稳定 ID：`GOV-072`｜原题号：72

安全中断应采用**协作式取消、状态机、检查点和副作用确认**，保证不再启动新动作、已提交动作状态明确且任务可恢复。

1. Orchestrator持久化`CANCEL_REQUESTED`并生成Token，沿Task树传播至子Agent、队列、模型和Tool；节点在调用及提交前检查Token。
2. 停止调度新节点，撤销未消费消息；运行中的只读操作先协作取消，超过Grace Period再强制终止，并记录遗留锁与资源。
3. 写操作设置Commit Boundary：未提交可回滚，已提交则查询状态并保存回执；超时Unknown进入对账，高风险操作不得因取消而再次执行。
4. 在安全点写Checkpoint，保存DAG版本、完成节点、未决Operation、幂等键和资源版本。状态由RUNNING进入CANCELLING，再进入CANCELLED或COMPENSATING。
5. 撤销结果使用显式补偿，仍受权限、审批和幂等控制；失败转人工。恢复时重验授权、资源版本和未决副作用，只运行未完成节点。

审计记录请求人、原因、传播范围、强杀、补偿和最终状态；监控取消延迟、孤儿任务、僵尸Tool及Unknown积压。

**相关知识点：** Cooperative Cancellation、Cancellation Token、Grace Period、Commit Boundary、Checkpoint、Unknown State、补偿事务、级联取消。
<a id="gov-073"></a>
### GOV-073 · 多Agent任务如何实现级联取消？

> 稳定 ID：`GOV-073`｜原题号：73

级联取消应以**任务树、取消令牌、租约和收敛协议**实现。父任务取消后阻止新子任务，并确认每个分支进入终态或补偿态。

1. Orchestrator维护父子TaskID和DAGVersion，取消请求写入`CANCEL_REQUESTED`及CancelEpoch；后续调度发现Epoch过期即拒绝启动。
2. Token沿任务树和Envelope传播至子Agent、模型、Tool及Job；节点在调用和提交前检查。广播携带TaskID与CancelEpoch，消费者幂等处理。
3. 未启动节点标记CANCELLED，排队消息失效；运行节点先协作取消，超过Grace Period后回收Lease。失联Worker由租约超时识别。
4. 子节点返回终态，父节点汇总Ack；全部分支收敛后才进入CANCELLED，Unknown或补偿失败转人工。
5. 已提交副作用先查询真实状态，再按Saga补偿；支付、发布、删除和写库仍需权限及审批。重复取消按CancelRequestID幂等。

审计记录请求人、原因、Epoch、传播、Ack、强杀、补偿和最终状态；监控收敛时间、未响应分支、僵尸Job及重复副作用。

**相关知识点：** Task Tree、CancelEpoch、Cancellation Token、Lease、Ack Barrier、Saga、幂等取消、孤儿任务。
<a id="gov-074"></a>
### GOV-074 · 长时间工具调用如何实现强制终止？

> 稳定 ID：`GOV-074`｜原题号：74

长工具调用应采用**Deadline、协作取消、进程隔离与分级强杀**。强杀是最后手段，还须处理资源回收、副作用未知和恢复。

1. 调用创建OperationID、JobID、Deadline和Token，工具在循环、I/O及提交点检查；长任务提供进度、Cancel和心跳，Worker使用Lease。
2. 超时后停止新输入并协作取消，在Grace Period内等待工具释放连接、锁、临时文件和子进程，返回Ack及Checkpoint。
3. 不响应时由Supervisor按进程组或容器终止，顺序为软信号、等待、强杀；容器限制CPU、内存、PID和网络，禁止影响其他租户。
4. 强杀后回收Lease、端口、临时目录和锁，并扫描孤儿进程。外部系统可能已接受请求，应以JobID或RequestID查询；Unknown转对账。
5. Workflow将节点置为CANCELLED、FAILED或UNKNOWN并写Checkpoint；有副作用则补偿或转人工。恢复仅执行未完成节点。

审计记录请求人、原因、信号、Ack、强杀、资源回收及状态；监控取消延迟、强杀率、僵尸进程、Unknown积压和重复副作用。

**相关知识点：** Deadline、Cooperative Cancellation、Supervisor、Process Group、Lease、Grace Period、Resource Limit、Unknown State、幂等。
<a id="gov-075"></a>
### GOV-075 · 任务暂停和任务取消有什么区别？

> 稳定 ID：`GOV-075`｜原题号：75

暂停与取消的区别是**是否继续原任务**：暂停保留上下文等待续跑；取消终止意图，不再执行未开始步骤，必要时补偿副作用。

| 维度 | 暂停 Pause | 取消 Cancel |
|---|---|---|
| 目标 | 暂时停止并恢复 | 永久终止当前任务 |
| 状态 | PAUSING→PAUSED | CANCELLING→CANCELLED |
| 数据 | 保留Checkpoint | 保留审计并释放资源 |
| 恢复 | 原TaskID从断点继续 | 通常创建新Task |
| 副作用 | 保持现状并校验 | 可按策略执行补偿 |

1. 暂停先停止调度，让运行节点到安全点，写入DAG版本、完成节点、未决Operation、幂等键和资源版本；恢复时重新获取Lease。
2. 取消沿任务树传播Token，未启动节点直接终止，运行节点在Grace Period内收敛；已提交写操作先查询状态，Unknown进入对账。
3. 暂停恢复时重验权限、审批、数据和资源版本；条件变化可生成新DAGVersion。取消后重启应创建新Task并引用原Task。
4. 两者都需幂等、合法状态迁移和审计，记录请求人、原因、传播、Checkpoint及状态；监控暂停超期、取消延迟、孤儿任务和补偿失败。

**相关知识点：** Pause、Cancel、Checkpoint、Cancellation Token、Lease、DAG Version、Unknown State、补偿事务、状态机。
<a id="gov-078"></a>
### GOV-078 · Human-in-the-Loop如何设计状态流转？

> 稳定 ID：`GOV-078`｜原题号：78

HITL应作为**状态机中的持久化等待节点**，不能阻塞线程。审批必须绑定计划、参数和资源版本，实质变化后原审批失效。

1. 状态为`READY→PENDING_APPROVAL→APPROVED/REJECTED/EXPIRED`；通过后进入`READY_TO_EXECUTE`，需修改则回到规划。
2. 审批前写Checkpoint，保存TaskID、DAGVersion、Action、参数Hash、资源版本、RiskScore、PolicyVersion、证据、回滚和期限，并释放Worker。
3. 验证Approver身份、角色、租户和职责分离；高风险操作要求双人审批。Decision用CAS和ApprovalID幂等写入，防止并发冲突。
4. 批准后重验参数Hash、资源版本、权限和有效期；变化则返回PENDING_APPROVAL。拒绝须有原因，模型只能重规划。
5. 超时可提醒、升级或拒绝，禁止默认批准；取消沿任务树传播。人工修改计划生成新DAGVersion和审批实例，原记录不可覆盖。

记录申请、修改、批准、拒绝、超时和执行结果，以TraceID关联；监控审批时长、过期率、重审率和批准后失败率。

**相关知识点：** HITL、Approval State Machine、Checkpoint、CAS、Four-eyes Principle、职责分离、Approval Binding、审批超时。
<a id="gov-079"></a>
### GOV-079 · 人工修改执行计划后如何继续执行？

> 稳定 ID：`GOV-079`｜原题号：79

人工修改后应生成**新DAG版本**，完成差异分析、约束校验和审批判断后再从Checkpoint继续，不得覆盖运行中计划。

1. 修改前将任务置为PAUSING，停止调度并保存Checkpoint，记录旧DAGVersion、完成节点、未决Operation、幂等键和资源版本。
2. 用Patch表达新增、删除、替换及依赖，生成DAGVersion、PlanHash和Editor。验证无环、依赖、Schema、能力、预算、Deadline和Policy。
3. 计算Semantic Diff：完成节点输出仍适用则复用；删除但有副作用的节点判断补偿；受上游变化的节点标记Stale，不能沿用旧验收。
4. Action、参数Hash、资源、影响或RiskScore变化则原审批失效，高风险步骤重审。人工修改不能绕过Tool Allowlist、最小权限或安全门禁。
5. 以CAS提交新版本，只将依赖满足的节点置为READY；UNKNOWN先对账，消息按EventID去重，新Trace链接原Task。

审计记录Diff、理由、编辑人、校验、审批、复用或失效节点及结果；若破坏不可变约束，应拒绝并给出结构化原因。

**相关知识点：** DAG Versioning、Plan Patch、Semantic Diff、Checkpoint、Stale Node、CAS、Approval Invalidation、Artifact Reuse。
<a id="gov-081"></a>
### GOV-081 · 如何记录人工干预历史？

> 稳定 ID：`GOV-081`｜原题号：81

人工干预应作为**不可变审计事件与计划版本**记录，回答谁在何时、以何权限、基于何证据修改了什么及其影响。

1. Event包含EventID、TenantID、ActorID、Role、TaskID、TraceID、时间、类型、原因、ApprovalID和SchemaVersion。
2. 暂停、取消、审批、参数修改、计划Patch和提权记录前后Hash、字段Diff、DAGVersion、资源版本、RiskScore、PolicyDecision及有效期。
3. 保存人工看到的证据，如模型建议、Tool回执、告警、影响和回滚；大内容放对象库，事件只存Hash与引用，敏感字段脱敏。
4. 事件写入Append-only或WORM，以Sequence、Hash Chain和签名保护。更正只能追加Correction Event，禁止覆盖原历史；查看敏感原文也需审计。
5. 干预Event与Checkpoint、Trace和结果关联，支持回放。人工修改生成新DAGVersion，并记录旧审批是否失效。

查询实行RBAC、租户隔离和留存策略；统计干预率、接管原因、审批时长、Override成功率和Break-glass使用，用于优化流程。

**相关知识点：** Intervention Event、Audit Trail、WORM、Hash Chain、Plan Diff、Correction Event、Break-glass、数据留存。
<a id="gov-082"></a>
### GOV-082 · Coding Agent如何支持人工Review代码？

> 稳定 ID：`GOV-082`｜原题号：82

Coding Agent应将Review设计为**基于Diff、证据和风险的合并门禁**。Agent生成可验证变更，人工判断业务意图与高风险事项。

1. Agent在隔离分支或Worktree工作，限制可写目录，不得推主分支；原子Commit附TaskID、需求、变更摘要、文件、风险和回滚方式。
2. 界面展示结构化Diff、调用关系、依赖、生成文件、配置/权限/数据库改动，并标记Agent修改；大改动拆成审查单元，禁止混入无关格式化。
3. 证据包括编译、单元/集成测试、Lint、类型、SAST、依赖漏洞、Secret扫描和覆盖率Diff；命令、环境、版本及结果可追溯，不接受口头声明。
4. 依据文件敏感度、规模、权限、外部输入、数据流和覆盖率生成RiskScore；鉴权、加密、支付、生产配置及Migration由Owner审批。
5. Reviewer可评论、修改、批准或拒绝；修改进入新Attempt且范围受限。代码或依赖变化后旧批准失效，合并前校验Commit SHA和门禁。

合并使用受保护分支、CODEOWNERS、必需检查和短期凭证，记录Reviewer、Commit SHA、检查与部署；上线异常可关联版本并回滚。

**相关知识点：** Pull Request、Protected Branch、CODEOWNERS、Diff Review、SAST、Secret Scan、Risk Score、Commit SHA、合并门禁。
<a id="gov-085"></a>
### GOV-085 · 审批链路如何与企业OA系统集成？

> 稳定 ID：`GOV-085`｜原题号：85

与OA集成应采用**Agent负责风险与执行，OA负责身份与审批**的分工，通过Approval Gateway隔离不同OA协议。

1. ApprovalRequest包含RequestID、TaskID、Action、参数Hash、资源版本、RiskScore、影响、回滚和有效期；敏感正文存对象库，OA只接收摘要。
2. Gateway按组织、资源Owner、金额或环境映射模板，使用SSO/IAM确认身份，支持会签、或签、顺序审批和职责分离；高风险禁止自批。
3. 通过签名API创建审批，保存OA InstanceID与RequestID映射。回调验证签名、时间戳、Nonce和来源，按CallbackID幂等处理，并提供轮询对账。
4. OA结果映射为APPROVED、REJECTED、EXPIRED或CANCELLED。执行前重验状态、参数Hash、资源版本、Policy和有效期；变化则新建审批。
5. 网络故障时保持PENDING_APPROVAL并释放Worker，禁止默认批准；设置提醒、升级和超时拒绝。执行及回滚结果回写OA。

双方审计关联Actor、ApprovalID、TaskID、TraceID、决策和结果，定期对账孤儿审批与状态不一致；OA凭证最小授权。

**相关知识点：** Approval Gateway、SSO/IAM、Webhook签名、mTLS、Nonce、幂等回调、职责分离、审批对账、参数绑定。
<a id="gov-088"></a>
### GOV-088 · Workflow Engine如何支持断点续跑？

> 稳定 ID：`GOV-088`｜原题号：88

Workflow Engine通过**持久化状态机、Event、Checkpoint、幂等和租约**续跑，保证故障后只推进依赖满足的未完成节点。

1. 工作流使用不可变DAGVersion；节点状态、Artifact、依赖、Deadline、重试和补偿持久化，不依赖Worker内存。
2. 状态迁移先写Event，再更新Projection；在Tool副作用、人工等待和汇聚点写Checkpoint，分别携带Sequence和Checksum。
3. Worker以Lease拉取READY节点，用CAS转为RUNNING；崩溃后由其他Worker接管。消费者按EventID和幂等键去重。
4. 接管时加载Checkpoint并回放Event，对UNKNOWN节点以JobID、RequestID或幂等键查询；已成功补写回执，明确失败才重试，无法确认转人工。
5. 调度器重算依赖，只恢复未验收节点；重试遵守Deadline。资源、权限或计划变化时生成新DAGVersion并重验。

副作用节点采用Outbox、幂等键和Saga，不能把重启视为回滚。监控恢复率、Lease冲突、Unknown积压和重复副作用，并定期演练。

**相关知识点：** Durable Workflow、Event Sourcing、Checkpoint、Lease、CAS、Outbox、幂等、Retry Budget、Saga。
<a id="gov-090"></a>
### GOV-090 · 分布式Agent状态如何保持一致？

> 稳定 ID：`GOV-090`｜原题号：90

分布式Agent应按**关键状态强约束、消息至少一次、副作用最终一致**分层设计。任务状态由权威Workflow Store管理，本地只作缓存。

1. Task和Node使用唯一ID与状态机，迁移携带ExpectedVersion并通过CAS提交；非法迁移及旧版本写入被拒绝。
2. Worker使用带Epoch和TTL的Lease；旧Owner在Lease失效后不能提交。资源冲突使用版本号、条件更新或按资源键串行化。
3. 状态与消息使用Transactional Outbox，消费者按EventID和业务键去重；消息带Sequence和Attempt，Inbox记录消费事件。
4. Tool写操作使用幂等键、资源版本和查询；跨系统采用Saga补偿，不强求两阶段提交。超时Unknown先对账，禁止直接重试。
5. Event Sourcing保存事实，Projection提供视图；审批、扣款、发布和终态等关键决策读取权威数据并保证Read-your-writes。

定期Reconciliation比对状态与回执，修复孤儿节点。监控版本冲突、重复事件、Lease争抢、补偿失败和一致性延迟。

**相关知识点：** CAS、Optimistic Concurrency、Lease Epoch、Transactional Outbox、Inbox、幂等、Saga、Eventual Consistency、Reconciliation。
<a id="gov-095"></a>
### GOV-095 · 如何建立Agent质量基线（Baseline）？

> 稳定 ID：`GOV-095`｜原题号：95

质量基线是**固定任务分布、评测协议和可追溯版本下的参考结果**，用于判断新版本是否真实提升。

1. 从真实业务、历史失败、长尾、对抗和高风险场景构建数据集，按TaskType、领域、难度、语言和风险分层；隔离训练、开发、回归和盲测集。
2. 为每类任务定义Rubric、必需验收、部分完成、不可评估和严重错误。确定性任务用规则、Schema与测试，开放式任务用人工双评及校准后的Judge。
3. 固化Agent、Workflow、Prompt、Model、RAG索引、Tool、Policy、数据快照和环境；规定采样次数、Seed、Timeout、Retry和成本口径。
4. 报告Task Success、事实性、安全、接管、P50/P95、Token和Cost/Success，以及切片样本量、置信区间和Failure Taxonomy；人工复核边界样本。
5. 基线具有日期、范围和Owner。业务分布、政策或依赖变化时创建新BaselineVersion并双跑新旧基线，禁止静默改题或Rubric。

发布依据相对基线差异和护栏；失败样本可进入回归集，盲测集保持隔离，线上A/B Test验证真实价值。

**相关知识点：** Baseline、Golden Set、Stratified Sampling、Rubric、Data Leakage、置信区间、Failure Taxonomy、Regression Test。
<a id="gov-103"></a>
### GOV-103 · 长链路任务如何设计验收节点？

> 稳定 ID：`GOV-103`｜原题号：103

长链路应采用**里程碑验收＋最终验收＋高风险前置门禁**，尽早阻断错误传播，同时避免每步都做昂贵评测。

1. 在子结果完成、Agent交接、并行汇聚、Tool副作用前后、人工审批和不可逆操作前设置节点；低风险内部步骤可抽样。
2. 每个节点定义版本化Acceptance Contract，包括Schema、事实与引用、完整性、资源状态、安全、误差和失败去向；规则独立于执行Agent。
3. 确定性条件用Schema、规则、测试、Hash或外部状态；开放内容使用Rubric、校准Judge或人工。越权、泄露和危险副作用作为Hard Gate。
4. 通过后生成签名Artifact和EvidenceID，记录来源、版本及Hash，下游只消费已验收制品。失败进入有限修复、重规划、补偿或人工；受影响旧Artifact标记Stale。
5. 最终节点重验原始目标、跨节点一致性和真实副作用，防止局部通过但整体失败。重规划生成新DAGVersion并重验受影响部分。

验收密度按Risk Score、错误传播和验证成本调整。监控节点失败率、最早发现位置、误收/误拒、P95和成本，将失败前移。

**相关知识点：** Milestone Validation、Acceptance Contract、Hard Gate、Artifact Attestation、EvidenceID、Stale Artifact、Risk-based Testing、端到端验收。
<a id="gov-105"></a>
### GOV-105 · 单元测试通过是否等于任务完成？

> 稳定 ID：`GOV-105`｜原题号：105

不等于。单元测试只证明**被覆盖的局部行为符合预期**，任务完成还要求需求、集成、回归、安全和业务验收均通过。

1. 测试可能覆盖不足、断言错误或被Agent改成迎合实现；Mock过多会绕开数据库、网络、权限和并发。须审查测试有效性、覆盖Diff和隐藏测试。
2. 需求层核对Acceptance Criteria、边界、错误处理、兼容性和性能；实现可能通过既有测试，却遗漏新需求或改变未测试行为。
3. 工程层运行构建、类型、Lint、集成/E2E、Migration和部署预演，并检查API/Schema、依赖与配置；跨服务变更不能由单测证明。
4. 安全层执行SAST、依赖漏洞、Secret、License、鉴权、注入和路径边界检查；严重漏洞、越权或误删属于硬失败。
5. 变更经Diff Review，确认无关修改、可维护性、可观测性和回滚；在隔离环境按真实入口验收，生产还需灰度确认。

单元测试只是证据之一，最终以Independent Verifier的Task Resolution为准，并报告首次通过、缺陷逃逸和回滚率，防止过拟合。

**相关知识点：** Unit Test、Integration/E2E、Acceptance Criteria、Test Coverage、Mutation Testing、SAST、Hidden Test、Task Resolution。
<a id="gov-130"></a>
### GOV-130 · 如何判断是Recall问题还是Rerank问题？

> 稳定 ID：`GOV-130`｜原题号：130

判断关键是**同时保存初始候选集与Rerank结果**，检查黄金文档的位置变化；只看最终TopK无法归因。

| 观测结果 | 主要根因 | 优化方向 |
|---|---|---|
| 候选无相关项 | Recall | 覆盖、切分、Embedding、过滤 |
| 候选有，重排后掉出 | Rerank | 排序模型、截断、候选深度 |
| 两阶段均命中，答案仍错 | Generation | Prompt、忠实度 |

1. 建立Query—Chunk黄金集，固定索引与过滤版本；记录Retriever TopN、阶段分数、Reranker TopK及最终上下文。
2. 计算Recall@N和Hit Rate@N；关键证据未进入TopN时，检查知识覆盖、Chunk边界、过滤、Embedding和查询改写。增大N仍不命中，通常属于召回问题。
3. 对已召回候选计算NDCG@K、MRR和TopK Recall；相关项原本靠前却被降权，或Oracle Reranker可显著提升，则属于重排问题。
4. 进行组件消融：固定Recall替换Reranker，或用黄金候选测试现有Reranker；同时检查去重、Token截断和上下文拼装。

归因应按领域和查询类型分层。**发生点不等于根因**，错误过滤表现为Recall缺失，根因可能是权限或元数据配置。

**相关知识点：** 两阶段检索、Recall@N、NDCG@K、MRR、Oracle实验、组件消融、黄金候选、元数据过滤、上下文截断。
<a id="gov-131"></a>
### GOV-131 · 知识库覆盖率如何计算？

> 稳定 ID：`GOV-131`｜原题号：131

知识库覆盖率应定义为**目标业务知识中，可被检索系统正确访问并支持回答的比例**，不能用“已导入文档数÷计划文档数”替代。

1. 先定义评测宇宙，可按权威文档清单、知识条目或真实问题集合统计。文档覆盖率等于成功入库且版本有效的必需文档数除以应入库文档数；内容覆盖率按章节、事实或业务规则加权。
2. 更有业务意义的是问题覆盖率：对代表性Query集合，若知识库存在足以回答的权威证据，则计为存在覆盖；若该证据还能在指定K内被检索并通过权限过滤，则计为可用覆盖。可用覆盖率通常低于静态覆盖率。
3. 生产问题按频次、风险或业务价值加权，计算加权覆盖率，避免大量低价值文档掩盖核心制度缺失；同时按领域、语言、地区、产品版本、租户和时效分层。
4. 覆盖判定需检查文档完整性、解析质量、Chunk边界、元数据、Embedding与索引状态。重复内容不增加分子，过期、冲突、无权限或无法召回的内容不能视为有效覆盖。
5. 通过无答案查询、搜索零结果、人工转接和用户反馈持续发现知识缺口，经人工确认后进入缺口清单；新文档上线后用黄金Query验证并设置新鲜度SLA。

建议同时报告静态文档覆盖、语义问题覆盖、可检索覆盖和时效覆盖，并附样本量与置信区间。**覆盖率衡量“有没有证据”，正确率衡量“证据是否正确使用”**。

**相关知识点：** 文档覆盖率、问题覆盖率、加权覆盖率、可检索覆盖、知识缺口、权威来源、数据新鲜度、黄金Query。
<a id="gov-142"></a>
### GOV-142 · 如何设计Agent自动反思与自修复机制？

> 稳定 ID：`GOV-142`｜原题号：142

自动反思应是**由外部证据触发、受预算约束的验证—诊断—修复循环**，不是让同一模型无限“再想一次”；高风险副作用不得自动重放。

1. 在计划、Tool调用和最终输出后设置Verifier，使用Schema、单元测试、业务终态、引用一致性、策略检查及经校准的Judge产生结构化错误，而非依赖模型自我感觉。
2. 反思器读取目标、当前状态、失败证据和允许动作，按Failure Taxonomy输出根因假设、可修复性、风险、候选补丁与预期验证方式；禁止把隐藏密钥、策略或无关长历史重新注入。
3. 修复动作按最小变更原则执行：纠正参数、重新检索、替换证据、调整局部计划或切换备用Tool；保留原计划与结果，形成可比较版本，不得修改成功标准。
4. 设置最大循环次数、Token、时延、重试和成本预算，检测重复状态与振荡；连续同类失败、低置信、状态未知或风险升高时停止并转人工，防止递归失控。
5. 写操作必须具备幂等键、检查点、回读验证和补偿；删除、资金、发布等不可逆操作的修复仅生成建议，由策略引擎重新授权或人工审批。

每轮保存Attempt、诊断证据、变更、验证结果和成本，离线评估修复成功率、误修率、平均循环数及净完成率提升。只有在回归集和故障注入中证明安全有效的修复策略才能上线。

**历史别名：** `MODEL-011`。

**相关知识点：** Reflexion、Verifier、Failure Taxonomy、预算控制、振荡检测、幂等性、检查点、补偿事务、人工接管。
<a id="gov-149"></a>
### GOV-149 · 如何识别低质量Chunk？

> 稳定 ID：`GOV-149`｜原题号：149

低质量Chunk是指**语义不完整、缺少上下文、含噪或过期，并导致误召、漏召或错误生成**的片段，应结合规则与下游效果识别。

1. 检查空白率、乱码、OCR置信度、异常符号、重复哈希、语言、长度和Token；过短可能语义不足，过长会混合主题，阈值按文档类型设定。
2. 检查标题、章节、表头、列表、代码块和引用；避免句中截断、代词无指向、表格失去列名、页眉混入正文及多个主题粘连。
3. 校验元数据与治理属性，包括SourceID、文档版本、更新时间、作者、权限、产品和生效范围；来源不可信、版本过期、相互冲突或权限缺失的Chunk应隔离而非直接索引。
4. 利用线上信号识别：高频召回但低引用、被Reranker持续降权、相似度异常高、引发负反馈或答案不忠实；低频召回不必然低质，可能对应必要长尾知识。
5. 通过黄金Query计算Chunk级命中、Context Precision和文档利用率，人工抽检高风险异常；可用Embedding离群与近重复聚类辅助发现，但不能仅凭向量距离删除。

修复可重新解析、结构切分、父子Chunk、补标题、去重或下线，重建索引后回放原Query。所有处理保留血缘和可回滚版本。

**相关知识点：** 结构感知切分、OCR质量、父子Chunk、近重复检测、Embedding离群、Context Precision、文档利用率、数据血缘。
<a id="gov-152"></a>
> **题目合并：** `GOV-152` 已并入 [TOOL-056 · Agent如何判断一个工具是否属于高风险工具？](../../02-capabilities/tools-skills-mcp/sandbox-security-1.md#tool-056)。

<a id="gov-158"></a>
> **题目合并：** `GOV-158` 已并入 [TOOL-062 · Human-in-the-Loop应该在哪些场景下介入？](../../02-capabilities/tools-skills-mcp/sandbox-security-1.md#tool-062)。

<a id="gov-160"></a>
### GOV-160 · 如何限制Agent执行危险Shell命令？

> 稳定 ID：`GOV-160`｜原题号：160

限制危险Shell的核心是**减少通用Shell暴露、在执行前解析语义、在沙箱中强制最小权限**；字符串黑名单容易被编码、别名和命令组合绕过。

1. 优先提供结构化文件、Git和进程工具，参数经Schema校验；确需Shell时使用独立低权限身份、固定目录和最小环境变量，密钥不进入上下文。
2. 对命令构建AST，识别管道、重定向、命令替换、后台、递归、通配符、提权、设备访问、下载执行及跨Shell调用；拒绝无法解析的命令。
3. Allowlist限定可执行文件、子命令、参数和路径，规范化绝对路径并解析符号链接；禁止根、主、系统目录及工作区外写入，限制数量与递归深度。
4. 在容器或微虚机执行，使用只读根文件系统、临时卷、系统调用过滤、网络Allowlist、资源配额及无特权模式；宿主机以MAC强制。
5. 删除、权限变更、包发布、远程脚本、数据库写入等先Dry Run，展示解析后的动作和Diff；高风险要求审批，Hard Deny不可通过用户确认绕过。

执行中监控资源和子进程，超限终止；执行后校验副作用，并记录原始与规范化命令、身份、目录、策略、审批和结果。策略需经红队测试。

**历史别名：** `TOOL-064`。

**相关知识点：** Shell AST、Allowlist、命令注入、路径规范化、沙箱、系统调用过滤、MAC、资源配额、Dry Run、Hard Deny。
<a id="gov-164"></a>
> **题目合并：** `GOV-164` 已并入 [TOOL-068 · Agent如何实现命令沙箱隔离？](../../02-capabilities/tools-skills-mcp/sandbox-security-1.md#tool-068)。

<a id="gov-165"></a>
### GOV-165 · 如何保证Agent只能修改指定目录？

> 稳定 ID：`GOV-165`｜原题号：165

保证目录边界应由**系统挂载与权限最终强制、应用路径校验前置防护**；字符串前缀无法防御相对路径、链接和竞态。

1. 为任务创建独立工作区，仅将允许目录读写挂载，其余只读或不可见；Agent使用非特权身份，不授予宿主目录、Docker Socket和其他租户卷权限。
2. 文件API将路径与任务根组合后规范化，解析`.`、`..`、大小写、UNC、挂载点和符号链接，再验证真实绝对路径位于Allowlist；禁止根目录和未解析路径。
3. 防止TOCTOU：使用目录句柄相对访问、禁止跟随符号链接、原子创建与重命名，并在打开后校验对象所属文件系统。
4. 优先暴露结构化文件工具而非通用Shell，限制写、删、移动的数量、大小、递归深度和扩展名；跨边界移动、硬链接、改变权限及重新挂载属于Hard Deny。
5. 修改前生成清单和Diff，批量操作需审批；修改后遍历工作区并比较快照，发现越界立即停止和回滚。

审计记录TaskID、主体、规范化路径、文件标识、策略版本、Diff和结果，测试覆盖目录穿越、链接交换、大小写、并发及挂载绕过。**边界必须在内核层成立，即使模型或应用校验失效也无法越权写入**。

**历史别名：** `TOOL-069`。

**相关知识点：** 路径规范化、Allowlist、符号链接、TOCTOU、目录句柄、只读挂载、文件系统沙箱、Hard Deny、快照。
<a id="gov-166"></a>
> **题目合并：** `GOV-166` 已并入 [TOOL-070 · Git Push为什么通常需要审批？](../../02-capabilities/tools-skills-mcp/sandbox-security-1.md#tool-070)。

<a id="gov-167"></a>
> **题目合并：** `GOV-167` 已并入 [TOOL-071 · 如何防止Agent直接向主分支提交代码？](../../02-capabilities/tools-skills-mcp/sandbox-security-1.md#tool-071)。

<a id="gov-176"></a>
> **题目合并：** `GOV-176` 已并入 [TOOL-080 · 如何防止多个Agent同时操作同一资源导致冲突？](../../02-capabilities/tools-skills-mcp/reliability.md#tool-080)。

<a id="gov-177"></a>
> **题目合并：** `GOV-177` 已并入 [TOOL-081 · Agent如何保证工具调用的幂等性？](../../02-capabilities/tools-skills-mcp/reliability.md#tool-081)。

<a id="gov-179"></a>
> **题目合并：** `GOV-179` 已并入 [TOOL-083 · Agent执行数据库DDL或DML操作应有哪些额外保护机制？](../../02-capabilities/tools-skills-mcp/sandbox-security-1.md#tool-083)。

<a id="gov-180"></a>
> **题目合并：** `GOV-180` 已并入 [TOOL-084 · 如何平衡Agent自动化效率与人工审批带来的成本？](../../02-capabilities/tools-skills-mcp/sandbox-security-1.md#tool-084)。

<a id="gov-185"></a>
### GOV-185 · Agent修改代码后如何保证不会引入安全漏洞？

> 稳定 ID：`GOV-185`｜原题号：185

无法保证零漏洞，应建立**最小变更、自动门禁、人工复核和可回滚发布**的纵深流程，将风险降到可接受范围。

1. Agent只在任务分支和沙箱修改授权目录，遵循威胁模型、信任边界与安全规范；限制Diff和依赖变化，禁止直推主分支或读取生产密钥。
2. 运行编译、单元、集成与安全回归，并执行SAST、秘密、依赖、许可证、IaC和恶意包扫描；接口增加鉴权、注入、SSRF及越权测试。
3. 新依赖锁定版本和哈希，要求可信来源、SBOM及来源证明；避免名称混淆和不必要依赖。隔离构建并签名制品。
4. Verifier检查认证授权、数据处理、加密、日志脱敏、错误处理和资源限制；Agent说明安全影响、测试证据及未解决项，不能以自评替代扫描。
5. 通过PR、Branch Protection、必需检查和Code Owner评审，高风险目录由安全人员复核；审批绑定提交SHA，变更后重新检查。发布先Canary，监控异常并支持自动回滚。

将漏洞样本加入回归集并更新规则；审计保存Agent版本、Diff、测试、扫描、审批和制品Digest。**生成速度不能绕过供应链与变更治理**。

**相关知识点：** 威胁建模、SAST、秘密扫描、SCA、SBOM、来源证明、Branch Protection、Code Owner、Canary、供应链安全。

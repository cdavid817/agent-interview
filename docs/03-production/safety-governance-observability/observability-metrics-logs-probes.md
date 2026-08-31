# Metrics、Logs、TelemetryRail 与零侵入探针

> 所属章节：[安全、治理与可观测性](README.md)｜本文件共 **29** 题。

<a id="gov-343"></a>
### 1. 什么是 Metrics？相比 Logs 和 Traces 它有什么优势？

Metrics 是**按时间聚合的数值序列**，如请求数、延迟直方图、Token 消耗；优势是体积小、可长期保存、便于告警与趋势分析，代价是丢失单次请求的细节。

1. 一条指标由名称、时间戳、数值和一组 Label 组成，存储成本与 Label 组合数成正比，而与请求量无关。
2. 相比日志，指标查询快、可做数学运算和多维聚合，适合看板与 SLO 计算。
3. 相比 Trace，指标能反映全局趋势和容量，但不能回答"这一次为什么慢"。
4. Exemplar 可以在直方图桶上附带一个 trace_id，实现从指标跳到样本 Trace。
5. 典型用法：指标发现异常 → Trace 定位环节 → 日志查看细节。

**相关知识点：** Metrics、时间序列、Label、聚合、Exemplar、看板、告警。
<a id="gov-344"></a>
### 2. Counter、Gauge、Histogram 三种指标类型分别适合什么场景？

Counter 记录**只增不减的累计量**，Gauge 记录**可升可降的瞬时值**，Histogram 记录**数值分布**；OTel 还提供 UpDownCounter 和异步（Observable）版本。

1. Counter 通常用 rate() 换算为速率再看，直接看累计值意义不大。
2. Gauge 采样时刻的值可能错过峰值，重要状态可配合 Histogram 或 max 聚合。
3. Histogram 预先分桶，计算 P95/P99 有近似误差，分桶要按业务量级设计。
4. 选错类型会导致无法计算需要的统计量，例如用 Gauge 记录延迟就得不到分位数。

| 类型 | 适用场景 | 示例 |
|---|---|---|
| Counter | 累计次数、总量 | 请求数、错误数、Token 总消耗 |
| Gauge | 当前状态 | 队列长度、并发任务数、内存占用 |
| Histogram | 分布与分位数 | 请求延迟、输出 Token 数、工具耗时 |

**相关知识点：** Counter、Gauge、Histogram、UpDownCounter、Observable Instrument、rate()、分桶。
<a id="gov-345"></a>
### 3. 为什么延迟类指标一般用 Histogram 而不是平均值？

平均值会**被少数极端值拉偏且掩盖尾部**，Histogram 保留分布信息，能同时计算平均、P50、P95、P99，并且可以跨实例聚合。

1. 大模型调用延迟长尾明显，平均 2 秒的接口可能有 5% 的请求超过 10 秒，平均值看不出来。
2. Histogram 把观测值计入预定义的桶，每个桶是一个 Counter，可以跨实例相加后再算分位数。
3. 在每个实例上分别算 P95 再取平均，在数学上是错误的，Histogram 避免了这个问题。
4. 桶边界要覆盖业务范围（LLM 调用可从 100 毫秒到 60 秒），OTel 的指数直方图可自动适配。
5. 用户体验和 SLO 通常以尾延迟定义，因此告警应基于分位数而不是均值。

**相关知识点：** Histogram、平均值偏差、长尾、分位数、指数直方图、跨实例聚合、SLO。
<a id="gov-346"></a>
### 4. 什么是 P50 / P95 / P99？为什么要关注尾延迟？

P50/P95/P99 表示**50%、95%、99% 的请求延迟不超过该值**，即中位数和尾延迟；尾延迟直接决定最差体验和 SLO，是比平均值更有意义的指标。

1. P50 反映典型体验，P95/P99 反映少数用户的糟糕体验；两者差距大说明系统不稳定。
2. 一次 Agent 任务包含多次串行调用，尾延迟会叠加放大：每步 P99 慢，整体 P50 也可能被拖慢。
3. 尾延迟常由重试、冷启动、限流、上下文过长和外部依赖抖动引起，需要按环节拆解。
4. 分位数不能简单相加或平均，跨维度汇总要回到 Histogram 的桶数据。
5. 常见 SLO 写法："P95 响应时间小于 8 秒且成功率大于 99%"。

**相关知识点：** P50、P95、P99、尾延迟、中位数、延迟放大、SLO。
<a id="gov-347"></a>
### 5. Agent 系统的核心指标有哪些？

Agent 核心指标应覆盖**流量、质量、性能、成本与人工介入**五个维度，且以任务而非请求为主要统计单位。

1. 流量：任务数、QPS、并发任务数、按任务类型与租户的分布。
2. 质量：任务完成率、验证通过率、工具调用成功率、检索命中率、幻觉/校验失败率。
3. 性能：端到端 P95 耗时、TTFT、每任务步数、每任务 LLM 调用次数、循环/超时次数。
4. 成本：输入/输出 Token、缓存命中率、单任务成本、单位成功任务成本。
5. 介入：人工接管率、审批等待时长、用户重试率和点踩率，作为在线质量信号。

**相关知识点：** 任务完成率、工具成功率、TTFT、单位成功任务成本、缓存命中率、人工接管率、指标体系。
<a id="gov-348"></a>
### 6. 什么是 RED 方法和 USE 方法？

RED（Rate、Errors、Duration）是**面向服务请求**的指标方法，USE（Utilization、Saturation、Errors）是**面向资源**的方法；服务层用 RED，基础设施层用 USE。

1. RED 为每个服务和端点统计请求速率、错误率和延迟分布，天然对应 SLI。
2. USE 为每种资源（CPU、内存、GPU、连接池、队列）统计利用率、饱和度和错误。
3. Agent 中 RED 可细化到每个模型、工具和检索服务；USE 关注模型推理并发、限流配额和队列积压。
4. 两者互补：RED 告诉你用户受影响了，USE 告诉你是哪种资源撑不住了。
5. 上线时先把 RED 三项和关键资源的 USE 配齐，再逐步补充业务指标。

**相关知识点：** RED、USE、Rate、Errors、Duration、Utilization、Saturation、SLI。
<a id="gov-349"></a>
### 7. 指标 Label（维度）设计要注意什么？为什么不能把 user_id 作为 Label？

Label 应**低基数、语义稳定、便于聚合**；user_id、trace_id 这类唯一值会让时间序列数量爆炸，导致存储与查询成本失控。

1. 每个 Label 取值组合都是一条独立时间序列；10 个 Label 各 10 个取值理论上就是 100 亿种组合。
2. 合适的 Label：服务、环境、模型名、工具名、任务类型、租户（租户数可控时）、状态码。
3. 不合适的 Label：用户 ID、会话 ID、请求 ID、Prompt 全文、时间戳。
4. 需要按用户下钻时走 Trace 或日志，指标只保留聚合视角；或用 Exemplar 携带样本。
5. 用后端的序列数监控和 Cardinality 报表定期检查，并设置每个指标的序列上限。

**相关知识点：** Label、高基数、时间序列爆炸、Cardinality、Exemplar、聚合维度。
<a id="gov-350"></a>
### 8. Prometheus 的 Pull 模式和 OTLP 的 Push 模式有什么区别？

Prometheus **主动拉取**各目标暴露的 /metrics 端点，OTLP 由 SDK **主动推送**到 Collector；前者便于服务发现与健康判断，后者适合短生命周期任务和无法暴露端口的环境。

1. Pull 依赖服务发现和可达端口，抓取失败本身就是健康信号（up 指标）。
2. Push 不需要目标可达，Serverless、批任务、客户端 SDK 更适合，但需处理重复上报与时钟问题。
3. 两者可以互转：Collector 用 prometheus receiver 拉取后按 OTLP 转发，或用 prometheusremotewrite exporter 推给 Prometheus。
4. 聚合时间性不同：Prometheus 是累计（cumulative），OTLP 支持 delta 与 cumulative，转换时需要注意。
5. 选型看部署形态；Agent 服务常用 Push 到 Collector，再统一导出到 Prometheus 兼容后端，并监控导出失败率。

**相关知识点：** Pull 模式、Push 模式、Prometheus、服务发现、up 指标、Remote Write、Aggregation Temporality。
<a id="gov-351"></a>
### 9. 什么是 SLI、SLO、SLA？Agent 服务的 SLO 可以怎么定义？

SLI 是**衡量服务质量的具体指标**，SLO 是**对 SLI 设定的内部目标**，SLA 是**对外承诺并附带后果的协议**；三者层层递进，SLO 通常比 SLA 更严格。

1. Agent 的 SLI 要用业务验收口径（任务成功）而不是 HTTP 成功率。
2. 可定义多档 SLO：可用性、时延、质量（幻觉率、验证通过率）、成本（单任务成本上限）。
3. 错误预算 = 1 − SLO，预算消耗速率决定是否暂停发布或降级功能。
4. SLO 需要按任务类型和租户区分，简单问答与复杂多步任务不能用同一目标。

| 概念 | 含义 | Agent 示例 |
|---|---|---|
| SLI | 可测量的指标 | 任务完成率、P95 耗时、工具成功率 |
| SLO | 内部目标 | 30 天完成率 ≥ 95%，P95 ≤ 10 秒 |
| SLA | 对外承诺 | 月可用性 ≥ 99.5%，未达则赔偿 |

**相关知识点：** SLI、SLO、SLA、错误预算、业务验收、任务完成率、Burn Rate。
<a id="gov-352"></a>
### 10. 如何基于指标配置告警？阈值一般怎么确定？

告警应**基于 SLO 和错误预算消耗速率，而不是单点阈值**；阈值来自历史基线、业务承诺和故障复盘，并持续按误报率调整。

1. 优先告警"用户可感知"的症状：完成率下降、P95 超标、错误率上升、成本异常，再关联原因指标。
2. 阈值确定方法：历史分位数（如过去 4 周 P99 的 1.2 倍）、SLO 反推、容量上限、成本预算。
3. 使用多窗口 Burn Rate（如 1 小时与 6 小时）区分紧急与缓慢劣化，减少抖动误报。
4. Agent 特有告警：Token 消耗突增、循环步数超限、工具失败率、人工接管率、模型质量回归。
5. 每条告警要有 Runbook 和负责人，定期统计误报率、漏报率和平均响应时间来调整。

**相关知识点：** 告警、SLO 告警、Burn Rate、多窗口、动态阈值、误报率、Runbook。
<a id="gov-353"></a>
### 11. 结构化日志和非结构化日志有什么区别？为什么推荐结构化日志？

结构化日志以**固定字段（如 JSON）**输出，非结构化日志是自由文本；结构化便于机器解析、索引、过滤和与 Trace 关联，是生产环境的推荐做法。

1. 非结构化日志靠正则解析，格式一变就失效，且难以按字段聚合统计。
2. 结构化日志字段如 timestamp、level、service、trace_id、span_id、event、task_id、duration_ms，可直接被 Loki、Elasticsearch 索引。
3. OTel Logs 数据模型本身就是结构化的 LogRecord，可与 Trace、Resource 共享属性。
4. 建议使用日志库的结构化 API（如 Python structlog、Java Logback JSON encoder），而不是手动拼 JSON。
5. 验证方式：统计无法解析的日志行比例和关键字段缺失率。

**相关知识点：** 结构化日志、JSON 日志、LogRecord、字段规范、日志解析、字段缺失率。
<a id="gov-354"></a>
### 12. 日志级别（DEBUG / INFO / WARN / ERROR）应该如何合理使用？

日志级别用于**区分信息的重要程度和排查场景**：DEBUG 面向开发调试，INFO 记录正常关键节点，WARN 表示可恢复的异常，ERROR 表示需要处理的失败。

1. DEBUG：详细中间状态、Prompt 组装细节，生产默认关闭，可按请求动态开启。
2. INFO：任务开始/结束、工具调用摘要、状态迁移、模型选择，量要可控。
3. WARN：重试成功、降级、超时后恢复、输出被校验修正，需要关注但不必立即响应。
4. ERROR：任务失败、工具不可用、校验不通过且无法恢复，应触发告警并携带上下文。
5. 常见误用：把预期的业务失败打成 ERROR 造成噪声，或把关键失败打成 INFO 导致漏报；可用 ERROR 日志数与真实故障数的比例作为验证指标。

**相关知识点：** 日志级别、DEBUG、INFO、WARN、ERROR、动态日志级别、告警噪声。
<a id="gov-355"></a>
### 13. 如何把日志和 Trace 关联起来？为什么要在日志中输出 trace_id？

在每条日志中输出**trace_id 和 span_id**，日志后端与追踪后端就可以双向跳转，把"这一次请求"的日志从海量日志中精确过滤出来。

1. 实现方式：日志库从当前 Span 上下文自动读取 ID 写入字段（Java MDC、Python 日志过滤器），OTel 各语言有现成的桥接。
2. 使用 OTel Logs SDK 时，LogRecord 会自动关联当前 trace_id、span_id 和 Resource。
3. 跨进程、异步任务要先保证上下文传播正确，否则日志中的 trace_id 为空或错误。
4. Grafana、Datadog 等后端支持从 Trace 视图一键查询同 trace_id 的日志，也支持从日志跳到 Trace。
5. 验证关联质量：统计缺少 trace_id 的日志占比，目标接近零。

**相关知识点：** trace_id、span_id、MDC、日志桥接、Log Correlation、上下文传播。
<a id="gov-356"></a>
### 14. Agent 的日志应记录哪些关键内容？

Agent 日志应记录**计划、决策摘要、工具调用、证据引用与结果验证**，做到可回放、可审计，同时不暴露隐藏思维链原文和敏感数据。

1. 任务级：任务 ID、类型、租户、Prompt 与模型版本、开始/结束时间、最终状态与失败原因。
2. 决策级：当前计划版本、选中的分支及理由摘要、重规划触发条件。
3. 工具级：工具名、参数摘要（脱敏）、返回状态、耗时、重试、副作用标记。
4. 证据级：检索命中的文档 ID 与分数、最终引用了哪些证据。
5. 验证级：校验规则结果、Judge 分数、人工审批操作，用于统计完成率并回流评估集。

**相关知识点：** 决策摘要、计划版本、工具审计、证据引用、可回放、验证记录、脱敏。
<a id="gov-357"></a>
### 15. 日志中的敏感信息（用户输入、密钥、PII）应如何处理？

敏感信息应**尽量不采集，采集则脱敏，脱敏后再分级存储与访问控制**；密钥类信息绝不允许进入日志。

1. 源头控制：日志库注册脱敏过滤器，对手机号、邮箱、证件号、Token 等模式做掩码或哈希。
2. 用户输入与 Prompt 默认只记录长度与哈希，需要原文时写入独立加密存储，日志留引用。
3. Collector 层再做一次 attributes/redaction 处理，作为统一兜底。
4. 按数据分级设置保留期与访问权限，高敏日志的访问需审批和审计。
5. 定期用 PII 扫描工具抽检日志与 Trace，统计命中率，命中即视为缺陷处理。

**相关知识点：** PII、脱敏、掩码、哈希、密钥泄露、数据分级、访问审计。
<a id="gov-358"></a>
### 16. 日志量过大时有哪些控制手段？

控制日志量的手段包括**调整级别、采样、聚合去重、限流与分层存储**，目标是在成本和排查能力之间取得平衡。

1. 生产关闭 DEBUG，热点路径的 INFO 改为指标或 Span 属性。
2. 对高频重复日志采样（如每秒最多 N 条同类日志），错误日志优先保留。
3. 对同类错误做去重聚合，输出"错误指纹 + 次数"而不是每条原文。
4. 在 Collector 或日志代理设置速率限制和背压，防止日志洪峰拖垮应用和后端。
5. 把大对象移到 Artifact 存储，日志只留引用；监控每个服务的日志字节速率与存储成本。

**相关知识点：** 日志采样、去重聚合、错误指纹、限流、背压、Artifact 外置、日志成本。
<a id="gov-359"></a>
### 17. 日志的冷热分层存储和保留策略一般怎么设计？

按访问频率把日志分为**热（近期高频查询）、温（偶尔查询）、冷（合规归档）**三层，逐层降低存储成本并设置不同的保留期。

1. 热层通常 3～7 天，全索引、SSD，支持实时排查与告警。
2. 温层 30～90 天，降低索引粒度或压缩存储，用于趋势分析和事后复盘。
3. 冷层数月到数年，对象存储归档，满足审计与合规要求，按需恢复查询。
4. 保留期按日志类型与数据分级区分：审计日志长、调试日志短，含敏感信息的更短。
5. 评估分层效果看单 GB 存储成本、热层查询延迟和冷数据恢复耗时。

**相关知识点：** 冷热分层、保留期、索引策略、对象存储、合规归档、存储成本。
<a id="gov-360"></a>
### 18. Traces、Metrics、Logs 三者应如何互相关联，实现从告警到根因的导航？

关联的核心是**共享标识与语义**：指标定位时间与范围，Exemplar 或时间窗口跳到 Trace，Trace 通过 trace_id 跳到日志，日志再回指 Trace，形成告警到根因的闭环。

1. 统一 Resource 属性（service.name、version、environment），三种信号在同一维度下切分。
2. 指标告警触发后，用 Exemplar 或同一时间窗、同一 Label 的 Trace 查询找到代表性样本。
3. 用 Trace 中错误 Span 的 trace_id/span_id 过滤日志，查看异常堆栈与上下文。
4. 日志或 Trace 中发现的模式再反向定义新指标与告警，完成闭环。
5. 衡量关联质量：从告警到定位根因的平均时间（MTTR 中的诊断阶段）和无 trace_id 日志的比例。

**相关知识点：** 信号关联、Exemplar、trace_id、Resource 统一、告警下钻、MTTR。
<a id="gov-361"></a>
### 19. 什么是 TelemetryRail？它在 Agent 可观测性体系中承担什么角色？

TelemetryRail 是本题库中对**Agent 平台统一遥测通道**的称呼（设计概念，而非某个特定开源产品）：所有运行时、框架和工具的遥测数据都沿这一条"轨道"以统一 Schema 流向采集、处理和存储，避免各模块各自建上报。

1. 定位：介于业务代码/框架适配层与可观测后端之间，提供统一的 Span、指标、事件与 Artifact 写入接口。
2. 统一语义：以 OTel 语义约定为基础，扩展 Agent 领域字段（task、plan、tool、evidence），确保跨框架可比。
3. 统一治理：脱敏、采样、限流、路由、租户隔离在轨道上集中执行，业务无需重复实现。
4. 统一消费：评估、回放、成本核算和审计从同一数据源读取，避免多份不一致的数据。
5. 衡量其价值可看接入新框架的成本、字段完整率和跨模块 Trace 断链率。

**相关知识点：** 统一遥测通道、Schema 统一、Agent 语义扩展、集中治理、租户隔离、断链率。
<a id="gov-362"></a>
### 20. TelemetryRail 与 OpenTelemetry Collector 是什么关系？

Collector 是**通用的遥测处理与转发组件**，TelemetryRail 是**面向 Agent 平台的一层封装与约定**，通常以 Collector 作为核心执行引擎，再补充 Agent 特有的接入 SDK、语义扩展与策略配置。

1. 上游差异：TelemetryRail 提供框架适配（LangChain Callback、LangGraph Hook、自研 Runtime 钩子）把事件转成 OTel 数据；Collector 只接收标准协议。
2. 处理差异：Collector 做批处理、采样、脱敏；TelemetryRail 在其之上定义 Agent 专属规则，如错误轨迹全保留、Prompt 内容外置。
3. 下游差异：Collector 导出到后端；TelemetryRail 还负责把轨迹送往评估集、回放存储与成本系统。
4. 边界：能用 Collector 现成 Processor 实现的能力不要在轨道内重复实现。
5. 验证：两者各自暴露吞吐、丢弃率和延迟指标，端到端断链率作为综合 SLI。

**相关知识点：** OpenTelemetry Collector、框架适配层、Callback/Hook、评估回流、回放存储、Pipeline 分层。
<a id="gov-363"></a>
### 21. TelemetryRail 如何统一接入不同框架（LangChain、LangGraph、自研 Runtime）的遥测数据？

通过**适配器把各框架的回调/钩子事件映射到统一的 Agent 事件模型**，再统一转换为 OTel Span、指标与事件，使 LangChain、LangGraph 与自研 Runtime 的数据在同一 Schema 下可比。

1. 定义框架无关的事件模型：task_start、plan、llm_call、tool_call、retrieval、validation、task_end，每类固定字段。
2. LangChain 用 Callback Handler，LangGraph 用节点/边的 Hook 与状态流，自研 Runtime 在执行器中直接埋点，各自实现同一适配接口。
3. 适配器负责补齐 Resource、传播 Trace 上下文、把框架内部对象转为脱敏摘要。
4. 已有社区插桩（如 OpenLLMetry、各框架的 OTel 集成）可以复用，轨道只做字段对齐。
5. 用一致性测试验证：同一任务在不同框架下产生的 Span 结构、属性名和指标口径一致，字段完整率达标。

**相关知识点：** 适配器模式、Callback Handler、LangGraph Hook、统一事件模型、OpenLLMetry、一致性测试。
<a id="gov-364"></a>
### 22. TelemetryRail 中如何实现遥测数据的过滤、脱敏和多后端分发？

在轨道中把这三类能力做成**可配置的处理链**：过滤决定留什么，脱敏决定怎么留，分发决定送到哪；规则按租户、环境与数据分级维护。

1. 过滤：按属性、Span 名、状态、成本阈值筛选；健康检查、心跳类噪声直接丢弃，错误与高成本全保留。
2. 脱敏：正则与字典匹配 PII、密钥；对 Prompt/Response 执行掩码、哈希或摘要，原文外置加密。
3. 分发：同一数据按需路由到多个后端——Trace 后端、指标后端、评估平台、成本系统、审计归档；可用 Collector 的多 Exporter 或路由 Processor。
4. 规则版本化并可回放测试，变更先在影子 Pipeline 验证。
5. 监控每一级的输入/输出量、丢弃率、脱敏命中率与分发失败率。

**相关知识点：** 过滤规则、脱敏处理器、多后端分发、路由 Processor、规则版本化、丢弃率。
<a id="gov-365"></a>
### 23. 什么是零侵入探针？它与 SDK 手动埋点有什么区别？

零侵入探针是**不修改业务代码，在运行时（字节码、Monkey Patch、内核）自动注入采集逻辑**的方式；SDK 手动埋点则由开发者在代码中显式调用 API。

1. 探针通过 Java Agent、Python 自动插桩、eBPF 或 Sidecar 注入，接入只需改启动参数或部署配置。
2. 优点：接入快、覆盖广、统一升级；缺点：只能采集通用协议层信息，缺乏业务语义。
3. 手动埋点能记录任务类型、Prompt 版本、验证结果等业务字段，但需要开发投入与维护。
4. 二者互补：探针打底覆盖 HTTP、DB、MQ、LLM SDK，关键业务节点手动补充属性。
5. 评估探针效果看接入耗时、Span 覆盖率与性能开销（CPU、延迟增加百分比）。

**相关知识点：** 零侵入、自动插桩、Java Agent、Monkey Patch、eBPF、Sidecar、Span 覆盖率。
<a id="gov-366"></a>
### 24. Java 的 -javaagent 是如何实现零侵入插桩的？

-javaagent 利用 JVM 的**Instrumentation API 在类加载时改写字节码**，在目标方法前后织入创建 Span、记录属性的逻辑，因此无需修改源码。

1. JVM 启动时加载 agent jar，调用其 premain 方法，注册 ClassFileTransformer。
2. 每个类加载时，Transformer 判断是否匹配插桩规则（如 Servlet、JDBC、HttpClient、OkHttp、Kafka 客户端）。
3. 匹配则用 ByteBuddy 等工具修改字节码，在方法入口/出口插入 Advice 代码，创建 Span 并传播上下文。
4. OpenTelemetry Java Agent 内置上百种框架的插桩，配置通过环境变量或系统属性完成。
5. 开销主要在类加载期与热点方法的额外调用，一般在个位数百分比，需在压测中验证延迟与吞吐变化。

**相关知识点：** Java Agent、Instrumentation API、字节码增强、ByteBuddy、premain、ClassFileTransformer。
<a id="gov-367"></a>
### 25. Python 的自动插桩（opentelemetry-instrument）是如何工作的？

opentelemetry-instrument 作为**启动包装器**，在应用启动前加载各插桩库，通过 Monkey Patching 替换目标库的关键函数，从而在调用时自动创建 Span。

1. opentelemetry-bootstrap 扫描已安装的包，安装匹配的 instrumentation 包（如 requests、flask、sqlalchemy、openai）。
2. 运行 `opentelemetry-instrument python app.py` 时，通过 sitecustomize 机制在解释器启动阶段初始化 SDK 并激活所有插桩库。
3. 每个插桩库用 wrapt 等工具包装原函数：调用前创建 Span、注入上下文，调用后记录结果与异常。
4. 配置通过环境变量完成，如 OTEL_SERVICE_NAME、OTEL_EXPORTER_OTLP_ENDPOINT、OTEL_TRACES_SAMPLER。
5. 局限：使用 gevent 或多进程模型时要注意初始化顺序；验证时确认 Span 覆盖率和 Exporter 成功率。

**相关知识点：** opentelemetry-instrument、opentelemetry-bootstrap、Monkey Patching、wrapt、sitecustomize、环境变量配置。
<a id="gov-368"></a>
### 26. 什么是 eBPF？它如何做到不修改应用代码就能观测？

eBPF 允许在**Linux 内核中安全运行沙箱程序**，挂载到系统调用、网络栈和函数入口（kprobe/uprobe/tracepoint）上采集数据，因此能在不改应用、不重启进程的情况下观测。

1. 采集点：内核事件（syscall、socket、TCP 状态）与用户态函数（uprobe），可解析 HTTP、gRPC、DB 协议。
2. 工具：Grafana Beyla（已捐赠为 OpenTelemetry eBPF Instrumentation）、Pixie、Odigos、Cilium Hubble 等，可输出 OTel 格式的 Trace 与 RED 指标。
3. 优点：语言无关，覆盖无法改造的旧服务和第三方进程，开销低。
4. 局限：难以获取应用内部语义（Prompt、任务 ID），加密流量需要 uprobe 到 TLS 库，跨进程传播 Trace 上下文的能力有限。
5. 部署需要较新内核和特权权限，评估时关注 CPU 开销与事件丢失率。

**相关知识点：** eBPF、kprobe、uprobe、tracepoint、Beyla、协议解析、内核可观测。
<a id="gov-369"></a>
### 27. OpenTelemetry Operator 如何在 Kubernetes 中自动注入探针？

OpenTelemetry Operator 通过**Instrumentation CRD 与 Pod 注解**，在 Pod 创建时用 Mutating Webhook 注入 Init 容器、探针文件与环境变量，实现集群级自动插桩。

1. 部署 Operator 后创建 Instrumentation 资源，声明各语言（Java、Python、Node.js、.NET、Go）的探针镜像、Exporter 地址、采样与传播配置。
2. 在 Deployment 或 Namespace 上添加注解，如 `instrumentation.opentelemetry.io/inject-python: "true"`。
3. Webhook 拦截 Pod 创建，注入 Init 容器把探针复制到共享卷，并设置 JAVA_TOOL_OPTIONS、PYTHONPATH、OTEL_* 等环境变量。
4. Operator 还可管理 Collector 的部署（Deployment、DaemonSet、Sidecar）和 Target Allocator。
5. 验证：查看 Pod 注入后的容器与环境变量，确认 Span 到达 Collector，监控注入失败率。

**相关知识点：** OpenTelemetry Operator、Instrumentation CRD、Mutating Webhook、Init 容器、Pod 注解、Target Allocator。
<a id="gov-370"></a>
### 28. 探针对应用的性能开销一般来自哪里？如何评估和控制？

探针开销主要来自**拦截与包装调用、Span 对象创建与属性序列化、导出的网络与序列化、以及采样与批处理占用的内存**；通常控制在 CPU 增加几个百分点、P99 延迟增加毫秒级。

1. 拦截开销：字节码增强或 Monkey Patch 在每次调用增加固定的函数调用与上下文读写。
2. 数据开销：属性越多、事件越多、内容越长，序列化与内存越高；Prompt 全文记录是主要放大器。
3. 导出开销：批处理大小、导出频率、压缩策略影响网络与 CPU；同步导出会阻塞请求。
4. 控制手段：头部采样降低创建量、限制属性长度、异步批量导出、关闭不需要的插桩库。
5. 评估方法：开关探针做 A/B 压测，比较吞吐、P95/P99 延迟、CPU 与内存；持续监控 Exporter 队列与丢弃数。

**相关知识点：** 探针开销、字节码增强、序列化、批量导出、采样、压测对比、Exporter 队列。
<a id="gov-371"></a>
### 29. 零侵入探针有哪些局限？什么情况下仍需手动埋点？

零侵入探针**只能看到通用协议层，看不到业务语义、自定义框架和进程内逻辑**；需要业务字段、精确边界或特殊运行模型时仍要手动埋点。

1. 业务语义缺失：任务类型、Prompt 版本、验证结果、租户等字段探针无法推断。
2. 覆盖盲区：自研 RPC、内部函数调用、非标准 LLM 网关、脚本语言的动态调用可能没有现成插桩。
3. 语义粒度：探针按库的边界建 Span，Agent 的规划、决策、验证等逻辑节点需要手动定义。
4. 异步与上下文：自定义线程池、协程调度可能丢失上下文，需要手动传播。
5. 实践：探针打底 + 在 Runtime 关键节点手动埋点 + 用 Span 覆盖率和属性完整率验证效果。

**相关知识点：** 探针局限、业务语义、自定义框架、手动埋点、上下文丢失、属性完整率。

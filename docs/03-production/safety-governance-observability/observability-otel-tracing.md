# 可观测性基础、OpenTelemetry 与 Trace

> 所属章节：[安全、治理与可观测性](README.md)｜本文件共 **31** 题。

<a id="gov-312"></a>
### 1. 什么是可观测性？它与传统监控有什么区别？

可观测性是**通过系统对外输出的遥测数据（Metrics、Logs、Traces）推断其内部状态的能力**；监控回答"已知问题是否发生"，可观测性回答"未知问题为什么发生"。

1. 监控基于预先定义的指标和阈值，适合已知故障模式，如 CPU 过高、错误率超标。
2. 可观测性强调高维度、可关联的数据，支持事后任意切片查询，用于定位未曾预料的问题。
3. 两者不是替代关系：监控是可观测性的输出之一，告警触发后靠 Trace 和日志下钻。
4. 衡量可观测性好坏可看 MTTD（发现时间）、MTTR（恢复时间），以及一次故障需要跨几个系统才能定位。
5. Agent 场景中模型行为不确定，"未知的未知"更多，可观测性比阈值监控更重要。

**相关知识点：** Observability、Monitoring、Telemetry、MTTD、MTTR、高基数、未知的未知。
<a id="gov-313"></a>
### 2. 可观测性的三大支柱（Metrics、Logs、Traces）分别回答什么问题？

Metrics 回答**"有多少、趋势如何"**，Logs 回答**"具体发生了什么"**，Traces 回答**"请求经过了哪些环节、时间花在哪"**，三者互补而非互相替代。

1. Metrics 是聚合后的数值时间序列，体积小、便于告警和看板，但缺乏单次请求细节。
2. Logs 是离散事件记录，信息最丰富，但量大、难聚合，需要结构化后才能高效查询。
3. Traces 以 Span 树描述一次请求的因果链和耗时分布，是分布式系统定位瓶颈的核心。
4. 三者靠 trace_id、service.name、时间戳等公共字段关联；Exemplar 可把指标点位链接到具体 Trace。
5. 实践中还会补充 Events（状态变化）和 Profiles（性能剖析）作为第四、第五种信号。

**相关知识点：** Metrics、Logs、Traces、Exemplar、Profiling、信号关联、OpenTelemetry Signals。
<a id="gov-314"></a>
### 3. 为什么 AI Agent 系统比普通微服务更需要可观测性？

Agent 的执行路径**由模型在运行时动态决定**，同一输入可能走出不同的工具调用序列，且错误往往不抛异常而是"安静地做错"，因此必须靠可观测性还原它到底做了什么。

1. 非确定性：温度、上下文和模型版本都会改变输出，无法用固定测试穷举，必须记录真实执行。
2. 隐式失败：HTTP 200 不代表任务成功，模型可能编造工具结果，或在错误分支上"顺利"结束。
3. 多跳链路：一次请求包含规划、检索、多次 LLM 与工具调用，耗时和成本分布只能靠 Trace 看清。
4. 成本维度：Token 消耗是 Agent 特有的核心指标，需要按模型、租户、任务类型持续监控。
5. 治理需求：审计、回放、评估集回流都依赖完整的轨迹记录。

**相关知识点：** 非确定性、隐式失败、Token 成本、轨迹记录、审计、回放。
<a id="gov-315"></a>
### 4. Agent 系统中通常需要观测哪些对象？

应覆盖**模型调用、工具调用、检索、规划决策、状态迁移与人工介入**六类对象，每类都记录输入摘要、输出摘要、耗时、状态和版本。

1. 模型调用：供应商、模型、Prompt 版本、输入/输出 Token、TTFT、总耗时、停止原因、缓存命中。
2. 工具调用：工具名、参数摘要、返回状态、副作用、重试次数、鉴权结果。
3. 检索：查询改写、命中文档数、相似度分数、Rerank 结果、引用是否被采用。
4. 规划与决策：计划版本、选中的分支、重规划原因；记录决策摘要而非隐藏思维链原文。
5. 状态与人工：任务状态迁移事件、等待人工审批的时长、人工修改内容，用于计算完成率和接管率。

**相关知识点：** LLM Span、Tool Span、检索 Span、决策摘要、状态事件、HITL、TTFT。
<a id="gov-316"></a>
### 5. 什么是插桩（Instrumentation）？手动插桩和自动插桩有什么区别？

插桩是**在代码或运行时中加入采集遥测数据的逻辑**；手动插桩由开发者显式调用 API 创建 Span、记录指标，自动插桩由探针或库在框架层统一注入。

1. 手动插桩精确、语义丰富，能记录业务字段（任务类型、租户、Prompt 版本），但需要改代码并长期维护。
2. 自动插桩覆盖 HTTP、数据库、消息队列、主流 LLM SDK 等通用组件，接入成本低，但拿不到业务语义。
3. 通常组合使用：自动插桩打底，关键业务节点手动补充属性和事件。
4. 插桩要遵守语义约定，否则不同服务的数据无法在同一看板上聚合。
5. 验证插桩质量可看 Span 覆盖率、缺失父子关系的比例和属性完整度。

**相关知识点：** Instrumentation、手动插桩、自动插桩、Instrumentation Library、语义约定、Span 覆盖率。
<a id="gov-317"></a>
### 6. 什么是 OpenTelemetry？它主要解决什么问题？

OpenTelemetry（OTel）是 CNCF 主导的**厂商中立的遥测数据采集标准与工具集**，统一了 Traces、Metrics、Logs 的 API、SDK、数据协议和采集器，解决"每换一个后端就要重新埋点"的问题。

1. 由 OpenTracing 和 OpenCensus 合并而来，提供多语言 API/SDK、自动插桩库、Collector 和 OTLP 协议。
2. 只负责生成、处理和导出数据，不提供存储与查询后端；后端可选 Jaeger、Tempo、Prometheus、Langfuse 等。
3. 通过语义约定统一字段命名，使不同语言、不同框架的数据可以互相关联。
4. 对 Agent 而言，其 GenAI 语义约定正在标准化模型调用的属性，方便跨厂商对比 Token 和延迟指标。
5. 采用 OTel 后更换后端只需改 Exporter 配置，插桩代码不变。

**相关知识点：** OpenTelemetry、CNCF、OpenTracing、OpenCensus、OTLP、厂商中立、Exporter。
<a id="gov-318"></a>
### 7. OpenTelemetry 由哪几部分组成？

OpenTelemetry 由**规范（Specification）、API、SDK、自动插桩库、Collector 和 OTLP 协议**组成，分别负责定义、埋点接口、实现、通用采集、数据处理和传输。

1. 规范定义数据模型（Trace、Metric、Log）、语义约定和各组件行为，保证多语言一致。
2. API 是业务代码依赖的接口，只声明 Tracer、Meter、Logger 等抽象，没有 SDK 时为空实现。
3. SDK 实现采样、批处理、资源检测和 Exporter，由应用入口或探针配置。
4. 自动插桩库（Instrumentation Libraries）针对 HTTP 框架、数据库驱动、LLM SDK 提供开箱即用的 Span。
5. Collector 是独立进程，接收、处理并转发数据；OTLP 是各组件之间的统一传输协议。验证接入时先看 Collector 是否收到数据，再看后端指标。

**相关知识点：** Specification、API、SDK、Instrumentation Library、Collector、OTLP、Exporter。
<a id="gov-319"></a>
### 8. OpenTelemetry 为什么把 API 和 SDK 分开设计？

API 与 SDK 分离是为了**让被插桩的库只依赖轻量接口、不绑定具体实现**，应用方可以自由选择或替换 SDK，甚至完全不启用而几乎零开销。

1. 第三方库（HTTP 客户端、LLM SDK）只引入 API 创建 Span，不关心数据去哪、怎么采样。
2. 应用在入口配置 SDK：采样器、处理器、Exporter、Resource；未配置时 API 返回 No-op 实现。
3. 分离避免了依赖冲突和版本锁定，也允许不同厂商提供替代 SDK 而保持插桩兼容。
4. 这一设计使自动插桩和手动插桩产生的数据自然汇入同一条流水线。
5. 排查"有埋点却没数据"时，先检查 SDK 是否在进程启动时正确初始化，再看 Exporter 成功率。

**相关知识点：** API/SDK 分离、No-op 实现、依赖解耦、TracerProvider、Exporter。
<a id="gov-320"></a>
### 9. 什么是 OTLP？它支持哪些传输协议？

OTLP（OpenTelemetry Protocol）是**OTel 各组件之间传输 Traces、Metrics、Logs 的统一数据协议**，基于 Protobuf 定义，支持 gRPC 和 HTTP 两种传输。

1. gRPC 传输默认端口 4317，二进制高效、支持流式，适合服务到 Collector 的高吞吐场景。
2. HTTP 传输默认端口 4318，支持 protobuf 或 JSON 编码，适合浏览器、受限网络或不便引入 gRPC 的语言。
3. 三种信号共享同一套 Resource 与 Scope 结构，方便按服务、实例关联。
4. 协议内置批量发送、压缩（gzip）和重试语义，减少网络开销。
5. 接入验证：在 Collector 开启 debug exporter，确认接收到的 Span 数量与应用侧发送数一致，关注导出失败率。

**相关知识点：** OTLP、gRPC、HTTP/protobuf、Protobuf、端口 4317/4318、批量导出。
<a id="gov-321"></a>
### 10. OpenTelemetry Collector 的作用是什么？

Collector 是**位于应用和后端之间的独立遥测处理服务**，负责接收、转换、过滤、采样、脱敏并转发数据，使应用无需感知后端细节。

1. 解耦：应用只向本地或集群 Collector 发送 OTLP，后端更换或多路分发在 Collector 配置中完成。
2. 治理：统一做脱敏、属性补齐、尾部采样、限流，避免每个服务重复实现。
3. 兼容：可接收 Jaeger、Zipkin、Prometheus、Fluent 等多种格式并转换为 OTLP。
4. 缓冲：批处理与队列缓解后端抖动，应用进程不被阻塞。
5. 需监控 Collector 自身的接收/导出速率、丢弃计数、队列长度和内存，避免成为单点瓶颈。

**相关知识点：** Collector、Pipeline、解耦、尾部采样、脱敏、多后端分发、背压。
<a id="gov-322"></a>
### 11. Collector 中的 Receiver、Processor、Exporter 分别负责什么？

Collector 的 Pipeline 由**Receiver（进）、Processor（变）、Exporter（出）**串联构成，每种信号可以配置独立的 Pipeline。

1. Receiver 监听端口或拉取数据，如 otlp、prometheus、filelog、kafka；决定 Collector 能接什么。
2. Processor 顺序处理数据，如 batch（批量）、memory_limiter（内存保护）、attributes（增删改属性）、filter、tail_sampling、transform。
3. Exporter 把数据写出到后端，如 otlp、prometheusremotewrite、loki、debug；一个 Pipeline 可挂多个 Exporter。
4. Connector 可把一条 Pipeline 的输出作为另一条的输入，例如从 Trace 派生 RED 指标。
5. 配置顺序影响效果：memory_limiter 应最先，batch 靠后；上线前用 debug exporter 验证每一步的数据量。

**相关知识点：** Receiver、Processor、Exporter、Connector、Pipeline、batch、memory_limiter、tail_sampling。
<a id="gov-323"></a>
### 12. Collector 的 Agent 模式和 Gateway 模式有什么区别？各适合什么场景？

**Agent 模式**是 Collector 与应用同机部署（Sidecar 或 DaemonSet），负责本地收集与初步处理；**Gateway 模式**是集中式集群，负责统一治理与导出；生产环境常两级组合。

1. Agent 模式离应用近，网络延迟低，可采集主机指标和日志文件，配置随应用分发。
2. Gateway 模式集中做尾部采样、脱敏、路由和后端认证，密钥不必下发到每台机器。
3. 尾部采样要求同一 Trace 的所有 Span 到达同一实例，Gateway 需按 trace_id 做负载均衡。
4. 小规模可只用 Agent 直连后端；多租户、多后端或需要统一策略时增加 Gateway 层。
5. 评估部署方案要看每级的资源开销、数据丢失率和策略变更的生效时间。

**相关知识点：** Agent 模式、Gateway 模式、Sidecar、DaemonSet、尾部采样、负载均衡、两级部署。
<a id="gov-324"></a>
### 13. 什么是 Semantic Conventions（语义约定）？为什么要统一属性命名？

语义约定是**对 Span 名称、属性键、指标名和 Resource 字段的标准化命名规范**，如 http.request.method、db.system；统一命名后，不同语言和服务的数据才能在同一看板上聚合与对比。

1. 覆盖 HTTP、数据库、消息、RPC、云资源、GenAI 等领域，每个领域定义必填与推荐属性。
2. 没有约定时，同一含义可能出现 http.method、method、HTTPMethod 三种写法，查询与告警无法复用。
3. 约定还规定 Span 命名规则和指标单位，例如时长用秒、直方图分桶建议。
4. 约定会演进，SDK 通过环境变量控制版本迁移，升级时要检查看板和告警是否兼容。
5. 团队可在标准之上定义内部约定（如 agent.task.type），并用 Collector 校验属性完整率。

**相关知识点：** Semantic Conventions、属性命名、Span 命名、指标单位、schema_url、属性完整率。
<a id="gov-325"></a>
### 14. OpenTelemetry 的 GenAI 语义约定中有哪些常见属性？

GenAI 语义约定为**模型调用统一了一组 gen_ai.* 属性、事件和指标**，核心包括操作类型、提供商、请求/响应模型、Token 用量和生成参数；该约定仍在演进，字段名以当前官方版本为准。

1. 请求侧：gen_ai.operation.name（chat、embeddings 等）、gen_ai.provider.name（旧版为 gen_ai.system）、gen_ai.request.model、gen_ai.request.temperature、gen_ai.request.max_tokens。
2. 响应侧：gen_ai.response.model、gen_ai.response.id、gen_ai.response.finish_reasons。
3. 用量：gen_ai.usage.input_tokens、gen_ai.usage.output_tokens，配套指标 gen_ai.client.token.usage 和 gen_ai.client.operation.duration。
4. 内容：Prompt 和 Completion 以事件或可选属性记录，默认关闭，需要显式开启并考虑脱敏。
5. Agent 相关扩展定义了工具调用、Agent 名称等属性，便于把工具 Span 与模型 Span 关联统计成功率。

**相关知识点：** GenAI Semantic Conventions、gen_ai.usage.input_tokens、gen_ai.request.model、finish_reasons、内容捕获、Token 指标。
<a id="gov-326"></a>
### 15. 什么是 Resource？它与 Span Attribute 有什么区别？

Resource 描述**产生遥测数据的实体本身**（服务、实例、主机、环境），在进程内固定；Span Attribute 描述**单次操作的细节**，每个 Span 各不相同。

1. 常见 Resource：service.name、service.version、deployment.environment、host.name、k8s.pod.name、cloud.region。
2. Resource 在 SDK 初始化时通过资源检测器和环境变量 OTEL_RESOURCE_ATTRIBUTES 设置，随所有信号一起导出。
3. Span Attribute 如 http.route、db.statement、gen_ai.request.model、agent.task.id，用于筛选和聚合单次调用。
4. 把实例级信息放 Resource 可减少重复传输；把请求级信息误放 Resource 会导致数据错乱。
5. 查询时 Resource 用于按服务、版本切分指标，对比发布前后的错误率与延迟。

**相关知识点：** Resource、Span Attribute、service.name、资源检测、OTEL_RESOURCE_ATTRIBUTES、Instrumentation Scope。
<a id="gov-327"></a>
### 16. 什么是 Context Propagation（上下文传播）？它为什么是分布式追踪的基础？

上下文传播是**把当前 Trace 上下文（trace_id、span_id、采样标志、Baggage）随请求跨进程、跨线程传递**的机制；没有它，各服务的 Span 就无法连成同一条链路。

1. 进程内通过线程本地或协程上下文携带当前 Span；跨进程通过 Propagator 在请求头中注入与提取。
2. 默认使用 W3C Trace Context（traceparent/tracestate），也支持 B3、Jaeger 等格式，可同时配置多种。
3. 消息队列、异步任务、定时任务需手动把上下文放入消息属性，否则链路断裂。
4. Baggage 可传递租户、任务 ID 等业务键值，但会进入所有下游请求头，需控制大小与敏感性。
5. 断链是最常见的问题，可通过监控"孤儿 Span 比例"和无父节点的 Server Span 数量来发现。

**相关知识点：** Context Propagation、Propagator、W3C Trace Context、B3、Baggage、孤儿 Span。
<a id="gov-328"></a>
### 17. W3C Trace Context 中的 traceparent 请求头包含哪些字段？

traceparent 由**四个用连字符分隔的十六进制字段**组成：version-trace_id-parent_id-trace_flags，例如 `00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01`。

1. version：2 个十六进制字符，当前固定为 00。
2. trace_id：32 个字符（16 字节），标识整条链路，全零为非法值。
3. parent_id：16 个字符（8 字节），即上游 Span 的 span_id，接收方以此建立父子关系。
4. trace_flags：2 个字符，目前只定义最低位 sampled（01 表示上游已采样）。
5. 配套的 tracestate 头以键值对列表携带厂商扩展信息；验证传播时可抓包检查两个头在下游是否保持一致。

**相关知识点：** traceparent、tracestate、trace_id、parent_id、trace_flags、sampled 标志、W3C Trace Context。
<a id="gov-329"></a>
### 18. 什么是 Trace？什么是 Span？两者是什么关系？

Trace 是**一次请求端到端的完整执行记录**，Span 是**Trace 中一个有起止时间的工作单元**；一条 Trace 由共享同一 trace_id 的多个 Span 通过父子关系组成一棵树。

1. Trace 本身没有独立的数据结构，它是所有相同 trace_id 的 Span 的集合。
2. Span 有名称、时间区间、属性、事件、状态以及 parent_span_id，Root Span 没有父节点。
3. 在 Agent 中，一次用户任务是一条 Trace，规划、每次 LLM 调用、每次工具调用各是一个 Span。
4. 通过树形结构可以算出关键路径、每个环节的耗时占比和并行度。
5. 查看 Trace 时优先关注总耗时、错误 Span 和 Span 数量异常（如循环调用导致 Span 数暴涨）。

**相关知识点：** Trace、Span、trace_id、parent_span_id、Root Span、Span 树、关键路径。
<a id="gov-330"></a>
### 19. 一个 Span 通常包含哪些字段？

一个 Span 通常包含**标识、时间、描述、附加信息与状态**五类字段，大对象应外置，只在 Span 中保留摘要与引用。

1. name 应是低基数的操作名，如 `chat <model>`、`tool.search`，不要把用户 ID 拼进名称。
2. attributes 用于筛选和聚合，events 记录过程中的时间点（如重试、首 Token 到达）。
3. status 与 HTTP 状态不等价，业务失败需要显式设置 Error。
4. 大字段（Prompt 全文、工具返回）应外置为 Artifact，Span 只留摘要与引用，控制单个 Span 的大小。
5. 检查字段完整性可统计缺少 parent_span_id、缺少 status 或 attributes 为空的 Span 占比。

| 类别 | 字段 |
|---|---|
| 标识 | trace_id、span_id、parent_span_id、trace_flags、trace_state |
| 时间 | start_time、end_time（或 duration） |
| 描述 | name、kind、Instrumentation Scope |
| 附加 | attributes、events、links |
| 状态 | status（Unset/Ok/Error）及描述、resource |

**相关知识点：** span_id、start_time、Span Attributes、Span Events、Span Links、Span Status、Instrumentation Scope。
<a id="gov-331"></a>
### 20. Trace ID 和 Span ID 分别起什么作用？

Trace ID 用于**把一次请求涉及的所有 Span 归到同一条链路**，Span ID 用于**唯一标识链路中的一个操作**，二者组合是查询、关联日志和建立父子关系的基础。

1. Trace ID 是 16 字节随机数，由入口（Root Span）生成，之后原样传播到所有下游。
2. Span ID 是 8 字节随机数，每创建一个 Span 生成一个；子 Span 通过 parent_span_id 指向父 Span 的 Span ID。
3. 日志输出 trace_id 与 span_id 后，可以从告警跳转到相关日志，再跳到 Trace。
4. ID 必须随机且不可预测，不应编码租户或用户信息；重复或全零 ID 会被后端丢弃。
5. Agent 中还会引入业务层 TaskID、RunID，与 Trace ID 建立映射，用于统计任务完成率。

**相关知识点：** Trace ID、Span ID、parent_span_id、随机 ID、TaskID、日志关联。
<a id="gov-332"></a>
### 21. 什么是 Root Span？父子 Span 是如何关联的？

Root Span 是**一条 Trace 中没有父节点的起始 Span**，通常由入口网关或首个接收请求的服务创建；子 Span 通过记录父 Span 的 span_id 建立层级关系。

1. 创建 Span 时 SDK 读取当前上下文中的活跃 Span，将其 span_id 写入新 Span 的 parent_span_id，并继承 trace_id。
2. 跨进程时父 Span 信息来自 traceparent 头，因此下游第一个 Span 是 Server 类型的子 Span。
3. 一条 Trace 理论上只有一个 Root Span；出现多个通常意味着传播断链。
4. 后端根据父子关系渲染瀑布图，并计算每个 Span 的自身耗时（排除子 Span）。
5. 排查时统计"多 Root Span 的 Trace 比例"可以衡量传播完整性。

**相关知识点：** Root Span、parent_span_id、活跃 Span、瀑布图、自身耗时、断链。
<a id="gov-333"></a>
### 22. Span Kind 有哪几种？

Span Kind 描述**Span 在调用关系中的角色**，共五种：Internal、Server、Client、Producer、Consumer，后端据此识别服务边界并计算 RED 指标。

1. Client 与 Server 成对出现，二者的时间差即网络延迟。
2. Producer 与 Consumer 通常不是父子关系，用 Link 关联。
3. LLM 调用 Span 应设为 Client，方便按外部依赖统计延迟和错误率。
4. Kind 设错会导致服务拓扑图和依赖指标失真。

| Kind | 含义 | 例子 |
|---|---|---|
| Internal | 进程内操作 | 规划、Prompt 组装 |
| Server | 接收同步请求 | HTTP 服务端处理 |
| Client | 发起同步请求 | 调用 LLM API、数据库 |
| Producer | 发送异步消息 | 投递任务到队列 |
| Consumer | 处理异步消息 | 队列消费者执行任务 |

**相关知识点：** Span Kind、Internal、Server、Client、Producer、Consumer、服务拓扑。
<a id="gov-334"></a>
### 23. Span Event 和 Span Link 各自适用什么场景？

Span Event 记录**Span 生命周期内某个时间点发生的事**，Span Link 表达**与其他 Span（可能属于不同 Trace）的因果关联**。

1. Event 有时间戳和属性，适合记录异常、重试、首 Token 到达、状态迁移等瞬时信息。
2. GenAI 约定用 Event 记录 Prompt 和 Completion 内容，便于按需开启与脱敏。
3. Link 在创建 Span 时指定，适合批处理（一个消费 Span 关联多条消息）、扇入扇出和跨天续跑。
4. 当异步任务不适合作为子 Span（生命周期远超父 Span）时，用 Link 而不是父子关系。
5. Event 过多会增大 Span 体积，应控制数量或改为日志；验证时关注单个 Span 的平均事件数。

**相关知识点：** Span Event、Span Link、异常事件、扇入扇出、批处理关联、跨 Trace 关联。
<a id="gov-335"></a>
### 24. Span Status 有哪些取值？什么情况下应标记为 Error？

Span Status 有 **Unset、Ok、Error** 三个取值；默认 Unset，应在操作确认失败时显式设为 Error 并附描述，只有明确需要覆盖默认判断时才设 Ok。

1. 自动插桩通常按协议规则设置：HTTP 5xx 标记 Error，4xx 在 Server 端不标记。
2. 业务失败（如工具返回 success=false、模型输出未通过校验）需要手动设置 Error，否则错误率指标失真。
3. Error 时应记录 exception 事件，包含类型、消息和堆栈。
4. 不要把可预期的空结果或重试中的临时失败都标为 Error，以免造成告警噪声。
5. 错误 Span 比例是核心 SLI，也是尾部采样"保留全部错误 Trace"的判断依据。

**相关知识点：** Span Status、Unset/Ok/Error、exception 事件、错误率、尾部采样、业务失败。
<a id="gov-336"></a>
### 25. 在 Agent 中，一次用户请求通常会拆分成哪些 Span？

一次 Agent 请求通常拆为**入口 Span → 规划 Span → 若干 LLM Span、检索 Span、工具 Span → 验证 Span → 响应 Span**，形成一棵可能包含循环迭代的树。

1. 入口 Span（Server）记录用户、租户、任务类型和总耗时。
2. 规划/决策 Span（Internal）记录计划版本、选中的分支和重规划次数。
3. 每次模型调用一个 LLM Span（Client），记录模型、Token、TTFT、停止原因；ReAct 循环每轮各一个。
4. 检索 Span 记录查询、命中数、分数；工具 Span 记录工具名、参数摘要、状态和副作用。
5. 验证与输出 Span 记录校验结果和最终状态，用于区分"流程结束"与"任务成功"，并计算完成率。

**相关知识点：** 入口 Span、规划 Span、LLM Span、检索 Span、工具 Span、验证 Span、ReAct 循环。
<a id="gov-337"></a>
### 26. 如何在 Span 中记录一次 LLM 调用的模型、Token 用量和延迟？

在 LLM Span 上按 GenAI 语义约定**设置模型与参数属性、从响应中读取 Token 用量、用 Span 时间与事件记录延迟**，同时把这些值累加到指标。

1. 请求前设置 gen_ai.request.model、temperature、max_tokens；响应后设置 gen_ai.response.model 和 finish_reasons。
2. Token 用量来自 API 响应的 usage 字段，写入 gen_ai.usage.input_tokens/output_tokens，缓存命中的 Token 单独记录。
3. 总延迟由 Span 起止时间得出；流式响应用 Event 记录首 Token 时间以计算 TTFT。
4. 同步更新指标：Token 计数器、调用时长直方图，按模型和任务类型打 Label，用于成本核算与 P95 告警。
5. 优先使用官方或社区的 LLM SDK 自动插桩库，避免手写遗漏字段。

**相关知识点：** gen_ai.usage.input_tokens、gen_ai.request.model、TTFT、流式响应、Token 指标、LLM 自动插桩。
<a id="gov-338"></a>
### 27. 在 Span 中记录 Prompt 与 Response 全文有什么风险？如何处理？

全文记录会带来**隐私泄露、存储膨胀、合规与安全风险**，应默认关闭，按需以"脱敏摘要 + 外置引用"的方式记录。

1. Prompt 常含用户 PII、业务机密和系统提示词，落到追踪后端等于扩大敏感数据的暴露面。
2. 单次调用可达数万 Token，Span 体积暴涨会拖慢后端并抬高存储成本。
3. 处理方式：默认只记录长度、哈希和摘要；需要时开启内容捕获，经脱敏后写入独立加密存储，Span 保留引用。
4. 按租户与数据分级配置策略，设置较短的保留期，访问需审计。
5. 验证脱敏效果：定期抽样检查 Trace 中的 PII 命中率，目标为零。

**相关知识点：** 内容捕获、PII、脱敏、Artifact 外置、数据分级、保留期、审计。
<a id="gov-339"></a>
### 28. 什么是采样（Sampling）？Head-based 与 Tail-based 采样有什么区别？

采样是**只保留一部分 Trace 以控制成本**；Head-based 在 Trace 开始时决定，Tail-based 在 Trace 结束后根据完整信息决定。

1. Head-based 由 Root Span 随机或按比例决定（如 TraceIdRatioBased），决策随 traceparent 传播，实现简单、开销低。
2. 缺点是决策时不知道请求会不会出错或变慢，可能丢掉最有价值的 Trace。
3. Tail-based 在 Collector 汇聚整条 Trace 后按规则决定：错误、超时、高成本、特定租户全部保留，其余按比例。
4. Tail-based 需要缓存等待 Trace 完成，占用内存，并要求同一 Trace 路由到同一 Collector 实例。
5. 常见组合：Head 100% 上报、Tail 按策略保留，然后监控保留率与后端存储成本。

**相关知识点：** Sampling、Head-based Sampling、Tail-based Sampling、TraceIdRatioBased、ParentBased、保留率。
<a id="gov-340"></a>
### 29. 为什么 Agent 追踪常建议全量采样，或按错误、按慢请求采样？

Agent 请求**量相对少、单条价值高、失败方式多样**，随机丢弃会让评估、回放和根因分析缺少样本，因此通常全量保留，或至少全量保留错误、慢和高成本的轨迹。

1. Agent 的每条 Trace 都是潜在的评估样本和回放依据，随机采样等于扔掉评测数据。
2. 失败常发生在语义层，不会体现为异常，需要事后按验证结果决定保留，只能靠尾部采样。
3. 慢请求与高 Token 请求是成本优化的主要对象，必须完整保留。
4. 若量太大，可对成功且低成本的常规请求按比例抽样，同时保留其指标。
5. 采样策略应能按租户和任务类型配置，并监控被丢弃的错误 Trace 数量，目标为零。

**相关知识点：** 全量采样、尾部采样、错误优先、慢请求、评估样本、回放、成本优化。
<a id="gov-341"></a>
### 30. 如何通过 Trace 找出一次 Agent 请求中耗时最长的环节？

在 Trace 瀑布图中**按自身耗时排序、结合关键路径分析**，定位串行链上占比最大的 Span，再看其属性判断是模型慢、工具慢还是排队等待。

1. 区分总耗时与自身耗时：父 Span 长可能只是因为子 Span 多，应看排除子节点后的自身时间。
2. 关键路径算法找出决定总时长的串行链，并行分支中只有最长的一条影响结果。
3. 对 LLM Span 看 TTFT 与生成时长，判断是排队、首 Token 慢还是输出过长。
4. 对工具 Span 看重试次数、外部依赖延迟；Span 之间的空隙代表本地计算或阻塞。
5. 对同类请求做聚合分析，比较 P95 慢请求与正常请求在各阶段的耗时差异，得到系统性瓶颈。

**相关知识点：** 瀑布图、自身耗时、关键路径、TTFT、Span 空隙、P95 分析。
<a id="gov-342"></a>
### 31. 异步任务或消息队列场景下，如何保持 Trace 的连续性？

跨异步边界必须**在发送侧把 Trace 上下文写入消息头，在消费侧提取并创建 Consumer Span**；长生命周期任务用 Link 而不是父子关系关联。

1. 生产者创建 Producer Span，把 traceparent（和 Baggage）注入消息属性或 Header。
2. 消费者读取消息头恢复上下文，创建 Consumer Span；Kafka、RabbitMQ 等主流客户端有自动插桩支持。
3. 若消费延迟很长或一条消息触发多个任务，用 Span Link 关联生产 Span，避免父 Span 长期挂起。
4. 定时任务、重试队列、跨天续跑应生成新 Trace，并通过 Link 与 TaskID 关联旧 Trace。
5. 检查连续性可监控 Consumer Span 中缺少上游 Link 或父信息的比例。

**相关知识点：** 异步传播、Producer/Consumer Span、消息头注入、Span Link、TaskID、断链监控。

# 权限、隐私与合规

> 所属章节：[安全、治理与可观测性](README.md)｜本文件共 **33** 题。

<a id="gov-014"></a>
### 对于删文件、改代码、执行命令、提交代码、部署发布等不同工具操作，如何设计权限和风险控制？（DeepSeek一面）

应以**最小权限、操作分级、资源范围、执行验证、可恢复和审计**控制工具。模型只提出动作，Policy按身份、资源、环境和风险签发一次性授权。

1. 将读取、修改、删除、命令、提交、推送和部署定义为独立Action并默认拒绝；RBAC给基线，ABAC结合目录、分支、环境和授权判断。路径规范化以防越界。
2. 删除和改代码限于工作区，先展示Diff或清单，优先移入回收区并备份。禁止未知通配范围；批量、关键配置或保护目录操作需确认。
3. Shell在无特权沙箱执行，使用命令/参数白名单、资源限额、出口控制和变量隔离；禁止Shell拼接。危险命令和不可逆操作必须审批。
4. Commit在临时分支执行并要求测试、扫描和签名；Push只准指定远端与非保护分支。合并、生产发布和数据库迁移通过PR、审批、Canary及回滚。
5. 调用记录TaskID、用户、工具/策略版本、参数来源、风险、审批、前后状态和幂等键。执行后验证哈希、测试、提交SHA及部署健康；异常立即停止或回滚。

| 操作 | 默认风险 | 核心控制 |
|---|---|---|
| 读/局部改 | 低至中 | 目录范围、Diff、测试 |
| 删除/Shell | 高 | 清单、沙箱、审批 |
| Commit/Push | 中至高 | 临时分支、保护规则 |
| 生产部署 | 极高 | 双人审批、灰度、回滚 |

**相关知识点：** Least Privilege、RBAC、ABAC、Policy Engine、路径规范化、Shell沙箱、Branch Protection、Canary、审计日志。
<a id="gov-015"></a>
### 一个Agent可以读取知识库，查询数据库修改代码并调用外部系统、应该如何设计完整的权限和安全体系？（腾讯二面）

完整体系应采用**身份贯穿、最小权限、集中Policy、凭据隔离、沙箱、审批和审计**。动作同时受用户委托、Agent身份及资源策略约束。

1. 用户经SSO认证，任务携带UserID、Tenant、AgentID和Purpose。RBAC定义基线，ABAC依据资源、动作、数据等级和风险判定；权限取用户与Agent交集。
2. Tool Registry声明Action、资源、读写、Schema和风险。Policy调用前鉴权并签发短期、最小Scope令牌；模型和日志不接触长期密钥。
3. 知识库按租户、文档和字段过滤；数据库用只读视图、参数化SQL和行列权限；代码限制工作区与分支，Shell进沙箱；外部API使用Egress白名单。
4. 写入、删除、资金、权限、主分支和生产发布需Dry Run、Diff、风险评分及HITL，并使用幂等、事务和补偿。Prompt Injection不能改变Policy。
5. 记录TaskID、操作者、策略、参数来源、授权、审批、回执和副作用；日志脱敏。监控越权、批量访问和外传，自动降权。

| 资源 | 关键控制 |
|---|---|
| 知识库 | 文档/字段ACL、检索后过滤 |
| 数据库 | 只读视图、参数化、行列权限 |
| 代码/Shell | 目录与分支、沙箱、Diff |
| 外部系统 | Scope令牌、Egress、幂等审批 |

**相关知识点：** SSO、RBAC、ABAC、Policy Engine、短期凭据、检索越权、SQL沙箱、Egress、HITL、审计。
<a id="gov-019"></a>
### Guardrails 如何设计？

Guardrails应是**模型外的分层策略系统**，覆盖输入、上下文、输出、工具和副作用，在风险与业务SLO下执行可审计的允许、拒绝、改写或人工升级。

1. 建立Policy Taxonomy，定义内容、隐私、越权、合规和工具风险，并按租户、地区及场景版本化。硬规则不可被质量分抵消；灰区输出风险。
2. 输入层检测恶意内容、Injection、PII、密钥和文件风险；上下文做权限过滤、来源标签及指令隔离。检测器组合规则、分类模型和DLP，不能只靠同一LLM。
3. 工具层由Policy以RBAC/ABAC校验主体、资源、动作和Purpose，限制Schema、参数、频率、出口及凭据Scope。高风险写操作要求Dry Run、HITL、幂等和回滚。
4. 输出层验证Schema、引用、敏感信息、代码与内容策略；可修复问题局部重生成，高风险问题拒绝或转人工。模型解释不改变Policy。
5. 决策记录规则/模型版本、命中项、风险和处置。以漏拦截、误拦截、严重事件、额外P95和接管率评估，并经红队、Shadow和灰度更新。

| 层次 | 主要对象 | 典型动作 |
|---|---|---|
| 输入/上下文 | 内容、PII、注入 | 阻断、脱敏、隔离 |
| 输出 | 事实、格式、安全 | 验证、重写、拒答 |
| 工具 | 权限与副作用 | 限权、审批、回滚 |

**相关知识点：** Policy Taxonomy、Input/Output Guardrail、DLP、RBAC、ABAC、HITL、误报漏报、Red Team、策略版本化。
<a id="gov-021"></a>
### 如何保证 Tool 调用安全？

Tool安全的核心是**模型只提调用意图，执行层负责工具发现、权限、参数、隔离、副作用和验收**。Prompt、RAG或回执中的“授权”均无效，默认拒绝。

1. Registry登记ToolID、版本、Schema、Action、资源、读写和风险，只暴露任务所需白名单。执行器校验ID与版本，禁止模型构造URL、命令或未注册工具。
2. 调用前用Schema、枚举、范围、跨字段规则和来源追踪校验；Policy依据User、Tenant、Agent、Resource、Action和Purpose执行RBAC/ABAC。执行器注入短期Scope令牌。
3. 低风险只读可自动执行；写入、删除、资金、权限和生产动作须Dry Run、Diff、风险评分与HITL。写操作带幂等键并使用事务或补偿；未知状态先查询。
4. SQL使用参数化、只读副本、行列权限和限额；Shell在无特权沙箱运行，限制命令、路径、资源与出口；外部API经Egress、mTLS和DLP。
5. 响应Envelope包含状态、错误、数据、证据和副作用，执行后验证后置条件。审计记录身份、策略、参数来源、授权、审批和回执；越权与批量访问触发熔断。

**相关知识点：** Tool Registry、JSON Schema、RBAC、ABAC、短期凭据、Dry Run、幂等、Sandbox、Egress、Postcondition、Tool Audit。
<a id="gov-022"></a>
### Agent 如何进行权限控制？

Agent权限应采用**用户委托与Agent服务权限取交集、默认拒绝、按请求授权**。能调用工具不等于拥有全部权限，模型文本也不能提升权限。

1. SSO/IAM确认User、Tenant、Agent及服务身份，并携带TaskID。RBAC定义岗位基线，ABAC依据资源、Action、环境、数据等级和风险判定。
2. Tool Registry把能力拆成`read`、`update`、`delete`和`deploy`等Action，声明资源、Schema和风险。Policy在每次调用前重新鉴权。
3. 以短期、单次、最小Scope的Capability Token授权，绑定用户、Task、Tool、Action和资源；长期密钥存于Vault并由执行器注入。
4. 低风险只读可自动执行；删除、外发、资金、权限和生产操作要求HITL与职责分离。审批令牌不可跨任务复用，参数变化时重审。
5. 数据实施租户、文档和字段过滤，代码/Shell限制目录、分支、命令及出口。审计记录Policy、授权、审批和副作用；异常访问触发降权或熔断。

| 模型 | 作用 | 局限 |
|---|---|---|
| RBAC | 定义岗位基线 | 难表达动态上下文 |
| ABAC | 按属性动态判断 | 策略复杂 |
| Capability Token | 限定单次具体能力 | 需安全签发与撤销 |

**相关知识点：** IAM、RBAC、ABAC、Least Privilege、Policy Engine、Capability Token、Vault、职责分离、动态授权、审计。
<a id="gov-029"></a>
### Agent执行日志应该记录哪些字段？

Agent执行日志应能**重建决策、定位故障、核算成本并满足审计**，采用结构化Event并由TraceID贯通。

1. 身份与时间：TenantID、UserID、AgentID、TaskID、TraceID、SpanID、事件时间、环境、版本和部署批次。
2. 执行状态：StepID、节点类型、状态迁移、Attempt、起止时间、耗时、超时、Worker、Checkpoint及因果EventID。
3. 模型数据：Provider、Model、参数、Prompt版本、输入输出的安全引用、Token、缓存命中、FinishReason、过滤结果和首Token延迟。
4. Tool与RAG：工具版本、参数摘要、幂等键、权限决策、审批单、结果、错误码和外部RequestID；检索记录Query、索引版本、文档ID、Score及引用。
5. 治理数据：策略版本、RiskScore、验收结果、人工修改、取消原因、成本和保留级别；异常包含标准类型、阶段及可重试性。

日志写入前实施**字段白名单、脱敏、加密和完整性保护**，禁止保存密钥、Cookie、完整凭证及非必要个人信息。Schema应版本化并分层存储；正常事件可采样，错误、高风险和审批事件不得采样。

**相关知识点：** Structured Logging、Trace Context、Event Schema、PII脱敏、Schema Versioning、日志采样、审计日志、数据留存。
<a id="gov-044"></a>
### 如何设计Agent审计系统？

Agent审计系统应形成**主体、决策、动作、结果和证据**的不可抵赖链路，回答谁以何权限、依据何策略、对何资源做了什么。

1. 事件包含TenantID、Actor、Delegator、AgentID、TaskID、TraceID、时间、动作、资源、参数摘要、前后状态、RiskScore、PolicyVersion、审批单、Tool回执、结果及错误，并带SchemaVersion。
2. 在认证、授权、计划变更、工具调用前后、审批、权限提升、数据导出和取消处强制埋点；高风险操作记录资源版本、幂等键及回滚标识。
3. 事件脱敏后写入Append-only存储，通过Hash Chain、签名、WORM或对象锁保护完整性；传输与静态加密，应用管理员无权修改记录。
4. 查询按最小权限授权，租户严格隔离；查看敏感原文属于新的审计事件。保留期限、Legal Hold、删除例外与导出流程由数据分级和法规决定。
5. 检测异常授权、批量删除、高风险调用、审批绕过及日志断档，并关联Trace回放；告警包含证据和处置Runbook。

审计与业务日志应分离：前者追求完整性和合规证据，不可采样；后者侧重排障。定期验证覆盖率、时间同步、签名及恢复可读性。

**相关知识点：** Audit Trail、Append-only、WORM、Hash Chain、数字签名、Legal Hold、职责分离、数据留存。
<a id="gov-046"></a>
### Tool调用如何做审计和回放？

Tool调用应具备**不可抵赖审计与无副作用回放**。审计回答谁在何授权下执行了什么，回放重建输入、策略和结果。

1. 调用前记录Actor、Tenant、Agent、Task、Trace、Tool版本、参数Hash、目标资源、RiskScore、PolicyVersion、授权、审批单、幂等键和预期副作用。
2. 调用后记录时间、Attempt、外部RequestID、状态码、标准错误、响应Hash、回执引用、资源前后版本和状态。参数与响应先脱敏，密钥及Cookie禁止落库。
3. 审计事件写入Append-only或WORM存储，以EventID、Sequence、Hash Chain和签名保护完整性；访问原文必须授权并再次审计。
4. 回放默认使用录制响应，按事件顺序驱动状态机，不访问生产系统。重新执行须进入沙箱，采用Mock、只读凭证或Dry-run，阻断支付、发布、删除和写库。
5. 读操作校验工具版本、参数Hash和数据快照；写操作使用幂等键、查询接口和补偿记录判断状态。超时且结果未知时不得直接重试。

回放生成ReplayID并链接原Trace，比较状态、响应Schema、Artifact Hash和验收结果；版本缺失时标记部分可复现，原证据不得覆盖。

**验证指标：** 误报率、漏报率、策略绕过率、告警恢复时间和审计覆盖率。

**相关知识点：** Audit Event、WORM、Hash Chain、Record/Replay、幂等键、Dry-run、副作用隔离、ReplayID。
<a id="gov-060"></a>
### Agent可观测平台整体架构如何设计？

整体架构采用**采集、处理、存储、分析、呈现与治理**六层，统一Trace、Metric、Log、Evaluation和Artifact，并以TaskID、TraceID连接。

1. 采集层由Instrumentation SDK覆盖Gateway、Workflow、模型、RAG、Tool、消息及人工；HTTP/RPC自动埋点，Prompt、规划与验收手工埋点。
2. 处理层以Collector和消息总线承接，完成Batch、背压、Schema校验、脱敏、采样、租户路由和缓存；错误、高风险及审计事件不可采样。
3. Metrics进时序库，Trace/Log进检索库，审计进WORM，大对象进加密对象库，评测进分析仓库；元数据目录维护血缘与保留策略。
4. 分析层构建SLO、DAG进度、Failure Taxonomy、根因、质量、成本、版本对比和异常检测；流处理告警，批处理分析趋势。
5. 应用层提供总览、Trace瀑布、Prompt/RAG/Tool钻取、回放、审计和A/B分析，并由Policy控制字段访问、租户隔离及导出。

平台需具备容灾、冷热分层、容量治理和查询限流，并监控Collector丢弃、断链、数据延迟和单位观测成本；Telemetry故障不得阻塞业务。

**相关知识点：** OpenTelemetry、数据分层、流批一体、SLO、WORM、Failure Taxonomy、成本归因、多租户治理、冷热存储。
<a id="gov-077"></a>
### 哪些操作必须人工审批？

是否审批应由**不可逆性、权限、数据级别、影响范围和可恢复性**决定。可能造成重大财务、生产、安全或合规后果且难以回滚的操作必须审批。

1. 生产变更：主分支合并、生产部署、扩大灰度、修改网络/IAM/密钥、关闭安全策略及不可自动回滚的基础设施操作。
2. 数据与财务：数据库DDL、无严格范围的DML、批量删除或导出、访问高敏文档、跨境传输、支付、退款、转账、采购和额度调整。
3. 外部影响：代表用户发送邮件或公告、提交法律文件、对客户作承诺、发布内容、创建账户及触达真实人员的动作。
4. 高权限与高风险工具：Shell危险命令、管理员权限、临时提权、绕过Guardrail、修改审计日志、安装未知依赖，及Prompt Injection或RiskScore超过阈值的请求。
5. 状态不确定的操作：超时Unknown后再次写入、补偿失败、资源版本冲突、计划被修改，以及低置信但后果严重的决策。

审批展示动作、目标、参数Diff、影响、RiskScore、证据、回滚和有效期，并绑定TaskID、资源版本及参数Hash；变化后重审。低风险、可逆且受限操作可自动执行。

**验证指标：** 误报率、漏报率、策略绕过率、告警恢复时间和审计覆盖率。

**相关知识点：** Human-in-the-Loop、Risk Score、不可逆操作、Four-eyes Principle、参数绑定、临时提权、审批有效期、最小权限。
<a id="gov-080"></a>
### Agent和人工决策冲突时如何处理？

冲突处理遵循**法律与Policy最高、授权人工优先、Agent提供证据**。人工不能绕过安全规则，其权限与审批范围仍需校验。

1. 识别事实、目标、方案、风险、权限或合规冲突，将双方主张、依据、置信度、影响和可逆性结构化，禁止争论文本直接驱动执行。
2. Policy Engine先裁决硬约束。人工要求若违反法律、租户边界、最小权限或安全门禁，系统必须拒绝；普通方案分歧由授权人工Override。
3. 高风险Override展示参数Diff、RiskScore、影响、证据和回滚，并执行双人审批；决定绑定TaskID、资源版本、参数Hash和有效期，变化后重审。
4. Agent发现新证据可提出一次Challenge或替代方案，但不得循环阻挠。人工决定后生成新DAGVersion，从Checkpoint继续，旧验收和审批按影响失效。
5. 人工之间冲突按职责矩阵、资源Owner和升级链处理，裁决前暂停高风险步骤；Break-glass须限时、最小范围并事后复核。

审计记录Agent建议、人工理由、证据、Policy、Override和结果；分析Override成功率与事故，持续优化策略。

**相关知识点：** Human Override、Policy Precedence、Challenge Protocol、Four-eyes Principle、Break-glass、职责矩阵、DAG Version、审计。
<a id="gov-084"></a>
### 数据库变更Agent如何实现风险控制？

数据库变更Agent应采用**默认只读、双重校验、审批绑定、受控执行和可验证回滚**。模型只生成候选，生产执行由确定性组件完成。

1. 使用短期最小权限凭证，按环境、库、表和动作限制；读写账户分离，生产DDL、批量DML和敏感访问必须审批。
2. SQL经Parser生成AST，拒绝多语句、危险函数和越界对象；Policy检查Allowlist、WHERE、LIMIT、影响行数、锁、扫描量和变更窗口。
3. 在影子库执行Explain、Dry-run与兼容测试，估算行数、耗时、锁和复制延迟。DDL优先Online Schema Change和Expand/Contract。
4. 审批展示规范化SQL、参数、目标、影响、备份/回滚和RiskScore，并绑定QueryHash与资源版本；变化后重审，高风险双人批准。
5. 执行器设置事务、Statement/Lock Timeout、行数上限、并发和Kill Switch，分批提交并监控。DML使用幂等键；超时Unknown先查事务状态。

执行前验证备份，执行后核对行数、约束、复制和一致性；审计记录Actor、审批、SQL Hash、参数摘要、Schema、回执及回滚。

**相关知识点：** SQL AST、Least Privilege、Online Schema Change、Expand/Contract、Dry-run、QueryHash、Lock Timeout、PITR、变更审计。
<a id="gov-086"></a>
### 如何设计一个统一的Agent审计平台？

统一审计平台应建立**跨Agent、模型、RAG、Tool和审批的一致事件规范**，形成主体—授权—动作—资源—结果—证据链，并与运行日志分离。

1. Audit Schema包含Tenant、Actor、Delegator、Agent、Task、Trace、时间、Action、Resource、参数Hash、RiskScore、PolicyVersion、ApprovalID和结果。
2. SDK与Gateway采集认证、授权、计划变更、工具调用、人工干预、提权、数据导出、发布、取消和补偿；关键事件不得关闭。
3. 入口完成规范化、去重和脱敏，正文存对象库。事件写入Append-only/WORM，以Sequence、Hash Chain和签名保护，管理员也不能篡改。
4. 支持按TaskID、TraceID、Actor、Resource和ApprovalID检索，提供时间线、Diff和证据导出；字段级RBAC、租户隔离及访问审计防泄露。
5. 检测越权、审批绕过、批量危险操作、跨租户访问和日志断档；告警可冻结凭证、暂停任务或转人工，但不可删除证据。

治理层维护事件覆盖、留存、Legal Hold和合规导出；持续验证签名、恢复可读性、丢失率与成本，并进行取证演练。

**相关知识点：** Audit Schema、Append-only、WORM、Hash Chain、数字签名、Legal Hold、字段级RBAC、取证、职责分离。
<a id="gov-091"></a>
### 如何构建企业级可审计Agent平台？

企业级平台要实现**身份可追溯、授权可解释、动作可回放、记录不可篡改**，治理必须位于模型和Tool之外。

1. 身份层接入SSO/IAM，区分User、Agent和Service；使用短期凭证，RBAC＋ABAC计算权限并记录PolicyVersion。
2. 执行层以DAG和状态机编排，模型、Prompt、RAG、Tool、审批和人工修改关联TaskID、TraceID及Artifact；高风险动作经Policy与HITL。
3. 审计层记录Actor、Action、Resource、状态、风险、授权、Tool回执和结果，写入Append-only/WORM，以Sequence、Hash Chain和签名保护。
4. 证据层保存PromptVersion、模型、索引、工具Schema、代码、内容Hash和Checkpoint；敏感正文存对象库，实行字段权限和租户隔离。
5. 平台提供时间线、Trace、DAG、Diff、审批和Replay，支持合规导出、Legal Hold及取证；检测越权、审批绕过、跨租户访问和日志断档。

治理定义数据分类、留存、职责分离、Break-glass和审计SLO；定期验证签名、权限及事件完整率，并进行取证演练。

**相关知识点：** SSO/IAM、RBAC/ABAC、Policy Gate、WORM、Hash Chain、Artifact Lineage、Legal Hold、职责分离、可审计性。
<a id="gov-114"></a>
### Agent日志体系应该记录哪些关键数据？

Agent日志应同时支持**故障定位、质量评估、安全审计和成本核算**，采用结构化事件而非拼接文本，并以TaskID、TraceID、SpanID和StepID贯穿全过程。

1. 请求层记录时间、入口、租户、用户或服务主体、会话、任务类型、环境、Agent版本及请求摘要；敏感原文保存加密引用，不直接落入普通日志。
2. 决策层记录计划版本、步骤、状态迁移、路由原因、模型与Prompt版本、参数、Token、延迟、重试、停止原因和置信度，支持复现“为何如此决策”。
3. RAG记录查询改写、索引与Embedding版本、过滤条件、文档ID、ChunkID、召回分数、重排结果和引用；Tool记录名称、版本、权限决策、参数摘要、幂等键、外部请求ID、返回码与耗时。
4. 多Agent记录发送者、接收者、MessageID、CausationID、委派目标和汇聚结果；人工环节记录审批人、策略、理由及时间，最终保存ArtifactID、验证结果和用户反馈。
5. 安全字段包含策略命中、风险分、越权、注入检测和审计事件；运行字段包含错误类型、堆栈指纹与成本。

日志Schema必须版本化，访问受RBAC控制并设置留存期限；对密钥、个人信息和业务机密执行采集前脱敏，建立完整性校验，且禁止将高基数字段滥用为监控标签。

**相关知识点：** 结构化日志、关联标识、数据血缘、审计日志、PII脱敏、Schema版本、日志分级、留存策略、幂等键。
<a id="gov-120"></a>
### 如何避免Agent评测指标被"刷高"？

防止指标被刷高的核心是让Agent团队**无法通过改变样本、口径、裁判或成本边界获得虚假收益**，并以多指标、盲测和审计约束Goodhart效应。

1. 在实验前冻结成功定义、分母、排除规则、主指标、护栏和停止条件；取消、超时、人工改写及降级任务必须明确归属，禁止把困难请求转为“无效样本”。
2. 评测集划分开发集、回归集和不可见保留集，保留集由独立平台托管并定期轮换；混入生产回放、长尾和对抗样本，使用哈希与近重复检测防止训练数据泄漏。
3. 不使用单一总分。完成率必须同时受安全违规、事实错误、人工介入、延迟和单次成功成本约束，并按任务类型、难度及风险分层，防止用简单任务或无限重试抬高均值。
4. Judge采用结构化Rubric、候选顺序随机、版本隐藏和多裁判仲裁；定期以人工盲审计算一致性、偏差和误判率。涉及代码、数据库或工具副作用时优先采用确定性验证。
5. 平台保存模型、Prompt、知识库、Tool、种子、Trace和评分版本，自动检查异常提分、样本缺失、SRM、重复答案及评测调用；评测规则与生产目标由独立角色审批。

最终以线上A/B业务终态验证离线提升，并抽查失败与“成功”样本。任何通过扩大预算、增加人工或降低安全门槛获得的提升，都应在净效益中扣除而非计作能力增长。

**相关知识点：** Goodhart定律、数据泄漏、隐藏测试集、盲测、护栏指标、分层评测、Judge校准、SRM、评测治理、审计追踪。
<a id="gov-153"></a>
> **题目合并：** `GOV-153` 已并入 [TOOL-057 · 如何设计Tool的权限模型？](../../02-capabilities/tools-skills-mcp/sandbox-security-1.md#tool-057)。

<a id="gov-154"></a>
> **题目合并：** `GOV-154` 已并入 [TOOL-058 · RBAC与ABAC分别适用于哪些场景？](../../02-capabilities/tools-skills-mcp/sandbox-security-1.md#tool-058)。

<a id="gov-157"></a>
> **题目合并：** `GOV-157` 已并入 [TOOL-061 · 风险评分如何影响Agent的执行策略？](../../02-capabilities/tools-skills-mcp/sandbox-security-1.md#tool-061)。

<a id="gov-159"></a>
> **题目合并：** `GOV-159` 已并入 [TOOL-063 · 如何避免Agent误删代码或误删文件？](../../02-capabilities/tools-skills-mcp/sandbox-security-1.md#tool-063)。

<a id="gov-162"></a>
> **题目合并：** `GOV-162` 已并入 [TOOL-066 · MCP工具调用过程中如何进行权限校验？](../../02-capabilities/tools-skills-mcp/mcp.md#tool-066)。

<a id="gov-163"></a>
> **题目合并：** `GOV-163` 已并入 [TOOL-067 · Tool调用前、中、后分别需要做哪些安全检查？](../../02-capabilities/tools-skills-mcp/sandbox-security-1.md#tool-067)。

<a id="gov-168"></a>
### 如何设计Agent的部署发布权限？

部署权限应将**生成、批准、执行和验证**拆为不同能力，以环境分级、短期凭证和门禁防止Agent独立完成高风险闭环。

1. Agent默认只构建制品、生成计划和提交请求；开发可限额自动发布，测试需通过CI，生产由受控服务或授权人员执行，Agent不持有长期凭证。
2. 权限细化到应用、环境、区域、版本、动作和时间，取用户授权、Agent上限、任务委托与组织策略交集；回滚、流量切换和迁移分别授权。
3. 制品来自受信CI，具有不可变Digest、签名、SBOM、来源证明并通过扫描；请求绑定Digest、配置Diff、目标和审批，变化后批准失效。
4. 生产发布使用JIT身份、双人审批和职责分离，限制窗口与爆炸半径；先Dry Run，再Canary或蓝绿放量，设置SLO和自动回滚阈值。
5. 执行器强制策略，Agent只调用高层Deploy API，不能获得集群管理员或任意Shell；密钥由Vault注入，网络和资源受限。

发布后Verifier检查版本、健康、业务和迁移终态，失败自动回滚；审计记录主体、制品、环境、审批和结果。Break-glass需限时、审计并复盘。

**历史别名：** `TOOL-072`。

**相关知识点：** 职责分离、环境分级、Just-in-Time、制品签名、SBOM、来源证明、Canary、蓝绿发布、自动回滚、Break-glass。
<a id="gov-171"></a>
> **题目合并：** `GOV-171` 已并入 [TOOL-075 · 如何设计完整的Tool Audit Log？](../../02-capabilities/tools-skills-mcp/reliability.md#tool-075)。

<a id="gov-173"></a>
### 企业级Agent如何满足安全合规要求？

企业Agent合规需建立**风险评估—控制实施—证据留存—持续审计**的可验证体系，并按行业、地区和数据类型映射要求。

1. 建立资产、数据流和处理清单，明确来源、目的、存储地、共享方及供应商；进行数据分级、威胁建模、隐私和第三方风险评估。
2. 身份权限采用SSO、MFA、RBAC与ABAC、最小权限、职责分离和JIT凭证；用户、Agent与服务身份分离，Tool由Policy Engine按任务授权。
3. 数据治理落实目的限制、最小化、留存与删除；传输和静态加密，密钥由KMS托管，Prompt、日志、Embedding及备份执行脱敏、隔离和跨境控制。
4. 安全覆盖注入、越权、外泄、供应链和沙箱逃逸；高风险副作用使用审批、Dry Run、幂等与回滚，版本变更经过评测、红队及门禁。
5. 审计保存主体、授权、输入摘要、决策、Tool、审批、版本和终态，采用不可变存储；建立告警、事件响应、取证和灾难恢复。

将控制映射到适用法规和标准，定期做权限复核、渗透测试、供应商审查与独立审计；提供透明说明、人工申诉和自动决策边界。

**历史别名：** `TOOL-077`。

**相关知识点：** 数据分级、DPIA、威胁建模、最小权限、职责分离、KMS、数据驻留、审计证据、事件响应、第三方风险。
<a id="gov-174"></a>
> **题目合并：** `GOV-174` 已并入 [TOOL-078 · 如何设计统一的Policy Engine管理所有工具权限？](../../02-capabilities/tools-skills-mcp/sandbox-security-1.md#tool-078)。

<a id="gov-175"></a>
### 如何实现动态授权和临时权限提升？

动态授权应采用**JIT、任务绑定、短时有效、可立即撤销**的能力令牌，由可信策略与审批触发，模型无权为自己提权。

1. Agent以低权限身份提交请求，包含用户、Agent、租户、TaskID、资源、动作、理由、风险、参数哈希、次数和TTL；Policy Engine验证权限与策略。
2. 根据风险自动批准、确认或双人审批。生产删除、资金、外发和授权变更要求职责分离；Hard Deny不能通过临时提升获得。
3. 签发短期、最小、不可转授的Token，绑定主体、任务、Tool、资源、动作、参数哈希、次数和有效期；凭证由Vault注入，不进入Prompt。
4. Tool网关与目标系统每次校验令牌、策略和资源归属，防止重放、跨租户和参数替换；高风险写入还需幂等键、Dry Run及终态验证。
5. 任务结束、审批撤回、风险升高或策略变化时立即撤销；缓存短TTL并支持失效。崩溃后不自动恢复高权令牌。

审计记录请求、决策、审批、令牌ID、使用、撤销和副作用，分析权限利用率；通过时间漂移、重放、参数篡改和转授测试验证边界。

**历史别名：** `TOOL-079`。

**相关知识点：** Just-in-Time、Capability Token、参数绑定、TTL、职责分离、Vault、Token撤销、重放防护、最小权限。
<a id="gov-178"></a>
### 如何设计Agent的多租户权限隔离？

多租户隔离应将TenantID作为**可信身份属性和资源访问强制边界**，在身份、数据、运行与观测层重复校验，不能依赖模型添加租户条件。

1. 用户、Agent、服务账户和令牌绑定TenantID，身份来自SSO或可信Token；权限取用户、Agent、任务委托与租户策略交集，禁止跨租户转授。
2. 数据库采用独立实例、Schema或行级安全；对象存储、向量索引、缓存、消息、Artifact和备份都含租户边界，并由服务端过滤。
3. Tool使用规范化ResourceID，Policy Engine校验主体租户、资源归属、动作和参数；服务端拒绝客户端任意TenantID。跨租户运维需受控角色和审批。
4. 按租户或任务隔离容器、卷、网络、队列、会话和密钥；设置CPU、Token、并发及速率配额，防止资源抢占。外部Tool使用专属连接或代理。
5. 日志、Trace、评测集和导出按租户控制与脱敏；审计记录主体、租户、资源、策略和终态，对跨租户拒绝告警。

通过随机TenantID、缓存投毒、向量越权、备份和管理员绕过测试验证。高敏租户可使用专属密钥与物理隔离，删除覆盖所有副本。

**历史别名：** `TOOL-082`。

**相关知识点：** TenantID、行级安全、命名空间、资源归属、Policy Engine、租户专属密钥、资源配额、侧信道、跨租户测试。
<a id="gov-181"></a>
### 企业级Agent权限体系如何与企业现有IAM、SSO和审批流程集成？

集成原则是**复用企业身份、保持Agent独立主体、统一策略映射权限、审批签发短期能力**，避免平台复制账户和长期凭证。

1. 通过OIDC或SAML接入SSO，继承MFA、条件访问和用户生命周期；从IAM同步用户、组织与组，再转换为平台RBAC角色和Capability。
2. 为Agent、服务和Tool建立Workload Identity，使用短期Token或mTLS；权限取用户授权、Agent上限、任务委托和组织策略交集，Agent不得冒充用户。
3. Policy Engine结合IAM角色、资源、数据级别、租户、环境、风险和审批做ABAC；PDP集中治理，网关、Tool Proxy及目标系统作为PEP。
4. 高风险调用向ITSM创建工单，附目标、参数哈希、Diff、风险和回滚；回调须验签、防重放，并签发绑定Task、Tool、资源、动作和TTL的JIT令牌。
5. 离职、组变更、会话吊销、工单撤回和风险变化触发令牌与缓存失效；Break-glass采用独立流程、强认证和复盘。

审计关联企业用户、Agent、TaskID、IAM会话、Policy、工单、令牌和副作用，并回传SIEM。上线前测试SCIM延迟、审批篡改、跨租户和撤销。

**历史别名：** `TOOL-085`。

**相关知识点：** IAM、SSO、OIDC、SAML、SCIM、Workload Identity、PDP/PEP、JIT授权、ITSM、SIEM、职责分离。
<a id="gov-183"></a>
### 如何区分Agent的权限和用户本人的权限？

用户与Agent是**独立安全主体**：用户权限表示业务授权，Agent权限表示自动化上限；调用取二者与任务策略的交集。

| 权限 | 表达内容 | 典型凭证 |
|---|---|---|
| 用户权限 | 可访问的业务资源 | SSO Token |
| Agent权限 | 自动化能力上限 | Workload Identity |
| 任务委托 | 本次动作、资源、期限 | Capability Token |

1. 用户通过SSO、MFA认证，Agent使用Workload Identity；日志记录用户与Agent，禁止共享Cookie或冒充用户。
2. Policy Engine计算用户授权、Agent上限、任务委托和组织策略的交集。用户能做但Agent被禁的操作需人工；用户无权的资源拒绝。
3. 任务委托绑定TaskID、Tool、动作、资源、参数哈希和TTL，不能转授或跨租户；子Agent不超过父级，参数变化后重授权。
4. 低风险签发短期令牌，高风险由审批平台签发JIT能力；Vault注入密钥，目标系统校验双重身份与资源归属。
5. 审计记录用户意图、Agent决策、策略、审批、调用和终态，支持分别撤销三类凭证。

用户离职、角色变化或审批撤回使授权失效；Agent异常可单独降权。

**相关知识点：** User Identity、Workload Identity、Effective Permission、权限交集、任务委托、Capability Token、JIT、双重审计。
<a id="gov-188"></a>
### 如何设计Agent工具调用的审计日志？

工具审计日志应形成**授权、执行与业务副作用的完整证据链**，回答主体、意图、资源、时间和结果，同时避免日志泄露。

1. 记录可信用户、Agent与服务身份、TenantID、TaskID、TraceID、SpanID和CallID；用户与Agent分别标识，不用模型生成的身份。
2. 记录Tool、版本、Schema、动作、ResourceID、任务目的、风险、Policy、Permit或Deny、命中规则和审批；审批绑定参数哈希、资源与TTL。
3. 记录请求Schema、参数哈希、幂等键、RequestID及脱敏摘要。密码、Token、密钥、PII和机密不得明文入库，必要时存加密Artifact。
4. 记录时间、环境、Attempt、重试、超时、返回码、错误、响应摘要、Dry Run和Diff；写操作保存影响数、终态、补偿、回滚与人工覆盖。
5. 异步调用分别记录受理和完成，以CausationID关联；状态未知时保留查询证据，不能只凭HTTP 2xx标记成功。

日志使用统一Schema、追加写、哈希链或WORM，加密并按租户隔离，设置RBAC、留存与法务保全；访问本身也留痕，对缺失、篡改和高风险序列告警。

**相关知识点：** Audit Log、WORM、哈希链、数据最小化、参数哈希、业务终态、CausationID、法务保全、访问审计。
<a id="gov-189"></a>
### RBAC和ABAC在Agent权限体系中如何选择？

Agent权限通常不应二选一，而应**RBAC确定稳定基线，ABAC结合上下文动态收窄**；只有简单场景才可单用RBAC。

| 选择维度 | RBAC | ABAC |
|---|---|---|
| 依据 | 角色与权限映射 | 主体、资源、动作、环境属性 |
| 优势 | 易理解和审计 | 细粒度、可表达风险 |
| 风险 | 角色爆炸、授权过宽 | 策略复杂、依赖属性质量 |

1. 岗位和Tool类别稳定，如客服只读工单、研发读仓库，可用RBAC确定候选Capability；生产写入不宜仅靠宽角色授权。
2. 需要租户、数据级别、资源归属、环境、时间、任务、风险或审批时使用ABAC，例如仅在审批期内发布指定版本。
3. 权限取用户授权、Agent上限、任务委托和组织策略交集；RBAC产出候选权限，ABAC按规范化资源与参数做Permit、Deny或RequireApproval。
4. 显式Deny和Hard Deny优先，属性缺失时默认拒绝。策略应代码化、版本化，具备测试、冲突检测、Canary和决策审计。
5. 当角色快速增长、例外频繁或相同角色因资源与风险需不同权限时，将动态条件迁移到ABAC；稳定岗位关系仍保留RBAC。

最终以可解释性、策略复杂度、决策延迟、误拦截和越权事件评估组合效果。

**相关知识点：** RBAC、ABAC、Capability、角色爆炸、属性治理、权限交集、Policy Engine、默认拒绝、策略即代码。
<a id="gov-190"></a>
### 多租户Agent平台如何做数据隔离？

多租户隔离应覆盖**业务数据、向量、记忆、缓存、日志、Artifact、备份和上下文**，TenantID由可信身份注入并在各层校验。

1. 按敏感度选择独立实例、Schema或共享表行级安全；共享模式中TenantID为主键组成，数据库启用RLS与服务端过滤，禁止模型拼接条件。
2. 对象存储使用租户桶或前缀，向量库使用租户命名空间与检索前过滤，缓存Key、消息、记忆、Artifact和队列均含TenantID，避免串租。
3. 用户、Agent和服务身份绑定租户，Policy Engine校验主体、资源归属和动作；跨租户运维使用独立角色、JIT凭证与双人审批，普通Agent设Hard Deny。
4. 执行环境隔离容器、卷、网络、密钥与临时文件；高敏租户使用专属KMS密钥或物理集群。备份、恢复、导出和删除保持同样边界。
5. 日志与Trace只存脱敏摘要或加密引用；Prompt组装前检查Chunk、记忆和Tool结果租户，模型输出经DLP检测，防止上下文混入与外发。

设置CPU、Token、并发和存储配额防邻居干扰。通过随机TenantID、缓存投毒、向量越权、消息重放、备份和管理员绕过测试，对跨租户拒绝告警。

**相关知识点：** TenantID、RLS、命名空间、权限感知缓存、租户密钥、数据驻留、DLP、侧信道、备份隔离、Hard Deny。

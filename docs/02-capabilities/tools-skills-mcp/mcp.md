# MCP 与协议接入

> 所属章节：[工具、Skills 与 MCP](README.md)｜本文件共 **23** 题。

<a id="tool-002"></a>
### 如何自定义工具供给大模型调用，开发工具的关键参数、完整实现流程（Agent初级）

自定义工具是把函数或外部服务封装为 **模型可理解、平台可校验、运行可控制** 的标准能力。

1. **定义契约**：设置唯一的 `name`，在 `description` 中写明用途、触发条件和禁用场景；用 JSON Schema 描述类型、必填项、枚举、范围及格式。
2. **实现工具**：执行函数负责业务校验、身份透传、下游调用和异常转换，统一返回 `success、code、data、message、retryable`；写操作增加幂等键或事务。
3. **注册与调用**：元数据进入 Registry，经 Schema、权限和连通性检查后注入模型候选集。模型生成 Tool Call，Executor 再校验参数与权限，执行后回传标准结果。
4. **测试与发布**：覆盖正常值、边界值、恶意输入、超时和重复调用；灰度观察选择准确率、参数正确率、业务成功率和延迟，异常时回滚。

| 关键参数 | 主要作用 | 设计要求 |
|---|---|---|
| `name`、`description` | 工具选择 | 语义明确、边界清晰 |
| `parameters` | 生成入参 | 使用枚举、范围和格式 |
| `timeout`、`risk_level` | 可靠性与审批 | 写、删操作提高等级 |

完整链路为 **契约设计→函数实现→Schema生成→注册审核→工具选择→校验鉴权→执行回传→监控迭代**。描述决定模型能否选对工具，确定性校验保障执行安全。

**相关知识点：** Function Calling、JSON Schema、Tool Registry、Tool Executor、结构化返回、幂等性、灰度发布。
<a id="tool-014"></a>
> **题目合并：** `TOOL-014` 已并入 [TOOL-048 · MCP与Function Calling有什么区别？](#tool-048)。

<a id="tool-016"></a>
### Tool 如何实现动态发现？

Tool 动态发现应形成 **能力发布、目录同步、权限过滤、候选检索、执行复核** 的闭环，使工具可热更新且受治理。

1. **能力发布**：工具启动或变更时向 Tool Registry 或 MCP Server 发布名称、描述、输入输出 Schema、版本、标签、风险等级和健康检查地址；注册端完成来源、签名、Schema 与兼容性检查。
2. **目录同步**：Agent 可按需拉取目录，也可订阅新增、升级、下线事件。客户端使用版本号、ETag 和 TTL 缓存，接收变更事件后精确失效，避免频繁全量加载。
3. **候选发现**：先按租户、用户权限、环境、版本和健康状态进行硬过滤，再使用标签、BM25 和向量检索召回工具，按相关度、成功率、延迟、成本和风险排序。
4. **调用确认**：模型选择工具后，Executor 在执行前重新解析逻辑名称，复核工具版本、健康、授权和参数 Schema；已下线或熔断的工具切换备用版本或要求重新规划。

| 发现机制 | 优点 | 适用场景 |
|---|---|---|
| Registry拉取 | 集中治理、实现简单 | 企业内部稳定工具 |
| 事件订阅 | 变更及时、流量较小 | 工具频繁发布下线 |
| MCP枚举 | 协议统一、跨应用复用 | 外部Server能力接入 |

动态发现只解决“候选能力如何更新”，实际执行仍必须经过鉴权、限流、风险审批和审计。生产环境还需灰度版本与废弃周期，防止热更新破坏在途任务。

**相关知识点：** 动态发现、Tool Registry、MCP、事件订阅、ETag、TTL、权限过滤、健康检查。
<a id="tool-019"></a>
### Tool Calling 与 Function Calling 有什么区别？

两者在模型 API 中常互换使用。严格区分时，**Function Calling 是生成结构化函数参数的机制，Tool Calling 是更广义的工具调用体系**。

| 维度 | Function Calling | Tool Calling |
|---|---|---|
| 关注点 | 函数名与结构化参数 | 工具从选择到结果回传的全流程 |
| 能力形态 | 以函数定义为主 | HTTP、数据库、Shell、MCP等 |
| 治理范围 | 主要约束模型输出 | 鉴权、审批、限流、重试、审计 |

1. **模型层**：开发者提供描述和 JSON Schema，模型返回调用意图，不会自动执行代码。此时两者基本同义。
2. **平台层**：广义 Tool Calling 还包括 Registry、候选检索、参数校验、Policy Engine、Executor、Adapter 和结果标准化。
3. **执行层**：函数只是工具的一种实现；工具还可采用 API、数据库、沙箱或 MCP，均需统一超时、幂等和错误模型。
4. **设计边界**：模型负责建议调用及参数；确定性系统负责授权、执行和结果校验，不能因输出符合 Schema 就跳过业务检查。

讨论模型接口时二者可视为近义词；讨论企业架构时，Tool Calling 表示完整体系，Function Calling 表示结构化交互机制。

**验证指标：** 工具选择准确率、调用成功率、参数错误率、P95 延迟和失败恢复率。

**相关知识点：** Function Calling、Tool Calling、JSON Schema、Tool Registry、Policy Engine、Tool Executor、MCP。
<a id="tool-031"></a>
### 如何接入 HTTP、本地函数、数据库、Shell、Python、MCP 等不同类型工具？

不同工具应通过 **统一 Tool SPI 加类型 Adapter** 接入：Adapter 封装协议差异，Executor 统一实施安全与可靠性策略。

1. **统一 SPI**：定义 `validate、execute、cancel、healthCheck`。输入含版本、参数、身份、Deadline、幂等键和 Trace，输出统一业务状态、数据与错误。
2. **类型适配**：HTTP 管理连接与认证；数据库使用参数绑定和事务；Shell/Python 在沙箱运行；MCP 处理会话、发现和协议转换。
3. **共性治理**：所有 Adapter 共用 Schema 校验、授权、限流、超时、重试、熔断、脱敏和审计，不得绕过策略或暴露凭据。
4. **生命周期管理**：Registry 保存 `tool_type`、端点、版本和健康，由工厂解析 Adapter。实例支持连接复用、取消和热更新；在途任务固定版本。

| 类型 | 关键风险 | 专用控制 |
|---|---|---|
| HTTP/MCP | 网络故障、远端不可信 | TLS、超时、内容检测 |
| 数据库 | 注入、误写、锁表 | 参数绑定、事务、行数上限 |
| Shell/Python | 逃逸、资源耗尽 | 微虚机、配额、网络隔离 |

新增类型只需实现 SPI 并通过契约测试，无需修改 Planner；指标按 Adapter 类型分桶。

**相关知识点：** Tool SPI、Adapter模式、连接池、参数绑定、沙箱、MCP Client、契约测试、热更新。
<a id="tool-042"></a>
### MCP 在 Agent 工具调用体系中解决了哪些问题？

MCP 解决 **接入协议不统一、发现静态、连接器重复开发和上下文难复用**，使 Host 与外部系统按 Client/Server 协作。

1. **统一接入**：Server 暴露 Tools、Resources 和 Prompts，Client 负责协商、调用和通知；不同宿主无需为每个数据源重做接口。
2. **运行时发现**：Client 可列举能力及 Schema 并感知变化，减少静态配置；Host 仍需按用户权限过滤。
3. **边界分离**：Resource 表达可寻址上下文，Tool 表达动作，Prompt 表达模板，使读取与副作用分开治理。
4. **生命周期解耦**：工具服务可独立部署和版本化，Agent 经协议复用；新增 Server 无需修改模型接口层。

| 传统集成问题 | MCP提供的机制 | 仍需宿主负责 |
|---|---|---|
| 每个系统编写连接器 | 标准Client/Server协议 | 业务适配 |
| 工具清单静态配置 | 能力发现与通知 | 权限过滤 |
| 数据与动作边界模糊 | Resources与Tools | 风险审批 |

MCP 不负责规划、业务正确性和最终授权，也不消除 Prompt Injection；企业仍需 Policy、沙箱、限流与审计。

**验证指标：** 工具选择准确率、调用成功率、参数错误率、P95 延迟和失败恢复率。

**相关知识点：** MCP Host、MCP Client、MCP Server、Tools、Resources、Prompts、能力协商、动态发现。
<a id="tool-046"></a>
### MCP协议的核心组成部分有哪些？

MCP 由 **Host、Client、Server、能力原语、传输与生命周期** 组成，建立模型应用与外部系统的标准通道。

1. **角色模型**：Host 承载 Agent 和策略；Client 在 Host 内与 Server 维护会话；Server 提供能力。授权、过滤与编排由 Host 负责。
2. **能力原语**：Tools 表示动作，Resources 表示 URI 寻址的数据，Prompts 表示提示模板，各自具有不同权限边界。
3. **消息与传输**：协议消息基于JSON-RPC请求、响应和通知；标准传输包括本地stdio与远程Streamable HTTP，具体安全要求随传输而异。
4. **生命周期**：初始化首先协商协议版本、双方能力和实现信息（`clientInfo`/`serverInfo`），然后进入正常操作，最后关闭连接。实现信息不是用户身份认证。

| 组成 | 主要职责 | 典型内容 |
|---|---|---|
| Host | 模型、策略和编排 | Agent应用 |
| Client | 会话、发现和调用 | 能力协商、请求转发 |
| Server | 提供外部能力 | Tools、Resources、Prompts |
| Transport | 消息承载 | 本地或远程通道 |

MCP 标准化连接与能力表达，不负责模型推理或业务正确性。授权不是所有实现的强制项：HTTP传输可采用MCP授权规范且该能力是可选的；stdio通常从环境获得凭据。企业仍需Policy、最小权限、审批和审计。

**验证指标：** 工具选择准确率、调用成功率、参数错误率、P95 延迟和失败恢复率。

**相关知识点：** MCP Host、MCP Client、MCP Server、Tools、Resources、Prompts、Transport、生命周期协商。
**官方规范：** [MCP Lifecycle](https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle)、[MCP Authorization](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization)。

<a id="tool-047"></a>
### MCP Client 和 MCP Server 如何通信？

MCP Client 与 Server 通过 **请求、响应和通知** 通信，经历初始化、发现、调用、变更和关闭生命周期。

1. **建立连接**：Host 创建 Client，经本地或远程通道连接 Server。双方初始化并协商协议版本、实现和能力；失败即终止会话。
2. **发现能力**：Client 列举 Tools、Resources 或 Prompts，Server 返回描述、Schema、URI 等元数据；Host 权限过滤后再提供给模型。
3. **调用交互**：Client发送带JSON-RPC `id`的请求，Server返回对应结果或错误；Notification不期待响应。进度、取消和长任务能力只有在协议版本与双方协商支持时才能使用。
4. **通知与关闭**：Server可通知能力列表变化，Client据此刷新缓存；关闭方式取决于传输。stdio通常关闭输入后等待并终止子进程，HTTP连接按传输语义结束。

| 消息类型 | 是否期待响应 | 典型用途 |
|---|---|---|
| Request | 是 | 列举、调用、读取 |
| Response | 对应请求 | 返回结果或错误 |
| Notification | 否 | 能力变化、进度通知 |

Deadline、Trace、终端用户身份和幂等键不是所有MCP请求的固定核心字段；如业务需要，应通过规范已定义的元数据/扩展和Host策略实现，不能假定Server天然接收。Server返回内容始终视为不可信数据。

**验证指标：** 工具选择准确率、调用成功率、参数错误率、P95 延迟和失败恢复率。

**相关知识点：** JSON-RPC、初始化协商、Request、Response、Notification、能力发现、Capability Negotiation、取消、Prompt Injection。
<a id="tool-048"></a>
### MCP与Function Calling有什么区别？

**Function Calling 是模型输出工具意图的机制，MCP 是 Host 与能力提供方的协议**。前者位于模型层，后者位于接入层。

| 维度 | Function Calling | MCP |
|---|---|---|
| 核心问题 | 模型如何选择工具和生成参数 | 外部能力如何发现与通信 |
| 工具来源 | 应用预配置并注入模型 | Client从Server运行时列举 |
| 能力范围 | 主要是函数或工具 | Tools、Resources、Prompts |

1. **Function Calling**：向模型提供名称、描述和 Schema，模型返回工具名与参数；宿主负责校验、授权和执行。
2. **MCP**：定义 Host、Client、Server 及消息和能力原语，使外部系统被不同应用复用；它不决定调用哪个工具。
3. **组合方式**：Host 将 MCP 发现的工具转换为 Function 定义；模型生成调用后，Executor 经 MCP Client 访问 Server。
4. **选型边界**：少量固定工具可只用 Function Calling；跨应用共享、动态发现和统一接入时增加 MCP。

两者不是替代关系，企业仍需实现 **权限、审批、业务校验、限流、超时、审计和注入防护**。

**历史别名：** `PLAN-128`、`TOOL-014`。

**验证指标：** 工具选择准确率、调用成功率、参数错误率、P95 延迟和失败恢复率。

**相关知识点：** Function Calling、MCP Host、MCP Client、MCP Server、Tool Discovery、JSON Schema、Tool Executor。
<a id="tool-049"></a>
### MCP相比传统Plugin机制优势是什么？

MCP 相比 Plugin 的优势是 **开放协议、运行时发现、跨宿主复用和多类上下文能力**，使集成转向 Client/Server 生态。

1. **降低绑定**：Plugin 依赖平台清单与 API；MCP 标准化角色和消息，同一 Server 可被不同应用与语言复用。
2. **动态发现**：Plugin 多在安装时声明，MCP Client 可列举 Tools、Resources 和 Prompts，并接收变化通知。
3. **上下文表达**：MCP 区分 Tool、Resource 和 Prompt，便于对数据读取与副作用采用不同权限策略。
4. **独立生命周期**：Server 可独立部署、升级和监控，Host 协商兼容能力，减少重复维护连接器。

| 维度 | 传统Plugin | MCP |
|---|---|---|
| 标准性 | 平台专用 | 开放协议 |
| 发现方式 | 安装时静态声明 | 运行时列举与通知 |
| 复用范围 | 绑定特定宿主 | 跨Host、语言和模型 |
| 能力类型 | 以动作接口为主 | Tools、Resources、Prompts |

MCP 不自动保证 Server 可信，也不替代授权与审计；企业仍需受控目录或 Gateway 治理来源、能力和数据流。

**相关知识点：** MCP、Plugin、开放协议、运行时发现、Tools、Resources、Prompts、MCP Gateway。
<a id="tool-050"></a>
### MCP如何实现工具发现（Tool Discovery）？

MCP 工具发现通过 **初始化协商、工具列举、变更通知和 Host 过滤** 完成，使 Client 获取 Server 的工具定义。

1. **初始化协商**：Client 与 Server 建立会话后交换协议版本和能力声明，确认双方支持工具能力；未声明该能力的 Server 不应被假定存在工具接口。
2. **列举工具**：Client 请求工具列表，Server 返回名称、描述、输入 Schema 和注解。结果可能分页，缓存需绑定 Server 身份与版本。
3. **动态更新**：Server 工具增加、删除或定义变化时发送列表变更通知，Client 将缓存标记失效并重新列举；不支持通知时使用 TTL 或会话重连刷新，避免长期使用过期 Schema。
4. **Host 治理**：先验证 Server、Schema 和命名冲突，再按租户、权限、环境、风险与健康过滤，必要时检索缩小候选。

| 阶段 | Server职责 | Client/Host职责 |
|---|---|---|
| 初始化 | 声明工具能力 | 协商与校验 |
| 列举 | 返回工具元数据 | 分页、缓存、建索引 |
| 变化 | 发送变更通知 | 失效并重新列举 |
| 调用前 | 执行工具 | 权限和参数复核 |

工具发现解决“有哪些能力”，不解决“是否允许调用”。每次执行仍需重新校验具体工具、版本、参数、授权、Deadline 和审计上下文。

**相关知识点：** Tool Discovery、能力协商、工具列举、变更通知、Schema、缓存失效、权限过滤。
<a id="tool-051"></a>
### MCP如何实现权限控制和安全隔离？

MCP 权限由 **可信 Server、最小暴露、Host 策略、Server 最终授权和隔离** 共同实现，连接成功不代表有权执行。

1. **身份与会话**：远程连接验证 Server 并加密，Client 使用限定受众、租户、Scope 和期限的令牌；本地 Server 限制进程与文件权限。
2. **发现过滤**：Host 审核 Server 与能力清单，按用户、租户、环境和风险过滤；未授权能力不进入模型上下文。
3. **调用授权**：Executor 对工具、参数和资源向 Policy 求值，高风险写入增加审批；Server 再做资源级鉴权。
4. **隔离防护**：高风险 Server 使用独立容器或账户，限制资源、网络和凭据；返回内容做大小限制、脱敏和注入检测。

| 控制位置 | 主要职责 | 典型机制 |
|---|---|---|
| Host/Client | 能力过滤与调用策略 | RBAC、ABAC、审批 |
| Transport | 身份与机密性 | TLS、短期令牌 |
| Server | 资源级最终授权 | Scope、租户校验 |
| Runtime | 限制爆炸半径 | 容器、网络策略 |

调用记录 Server、版本、用户、授权和 Trace；用户确认不能覆盖禁止策略，令牌撤销后缓存立即失效。

**相关知识点：** MCP安全、最小权限、Policy Engine、短期令牌、资源级授权、运行隔离、Prompt Injection。
<a id="tool-052"></a>
### MCP如何支持动态工具注册？

MCP 动态注册是 **Server 更新目录并通知 Client 重新发现**；企业还需来源审核、版本控制和权限门禁。

1. **Server 侧变更**：Server 启动或配置变化后更新目录，提供名称、描述、Schema、版本与风险注解；不兼容变更不能静默覆盖。
2. **变化通知**：当工具列表变化时，Server 向 Client 发送列表变更通知；Client 将对应 Server 的目录缓存失效，再发起列举请求获取完整新定义。若不支持通知，则通过重连或 TTL 刷新。
3. **Host 治理**：新工具经过身份、签名、Schema、命名冲突和安全审核，再按租户、权限、环境与风险决定可见范围。
4. **版本一致性**：Registry 保存逻辑名、Server、Schema 哈希和版本。新任务灰度使用新版，在途任务固定旧定义；执行前再次确认存在、健康和授权。

| 变化类型 | Client处理 | 发布策略 |
|---|---|---|
| 新增工具 | 重新列举并建索引 | 审核后灰度可见 |
| 兼容字段新增 | 刷新Schema | 次版本升级 |
| 不兼容修改 | 保留独立版本 | 主版本迁移 |
| 工具删除 | 立即失效缓存 | 提供替代与废弃期 |

动态注册只更新能力目录，不授予权限。发现、授权和调用必须分开，所有变更与调用都需关联 Server 身份、版本和 `trace_id`。

**验证指标：** 工具选择准确率、调用成功率、参数错误率、P95 延迟和失败恢复率。

**相关知识点：** 动态注册、工具列表通知、缓存失效、Schema哈希、语义版本、灰度发布、权限过滤。
<a id="tool-053"></a>
### MCP资源（Resources）和工具（Tools）有什么区别？

**Resource 提供可寻址上下文，Tool 执行带动作语义的能力**。边界是访问方式、副作用和授权，不只是读写之分。

| 维度 | Resources | Tools |
|---|---|---|
| 定位 | 向模型提供上下文 | 执行查询、计算或写入 |
| 标识 | URI及资源元数据 | 名称、描述和输入Schema |
| 使用方式 | 列举、读取、订阅 | 结构化参数调用 |
| 风险重点 | 数据泄露、内容注入 | 权限、副作用、重复执行 |

1. **Resource 模型**：适合文件、文档、配置和数据库视图等稳定内容。Host 选择何时读取和注入，内容携带来源与时间。
2. **Tool 模型**：适合参数化计算、实时查询或业务动作，需定义 Schema、业务状态、超时、幂等和风险。
3. **权限差异**：Resource 按数据源、路径、租户和敏感等级授权；Tool 还根据操作、环境、影响和可逆性审批。
4. **建模原则**：稳定、可寻址、无动作语义的数据优先作为 Resource；需要计算、动态参数或产生副作用时使用 Tool。不要把所有读取都包装为工具，也不要用 Resource 绕过动作审计。

例如代码文件可作为 Resource，运行测试应作为 Tool。两者返回内容都属于不可信输入，需要大小限制、脱敏、来源标记和 Prompt Injection 防护。

**相关知识点：** MCP Resources、MCP Tools、URI、JSON Schema、副作用、资源授权、Prompt Injection。
<a id="tool-054"></a>
### MCP在企业内部落地会遇到哪些挑战？

MCP 企业落地难在 **Server 可信度、身份权限、版本兼容、多租户、内容安全和运维**，而非协议连接。

1. **可信供给**：Server 可能恶意、过权或无人维护。需建立受控目录，记录负责人、签名、数据等级、风险和 SLA，未审核能力不得上线。
2. **身份集成**：对接 IAM、SSO、Vault 和审批，分离用户、Agent 与 Server 身份；权限细化到租户、工具、资源和环境。
3. **兼容治理**：管理协议、Server、Schema 和 Host 版本，通过契约测试、语义版本、灰度与废弃周期防止中断。
4. **运行与安全**：建设 MCP Gateway 统一实施限流、熔断、审计、网络策略、结果大小限制和 Prompt Injection 防护；高风险 Server 使用隔离运行时，跨租户数据和缓存严格分区。

| 挑战 | 典型风险 | 治理措施 |
|---|---|---|
| Server可信度 | 恶意或无主能力 | 签名、白名单、负责人 |
| 身份权限 | 越权和凭据泄露 | IAM、ABAC、短期令牌 |
| 版本演进 | Schema不兼容 | 契约测试、灰度 |
| 内容安全 | 间接提示注入 | 来源标记、内容隔离 |

还需解决可观测语义不统一、故障归因和成本分摊。平台指标应覆盖采用率、业务成功率、P95、风险事件和单任务成本。

**相关知识点：** MCP Gateway、IAM、Server签名、契约测试、多租户、Prompt Injection、SLA、成本治理。
<a id="tool-055"></a>
### MCP如何支持多Agent协作？

MCP 通过 **共享能力目录和上下文资源** 降低多 Agent 接入成本，但分工、协商和一致性由编排层负责。

1. **共享能力**：各 Agent 经 MCP Client 访问受控 Server，复用 Tools、Resources 和 Prompts，无需重复开发连接器。
2. **共享上下文**：中间产物写入带 URI、版本和权限的 Resource，其他 Agent 按需读取；内容标记来源、任务与租户。
3. **身份授权**：MCP核心协议不会自动透传终端用户身份。Host应为每个Agent或用户建立独立的凭据、Scope、预算与Trace关联，Server仍对最终资源鉴权；stdio凭据通常来自环境，HTTP可使用可选授权规范。
4. **并发一致性**：多个 Agent 写同一资源时使用版本号、ETag、锁或租约，并为工具调用设置幂等键。冲突时重新读取与规划，不可自动覆盖；任务编排器负责所有权、依赖、超时和补偿。

| 能力 | MCP负责 | 协作层负责 |
|---|---|---|
| 工具复用 | 标准发现与调用 | 为Agent分配能力 |
| 上下文共享 | Resources读取 | 内容选择与任务关联 |
| 安全 | 协商能力并承载请求；不充当身份系统 | 凭据、角色、审批和预算 |
| 一致性 | 暴露版本化接口 | 锁、冲突与补偿策略 |

MCP 是能力接入基础，不是多 Agent 调度协议；完整系统还需任务队列、状态存储、协调器和审计。

**相关知识点：** 多Agent、MCP Resources、工作负载身份、ETag、租约、幂等性、任务编排、共享上下文。
<a id="tool-066"></a>
### MCP工具调用过程中如何进行权限校验？

MCP Tool 权限应贯穿 **发现、调用前决策、Server 最终授权和审计**，连接成功不代表可用全部工具。

1. **发现阶段**：Host 验证 Server 身份和签名，按用户、租户、环境与风险过滤；无权限工具不进入模型上下文。
2. **调用前校验**：Executor 将身份、工具、版本、参数、资源和环境提交 Policy，综合 RBAC、ABAC、风险与审批决策；参数变化需重新授权。
3. **凭据传输**：Client 使用限定 audience、scope、租户和期限的短期令牌；高风险审批令牌绑定工具、参数与有效期。
4. **Server 授权**：Server 再验证签名、受众、Scope、租户和资源权限；写操作检查幂等键与业务状态。

| 校验点 | 核心问题 | 失败处理 |
|---|---|---|
| Host发现 | 能否看见该工具 | 不进入候选 |
| Executor | 当前请求能否执行 | 拒绝或审批 |
| Server | 能否访问具体资源 | 返回权限错误 |
| 调用后 | 实际影响是否合规 | 审计、告警 |

审计关联用户、Agent、Server、版本、策略、审批和 Trace；令牌撤销或权限变化后缓存立即失效。

权限决策还应设置短 TTL，并将策略版本写入调用上下文，确保回放时能够解释当时为何放行或拒绝。

**历史别名：** `GOV-162`。

**相关知识点：** MCP权限、RBAC、ABAC、Policy Engine、短期令牌、资源级授权、审批令牌、审计。
<a id="tool-092"></a>
### 如何设计沙箱与外部工具调用（Tool Calling）之间的安全通信协议？

沙箱不直接访问企业服务或持有长期凭据，通过 **Tool Gateway、结构化消息、最小授权和结果校验** 通信。

1. **通信拓扑**：沙箱网络默认拒绝，只连接本机代理或 Gateway。Gateway 负责身份、Policy、协议适配与外连；沙箱不能自定义目标。
2. **请求契约**：消息包含任务、租户、工具逻辑名与版本、结构化参数、Deadline、幂等键、Trace 和随机数。使用 mTLS 或短期会话令牌认证，并通过签名、时间窗和 nonce 防重放。
3. **权限执行**：Gateway 根据用户委托、沙箱工作负载身份、工具、资源和风险向 Policy Engine 求值；高风险操作要求绑定规范化参数的审批令牌。真实凭据仅在 Gateway 侧短暂使用。
4. **结果与故障**：结果包含业务状态、Schema、来源和错误，经大小限制、脱敏和检测后返回。协议支持取消、查询和流控；超时写操作先查状态。

| 组件 | 信任级别 | 主要职责 |
|---|---|---|
| Sandbox | 不可信 | 生成结构化请求 |
| Gateway | 可信策略点 | 鉴权、限流、审计 |
| Tool Service | 资源权威方 | 最终资源级授权 |

所有请求与响应绑定 Trace 并写审计；任务结束立即吊销会话令牌。Gateway 还需限制目标域名、并发和响应大小，防止横向移动与资源耗尽。

**验证指标：** 工具选择准确率、调用成功率、参数错误率、P95 延迟和失败恢复率。

**相关知识点：** Tool Gateway、mTLS、短期令牌、nonce、防重放、Policy Engine、流控、结果脱敏。
<a id="tool-095"></a>
### LangChain 和 Spring AI 的核心区别是什么？

核心差异是：**LangChain以AI编排与Agent生态为中心，Spring AI以Spring体系中的可移植AI抽象和企业集成为中心**。

1. **定位**：LangChain提供模型、工具、检索与Agent抽象，并可结合LangGraph构建持久化、有状态的执行图；Spring AI提供Model API、ChatClient、Advisor、Vector Store、Tool Calling及MCP。
2. **生态**：LangChain面向Python和TypeScript，连接器丰富，适合快速验证；Spring AI面向Java，衔接依赖注入、自动装配、可观测性及微服务规范。
3. **取舍**：LangChain迭代快、抽象较多，需控制版本和隐式状态；Spring AI符合Java团队习惯，高级Agent编排常需状态机或工作流补足。

| 维度 | LangChain | Spring AI |
|---|---|---|
| 核心优势 | Agent编排与广泛集成 | Spring原生工程化 |
| 主要语言 | Python、TypeScript | Java |
| 典型场景 | AI产品、快速试验 | 企业Java系统 |

两者均不能自动解决权限、评测、成本与安全问题。选型应验证模型切换、可观测性、故障恢复和维护能力，并用内部接口隔离框架。

**相关知识点：** LangChain、LangGraph、Spring AI、ChatClient、Advisor、Tool Calling、Vector Store、MCP、框架适配层。
<a id="tool-100"></a>
### 自研 Agent 框架如何避免重复造轮子？

自研的重点应是企业特有的**控制面、执行语义与治理能力**，而不是重写模型SDK、向量数据库客户端和通用解析器；采用薄内核、标准协议和可替换适配器能够控制自研边界。

1. **先做能力盘点**：把需求拆为模型、工具、编排、记忆、检索、评测、追踪和安全，标明差异化能力。成熟组件满足要求时直接复用。
2. **定义稳定接口**：内部统一Model、Tool、Memory、Retriever、Checkpoint和Event接口，外部实现通过Adapter接入；优先采用JSON Schema、OpenTelemetry、MCP等标准，避免业务代码绑定某个框架。
3. **保持内核最小**：内核只负责状态转移、上下文传递、预算、取消、恢复及策略钩子。连接器、存储、模型供应商和UI作为插件，独立版本化。
4. **用验证决定去留**：为引入组件执行许可证、安全、活跃度、性能和退出成本评估；通过契约测试保证替换能力，并定期比较自研维护成本与社区方案。

| 能力 | 建议策略 | 原因 |
|---|---|---|
| 模型/存储连接器 | 优先复用 | 通用且变化频繁 |
| 编排状态语义 | 按需自研 | 决定可靠性与差异化 |
| 追踪协议 | 采用标准 | 便于跨组件关联 |
| 权限与审计 | 企业自持 | 与组织策略强相关 |

可先封装开源框架验证，再逐步下沉关键模块。衡量标准包括交付速度、升级工时、故障率、性能和替换成本。

**相关知识点：** 薄内核、插件架构、Adapter、契约测试、OpenTelemetry、MCP、Build vs Buy、退出成本、软件供应链。
<a id="tool-109"></a>
### Spring AI 更适合哪些 Java 企业应用场景？

Spring AI更适合**既有Spring技术栈中以业务集成、统一治理和可维护性为优先**的应用，尤其适合把模型能力嵌入微服务。

1. **知识助手与RAG**：用ChatClient、Advisor、Embedding、Vector Store和ETL接入知识库，并复用Spring Security过滤数据权限。
2. **流程增强**：在客服、工单、合同审阅等服务中调用Tool，连接已有Service和消息系统；事务、幂等与审批仍由业务层控制。
3. **多模型部署**：通过Model API和Spring Boot配置切换供应商，结合自动装配、配置中心、密钥管理与环境隔离。
4. **平台治理**：接入指标、追踪、日志、限流和容错体系，集中观测模型与工具链路；MCP用于标准化外部能力。

| 场景 | 适配度 | 原因 |
|---|---|---|
| Java微服务增加AI能力 | 高 | 复用Spring工程体系 |
| 企业RAG与业务工具调用 | 高 | API与数据集成完整 |
| Python算法快速实验 | 较低 | 生态重心不匹配 |
| 超复杂动态Agent研究 | 中 | 需补充编排运行时 |

Spring AI仍需补充评测、安全、审批和可靠工作流；统一API不代表供应商行为一致，模型切换必须回归测试。

**相关知识点：** Spring AI、ChatClient、Advisor、Model API、Vector Store、ETL、Tool Calling、MCP、Spring Boot、可观测性。
<a id="tool-112"></a>
### Tool Calling与MCP协议有什么区别？

**Tool Calling是模型表达调用意图的能力，MCP是AI应用连接外部能力的标准协议**。前者解决结构化输出，后者解决发现、传输与互操作。

1. **边界**：Tool Calling由模型API定义Schema和结果回填，应用负责执行；MCP定义Client、Server及JSON-RPC交互，服务端可暴露Tools、Resources和Prompts。
2. **生命周期**：Tool Calling的列表多由应用随请求提供；MCP支持能力协商、发现与远程调用，使Server可被不同Host复用。
3. **组合方式**：先从MCP Server发现工具并转换Schema；模型产生调用后，MCP Client发送tools/call，再回传结果。
4. **安全**：两者不自动保证安全。Host仍需验证Server、过滤工具、取得同意、最小授权并审计。

| 维度 | Tool Calling | MCP |
|---|---|---|
| 层次 | 模型交互能力 | 客户端—服务端协议 |
| 核心对象 | 工具定义与调用意图 | Tools、Resources、Prompts |
| 执行者 | 应用 | MCP Server |
| 主要价值 | 结构化决策 | 标准发现与互操作 |

本地调用需求适合Tool Calling；跨应用连接多数据源或构建插件生态时，MCP更能减少重复适配。

**历史别名：** `ENG-131`。

**相关知识点：** Function Calling、JSON Schema、MCP Client、MCP Server、JSON-RPC、能力协商、tools/list、tools/call、Host安全边界。
<a id="tool-117"></a>
### MCP与Tool Calling如何融合？

融合方式是**MCP负责发现与通信，Tool Calling负责选择和参数，Host负责安全与编排**，使协议层与推理层解耦。

1. **发现转换**：Host作为MCP Client连接受信Server，以tools/list获取Schema，经权限、风险和兼容性过滤后，转换为模型Tool定义。
2. **调用闭环**：模型生成调用；Host校验参数、授权与确认，再以tools/call发送。结果规范化、截断并标记为不可信内容后加入上下文。
3. **会话治理**：映射Tool Call ID、MCP请求ID与Trace ID，处理超时、取消和重连。当前任务固定工具版本，避免语义漂移。
4. **安全边界**：只连接白名单Server并验证身份；注解不作为授权依据。按用户下传短期凭证，高风险工具绑定审批令牌。

| 层次 | 组件 | 职责 |
|---|---|---|
| 推理层 | LLM Tool Calling | 选择工具、生成参数 |
| 宿主层 | Agent Host | 过滤、授权、编排、审计 |
| 协议层 | MCP Client/Server | 发现与标准调用 |
| 执行层 | 业务服务 | 最终资源级校验 |

通过Schema兼容、恶意Server、权限矩阵和链路追踪测试，避免把互通误认为互信。

**历史别名：** `GOV-054`。

**相关知识点：** MCP Host、MCP Client、Tool Calling、tools/list、tools/call、Schema转换、能力过滤、Trace映射、零信任。

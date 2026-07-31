# 十一、OpenClaw

> 本章共 **56** 题，覆盖 OpenClaw 的 Gateway、Agent Runtime、渠道路由、工作区、会话与记忆、工具与插件、沙箱、多 Agent、自动化、模型容错和生产治理。
>
> 内容按 **2026-07-31** 可访问的官方文档核验。回答时应区分“OpenClaw 已实现能力”“实验能力”和“企业扩展建议”，并以实际安装版本的文档与配置 Schema 为准。

#### 1、OpenClaw 的产品定位是什么？它与普通聊天机器人有什么区别？
OpenClaw 是运行在自有设备或服务器上的**自托管 Agent Gateway 与个人助手运行时**。它把消息渠道、模型、会话、记忆、工具、Skills、Plugins、自动化任务和设备节点连接到一个常驻控制面，而不只是提供一次请求—一次回答的聊天接口。

与普通机器人相比，它能保留跨渠道会话、调用本地或远程工具、执行后台任务并主动交付结果。它也不是天然的企业工作流引擎或专用 Coding Agent；确定性事务可交给工作流系统，仓库编码可通过 ACP 或专门 Harness 执行。

**相关知识点：** Self-hosted、Gateway、Agent Runtime、渠道适配、个人助手、ACP、控制面。

---

#### 2、OpenClaw Gateway 在整体架构中承担什么职责？
Gateway 是 OpenClaw 的**常驻控制面和连接中枢**，负责接受渠道与客户端连接、解析路由、管理会话、启动 Agent Run、调度后台任务并把结果交付回目标渠道。

1. 控制流通过 Gateway 统一进入，渠道凭据、Agent Binding、会话键和回复路由在这里汇合。
2. 内置 Agent Loop通常在Gateway进程内运行；沙箱只把符合配置的工具执行移到隔离环境，不等于把整个Gateway放入沙箱。
3. Gateway故障会影响多个Agent和渠道，因此需要健康检查、日志、配置校验、备份和进程守护。
4. 不可信租户不应只靠会话隔离共用同一Gateway，强信任边界应拆到OS用户、主机或独立Gateway。

**相关知识点：** WebSocket Gateway、控制面、会话路由、故障域、进程守护、信任边界。

---

#### 3、OpenClaw 内置 Agent Runtime 的一次执行循环是怎样的？
一次Run可概括为**组装上下文—调用模型—执行工具—回灌结果—继续或结束—交付回复**。模型决定是否请求工具，Runtime负责校验可见工具、执行并把Observation加入后续轮次。

上下文包含系统指令、工作区引导文件、会话历史、按需记忆、Skill说明和工具Schema。流式文本、工具事件与最终回复有不同生命周期；等待外部结果时还要处理超时、取消和运行期Steering。官方没有保证所有任务都先生成固定DAG，因此不能把模型的动态循环描述成内建Planner服务。

**相关知识点：** Agent Loop、Prompt Assembly、Tool Calling、Observation、Streaming、Steering、停止条件。

---

#### 4、OpenClaw 如何把不同消息渠道和会话路由到正确的 Agent？
OpenClaw通过**渠道适配器、Agent Binding和会话键**进行确定性路由。Binding可按渠道、账号、群组或具体对话选择Agent，每个Agent再使用独立工作区与会话存储。

应先定义匹配优先级和兜底Agent，再验证私聊、群聊、线程、多个账号和跨渠道切换。回复目标不能只依赖模型生成，应由入站元数据和当前Reply Route确定。跨渠道Docking或共享主会话会提高连续性，也会扩大信息可见范围，必须符合用户和组织边界。

**相关知识点：** Channel Adapter、Agent Binding、Session Key、Reply Route、Thread、Channel Docking。

---

#### 5、为什么 OpenClaw 为每个 Agent 设置独立工作区？工作区中通常放什么？
工作区同时是Agent的**可操作目录和持久上下文载体**。独立工作区能隔离身份、规则、记忆、Skills和产物，避免多个Agent无意共享文件。

工作区通常包含`AGENTS.md`、`SOUL.md`、`IDENTITY.md`、`USER.md`、`TOOLS.md`、`MEMORY.md`、每日记忆目录及项目文件。不同文件承担规则、人格、用户偏好、工具说明和长期事实等职责。应把可恢复文件纳入受控备份或版本管理，但密钥、会话令牌和敏感原始记录不能直接提交Git。

**相关知识点：** Agent Workspace、Bootstrap Files、身份隔离、配置即代码、备份、Secret Management。

---

#### 6、OpenClaw 的主会话、群组会话和子 Agent 会话有什么差异？
三者的区别在于**身份范围、上下文继承、回复目标和权限风险**。

1. 主会话是个人Agent的滚动对话，可跨入口保持连续体验。
2. 群组或频道通常使用独立会话键，避免把私人主会话内容直接暴露给群成员。
3. 子Agent在独立后台会话运行，默认只获得受限引导文件和工具面；只有明确需要时才Fork父上下文。
4. 会话隔离不等于数据隔离。共享工作区、工具凭据或全局可见Session Tool仍可能跨边界泄漏信息。

设计时应同时检查Session Key、工具策略、工作区、Memory和交付路由。

**相关知识点：** Main Session、Group Session、Subagent Session、Context Fork、Session Visibility、数据隔离。

---

#### 7、OpenClaw 的 Memory 与会话历史有什么区别？
会话历史记录**发生过的对话与工具事件**，Memory保存**值得跨会话复用的稳定信息**。把全部历史当Memory会导致噪声、隐私和Token成本不断增长。

OpenClaw可从工作区笔记和已配置的Memory Engine检索相关片段；默认内存后端可结合关键词、向量和混合搜索。写入时应保留来源、时间与置信度，区分用户明确事实、Agent推断和临时任务状态。冲突事实需要更新或保留版本，敏感数据应设访问和保留策略。

**相关知识点：** Episodic History、Durable Memory、Hybrid Search、Provenance、Memory Lifecycle、隐私。

---

#### 8、OpenClaw 如何利用混合检索提高 Memory Recall？
混合检索将**关键词精确命中、向量语义召回与重排**结合：人名、编号和专有词适合词法搜索，偏好与语义相近表达适合向量搜索，融合后再按相关性、新鲜度和来源筛选。

查询前应识别实体、时间和当前任务，检索结果必须带来源文件与范围；低置信结果只能作为候选，不能覆盖用户当前陈述。评估要使用真实跨会话问题，报告Recall@K、上下文Precision、过期记忆率、冲突率和额外Token，而非只看Embedding相似度。

**相关知识点：** BM25、Embedding、Hybrid Retrieval、Rerank、Recall@K、Context Precision、记忆冲突。

---

#### 9、OpenClaw 中 Tools、Skills 和 Plugins 的边界是什么？
三者分别解决**行动、方法和扩展载体**。

| 机制 | 核心作用 | 典型内容 |
|---|---|---|
| Tool | 可调用的结构化动作 | 读写文件、浏览器、消息、节点 |
| Skill | 教Agent何时及如何完成工作 | `SKILL.md`、流程、规范、脚本 |
| Plugin | 向Runtime注册新能力 | Tool、Provider、Channel、Hook、Skill |

Skill不会天然新增底层权限，Plugin也不应绕过Tool Policy。第三方Skill和Plugin都属于供应链输入，应审查来源、安装脚本、依赖、Secret使用和升级变化。

**相关知识点：** Tool Schema、Agent Skills、Plugin SDK、能力注册、最小权限、供应链安全。

---

#### 10、OpenClaw 的工具可见性和 Allow/Deny 策略如何生效？
工具不是安装后就必然对模型可见，而是经过**Profile、全局策略、Provider限制、Agent策略、渠道权限、沙箱状态和Plugin可用性**等多层过滤，最终集合才进入模型上下文。

配置原则是默认最小集合、按Agent和场景增量开放；Deny应优先于Allow，不能指望Prompt要求代替宿主策略。排障时应检查最终Effective Policy，而不是只看某一层配置。减少无关工具还会降低误选率和工具Schema的Token开销。

**相关知识点：** Tool Profile、Allowlist、Denylist、策略优先级、Effective Policy、Tool Surface。

---

#### 11、OpenClaw 的 Sandbox 隔离了什么？没有隔离什么？
Sandbox主要隔离**工具执行**，包括`exec`、文件读写、Patch、Process及可选浏览器；Gateway本身仍在宿主机运行。可按Agent、Session或共享范围创建环境，并选择Docker、SSH或OpenShell等后端。

`workspaceAccess`决定工作区不可见、只读或可写，网络和额外挂载也需单独限制。Elevated工具可能绕过沙箱，所以沙箱不是单独充分的安全边界。生产中还应限制宿主凭据、容器Socket、设备文件和出口网络，并用恶意路径、符号链接和Prompt Injection测试验证。

**相关知识点：** Sandbox Backend、Workspace Access、Filesystem Isolation、Network Egress、Elevated Mode、纵深防御。

---

#### 12、Exec Approval、Elevated Mode 和真正的系统授权有什么区别？
Exec Approval是**人机交互护栏**，Elevated Mode是**允许命令脱离工具沙箱执行的逃生路径**，系统授权则由OS、容器、云IAM和目标服务ACL强制。

批准一条命令不应自动授予宽泛后续权限；Elevated来源应严格限制并记录主体、命令、目标和结果。即使模型或用户文本声称“已批准”，宿主仍必须检查实际身份与策略。不可逆、外发或高价值操作还需二次确认、幂等键和业务后置校验。

**相关知识点：** Human Approval、Elevated Exec、IAM、ACL、Least Privilege、审计、后置校验。

---

#### 13、如何防止不可信频道用户控制 OpenClaw 执行危险操作？
安全链路应是**入口鉴权—发送者Allowlist—会话隔离—工具最小化—沙箱—高风险确认—审计**。

群聊和公开频道默认不应暴露文件、Shell、浏览器登录态或Session History；提及触发和机器人互聊还要防循环。网页、邮件、附件和其他用户消息都作为不可信数据，不能覆盖系统与Agent规则。高风险Agent可配置只读工作区和无Shell工具，互不信任用户应拆分Gateway而非只靠Prompt区分。

**相关知识点：** Pairing、Sender Allowlist、Group Policy、Prompt Injection、Bot Loop、只读Agent、租户隔离。

---

#### 14、OpenClaw 多 Agent 路由与临时子 Agent 委派有什么区别？
多Agent路由是**长期配置的身份与入口分工**，子Agent委派是**某次Run中的临时后台协作**。

前者通过Binding把渠道或会话交给固定Agent，每个Agent有自己的工作区、模型和策略；后者由父Run用会话工具启动，完成后通过Announce链回报。长期领域边界、不同信任级别适合配置Agent；独立研究、慢任务和并行验证适合子Agent。两者都不能默认并发写共享资源。

**相关知识点：** Multi-agent Routing、Agent Binding、Subagent、Delegation、Announce、共享写冲突。

---

#### 15、OpenClaw 子 Agent 如何控制上下文、权限和并发？
子Agent默认使用独立Session和独立上下文，只继承规定的引导信息；需要完整对话时才显式Fork。其工具先经过目标Agent策略，再经过子Agent限制层，部分会话、消息、Gateway和Cron能力默认不可用。

应限制并发数、每个父Agent的子任务数、嵌套深度、模型、超时和预算。子Agent完成通知属于回传机制，不应被当作Exactly-once业务提交；关键产物写入可验证Artifact并由父Agent验收。共享Gateway资源下，盲目增加并发可能降低总体吞吐。

**相关知识点：** Context Isolation、Tool Restriction、Concurrency Lane、Nesting Depth、Artifact、Best-effort Announce。

---

#### 16、OpenClaw 如何通过 ACP 接入 Claude Code、Codex 等 Coding Harness？
ACP用于把外部Coding Harness作为**具有独立会话和执行语义的Agent后端**接入OpenClaw。OpenClaw负责渠道入口、会话协调和交付，Claude Code、Codex或其他Harness负责仓库探索、修改、命令和验证。

接入时要明确工作目录、认证、权限模式、会话生命周期、取消、超时和产物回传。ACP不是MCP：ACP管理Agent会话与任务，MCP主要标准化工具和资源连接。外部Harness的Checkpoint、沙箱和审批语义应按自身文档描述，不能归功于OpenClaw内置Loop。

**相关知识点：** Agent Client Protocol、Coding Harness、Session Backend、MCP、权限传递、结果交付。

---

#### 17、OpenClaw 的 MCP 能力应如何理解和治理？
MCP是OpenClaw连接或暴露标准化工具与上下文的协议层，但**协议互通不等于自动可信**。接入Server前应固定来源与版本，验证Transport、认证、工具Schema、超时和错误语义，再通过Include/Exclude与Agent Policy缩小工具面。

远程Server需要TLS、OAuth或短期凭据，本地stdio Server同样可能访问宿主资源。工具结果一律视为不可信输入；写操作还需目标系统ACL、幂等和审计。大规模工具目录可结合Tool Search按需发现，避免把全部Schema塞入Prompt。

**相关知识点：** MCP、stdio、HTTP、OAuth、Tool Filtering、Schema、Tool Search。

---

#### 18、OpenClaw 的 Code Mode 与普通工具调用有什么差异？
普通工具调用由模型逐个选择并回收每次结果；Code Mode允许在受控JavaScript/TypeScript工作流中**发现、组合和并发调用大量合格工具**，减少中间结果反复进入模型上下文。

它适合结构化批处理、聚合和多工具编排，但应限制可调用工具、循环次数、输出大小和执行时间。脚本仍受宿主策略与沙箱约束，不能将模型生成代码视为可信程序。该能力若标注实验性，生产采用必须固定版本、回归并准备降级到普通调用。

**相关知识点：** Code Mode、Tool Search、Nested Calls、Context Reduction、执行预算、实验能力。

---

#### 19、OpenClaw 中 Cron、Heartbeat、Hooks 和 Task Flow 应如何选型？
它们对应不同触发和编排语义。

| 机制 | 适用场景 | 关键特点 |
|---|---|---|
| Cron/Automation | 固定时间或一次性调度 | 可创建隔离Run并交付 |
| Heartbeat | 周期检查个人主会话 | 合并轻量检查，避免刷屏 |
| Hook/Webhook | 生命周期或外部事件 | 事件驱动、低等待 |
| Task Flow | 多步骤后台编排 | 显式阶段、任务与交接 |

强事务、补偿和跨系统Exactly-once仍应由专业工作流系统承担。选择依据是触发方式、状态持久性、失败恢复和交付SLA，而非都用Cron模拟。

**相关知识点：** Scheduler、Heartbeat、Event Hook、Webhook、Task Flow、Durable Workflow。

---

#### 20、OpenClaw 的后台任务如何避免“运行了但用户没收到结果”？
任务完成与结果交付是两个状态，必须分别记录。后台任务应保存Task ID、Owner、来源会话、状态、结果Artifact、预期渠道和Delivery Receipt。

执行成功后按解析出的路由发送，失败要重试、降级或进入待处理队列；重试使用幂等键，避免同一消息重复外发。Gateway重启后应能查询未完成或未交付任务，关键业务不能只依赖一次Best-effort Announce。监控完成率、交付率、重复率、P95和积压年龄。

**相关知识点：** Background Task、Delivery Receipt、Outbox、Idempotency、Dead Letter、任务与交付分离。

---

#### 21、OpenClaw 的模型选择、认证 Profile 轮换与 Fallback 如何协作？
模型解析先确定Provider与Model，再选择可用认证Profile；遇到符合条件的认证或Provider故障时，可轮换Profile并沿配置的Fallback链尝试其他模型。

显式会话选模、Agent默认模型和任务级覆盖可能有不同优先级，必须检查Effective Model。Fallback要考虑能力、上下文、工具支持、数据区域和价格兼容，不能只按名称替换。业务错误、工具错误和错误Prompt不应靠切模型掩盖。监控切换原因、成功率、质量退化和成本变化。

**相关知识点：** Model Resolution、Auth Profile、Failover、Fallback Chain、Capability Compatibility、路由观测。

---

#### 22、OpenClaw 如何处理长会话的上下文增长？
主要手段是**Session Pruning、Compaction、Memory写入与按需Recall**。旧的大型工具结果可先裁剪，接近窗口上限时将历史压缩成摘要；稳定事实写入Memory后在后续会话按需检索。

压缩摘要必须保留目标、未完成事项、关键决定、约束、来源和Artifact引用。磁盘上仍有完整Transcript不代表模型仍能看到细节，可用Context检查工具确认实际注入。评估应关注压缩后的任务延续率、约束丢失率、缓存命中与Token，而非只看缩短比例。

**相关知识点：** Context Window、Pruning、Compaction、Memory Flush、Recall、Prompt Cache。

---

#### 23、OpenClaw 的浏览器和设备 Node 能力有哪些安全风险？
浏览器可能携带登录态、Cookie和高价值会话，设备Node可能访问摄像头、屏幕、位置、通知或本地应用，因此都属于**高权限执行面**。

应使用专用Profile或隔离浏览器，限制允许域名、下载、上传和外部协议；敏感提交前预览并确认。Node需要配对、设备身份、能力Allowlist和可撤销授权，移动设备隐私权限还受操作系统控制。截图和页面内容也可能包含Prompt Injection或敏感数据，日志与Artifact应脱敏和限期保存。

**相关知识点：** Browser Automation、Authenticated Session、Node Pairing、Capability Grant、TCC、数据脱敏。

---

#### 24、如何为 OpenClaw 编写可维护的 Skill？
一个好Skill应有**准确触发描述、最小必要指令、明确输入输出、可复用脚本和验证步骤**。`SKILL.md`只放Agent需要遵循的流程，长参考资料按需加载，确定性操作优先复用Skill目录内脚本。

Skill不能把Secret写入正文，也不能用文字要求绕过工具策略。发布前测试正触发、误触发、缺依赖、恶意输入和失败恢复；版本升级要回归实际任务。第三方Skill安装前审查源代码、依赖和安装行为，并在不可信场景使用沙箱。

**相关知识点：** SKILL.md、渐进加载、Trigger Description、脚本复用、依赖门禁、Skill Supply Chain。

---

#### 25、OpenClaw Plugin 的设计和升级需要关注哪些兼容性问题？
Plugin可注册Tool、Channel、Provider、Hook和其他Runtime能力，因而兼容面包括**Manifest、配置Schema、SDK接口、权限、事件和持久数据**。

插件应声明支持版本与弃用信息，对配置做严格校验，启动失败时Fail Closed或明确降级。升级先在隔离Gateway回放渠道、工具和自动化场景，再灰度发布；迁移必须可回滚，避免新旧版本同时写不兼容状态。Plugin拥有宿主代码权限，安全审查强度应高于普通Prompt或Skill。

**相关知识点：** Plugin SDK、Manifest、Semantic Versioning、Schema Migration、Canary、Fail Closed。

---

#### 26、OpenClaw 的配置应如何进行版本管理和安全发布？
将非敏感配置、工作区规则、Skills和Plugin清单纳入Git，Secret通过环境变量、SecretRef或外部Vault注入。发布流水线先做Schema校验、`doctor`检查、权限差异审查和场景回归，再灰度重载或重启。

每次发布记录OpenClaw版本、配置Commit、模型、Plugin和迁移结果。高风险变化包括扩大Sender范围、开放Elevated、增加宿主挂载、共享Sandbox或放宽Session可见性，应设置人工门禁。回滚既要恢复配置，也要考虑已经发生的数据迁移和外部副作用。

**相关知识点：** Configuration as Code、SecretRef、Schema Validation、Policy Diff、Canary、Rollback。

---

#### 27、如何建立 OpenClaw 的可观测性和故障排查路径？
先按**入口—路由—会话—模型—工具—任务—交付**建立关联链。请求应携带Channel、Agent、Session、Run和Task标识，记录模型路由、工具状态、时延、Token、审批和Delivery Receipt。

排障通常从`status`、Gateway健康、渠道连接、日志和`doctor`开始，再检查Effective Config、模型认证、Tool Policy、Sandbox和目标渠道。敏感Prompt、媒体和凭据不得进入普通日志。指标至少包含请求与交付成功率、P95、队列深度、模型Fallback、工具失败、Token和单位成功成本。

**相关知识点：** Health Check、Doctor、Structured Log、Correlation ID、Metrics、Delivery Observability。

---

#### 28、OpenClaw 如何做备份、恢复和灾难演练？
先区分可重建配置、Agent工作区、Memory、会话记录、任务状态、渠道凭据和Plugin数据。备份应加密、版本化并测试恢复，Secret可通过外部密钥系统重新签发，而不是长期复制明文。

恢复后校验文件权限、Schema迁移、渠道连接、会话归属、未完成任务和重复交付风险。外部副作用不能靠恢复本地文件撤销，要用幂等键、查账与补偿。定期演练主机丢失、配置损坏、Provider不可用和凭据泄漏，并记录RPO、RTO和人工步骤。

**相关知识点：** Backup、Restore Drill、RPO、RTO、Key Rotation、幂等恢复、补偿。

---

#### 29、OpenClaw 是否适合直接作为多租户 SaaS 的共享 Runtime？
默认信任模型更适合**单一可信操作者边界**，不应把Agent或Session配置当作敌对租户的强隔离。共享Gateway会共享进程故障域，并可能通过文件、凭据、Session Tool、Plugin或缓存形成越权路径。

若提供SaaS，应按租户或信任域拆分容器/VM、OS身份、Gateway、存储、密钥和网络策略，控制资源配额并验证删除与审计。外层控制面负责身份、计费、调度和生命周期。是否共享模型网关可另行决策，但数据和工具授权必须保持租户上下文。

**相关知识点：** Multi-tenancy、Trust Domain、Process Isolation、Tenant Context、Quota、Data Residency。

---

#### 30、如何设计 OpenClaw 的面试级评测体系？
评测应覆盖**功能、任务质量、安全、可靠性、效率和渠道体验**，并绑定具体版本。

1. 功能：路由、会话、记忆召回、工具、自动化和交付是否符合契约。
2. 质量：用真实个人助手任务评Strict/Partial完成率、引用和人工介入。
3. 安全：测试陌生发送者、间接注入、路径越界、Elevated、跨Agent和Secret泄漏。
4. 可靠性：注入Gateway重启、Provider限流、渠道断连、重复Webhook和任务恢复。
5. 效率：统计P50/P95、Token、缓存、并发、单位成功成本和电量/资源占用。

模型说“完成”不算成功，必须以目标渠道、文件、业务状态或人工Rubric为证据。

**相关知识点：** End-to-end Eval、Failure Injection、Security Red Team、Strict Success、版本矩阵、单位成功成本。

---

## 原章节迁移题（26 题）

> 以下题目由「Agent 核心架构」迁入，保留原答案内容并统一纳入 OpenClaw 专章。

#### 31、OpenClaw 设计方案（附加专题）
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

---

#### 32、OpenClaw 与 Claude Code 的架构差异是什么？
**【核心思路】**
两者不是同类产品。OpenClaw 是**自托管、常驻的个人助手控制面**，通过 Gateway 连接消息渠道、会话、Memory、Skills、工具和设备，并支持多个模型Provider。Claude Code是面向代码仓库的专用Coding Agent，核心交互围绕读取、修改和验证代码。

OpenClaw官方建议直接仓库编码使用Claude Code或Codex，而用OpenClaw承担持久记忆、跨设备入口和工具协调。若需在OpenClaw中托管编码Harness，应走其ACP等明确接口，不能把通用文件/Bash能力等同于内建的完整Coding Agent能力。

---

#### 33、OpenClaw 如何实现长任务执行？
**【核心思路】**
当前可用机制包括后台任务、子Agent独立会话、Cron/Heartbeat、会话持久化和上下文压缩。长或并行工作可交给子Agent，完成后回传摘要，避免阻塞主会话；定时任务由常驻Gateway调度。

需要注意：官方没有承诺“每个步骤事务化Checkpoint并可精确续跑”。Gateway重启可能丢失尚未投递的子Agent完成通知，云Worker也仍是未实现提案。高可靠长任务应由外层工作流保存任务ID、幂等键、阶段Artifact和验收状态。

---

#### 34、OpenClaw 的 Agent Loop 如何设计？
**【核心思路】**
官方架构中一次Agent Run在Gateway进程内完成模型调用、工具执行和结果回灌。可以用“模型决策→工具调用→观察→继续或回复”理解，但不应断言内部固定采用某一种公开的ReAct Prompt或独立Planner。

工程关注点是有效工具策略、运行超时、上下文压缩、不可信工具输出、停止条件和可见的最终结果。若通过ACP托管外部Coding Harness，其循环与恢复语义由对应Harness决定，不应混入OpenClaw原生Loop描述。

---

#### 35、OpenClaw 为什么需要 Memory 系统？
**【核心思路】**
OpenClaw是常驻个人助手，需要跨会话保存偏好、长期事实和每日工作记录。官方Memory主要是工作区中的Markdown文件：长期内容在`MEMORY.md`，每日记录在`memory/YYYY-MM-DD.md`；在压缩前可触发Memory Flush提醒模型写入耐久信息。

Memory文件持久存在不代表每轮都进入上下文，相关内容通过搜索按需召回。写入仍需用户或工具事实支撑，敏感信息、临时推断和失败结果不应自动沉淀；多Agent场景还要明确工作区和访问边界。

---

#### 36、OpenClaw 如何解决上下文窗口限制？
**【核心思路】**
OpenClaw通过会话压缩、Memory Flush与Memory Search减少长期会话对窗口的占用；工具和文件内容应按需读取，而非全量注入。独立子Agent默认使用隔离上下文，只有确需当前对话时才Fork。

压缩会丢失细节，因此关键约束、决定和引用应写入可审查的工作区文件或Artifact。具体上下文上限取决于所选模型，不能把磁盘Memory容量等同于模型Context Window。

---

#### 37、OpenClaw 如何实现多 Agent 协作？
**【核心思路】**
OpenClaw有两类机制：配置多个Agent并用Bindings把渠道、账号或对话路由到指定Agent；以及由当前Run通过`sessions_spawn`启动后台子Agent。每个配置Agent有自己的工作区、Agent目录和会话存储，子Agent则在独立会话运行并向请求方回报。

子Agent默认不复制完整主会话，也不拥有全部会话/消息工具；权限还受Profile、Tool Policy和Sandbox限制。它们适合研究、慢任务和弱依赖并行，不应默认并发写同一资源。

---

#### 38、OpenClaw 中的 Planner 如何实现？
**【核心思路】**
官方文档没有把OpenClaw描述为固定的“独立Planner服务+TODO DAG”架构。任务拆解通常由所选模型、系统指令、Skill或外部Harness完成；子Agent工具可以执行明确的委派。

若企业需要可审计规划，应在应用层把目标、依赖、负责人、验收和预算写成结构化任务，并由Gateway会话或外部工作流驱动。该方案属于扩展设计，不应冒充OpenClaw默认内部实现。

---

#### 39、OpenClaw 如何做任务拆解？
**【核心思路】**
OpenClaw可由主Agent把独立研究或慢任务委派给子Agent，但官方没有规定统一DAG算法。可靠做法是把复杂任务拆成输入清楚、输出可交付、权限有限且能独立验证的子任务，并限制并发和嵌套深度。

强依赖步骤留在同一会话顺序执行；并行任务通过Artifact而非共享隐式上下文交接。拆解质量用完成率、冲突率、重复工作和单位成功成本验证。

---

#### 40、OpenClaw 如何实现工具调用决策？
**【核心思路】**
模型根据当前上下文与可见工具描述产生调用，Gateway再应用工具Profile、Allow/Deny、Sandbox和Elevated等策略。模型“想调用”不等于获准执行，宿主策略才是权限边界。

提高正确率应精简工具面、准确描述Schema、调用前校验参数与身份、调用后验证业务状态。外部内容和工具返回都视为不可信，不能用其中指令扩大权限。

---

#### 41、OpenClaw 如何接入 MCP 工具？
**【核心思路】**
当前`openclaw mcp`有两条明确路径：`openclaw mcp serve`让OpenClaw作为MCP Server，通过stdio向外部客户端暴露Gateway支持的渠道会话；`mcp add/set/configure/...`管理外部MCP Server定义，供符合条件的Runtime使用。

接入后应以`status/doctor/probe`验证连接与能力，并用Include/Exclude过滤工具。远程HTTP可配置OAuth，静态Secret不得写入仓库。还需区分MCP与ACP：托管Coding Harness会话使用ACP，不应混称为MCP。

---

#### 42、OpenClaw 如何管理 Prompt 版本？
**【核心思路】**
OpenClaw通过工作区文件、Agent配置、Skills和Plugins影响行为，但官方文档没有承诺内建完整的企业Prompt Registry与灰度系统。

生产建议把`AGENTS.md`、`SOUL.md`、Skills及相关配置纳入Git或配置发布系统，记录OpenClaw、模型和工具版本，经过Review、离线评测、灰度和回滚再发布。该治理链是企业扩展，而非默认产品能力。

---

#### 43、OpenClaw 如何实现任务 Checkpoint 恢复？
**【核心思路】**
OpenClaw会持久化会话和本地状态，也支持压缩与Memory，但这不等同于每一步具有事务化Checkpoint和Exactly-once恢复。子Agent完成通知在Gateway重启场景也可能丢失。

需要强恢复语义时，应由外层任务系统保存阶段状态、输入hash、Artifact、幂等键和后置条件；恢复前验证资源是否已改变，再决定重放、补偿或人工接管。不要把建议方案描述成OpenClaw当前保证。

---

#### 44、OpenClaw 如何保证 Agent 执行稳定性？
**【核心思路】**
官方运维能力包括`status`、`health`、`logs`、`doctor`、模型Fallback以及任务/子Agent检查。工具策略、Sandbox、渠道Allowlist和资源限制用于缩小故障与误操作影响。

稳定性仍需外部SLO、超时、并发上限、幂等、依赖监控和故障演练。模型Fallback只覆盖符合条件的模型/认证故障，不能替代工具、渠道或业务错误处理。

---

#### 45、OpenClaw 如何实现模型切换与熔断？
**【核心思路】**
用户可用`/model`切换当前会话模型，配置可为默认或单个Agent指定Primary与Fallback。运行时先在当前Provider轮换认证Profile，遇到可Failover的错误后再沿Fallback链切换，并在恢复后探测原模型。

显式用户选择通常是严格选择，不一定自动走默认Fallback；不同来源的模型选择有不同规则。因此应按实际配置和错误类型验证，不能笼统声称所有超时或限流都会无感切换。

---

#### 46、OpenClaw 如何设计 Agent 状态机？
**【核心思路】**
OpenClaw确实维护会话、后台任务、子Agent和路由状态，但官方没有将其描述为用户可配置的通用业务状态机。

若业务需要Created、Running、WaitingApproval、Succeeded、Failed等严格状态，应由外部Workflow或Plugin持久化合法转移、版本和幂等键，OpenClaw只作为交互与执行入口。这样可避免把内部会话状态误当作业务事务状态。

---

#### 47、OpenClaw 如何做任务完成率评估？
**【核心思路】**
OpenClaw官方没有定义适用于所有任务的内建“完成率”。应由场景Owner建立有效任务分母和Acceptance Criteria：消息发送看目标渠道状态，定时任务看实际交付，研究任务看引用和人工Rubric，ACP编码任务看Patch、编译和测试。

报告Strict/Partial完成率、人工接管、重试、P95和单位成功成本，并关联OpenClaw、模型、Skill和工具版本。不能用模型的最终文本或单次工具成功代替任务完成。

---

#### 48、OpenClaw 如何实现 Workflow 编排？
**【核心思路】**
OpenClaw提供Cron、Heartbeat、Hooks、Skills、会话和子Agent等自动化组件，但不应据此声称它等同于完整BPMN或耐久工作流引擎。

确定性的审批、事务、补偿和Exactly-once调度应放在专业Workflow系统；OpenClaw负责自然语言交互、非确定性判断和工具调用。二者通过任务ID、回调、Artifact和幂等接口衔接。

---

#### 49、OpenClaw 如何设计 Memory 检索机制？
**【核心思路】**
Memory事实来源是工作区Markdown文件，语义搜索可配置OpenAI、本地或其他支持的Embedding Provider。磁盘文件是耐久存储，检索只把相关片段带回有限模型上下文。

应保留来源文件和日期，定期清理陈旧或冲突记忆。使用外部Provider做Embedding时，相关内容会发送给该服务；若有数据不出域要求，应选择本地Provider并实测索引质量。

---

#### 50、OpenClaw 如何降低 Token 消耗？
**【核心思路】**
优先使用会话压缩、Memory按需检索、精简工具与Skill、裁剪长工具输出，并让隔离子Agent只接收完成任务所需的上下文。不同Agent和Cron任务可配置更便宜模型，但工具型不可信输入不应为降本而使用明显不足的模型。

监控输入、输出、缓存、工具返回和子AgentToken，以及每个成功任务的总成本。官方文档未保证所有Provider都具备相同的前缀缓存或计费行为，应以Provider账单和实测为准。

---

#### 51、OpenClaw 在企业级生产环境如何落地？
**【核心思路】**
先接受其官方信任模型：一个Gateway对应一个可信操作者边界；互不信任的员工、客户或租户应拆分OS用户、主机和Gateway。再配置渠道配对/Allowlist、工具Policy、Sandbox、最小文件和网络权限及短期凭据。

明确消息平台、模型Provider和Embedding Provider的数据流、区域与保留；上线前做红队、备份恢复、升级回滚和事件响应。企业Prompt发布、集中审计、SLO和成本分摊通常需要外部平台补齐。

---

#### 52、OpenClaw 如何实现 Agent 可观测性建设？
**【核心思路】**
内建入口包括`openclaw status`、`gateway status`、`health`、`logs`、`doctor`以及任务/子Agent检查，可观察Gateway、渠道、Provider、会话和运行故障。

企业扩展应把请求ID贯穿渠道、会话、模型和工具，记录工具名、参数摘要、结果状态、时延、Token、路由和审批；敏感Prompt与媒体需脱敏和分级保留。记录决策摘要与外部证据即可，不应把不可验证的隐藏思维链当审计事实。

---

#### 53、OpenClaw 如何进行 Agent 性能优化？
**【核心思路】**
先用Trace拆分渠道、排队、模型首Token、工具和交付耗时，再优化关键路径。可减少无关工具与上下文、给独立子Agent设置并发上限、按任务选模型，并缓存稳定的外部查询结果。

当前原生Agent会话共享Gateway进程资源，增加并发可能造成竞争；不能按“无状态Runtime可无限水平扩展”估算容量。应压测目标硬件并设置SLO、限流、超时和资源隔离。

---

#### 54、OpenClaw 如何设计多模型调度策略？
**【核心思路】**
当前可按Agent设置默认模型、按Cron任务覆盖模型、给子Agent指定模型，并允许用户用`/model`切换；Primary/Fallback负责故障切换。这是配置式路由，不等同于内建的自动难度分类或在线Bandit。

需要自适应调度时，可在外层按任务、风险和成本选择目标Agent/模型，并以完成率和安全门槛验证。具备文件、网络或不可信内容工具的Agent不宜仅为省钱路由到抗注入能力不足的模型。

---

#### 55、OpenClaw 如何保证工具调用安全性？
**【核心思路】**
先用渠道配对和Allowlist限制谁能发指令，再用Tool Profile与Allow/Deny限制能调用什么；Sandbox限制文件、进程和网络范围，Elevated能力另设门槛。外部网页、邮件和媒体内容统一视为不可信。

Exec Approval只是操作者意图护栏，不是敌对多租户隔离；强边界需要独立OS用户/主机/Gateway。对写入、外发和设备控制采用短期凭据、预览确认、后置校验和审计。

---

#### 56、OpenClaw 如何支持大规模 Agent 集群部署？
**【核心思路】**
截至当前官方文档，OpenClaw Agent会话的Loop、工具和推理运行在**单机Gateway进程**；“Cloud workers plan”明确标注为尚未实现的提案。因此不能声称已有Redis Checkpoint、Kubernetes无状态接管或通用分布式调度。

现阶段扩展方式是控制单Gateway并发、将互不信任边界拆为多个Gateway，并用外部编排、监控和负载入口管理实例。若需要每任务隔离的远程Worker，应自行实现或等待官方能力，并通过故障恢复、状态一致性和安全评测后再称为生产集群方案。

---

## 官方核验资料

- [OpenClaw 文档索引](https://docs.openclaw.ai/llms.txt)
- [Gateway 架构](https://docs.openclaw.ai/concepts/architecture)
- [Agent Runtime](https://docs.openclaw.ai/agent)
- [Memory](https://docs.openclaw.ai/concepts/memory)
- [工具、Skills 与 Plugins](https://docs.openclaw.ai/tools)
- [Sandboxing](https://docs.openclaw.ai/gateway/sandboxing)
- [Security](https://docs.openclaw.ai/gateway/security)
- [Sub-agents](https://docs.openclaw.ai/subagents)
- [Automation](https://docs.openclaw.ai/automation)
- [ACP Agents](https://docs.openclaw.ai/tools/acp-agents)

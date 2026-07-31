# 十二、Claude Code

> 本章共 **100** 题，覆盖 Claude Code 的 Agent Loop、请求与消息生命周期、上下文与Prompt Cache、代码库探索、工具与权限、Hooks、MCP、Subagents、Agent Teams、Checkpoint、Agent SDK、CI/CD、可观测性和企业治理。
>
> 内容按 **2026-07-31** 可访问的 Claude Code 官方文档核验。不同终端、IDE、Desktop、Web、订阅方案和模型Provider的功能可能不同，面试回答应给出版本与运行Surface，避免把建议架构描述成产品内部实现。

#### 1、Claude Code 的产品定位是什么？它与 IDE 补全工具有什么区别？
Claude Code 是可在终端、IDE、Desktop和Web使用的**Agentic Coding Tool**，能够自主读取代码库、编辑文件、运行命令并连接开发工具。它的核心单位是一个围绕任务持续执行的Agent Session，而不是单次生成下一行代码。

IDE补全主要根据光标附近上下文给出局部建议；Claude Code会主动搜索、制定或调整步骤、跨文件修改并运行验证。它仍需要明确验收、权限和人工Review，不能把模型最终回复当作代码正确性的证据。

**相关知识点：** Coding Agent、Agent Session、代码补全、Tool Use、验证闭环、Human Review。

---

#### 2、Claude Code 的 Agent Loop 是如何工作的？
Agent Loop可概括为**接收目标—评估状态—请求工具—执行工具—回灌结果—继续或输出最终结果**。一次“思考并调用一组工具、接收结果”的循环构成一个Turn，直到模型不再调用工具或达到停止条件。

Runtime向模型提供系统提示、项目指令、会话历史和工具定义；Hooks可在关键事件拦截、修改或阻止动作。复杂任务可能经历多轮读取、编辑、测试和修正，因此要设置权限、最大轮数、成本和业务验收，避免无限循环或“文本完成”。

**相关知识点：** Agentic Loop、Turn、Tool Result、Hook、Max Turns、停止条件。

---

#### 3、Claude Code 如何理解大型代码库，而不把整个仓库放进上下文？
它采用**代理式探索和按需取证**：先读取项目规则与目录结构，再用Glob、Grep、Read、Git、代码智能和构建反馈定位相关符号，只展开当前任务需要的文件和范围。

大型仓库可使用根级与子目录`CLAUDE.md`、`.claude/rules/`、按包Skills、稀疏Worktree和明确的构建命令缩小搜索面。公开文档没有保证默认维护完整向量索引或Call Graph，因此面试中应把这类索引描述为可接入的增强方案，而非既定内部实现。

**相关知识点：** Agentic Search、Progressive Context、Grep、Code Intelligence、Monorepo、Sparse Worktree。

---

#### 4、Claude Code 的上下文由哪些部分组成？为什么会发生 Compaction？
上下文通常包含系统提示、工具Schema、对话历史、`CLAUDE.md`与Rules、已加载Skill、文件片段和工具结果。随着Agent读取文件和运行命令，窗口逐渐被占用；接近上限时会压缩较早对话以继续任务。

Compaction保留摘要而非逐字历史，因此关键目标、约束、决定、失败原因和验证状态应写入稳定文件或清晰摘要。大型工具输出先过滤或落盘再引用。可用上下文检查功能确认实际加载内容，不能把磁盘Transcript、Auto Memory容量等同于模型窗口。

**相关知识点：** Context Window、Prompt Assembly、Compaction、Tool Output、Context Inspection、Artifact。

---

#### 5、CLAUDE.md、`.claude/rules/` 和普通任务提示应如何分工？
`CLAUDE.md`承载跨会话稳定的项目约定，`.claude/rules/`适合拆分主题或路径相关规则，任务提示描述本次目标和验收。

1. 根级规则写架构、构建、测试和仓库级禁令。
2. 子目录规则只描述对应模块，避免把所有细节常驻上下文。
3. 本地个人偏好放`CLAUDE.local.md`或用户级配置，不污染团队仓库。
4. 临时Bug信息和一次性步骤留在任务Prompt或Issue。

多个层级通常是叠加加载，不应依赖隐含“最深文件必然覆盖”来解决冲突；规则应无冲突或显式声明优先关系。

**相关知识点：** CLAUDE.md、Rules、Path Scope、Persistent Instructions、Local Override、指令冲突。

---

#### 6、Claude Code 的 Auto Memory 与 CLAUDE.md 有什么区别？
`CLAUDE.md`是团队或用户**主动维护的规范性指令**，Auto Memory是Claude在使用中积累的**经验性笔记**。前者应被Review并纳入版本管理，后者更适合个人环境、调试发现和重复偏好。

Auto Memory可能过时、误归纳或只适用于某台机器，不能用来保存密钥、业务权威事实或替代仓库文档。稳定且被验证的经验应提升为`CLAUDE.md`、Rule、Skill或正式文档；错误记忆要可查看、修正和删除。

**相关知识点：** Auto Memory、Explicit Memory、Team Policy、Provenance、Memory Promotion、知识治理。

---

#### 7、Claude Code 中 CLAUDE.md、Skills、Subagents、Hooks、MCP 和 Plugins 如何选型？
它们分别解决不同层次的扩展问题。

| 机制 | 主要用途 |
|---|---|
| CLAUDE.md / Rules | 常驻项目约定 |
| Skill | 按需加载的知识与工作流 |
| Subagent | 隔离上下文和角色的委派 |
| Hook | 生命周期上的确定性控制 |
| MCP | 接入外部工具和数据 |
| Plugin | 打包分发Skills、Agents、Hooks和MCP |

不要用常驻规则塞入大篇操作手册，也不要用Prompt代替安全Hook。选择原则是信息是否常驻、是否需要新权限、是否要求确定性、是否需要独立上下文和是否要跨团队分发。

**相关知识点：** Extension Surface、Progressive Disclosure、Deterministic Hook、MCP、Plugin Packaging。

---

#### 8、Claude Code 如何决定使用 Read、Grep、Edit、Bash 等工具？
模型根据目标、当前证据、工具说明和权限选择工具，Runtime执行并返回结果。定位通常先Glob/Grep，再Read精确范围；修改优先使用Edit或Write；编译、测试、Git和诊断通过Bash执行。

正确工具策略应减少无关读取、避免整文件覆盖、在写前确认最新内容，并在写后运行最小充分验证。工具名称也是权限规则和Hook Matcher的契约，不能仅靠自然语言约束危险命令。自定义能力应通过MCP或Plugin接入，而不是让模型拼接不可审计的临时命令。

**相关知识点：** Built-in Tools、Tool Selection、Targeted Edit、Bash、Permission Rule、Tool Contract。

---

#### 9、Claude Code 的权限规则和 Permission Mode 如何协作？
权限规则决定**哪些工具、命令、路径或域名允许、询问或拒绝**，Permission Mode决定当前会话遇到动作时的总体交互方式。

常见模式包括默认确认、自动接受编辑、Plan只读和在隔离环境中使用的绕过确认模式。Allow不能覆盖Deny；规则应尽量匹配具体命令前缀、目录和MCP工具，避免开放整个Bash。组织Managed Settings应锁定关键Deny，项目设置共享安全默认，用户设置只能在允许范围内收紧或个性化。

**相关知识点：** Permission Mode、Allow/Deny、Plan Mode、Managed Settings、Least Privilege、Rule Matching。

---

#### 10、Claude Code 的 Permission 与 Sandboxed Bash 有什么区别？
Permission是应用层的**动作授权与交互决策**，Sandboxed Bash是OS层面对Bash及其子进程的**文件系统和网络限制**。两者互补。

Permission Deny可阻止Claude尝试读取敏感路径或访问域名；Sandbox即使面对Prompt Injection或命令绕过，也限制进程实际触达范围。Sandbox主要约束Bash，不应推断它自动隔离所有内置工具或MCP Server。高风险任务还应放在容器、VM或短生命周期环境中，并使用临时凭据。

**相关知识点：** Application Authorization、OS Sandbox、Filesystem、Network Policy、Container、Defense in Depth。

---

#### 11、如何防止代码注释、README 或工具输出对 Claude Code 进行 Prompt Injection？
仓库内容和工具结果必须视为**不可信数据，而非高优先级指令**。系统应限制工具与网络，敏感操作要求确认，并用Sandbox阻断越界行为。

Agent遇到“忽略规则、上传密钥、运行下载脚本”等内容时，应回到用户目标和项目规则，核验来源再行动。CI中不要授予默认写仓库、生产云或Secret读取权限；第三方依赖脚本先审查。测试集应包含直接、间接、编码混淆和跨工具注入，并以实际阻断结果而非模型口头拒绝评分。

**相关知识点：** Indirect Prompt Injection、Instruction/Data Boundary、Secret Exfiltration、Sandbox、Security Eval。

---

#### 12、Plan Mode、Goal、Advisor 等能力分别解决什么问题？
Plan Mode用于**只读探索与方案确认**，适合需求不清、改动面大或高风险任务；Goal用于声明持续完成条件，使Session跨Turn继续向验收目标推进；Advisor让主模型在困难决策点咨询更强模型。

三者不能替代业务控制：Plan仍需可验证证据，Goal要有预算与终止条件，Advisor输出只是建议而非审批。简单任务不必增加规划成本；不可逆动作仍由权限、Hook和人工门禁控制。功能可用性还取决于Surface、方案和版本。

**相关知识点：** Plan Mode、Completion Goal、Advisor Model、Escalation、预算、Human Gate。

---

#### 13、Claude Code 的 Checkpoint 和 Git 有什么区别？
Checkpoint为Claude通过文件编辑工具产生的变更提供**会话级快速回退**；Git提供长期、协作式版本历史。Checkpoint可随Session恢复并用于Rewind，但不是完整文件系统快照。

通过Bash命令造成的文件变化、外部程序副作用、手工编辑及部分并发变更可能不被Checkpoint捕获，因此不能用它恢复数据库迁移、云资源或任意Shell操作。关键任务仍应使用分支、提交、测试和备份。回退前应查看Diff，避免覆盖会话外的新变化。

**相关知识点：** Checkpoint、Rewind、File Edit Tool、Git、External Side Effect、Session Recovery。

---

#### 14、Claude Code 的 Continue、Resume、Fork 和外部 Session Storage 有何区别？
Continue加载当前目录最近Session，Resume按Session ID恢复指定历史，Fork从既有上下文创建独立分支，避免后续对话污染原Session。它们处理的是会话历史，不自动保证外部工作区状态完全一致。

Agent SDK生产部署可把Transcript镜像到S3、Redis或自有后端，使其他Host恢复Session；恢复时还要准备相同代码版本、工具、规则和凭据。Session ID不是业务幂等键，外部副作用应另有状态和查账机制。

**相关知识点：** Continue、Resume、Fork Session、Transcript、External Storage、Environment Rehydration。

---

#### 15、Claude Code Hooks 与普通Prompt规则有什么区别？
Hook是在Session、工具、通知、Subagent等生命周期事件上运行的**确定性程序化控制**；Prompt规则只影响模型决策，不能保证必然执行。

PreToolUse可校验或阻止命令，PostToolUse可格式化、扫描或记录结果，Stop/SubagentStop可根据验证结果要求继续，Notification可转发等待确认事件。Hook必须快速、幂等、超时可控并处理不可信JSON输入；项目Hook本身也属于可执行代码，应Review和限制权限。

**相关知识点：** PreToolUse、PostToolUse、Stop Hook、SubagentStart、Matcher、Deterministic Guardrail。

---

#### 16、Claude Code 如何通过 MCP 扩展工具？大工具集如何控制上下文成本？
MCP Server向Claude Code暴露标准化Tool、Resource或Prompt，可按本地、项目或用户Scope配置。接入时要验证Transport、认证、Schema、超时和Server权限，并通过Managed MCP限制组织可连接的Server。

工具数量很大时，可使用Tool Search按需加载符合任务的工具定义，避免所有Schema常驻上下文。Tool Search提高发现效率但不授予权限；最终调用仍受Allow/Deny、Hook、Sandbox和目标服务ACL约束。MCP返回内容同样可能包含恶意指令。

**相关知识点：** MCP Server、Configuration Scope、Managed MCP、Tool Search、Deferred Loading、ACL。

---

#### 17、Claude Code Subagent 适合解决什么问题？如何避免滥用？
Subagent拥有独立上下文、工具集合、模型和专用指令，适合代码探索、安全Review、测试分析等**可独立交付且上下文噪声大的任务**。

主Agent应传递目标、范围、证据和输出契约，而非模糊地要求“看看”。只读探索Agent不应拥有Edit/Bash写权限；修改任务要避免多个Agent同时触碰同一文件。子Agent会增加Token、等待和汇总偏差，应按风险和可并行性选择，并由主Agent验证结果。

**相关知识点：** Context Isolation、Custom Subagent、Tool Allowlist、Delegation Contract、Result Verification、成本。

---

#### 18、Subagents、Agent Teams 和 Agent View 有什么区别？
Subagent是主Session内部的任务委派；Agent Teams让多个Claude Code实例围绕共享任务、消息和协调机制协作；Agent View是从一个界面派发和监控多个Session的管理Surface。

| 机制 | 协作关系 | 适用场景 |
|---|---|---|
| Subagent | 主从、结果回传 | 有边界的研究与Review |
| Agent Teams | 多实例协作 | 大型并行任务与角色分工 |
| Agent View | 人管理多个Session | 多仓库或多任务运营 |

并行度不是越高越好。共享依赖、同文件修改和不清晰验收会放大冲突与成本。

**相关知识点：** Agent Teams、Agent View、Shared Task、Inter-agent Messaging、Orchestration。

---

#### 19、多个 Claude Code Session 并行修改代码时如何避免冲突？
采用**任务分片—隔离Worktree/分支—单一集成者—合并后全量验证**。按模块、文件或职责划分范围，每个Session基于固定Base Commit工作并生成最小Diff。

Desktop和其他Surface可提供Git隔离，但仍要记录Base SHA。合并时使用三方合并，重叠符号和接口变化由人或集成Agent审查；禁止共享目录里的最后写入胜出。目标Branch变化后Rebase并重新测试。数据库Schema、锁文件和公共接口等热点资产应串行修改。

**相关知识点：** Git Worktree、Branch Isolation、Base SHA、Three-way Merge、Merge Queue、Hotspot File。

---

#### 20、如何在 CI/CD 中安全运行 Claude Code？
CI使用非交互Agent SDK或Print模式，输入固定任务，设置允许工具、最大Turn、结构化输出和超时。工作区使用临时Runner或容器，凭据按Job短期签发，默认只读仓库。

自动修复应创建分支或PR而非直推保护分支；测试、静态分析、策略和人工Review仍是发布门禁。来自Issue、PR和代码的文本均不可信，不能让其控制Secret或任意网络。保存Session ID、版本、Diff、测试和成本，失败时输出可诊断状态而不是无限重试。

**相关知识点：** Headless Mode、Agent SDK、Ephemeral Runner、OIDC、Protected Branch、Structured Output。

---

#### 21、Claude Agent SDK 与直接调用 Claude API 或 Claude Code CLI 有什么区别？
Claude API提供模型原语，需要应用自己实现Agent Loop、工具执行和会话；Claude Code CLI面向开发者交互；Claude Agent SDK把与Claude Code相同的**循环、工具和上下文管理**作为Python/TypeScript库嵌入应用。

SDK适合需要程序控制工具、权限、Hooks、流式消息、Session和结构化结果的产品。它不是无状态封装：生产部署要管理持久工作目录、子进程、会话存储、隔离和成本。简单文本生成仍可直接使用Messages API，避免引入完整Agent运行时。

**相关知识点：** Messages API、CLI、Claude Agent SDK、Embedded Runtime、Stateful Session、Build vs Buy。

---

#### 22、Claude Agent SDK 如何处理结构化输出、审批和用户澄清？
结构化输出允许Agent经过多轮工具执行后，按JSON Schema、Zod或Pydantic返回可校验结果；审批与澄清则通过SDK事件向宿主应用请求用户输入，再把决定送回Session。

Schema校验失败应重试有限次数或返回明确错误，不能把未验证文本强转成业务对象。审批请求要展示动作、目标、风险和参数，设置超时与取消；Web服务需把Session和正确用户绑定，防止他人批准。高风险操作在批准后仍要由后端重新鉴权。

**相关知识点：** Structured Output、JSON Schema、Approval Flow、User Input、Session Binding、TOCTOU。

---

#### 23、Claude Code 如何降低 Token 成本并保持质量？
先减少无关上下文：精简`CLAUDE.md`、让Skill按需加载、用Grep定位后局部Read、过滤长日志、把稳定产物落盘。Prompt Caching可复用稳定前缀，但修改规则、切模型或频繁改变工具集合会降低命中。

按任务复杂度选择模型和Thinking预算，独立探索可交给较便宜Subagent，但高风险判断不应只为省钱降级。跟踪输入、输出、缓存读写、工具输出、子Agent和每个成功任务总成本；以质量约束下的单位成功成本优化，而非单次Token最少。

**相关知识点：** Prompt Caching、Context Hygiene、Model Routing、Thinking Budget、Cost per Success。

---

#### 24、Claude Code 和 Agent SDK 如何建设可观测性？
可观测性应关联**Session—Turn—Model—Tool—Hook—Subagent—Result**。CLI可启用使用监控，Agent SDK可导出OpenTelemetry Trace、Metric和Event。

记录模型与Prompt/规则版本、工具名、耗时、状态、Token、费用、权限决定和验证结果；源码、Prompt、Secret与工具原文按敏感级别脱敏或只保存Hash/受控引用。异步Session和容器迁移使用Session ID与业务Task ID关联。关键指标包括完成率、P95、工具失败、权限阻断、重试、缓存和单位成功成本。

**相关知识点：** OpenTelemetry、Trace、Metric、Event、Session ID、Cost Attribution、PII Redaction。

---

#### 25、企业如何通过 Managed Settings 和 LLM Gateway 治理 Claude Code？
Managed Settings集中下发不可被普通用户放宽的权限、MCP、网络和功能策略；LLM Gateway集中处理认证、模型访问、用量、预算、审计和路由。二者分别治理客户端行为和模型流量。

上线前要验证Gateway完整转发Claude Code需要的API字段、流式响应和Beta能力，避免静默降级。客户端仍需Sandbox与最小工具权限，Gateway也不能替代代码仓库和云资源ACL。配置变更应版本化、灰度、监控并可回滚，开发者可查看Effective Config以便排障。

**相关知识点：** Managed Settings、LLM Gateway、Policy Enforcement、Spend Limit、Protocol Compatibility、Effective Config。

---

#### 26、Claude Code 的 Anthropic、Bedrock、Google Cloud 和 Microsoft Foundry 部署如何选型？
选择取决于**现有云治理、模型可用性、区域、IAM、采购、日志和功能兼容性**。直接Anthropic通常获得原生更新路径；云Provider便于复用企业账号、网络和审计体系，但模型名称、区域、配额和部分Feature Availability可能不同。

不要把Provider切换当成完全透明。应建立版本矩阵，测试工具调用、长上下文、缓存、流式、Agent Teams、Web/IDE Surface和Gateway。凭据使用短期身份或Helper，按团队和环境分账；Fallback前确认数据区域与合规允许。

**相关知识点：** Anthropic API、Amazon Bedrock、Google Cloud、Microsoft Foundry、IAM、Feature Matrix。

---

#### 27、Claude Code 的 Code Review 如何减少误报和漏报？
有效Review需要**明确差异范围、仓库上下文、严重级别和可验证证据**。`CLAUDE.md`提供项目约定，Review专用规则可放`REVIEW.md`；多Agent分析发现候选后，应检查可达路径、测试和上下游影响再报告。

每条Finding至少包含位置、触发条件、影响和修复建议，风格偏好不能冒充Bug。用历史真实缺陷、无缺陷PR和对抗样本校准Precision/Recall，按语言和风险切片。自动Review是合并门禁的输入之一，不能替代测试、安全扫描和Owner审批。

**相关知识点：** Code Review、REVIEW.md、Multi-agent Analysis、Finding Evidence、Precision、Recall。

---

#### 28、Claude Code 修改代码后应如何设计验证闭环？
验证顺序应从**最小、快速、确定性检查**逐步扩大：格式化与静态检查、受影响单测、组件/集成测试、构建，再按风险运行端到端与安全测试。

Agent先从仓库规则或CI配置找到权威命令，失败后区分代码缺陷、环境缺失、测试Flaky和既有失败。修复循环设置次数和时间预算，每次改动都要说明与失败证据的关系。最终报告实际运行的命令、结果、未执行项和剩余风险，禁止把“看起来正确”当验证。

**相关知识点：** Test Pyramid、Static Analysis、Affected Tests、Flaky Test、Retry Budget、Verification Evidence。

---

#### 29、如何构建 Claude Code 的离线评测集和上线门禁？
评测集应包含真实Issue、Bug修复、跨文件功能、重构、测试生成、Review、安全任务和历史失败，并固定仓库Commit、依赖与执行环境。

核心指标包括Patch Apply、编译、测试、隐藏测试、任务完成、非预期Diff、安全违规、人工介入、P95和单位成功成本。采用容器重复运行，记录模型、Claude Code、规则、Skill、Hook和MCP版本；确定性测试优先，LLM Judge仅用于语义Rubric并经人工校准。新版本必须总体提升且关键风险切片无回归。

**相关知识点：** Coding Agent Eval、Repository Snapshot、Hidden Test、Patch Correctness、Regression Gate、LLM Judge。

---

#### 30、企业推广 Claude Code 时如何衡量真实价值，而不是只看使用量？
使用量只说明调用发生，价值应看**质量调整后的工程结果**。建立采用前基线，比较Issue周期、PR吞吐、Review等待、缺陷逃逸、回滚、人工返工和开发者满意度。

按任务类型和团队做Cohort，计算被接受并上线的改动比例、净节省时间、单位成功成本和安全事件。控制任务难度、人员经验与并行流程变化，避免把相关性当因果。Pilot先覆盖低风险高频任务，达到质量、安全和经济门槛后再扩大权限；无收益或返工增加时应缩小场景。

**相关知识点：** Adoption、Acceptance Rate、Lead Time、Defect Escape、Cohort、TCO、ROI。

---

## 原章节迁移题（50 题）

> 以下题目由「Agent 核心架构」「任务规划与执行」「工具与能力体系」「工程落地与平台化」迁入，保留原答案内容并统一纳入 Claude Code 专章。

#### 31、Claude Code、Cursor、OpenCode 等 Agent 的 Runtime 有哪些共同点？
**【核心思路】**
它们本质是同一类"**编码 Agent**"，Runtime 共性明显：**ReAct 式主循环 + 丰富的文件/命令/搜索/编辑工具 + Agentic Search（而非纯 RAG）+ 大代码库上下文管理 + 危险操作权限确认 + 项目级记忆（规则文件）**。

**【深入拆解】**
- **共同的主循环**：都是"LLM 决策 → 调工具 → 看结果 → 再决策"的 ReAct 循环，直到任务完成，带最大步数护栏。
- **共同的工具集**：文件读写、Bash/终端执行、代码搜索（grep/glob）、**基于 diff 的精确编辑**、以及 **MCP** 扩展外部工具。
- **共同的 Context 策略——Agentic Search**：面对大代码库都**不做一次性全库向量 RAG**，而是让 Agent 自己按需 grep/read 探索（更精确、更省 Token）。这是编码 Agent 的关键共识。
- **共同的安全模型**：写文件、执行命令等**破坏性操作走用户确认/权限白名单**。
- **共同的项目记忆**：都有项目级配置/规则文件（CLAUDE.md、`.cursorrules` 等）注入长期约定。
- **差异点**：Cursor 深度绑 IDE、有 Tab 补全；Claude Code/OpenCode 偏 CLI/终端；OpenCode 强调开源与模型无关。

| 共同点 | 具体表现 |
|---|---|
| 主循环 | ReAct + 步数护栏 |
| 工具 | 文件/Bash/搜索/diff 编辑/MCP |
| Context | Agentic Search 按需加载 |
| 安全 | 危险操作确认 |
| 记忆 | 项目规则文件 |

---

#### 32、Claude Code、OpenAI Codex、Cursor 等代码Agent是如何进行任务识别和路由的？
**三类产品公开呈现的共同机制是“理解请求—获取上下文—选择工具—执行—验证”，但内部分类器与评分算法未完整公开。**

1. 它们依据请求、文件、仓库规则、会话和模式判断问答、修改、调试或开发，再决定搜索、编辑、命令或工具。执行中根据检索、编译和测试反馈继续选路，属于动态**Agent Loop**。

| 产品 | 官方公开的路由入口 | 执行与安全特征 |
| --- | --- | --- |
| Claude Code | 上下文、工具、权限模式 | 探索、编辑、命令、MCP |
| OpenAI Codex | 请求、AGENTS、Skill、工具 | 循环、沙箱、审批、测试 |
| Cursor | Ask、Manual、Agent、Custom | 搜索、编辑、终端、Diff |

2. Claude Code按需探索代码库，可限制工具并恢复会话；Codex由Harness协调用户、模型与工具，以沙箱和审批控制动作；Cursor提供模式路由：Ask只读，Manual精确编辑，Agent处理多文件任务，Custom配置工具。

3. 能力路由还选择搜索、读取、编辑、终端、测试和MCP。项目规则提供上下文，权限或模式决定动作，测试与Diff验证结果；高风险命令由**沙箱或审批**门控。

4. 不能根据界面断言内部使用分类模型、DAG或置信度公式。比较时固定版本，用同一任务集评估完成率、误修改率、确认次数、调用数、P95延迟、成本与恢复能力。

**相关知识点：** Agent Loop、代码检索、工具路由、项目规则、MCP、沙箱、权限审批、Diff审查、版本评测。

---

#### 33、Claude Code、OpenAI Agent、Manus等Agent在任务规划方面有哪些共同设计思想？
**三类Agent都以多轮工具循环推进目标，并用计划、环境反馈、权限门控和人工介入提高长链可靠性。**

1. 它们反复经历“理解—行动—调用工具—观察—修正”。计划不一定是完整DAG：简单任务边执行边决策，复杂或高风险任务显式展示方案、约束与检查点。

| 产品公开能力 | 可验证设计信号 | 体现的思想 |
| --- | --- | --- |
| Claude Code | Plan模式、权限、会话恢复 | 受控工具循环 |
| OpenAI Agents SDK | Tools、Handoffs、Guardrails、Tracing | 编排与观测 |
| Manus | Plan Mode、确认执行、沙箱 | 计划审阅与隔离 |

2. 三者均强调**工具落地与环境反馈**：Agent通过文件、命令、浏览器或连接器获取状态，结果影响下一步；不能把“准备调用”当作“已完成”。代码任务需用测试或产物验收。

3. 共同安全设计是最小权限、隔离和关键动作确认。Claude Code公开工具权限；OpenAI公开Guardrails和沙箱；Manus Plan Mode要求确认计划后再构建。长任务保存会话、文件或环境。

4. 公开资料只能证明产品能力，不能证明内部算法。选型应固定版本，用同一任务集比较完成率、误执行率、接管率、P95时延、成本和恢复能力，避免从界面推断实现。

**相关知识点：** Agent Loop、Tool Use、Plan Mode、Guardrails、Sandbox、Human-in-the-loop、Tracing、会话恢复、产品评测。

---

#### 34、LangGraph、OpenAI Agents SDK、Claude Code等Agent框架分别如何实现任务恢复与重新规划？
**三者都能继续任务，但恢复边界不同：LangGraph面向图状态，OpenAI SDK面向运行或会话，Claude Code面向对话与文件。**

1. LangGraph按Thread保存图快照，失败后从成功步骤恢复，并复用同轮已完成节点。Interrupt以相同thread_id继续；Replan需用条件边、Command或Planner节点实现。

2. OpenAI SDK用Session保存历史，HITL可序列化RunState并在审批后继续。Runner执行模型、工具与Handoff循环，但**副作用持久化、补偿及全局Replan由应用层实现**。

| 框架 | 主要恢复单元 | 重新规划方式 |
| --- | --- | --- |
| LangGraph | 图快照 | 条件边、Planner |
| OpenAI SDK | RunState、Session | 模型循环、应用编排 |
| Claude Code | 会话、文件快照 | 提示、Plan或分支 |

3. Claude Code可续接或分支会话；编辑前保存文件，rewind可恢复代码、对话或两者。它不跟踪Bash与外部变化，不能替代Git或Saga；Replan主要靠调整提示、回退或分支，并非公开DAG算法。

4. **会话恢复不等于执行恢复，文件回退不等于副作用补偿**；关键写操作仍需幂等键、业务快照与审计。

**相关知识点：** 图快照、RunState、Session、Handoff、Checkpoint、Rewind、Replan、幂等、Saga。

---

#### 35、Claude Code的任务调度机制是什么？
**Claude Code的核心调度是受权限和预算约束的Agent循环；定时任务、子Agent与并行工具调用属于其上层调度能力。**

1. 每轮由模型读取提示、历史和工具定义，选择文本或工具调用；运行时执行工具并把结果反馈模型，直到输出不含工具调用。可用max_turns与预算限制终止。只读工具可并行，Edit、Write、Bash等有状态工具通常串行，防止冲突。

2. 模型依据任务选择Read、Glob、Grep、Bash等工具，权限层再决定允许、询问或拒绝；拒绝结果会返回模型以调整路径。**模型负责下一步决策，Harness负责执行顺序、安全边界、消息传递与资源限制**。

| 调度层 | 执行方式 | 主要边界 |
| --- | --- | --- |
| 主循环 | 模型—工具迭代 | 轮次、预算 |
| 工具批次 | 只读并行、写入串行 | 冲突与权限 |
| Subagent | 独立上下文执行 | 结果回传主Agent |
| 定时任务 | 到期提示入队 | 会话与优先级 |

3. 会话保存上下文并支持resume，接近窗口上限时自动压缩；Subagent使用独立上下文，只把结果返回主会话。定时提示在轮次之间低优先级入队，不会打断正在生成的响应。内部模型如何排序候选行动并未公开，不能臆测为固定DAG或特定搜索算法。

**相关知识点：** Agent Loop、Harness、Tool Use、权限模式、并行只读工具、Subagent、Session、上下文压缩、定时任务。

---

#### 36、Claude Code、Cursor、OpenHands 的 Skill 分层有什么差异？
三者概念并不等价：**Claude Code强调工作流与扩展组合，Cursor偏项目规则和IDE约束，OpenHands强调可触发、可共享的上下文模块**。

1. **Claude Code**：CLAUDE.md承载常驻规则，SKILL.md按需加载知识或流程；可结合MCP、Subagent、Hooks和Plugin，覆盖指令、能力与执行控制。
2. **Cursor**：核心是Rules与Custom Modes。Rules可按路径、相关性、手动或始终附加；Agent使用搜索、编辑、终端和MCP，形成“规则+工具+模式”组合。
3. **OpenHands**：AGENTS.md提供常驻上下文，SKILL.md支持渐进或关键词触发；还支持组织与全局共享，SDK可程序化加载。

| 产品 | 主要分层 | 突出特点 |
|---|---|---|
| Claude Code | 规则→Skill→工具/子代理 | 扩展组合 |
| Cursor | Rules/Mode→工具 | IDE作用域 |
| OpenHands | Context→触发Skill→运行时 | 组织共享 |

不能把Rules、Skill和Subagent直接等价。选型应验证权限、审计、共享、观测和版本治理。

相关知识点：**CLAUDE.md、SKILL.md、Cursor Rules、AGENTS.md、Subagent、Hooks、MCP、渐进加载**。

---

#### 37、Claude Code、OpenHands、Cursor中的Skill路由是如何实现的？
三者都采用“常驻规则+按需能力”，但入口不同：**Claude Code靠描述与命令，OpenHands支持用户、Agent和关键词触发，Cursor按Rules作用域、相关性或手动附加**。

1. **Claude Code**：会话加载Skill名称与描述，模型按相关性加载全文，用户也可用命令调用；可限制仅用户调用，并结合Subagent、MCP与Hooks。CLAUDE.md是常驻记忆。
2. **OpenHands**：AGENTS.md常驻；SKILL.md先暴露摘要，再由用户或Agent按需加载，也支持关键词。项目、用户、组织和全局作用域有优先级。
3. **Cursor**：Rules可始终加载、按文件glob附加、由Agent按描述请求或用户手动引用；嵌套Rules随目录作用域生效，Custom Modes控制工具。

| 产品 | 主要路由信号 | 核心粒度 |
|---|---|---|
| Claude Code | 描述/命令 | Skill工作流 |
| OpenHands | 关键词、用户/Agent | 渐进Skill |
| Cursor | glob、描述、手动 | Rules与Mode |

这些机制会随版本变化，并非统一向量Router。企业需补充权限、版本、评测、审计和拒选。

相关知识点：**Claude Code、OpenHands、Cursor Rules、AGENTS.md、CLAUDE.md、渐进加载、glob、显式调用、MCP**。

---

#### 38、Claude Code设计方案（附加专题）
Claude Code类Agent应包含**交互、上下文、规划执行、受控工具、验证恢复和治理**，在大型仓库中完成可验证的最小修改。

1. 入口解析目标、目录、Git状态和项目规则，建立TaskID与权限会话；需求不清先澄清，高风险动作展示目标和Diff。
2. 构建Repo Map、Symbol/AST、BM25、Embedding与Call Graph，结合LSP、Git和测试渐进检索；按Commit更新，避免整库加载。
3. 采用Plan—Act—Observe—Verify，将任务拆为可验证Step，模型只选结构化工具；新证据触发重规划，并设置步骤、Token和重试预算。
4. 提供Read、Search、Edit、Shell、Git、Test和MCP，使用Schema、路径Allowlist、沙箱与Policy Engine；危险Shell、Push和发布需审批。
5. 使用Patch修改，执行编译、单测、静态、安全检查及影响分析；失败局部重试，状态与Artifact通过检查点持久化。

平台记录模型、Prompt、索引、Tool、Trace、Diff、测试和成本，支持恢复与回放。评估完成率、补丁正确率、定位Recall、安全和成功成本。

**相关知识点：** Repo Map、Plan-Act-Observe、Tool Schema、MCP、沙箱、最小Diff、Change Impact Analysis、检查点、可观测性。

---

#### 39、Claude Code、GitHub Copilot、Cursor等Coding Agent在代码定位策略上有哪些异同？
三者都采用**按需检索与渐进读取**；差异来自产品入口、索引、执行环境和平台耦合。实现会随版本变化，未公开算法不能视为事实。

| 产品 | 公开可见的定位侧重 | 典型上下文 |
|---|---|---|
| Claude Code | 终端工具循环 | 工作树、项目指令、命令结果 |
| GitHub Copilot | 语义索引与GitHub融合 | 仓库、Issue、PR、云环境 |
| Cursor | 编辑器内索引 | 文件、光标、选区 |

1. 共同流程是提取词法与语义线索，以路径、文本、Symbol或语义搜索召回，读取少量文件，再依据调用、错误和测试扩展。
2. Claude Code强调模型在Agent Loop中调用Glob、Grep、Read等本地工具；定位结果与Shell、Git和测试Observation进入下一轮。
3. Copilot官方文档强调仓库语义索引；GitHub表面还可利用Issue、PR与Code Search，云端Agent在隔离环境中探索和验证。
4. Cursor以IDE状态为先验，光标、打开文件、选区和编辑历史缩小候选，再结合代码库索引；定位与编辑交互紧密。
5. 应在同一仓库、任务和权限下测Recall@K、MRR、跨文件完成率、无关上下文率、Token、P95及索引新鲜度。

**相关知识点：** 渐进检索、Agent Loop、语义索引、IDE上下文、Repository Context、Code Search、Recall@K、索引新鲜度。

---

#### 40、Claude Code如何快速理解几十万行代码的大型项目？
Claude Code通过**代理式探索、按需读取、持久指令和运行反馈**形成任务相关理解，不会一次装入整个仓库；未公开部分不应推断为固定索引架构。

1. 会话加载适用的CLAUDE.md及记忆，获得构建命令、目录约定、架构边界和规范；项目应把稳定规则写成可执行说明。
2. 面对任务先查看目录、配置、README、入口和Git状态，再使用Glob、Grep等工具定位文件与Symbol；只读取相关区间，并沿Import、调用、类型和测试关系扩展，而不是顺序遍历全部源码。
3. 通过Shell运行构建、测试、静态分析和Git查询，将错误栈、失败用例及历史Diff作为高信息密度证据；读取—假设—验证循环持续修正模型对项目的理解。
4. 上下文包含对话、文件内容、命令输出、CLAUDE.md、记忆、技能与工具定义。接近窗口上限时执行压缩，保留目标、关键发现、已修改内容和待办；项目根CLAUDE.md可在压缩后重新注入。
5. 大型仓库应提供模块化CLAUDE.md、路径规则、清晰构建入口和可运行测试；外部代码检索或MCP可补充专用索引，但属于工程扩展，不能与产品默认内部实现混为一谈。

快速理解的衡量标准不是“读过多少文件”，而是以较少读取获得足够证据，并能通过测试证明修改正确。

**相关知识点：** 代理式探索、按需读取、CLAUDE.md、Glob/Grep、调用关系、工具反馈、上下文压缩、MCP、证据驱动验证。

---

#### 41、Claude Code的上下文是如何动态组装的？
Claude Code上下文是**稳定指令、会话状态、按需证据和压缩摘要**的动态组合，随目录、文件、工具结果和剩余窗口变化。

1. 稳定层包含系统指令、当前权限与工具描述，以及按作用域加载的CLAUDE.md、规则和必要记忆。根目录规则提供项目共识，进入子目录并读取文件时再引入更具体的局部规则。
2. 会话层保存目标、对话、计划、决定、修改和待办。工具调用及结果进入上下文，使后续推理能引用文件、退出码和测试反馈。
3. 证据层由Agent按任务主动获取：先用目录、搜索和Symbol定位，再读取相关代码区间、配置、文档、Git Diff与测试。大输出应过滤、分页或摘要，避免低价值日志挤占窗口。
4. 工具与扩展也消耗上下文；MCP工具定义可按需发现，专用技能仅在任务需要时加载。组装时应优先保留约束、接口契约、失败证据和正在编辑的代码。
5. 窗口接近上限时自动或手动Compact，把早期交互压缩为任务状态摘要；压缩须保留目标、关键路径、验证结果、未完成事项和风险。根CLAUDE.md可重新注入，纯会话指令若未进入摘要则可能丢失。

工程上应通过`/context`观察占用，把长期规则放入CLAUDE.md，把大日志落盘后按需读取，并用Commit与路径标识证据版本。

**相关知识点：** 上下文分层、作用域规则、工具结果、按需读取、Token预算、MCP工具发现、上下文压缩、状态摘要、证据版本。

---

#### 42、CLAUDE.md与普通System Prompt有什么区别？
CLAUDE.md是**按目录加载的项目持久指令**；System Prompt是运行时最高层行为与安全指令，两者的权威级别和维护主体不同。

| 维度 | CLAUDE.md | System Prompt |
|---|---|---|
| 所有者 | 用户、团队或仓库 | 产品与运行平台 |
| 作用域 | 用户级、项目级、目录级 | 当前Agent运行时 |
| 内容 | 构建命令、规范、架构约束 | 身份、能力边界、安全规则 |
| 可见与版本化 | Markdown可审阅，可随仓库提交 | 通常不可完整查看，随产品配置 |
| 优先级 | 服从更高层指令 | 高于项目与用户内容 |

1. CLAUDE.md存放稳定且可执行的项目事实，如测试命令、禁改目录、风格和模块边界；不应堆放临时任务、大段文档或密钥。
2. 根文件定义全局规则，子目录文件补充局部约束；冲突会降低遵循度，应写明适用路径并保持简短。
3. System Prompt负责不能由仓库任意覆盖的边界，例如工具协议和安全策略。CLAUDE.md即使写入“忽略权限”，也不能越过平台规则。
4. 对话Prompt服务当前会话；跨会话约束应进入CLAUDE.md，固定生命周期检查应使用Hook，而非仅依赖语言提醒。

因此，CLAUDE.md是项目治理入口，不是System Prompt的替代品；敏感控制仍需权限、沙箱和Hook形成硬约束。

**相关知识点：** 指令层级、CLAUDE.md、System Prompt、目录作用域、配置即代码、Hooks、权限控制、持久上下文。

---

#### 43、长任务超过上下文窗口后如何处理？
长任务应采用**状态外置、阶段检查点、语义压缩、按需恢复和可验证交接**，把上下文窗口视为工作缓存，而非唯一记忆。

1. 先把任务拆成有验收条件的阶段，在持久状态中保存目标、约束、计划、完成项、待办、关键决定、证据路径、Git Commit、Diff和测试结果；每个工具动作关联步骤ID并保证幂等。
2. 接近窗口阈值时执行压缩，摘要必须保留当前目标、架构判断、失败尝试、尚未解决风险、修改文件与下一动作；丢弃重复讨论、完整日志和已被新证据推翻的假设。
3. 大文件、日志、检索结果和中间产物写入工作区或对象存储，摘要只保留路径、hash、生成时间与关键片段；恢复时按需重新读取，避免把全部材料再次注入。
4. 稳定项目规则写入CLAUDE.md或等价规则文件，任务状态写入Checkpoint，二者分离。Claude Code可自动或手动Compact；根级CLAUDE.md会重新注入，但会话中的临时约束应主动写入摘要。
5. 恢复后先校验仓库HEAD、工作树、依赖版本和外部资源是否变化，再重放未完成节点；若证据过期则重新检索。压缩前后运行小型一致性检查，确认目标、已改文件和验收命令未丢失。

还需设置最大轮次与成本预算；无法完成时输出可继续执行的交接包，而不是生成未经验证的结果。

**相关知识点：** 上下文窗口、Checkpoint、状态外置、语义压缩、幂等恢复、内容寻址、Git快照、任务交接、预算控制。

---

#### 44、如何设计代码仓库的增量索引机制？
增量索引以**Git快照为边界、内容hash为复用依据、依赖图为传播路径**，保证查询不读到半成品且可重建。

1. 基线Manifest记录repo、Commit、path、blob hash、language、Parser与Embedding版本、Symbol及索引段；Webhook获取增删改和重命名。
2. 规范化Diff：重命名复用blob结果；修改文件重解析AST和Symbol，仅为变化块计算Embedding；删除写墓碑，相同hash复用制品。
3. 按Import、调用、继承和构建依赖计算影响闭包。签名变化重算引用边，函数体变化仅更新本块和有限邻接。
4. 更新写入影子版本，经Schema校验、数量对账和抽样检索后原子切换；失败保留旧快照，查询始终绑定版本。
5. 事件以repo+Commit幂等，维护Watermark、重试和死信队列；定期对账Git树与Manifest，合并小段并清理过期墓碑。

监控延迟、积压、解析失败、复用率和闭包大小；Parser或Embedding升级建立新版本并灰度切换，不能混写。

**相关知识点：** Git Diff、内容寻址、Manifest、AST增量解析、依赖影响域、墓碑、影子索引、原子切换、Watermark、索引对账。

---

#### 45、如何结合关键词检索、向量检索和AST检索？
三类检索应形成**词法精确召回、语义扩展召回、结构约束验证**的混合链路；查询类型决定权重，由统一候选Schema融合。

| 方式 | 优势 | 局限 | 适合查询 |
|---|---|---|---|
| 关键词/BM25 | 标识符、错误码精确且低成本 | 同义表达召回弱 | Symbol、路径、日志 |
| 向量检索 | 理解意图、注释与相似实现 | 可能语义近但结构无关 | 功能描述、相似代码 |
| AST检索 | 识别定义、调用和语法模式 | 依赖语言Parser | 重构、引用、结构规则 |

1. 按Symbol与语法边界切块，保存Token、Embedding、AST节点类型、定义引用边、路径、Commit和ACL，使候选跨通道对齐。
2. 路由提取标识符、语言、结构谓词和意图。类名或错误码提高BM25权重；业务描述扩大向量召回；调用者、继承或特定语法启用AST。
3. 各通道并行取Top-K，以RRF统一尺度，再按Symbol命中、语义分数、AST约束、图距离、新鲜度和路径重排；硬性结构条件用于过滤。
4. 对Top-N补充定义、引用和测试，去重后按Token预算组装；通道超时可降级，仍保留来源和分数。

评测除Recall@K、MRR和NDCG外，应做单通道消融，并按查询类型观察融合增益；若向量召回提高但结构错误增加，应加强AST过滤与难负样本。

**相关知识点：** BM25、向量检索、AST检索、查询路由、统一候选Schema、RRF、结构过滤、依赖图、混合检索消融。

---

#### 46、Claude Code如何定位跨文件调用关系？
Claude Code定位跨文件关系依赖**搜索、语义线索、构建与运行反馈的迭代探索**；公开文档未声明默认维护完整Call Graph，不能把图索引视为既定机制。

1. 从错误栈、目标Symbol、接口名或入口文件出发，使用Grep、Glob和文件读取查找定义、引用、Import、导出与注册点；精确标识符优先于宽泛语义搜索。
2. 沿静态线索扩展：调用表达式连接被调用定义，接口连接实现类，依赖注入连接绑定配置，路由连接处理器，事件Topic连接生产者与消费者；每条关系记录路径、行号和证据来源。
3. 对动态语言、反射、代码生成和配置驱动关系，读取构建产物、框架配置、注册表及生成脚本，并运行测试、类型检查或应用Trace验证。仅凭名称相似不得判定真实调用。
4. 先读取签名和相关片段，证据不足再展开完整函数、调用者及邻近测试；维护已读文件与Symbol集合，避免重复扫描，并以当前Git Commit约束所有证据。
5. 修改后反向搜索全部引用，执行受影响测试和静态检查，确认接口两端同步更新。大型仓库可通过LSP、代码搜索或MCP接入专用Symbol/Call Graph服务，提高确定性和速度。

最终产物应区分“静态确定”“运行验证”“推测候选”三种边类型，防止把不完整调用链当作事实。

**相关知识点：** 跨文件检索、定义引用、Call Graph、依赖注入、反射、运行时Trace、LSP、证据置信度、影响分析。

---

#### 47、Agent如何判断应该读取哪些文件？
Agent依据**任务相关性、依赖距离、证据缺口、风险与Token成本**选择文件，采用由窄到宽的主动检索。

1. 解析目标行为、实体、错误、语言、模块和验收条件；先读项目规则、目录树、构建配置、入口及Git状态，确定Commit和范围。
2. 候选按Symbol、路径、错误栈、语义相似度、调用距离、近期Diff共变和测试关联评分；生成文件、缓存和二进制降权。
3. 首轮只读候选文件的签名、命中区间和邻近上下文。若缺少定义、调用者、接口实现、配置绑定或测试证据，再沿AST、LSP或依赖图扩展一至两跳；动态关系通过运行日志或Trace验证。
4. 记录file+Commit+range+hash及事实，同一范围不重复读；大文件按Symbol或行区间分页，日志先过滤。
5. 以证据覆盖率和边际信息增益作为停止条件：已能解释现象、确定最小修改面并列出验证命令时停止；连续两轮没有新增高价值证据则调整查询或请求澄清。

高风险修改应额外读取调用方、兼容契约、安全配置和回归测试；只读问答则控制扩展深度。离线评估可使用Context Recall、Precision、重复读取率和任务完成率校准阈值。

**相关知识点：** 候选排序、主动检索、依赖距离、信息增益、证据覆盖率、范围读取、读取去重、停止条件、Context Precision。

---

#### 48、Agent如何避免反复读取相同代码？
避免重复读取需要**版本化读取账本、内容缓存、事实摘要和差量补读**；自然语言提醒不能保证跨轮次一致性。

1. Read Record记录repo、Commit、path、range、blob hash、工具参数和摘要；查询前规范化判重，同版本同区间引用已有Artifact。
2. 文件缓存保存元数据与Symbol，区间缓存保存片段，语义缓存保存事实和接口。摘要携带路径与行号，需要精确语法时回源。
3. 合并重叠区间，如已读1—200行后请求150—260行，只补读201—260行；大文件按AST节点切分，避免全量失效。
4. 编辑后比较新旧blob hash和Diff，仅失效变化块及依赖摘要；未变化区间继续复用。切换分支、Commit、生成代码版本或权限版本时必须重新校验，不能误用陈旧缓存。
5. Planner维护Evidence Map；只命中已读内容且无新关系的候选降权。连续重复调用由循环检测器阻断并改写查询。

监控重复字节率、重复Token率、缓存命中率和陈旧命中率。压缩时保留账本索引与关键事实，详细内容外置。

**相关知识点：** Read Record、内容寻址、区间缓存、Artifact引用、差量读取、Evidence Map、缓存失效、循环检测、上下文外置。

---

#### 49、Claude Code的工具调用协议如何设计？
工具协议应是**强类型请求、结构化结果、权限前置、可取消执行与审计**的契约；模型提出意图，宿主负责校验和执行。

1. Tool Registry声明名称、版本、JSON Schema、读写等级、幂等性、超时、资源上限和权限，并明确失败语义。
2. 请求包含session、call、step、tool、arguments、cwd、Commit、权限和deadline。宿主校验Schema、路径、策略、ACL及预算，高风险动作请求确认。
3. 沙箱执行支持超时、取消、限流和进程树清理；幂等工具可按idempotency_key重试，非幂等写操作不得自动重放。
4. 结果返回status、exit_code、输出摘要、Artifact、Diff、耗时、错误类别和retryable。大输出落盘，模型接收关键片段与游标。
5. 审计日志关联输入hash、策略、审批、环境和结果；敏感字段脱敏。Pre/Post Hook可阻断危险调用或触发测试与告警。

MCP可接入外部工具，但不替代权限、沙箱与事务控制；破坏性Schema变更使用新版本灰度发布。

**相关知识点：** Tool Registry、JSON Schema、Call ID、幂等键、权限前置、沙箱、取消传播、结构化错误、Artifact、审计日志、MCP。

---

#### 50、Shell命令如何进行安全校验？
Shell安全校验采用**结构化解析、策略判定、最小权限沙箱、执行约束和审计**，不能仅依赖字符串黑名单。

1. 模型尽量提交argv、cwd、环境变量和重定向的结构化请求；必须接收命令串时，使用对应Shell语法解析器生成AST，识别管道、子命令、重定向、变量展开、通配符和编码绕过，禁止把未可信输入再次拼接解释。
2. 路径先规范化并解析符号链接，校验读写目标位于允许工作区；命令、参数、域名和文件按deny→ask→allow策略匹配。递归删除、提权、磁盘格式化、凭证访问、外传和持久化操作默认拒绝或强制确认。
3. 在非Root容器或OS沙箱中执行，设置只读根文件系统、可写目录白名单、网络域名白名单、进程/CPU/内存/磁盘配额及Secret最小注入；权限校验与沙箱必须同时存在。
4. 执行前展示展开后的命令、cwd、影响文件和风险等级；写操作绑定当前Git状态并建立可恢复快照。运行时设置超时、输出限额、取消传播及进程树回收，阻止后台逃逸。
5. 记录原始请求、规范化AST、策略命中、审批、环境hash、退出码和文件Diff，敏感值脱敏；执行后检查越界修改、异常网络连接和新建可执行文件。

安全规则需用绕过语料持续测试，并对误拦截率与漏拦截率分层评估；高风险类别应选择失败关闭。

**相关知识点：** Shell AST、命令注入、路径规范化、符号链接、deny-ask-allow、沙箱、最小权限、资源配额、审计、失败关闭。

---

#### 51、如何防止Agent执行危险命令？
防止危险命令必须贯彻**模型不拥有最终执行权、默认最小权限、高风险显式确认、系统级隔离和全程可追溯**，任何单一Prompt或黑名单都不足以构成安全边界。

1. 工具层按风险分级：只读查询可自动执行，工作区内可逆编辑按策略授权，删除、提权、外网发送、凭证读取、生产变更和不可逆操作默认拒绝。规则采用deny优先，并由企业托管策略锁定。
2. 对命令进行Shell AST解析和参数级校验，规范化路径、符号链接、重定向、管道及变量展开；识别`rm`别名、脚本间接调用、编码、子Shell等绕过方式。高风险判断不交给同一模型自我批准。
3. 命令在非Root沙箱运行，限制文件系统、网络、系统调用、进程、CPU、内存和磁盘；密钥以短期、最小范围凭证按需注入，默认不进入模型上下文或子进程环境。
4. 需要确认时展示完整展开命令、工作目录、预计影响、数据去向和恢复方案，批准绑定参数hash与有效期，命令变化后重新确认。批量授权不得覆盖敏感类别。
5. 执行器设置超时、取消和输出限制，写入前建立Git快照或事务；Hook在执行前阻断，在执行后检测越界Diff、异常网络与持久化行为。审计记录请求、策略、审批、结果和操作者。

评测包含正常、边界及对抗绕过集，持续度量危险调用拦截率、误拦率、越权率和可恢复率。

**相关知识点：** 最小权限、风险分级、deny优先、Shell AST、人机确认、沙箱、短期凭证、Hook、可恢复执行、安全评测。

---

#### 52、如何防止Prompt Injection通过代码或文档攻击Agent？
代码、注释、文档和检索结果都应视为**不可信数据而非指令**。即使模型受影响，系统仍须阻止越权读取、执行或外传。

1. 建立指令层级与数据边界：系统和用户授权才可改变目标；仓库内容以带来源、路径、Commit和信任标签的引用块注入，并明确其中命令不得自动执行。解析器保留代码与说明的类型信息。
2. 检索阶段扫描“忽略规则”“读取密钥”“上传内容”等可疑模式，降低信任或隔离展示，但不能仅依赖分类器；外部网页、第三方依赖和新提交按更低信任级处理。
3. 工具调用必须经过独立策略引擎，校验身份、ACL、路径、网络域名、命令风险和数据敏感度。读取文档不能隐式获得Shell、Secret或外网写权限，敏感动作要求参数级确认。
4. 在沙箱中限制文件、网络和进程，Secret默认不进入上下文；输出前运行DLP和数据流检查，阻断源码、密钥或个人信息流向未授权目标。MCP服务器也按独立主体授权。
5. 审查计划是否服务用户目标、证据是否来自不可信指令、是否出现提权或异常域名。命中风险时停止并说明来源。

持续使用间接注入、编码混淆、图片文字和多跳工具链红队集评测，监控攻击成功率、越权率、误拦率与敏感数据暴露率。

**相关知识点：** 间接Prompt Injection、信任边界、来源标记、策略引擎、最小权限、沙箱、DLP、数据流控制、MCP安全、红队评测。

---

#### 53、如何避免Agent泄漏密钥和环境变量？
核心原则是**密钥不进入模型上下文、按任务最小化授权、执行时短期注入、输出链路持续脱敏**；Prompt中的保密要求不能替代系统控制。

1. 密钥存入Vault/KMS，不写入仓库、配置文档、日志或长期环境变量。工具凭任务身份申请短时、单用途凭证，限定资源、操作、网络目标和TTL，结束后立即吊销。
2. 默认拒绝读取`.env`、凭证目录、云元数据和进程环境；文件搜索与RAG索引阶段排除敏感路径。确需使用时由宿主直接传给目标进程或代理服务，模型只获得引用句柄和成功状态。
3. 为子进程构造干净环境白名单，避免继承宿主全部变量；沙箱限制文件、网络和调试接口，防止通过`env`、`/proc`、崩溃转储或DNS外带。
4. 在工具输入、标准输出、日志、Trace、模型消息和最终响应执行Secret Scanner与DLP。使用精确指纹、格式规则和熵检测组合，命中后遮蔽、阻断并轮换；脱敏应发生在持久化和模型可见之前。
5. 外部HTTP、MCP与通知工具实施域名及字段级策略，敏感数据流向需显式批准。审计记录谁在何时以何种范围使用密钥，但不记录密钥值。

通过蜜罐密钥、间接注入和编码外带场景做持续红队，监控凭证暴露率、越权访问、脱敏漏检、短期凭证时长及轮换时延。

**相关知识点：** Vault、KMS、短期凭证、最小授权、环境白名单、Secret Scanner、DLP、数据流策略、蜜罐密钥、凭证轮换。

---

#### 54、Claude Code的权限确认机制如何设计？
权限确认基于**动作风险、参数范围和授权生命周期**，采用deny→ask→allow策略；确认只授权具体动作。

1. 工具声明只读、写入、网络、凭证、生产或破坏性等级。策略合并企业、用户、项目和会话规则，高层deny不可被覆盖。
2. 请求经规范化后匹配工具、命令、路径、域名、资源和数据类型。普通读取可免确认；工作区编辑可按会话授权；提权、删除、外发、生产变更和Secret访问每次确认或直接拒绝。
3. 界面展示展开命令、cwd、目标、预计副作用、数据范围和恢复方式；令牌绑定call_id、参数hash、身份、TTL与次数，参数变化即失效。
4. “本次允许”“本会话允许”和“持久规则”分开；持久授权应写入可审阅配置并支持撤销。宽泛通配符、高风险跨项目授权和批量静默批准应受企业策略禁止。
5. PreToolUse Hook可进一步阻断或强制询问，但不能绕过deny。获批动作仍在沙箱执行，并接受路径、网络和资源限制；结果、审批人、规则来源和Diff写入审计。

非交互场景只允许预声明的低风险能力，遇到ask动作暂停并生成审批包；以越权率、确认疲劳和误拦率调整策略。

**相关知识点：** deny-ask-allow、风险分级、参数绑定授权、审批TTL、托管策略、PreToolUse Hook、确认疲劳、非交互审批、审计。

---

#### 55、沙箱应该使用容器、虚拟机还是操作系统权限隔离？
选择取决于**威胁等级、启动时延、租户边界与成本**。通常以OS权限为基础、容器承载常规任务，高风险任务升级至微虚拟机。

| 方案 | 隔离强度 | 启动与密度 | 适用场景 |
|---|---|---|---|
| OS权限/沙箱 | 中，依赖内核机制 | 最快、密度最高 | 本地开发、可信代码 |
| 容器 | 中高，共享宿主内核 | 秒级或更快、密度高 | CI、一般企业任务 |
| VM/微VM | 高，独立内核 | 较慢、成本较高 | 不可信代码、强租户隔离 |

1. OS层使用非Root、ACL、namespace、seccomp、MAC或受限令牌，限制文件、系统调用、进程与网络。
2. 容器提供可复现镜像、只读根文件系统、临时工作盘和资源配额，但共享内核意味着内核漏洞可能突破边界，不能把“容器化”等同于绝对安全。
3. VM或微VM提供独立内核，适合陌生仓库、第三方脚本和高价值数据，但需镜像池、快照预热和强制销毁。
4. 建立风险路由：只读工具可用进程隔离，工作区构建进入容器，含网络、未知二进制或跨租户数据进入微VM；生产权限工具与代码执行环境进一步分离。

无论方案如何，都要最小化挂载和Secret、限制出口域名、设置CPU/内存/磁盘/时长、清理进程树，并记录镜像摘要与策略版本。选择依据应通过逃逸测试、P95启动时间、成本和任务成功率共同验证。

**相关知识点：** 容器、虚拟机、微VM、Namespace、seccomp、MAC、非Root、风险路由、网络隔离、资源配额。

---

#### 56、MCP在Claude Code中承担什么作用？
MCP是**标准化连接外部工具、数据源与业务系统**的扩展层，使Claude Code无需为每个系统编写专有协议；它不是安全边界。

1. MCP Server以Schema暴露Tools与Resources，Client负责连接、发现和调用，可接入Issue、数据库、文档、监控和部署平台。
2. 工具描述和Schema支持结构化调用，结果带来源返回；工具可按需发现和延迟加载，避免长期占用上下文。
3. 配置可按用户、项目或企业管理，传输可用本地进程或远程连接；身份、Secret和网络策略由运行环境管理。
4. MCP只解决“如何发现和调用”的互操作问题。是否允许调用、能访问哪些资源、是否需要确认，仍由Claude Code权限规则、Hook、沙箱以及MCP Server自身ACL共同决定。
5. 服务端返回结构化错误、幂等语义和来源；客户端配置超时、熔断、并发上限与降级。返回内容视为不可信数据。

MCP是客户端与能力提供方的协议，Tool Calling是模型提出调用的机制；二者可组合但不互相替代。

**相关知识点：** MCP Client/Server、Tools、Resources、Schema、延迟加载、Tool Calling、ACL、Hook、间接注入、熔断降级。

---

#### 57、MCP Server异常时如何熔断和降级？
MCP异常治理按**故障隔离、快速失败、有界重试、能力级熔断和可解释降级**设计，避免外部服务拖垮Agent循环。

1. 连接、工具发现和每次调用分别设置超时、并发上限与输出上限；统一错误分类为超时、限流、认证、参数、服务端、协议和数据质量错误，并标记retryable。
2. 只对网络抖动、限流和部分5xx进行指数退避加随机抖动，限制次数和总时长；写操作必须具备idempotency_key及服务端去重，否则不自动重试。
3. 熔断器按server+tool+tenant维护滑动窗口，综合失败率、慢调用比例和最小样本量进入Open；冷却后Half-Open放少量探测，成功再恢复。认证失败或协议不兼容直接打开并告警。
4. 降级按能力预先定义：检索服务异常回退本地索引或缓存快照，监控服务异常只读已有Artifact，写入型业务工具异常则保存待执行计划并暂停，不能伪造成功。缓存须携带版本、TTL和陈旧标识。
5. Planner接收结构化降级状态，重新评估任务能否满足验收条件；关键证据缺失时明确停止，非关键能力缺失则缩小范围继续。熔断状态应跨Agent共享，防止请求风暴。

监控调用成功率、P95/P99、熔断次数、半开恢复率、重试放大系数和降级完成率；通过故障注入验证超时传播、取消、幂等及恢复流程。

**相关知识点：** 熔断器、Half-Open、指数退避、随机抖动、幂等键、错误分类、缓存降级、请求风暴、故障注入。

---

#### 58、Claude Code如何实现最小范围代码修改？
最小修改依赖**先定位契约与影响域、再生成局部补丁、最后用Diff和测试约束范围**；目标是满足验收条件所需的最小语义变化，而非追求最少字符。

1. 修改前确认用户目标、禁止范围、当前Git状态和基线测试；通过搜索、定义引用、调用链及邻近测试确定根因，列出必须改、可能受影响和明确不改的文件。
2. 以Symbol或代码区间读取上下文，保留现有架构、命名、格式和错误处理；优先修改现有扩展点，避免无关重构、依赖升级、全局格式化及“顺便修复”。
3. 编辑工具提交带前后文锚点的Patch，并校验旧内容hash，防止并发变化时误覆盖。新增接口时同步修改最少必要调用方和测试；生成文件应修改源模板后再重新生成。
4. 每次编辑立即审查`git diff --stat`与逐行Diff，检查修改文件数、删除量、换行符、格式噪声、意外权限位及敏感内容。超出计划范围则撤销该局部补丁并重新定位。
5. 按影响域执行格式化、静态检查、目标测试和必要回归；失败时基于证据修补，不通过扩大重写掩盖问题。最终说明变更理由、文件、验证结果和剩余风险。

可设置文件数、变更行数和目录的软预算，超过阈值触发重新规划或确认；预算用于暴露风险，不能迫使跨层功能被错误压缩成不完整补丁。

**相关知识点：** 最小语义变更、影响域、Patch锚点、乐观并发控制、Git Diff、变更预算、回归测试、生成代码。

---

#### 59、如何防止模型整文件重写导致代码丢失？
工具层应强制**局部Patch、版本前置条件、Diff预算和可恢复写入**；整文件写入属于高风险能力，默认限制。

1. 编辑接口优先接受search/replace、AST节点变换或Unified Diff，要求提供唯一上下文锚点；写入前校验path、blob hash或mtime，文件已变化时拒绝并重新读取。
2. 整文件Write与局部Edit权限分离。仅新文件、小文件或生成物允许Write；覆盖现有文件展示原因、大小、删除比例和预览。
3. 在临时文件或内存应用补丁，完成语法、编码、换行符和Patch命中数校验后原子替换；保留Git基线、备份或事务日志。工具失败不得留下半写文件。
4. 写后比较Diff、文件hash、Symbol数量和关键区段。删除比例、文件数、格式噪声或公共API变化超阈值时阻断；生成代码应修改源模板。
5. 运行格式化、解析、类型检查和目标测试，并检查未跟踪文件及权限位。多Agent场景为文件加租约或使用独立Worktree，合并时按Patch审查，避免最后写入者覆盖他人。

阈值按任务配置，重构可放宽但须加强回归；自动恢复只撤销本次补丁，不得重置用户已有修改。

**相关知识点：** 局部Patch、乐观锁、原子写入、Diff Budget、Git基线、事务日志、AST Edit、Worktree、并发冲突。

---

#### 60、代码修改后如何自动验证正确性？
自动验证应构建**从变更结构、静态语义、目标行为到系统回归的分层证据链**；测试通过只说明已检查范围未失败，不能单独证明整体正确。

1. 先验证Patch可应用、文件可解析、格式与生成规则一致，并审查Diff是否仅包含计划内文件、是否意外删除代码、改变权限位或混入Secret。
2. 根据语言运行编译、类型检查、Lint和静态安全扫描；公共接口变化还要执行API/ABI兼容检查、Schema验证及依赖引用分析。
3. 由影响分析选择最接近变更的单元测试、契约测试和集成测试，优先快速反馈；随后按风险扩大至模块回归。新增行为必须有能在旧代码失败、在新代码通过的测试，防止无效断言。
4. 涉及数据库、消息、并发、性能或UI时，在隔离环境执行迁移回滚、契约、竞态、基准或端到端验证；外部依赖使用可信Test Double，并保留少量真实集成验证。
5. 将每项验收标准映射到测试或可观察证据，汇总命令、退出码、覆盖范围、失败原因和未验证项。失败分类为代码、测试、环境或基础设施，仅可恢复错误允许有界重试。

CI中采用风险分级门禁：低风险补丁可快速合并，高风险要求完整回归、人工Review和灰度。上线后监控错误率、延迟和业务指标，以Canary及自动回滚补足离线验证盲区。

**相关知识点：** Diff审查、编译与静态分析、影响分析、测试金字塔、契约测试、变更有效性、风险门禁、Canary、自动回滚。

---

#### 61、测试失败后Agent如何进行反思和重试？
有效反思是**基于失败证据更新假设并选择新动作**，不是重复生成同类补丁。重试必须有分类、预算、差异和停止条件。

1. 保存测试命令、退出码、失败用例、堆栈、环境、当前Diff与基线结果；先确认失败是否由本次变更引入，区分代码缺陷、测试预期错误、环境缺失、依赖波动和Flaky。
2. 将日志压缩为结构化Failure Record：现象、首个根因帧、相关Symbol、可复现性、错误类别、可恢复性和证据置信度。避免被后续级联错误误导。
3. 比较“预期行为—实际行为—补丁意图”，提出可证伪的新假设；定向读取失败路径、调用方和测试夹具。每轮明确与上一轮不同的新证据或策略，没有差异则不得重试。
4. 生成最小修复后先运行单个失败测试，再执行受影响测试和必要回归。环境类错误可按退避策略有限重试；代码断言失败不应原样重跑，除非已修改代码或测试数据。
5. 状态机记录attempt_id、假设、动作、结果和成本。相同签名连续出现、补丁来回震荡、超过轮次/Token/时间预算或需要改变需求时停止，恢复至最后稳定Checkpoint并报告阻塞证据。

不得为通过测试而删除断言、跳过用例、扩大Mock或修改无关生产逻辑。最终评估首次修复率、平均重试数、无效重试率、回归通过率和人工接管率。

**相关知识点：** Failure Record、错误分类、可证伪假设、有界重试、Flaky Test、Checkpoint、震荡检测、失败签名、人工接管。

---

#### 62、Agent如何区分可恢复错误与不可恢复错误？
标准是错误能否在**不提权、不改变目标且保持状态一致**的前提下，通过有限动作消除；应由结构化策略判断。

| 类型 | 典型示例 | 处理 |
|---|---|---|
| 可恢复 | 临时超时、限流、锁冲突、可补依赖、测试Flaky | 退避、刷新、补偿或换路径 |
| 不可恢复 | 明确拒权、非法需求、数据损坏、预算耗尽、破坏性前置失败 | 停止、回滚、请求人工 |

1. 工具返回错误码、retryable、side_effect、state_unknown和retry_after，Agent结合状态、退出码和领域规则分类。
2. 重试须具备新条件，如等待退避、刷新Token、释放锁、修正参数或切换副本。代码未变化时，编译错误原样重跑无价值。
3. 写操作超时且状态未知时，以幂等键查询或补偿，禁止盲目重放。权限不足只有用户授权后才可转为可恢复。
4. 分类器输出置信度和证据；低置信度、高风险、副作用未知或跨越安全边界时按不可恢复处理。每类设置最大次数、总时长和成本预算。
5. 不可恢复时取消下游任务、回收进程、恢复Checkpoint，保留Diff与诊断包，说明失败原因和所需外部动作。

通过故障回放与注入校准，监控无效重试率、重复副作用、恢复成功率和平均恢复时间。

**相关知识点：** 错误分类、retryable、幂等键、状态未知、补偿事务、退避重试、Checkpoint、故障注入、MTTR。

---

#### 63、如何防止Agent陷入无限循环？
防循环需要**显式状态机、硬预算、进展度量、重复检测和外部终止器**；模型自述“继续尝试”不能成为继续执行的充分条件。

1. 将任务表示为有限状态与步骤DAG，每步定义输入、成功条件、失败分支、最大尝试次数和允许工具；禁止无状态的自由循环。
2. 设置不可由模型修改的总轮次、Token、时间、费用、工具调用和写操作预算，并为子任务分配子预算；任一硬上限触发取消、进程回收和Checkpoint。
3. 为每轮计算状态指纹，包含计划节点、查询、工具与参数、错误签名、关键文件hash和测试结果。相同指纹重复、A↔B状态震荡或同一Diff反复应用时立即阻断。
4. 定义进展函数：新证据、失败用例减少、验收项完成或风险下降才算进展。连续N轮边际增益低于阈值时必须改写计划、降级或请求人工，不能只换措辞。
5. 重试策略按错误类别有界执行，写操作依赖幂等键；测试失败必须产生新假设或代码变化。Watchdog独立于Agent维护心跳、租约和取消信号，防止工具子进程持续运行。

终止后输出目标、已完成项、最后稳定状态、重复模式、失败证据及下一步，而非宣称成功。评测应统计平均轮次、无效调用率、震荡率、预算超限率和终止后的可恢复率。

**相关知识点：** 有限状态机、步骤DAG、硬预算、状态指纹、震荡检测、进展函数、Watchdog、幂等重试、Checkpoint。

---

#### 64、Agent的任务终止条件如何设计？
任务终止区分**成功、部分完成、失败、取消和阻塞**，由可验证条件触发；停止执行与宣告成功是不同决策。

1. 将需求转换为Acceptance Criteria，包括产物、范围、测试、质量阈值和禁止副作用；每项绑定机器检查、工具证据或人工确认。
2. 成功需同时满足：计划必需节点完成，Diff位于范围内，目标测试与静态检查通过，无未处理高风险告警，产物可定位且工作树状态已说明。工具成功不等于业务目标完成。
3. 部分完成用于独立子目标已交付但剩余项受阻；失败用于确定性错误无法在授权和预算内修复；阻塞表示需要用户选择、权限或外部系统；取消则立即传播到工具和子Agent。
4. 达到最大轮次、Token、费用、截止时间、无进展或重复状态阈值即停止。写操作状态未知时先执行幂等查询或补偿。
5. 终止器应独立于执行模型，读取结构化状态和Evidence。结束时持久化Commit/Checkpoint、Diff、验证命令及结果、未完成项、风险和恢复入口，并释放锁、租约、进程与短期凭证。

规则按风险分级：只读问答看证据充分度，代码修改要求测试，生产动作还需审批与观测窗口。评估误成功率、超时率和恢复率。

**相关知识点：** Acceptance Criteria、终态机、成功证据、部分完成、取消传播、硬预算、独立终止器、资源回收、误成功率。

---

#### 65、Claude Code如何支持任务中断和恢复？
关键是**取消运行与持久化状态解耦**：停止副作用，保存Checkpoint，恢复时验证外部状态是否与快照一致。

1. 会话、计划节点和调用使用稳定ID；状态保存目标、约束、DAG、完成节点、Evidence、Diff、Git HEAD、测试、预算和待办。
2. 中断时传播Cancellation Token，停止模型流、MCP调用和子进程树；写操作等待安全点或补偿，记录成功、失败或未知。
3. 在步骤完成、写入前后、测试结束及压缩前原子落盘，Artifact按hash外置；短期凭证和锁释放后重新申请。
4. 恢复先校验身份、权限、HEAD、工作树hash、锁文件及外部版本。未变化则继续；发生漂移则重检索或处理冲突。
5. 工具调用以幂等键去重，状态未知的写操作先查询服务端；已完成节点只有在输入hash一致时复用。恢复后展示先前修改、剩余计划和风险，让用户能够调整范围。

Checkpoint应加密、设TTL并隔离租户；通过强杀、断网、重启和Git漂移演练，衡量恢复率、重复副作用率与恢复时间。

**相关知识点：** Cancellation Token、Checkpoint、计划DAG、内容寻址、幂等恢复、状态漂移、补偿事务、进程回收、恢复演练。

---

#### 66、如何持久化Agent的执行状态？
执行状态采用**事件日志记录事实、快照加速恢复、Artifact外置、版本约束一致性**，不能只保存自然语言摘要。

1. Task、Plan Node、Tool Call、Evidence、Artifact和Approval使用稳定ID；状态包含目标、节点、依赖、预算、Commit、工作树hash和验收结果。
2. 状态变化写追加式Event Log，如TaskCreated、ToolFinished、PatchApplied；事件含seq、actor、输入hash、幂等键和Schema版本。
3. 定期生成Snapshot，保存DAG、完成项、待办和关键事实。代码、日志与Diff存入对象存储，以URI、hash、ACL和TTL引用。
4. 用事务或Outbox保证状态与消息一致，以乐观锁防止覆盖。写操作先记Intent再记Result，崩溃后通过幂等查询恢复。
5. 状态按租户加密隔离，Secret只存引用；恢复时验证Schema、权限、Artifact hash及外部版本，漂移则重新规划。

关系库承载元数据，事件流承载调度，对象存储承载Artifact；监控快照延迟、重放耗时、不一致率和恢复率。

**相关知识点：** Event Sourcing、Snapshot、Artifact Store、Outbox、乐观锁、幂等键、状态未知、Schema版本、租户隔离。

---

#### 67、如何设计主Agent与子Agent的协作机制？
主子Agent采用**主Agent统一目标与集成、子Agent承担独立任务、结构化交付证据**，避免共享无限增长的对话。

1. 主Agent将目标拆为DAG，仅委派输入完备、产物明确且可独立验证的节点；契约包含目标、范围、上下文、权限、预算和验收标准。
2. 子Agent获得最小上下文与独立session，不继承全部历史、Secret或写权限；输出状态、证据、Artifact、Patch、验证、风险和未决问题。
3. 主Agent维护唯一状态和Decision Log，负责调度、取消、冲突及最终决策；子Agent不得自行扩大范围或委派高风险权限。
4. 并行任务优先使用只读研究或独立Worktree/文件所有权。合并时校验基线Commit、Patch冲突、公共接口和测试；同一文件的写入由租约或主Agent串行化。
5. 失败以结构化错误返回，可恢复任务重试或换Agent；心跳、超时和最大递归深度防止孤儿任务，取消向下游传播。

评估完成率、冲突率、重复率、上下文成本、返工率和集成时间；强耦合小任务通常由单Agent完成更有效。

**相关知识点：** 任务DAG、委派契约、Result Envelope、最小上下文、Decision Log、Worktree、文件租约、取消传播、递归深度。

---

#### 68、子Agent的上下文和工具权限如何隔离？
隔离原则是**按任务提供必要信息、按身份授予最小能力、由环境阻断越界**。子Agent不自动继承主Agent权限。

1. Context Package仅含目标、范围、规则、Evidence、Commit和验收条件；Secret、无关对话、其他租户及高敏Artifact不传递。
2. 子Agent使用独立session、身份和短期凭证，令牌限定tool、path、repo、domain、action、TTL和次数；主Agent不能越权转授。
3. 使用独立Worktree、容器或微VM，限制挂载、网络、进程、资源和环境变量；共享Artifact经ACL句柄访问，写入以Patch返回。
4. Tool Gateway每次校验身份、范围和参数。高风险动作请求确认，审批令牌绑定参数，禁止跨子任务复用。
5. 日志、记忆、缓存和检索带tenant/task标签；返回前执行DLP。结束后撤销凭证、销毁沙箱并释放锁。

共享发现由主Agent审查后写入Evidence Store。通过跨任务访问、路径逃逸、注入和凭证转授测试验证隔离。

**相关知识点：** Context Package、最小权限、能力令牌、Worktree、微VM、Tool Gateway、ACL、DLP、凭证撤销、租户隔离。

---

#### 69、多Agent并发修改同一文件时如何解决冲突？
应在**调度阶段减少共享写入，执行阶段隔离工作树，合并阶段进行语义验证**；禁止对源码采用最后写入者获胜。

1. 主Agent根据Symbol、文件和依赖图划分Ownership，尽量让并行任务修改不同模块；共享接口先由一个任务确定契约，其他任务基于版本化接口开发。
2. 每个Agent在独立Git Worktree或分支工作，补丁记录base_commit、path、blob hash和意图；同一文件可采用短期写租约或由主Agent串行分配，避免物理覆盖。
3. 合并前Rebase到统一基线。无重叠Patch可三方合并；重叠区段、重命名、公共签名和配置进入冲突队列，读取双方意图和测试后处理。
4. 文本无冲突不代表语义无冲突，因此合并后重建AST、检查重复Symbol、接口兼容、调用关系和配置覆盖，并执行双方目标测试、受影响测试和静态分析。
5. 冲突解决记录采用或舍弃的变更及理由，不能让合并Agent扩大需求。无法同时满足验收条件时暂停并交由主Agent重新规划或请求用户决定。

乐观锁用于低冲突任务，悲观锁适合热点配置；按冲突率、等待、返工率和回归失败率选择。回滚不得覆盖用户未提交修改。

**相关知识点：** Git Worktree、文件Ownership、写租约、三方合并、乐观锁、语义冲突、AST验证、接口契约、冲突队列。

---

#### 70、Hooks与普通工具调用有什么区别？
Hook是**由生命周期事件触发的外部控制机制**，普通工具调用由模型主动选择；前者用于治理，后者用于任务执行。

| 维度 | Hook | 普通工具调用 |
|---|---|---|
| 触发者 | Session、Tool、Compact等事件 | 模型或Planner |
| 是否依赖模型选择 | 否，匹配事件即运行 | 是 |
| 主要用途 | 阻断、审计、格式化、注入上下文 | 搜索、编辑、测试、访问系统 |
| 决策位置 | 工具前后或会话生命周期 | Agent循环内部 |

1. PreToolUse在执行前检查路径、风险与策略，并允许、拒绝或要求确认；PostToolUse可格式化、扫描Diff或审计，均不依赖模型请求。
2. 工具调用具有名称、Schema、参数和返回值，模型按目标选择；仍须经过权限与沙箱。Hook不适合作通用推理工具。
3. Hook可运行命令、HTTP、MCP或确定性检查；应快速、幂等、限制输出并设置超时，防止阻塞任务。
4. Hook是纵深防御而非权限替代。托管Hook适合强制策略，项目Hook应审查来源并限制修改。

应把“每次都必须发生”的动作放入Hook，把“是否需要取决于任务”的动作交给工具调用；两者共同记录event_id和call_id，形成可追溯链路。

**相关知识点：** 生命周期事件、PreToolUse、PostToolUse、确定性触发、Tool Calling、权限控制、幂等Hook、托管策略、审计链路。

---

#### 71、如何利用Hooks实现安全审计和质量检查？
Hooks部署在**动作前阻断、动作后验证、任务结束汇总**三个位置，将安全与质量规则转为确定性控制。

1. PreToolUse规范化Shell AST与路径，检查禁用命令、敏感目录、域名、Secret、生产资源及Diff预算；高风险拒绝或确认。
2. PostToolUse运行格式化、解析、Lint、Secret Scan和SAST，检查Diff、删除比例、权限位及越界文件；失败则阻断提交。
3. PostToolUseFailure记录错误、重试和副作用，检测重复调用；Stop阶段确认验收测试、未提交Diff、告警和审计完整性。
4. 审计含event_id、call_id、actor、规则版本、输入hash、决策、审批和结果，写入防篡改存储；Secret预先脱敏。
5. 强制规则使用托管Hook，项目Hook需审查。Hook在低权限环境运行，设置超时、输出上限与失败策略；安全Hook失败应关闭执行。

规则先观察误报，再灰度阻断；监控覆盖率、拦截率、误报率、P95延迟和绕过事件，并用对抗样例回归。

**相关知识点：** PreToolUse、PostToolUse、SAST、Secret Scan、Diff Budget、防篡改审计、托管Hook、失败关闭、观察模式。

---

#### 72、Claude Code如何集成Git、IDE和CI/CD？
集成以**Git作为事实源、IDE提供上下文、CI/CD承担验证与发布门禁**，通过Commit、任务ID和Artifact追踪。

1. Git层读取HEAD、工作树和Diff，保留用户未提交变更；Agent在独立分支或Worktree生成Patch，禁止强推或改写历史。
2. IDE传递仓库、打开文件、选区和诊断，展示计划、Diff、确认及测试；LSP提供定义、引用和诊断，IDE不得绕过权限。
3. 本地运行格式化、类型检查和目标测试，再创建PR；PR包含摘要、影响域、验证命令、风险和AI来源标识。
4. CI从干净Commit重跑构建、测试、SAST、Secret和依赖扫描；结果经Check Run回传，Agent不得篡改门禁。
5. CD与代码执行身份分离，生产部署需要审批、短期凭证、Canary和回滚；高风险动作遵循组织策略。

事件共享repo、commit、pr、run和session；以签名Webhook、最小Token权限和审计防伪。评估PR通过率、CI通过率和回滚率。

**相关知识点：** Git Worktree、LSP、PR工作流、CI门禁、Check Run、Webhook、SAST、Canary、短期凭证、端到端追踪。

---

#### 73、如何设计Coding Agent的可观测性系统？
可观测性覆盖**任务、模型、检索、工具副作用、质量、成本和安全**，以统一Trace关联生命周期。

1. 为task、step、model、retrieval、tool、patch、test和approval分配ID；事件携带tenant、repo、commit、agent、model和规则版本。
2. Metrics统计完成率、首次补丁通过率、接管率、重试率、Recall@K、工具成功率、P95/P99、Token、费用和安全拦截，并分层切片。
3. Trace记录计划、查询与证据ID、工具参数hash、错误、Diff和测试；大日志与代码存为Artifact，不写入完整Prompt或Secret。
4. Log采用结构化Schema，实施脱敏、采样、租户隔离、加密、TTL和RBAC；高风险审计不采样并防篡改。
5. Dashboard为排队、模型错误、MCP熔断、失败风暴、成本异常和越权建立SLO告警；以Trace回放和失败聚类定位回归。

业务与系统指标关联，如成功任务单位成本；验证遥测不会泄密或显著增延迟，并用观测数据更新评测集。

**相关知识点：** OpenTelemetry、Trace/Span、SLO、结构化日志、Artifact、脱敏、失败聚类、单位成功成本、安全审计、评测闭环。

---

#### 74、如何评估Claude Code的任务完成率？
任务完成率是**在约束与预算内，满足全部必需验收且无禁止副作用的任务比例**，不能以模型自报或生成补丁替代。

1. 固定Commit、环境、输入、范围和Acceptance Criteria，分为必需项、质量项和禁止项；必需项失败即非完全完成。
2. Judge运行Patch应用、编译、目标/隐藏测试、静态分析、Diff和安全检查；开放任务再由盲审按Rubric评估。
3. 报告Strict Success、Partial Completion、Valid Patch、首次通过率和无回归率。公式为成功数/有效任务数，环境故障单列。
4. 按任务类型、难度、语言、仓库规模、单/跨文件、模型版本和工具配置切片；同一任务多次运行，报告均值、置信区间及pass@1，避免随机性掩盖退化。
5. 线上以采纳、PR合并、回滚、缺陷逃逸和耗时验证离线分数；任务改写或扩大范围时建立新版本。

评测集需含真实任务和失败长尾，防止训练污染；所有Judge保存证据和版本。核心指标还应与Token、费用和时延结合，形成**单位成本成功率**。

**相关知识点：** Acceptance Criteria、Strict Success Rate、Partial Completion、隐藏测试、盲审、pass@1、置信区间、任务切片、单位成功成本。

---

#### 75、如何构建Coding Agent的离线评测集？
离线评测集应以**真实任务、可复现仓库快照、可执行验收和防污染治理**为核心，覆盖代码定位、修改、验证及安全的完整闭环。

1. 从已合并PR、Issue、缺陷单和维护任务抽取样本，回退到修改前Commit；保留需求、环境、依赖和原始测试，将开发者补丁只作为参考，不作为唯一正确答案。
2. 按问答、缺陷修复、功能、重构、测试生成、依赖升级和安全任务分层，覆盖多语言、仓库规模、跨文件、动态调用及长尾失败；控制难度与线上分布，并保留挑战集。
3. 每题定义Acceptance Criteria：Patch可应用、编译、公开/隐藏测试、静态检查、Diff范围、性能和禁止副作用。无法完全自动判定的设计质量使用双人盲审Rubric与仲裁。
4. 用容器或VM固定工具链、依赖、种子、时间和外部服务替身，断网运行并校验基线；Flaky样本隔离治理。任务、仓库与测试均版本化，产出可重放Trace。
5. 数据按仓库和时间切分，近重复检测防止同一修复泄漏到训练与测试；定期检查模型污染。线上失败经脱敏、去重和审核后回流，旧集保持冻结用于纵向比较。

报告完成率、定位Recall、Valid Patch、首次通过率、回归率、Token、时延及安全违规，并按切片给出置信区间；Judge和环境版本变化需重新建立基线。

**相关知识点：** 仓库快照、真实PR任务、隐藏测试、盲审Rubric、可复现环境、Flaky治理、时间切分、数据污染、挑战集。

---

#### 76、如何评估代码修改是否存在非预期影响？
通过**变更面审计、依赖分析、分层回归、行为差分和上线观测**识别影响；目标测试只覆盖已知预期。

1. 比较文件、行、Symbol、API、Schema、配置、依赖、权限位和生成物，标记计划外修改、格式噪声、删除及Secret；每项Diff关联需求。
2. 构建定义引用、调用、继承、数据表、Topic、路由和构建依赖图，计算影响模块、测试和下游；以Trace补充动态关系。
3. 执行编译、静态分析、目标测试和模块回归；接口、数据库、并发、性能变化增加契约、回滚、竞态和基准测试。
4. 对新旧版本做Differential Testing，比较返回值、异常、写入、事件、延迟和资源量；随机行为固定种子并设容差。
5. 高风险变更使用Shadow、Canary和Feature Flag，观察错误率、P95、业务KPI及下游告警，超过阈值自动回滚；观测窗口应覆盖周期性任务。

输出影响清单、验证覆盖和未验证风险，由Owner审查；指标包括回归缺陷率、回滚率、影响Recall和测试Precision。

**相关知识点：** Change Impact Analysis、依赖图、公共API、Differential Testing、契约测试、Shadow、Canary、Feature Flag、变更失败率。

---

#### 77、如何降低Claude Code的Token成本？
降本应优化**每个成功任务的总Token**，而非单次请求最短；过度裁剪会增加重试和返工。

1. 项目规则简短明确，以目录级CLAUDE.md或按需技能承载局部知识；MCP工具按需发现，不让全部Schema常驻。
2. 先用目录、Grep、Symbol和摘要定位，再按区间读取函数、调用方和测试；维护Read Record与事实摘要，避免重复。
3. 工具输出过滤、分页和结构化，日志保留首个根因、关键栈及Artifact；大文件落盘，窗口压缩时保留目标、Diff和待办。
4. 采用任务感知模型路由：分类、查询改写、摘要和格式检查使用小模型，复杂规划、跨文件推理及高风险Review使用强模型；相同稳定前缀使用Prompt Cache，批量Embedding合并处理。
5. 设置Token预算、检索深度、重试和无进展终止条件；测试失败必须带来新证据，以完成率和质量作为成本护栏。

观测Input/Output/Cache Token、工具返回Token、压缩次数、任务总成本及成功任务单位成本，并按任务类型做A/B。任何优化都须保证Context Recall、首次补丁通过率和安全指标不下降。

**相关知识点：** Token Budget、渐进式上下文、Read Record、Prompt Cache、模型路由、输出过滤、上下文压缩、单位成功成本。

---

#### 78、如何进行大小模型分工和模型路由？
大小模型依据**任务难度、风险、上下文、工具需求和失败代价**动态路由，以质量约束下的单位成功成本最小为目标。

1. 小模型承担分类、抽取、查询改写、摘要、格式校验和简单问答；大模型承担需求澄清、复杂规划、跨文件推理、安全Review及恢复。
2. 路由特征包括任务类型、代码规模、依赖跳数、所需上下文、历史成功率、用户SLA、数据敏感度和剩余预算；风险规则优先于成本，例如生产与安全任务直接使用高能力模型并增加验证。
3. 小模型先输出置信度、证据覆盖和结构化结果；低置信、冲突或验证失败时升级。大模型接收压缩目标、证据和失败记录。
4. Validator独立检查Schema、引用、测试和安全；不能由路由模型同时自评。对写操作可使用大模型生成、小模型检查格式，但关键语义Review仍需强模型或人工。
5. 路由以规则起步，再用Bandit灰度优化；设置健康熔断、供应商降级、最大升级次数和预算，防止震荡。

评估完成率、误路由率、升级率、P95、Token、费用和单位成功成本，并按任务风险检查质量下限。模型版本变化时重新校准阈值，保留固定对照组。

**相关知识点：** Model Routing、级联推理、置信度校准、风险路由、Validator、Bandit、模型熔断、单位成功成本、误路由率。

---

#### 79、企业内部部署Claude Code需要考虑哪些安全问题？
企业部署围绕**身份权限、数据边界、工具执行、供应链、审计合规和模型数据使用**建立纵深防御。

1. 接入SSO/MFA和短期身份，按用户、仓库、路径与工具实施RBAC/ABAC；企业deny高于项目配置，支持即时撤权。
2. 明确源码、Prompt、遥测和响应的数据流、区域、保留、训练使用与删除；敏感仓库使用合规端点，传输存储加密，缓存隔离。
3. Secret存入Vault，默认拒绝`.env`和凭证目录读取；工具使用最小范围短期令牌。DLP与Secret Scanner覆盖输入、工具输出、日志、Trace及外发。
4. Shell与MCP在非Root沙箱运行，限制挂载、系统调用、网络域名和资源；危险命令、生产写入、外部发送及新MCP Server需策略审批。仓库文档视为不可信，防范间接Prompt Injection。
5. 插件、Hook、MCP、镜像和依赖实行白名单、签名、版本锁定、SBOM与扫描；审计关联身份、工具、审批、Diff和结果。

上线前完成威胁建模、红队和事件响应演练；监控越权、泄密、危险调用和供应链告警。高敏任务使用微VM与双重审批。

**相关知识点：** SSO、RBAC/ABAC、数据驻留、DLP、Vault、沙箱、间接注入、SBOM、供应链安全、防篡改审计、威胁建模。

---

#### 80、OpenCode与Claude Code的架构差异是什么？
两者取向不同：**OpenCode强调开源、模型可替换和可扩展；Claude Code强调Claude原生体验与完整能力体系**。功能应以同版本实测为准。

| 维度 | OpenCode | Claude Code |
|---|---|---|
| 模型层 | 多Provider配置，便于替换与自托管端点 | 以Claude模型及Anthropic平台能力为中心 |
| 可审计性 | 核心代码开源，可修改运行逻辑 | 产品内部实现未完整公开 |
| 扩展 | Agents、Tools、Plugins、MCP、LSP | CLAUDE.md、Skills、Hooks、MCP、Subagents、Plugins |
| 权限 | 工具/命令级allow、ask、deny | 分层权限、托管策略、Hooks与沙箱 |

1. OpenCode适合控制模型供应商与源代码的团队，可配置Agent、权限和外部能力；团队需承担模型适配、升级兼容与安全加固。
2. Claude Code整合项目指令、记忆、工具、Hooks、权限、子Agent及官方模型，产品一致性较强；定制依赖公开配置与SDK。
3. 两者均不能被假定默认拥有完美大仓索引或绝对安全沙箱；检索、IAM、审计、数据驻留和隔离需逐项验证。

选型应在相同仓库、任务集、模型和策略下，对比完成率、延迟、单位成功成本、治理与锁定风险。

**相关知识点：** 开源Coding Agent、模型Provider、MCP、LSP、Hooks、Subagents、权限策略、可扩展性、供应商锁定、单位成功成本。

---

## 原理深入专题

#### 81、Claude模型本身是无状态的，Claude Code为什么能表现为持续工作的Agent？
模型API的单次请求本身不保存上一轮状态。持续性来自Claude Code这个**Agent Harness**：它保存Session Transcript和工作目录状态，在下一轮请求中重新组装系统提示、项目上下文、历史消息、工具定义及最新工具结果。

因此需要区分三类状态：

1. 模型上下文状态：当前请求中可见的Token，受窗口和Compaction限制。
2. Harness状态：Session ID、Transcript、权限模式、任务和工具调用记录。
3. 外部环境状态：文件、Git、进程、数据库和远程服务中的真实副作用。

恢复Transcript只能恢复对话状态，不能自动回滚或重建外部环境。面试中不应把连续行为解释成“模型内部一直记得”，也不能把Claude Code公开可观察的Harness机制扩写成未公开的模型内部实现。

**相关知识点：** Stateless Model、Agent Harness、Session Transcript、Context Reconstruction、External State、状态分层。

---

#### 82、Claude Code的一次Agent Turn在消息层面经历哪些阶段？
一个Turn通常从当前上下文发给模型开始。模型返回包含文本和一个或多个`tool_use`请求的Assistant Message；Runtime校验工具名和参数，执行权限、Hook与工具逻辑，再把带对应调用ID的`tool_result`回灌给模型。模型基于新证据继续请求工具或返回不含工具调用的最终回复。

独立的读取或搜索可以并行执行，存在数据依赖的动作必须串行。例如先读取文件再生成精确Edit，不能把读和写作为无依赖调用并行。工具失败也应作为结构化Observation回灌，而不是由宿主静默吞掉。

CLI显示的一条回复、一次API请求、一个Turn和一个完整任务不是同一概念。模型停止调用工具只代表Loop到达协议终点，不等于测试通过或业务目标完成。

**相关知识点：** Assistant Message、tool_use、tool_result、Tool Call ID、Turn、Parallel Tool Use、Protocol Termination。

---

#### 83、Claude Code的Agent Loop为什么能够根据执行结果动态调整，而不是一次性执行固定计划？
模型每次只基于**当前可见状态**决定下一步，工具结果会成为下一轮的新Observation。测试失败、文件内容与预期不同或权限被拒绝都会改变后续决策，因此计划本质上是滚动更新的，而不是启动时生成后机械执行。

这个机制类似`observe → decide → act → observe`的闭环：模型负责概率性判断，工具提供外部证据，Harness负责消息传递和执行控制。Plan或Todo可以稳定目标和顺序，但不会把模型转换为确定性工作流引擎。

可靠性来自外部闭环：每次修改后运行Validator，失败必须产生新证据或改变策略；连续重复相同调用时由最大Turn、预算、无进展检测或人工中断停止。

**相关知识点：** Closed-loop Control、Rolling Plan、Observation、Replanning、Validator、No-progress Detection。

---

#### 84、工具Schema和工具描述为什么会影响Claude Code的推理与行为？
工具定义构成模型当前可选择的**动作空间**。名称、描述、参数Schema和示例告诉模型工具能做什么、何时使用以及怎样构造参数；含糊或重叠的描述会增加误选工具和参数错误。

Runtime仍需做确定性校验：验证JSON Schema、权限和路径，执行工具并限制超时与输出大小。模型选择某个工具只是请求，不是授权；工具返回成功也不代表业务结果正确。

设计自定义MCP工具时应采用清晰动词、窄职责、强类型参数和结构化错误，并让读写能力可区分。工具集过大时使用Tool Search延迟加载Schema，降低上下文噪声。

**相关知识点：** Action Space、Tool Schema、Tool Description、Structured Error、Capability Boundary、Schema Validation。

---

#### 85、Claude Code的上下文窗口在长任务中如何演化？
上下文不会在每个Turn后重置。系统提示、项目上下文、对话、文件内容、工具输入输出会逐步累积；固定前缀通常可被Prompt Cache复用，但仍占模型可见窗口。

接近窗口上限时，Claude Code先清理较旧的工具输出，再在需要时把历史压缩成摘要。摘要保留的是信息的有损表示，早期临时指令、精确错误文本和细节可能丢失。项目根级`CLAUDE.md`和Auto Memory可从磁盘重新注入；按路径加载的规则和嵌套指令进入消息历史后可能被压缩，后续再次读取匹配文件时才重新加载。

因此长任务应把目标、验收、关键决定、已改文件和测试状态持久化到稳定Artifact；大输出过滤或落盘，阶段切换时主动Compact或Clear。

**相关知识点：** Context Accumulation、Tool Output Eviction、Lossy Compaction、Context Rehydration、Path-scoped Rules、Artifact。

---

#### 86、Claude Code的Prompt Cache原理是什么？哪些操作会造成Cache Miss？
每轮请求的大部分前缀相同：系统提示与工具定义在前，项目上下文居中，对话和新消息追加在后。Prompt Cache按**精确前缀匹配**复用服务端已处理内容，并不是按语义或文件分别缓存。

系统提示、工具集合或前部内容变化会使其后的缓存失效。切换模型使用另一套Cache；MCP Server连接状态或工具列表变化会改变系统层；Compaction用摘要替换对话历史，使Conversation层重新建立缓存；升级Claude Code也可能改变系统提示和内置工具。

缓存降低重复输入的费用和延迟，但不扩大上下文窗口，也不保证恢复后的首轮便宜。应在任务开始时稳定模型和MCP集合，在自然阶段边界Compact，并用Usage数据观察Cache Read与Cache Creation。

**相关知识点：** Prompt Cache、Exact Prefix Match、Cache Invalidation、Cache Read、Cache Creation、Stable Prefix。

---

#### 87、CLAUDE.md和路径规则是如何进入模型上下文的？
项目根级`CLAUDE.md`、用户级指令和Auto Memory通常在Session启动时加载，形成每轮请求中的项目上下文。嵌套`CLAUDE.md`和带`paths`范围的Rules采用延迟机制：当Claude读取匹配路径的文件时，相应指令才进入消息历史。

这解释了两个现象：第一，局部规则不会无条件占用所有任务的上下文；第二，局部规则被Compaction摘要后不一定持续逐字存在，直到再次触发对应文件读取。必须跨整个Session保持的约束，应放在根级无路径范围的规则或由权限、Hook强制执行。

指令层级用于提供行为上下文，不是安全边界。敏感路径禁止、生产写入限制和命令审批仍要由Permission、Sandbox与服务端ACL执行。

**相关知识点：** Project Context、Instruction Loading、Lazy Rule Loading、Path Scope、Compaction Boundary、Policy Enforcement。

---

#### 88、Claude Code Skill的渐进式加载原理是什么？
Session启动时通常只把Skill的名称和描述暴露给模型，用于判断是否相关；模型或用户调用后，Skill正文才进入当前对话。这种**Progressive Disclosure**避免把每个工作流的完整说明常驻上下文。

Skill正文进入主Session上下文，适合复用步骤、模板和领域知识；Subagent则创建隔离上下文，适合会产生大量中间材料的独立任务。Skill不是可执行安全策略：它能指导模型调用工具，但不能保证指令必然执行。

描述应明确触发条件，正文把关键规则放在前部并控制体积。需要人工显式调用的Skill可关闭模型自动调用，避免大量描述干扰路由和占用上下文。

**相关知识点：** Skill Discovery、Progressive Disclosure、Description Routing、On-demand Context、Skill Invocation、Context Budget。

---

#### 89、MCP Tool Search为什么能减少上下文占用？它的代价是什么？
默认情况下，Claude Code只在启动上下文中保留MCP工具名称，把完整Schema延迟到需要时再通过Tool Search发现并加载。这样连接大量Server时，不必在每轮请求中携带全部工具定义。

代价是多一次发现决策，并依赖模型和Provider支持`tool_reference`能力。关闭Tool Search、使用不兼容模型或某些不转发相关Block的代理时，工具Schema可能回退为全部预加载。设置`alwaysLoad`的工具也会固定占用上下文，并可能使启动等待Server连接。

Tool Search只解决发现与Token问题，不解决可信性、权限和可用性。加载后的工具仍需Permission、Hook、Sandbox或后端ACL约束，MCP结果仍按不可信输入处理。

**相关知识点：** Deferred Tool Loading、Tool Search、tool_reference、Schema Cost、alwaysLoad、Provider Compatibility。

---

#### 90、Claude Code理解调用关系主要依赖模型推理，还是依赖LSP和索引？
两者结合，但职责不同。模型从已读取的代码、类型和命名中推断语义；Grep、Glob和Read提供文本证据；启用代码智能插件后，LSP Tool可提供定义、引用、诊断等结构化信息。

LSP不是模型内部记忆，也不保证覆盖反射、动态导入、宏、生成代码或运行时绑定。公开文档也没有承诺Claude Code默认为所有仓库维护完整Call Graph或向量索引。复杂项目应把静态关系、Git历史、构建反馈和运行Trace交叉验证。

正确流程是先用低成本搜索缩小范围，再通过LSP/AST确认符号关系，最后用编译和测试验证。没有代码智能时，Agent会更多依赖文本搜索和逐文件阅读，成本和误判率通常更高。

**相关知识点：** LSP Tool、Code Intelligence、Text Search、Static Analysis、Dynamic Dispatch、Evidence Triangulation。

---

#### 91、Claude Code的Bash工具如何处理Shell状态和后台任务？
Bash调用由Harness启动进程执行，命令的stdout、stderr和退出状态作为工具结果返回。不能假设不同Bash调用天然共享同一个交互式Shell状态；需要跨调用持久化的环境变量应通过启动环境、`CLAUDE_ENV_FILE`或SessionStart Hook明确注入。

长时间命令可以转为后台任务，Runtime返回Task ID，使Agent继续工作并在之后查询输出。后台进程属于外部环境状态，不会因为对话Compact、Rewind或模型停止调用工具而自动撤销。

工程上要为进程设置超时、日志上限、端口和清理策略，并区分“命令已启动”“进程仍健康”和“业务已就绪”。测试Server启动后应通过健康检查而非仅看零退出码判断成功。

**相关知识点：** Process Execution、stdout/stderr、Exit Status、CLAUDE_ENV_FILE、Background Task、Process Lifecycle。

---

#### 92、一次工具调用同时命中Hook、Deny、Ask和Allow时，权限决策如何理解？
权限决策遵循**拒绝优先和多层约束**。`PreToolUse`在权限提示前运行，可阻止、修改输入或提出决策；显式Deny仍不能被Hook的Allow结果绕过，Ask也仍可要求确认。阻断型Hook可在Allow规则存在时拒绝动作。

随后Permission规则根据工具、命令、路径或域名匹配Deny、Ask和Allow。Sandbox启用自动放行时，只是用OS隔离边界替代部分逐命令确认，显式Deny与关键路径保护仍然有效。MCP或远端服务还会执行自己的身份与资源授权。

因此最终可执行范围是Hook、Managed Settings、项目/用户权限、Sandbox和后端ACL的交集，而不是某一条Allow的并集。

**相关知识点：** Deny-first、PreToolUse、Permission Evaluation、Managed Settings、Policy Intersection、Backend ACL。

---

#### 93、Claude Code Sandbox的安全边界是如何形成的？为什么仍可能需要人工确认？
Sandbox在OS层限制Bash及其子进程的文件系统和网络访问；Permission层对所有工具的动作进行授权。两者合并后，命令即使受到Prompt Injection影响，也应被限制在允许挂载和域名内。

Sandbox不是所有能力的统一虚拟机：内置Read/Edit、WebFetch和MCP有各自权限路径，Bash之外的工具不能只靠Shell Sandbox保护。若平台依赖缺失，默认配置可能警告后继续以非Sandbox方式执行；高安全环境应启用不可用即失败。

某些不兼容命令可以请求在Sandbox外重试，这个Escape Hatch需要走常规权限流程，并可被组织关闭。生产任务还应使用短生命周期容器或VM、临时凭据和服务端最小权限。

**相关知识点：** OS Sandbox、Fail Open、Fail Closed、Escape Hatch、Filesystem Boundary、Network Boundary、Defense in Depth。

---

#### 94、Claude Code Hooks在Runtime中类似什么机制？其阻断语义如何实现？
Hooks可理解为Agent Runtime的**生命周期事件总线和策略扩展点**。Session、Prompt、Tool、Permission、Compaction、Subagent和Task等事件触发外部命令、HTTP端点或其他处理器，输入输出通过结构化JSON传递。

命令Hook退出码`0`表示正常并可解析JSON，退出码`2`在支持阻断的事件上表达拒绝；不同事件的阻断效果不同，例如`PreToolUse`可阻止尚未执行的工具，而`PostToolUse`只能反馈，因为副作用已经发生。多个匹配Hook可能并行执行后合并结果，拒绝应优先。

HTTP Hook的非2xx或超时通常是非阻断错误，不能仅靠返回500实现安全拒绝；需要在2xx JSON中返回对应Decision。安全Hook必须默认策略明确、输入严格解析、超时可控并有审计。

**相关知识点：** Lifecycle Event Bus、Hook JSON Protocol、Exit Code 2、Pre/Post Semantics、Decision Merge、Fail-open HTTP Hook。

---

#### 95、Session、Context、Checkpoint和Git分别保存哪一层状态？
四者解决不同问题：

| 机制 | 保存内容 | 主要用途 |
|---|---|---|
| Context | 当前模型请求可见信息 | 本轮推理 |
| Session Transcript | 消息、工具调用和元数据 | 恢复对话 |
| Checkpoint | Claude编辑工具改动前的文件状态 | 会话级撤销 |
| Git | 显式提交的仓库版本历史 | 长期协作与审计 |

Compaction改变Context表示但保留Session；Resume加载Transcript但不保证进程和远端资源仍在；Checkpoint不覆盖Bash或外部程序造成的全部文件变化；Git也不记录未提交的数据库或云端副作用。

可靠恢复必须同时记录代码Base SHA、工作区Diff、Session ID、外部操作幂等键和验证状态，并针对每层采用对应的回退方法。

**相关知识点：** State Plane、Context、Transcript、Checkpoint、Git、External Side Effect、Recovery Point。

---

#### 96、Claude Code Session Transcript的持久化原理是什么？
CLI会持续把Session事件写入本地JSONL Transcript，Session与项目目录关联。`continue`、`resume`和`fork`读取或分支这份历史，再结合当前工作目录、配置和凭据恢复运行。

Agent SDK的外部Session Store采用**本地先写、外部镜像**：Claude Code子进程先写本地文件，SDK再批量调用`append()`。镜像失败会产生错误事件但通常不中断Agent，失败批次也不保证自动重试，因此外部存储不是天然强一致日志。

Transcript可能包含源码片段、命令输出和用户输入，应加密、鉴权、设置保留期并脱敏。外部Store与文件Checkpoint存在兼容限制时，应以当前SDK文档和运行验证为准。

**相关知识点：** JSONL Transcript、Local-first Persistence、Dual Write、Best-effort Mirror、Session Fork、Retention Policy。

---

#### 97、Subagent为什么能节省主Session上下文？它实际继承了什么？
Subagent启动一个新的隔离上下文，不读取父Session的完整消息历史和已读文件。主Agent把任务、边界和必要证据压缩成Delegation Message；Subagent加载自己的系统提示、项目级上下文和被授权的工具，完成后只把最终摘要作为工具结果返回父Session。

节省来自“大量搜索和中间输出留在子上下文”，而不是免费执行。委派摘要缺少关键信息会导致重复探索，返回过长也会重新占满父上下文。Subagent通常不能再生成嵌套Subagent，需要由主Agent串联任务。

权限方面应显式收窄工具和MCP Server；父Session的安全边界不能通过子Agent扩大。高耦合、需要频繁共享上下文的修改留在主Session通常更合适。

**相关知识点：** Fresh Context、Delegation Message、Context Isolation、Summary Return、Tool Scoping、Nested Delegation。

---

#### 98、Agent Teams的协调原理与普通并行Tool Call有什么区别？
并行Tool Call发生在同一Agent Turn内，共享一个上下文，适合无依赖的读取和查询。Agent Teams则由多个独立Claude Code实例组成，每个Teammate有自己的上下文，通过共享任务列表和消息通道协调，Lead负责分配、跟踪和综合。

独立上下文提高并行探索能力，也引入状态一致性问题。共享任务状态并不等于共享完整推理证据；Teammate修改同一工作区时也没有自动获得Git隔离。官方建议按文件或模块划分所有权，需要隔离时使用独立Worktree和分支。

选择并行方式要看任务粒度、依赖和通信成本：毫秒级独立读取用并行工具，短期独立研究用Subagent，持续多角色协作用Agent Teams，多任务由人调度可用Agent View。

**相关知识点：** Parallel Tool Call、Independent Context、Shared Task List、Lead/Teammate、Message Passing、Worktree Isolation。

---

#### 99、Claude Code面对工具失败时，恢复机制的本质是什么？
工具失败会作为Observation进入下一轮，模型可根据错误类型选择重试、修改参数、换工具、降级或请求用户。Harness提供最大Turn、权限拒绝、取消和Session恢复等控制，但不会自动证明某个重试策略正确。

应先把失败分类：

1. 瞬时失败：限流、网络抖动，可指数退避并设置上限。
2. 输入或前置条件失败：修正参数、路径、依赖或环境。
3. 权限与策略失败：不能通过改写命令绕过，应请求授权或停止。
4. 确定性业务失败：保留证据、改变方案或升级人工。

连续调用相同工具、错误指纹不变且没有新证据就是无进展。此时应停止重试并输出当前状态、已验证事实和需要的外部决策。

**相关知识点：** Error Observation、Retry Taxonomy、Exponential Backoff、Policy Failure、Error Fingerprint、No-progress Loop。

---

#### 100、如何从原理层面调试一个“Claude Code没有按预期工作”的问题？
按**输入上下文—模型决策—权限控制—工具执行—环境副作用—验证结果**逐层定位，而不是只修改Prompt。

1. 用`/context`和`/memory`确认实际加载的CLAUDE.md、Rules、Skill与上下文占用，检查是否发生Compaction。
2. 查看Transcript和Debug日志，确认模型请求了什么工具、参数是什么、Tool Result是否完整以及调用ID是否匹配。
3. 检查Hook、Deny/Ask/Allow、Sandbox和MCP/服务端ACL，区分模型没请求、策略拒绝和执行失败。
4. 在相同Base SHA、配置、模型与依赖下单独重放命令，检查后台进程、环境变量和外部服务状态。
5. 用测试、Diff和Trace验证真实结果；记录Claude Code版本、模型、Provider和随机运行差异。

这种分层方法能把“模型能力问题”与上下文污染、工具契约、权限、环境漂移和验收缺失区分开。

**相关知识点：** Layered Debugging、Context Inspection、Transcript、Tool Trace、Policy Debugging、Environment Reproduction、Result Verification。

---

## 官方核验资料

- [Claude Code 文档索引](https://code.claude.com/docs/llms.txt)
- [Claude Code 工作原理](https://code.claude.com/docs/en/how-claude-code-works)
- [Agent Loop 原理](https://code.claude.com/docs/en/agent-sdk/agent-loop)
- [上下文窗口](https://code.claude.com/docs/en/context-window)
- [Prompt Cache](https://code.claude.com/docs/en/prompt-caching)
- [大型代码库](https://code.claude.com/docs/en/large-codebases)
- [项目记忆](https://code.claude.com/docs/en/memory)
- [工具参考](https://code.claude.com/docs/en/tools-reference)
- [权限](https://code.claude.com/docs/en/permissions)
- [Sandboxing](https://code.claude.com/docs/en/sandboxing)
- [Hooks](https://code.claude.com/docs/en/hooks)
- [MCP](https://code.claude.com/docs/en/mcp)
- [Subagents](https://code.claude.com/docs/en/sub-agents)
- [Agent Teams](https://code.claude.com/docs/en/agent-teams)
- [Checkpointing](https://code.claude.com/docs/en/checkpointing)
- [Session 管理](https://code.claude.com/docs/en/sessions)
- [外部 Session Storage](https://code.claude.com/docs/en/agent-sdk/session-storage)
- [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview)

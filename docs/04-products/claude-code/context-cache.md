# 上下文与 Prompt Cache

> 所属章节：[Claude Code](README.md)｜本文件共 **28** 题。

<a id="cc-003"></a>
### Claude Code 如何理解大型代码库，而不把整个仓库放进上下文？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

它采用**代理式探索和按需取证**：先读取项目规则与目录结构，再用Glob、Grep、Read、Git、代码智能和构建反馈定位相关符号，只展开当前任务需要的文件和范围。

大型仓库可使用根级与子目录`CLAUDE.md`、`.claude/rules/`、按包Skills、稀疏Worktree和明确的构建命令缩小搜索面。公开文档没有保证默认维护完整向量索引或Call Graph，因此面试中应把这类索引描述为可接入的增强方案，而非既定内部实现。

**验证指标：** 任务完成率、测试通过率、误修改率、P95 延迟和单任务 Token 成本。

**相关知识点：** Agentic Search、Progressive Context、Grep、Code Intelligence、Monorepo、Sparse Worktree。
<a id="cc-004"></a>
### Claude Code 的上下文由哪些部分组成？为什么会发生 Compaction？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

上下文通常包含系统提示、工具Schema、对话历史、`CLAUDE.md`与Rules、已加载Skill、文件片段和工具结果。随着Agent读取文件和运行命令，窗口逐渐被占用；接近上限时会压缩较早对话以继续任务。

Compaction保留摘要而非逐字历史，因此关键目标、约束、决定、失败原因和验证状态应写入稳定文件或清晰摘要。大型工具输出先过滤或落盘再引用。可用上下文检查功能确认实际加载内容，不能把磁盘Transcript、Auto Memory容量等同于模型窗口。

**相关知识点：** Context Window、Prompt Assembly、Compaction、Tool Output、Context Inspection、Artifact。
<a id="cc-005"></a>
### CLAUDE.md、`.claude/rules/` 和普通任务提示应如何分工？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

`CLAUDE.md`承载跨会话稳定的项目约定，`.claude/rules/`适合拆分主题或路径相关规则，任务提示描述本次目标和验收。

1. 根级规则写架构、构建、测试和仓库级禁令。
2. 子目录规则只描述对应模块，避免把所有细节常驻上下文。
3. 本地个人偏好放`CLAUDE.local.md`或用户级配置，不污染团队仓库。
4. 临时Bug信息和一次性步骤留在任务Prompt或Issue。

多个层级通常是叠加加载，不应依赖隐含“最深文件必然覆盖”来解决冲突；规则应无冲突或显式声明优先关系。

**相关知识点：** CLAUDE.md、Rules、Path Scope、Persistent Instructions、Local Override、指令冲突。
<a id="cc-006"></a>
### Claude Code 的 Auto Memory 与 CLAUDE.md 有什么区别？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

`CLAUDE.md`是团队或用户**主动维护的规范性指令**，Auto Memory是Claude在使用中积累的**经验性笔记**。前者应被Review并纳入版本管理，后者更适合个人环境、调试发现和重复偏好。

Auto Memory可能过时、误归纳或只适用于某台机器，不能用来保存密钥、业务权威事实或替代仓库文档。稳定且被验证的经验应提升为`CLAUDE.md`、Rule、Skill或正式文档；错误记忆要可查看、修正和删除。

**相关知识点：** Auto Memory、Explicit Memory、Team Policy、Provenance、Memory Promotion、知识治理。
<a id="cc-007"></a>
### Claude Code 中 CLAUDE.md、Skills、Subagents、Hooks、MCP 和 Plugins 如何选型？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

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

**验证指标：** 任务完成率、测试通过率、误修改率、P95 延迟和单任务 Token 成本。

**相关知识点：** Extension Surface、Progressive Disclosure、Deterministic Hook、MCP、Plugin Packaging。
<a id="cc-016"></a>
### Claude Code 如何通过 MCP 扩展工具？大工具集如何控制上下文成本？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

MCP Server向Claude Code暴露标准化Tool、Resource或Prompt，可按本地、项目或用户Scope配置。接入时要验证Transport、认证、Schema、超时和Server权限，并通过Managed MCP限制组织可连接的Server。

工具数量很大时，可使用Tool Search按需加载符合任务的工具定义，避免所有Schema常驻上下文。Tool Search提高发现效率但不授予权限；最终调用仍受Allow/Deny、Hook、Sandbox和目标服务ACL约束。MCP返回内容同样可能包含恶意指令。

**相关知识点：** MCP Server、Configuration Scope、Managed MCP、Tool Search、Deferred Loading、ACL。
<a id="cc-017"></a>
### Claude Code Subagent 适合解决什么问题？如何避免滥用？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

Subagent拥有独立上下文、工具集合、模型和专用指令，适合代码探索、安全Review、测试分析等**可独立交付且上下文噪声大的任务**。

主Agent应传递目标、范围、证据和输出契约，而非模糊地要求“看看”。只读探索Agent不应拥有Edit/Bash写权限；修改任务要避免多个Agent同时触碰同一文件。子Agent会增加Token、等待和汇总偏差，应按风险和可并行性选择，并由主Agent验证结果。

**相关知识点：** Context Isolation、Custom Subagent、Tool Allowlist、Delegation Contract、Result Verification、成本。
<a id="cc-023"></a>
### Claude Code 如何降低 Token 成本并保持质量？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

先减少无关上下文：精简`CLAUDE.md`、让Skill按需加载、用Grep定位后局部Read、过滤长日志、把稳定产物落盘。Prompt Caching可复用稳定前缀，但修改规则、切模型或频繁改变工具集合会降低命中。

按任务复杂度选择模型和Thinking预算，独立探索可交给较便宜Subagent，但高风险判断不应只为省钱降级。跟踪输入、输出、缓存读写、工具输出、子Agent和每个成功任务总成本；以质量约束下的单位成功成本优化，而非单次Token最少。

**相关知识点：** Prompt Caching、Context Hygiene、Model Routing、Thinking Budget、Cost per Success。
<a id="cc-036"></a>
### Claude Code、Cursor、OpenHands 的 Skill 分层有什么差异？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

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

**相关知识点：** CLAUDE.md、SKILL.md、Cursor Rules、AGENTS.md、Subagent、Hooks、MCP、渐进加载。
<a id="cc-037"></a>
### Claude Code、OpenHands、Cursor中的Skill路由是如何实现的？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

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

**相关知识点：** Claude Code、OpenHands、Cursor Rules、AGENTS.md、CLAUDE.md、渐进加载、glob、显式调用、MCP。
<a id="cc-040"></a>
### Claude Code如何快速理解几十万行代码的大型项目？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

Claude Code通过**代理式探索、按需读取、持久指令和运行反馈**形成任务相关理解，不会一次装入整个仓库；未公开部分不应推断为固定索引架构。

1. 会话加载适用的CLAUDE.md及记忆，获得构建命令、目录约定、架构边界和规范；项目应把稳定规则写成可执行说明。
2. 面对任务先查看目录、配置、README、入口和Git状态，再使用Glob、Grep等工具定位文件与Symbol；只读取相关区间，并沿Import、调用、类型和测试关系扩展，而不是顺序遍历全部源码。
3. 通过Shell运行构建、测试、静态分析和Git查询，将错误栈、失败用例及历史Diff作为高信息密度证据；读取—假设—验证循环持续修正模型对项目的理解。
4. 上下文包含对话、文件内容、命令输出、CLAUDE.md、记忆、技能与工具定义。接近窗口上限时执行压缩，保留目标、关键发现、已修改内容和待办；项目根CLAUDE.md可在压缩后重新注入。
5. 大型仓库应提供模块化CLAUDE.md、路径规则、清晰构建入口和可运行测试；外部代码检索或MCP可补充专用索引，但属于工程扩展，不能与产品默认内部实现混为一谈。

快速理解的衡量标准不是“读过多少文件”，而是以较少读取获得足够证据，并能通过测试证明修改正确。

**相关知识点：** 代理式探索、按需读取、CLAUDE.md、Glob/Grep、调用关系、工具反馈、上下文压缩、MCP、证据驱动验证。
<a id="cc-041"></a>
### Claude Code的上下文是如何动态组装的？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

Claude Code上下文是**稳定指令、会话状态、按需证据和压缩摘要**的动态组合，随目录、文件、工具结果和剩余窗口变化。

1. 稳定层包含系统指令、当前权限与工具描述，以及按作用域加载的CLAUDE.md、规则和必要记忆。根目录规则提供项目共识，进入子目录并读取文件时再引入更具体的局部规则。
2. 会话层保存目标、对话、计划、决定、修改和待办。工具调用及结果进入上下文，使后续推理能引用文件、退出码和测试反馈。
3. 证据层由Agent按任务主动获取：先用目录、搜索和Symbol定位，再读取相关代码区间、配置、文档、Git Diff与测试。大输出应过滤、分页或摘要，避免低价值日志挤占窗口。
4. 工具与扩展也消耗上下文；MCP工具定义可按需发现，专用技能仅在任务需要时加载。组装时应优先保留约束、接口契约、失败证据和正在编辑的代码。
5. 窗口接近上限时自动或手动Compact，把早期交互压缩为任务状态摘要；压缩须保留目标、关键路径、验证结果、未完成事项和风险。根CLAUDE.md可重新注入，纯会话指令若未进入摘要则可能丢失。

工程上应通过`/context`观察占用，把长期规则放入CLAUDE.md，把大日志落盘后按需读取，并用Commit与路径标识证据版本。

**相关知识点：** 上下文分层、作用域规则、工具结果、按需读取、Token预算、MCP工具发现、上下文压缩、状态摘要、证据版本。
<a id="cc-042"></a>
### CLAUDE.md与普通System Prompt有什么区别？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

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
<a id="cc-043"></a>
### 长任务超过上下文窗口后如何处理？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

长任务应采用**状态外置、阶段检查点、语义压缩、按需恢复和可验证交接**，把上下文窗口视为工作缓存，而非唯一记忆。

1. 先把任务拆成有验收条件的阶段，在持久状态中保存目标、约束、计划、完成项、待办、关键决定、证据路径、Git Commit、Diff和测试结果；每个工具动作关联步骤ID并保证幂等。
2. 接近窗口阈值时执行压缩，摘要必须保留当前目标、架构判断、失败尝试、尚未解决风险、修改文件与下一动作；丢弃重复讨论、完整日志和已被新证据推翻的假设。
3. 大文件、日志、检索结果和中间产物写入工作区或对象存储，摘要只保留路径、hash、生成时间与关键片段；恢复时按需重新读取，避免把全部材料再次注入。
4. 稳定项目规则写入CLAUDE.md或等价规则文件，任务状态写入Checkpoint，二者分离。Claude Code可自动或手动Compact；根级CLAUDE.md会重新注入，但会话中的临时约束应主动写入摘要。
5. 恢复后先校验仓库HEAD、工作树、依赖版本和外部资源是否变化，再重放未完成节点；若证据过期则重新检索。压缩前后运行小型一致性检查，确认目标、已改文件和验收命令未丢失。

还需设置最大轮次与成本预算；无法完成时输出可继续执行的交接包，而不是生成未经验证的结果。

**相关知识点：** 上下文窗口、Checkpoint、状态外置、语义压缩、幂等恢复、内容寻址、Git快照、任务交接、预算控制。
<a id="cc-047"></a>
### Agent如何判断应该读取哪些文件？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

Agent依据**任务相关性、依赖距离、证据缺口、风险与Token成本**选择文件，采用由窄到宽的主动检索。

1. 解析目标行为、实体、错误、语言、模块和验收条件；先读项目规则、目录树、构建配置、入口及Git状态，确定Commit和范围。
2. 候选按Symbol、路径、错误栈、语义相似度、调用距离、近期Diff共变和测试关联评分；生成文件、缓存和二进制降权。
3. 首轮只读候选文件的签名、命中区间和邻近上下文。若缺少定义、调用者、接口实现、配置绑定或测试证据，再沿AST、LSP或依赖图扩展一至两跳；动态关系通过运行日志或Trace验证。
4. 记录file+Commit+range+hash及事实，同一范围不重复读；大文件按Symbol或行区间分页，日志先过滤。
5. 以证据覆盖率和边际信息增益作为停止条件：已能解释现象、确定最小修改面并列出验证命令时停止；连续两轮没有新增高价值证据则调整查询或请求澄清。

高风险修改应额外读取调用方、兼容契约、安全配置和回归测试；只读问答则控制扩展深度。离线评估可使用Context Recall、Precision、重复读取率和任务完成率校准阈值。

**相关知识点：** 候选排序、主动检索、依赖距离、信息增益、证据覆盖率、范围读取、读取去重、停止条件、Context Precision。
<a id="cc-067"></a>
### 如何设计主Agent与子Agent的协作机制？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

主子Agent采用**主Agent统一目标与集成、子Agent承担独立任务、结构化交付证据**，避免共享无限增长的对话。

1. 主Agent将目标拆为DAG，仅委派输入完备、产物明确且可独立验证的节点；契约包含目标、范围、上下文、权限、预算和验收标准。
2. 子Agent获得最小上下文与独立session，不继承全部历史、Secret或写权限；输出状态、证据、Artifact、Patch、验证、风险和未决问题。
3. 主Agent维护唯一状态和Decision Log，负责调度、取消、冲突及最终决策；子Agent不得自行扩大范围或委派高风险权限。
4. 并行任务优先使用只读研究或独立Worktree/文件所有权。合并时校验基线Commit、Patch冲突、公共接口和测试；同一文件的写入由租约或主Agent串行化。
5. 失败以结构化错误返回，可恢复任务重试或换Agent；心跳、超时和最大递归深度防止孤儿任务，取消向下游传播。

评估完成率、冲突率、重复率、上下文成本、返工率和集成时间；强耦合小任务通常由单Agent完成更有效。

**相关知识点：** 任务DAG、委派契约、Result Envelope、最小上下文、Decision Log、Worktree、文件租约、取消传播、递归深度。
<a id="cc-068"></a>
### 子Agent的上下文和工具权限如何隔离？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

隔离原则是**按任务提供必要信息、按身份授予最小能力、由环境阻断越界**。子Agent不自动继承主Agent权限。

1. Context Package仅含目标、范围、规则、Evidence、Commit和验收条件；Secret、无关对话、其他租户及高敏Artifact不传递。
2. 子Agent使用独立session、身份和短期凭证，令牌限定tool、path、repo、domain、action、TTL和次数；主Agent不能越权转授。
3. 使用独立Worktree、容器或微VM，限制挂载、网络、进程、资源和环境变量；共享Artifact经ACL句柄访问，写入以Patch返回。
4. Tool Gateway每次校验身份、范围和参数。高风险动作请求确认，审批令牌绑定参数，禁止跨子任务复用。
5. 日志、记忆、缓存和检索带tenant/task标签；返回前执行DLP。结束后撤销凭证、销毁沙箱并释放锁。

共享发现由主Agent审查后写入Evidence Store。通过跨任务访问、路径逃逸、注入和凭证转授测试验证隔离。

**相关知识点：** Context Package、最小权限、能力令牌、Worktree、微VM、Tool Gateway、ACL、DLP、凭证撤销、租户隔离。
<a id="cc-077"></a>
### 如何降低Claude Code的Token成本？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

降本应优化**每个成功任务的总Token**，而非单次请求最短；过度裁剪会增加重试和返工。

1. 项目规则简短明确，以目录级CLAUDE.md或按需技能承载局部知识；MCP工具按需发现，不让全部Schema常驻。
2. 先用目录、Grep、Symbol和摘要定位，再按区间读取函数、调用方和测试；维护Read Record与事实摘要，避免重复。
3. 工具输出过滤、分页和结构化，日志保留首个根因、关键栈及Artifact；大文件落盘，窗口压缩时保留目标、Diff和待办。
4. 采用任务感知模型路由：分类、查询改写、摘要和格式检查使用小模型，复杂规划、跨文件推理及高风险Review使用强模型；相同稳定前缀使用Prompt Cache，批量Embedding合并处理。
5. 设置Token预算、检索深度、重试和无进展终止条件；测试失败必须带来新证据，以完成率和质量作为成本护栏。

观测Input/Output/Cache Token、工具返回Token、压缩次数、任务总成本及成功任务单位成本，并按任务类型做A/B。任何优化都须保证Context Recall、首次补丁通过率和安全指标不下降。

**相关知识点：** Token Budget、渐进式上下文、Read Record、Prompt Cache、模型路由、输出过滤、上下文压缩、单位成功成本。
<a id="cc-081"></a>
### Claude模型本身是无状态的，Claude Code为什么能表现为持续工作的Agent？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

模型API的单次请求本身不保存上一轮状态。持续性来自Claude Code这个**Agent Harness**：它保存Session Transcript和工作目录状态，在下一轮请求中重新组装系统提示、项目上下文、历史消息、工具定义及最新工具结果。

因此需要区分三类状态：

1. 模型上下文状态：当前请求中可见的Token，受窗口和Compaction限制。
2. Harness状态：Session ID、Transcript、权限模式、任务和工具调用记录。
3. 外部环境状态：文件、Git、进程、数据库和远程服务中的真实副作用。

恢复Transcript只能恢复对话状态，不能自动回滚或重建外部环境。面试中不应把连续行为解释成“模型内部一直记得”，也不能把Claude Code公开可观察的Harness机制扩写成未公开的模型内部实现。

**相关知识点：** Stateless Model、Agent Harness、Session Transcript、Context Reconstruction、External State、状态分层。
<a id="cc-085"></a>
### Claude Code的上下文窗口在长任务中如何演化？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

上下文不会在每个Turn后重置。系统提示、项目上下文、对话、文件内容、工具输入输出会逐步累积；固定前缀通常可被Prompt Cache复用，但仍占模型可见窗口。

接近窗口上限时，Claude Code先清理较旧的工具输出，再在需要时把历史压缩成摘要。摘要保留的是信息的有损表示，早期临时指令、精确错误文本和细节可能丢失。项目根级`CLAUDE.md`和Auto Memory可从磁盘重新注入；按路径加载的规则和嵌套指令进入消息历史后可能被压缩，后续再次读取匹配文件时才重新加载。

因此长任务应把目标、验收、关键决定、已改文件和测试状态持久化到稳定Artifact；大输出过滤或落盘，阶段切换时主动Compact或Clear。

**相关知识点：** Context Accumulation、Tool Output Eviction、Lossy Compaction、Context Rehydration、Path-scoped Rules、Artifact。
<a id="cc-086"></a>
### Claude Code的Prompt Cache原理是什么？哪些操作会造成Cache Miss？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

每轮请求的大部分前缀相同：系统提示与工具定义在前，项目上下文居中，对话和新消息追加在后。Prompt Cache按**精确前缀匹配**复用服务端已处理内容，并不是按语义或文件分别缓存。

系统提示、工具集合或前部内容变化会使其后的缓存失效。切换模型使用另一套Cache；MCP Server连接状态或工具列表变化会改变系统层；Compaction用摘要替换对话历史，使Conversation层重新建立缓存；升级Claude Code也可能改变系统提示和内置工具。

缓存降低重复输入的费用和延迟，但不扩大上下文窗口，也不保证恢复后的首轮便宜。应在任务开始时稳定模型和MCP集合，在自然阶段边界Compact，并用Usage数据观察Cache Read与Cache Creation。

**相关知识点：** Prompt Cache、Exact Prefix Match、Cache Invalidation、Cache Read、Cache Creation、Stable Prefix。
<a id="cc-087"></a>
### CLAUDE.md和路径规则是如何进入模型上下文的？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

项目根级`CLAUDE.md`、用户级指令和Auto Memory通常在Session启动时加载，形成每轮请求中的项目上下文。嵌套`CLAUDE.md`和带`paths`范围的Rules采用延迟机制：当Claude读取匹配路径的文件时，相应指令才进入消息历史。

这解释了两个现象：第一，局部规则不会无条件占用所有任务的上下文；第二，局部规则被Compaction摘要后不一定持续逐字存在，直到再次触发对应文件读取。必须跨整个Session保持的约束，应放在根级无路径范围的规则或由权限、Hook强制执行。

指令层级用于提供行为上下文，不是安全边界。敏感路径禁止、生产写入限制和命令审批仍要由Permission、Sandbox与服务端ACL执行。

**相关知识点：** Project Context、Instruction Loading、Lazy Rule Loading、Path Scope、Compaction Boundary、Policy Enforcement。
<a id="cc-088"></a>
### Claude Code Skill的渐进式加载原理是什么？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

Session启动时通常只把Skill的名称和描述暴露给模型，用于判断是否相关；模型或用户调用后，Skill正文才进入当前对话。这种**Progressive Disclosure**避免把每个工作流的完整说明常驻上下文。

Skill正文进入主Session上下文，适合复用步骤、模板和领域知识；Subagent则创建隔离上下文，适合会产生大量中间材料的独立任务。Skill不是可执行安全策略：它能指导模型调用工具，但不能保证指令必然执行。

描述应明确触发条件，正文把关键规则放在前部并控制体积。需要人工显式调用的Skill可关闭模型自动调用，避免大量描述干扰路由和占用上下文。

**验证指标：** 任务完成率、测试通过率、误修改率、P95 延迟和单任务 Token 成本。

**相关知识点：** Skill Discovery、Progressive Disclosure、Description Routing、On-demand Context、Skill Invocation、Context Budget。
<a id="cc-089"></a>
### MCP Tool Search为什么能减少上下文占用？它的代价是什么？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

默认情况下，Claude Code只在启动上下文中保留MCP工具名称，把完整Schema延迟到需要时再通过Tool Search发现并加载。这样连接大量Server时，不必在每轮请求中携带全部工具定义。

代价是多一次发现决策，并依赖模型和Provider支持`tool_reference`能力。关闭Tool Search、使用不兼容模型或某些不转发相关Block的代理时，工具Schema可能回退为全部预加载。设置`alwaysLoad`的工具也会固定占用上下文，并可能使启动等待Server连接。

Tool Search只解决发现与Token问题，不解决可信性、权限和可用性。加载后的工具仍需Permission、Hook、Sandbox或后端ACL约束，MCP结果仍按不可信输入处理。

**相关知识点：** Deferred Tool Loading、Tool Search、tool_reference、Schema Cost、alwaysLoad、Provider Compatibility。
<a id="cc-095"></a>
### Session、Context、Checkpoint和Git分别保存哪一层状态？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

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
<a id="cc-097"></a>
### Subagent为什么能节省主Session上下文？它实际继承了什么？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

Subagent启动一个新的隔离上下文，不读取父Session的完整消息历史和已读文件。主Agent把任务、边界和必要证据压缩成Delegation Message；Subagent加载自己的系统提示、项目级上下文和被授权的工具，完成后只把最终摘要作为工具结果返回父Session。

节省来自“大量搜索和中间输出留在子上下文”，而不是免费执行。委派摘要缺少关键信息会导致重复探索，返回过长也会重新占满父上下文。Subagent通常不能再生成嵌套Subagent，需要由主Agent串联任务。

权限方面应显式收窄工具和MCP Server；父Session的安全边界不能通过子Agent扩大。高耦合、需要频繁共享上下文的修改留在主Session通常更合适。

**验证指标：** 任务完成率、测试通过率、误修改率、P95 延迟和单任务 Token 成本。

**相关知识点：** Fresh Context、Delegation Message、Context Isolation、Summary Return、Tool Scoping、Nested Delegation。
<a id="cc-098"></a>
### Agent Teams的协调原理与普通并行Tool Call有什么区别？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

并行Tool Call发生在同一Agent Turn内，共享一个上下文，适合无依赖的读取和查询。Agent Teams则由多个独立Claude Code实例组成，每个Teammate有自己的上下文，通过共享任务列表和消息通道协调，Lead负责分配、跟踪和综合。

独立上下文提高并行探索能力，也引入状态一致性问题。共享任务状态并不等于共享完整推理证据；Teammate修改同一工作区时也没有自动获得Git隔离。官方建议按文件或模块划分所有权，需要隔离时使用独立Worktree和分支。

选择并行方式要看任务粒度、依赖和通信成本：毫秒级独立读取用并行工具，短期独立研究用Subagent，持续多角色协作用Agent Teams，多任务由人调度可用Agent View。

**相关知识点：** Parallel Tool Call、Independent Context、Shared Task List、Lead/Teammate、Message Passing、Worktree Isolation。
<a id="cc-100"></a>
### 如何从原理层面调试一个“Claude Code没有按预期工作”的问题？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

按**输入上下文—模型决策—权限控制—工具执行—环境副作用—验证结果**逐层定位，而不是只修改Prompt。

1. 用`/context`和`/memory`确认实际加载的CLAUDE.md、Rules、Skill与上下文占用，检查是否发生Compaction。
2. 查看Transcript和Debug日志，确认模型请求了什么工具、参数是什么、Tool Result是否完整以及调用ID是否匹配。
3. 检查Hook、Deny/Ask/Allow、Sandbox和MCP/服务端ACL，区分模型没请求、策略拒绝和执行失败。
4. 在相同Base SHA、配置、模型与依赖下单独重放命令，检查后台进程、环境变量和外部服务状态。
5. 用测试、Diff和Trace验证真实结果；记录Claude Code版本、模型、Provider和随机运行差异。

这种分层方法能把“模型能力问题”与上下文污染、工具契约、权限、环境漂移和验收缺失区分开。

**相关知识点：** Layered Debugging、Context Inspection、Transcript、Tool Trace、Policy Debugging、Environment Reproduction、Result Verification。

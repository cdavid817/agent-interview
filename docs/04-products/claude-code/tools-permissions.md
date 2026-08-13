# 工具、权限与安全

> 所属章节：[Claude Code](README.md)｜本文件共 **28** 题。

<a id="cc-008"></a>
### Claude Code 如何决定使用 Read、Grep、Edit、Bash 等工具？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

模型根据目标、当前证据、工具说明和权限选择工具，Runtime执行并返回结果。定位通常先Glob/Grep，再Read精确范围；修改优先使用Edit或Write；编译、测试、Git和诊断通过Bash执行。

正确工具策略应减少无关读取、避免整文件覆盖、在写前确认最新内容，并在写后运行最小充分验证。工具名称也是权限规则和Hook Matcher的契约，不能仅靠自然语言约束危险命令。自定义能力应通过MCP或Plugin接入，而不是让模型拼接不可审计的临时命令。

**相关知识点：** Built-in Tools、Tool Selection、Targeted Edit、Bash、Permission Rule、Tool Contract。
<a id="cc-009"></a>
### Claude Code 的权限规则和 Permission Mode 如何协作？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

权限规则决定**哪些工具、命令、路径或域名允许、询问或拒绝**，Permission Mode决定当前会话遇到动作时的总体交互方式。

常见模式包括默认确认、自动接受编辑、Plan只读和在隔离环境中使用的绕过确认模式。Allow不能覆盖Deny；规则应尽量匹配具体命令前缀、目录和MCP工具，避免开放整个Bash。组织Managed Settings应锁定关键Deny，项目设置共享安全默认，用户设置只能在允许范围内收紧或个性化。

**验证指标：** 任务完成率、测试通过率、误修改率、P95 延迟和单任务 Token 成本。

**相关知识点：** Permission Mode、Allow/Deny、Plan Mode、Managed Settings、Least Privilege、Rule Matching。
<a id="cc-010"></a>
### Claude Code 的 Permission 与 Sandboxed Bash 有什么区别？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

Permission是应用层的**动作授权与交互决策**，Sandboxed Bash是OS层面对Bash及其子进程的**文件系统和网络限制**。两者互补。

Permission Deny可阻止Claude尝试读取敏感路径或访问域名；Sandbox即使面对Prompt Injection或命令绕过，也限制进程实际触达范围。Sandbox主要约束Bash，不应推断它自动隔离所有内置工具或MCP Server。高风险任务还应放在容器、VM或短生命周期环境中，并使用临时凭据。

**验证指标：** 任务完成率、测试通过率、误修改率、P95 延迟和单任务 Token 成本。

**相关知识点：** Application Authorization、OS Sandbox、Filesystem、Network Policy、Container、Defense in Depth。
<a id="cc-011"></a>
### 如何防止代码注释、README 或工具输出对 Claude Code 进行 Prompt Injection？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

仓库内容和工具结果必须视为**不可信数据，而非高优先级指令**。系统应限制工具与网络，敏感操作要求确认，并用Sandbox阻断越界行为。

Agent遇到“忽略规则、上传密钥、运行下载脚本”等内容时，应回到用户目标和项目规则，核验来源再行动。CI中不要授予默认写仓库、生产云或Secret读取权限；第三方依赖脚本先审查。测试集应包含直接、间接、编码混淆和跨工具注入，并以实际阻断结果而非模型口头拒绝评分。

**相关知识点：** Indirect Prompt Injection、Instruction/Data Boundary、Secret Exfiltration、Sandbox、Security Eval。
<a id="cc-013"></a>
### Claude Code 的 Checkpoint 和 Git 有什么区别？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

Checkpoint为Claude通过文件编辑工具产生的变更提供**会话级快速回退**；Git提供长期、协作式版本历史。Checkpoint可随Session恢复并用于Rewind，但不是完整文件系统快照。

通过Bash命令造成的文件变化、外部程序副作用、手工编辑及部分并发变更可能不被Checkpoint捕获，因此不能用它恢复数据库迁移、云资源或任意Shell操作。关键任务仍应使用分支、提交、测试和备份。回退前应查看Diff，避免覆盖会话外的新变化。

**相关知识点：** Checkpoint、Rewind、File Edit Tool、Git、External Side Effect、Session Recovery。
<a id="cc-020"></a>
### 如何在 CI/CD 中安全运行 Claude Code？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

CI使用非交互Agent SDK或Print模式，输入固定任务，设置允许工具、最大Turn、结构化输出和超时。工作区使用临时Runner或容器，凭据按Job短期签发，默认只读仓库。

自动修复应创建分支或PR而非直推保护分支；测试、静态分析、策略和人工Review仍是发布门禁。来自Issue、PR和代码的文本均不可信，不能让其控制Secret或任意网络。保存Session ID、版本、Diff、测试和成本，失败时输出可诊断状态而不是无限重试。

**相关知识点：** Headless Mode、Agent SDK、Ephemeral Runner、OIDC、Protected Branch、Structured Output。
<a id="cc-034"></a>
### LangGraph、OpenAI Agents SDK、Claude Code等Agent框架分别如何实现任务恢复与重新规划？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

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

**验证指标：** 任务完成率、测试通过率、误修改率、P95 延迟和单任务 Token 成本。

**相关知识点：** 图快照、RunState、Session、Handoff、Checkpoint、Rewind、Replan、幂等、Saga。
<a id="cc-038"></a>
### Claude Code设计方案（附加专题）

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

Claude Code类Agent应包含**交互、上下文、规划执行、受控工具、验证恢复和治理**，在大型仓库中完成可验证的最小修改。

1. 入口解析目标、目录、Git状态和项目规则，建立TaskID与权限会话；需求不清先澄清，高风险动作展示目标和Diff。
2. 构建Repo Map、Symbol/AST、BM25、Embedding与Call Graph，结合LSP、Git和测试渐进检索；按Commit更新，避免整库加载。
3. 采用Plan—Act—Observe—Verify，将任务拆为可验证Step，模型只选结构化工具；新证据触发重规划，并设置步骤、Token和重试预算。
4. 提供Read、Search、Edit、Shell、Git、Test和MCP，使用Schema、路径Allowlist、沙箱与Policy Engine；危险Shell、Push和发布需审批。
5. 使用Patch修改，执行编译、单测、静态、安全检查及影响分析；失败局部重试，状态与Artifact通过检查点持久化。

平台记录模型、Prompt、索引、Tool、Trace、Diff、测试和成本，支持恢复与回放。评估完成率、补丁正确率、定位Recall、安全和成功成本。

**相关知识点：** Repo Map、Plan-Act-Observe、Tool Schema、MCP、沙箱、最小Diff、Change Impact Analysis、检查点、可观测性。
<a id="cc-049"></a>
### Claude Code的工具调用协议如何设计？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

工具协议应是**强类型请求、结构化结果、权限前置、可取消执行与审计**的契约；模型提出意图，宿主负责校验和执行。

1. Tool Registry声明名称、版本、JSON Schema、读写等级、幂等性、超时、资源上限和权限，并明确失败语义。
2. 请求包含session、call、step、tool、arguments、cwd、Commit、权限和deadline。宿主校验Schema、路径、策略、ACL及预算，高风险动作请求确认。
3. 沙箱执行支持超时、取消、限流和进程树清理；幂等工具可按idempotency_key重试，非幂等写操作不得自动重放。
4. 结果返回status、exit_code、输出摘要、Artifact、Diff、耗时、错误类别和retryable。大输出落盘，模型接收关键片段与游标。
5. 审计日志关联输入hash、策略、审批、环境和结果；敏感字段脱敏。Pre/Post Hook可阻断危险调用或触发测试与告警。

MCP可接入外部工具，但不替代权限、沙箱与事务控制；破坏性Schema变更使用新版本灰度发布。

**相关知识点：** Tool Registry、JSON Schema、Call ID、幂等键、权限前置、沙箱、取消传播、结构化错误、Artifact、审计日志、MCP。
<a id="cc-050"></a>
### Shell命令如何进行安全校验？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

Shell安全校验采用**结构化解析、策略判定、最小权限沙箱、执行约束和审计**，不能仅依赖字符串黑名单。

1. 模型尽量提交argv、cwd、环境变量和重定向的结构化请求；必须接收命令串时，使用对应Shell语法解析器生成AST，识别管道、子命令、重定向、变量展开、通配符和编码绕过，禁止把未可信输入再次拼接解释。
2. 路径先规范化并解析符号链接，校验读写目标位于允许工作区；命令、参数、域名和文件按deny→ask→allow策略匹配。递归删除、提权、磁盘格式化、凭证访问、外传和持久化操作默认拒绝或强制确认。
3. 在非Root容器或OS沙箱中执行，设置只读根文件系统、可写目录白名单、网络域名白名单、进程/CPU/内存/磁盘配额及Secret最小注入；权限校验与沙箱必须同时存在。
4. 执行前展示展开后的命令、cwd、影响文件和风险等级；写操作绑定当前Git状态并建立可恢复快照。运行时设置超时、输出限额、取消传播及进程树回收，阻止后台逃逸。
5. 记录原始请求、规范化AST、策略命中、审批、环境hash、退出码和文件Diff，敏感值脱敏；执行后检查越界修改、异常网络连接和新建可执行文件。

安全规则需用绕过语料持续测试，并对误拦截率与漏拦截率分层评估；高风险类别应选择失败关闭。

**相关知识点：** Shell AST、命令注入、路径规范化、符号链接、deny-ask-allow、沙箱、最小权限、资源配额、审计、失败关闭。
<a id="cc-051"></a>
### 如何防止Agent执行危险命令？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

防止危险命令必须贯彻**模型不拥有最终执行权、默认最小权限、高风险显式确认、系统级隔离和全程可追溯**，任何单一Prompt或黑名单都不足以构成安全边界。

1. 工具层按风险分级：只读查询可自动执行，工作区内可逆编辑按策略授权，删除、提权、外网发送、凭证读取、生产变更和不可逆操作默认拒绝。规则采用deny优先，并由企业托管策略锁定。
2. 对命令进行Shell AST解析和参数级校验，规范化路径、符号链接、重定向、管道及变量展开；识别`rm`别名、脚本间接调用、编码、子Shell等绕过方式。高风险判断不交给同一模型自我批准。
3. 命令在非Root沙箱运行，限制文件系统、网络、系统调用、进程、CPU、内存和磁盘；密钥以短期、最小范围凭证按需注入，默认不进入模型上下文或子进程环境。
4. 需要确认时展示完整展开命令、工作目录、预计影响、数据去向和恢复方案，批准绑定参数hash与有效期，命令变化后重新确认。批量授权不得覆盖敏感类别。
5. 执行器设置超时、取消和输出限制，写入前建立Git快照或事务；Hook在执行前阻断，在执行后检测越界Diff、异常网络与持久化行为。审计记录请求、策略、审批、结果和操作者。

评测包含正常、边界及对抗绕过集，持续度量危险调用拦截率、误拦率、越权率和可恢复率。

**相关知识点：** 最小权限、风险分级、deny优先、Shell AST、人机确认、沙箱、短期凭证、Hook、可恢复执行、安全评测。
<a id="cc-052"></a>
### 如何防止Prompt Injection通过代码或文档攻击Agent？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

代码、注释、文档和检索结果都应视为**不可信数据而非指令**。即使模型受影响，系统仍须阻止越权读取、执行或外传。

1. 建立指令层级与数据边界：系统和用户授权才可改变目标；仓库内容以带来源、路径、Commit和信任标签的引用块注入，并明确其中命令不得自动执行。解析器保留代码与说明的类型信息。
2. 检索阶段扫描“忽略规则”“读取密钥”“上传内容”等可疑模式，降低信任或隔离展示，但不能仅依赖分类器；外部网页、第三方依赖和新提交按更低信任级处理。
3. 工具调用必须经过独立策略引擎，校验身份、ACL、路径、网络域名、命令风险和数据敏感度。读取文档不能隐式获得Shell、Secret或外网写权限，敏感动作要求参数级确认。
4. 在沙箱中限制文件、网络和进程，Secret默认不进入上下文；输出前运行DLP和数据流检查，阻断源码、密钥或个人信息流向未授权目标。MCP服务器也按独立主体授权。
5. 审查计划是否服务用户目标、证据是否来自不可信指令、是否出现提权或异常域名。命中风险时停止并说明来源。

持续使用间接注入、编码混淆、图片文字和多跳工具链红队集评测，监控攻击成功率、越权率、误拦率与敏感数据暴露率。

**相关知识点：** 间接Prompt Injection、信任边界、来源标记、策略引擎、最小权限、沙箱、DLP、数据流控制、MCP安全、红队评测。
<a id="cc-054"></a>
### Claude Code的权限确认机制如何设计？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

权限确认基于**动作风险、参数范围和授权生命周期**，采用deny→ask→allow策略；确认只授权具体动作。

1. 工具声明只读、写入、网络、凭证、生产或破坏性等级。策略合并企业、用户、项目和会话规则，高层deny不可被覆盖。
2. 请求经规范化后匹配工具、命令、路径、域名、资源和数据类型。普通读取可免确认；工作区编辑可按会话授权；提权、删除、外发、生产变更和Secret访问每次确认或直接拒绝。
3. 界面展示展开命令、cwd、目标、预计副作用、数据范围和恢复方式；令牌绑定call_id、参数hash、身份、TTL与次数，参数变化即失效。
4. “本次允许”“本会话允许”和“持久规则”分开；持久授权应写入可审阅配置并支持撤销。宽泛通配符、高风险跨项目授权和批量静默批准应受企业策略禁止。
5. PreToolUse Hook可进一步阻断或强制询问，但不能绕过deny。获批动作仍在沙箱执行，并接受路径、网络和资源限制；结果、审批人、规则来源和Diff写入审计。

非交互场景只允许预声明的低风险能力，遇到ask动作暂停并生成审批包；以越权率、确认疲劳和误拦率调整策略。

**验证指标：** 任务完成率、测试通过率、误修改率、P95 延迟和单任务 Token 成本。

**相关知识点：** deny-ask-allow、风险分级、参数绑定授权、审批TTL、托管策略、PreToolUse Hook、确认疲劳、非交互审批、审计。
<a id="cc-055"></a>
### 沙箱应该使用容器、虚拟机还是操作系统权限隔离？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

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
<a id="cc-059"></a>
### 如何防止模型整文件重写导致代码丢失？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

工具层应强制**局部Patch、版本前置条件、Diff预算和可恢复写入**；整文件写入属于高风险能力，默认限制。

1. 编辑接口优先接受search/replace、AST节点变换或Unified Diff，要求提供唯一上下文锚点；写入前校验path、blob hash或mtime，文件已变化时拒绝并重新读取。
2. 整文件Write与局部Edit权限分离。仅新文件、小文件或生成物允许Write；覆盖现有文件展示原因、大小、删除比例和预览。
3. 在临时文件或内存应用补丁，完成语法、编码、换行符和Patch命中数校验后原子替换；保留Git基线、备份或事务日志。工具失败不得留下半写文件。
4. 写后比较Diff、文件hash、Symbol数量和关键区段。删除比例、文件数、格式噪声或公共API变化超阈值时阻断；生成代码应修改源模板。
5. 运行格式化、解析、类型检查和目标测试，并检查未跟踪文件及权限位。多Agent场景为文件加租约或使用独立Worktree，合并时按Patch审查，避免最后写入者覆盖他人。

阈值按任务配置，重构可放宽但须加强回归；自动恢复只撤销本次补丁，不得重置用户已有修改。

**相关知识点：** 局部Patch、乐观锁、原子写入、Diff Budget、Git基线、事务日志、AST Edit、Worktree、并发冲突。
<a id="cc-061"></a>
### 测试失败后Agent如何进行反思和重试？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

有效反思是**基于失败证据更新假设并选择新动作**，不是重复生成同类补丁。重试必须有分类、预算、差异和停止条件。

1. 保存测试命令、退出码、失败用例、堆栈、环境、当前Diff与基线结果；先确认失败是否由本次变更引入，区分代码缺陷、测试预期错误、环境缺失、依赖波动和Flaky。
2. 将日志压缩为结构化Failure Record：现象、首个根因帧、相关Symbol、可复现性、错误类别、可恢复性和证据置信度。避免被后续级联错误误导。
3. 比较“预期行为—实际行为—补丁意图”，提出可证伪的新假设；定向读取失败路径、调用方和测试夹具。每轮明确与上一轮不同的新证据或策略，没有差异则不得重试。
4. 生成最小修复后先运行单个失败测试，再执行受影响测试和必要回归。环境类错误可按退避策略有限重试；代码断言失败不应原样重跑，除非已修改代码或测试数据。
5. 状态机记录attempt_id、假设、动作、结果和成本。相同签名连续出现、补丁来回震荡、超过轮次/Token/时间预算或需要改变需求时停止，恢复至最后稳定Checkpoint并报告阻塞证据。

不得为通过测试而删除断言、跳过用例、扩大Mock或修改无关生产逻辑。最终评估首次修复率、平均重试数、无效重试率、回归通过率和人工接管率。

**相关知识点：** Failure Record、错误分类、可证伪假设、有界重试、Flaky Test、Checkpoint、震荡检测、失败签名、人工接管。
<a id="cc-062"></a>
### Agent如何区分可恢复错误与不可恢复错误？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

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
<a id="cc-065"></a>
### Claude Code如何支持任务中断和恢复？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

关键是**取消运行与持久化状态解耦**：停止副作用，保存Checkpoint，恢复时验证外部状态是否与快照一致。

1. 会话、计划节点和调用使用稳定ID；状态保存目标、约束、DAG、完成节点、Evidence、Diff、Git HEAD、测试、预算和待办。
2. 中断时传播Cancellation Token，停止模型流、MCP调用和子进程树；写操作等待安全点或补偿，记录成功、失败或未知。
3. 在步骤完成、写入前后、测试结束及压缩前原子落盘，Artifact按hash外置；短期凭证和锁释放后重新申请。
4. 恢复先校验身份、权限、HEAD、工作树hash、锁文件及外部版本。未变化则继续；发生漂移则重检索或处理冲突。
5. 工具调用以幂等键去重，状态未知的写操作先查询服务端；已完成节点只有在输入hash一致时复用。恢复后展示先前修改、剩余计划和风险，让用户能够调整范围。

Checkpoint应加密、设TTL并隔离租户；通过强杀、断网、重启和Git漂移演练，衡量恢复率、重复副作用率与恢复时间。

**相关知识点：** Cancellation Token、Checkpoint、计划DAG、内容寻址、幂等恢复、状态漂移、补偿事务、进程回收、恢复演练。
<a id="cc-069"></a>
> **题目合并：** `CC-069` 已并入 [MULTI-033 · 多Agent并发修改同一文件时如何解决冲突？](../../02-capabilities/multi-agent/conflict-reliability.md#multi-033)。

<a id="cc-071"></a>
### 如何利用Hooks实现安全审计和质量检查？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

Hooks部署在**动作前阻断、动作后验证、任务结束汇总**三个位置，将安全与质量规则转为确定性控制。

1. PreToolUse规范化Shell AST与路径，检查禁用命令、敏感目录、域名、Secret、生产资源及Diff预算；高风险拒绝或确认。
2. PostToolUse运行格式化、解析、Lint、Secret Scan和SAST，检查Diff、删除比例、权限位及越界文件；失败则阻断提交。
3. PostToolUseFailure记录错误、重试和副作用，检测重复调用；Stop阶段确认验收测试、未提交Diff、告警和审计完整性。
4. 审计含event_id、call_id、actor、规则版本、输入hash、决策、审批和结果，写入防篡改存储；Secret预先脱敏。
5. 强制规则使用托管Hook，项目Hook需审查。Hook在低权限环境运行，设置超时、输出上限与失败策略；安全Hook失败应关闭执行。

规则先观察误报，再灰度阻断；监控覆盖率、拦截率、误报率、P95延迟和绕过事件，并用对抗样例回归。

**相关知识点：** PreToolUse、PostToolUse、SAST、Secret Scan、Diff Budget、防篡改审计、托管Hook、失败关闭、观察模式。
<a id="cc-073"></a>
### 如何设计Coding Agent的可观测性系统？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

可观测性覆盖**任务、模型、检索、工具副作用、质量、成本和安全**，以统一Trace关联生命周期。

1. 为task、step、model、retrieval、tool、patch、test和approval分配ID；事件携带tenant、repo、commit、agent、model和规则版本。
2. Metrics统计完成率、首次补丁通过率、接管率、重试率、Recall@K、工具成功率、P95/P99、Token、费用和安全拦截，并分层切片。
3. Trace记录计划、查询与证据ID、工具参数hash、错误、Diff和测试；大日志与代码存为Artifact，不写入完整Prompt或Secret。
4. Log采用结构化Schema，实施脱敏、采样、租户隔离、加密、TTL和RBAC；高风险审计不采样并防篡改。
5. Dashboard为排队、模型错误、MCP熔断、失败风暴、成本异常和越权建立SLO告警；以Trace回放和失败聚类定位回归。

业务与系统指标关联，如成功任务单位成本；验证遥测不会泄密或显著增延迟，并用观测数据更新评测集。

**相关知识点：** OpenTelemetry、Trace/Span、SLO、结构化日志、Artifact、脱敏、失败聚类、单位成功成本、安全审计、评测闭环。
<a id="cc-079"></a>
### 企业内部部署Claude Code需要考虑哪些安全问题？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

企业部署围绕**身份权限、数据边界、工具执行、供应链、审计合规和模型数据使用**建立纵深防御。

1. 接入SSO/MFA和短期身份，按用户、仓库、路径与工具实施RBAC/ABAC；企业deny高于项目配置，支持即时撤权。
2. 明确源码、Prompt、遥测和响应的数据流、区域、保留、训练使用与删除；敏感仓库使用合规端点，传输存储加密，缓存隔离。
3. Secret存入Vault，默认拒绝`.env`和凭证目录读取；工具使用最小范围短期令牌。DLP与Secret Scanner覆盖输入、工具输出、日志、Trace及外发。
4. Shell与MCP在非Root沙箱运行，限制挂载、系统调用、网络域名和资源；危险命令、生产写入、外部发送及新MCP Server需策略审批。仓库文档视为不可信，防范间接Prompt Injection。
5. 插件、Hook、MCP、镜像和依赖实行白名单、签名、版本锁定、SBOM与扫描；审计关联身份、工具、审批、Diff和结果。

上线前完成威胁建模、红队和事件响应演练；监控越权、泄密、危险调用和供应链告警。高敏任务使用微VM与双重审批。

**相关知识点：** SSO、RBAC/ABAC、数据驻留、DLP、Vault、沙箱、间接注入、SBOM、供应链安全、防篡改审计、威胁建模。
<a id="cc-080"></a>
### OpenCode与Claude Code的架构差异是什么？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

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
<a id="cc-084"></a>
### 工具Schema和工具描述为什么会影响Claude Code的推理与行为？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

工具定义构成模型当前可选择的**动作空间**。名称、描述、参数Schema和示例告诉模型工具能做什么、何时使用以及怎样构造参数；含糊或重叠的描述会增加误选工具和参数错误。

Runtime仍需做确定性校验：验证JSON Schema、权限和路径，执行工具并限制超时与输出大小。模型选择某个工具只是请求，不是授权；工具返回成功也不代表业务结果正确。

设计自定义MCP工具时应采用清晰动词、窄职责、强类型参数和结构化错误，并让读写能力可区分。工具集过大时使用Tool Search延迟加载Schema，降低上下文噪声。

**相关知识点：** Action Space、Tool Schema、Tool Description、Structured Error、Capability Boundary、Schema Validation。
<a id="cc-091"></a>
### Claude Code的Bash工具如何处理Shell状态和后台任务？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

Bash调用由Harness启动进程执行，命令的stdout、stderr和退出状态作为工具结果返回。不能假设不同Bash调用天然共享同一个交互式Shell状态；需要跨调用持久化的环境变量应通过启动环境、`CLAUDE_ENV_FILE`或SessionStart Hook明确注入。

长时间命令可以转为后台任务，Runtime返回Task ID，使Agent继续工作并在之后查询输出。后台进程属于外部环境状态，不会因为对话Compact、Rewind或模型停止调用工具而自动撤销。

工程上要为进程设置超时、日志上限、端口和清理策略，并区分“命令已启动”“进程仍健康”和“业务已就绪”。测试Server启动后应通过健康检查而非仅看零退出码判断成功。

**相关知识点：** Process Execution、stdout/stderr、Exit Status、CLAUDE_ENV_FILE、Background Task、Process Lifecycle。
<a id="cc-092"></a>
### 一次工具调用同时命中Hook、Deny、Ask和Allow时，权限决策如何理解？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

权限决策遵循**拒绝优先和多层约束**。`PreToolUse`在权限提示前运行，可阻止、修改输入或提出决策；显式Deny仍不能被Hook的Allow结果绕过，Ask也仍可要求确认。阻断型Hook可在Allow规则存在时拒绝动作。

随后Permission规则根据工具、命令、路径或域名匹配Deny、Ask和Allow。Sandbox启用自动放行时，只是用OS隔离边界替代部分逐命令确认，显式Deny与关键路径保护仍然有效。MCP或远端服务还会执行自己的身份与资源授权。

因此最终可执行范围是Hook、Managed Settings、项目/用户权限、Sandbox和后端ACL的交集，而不是某一条Allow的并集。

**验证指标：** 任务完成率、测试通过率、误修改率、P95 延迟和单任务 Token 成本。

**相关知识点：** Deny-first、PreToolUse、Permission Evaluation、Managed Settings、Policy Intersection、Backend ACL。
<a id="cc-093"></a>
### Claude Code Sandbox的安全边界是如何形成的？为什么仍可能需要人工确认？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

Sandbox在OS层限制Bash及其子进程的文件系统和网络访问；Permission层对所有工具的动作进行授权。两者合并后，命令即使受到Prompt Injection影响，也应被限制在允许挂载和域名内。

Sandbox不是所有能力的统一虚拟机：内置Read/Edit、WebFetch和MCP有各自权限路径，Bash之外的工具不能只靠Shell Sandbox保护。若平台依赖缺失，默认配置可能警告后继续以非Sandbox方式执行；高安全环境应启用不可用即失败。

某些不兼容命令可以请求在Sandbox外重试，这个Escape Hatch需要走常规权限流程，并可被组织关闭。生产任务还应使用短生命周期容器或VM、临时凭据和服务端最小权限。

**验证指标：** 任务完成率、测试通过率、误修改率、P95 延迟和单任务 Token 成本。

**相关知识点：** OS Sandbox、Fail Open、Fail Closed、Escape Hatch、Filesystem Boundary、Network Boundary、Defense in Depth。
<a id="cc-099"></a>
### Claude Code面对工具失败时，恢复机制的本质是什么？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

工具失败会作为Observation进入下一轮，模型可根据错误类型选择重试、修改参数、换工具、降级或请求用户。Harness提供最大Turn、权限拒绝、取消和Session恢复等控制，但不会自动证明某个重试策略正确。

应先把失败分类：

1. 瞬时失败：限流、网络抖动，可指数退避并设置上限。
2. 输入或前置条件失败：修正参数、路径、依赖或环境。
3. 权限与策略失败：不能通过改写命令绕过，应请求授权或停止。
4. 确定性业务失败：保留证据、改变方案或升级人工。

连续调用相同工具、错误指纹不变且没有新证据就是无进展。此时应停止重试并输出当前状态、已验证事实和需要的外部决策。

**相关知识点：** Error Observation、Retry Taxonomy、Exponential Backoff、Policy Failure、Error Fingerprint、No-progress Loop。

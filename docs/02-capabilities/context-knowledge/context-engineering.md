# Context Engineering 与组装

> 所属章节：[上下文与知识系统](README.md)｜本文件共 **8** 题。

<a id="ctx-071"></a>
### CTX-071 · 如何识别用户偏好类信息？

> 稳定 ID：`CTX-071`｜原题号：71

**用户偏好识别应区分明确声明、行为推断和情境选择，只有稳定、可解释且允许保存的偏好才能进入长期记忆。**

| 类型 | 示例 | 处理 |
| --- | --- | --- |
| 明确偏好 | “以后报告使用中文” | 高置信候选 |
| 行为偏好 | 多次选择表格输出 | 累积证据后确认 |
| 情境选择 | 本次不要图表 | 仅当前任务有效 |

1. 抽取器识别“喜欢、默认、以后、总是、不要、除非”等信号，并结合选择日志、纠错和重复模式；输出subject、key、value、scope、polarity、confidence和source_ids。否定、比较、条件与范围必须保留，例如“工作报告简洁，但技术设计要详细”不能压成“偏好简洁”。

2. **明确声明的权重高于行为推断，单次选择不能自动升级为稳定偏好。**行为候选需达到次数、时间稳定性和反例比例阈值，敏感属性禁止从行为推断。保存前检查用户归属、用途、权限、重复和冲突；新偏好采用版本更新，旧值标记superseded。

3. 召回时按任务类型、渠道、地域和时间匹配scope，将偏好作为软约束；与当前请求冲突时以当前请求为准，并记录纠错。评测抽取Precision、错误泛化率、冲突识别率、用户纠错率、采纳率和删除完成率，定期支持用户查看、修改或删除偏好。

**相关知识点：** Preference Extraction、Explicit Preference、Implicit Preference、Scope、Polarity、置信度校准、Supersedes、敏感属性推断、用户控制。
<a id="ctx-160"></a>
### CTX-160 · 企业级 Agent 的 Prompt 分层应该如何设计？

> 稳定 ID：`CTX-160`｜原题号：160

**企业级Agent Prompt应按全局策略、业务策略、Skill方法、任务目标和动态上下文分层，由Prompt Builder按优先级组装。**

1. System层定义角色、安全边界和禁止行为；Policy层承载组织流程与授权；Skill层提供任务方法、工具选择和失败处理；Task层描述目标与验收标准；Context层注入状态、Memory、RAG证据和工具结果。上层约束不得被下层覆盖，各层由明确owner维护。

2. 静态指令由模板仓库管理，动态内容使用XML标签或JSON结构，标记source、trust_level、version和时间；外部文本只能作为数据。Prompt Builder依据意图、权限、工具和Token预算选择Skill与证据，再去重压缩。**权限检查与工具参数校验必须由代码强制完成，不能只写在Prompt中。**

3. 每层独立版本化并声明变更原因、依赖模型、输出Schema和兼容范围；trace记录组合清单及哈希。上线前评估指令遵循、工具选择、注入防护和格式稳定性，先影子再灰度。线上监控Token、任务成功率和分层冲突，异常时只回滚责任层。

**相关知识点：** System Prompt、Policy Prompt、Skill Prompt、Task Prompt、Context Layer、Prompt Builder、信任边界、结构化变量、分层版本、可复现Trace。
<a id="ctx-161"></a>
### CTX-161 · System Prompt 和 Skill Prompt 的职责边界是什么？

> 稳定 ID：`CTX-161`｜原题号：161

**System Prompt定义跨任务恒定的身份与安全边界，Skill Prompt定义特定能力被选中后如何执行，两者不得互相复制或越权。**

1. System层包含角色、指令优先级、禁止动作、授权要求和通用工具约束，应简洁稳定；Skill层包含触发条件、执行步骤、工具Schema、前后置条件和异常处理，由能力团队维护。Skill未启用时，其方法不应占用上下文或影响其他任务。

2. Skill只能细化System允许的行为，不能放宽权限、暴露秘密或覆盖安全拒绝；System也不应堆积每个领域的流程，否则会膨胀和冲突。**判断标准是“是否对所有任务恒真”：恒真约束放System，仅在特定能力成立的方法放Skill。**业务目标和用户输入留在Task或Context层。

| 层级 | 职责 | 变化频率 |
| --- | --- | --- |
| System Prompt | 全局身份、安全、权限原则 | 低 |
| Skill Prompt | 领域方法、工具流程、异常处理 | 中 |

3. Prompt Builder先加载System，再按路由选择Skill，记录版本和组合哈希。测试覆盖Skill冲突、未触发、恶意Skill文本及System升级兼容性；安全规则由代码强制。分别评估System跨场景遵循率与Skill任务成功率，支持独立灰度和回滚。

**相关知识点：** System Prompt、Skill Prompt、指令优先级、职责分离、能力路由、工具Schema、组合哈希、兼容性测试、独立灰度、策略强制。
<a id="ctx-162"></a>
### CTX-162 · Prompt 模板如何进行版本管理？

> 稳定 ID：`CTX-162`｜原题号：162

**Prompt模板应像代码一样具备不可变版本、评审、自动评测、灰度发布、运行追踪和快速回滚能力。**

1. 模板存入Git或Prompt Registry，使用template_id和语义版本，记录owner、场景、变更说明、变量Schema、输出Schema、依赖模型与安全策略；已发布版本不可原地修改。动态变量与正文分离，定义类型、必填、默认值和信任级别。构建时生成内容哈希，并静态检查缺失变量、冲突指令及未转义外部数据。

2. 变更需经代码评审和Golden Dataset回归，比较任务成功、指令遵循、格式合法、工具调用、安全拒绝、Token和延迟；模型升级与Prompt变更尽量分开实验。**发布单元必须同时锁定模板版本、模型版本、输出Schema和关键检索配置，只有模板编号无法复现请求。**破坏性Schema变化提升主版本。

3. 上线采用影子流量、Canary和A/B，按用户稳定分桶，设置质量、安全、成本护栏及自动回滚阈值；日志保存template_id、version、hash、实验组和组装片段标识。发布后监控失败分桶与用户纠正，异常一键切回稳定版。废弃版本保留审计元数据与评测报告，停止新流量但支持历史追溯。

**相关知识点：** Prompt Registry、语义版本、GitOps、变量Schema、内容哈希、Golden Dataset、Canary、A/B测试、稳定分桶、自动回滚、运行追踪。
<a id="ctx-173"></a>
### CTX-173 · 如何衡量上下文质量而不是上下文长度？

> 稳定 ID：`CTX-173`｜原题号：173

**上下文质量应以必要信息覆盖、相关性、可信度、新鲜度、一致性、安全性和单位Token任务贡献衡量，而不是以Token总量衡量。**

1. 建立任务级Gold Context，标注必需的指令、状态、事实和证据；Context Recall衡量覆盖，Context Precision衡量有用内容比例，证据密度衡量有效Token占比。再评价来源权威性、版本新鲜度、权限合法性和引用可追溯性，过期或越权内容即使语义相关也属于低质量。

2. 冲突率、重复率、摘要事实一致性、关键约束保留率和Prompt Injection暴露衡量内部质量；位置消融可检查模型是否真正利用关键片段。**高质量上下文的特征是删掉无关部分后结果不变，删掉关键部分后性能显著下降。**可用leave-one-out消融估计片段边际贡献，再计算任务收益除以输入Token或成本。

3. 端到端验证任务成功率、答案忠实度、工具调用正确率、用户纠正、P95和单位成功成本；检索与生成利用分开诊断。仪表盘按System、History、Memory、RAG和Tool展示Token、有效证据、冲突及采用率。对不同预算档位回归，选择质量稳定且证据密度最高的最小充分上下文。

**相关知识点：** Gold Context、Context Recall、Context Precision、证据密度、可信度、新鲜度、冲突率、Leave-one-out消融、边际贡献、最小充分上下文。
<a id="ctx-180"></a>
### CTX-180 · MCP Tool 返回超长结果如何处理？

> 稳定 ID：`CTX-180`｜原题号：180

**MCP Tool返回超长结果时，应在服务端分页或产物化，客户端只注入当前任务需要的结构化摘要和可继续读取的引用。**

1. 工具支持limit、cursor、fields和filter，在源头限制结果；大文件、导出和日志保存为MCP Resource或工作区文件，Tool只返回resource_uri、类型、大小、哈希与预览。客户端设置结果Token上限，截断时显式返回truncated和next_cursor。

2. Result Adapter按Schema提取status、关键字段、计数、错误和产物引用；表格筛列聚合，日志保留退出码、错误段与尾部，搜索精排后取Top-N。**压缩不能删除影响控制流的数字、否定、错误码、副作用证明和分页状态，也不能把部分结果伪装成完整结果。**摘要需回指Resource。

3. Agent按cursor或resource_uri局部读取，避免重复完整Tool；读取仍执行租户和ACL校验。trace记录tool_call_id、参数哈希、结果哈希、压缩器版本和引用。评测压缩率、关键字段保留率、下一步成功率、错误诊断率、延迟及Token成本，并测试超长、分页中断、二进制和恶意内容。

**相关知识点：** MCP Tool、MCP Resource、Cursor Pagination、字段投影、Resource URI、Result Adapter、截断标记、结果哈希、按需读取、关键字段保留率。
<a id="ctx-184"></a>
### CTX-184 · 如何监控和评估 Prompt 的效果？

> 稳定 ID：`CTX-184`｜原题号：184

**Prompt效果应以任务成功、指令遵循、事实忠实、安全性和资源效率联合衡量，并通过版本化离线回归与线上对照实验持续监控。**

1. 建立覆盖正常、边界、冲突指令、长上下文、工具失败和Prompt Injection的Golden Dataset；每条样本定义任务目标、允许证据、预期行为、禁止行为和输出Schema。离线检查任务成功率、约束遵循率、答案正确性、Faithfulness、引用准确率、格式通过率、拒答合理性及攻击成功率，并固定模型、知识和工具模拟版本。

2. LLM-as-a-Judge可按明确Rubric扩展评测，但要提供输入、证据和预期标准，并用人工样本校准一致性、位置偏差与自偏好。**不能只评答案措辞是否流畅，Prompt的核心价值是让系统稳定完成任务并遵守约束。**结构化输出和安全规则优先使用解析器与Schema检查。

3. 线上记录Prompt与模型版本、实验组、Token、裁剪原因、工具结果、延迟、重试和反馈；按用户或会话分桶做A/B，主指标为任务成功率，安全、P95和成本作为护栏。告警按场景分层，退化时重放Trace比较旧新Prompt，确认是模板、上下文、模型还是数据变化。

**相关知识点：** Prompt Evaluation、Golden Dataset、指令遵循率、Faithfulness、Schema校验、LLM-as-a-Judge、Prompt Injection、A/B测试。
<a id="ctx-192"></a>
### CTX-192 · 模型如何区分工具返回结果和用户输入？

> 稳定 ID：`CTX-192`｜原题号：192

**模型主要依靠消息角色、tool_call_id和结构化协议区分工具结果与用户输入，应用层必须保持这些边界，不能把所有内容拼成普通文本。**

1. 协议包含system、user、assistant和tool等角色。模型发出带name、arguments与call_id的调用，执行器返回匹配的tool消息；模型因此区分用户意图与外部结果。多工具并行时call_id负责结果归属。若框架把tool结果改成user消息，模型只能依赖文字标签猜测来源。

2. 工具返回应符合Schema，并封装tool_name、call_id、status、source、payload和error；长结果外置，Prompt只注入必要字段与引用。**角色能标识来源，但不能证明内容可信，工具结果仍需参数校验、来源验证、脱敏和权限控制。**网页或文档指令视为数据，不得提升为System规则。

3. System Prompt明确角色信任级别：用户描述目标，工具提供事实或状态，只有策略层可修改约束。执行器拒绝未知call_id、重复结果和Schema不符数据，错误以显式状态返回。测试覆盖并行、超时、恶意工具输出和伪造标签，监控错误归因、注入成功率与引用准确率。

**相关知识点：** Message Role、tool_call_id、Function Calling、JSON Schema、工具结果封装、信任边界、Prompt Injection、来源验证。

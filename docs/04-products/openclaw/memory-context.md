# 记忆与上下文

> 所属章节：[OpenClaw](README.md)｜本文件共 **8** 题。

<a id="oclaw-008"></a>
### OCLAW-008 · OpenClaw 如何利用混合检索提高 Memory Recall？

> 稳定 ID：`OCLAW-008`｜原题号：8｜核验日期：2026-08-03｜来源：[官方资料](references.md)

混合检索将**关键词精确命中、向量语义召回与重排**结合：人名、编号和专有词适合词法搜索，偏好与语义相近表达适合向量搜索，融合后再按相关性、新鲜度和来源筛选。

查询前应识别实体、时间和当前任务，检索结果必须带来源文件与范围；低置信结果只能作为候选，不能覆盖用户当前陈述。评估要使用真实跨会话问题，报告Recall@K、上下文Precision、过期记忆率、冲突率和额外Token，而非只看Embedding相似度。

**相关知识点：** BM25、Embedding、Hybrid Retrieval、Rerank、Recall@K、Context Precision、记忆冲突。
<a id="oclaw-013"></a>
### OCLAW-013 · 如何防止不可信频道用户控制 OpenClaw 执行危险操作？

> 稳定 ID：`OCLAW-013`｜原题号：13｜核验日期：2026-08-03｜来源：[官方资料](references.md)

安全链路应是**入口鉴权—发送者Allowlist—会话隔离—工具最小化—沙箱—高风险确认—审计**。

群聊和公开频道默认不应暴露文件、Shell、浏览器登录态或Session History；提及触发和机器人互聊还要防循环。网页、邮件、附件和其他用户消息都作为不可信数据，不能覆盖系统与Agent规则。高风险Agent可配置只读工作区和无Shell工具，互不信任用户应拆分Gateway而非只靠Prompt区分。

**验证指标：** 任务完成率、工具调用成功率、P95 延迟、Token 消耗和人工接管率。

**相关知识点：** Pairing、Sender Allowlist、Group Policy、Prompt Injection、Bot Loop、只读Agent、租户隔离。
<a id="oclaw-015"></a>
### OCLAW-015 · OpenClaw 子 Agent 如何控制上下文、权限和并发？

> 稳定 ID：`OCLAW-015`｜原题号：15｜核验日期：2026-08-03｜来源：[官方资料](references.md)

子Agent默认使用独立Session和独立上下文，只继承规定的引导信息；需要完整对话时才显式Fork。其工具先经过目标Agent策略，再经过子Agent限制层，部分会话、消息、Gateway和Cron能力默认不可用。

应限制并发数、每个父Agent的子任务数、嵌套深度、模型、超时和预算。子Agent完成通知属于回传机制，不应被当作Exactly-once业务提交；关键产物写入可验证Artifact并由父Agent验收。共享Gateway资源下，盲目增加并发可能降低总体吞吐。

**相关知识点：** Context Isolation、Tool Restriction、Concurrency Lane、Nesting Depth、Artifact、Best-effort Announce。
<a id="oclaw-018"></a>
### OCLAW-018 · OpenClaw 的 Code Mode 与普通工具调用有什么差异？

> 稳定 ID：`OCLAW-018`｜原题号：18｜核验日期：2026-08-03｜来源：[官方资料](references.md)

普通工具调用由模型逐个选择并回收每次结果；Code Mode允许在受控JavaScript/TypeScript工作流中**发现、组合和并发调用大量合格工具**，减少中间结果反复进入模型上下文。

它适合结构化批处理、聚合和多工具编排，但应限制可调用工具、循环次数、输出大小和执行时间。脚本仍受宿主策略与沙箱约束，不能将模型生成代码视为可信程序。该能力若标注实验性，生产采用必须固定版本、回归并准备降级到普通调用。

**验证指标：** 任务完成率、工具调用成功率、P95 延迟、Token 消耗和人工接管率。

**相关知识点：** Code Mode、Tool Search、Nested Calls、Context Reduction、执行预算、实验能力。
<a id="oclaw-035"></a>
### OCLAW-035 · OpenClaw 为什么需要 Memory 系统？

> 稳定 ID：`OCLAW-035`｜原题号：35｜核验日期：2026-08-03｜来源：[官方资料](references.md)

**【核心思路】**
OpenClaw是常驻个人助手，需要跨会话保存偏好、长期事实和每日工作记录。官方Memory主要是工作区中的Markdown文件：长期内容在`MEMORY.md`，每日记录在`memory/YYYY-MM-DD.md`；在压缩前可触发Memory Flush提醒模型写入耐久信息。

Memory文件持久存在不代表每轮都进入上下文，相关内容通过搜索按需召回。写入仍需用户或工具事实支撑，敏感信息、临时推断和失败结果不应自动沉淀；多Agent场景还要明确工作区和访问边界。

**验证指标：** 任务完成率、工具调用成功率、P95 延迟、Token 消耗和人工接管率。

**相关知识点：** OpenClaw、Multi-Agent、检索、Memory、Agent Runtime。
<a id="oclaw-036"></a>
### OCLAW-036 · OpenClaw 如何解决上下文窗口限制？

> 稳定 ID：`OCLAW-036`｜原题号：36｜核验日期：2026-08-03｜来源：[官方资料](references.md)

**【核心思路】**
OpenClaw通过会话压缩、Memory Flush与Memory Search减少长期会话对窗口的占用；工具和文件内容应按需读取，而非全量注入。独立子Agent默认使用隔离上下文，只有确需当前对话时才Fork。

压缩会丢失细节，因此关键约束、决定和引用应写入可审查的工作区文件或Artifact。具体上下文上限取决于所选模型，不能把磁盘Memory容量等同于模型Context Window。

**验证指标：** 任务完成率、工具调用成功率、P95 延迟、Token 消耗和人工接管率。

**相关知识点：** OpenClaw、Memory、Context Window、Window。
<a id="oclaw-042"></a>
### OCLAW-042 · OpenClaw 如何管理 Prompt 版本？

> 稳定 ID：`OCLAW-042`｜原题号：42｜核验日期：2026-08-03｜来源：[官方资料](references.md)

**【核心思路】**
OpenClaw通过工作区文件、Agent配置、Skills和Plugins影响行为，但官方文档没有承诺内建完整的企业Prompt Registry与灰度系统。

生产建议把`AGENTS.md`、`SOUL.md`、Skills及相关配置纳入Git或配置发布系统，记录OpenClaw、模型和工具版本，经过Review、离线评测、灰度和回滚再发布。该治理链是企业扩展，而非默认产品能力。

**相关知识点：** OpenClaw、Skill、Prompt Engineering、评测体系、灰度发布。
<a id="oclaw-049"></a>
### OCLAW-049 · OpenClaw 如何设计 Memory 检索机制？

> 稳定 ID：`OCLAW-049`｜原题号：49｜核验日期：2026-08-03｜来源：[官方资料](references.md)

**【核心思路】**
Memory事实来源是工作区Markdown文件，语义搜索可配置OpenAI、本地或其他支持的Embedding Provider。磁盘文件是耐久存储，检索只把相关片段带回有限模型上下文。

应保留来源文件和日期，定期清理陈旧或冲突记忆。使用外部Provider做Embedding时，相关内容会发送给该服务；若有数据不出域要求，应选择本地Provider并实测索引质量。

**验证指标：** 任务完成率、工具调用成功率、P95 延迟、Token 消耗和人工接管率。

**相关知识点：** OpenClaw、Embedding、检索、Memory、Agent Runtime。

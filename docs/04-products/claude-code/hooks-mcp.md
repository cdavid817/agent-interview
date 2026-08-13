# Hooks、MCP 与扩展

> 所属章节：[Claude Code](README.md)｜本文件共 **7** 题。

<a id="cc-015"></a>
### 1. Claude Code Hooks 与普通Prompt规则有什么区别？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

Hook是在Session、工具、通知、Subagent等生命周期事件上运行的**确定性程序化控制**；Prompt规则只影响模型决策，不能保证必然执行。

PreToolUse可校验或阻止命令，PostToolUse可格式化、扫描或记录结果，Stop/SubagentStop可根据验证结果要求继续，Notification可转发等待确认事件。Hook必须快速、幂等、超时可控并处理不可信JSON输入；项目Hook本身也属于可执行代码，应Review和限制权限。

**相关知识点：** PreToolUse、PostToolUse、Stop Hook、SubagentStart、Matcher、Deterministic Guardrail。
<a id="cc-021"></a>
### 2. Claude Agent SDK 与直接调用 Claude API 或 Claude Code CLI 有什么区别？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

Claude API提供模型原语，需要应用自己实现Agent Loop、工具执行和会话；Claude Code CLI面向开发者交互；Claude Agent SDK把与Claude Code相同的**循环、工具和上下文管理**作为Python/TypeScript库嵌入应用。

SDK适合需要程序控制工具、权限、Hooks、流式消息、Session和结构化结果的产品。它不是无状态封装：生产部署要管理持久工作目录、子进程、会话存储、隔离和成本。简单文本生成仍可直接使用Messages API，避免引入完整Agent运行时。

**相关知识点：** Messages API、CLI、Claude Agent SDK、Embedded Runtime、Stateful Session、Build vs Buy。
<a id="cc-022"></a>
### 3. Claude Agent SDK 如何处理结构化输出、审批和用户澄清？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

结构化输出允许Agent经过多轮工具执行后，按JSON Schema、Zod或Pydantic返回可校验结果；审批与澄清则通过SDK事件向宿主应用请求用户输入，再把决定送回Session。

Schema校验失败应重试有限次数或返回明确错误，不能把未验证文本强转成业务对象。审批请求要展示动作、目标、风险和参数，设置超时与取消；Web服务需把Session和正确用户绑定，防止他人批准。高风险操作在批准后仍要由后端重新鉴权。

**相关知识点：** Structured Output、JSON Schema、Approval Flow、User Input、Session Binding、TOCTOU。
<a id="cc-024"></a>
### 4. Claude Code 和 Agent SDK 如何建设可观测性？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

可观测性应关联**Session—Turn—Model—Tool—Hook—Subagent—Result**。CLI可启用使用监控，Agent SDK可导出OpenTelemetry Trace、Metric和Event。

记录模型与Prompt/规则版本、工具名、耗时、状态、Token、费用、权限决定和验证结果；源码、Prompt、Secret与工具原文按敏感级别脱敏或只保存Hash/受控引用。异步Session和容器迁移使用Session ID与业务Task ID关联。关键指标包括完成率、P95、工具失败、权限阻断、重试、缓存和单位成功成本。

**相关知识点：** OpenTelemetry、Trace、Metric、Event、Session ID、Cost Attribution、PII Redaction。
<a id="cc-056"></a>
### 5. MCP在Claude Code中承担什么作用？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

MCP是**标准化连接外部工具、数据源与业务系统**的扩展层，使Claude Code无需为每个系统编写专有协议；它不是安全边界。

1. MCP Server以Schema暴露Tools与Resources，Client负责连接、发现和调用，可接入Issue、数据库、文档、监控和部署平台。
2. 工具描述和Schema支持结构化调用，结果带来源返回；工具可按需发现和延迟加载，避免长期占用上下文。
3. 配置可按用户、项目或企业管理，传输可用本地进程或远程连接；身份、Secret和网络策略由运行环境管理。
4. MCP只解决“如何发现和调用”的互操作问题。是否允许调用、能访问哪些资源、是否需要确认，仍由Claude Code权限规则、Hook、沙箱以及MCP Server自身ACL共同决定。
5. 服务端返回结构化错误、幂等语义和来源；客户端配置超时、熔断、并发上限与降级。返回内容视为不可信数据。

MCP是客户端与能力提供方的协议，Tool Calling是模型提出调用的机制；二者可组合但不互相替代。

**相关知识点：** MCP Client/Server、Tools、Resources、Schema、延迟加载、Tool Calling、ACL、Hook、间接注入、熔断降级。
<a id="cc-072"></a>
### 6. Claude Code如何集成Git、IDE和CI/CD？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

集成以**Git作为事实源、IDE提供上下文、CI/CD承担验证与发布门禁**，通过Commit、任务ID和Artifact追踪。

1. Git层读取HEAD、工作树和Diff，保留用户未提交变更；Agent在独立分支或Worktree生成Patch，禁止强推或改写历史。
2. IDE传递仓库、打开文件、选区和诊断，展示计划、Diff、确认及测试；LSP提供定义、引用和诊断，IDE不得绕过权限。
3. 本地运行格式化、类型检查和目标测试，再创建PR；PR包含摘要、影响域、验证命令、风险和AI来源标识。
4. CI从干净Commit重跑构建、测试、SAST、Secret和依赖扫描；结果经Check Run回传，Agent不得篡改门禁。
5. CD与代码执行身份分离，生产部署需要审批、短期凭证、Canary和回滚；高风险动作遵循组织策略。

事件共享repo、commit、pr、run和session；以签名Webhook、最小Token权限和审计防伪。评估PR通过率、CI通过率和回滚率。

**相关知识点：** Git Worktree、LSP、PR工作流、CI门禁、Check Run、Webhook、SAST、Canary、短期凭证、端到端追踪。
<a id="cc-094"></a>
### 7. Claude Code Hooks在Runtime中类似什么机制？其阻断语义如何实现？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

Hooks可理解为Agent Runtime的**生命周期事件总线和策略扩展点**。Session、Prompt、Tool、Permission、Compaction、Subagent和Task等事件触发外部命令、HTTP端点或其他处理器，输入输出通过结构化JSON传递。

命令Hook退出码`0`表示正常并可解析JSON，退出码`2`在支持阻断的事件上表达拒绝；不同事件的阻断效果不同，例如`PreToolUse`可阻止尚未执行的工具，而`PostToolUse`只能反馈，因为副作用已经发生。多个匹配Hook可能并行执行后合并结果，拒绝应优先。

HTTP Hook的非2xx或超时通常是非阻断错误，不能仅靠返回500实现安全拒绝；需要在2xx JSON中返回对应Decision。安全Hook必须默认策略明确、输入严格解析、超时可控并有审计。

**验证指标：** 任务完成率、测试通过率、误修改率、P95 延迟和单任务 Token 成本。

**相关知识点：** Lifecycle Event Bus、Hook JSON Protocol、Exit Code 2、Pre/Post Semantics、Decision Merge、Fail-open HTTP Hook。

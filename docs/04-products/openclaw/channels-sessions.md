# 渠道、会话与路由

> 所属章节：[OpenClaw](README.md)｜本文件共 **8** 题。

<a id="oclaw-004"></a>
### 1. OpenClaw 如何把不同消息渠道和会话路由到正确的 Agent？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

OpenClaw通过**渠道适配器、Agent Binding和会话键**进行确定性路由。Binding可按渠道、账号、群组或具体对话选择Agent，每个Agent再使用独立工作区与会话存储。

应先定义匹配优先级和兜底Agent，再验证私聊、群聊、线程、多个账号和跨渠道切换。回复目标不能只依赖模型生成，应由入站元数据和当前Reply Route确定。跨渠道Docking或共享主会话会提高连续性，也会扩大信息可见范围，必须符合用户和组织边界。

**相关知识点：** Channel Adapter、Agent Binding、Session Key、Reply Route、Thread、Channel Docking。
<a id="oclaw-006"></a>
### 2. OpenClaw 的主会话、群组会话和子 Agent 会话有什么差异？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

三者的区别在于**身份范围、上下文继承、回复目标和权限风险**。

1. 主会话是个人Agent的滚动对话，可跨入口保持连续体验。
2. 群组或频道通常使用独立会话键，避免把私人主会话内容直接暴露给群成员。
3. 子Agent在独立后台会话运行，默认只获得受限引导文件和工具面；只有明确需要时才Fork父上下文。
4. 会话隔离不等于数据隔离。共享工作区、工具凭据或全局可见Session Tool仍可能跨边界泄漏信息。

设计时应同时检查Session Key、工具策略、工作区、Memory和交付路由。

**验证指标：** 任务完成率、工具调用成功率、P95 延迟、Token 消耗和人工接管率。

**相关知识点：** Main Session、Group Session、Subagent Session、Context Fork、Session Visibility、数据隔离。
<a id="oclaw-007"></a>
### 3. OpenClaw 的 Memory 与会话历史有什么区别？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

会话历史记录**发生过的对话与工具事件**，Memory保存**值得跨会话复用的稳定信息**。把全部历史当Memory会导致噪声、隐私和Token成本不断增长。

OpenClaw可从工作区笔记和已配置的Memory Engine检索相关片段；默认内存后端可结合关键词、向量和混合搜索。写入时应保留来源、时间与置信度，区分用户明确事实、Agent推断和临时任务状态。冲突事实需要更新或保留版本，敏感数据应设访问和保留策略。

**相关知识点：** Episodic History、Durable Memory、Hybrid Search、Provenance、Memory Lifecycle、隐私。
<a id="oclaw-014"></a>
### 4. OpenClaw 多 Agent 路由与临时子 Agent 委派有什么区别？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

多Agent路由是**长期配置的身份与入口分工**，子Agent委派是**某次Run中的临时后台协作**。

前者通过Binding把渠道或会话交给固定Agent，每个Agent有自己的工作区、模型和策略；后者由父Run用会话工具启动，完成后通过Announce链回报。长期领域边界、不同信任级别适合配置Agent；独立研究、慢任务和并行验证适合子Agent。两者都不能默认并发写共享资源。

**相关知识点：** Multi-agent Routing、Agent Binding、Subagent、Delegation、Announce、共享写冲突。
<a id="oclaw-016"></a>
### 5. OpenClaw 如何通过 ACP 接入 Claude Code、Codex 等 Coding Harness？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

ACP用于把外部Coding Harness作为**具有独立会话和执行语义的Agent后端**接入OpenClaw。OpenClaw负责渠道入口、会话协调和交付，Claude Code、Codex或其他Harness负责仓库探索、修改、命令和验证。

接入时要明确工作目录、认证、权限模式、会话生命周期、取消、超时和产物回传。ACP不是MCP：ACP管理Agent会话与任务，MCP主要标准化工具和资源连接。外部Harness的Checkpoint、沙箱和审批语义应按自身文档描述，不能归功于OpenClaw内置Loop。

**相关知识点：** Agent Client Protocol、Coding Harness、Session Backend、MCP、权限传递、结果交付。
<a id="oclaw-021"></a>
### 6. OpenClaw 的模型选择、认证 Profile 轮换与 Fallback 如何协作？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

模型解析先确定Provider与Model，再选择可用认证Profile；遇到符合条件的认证或Provider故障时，可轮换Profile并沿配置的Fallback链尝试其他模型。

显式会话选模、Agent默认模型和任务级覆盖可能有不同优先级，必须检查Effective Model。Fallback要考虑能力、上下文、工具支持、数据区域和价格兼容，不能只按名称替换。业务错误、工具错误和错误Prompt不应靠切模型掩盖。监控切换原因、成功率、质量退化和成本变化。

**相关知识点：** Model Resolution、Auth Profile、Failover、Fallback Chain、Capability Compatibility、路由观测。
<a id="oclaw-022"></a>
### 7. OpenClaw 如何处理长会话的上下文增长？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

主要手段是**Session Pruning、Compaction、Memory写入与按需Recall**。旧的大型工具结果可先裁剪，接近窗口上限时将历史压缩成摘要；稳定事实写入Memory后在后续会话按需检索。

压缩摘要必须保留目标、未完成事项、关键决定、约束、来源和Artifact引用。磁盘上仍有完整Transcript不代表模型仍能看到细节，可用Context检查工具确认实际注入。评估应关注压缩后的任务延续率、约束丢失率、缓存命中与Token，而非只看缩短比例。

**相关知识点：** Context Window、Pruning、Compaction、Memory Flush、Recall、Prompt Cache。
<a id="oclaw-023"></a>
### 8. OpenClaw 的浏览器和设备 Node 能力有哪些安全风险？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

浏览器可能携带登录态、Cookie和高价值会话，设备Node可能访问摄像头、屏幕、位置、通知或本地应用，因此都属于**高权限执行面**。

应使用专用Profile或隔离浏览器，限制允许域名、下载、上传和外部协议；敏感提交前预览并确认。Node需要配对、设备身份、能力Allowlist和可撤销授权，移动设备隐私权限还受操作系统控制。截图和页面内容也可能包含Prompt Injection或敏感数据，日志与Artifact应脱敏和限期保存。

**验证指标：** 任务完成率、工具调用成功率、P95 延迟、Token 消耗和人工接管率。

**相关知识点：** Browser Automation、Authenticated Session、Node Pairing、Capability Grant、TCC、数据脱敏。

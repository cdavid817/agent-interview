# 核心 100 题

> 从完整题库中按章节配额选取原始序号靠前的基础问题，适合快速建立知识主干。该清单由稳定 ID 自动生成，不复制答案。

## Agent 核心架构

- [ARC-001 · 如果让你从 0 到 1 设计一个企业级 Agent，你会如何设计整体架构？（DeepSeek 一面）](../01-foundations/agent-architecture/architecture.md#arc-001)
- [ARC-002 · 一个 Agent 系统应该拆分成哪些核心模块？每个模块分别负责什么？（DeepSeek 一面）](../01-foundations/agent-architecture/architecture.md#arc-002)
- [ARC-003 · 一个企业级 Agent 系统应该拆分成哪些核心模块？规划器、执行器、工具层及记忆层和评测层如何协作？（腾讯二面）](../01-foundations/agent-architecture/runtime-harness.md#arc-003)
- [ARC-004 · 如果让你从 0 到 1 设计一个面向千万用户的大模型应用平台，你会如何划分整体架构？（腾讯二面）](../01-foundations/agent-architecture/platform.md#arc-004)
- [ARC-005 · 腾讯如果要把大模型能力同时接入不同产品，不同产品之间应该如何划分职责？（腾讯二面）](../01-foundations/agent-architecture/architecture.md#arc-005)
- [ARC-006 · 整个 Agent 是怎么运转的？从用户输入到最终完成任务，中间经历了哪些步骤？（DeepSeek 二面）](../01-foundations/agent-architecture/architecture.md#arc-006)
- [ARC-007 · ReAct 加 COT 执行流程和区别（Agent 初级）](../01-foundations/agent-architecture/architecture.md#arc-007)
- [ARC-008 · 为什么没用 LangChain、Spring AI 这些 Agent 开发框架？（豆包一面）](../01-foundations/agent-architecture/frameworks.md#arc-008)
- [ARC-009 · LangChain 和 LangGraph 的区别以及各自适用场景（Agent 初级）](../01-foundations/agent-architecture/frameworks.md#arc-009)
- [ARC-010 · 为什么企业级 Agent 要采用分层架构？](../01-foundations/agent-architecture/architecture.md#arc-010)

## Transformer

- [TRANS-001 · LLM的输入到底是什么？模型真正看到的是什么？（百度Agent）](../01-foundations/transformer/tokens-position.md#trans-001)
- [TRANS-002 · Self-Attention的核心作用是什么？为什么要拆成QKV？为什么Attention可以建模长距离关系？（百度Agent）](../01-foundations/transformer/tokens-position.md#trans-002)
- [TRANS-003 · 为什么需要Multi-Head？为什么Attention可以看成动态加权？（百度Agent）](../01-foundations/transformer/attention.md#trans-003)
- [TRANS-004 · 同一个token的Q、K、V为什么不一样？（百度Agent）](../01-foundations/transformer/tokens-position.md#trans-004)
- [TRANS-005 · Attention复杂度很高，如果上下文特别长，会怎么优化？（百度Agent）](../01-foundations/transformer/attention.md#trans-005)
- [TRANS-006 · Token和字符数、单词数之间是什么关系？](../01-foundations/transformer/tokens-position.md#trans-006)
- [TRANS-007 · 为什么不同模型计算出的Token数不一样？](../01-foundations/transformer/tokens-position.md#trans-007)
- [TRANS-008 · Transformer真正计算的对象为什么是向量而不是文本？](../01-foundations/transformer/tokens-position.md#trans-008)

## 任务规划与执行

- [PLAN-001 · Agent如何做任务识别，比如判断一个任务是简单问答、代码解释、代码修改，还是复杂开发任务？（DeepSeek一面）](../02-capabilities/planning-execution/task-routing.md#plan-001)
- [PLAN-002 · 用户输入一个需求以后，Agent如何理解用户意图，并进行任务拆解？（DeepSeek二面）](../02-capabilities/planning-execution/task-routing.md#plan-002)
- [PLAN-003 · 对于复杂任务，Agent应该如何进行任务拆解和执行计划生成？（DeepSeek一面）](../02-capabilities/planning-execution/task-routing.md#plan-003)
- [PLAN-004 · 任务拆解以后，Agent如何决定先做什么、后做什么？什么时候调用模型，什么时候调用工具？（DeepSeek二面）](../02-capabilities/planning-execution/workflow.md#plan-004)
- [PLAN-005 · 如何设计Agent规划器，避免频繁重新规划？（千问二面）](../02-capabilities/planning-execution/recovery-1.md#plan-005)
- [PLAN-006 · Agent在执行任务过程中，如何判断当前步骤是否成功？失败后如何重试、回滚或重新规划？（DeepSeek一面）](../02-capabilities/planning-execution/recovery-1.md#plan-006)
- [PLAN-007 · Agent执行复杂任务时，如何支持暂停、恢复、重试、回滚、人工干预和任务回放？（腾讯二面）](../02-capabilities/planning-execution/task-routing.md#plan-007)
- [PLAN-008 · DAG任务调度完整执行流程（Agent初级）](../02-capabilities/planning-execution/workflow.md#plan-008)
- [PLAN-009 · 反思机制怎么做？（豆包二面）](../02-capabilities/planning-execution/reasoning-patterns.md#plan-009)
- [PLAN-010 · 说下你对Agent的理解，如何通过反思机制提升整体任务执行成功率？（Agent中级）](../02-capabilities/planning-execution/reasoning-patterns.md#plan-010)
- [PLAN-011 · Agent反复循环调用同一个工具、重复执行任务，怎么排查根源并优化（Agent初级）](../02-capabilities/planning-execution/recovery-1.md#plan-011)
- [PLAN-012 · Agent幂等性怎么设计？（豆包一面）](../02-capabilities/planning-execution/recovery-1.md#plan-012)

## 上下文与知识系统

- [CTX-001 · 介绍一下Harness Engineering（上下文工程）（附加专题）](../02-capabilities/context-knowledge/session-state.md#ctx-001)
- [CTX-002 · 长短期记忆是怎么设计的？短期记忆和长期记忆分别保存什么？（DeepSeek二面）](../02-capabilities/context-knowledge/memory-1.md#ctx-002)
- [CTX-003 · Agent为什么必须设计记忆模块，短期对话记忆、长期持久记忆分别怎么落地，各自解决什么业务痛点（Agent中级）](../02-capabilities/context-knowledge/memory-1.md#ctx-003)
- [CTX-004 · 分层记忆完整体系：瞬时上下文记忆、短期会话记忆、长期持久记忆、知识库外部记忆四层设计；记忆自动压缩、过期清理、重要信息持久留存策略（Agent高级）](../02-capabilities/context-knowledge/memory-1.md#ctx-004)
- [CTX-005 · 为什么要把长期记忆分成静态长期记忆和动态长期记忆？（DeepSeek二面）](../02-capabilities/context-knowledge/memory-1.md#ctx-005)
- [CTX-006 · 每一轮对话都触发长期记忆存储，会不会导致记忆膨胀？以后怎么处理？（DeepSeek二面）](../02-capabilities/context-knowledge/memory-1.md#ctx-006)
- [CTX-007 · 大模型如何判断哪些长期记忆需要召回？如何避免召回太多导致上下文污染？（DeepSeek二面）](../02-capabilities/context-knowledge/memory-1.md#ctx-007)
- [CTX-008 · 上下文是怎么构建的？怎么避免上下文过长或者信息污染？（百度Agent）](../02-capabilities/context-knowledge/compression-cache.md#ctx-008)
- [CTX-009 · 如何理解Agent中的状态和上下文？（千问二面）](../02-capabilities/context-knowledge/session-state.md#ctx-009)
- [CTX-010 · 长短期记忆如何设计提取、压缩和冲突更新机制？（千问一面）](../02-capabilities/context-knowledge/memory-1.md#ctx-010)

## 工具、Skills 与 MCP

- [TOOL-001 · Agent工具调用系统应该怎么设计？工具如何注册、调用、鉴权、限流和追踪？（DeepSeek一面）](../02-capabilities/tools-skills-mcp/sandbox-security-1.md#tool-001)
- [TOOL-002 · 如何自定义工具供给大模型调用，开发工具的关键参数、完整实现流程（Agent初级）](../02-capabilities/tools-skills-mcp/mcp.md#tool-002)
- [TOOL-003 · MCP和Skills有什么区别？（豆包一面）](../02-capabilities/tools-skills-mcp/skill-routing.md#tool-003)
- [TOOL-004 · 工具调用过程中各类异常怎么捕获、兜底处理（Agent初级）](../02-capabilities/tools-skills-mcp/reliability.md#tool-004)
- [TOOL-005 · 工具调用返回200，但业务逻辑错误怎么办？（千问二面）](../02-capabilities/tools-skills-mcp/reliability.md#tool-005)
- [TOOL-006 · Agent生成SQL、代码或Shell命令时如何设计沙箱，了解如何确认机制？（腾讯一面）](../02-capabilities/tools-skills-mcp/sandbox-security-1.md#tool-006)
- [TOOL-007 · Skill沉淀体系应该怎么设计？什么样的任务适合沉淀成Skill？（DeepSeek一面）](../02-capabilities/tools-skills-mcp/skill-governance-1.md#tool-007)
- [TOOL-008 · 用户输入进来以后，系统如何匹配相关Skill？（DeepSeek二面）](../02-capabilities/tools-skills-mcp/skill-routing.md#tool-008)
- [TOOL-009 · Skill分层体系是怎么设计的？为什么要这样分层？不同层级Skill的职责边界是什么？（DeepSeek二面）](../02-capabilities/tools-skills-mcp/skill-governance-1.md#tool-009)
- [TOOL-010 · 有没有Skill沉淀机制？Skill是系统自动沉淀，还是只能用户手动构造？（DeepSeek二面）](../02-capabilities/tools-skills-mcp/skill-governance-1.md#tool-010)

## 多 Agent 与协作

- [MULTI-001 · Agent是单Agent还是多Agent？为什么这么设计？有没有考虑过另一种方案？（百度Agent）](../02-capabilities/multi-agent/selection-architecture.md#multi-001)
- [MULTI-002 · 复杂任务如何拆分子任务下发给子Agent，怎么避免任务重复下发、重复执行（Agent中级）](../02-capabilities/multi-agent/orchestration.md#multi-002)
- [MULTI-003 · 多Agent通信和进度同步怎么做？（豆包一面）](../02-capabilities/multi-agent/communication-state.md#multi-003)
- [MULTI-004 · A2A多智能体通信场景下，Agent调用超时、接口报错、服务宕机，重试、降级、兜底的完整方案（Agent中级）](../02-capabilities/multi-agent/orchestration.md#multi-004)
- [MULTI-005 · A2A通信超时、子Agent服务宕机、工具调用雪崩场景下的熔断、降级、流量隔离、备用Agent兜底策略（Agent高级）](../02-capabilities/multi-agent/communication-state.md#multi-005)
- [MULTI-006 · 多Agent主流两种架构：中心化调度、去中心化自治，分别讲实现方式、优缺点、适配什么业务场景（Agent中级）](../02-capabilities/multi-agent/selection-architecture.md#multi-006)
- [MULTI-007 · 对A2A架构是否了解；什么场景下单一Agent无法完成任务，需要引入多Agent协同处理（Agent初级）](../02-capabilities/multi-agent/selection-architecture.md#multi-007)
- [MULTI-008 · 大规模多Agent集群架构：中心化管控、联邦式协同、去中心化自治三种架构的取舍、优缺点、适配业务场景（Agent高级）](../02-capabilities/multi-agent/selection-architecture.md#multi-008)

## RAG

- [RAG-001 · RAG为什么需要混合检索？（豆包一面）](../02-capabilities/rag/embedding-vector-1.md#rag-001)
- [RAG-002 · 混合检索怎么优化？（豆包一面）](../02-capabilities/rag/embedding-vector-1.md#rag-002)
- [RAG-003 · RAG系统为什么需要同时使用稀疏检索和稠密检索？生产环境中如何调整两路召回权重？（腾讯一面）](../02-capabilities/rag/embedding-vector-1.md#rag-003)
- [RAG-004 · 稠密向量和稀疏向量有什么区别？（千问一面）](../02-capabilities/rag/embedding-vector-1.md#rag-004)
- [RAG-005 · 向量数据库的性能怎么优化？（豆包一面）](../02-capabilities/rag/embedding-vector-1.md#rag-005)
- [RAG-006 · 数据量上来以后，向量检索变慢怎么办？（豆包一面）](../02-capabilities/rag/embedding-vector-1.md#rag-006)
- [RAG-007 · 文档频繁更新时RAG如何实现增量索引避免每次都进行全量切片和向量化？（腾讯一面）](../02-capabilities/rag/ingestion-chunking.md#rag-007)
- [RAG-008 · RAG检索结果更新不及时，用户仍然搜到旧内容，应该如何定位和解决？（腾讯一面）](../02-capabilities/rag/retrieval-1.md#rag-008)
- [RAG-009 · 文档更新后如何实现增量索引？（千问一面）](../02-capabilities/rag/ingestion-chunking.md#rag-009)
- [RAG-010 · 业务知识库频繁新增、修改、删除文档，向量库增量更新架构如何设计，避免全量重向量化（Agent中级）](../02-capabilities/rag/ingestion-chunking.md#rag-010)
- [RAG-011 · 如何评估一个RAG系统的效果？检索环节和生成环节分别需要关注哪些指标？（腾讯一面）](../02-capabilities/rag/retrieval-1.md#rag-011)
- [RAG-012 · 为什么长文档需要切片后再向量化？（千问一面）](../02-capabilities/rag/ingestion-chunking.md#rag-012)

## 模型能力与成本

- [MODEL-001 · 模型API异常如何熔断和切换？（豆包二面）](../03-production/model-capability-cost/routing-fallback.md#model-001)
- [MODEL-002 · 多模型调度策略怎么设计？（豆包二面）](../03-production/model-capability-cost/routing-fallback.md#model-002)
- [MODEL-003 · 小模型和大模型如何分工？（豆包二面）](../03-production/model-capability-cost/cost-token.md#model-003)
- [MODEL-004 · Prompt Cache 如何设计？](../03-production/model-capability-cost/cache.md#model-004)
- [MODEL-005 · 如何降低 Token 消耗？](../03-production/model-capability-cost/cost-token.md#model-005)
- [MODEL-006 · Reflection会增加多少Token成本？](../03-production/model-capability-cost/cost-token.md#model-006)
- [MODEL-007 · 如何控制反思带来的延迟？](../03-production/model-capability-cost/streaming-capacity.md#model-007)
- [MODEL-008 · 什么场景适合关闭Reflection？](../03-production/model-capability-cost/cost-token.md#model-008)

## 安全、治理与可观测性

- [GOV-001 · 如果检测到用户存在极端情绪，Agent如何进行干预？（千问一面）](../03-production/safety-governance-observability/prompt-security.md#gov-001)
- [GOV-002 · 大模型幻觉产生的底层原因，以及基础层面可行的优化手段（Agent初级）](../03-production/safety-governance-observability/hallucination.md#gov-002)
- [GOV-003 · 模型产生幻觉的原因是什么？工程上有什么办法降低幻觉？（百度Agent）](../03-production/safety-governance-observability/hallucination.md#gov-003)
- [GOV-004 · 如何减少RAG幻觉问题？（千问一面）](../03-production/safety-governance-observability/hallucination.md#gov-004)
- [GOV-005 · 大模型幻觉系统性治理：检索校验、结果事实核验、反思校验、多轮自我修正、规则拦截多层防护（Agent高级）](../03-production/safety-governance-observability/hallucination.md#gov-005)
- [GOV-006 · 在Agent工具调用场景下，大模型幻觉有哪些典型表现，对应的落地优化手段（Agent高级）](../03-production/safety-governance-observability/hallucination.md#gov-006)
- [GOV-007 · Agent执行过程如何追踪？（豆包二面）](../03-production/safety-governance-observability/observability.md#gov-007)
- [GOV-008 · Agent执行过程如何实现全链路追踪？如何推荐模型，Prompt，知识库及工具调用和任务状态？（腾讯一面）](../03-production/safety-governance-observability/observability.md#gov-008)
- [GOV-009 · 全链路可观测平台：Agent每一步规划、工具调用、模型输入输出、耗时、报错全链路埋点（Agent高级）](../03-production/safety-governance-observability/observability.md#gov-009)
- [GOV-010 · 任务如何回放、打断、人工干预？（豆包二面）](../03-production/safety-governance-observability/observability.md#gov-010)

## 工程落地与平台化

- [ENG-001 · Prompt如何评估和优化？（豆包一面）](../03-production/engineering-platform/promptops.md#eng-001)
- [ENG-002 · 代码Agent项目的提示词模板是怎么设计和迭代的（百度Agent）](../03-production/engineering-platform/promptops.md#eng-002)
- [ENG-003 · System Prompt为什么比User Prompt权限更高？（百度Agent）](../03-production/engineering-platform/promptops.md#eng-003)
- [ENG-004 · 怎么判断一个提示词模板是真的更好了？有没有量化的评估标准？（百度Agent）](../03-production/engineering-platform/promptops.md#eng-004)
- [ENG-005 · 如果企业项目有几十万行代码，Coding Agent如何快速定位和理解相关代码上下文？（DeepSeek一面）](../03-production/engineering-platform/coding-agent.md#eng-005)
- [ENG-006 · 做代码理解的时候，AST、调用关系这些信息是怎么用起来的？（百度Agent）](../03-production/engineering-platform/code-search.md#eng-006)
- [ENG-007 · 代码上下文检索系统应该怎么设计？如何结合向量检索、关键词检索、AST分析和调用链分析？（DeepSeek一面）](../03-production/engineering-platform/code-search.md#eng-007)
- [ENG-008 · 单测生成里，哪些代码不适合生成单测？怎么识别并过滤？（百度Agent）](../03-production/engineering-platform/code-search.md#eng-008)

## OpenClaw

- [OCLAW-001 · OpenClaw 的产品定位是什么？它与普通聊天机器人有什么区别？](../04-products/openclaw/architecture-runtime.md#oclaw-001)
- [OCLAW-002 · OpenClaw Gateway 在整体架构中承担什么职责？](../04-products/openclaw/architecture-runtime.md#oclaw-002)

## Claude Code

- [CC-001 · Claude Code 的产品定位是什么？它与 IDE 补全工具有什么区别？](../04-products/claude-code/agent-loop.md#cc-001)
- [CC-002 · Claude Code 的 Agent Loop 是如何工作的？](../04-products/claude-code/agent-loop.md#cc-002)

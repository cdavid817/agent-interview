# 稳定 ID 合并映射

> 重复题合并后，旧 ID 永不复用。原题目位置保留跳转锚点，本表提供长期迁移记录。

| 旧 ID | 主问题 |
|---|---|
| `ARC-032` | [CTX-191 · 如何控制Context Window和Token成本？](../02-capabilities/context-knowledge/compression-cache.md#ctx-191) |
| `ARC-037` | [CTX-032 · 长期记忆如何存储、召回和更新？](../02-capabilities/context-knowledge/memory-1.md#ctx-032) |
| `ARC-041` | [GOV-024 · 如何降低Agent幻觉和错误调用工具的问题？](../03-production/safety-governance-observability/hallucination.md#gov-024) |
| `ARC-071` | [MODEL-101 · 如何控制大模型调用成本？](../03-production/model-capability-cost/cost-token.md#model-101) |
| `ARC-081` | [TOOL-110 · 工具调用失败时如何重试和降级？](../02-capabilities/tools-skills-mcp/reliability.md#tool-110) |
| `ARC-082` | [CTX-033 · 记忆层如何避免信息污染？](../02-capabilities/context-knowledge/memory-1.md#ctx-033) |
| `ARC-086` | [TOOL-111 · 如何保证工具调用的安全性？](../02-capabilities/tools-skills-mcp/sandbox-security-1.md#tool-111) |
| `CC-069` | [MULTI-033 · 多Agent并发修改同一文件时如何解决冲突？](../02-capabilities/multi-agent/conflict-reliability.md#multi-033) |
| `CTX-059` | [CTX-139 · 如何评估记忆召回效果？](../02-capabilities/context-knowledge/memory-3.md#ctx-139) |
| `CTX-110` | [CTX-085 · 向量检索和关键词检索如何结合？](../02-capabilities/context-knowledge/knowledge-retrieval.md#ctx-085) |
| `CTX-136` | [CTX-085 · 向量检索和关键词检索如何结合？](../02-capabilities/context-knowledge/knowledge-retrieval.md#ctx-085) |
| `CTX-138` | [TOOL-218 · Rerank模型如何设计？](../02-capabilities/tools-skills-mcp/tool-platform.md#tool-218) |
| `CTX-148` | [CTX-031 · Memory Service应该独立部署吗？](../02-capabilities/context-knowledge/memory-1.md#ctx-031) |
| `CTX-167` | [CTX-206 · Context Compression 如何实现？](../02-capabilities/context-knowledge/compression-cache.md#ctx-206) |
| `CTX-187` | [MODEL-004 · Prompt Cache 如何设计？](../03-production/model-capability-cost/cache.md#model-004) |
| `CTX-188` | [MODEL-118 · Semantic Cache如何设计？](../03-production/model-capability-cost/cache.md#model-118) |
| `CTX-201` | [PLAN-125 · Agent如何决定是否调用工具？](../02-capabilities/planning-execution/recovery-1.md#plan-125) |
| `ENG-044` | [GOV-126 · Prompt评测体系如何搭建？](../03-production/safety-governance-observability/evaluation.md#gov-126) |
| `ENG-045` | [GOV-127 · Prompt AB Test如何实施？](../03-production/safety-governance-observability/evaluation.md#gov-127) |
| `ENG-131` | [TOOL-112 · Tool Calling与MCP协议有什么区别？](../02-capabilities/tools-skills-mcp/mcp.md#tool-112) |
| `ENG-161` | [ARC-050 · 多模型路由策略如何设计？](../01-foundations/agent-architecture/architecture.md#arc-050) |
| `ENG-190` | [GOV-023 · 幻觉率如何量化评估？](../03-production/safety-governance-observability/hallucination.md#gov-023) |
| `GOV-042` | [MULTI-032 · 多Agent协同时如何实现链路关联？](../02-capabilities/multi-agent/multi-agent-basics.md#multi-032) |
| `GOV-050` | [TOOL-113 · 工具调用失败如何自动恢复？](../02-capabilities/tools-skills-mcp/sandbox-security-1.md#tool-113) |
| `GOV-051` | [TOOL-114 · 工具超时如何处理？](../02-capabilities/tools-skills-mcp/reliability.md#tool-114) |
| `GOV-052` | [TOOL-115 · Tool参数生成错误如何治理？](../02-capabilities/tools-skills-mcp/sandbox-security-1.md#tool-115) |
| `GOV-053` | [TOOL-116 · 如何评估工具调用质量？](../02-capabilities/tools-skills-mcp/tool-platform.md#tool-116) |
| `GOV-054` | [TOOL-117 · MCP与Tool Calling如何融合？](../02-capabilities/tools-skills-mcp/mcp.md#tool-117) |
| `GOV-128` | [ENG-046 · 如何量化评估Prompt优化效果？](../03-production/engineering-platform/promptops.md#eng-046) |
| `GOV-133` | [TOOL-113 · 工具调用失败如何自动恢复？](../02-capabilities/tools-skills-mcp/sandbox-security-1.md#tool-113) |
| `GOV-143` | [MODEL-012 · 如何利用LLM-as-a-Judge进行失败归因？](../03-production/model-capability-cost/evaluation.md#model-012) |
| `GOV-144` | [MULTI-034 · 多Agent系统如何进行链路追踪？](../02-capabilities/multi-agent/multi-agent-basics.md#multi-034) |
| `GOV-152` | [TOOL-056 · Agent如何判断一个工具是否属于高风险工具？](../02-capabilities/tools-skills-mcp/sandbox-security-1.md#tool-056) |
| `GOV-153` | [TOOL-057 · 如何设计Tool的权限模型？](../02-capabilities/tools-skills-mcp/sandbox-security-1.md#tool-057) |
| `GOV-154` | [TOOL-058 · RBAC与ABAC分别适用于哪些场景？](../02-capabilities/tools-skills-mcp/sandbox-security-1.md#tool-058) |
| `GOV-156` | [TOOL-060 · Risk Score应该包含哪些评估维度？](../02-capabilities/tools-skills-mcp/tool-platform.md#tool-060) |
| `GOV-157` | [TOOL-061 · 风险评分如何影响Agent的执行策略？](../02-capabilities/tools-skills-mcp/sandbox-security-1.md#tool-061) |
| `GOV-158` | [TOOL-062 · Human-in-the-Loop应该在哪些场景下介入？](../02-capabilities/tools-skills-mcp/sandbox-security-1.md#tool-062) |
| `GOV-159` | [TOOL-063 · 如何避免Agent误删代码或误删文件？](../02-capabilities/tools-skills-mcp/sandbox-security-1.md#tool-063) |
| `GOV-161` | [TOOL-065 · 如何防止Prompt Injection诱导Agent执行恶意工具？](../02-capabilities/tools-skills-mcp/sandbox-security-1.md#tool-065) |
| `GOV-162` | [TOOL-066 · MCP工具调用过程中如何进行权限校验？](../02-capabilities/tools-skills-mcp/mcp.md#tool-066) |
| `GOV-163` | [TOOL-067 · Tool调用前、中、后分别需要做哪些安全检查？](../02-capabilities/tools-skills-mcp/sandbox-security-1.md#tool-067) |
| `GOV-164` | [TOOL-068 · Agent如何实现命令沙箱隔离？](../02-capabilities/tools-skills-mcp/sandbox-security-1.md#tool-068) |
| `GOV-166` | [TOOL-070 · Git Push为什么通常需要审批？](../02-capabilities/tools-skills-mcp/sandbox-security-1.md#tool-070) |
| `GOV-167` | [TOOL-071 · 如何防止Agent直接向主分支提交代码？](../02-capabilities/tools-skills-mcp/sandbox-security-1.md#tool-071) |
| `GOV-169` | [TOOL-073 · Agent如何支持灰度发布和自动回滚？](../02-capabilities/tools-skills-mcp/reliability.md#tool-073) |
| `GOV-170` | [TOOL-074 · Agent执行失败后如何恢复现场？](../02-capabilities/tools-skills-mcp/reliability.md#tool-074) |
| `GOV-171` | [TOOL-075 · 如何设计完整的Tool Audit Log？](../02-capabilities/tools-skills-mcp/reliability.md#tool-075) |
| `GOV-172` | [TOOL-076 · Trace ID如何贯穿整个Agent执行链路？](../02-capabilities/tools-skills-mcp/tool-platform.md#tool-076) |
| `GOV-174` | [TOOL-078 · 如何设计统一的Policy Engine管理所有工具权限？](../02-capabilities/tools-skills-mcp/sandbox-security-1.md#tool-078) |
| `GOV-176` | [TOOL-080 · 如何防止多个Agent同时操作同一资源导致冲突？](../02-capabilities/tools-skills-mcp/reliability.md#tool-080) |
| `GOV-177` | [TOOL-081 · Agent如何保证工具调用的幂等性？](../02-capabilities/tools-skills-mcp/reliability.md#tool-081) |
| `GOV-179` | [TOOL-083 · Agent执行数据库DDL或DML操作应有哪些额外保护机制？](../02-capabilities/tools-skills-mcp/sandbox-security-1.md#tool-083) |
| `GOV-180` | [TOOL-084 · 如何平衡Agent自动化效率与人工审批带来的成本？](../02-capabilities/tools-skills-mcp/sandbox-security-1.md#tool-084) |
| `MODEL-011` | [GOV-142 · 如何设计Agent自动反思与自修复机制？](../03-production/safety-governance-observability/governance.md#gov-142) |
| `MODEL-025` | [MODEL-118 · Semantic Cache如何设计？](../03-production/model-capability-cost/cache.md#model-118) |
| `MODEL-026` | [MODEL-119 · RAG与大上下文模型如何取舍？](../03-production/model-capability-cost/cost-token.md#model-119) |
| `MODEL-039` | [MODEL-124 · 多模型环境下如何进行统一评测？](../03-production/model-capability-cost/routing-fallback.md#model-124) |
| `MODEL-041` | [MODEL-126 · 如果预算固定，如何设计最优模型资源分配策略？](../03-production/model-capability-cost/cost-token.md#model-126) |
| `MODEL-043` | [MODEL-128 · 如何构建自动化模型路由闭环优化系统？](../03-production/model-capability-cost/routing-fallback.md#model-128) |
| `MODEL-044` | [MODEL-129 · 开源模型与商业模型混合部署如何设计？](../03-production/model-capability-cost/model-engineering.md#model-129) |
| `MODEL-047` | [MODEL-099 · 如何处理模型调用失败和超时？](../03-production/model-capability-cost/routing-fallback.md#model-099) |
| `MODEL-048` | [MODEL-100 · 如何评估不同模型的能力画像？](../03-production/model-capability-cost/cost-token.md#model-100) |
| `MODEL-049` | [MODEL-101 · 如何控制大模型调用成本？](../03-production/model-capability-cost/cost-token.md#model-101) |
| `MODEL-050` | [MODEL-102 · 敏感数据如何保证不被发送到外部模型？](../03-production/model-capability-cost/cost-token.md#model-102) |
| `MODEL-051` | [MODEL-103 · 如何设计模型降级和兜底策略？](../03-production/model-capability-cost/routing-fallback.md#model-103) |
| `MODEL-052` | [MODEL-104 · 如何支持多厂商模型统一接入？](../03-production/model-capability-cost/routing-fallback.md#model-104) |
| `MODEL-053` | [MODEL-105 · 如何做模型效果的A/B实验？](../03-production/model-capability-cost/evaluation.md#model-105) |
| `MODEL-074` | [CTX-195 · 长对话场景如何进行上下文压缩？](../02-capabilities/context-knowledge/compression-cache.md#ctx-195) |
| `MODEL-098` | [MODEL-014 · 模型路由策略是规则驱动还是模型驱动？](../03-production/model-capability-cost/routing-fallback.md#model-014) |
| `MODEL-106` | [MODEL-054 · 如何记录一次请求为什么选择了某个模型？](../03-production/model-capability-cost/cost-token.md#model-054) |
| `MODEL-107` | [MODEL-055 · 多模型路由策略具体如何设计？规则路由和LLM路由如何选择？](../03-production/model-capability-cost/routing-fallback.md#model-055) |
| `MODEL-108` | [MODEL-015 · 如何自动判断一个任务的复杂度等级？](../03-production/model-capability-cost/cost-token.md#model-015) |
| `MODEL-109` | [MODEL-016 · 模型路由层如何实现实时决策？](../03-production/model-capability-cost/routing-fallback.md#model-016) |
| `MODEL-110` | [MODEL-017 · 如何设计模型能力评估体系？](../03-production/model-capability-cost/evaluation.md#model-017) |
| `MODEL-111` | [MODEL-018 · 小模型升级到大模型的触发条件有哪些？](../03-production/model-capability-cost/routing-fallback.md#model-018) |
| `MODEL-112` | [MODEL-019 · 如何衡量模型升级带来的ROI？](../03-production/model-capability-cost/cost-token.md#model-019) |
| `MODEL-113` | [MODEL-020 · 如何设计模型降级和熔断机制？](../03-production/model-capability-cost/routing-fallback.md#model-020) |
| `MODEL-114` | [MODEL-021 · 模型故障时如何实现无感切换？](../03-production/model-capability-cost/routing-fallback.md#model-021) |
| `MODEL-115` | [MODEL-022 · 如何避免模型频繁升级导致成本失控？](../03-production/model-capability-cost/cost-token.md#model-022) |
| `MODEL-116` | [MODEL-023 · Prompt压缩有哪些常见方案？](../03-production/model-capability-cost/cache.md#model-023) |
| `MODEL-117` | [MODEL-024 · Context裁剪如何避免关键信息丢失？](../03-production/model-capability-cost/cost-token.md#model-024) |
| `MODEL-120` | [MODEL-027 · 如何建立模型质量评分体系？](../03-production/model-capability-cost/evaluation.md#model-027) |
| `MODEL-121` | [MODEL-028 · 如何实现在线A/B测试与灰度发布？](../03-production/model-capability-cost/evaluation.md#model-028) |
| `MODEL-122` | [MODEL-029 · 企业级模型网关需要具备哪些能力？](../03-production/model-capability-cost/routing-fallback.md#model-029) |
| `MODEL-123` | [MODEL-038 · 如何统计单个Agent任务的真实成本？](../03-production/model-capability-cost/cost-token.md#model-038) |
| `MODEL-125` | [MODEL-040 · 如何实现质量、时延、成本三目标优化？](../03-production/model-capability-cost/cost-token.md#model-040) |
| `MODEL-127` | [MODEL-042 · 千万级用户场景下如何进行模型容量规划？](../03-production/model-capability-cost/cache.md#model-042) |
| `MODEL-130` | [MODEL-045 · MCP、Tool Calling、Agent场景下如何进行模型路由？](../03-production/model-capability-cost/routing-fallback.md#model-045) |
| `MODEL-131` | [MODEL-046 · 如何设计企业级统一模型接入层（Model Gateway）？](../03-production/model-capability-cost/routing-fallback.md#model-046) |
| `PLAN-036` | [PLAN-264 · Checkpoint 如何设计？](../02-capabilities/planning-execution/recovery-3.md#plan-264) |
| `PLAN-070` | [PLAN-098 · Agent如何判断一个任务是否需要拆解？](../02-capabilities/planning-execution/task-routing.md#plan-098) |
| `PLAN-128` | [TOOL-048 · MCP与Function Calling有什么区别？](../02-capabilities/tools-skills-mcp/mcp.md#tool-048) |
| `PLAN-175` | [PLAN-116 · 企业级Agent如何实现可观测性（Observability）？](../02-capabilities/planning-execution/planning.md#plan-116) |
| `PLAN-205` | [PLAN-024 · ReAct 与 Plan-and-Execute 有什么区别？](../02-capabilities/planning-execution/reasoning-patterns.md#plan-024) |
| `PLAN-206` | [PLAN-098 · Agent如何判断一个任务是否需要拆解？](../02-capabilities/planning-execution/task-routing.md#plan-098) |
| `PLAN-225` | [TOOL-176 · 什么样的任务适合沉淀为 Skill？](../02-capabilities/tools-skills-mcp/skill-workflows.md#tool-176) |
| `PLAN-258` | [PLAN-153 · 如何设计Agent的状态机？](../02-capabilities/planning-execution/workflow.md#plan-153) |
| `RAG-078` | [RAG-051 · Rerank模型如何训练？](../02-capabilities/rag/reranking.md#rag-051) |
| `RAG-110` | [RAG-077 · Cross Encoder和Bi Encoder有什么区别？](../02-capabilities/rag/retrieval-1.md#rag-077) |
| `TOOL-012` | [TOOL-006 · Agent生成SQL、代码或Shell命令时如何设计沙箱，了解如何确认机制？（腾讯一面）](../02-capabilities/tools-skills-mcp/sandbox-security-1.md#tool-006) |
| `TOOL-014` | [TOOL-048 · MCP与Function Calling有什么区别？](../02-capabilities/tools-skills-mcp/mcp.md#tool-048) |
| `TOOL-059` | [GOV-155 · 为什么企业级Agent通常采用最小权限原则？](../03-production/safety-governance-observability/prompt-security.md#gov-155) |
| `TOOL-064` | [GOV-160 · 如何限制Agent执行危险Shell命令？](../03-production/safety-governance-observability/governance.md#gov-160) |
| `TOOL-069` | [GOV-165 · 如何保证Agent只能修改指定目录？](../03-production/safety-governance-observability/governance.md#gov-165) |
| `TOOL-072` | [GOV-168 · 如何设计Agent的部署发布权限？](../03-production/safety-governance-observability/access-privacy.md#gov-168) |
| `TOOL-077` | [GOV-173 · 企业级Agent如何满足安全合规要求？](../03-production/safety-governance-observability/access-privacy.md#gov-173) |
| `TOOL-079` | [GOV-175 · 如何实现动态授权和临时权限提升？](../03-production/safety-governance-observability/access-privacy.md#gov-175) |
| `TOOL-082` | [GOV-178 · 如何设计Agent的多租户权限隔离？](../03-production/safety-governance-observability/access-privacy.md#gov-178) |
| `TOOL-085` | [GOV-181 · 企业级Agent权限体系如何与企业现有IAM、SSO和审批流程集成？](../03-production/safety-governance-observability/access-privacy.md#gov-181) |
| `TOOL-128` | [TOOL-149 · Skill和Tool有什么区别？](../02-capabilities/tools-skills-mcp/skill-workflows.md#tool-149) |
| `TOOL-148` | [TOOL-176 · 什么样的任务适合沉淀为 Skill？](../02-capabilities/tools-skills-mcp/skill-workflows.md#tool-176) |
| `TOOL-161` | [TOOL-150 · Skill如何进行版本管理？](../02-capabilities/tools-skills-mcp/skill-governance-1.md#tool-150) |
| `TOOL-182` | [TOOL-213 · Code Review Skill如何设计？](../02-capabilities/tools-skills-mcp/skill-routing.md#tool-213) |
| `TOOL-214` | [TOOL-183 · Bug Fix Skill 如何设计？](../02-capabilities/tools-skills-mcp/skill-governance-1.md#tool-183) |
| `RAG-046` | [RAG-073 · 如何评估Embedding模型质量？](../02-capabilities/rag/embedding-vector-1.md#rag-073) |
| `TOOL-173` | [PLAN-265 · Workflow 如何断点续跑？](../02-capabilities/planning-execution/recovery-3.md#plan-265) |
| `MODEL-083` | [MODEL-013 · 如何判断一个任务应该走大模型还是小模型？](../03-production/model-capability-cost/cost-token.md#model-013) |

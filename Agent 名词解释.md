# Agent 名词解释

> 本文件保留在面试题「相关知识点」中至少出现 **5** 次的术语，并补充 Agent 领域核心术语；共 **677** 个去重术语，按 12 个主题分类。
>
> 当前覆盖 `docs/` 下 **12** 个章节、**1727** 处「相关知识点」。筛选规则由 `scripts/glossary_core_terms.txt` 与最小出现次数共同维护。

## 一、架构设计类

1. 多租户
2. 控制面
3. 冷热分层
4. 事件驱动
5. A2A
6. Adapter
7. Agent
8. Agent Harness
9. Agent Loop
10. Agent Runtime
11. AGENTS.md
12. Artifact
13. Artifact Store
14. AutoGen
15. Capability
16. Claude Code
17. CrewAI
18. Gateway
19. LangGraph
20. Namespace
21. OpenClaw
22. Runtime
23. Semantic Kernel
24. Semantic Versioning
25. Session
26. Session State
27. Workspace

## 二、任务规划与编排类

1. 并行调度
2. 补偿
3. 持久化状态机
4. 冲突检测
5. 冲突消解
6. 单位成功任务成本
7. 动态重规划
8. 断点续跑
9. 对账
10. 反思预算
11. 反向依赖
12. 根因分析
13. 公平调度
14. 关键路径
15. 哈希链
16. 环检测
17. 混淆矩阵
18. 计划版本
19. 检查点
20. 结构化并发
21. 结果聚合
22. 局部重规划
23. 局部Replan
24. 幂等消费
25. 命名空间
26. 目标反推
27. 能力编排
28. 能力路由
29. 能力契约
30. 能力协商
31. 能力注册表
32. 批处理
33. 任务分解
34. 任务粒度
35. 任务契约
36. 任务DAG
37. 容量规划
38. 事件溯源
39. 事务发件箱
40. 输入输出契约
41. 数据漂移
42. 数据血缘
43. 拓扑排序
44. 停止条件
45. 唯一约束
46. 委派预算
47. 心跳
48. 循环检测
49. 业务不变量
50. 依赖图
51. 异步队列
52. 意图识别
53. 有限状态机
54. 职责分离
55. 指代消解
56. 至少一次投递
57. 终止条件
58. 重排
59. 重试放大
60. 重试风暴
61. 重试预算
62. 状态机
63. 状态迁移
64. 自我修正
65. 租约
66. Attempt
67. Attempt ID
68. Audit
69. Backpressure
70. CAS
71. Checkpoint
72. Circuit Breaker
73. Critic
74. DAG
75. DLQ
76. Dry Run
77. Event
78. Exponential Backoff
79. Fail Closed
80. fencing
81. HITL
82. Inbox
83. Jitter
84. JSON-RPC
85. Lease
86. Metadata Filter
87. Multi-Agent
88. MVCC
89. Observability
90. Orchestrator
91. Plan Validator
92. Planner
93. ReAct
94. Ready Queue
95. Reflection
96. Repair
97. Replan
98. RePlanner
99. Retry
100. Retry Budget
101. Retry-After
102. Rollback
103. RPM
104. RPO
105. RTO
106. Saga
107. Saga补偿
108. Sequence
109. SSE
110. State Machine
111. Subagent
112. Success Criteria
113. Supervisor
114. Task Decomposition
115. Task ID
116. Task Spec
117. Task State
118. TaskID
119. TOCTOU
120. TPM
121. TPS
122. Transactional Outbox
123. TTFT
124. Worker租约
125. Workflow
126. WORM

## 三、模型调用与路由类

1. 部分结果
2. 动态Batch
3. 对比学习
4. 滑动窗口
5. 级联推理
6. 结构化状态
7. 模型级联
8. 模型路由
9. 默认拒绝
10. 能力画像
11. 数据分级
12. 预算传播
13. 蒸馏
14. 知识蒸馏
15. ASR
16. Attention
17. Cancellation Token
18. Capability Token
19. Causal Mask
20. Cross-Attention
21. Decode
22. DPO
23. Early Exit
24. Fallback
25. fencing token
26. FinOps
27. FlashAttention
28. GQA
29. KV Cache
30. KV量化
31. LLM
32. Load Shedding
33. LoRA
34. Model Gateway
35. Model Router
36. MQA
37. N+1
38. NLI
39. OCR
40. PagedAttention
41. Prefill
42. Prefix Cache
43. Quantization
44. RLHF
45. RoPE
46. Self-Attention
47. Semantic Cache
48. Softmax
49. Sparse Attention
50. Temperature
51. Token
52. Token预算
53. Tokenizer
54. Top-p
55. Transformer

## 四、Prompt 工程类

1. 层级摘要
2. 抽取式压缩
3. 分层摘要
4. 滚动摘要
5. 渐进式上下文
6. 结构化摘要
7. 上下文窗口
8. 上下文污染
9. 上下文压缩
10. 摘要漂移
11. 指令优先级
12. 最小充分上下文
13. Compaction
14. Context Builder
15. Context Engineering
16. Context Pollution
17. Context Precision
18. Context Propagation
19. Context Window
20. Contextual Compression
21. Few-shot
22. Lost in the Middle
23. Prompt
24. Prompt Builder
25. Prompt Cache
26. Prompt Engineering
27. Prompt Registry
28. Structured Output
29. System Prompt
30. Token Budget
31. Zero-shot

## 五、RAG 与知识库类

1. 版本回滚
2. 版本链
3. 查询路由
4. 代码检索
5. 倒排索引
6. 动态Top-K
7. 动态Top-N
8. 分布外检测
9. 分数校准
10. 符号索引
11. 父子索引
12. 负迁移
13. 故障演练
14. 故障域
15. 候选配额
16. 混合检索
17. 困难负例
18. 邻接合并
19. 邻接扩展
20. 幂等Upsert
21. 墓碑
22. 墓碑删除
23. 数据新鲜度
24. 双索引
25. 索引版本
26. 索引对账
27. 稳定Chunk ID
28. 向量检索
29. 向量索引
30. 影子索引
31. 语义版本
32. 语义检索
33. 语义切块
34. 语义去重
35. 元数据过滤
36. 增量索引
37. 证据覆盖率
38. 证据集合覆盖率
39. 证据链
40. 证据密度
41. 证据驱动
42. 证据溯源
43. 证据完整率
44. 证据引用
45. 状态查询
46. 最小充分证据
47. Active Version
48. Bi-Encoder
49. BM25
50. CDC
51. Chunk Overlap
52. Chunking
53. Citation
54. Content Hash
55. Cross Encoder
56. Cross-encoder
57. Embedding
58. Faithfulness
59. GraphRAG
60. Grounding
61. Hallucination
62. Hard Negative
63. Hybrid Retrieval
64. Hybrid Search
65. IDF
66. Learning to Rank
67. Logs
68. MMR
69. MTTD
70. Progressive Retrieval
71. Provenance
72. Query Rewrite
73. RAG
74. Recall—Latency曲线
75. Recursive Chunking
76. Rerank
77. Reranker
78. Retrieval Router
79. Retriever
80. RRF
81. Semantic Chunking
82. Supersedes
83. Top-K
84. Top-N
85. Valid Time

## 六、向量数据库类

1. ANN
2. Chroma
3. DiskANN
4. efSearch
5. FAISS
6. HNSW
7. IVF
8. Milvus
9. nprobe
10. pgvector
11. Pinecone
12. PQ
13. Qdrant
14. Weaviate

## 七、记忆系统类

1. 工作记忆
2. 候选记忆
3. 记忆巩固
4. 记忆晋升
5. 记忆衰减
6. 曝光偏差
7. 情景记忆
8. 删除证明
9. 语义记忆
10. 长期记忆
11. Episodic Memory
12. Long-term Memory
13. Memory
14. Memory Compression
15. Memory Consolidation
16. Memory Reranker
17. Memory Retrieval
18. Memory Scoring
19. Memory Service
20. Rolling Summary
21. Semantic Memory
22. Short-term Memory
23. Source ID
24. Working Memory

## 八、工具调用类

1. 版本固定
2. 不可变制品
3. 参数绑定
4. 参数哈希
5. 策略即代码
6. 程序性知识
7. 调用图
8. 紧急撤销
9. 进展函数
10. 拒选机制
11. 一次成功成本
12. 制品签名
13. 专用度
14. ACP
15. Agent SDK
16. AST
17. At-Least-Once
18. Browser
19. Call Graph
20. capabilities
21. CFG
22. CHA
23. Chain-of-Thought
24. Change Impact Analysis
25. CLAUDE.md
26. CODEOWNERS
27. Computer Use
28. Durable Execution
29. Executor
30. Firecracker
31. Function Calling
32. Git Worktree
33. Hash Chain
34. Hook
35. Idempotency
36. Idempotency Key
37. JSON Schema
38. Last-Event-ID
39. Least Privilege
40. Lockfile
41. LSP
42. Margin
43. MCP
44. MCP Client
45. MCP Host
46. MCP Server
47. OpenAI Agents SDK
48. Owner机制
49. Plugin
50. Precision
51. Prompts
52. Recall
53. Resources
54. SAST
55. Schema
56. Schema校验
57. Schema演进
58. Shell
59. Shell AST
60. Skill
61. Skill Contract
62. Skill Registry
63. Skill Router
64. SQL AST
65. Symbol Index
66. Tool Calling
67. Tool Executor
68. Tool Registry
69. Tool Schema
70. Tool Selection
71. Tools
72. Worktree

## 九、安全与治理类

1. 版本治理
2. 成本治理
3. 短期令牌
4. 短期凭据
5. 多租户隔离
6. 供应链安全
7. 故障隔离
8. 故障注入
9. 红队测试
10. 令牌桶
11. 权限过滤
12. 权限交集
13. 权限校验
14. 沙箱
15. 上下文隔离
16. 审计
17. 审计日志
18. 审计追踪
19. 数据脱敏
20. 数据泄漏
21. 数据驻留
22. 数据最小化
23. 双人审批
24. 脱敏
25. 行级安全
26. 依赖注入
27. 指令数据隔离
28. 纵深防御
29. 租户隔离
30. 最小权限
31. ABAC
32. ACL
33. Allowlist
34. Branch Protection
35. Break-glass
36. CausationID
37. Code Owner
38. Cost/Success
39. DLP
40. Guardrail
41. Hard Deny
42. IAM
43. Jailbreak
44. JWT
45. KMS
46. Legal Hold
47. OAuth
48. PII
49. Policy
50. Policy Engine
51. Prompt Injection
52. RBAC
53. Retention Policy
54. Risk Score
55. Sandbox
56. SBOM
57. seccomp
58. Secret
59. SSO
60. Unknown State
61. Vault
62. Zero Trust

## 十、可观测性类

1. 版本水位
2. 成本监控
3. 错误预算
4. 错误指纹
5. 结构化日志
6. 可观测性
7. 全链路Trace
8. 尾延迟
9. Distributed Tracing
10. Event Log
11. Exemplar
12. Log
13. Metric
14. Metrics
15. OpenTelemetry
16. P95
17. P99
18. SLA
19. SLO
20. Span
21. Span Link
22. Tail Sampling
23. Trace
24. Trace Context
25. Trace ID
26. TraceID
27. W3C Trace Context

## 十一、评测体系类

1. 边际收益
2. 边置信度
3. 测试金字塔
4. 成本归因
5. 错误分类
6. 错误归因
7. 端到端评测
8. 多标签分类
9. 反事实评估
10. 分层评测
11. 护栏指标
12. 黄金集
13. 回归测试
14. 回归评测
15. 结果验证
16. 困难负样本
17. 难负样本
18. 配对评测
19. 契约测试
20. 任务完成率
21. 事实一致性
22. 消融实验
23. 效应量
24. 校准
25. 验证器
26. 质量门
27. 质量门禁
28. 置信度
29. 置信度校准
30. 置信门控
31. 置信区间
32. 置信校准
33. 最终一致性
34. A/B Test
35. A/B Testing
36. A/B测试
37. Acceptance Criteria
38. Accuracy
39. Benchmark
40. Burn Rate
41. Canary
42. ECE
43. F1
44. Failure Taxonomy
45. Flaky Test
46. Golden Dataset
47. Ground Truth
48. Judge校准
49. LLM Judge
50. LLM-as-a-Judge
51. MDE
52. MRR
53. Mutation Score
54. Mutation Testing
55. NDCG
56. Pareto前沿
57. Pareto最优
58. Pass@K
59. Precision@K
60. Precision@N
61. Rate Limiting
62. Recall@K
63. Repo Map
64. ROI
65. Rubric
66. Shadow
67. SRM

## 十二、工程稳定性类

1. 版本管理
2. 背压
3. 补偿事务
4. 单位成功成本
5. 动态路由
6. 动态权重
7. 短期凭证
8. 对象存储
9. 多重检验
10. 分布漂移
11. 分布式追踪
12. 风险分级
13. 规则引擎
14. 后置条件
15. 缓存键
16. 缓存失效
17. 灰度发布
18. 回收期
19. 降级
20. 静态分析
21. 来源追踪
22. 乐观锁
23. 路径规范化
24. 幂等
25. 幂等恢复
26. 幂等键
27. 幂等性
28. 内容哈希
29. 内容寻址
30. 能力发现
31. 配置快照
32. 取消传播
33. 去重
34. 人工接管
35. 容器
36. 熔断
37. 熔断降级
38. 熔断器
39. 审批
40. 失败聚类
41. 时间衰减
42. 数据污染
43. 死信队列
44. 随机抖动
45. 位置偏差
46. 稳定分桶
47. 稳定哈希
48. 信任边界
49. 信息增益
50. 业务终态
51. 影响分析
52. 硬约束
53. 预算控制
54. 原子切换
55. 早停
56. 增量更新
57. 指数退避
58. 主动学习
59. 注意力稀释
60. 状态未知
61. 资源配额
62. 自动回滚
63. 总拥有成本
64. 最小可检测效应
65. 作用域
66. Bandit
67. Bulkhead
68. Cache
69. Cohort
70. Commit SHA
71. Deadline
72. Dry-run
73. Event Sourcing
74. Feature Flag
75. Half-Open
76. Human-in-the-loop
77. MTTR
78. Observation
79. Outbox
80. Runbook
81. SingleFlight
82. Snapshot
83. TCO
84. TTL
85. Validator
86. Vector Search
87. Verifier

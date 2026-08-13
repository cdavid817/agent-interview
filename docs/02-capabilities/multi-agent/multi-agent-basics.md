# 多 Agent 基础

> 所属章节：[多 Agent 与协作](README.md)｜本文件共 **3** 题。

<a id="multi-029"></a>
### Orchestrator本身如果挂掉了，怎么保证整体任务不丢失？

Orchestrator应是**无状态或可重建控制器，权威状态持久化在外部存储**。高可用副本只能缩短恢复；任务与副作用若只在内存中，新实例仍无法续跑。

1. 接收任务时先把TaskID、输入、计划版本、状态和幂等键写入数据库，再确认。计划变更、回执和检查点用事件日志或WAL持久化，大载荷存对象存储。
2. 多副本通过Leader Election或分区所有权保证单一协调者。Leader持租约与Fencing Token写状态；切换后提升Token，拒绝旧Leader命令，防止脑裂。
3. Worker原子领取租约并以幂等键提交。新Leader扫描`Running`与过期租约：完成项复用，未知项先查状态，未执行项重派，禁止整任务重放。
4. 状态与事件使用Outbox，重复消息由消费幂等处理。非幂等副作用须有业务唯一键、查询接口或Saga补偿。
5. 定期演练备份、切换和日志回放，监控选主时延、重复执行与状态漂移，并明确RPO、RTO。

| 保障层 | 核心机制 | 目标 |
|---|---|---|
| 状态 | DB、WAL、检查点 | 可重建 |
| 控制面 | 多副本、选主、Fencing | 自动接管 |
| 执行 | 租约、幂等 | 不重复副作用 |
| 消息 | Outbox、重放 | 不丢事件 |

**相关知识点：** 高可用、Leader Election、WAL、检查点、租约、Fencing Token、脑裂、Outbox、幂等续跑、RPO、RTO。
<a id="multi-032"></a>
### 多Agent协同时如何实现链路关联？

链路关联采用**Trace传播、任务标识和异步因果建模**。TraceID描述一次调用链，TaskID覆盖长任务，MessageID识别消息，IdempotencyKey标识业务操作，四者不可混用。

1. 入口创建W3C Trace Context；Agent、LLM、Tool、评审和汇聚各建Span，并记录AgentID、TaskID、PlanVersion、状态与成本。
2. RPC通过Header传播；队列在消息属性中携带Trace Context、TaskID、MessageID和CorrelationID。生产与消费Span用Span Link表达异步因果。
3. 并行分支共享TraceID但使用独立SpanID，汇聚节点链接各上游；重试新建Span并指向原失败项。跨进程续跑可新建Trace，用TaskID或Link关联。
4. 日志注入TraceID、SpanID和TaskID，审计另记主体、权限与副作用。Prompt和结果保存脱敏摘要或受控引用。

| 标识 | 作用域 | 主要用途 |
|---|---|---|
| TraceID | 一次链路 | 性能与因果追踪 |
| TaskID | 业务任务全生命周期 | 续跑和跨Trace关联 |
| MessageID | 单条消息 | 重投识别 |
| IdempotencyKey | 一次业务操作 | 防重复副作用 |

**历史别名：** `GOV-042`。

**相关知识点：** W3C Trace Context、TraceID、SpanID、Span Link、TaskID、CorrelationID、异步追踪、尾部采样、孤儿Span。
<a id="multi-034"></a>
### 多Agent系统如何进行链路追踪？

多Agent链路追踪采用**OpenTelemetry、W3C上下文、语义Span和Collector**，还原规划、路由、执行、工具与汇聚的因果链，分析时延、错误和成本。

1. 入口创建Trace，各Agent、LLM、Tool、Critic和汇聚创建Span，记录TaskID、AgentID、PlanVersion、状态、Token、费用和重试；敏感全文不进标签。
2. HTTP/gRPC通过`traceparent`传播，队列通过消息属性传播；异步消费用Span Link。并行分支共享TraceID，重试新建Span并引用失败项。
3. 自动Instrumentation采集网络与数据库，Agent决策、Prompt版本和质量门禁自定义埋点；日志注入TraceID、SpanID，指标用Exemplar关联Trace。
4. Collector负责接收、脱敏、批处理和导出。正常链路采样，错误、高时延、高成本及高风险任务尾部保留；审计日志独立存储。

| 信号 | 回答的问题 | 主要用途 |
|---|---|---|
| Trace | 调用经过哪里 | 因果与性能分析 |
| Log | 具体发生什么 | 事件定位 |
| Metric | 是否系统性异常 | 告警与容量 |
| Audit | 谁执行了什么 | 合规追责 |

**历史别名：** `GOV-144`。

**相关知识点：** OpenTelemetry、Instrumentation、OTel Collector、W3C Trace Context、Span Link、Exemplar、尾部采样、Agent语义埋点。

# 协作效果与评测

> 所属章节：[多 Agent 与协作](README.md)｜本文件共 **1** 题。

<a id="multi-031"></a>
### MULTI-031 · 相比单体应用，Multi-Agent系统的可观测性（Observability）怎么设计？

> 稳定 ID：`MULTI-031`｜原题号：31

Multi-Agent可观测性要在**Logs、Metrics、Traces**上增加任务语义、模型决策、跨Agent因果和成本质量信号，既定位故障，也解释路由、停滞与结果依据。

1. Trace表示用户目标，Span覆盖规划、路由、Agent、LLM、Tool、评审和汇聚；TaskID用于续跑，MessageID关联异步消息。同步与队列均传播W3C Trace Context。
2. 日志记录事件、状态迁移、错误、候选路由和策略决策；Prompt与输出保存脱敏摘要、哈希或受控引用，并执行访问控制与保留期。
3. 指标覆盖资源与队列、P95与错误率、Token与重试、任务完成率和单位成功成本，并按模型、Agent版本、租户和任务类型切片。
4. 错误、高延迟、高成本和高风险Trace全量保留；保存计划、状态和证据版本支持回放，模型重放须固定版本并标注非确定性。
5. 告警关注停滞、重试放大、路由漂移、成本突增和严重误执行。

| 维度 | 单体应用 | Multi-Agent系统 |
|---|---|---|
| 关联范围 | 进程或服务调用 | Agent、消息、Tool和任务 |
| 核心信号 | 时延、错误、资源 | 增加决策、Token、质量 |
| 回放 | 请求与日志 | 计划、状态、证据版本 |

**相关知识点：** OpenTelemetry、W3C Trace Context、Trace、Span、TaskID、语义约定、尾部采样、成本归因、执行回放。

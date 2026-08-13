# 自动化与多 Agent

> 所属章节：[OpenClaw](README.md)｜本文件共 **2** 题。

<a id="oclaw-019"></a>
### 1. OpenClaw 中 Cron、Heartbeat、Hooks 和 Task Flow 应如何选型？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

它们对应不同触发和编排语义。

| 机制 | 适用场景 | 关键特点 |
|---|---|---|
| Cron/Automation | 固定时间或一次性调度 | 可创建隔离Run并交付 |
| Heartbeat | 周期检查个人主会话 | 合并轻量检查，避免刷屏 |
| Hook/Webhook | 生命周期或外部事件 | 事件驱动、低等待 |
| Task Flow | 多步骤后台编排 | 显式阶段、任务与交接 |

强事务、补偿和跨系统Exactly-once仍应由专业工作流系统承担。选择依据是触发方式、状态持久性、失败恢复和交付SLA，而非都用Cron模拟。

**相关知识点：** Scheduler、Heartbeat、Event Hook、Webhook、Task Flow、Durable Workflow。
<a id="oclaw-037"></a>
### 2. OpenClaw 如何实现多 Agent 协作？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

**【核心思路】**
OpenClaw有两类机制：配置多个Agent并用Bindings把渠道、账号或对话路由到指定Agent；以及由当前Run通过`sessions_spawn`启动后台子Agent。每个配置Agent有自己的工作区、Agent目录和会话存储，子Agent则在独立会话运行并向请求方回报。

子Agent默认不复制完整主会话，也不拥有全部会话/消息工具；权限还受Profile、Tool Policy和Sandbox限制。它们适合研究、慢任务和弱依赖并行，不应默认并发写同一资源。

**验证指标：** 任务完成率、工具调用成功率、P95 延迟、Token 消耗和人工接管率。

**相关知识点：** OpenClaw、Multi-Agent、权限控制、Sandbox、任务调度。

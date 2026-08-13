# Subagents 与 Agent Teams

> 所属章节：[Claude Code](README.md)｜本文件共 **1** 题。

<a id="cc-018"></a>
### 1. Subagents、Agent Teams 和 Agent View 有什么区别？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

Subagent是主Session内部的任务委派；Agent Teams让多个Claude Code实例围绕共享任务、消息和协调机制协作；Agent View是从一个界面派发和监控多个Session的管理Surface。

| 机制 | 协作关系 | 适用场景 |
|---|---|---|
| Subagent | 主从、结果回传 | 有边界的研究与Review |
| Agent Teams | 多实例协作 | 大型并行任务与角色分工 |
| Agent View | 人管理多个Session | 多仓库或多任务运营 |

并行度不是越高越好。共享依赖、同文件修改和不清晰验收会放大冲突与成本。

**相关知识点：** Agent Teams、Agent View、Shared Task、Inter-agent Messaging、Orchestration。

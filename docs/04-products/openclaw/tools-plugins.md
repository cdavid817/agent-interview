# 工具、Skills 与 Plugins

> 所属章节：[OpenClaw](README.md)｜本文件共 **8** 题。

<a id="oclaw-009"></a>
### 1. OpenClaw 中 Tools、Skills 和 Plugins 的边界是什么？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

三者分别解决**行动、方法和扩展载体**。

| 机制 | 核心作用 | 典型内容 |
|---|---|---|
| Tool | 可调用的结构化动作 | 读写文件、浏览器、消息、节点 |
| Skill | 教Agent何时及如何完成工作 | `SKILL.md`、流程、规范、脚本 |
| Plugin | 向Runtime注册新能力 | Tool、Provider、Channel、Hook、Skill |

Skill不会天然新增底层权限，Plugin也不应绕过Tool Policy。第三方Skill和Plugin都属于供应链输入，应审查来源、安装脚本、依赖、Secret使用和升级变化。

**验证指标：** 任务完成率、工具调用成功率、P95 延迟、Token 消耗和人工接管率。

**相关知识点：** Tool Schema、Agent Skills、Plugin SDK、能力注册、最小权限、供应链安全。
<a id="oclaw-010"></a>
### 2. OpenClaw 的工具可见性和 Allow/Deny 策略如何生效？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

工具不是安装后就必然对模型可见，而是经过**Profile、全局策略、Provider限制、Agent策略、渠道权限、沙箱状态和Plugin可用性**等多层过滤，最终集合才进入模型上下文。

配置原则是默认最小集合、按Agent和场景增量开放；Deny应优先于Allow，不能指望Prompt要求代替宿主策略。排障时应检查最终Effective Policy，而不是只看某一层配置。减少无关工具还会降低误选率和工具Schema的Token开销。

**相关知识点：** Tool Profile、Allowlist、Denylist、策略优先级、Effective Policy、Tool Surface。
<a id="oclaw-017"></a>
### 3. OpenClaw 的 MCP 能力应如何理解和治理？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

MCP是OpenClaw连接或暴露标准化工具与上下文的协议层，但**协议互通不等于自动可信**。接入Server前应固定来源与版本，验证Transport、认证、工具Schema、超时和错误语义，再通过Include/Exclude与Agent Policy缩小工具面。

远程Server需要TLS、OAuth或短期凭据，本地stdio Server同样可能访问宿主资源。工具结果一律视为不可信输入；写操作还需目标系统ACL、幂等和审计。大规模工具目录可结合Tool Search按需发现，避免把全部Schema塞入Prompt。

**相关知识点：** MCP、stdio、HTTP、OAuth、Tool Filtering、Schema、Tool Search。
<a id="oclaw-024"></a>
### 4. 如何为 OpenClaw 编写可维护的 Skill？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

一个好Skill应有**准确触发描述、最小必要指令、明确输入输出、可复用脚本和验证步骤**。`SKILL.md`只放Agent需要遵循的流程，长参考资料按需加载，确定性操作优先复用Skill目录内脚本。

Skill不能把Secret写入正文，也不能用文字要求绕过工具策略。发布前测试正触发、误触发、缺依赖、恶意输入和失败恢复；版本升级要回归实际任务。第三方Skill安装前审查源代码、依赖和安装行为，并在不可信场景使用沙箱。

**相关知识点：** SKILL.md、渐进加载、Trigger Description、脚本复用、依赖门禁、Skill Supply Chain。
<a id="oclaw-025"></a>
### 5. OpenClaw Plugin 的设计和升级需要关注哪些兼容性问题？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

Plugin可注册Tool、Channel、Provider、Hook和其他Runtime能力，因而兼容面包括**Manifest、配置Schema、SDK接口、权限、事件和持久数据**。

插件应声明支持版本与弃用信息，对配置做严格校验，启动失败时Fail Closed或明确降级。升级先在隔离Gateway回放渠道、工具和自动化场景，再灰度发布；迁移必须可回滚，避免新旧版本同时写不兼容状态。Plugin拥有宿主代码权限，安全审查强度应高于普通Prompt或Skill。

**验证指标：** 任务完成率、工具调用成功率、P95 延迟、Token 消耗和人工接管率。

**相关知识点：** Plugin SDK、Manifest、Semantic Versioning、Schema Migration、Canary、Fail Closed。
<a id="oclaw-040"></a>
### 6. OpenClaw 如何实现工具调用决策？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

**【核心思路】**
模型根据当前上下文与可见工具描述产生调用，Gateway再应用工具Profile、Allow/Deny、Sandbox和Elevated等策略。模型“想调用”不等于获准执行，宿主策略才是权限边界。

提高正确率应精简工具面、准确描述Schema、调用前校验参数与身份、调用后验证业务状态。外部内容和工具返回都视为不可信，不能用其中指令扩大权限。

**相关知识点：** OpenClaw、Tool Calling、权限控制、Sandbox、Agent Runtime。
<a id="oclaw-041"></a>
### 7. OpenClaw 如何接入 MCP 工具？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

**【核心思路】**
当前`openclaw mcp`有两条明确路径：`openclaw mcp serve`让OpenClaw作为MCP Server，通过stdio向外部客户端暴露Gateway支持的渠道会话；`mcp add/set/configure/...`管理外部MCP Server定义，供符合条件的Runtime使用。

接入后应以`status/doctor/probe`验证连接与能力，并用Include/Exclude过滤工具。远程HTTP可配置OAuth，静态Secret不得写入仓库。还需区分MCP与ACP：托管Coding Harness会话使用ACP，不应混称为MCP。

**相关知识点：** OpenClaw、Harness Engineering、Agent Runtime、MCP、工程扩展。
<a id="oclaw-055"></a>
### 8. OpenClaw 如何保证工具调用安全性？

> 核验日期：2026-08-03｜来源：[官方资料](references.md)

**【核心思路】**
先用渠道配对和Allowlist限制谁能发指令，再用Tool Profile与Allow/Deny限制能调用什么；Sandbox限制文件、进程和网络范围，Elevated能力另设门槛。外部网页、邮件和媒体内容统一视为不可信。

Exec Approval只是操作者意图护栏，不是敌对多租户隔离；强边界需要独立OS用户/主机/Gateway。对写入、外发和设备控制采用短期凭据、预览确认、后置校验和审计。

**验证指标：** 任务完成率、工具调用成功率、P95 延迟、Token 消耗和人工接管率。

**相关知识点：** OpenClaw、Tool Calling、多租户、Sandbox、Agent Runtime。

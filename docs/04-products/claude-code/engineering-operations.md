# 工程集成与企业治理

> 所属章节：[Claude Code](README.md)｜本文件共 **9** 题。

<a id="cc-025"></a>
### CC-025 · 企业如何通过 Managed Settings 和 LLM Gateway 治理 Claude Code？

> 稳定 ID：`CC-025`｜原题号：25｜核验日期：2026-08-03｜来源：[官方资料](references.md)

Managed Settings集中下发不可被普通用户放宽的权限、MCP、网络和功能策略；LLM Gateway集中处理认证、模型访问、用量、预算、审计和路由。二者分别治理客户端行为和模型流量。

上线前要验证Gateway完整转发Claude Code需要的API字段、流式响应和Beta能力，避免静默降级。客户端仍需Sandbox与最小工具权限，Gateway也不能替代代码仓库和云资源ACL。配置变更应版本化、灰度、监控并可回滚，开发者可查看Effective Config以便排障。

**相关知识点：** Managed Settings、LLM Gateway、Policy Enforcement、Spend Limit、Protocol Compatibility、Effective Config。
<a id="cc-026"></a>
### CC-026 · Claude Code 的 Anthropic、Bedrock、Google Cloud 和 Microsoft Foundry 部署如何选型？

> 稳定 ID：`CC-026`｜原题号：26｜核验日期：2026-08-03｜来源：[官方资料](references.md)

选择取决于**现有云治理、模型可用性、区域、IAM、采购、日志和功能兼容性**。直接Anthropic通常获得原生更新路径；云Provider便于复用企业账号、网络和审计体系，但模型名称、区域、配额和部分Feature Availability可能不同。

不要把Provider切换当成完全透明。应建立版本矩阵，测试工具调用、长上下文、缓存、流式、Agent Teams、Web/IDE Surface和Gateway。凭据使用短期身份或Helper，按团队和环境分账；Fallback前确认数据区域与合规允许。

**相关知识点：** Anthropic API、Amazon Bedrock、Google Cloud、Microsoft Foundry、IAM、Feature Matrix。
<a id="cc-027"></a>
### CC-027 · Claude Code 的 Code Review 如何减少误报和漏报？

> 稳定 ID：`CC-027`｜原题号：27｜核验日期：2026-08-03｜来源：[官方资料](references.md)

有效Review需要**明确差异范围、仓库上下文、严重级别和可验证证据**。`CLAUDE.md`提供项目约定，Review专用规则可放`REVIEW.md`；多Agent分析发现候选后，应检查可达路径、测试和上下游影响再报告。

每条Finding至少包含位置、触发条件、影响和修复建议，风格偏好不能冒充Bug。用历史真实缺陷、无缺陷PR和对抗样本校准Precision/Recall，按语言和风险切片。自动Review是合并门禁的输入之一，不能替代测试、安全扫描和Owner审批。

**相关知识点：** Code Review、REVIEW.md、Multi-agent Analysis、Finding Evidence、Precision、Recall。
<a id="cc-028"></a>
### CC-028 · Claude Code 修改代码后应如何设计验证闭环？

> 稳定 ID：`CC-028`｜原题号：28｜核验日期：2026-08-03｜来源：[官方资料](references.md)

验证顺序应从**最小、快速、确定性检查**逐步扩大：格式化与静态检查、受影响单测、组件/集成测试、构建，再按风险运行端到端与安全测试。

Agent先从仓库规则或CI配置找到权威命令，失败后区分代码缺陷、环境缺失、测试Flaky和既有失败。修复循环设置次数和时间预算，每次改动都要说明与失败证据的关系。最终报告实际运行的命令、结果、未执行项和剩余风险，禁止把“看起来正确”当验证。

**相关知识点：** Test Pyramid、Static Analysis、Affected Tests、Flaky Test、Retry Budget、Verification Evidence。
<a id="cc-030"></a>
### CC-030 · 企业推广 Claude Code 时如何衡量真实价值，而不是只看使用量？

> 稳定 ID：`CC-030`｜原题号：30｜核验日期：2026-08-03｜来源：[官方资料](references.md)

使用量只说明调用发生，价值应看**质量调整后的工程结果**。建立采用前基线，比较Issue周期、PR吞吐、Review等待、缺陷逃逸、回滚、人工返工和开发者满意度。

按任务类型和团队做Cohort，计算被接受并上线的改动比例、净节省时间、单位成功成本和安全事件。控制任务难度、人员经验与并行流程变化，避免把相关性当因果。Pilot先覆盖低风险高频任务，达到质量、安全和经济门槛后再扩大权限；无收益或返工增加时应缩小场景。

**相关知识点：** Adoption、Acceptance Rate、Lead Time、Defect Escape、Cohort、TCO、ROI。
> 以下题目由「Agent 核心架构」「任务规划与执行」「工具与能力体系」「工程落地与平台化」迁入，保留原答案内容并统一纳入 Claude Code 专章。

<a id="cc-074"></a>
### CC-074 · 如何评估Claude Code的任务完成率？

> 稳定 ID：`CC-074`｜原题号：74｜核验日期：2026-08-03｜来源：[官方资料](references.md)

任务完成率是**在约束与预算内，满足全部必需验收且无禁止副作用的任务比例**，不能以模型自报或生成补丁替代。

1. 固定Commit、环境、输入、范围和Acceptance Criteria，分为必需项、质量项和禁止项；必需项失败即非完全完成。
2. Judge运行Patch应用、编译、目标/隐藏测试、静态分析、Diff和安全检查；开放任务再由盲审按Rubric评估。
3. 报告Strict Success、Partial Completion、Valid Patch、首次通过率和无回归率。公式为成功数/有效任务数，环境故障单列。
4. 按任务类型、难度、语言、仓库规模、单/跨文件、模型版本和工具配置切片；同一任务多次运行，报告均值、置信区间及pass@1，避免随机性掩盖退化。
5. 线上以采纳、PR合并、回滚、缺陷逃逸和耗时验证离线分数；任务改写或扩大范围时建立新版本。

评测集需含真实任务和失败长尾，防止训练污染；所有Judge保存证据和版本。核心指标还应与Token、费用和时延结合，形成**单位成本成功率**。

**相关知识点：** Acceptance Criteria、Strict Success Rate、Partial Completion、隐藏测试、盲审、pass@1、置信区间、任务切片、单位成功成本。
<a id="cc-075"></a>
### CC-075 · 如何构建Coding Agent的离线评测集？

> 稳定 ID：`CC-075`｜原题号：75｜核验日期：2026-08-03｜来源：[官方资料](references.md)

离线评测集应以**真实任务、可复现仓库快照、可执行验收和防污染治理**为核心，覆盖代码定位、修改、验证及安全的完整闭环。

1. 从已合并PR、Issue、缺陷单和维护任务抽取样本，回退到修改前Commit；保留需求、环境、依赖和原始测试，将开发者补丁只作为参考，不作为唯一正确答案。
2. 按问答、缺陷修复、功能、重构、测试生成、依赖升级和安全任务分层，覆盖多语言、仓库规模、跨文件、动态调用及长尾失败；控制难度与线上分布，并保留挑战集。
3. 每题定义Acceptance Criteria：Patch可应用、编译、公开/隐藏测试、静态检查、Diff范围、性能和禁止副作用。无法完全自动判定的设计质量使用双人盲审Rubric与仲裁。
4. 用容器或VM固定工具链、依赖、种子、时间和外部服务替身，断网运行并校验基线；Flaky样本隔离治理。任务、仓库与测试均版本化，产出可重放Trace。
5. 数据按仓库和时间切分，近重复检测防止同一修复泄漏到训练与测试；定期检查模型污染。线上失败经脱敏、去重和审核后回流，旧集保持冻结用于纵向比较。

报告完成率、定位Recall、Valid Patch、首次通过率、回归率、Token、时延及安全违规，并按切片给出置信区间；Judge和环境版本变化需重新建立基线。

**相关知识点：** 仓库快照、真实PR任务、隐藏测试、盲审Rubric、可复现环境、Flaky治理、时间切分、数据污染、挑战集。
<a id="cc-078"></a>
### CC-078 · 如何进行大小模型分工和模型路由？

> 稳定 ID：`CC-078`｜原题号：78｜核验日期：2026-08-03｜来源：[官方资料](references.md)

大小模型依据**任务难度、风险、上下文、工具需求和失败代价**动态路由，以质量约束下的单位成功成本最小为目标。

1. 小模型承担分类、抽取、查询改写、摘要、格式校验和简单问答；大模型承担需求澄清、复杂规划、跨文件推理、安全Review及恢复。
2. 路由特征包括任务类型、代码规模、依赖跳数、所需上下文、历史成功率、用户SLA、数据敏感度和剩余预算；风险规则优先于成本，例如生产与安全任务直接使用高能力模型并增加验证。
3. 小模型先输出置信度、证据覆盖和结构化结果；低置信、冲突或验证失败时升级。大模型接收压缩目标、证据和失败记录。
4. Validator独立检查Schema、引用、测试和安全；不能由路由模型同时自评。对写操作可使用大模型生成、小模型检查格式，但关键语义Review仍需强模型或人工。
5. 路由以规则起步，再用Bandit灰度优化；设置健康熔断、供应商降级、最大升级次数和预算，防止震荡。

评估完成率、误路由率、升级率、P95、Token、费用和单位成功成本，并按任务风险检查质量下限。模型版本变化时重新校准阈值，保留固定对照组。

**相关知识点：** Model Routing、级联推理、置信度校准、风险路由、Validator、Bandit、模型熔断、单位成功成本、误路由率。
<a id="cc-090"></a>
### CC-090 · Claude Code理解调用关系主要依赖模型推理，还是依赖LSP和索引？

> 稳定 ID：`CC-090`｜原题号：90｜核验日期：2026-08-03｜来源：[官方资料](references.md)

两者结合，但职责不同。模型从已读取的代码、类型和命名中推断语义；Grep、Glob和Read提供文本证据；启用代码智能插件后，LSP Tool可提供定义、引用、诊断等结构化信息。

LSP不是模型内部记忆，也不保证覆盖反射、动态导入、宏、生成代码或运行时绑定。公开文档也没有承诺Claude Code默认为所有仓库维护完整Call Graph或向量索引。复杂项目应把静态关系、Git历史、构建反馈和运行Trace交叉验证。

正确流程是先用低成本搜索缩小范围，再通过LSP/AST确认符号关系，最后用编译和测试验证。没有代码智能时，Agent会更多依赖文本搜索和逐文件阅读，成本和误判率通常更高。

**相关知识点：** LSP Tool、Code Intelligence、Text Search、Static Analysis、Dynamic Dispatch、Evidence Triangulation。

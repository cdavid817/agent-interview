# Coding Agent 沙箱/可观测/评测与 OTel 255 题 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 向题库补充 255 道面试题——Coding Agent 沙箱 60 题、Coding Agent 可观测性 60 题、Coding Agent 评测 75 题（含 DeepEval 15 题）、OpenTelemetry 60 题——题库总数 1,798 → 2,053。

**Architecture:** 九个新的题目文件按现有 `question-schema.md` 格式写入两个既有章节（`docs/03-production/engineering-platform/` 与 `docs/03-production/safety-governance-observability/`）。不新增章节、不新增 ID 前缀、不改任何脚本。章节索引、根 README 统计、重复题报告、核心 100 题、术语索引与 Anki 卡组全部由既有脚本重建。

**Tech Stack:** Markdown、Python 3.12（`scripts/validate.py`、`build_indexes.py`、`build_anki.py`）、PowerShell 7（`build_glossary.ps1`）、`genanki` + `markdown`。

**设计文档：** `specs/2026-08-30-coding-agent-sandbox-observability-eval-design.md`

---

## Global Constraints

以下是 `scripts/validate.py` 的硬性要求与仓库既有惯例，**每个任务都适用**。

### 格式

- 题目锚点格式固定：`<a id="eng-203"></a>` 独占一行（ID 小写），紧跟下一行 `### N. 题干`，N 为**该文件内**的顺序号，从 1 递增。
- 锚点与标题之间不得有空行，否则 `QUESTION_RE` 匹配不上，该题不会被识别。
- **本计划涉及的两个章节都不是产品专题**，`ENG` 与 `GOV` 前缀不触发产品校验分支，因此**不写**核验日期行、**不写**来源行。写了反而与章节惯例不符。
- 每个文件必须以 `# ` 开头的 H1 标题起始。
- 文件头第二行为所属章节说明，格式见下方模板。文件头声明的题数必须与实际题数一致（这一行由人工维护，脚本不改）。

文件头模板：

```markdown
# <文件标题>

> 所属章节：[<章节名>](README.md)｜本文件共 **<N>** 题。
```

单题模板：

```markdown
<a id="eng-203"></a>
### 1. 把仓库送进沙箱有哪些方式？完整 clone、工作树快照与只读挂载如何取舍？

（结论段：一句话给出核心判断，用 `**粗体**` 标出关键取舍。）

1. （机制第一点）
2. （机制第二点）
3. （机制第三点）
4. （机制第四点）
5. （机制第五点）

（收束段：适用边界、失败模式、以及可采集的验证指标。）

**相关知识点：** 术语一、术语二、术语三。
```

### 校验硬约束

- 同一文件内稳定 ID 数字必须**严格递增**，否则报「文件内稳定 ID 未按数字递增」。
- 每题**有且仅有一行**以 `**相关知识点：**` 开头的行，行内**不得出现** `ENG-203`、`GOV-192` 形式的题目 ID。
- 每题答案必须命中可验证信号词之一，否则报「缺少可验证指标」。信号词表（`METRIC_SIGNAL_RE`）：指标、准确率、召回率、成功率、完成率、错误率、命中率、延迟、时延、吞吐、QPS、P95、P99、SLO、SLA、成本、Token、覆盖率、通过率、满意度、ROI、可验证、验证、测试、评测、监控、命中、耗时。
- 任意去除空白后 **≥100 字符**的段落不得与题库中任何其他题目的段落重复，否则报「答案包含跨题重复长段落」。**255 题同主题写作，这是本计划最高频的失败点。**
- 标题标准化（去空白标点、casefold、剥离结尾的「（xx面）」类括注）后不得与题库中任何既有标题重复。spec 第六节已做过全量比对，255 条标题与现有 1,798 题**零冲突**；只要照抄 spec 里的标题就不会撞，**改写标题前必须重新比对**。
- 单个题目文件不超过 50 题（本计划最大单文件 30 题）。
- 答案正文中若出现 `[文本](路径)` 形式，路径必须真实存在——`validate_local_links()` 不剥离代码围栏，代码块里的示例链接同样会被判为坏链。**本计划的题目答案里不要写任何 Markdown 链接。**
- Markdown 代码围栏必须成对闭合。

### 内容约束

- **答案篇幅 450–700 字（去空白字符），复杂题可到 800。** 这是本计划涉及的两个章节的实测水平：`observability.md` 中位数 606、`evaluation.md` 中位数 601、`coding-agent.md` 中位数 577，最长 855。**不要按产品专题章节的 250–550 字写**，那是另一批文件的标准。
- 答案结构：结论段（点出核心判断）→ 编号机制 3～5 条 → 收束段（边界、失败模式、验证指标）→ 相关知识点。必要时可加一张小表格（既有题目有此先例）。
- **事实颗粒度**：点名稳定的概念与机制（SWE-bench Verified、fail-to-pass、W3C Trace Context、OTLP、尾部采样、G-Eval、gVisor、Firecracker、seccomp 等），**不写**榜单分数、模型价格、版本号、API 签名这类会过期的内容。
- 遵守 `docs/00-guide/ownership-rules.md`：本计划的题目只写本章节负责的部分，跨章节内容点到为止，不展开。
- 不把 HTTP 成功、模型自述完成或单一 LLM Judge 分数当作业务正确性。

### 每个任务的收尾

每个内容任务结束前必须跑通：

```bash
python scripts/build_indexes.py && python scripts/validate.py
```

Expected: `All checks passed.`，且统计表的 Total 与该任务的预期值一致。

> 术语索引（`build_glossary.ps1`）**只在 Task 10 跑一次**。中途跑会让 `validate_glossary()` 的「常见术语」阈值随新增题目反复漂移，每个任务都要重建一遍术语表，徒增噪声。若中途 `validate.py` 报术语索引相关错误（缺少常见术语 / 包含未达保留条件的术语），说明某个新术语跨过了 5 次阈值——此时按需在该任务里补跑一次 `pwsh -File scripts/build_glossary.ps1` 即可。

---

## File Structure

| 文件 | 职责 | 题数 | ID 区间 |
|---|---|---:|---|
| `docs/03-production/engineering-platform/coding-agent-sandbox.md` | 编码沙箱的隔离模型与执行边界 | 30 | ENG-203…232 |
| `docs/03-production/engineering-platform/coding-agent-sandbox-ops.md` | 编码沙箱的运维、交付与验证 | 30 | ENG-233…262 |
| `docs/03-production/safety-governance-observability/coding-agent-observability.md` | 编码会话的埋点与链路 | 30 | GOV-192…221 |
| `docs/03-production/safety-governance-observability/coding-agent-observability-metrics.md` | 编码指标、归因与观测治理 | 30 | GOV-222…251 |
| `docs/03-production/safety-governance-observability/coding-agent-evaluation.md` | 编码基准与评测集构造 | 30 | GOV-252…281 |
| `docs/03-production/safety-governance-observability/coding-agent-evaluation-ops.md` | 线上评测指标与发布流程 | 30 | GOV-282…311 |
| `docs/03-production/safety-governance-observability/deepeval.md` | DeepEval 评测框架 | 15 | GOV-312…326 |
| `docs/03-production/safety-governance-observability/otel-basics.md` | OTel 核心概念与数据模型 | 30 | GOV-327…356 |
| `docs/03-production/safety-governance-observability/otel-collector-ops.md` | OTel Collector、采样与落地 | 30 | GOV-357…386 |
| `docs/03-production/engineering-platform/README.md` | 章节索引（脚本重写子主题表，头部描述行人工改） | — | — |
| `docs/03-production/safety-governance-observability/README.md` | 同上 | — | — |
| `README.md` | 根 README（统计块脚本重写，Anki 卡片数人工改） | — | — |

**任务与 Total 对照**（起点 1,798）：

| 任务 | 产出 | 章节计数 | Total |
|---|---|---|---:|
| Task 1 | ENG-203…232 | `227  ENG` | 1,828 |
| Task 2 | ENG-233…262 | `257  ENG` | 1,858 |
| Task 3 | GOV-192…221 | `189  GOV` | 1,888 |
| Task 4 | GOV-222…251 | `219  GOV` | 1,918 |
| Task 5 | GOV-252…281 | `249  GOV` | 1,948 |
| Task 6 | GOV-282…311 | `279  GOV` | 1,978 |
| Task 7 | GOV-312…326 | `294  GOV` | 1,993 |
| Task 8 | GOV-327…356 | `324  GOV` | 2,023 |
| Task 9 | GOV-357…386 | `354  GOV` | 2,053 |
| Task 10 | 生成物与导航 | 不变 | 2,053 |

---

### Task 1: Coding Agent 沙箱与执行隔离（ENG-203…232，30 题）

**Files:**
- Create: `docs/03-production/engineering-platform/coding-agent-sandbox.md`
- Modify: `docs/03-production/engineering-platform/README.md`（由 `build_indexes.py` 重写子主题表）

**Interfaces:**
- Consumes: 无（本计划第一个任务）
- Produces: 锚点 `eng-203` … `eng-232`；Task 2 从 `ENG-233` 在新文件续写

- [ ] **Step 1: 写文件头**

```markdown
# Coding Agent 沙箱与执行隔离

> 所属章节：[工程落地与平台化](README.md)｜本文件共 **30** 题。
```

- [ ] **Step 2: 写 30 题**

格式见 Global Constraints 的单题模板。ID、顺序号与标题对照表（**标题逐字照抄，不要改写**）：

| ID | 序号 | 标题 |
|---|---:|---|
| ENG-203 | 1 | 把仓库送进沙箱有哪些方式？完整 clone、工作树快照与只读挂载如何取舍？ |
| ENG-204 | 2 | 多个 Coding Agent 并行修改同一仓库时，如何用 Git worktree 做工作区隔离？ |
| ENG-205 | 3 | 超大仓库如何用稀疏检出与浅克隆压缩沙箱准备时间？ |
| ENG-206 | 4 | 子模块、Git LFS 和生成物目录在沙箱里应该如何处理？ |
| ENG-207 | 5 | 沙箱工作区的生命周期如何定义？何时可以复用、何时必须销毁重建？ |
| ENG-208 | 6 | 编码任务的沙箱该选进程隔离、容器还是 microVM？决策依据是什么？ |
| ENG-209 | 7 | Agent 需要完整工具链才能跑构建和测试，如何既保持隔离又不每次冷编译？ |
| ENG-210 | 8 | 构建缓存跨任务复用会带来哪些污染与投毒风险？如何治理？ |
| ENG-211 | 9 | 沙箱如何用可写层承载修改，并干净地导出变更？ |
| ENG-212 | 10 | 一个仓库同时包含多种语言运行时，沙箱如何避免镜像无限膨胀？ |
| ENG-213 | 11 | 沙箱内安装依赖需要出网，如何避免出网策略变成任意外联通道？ |
| ENG-214 | 12 | 私有制品库如何接入沙箱？代理、镜像与直连各有什么风险？ |
| ENG-215 | 13 | 依赖安装脚本可以执行任意代码，沙箱如何限制这一步的权限？ |
| ENG-216 | 14 | 完全离线的沙箱可行吗？依赖预取与锁文件如何配合？ |
| ENG-217 | 15 | Agent 主动引入新依赖时，如何在沙箱内做供应链审查？ |
| ENG-218 | 16 | 沙箱内的 Git 凭证如何做到只能推特性分支、不能推主干？ |
| ENG-219 | 17 | 制品库与云服务凭证如何注入沙箱而不进入模型上下文？ |
| ENG-220 | 18 | 集成测试需要真实凭证时，如何设计最小权限与短时效令牌？ |
| ENG-221 | 19 | 如何防止密钥经由命令回显、日志和 Trace 泄漏出沙箱？ |
| ENG-222 | 20 | 沙箱凭证泄漏后如何快速定位影响面并完成轮换？ |
| ENG-223 | 21 | Bash 命令允许清单为什么容易被绕过？管道、命令替换与转义如何处理？ |
| ENG-224 | 22 | 如何在沙箱内判定一条命令是否高危？静态规则与模型判定如何配合？ |
| ENG-225 | 23 | 沙箱的只读模式该覆盖哪些操作？它与审批模式如何切换？ |
| ENG-226 | 24 | 审批点应该设在命令级、工具级还是任务级？ |
| ENG-227 | 25 | Agent 在沙箱内执行了破坏性操作，如何回滚工作区与外部副作用？ |
| ENG-228 | 26 | 仓库里的 README、注释和 Issue 可能带注入指令，如何阻断它们触发命令执行？ |
| ENG-229 | 27 | 依赖包元数据与第三方代码中的注入如何防范？ |
| ENG-230 | 28 | CI 日志、测试输出和编译报错回填上下文时会引入什么风险？ |
| ENG-231 | 29 | 工具返回值与 MCP Server 响应进入上下文前应做哪些过滤？ |
| ENG-232 | 30 | 面向 Coding Agent 的注入防御如何做纵深分层？各层分别拦得住什么？ |

**写作前必读**：`docs/02-capabilities/tools-skills-mcp/sandbox-security-1.md` 的 41 题与 `sandbox-security-2.md` 的 7 题。那两个文件已覆盖**通用 Agent 沙箱**：容器与 Firecracker 权衡、冷启动优化、seccomp syscall 过滤、逃逸防范、超时优雅终止、审计日志设计、弹性伸缩、命令沙箱隔离、防误删文件、Prompt Injection 诱导工具、SQL 影响评估。

本文件必须始终站在**编码任务**的具体处境上作答：要 checkout 一个真实仓库、要跑得动这个仓库的构建与测试、要产出一个能被人 review 的 diff。区分示例：

| 既有通用题 | 本文件对应题的切入点 |
|---|---|
| 容器隔离和虚拟机隔离在安全性和性能上的权衡 | ENG-208 从「跑构建和测试需要什么工具链与文件系统性能」切入 |
| 如何保证 Agent 只能修改指定目录 | ENG-211 从「可写层如何承载修改并导出为 patch」切入 |
| 沙箱逃逸风险如何防护 | 本文件不写防护措施（ENG-258/259 在 Task 2 写验证与演练） |
| 沙箱执行超时后如何优雅终止并回收资源 | 本文件不收录该题 |
| 如何限制 Agent 执行危险 Shell 命令 | ENG-223 只写「允许清单为什么被绕过」的机制，ENG-224 只写判定方法 |

- [ ] **Step 3: 验证**

```bash
python scripts/build_indexes.py && python scripts/validate.py
```

Expected: `All checks passed.`，统计表 `227  ENG  工程落地与平台化`，Total 1828。

常见失败与处理：

| 报错 | 原因 | 处理 |
|---|---|---|
| `缺少可验证指标` | 该题答案没命中信号词表 | 在收束段补一句可采集的指标 |
| `答案包含跨题重复长段落` | 与 `sandbox-security-*.md` 撞了 | 按提示的两个 ID 定位，改写本文件那一题 |
| `标准化题目标题重复` | 标题被改写后撞了既有题 | 改回对照表里的原标题 |
| `应有且仅有一处相关知识点` | 漏写或写了两行 | 每题只保留一行 |
| `文件内稳定 ID 未按数字递增` | 顺序写错 | 按对照表顺序排列 |

- [ ] **Step 4: 提交**

```bash
git add docs/03-production/engineering-platform/
git commit -m "feat: 新增 Coding Agent 沙箱与执行隔离 30 题（ENG-203…232）"
```

---

### Task 2: Coding Agent 沙箱运维与验证（ENG-233…262，30 题）

**Files:**
- Create: `docs/03-production/engineering-platform/coding-agent-sandbox-ops.md`
- Modify: `docs/03-production/engineering-platform/README.md`（脚本重写）

**Interfaces:**
- Consumes: Task 1 产出的 `coding-agent-sandbox.md`，末尾锚点 `eng-232`
- Produces: 锚点 `eng-233` … `eng-262`；ENG 前缀在本计划到此为止

- [ ] **Step 1: 写文件头**

```markdown
# Coding Agent 沙箱运维与验证

> 所属章节：[工程落地与平台化](README.md)｜本文件共 **30** 题。
```

- [ ] **Step 2: 写 30 题**

| ID | 序号 | 标题 |
|---|---:|---|
| ENG-233 | 1 | 沙箱池化如何按仓库预热？命中率与资源浪费如何平衡？ |
| ENG-234 | 2 | 沙箱冷启动时间由哪些环节构成？各段分别如何优化？ |
| ENG-235 | 3 | 如何按团队与仓库设置沙箱并发与资源配额？ |
| ENG-236 | 4 | 沙箱集群如何调度长任务与短任务的混合负载？ |
| ENG-237 | 5 | 资源紧张时沙箱如何抢占与驱逐？被驱逐的任务如何恢复？ |
| ENG-238 | 6 | 沙箱基础镜像如何随仓库工具链演进？维护责任如何划分？ |
| ENG-239 | 7 | 一个平台要服务多种语言与版本，镜像矩阵如何收敛？ |
| ENG-240 | 8 | 「沙箱里过、CI 里挂」的环境漂移如何检测与量化？ |
| ENG-241 | 9 | devcontainer、Nix 等既有环境定义能否直接复用为 Agent 沙箱？ |
| ENG-242 | 10 | 沙箱环境的可复现性如何保证？哪些不确定性必须消除？ |
| ENG-243 | 11 | 长时编码会话的沙箱状态如何保存与恢复？ |
| ENG-244 | 12 | 沙箱任务的检查点该记录什么才能支持断点续跑？ |
| ENG-245 | 13 | 后台自主编码任务的沙箱与交互式会话有什么不同要求？ |
| ENG-246 | 14 | 沙箱如何支持「跑起来看效果」：启动服务、访问端口、验证行为？ |
| ENG-247 | 15 | 需要浏览器或图形环境验证时，沙箱如何提供而不扩大攻击面？ |
| ENG-248 | 16 | 修改结果如何从沙箱提取为可审查的 patch？ |
| ENG-249 | 17 | 沙箱产出如何落地为 PR？分支保护与 CI 触发如何配合？ |
| ENG-250 | 18 | 如何在提交前拦截密钥、大文件与生成物？ |
| ENG-251 | 19 | 同一任务多次迭代产生的中间提交如何整理？ |
| ENG-252 | 20 | 沙箱产出的构建工件如何签名与溯源？ |
| ENG-253 | 21 | 沙箱执行记录要留什么，才能回答「谁在什么代码上跑了什么命令」？ |
| ENG-254 | 22 | 沙箱审计数据如何满足合规要求？留存与访问如何控制？ |
| ENG-255 | 23 | 沙箱成本如何归属到团队、仓库与任务？ |
| ENG-256 | 24 | 如何从沙箱行为数据中识别异常与滥用？ |
| ENG-257 | 25 | 沙箱审计日志本身如何防篡改？ |
| ENG-258 | 26 | 如何验证沙箱真的隔离了？有哪些可执行的对抗性测试？ |
| ENG-259 | 27 | 逃逸演练如何组织？红队应重点攻击哪些面？ |
| ENG-260 | 28 | 沙箱平台的 SLO 该怎么定？哪些指标直接影响 Agent 成功率？ |
| ENG-261 | 29 | 沙箱故障如何降级？降级期间哪些能力必须关闭？ |
| ENG-262 | 30 | 沙箱相关事故的复盘应该沉淀哪些可执行改进？ |

**去重提醒**：

- ENG-233/234 与 `sandbox-security-1.md` 的「如何设计沙箱的冷启动优化方案，降低池化管理的资源浪费？」相邻。既有题讲通用池化策略；ENG-233 只写**按仓库预热**（镜像层、依赖缓存、索引预建这些仓库相关的热数据），ENG-234 只写**冷启动的分段构成与各段优化**。
- ENG-236/237 与既有「大规模并发场景下，沙箱集群如何做弹性伸缩与调度？」相邻。本文件写**长短任务混合负载**与**驱逐后的恢复**，不重述弹性伸缩本身。
- ENG-253/254/257 与既有「沙箱的审计日志系统如何设计，以支持安全事件的快速定位与回溯？」相邻。本文件写**编码执行记录的具体字段**（仓库、Commit、命令、diff）、**合规留存**与**防篡改**三个不同侧面。
- ENG-258/259 与既有「沙箱逃逸（sandbox escape）风险如何防范？」相邻。既有题写防护；本文件写**如何验证防护有效**（对抗性测试、演练组织）。
- ENG-250 与 `sandbox-testing.md` 无重叠，但写作时不要跑进单测生成的话题。

- [ ] **Step 3: 验证**

```bash
python scripts/build_indexes.py && python scripts/validate.py
```

Expected: `All checks passed.`，`257  ENG  工程落地与平台化`，Total 1858。

- [ ] **Step 4: 提交**

```bash
git add docs/03-production/engineering-platform/
git commit -m "feat: 新增 Coding Agent 沙箱运维与验证 30 题（ENG-233…262）"
```

---

### Task 3: Coding Agent 可观测性——埋点与链路（GOV-192…221，30 题）

**Files:**
- Create: `docs/03-production/safety-governance-observability/coding-agent-observability.md`
- Modify: `docs/03-production/safety-governance-observability/README.md`（脚本重写）

**Interfaces:**
- Consumes: 无（GOV 前缀在本计划的第一个任务）
- Produces: 锚点 `gov-192` … `gov-221`；Task 4 从 `GOV-222` 在新文件续写

- [ ] **Step 1: 写文件头**

```markdown
# Coding Agent 可观测性：埋点与链路

> 所属章节：[安全、治理与可观测性](README.md)｜本文件共 **30** 题。
```

- [ ] **Step 2: 写 30 题**

| ID | 序号 | 标题 |
|---|---:|---|
| GOV-192 | 1 | Coding Agent 一次会话该记录哪些事件？与通用 Agent 的 Trace 有何不同？ |
| GOV-193 | 2 | 编码会话的 Span 层级如何划分：任务、轮次、工具调用还是文件？ |
| GOV-194 | 3 | 一次会话中的「轮次」如何定义才对分析有用？ |
| GOV-195 | 4 | 交互式会话与后台自主任务的观测模型能统一吗？ |
| GOV-196 | 5 | 会话与 PR、Issue、工单如何建立稳定关联？ |
| GOV-197 | 6 | 代码编辑如何做到可追溯：哪次修改基于哪条证据？ |
| GOV-198 | 7 | 编辑失败（patch 打不上、字符串不匹配）如何度量与归因？ |
| GOV-199 | 8 | 如何观测「改了又改」的返工模式？ |
| GOV-200 | 9 | 最终 diff 与中间编辑序列都要留吗？各自回答什么问题？ |
| GOV-201 | 10 | 如何把一个有问题的 PR 归因到会话中的某一步？ |
| GOV-202 | 11 | 上下文构建过程该记录什么？窗口占用如何可视化？ |
| GOV-203 | 12 | 检索质量在线上如何观测？没有标注数据怎么办？ |
| GOV-204 | 13 | 如何识别「读了大量无关文件」这类上下文浪费？ |
| GOV-205 | 14 | 上下文压缩发生时该记录什么，才能事后判断压丢了什么？ |
| GOV-206 | 15 | 如何从 Trace 中识别反复读取同一批文件的低效循环？ |
| GOV-207 | 16 | Token 与缓存命中如何埋点才能定位成本异常？ |
| GOV-208 | 17 | 编码任务的延迟该拆成哪些段？哪一段最值得优化？ |
| GOV-209 | 18 | 单次任务成本如何归因到具体步骤与工具？ |
| GOV-210 | 19 | 模型侧的 TTFT、输出速率与工具等待如何分别观测？ |
| GOV-211 | 20 | 成本异常告警如何避免被正常的大任务误触发？ |
| GOV-212 | 21 | 一次任务跨越 IDE、CI 与代码托管平台，如何端到端串联？ |
| GOV-213 | 22 | IDE 侧埋点有哪些限制？本地数据如何合规上报？ |
| GOV-214 | 23 | CI 中的构建与测试结果如何回接到 Agent 会话？ |
| GOV-215 | 24 | 子 Agent 与并行任务的 Trace 如何与主会话关联？ |
| GOV-216 | 25 | MCP Server 与外部工具的调用如何纳入同一链路？ |
| GOV-217 | 26 | 会话回放要复现代码状态，如何绑定 Commit 与工作区快照？ |
| GOV-218 | 27 | 回放需要哪些不可变输入？哪些环节天然不可复现？ |
| GOV-219 | 28 | 回放数据的存储成本如何控制？ |
| GOV-220 | 29 | 如何用回放定位「同样的输入这次却失败了」？ |
| GOV-221 | 30 | 回放能力如何服务于评测集与训练数据构建？ |

**写作前必读**：同章节的 `observability.md` 全部 31 题。它已覆盖**通用 Agent 追踪**：TraceID/TaskID/SpanID 设计、Step 与 Task 级追踪的区别、多 Agent 消息传递追踪、Prompt 执行记录、回放一致性、Prompt 变更后能否回放、回放日志存储成本、OpenTelemetry 用于 Agent 监控、Tool Calling 成功率监控、告警体系、百万级任务下的监控性能。

本文件的每一题都必须以**代码**为观测对象——文件、符号、diff、patch、构建、测试、PR——而不是抽象的「工具调用」。区分示例：

| 既有通用题 | 本文件对应题的切入点 |
|---|---|
| TraceId 和 TaskId 如何设计 | GOV-193 写编码会话的 Span 层级该切到文件还是工具调用这一具体粒度 |
| 如何实现 Agent 执行过程回放 | GOV-217 只写**代码状态的复现**：Commit、工作区快照、依赖版本如何绑定 |
| 如何降低回放日志存储成本 | GOV-219 写编码场景特有的成本大头（全量 diff、文件内容），与既有题的通用分层存储不同 |
| Prompt 执行过程如何记录 | 本文件不写 Prompt 记录，GOV-202 只写**上下文构建过程**与窗口占用 |
| MCP Tool 调用链路如何追踪 | GOV-216 只写它如何并入编码会话的同一条链路，不重述 MCP 追踪机制 |

- [ ] **Step 3: 验证**

```bash
python scripts/build_indexes.py && python scripts/validate.py
```

Expected: `All checks passed.`，`189  GOV  安全、治理与可观测性`，Total 1888。

- [ ] **Step 4: 提交**

```bash
git add docs/03-production/safety-governance-observability/
git commit -m "feat: 新增 Coding Agent 可观测性埋点与链路 30 题（GOV-192…221）"
```

---

### Task 4: Coding Agent 可观测性——指标、归因与治理（GOV-222…251，30 题）

**Files:**
- Create: `docs/03-production/safety-governance-observability/coding-agent-observability-metrics.md`
- Modify: `docs/03-production/safety-governance-observability/README.md`（脚本重写）

**Interfaces:**
- Consumes: Task 3 产出的 `coding-agent-observability.md`，末尾锚点 `gov-221`
- Produces: 锚点 `gov-222` … `gov-251`

- [ ] **Step 1: 写文件头**

```markdown
# Coding Agent 可观测性：指标、归因与治理

> 所属章节：[安全、治理与可观测性](README.md)｜本文件共 **30** 题。
```

- [ ] **Step 2: 写 30 题**

| ID | 序号 | 标题 |
|---|---:|---|
| GOV-222 | 1 | Coding Agent 的黄金信号如何定义？ |
| GOV-223 | 2 | 「任务成功」在编码场景该怎么判定才不自欺？ |
| GOV-224 | 3 | 哪些指标能反映 Agent 的真实产出而不是活动量？ |
| GOV-225 | 4 | 指标该按仓库、语言还是任务类型分层？ |
| GOV-226 | 5 | 如何设计一个不会被优化行为扭曲的指标组合？ |
| GOV-227 | 6 | 编码任务的失败该如何分类才能统计与改进？ |
| GOV-228 | 7 | Coding Agent 成功率下跌时，如何区分是模型、仓库还是工具链变了？ |
| GOV-229 | 8 | 如何自动把失败会话聚类成可处理的问题簇？ |
| GOV-230 | 9 | 长尾失败如何抽样分析而不被高频问题淹没？ |
| GOV-231 | 10 | 归因结论如何验证？怎么避免把相关当因果？ |
| GOV-232 | 11 | Agent 声称「已完成」但测试从未执行，如何在观测层发现？ |
| GOV-233 | 12 | 长时任务如何检测「卡住」：无进展、循环重试与抖动？ |
| GOV-234 | 13 | 如何识别 Agent 绕过约束的行为，例如跳过检查、放宽断言？ |
| GOV-235 | 14 | 输出看似正确但证据不足，观测层能提供哪些信号？ |
| GOV-236 | 15 | 如何度量「表面完成率」与「实际交付率」的差距？ |
| GOV-237 | 16 | Coding Agent 平台的 SLO 该怎么定？ |
| GOV-238 | 17 | 哪些编码场景的异常值得告警？如何抑制噪声？ |
| GOV-239 | 18 | 质量类指标能不能直接做告警？阈值怎么定？ |
| GOV-240 | 19 | 单用户异常与平台级异常如何区分？ |
| GOV-241 | 20 | 从告警到定位再到止损的链路如何缩短？ |
| GOV-242 | 21 | 代码内容进入 Trace 有什么风险？脱敏策略如何设计？ |
| GOV-243 | 22 | 哪些字段必须外置存储而不进 Span 属性？ |
| GOV-244 | 23 | 观测数据的留存期与访问控制如何设计？ |
| GOV-245 | 24 | 跨租户与跨团队的观测数据如何隔离？ |
| GOV-246 | 25 | 采样如何做才不会丢掉关键失败样本？ |
| GOV-247 | 26 | Coding Agent 观测平台的整体架构如何分层？ |
| GOV-248 | 27 | 高频编辑事件如何聚合才能既省成本又不丢信息？ |
| GOV-249 | 28 | 观测指标如何反哺 Prompt、工具与上下文策略？ |
| GOV-250 | 29 | 观测数据如何支撑容量规划与成本预算？ |
| GOV-251 | 30 | 如何评估观测体系本身的有效性？ |

**去重提醒**：

- GOV-227 与 `incident-reliability.md` 的「如何建立 Agent Failure Taxonomy？」相邻。既有题写通用失败分类法的建立方法；GOV-227 必须给出**编码任务特有的失败类目**（定位错、编辑打不上、测试没跑、构建挂、改错模块、超预算等）并说明如何统计。
- GOV-228 与 `evaluation.md` 的「如何通过监控发现 Agent 能力退化？」和 `observability.md` 的「Agent 平台如何实现实时告警与根因分析？」相邻。GOV-228 只写**三类变化源的区分方法**：模型侧、仓库侧、工具链侧各自留下什么可观测痕迹。
- GOV-237 与 `observability.md` 的 SLO 内容相邻，且与 Task 2 的 ENG-260（沙箱平台 SLO）相邻。GOV-237 写**Agent 产品侧**的 SLO（任务成功率、端到端时长、成本），ENG-260 写**沙箱基础设施侧**的 SLO（可用性、启动时延、资源满足率），两者不要互相重述。
- GOV-242/243/244 与 `access-privacy.md` 的「Agent 执行日志应该记录哪些字段？」「Agent 日志体系应该记录哪些关键数据？」相邻。本组只写**代码内容**这一类特殊载荷的处理。
- GOV-249 与 `evaluation.md` 的「如何利用追踪数据持续优化 Agent 性能与成本？」和「如何建立 Agent 持续优化闭环体系？」相邻。GOV-249 收窄到**Prompt、工具、上下文策略**三个具体改进对象，不写通用闭环。

- [ ] **Step 3: 验证**

```bash
python scripts/build_indexes.py && python scripts/validate.py
```

Expected: `All checks passed.`，`219  GOV  安全、治理与可观测性`，Total 1918。

- [ ] **Step 4: 提交**

```bash
git add docs/03-production/safety-governance-observability/
git commit -m "feat: 新增 Coding Agent 观测指标与归因治理 30 题（GOV-222…251）"
```

---

### Task 5: Coding Agent 评测——基准与评测集（GOV-252…281，30 题）

**Files:**
- Create: `docs/03-production/safety-governance-observability/coding-agent-evaluation.md`
- Modify: `docs/03-production/safety-governance-observability/README.md`（脚本重写）

**Interfaces:**
- Consumes: Task 4 产出的 `coding-agent-observability-metrics.md`，末尾锚点 `gov-251`
- Produces: 锚点 `gov-252` … `gov-281`

- [ ] **Step 1: 写文件头**

```markdown
# Coding Agent 评测：基准与评测集

> 所属章节：[安全、治理与可观测性](README.md)｜本文件共 **30** 题。
```

- [ ] **Step 2: 写 30 题**

| ID | 序号 | 标题 |
|---|---:|---|
| GOV-252 | 1 | SWE-bench 是怎么构造的？它衡量了什么、没衡量什么？ |
| GOV-253 | 2 | SWE-bench Verified 相比原始集解决了什么问题？ |
| GOV-254 | 3 | 为什么公开基准的高分不能直接推断企业仓库表现？ |
| GOV-255 | 4 | 基准污染如何识别与缓解？ |
| GOV-256 | 5 | 除了缺陷修复类基准，还有哪些维度的编码基准值得关注？ |
| GOV-257 | 6 | fail-to-pass 与 pass-to-pass 是什么？为什么执行式评测需要两组测试？ |
| GOV-258 | 7 | 评测环境如何做到可复现：仓库快照、依赖锁定与网络隔离？ |
| GOV-259 | 8 | 评测 harness 如何隔离与并行？失败重试要不要允许？ |
| GOV-260 | 9 | 把测试作为唯一判据有哪些盲区？ |
| GOV-261 | 10 | 无法执行验证的任务（文档、配置、前端视觉）如何评测？ |
| GOV-262 | 11 | 如何用自家 PR 历史构造评测集？有哪些陷阱？ |
| GOV-263 | 12 | 评测样本如何标注？黄金补丁必须唯一吗？ |
| GOV-264 | 13 | 评测集如何做难度与类型分层？ |
| GOV-265 | 14 | 评测集规模多大才够？如何判断覆盖不足？ |
| GOV-266 | 15 | 涉密代码如何在不外泄的前提下参与评测？ |
| GOV-267 | 16 | pass@k 与 pass@1 分别适合回答什么问题？ |
| GOV-268 | 17 | resolve rate 之外还该看哪些结果级指标？ |
| GOV-269 | 18 | 轨迹级评测与结果级评测各能发现什么问题？ |
| GOV-270 | 19 | 如何评估补丁质量而不只看测试是否通过？ |
| GOV-271 | 20 | 如何评测 Agent「该求助时是否求助」的能力？ |
| GOV-272 | 21 | Agent 修改测试让评测通过，如何检测与防范？ |
| GOV-273 | 22 | 除改测试外，编码场景还有哪些 reward hacking 形态？ |
| GOV-274 | 23 | 评测集被反复优化后如何识别过拟合？ |
| GOV-275 | 24 | LLM-as-Judge 评估代码质量有哪些特有的失效模式？ |
| GOV-276 | 25 | 如何设计对抗样本来检验评测体系本身的鲁棒性？ |
| GOV-277 | 26 | 评测任务的输入该给到什么程度：Issue 原文、复现步骤还是已定位的文件？ |
| GOV-278 | 27 | 多文件、跨模块的修改任务如何设计评测？ |
| GOV-279 | 28 | 需要多轮探索的长任务，评测与单点修复有何不同？ |
| GOV-280 | 29 | 需要人类澄清的任务如何进评测集？ |
| GOV-281 | 30 | 评测中该给 Agent 多少工具与权限？给多或给少各会带来什么偏差？ |

**写作前必读**：同章节 `evaluation.md` 的 35 题。它已覆盖通用评测：任务完成率定义与归因、LLM-as-Judge 优缺点、降低评测主观性、多模型交叉评测、自动验收、评测平台建设、质量评测集构造、A/B Test、上线前评测流程。其中三题已触及编码场景但停留在概览层——「Coding Agent 最重要的评估指标是什么？」「如何评估代码生成质量？」「如何评估代码修改带来的风险？」，本文件必须下沉到**基准构造、执行式评测机制、样本标注与作弊检测**的具体做法。

其他去重提醒：

- GOV-272/273 与 `access-privacy.md` 的「如何避免 Agent 评测指标被『刷高』？」相邻。既有题写通用防刷分；本组只写编码场景的具体形态——改测试、加 skip 标记、放宽断言、写死返回值、只改被测函数签名等。
- 本文件**不收录代码定位准确率的评测题**：`platform-engineering.md` 已有「如何评估 Agent 定位代码上下文的准确率（如何设计离线评测集）？」，`coding-agent.md` 与 `sandbox-testing.md` 另有两道同主题题。
- GOV-275 与 `evaluation.md` 的「LLM-as-Judge 有哪些优缺点？」相邻。GOV-275 只写**评代码时**的特有失效：偏好长补丁、看不出语义等价、被注释误导、对陌生框架给低分等。
- GOV-259 与 Task 1/2 的沙箱题相邻。评测 harness 的隔离只写**评测特有的需求**（批量并行、结果可比、环境完全一致），沙箱本身的实现不在此展开。

- [ ] **Step 3: 验证**

```bash
python scripts/build_indexes.py && python scripts/validate.py
```

Expected: `All checks passed.`，`249  GOV  安全、治理与可观测性`，Total 1948。

- [ ] **Step 4: 提交**

```bash
git add docs/03-production/safety-governance-observability/
git commit -m "feat: 新增 Coding Agent 评测基准与评测集 30 题（GOV-252…281）"
```

---

### Task 6: Coding Agent 评测——线上指标与流程（GOV-282…311，30 题）

**Files:**
- Create: `docs/03-production/safety-governance-observability/coding-agent-evaluation-ops.md`
- Modify: `docs/03-production/safety-governance-observability/README.md`（脚本重写）

**Interfaces:**
- Consumes: Task 5 产出的 `coding-agent-evaluation.md`，末尾锚点 `gov-281`
- Produces: 锚点 `gov-282` … `gov-311`

- [ ] **Step 1: 写文件头**

```markdown
# Coding Agent 评测：线上指标与流程

> 所属章节：[安全、治理与可观测性](README.md)｜本文件共 **30** 题。
```

- [ ] **Step 2: 写 30 题**

| ID | 序号 | 标题 |
|---|---:|---|
| GOV-282 | 1 | 线上该采集哪些指标？PR 采纳率、回滚率与 Review 轮次如何定义？ |
| GOV-283 | 2 | 采纳率如何排除「改到能用」的伪采纳？ |
| GOV-284 | 3 | 如何度量 Agent 产出给 Review 带来的额外负担？ |
| GOV-285 | 4 | 交付速度提升与质量下降如何同时观测？ |
| GOV-286 | 5 | 如何把编码指标与团队的业务结果关联起来？ |
| GOV-287 | 6 | 离线 resolve rate 与线上采纳率对不上，如何排查这个落差？ |
| GOV-288 | 7 | 评测集与真实任务的分布差异如何量化？ |
| GOV-289 | 8 | 线上失败样本如何回流进评测集？ |
| GOV-290 | 9 | 用户中途放弃的会话算失败吗？如何定义与采集？ |
| GOV-291 | 10 | 影子运行在编码场景如何落地？ |
| GOV-292 | 11 | 模型或 Prompt 升级时，回归评测集如何设计才能挡住退化？ |
| GOV-293 | 12 | 发布门禁该卡哪些指标？它卡不住什么？ |
| GOV-294 | 13 | 灰度在编码场景如何切流：按用户、仓库还是任务类型？ |
| GOV-295 | 14 | 评测集会老化和过拟合，如何治理它自身的生命周期？ |
| GOV-296 | 15 | 供应商模型变更不可控时，如何持续监测能力漂移？ |
| GOV-297 | 16 | 每条样本都要跑构建和测试，如何做分层评测降本？ |
| GOV-298 | 17 | 单次运行不可复现时，小样本下如何判断版本提升是真的？ |
| GOV-299 | 18 | 一次评测要跑多少次才有把握？方差从哪里来？ |
| GOV-300 | 19 | 评测的时间与算力预算如何分配到不同阶段？ |
| GOV-301 | 20 | 如何用廉价代理指标做快速筛选、用贵指标做最终判定？ |
| GOV-302 | 21 | 如何评估 Agent 对既有代码风格与架构约定的遵守程度？ |
| GOV-303 | 22 | 安全维度如何评测：是否引入漏洞或泄露密钥？ |
| GOV-304 | 23 | 可维护性与可读性如何评？这些主观维度怎么控制方差？ |
| GOV-305 | 24 | 多个 Coding Agent 产品选型时，如何设计一次公平的对比评测？ |
| GOV-306 | 25 | 人工评审在评测体系里承担什么不可替代的作用？ |
| GOV-307 | 26 | Coding Agent 评测平台该由谁负责？与模型团队、平台团队如何分工？ |
| GOV-308 | 27 | 评测结果如何呈现才能驱动决策，而不是变成一块看板？ |
| GOV-309 | 28 | 评测数据的权限与保密如何设计？ |
| GOV-310 | 29 | 一次评测的完整可复现记录该包含什么？如何长期归档？ |
| GOV-311 | 30 | 评测体系自身如何被评估？怎么判断它是否有效？ |

**去重提醒**：

- GOV-303 与 `governance.md` 的「Agent 修改代码后如何保证不会引入安全漏洞？」相邻。既有题写**防护措施**；GOV-303 只写**如何评测**——用什么样本、什么判据、如何度量漏报与误报。
- GOV-306 与 `sandbox-testing.md` 的「如何设计 Agent 生成单测的人工抽检（Review）流程与抽样策略？」相邻。既有题是单测生成场景的抽检流程；GOV-306 写人工评审在**整个评测体系**中的定位——它补的是自动指标测不到的哪一类判断。
- GOV-292/293/294 与 `evaluation.md` 的「Agent 能力升级后如何验证效果提升？」「如何设计 A/B Test 评估 Agent 版本效果？」「企业级 Agent 上线前需要经过哪些评测流程？」相邻。本组必须落在编码场景的具体切面：回归集按仓库与任务类型构造、门禁卡不住的是什么、灰度按仓库切流的理由。
- GOV-307 与 `evaluation.md` 的「如何构建 Agent 评测平台（Evaluation Platform）？」相邻。既有题写平台架构；GOV-307 只写**组织与责任划分**。
- GOV-310 与 Task 9 的 GOV-386（OTel 埋点与自建评测共用数据）相邻。GOV-310 站在评测侧写归档记录的构成，GOV-386 站在埋点侧写数据如何被多方消费。

- [ ] **Step 3: 验证**

```bash
python scripts/build_indexes.py && python scripts/validate.py
```

Expected: `All checks passed.`，`279  GOV  安全、治理与可观测性`，Total 1978。

- [ ] **Step 4: 提交**

```bash
git add docs/03-production/safety-governance-observability/
git commit -m "feat: 新增 Coding Agent 线上评测指标与流程 30 题（GOV-282…311）"
```

---

### Task 7: DeepEval 评测框架（GOV-312…326，15 题）

**Files:**
- Create: `docs/03-production/safety-governance-observability/deepeval.md`
- Modify: `docs/03-production/safety-governance-observability/README.md`（脚本重写）

**Interfaces:**
- Consumes: Task 6 产出的 `coding-agent-evaluation-ops.md`，末尾锚点 `gov-311`
- Produces: 锚点 `gov-312` … `gov-326`

- [ ] **Step 1: 写文件头**

```markdown
# DeepEval 评测框架

> 所属章节：[安全、治理与可观测性](README.md)｜本文件共 **15** 题。
```

- [ ] **Step 2: 写 15 题**

| ID | 序号 | 标题 |
|---|---:|---|
| GOV-312 | 1 | DeepEval 解决了什么问题？与自己写脚本跑 LLM-as-Judge 有何不同？ |
| GOV-313 | 2 | LLMTestCase 的字段设计体现了什么评测范式？ |
| GOV-314 | 3 | G-Eval 是怎么工作的？与直接写一段打分 Prompt 有什么不同？ |
| GOV-315 | 4 | DeepEval 的 RAG 指标三件套分别度量什么？什么情况下会误判？ |
| GOV-316 | 5 | 指标阈值如何确定？为什么不能拍脑袋定？ |
| GOV-317 | 6 | EvaluationDataset 与 Golden 的关系是什么？为什么要区分？ |
| GOV-318 | 7 | 合成评测数据在什么场景可用、什么场景不可用？ |
| GOV-319 | 8 | DeepEval 的 pytest 集成意味着什么？评测何时该进 CI？ |
| GOV-320 | 9 | 组件级评测相比端到端评测能多发现什么？ |
| GOV-321 | 10 | 评测本身依赖 LLM，如何控制它的成本、方差与不确定性？ |
| GOV-322 | 11 | 多轮会话评测与单轮评测的差别在哪？ |
| GOV-323 | 12 | 工具调用与任务完成类指标适合评什么？对 Coding Agent 够用吗？ |
| GOV-324 | 13 | 框架内置的学术基准在企业场景有什么用、有什么误导？ |
| GOV-325 | 14 | 红队评测在 Agent 上如何组织？与常规评测是什么关系？ |
| GOV-326 | 15 | DeepEval 适配 Coding Agent 时，哪些指标能直接用、哪些必须自建？ |

**本任务的特殊约束——事实准确性**：

DeepEval 是一个持续演进的开源框架，其 API 面会变。写作时只讲**设计范式与工程判断**，不写具体的类名参数、版本号、默认阈值数值、导入路径。允许出现的名词限于稳定的概念层：`LLMTestCase` 的字段划分（输入、实际输出、期望输出、检索上下文）、G-Eval 的思维链评分范式、答案相关性 / 忠实度 / 上下文精确率与召回率这组 RAG 指标、`EvaluationDataset` 与 Golden 的分离、合成数据生成、pytest 风格的断言式评测、组件级评测、红队评测。

判断标准：如果一句话在框架下个版本改了参数名就会变错，那句话不该写。

**去重提醒**：

- GOV-314 与 `evaluation.md` 的「LLM-as-Judge 有哪些优缺点？」「如何降低大模型评测结果的主观性？」相邻。GOV-314 只写 G-Eval 这种**把评分标准展开成步骤再打分**的范式相比裸 Prompt 打分改善了什么、没改善什么。
- GOV-315 与 `rag/evaluation-governance.md` 及 `evaluation.md` 的「RAG 召回率与准确率如何评估？」相邻。GOV-315 只写这三个指标**在框架里的定义口径**与各自的误判场景，不重述 RAG 评测方法论。
- GOV-321 与 Task 6 的 GOV-298/299（评测方差与显著性）相邻。GOV-321 写的是**评判器本身**的方差与成本（judge 模型选择、温度、缓存、并发），GOV-298/299 写的是**被测系统**的方差。
- GOV-325 与 `prompt-security.md` 及 `governance.md` 的 Prompt Injection 题相邻。GOV-325 只写红队评测**作为评测活动**如何组织（用例来源、覆盖维度、通过标准），不写防御措施。

- [ ] **Step 3: 验证**

```bash
python scripts/build_indexes.py && python scripts/validate.py
```

Expected: `All checks passed.`，`294  GOV  安全、治理与可观测性`，Total 1993。

- [ ] **Step 4: 提交**

```bash
git add docs/03-production/safety-governance-observability/
git commit -m "feat: 新增 DeepEval 评测框架 15 题（GOV-312…326）"
```

---

### Task 8: OpenTelemetry 核心概念与数据模型（GOV-327…356，30 题）

**Files:**
- Create: `docs/03-production/safety-governance-observability/otel-basics.md`
- Modify: `docs/03-production/safety-governance-observability/README.md`（脚本重写）

**Interfaces:**
- Consumes: Task 7 产出的 `deepeval.md`，末尾锚点 `gov-326`
- Produces: 锚点 `gov-327` … `gov-356`；Task 9 从 `GOV-357` 在新文件续写

- [ ] **Step 1: 写文件头**

```markdown
# OpenTelemetry 核心概念与数据模型

> 所属章节：[安全、治理与可观测性](README.md)｜本文件共 **30** 题。
```

- [ ] **Step 2: 写 30 题**

| ID | 序号 | 标题 |
|---|---:|---|
| GOV-327 | 1 | OpenTelemetry 解决了什么问题？它与具体后端是什么关系？ |
| GOV-328 | 2 | Trace、Metric、Log 三大信号各自回答什么问题？ |
| GOV-329 | 3 | Profiling 等较新的信号在 OTel 中处于什么位置？ |
| GOV-330 | 4 | OTel 的 API 与 SDK 为什么要分开？ |
| GOV-331 | 5 | 引入 OTel 的成本有哪些？什么情况下不该上？ |
| GOV-332 | 6 | Span 的必备字段有哪些？各自的语义是什么？ |
| GOV-333 | 7 | SpanKind 有哪些取值？为什么需要区分？ |
| GOV-334 | 8 | Span Link 与父子关系有什么区别？什么时候必须用 Link？ |
| GOV-335 | 9 | Span Event 与独立的 Log 记录如何取舍？ |
| GOV-336 | 10 | Span Status 与异常记录应该怎么用？ |
| GOV-337 | 11 | W3C Trace Context 的 traceparent 与 tracestate 分别承担什么职责？ |
| GOV-338 | 12 | Baggage 是什么？滥用会带来什么问题？ |
| GOV-339 | 13 | 跨进程、跨线程与异步任务的 Context 如何正确传播？ |
| GOV-340 | 14 | 消息队列场景的 Context 传播有哪些坑？ |
| GOV-341 | 15 | Trace 断裂通常是什么原因造成的？如何检测？ |
| GOV-342 | 16 | TracerProvider、Tracer、SpanProcessor 与 Exporter 的职责如何划分？ |
| GOV-343 | 17 | 批量 SpanProcessor 的关键参数如何影响可靠性与内存？ |
| GOV-344 | 18 | Resource 该放什么？它与 Span 属性的边界在哪？ |
| GOV-345 | 19 | Instrumentation Scope 有什么用？ |
| GOV-346 | 20 | 自动埋点与手动埋点如何配合？自动埋点的局限是什么？ |
| GOV-347 | 21 | Counter、UpDownCounter、Gauge 与 Histogram 分别适用什么场景？ |
| GOV-348 | 22 | 同步仪器与异步（可观察）仪器的差别是什么？ |
| GOV-349 | 23 | Temporality 的 Delta 与 Cumulative 如何选择？ |
| GOV-350 | 24 | View 与聚合配置能解决什么问题？ |
| GOV-351 | 25 | Exemplar 如何把指标与 Trace 关联起来？ |
| GOV-352 | 26 | OTel 的 Logs 为什么走「桥接」路线？ |
| GOV-353 | 27 | 日志如何与 Trace 关联？需要哪些字段？ |
| GOV-354 | 28 | 语义约定为什么重要？不遵守会有什么后果？ |
| GOV-355 | 29 | 语义约定处在稳定与实验的不同阶段，工程上如何应对变更？ |
| GOV-356 | 30 | 属性命名与高基数问题如何治理？ |

**写作前必读**：题库现有三道 OpenTelemetry 题——`governance.md` 的「OpenTelemetry 在 Agent 系统中如何落地？」与「OpenTelemetry 在 Agent 中的应用方式？」，`observability.md` 的「OpenTelemetry 如何用于 Agent 监控？」。这三题都停留在「在 Agent 系统里怎么用」的概述层。

本文件是**规范与数据模型层**的系统覆盖，与那三题的关系类似「HTTP 协议规范」与「怎么用 HTTP 做 API」。写作时：

- 不重述「Agent 系统如何接入 OTel」这个整体命题——那是既有题的地盘，也是 Task 9 后两簇的地盘。
- 每题的落点是 OTel 自身的机制：字段语义、传播格式、SDK 组件职责、仪器类型、聚合与时间性、语义约定的治理。
- 举例可以用 Agent / LLM 场景，但结论必须是 OTel 通用的。

**篇幅提示**：这批题中有一部分（如 GOV-329、GOV-345）本身考点密度不高，写到 450 字即可，不要注水。考点密度不足的题宁可短，也不要靠展开无关背景凑字数。

- [ ] **Step 3: 验证**

```bash
python scripts/build_indexes.py && python scripts/validate.py
```

Expected: `All checks passed.`，`324  GOV  安全、治理与可观测性`，Total 2023。

> 本任务集中引入大量 OTel 术语（Span、Baggage、Resource、Exemplar、Temporality 等）。若 `validate.py` 报术语索引相关错误，在本任务内补跑一次：
> ```bash
> pwsh -File scripts/build_glossary.ps1 && python scripts/validate.py
> ```

- [ ] **Step 4: 提交**

```bash
git add docs/03-production/safety-governance-observability/ docs/reference/术语索引.md
git commit -m "feat: 新增 OpenTelemetry 核心概念与数据模型 30 题（GOV-327…356）"
```

---

### Task 9: OpenTelemetry Collector、采样与落地（GOV-357…386，30 题）

**Files:**
- Create: `docs/03-production/safety-governance-observability/otel-collector-ops.md`
- Modify: `docs/03-production/safety-governance-observability/README.md`（脚本重写）

**Interfaces:**
- Consumes: Task 8 产出的 `otel-basics.md`，末尾锚点 `gov-356`
- Produces: 锚点 `gov-357` … `gov-386`；本计划全部 255 题到此写完

- [ ] **Step 1: 写文件头**

```markdown
# OpenTelemetry Collector、采样与落地

> 所属章节：[安全、治理与可观测性](README.md)｜本文件共 **30** 题。
```

- [ ] **Step 2: 写 30 题**

| ID | 序号 | 标题 |
|---|---:|---|
| GOV-357 | 1 | Collector 的 Receiver、Processor、Exporter 与 Connector 如何组成 pipeline？ |
| GOV-358 | 2 | 为什么要用 Collector 而不是 SDK 直连后端？ |
| GOV-359 | 3 | 常用 Processor 各解决什么问题？编排顺序为什么重要？ |
| GOV-360 | 4 | Connector 能做什么？典型用法有哪些？ |
| GOV-361 | 5 | Collector 配置如何做灰度与回滚？ |
| GOV-362 | 6 | Agent 模式与 Gateway 模式如何选择？两者能否共存？ |
| GOV-363 | 7 | Collector 如何扩缩容？有状态处理器有什么约束？ |
| GOV-364 | 8 | 背压与丢数据发生在哪些环节？如何观测？ |
| GOV-365 | 9 | Collector 自身如何被监控？ |
| GOV-366 | 10 | 多集群、多区域的采集拓扑如何设计？ |
| GOV-367 | 11 | 头部采样与尾部采样各自的适用场景与代价是什么？ |
| GOV-368 | 12 | 一致性采样如何保证同一 Trace 不被拆散？ |
| GOV-369 | 13 | 尾部采样需要哪些资源？规模上限在哪？ |
| GOV-370 | 14 | 采样率如何确定？如何避免丢掉稀有错误？ |
| GOV-371 | 15 | 采样与指标准确性如何兼顾？ |
| GOV-372 | 16 | OTLP 相比厂商私有协议的价值是什么？ |
| GOV-373 | 17 | Trace 后端选型要看哪些能力？ |
| GOV-374 | 18 | OTel Metrics 接入 Prometheus 生态有哪些注意点？ |
| GOV-375 | 19 | 可观测数据的成本由什么驱动？有哪些有效的降本手段？ |
| GOV-376 | 20 | 从既有埋点体系迁移到 OTel 如何分阶段推进？ |
| GOV-377 | 21 | OTel 的 GenAI 语义约定覆盖了哪些内容？现状如何？ |
| GOV-378 | 22 | 一次 LLM 调用该建模成什么样的 Span？记录哪些属性？ |
| GOV-379 | 23 | 提示词与响应内容要不要进 Span？如何权衡合规与可调试性？ |
| GOV-380 | 24 | Token 与成本适合做成 Metric 还是 Span 属性？ |
| GOV-381 | 25 | 流式响应如何在 Span 上表达？TTFT 怎么记？ |
| GOV-382 | 26 | Agent 的多步执行如何映射到 OTel 的 Span 树？ |
| GOV-383 | 27 | 工具调用与检索步骤如何按语义约定建模？ |
| GOV-384 | 28 | 长时与异步 Agent 任务在 OTel 上有什么表达难题？ |
| GOV-385 | 29 | GenAI 场景的高基数与大属性如何治理？ |
| GOV-386 | 30 | OTel 埋点如何与自建评测、成本系统共用一套数据？ |

**去重提醒**：

- 后两簇（GOV-377…386）是本文件唯一的 GenAI 内容，与既有三道 OpenTelemetry 题、以及 Task 3/4 的 Coding Agent 观测题贴得最近。区分原则：**本组只回答「按 OTel 规范该怎么表达」，不回答「该观测什么」**。
  - GOV-378 写 LLM 调用的 Span 建模（SpanKind 取哪个、属性怎么命名、错误怎么标），不写「模型调用该记录哪些业务字段」——那是 `observability.md` 已有的内容。
  - GOV-382 写多步执行到 Span 树的**映射方法**（父子还是 Link、根 Span 放哪、异步怎么接），不写 Agent 该拆哪些步骤——那是 Task 3 的 GOV-193。
  - GOV-380 与 Task 3 的 GOV-207（Token 与缓存命中埋点）相邻。GOV-380 只回答**数据类型选择**：什么该进 Metric、什么该进 Span 属性、各自的查询代价。
  - GOV-385 与 Task 8 的 GOV-356（属性命名与高基数）相邻。GOV-356 写通用治理原则，GOV-385 只写 GenAI 特有的两个麻烦：模型名与会话 ID 这类天然高基数维度、提示词这类超大属性。
  - GOV-386 与 Task 6 的 GOV-310 相邻，分工见 Task 6 的去重提醒。
- GOV-374 与 `evaluation.md` 的「Prometheus 需要监控哪些指标？」相邻。既有题写监控哪些业务指标；GOV-374 只写 OTel Metrics 与 Prometheus 生态的**对接问题**（命名转换、Temporality 不匹配、直方图桶、拉取与推送）。

- [ ] **Step 3: 验证**

```bash
python scripts/build_indexes.py && python scripts/validate.py
```

Expected: `All checks passed.`，`354  GOV  安全、治理与可观测性`，Total 2053。

- [ ] **Step 4: 提交**

```bash
git add docs/03-production/safety-governance-observability/
git commit -m "feat: 新增 OpenTelemetry Collector 采样与落地 30 题（GOV-357…386）"
```

---

### Task 10: 重建生成物并更新导航

**Files:**
- Modify: `docs/03-production/engineering-platform/README.md`（头部描述行）
- Modify: `docs/03-production/safety-governance-observability/README.md`（头部描述行）
- Modify: `README.md`（Anki 卡片数、仓库结构树注释）
- Regenerate: `docs/reference/术语索引.md`
- Regenerate: `dist/anki/AgentInterview-完整题库.apkg`、`dist/anki/AgentInterview-核心100.apkg`

**Interfaces:**
- Consumes: Task 1–9 产出的全部 255 题

> `docs/README.md` 与 `docs/03-production/README.md` **不需要改**：本计划未新增章节，`validate_navigation_indexes()` 只校验章节级链接，两处导航已覆盖 ENG 与 GOV 章节。

- [ ] **Step 1: 重建术语索引**

```bash
pwsh -File scripts/build_glossary.ps1
```

255 题引入的新术语（OTel 的 Baggage、Exemplar、Temporality，评测的 fail-to-pass、pass@k，沙箱的 worktree、overlay 等）中，凡在「相关知识点」里累计出现 ≥5 次的都会被收进索引。

- [ ] **Step 2: 更新两个章节 README 的头部描述行**

`docs/03-production/engineering-platform/README.md` 第 3 行改为：

```markdown
> PromptOps、Coding Agent、代码检索、沙箱隔离与运维、测试交付、多模态和产品指标。
```

`docs/03-production/safety-governance-observability/README.md` 第 3 行改为：

```markdown
> 幻觉治理、安全权限、评测与 DeepEval、全链路观测、OpenTelemetry、审计和事件响应。
```

> 「本章共 N 题」那一行与「## 子主题」表格由 `build_indexes.py` 重写，不要手改。

- [ ] **Step 3: 重建 Anki 卡组**

```bash
python scripts/build_anki.py
```

Expected: `dist/anki/` 下两个 `.apkg` 重新生成。

- [ ] **Step 4: 更新根 `README.md` 的 Anki 卡片数**

把 `**1,798 张卡片**` 改为 `**2,053 张卡片**`。核心 100 那一行不变。

> 首段的 `现收录 **1,798 道问题及参考答案**` 与「内容导航」统计表由 `build_indexes.py` 自动重写，**不要手改**。

- [ ] **Step 5: 更新根 `README.md` 的仓库结构树注释**

`03-production` 那一行改为：

```text
│  ├─ 03-production/     # 模型成本、安全治理与可观测、评测、工程平台
```

- [ ] **Step 6: 最终验证**

```bash
python scripts/build_indexes.py --check && python scripts/validate.py
```

Expected: `Generated indexes are up to date.` 与 `All checks passed.`，统计表末行 `Total: 2053`，其中 `257  ENG` 与 `354  GOV`。

再确认九个新文件的题数与文件头声明一致：

```bash
for f in docs/03-production/engineering-platform/coding-agent-sandbox.md \
         docs/03-production/engineering-platform/coding-agent-sandbox-ops.md \
         docs/03-production/safety-governance-observability/coding-agent-observability.md \
         docs/03-production/safety-governance-observability/coding-agent-observability-metrics.md \
         docs/03-production/safety-governance-observability/coding-agent-evaluation.md \
         docs/03-production/safety-governance-observability/coding-agent-evaluation-ops.md \
         docs/03-production/safety-governance-observability/deepeval.md \
         docs/03-production/safety-governance-observability/otel-basics.md \
         docs/03-production/safety-governance-observability/otel-collector-ops.md; do
  printf "%-78s 实际 %2s  声明 %s\n" "$(basename $f)" \
    "$(grep -c '^### ' $f)" "$(grep -o '本文件共 \*\*[0-9]*\*\* 题' $f | grep -o '[0-9]*')"
done
```

Expected: 九行的「实际」与「声明」两列全部相等，依次为 30 30 30 30 30 30 15 30 30。

- [ ] **Step 7: 提交**

```bash
git add README.md docs/ dist/anki/
git commit -m "docs: 题库统计、术语索引与 Anki 卡组同步至 2053 题"
```

---

## Self-Review

**Spec coverage**

| Spec 章节 | 对应任务 |
|---|---|
| 一、文件布局 | Task 1–9 的 Files 块；File Structure 表 |
| 二、稳定 ID 分配 | 各任务的对照表；File Structure 的任务与 Total 对照 |
| 三、归属依据 | 已落实为 Task 1–2 写 ENG、Task 3–9 写 GOV |
| 四、完整题目清单（255 题） | Task 1–9 的对照表逐条照抄 |
| 五、写作约束 | Global Constraints |
| 六、去重基线（15 条） | 分配到各任务的「写作前必读」与「去重提醒」 |
| 七、执行顺序 | Task 1→10 |
| 八、风险 | 已内联到各任务的验证步骤与去重提醒 |

**执行中发现并已修正的问题**

1. **答案篇幅**：spec 只说「密度对齐仓库现有水平」，没给数字。实测本计划涉及的两个章节：`observability.md` 中位数 606 字、`evaluation.md` 601 字、`coding-agent.md` 577 字，最长 855。已在 Global Constraints 定为 450–700 字、复杂题到 800。这与上一份计划给产品专题章节定的 250–550 字**不是同一个标准**，已明确标注避免误用。

2. **术语索引的重建时机**：spec 的执行顺序把 `build_glossary.ps1` 放在全部写完之后。但 `validate_glossary()` 每次都跑，中途若某新术语跨过 5 次阈值就会报错。已明确：默认只在 Task 10 跑一次，中途报错时在当前任务内补跑（Task 8 因集中引入 OTel 术语，最可能触发，已单独标注）。

3. **根 README 哪些是自动的**：spec 说「手工更新根 README.md 的题量数字与 Anki 卡片数」。实际上 `build_indexes.py` 的 `replace_stats()` 已用正则重写了 `现收录 **N 道`，手改反而会被脚本覆盖。Task 10 已改为只手改 Anki 卡片数与结构树注释。

4. **`docs/README.md` 是否要改**：spec 说不需要改，已核对 `validate_navigation_indexes()` 只校验章节级 README 链接，本计划未新增章节，确认不需要改，并在 Task 10 显式说明避免执行者多改。

5. **ENG-260 与 GOV-237 的 SLO 撞车**：spec 的去重基线没覆盖到这对。两题都叫「SLO 该怎么定」，分属沙箱基础设施与 Agent 产品两层。已在 Task 4 的去重提醒里写明分工。

6. **GOV-310 与 GOV-386 的数据共用撞车**：spec 第六节未覆盖。已在 Task 6 与 Task 9 双向标注分工（评测侧写归档构成，埋点侧写多方消费）。

7. **题数与 Total 自洽**：30×8 + 15 = 255；1798 + 255 = 2053；ENG 197+60=257；GOV 159+195=354。各任务的预期 Total 递增值与本任务题数一致。

8. **ID 连续性**：ENG-203…262 共 60 个、GOV-192…386 共 195 个，均无缺口，文件内数字严格递增。已在写 spec 时用脚本校验过，标题与既有 1,798 题零冲突、255 题内部零重复。

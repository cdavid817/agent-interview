# Agent Interview

[![Validate](https://github.com/cdavid817/agent-interview/actions/workflows/validate.yml/badge.svg)](https://github.com/cdavid817/agent-interview/actions/workflows/validate.yml)

一套面向 **AI Agent / 大模型应用工程师** 的中文面试题库，覆盖架构、任务执行、上下文、工具、多 Agent、模型、安全、工程落地、RAG、Transformer、OpenClaw 和 Claude Code 十二个方向。

项目当前收录 **1,840 道问题及参考答案**。内容强调工程边界、失败处理、验证指标和生产实践，不把模型生成的设计推演当成产品已实现能力。

## 内容导航

| 章节 | 题数 | 主要内容 |
|---|---:|---|
| [一、Agent 核心架构](docs/一、Agent核心架构.md) | 87 | 分层架构、Runtime、Harness、框架与平台化 |
| [二、任务规划与执行](docs/二、任务规划与执行.md) | 307 | 任务识别、规划、ReAct、Reflection、恢复 |
| [三、上下文与知识系统](docs/三、上下文与知识系统.md) | 206 | Context、Memory、状态恢复、压缩与权限 |
| [四、工具与能力体系](docs/四、工具与能力体系.md) | 237 | Tool Calling、MCP、鉴权、沙箱、幂等 |
| [五、多 Agent 与协作](docs/五、多Agent与协作.md) | 34 | 选型、Supervisor、通信、冲突和协作评测 |
| [六、模型能力与成本](docs/六、模型能力与成本.md) | 160 | 路由、缓存、Token、微调、流式输出 |
| [七、安全、治理与可观测性](docs/七、安全、治理与可观测性.md) | 191 | 幻觉、注入、权限、评测、Tracing、SLO |
| [八、工程落地与平台化](docs/八、工程落地与平台化.md) | 202 | PromptOps、Coding Agent、单测、多模态、KPI |
| [九、RAG](docs/九、RAG.md) | 200 | 切分、Embedding、混合召回、重排、索引与评测 |
| [十、Transformer](docs/十、Transformer.md) | 60 | Attention、位置编码、MoE、长上下文与推理优化 |
| [十一、OpenClaw](docs/十一、OpenClaw.md) | 56 | Gateway、渠道、记忆、工具、沙箱、自动化与生产治理 |
| [十二、Claude Code](docs/十二、ClaudeCode.md) | 100 | Agent Loop、消息生命周期、上下文原理、Prompt Cache、权限、Hooks、MCP 与 Agent SDK |
| **合计** | **1,840** |  |

## 如何使用

### 快速准备

1. 先阅读“Agent 核心架构”前 10 题，形成系统全景。
2. 从目标岗位相关章节挑选 30～50 题，先独立口述，再对照参考答案。
3. 每道题按“结论—机制—权衡—风险—指标”组织 2～5 分钟回答。
4. 将自己做过的项目、数据规模、故障案例和取舍补充进去，避免只背通用模板。

### 建议学习路径

- **入门**：核心架构 → Transformer 基础 → Tool Calling → Context/Memory → RAG 基础。
- **进阶**：状态与恢复 → 混合检索与重排 → 多模型路由 → MCP → 多 Agent → 评测与可观测。
- **高级/架构岗**：RAG 生产治理 → 推理优化 → 多租户平台 → 成本与容量 → 安全治理 → Coding Agent → 业务 KPI。

### 模拟面试

- 随机抽取一道题，限制 3 分钟回答。
- 追问“为什么这样设计”“失败怎么办”“如何验证”“规模扩大十倍怎么办”。
- 用真实项目替换答案中的通用组件，并给出至少一个量化指标。

## 内容原则

- **事实与方案分开**：产品、协议和框架能力以官方资料为准；未实现功能或架构推演明确标注为建议。
- **证据优先**：完成与正确性优先由测试、规则、业务状态和引用验证，不以模型自评为准。
- **不展示隐藏思维链**：可观测性记录计划、决策摘要、工具、证据和结果。
- **时效性**：模型价格、上下文上限、产品功能和协议会变化，使用前请核对版本与日期。
- **非唯一答案**：题库提供的是回答框架，不代替候选人的项目经验和独立判断。

## 仓库结构

```text
agent-interview/
├─ README.md
├─ CONTRIBUTING.md
├─ Agent 名词解释.md      # 全部题目相关知识点分类索引
├─ docs/                  # 十二个主题题库
├─ scripts/build_glossary.ps1
├─ scripts/validate.py    # 题号、格式和统计校验
└─ .github/               # CI 与内容纠错模板
```

## 本地校验

需要 Python 3.9 或更高版本：

```bash
pwsh -File scripts/build_glossary.ps1
python scripts/validate.py
```

第一条命令从全部章节同步“相关知识点”到分类术语表。校验内容包括文件是否齐全、题号是否连续、题目与答案是否为空、章节题数和总题数是否正确、名词解释覆盖是否完整，以及 README 本地链接是否有效。

## 参与贡献

欢迎补充真实面试题、修正事实错误、更新过时产品能力或改进答案。提交前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。如果发现模型幻觉或协议描述不准确，可使用“内容纠错”Issue 模板，并尽量附上官方资料。

## License

本项目采用 [MIT License](LICENSE)。

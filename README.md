# Agent Interview

[![Validate](https://github.com/cdavid817/agent-interview/actions/workflows/validate.yml/badge.svg)](https://github.com/cdavid817/agent-interview/actions/workflows/validate.yml)

面向 **AI Agent / 大模型应用工程师** 的中文面试题库，现收录 **1,781 道问题及参考答案**。内容强调工程边界、失败处理、验证指标和生产实践。

题库采用“领域 → 章节 → 子主题 → 稳定题目 ID”结构。旧版十二个大文件保留迁移入口，新增引用请使用 `ARC-001`、`PLAN-001` 等稳定 ID。

## 开始使用

- [题库总导航](docs/README.md)
- [学习路径](docs/00-guide/learning-paths.md)
- [核心 100 题](docs/00-guide/core-100.md)
- [回答与评分框架](docs/00-guide/answer-rubric.md)
- [贡献指南](CONTRIBUTING.md)
- [重复题候选报告](docs/reference/duplicate-questions.md)
- [稳定 ID 合并映射](docs/reference/id-aliases.md)
- [术语索引](docs/reference/术语索引.md)

## 导入 Anki

仓库已提供可直接导入的 Anki 卡组：

- [AgentInterview-完整题库.apkg](dist/anki/AgentInterview-完整题库.apkg)：**1,738 张卡片**，包含当前全部面试题。
- [AgentInterview-核心100.apkg](dist/anki/AgentInterview-核心100.apkg)：**100 张卡片**，适合先建立知识主干。

下载后双击 `.apkg` 文件，在 Anki 中确认导入即可。两份卡组包含重复的稳定题目 ID，请选择其中一份导入，不要同时导入。

卡片正面为问题，背面包含核心思路、可展开的深入拆解、相关知识点和题目来源。标签支持按领域、章节、知识点、面试来源以及 `set::核心100` 筛选。

题库更新后，可安装依赖并重新生成卡组：

```powershell
python -m pip install genanki markdown
python scripts/build_anki.py
```

生成结果位于 `dist/anki/`。卡片以稳定题目 ID 生成唯一标识，重新导入完整包可更新已有笔记，避免重复卡片。

## 内容导航

<!-- QUESTION_STATS_START -->
| 领域 | 章节 | 题数 |
|---|---|---:|
| 基础原理 | [Agent 核心架构](docs/01-foundations/agent-architecture/README.md) | 92 |
| 基础原理 | [Transformer](docs/01-foundations/transformer/README.md) | 60 |
| 核心能力 | [任务规划与执行](docs/02-capabilities/planning-execution/README.md) | 299 |
| 核心能力 | [上下文与知识系统](docs/02-capabilities/context-knowledge/README.md) | 197 |
| 核心能力 | [工具、Skills 与 MCP](docs/02-capabilities/tools-skills-mcp/README.md) | 221 |
| 核心能力 | [多 Agent 与协作](docs/02-capabilities/multi-agent/README.md) | 38 |
| 核心能力 | [RAG](docs/02-capabilities/rag/README.md) | 197 |
| 生产工程 | [模型能力与成本](docs/03-production/model-capability-cost/README.md) | 123 |
| 生产工程 | [安全、治理与可观测性](docs/03-production/safety-governance-observability/README.md) | 159 |
| 生产工程 | [工程落地与平台化](docs/03-production/engineering-platform/README.md) | 197 |
| 产品专题 | [OpenClaw](docs/04-products/openclaw/README.md) | 56 |
| 产品专题 | [Claude Code](docs/04-products/claude-code/README.md) | 117 |
| 产品专题 | [OpenCode](docs/04-products/opencode/README.md) | 25 |
|  | **合计** | **1,781** |
<!-- QUESTION_STATS_END -->

## 仓库结构

```text
agent-interview/
├─ README.md
├─ CONTRIBUTING.md
├─ docs/
│  ├─ 00-guide/          # 学习路径、评分框架和题目规范
│  ├─ 01-foundations/    # Agent 架构、Transformer
│  ├─ 02-capabilities/   # 规划、上下文、工具、多 Agent、RAG
│  ├─ 03-production/     # 模型成本、安全治理、工程平台
│  ├─ 04-products/       # OpenClaw、Claude Code
│  └─ reference/         # 重复题报告与术语索引
└─ scripts/              # 迁移、索引生成和结构校验
```

## 本地校验

需要 Python 3.9 或更高版本：

```bash
python scripts/build_indexes.py --check
python scripts/validate.py
```

术语发生变化时运行：

```powershell
pwsh -File scripts/build_glossary.ps1
```

## 内容原则

- **事实与方案分开**：区分官方已实现能力、配置能力、工程建议和未来提案。
- **证据优先**：以测试、规则、业务状态和引用验证结果，不以模型自评为准。
- **不展示隐藏思维链**：记录计划、决策摘要、工具、证据和结果即可。
- **时效性**：模型价格、上下文上限和产品能力使用前应核对版本与日期。
- **非唯一答案**：参考答案提供回答框架，不能代替候选人的真实项目经验。

## License

本项目采用 [MIT License](LICENSE)。

#!/usr/bin/env python3
"""One-time migration from flat chapter files to a topic-oriented question bank."""

from __future__ import annotations

import re
import os
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
MAX_QUESTIONS_PER_FILE = 50
QUESTION_RE = re.compile(r"^####\s+(\d+)、(.+?)\s*$", re.MULTILINE)
REFERENCE_RE = re.compile(r"^##\s+.*(?:核验资料|参考资料).*?$", re.MULTILINE)


CHAPTERS = [
    {
        "legacy": "一、Agent核心架构.md",
        "area": "01-foundations",
        "slug": "agent-architecture",
        "prefix": "ARC",
        "title": "Agent 核心架构",
        "summary": "企业级 Agent 分层架构、Runtime、Harness、框架选型与平台边界。",
        "topics": [
            ("frameworks", "框架选型", r"LangChain|LangGraph|AutoGen|CrewAI|Semantic Kernel|框架|OpenCode"),
            ("platform", "平台化与规模化", r"平台|中台|多租户|千万|业务线|私有化|计费|资源隔离|高可用|容灾|灰度|A/B|模型网关"),
            ("runtime-harness", "Runtime 与 Harness", r"Runtime|Harness|运行链路|规划器|执行器|状态机|Agent Loop"),
            ("reliability", "可靠性与治理", r"失败|重试|降级|恢复|评估|可观测|安全|权限|成本|Token|幻觉"),
            ("architecture", "整体架构与模块边界", r".*"),
        ],
    },
    {
        "legacy": "二、任务规划与执行.md",
        "area": "02-capabilities",
        "slug": "planning-execution",
        "prefix": "PLAN",
        "title": "任务规划与执行",
        "summary": "任务识别、规划拆解、推理模式、工作流、失败恢复与结果验证。",
        "topics": [
            ("task-routing", "任务识别与复杂度路由", r"任务识别|意图|复杂度|简单任务|复杂任务|是否需要拆|澄清|路由"),
            ("reasoning-patterns", "ReAct、Reflection 与推理模式", r"ReAct|Reflection|反思|CoT|思维链|Tree of Thoughts|Graph of Thoughts|ToT|GoT|MCTS|Self-"),
            ("recovery", "失败恢复与重规划", r"失败|重试|恢复|回滚|补偿|断点|Checkpoint|超时|死锁|Replan|重规划|幂等"),
            ("verification", "完成判定与执行评测", r"完成|验证|验收|评估|质量|终止|停止条件|成功率|Judge"),
            ("workflow", "工作流、状态与调度", r"Workflow|工作流|状态机|编排|调度|并行|队列|优先级|DAG|依赖|关键路径"),
            ("planning", "规划、拆解与执行", r".*"),
        ],
    },
    {
        "legacy": "三、上下文与知识系统.md",
        "area": "02-capabilities",
        "slug": "context-knowledge",
        "prefix": "CTX",
        "title": "上下文与知识系统",
        "summary": "上下文工程、会话状态、记忆、压缩缓存、知识接入与治理。",
        "topics": [
            ("memory", "记忆系统", r"记忆|Memory|遗忘|画像|长期|短期记忆|Episodic"),
            ("compression-cache", "上下文压缩与缓存", r"压缩|摘要|裁剪|Token|窗口|Cache|缓存|Lost in the Middle"),
            ("session-state", "会话与任务状态", r"Session|会话|状态|Checkpoint|恢复|持久化"),
            ("knowledge-retrieval", "知识接入与检索", r"RAG|检索|Embedding|向量|知识库|索引|召回"),
            ("governance", "上下文安全与治理", r"权限|安全|污染|注入|隐私|隔离|治理|审计"),
            ("context-engineering", "Context Engineering 与组装", r".*"),
        ],
    },
    {
        "legacy": "四、工具与能力体系.md",
        "area": "02-capabilities",
        "slug": "tools-skills-mcp",
        "prefix": "TOOL",
        "title": "工具、Skills 与 MCP",
        "summary": "工具契约、执行治理、MCP、沙箱以及 Skill 的发现、编排和生命周期。",
        "topics": [
            ("skill-governance", "Skill 生命周期与治理", r"Skill.*(?:版本|市场|Marketplace|Registry|注册|共享|复用|权限|依赖|发布|回滚|运营|资产|沉淀|Store)|(?:版本|市场|注册|共享|复用|权限|依赖|发布|回滚|运营).*Skill"),
            ("skill-routing", "Skill 发现、检索与路由", r"Skill.*(?:匹配|路由|Router|召回|检索|选择|推荐|发现|语义|重叠)|(?:匹配|路由|召回|检索|选择|推荐|发现).*Skill"),
            ("skill-workflows", "Workflow Skill 与能力编排", r"Skill.*(?:Workflow|工作流|编排|DAG|嵌套|多个|拆分|上下文|传递)|(?:Workflow|工作流|编排|DAG|嵌套).*Skill"),
            ("skill-concepts", "Skill 概念与设计", r"Skill"),
            ("mcp", "MCP 与协议接入", r"MCP|Function Calling|协议|Resources|Prompts|stdio|SSE"),
            ("sandbox-security", "沙箱、权限与高风险操作", r"沙箱|Shell|SQL|危险|权限|鉴权|安全|审批|确认|注入|隔离"),
            ("reliability", "工具执行可靠性", r"失败|重试|降级|超时|熔断|幂等|恢复|回滚|日志|追踪"),
            ("tool-platform", "工具注册、路由与执行", r".*"),
        ],
    },
    {
        "legacy": "五、多Agent与协作.md",
        "area": "02-capabilities",
        "slug": "multi-agent",
        "prefix": "MULTI",
        "title": "多 Agent 与协作",
        "summary": "单/多 Agent 选型、任务分派、通信状态、冲突处理与协作评测。",
        "topics": [
            ("selection-architecture", "选型与角色架构", r"单Agent|单 Agent|架构|角色|Supervisor|中心化|去中心化"),
            ("orchestration", "任务分派与协作编排", r"分派|编排|调度|并行|委派|拆解|路由"),
            ("communication-state", "通信、上下文与共享状态", r"通信|消息|上下文|共享|状态|黑板|协议"),
            ("conflict-reliability", "冲突、容错与一致性", r"冲突|失败|容错|恢复|一致性|死锁|重试|隔离"),
            ("evaluation", "协作效果与评测", r"评估|评测|指标|效果|成本|收益"),
            ("multi-agent-basics", "多 Agent 基础", r".*"),
        ],
    },
    {
        "legacy": "六、模型能力与成本.md",
        "area": "03-production",
        "slug": "model-capability-cost",
        "prefix": "MODEL",
        "title": "模型能力与成本",
        "summary": "模型接入与路由、缓存、成本、评测、微调、流式输出和容量治理。",
        "topics": [
            ("routing-fallback", "模型路由与降级", r"路由|切换|Fallback|熔断|多模型|厂商|模型选择|升级到大模型"),
            ("cost-token", "Token 与成本治理", r"成本|Token|预算|计费|价格|配额"),
            ("cache", "模型缓存", r"Cache|缓存"),
            ("evaluation", "模型评测与实验", r"评测|评估|A/B|Benchmark|效果|Judge"),
            ("finetuning", "微调、蒸馏与模型适配", r"微调|LoRA|蒸馏|SFT|RLHF|DPO|训练"),
            ("streaming-capacity", "流式输出与容量规划", r"流式|并发|吞吐|容量|限流|排队|GPU|延迟"),
            ("model-engineering", "模型工程综合", r".*"),
        ],
    },
    {
        "legacy": "七、安全、治理与可观测性.md",
        "area": "03-production",
        "slug": "safety-governance-observability",
        "prefix": "GOV",
        "title": "安全、治理与可观测性",
        "summary": "幻觉治理、安全权限、评测、全链路观测、审计和事件响应。",
        "topics": [
            ("hallucination", "幻觉与事实可靠性", r"幻觉|事实|Ground|引用|置信度"),
            ("prompt-security", "Prompt 与内容安全", r"Prompt Injection|提示词注入|越狱|内容安全|极端情绪|敏感"),
            ("access-privacy", "权限、隐私与合规", r"权限|鉴权|隐私|合规|租户|数据泄露|最小权限|RBAC|ABAC|审计"),
            ("evaluation", "评测与质量治理", r"评测|评估|完成率|准确率|Judge|红队|测试集|指标"),
            ("observability", "Tracing、监控与 SLO", r"可观测|追踪|Tracing|Trace|日志|监控|告警|SLO|SLA|指标|回放"),
            ("incident-reliability", "故障恢复与事件响应", r"失败|恢复|重试|降级|熔断|回滚|事故|应急|容灾|高可用"),
            ("governance", "治理体系综合", r".*"),
        ],
    },
    {
        "legacy": "八、工程落地与平台化.md",
        "area": "03-production",
        "slug": "engineering-platform",
        "prefix": "ENG",
        "title": "工程落地与平台化",
        "summary": "PromptOps、Coding Agent、代码检索、沙箱测试、多模态和产品指标。",
        "topics": [
            ("promptops", "PromptOps 与配置治理", r"Prompt|提示词|模板|配置|版本"),
            ("coding-agent", "Coding Agent 架构与执行", r"Coding Agent|代码生成|代码修改|Code Review|Bug Fix|仓库|IDE"),
            ("code-search", "代码理解与检索", r"代码检索|AST|调用图|符号|Embedding|索引|Repository"),
            ("sandbox-testing", "沙箱、测试与交付", r"Docker|Sandbox|沙箱|单测|测试|CI/CD|构建|验证|部署"),
            ("multimodal", "多模态 Agent", r"多模态|图片|图像|语音|视频|OCR|VLM"),
            ("product-metrics", "产品指标、KPI 与 ROI", r"KPI|ROI|用户|留存|满意度|产品|业务指标|成本"),
            ("platform-engineering", "平台工程综合", r".*"),
        ],
    },
    {
        "legacy": "九、RAG.md",
        "area": "02-capabilities",
        "slug": "rag",
        "prefix": "RAG",
        "title": "RAG",
        "summary": "文档处理、向量表示、检索重排、索引更新、生成和生产评测。",
        "topics": [
            ("ingestion-chunking", "文档解析与切分", r"文档|解析|切分|Chunk|分块|表格|PDF|OCR"),
            ("embedding-vector", "Embedding 与向量数据库", r"Embedding|向量|HNSW|Milvus|FAISS|维度|相似度"),
            ("retrieval", "召回与混合检索", r"召回|检索|BM25|Hybrid|关键词|Query|TopK|Top-K"),
            ("reranking", "重排与结果融合", r"Rerank|重排|RRF|Cross-Encoder|融合|MMR"),
            ("index-freshness", "索引更新与知识新鲜度", r"索引|更新|增量|实时|删除|版本|新鲜|一致性"),
            ("generation-grounding", "生成、引用与幻觉治理", r"生成|幻觉|引用|证据|Ground|上下文组装"),
            ("evaluation-governance", "RAG 评测与生产治理", r"评测|评估|指标|权限|安全|成本|延迟|生产|监控"),
            ("rag-basics", "RAG 基础与架构", r".*"),
        ],
    },
    {
        "legacy": "十、Transformer.md",
        "area": "01-foundations",
        "slug": "transformer",
        "prefix": "TRANS",
        "title": "Transformer",
        "summary": "表示、Attention、网络结构、MoE、长上下文和推理优化。",
        "topics": [
            ("tokens-position", "Token、Embedding 与位置编码", r"Token|Embedding|位置编码|RoPE|ALiBi|输入|向量"),
            ("attention", "Attention 机制", r"Attention|QKV|Multi-Head|Self-Attention|Mask"),
            ("architecture-training", "网络结构与训练", r"Encoder|Decoder|FFN|归一化|LayerNorm|RMSNorm|残差|训练|梯度|Softmax"),
            ("moe", "MoE", r"MoE|专家|Router"),
            ("long-context", "长上下文与 KV Cache", r"长上下文|KV Cache|Context|窗口"),
            ("inference", "推理与性能优化", r"推理|量化|吞吐|显存|Prefill|Decode|投机|FlashAttention"),
            ("transformer-basics", "Transformer 基础", r".*"),
        ],
    },
    {
        "legacy": "十一、OpenClaw.md",
        "area": "04-products",
        "slug": "openclaw",
        "prefix": "OCLAW",
        "title": "OpenClaw",
        "summary": "OpenClaw 的 Gateway、Runtime、会话记忆、工具插件、自动化与生产治理。",
        "topics": [
            ("architecture-runtime", "架构、Gateway 与 Runtime", r"定位|架构|Gateway|Runtime|运行|控制面|工作区"),
            ("channels-sessions", "渠道、会话与路由", r"渠道|Channel|消息|会话|Session|路由|群聊"),
            ("memory-context", "记忆与上下文", r"记忆|Memory|上下文|Context|Prompt"),
            ("tools-plugins", "工具、Skills 与 Plugins", r"工具|Tool|Skill|Plugin|MCP|浏览器|节点"),
            ("automation-multi-agent", "自动化与多 Agent", r"Cron|Heartbeat|自动化|多 Agent|协作|并行"),
            ("security-operations", "安全与生产运维", r"沙箱|安全|权限|部署|监控|高可用|容错|模型切换|成本|治理"),
            ("openclaw-basics", "OpenClaw 综合", r".*"),
        ],
    },
    {
        "legacy": "十二、ClaudeCode.md",
        "area": "04-products",
        "slug": "claude-code",
        "prefix": "CC",
        "title": "Claude Code",
        "summary": "Claude Code 的 Agent Loop、上下文、工具权限、Hooks、MCP、Subagents 与 SDK。",
        "topics": [
            ("agent-loop", "产品定位与 Agent Loop", r"定位|Agent Loop|循环|生命周期|请求|消息"),
            ("context-cache", "上下文与 Prompt Cache", r"上下文|Context|Prompt Cache|缓存|压缩|CLAUDE\.md|记忆"),
            ("tools-permissions", "工具、权限与安全", r"工具|权限|沙箱|安全|Bash|文件|Checkpoint"),
            ("hooks-mcp", "Hooks、MCP 与扩展", r"Hook|MCP|Plugin|Skill|扩展|SDK"),
            ("subagents-teams", "Subagents 与 Agent Teams", r"Subagent|子 Agent|Agent Team|多 Agent|协作"),
            ("engineering-operations", "工程集成与企业治理", r"CI/CD|IDE|GitHub|部署|企业|治理|监控|成本|审计"),
            ("claude-code-basics", "Claude Code 综合", r".*"),
        ],
    },
]


def clean_body(body: str) -> str:
    body = re.sub(r"(?m)^#{1,3}\s+.*?\s*$", "", body)
    body = re.sub(r"(?m)^\s*---\s*$", "", body)
    return re.sub(r"\n{3,}", "\n\n", body).strip()


def parse_questions(path: Path) -> tuple[list[dict[str, str | int]], str]:
    text = path.read_text(encoding="utf-8-sig")
    matches = list(QUESTION_RE.finditer(text))
    if not matches:
        raise ValueError(f"No questions found in {path}")
    reference_match = REFERENCE_RE.search(text, matches[-1].end())
    content_end = reference_match.start() if reference_match else len(text)
    references = text[reference_match.start():].strip() if reference_match else ""
    questions: list[dict[str, str | int]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else content_end
        questions.append(
            {
                "number": int(match.group(1)),
                "title": match.group(2).strip(),
                "body": clean_body(text[match.end():end]),
            }
        )
    return questions, references


def classify(question: dict[str, str | int], topics: list[tuple[str, str, str]]) -> tuple[str, str]:
    body = str(question["body"])
    related = " ".join(re.findall(r"相关知识点[：:]\s*\**\s*(.+)$", body, re.MULTILINE))
    haystack = f"{question['title']} {related}"
    for slug, title, pattern in topics:
        if re.search(pattern, haystack, re.IGNORECASE):
            return slug, title
    raise AssertionError("Every chapter must have a catch-all topic")


def relative_link(from_path: Path, to_path: Path) -> str:
    return Path(*([".."] * len(from_path.parent.relative_to(ROOT).parts))).joinpath(
        to_path.relative_to(ROOT)
    ).as_posix()


def write_chapter(chapter: dict[str, object], questions: list[dict[str, str | int]], references: str) -> list[dict[str, object]]:
    chapter_dir = DOCS / str(chapter["area"]) / str(chapter["slug"])
    chapter_dir.mkdir(parents=True, exist_ok=True)
    grouped: dict[tuple[str, str], list[dict[str, str | int]]] = defaultdict(list)
    records: list[dict[str, object]] = []
    for question in questions:
        topic = classify(question, chapter["topics"])  # type: ignore[arg-type]
        grouped[topic].append(question)

    index_rows: list[str] = []
    for topic_slug, topic_title, _ in chapter["topics"]:  # type: ignore[assignment]
        topic_questions = grouped.get((topic_slug, topic_title), [])
        for part_index, offset in enumerate(range(0, len(topic_questions), MAX_QUESTIONS_PER_FILE), 1):
            chunk = topic_questions[offset:offset + MAX_QUESTIONS_PER_FILE]
            suffix = f"-{part_index}" if len(topic_questions) > MAX_QUESTIONS_PER_FILE else ""
            filename = f"{topic_slug}{suffix}.md"
            path = chapter_dir / filename
            display_title = f"{topic_title}（{part_index}）" if suffix else topic_title
            lines = [
                f"# {display_title}",
                "",
                f"> 所属章节：[{chapter['title']}](README.md)｜本文件共 **{len(chunk)}** 题。",
                "",
            ]
            for index, question in enumerate(chunk, 1):
                stable_id = f"{chapter['prefix']}-{int(question['number']):03d}"
                lines.extend(
                    [
                        f'<a id="{stable_id.lower()}"></a>',
                        f"### {index}. {question['title']}",
                        "",
                        str(question["body"]),
                        "",
                    ]
                )
                records.append(
                    {
                        "id": stable_id,
                        "title": str(question["title"]),
                        "chapter": str(chapter["title"]),
                        "topic": topic_title,
                        "path": path,
                    }
                )
            path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
            index_rows.append(f"| [{display_title}]({filename}) | {len(chunk)} | `{chunk[0]['number']}`–`{chunk[-1]['number']}` |")

    if references:
        reference_path = chapter_dir / "references.md"
        reference_path.write_text(f"# {chapter['title']}核验资料\n\n{references}\n", encoding="utf-8")

    chapter_index = [
        f"# {chapter['title']}",
        "",
        f"> {chapter['summary']}",
        "",
        f"本章共 **{len(questions)}** 题。题目使用 `{chapter['prefix']}-NNN` 稳定 ID，移动文件不会改变引用。",
        "",
        "## 子主题",
        "",
        "| 子主题 | 题数 | 原题号 |",
        "|---|---:|---:|",
        *index_rows,
    ]
    if references:
        chapter_index.extend(["", "## 资料", "", "- [官方与框架核验资料](references.md)"])
    (chapter_dir / "README.md").write_text("\n".join(chapter_index).rstrip() + "\n", encoding="utf-8")

    legacy_path = DOCS / str(chapter["legacy"])
    target = Path(str(chapter["area"])) / str(chapter["slug"]) / "README.md"
    legacy_path.write_text(
        f"# {chapter['title']}（已迁移）\n\n"
        f"> 为降低单文件体积，本章已按子主题迁移。\n\n"
        f"请访问新的[{chapter['title']}目录]({target.as_posix()})。稳定题目 ID 可用于长期引用。\n",
        encoding="utf-8",
    )
    return records


def write_area_indexes() -> None:
    area_meta = {
        "01-foundations": ("基础原理", "Agent 架构与模型基础。"),
        "02-capabilities": ("核心能力", "规划、上下文、工具、多 Agent 与 RAG。"),
        "03-production": ("生产工程", "模型成本、安全治理、可观测性与平台落地。"),
        "04-products": ("产品专题", "按版本核验的 Agent 产品专题。"),
    }
    for area, (title, summary) in area_meta.items():
        chapters = [chapter for chapter in CHAPTERS if chapter["area"] == area]
        lines = [f"# {title}", "", f"> {summary}", ""]
        for chapter in chapters:
            lines.append(f"- [{chapter['title']}]({chapter['slug']}/README.md)：{chapter['summary']}")
        area_path = DOCS / area
        area_path.mkdir(parents=True, exist_ok=True)
        (area_path / "README.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def normalize_title(title: str) -> str:
    title = re.sub(r"[（(][^）)]*(?:面|Agent|高级|初级|中级)[^）)]*[）)]\s*$", "", title, flags=re.IGNORECASE)
    return re.sub(r"[\s`*_，。！？、：；,.!?;:“”\"'（）()\-/]", "", title.casefold())


def write_duplicate_report(records: list[dict[str, object]]) -> None:
    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for record in records:
        groups[normalize_title(str(record["title"]))].append(record)
    duplicates = [group for group in groups.values() if len(group) > 1]
    duplicates.sort(key=lambda group: (-len(group), str(group[0]["title"])))
    report_path = DOCS / "reference" / "duplicate-questions.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# 重复题候选报告",
        "",
        "> 本报告按标准化标题自动生成，只表示需要人工审查，不代表答案可以直接删除。建议保留第一条作为主问题候选，其余内容合并为相似问法、追问或补充答案。",
        "",
        f"共发现 **{len(duplicates)}** 组候选，涉及 **{sum(len(group) for group in duplicates)}** 道题。",
        "",
    ]
    for index, group in enumerate(duplicates, 1):
        lines.extend([f"## {index}. {group[0]['title']}", ""])
        for item_index, record in enumerate(group):
            path = Path(record["path"])  # type: ignore[arg-type]
            rel = Path(os.path.relpath(path, report_path.parent)).as_posix()
            label = "主问题候选" if item_index == 0 else "相似问法"
            lines.append(f"- {label}：[{record['id']} · {record['title']}]({rel}#{str(record['id']).lower()})（{record['chapter']} / {record['topic']}）")
        lines.append("")
    report_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def collect_migrated_records() -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    migrated_re = re.compile(r"^###\s+([A-Z]+-\d{3})\s+·\s+(.+?)\s*$", re.MULTILINE)
    for chapter in CHAPTERS:
        chapter_dir = DOCS / str(chapter["area"]) / str(chapter["slug"])
        for path in sorted(chapter_dir.glob("*.md")):
            if path.name in {"README.md", "references.md"}:
                continue
            text = path.read_text(encoding="utf-8-sig")
            topic_match = re.search(r"^#\s+(.+?)\s*$", text, re.MULTILINE)
            topic = topic_match.group(1) if topic_match else path.stem
            topic = re.sub(r"（\d+）$", "", topic)
            for match in migrated_re.finditer(text):
                records.append(
                    {
                        "id": match.group(1),
                        "title": match.group(2).strip(),
                        "chapter": str(chapter["title"]),
                        "topic": topic,
                        "path": path,
                    }
                )
    return records


def main() -> None:
    missing = [str(chapter["legacy"]) for chapter in CHAPTERS if not QUESTION_RE.search((DOCS / str(chapter["legacy"])).read_text(encoding="utf-8-sig"))]
    if missing:
        all_records = collect_migrated_records()
        if not all_records:
            raise SystemExit("Neither legacy nor migrated questions were found.")
        write_area_indexes()
        write_duplicate_report(all_records)
        print(f"Resumed index generation for {len(all_records)} migrated questions.")
        return

    all_records: list[dict[str, object]] = []
    for chapter in CHAPTERS:
        questions, references = parse_questions(DOCS / str(chapter["legacy"]))
        expected = list(range(1, len(questions) + 1))
        actual = [int(question["number"]) for question in questions]
        if actual != expected:
            raise ValueError(f"Non-contiguous legacy numbering: {chapter['legacy']}")
        all_records.extend(write_chapter(chapter, questions, references))
    write_area_indexes()
    write_duplicate_report(all_records)
    print(f"Migrated {len(all_records)} questions into {len(CHAPTERS)} topic indexes.")


if __name__ == "__main__":
    main()

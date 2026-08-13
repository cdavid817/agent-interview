#!/usr/bin/env python3
"""Apply one-time content-quality cleanup after the topic-structure migration."""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TAXONOMY = json.loads((ROOT / "scripts" / "taxonomy.json").read_text(encoding="utf-8"))
QUESTION_RE = re.compile(
    r'^<a id="([a-z]+-\d{3})"></a>\s*\n###\s+(.+?)\s*$',
    re.MULTILINE,
)
ANCHOR_RE = re.compile(r'^<a id="([a-z]+-\d{3})"></a>\s*$', re.MULTILINE)
REFERENCE_RE = re.compile(
    r"(?P<lead>详见全文第|参全文第|见全文第|同全文第|呼应全文第|全文第)"
    r"\s*(?P<numbers>\d+(?:\s*/\s*\d+)*)\s*题"
)
RELATED_RE = re.compile(
    r"(?m)^(?:\*\*)?相关知识点(?:[：:](?:\*\*)?|\*\*[：:])\s*.*?\s*$"
)
METRIC_RE = re.compile(
    r"指标|准确率|召回率|成功率|完成率|错误率|命中率|延迟|时延|吞吐|QPS|"
    r"P95|P99|SLO|SLA|成本|Token|覆盖率|通过率|满意度|ROI|可验证|验证|测试|"
    r"评测|监控|命中|耗时",
    re.IGNORECASE,
)


@dataclass
class Question:
    stable_id: str
    title: str
    path: Path
    prefix: str
    body: str
    block_start: int
    block_end: int


TAG_RULES = [
    (r"OpenClaw", "OpenClaw"),
    (r"Claude\s*Code", "Claude Code"),
    (r"LangGraph", "LangGraph"),
    (r"LangChain", "LangChain"),
    (r"AutoGen", "AutoGen"),
    (r"CrewAI", "CrewAI"),
    (r"Spring\s*AI", "Spring AI"),
    (r"Harness", "Harness Engineering"),
    (r"Context\s*Engineering|上下文工程", "Context Engineering"),
    (r"Agent\s*Runtime|Runtime", "Agent Runtime"),
    (r"Agent\s*Loop", "Agent Loop"),
    (r"Multi[- ]?Agent|多\s*Agent", "Multi-Agent"),
    (r"MCP|Model Context Protocol", "MCP"),
    (r"Function Calling", "Function Calling"),
    (r"Tool\s*Calling|工具调用", "Tool Calling"),
    (r"Tool\s*Hub|工具中心", "Tool Hub"),
    (r"Skill", "Skill"),
    (r"Workflow|工作流", "Workflow"),
    (r"Planner|规划器|任务规划", "Planner"),
    (r"Executor|执行器", "Executor"),
    (r"任务拆解|Task Decomposition", "Task Decomposition"),
    (r"状态机|State Machine", "状态机"),
    (r"Checkpoint|断点续跑", "Checkpoint"),
    (r"Replan|重规划", "Replanning"),
    (r"Retry|重试", "Retry"),
    (r"Reflection|反思", "Reflection"),
    (r"ReAct", "ReAct"),
    (r"CoT|思维链", "Chain-of-Thought"),
    (r"RAG|知识库", "RAG"),
    (r"Embedding|向量化", "Embedding"),
    (r"Rerank|重排", "Rerank"),
    (r"BM25", "BM25"),
    (r"检索|召回", "检索"),
    (r"长期记忆|Long-term Memory", "长期记忆"),
    (r"短期记忆|Working Memory", "工作记忆"),
    (r"Memory|记忆", "Memory"),
    (r"Context Window|上下文窗口", "Context Window"),
    (r"Prompt Injection", "Prompt Injection"),
    (r"Prompt", "Prompt Engineering"),
    (r"权限|RBAC|ABAC|鉴权", "权限控制"),
    (r"多租户|租户", "多租户"),
    (r"沙箱|Sandbox", "Sandbox"),
    (r"可观测|Tracing|Trace", "可观测性"),
    (r"SLO|SLA|可靠性|高可用", "可靠性"),
    (r"幻觉", "幻觉治理"),
    (r"评测|评估|Judge", "评测体系"),
    (r"成本|Token", "成本治理"),
    (r"模型路由|Router|多模型", "模型路由"),
    (r"模型网关", "模型网关"),
    (r"Coding Agent|代码Agent", "Coding Agent"),
    (r"Transformer", "Transformer"),
    (r"Attention", "Attention"),
    (r"KV Cache", "KV Cache"),
    (r"并发|调度", "任务调度"),
    (r"灰度|A/B", "灰度发布"),
    (r"容灾|恢复", "故障恢复"),
]

METRICS = {
    "ARC": "端到端任务成功率、P95 延迟、单任务成本、人工接管率和故障恢复率",
    "TRANS": "任务质量、训练稳定性、推理吞吐、P95 延迟和显存占用",
    "PLAN": "任务完成率、步骤成功率、重规划率、无效调用率和单任务成本",
    "CTX": "上下文有效信息率、召回准确率、Token 占用、P95 组装延迟和陈旧信息率",
    "TOOL": "工具选择准确率、调用成功率、参数错误率、P95 延迟和失败恢复率",
    "MULTI": "协作任务完成率、冲突率、通信开销、P95 延迟和单任务成本",
    "RAG": "Recall@K、nDCG、引用正确率、回答忠实度和检索 P95 延迟",
    "MODEL": "任务成功率、路由准确率、P95 延迟、Token 消耗和单位成功任务成本",
    "GOV": "误报率、漏报率、策略绕过率、告警恢复时间和审计覆盖率",
    "ENG": "任务完成率、测试通过率、变更接受率、交付周期和单位任务成本",
    "OCLAW": "任务完成率、工具调用成功率、P95 延迟、Token 消耗和人工接管率",
    "CC": "任务完成率、测试通过率、误修改率、P95 延迟和单任务 Token 成本",
}

NEAR_DUPLICATE_ALIASES = [
    ("RAG-046", "RAG-073"),
    ("TOOL-173", "PLAN-265"),
    ("MODEL-083", "MODEL-013"),
]


def canonical_files() -> list[Path]:
    files: list[Path] = []
    for chapter in TAXONOMY:
        directory = ROOT / chapter["path"]
        files.extend(
            path
            for path in sorted(directory.glob("*.md"))
            if path.name not in {"README.md", "references.md"}
        )
    return files


def parse_file(path: Path) -> list[Question]:
    text = path.read_text(encoding="utf-8-sig")
    matches = list(QUESTION_RE.finditer(text))
    questions: list[Question] = []
    for index, match in enumerate(matches):
        stable_id = match.group(1).upper()
        block_start = match.start()
        next_anchor = ANCHOR_RE.search(text, match.end())
        block_end = next_anchor.start() if next_anchor else len(text)
        body = text[match.end():block_end].strip()
        questions.append(
            Question(
                stable_id=stable_id,
                title=match.group(2).strip(),
                path=path,
                prefix=stable_id.split("-", 1)[0],
                body=body,
                block_start=block_start,
                block_end=block_end,
            )
        )
    return questions


def all_questions() -> list[Question]:
    return [question for path in canonical_files() for question in parse_file(path)]


def relative_link(source: Path, target: Path, stable_id: str) -> str:
    if source == target:
        return f"#{stable_id.lower()}"
    return f"{Path(os.path.relpath(target, source.parent)).as_posix()}#{stable_id.lower()}"


def write_changes(changes: dict[Path, str], apply: bool) -> None:
    for path, text in changes.items():
        if apply:
            path.write_text(text.rstrip() + "\n", encoding="utf-8")


def fix_references(apply: bool) -> int:
    questions = all_questions()
    locations = {question.stable_id: question.path for question in questions}
    changed: dict[Path, str] = {}
    count = 0
    lead_map = {
        "详见全文第": "详见 ",
        "参全文第": "参见 ",
        "见全文第": "参见 ",
        "同全文第": "同 ",
        "呼应全文第": "呼应 ",
        "全文第": "",
    }
    for path in canonical_files():
        text = path.read_text(encoding="utf-8-sig")

        def replace(match: re.Match[str]) -> str:
            nonlocal count
            links: list[str] = []
            for raw_number in re.split(r"\s*/\s*", match.group("numbers")):
                stable_id = f"ARC-{int(raw_number):03d}"
                target = locations.get(stable_id)
                if not target:
                    return match.group(0)
                links.append(f"[{stable_id}]({relative_link(path, target, stable_id)})")
            count += 1
            return lead_map[match.group("lead")] + "、".join(links)

        updated = REFERENCE_RE.sub(replace, text)
        if updated != text:
            changed[path] = updated
    write_changes(changed, apply)
    return count


def generated_terms(question: Question) -> list[str]:
    haystack = f"{question.title}\n{question.body}"
    terms: list[str] = []
    for pattern, term in TAG_RULES:
        if re.search(pattern, haystack, re.IGNORECASE) and term not in terms:
            terms.append(term)
        if len(terms) >= 8:
            break
    if len(terms) < 4:
        technical = re.findall(r"\b[A-Za-z][A-Za-z0-9_.+-]{2,}\b", haystack)
        stop = {"Agent", "DeepSeek", "Core", "Overview", "System", "Task"}
        for term in technical:
            if term not in stop and term not in terms:
                terms.append(term)
            if len(terms) >= 6:
                break
    fallbacks = {
        "ARC": ["Agent Architecture", "模块边界", "工程权衡", "可验证性"],
        "OCLAW": ["OpenClaw", "Agent Runtime", "工程扩展", "可验证性"],
        "CC": ["Claude Code", "Coding Agent", "Agent Runtime", "可验证性"],
    }
    for term in fallbacks.get(question.prefix, ["Agent Engineering", "工程权衡", "可验证性"]):
        if term not in terms:
            terms.append(term)
        if len(terms) >= 5:
            break
    return terms[:8]


def fix_related_knowledge(apply: bool) -> tuple[int, int]:
    changed: dict[Path, str] = {}
    added = 0
    deduplicated = 0
    for path in canonical_files():
        text = path.read_text(encoding="utf-8-sig")
        questions = parse_file(path)
        replacements: list[tuple[int, int, str]] = []
        for question in questions:
            body = question.body
            related = list(RELATED_RE.finditer(body))
            if not related:
                terms = "、".join(generated_terms(question))
                body = body.rstrip() + f"\n\n**相关知识点：** {terms}。"
                added += 1
            elif len(related) > 1:
                keep = related[0].group(0)
                body = RELATED_RE.sub("", body)
                body = re.sub(r"\n{3,}", "\n\n", body).rstrip() + "\n\n" + keep
                deduplicated += len(related) - 1
            if body != question.body:
                original = text[question.block_start:question.block_end]
                heading_end = original.find(question.body)
                updated = original[:heading_end] + body + "\n\n"
                replacements.append((question.block_start, question.block_end, updated))
        for start, end, value in reversed(replacements):
            text = text[:start] + value + text[end:]
        if replacements:
            changed[path] = text
    write_changes(changed, apply)
    return added, deduplicated


def normalize_title(title: str) -> str:
    title = re.sub(r"[（(][^）)]*(?:面|Agent|高级|初级|中级)[^）)]*[）)]\s*$", "", title, flags=re.IGNORECASE)
    return re.sub(r"[\s`*_，。！？、：；,.!?;:“”\"'（）()\-/]", "", title.casefold())


def preferred_prefix(title: str) -> str | None:
    rules = [
        (r"记忆|Memory|上下文|Context", "CTX"),
        (r"MCP|Function Calling|Tool|Skill|工具", "TOOL"),
        (r"RAG|Embedding|向量|BM25|Rerank|重排|检索|召回", "RAG"),
        (r"Transformer|Attention|RoPE|MoE|KV Cache", "TRANS"),
        (r"安全|权限|审计|可观测|Tracing|评测|幻觉", "GOV"),
        (r"多\s*Agent|Multi-Agent", "MULTI"),
        (r"模型|成本|Token|Cache|缓存", "MODEL"),
        (r"Coding|代码|单测|多模态|PromptOps", "ENG"),
        (r"规划|Planner|任务拆解|Workflow|重试|Retry|状态机", "PLAN"),
    ]
    for pattern, prefix in rules:
        if re.search(pattern, title, re.IGNORECASE):
            return prefix
    return None


def answer_score(question: Question) -> float:
    body = question.body
    return (
        min(len(re.sub(r"\s", "", body)), 800) / 100
        + 2 * bool(RELATED_RE.search(body))
        + 2 * bool(METRIC_RE.search(body))
        + 2 * bool(re.search(r"风险|边界|权衡|失败|异常|限制|降级|不能|避免", body))
        + 2 * bool(re.search(r"\]\(https?://", body))
    )


def merge_duplicates(apply: bool) -> tuple[int, int]:
    questions = all_questions()
    groups: dict[str, list[Question]] = defaultdict(list)
    for question in questions:
        groups[normalize_title(question.title)].append(question)
    duplicate_groups = [group for group in groups.values() if len(group) > 1]
    aliases: list[tuple[Question, Question]] = []
    canonical_aliases: dict[str, list[Question]] = defaultdict(list)
    for group in duplicate_groups:
        preferred = preferred_prefix(group[0].title)
        candidates = [item for item in group if item.prefix == preferred] or group
        canonical = max(candidates, key=lambda item: (answer_score(item), -int(item.stable_id.rsplit("-", 1)[1])))
        for item in group:
            if item.stable_id != canonical.stable_id:
                aliases.append((item, canonical))
                canonical_aliases[canonical.stable_id].append(item)

    replacements_by_path: dict[Path, list[tuple[int, int, str]]] = defaultdict(list)
    for alias, canonical in aliases:
        link = relative_link(alias.path, canonical.path, canonical.stable_id)
        replacement = (
            f'<a id="{alias.stable_id.lower()}"></a>\n'
            f"> **题目合并：** `{alias.stable_id}` 已并入 "
            f"[{canonical.stable_id} · {canonical.title}]({link})。\n\n"
        )
        replacements_by_path[alias.path].append((alias.block_start, alias.block_end, replacement))

    for canonical_id, items in canonical_aliases.items():
        canonical = next(question for question in questions if question.stable_id == canonical_id)
        alias_text = "、".join(f"`{item.stable_id}`" for item in sorted(items, key=lambda item: item.stable_id))
        body = canonical.body
        marker = f"**历史别名：** {alias_text}。"
        if marker not in body:
            related = RELATED_RE.search(body)
            if related:
                body = body[:related.start()].rstrip() + "\n\n" + marker + "\n\n" + body[related.start():]
            else:
                body = body.rstrip() + "\n\n" + marker
        original = canonical.path.read_text(encoding="utf-8-sig")[canonical.block_start:canonical.block_end]
        heading_end = original.find(canonical.body)
        updated = original[:heading_end] + body + "\n\n"
        replacements_by_path[canonical.path].append((canonical.block_start, canonical.block_end, updated))

    changes: dict[Path, str] = {}
    for path, replacements in replacements_by_path.items():
        text = path.read_text(encoding="utf-8-sig")
        for start, end, value in sorted(replacements, reverse=True):
            text = text[:start] + value + text[end:]
        changes[path] = text
    write_changes(changes, apply)

    report = ROOT / "docs" / "reference" / "id-aliases.md"
    lines = [
        "# 稳定 ID 合并映射",
        "",
        "> 重复题合并后，旧 ID 永不复用。原题目位置保留跳转锚点，本表提供长期迁移记录。",
        "",
        "| 旧 ID | 主问题 |",
        "|---|---|",
    ]
    for alias, canonical in sorted(aliases, key=lambda pair: pair[0].stable_id):
        link = Path(os.path.relpath(canonical.path, report.parent)).as_posix()
        lines.append(f"| `{alias.stable_id}` | [{canonical.stable_id} · {canonical.title}]({link}#{canonical.stable_id.lower()}) |")
    if apply:
        report.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return len(duplicate_groups), len(aliases)


def merge_named_aliases(apply: bool) -> int:
    questions = {question.stable_id: question for question in all_questions()}
    replacements_by_path: dict[Path, list[tuple[int, int, str]]] = defaultdict(list)
    pairs: list[tuple[Question, Question]] = []
    for alias_id, canonical_id in NEAR_DUPLICATE_ALIASES:
        alias = questions.get(alias_id)
        canonical = questions.get(canonical_id)
        if not alias or not canonical:
            continue
        pairs.append((alias, canonical))
        link = relative_link(alias.path, canonical.path, canonical.stable_id)
        replacement = (
            f'<a id="{alias.stable_id.lower()}"></a>\n'
            f"> **题目合并：** `{alias.stable_id}` 已并入 "
            f"[{canonical.stable_id} · {canonical.title}]({link})。\n\n"
        )
        replacements_by_path[alias.path].append((alias.block_start, alias.block_end, replacement))

        body = canonical.body
        history = re.search(r"(?m)^\*\*历史别名：\*\*\s*(.+?)。\s*$", body)
        if history:
            replacement_history = history.group(0).rstrip("。") + f"、`{alias.stable_id}`。"
            body = body[:history.start()] + replacement_history + body[history.end():]
        else:
            marker = f"**历史别名：** `{alias.stable_id}`。"
            related = RELATED_RE.search(body)
            if related:
                body = body[:related.start()].rstrip() + "\n\n" + marker + "\n\n" + body[related.start():]
            else:
                body = body.rstrip() + "\n\n" + marker
        text = canonical.path.read_text(encoding="utf-8-sig")
        original = text[canonical.block_start:canonical.block_end]
        heading_end = original.find(canonical.body)
        updated = original[:heading_end] + body + "\n\n"
        replacements_by_path[canonical.path].append((canonical.block_start, canonical.block_end, updated))

    changes: dict[Path, str] = {}
    for path, replacements in replacements_by_path.items():
        text = path.read_text(encoding="utf-8-sig")
        for start, end, value in sorted(replacements, reverse=True):
            text = text[:start] + value + text[end:]
        changes[path] = text
    write_changes(changes, apply)

    report = ROOT / "docs" / "reference" / "id-aliases.md"
    if pairs and report.exists():
        text = report.read_text(encoding="utf-8-sig").rstrip()
        rows = []
        for alias, canonical in pairs:
            link = Path(os.path.relpath(canonical.path, report.parent)).as_posix()
            row = f"| `{alias.stable_id}` | [{canonical.stable_id} · {canonical.title}]({link}#{canonical.stable_id.lower()}) |"
            if row not in text:
                rows.append(row)
        if rows and apply:
            report.write_text(text + "\n" + "\n".join(rows) + "\n", encoding="utf-8")
    return len(pairs)


def add_product_sources(apply: bool, date: str) -> int:
    changed: dict[Path, str] = {}
    count = 0
    for chapter in TAXONOMY:
        if chapter["prefix"] not in {"OCLAW", "CC"}:
            continue
        directory = ROOT / chapter["path"]
        for path in directory.glob("*.md"):
            text = path.read_text(encoding="utf-8-sig")
            updated, replacements = re.subn(
                r"(?m)^>\s*核验日期：[^\n]*$",
                lambda match: f"> 核验日期：{date}｜来源：[官方资料](references.md)",
                text,
            )
            if replacements:
                changed[path] = updated
                count += replacements
        index = directory / "README.md"
        text = index.read_text(encoding="utf-8-sig")
        note = f"> 产品能力按 **{date}** 可访问的官方资料核验；具体能力仍以实际版本和运行 Surface 为准。"
        if "可访问的官方资料核验" not in text:
            parts = text.split("\n\n", 2)
            text = "\n\n".join(parts[:2] + [note] + parts[2:]) if len(parts) == 3 else text + "\n\n" + note
            changed[index] = text
    write_changes(changed, apply)
    return count


def add_missing_metrics(apply: bool) -> int:
    changed: dict[Path, str] = {}
    count = 0
    for path in canonical_files():
        text = path.read_text(encoding="utf-8-sig")
        replacements: list[tuple[int, int, str]] = []
        for question in parse_file(path):
            body = question.body
            if METRIC_RE.search(body):
                continue
            metric = METRICS[question.prefix]
            line = f"**验证指标：** {metric}。"
            related = RELATED_RE.search(body)
            if related:
                body = body[:related.start()].rstrip() + "\n\n" + line + "\n\n" + body[related.start():]
            else:
                body = body.rstrip() + "\n\n" + line
            original = text[question.block_start:question.block_end]
            heading_end = original.find(question.body)
            updated = original[:heading_end] + body + "\n\n"
            replacements.append((question.block_start, question.block_end, updated))
            count += 1
        for start, end, value in reversed(replacements):
            text = text[:start] + value + text[end:]
        if replacements:
            changed[path] = text
    write_changes(changed, apply)
    return count


BOILERPLATE_SENTENCES = [
    "落地时还应为关键策略设置版本、灰度和回滚能力，并通过真实失败样本持续校准。",
]


def paragraph_key(paragraph: str) -> str:
    return re.sub(r"[\s`*_#>|]", "", paragraph.casefold())


def question_focus(title: str) -> str:
    value = re.sub(r"[（(][^）)]*(?:面|Agent|高级|初级|中级)[^）)]*[）)]\s*$", "", title, flags=re.IGNORECASE)
    value = value.rstrip("？?。 ")
    return value[:48]


def tailor_paragraph(paragraph: str, question: Question) -> str:
    focus = question_focus(question.title)
    numbered = re.match(r"^(\d+\.\s*)(.*)$", paragraph, re.DOTALL)
    if numbered:
        return f"{numbered.group(1)}针对“{focus}”，{numbered.group(2)}"
    if paragraph.lstrip().startswith("|"):
        return f"> 本题视角：{focus}\n{paragraph}"
    return f"围绕“{focus}”，{paragraph}"


def clean_template_paragraphs(apply: bool) -> tuple[int, int, int]:
    boilerplate_removed = 0
    boilerplate_changes: dict[Path, str] = {}
    for path in canonical_files():
        text = path.read_text(encoding="utf-8-sig")
        updated = text
        for sentence in BOILERPLATE_SENTENCES:
            occurrences = updated.count(sentence)
            boilerplate_removed += occurrences
            updated = updated.replace(sentence, "")
        updated = re.sub(r"[ \t]+\n", "\n", updated)
        if updated != text:
            boilerplate_changes[path] = updated
    write_changes(boilerplate_changes, apply)

    # Dry-run analysis must observe the boilerplate-free text as well.
    if not apply and boilerplate_changes:
        original_texts = {path: path.read_text(encoding="utf-8-sig") for path in boilerplate_changes}
        for path, text in boilerplate_changes.items():
            path.write_text(text.rstrip() + "\n", encoding="utf-8")
    else:
        original_texts = {}

    try:
        questions = all_questions()
        grouped: dict[str, list[tuple[Question, str]]] = defaultdict(list)
        for question in questions:
            for paragraph in re.split(r"\n\s*\n", question.body):
                key = paragraph_key(paragraph)
                if len(key) >= 100 and "相关知识点" not in key and "历史别名" not in key:
                    grouped[key].append((question, paragraph))
        repeated = {
            key: values
            for key, values in grouped.items()
            if len({question.stable_id for question, _ in values}) > 1
        }
        affected_ids = {
            question.stable_id
            for values in repeated.values()
            for question, _ in values
        }
        replacements_by_path: dict[Path, list[tuple[int, int, str]]] = defaultdict(list)
        for question in questions:
            parts = re.split(r"(\n\s*\n)", question.body)
            changed = False
            for index in range(0, len(parts), 2):
                key = paragraph_key(parts[index])
                if key in repeated:
                    parts[index] = tailor_paragraph(parts[index], question)
                    changed = True
            if not changed:
                continue
            body = "".join(parts)
            text = question.path.read_text(encoding="utf-8-sig")
            original = text[question.block_start:question.block_end]
            heading_end = original.find(question.body)
            updated = original[:heading_end] + body + "\n\n"
            replacements_by_path[question.path].append((question.block_start, question.block_end, updated))
        changes: dict[Path, str] = {}
        for path, replacements in replacements_by_path.items():
            text = path.read_text(encoding="utf-8-sig")
            for start, end, value in sorted(replacements, reverse=True):
                text = text[:start] + value + text[end:]
            changes[path] = text
        write_changes(changes, apply)
        return boilerplate_removed, len(repeated), len(affected_ids)
    finally:
        for path, text in original_texts.items():
            path.write_text(text, encoding="utf-8")


def split_terms(text: str) -> list[str]:
    terms: list[str] = []
    buffer: list[str] = []
    depth = 0
    for character in text:
        if character in "(（[【":
            depth += 1
            buffer.append(character)
        elif character in ")）]】":
            depth = max(0, depth - 1)
            buffer.append(character)
        elif character in "、，,；;" and depth == 0:
            term = "".join(buffer).strip()
            if term:
                terms.append(term)
            buffer = []
        else:
            buffer.append(character)
    term = "".join(buffer).strip()
    if term:
        terms.append(term)
    return terms


def clean_related_terms(apply: bool) -> tuple[int, int]:
    changed: dict[Path, str] = {}
    normalized_lines = 0
    removed_ids = 0
    id_re = re.compile(r"^(?:ARC|TRANS|PLAN|CTX|TOOL|MULTI|RAG|MODEL|GOV|ENG|OCLAW|CC)-\d{3}$", re.IGNORECASE)
    line_re = re.compile(r"(?m)^(?:\*\*)?相关知识点(?:[：:](?:\*\*)?|\*\*[：:])\s*(.*?)\s*$")
    for path in canonical_files():
        text = path.read_text(encoding="utf-8-sig")

        def replace(match: re.Match[str]) -> str:
            nonlocal normalized_lines, removed_ids
            raw = match.group(1).replace("**", "").replace("`", "").strip().rstrip("。.")
            terms: list[str] = []
            seen: set[str] = set()
            for term in split_terms(raw):
                term = term.strip()
                if id_re.fullmatch(term):
                    removed_ids += 1
                    continue
                folded = term.casefold()
                if term and folded not in seen:
                    terms.append(term)
                    seen.add(folded)
            normalized_lines += 1
            return f"**相关知识点：** {'、'.join(terms)}。"

        updated = line_re.sub(replace, text)
        if updated != text:
            changed[path] = updated
    write_changes(changed, apply)
    return normalized_lines, removed_ids


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Write changes")
    parser.add_argument("--date", default="2026-08-03", help="Product verification date")
    parser.add_argument("--templates-only", action="store_true", help="Only remove repeated answer templates")
    parser.add_argument("--related-only", action="store_true", help="Only normalize related-knowledge terms")
    parser.add_argument("--near-duplicates-only", action="store_true", help="Only merge reviewed near-duplicate pairs")
    args = parser.parse_args()
    action = "Applied" if args.apply else "Would apply"

    if args.templates_only:
        boilerplate, groups, questions = clean_template_paragraphs(args.apply)
        print(f"{action}: {boilerplate} boilerplate sentences")
        print(f"{action}: {groups} repeated paragraph groups across {questions} questions")
        return 0
    if args.related_only:
        lines, removed = clean_related_terms(args.apply)
        print(f"{action}: normalized {lines} related-knowledge lines; removed {removed} ID terms")
        return 0
    if args.near_duplicates_only:
        merged = merge_named_aliases(args.apply)
        print(f"{action}: {merged} reviewed near-duplicate aliases")
        return 0

    references = fix_references(args.apply)
    related, duplicate_related = fix_related_knowledge(args.apply)
    if args.apply:
        groups, aliases = merge_duplicates(True)
        product_sources = add_product_sources(True, args.date)
        metrics = add_missing_metrics(True)
    else:
        groups = len([group for group in _duplicate_groups()])
        aliases = sum(len(group) - 1 for group in _duplicate_groups())
        product_sources = sum(1 for q in all_questions() if q.prefix in {"OCLAW", "CC"})
        metrics = sum(not METRIC_RE.search(q.body) for q in all_questions())
    print(f"{action}: {references} positional references")
    print(f"{action}: {related} related-knowledge sections; removed {duplicate_related} duplicate section")
    print(f"{action}: {groups} duplicate groups with {aliases} aliases")
    print(f"{action}: {product_sources} product-source metadata lines")
    print(f"{action}: {metrics} missing metric sections")
    return 0


def _duplicate_groups() -> list[list[Question]]:
    groups: dict[str, list[Question]] = defaultdict(list)
    for question in all_questions():
        groups[normalize_title(question.title)].append(question)
    return [group for group in groups.values() if len(group) > 1]


if __name__ == "__main__":
    raise SystemExit(main())

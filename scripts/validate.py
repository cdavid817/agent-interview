#!/usr/bin/env python3
"""Validate the topic-oriented Agent Interview question bank."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
TAXONOMY_PATH = ROOT / "scripts" / "taxonomy.json"
TAXONOMY = json.loads(TAXONOMY_PATH.read_text(encoding="utf-8"))
QUESTION_RE = re.compile(
    r'^<a id="([a-z]+-\d{3})"></a>\s*\n###\s+(?:\d+\.\s+)?(.+?)\s*$',
    re.MULTILINE,
)
LEGACY_QUESTION_RE = re.compile(r"^####\s+\d+、", re.MULTILINE)
ANCHOR_RE = re.compile(r'<a id="([a-z]+-\d{3})"></a>\s*$', re.MULTILINE)
LOCAL_LINK_RE = re.compile(r"\[[^\]]+\]\((?!https?://|mailto:|#)([^)]+)\)")
STABLE_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]*#([a-z]+-\d{3}))\)")
RELATED_KNOWLEDGE_RE = re.compile(r"相关知识点[：:]\s*\**\s*(.+)$")
RELATED_LINE_RE = re.compile(
    r"(?m)^(?:\*\*)?相关知识点(?:[：:](?:\*\*)?|\*\*[：:])\s*.*?\s*$"
)
METRIC_SIGNAL_RE = re.compile(
    r"指标|准确率|召回率|成功率|完成率|错误率|命中率|延迟|时延|吞吐|QPS|"
    r"P95|P99|SLO|SLA|成本|Token|覆盖率|通过率|满意度|ROI|可验证|验证|测试|"
    r"评测|监控|命中|耗时",
    re.IGNORECASE,
)
POSITIONAL_REFERENCE_RE = re.compile(
    r"(?:详见全文第|参全文第|见全文第|同全文第|呼应全文第|全文第)\s*\d+"
)
GLOSSARY = DOCS / "reference" / "术语索引.md"
GLOSSARY_CORE_TERMS = ROOT / "scripts" / "glossary_core_terms.txt"
MAX_QUESTIONS_PER_FILE = 50
GLOSSARY_SECTIONS = [
    "一、架构设计类",
    "二、任务规划与编排类",
    "三、模型调用与路由类",
    "四、Prompt 工程类",
    "五、RAG 与知识库类",
    "六、向量数据库类",
    "七、记忆系统类",
    "八、工具调用类",
    "九、安全与治理类",
    "十、可观测性类",
    "十一、评测体系类",
    "十二、工程稳定性类",
]
GLOSSARY_ITEM_RE = re.compile(r"^(\d+)\.\s+(.+?)\s*$", re.MULTILINE)


def question_files() -> list[tuple[dict[str, str], Path]]:
    result: list[tuple[dict[str, str], Path]] = []
    for chapter in TAXONOMY:
        directory = ROOT / chapter["path"]
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.md")):
            if path.name in {"README.md", "references.md"}:
                continue
            if QUESTION_RE.search(path.read_text(encoding="utf-8-sig")):
                result.append((chapter, path))
    return result


def validate_taxonomy() -> list[str]:
    errors: list[str] = []
    prefixes = [chapter["prefix"] for chapter in TAXONOMY]
    paths = [chapter["path"] for chapter in TAXONOMY]
    if len(prefixes) != len(set(prefixes)):
        errors.append("scripts/taxonomy.json: 章节前缀重复")
    if len(paths) != len(set(paths)):
        errors.append("scripts/taxonomy.json: 章节路径重复")
    for chapter in TAXONOMY:
        directory = ROOT / chapter["path"]
        if not directory.is_dir():
            errors.append(f"scripts/taxonomy.json: 章节目录不存在: {chapter['path']}")
        elif not (directory / "README.md").exists():
            errors.append(f"{chapter['path']}: 缺少 README.md")
    return errors


def validate_questions() -> tuple[list[str], Counter[str], int]:
    errors: list[str] = []
    ids: dict[str, Path] = {}
    prefix_counts: Counter[str] = Counter()
    total = 0
    allowed_prefixes = {chapter["prefix"] for chapter in TAXONOMY}
    normalized_titles: dict[str, list[str]] = defaultdict(list)
    repeated_paragraphs: dict[str, set[str]] = defaultdict(set)

    for chapter, path in question_files():
        text = path.read_text(encoding="utf-8-sig")
        matches = list(QUESTION_RE.finditer(text))
        relative = path.relative_to(ROOT)
        if not text.startswith("# "):
            errors.append(f"{relative}: 文件必须以 H1 标题开始")
        if len(matches) > MAX_QUESTIONS_PER_FILE:
            errors.append(f"{relative}: 单文件 {len(matches)} 题，超过上限 {MAX_QUESTIONS_PER_FILE}")
        if text.count("```") % 2:
            errors.append(f"{relative}: Markdown 代码围栏未闭合")
        if LEGACY_QUESTION_RE.search(text):
            errors.append(f"{relative}: 仍包含旧版位置题号")

        previous_number = -1
        for index, match in enumerate(matches):
            stable_id = match.group(1).upper()
            title = match.group(2)
            prefix, raw_number = stable_id.rsplit("-", 1)
            number = int(raw_number)
            total += 1
            prefix_counts[prefix] += 1
            if prefix not in allowed_prefixes:
                errors.append(f"{relative}: 未登记的题目前缀 {prefix}")
            if prefix != chapter["prefix"]:
                errors.append(f"{relative}: {stable_id} 不属于章节前缀 {chapter['prefix']}")
            if stable_id in ids:
                errors.append(f"{relative}: 稳定 ID {stable_id} 与 {ids[stable_id].relative_to(ROOT)} 重复")
            else:
                ids[stable_id] = path
            if number <= previous_number:
                errors.append(f"{relative}: 文件内稳定 ID 未按数字递增")
            previous_number = number
            if not title.strip():
                errors.append(f"{relative}: {stable_id} 标题为空")
            normalized_title = re.sub(
                r"[\s`*_，。！？、：；,.!?;:“”\"'（）()\-/]",
                "",
                re.sub(
                    r"[（(][^）)]*(?:面|Agent|高级|初级|中级)[^）)]*[）)]\s*$",
                    "",
                    title,
                    flags=re.IGNORECASE,
                ).casefold(),
            )
            normalized_titles[normalized_title].append(stable_id)

            body_end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            body = text[match.end():body_end]
            answer = re.sub(r"(?m)^>\s*(?:稳定 ID|核验日期)[^\n]*$", "", body)
            answer = re.sub(r"(?m)^\s*---\s*$", "", answer).strip()
            if not answer:
                errors.append(f"{relative}: {stable_id} 答案为空")
            related_lines = RELATED_LINE_RE.findall(answer)
            if len(related_lines) != 1:
                errors.append(f"{relative}: {stable_id} 应有且仅有一处相关知识点，实际 {len(related_lines)}")
            if re.search(
                r"相关知识点.*\b(?:ARC|TRANS|PLAN|CTX|TOOL|MULTI|RAG|MODEL|GOV|ENG|OCLAW|CC|OPC)-\d{3}\b",
                answer,
                re.IGNORECASE,
            ):
                errors.append(f"{relative}: {stable_id} 的相关知识点混入题目 ID")
            if not METRIC_SIGNAL_RE.search(answer):
                errors.append(f"{relative}: {stable_id} 缺少可验证指标")
            if POSITIONAL_REFERENCE_RE.search(answer):
                errors.append(f"{relative}: {stable_id} 仍使用旧位置题号引用")
            if prefix in {"OCLAW", "CC", "OPC"}:
                if not re.search(r"核验日期：\d{4}-\d{2}-\d{2}", body):
                    errors.append(f"{relative}: {stable_id} 缺少产品核验日期")
                if not any(
                    f"来源：[{label}](references.md)" in body
                    for label in ("官方资料", "源码分析")
                ):
                    errors.append(f"{relative}: {stable_id} 缺少产品资料链接")
            for paragraph in re.split(r"\n\s*\n", answer):
                key = re.sub(r"[\s`*_#>|]", "", paragraph.casefold())
                if len(key) >= 100 and "相关知识点" not in key and "历史别名" not in key:
                    repeated_paragraphs[key].add(stable_id)

    for prefix in allowed_prefixes:
        if not prefix_counts[prefix]:
            errors.append(f"题库缺少前缀为 {prefix} 的题目")
    for stable_ids in normalized_titles.values():
        if len(stable_ids) > 1:
            errors.append(f"标准化题目标题重复: {', '.join(stable_ids)}")
    for stable_ids in repeated_paragraphs.values():
        if len(stable_ids) > 1:
            errors.append(f"答案包含跨题重复长段落: {', '.join(sorted(stable_ids))}")
    return errors, prefix_counts, total


def validate_aliases() -> list[str]:
    errors: list[str] = []
    active_ids: set[str] = set()
    anchors: Counter[str] = Counter()
    for _, path in question_files():
        text = path.read_text(encoding="utf-8-sig")
        active_ids.update(match.group(1).upper() for match in QUESTION_RE.finditer(text))
        anchors.update(match.group(1).upper() for match in ANCHOR_RE.finditer(text))
    report = DOCS / "reference" / "id-aliases.md"
    if not report.exists():
        return [f"{report.relative_to(ROOT)}: 文件不存在"]
    alias_ids = set(re.findall(r"(?m)^\| `([A-Z]+-\d{3})` \|", report.read_text(encoding="utf-8-sig")))
    for alias_id in sorted(alias_ids):
        if alias_id in active_ids:
            errors.append(f"{report.relative_to(ROOT)}: {alias_id} 同时是活动题目和历史别名")
        if anchors[alias_id] != 1:
            errors.append(f"{report.relative_to(ROOT)}: {alias_id} 应有一个跳转锚点，实际 {anchors[alias_id]}")
    unregistered = {anchor for anchor in anchors if anchor not in active_ids and anchor not in alias_ids}
    if unregistered:
        errors.append(f"未登记的历史别名锚点: {', '.join(sorted(unregistered))}")
    return errors


def validate_all_markdown_locations() -> list[str]:
    errors: list[str] = []
    canonical_roots = tuple((ROOT / chapter["path"]).resolve() for chapter in TAXONOMY)
    for path in DOCS.rglob("*.md"):
        text = path.read_text(encoding="utf-8-sig")
        text_without_fences = re.sub(r"```[\s\S]*?```", "", text)
        if not QUESTION_RE.search(text_without_fences):
            continue
        resolved = path.resolve()
        if not any(root == resolved.parent for root in canonical_roots):
            errors.append(f"{path.relative_to(ROOT)}: 题目位于未登记目录")
    return errors


def validate_readme_product_index() -> list[str]:
    """docs/README.md is hand-maintained; build_indexes.py never touches it.

    The "产品专题" list has silently dropped a newly added 04-products
    chapter before (caught only in code review). Guard against a repeat by
    requiring every TAXONOMY chapter in the 产品专题 area to have a link in
    that section.
    """
    errors: list[str] = []
    readme = DOCS / "README.md"
    product_area = "产品专题"
    if not readme.exists():
        return [f"{readme.relative_to(ROOT)}: 文件不存在"]
    text = readme.read_text(encoding="utf-8-sig")
    section_match = re.search(
        rf"^## {re.escape(product_area)}\s*$([\s\S]*?)(?=^## |\Z)", text, re.MULTILINE
    )
    if not section_match:
        return [f"{readme.relative_to(ROOT)}: 缺少「{product_area}」小节，无法确认是否覆盖全部产品章节"]
    section = section_match.group(1)
    linked_paths = set()
    for raw_target in LOCAL_LINK_RE.findall(section):
        target = unquote(raw_target.split("#", 1)[0].strip().strip("<>"))
        if target:
            linked_paths.add((readme.parent / target).resolve())
    for chapter in TAXONOMY:
        if chapter["area"] != product_area:
            continue
        expected = (ROOT / chapter["path"] / "README.md").resolve()
        if expected not in linked_paths:
            errors.append(
                f"{readme.relative_to(ROOT)}: 「{product_area}」清单缺少章节 {chapter['title']}"
                f"（应链接 {chapter['path']}/README.md）"
            )
    return errors


def validate_local_links() -> list[str]:
    errors: list[str] = []
    paths = [ROOT / "README.md", ROOT / "CONTRIBUTING.md", ROOT / "Agent 名词解释.md", *DOCS.rglob("*.md")]
    for path in paths:
        # 逐字收录的第三方资料，仓库不维护其正文内链
        if path.is_relative_to(DOCS / "reference" / "deep-dive"):
            continue
        text = path.read_text(encoding="utf-8-sig")
        for raw_target in LOCAL_LINK_RE.findall(text):
            target = unquote(raw_target.split("#", 1)[0].strip().strip("<>"))
            if not target:
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                errors.append(f"{path.relative_to(ROOT)}: 本地链接不存在: {raw_target}")
        for raw_target, fragment in STABLE_LINK_RE.findall(text):
            raw_path = unquote(raw_target.split("#", 1)[0].strip().strip("<>"))
            target_path = (path.parent / raw_path).resolve() if raw_path else path.resolve()
            if not target_path.exists():
                continue
            target_text = target_path.read_text(encoding="utf-8-sig")
            if f'<a id="{fragment}"></a>' not in target_text:
                errors.append(f"{path.relative_to(ROOT)}: 稳定 ID 锚点不存在: {raw_target}")
    return errors


def normalize_term(term: str) -> str:
    value = term.replace("*", "").replace("`", "")
    value = re.sub(r"\s+", " ", value).strip()
    return value.rstrip("。.").strip()


def split_knowledge_terms(text: str) -> list[str]:
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
            term = normalize_term("".join(buffer))
            if term:
                terms.append(term)
            buffer = []
        else:
            buffer.append(character)
    term = normalize_term("".join(buffer))
    if term:
        terms.append(term)
    return terms


def collect_related_knowledge() -> Counter[str]:
    terms: Counter[str] = Counter()
    for _, path in question_files():
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            match = RELATED_KNOWLEDGE_RE.search(line)
            if match:
                terms.update(term.casefold() for term in split_knowledge_terms(match.group(1)))
    return terms


def validate_glossary() -> list[str]:
    errors: list[str] = []
    if not GLOSSARY.exists():
        return [f"{GLOSSARY.relative_to(ROOT)}: 文件不存在"]
    text = GLOSSARY.read_text(encoding="utf-8-sig")
    if not text.startswith("# Agent 术语索引"):
        errors.append(f"{GLOSSARY.relative_to(ROOT)}: 标题必须说明这是术语索引")
    sections = re.findall(r"^##\s+(.+?)\s*$", text, re.MULTILINE)
    if sections != GLOSSARY_SECTIONS:
        errors.append(f"{GLOSSARY.relative_to(ROOT)}: 分类缺失、顺序错误或存在未登记分类")
    section_blocks = re.findall(r"^##\s+(.+?)\s*$([\s\S]*?)(?=^##\s+|\Z)", text, re.MULTILINE)
    for section, body in section_blocks:
        numbers = [int(match.group(1)) for match in GLOSSARY_ITEM_RE.finditer(body)]
        if numbers != list(range(1, len(numbers) + 1)):
            errors.append(f"{GLOSSARY.relative_to(ROOT)}: “{section}”编号不连续")
    terms = [normalize_term(match.group(2)) for match in GLOSSARY_ITEM_RE.finditer(text)]
    folded = [term.casefold() for term in terms]
    if len(folded) != len(set(folded)):
        errors.append(f"{GLOSSARY.relative_to(ROOT)}: 存在重复术语")
    declared = re.search(r"共 \*\*(\d+)\*\* 个去重术语", text)
    if not declared or int(declared.group(1)) != len(terms):
        errors.append(f"{GLOSSARY.relative_to(ROOT)}: 声明术语数与实际不一致（实际 {len(terms)}）")
    threshold_match = re.search(r"至少出现 \*\*(\d+)\*\* 次", text)
    threshold = int(threshold_match.group(1)) if threshold_match else 5
    core_terms = {
        normalize_term(line).casefold()
        for line in GLOSSARY_CORE_TERMS.read_text(encoding="utf-8-sig").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    expected = {term for term, count in collect_related_knowledge().items() if count >= threshold} | core_terms
    actual = set(folded)
    if missing := expected - actual:
        errors.append(f"{GLOSSARY.relative_to(ROOT)}: 缺少 {len(missing)} 个常见或核心术语")
    if uncommon := actual - expected:
        errors.append(f"{GLOSSARY.relative_to(ROOT)}: 包含 {len(uncommon)} 个未达到保留条件的术语")
    return errors


def validate_generated_indexes() -> list[str]:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_indexes.py"), "--check"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    if result.returncode == 0:
        return []
    detail = (result.stdout + result.stderr).strip().replace("\n", "; ")
    return [f"生成索引已过期，请运行 python scripts/build_indexes.py：{detail}"]


def main() -> int:
    errors: list[str] = []
    errors.extend(validate_taxonomy())
    question_errors, prefix_counts, total = validate_questions()
    errors.extend(question_errors)
    errors.extend(validate_all_markdown_locations())
    errors.extend(validate_aliases())
    errors.extend(validate_local_links())
    errors.extend(validate_readme_product_index())
    errors.extend(validate_glossary())
    errors.extend(validate_generated_indexes())

    print("Agent Interview validation")
    print("-" * 64)
    for chapter in TAXONOMY:
        print(f"{prefix_counts[chapter['prefix']]:4}  {chapter['prefix']:<6}  {chapter['title']}")
    print("-" * 64)
    print(f"Total: {total}")
    if errors:
        print("\nValidation errors:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("All checks passed.")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())

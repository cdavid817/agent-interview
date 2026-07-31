#!/usr/bin/env python3
"""Validate the structure and statistics of the Agent Interview repository."""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EXPECTED = {
    "一、Agent核心架构.md": 87,
    "二、任务规划与执行.md": 307,
    "三、上下文与知识系统.md": 206,
    "四、工具与能力体系.md": 237,
    "五、多Agent与协作.md": 34,
    "六、模型能力与成本.md": 160,
    "七、安全、治理与可观测性.md": 191,
    "八、工程落地与平台化.md": 202,
    "九、RAG.md": 200,
    "十、Transformer.md": 60,
    "十一、OpenClaw.md": 56,
    "十二、ClaudeCode.md": 80,
}
QUESTION_RE = re.compile(r"^####\s+(\d+)、(.+?)\s*$", re.MULTILINE)
LOCAL_LINK_RE = re.compile(r"\[[^\]]+\]\((?!https?://|#)([^)]+)\)")
GLOSSARY = ROOT / "Agent 名词解释.md"
GLOSSARY_CORE_TERMS = ROOT / "scripts" / "glossary_core_terms.txt"
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
RELATED_KNOWLEDGE_RE = re.compile(r"相关知识点[：:]\s*\**\s*(.+)$")
PRODUCT_QUESTION_RE = re.compile(
    r"^####\s+\d+、.*(?:OpenClaw|Claude\s*Code|ClaudeCode|CLAUDE\.md)",
    re.IGNORECASE | re.MULTILINE,
)
PRODUCT_CHAPTERS = {"十一、OpenClaw.md", "十二、ClaudeCode.md"}


def validate_document(path: Path, expected_count: int) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8-sig")

    if not text.startswith("# "):
        errors.append(f"{path.name}: 文件必须以 H1 标题开始")

    matches = list(QUESTION_RE.finditer(text))
    numbers = [int(match.group(1)) for match in matches]
    expected_numbers = list(range(1, expected_count + 1))

    if len(matches) != expected_count:
        errors.append(
            f"{path.name}: 题数应为 {expected_count}，实际为 {len(matches)}"
        )
    if numbers != expected_numbers:
        errors.append(f"{path.name}: 题号不连续或顺序错误")

    for index, match in enumerate(matches):
        number = int(match.group(1))
        title = match.group(2).strip()
        body_start = match.end()
        body_end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[body_start:body_end]
        body = re.sub(r"(?m)^\s*---\s*$", "", body).strip()

        if not title:
            errors.append(f"{path.name}: 第 {number} 题标题为空")
        if not body:
            errors.append(f"{path.name}: 第 {number} 题答案为空")

    if text.count("```") % 2:
        errors.append(f"{path.name}: Markdown 代码围栏未闭合")

    return errors


def validate_readme_links() -> list[str]:
    errors: list[str] = []
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")

    for raw_target in LOCAL_LINK_RE.findall(text):
        target = raw_target.split("#", 1)[0].strip()
        if not target:
            continue
        if not (ROOT / target).exists():
            errors.append(f"README.md: 本地链接不存在: {raw_target}")

    return errors


def normalize_term(term: str) -> str:
    value = term.replace("*", "").replace("`", "")
    value = re.sub(r"\s+", " ", value).strip()
    return value.rstrip("。.").strip()


def split_knowledge_terms(text: str) -> list[str]:
    terms: list[str] = []
    buffer: list[str] = []
    depth = 0
    openers = {"(", "（", "[", "【"}
    closers = {")", "）", "]", "】"}
    delimiters = {"、", "，", ",", "；", ";"}

    for character in text:
        if character in openers:
            depth += 1
            buffer.append(character)
        elif character in closers:
            depth = max(0, depth - 1)
            buffer.append(character)
        elif character in delimiters and depth == 0:
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
    for path in DOCS.glob("*.md"):
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            match = RELATED_KNOWLEDGE_RE.search(line)
            if not match:
                continue
            terms.update(
                term.casefold() for term in split_knowledge_terms(match.group(1))
            )
    return terms


def load_core_glossary_terms() -> set[str]:
    if not GLOSSARY_CORE_TERMS.exists():
        return set()
    return {
        normalize_term(line).casefold()
        for line in GLOSSARY_CORE_TERMS.read_text(
            encoding="utf-8-sig"
        ).splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


def validate_glossary() -> list[str]:
    errors: list[str] = []
    if not GLOSSARY.exists():
        return [f"{GLOSSARY.name}: 文件不存在"]
    if not GLOSSARY_CORE_TERMS.exists():
        errors.append(f"{GLOSSARY_CORE_TERMS.name}: 核心术语清单不存在")

    text = GLOSSARY.read_text(encoding="utf-8-sig")
    if not text.startswith("# Agent 名词解释"):
        errors.append(f"{GLOSSARY.name}: 文件必须以对应 H1 标题开始")

    sections = re.findall(r"^##\s+(.+?)\s*$", text, re.MULTILINE)
    if sections != GLOSSARY_SECTIONS:
        errors.append(f"{GLOSSARY.name}: 一级分类缺失、顺序错误或存在未登记分类")

    section_blocks = re.findall(
        r"^##\s+(.+?)\s*$([\s\S]*?)(?=^##\s+|\Z)", text, re.MULTILINE
    )
    for section, body in section_blocks:
        section_matches = list(GLOSSARY_ITEM_RE.finditer(body))
        numbers = [int(match.group(1)) for match in section_matches]
        if numbers != list(range(1, len(numbers) + 1)):
            errors.append(
                f"{GLOSSARY.name}: “{section}”术语编号未从 1 开始连续递增"
            )

    matches = list(GLOSSARY_ITEM_RE.finditer(text))

    terms = [normalize_term(match.group(2)) for match in matches]
    folded_terms = [term.casefold() for term in terms]
    if any(not term for term in terms):
        errors.append(f"{GLOSSARY.name}: 存在空术语")
    if len(set(folded_terms)) != len(folded_terms):
        errors.append(f"{GLOSSARY.name}: 存在重复术语")

    declared_match = re.search(r"共 \*\*(\d+)\*\* 个去重术语", text)
    if not declared_match or int(declared_match.group(1)) != len(terms):
        errors.append(
            f"{GLOSSARY.name}: 声明术语数与实际不一致（实际 {len(terms)}）"
        )

    threshold_match = re.search(r"至少出现 \*\*(\d+)\*\* 次", text)
    if not threshold_match:
        errors.append(f"{GLOSSARY.name}: 未声明常见术语最小出现次数")
        threshold = 5
    else:
        threshold = int(threshold_match.group(1))

    knowledge_counts = collect_related_knowledge()
    expected_terms = {
        term for term, count in knowledge_counts.items() if count >= threshold
    }
    expected_terms.update(load_core_glossary_terms())
    actual_terms = set(folded_terms)

    missing = expected_terms - actual_terms
    if missing:
        preview = "、".join(sorted(missing)[:10])
        errors.append(
            f"{GLOSSARY.name}: 缺少 {len(missing)} 个常见或核心术语，示例：{preview}"
        )

    uncommon = actual_terms - expected_terms
    if uncommon:
        preview = "、".join(sorted(uncommon)[:10])
        errors.append(
            f"{GLOSSARY.name}: 包含 {len(uncommon)} 个未达到保留条件的术语，"
            f"示例：{preview}"
        )

    return errors


def validate_product_question_locations() -> list[str]:
    errors: list[str] = []
    for path in DOCS.glob("*.md"):
        if path.name in PRODUCT_CHAPTERS:
            continue
        text = path.read_text(encoding="utf-8-sig")
        matches = PRODUCT_QUESTION_RE.findall(text)
        if matches:
            errors.append(
                f"{path.name}: OpenClaw/Claude Code 专题题必须迁入对应专章"
            )
    return errors


def main() -> int:
    errors: list[str] = []

    actual_names = {path.name for path in DOCS.glob("*.md")}
    expected_names = set(EXPECTED)
    missing = sorted(expected_names - actual_names)
    extra = sorted(actual_names - expected_names)
    if missing:
        errors.append(f"docs/: 缺少文件: {', '.join(missing)}")
    if extra:
        errors.append(f"docs/: 存在未登记文件: {', '.join(extra)}")

    total = 0
    print("Agent Interview validation")
    print("-" * 58)
    for name, expected_count in EXPECTED.items():
        path = DOCS / name
        if not path.exists():
            continue
        file_errors = validate_document(path, expected_count)
        errors.extend(file_errors)
        total += expected_count
        status = "FAIL" if file_errors else "OK"
        print(f"{status:4}  {expected_count:4}  {name}")

    errors.extend(validate_readme_links())
    glossary_errors = validate_glossary()
    errors.extend(glossary_errors)
    errors.extend(validate_product_question_locations())
    glossary_status = "FAIL" if glossary_errors else "OK"
    if GLOSSARY.exists():
        glossary_count = len(
            GLOSSARY_ITEM_RE.findall(GLOSSARY.read_text(encoding="utf-8-sig"))
        )
        print(f"{glossary_status:4}  {glossary_count:4}  {GLOSSARY.name}")
    if total != 1820:
        errors.append(f"总题数应为 1820，配置值为 {total}")

    print("-" * 58)
    print(f"Total: {total}")
    if errors:
        print("\nValidation errors:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("All checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

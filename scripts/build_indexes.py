#!/usr/bin/env python3
"""Build question counts, chapter indexes, and the duplicate-candidate report."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TAXONOMY = json.loads((ROOT / "scripts" / "taxonomy.json").read_text(encoding="utf-8"))
QUESTION_RE = re.compile(
    r'^<a id="([a-z]+-\d{3})"></a>\s*\n###\s+(.+?)\s*$',
    re.MULTILINE,
)
STATS_START = "<!-- QUESTION_STATS_START -->"
STATS_END = "<!-- QUESTION_STATS_END -->"
CORE_ALLOCATIONS = {
    "ARC": 10, "TRANS": 8, "PLAN": 12, "CTX": 10, "TOOL": 10, "MULTI": 8,
    "RAG": 12, "MODEL": 8, "GOV": 10, "ENG": 8, "OCLAW": 2, "CC": 2,
}


def question_files(chapter: dict[str, str]) -> list[Path]:
    directory = ROOT / chapter["path"]
    return [
        path
        for path in sorted(directory.glob("*.md"))
        if path.name not in {"README.md", "references.md"}
        and QUESTION_RE.search(path.read_text(encoding="utf-8-sig"))
    ]


def questions_in(path: Path) -> list[tuple[str, str]]:
    return [(match.group(1).upper(), match.group(2)) for match in QUESTION_RE.finditer(path.read_text(encoding="utf-8-sig"))]


def replace_stats(readme: str) -> str:
    rows: list[str] = []
    total = 0
    for chapter in TAXONOMY:
        count = sum(len(questions_in(path)) for path in question_files(chapter))
        total += count
        link = f"{chapter['path']}/README.md"
        rows.append(f"| {chapter['area']} | [{chapter['title']}]({link}) | {count} |")
    block = "\n".join(
        [
            STATS_START,
            "| 领域 | 章节 | 题数 |",
            "|---|---|---:|",
            *rows,
            f"|  | **合计** | **{total:,}** |",
            STATS_END,
        ]
    )
    pattern = re.compile(re.escape(STATS_START) + r"[\s\S]*?" + re.escape(STATS_END))
    if not pattern.search(readme):
        raise ValueError("README.md is missing question-stat markers")
    readme = pattern.sub(block, readme)
    return re.sub(r"现收录 \*\*[\d,]+ 道", f"现收录 **{total:,} 道", readme)


def chapter_index_content(chapter: dict[str, str], current: str) -> str:
    files = question_files(chapter)
    count = sum(len(questions_in(path)) for path in files)
    current = re.sub(r"本章共 \*\*\d+\*\* 题", f"本章共 **{count}** 题", current)
    rows = []
    for path in files:
        text = path.read_text(encoding="utf-8-sig")
        title_match = re.search(r"^#\s+(.+?)\s*$", text, re.MULTILINE)
        title = title_match.group(1) if title_match else path.stem
        rows.append(f"| [{title}]({path.name}) | {len(questions_in(path))} |")
    section = "\n".join(
        [
            "## 子主题",
            "",
            "| 子主题 | 题数 |",
            "|---|---:|",
            *rows,
            "",
        ]
    )
    pattern = re.compile(r"^## 子主题\s*$[\s\S]*?(?=^## |\Z)", re.MULTILINE)
    if not pattern.search(current):
        raise ValueError(f"Missing topic section: {chapter['path']}/README.md")
    return pattern.sub(section, current).rstrip() + "\n"


def normalize_title(title: str) -> str:
    title = re.sub(r"[（(][^）)]*(?:面|Agent|高级|初级|中级)[^）)]*[）)]\s*$", "", title, flags=re.IGNORECASE)
    return re.sub(r"[\s`*_，。！？、：；,.!?;:“”\"'（）()\-/]", "", title.casefold())


def duplicate_report() -> str:
    records: list[dict[str, object]] = []
    for chapter in TAXONOMY:
        for path in question_files(chapter):
            text = path.read_text(encoding="utf-8-sig")
            topic_match = re.search(r"^#\s+(.+?)\s*$", text, re.MULTILINE)
            topic = topic_match.group(1) if topic_match else path.stem
            for stable_id, title in questions_in(path):
                records.append({"id": stable_id, "title": title, "chapter": chapter["title"], "topic": topic, "path": path})
    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for record in records:
        groups[normalize_title(str(record["title"]))].append(record)
    duplicates = [group for group in groups.values() if len(group) > 1]
    duplicates.sort(key=lambda group: (-len(group), str(group[0]["title"])))
    report_path = ROOT / "docs" / "reference" / "duplicate-questions.md"
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
            rel = Path(os.path.relpath(Path(record["path"]), report_path.parent)).as_posix()
            label = "主问题候选" if item_index == 0 else "相似问法"
            lines.append(f"- {label}：[{record['id']} · {record['title']}]({rel}#{str(record['id']).lower()})（{record['chapter']} / {record['topic']}）")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def core_questions() -> str:
    guide_path = ROOT / "docs" / "00-guide" / "core-100.md"
    lines = [
        "# 核心 100 题",
        "",
        "> 从完整题库中按章节配额选取原始序号靠前的基础问题，适合快速建立知识主干。该清单由稳定 ID 自动生成，不复制答案。",
        "",
    ]
    selected_total = 0
    for chapter in TAXONOMY:
        records: list[tuple[int, str, str, Path]] = []
        for path in question_files(chapter):
            for stable_id, title in questions_in(path):
                records.append((int(stable_id.rsplit("-", 1)[1]), stable_id, title, path))
        selected = sorted(records)[:CORE_ALLOCATIONS[chapter["prefix"]]]
        selected_total += len(selected)
        lines.extend([f"## {chapter['title']}", ""])
        for _, stable_id, title, path in selected:
            rel = Path(os.path.relpath(path, guide_path.parent)).as_posix()
            lines.append(f"- [{stable_id} · {title}]({rel}#{stable_id.lower()})")
        lines.append("")
    if selected_total != 100:
        raise ValueError(f"Core-question allocation produced {selected_total}, expected 100")
    return "\n".join(lines).rstrip() + "\n"


def update(path: Path, expected: str, check: bool, changed: list[Path]) -> None:
    current = path.read_text(encoding="utf-8-sig") if path.exists() else ""
    if current == expected:
        return
    changed.append(path)
    if not check:
        path.write_text(expected, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail if generated indexes are stale")
    args = parser.parse_args()
    changed: list[Path] = []

    root_readme = ROOT / "README.md"
    update(root_readme, replace_stats(root_readme.read_text(encoding="utf-8-sig")), args.check, changed)
    for chapter in TAXONOMY:
        index = ROOT / chapter["path"] / "README.md"
        current = index.read_text(encoding="utf-8-sig")
        update(index, chapter_index_content(chapter, current), args.check, changed)
    duplicate_path = ROOT / "docs" / "reference" / "duplicate-questions.md"
    update(duplicate_path, duplicate_report(), args.check, changed)
    core_path = ROOT / "docs" / "00-guide" / "core-100.md"
    update(core_path, core_questions(), args.check, changed)

    if changed:
        action = "Stale" if args.check else "Updated"
        for path in changed:
            print(f"{action}: {path.relative_to(ROOT)}")
        return 1 if args.check else 0
    print("Generated indexes are up to date.")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())

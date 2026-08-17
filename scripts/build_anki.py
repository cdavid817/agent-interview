#!/usr/bin/env python3
"""Build deterministic Anki packages from the interview question bank."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from dataclasses import dataclass
from pathlib import Path

try:
    import genanki
    import markdown
except ImportError as exc:  # pragma: no cover - user-facing dependency check
    raise SystemExit(
        "缺少依赖，请先运行: python -m pip install genanki markdown"
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
TAXONOMY = ROOT / "scripts" / "taxonomy.json"
CORE_100 = ROOT / "docs" / "00-guide" / "core-100.md"

QUESTION_RE = re.compile(
    r'(?m)^(?P<anchors>(?:<a id="[^"]+"></a>\s*\n)+)'
    r"###\s+\d+\.\s+(?P<title>.+?)\s*$"
)
ANCHOR_RE = re.compile(r'<a id="([^"]+)"></a>')
KNOWLEDGE_RE = re.compile(r"(?m)^\*\*相关知识点[：:]\*\*\s*(.+?)\s*$")
CORE_MARKER_RE = re.compile(r"(?m)^\*\*【核心思路】\*\*\s*$")
DETAIL_MARKER_RE = re.compile(r"(?m)^\*\*【深入拆解】\*\*\s*$")


@dataclass(frozen=True)
class Question:
    qid: str
    title: str
    core_md: str
    detail_md: str
    knowledge: tuple[str, ...]
    area: str
    topic: str
    source: str


def stable_int(value: str) -> int:
    """Return a stable positive 31-bit integer for Anki model/deck IDs."""
    return int.from_bytes(hashlib.sha1(value.encode("utf-8")).digest()[:4], "big") & 0x7FFFFFFF


def tag_part(value: str) -> str:
    value = re.sub(r"[\s/\\]+", "_", value.strip())
    return re.sub(r"[^\w\-+.\u4e00-\u9fff]", "", value)


def markdown_html(value: str) -> str:
    if not value.strip():
        return ""
    return markdown.markdown(
        value.strip(),
        extensions=["tables", "fenced_code", "sane_lists"],
        output_format="html5",
    )


def select_primary_id(anchors: list[str], prefix: str) -> str:
    expected = re.compile(rf"^{re.escape(prefix)}-\d{{3,}}$", re.IGNORECASE)
    matches = [anchor for anchor in anchors if expected.match(anchor)]
    if not matches:
        raise ValueError(f"题目前没有 {prefix}-NNN 稳定 ID: {anchors}")
    return matches[-1].upper()


def split_answer(body: str) -> tuple[str, str, tuple[str, ...]]:
    knowledge_match = KNOWLEDGE_RE.search(body)
    knowledge: tuple[str, ...] = ()
    if knowledge_match:
        knowledge = tuple(
            item.strip().rstrip("。.")
            for item in re.split(r"[、,，;；]", knowledge_match.group(1))
            if item.strip()
        )
        body = body[: knowledge_match.start()] + body[knowledge_match.end() :]

    core_match = CORE_MARKER_RE.search(body)
    detail_match = DETAIL_MARKER_RE.search(body)
    if core_match and detail_match and core_match.end() <= detail_match.start():
        core = body[core_match.end() : detail_match.start()].strip()
        detail = body[detail_match.end() :].strip()
    elif core_match:
        core = body[core_match.end() :].strip()
        detail = ""
    else:
        core = body.strip()
        detail = ""
    return core, detail, knowledge


def load_questions() -> list[Question]:
    taxonomy = json.loads(TAXONOMY.read_text(encoding="utf-8"))
    questions: list[Question] = []
    seen: set[str] = set()

    for section in taxonomy:
        section_dir = ROOT / section["path"]
        for path in sorted(section_dir.glob("*.md")):
            if path.name.lower() in {"readme.md", "references.md"}:
                continue
            text = path.read_text(encoding="utf-8")
            matches = list(QUESTION_RE.finditer(text))
            for index, match in enumerate(matches):
                anchors = ANCHOR_RE.findall(match.group("anchors"))
                qid = select_primary_id(anchors, section["prefix"])
                if qid in seen:
                    raise ValueError(f"重复稳定 ID: {qid}")
                seen.add(qid)
                body_end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
                body = text[match.end() : body_end].strip()
                core, detail, knowledge = split_answer(body)
                if not core:
                    raise ValueError(f"题目没有答案: {qid}")
                questions.append(
                    Question(
                        qid=qid,
                        title=match.group("title").strip(),
                        core_md=core,
                        detail_md=detail,
                        knowledge=knowledge,
                        area=section["area"],
                        topic=section["title"],
                        source=path.relative_to(ROOT).as_posix(),
                    )
                )
    return questions


def load_core_ids() -> set[str]:
    text = CORE_100.read_text(encoding="utf-8")
    return {match.upper() for match in re.findall(r"\b([A-Z]+-\d{3})\b", text)}


CSS = r"""
.card { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif; font-size: 18px; line-height: 1.65; color: #202124; background: #fbfaf7; max-width: 860px; margin: auto; padding: 22px; text-align: left; }
.meta { color: #64748b; font-size: 13px; letter-spacing: .02em; margin-bottom: 12px; }
.question { font-size: 25px; font-weight: 700; line-height: 1.4; color: #102a43; margin: 10px 0 20px; }
.prompt { color: #64748b; border-left: 4px solid #cbd5e1; padding-left: 12px; font-size: 15px; }
.answer-title { color: #0f766e; font-size: 14px; font-weight: 700; letter-spacing: .08em; margin: 18px 0 8px; }
.core { border-left: 4px solid #14b8a6; background: #f0fdfa; padding: 10px 16px; border-radius: 5px; }
details { margin-top: 16px; border: 1px solid #d7dee8; border-radius: 7px; background: #fff; padding: 10px 14px; }
summary { cursor: pointer; color: #334155; font-weight: 700; }
table { border-collapse: collapse; width: 100%; font-size: 15px; display: block; overflow-x: auto; }
th, td { border: 1px solid #cbd5e1; padding: 6px 9px; vertical-align: top; }
th { background: #eaf0f6; }
pre { overflow-x: auto; background: #172033; color: #e2e8f0; padding: 12px; border-radius: 6px; }
code { font-family: Consolas, monospace; font-size: .9em; }
.knowledge { margin-top: 18px; color: #475569; font-size: 14px; }
.source { margin-top: 16px; color: #94a3b8; font-size: 12px; }
hr#answer { border: 0; border-top: 1px solid #d7dee8; margin: 22px 0; }
"""


def build_model() -> genanki.Model:
    return genanki.Model(
        stable_int("AgentInterview::model::v1"),
        "AgentInterview 面试问答 v1",
        fields=[
            {"name": "ID"},
            {"name": "Question"},
            {"name": "Core"},
            {"name": "Detail"},
            {"name": "Knowledge"},
            {"name": "Source"},
        ],
        templates=[
            {
                "name": "面试题",
                "qfmt": '<div class="meta">{{ID}}</div><div class="question">{{Question}}</div><div class="prompt">先口述：定义 / 机制 / 取舍 / 风险 / 指标，再翻面核对。</div>',
                "afmt": '{{FrontSide}}<hr id="answer"><div class="answer-title">核心思路</div><div class="core">{{Core}}</div>{{#Detail}}<details><summary>深入拆解（点击展开）</summary>{{Detail}}</details>{{/Detail}}{{#Knowledge}}<div class="knowledge"><b>相关知识点：</b>{{Knowledge}}</div>{{/Knowledge}}<div class="source">来源：{{Source}}</div>',
            }
        ],
        css=CSS,
        sort_field_index=0,
    )


def question_tags(question: Question, is_core: bool) -> list[str]:
    tags = [
        f"area::{tag_part(question.area)}",
        f"topic::{tag_part(question.topic)}",
        f"prefix::{question.qid.split('-', 1)[0]}",
    ]
    if is_core:
        tags.append("set::核心100")
    for item in question.knowledge:
        clean = tag_part(item)
        if clean:
            tags.append(f"knowledge::{clean}")
    company_patterns = {
        "DeepSeek": "DeepSeek",
        "腾讯": "腾讯",
        "百度": "百度",
        "豆包": "豆包",
        "千问": "千问",
        "Agent初级": "Agent初级",
        "Agent中级": "Agent中级",
        "Agent高级": "Agent高级",
    }
    for needle, tag in company_patterns.items():
        if needle in question.title:
            tags.append(f"source::{tag}")
    return sorted(set(tags))


def make_note(model: genanki.Model, question: Question, is_core: bool) -> genanki.Note:
    return genanki.Note(
        model=model,
        guid=genanki.guid_for("AgentInterview", question.qid),
        fields=[
            question.qid,
            html.escape(question.title),
            markdown_html(question.core_md),
            markdown_html(question.detail_md),
            html.escape("、".join(question.knowledge)),
            html.escape(question.source),
        ],
        tags=question_tags(question, is_core),
    )


def write_package(
    questions: list[Question], core_ids: set[str], output: Path, package_name: str
) -> None:
    model = build_model()
    decks: dict[str, genanki.Deck] = {}
    for question in questions:
        deck_name = f"{package_name}::{question.area}::{question.topic}"
        deck = decks.setdefault(deck_name, genanki.Deck(stable_int(deck_name), deck_name))
        deck.add_note(make_note(model, question, question.qid in core_ids))
    output.parent.mkdir(parents=True, exist_ok=True)
    genanki.Package(list(decks.values())).write_to_file(str(output))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "dist" / "anki", help="输出目录"
    )
    args = parser.parse_args()

    questions = load_questions()
    core_ids = load_core_ids()
    question_ids = {question.qid for question in questions}
    missing = sorted(core_ids - question_ids)
    if missing:
        raise ValueError(f"核心 100 存在无对应题目的 ID: {', '.join(missing)}")
    if not questions:
        raise ValueError("没有解析到任何题目")
    if len(core_ids) != 100:
        raise ValueError(f"预期核心 100 题，实际解析到 {len(core_ids)} 题")

    full_path = args.output_dir / "AgentInterview-完整题库.apkg"
    core_path = args.output_dir / "AgentInterview-核心100.apkg"
    write_package(questions, core_ids, full_path, "AgentInterview")
    write_package(
        [question for question in questions if question.qid in core_ids],
        core_ids,
        core_path,
        "AgentInterview 核心100",
    )
    print(f"完整题库: {full_path} ({len(questions)} 张)")
    print(f"核心 100: {core_path} ({len(core_ids)} 张)")


if __name__ == "__main__":
    main()

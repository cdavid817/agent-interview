#!/usr/bin/env python3
"""Validate the structure and statistics of the Agent Interview repository."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EXPECTED = {
    "一、Agent核心架构.md": 114,
    "二、任务规划与执行.md": 311,
    "三、上下文与知识系统.md": 391,
    "四、工具与能力体系.md": 239,
    "五、多Agent与协作.md": 34,
    "六、模型能力与成本.md": 206,
    "七、安全、治理与可观测性.md": 191,
    "八、工程落地与平台化.md": 245,
}
QUESTION_RE = re.compile(r"^####\s+(\d+)、(.+?)\s*$", re.MULTILINE)
LOCAL_LINK_RE = re.compile(r"\[[^\]]+\]\((?!https?://|#)([^)]+)\)")


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
    if total != 1731:
        errors.append(f"总题数应为 1731，配置值为 {total}")

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

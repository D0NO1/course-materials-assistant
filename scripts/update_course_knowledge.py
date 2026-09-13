"""Merge structured course findings into a small, readable course knowledge base."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


COLLECTIONS = (
    "glossary",
    "topics",
    "assignments",
    "milestones",
    "exam_focus",
    "source_chunks",
    "concept_relations",
    "question_bank",
)
KEYS = {
    "glossary": "term",
    "topics": "topic",
    "assignments": "name",
    "milestones": "name",
    "exam_focus": "topic",
    "source_chunks": "id",
    "concept_relations": "relation",
    "question_bank": "question",
}


def _load(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def _merge(old: list[dict], new: list[dict], key: str) -> list[dict]:
    merged = {str(item.get(key, "")).casefold(): dict(item) for item in old if item.get(key)}
    for item in new:
        identifier = str(item.get(key, "")).casefold()
        if identifier:
            merged[identifier] = dict(item)
    return sorted(merged.values(), key=lambda item: str(item.get(key, "")).casefold())


def update_knowledge(course_root: str | Path, payload: dict) -> dict:
    root = Path(course_root).resolve()
    metadata = root / ".course-assistant"
    metadata.mkdir(parents=True, exist_ok=True)
    result = {}
    for collection in COLLECTIONS:
        path = metadata / f"{collection}.json"
        result[collection] = _merge(
            _load(path), payload.get(collection, []), KEYS[collection]
        )
        path.write_text(
            json.dumps(result[collection], ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    _write_glossary(metadata / "glossary.md", result["glossary"])
    _write_exam_focus(metadata / "exam-focus.md", result["exam_focus"])
    return result


def _write_glossary(path: Path, items: list[dict]) -> None:
    lines = ["# Course Glossary / 课程术语表", "", "| Term / 术语 | Meaning / 含义 |", "|---|---|"]
    for item in items:
        meaning = item.get("meaning", "")
        if item.get("meaning_zh"):
            meaning = f"{meaning}<br>{item['meaning_zh']}"
        lines.append(f"| {item.get('term', '')} | {meaning} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_exam_focus(path: Path, items: list[dict]) -> None:
    lines = [
        "# Final Exam Focus / Final Exam 考点",
        "",
        "This file accumulates confirmed exam-relevant topics from analyzed course materials.<br>本文件持续整理课程材料中确认过的期末考试相关内容。",
        "",
    ]
    for number, item in enumerate(items, start=1):
        lines.append(f"## {number}. {item.get('topic', '')}")
        if item.get("why"):
            why = item["why"]
            if item.get("why_zh"):
                why = f"{why}<br>{item['why_zh']}"
            lines.append(f"Why it matters / 重要原因: {why}")
        if item.get("must_know"):
            must_know = item["must_know"]
            if item.get("must_know_zh"):
                must_know = f"{must_know}<br>{item['must_know_zh']}"
            lines.append(f"Must know / 必须掌握: {must_know}")
        sources = item.get("sources", [])
        if sources:
            lines.append("Sources: " + "; ".join(str(source) for source in sources))
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("course_root", type=Path)
    parser.add_argument("payload_json", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.payload_json.read_text(encoding="utf-8"))
    print(json.dumps(update_knowledge(args.course_root, payload), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

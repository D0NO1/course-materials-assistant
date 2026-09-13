"""Generate a cumulative, source-backed Final Exam review package."""

from __future__ import annotations

import json
from pathlib import Path


def _load(metadata: Path, name: str) -> list[dict]:
    path = metadata / f"{name}.json"
    if not path.exists():
        return []
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def _priority(item: dict) -> str:
    value = str(item.get("importance", "medium")).casefold()
    if value in {"high", "critical", "very high"}:
        return "high_priority"
    if value in {"low", "review-if-time"}:
        return "review_if_time"
    return "medium_priority"


def generate_exam_review(course_root: str | Path) -> dict:
    root = Path(course_root).resolve()
    metadata = root / ".course-assistant"
    topics = {str(item.get("topic", "")).casefold(): dict(item) for item in _load(metadata, "topics") if item.get("topic")}
    for focus in _load(metadata, "exam_focus"):
        key = str(focus.get("topic", "")).casefold()
        if not key:
            continue
        merged = topics.setdefault(key, {"topic": focus["topic"]})
        merged.update(focus)
    review = {
        "course": root.name,
        "high_priority": [],
        "medium_priority": [],
        "review_if_time": [],
        "question_bank": _load(metadata, "question_bank"),
        "source_policy": "Source-backed review; actual exam questions are not known.",
    }
    for item in sorted(topics.values(), key=lambda value: str(value.get("topic", "")).casefold()):
        review[_priority(item)].append(item)
    metadata.mkdir(parents=True, exist_ok=True)
    (metadata / "final-exam-review.json").write_text(
        json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    _write_markdown(metadata / "final-exam-review.md", review)
    return review


def _write_markdown(path: Path, review: dict) -> None:
    lines = [
        "# Final Exam Review / Final Exam 复习",
        "",
        "Source-backed review; actual exam questions are not known.<br>基于课程材料的复习；无法保证是实际考试题目。",
        "",
    ]
    labels = {
        "high_priority": "High Priority / 高优先级",
        "medium_priority": "Medium Priority / 中优先级",
        "review_if_time": "Review If Time / 有时间再复习",
    }
    for key, label in labels.items():
        lines.append(f"## {label}")
        for item in review[key]:
            lines.append(f"- **{item.get('topic', '')}**")
            if item.get("why"):
                why = item["why"]
                if item.get("why_zh"):
                    why += f"<br>{item['why_zh']}"
                lines.append(f"  - Why / 原因: {why}")
            if item.get("must_know"):
                must = item["must_know"]
                if item.get("must_know_zh"):
                    must += f"<br>{item['must_know_zh']}"
                lines.append(f"  - Must know / 必须掌握: {must}")
            if item.get("sources"):
                lines.append(f"  - Sources / 来源: {'; '.join(map(str, item['sources']))}")
        lines.append("")
    if review["question_bank"]:
        lines.append("## Self-Test / 自测")
        for item in review["question_bank"]:
            lines.append(f"- Question / 问题: {item.get('question', '')}")
            lines.append(f"  - Answer / 答案: {item.get('answer', '')}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

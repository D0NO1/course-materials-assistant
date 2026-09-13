"""Generate an assignment and due-date tracker from extracted material."""

from __future__ import annotations

import json
import re
from pathlib import Path


DATE_PATTERNS = (
    re.compile(r"\b(20\d{2})-(\d{2})-(\d{2})\b"),
    re.compile(r"\b(\d{1,2})/(\d{1,2})/(20\d{2})\b"),
)


def _dates(text: str) -> list[str]:
    values = []
    for pattern in DATE_PATTERNS:
        for match in pattern.finditer(text):
            parts = match.groups()
            if len(parts[0]) == 4:
                values.append("-".join(parts))
            else:
                month, day, year = parts
                values.append(f"{year}-{int(month):02d}-{int(day):02d}")
    return values


def _paragraph_text(material: dict) -> list[tuple[str, str]]:
    content = material.get("content", {})
    paragraphs = content.get("paragraphs", []) if isinstance(content, dict) else []
    return [(str(item.get("text", "")), str(material.get("file", ""))) for item in paragraphs]


def generate_assignment_tracker(course_root: str | Path, extracted_materials: list[dict]) -> dict:
    root = Path(course_root).resolve()
    groups: dict[str, dict] = {}
    for material in extracted_materials:
        for text, filename in _paragraph_text(material):
            lowered = text.casefold()
            if not any(token in lowered for token in ("assignment", "milestone", "project", "homework", "due")):
                continue
            match = re.search(r"\b((?:milestone|assignment|project|homework)\s*\w*)\b", text, re.I)
            name = match.group(1).strip() if match else Path(filename).stem
            key = name.casefold()
            item = groups.setdefault(key, {
                "name": name,
                "due_dates": [],
                "deliverables": [],
                "requirements": [],
                "conflicts": [],
                "status": "discovered",
                "sources": [],
            })
            for due_date in _dates(text):
                if due_date not in item["due_dates"]:
                    item["due_dates"].append(due_date)
            if filename and filename not in item["sources"]:
                item["sources"].append(filename)
            if any(token in lowered for token in ("submit", "required", "include")):
                item["requirements"].append(text)
    assignments = sorted(groups.values(), key=lambda value: value["name"].casefold())
    for item in assignments:
        item["due_dates"].sort()
        if len(item["due_dates"]) > 1:
            item["conflicts"] = ["Multiple source dates found; verify with the instructor or current announcement."]
    result = {"course": root.name, "assignments": assignments}
    metadata = root / ".course-assistant"
    metadata.mkdir(parents=True, exist_ok=True)
    (metadata / "assignment-tracker.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    _write_markdown(metadata / "assignment-tracker.md", result)
    return result


def _write_markdown(path: Path, result: dict) -> None:
    lines = ["# Assignment Tracker / 作业追踪", ""]
    for item in result["assignments"]:
        dates = ", ".join(item["due_dates"]) or "Not found / 未找到"
        lines.append(f"## {item['name']}")
        lines.append(f"Due dates / 截止日期: {dates}")
        lines.append(f"Status / 状态: {item['status']}")
        if item["conflicts"]:
            lines.append("Conflict / 冲突: " + " ".join(item["conflicts"]))
        if item["requirements"]:
            lines.append("Requirements / 要求:")
            lines.extend(f"- {value}" for value in item["requirements"])
        if item["sources"]:
            lines.append("Sources / 来源: " + "; ".join(item["sources"]))
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")

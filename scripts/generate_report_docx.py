"""Generate a readable Word report from structured course-analysis data."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt

from learning_config import order_bilingual


def _safe_name(value: str) -> str:
    if isinstance(value, dict):
        value = value.get("en", "course-analysis")
    value = re.sub(r"[<>:\"/\\|?*]+", "", value).strip()
    return re.sub(r"\s+", "-", value) or "course-analysis"


def _xml_safe(value: str) -> str:
    """Remove characters forbidden by XML 1.0 while preserving normal whitespace."""
    return "".join(char for char in value if char in "\t\n\r" or ord(char) >= 32)


def _bilingual(value: object, mode: str = "en-zh") -> tuple[str, str | None]:
    if isinstance(value, dict):
        en = str(value.get("en", ""))
        zh = str(value.get("zh", "")) if value.get("zh") else ""
        ordered = order_bilingual(en, zh, mode)
        return ordered[0], ordered[1] if len(ordered) > 1 else None
    return str(value), None


def _add_bilingual_paragraph(document: Document, value: object, mode: str = "en-zh", style: str | None = None):
    en, zh = _bilingual(value, mode)
    paragraph = document.add_paragraph(style=style)
    paragraph.add_run(_xml_safe(en))
    if zh:
        paragraph.add_run("\n" + _xml_safe(zh))
    return paragraph


def generate_report(course_root: str | Path, report: dict) -> Path:
    root = Path(course_root).resolve()
    output_dir = root / ".course-assistant" / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = report.get("output_filename") or _safe_name(report.get("title", "analysis"))
    output = output_dir / f"{stamp}-{_safe_name(str(filename))}.docx"

    document = Document()
    language_mode = str(report.get("language_mode", "en-zh"))
    section = document.sections[0]
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.8)

    normal = document.styles["Normal"]
    normal.font.name = "Aptos"
    normal.font.size = Pt(10.5)

    title = document.add_paragraph(style="Title")
    title.alignment = WD_ALIGN_PARAGRAPH.LEFT
    title_en, title_zh = _bilingual(report.get("title", "Course Analysis Report"), language_mode)
    title.add_run(title_en)
    if title_zh:
        title.add_run("\n" + title_zh)

    metadata = document.add_paragraph()
    metadata.add_run("Course / 课程: ").bold = True
    metadata.add_run(str(report.get("course", root.name)))
    metadata.add_run("\nGenerated / 生成日期: ").bold = True
    metadata.add_run(str(report.get("generated", datetime.now().strftime("%Y-%m-%d"))))

    status_fields = [
        ("Analysis status", report.get("analysis_status")),
        ("Render status", report.get("render_status")),
        ("Source count", report.get("source_count")),
    ]
    status_fields = [(label, value) for label, value in status_fields if value is not None]
    if status_fields:
        status = document.add_paragraph()
        for index, (label, value) in enumerate(status_fields):
            if index:
                status.add_run("\n")
            status.add_run(f"{label}: ").bold = True
            status.add_run(str(value))

    document.add_heading("Core Summary / 核心总结", level=1)
    _add_bilingual_paragraph(document, report.get("summary", ""), language_mode)

    for section_data in report.get("sections", []):
        heading = section_data.get("heading", "Section")
        if section_data.get("heading_zh"):
            heading = f"{heading} / {section_data['heading_zh']}"
        document.add_heading(str(heading), level=1)
        for item in section_data.get("items", []):
            _add_bilingual_paragraph(document, item, language_mode, style="List Bullet")

    sources = report.get("sources", [])
    if sources:
        document.add_heading("Sources / 来源", level=1)
        for source in sources:
            document.add_paragraph(str(source), style="List Bullet")

    document.save(output)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("course_root", type=Path)
    parser.add_argument("report_json", type=Path, help="JSON file containing report data")
    args = parser.parse_args()
    report = json.loads(args.report_json.read_text(encoding="utf-8"))
    print(generate_report(args.course_root, report))


if __name__ == "__main__":
    main()

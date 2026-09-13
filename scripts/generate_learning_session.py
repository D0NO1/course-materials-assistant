"""Create deterministic, source-backed student learning sessions."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from learning_config import DEFAULT_CONFIG, order_bilingual

SUPPORTED_MODES = ("preview", "understand", "review", "assignment", "exam")


def _text_items(material: dict) -> list[tuple[str, str]]:
    content = material.get("content") or {}
    result: list[tuple[str, str]] = []
    for page in content.get("pages", []):
        result.append((str(page.get("text", "")), f"{material.get('file', '')}, p. {page.get('page')}"))
    for slide in content.get("slides", []):
        text = " ".join([str(slide.get("title", "")), *map(str, slide.get("text", [])), str(slide.get("notes", ""))]).strip()
        result.append((text, f"{material.get('file', '')}, slide {slide.get('slide')}"))
    for paragraph in content.get("paragraphs", []):
        label = paragraph.get("heading") or paragraph.get("style") or f"paragraph {paragraph.get('paragraph', '')}"
        result.append((str(paragraph.get("text", "")), f"{material.get('file', '')}, {label}"))
    return [(text.strip(), locator) for text, locator in result if text.strip()]


def _item(en: str, zh: str, sources: list[str] | None = None, evidence: str | None = None) -> dict:
    value = {"en": en, "zh": zh}
    if sources:
        value["sources"] = sorted(set(sources))
    if evidence:
        value["evidence"] = evidence
    return value


def _collect(materials: list[dict]) -> tuple[list[tuple[str, str]], list[str], list[str]]:
    texts: list[tuple[str, str]] = []
    sources: list[str] = []
    warnings: list[str] = []
    for material in materials:
        file = str(material.get("file", ""))
        if file:
            sources.append(file)
        texts.extend(_text_items(material))
        if material.get("status") != "extracted":
            warnings.append(f"{file}: {material.get('status', 'unknown')} - {'; '.join(map(str, material.get('warnings', [])))}")
    return texts, sorted(set(sources)), warnings


def _dates(text: str) -> list[str]:
    return re.findall(r"\b20\d{2}-\d{2}-\d{2}\b", text)


def _sections(mode: str, texts: list[tuple[str, str]], config: dict) -> list[dict]:
    all_text = " ".join(text for text, _ in texts)
    sources = [locator for _, locator in texts]
    objective_lines = [(text, locator) for text, locator in texts if any(token in text.casefold() for token in ("objective", "goal", "learn", "explain"))]
    assignment_lines = [(text, locator) for text, locator in texts if any(token in text.casefold() for token in ("assignment", "milestone", "project", "homework", "submit", "due"))]
    key_lines = [(text, locator) for text, locator in texts if any(token in text.casefold() for token in ("scope", "sdlc", "feasibility", "system", "process", "model"))]
    evidence = "course-confirmed emphasis" if objective_lines else "repeated across materials"
    if mode == "preview":
        items = [_item(text, f"课程材料中的学习目标：{text}", [locator], "course-confirmed emphasis") for text, locator in objective_lines[:5]]
        items.append(_item("What should I know before class? Review the key terms and the first source pages or slides.", "课前应该知道什么？先复习关键词，并阅读最前面的相关页面或幻灯片。", sources[:5], "assistant-priority inference"))
        items.append(_item("What should I ask in class? Ask about any term or diagram that remains unclear.", "课堂上应该问什么？对于仍然不清楚的术语或图表，及时向老师提问。", [], "assistant-priority inference"))
        return [{"heading": "Pre-Class Preview", "heading_zh": "课前预习", "items": items}]
    if mode == "understand":
        items = [_item(text, f"中文解释：{text}", [locator], evidence) for text, locator in key_lines[:8]]
        items.append(_item("The material should be understood through its concepts, relationships, and examples.", "理解材料时，应同时关注概念、概念之间的关系以及例子。", sources[:5], "assistant-priority inference"))
        return [{"heading": "Lecture Understanding", "heading_zh": "课堂理解", "items": items}]
    if mode == "review":
        items = [_item(f"Key point: {text}", f"核心要点：{text}", [locator], evidence) for text, locator in key_lines[:8]]
        items.append(_item("Self-test: Can you define the main terms and explain their relationships without looking at the notes?", "自测：不看笔记时，你能否定义主要术语并解释它们之间的关系？", sources[:5], "assistant-priority inference"))
        items.append(_item("Review next: revisit the items marked unclear and compare them with the source material.", "下一步复习：重新查看标记为不清楚的内容，并与原始课程材料进行对照。", [], "assistant-priority inference"))
        return [{"heading": "Post-Class Review", "heading_zh": "课后复习", "items": items}]
    if mode == "assignment":
        items = [_item(f"Assignment evidence: {text}", f"作业材料：{text}", [locator], "course-confirmed emphasis") for text, locator in assignment_lines[:8]]
        dates = sorted(set(date for text, _ in assignment_lines for date in _dates(text)))
        if dates:
            items.append(_item(f"Due dates found: {', '.join(dates)}", f"发现的截止日期：{', '.join(dates)}", sources[:5], "needs confirmation" if len(dates) > 1 else "course-confirmed emphasis"))
        items.append(_item("Submission checklist: confirm deliverables, required format, deadline, and rubric coverage before submitting.", "提交清单：提交前确认交付物、格式要求、截止日期以及评分标准覆盖情况。", [], "assistant-priority inference"))
        return [{"heading": "Assignment Requirement Guide", "heading_zh": "作业要求指南", "items": items}]
    items = [_item(f"Priority topic: {text}", f"优先掌握的考点：{text}", [locator], evidence) for text, locator in key_lines[:8]]
    items.append(_item("Generated question angles are study prompts; actual exam questions are not known.", "生成的问题角度只是复习提示；无法知道实际考试题目。", sources[:5], "needs confirmation"))
    items.append(_item("Last-week plan: review high-value definitions, comparisons, processes, and application examples, then complete the self-test.", "最后一周计划：复习高价值定义、比较、流程和应用例子，然后完成自测。", [], "assistant-priority inference"))
    return [{"heading": "Final Exam Focus", "heading_zh": "Final Exam 考点", "items": items}]


def generate_learning_session(course_root: str | Path, extracted_materials: list[dict], mode: str, config: dict | None = None) -> dict:
    if mode not in SUPPORTED_MODES:
        raise ValueError(f"unsupported learning mode: {mode}")
    root = Path(course_root).resolve()
    settings = dict(DEFAULT_CONFIG)
    settings.update(config or {})
    texts, sources, warnings = _collect(extracted_materials)
    sections = _sections(mode, texts, settings)
    result = {
        "course": root.name,
        "mode": mode,
        "language_mode": settings.get("language_mode", "en-zh"),
        "audience": settings.get("audience", DEFAULT_CONFIG["audience"]),
        "title": {"en": f"{mode.title()} Learning Guide", "zh": "双语学习指南"},
        "summary": {"en": "A source-backed learning guide generated from the indexed course materials.", "zh": "根据已索引课程材料生成的、有来源依据的学习指南。"},
        "sections": sections,
        "sources": sources,
        "warnings": warnings,
        "source_policy": "Source-backed study support; actual exam questions are not known.",
        "generated": datetime.now().strftime("%Y-%m-%d"),
    }
    return result


def write_learning_session(course_root: str | Path, result: dict) -> Path:
    root = Path(course_root).resolve()
    metadata = root / ".course-assistant"
    metadata.mkdir(parents=True, exist_ok=True)
    path = metadata / f"learning-session-{result['mode']}.json"
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path

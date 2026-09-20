"""Create deterministic, source-backed student learning sessions."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from learning_config import DEFAULT_CONFIG, order_bilingual
from translation_support import translate_text

SUPPORTED_MODES = ("preview", "understand", "review", "assignment", "exam")
LEARNING_FILENAMES = {
    "preview": "01-课前预习-双语",
    "understand": "02-课堂理解-双语",
    "review": "03-课后复习-双语",
    "assignment": "04-作业任务-双语",
    "exam": "05-期末考试考点复习-双语",
}


def learning_filename(mode: str, extension: str = ".json") -> str:
    if mode not in LEARNING_FILENAMES:
        raise ValueError(f"unsupported learning mode: {mode}")
    suffix = extension if extension.startswith(".") else f".{extension}"
    return LEARNING_FILENAMES[mode] + suffix


def _text_items(material: dict) -> list[tuple[str, str]]:
    content = material.get("content") or {}
    result: list[tuple[str, str]] = []
    for page in content.get("pages", []):
        text = _clean_source_text(page.get("text", ""))
        result.append((text, f"{material.get('file', '')}, p. {page.get('page')}"))
    for slide in content.get("slides", []):
        text = _slide_text(slide)
        result.append((text, f"{material.get('file', '')}, slide {slide.get('slide')}"))
    for paragraph in content.get("paragraphs", []):
        label = paragraph.get("heading") or paragraph.get("style") or f"paragraph {paragraph.get('paragraph', '')}"
        text = _clean_source_text(paragraph.get("text", ""))
        result.append((text, f"{material.get('file', '')}, {label}"))
    return [(text, locator) for text, locator in result if text]


def _clean_source_text(value: object) -> str:
    text = str(value or "")
    text = text.replace("\u000b", " ").replace("\u00a0", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _slide_text(slide: dict) -> str:
    """Build one readable slide record without repeating title, notes, or footer text."""
    title = _clean_source_text(slide.get("title", ""))
    raw_text = [str(value) for value in slide.get("text", []) if str(value).strip()]
    candidates = raw_text if raw_text else [str(slide.get("notes", ""))]
    title_key = title.casefold()
    slide_number = str(slide.get("slide", "")).strip()
    parts: list[str] = []
    for candidate in candidates:
        for fragment in re.split(r"\s*\n\s*", candidate):
            text = _clean_source_text(fragment)
            if not text or text.casefold() == title_key:
                continue
            if slide_number and text == slide_number:
                continue
            if "security awareness" in text.casefold() and "edition" in text.casefold():
                continue
            if text.casefold() in {part.casefold() for part in parts}:
                continue
            parts.append(text)
    ordered = [title] if title else []
    ordered.extend(parts)
    return _clean_source_text(" ".join(ordered))


def _item(en: str, zh: str, sources: list[str] | None = None, evidence: str | None = None) -> dict:
    value = {"en": en, "zh": zh}
    if sources:
        value["sources"] = sorted(set(sources))
    if evidence:
        value["evidence"] = evidence
    return value


def _display_text(text: str, limit: int = 240) -> str:
    compact = _clean_source_text(text)
    words = compact.split()
    for size in range(min(len(words) // 2, 40), 1, -1):
        if words[:size] == words[size : size * 2]:
            words = words[size:]
            compact = " ".join(words)
            break
    return compact if len(compact) <= limit else compact[: limit - 3].rstrip() + "..."


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


COURSE_CORE = {
    "mis-301": [
        ("Information security protects devices, people, and organizational policies.", "信息安全保护设备、人员，以及组织中的政策和流程。"),
        ("Attackers differ by motivation, skill, target, and method.", "攻击者可以根据动机、技能、目标和攻击方式进行区分。"),
        ("Security awareness helps people recognize and prevent common attacks.", "安全意识帮助人们识别并预防常见攻击。"),
    ],
    "mis-328": [
        ("Analytics supports better business decisions by turning data into evidence.", "分析通过把数据转化为证据来支持更好的商业决策。"),
        ("Simon’s decision process includes intelligence, design, choice, and implementation.", "Simon 决策过程包括情报、设计、选择和实施四个阶段。"),
        ("OLTP captures operational transactions, while OLAP supports analysis and decision making.", "OLTP 负责记录日常事务，而 OLAP 用于分析和决策支持。"),
    ],
    "mis-413": [
        ("The SDLC organizes systems work from planning and analysis through design, testing, and maintenance.", "系统开发生命周期（SDLC）把系统工作组织为规划、分析、设计、测试和维护等阶段。"),
        ("Systems analysis identifies business needs and documents requirements before design begins.", "系统分析先识别业务需求并记录需求，然后再进入系统设计。"),
        ("DFD, ERD, and use cases model processes, data, and system behavior from different viewpoints.", "DFD、ERD 和用例分别从不同角度描述系统流程、数据和系统行为。"),
        ("Feasibility asks whether a proposed system is technically, economically, and operationally realistic.", "可行性分析判断拟议系统在技术、经济和运营方面是否可行。"),
    ],
    "mis-423": [
        ("A database organizes related data so it can be stored, retrieved, and used for decisions.", "数据库组织相关数据，使数据能够被存储、检索并用于决策。"),
        ("A DBMS provides the functions needed to define, store, retrieve, and manage database data.", "数据库管理系统（DBMS）提供定义、存储、检索和管理数据所需的功能。"),
        ("Relational design uses tables, keys, relationships, and normalization to reduce data problems.", "关系数据库设计使用表、键、关系和规范化来减少数据问题。"),
        ("SQL is used to manipulate data and answer increasingly complex business questions.", "SQL 用于操作数据，并回答越来越复杂的业务问题。"),
    ],
}

COURSE_SUMMARIES = {
    "mis-301": (
        "This course explains how information security protects devices, people, and organizations from changing attacks.",
        "本课程解释信息安全如何保护设备、人员和组织，并帮助学生理解不断变化的攻击方式。",
    ),
    "mis-328": (
        "This course connects business intelligence, analytics, data science, and artificial intelligence to better decisions.",
        "本课程把商业智能、分析、数据科学和人工智能联系起来，说明数据如何支持更好的商业决策。",
    ),
    "mis-413": (
        "This course follows the systems analyst's work from defining a business problem and requirements to modeling, design, testing, and maintenance.",
        "本课程按照系统分析师的工作流程展开：从定义业务问题和需求，到建模、设计、测试与维护。",
    ),
    "mis-423": (
        "This course explains why organizations move from file-based data processing to database systems and DBMS-supported data management.",
        "本课程说明组织为什么从文件系统数据处理转向数据库系统，以及数据库管理系统如何支持数据管理。",
    ),
}

COURSE_EXAM_TOPICS = {
    "mis-301": [
        ("The CIA triad defines confidentiality, integrity, and availability as core information-security goals.", "CIA 三要素把保密性、完整性和可用性定义为信息安全的核心目标。", ("confidentiality", "integrity", "availability")),
        ("Information security uses products, people, and policies to protect information at multiple layers.", "信息安全通过产品、人员以及政策和流程等多个层面保护信息。", ("products", "people", "policies")),
        ("An asset can face a threat through a vulnerability, creating risk that security controls must reduce.", "资产可能通过漏洞受到威胁并产生风险，安全控制措施的任务就是降低这种风险。", ("asset", "threat", "vulnerability", "risk")),
        ("Attackers should be compared by motivation, skill, target, and method rather than treated as one group.", "分析攻击者时要比较其动机、技能、目标和方法，不能把所有攻击者看成同一类。", ("attackers", "motivation", "target")),
        ("Password attacks, social engineering, and identity theft exploit both technical weaknesses and human behavior.", "密码攻击、社会工程和身份盗窃同时利用技术弱点与人的行为弱点。", ("password", "social engineering", "identity theft")),
        ("Malware can spread, hide itself, and deliver payloads such as theft, damage, or unauthorized control.", "恶意软件可以传播、隐藏自身，并执行数据窃取、破坏或未授权控制等载荷功能。", ("malware", "payload", "infection", "concealment")),
        ("Internet, email, browser, wireless, and mobile defenses must be updated as new attacks appear.", "互联网、电子邮件、浏览器、无线设备和移动设备的防御措施必须随着新攻击出现而更新。", ("internet", "email", "browser", "wireless", "mobile")),
        ("Privacy, cryptography, authentication, and nonrepudiation protect information and support accountability.", "隐私、密码学、身份验证和不可否认性共同保护信息，并支持责任追踪。", ("privacy", "cryptography", "authentication", "nonrepudiation")),
    ],
    "mis-328": [
        ("Business intelligence, analytics, data science, and artificial intelligence turn data into decision support.", "商业智能、分析、数据科学和人工智能把数据转化为决策支持。", ("business intelligence", "analytics", "data science", "artificial intelligence")),
        ("Simon’s decision process moves through intelligence, design, choice, and implementation.", "Simon 决策过程依次包括情报、设计、选择和实施四个阶段。", ("simon", "decision-making process", "intelligence", "choice")),
        ("A BI framework connects data sources, data management, analytics, visualization, and business users.", "商业智能框架把数据源、数据管理、分析、可视化和业务用户连接起来。", ("framework", "business intelligence", "architecture")),
        ("OLTP records fast operational transactions, while OLAP supports multidimensional analysis and management decisions.", "OLTP 记录快速的日常业务事务，而 OLAP 支持多维分析和管理决策。", ("oltp", "olap", "transaction processing", "analytic processing")),
        ("BI systems must align with business strategy and address cost, security, privacy, and data-quality concerns.", "商业智能系统必须与业务战略一致，并处理成本、安全、隐私和数据质量问题。", ("strategy", "cost", "security", "privacy", "data quality")),
        ("Artificial intelligence applies computational methods to tasks that normally require human intelligence.", "人工智能使用计算方法完成通常需要人类智能的任务。", ("artificial intelligence", "human and computer intelligence")),
        ("Data preprocessing improves the quality and usability of data before analytics begins.", "数据预处理在分析开始前提升数据的质量和可用性。", ("preprocessing", "analytics ready data", "data quality")),
        ("Predictive analytics uses historical data and variables to estimate likely future outcomes.", "预测分析使用历史数据和相关变量来估计未来可能出现的结果。", ("predictive", "model", "forecast")),
    ],
    "mis-413": [
        ("Project scope defines the boundary of the system-analysis work.", "项目范围定义系统分析工作的边界，明确项目包含什么以及不包含什么。", ("scope",)),
        ("The SDLC moves a project from planning and analysis through design, build and test, and maintenance.", "系统开发生命周期（SDLC）把项目从规划和分析推进到设计、构建与测试，再进入维护阶段。", ("sdlc", "life cycle")),
        ("Technical, economic, and operational feasibility test whether a proposed system is realistic.", "技术、经济和运营可行性分别判断拟议系统在技术、成本收益和实际使用方面是否可行。", ("technical feasibility", "economic feasibility", "operational feasibility")),
        ("Functional requirements describe what the system must do; non-functional requirements describe qualities and constraints.", "功能需求说明系统必须做什么；非功能需求说明系统应达到的质量和约束条件。", ("functional requirements", "non-functional requirements")),
        ("A data-flow diagram models processes, data stores, data flows, and external entities.", "数据流图（DFD）描述处理过程、数据存储、数据流和外部实体。", ("data-flow diagram", "data flow")),
        ("An entity-relationship diagram models data entities, attributes, and relationships.", "实体关系图（ERD）描述数据实体、属性以及实体之间的关系。", ("entity-relationship diagram", "erd", "data modeling")),
        ("A use case describes how an actor interacts with the system to achieve a goal.", "用例描述参与者如何与系统交互以完成一个目标。", ("use case", "uml", "actor")),
        ("Design turns analyzed requirements into interfaces, architecture, and implementation decisions.", "系统设计把已经分析的需求转化为界面、架构和实施方案。", ("design", "interface", "architecture")),
        ("Testing and maintenance verify the system and keep it useful after delivery.", "测试用于验证系统，维护则确保系统交付后仍然有用并能够适应变化。", ("testing", "maintenance", "implementation")),
    ],
    "mis-423": [
        ("Data are raw facts, while information is processed data that has meaning for a user.", "数据是原始事实；信息是经过处理并对用户具有意义的数据。", ("data versus information", "raw facts", "processed data")),
        ("File-system processing stores data in separate files, which makes sharing and consistent management difficult.", "文件系统把数据分散存储在不同文件中，因此共享数据和保持一致管理比较困难。", ("file system", "evolution", "file system data processing")),
        ("Data dependence forces programs to change when file structures change; data independence reduces that coupling.", "数据依赖要求文件结构变化时同步修改程序；数据独立性可以减少这种耦合。", ("structural and data dependence", "data independence")),
        ("Data redundancy creates duplicate values and can cause update, insertion, and deletion anomalies.", "数据冗余会产生重复值，并可能导致更新异常、插入异常和删除异常。", ("data redundancy", "anomaly")),
        ("A database provides an organized collection of related data for storage, retrieval, and decision making.", "数据库是有组织的相关数据集合，可用于存储、检索和支持决策。", ("introducing the database", "database")),
        ("Database components include data, hardware, software, procedures, and people working together in an environment.", "数据库系统环境包括数据、硬件、软件、操作流程和人员，这些部分共同完成数据管理。", ("database components", "system environment")),
        ("A DBMS manages the interaction between end users and the database and provides core data-management functions.", "数据库管理系统（DBMS）管理最终用户与数据库之间的交互，并提供核心数据管理功能。", ("database management system", "dbms", "dbms functions")),
        ("Database systems reduce many file-system problems but still require design, administration, and responsible use.", "数据库系统可以减少许多文件系统问题，但仍需要良好设计、管理和规范使用。", ("advantages of the dbms", "disadvantages of database systems", "database design")),
    ],
}

COURSE_PREVIEW_TOPICS = {
    "mis-301": [
        ("Start with why information security matters and what it must protect.", "先理解信息安全为什么重要，以及它需要保护什么。", ("information security", "defining information security")),
        ("Learn to classify attackers by motivation, skill, target, and method.", "学习根据动机、技能、目标和方法区分不同攻击者。", ("attackers", "motivation", "target")),
        ("Preview how security awareness helps prevent attacks that involve human behavior.", "预习安全意识如何帮助人们防范涉及人为行为的攻击。", ("security awareness", "social engineering")),
    ],
    "mis-328": [
        ("Start with how business intelligence turns data into decision support.", "先理解商业智能如何把数据转化为决策支持。", ("business intelligence", "decision support")),
        ("Preview Simon's intelligence, design, choice, and implementation stages.", "预习 Simon 决策过程中的情报、设计、选择和实施四个阶段。", ("simon", "decision-making process")),
        ("Distinguish operational transaction processing from analytical processing.", "区分面向日常业务的事务处理和面向分析的分析处理。", ("oltp", "olap", "transaction processing")),
    ],
    "mis-413": [
        ("Start with project scope and the analyst's role in defining the problem.", "先理解项目范围，以及系统分析师如何界定问题。", ("scope", "problem")),
        ("Preview the SDLC stages from planning and analysis to maintenance.", "预习从规划、分析到维护的系统开发生命周期（SDLC）阶段。", ("sdlc", "life cycle")),
        ("Learn why requirements, feasibility, and models matter before design.", "理解为什么在设计之前必须关注需求、可行性和系统模型。", ("requirements", "feasibility", "model")),
    ],
    "mis-423": [
        ("Start by separating raw data from meaningful information.", "先区分原始数据和具有实际意义的信息。", ("data versus information", "raw facts")),
        ("Preview why organizations move from file processing to database systems.", "预习组织为什么从文件处理转向数据库系统。", ("file system", "evolution", "database")),
        ("Learn how a DBMS manages data and supports users.", "理解数据库管理系统（DBMS）如何管理数据并支持用户使用。", ("dbms", "database management system")),
    ],
}


def _core_items(course_name: str) -> list[dict]:
    lowered = course_name.casefold()
    for code, items in COURSE_CORE.items():
        if code in lowered:
            return [_item(en, zh, [], "course-confirmed emphasis") for en, zh in items]
    return []


def _course_code(course_name: str) -> str | None:
    lowered = course_name.casefold()
    return next((code for code in COURSE_CORE if code in lowered), None)


def _matching_sources(texts: list[tuple[str, str]], keywords: tuple[str, ...]) -> list[str]:
    matches = [locator for text, locator in texts if any(keyword.casefold() in text.casefold() for keyword in keywords)]
    return sorted(set(matches))[:3]


def _topic_items(course_name: str, texts: list[tuple[str, str]], topic_map: dict[str, list[tuple[str, str, tuple[str, ...]]]]) -> list[dict]:
    code = _course_code(course_name)
    if not code or code not in topic_map:
        return []
    result = []
    for english, chinese, keywords in topic_map[code]:
        sources = _matching_sources(texts, keywords)
        result.append(_item(english, chinese, sources, "repeated across materials" if sources else "assistant-priority inference"))
    return result


def _exam_topic_items(course_name: str, texts: list[tuple[str, str]]) -> list[dict]:
    return _topic_items(course_name, texts, COURSE_EXAM_TOPICS)


def _preview_topic_items(course_name: str, texts: list[tuple[str, str]]) -> list[dict]:
    return _topic_items(course_name, texts, COURSE_PREVIEW_TOPICS)


def _prefixed_item(item: dict, english_prefix: str, chinese_prefix: str) -> dict:
    return _item(
        english_prefix + str(item.get("en", "")),
        chinese_prefix + str(item.get("zh", "")),
        list(item.get("sources", [])),
        item.get("evidence"),
    )


def _assignment_label(text: str) -> str:
    match = re.search(r"\b((?:milestone|assignment|project|homework)(?:\s+\d+)?)\b", text, re.IGNORECASE)
    return match.group(1).strip() if match else "Course assignment"


def _assignment_topic_items(assignment_lines: list[tuple[str, str]]) -> list[dict]:
    groups: dict[str, dict] = {}
    for text, locator in assignment_lines:
        label = _assignment_label(text)
        key = label.casefold()
        group = groups.setdefault(key, {"name": label, "texts": [], "sources": [], "dates": []})
        group["texts"].append(text)
        if locator not in group["sources"]:
            group["sources"].append(locator)
        for date in _dates(text):
            if date not in group["dates"]:
                group["dates"].append(date)

    result: list[dict] = []
    for group in groups.values():
        name = group["name"]
        combined = " ".join(group["texts"]).casefold()
        details_en = []
        details_zh = []
        if "powerpoint" in combined or "presentation" in combined:
            details_en.append("a presentation")
            details_zh.append("演示文稿")
        if "present in class" in combined or "presented this project" in combined:
            details_en.append("an in-class presentation")
            details_zh.append("课堂展示")
        if "d2l" in combined:
            details_en.append("posting the final work on D2L")
            details_zh.append("将最终作品发布到 D2L")
        if "textbook" in combined or "notes" in combined or "web" in combined:
            details_en.append("course materials as references")
            details_zh.append("使用课程材料作为参考")

        if details_en:
            english = f"{name} requires {', '.join(details_en)}; verify the exact topic and final submission instructions."
            chinese_details = "、".join(details_zh)
            chinese = f"{name} 需要完成{chinese_details}；请确认具体主题和最终提交要求。"
        else:
            english = f"{name} is listed in the course materials; review its deliverables and submission instructions."
            chinese = f"课程材料列出了 {name}；请查看它的交付物和提交要求。"
        result.append(_item(english, chinese, group["sources"], "course-confirmed emphasis"))

        for date in sorted(group["dates"]):
            result.append(_item(
                f"{name} lists {date} as a due date; confirm it against the latest announcement.",
                f"{name} 的材料中写明截止日期为 {date}；请以老师的最新通知为准。",
                group["sources"],
                "needs confirmation",
            ))
    return result[:8]


def _sections(course_name: str, mode: str, texts: list[tuple[str, str]], config: dict) -> list[dict]:
    all_text = " ".join(text for text, _ in texts)
    sources = [locator for _, locator in texts]
    objective_lines = [(text, locator) for text, locator in texts if any(token in text.casefold() for token in ("objective", "goal", "learn", "explain"))]
    assignment_lines = [(text, locator) for text, locator in texts if any(token in text.casefold() for token in ("assignment", "milestone", "project", "homework", "submit", "due"))]
    key_lines = [(text, locator) for text, locator in texts if any(token in text.casefold() for token in ("scope", "sdlc", "feasibility", "system", "process", "model"))]
    evidence = "course-confirmed emphasis" if objective_lines else "repeated across materials"
    core = _core_items(course_name)
    if mode == "preview":
        items = _preview_topic_items(course_name, texts)
        if not items:
            items = [_item(_display_text(text, 180), translate_text(_display_text(text, 180)), [locator], "course-confirmed emphasis") for text, locator in objective_lines[:5]]
        items.append(_item("What should I know before class? Review the key terms and the first source pages or slides.", "课前应该知道什么？先复习关键词，并阅读最前面的相关页面或幻灯片。", sources[:5], "assistant-priority inference"))
        items.append(_item("What should I ask in class? Ask about any term or diagram that remains unclear.", "课堂上应该问什么？对于仍然不清楚的术语或图表，及时向老师提问。", [], "assistant-priority inference"))
        return ([{"heading": "Course Core", "heading_zh": "课程核心", "items": core}] if core else []) + [{"heading": "Pre-Class Preview", "heading_zh": "课前预习", "items": items}]
    if mode == "understand":
        items = _exam_topic_items(course_name, texts)[:8]
        if not items:
            items = [_item(_display_text(text, 180), translate_text(_display_text(text, 180)), [locator], evidence) for text, locator in key_lines[:8]]
        items.append(_item("The material should be understood through its concepts, relationships, and examples.", "理解材料时，应同时关注概念、概念之间的关系以及例子。", sources[:5], "assistant-priority inference"))
        return ([{"heading": "Course Core", "heading_zh": "课程核心", "items": core}] if core else []) + [{"heading": "Lecture Understanding", "heading_zh": "课堂理解", "items": items}]
    if mode == "review":
        review_cards = _exam_topic_items(course_name, texts)[:8]
        if review_cards:
            items = [_prefixed_item(item, "Review point: ", "复习要点：") for item in review_cards]
        else:
            items = [_item(f"Key point: {_display_text(text, 180)}", "核心要点：" + translate_text(_display_text(text, 180)), [locator], evidence) for text, locator in key_lines[:8]]
        items.append(_item("Self-test: Can you define the main terms and explain their relationships without looking at the notes?", "自测：不看笔记时，你能否定义主要术语并解释它们之间的关系？", sources[:5], "assistant-priority inference"))
        items.append(_item("Review next: revisit the items marked unclear and compare them with the source material.", "下一步复习：重新查看标记为不清楚的内容，并与原始课程材料进行对照。", [], "assistant-priority inference"))
        return ([{"heading": "Course Core", "heading_zh": "课程核心", "items": core}] if core else []) + [{"heading": "Post-Class Review", "heading_zh": "课后复习", "items": items}]
    if mode == "assignment":
        items = _assignment_topic_items(assignment_lines)
        if not items:
            items = [_item(f"Assignment evidence: {_display_text(text, 180)}", "作业材料：" + translate_text(_display_text(text, 180)), [locator], "course-confirmed emphasis") for text, locator in assignment_lines[:8]]
        items.append(_item("Submission checklist: confirm deliverables, required format, deadline, and rubric coverage before submitting.", "提交清单：提交前确认交付物、格式要求、截止日期以及评分标准覆盖情况。", sources[:5], "assistant-priority inference"))
        return ([{"heading": "Course Core", "heading_zh": "课程核心", "items": core}] if core else []) + [{"heading": "Assignment Requirement Guide", "heading_zh": "作业要求指南", "items": items}]
    topic_items = _exam_topic_items(course_name, texts)
    items = topic_items or [_item(f"Priority topic: {_display_text(text)}", "优先掌握的考点：" + translate_text(text), [locator], evidence) for text, locator in key_lines[:8]]
    items.append(_item("Generated question angles are study prompts; actual exam questions are not known.", "生成的问题角度只是复习提示；无法知道实际考试题目。", sources[:5], "needs confirmation"))
    items.append(_item("Last-week plan: review high-value definitions, comparisons, processes, and application examples, then complete the self-test.", "最后一周计划：复习高价值定义、比较、流程和应用例子，然后完成自测。", [], "assistant-priority inference"))
    return ([{"heading": "Course Core", "heading_zh": "课程核心", "items": core}] if core else []) + [{"heading": "Final Exam Focus", "heading_zh": "Final Exam 考点", "items": items}]


def generate_learning_session(course_root: str | Path, extracted_materials: list[dict], mode: str, config: dict | None = None) -> dict:
    if mode not in SUPPORTED_MODES:
        raise ValueError(f"unsupported learning mode: {mode}")
    root = Path(course_root).resolve()
    settings = dict(DEFAULT_CONFIG)
    settings.update(config or {})
    texts, sources, warnings = _collect(extracted_materials)
    sections = _sections(root.name, mode, texts, settings)
    code = _course_code(root.name)
    summary = COURSE_SUMMARIES.get(code, ("A source-backed learning guide generated from the indexed course materials.", "根据已索引课程材料生成的、有来源依据的学习指南。"))
    result = {
        "course": root.name,
        "mode": mode,
        "language_mode": settings.get("language_mode", "en-zh"),
        "audience": settings.get("audience", DEFAULT_CONFIG["audience"]),
        "title": {"en": f"{mode.title()} Learning Guide", "zh": "双语学习指南"},
        "output_filename": LEARNING_FILENAMES[mode],
        "summary": {"en": summary[0], "zh": summary[1]},
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
    path = metadata / learning_filename(result["mode"])
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path

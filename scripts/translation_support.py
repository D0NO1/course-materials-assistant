"""Offline Chinese learning support for common English course phrases."""

from __future__ import annotations

import re


FULL_SENTENCES = {
    "scope defines what the project will and will not include.": "项目范围（Scope）定义项目将包含什么，以及不会包含什么。",
    "the sdlc consists of planning, analysis, design, build and test, and maintenance.": "系统开发生命周期（SDLC）包括规划、分析、设计、构建与测试，以及维护。",
    "technical feasibility asks whether we have the technology and skills.": "技术可行性分析我们是否拥有实现系统所需的技术和技能。",
    "economic feasibility asks whether the benefits justify the costs.": "经济可行性分析系统带来的收益是否值得投入这些成本。",
    "operational feasibility asks whether people will use the system and whether it fits their work.": "运营可行性分析用户是否愿意使用系统，以及系统是否适合他们的工作流程。",
}

PHRASES = (
    ("information security", "信息安全（Information Security）"),
    ("cybersecurity", "网络安全（Cybersecurity）"),
    ("security awareness", "安全意识（Security Awareness）"),
    ("data theft", "数据盗窃"),
    ("identity theft", "身份盗窃"),
    ("threat actors", "威胁行为者"),
    ("state-sponsored attackers", "国家支持的攻击者"),
    ("business intelligence", "商业智能（Business Intelligence）"),
    ("decision support", "决策支持"),
    ("decision-making process", "决策过程"),
    ("predictive analytics", "预测分析"),
    ("big data", "大数据（Big Data）"),
    ("data science", "数据科学"),
    ("artificial intelligence", "人工智能（Artificial Intelligence）"),
    ("online transaction processing", "在线事务处理（OLTP）"),
    ("online analytical processing", "在线分析处理（OLAP）"),
    ("systems development life cycle", "系统开发生命周期（SDLC）"),
    ("functional requirements", "功能需求"),
    ("non-functional requirements", "非功能需求"),
    ("technical feasibility", "技术可行性"),
    ("economic feasibility", "经济可行性"),
    ("operational feasibility", "运营可行性"),
    ("scope creep", "范围蔓延"),
    ("project scope", "项目范围"),
    ("data-flow diagram", "数据流图（DFD）"),
    ("entity-relationship diagram", "实体关系图（ERD）"),
    ("use case", "用例"),
    ("database management system", "数据库管理系统（DBMS）"),
    ("relational database", "关系数据库"),
    ("file system", "文件系统"),
    ("normalization", "规范化"),
    ("course objective", "课程目标"),
    ("learning objective", "学习目标"),
    ("assignment", "作业"),
    ("milestone", "里程碑任务"),
    ("submit", "提交"),
    ("due date", "截止日期"),
    ("final exam", "Final Exam（期末考试）"),
)


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\u000b", " ")).strip()


def translate_text(text: str) -> str:
    """Return a useful Chinese explanation without sending source text online."""
    source = _clean(str(text))
    if not source:
        return "暂无可提取的文字内容。"
    exact = FULL_SENTENCES.get(source.casefold())
    if exact:
        return exact
    lowered = source.casefold()
    if len(source) > 180:
        concepts = []
        for english, chinese in PHRASES:
            if english in lowered and chinese not in concepts:
                concepts.append(chinese)
        if "objective" in lowered or "goal" in lowered:
            lead = "本段概括课程或章节的学习目标，重点是"
        elif "assignment" in lowered or "submit" in lowered or "due" in lowered or "milestone" in lowered:
            lead = "本段概括作业、里程碑或提交要求，重点是"
        elif "assessment" in lowered or "exam" in lowered or "quiz" in lowered:
            lead = "本段概括课程考核安排，重点是"
        else:
            lead = "本段概括课程材料的主要内容，重点是"
        return lead + "、".join(concepts[:6]) + "。"
    translated = source
    changed = False
    for english, chinese in PHRASES:
        updated = re.sub(re.escape(english), chinese, translated, flags=re.IGNORECASE)
        changed = changed or updated != translated
        translated = updated
    if "objective" in lowered or "goal" in lowered:
        lead = "本段说明学习目标："
    elif "difference" in lowered or "versus" in lowered or "compare" in lowered:
        lead = "本段比较相关概念："
    elif "assignment" in lowered or "submit" in lowered or "due" in lowered or "milestone" in lowered:
        lead = "本段说明作业或提交要求："
    elif "phase" in lowered or "process" in lowered or "consists" in lowered:
        lead = "本段介绍一个过程或阶段："
    elif changed:
        lead = "中文辅助解释："
    else:
        keywords = "；".join(source.split()[:12])
        return f"本段介绍课程中的相关内容。原文关键词：{keywords}。"
    return lead + translated

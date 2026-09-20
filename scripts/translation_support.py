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

TOPIC_SUMMARIES = (
    (
        ("today's attacks", "point-of-sale", "payment card"),
        "本页介绍当代攻击案例：攻击者可能从销售点系统窃取支付卡信息，也可能利用医疗信息实施身份盗窃和账单欺诈。",
    ),
    (
        ("today's attacks", "wireless", "vehicles"),
        "本页说明家庭无线设备、汽车和飞机娱乐系统都可能成为攻击入口；系统一旦存在漏洞，攻击者可能远程控制设备或继续进入其他系统。",
    ),
    (
        ("car hacking",),
        "汽车已经包含复杂的电子系统，因此汽车黑客攻击的核心是利用电子系统漏洞进入车辆或操纵车辆功能。",
    ),
    (
        ("defining information security",),
        "信息安全要保护存储、处理和传输信息的设备，并通过产品、人员和组织政策等多个层面降低风险。",
    ),
    (
        ("brokers", "vulnerability"),
        "漏洞经纪人会把漏洞知识出售给其他攻击者或政府；这类攻击者通常希望隐蔽地进入系统并窃取信息。",
    ),
    (
        ("update defenses",),
        "防御措施必须持续更新，因为新型攻击会使原有保护失效；安全工作不是一次性完成的。",
    ),
    (
        ("data versus information",),
        "数据是尚未解释的原始事实；信息是经过处理、能够为用户提供有意义结果的数据。考试时要能说明二者的区别以及数据管理的作用。",
    ),
    (
        ("raw facts", "processed data"),
        "原始事实本身还没有呈现意义；经过处理并放入使用场景后，数据才成为对用户有意义的信息。",
    ),
    (
        ("evolution of file system data processing",),
        "本页说明数据管理从传统文件系统逐步发展到数据库系统的过程，重点是文件系统在共享、维护和一致性方面的限制。",
    ),
    (
        ("problems with file system data processing",),
        "文件系统容易产生数据重复、数据不一致和程序与数据结构相互依赖等问题，这些问题推动了数据库系统的发展。",
    ),
    (
        ("structural and data dependence",),
        "结构依赖和数据依赖意味着程序必须适应文件结构的变化，修改成本高；数据库设计追求更强的数据独立性。",
    ),
    (
        ("decision-making process", "simon"),
        "Simon 决策过程包括情报、设计、选择和实施四个阶段：先发现问题，再设计备选方案，选择方案，最后执行并反馈。",
    ),
    (
        ("transaction processing versus analytic processing",),
        "事务处理（OLTP）关注快速记录日常业务；分析处理（OLAP）关注跨时间、跨维度分析数据，为管理决策提供支持。",
    ),
    (
        ("critical b i system considerations",),
        "商业智能系统需要同时考虑战略匹配、成本收益、安全、隐私、数据质量以及系统建设方式等因素。",
    ),
    (
        ("opening vignette", "predictive model"),
        "案例引导学生思考如何使用历史数据建立预测模型，例如用球票续订因素预测客户是否会继续购买。",
    ),
)

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
    normalized = (
        text.replace("\u000b", " ")
        .replace("\u00a0", " ")
        .replace("\u2019", "'")
        .replace("\u2018", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u2013", "-")
        .replace("\u2014", "-")
    )
    return re.sub(r"\s+", " ", normalized).strip()


def translate_text(text: str) -> str:
    """Return a useful Chinese explanation without sending source text online."""
    source = _clean(str(text))
    if not source:
        return "暂无可提取的文字内容。"
    exact = FULL_SENTENCES.get(source.casefold())
    if exact:
        return exact
    lowered = source.casefold()
    for required_terms, chinese in TOPIC_SUMMARIES:
        if all(term in lowered for term in required_terms):
            return chinese
    if len(source) > 180:
        concepts = []
        for english, chinese in PHRASES:
            if english in lowered and chinese not in concepts:
                concepts.append(chinese)
        if "objective" in lowered or "goal" in lowered:
            lead = "学习目标重点包括"
        elif "assignment" in lowered or "submit" in lowered or "due" in lowered or "milestone" in lowered:
            lead = "作业或提交要求重点包括"
        elif "assessment" in lowered or "exam" in lowered or "quiz" in lowered:
            lead = "考核信息重点包括"
        else:
            lead = "本段识别到的课程术语包括"
        if concepts:
            return lead + "、".join(concepts[:6]) + "。"
        return "未匹配到可靠的本地翻译；请结合英文原文和来源位置核对这段内容，不要把自动提示当作正式译文。"
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
        return "未匹配到可靠的本地翻译；请结合英文原文和来源位置核对这句话，不要把自动提示当作正式译文。"
    return lead + translated

---
name: course-materials-assistant
description: Use when analyzing, organizing, summarizing, or reviewing mixed academic course materials such as PDF, Word, Excel, PowerPoint, Access files, notes, readings, and assignments.
metadata:
  short-description: Scan and understand mixed course materials
---

# Course Materials Assistant

This skill is designed for students in Chinese-foreign cooperative programs, international students, and mixed-language classes who need help understanding English-medium professional courses.

## Student learning modes

Use `learn <course> --mode <mode>` for:

- `preview`: pre-class goals, prerequisites, questions, and reading priority.
- `understand`: plain-English explanation, Chinese support, relationships, and examples.
- `review`: bilingual key points, self-test, and next review actions.
- `assignment`: deliverables, requirements, dates, conflicts, and submission checklist.
- `exam`: cumulative Final Exam focus, ranked topics, comparisons, processes, and study plan.

Language output can be configured as `en-zh`, `zh-en`, `english-only`, `chinese-support`, or `plain-english`. The default is `en-zh`: English first and Chinese immediately below. Audience values are `cooperative-program-student`, `international-student`, and `mixed-class`.

Example:

```powershell
python scripts/cli.py learn "D:\Courses\MIS-413" --mode preview
python scripts/cli.py learn "D:\Courses\MIS-413" --mode exam --config config.json
```

Use this skill when the user asks to understand, summarize, organize, compare, or check academic materials in a user-selected course directory. Do not require a particular drive, directory, or operating system.

## Default workflow

1. Resolve the course folder from the path the user provides. If the user explicitly refers to a parent course directory, resolve the course code or name under that directory; otherwise do not guess a local course root.
2. Recursively scan that course folder before answering. Use `scripts/index_course.py` to create or update `.course-assistant/index.json` and `.course-assistant/index.md`.
3. Treat the index as an inventory, not proof that a file's full contents were understood. Read only the relevant files for the requested task.
4. Report source evidence using file paths and, where available, PDF pages, Word headings, Excel sheet names, or Access object names.
5. Preserve source files. Write generated notes and reports to `.course-assistant` or a user-specified output folder; do not overwrite assignments, datasets, or databases.
6. After producing an analysis, automatically generate a new Word report in `<course-folder>\\.course-assistant\\reports\\`. Use a timestamp and analysis topic in the filename so previous reports are preserved.
7. After producing a substantive analysis, merge confirmed findings into the course knowledge base with `scripts/update_course_knowledge.py`.
8. Make summaries bilingual by default: present the English sentence or point first, followed immediately by the Chinese explanation. Do not generate a monolingual course summary unless the user explicitly requests English-only or Chinese-only output.

## Supported material routing

- PDF: extract headings, page-level topics, definitions, models, diagrams, and likely exam concepts. Flag scanned or unreadable pages.
- Word: extract assignment instructions, rubric language, dates, word limits, formatting, citations, and draft structure.
- Excel: inspect workbook sheets, headers, formulas, data types, missing or duplicate values, hidden content, and charts. Do not change source workbooks unless explicitly asked; prefer a new output copy.
- PowerPoint: inspect slide numbers, titles, body text, speaker notes, tables, and embedded diagrams. Summarize slide-by-slide or by topic, preserve slide-number evidence, and visually review diagrams such as DFD, ERD, UML, process flows, and screenshots when their structure matters.
- Access: inspect tables, fields, types, primary keys, indexes, relationships, queries, forms, reports, macros, and modules when the local runtime supports them. Distinguish structure-only inspection from data access and query execution.
- Other files: inventory them and describe what could or could not be read. Do not pretend an unsupported format was analyzed.

## Output modes

Choose the mode implied by the request, or use the balanced mode by default:

- `速读`: one-sentence thesis, 5-10 key points, and next reading priority.
- `理解`: Chinese explanation of the argument, concept relationships, examples, and difficult English wording while retaining important English terms.
- `考试`: definitions, comparisons, processes, models, likely question angles, common confusions, and flashcards.
- `作业`: assignment goal, deliverables, rubric coverage, missing requirements, risks, and a submission checklist.
- `文件分析`: format-specific structure, data or document findings, limitations, and verified versus unverified operations.
- `复习`: glossary, bilingual notes, quiz questions, answers, and weak-topic review.

## Course indexing

Run the indexer for a selected course:

```powershell
& '<bundled-python>' 'scripts/index_course.py' '<course-folder>'
```

The path is configurable and must point to an existing Windows, macOS, or Linux course directory.

The indexer records relative path, extension, category, size, modification time, SHA-256, and status. Status values include `indexed`, `unchanged`, and `missing`. PowerPoint files use the `powerpoint` category. It skips its own `.course-assistant` directory and does not copy full source contents into the index.

Keep course-level derived files in:

```text
<course-folder>\.course-assistant\
  index.json
  index.md
  glossary.md
  assignment-tracker.md
  topics.json
  assignments.json
  milestones.json
  exam-focus.md
  exam_focus.json
  reports\\

Learning-session files use bilingual names: `01-课前预习-Pre-Class-Preview`, `02-课堂理解-Lecture-Understanding`, `03-课后复习-Post-Class-Review`, `04-作业任务-Assignment-Guide`, and `05-Final-Exam考点复习-Final-Exam-Review`.
```

Create `glossary.md` or `assignment-tracker.md` only when the user requests terminology or assignment tracking, not on every scan.

## Deep extraction and CLI

When the task requires actual file content rather than inventory, use the normalized extractor:

```powershell
& '<bundled-python>' 'scripts/cli.py' extract '<file>' --output '<output.json>'
& '<bundled-python>' 'scripts/cli.py' analyze '<course-folder>'
```

Extraction results use `extracted`, `inventory-only`, `unsupported`, or `error` status. Preserve page, heading, slide, sheet, table, or object locators. Missing parser dependencies and scanned or unreadable pages must remain visible in warnings.

Generate cumulative review and assignment outputs with:

```powershell
& '<bundled-python>' 'scripts/cli.py' exam-review '<course-folder>'
& '<bundled-python>' 'scripts/cli.py' assignments '<course-folder>'
```

Keep conflicting due dates in the output and label them for verification. Do not invent requirements or claim that generated questions are actual exam questions.

## Course knowledge base

Maintain knowledge only from analyzed and source-supported material. The update payload uses these collections:

```json
{
  "glossary": [{"term": "SDLC", "meaning": "...", "meaning_zh": "..."}],
  "topics": [{"topic": "Scope", "importance": "high", "sources": ["Week 2, p. 10"]}],
  "assignments": [{"name": "Milestone 2", "requirements": ["..."]}],
  "milestones": [{"name": "Milestone 2", "status": "discovered"}],
  "exam_focus": [{"topic": "Feasibility", "why": "...", "why_zh": "...", "must_know": "...", "must_know_zh": "...", "sources": ["..."]}]
}
```

Merge new confirmed entries with:

```powershell
& '<bundled-python>' 'scripts/update_course_knowledge.py' '<course-folder>' '<payload.json>'
```

Deduplicate glossary entries by `term`, topics and exam points by `topic`, and assignments and milestones by `name`. Replace an existing entry only when the newer source-supported analysis is more complete or correct.

## Final Exam focus

Treat final-exam preparation as a cumulative mode. When the user asks for final-exam preparation or a full review:

1. Scan and update the course index.
2. Read the syllabus, all analyzed knowledge files, and all relevant course materials.
3. Separate confirmed instructor/course-material emphasis from the assistant's inferred priority.
4. Produce a ranked exam-focus list covering definitions, comparisons, processes, models, calculations, case applications, common confusions, and likely question forms.
5. Include source locators for every major topic.
6. Generate a Word report titled `Final Exam Focus` in `.course-assistant\\reports\\`.

The final-exam report should contain:

- course-wide topic map
- high-priority, medium-priority, and review-if-time topics
- bilingual key terms and sentence patterns
- comparison tables such as Waterfall vs Agile or technical vs economic vs operational feasibility
- process/model checklists such as SDLC, DFD, ERD, and use cases
- likely question angles, without claiming to know the actual exam questions
- a source-backed last-week study plan
- a self-test section with answers based only on analyzed materials

Never label a topic as guaranteed to appear on the final. Use labels such as `course-confirmed emphasis`, `repeated across materials`, or `assistant-priority inference`.

## Word result reports

Every completed analysis should produce a readable `.docx` result report unless the user explicitly asks for chat-only output. Build a structured report with `scripts/generate_report_docx.py`, including:

- title, course name, and generation date
- core conclusion or summary
- sections for key points, bilingual sentences, exam focus, assignment requirements, or file findings as applicable
- source files and page, slide, sheet, heading, or database-object locators when available

Use the bundled Python runtime and a JSON object with `title`, `course`, `generated`, `summary`, `sections`, and `sources`. Optional metadata fields include `analysis_status`, `render_status`, and `source_count`. Save reports under `.course-assistant\\reports\\`; never overwrite source documents or an earlier report. Render and inspect the generated DOCX when LibreOffice and a PDF rasterizer are available. If rendering is unavailable, report that DOCX generation succeeded but page-level rendering was not verified.

## Evidence and safety boundaries

- Never infer a teacher's required answer from a generic textbook explanation.
- Do not silently choose between conflicting dates, rubrics, or versions; show the conflict and identify the source.
- Mark extraction failures, missing dependencies, and unsupported operations explicitly.
- Do not execute Access macros or mutate databases as part of ordinary analysis.
- For assignments, support understanding, planning, checking, and revision. Do not invent data, sources, experiments, or personal experience.

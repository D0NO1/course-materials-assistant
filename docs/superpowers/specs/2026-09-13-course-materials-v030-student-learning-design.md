# Course Materials Assistant v0.3.0 Student Learning Design

## Product Positioning

Course Materials Assistant helps students in Chinese-foreign cooperative university programs and international students understand English-medium professional courses. It turns mixed course materials into source-backed bilingual learning support for preparation, class comprehension, review, assignments, and Final Exam study.

双语课程学习助手帮助中外合作项目学生与国际学生理解英语授课的专业课程，将混合课程材料转化为有来源依据的双语学习支持，覆盖课前预习、课堂理解、课后复习、作业理解和 Final Exam 备考。

## Goals

- Preserve the existing recursive index and mixed-format extraction behavior.
- Make the default output useful for a student who understands concepts better with immediate bilingual support.
- Support both English-first/Chinese-following and Chinese-first/English-following output without duplicating analysis logic.
- Convert course goals, weekly objectives, concepts, assignments, and exam focus into actionable study steps.
- Keep every substantive claim traceable to a file and locator when available.
- Clearly distinguish course-confirmed emphasis, repeated material evidence, and assistant-priority inference.

## Non-Goals

- Predicting actual exam questions or claiming guaranteed exam coverage.
- Replacing the instructor, syllabus, grading rubric, or official assignment instructions.
- Executing Access macros, changing source databases, or editing original course files.
- Uploading private course materials or generated reports to the public GitHub repository.
- Building a full standalone GUI in this release.

## Learning Modes

The CLI and skill support these user-facing modes:

1. `preview`: course purpose, lecture thesis, prerequisite vocabulary, pre-class questions, and reading priority.
2. `understand`: plain-English explanation, Chinese support, concept relationships, examples, and difficult wording.
3. `review`: bilingual key points, glossary, retrieval questions, answers, and unresolved topics.
4. `assignment`: task objective, deliverables, rubric language, dates, risks, and submission checklist.
5. `exam`: cumulative Final Exam topic map, ranked priorities, comparisons, processes, question angles, and last-week plan.

The existing `analyze`, `exam-review`, and `assignments` commands remain compatible. A new learning-session command may select one mode while reusing the same extraction and evidence model.

## Language and Audience Configuration

Configuration is optional and defaults to the current behavior:

```json
{
  "language_mode": "en-zh",
  "audience": "cooperative-program-student",
  "generate_docx": true,
  "render_docx": true,
  "exam_mode": "cumulative"
}
```

Supported `language_mode` values:

- `en-zh`: English point first, Chinese immediately below.
- `zh-en`: Chinese explanation first, English immediately below.
- `english-only`: English output only.
- `chinese-support`: Chinese explanation with important English terms retained.
- `plain-english`: simpler English with Chinese support available in the selected report mode.

Supported `audience` values:

- `cooperative-program-student`
- `international-student`
- `mixed-class`

Audience affects explanation emphasis, not source evidence or factual claims. International-student mode supports English explanations of Chinese notices or assignment instructions when such source text is present.

## Report Structure

Generated reports remain under `<course>\\.course-assistant\\reports\\` and preserve prior reports. Student-facing reports add:

- Course purpose and learning outcomes.
- Weekly or lecture objective map.
- What this material is about.
- What to know before class.
- Key terms with bilingual definitions and source locators.
- What is still unclear and what to ask the instructor.
- What to review next.
- Assignment requirements and a submission checklist when assignments are present.
- Cumulative Final Exam focus with evidence labels and a study plan.

The report generator keeps a structured bilingual section model so that changing language direction changes rendering order rather than duplicating content.

## Data Flow and Components

1. `index_course.py` inventories changed and missing files while excluding `.course-assistant`.
2. Format extractors produce normalized records with status, text, and locators.
3. A learning-session layer classifies extracted evidence into goals, objectives, concepts, assignments, questions, and exam-focus candidates.
4. The knowledge updater merges only source-supported entries into cumulative course files.
5. Mode-specific generators build Markdown/JSON and optional DOCX reports.
6. Rendering is attempted through LibreOffice when configured; failures remain visible as metadata and do not erase the generated DOCX.

## Evidence Rules

Every major topic or requirement includes one of:

- `course-confirmed emphasis`: explicitly stated in syllabus, lecture, rubric, or instructor material.
- `repeated across materials`: appears repeatedly across analyzed source files.
- `assistant-priority inference`: ranked as useful based on structure or recurrence, but not confirmed by the instructor.
- `needs confirmation`: ambiguous, conflicting, or insufficiently extracted.

Conflicting dates, requirements, and versions are preserved with their source locators. Unsupported, unreadable, and inventory-only files remain visible in warnings.

## CLI Contract

Existing commands stay stable. Add:

```text
python scripts/cli.py learn <course_root> --mode preview
python scripts/cli.py learn <course_root> --mode understand
python scripts/cli.py learn <course_root> --mode review
python scripts/cli.py learn <course_root> --mode assignment
python scripts/cli.py learn <course_root> --mode exam
```

The command scans first, extracts supported materials, selects the requested mode, writes a structured result under `.course-assistant`, updates cumulative knowledge where appropriate, and generates a timestamped bilingual DOCX by default. `--config` can override language mode, audience, and rendering preferences.

## Testing and Acceptance Criteria

- Existing v0.2 tests continue to pass unchanged unless a test explicitly covers an intentional compatibility update.
- Mode routing is tested for all five learning modes.
- Language rendering is tested for `en-zh`, `zh-en`, and at least one single-language mode.
- Reports contain course goals, actionable next steps, and source locators when source records provide them.
- Exam output preserves cumulative behavior and does not use guaranteed-exam language.
- Assignment output preserves conflicting due dates and marks them for confirmation.
- Missing, unsupported, and inventory-only extraction statuses remain visible.
- Generated outputs stay under `.course-assistant`; source files remain byte-for-byte untouched.
- Public package scans contain no course materials, generated private reports, credentials, or personal email addresses.

## Versioning

This change is released as `v0.3.0 Bilingual Student Learning Edition`. Existing v0.2 commands and output files remain supported.

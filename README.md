# Course Materials Assistant

Course Materials Assistant is a Codex skill with reusable Python scripts for organizing mixed academic course materials and turning English course content into bilingual English-Chinese study notes.

## Features

- Recursive, incremental course-folder indexing with SHA-256 file tracking.
- Routing for PDF, Word, Excel, PowerPoint, and Access files.
- Bilingual English-first, Chinese-following summaries by default.
- Course glossary, topic, assignment, milestone, and cumulative Final Exam knowledge files.
- Timestamped Word reports that preserve source references.
- Optional LibreOffice-based DOCX rendering verification.
- Normalized PDF, DOCX, PPTX, and XLSX extraction with source locators.
- Cumulative Final Exam review files and assignment deadline tracking.
- A lightweight CLI under `scripts/cli.py`.
- Source-preserving behavior: generated files stay in `.course-assistant`.

## Requirements

- Python 3.11 or newer.
- `python-docx` for Word report generation.
- LibreOffice is optional and is only needed for page-level DOCX rendering checks.
- Access support depends on the local runtime. The indexer can inventory `.accdb` and `.mdb` files without opening or modifying them.

## Installation

```powershell
python -m pip install -r requirements.txt
```

The skill folder can be installed into a Codex skills directory according to the Codex skill installation workflow. The Python scripts can also be run directly from this repository.

## Quick Start

Index any existing course directory:

```powershell
python scripts/index_course.py "D:\Courses\MIS-413-91 - Systems Analysis"
```

The same command works with any Windows, macOS, or Linux course path. The indexer writes `index.json` and `index.md` below the course's `.course-assistant` directory.

Generate a Word report from a JSON payload:

```powershell
python scripts/generate_report_docx.py "D:\Courses\MIS-413" report.json
```

Merge analyzed findings into the course knowledge base:

```powershell
python scripts/update_course_knowledge.py "D:\Courses\MIS-413" knowledge-payload.json
```

Extract one file or an entire course directory:

```powershell
python scripts/cli.py extract "D:\Courses\MIS-413\lecture.pptx" --output lecture.json
python scripts/cli.py analyze "D:\Courses\MIS-413"
```

Generate cumulative Final Exam and assignment tracking outputs:

```powershell
python scripts/cli.py exam-review "D:\Courses\MIS-413"
python scripts/cli.py assignments "D:\Courses\MIS-413"
```

## Supported Formats

The indexer classifies `.pdf`, `.doc`, `.docx`, `.xls`, `.xlsx`, `.xlsm`, `.ppt`, `.pptx`, `.accdb`, and `.mdb`. The CLI and extractors read supported PDF, DOCX, PPTX, and XLSX files when their dependencies are installed, while the Codex skill remains responsible for source-backed interpretation and bilingual reasoning.

When content is analyzed, source locators should be preserved where available:

- PDF page numbers.
- Word headings.
- Excel sheet names and relevant cells or tables.
- PowerPoint slide numbers.
- Access table, query, form, report, or module names.

Access macros are never executed during ordinary analysis, and databases are not mutated.

## Output Structure

```text
course-folder/
└── .course-assistant/
    ├── index.json
    ├── index.md
    ├── glossary.json
    ├── glossary.md
    ├── topics.json
    ├── assignments.json
    ├── milestones.json
    ├── exam_focus.json
    ├── exam-focus.md
    ├── extracted-materials.json
    ├── final-exam-review.json
    ├── final-exam-review.md
    ├── assignment-tracker.json
    ├── assignment-tracker.md
    └── reports/
```

Generated course data is intentionally ignored by Git. Keep source files and private reports outside the public repository.

## Bilingual and Final Exam Behavior

The skill writes the English sentence or point first and the Chinese explanation immediately after it. Final Exam summaries accumulate only source-supported findings and distinguish course-confirmed emphasis from assistant-priority inference. The skill does not claim to know actual exam questions.

## Rendering Reports

DOCX generation does not require LibreOffice. When LibreOffice and a PDF rasterizer are available, render the report to PDF and page images for visual QA. If those tools are unavailable, report that the DOCX was generated but page-level rendering was not verified.

## Privacy

Do not commit real course materials, assignments, student identifiers, databases, generated reports, `.course-assistant` directories, or temporary extraction files. The included `.gitignore` provides safe defaults, but review `git status` before publishing.

Extracted JSON includes a local `path` field to support traceability. Review or remove that field before sharing extracted JSON outside your computer if the path contains a username, private directory name, or mounted-drive information.

## Testing

```powershell
python -m unittest discover -s tests -v
```

GitHub Actions runs the same test suite on Python 3.11 and 3.12.

## Limitations

- Deep PDF, PPTX, and XLSX extraction depends on the declared parser dependencies and the file contents.
- `.accdb` and `.mdb` files are inventory-only in this release; no macros or database mutations are performed.
- LibreOffice visual rendering is optional and platform-dependent.
- The first release does not provide a standalone `course-materials-assistant` command-line application.

## Contributing

Keep changes focused, add a regression test for behavior changes, preserve source-file safety, and do not include personal course materials in commits or issue attachments.

## License

MIT License. See `LICENSE`.

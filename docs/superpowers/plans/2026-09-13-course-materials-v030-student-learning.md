# Bilingual Student Learning Edition v0.3.0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task with checkpoints.

**Goal:** Add student-centered bilingual learning sessions for preview, understanding, review, assignments, and cumulative Final Exam preparation while preserving all v0.2 behavior.

**Architecture:** Add a small pure-function learning-session module that consumes normalized extraction records and produces a structured report payload. Keep extraction, indexing, knowledge merging, and DOCX rendering as existing boundaries. Extend the CLI with a `learn` command and configuration loading, then reuse the existing report generator for timestamped Word output.

**Tech Stack:** Python 3.11+, standard library JSON/argparse/pathlib, existing `python-docx` report generator, unittest.

## Global Constraints

- Existing v0.2 commands and output files remain supported.
- Default language mode is `en-zh`: English first, Chinese immediately below.
- Source files remain untouched; derived outputs stay under `.course-assistant`.
- Never claim generated questions are actual exam questions.
- Preserve source locators and extraction statuses.
- Access files remain inventory-only and macros are never executed.
- No private course materials, reports, credentials, or personal email addresses enter the public package.

### Task 1: Add Configuration and Bilingual Ordering Helpers

**Files:**
- Create: `scripts/learning_config.py`
- Modify: `examples/config.example.json`
- Test: `tests/test_learning_config.py`

**Interfaces:**
- `load_config(path: str | Path | None = None) -> dict`
- `normalize_language_mode(value: str | None) -> str`
- `order_bilingual(en: str, zh: str, mode: str) -> list[str]`

- [ ] **Step 1: Write failing tests** for default config, valid modes, invalid-mode fallback, `en-zh`, `zh-en`, `english-only`, and `chinese-support`.
- [ ] **Step 2: Run `python -m unittest tests.test_learning_config -v` and verify the new imports/functions fail.**
- [ ] **Step 3: Implement the minimal config loader with defaults for `language_mode`, `audience`, `generate_docx`, `render_docx`, and `exam_mode`; ignore unknown keys.**
- [ ] **Step 4: Run the focused test and verify it passes.**
- [ ] **Step 5: Add the v0.3 example configuration and commit with `feat: add bilingual learning configuration`.**

### Task 2: Build Student Learning Session Generator

**Files:**
- Create: `scripts/generate_learning_session.py`
- Test: `tests/test_learning_session.py`

**Interfaces:**
- `SUPPORTED_MODES: tuple[str, ...]`
- `generate_learning_session(course_root: str | Path, extracted_materials: list[dict], mode: str, config: dict | None = None) -> dict`
- `write_learning_session(course_root: str | Path, result: dict) -> Path`

- [ ] **Step 1: Write failing tests** using normalized PDF/DOCX/PPTX-like records that assert all five modes are accepted, each result has `mode`, `course`, `sections`, `sources`, and `warnings`, and each major section has bilingual fields.
- [ ] **Step 2: Add tests for evidence labels, locator preservation, unsupported status warnings, assignment dates, and exam language that avoids guaranteed-exam claims.**
- [ ] **Step 3: Run the focused tests and verify failure.**
- [ ] **Step 4: Implement deterministic extraction of titles, headings, paragraphs, slide/page locators, assignment signals, and exam-focus entries from existing normalized records.**
- [ ] **Step 5: Implement mode-specific sections: preview objectives/prerequisites/questions, understand explanation/concept links, review key points/self-test/next review, assignment deliverables/checklist/conflicts, and exam ranked priorities/study plan.**
- [ ] **Step 6: Use `order_bilingual` for output ordering while retaining canonical `en` and `zh` fields in JSON.**
- [ ] **Step 7: Write JSON and Markdown under `.course-assistant` without touching source files.**
- [ ] **Step 8: Run focused tests and verify pass.**
- [ ] **Step 9: Commit with `feat: add student learning session generator`.**

### Task 3: Add CLI Learning Workflow

**Files:**
- Modify: `scripts/cli.py`
- Test: `tests/test_cli.py`

**Interfaces:**
- New command: `learn <course_root> --mode {preview,understand,review,assignment,exam} [--config path] [--no-docx]`

- [ ] **Step 1: Add failing CLI tests** for mode routing, missing course errors, config loading, JSON output path, and `--no-docx` behavior.
- [ ] **Step 2: Run the focused CLI tests and verify failure.**
- [ ] **Step 3: Add parser arguments and call `build_index`, `_extract_course`, `generate_learning_session`, and `write_learning_session` in that order.**
- [ ] **Step 4: When DOCX is enabled, pass a report payload to `generate_report` with the learning sections and source count; expose generated path in the command JSON.**
- [ ] **Step 5: Keep existing command branches unchanged and run focused tests.**
- [ ] **Step 6: Commit with `feat: expose learning sessions through cli`.**

### Task 4: Upgrade Skill and Public Documentation

**Files:**
- Modify: `SKILL.md`
- Modify: `README.md`
- Modify: `agents/openai.yaml`
- Test: `tests/test_documentation_contract.py`

**Interfaces:**
- Documentation must describe the student audience, five modes, language modes, evidence labels, and `learn` examples.

- [ ] **Step 1: Write failing documentation contract tests** that search for the five mode names, `en-zh`, `zh-en`, `international-student`, and `learn`.
- [ ] **Step 2: Run the focused test and verify failure if any contract is absent.**
- [ ] **Step 3: Update the skill instructions and README with bilingual student workflow, configuration, outputs, and privacy boundaries.**
- [ ] **Step 4: Update the agent metadata to identify the student-learning use case without exposing local paths.**
- [ ] **Step 5: Run documentation tests and commit with `docs: describe bilingual student learning edition`.**

### Task 5: Full Verification, Global Sync, and Upload Package

**Files:**
- Modify only generated release artifacts outside the public source tree.

- [ ] **Step 1: Run `python -m unittest discover -s tests -v` from the repository and require all tests to pass.**
- [ ] **Step 2: Run the skill validator if its dependencies are available; record a clear limitation if unavailable.**
- [ ] **Step 3: Run CLI smoke tests on a temporary course fixture for all five modes and verify JSON/DOCX paths remain under `.course-assistant`.**
- [ ] **Step 4: Run security scans for API keys, tokens, private keys, emails, course paths, course materials, `.course-assistant`, `work`, and bytecode in the public tree.**
- [ ] **Step 5: Sync validated skill files to `<Codex skill directory>\course-materials-assistant` and verify required files.**
- [ ] **Step 6: Rebuild `course-materials-assistant-v0.3.0-upload.zip` without `.git`, `.course-assistant`, `work`, bytecode, or course materials.**
- [ ] **Step 7: Verify ZIP listing, SHA-256, and final `git status`.**
- [ ] **Step 8: Commit release metadata with `chore: prepare v0.3.0 upload package`.**

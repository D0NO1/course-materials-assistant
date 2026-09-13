"""Route course files through a normalized, source-located extraction contract."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from index_course import SUPPORTED


def _base_result(path: Path, fmt: str) -> dict:
    return {
        "file": path.name,
        "path": str(path),
        "format": fmt,
        "status": "error",
        "content": {},
        "locators": [],
        "warnings": [],
    }


def _dispatch(path: Path, fmt: str) -> dict:
    if fmt == "pdf":
        from extract_pdf import extract_pdf

        return extract_pdf(path)
    if fmt == "word":
        from extract_docx import extract_docx

        return extract_docx(path)
    if fmt == "powerpoint":
        from extract_pptx import extract_pptx

        return extract_pptx(path)
    if fmt == "excel":
        from extract_xlsx import extract_xlsx

        return extract_xlsx(path)
    if fmt == "access":
        from inspect_access import inspect_access

        return inspect_access(path)
    result = _base_result(path, fmt)
    result["status"] = "unsupported"
    result["warnings"].append("No extractor is registered for this file type.")
    return result


def extract_material(path: str | Path) -> dict:
    source = Path(path)
    fmt = SUPPORTED.get(source.suffix.lower(), "other")
    if not source.exists() or not source.is_file():
        result = _base_result(source, fmt)
        result["warnings"].append("The source file does not exist or is not a file.")
        return result
    try:
        result = _dispatch(source, fmt)
    except Exception as exc:  # Keep batch extraction alive and expose the failure.
        result = _base_result(source, fmt)
        result["warnings"].append(f"Extraction failed: {exc}")
    result.setdefault("file", source.name)
    result.setdefault("path", str(source))
    result.setdefault("format", fmt)
    result.setdefault("content", {})
    result.setdefault("locators", [])
    result.setdefault("warnings", [])
    return result


def extract_many(paths: Iterable[str | Path]) -> list[dict]:
    return [extract_material(path) for path in paths]


def write_json(result: object, output: str | Path) -> Path:
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return destination


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    target = args.path
    paths = sorted(target.rglob("*")) if target.is_dir() else [target]
    results = extract_many(path for path in paths if path.is_file())
    payload = results if target.is_dir() else results[0]
    if args.output:
        write_json(payload, args.output)
        print(args.output)
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))

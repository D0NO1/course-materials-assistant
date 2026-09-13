"""Extract PDF text with page locators when pypdf is available."""

from __future__ import annotations

from pathlib import Path


def extract_pdf(path: str | Path) -> dict:
    source = Path(path)
    result = {
        "file": source.name,
        "path": str(source),
        "format": "pdf",
        "status": "extracted",
        "content": {"pages": []},
        "locators": [],
        "warnings": [],
    }
    try:
        from pypdf import PdfReader
    except ImportError:
        result["status"] = "inventory-only"
        result["warnings"].append("Install pypdf for PDF text extraction.")
        return result
    try:
        reader = PdfReader(str(source))
        for number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            result["content"]["pages"].append({"page": number, "text": text})
            result["locators"].append({"type": "page", "number": number})
            if not text.strip():
                result["warnings"].append(f"Page {number} has no extractable text.")
    except Exception as exc:
        result["status"] = "error"
        result["warnings"].append(f"PDF extraction failed: {exc}")
    return result

"""Build a read-only, incremental index for one course directory."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


SUPPORTED = {
    ".pdf": "pdf",
    ".doc": "word",
    ".docx": "word",
    ".xls": "excel",
    ".xlsx": "excel",
    ".xlsm": "excel",
    ".accdb": "access",
    ".mdb": "access",
    ".ppt": "powerpoint",
    ".pptx": "powerpoint",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _category(path: Path) -> str:
    return SUPPORTED.get(path.suffix.lower(), "other")


def _load_previous(index_path: Path) -> dict:
    if not index_path.exists():
        return {"files": []}
    try:
        return json.loads(index_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"files": []}


def build_index(course_root: str | Path) -> dict:
    root = Path(course_root).resolve()
    if not root.exists() or not root.is_dir():
        raise ValueError(f"course directory does not exist: {root}")
    metadata_dir = root / ".course-assistant"
    index_path = metadata_dir / "index.json"
    previous = _load_previous(index_path)
    previous_by_path = {entry["path"]: entry for entry in previous.get("files", [])}
    current_paths = set()
    entries = []

    for path in sorted(root.rglob("*")):
        if not path.is_file() or metadata_dir in path.parents:
            continue
        relative = path.relative_to(root).as_posix()
        current_paths.add(relative)
        file_hash = _sha256(path)
        prior = previous_by_path.get(relative)
        status = "unchanged" if prior and prior.get("sha256") == file_hash else "indexed"
        entries.append({
            "path": relative,
            "category": _category(path),
            "extension": path.suffix.lower(),
            "size": path.stat().st_size,
            "modified_utc": datetime.fromtimestamp(
                path.stat().st_mtime, tz=timezone.utc
            ).isoformat(),
            "sha256": file_hash,
            "status": status,
        })

    for relative, prior in previous_by_path.items():
        if relative not in current_paths:
            missing = dict(prior)
            missing["status"] = "missing"
            entries.append(missing)

    entries.sort(key=lambda entry: entry["path"])
    result = {
        "course_root": ".",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "files": entries,
    }
    metadata_dir.mkdir(exist_ok=True)
    index_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    _write_markdown(metadata_dir / "index.md", result)
    return result


def _write_markdown(path: Path, result: dict) -> None:
    lines = [
        "# Course Materials Index",
        "",
        f"Generated (UTC): `{result['generated_utc']}`",
        "",
        "| Path | Category | Size | Status |",
        "|---|---|---:|---|",
    ]
    for entry in result["files"]:
        lines.append(
            f"| `{entry['path']}` | {entry['category']} | {entry['size']} | {entry['status']} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("course_root", type=Path)
    args = parser.parse_args()
    summary = build_index(args.course_root)
    print(json.dumps({"files": len(summary["files"]), "index": ".course-assistant/index.json"}))

"""Provide safe inventory-only routing for Access databases."""

from __future__ import annotations

from pathlib import Path


def inspect_access(path: str | Path) -> dict:
    source = Path(path)
    return {
        "file": source.name,
        "path": str(source),
        "format": "access",
        "status": "inventory-only",
        "content": {"database_objects": []},
        "locators": [],
        "warnings": [
            "Access structure inspection is runtime-dependent; macros and database mutations are disabled."
        ],
    }

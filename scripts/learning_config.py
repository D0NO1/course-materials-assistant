"""Configuration and bilingual ordering helpers for student learning reports."""

from __future__ import annotations

import json
from pathlib import Path


LANGUAGE_MODES = ("en-zh", "zh-en", "english-only", "chinese-support", "plain-english")
DEFAULT_CONFIG = {
    "language_mode": "en-zh",
    "audience": "cooperative-program-student",
    "generate_docx": True,
    "render_docx": True,
    "exam_mode": "cumulative",
}


def normalize_language_mode(value: str | None) -> str:
    return value if value in LANGUAGE_MODES else DEFAULT_CONFIG["language_mode"]


def load_config(path: str | Path | None = None) -> dict:
    config = dict(DEFAULT_CONFIG)
    if path is not None:
        source = Path(path)
        if source.exists():
            loaded = json.loads(source.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                config.update({key: loaded[key] for key in DEFAULT_CONFIG if key in loaded})
    config["language_mode"] = normalize_language_mode(config.get("language_mode"))
    if config.get("audience") not in {"cooperative-program-student", "international-student", "mixed-class"}:
        config["audience"] = DEFAULT_CONFIG["audience"]
    return config


def order_bilingual(en: str, zh: str, mode: str) -> list[str]:
    if mode == "english-only":
        return [en]
    if mode == "chinese-support":
        return [zh, en]
    if mode == "zh-en":
        return [zh, en]
    return [en, zh]

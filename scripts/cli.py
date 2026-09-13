"""Command-line entry point for course material workflows."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from extract_material import extract_many, extract_material, write_json
from generate_assignment_tracker import generate_assignment_tracker
from generate_exam_review import generate_exam_review
from index_course import SUPPORTED, build_index


def _course_files(root: Path) -> list[Path]:
    return [
        path for path in sorted(root.rglob("*"))
        if path.is_file() and ".course-assistant" not in path.parts
        and path.suffix.lower() in SUPPORTED
    ]


def _extract_course(root: Path) -> list[dict]:
    return extract_many(_course_files(root))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="course-materials-assistant")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan = subparsers.add_parser("scan", help="Build or update a course index")
    scan.add_argument("course_root", type=Path)

    extract = subparsers.add_parser("extract", help="Extract one file or course directory")
    extract.add_argument("path", type=Path)
    extract.add_argument("--output", type=Path)

    analyze = subparsers.add_parser("analyze", help="Scan and extract all supported course files")
    analyze.add_argument("course_root", type=Path)

    exam = subparsers.add_parser("exam-review", help="Generate cumulative Final Exam review files")
    exam.add_argument("course_root", type=Path)

    assignments = subparsers.add_parser("assignments", help="Generate assignment and due-date tracking files")
    assignments.add_argument("course_root", type=Path)

    args = parser.parse_args(argv)
    try:
        if args.command == "scan":
            print(json.dumps(build_index(args.course_root), ensure_ascii=False, indent=2))
        elif args.command == "extract":
            target = args.path
            if target.is_dir():
                payload = extract_many(_course_files(target))
            else:
                payload = extract_material(target)
            if args.output:
                write_json(payload, args.output)
                print(args.output)
            else:
                print(json.dumps(payload, ensure_ascii=False, indent=2))
        elif args.command == "analyze":
            if not args.course_root.exists() or not args.course_root.is_dir():
                raise ValueError(f"course directory does not exist: {args.course_root}")
            build_index(args.course_root)
            payload = _extract_course(args.course_root)
            output = args.course_root / ".course-assistant" / "extracted-materials.json"
            write_json(payload, output)
            print(output)
        elif args.command == "exam-review":
            print(json.dumps(generate_exam_review(args.course_root), ensure_ascii=False, indent=2))
        elif args.command == "assignments":
            if not args.course_root.exists() or not args.course_root.is_dir():
                raise ValueError(f"course directory does not exist: {args.course_root}")
            print(json.dumps(
                generate_assignment_tracker(args.course_root, _extract_course(args.course_root)),
                ensure_ascii=False,
                indent=2,
            ))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

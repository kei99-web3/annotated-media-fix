#!/usr/bin/env python3
"""Validate an annotated-media-fix JSON export and optional fix brief."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


VALID_MEDIA_TYPES = {"image", "video", "slide", "storyboard", "mixed"}
VALID_ANNOTATION_TYPES = {"rect", "arrow", "pen"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate annotated-media-fix artifacts.")
    parser.add_argument("--annotations", required=True, help="Annotation JSON file.")
    parser.add_argument("--fix-brief", help="Optional fix brief markdown file.")
    return parser.parse_args()


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def validate_annotations(path: Path) -> dict:
    if not path.exists():
        fail(f"Missing annotation JSON: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != "annotated-media-fix/v1":
        fail("schema must be annotated-media-fix/v1")
    if data.get("media_type") not in VALID_MEDIA_TYPES:
        fail(f"media_type must be one of {sorted(VALID_MEDIA_TYPES)}")
    media = data.get("media")
    if not isinstance(media, dict) or not media.get("src"):
        fail("media.src is required")
    annotations = data.get("annotations")
    if not isinstance(annotations, list):
        fail("annotations must be a list")
    for index, item in enumerate(annotations, start=1):
        if item.get("type") not in VALID_ANNOTATION_TYPES:
            fail(f"annotation {index} has invalid type")
        if not item.get("id"):
            fail(f"annotation {index} is missing id")
    return data


def validate_fix_brief(path: Path, annotation_ids: set[str]) -> None:
    if not path.exists():
        fail(f"Missing fix brief: {path}")
    text = path.read_text(encoding="utf-8")
    required = ["## Baseline", "## Fixes", "## Generation Gate", "## Verification"]
    for marker in required:
        if marker not in text:
            fail(f"fix brief missing section: {marker}")
    missing = [item for item in sorted(annotation_ids) if item not in text]
    if missing:
        fail(f"fix brief does not mention annotation ids: {', '.join(missing)}")


def main() -> None:
    args = parse_args()
    data = validate_annotations(Path(args.annotations))
    annotation_ids = {str(item["id"]) for item in data["annotations"]}
    if args.fix_brief:
        validate_fix_brief(Path(args.fix_brief), annotation_ids)
    print(f"OK: {len(annotation_ids)} annotation(s) validated")


if __name__ == "__main__":
    main()

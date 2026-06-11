#!/usr/bin/env python3
"""Find the newest annotated-media-fix JSON export on the local PC."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


SCHEMA = "annotated-media-fix/v1"
DEFAULT_NAMES = {"annotations.json", "annotated-media-fix.json"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Find the latest annotated-media-fix JSON export.")
    parser.add_argument(
        "--root",
        action="append",
        default=[],
        help="Directory to search. Can be passed multiple times. Defaults to Downloads, Desktop, and cwd.",
    )
    parser.add_argument(
        "--since-minutes",
        type=int,
        default=240,
        help="Only consider files modified within this many minutes. Use 0 to disable.",
    )
    parser.add_argument("--json", action="store_true", help="Print a JSON object instead of only the path.")
    return parser.parse_args()


def default_roots() -> list[Path]:
    home = Path.home()
    candidates = [home / "Downloads", home / "Desktop", Path.cwd()]
    return [path for path in candidates if path.exists()]


def is_annotation_file(path: Path) -> bool:
    if path.suffix.lower() != ".json":
        return False
    if path.name not in DEFAULT_NAMES and "annotation" not in path.name.lower():
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return False
    return data.get("schema") == SCHEMA and isinstance(data.get("annotations"), list)


def iter_candidates(roots: list[Path], since_minutes: int) -> list[Path]:
    now = None
    cutoff = None
    if since_minutes > 0:
        import time

        now = time.time()
        cutoff = now - since_minutes * 60

    found: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*.json"):
            try:
                if cutoff is not None and path.stat().st_mtime < cutoff:
                    continue
            except OSError:
                continue
            if is_annotation_file(path):
                found.append(path)
    return sorted(found, key=lambda item: item.stat().st_mtime, reverse=True)


def main() -> None:
    args = parse_args()
    roots = [Path(item).expanduser().resolve() for item in args.root] if args.root else default_roots()
    candidates = iter_candidates(roots, args.since_minutes)
    if not candidates:
        raise SystemExit("No annotated-media-fix JSON export found.")

    latest = candidates[0]
    if args.json:
        payload = {
            "path": str(latest),
            "mtime": latest.stat().st_mtime,
            "roots": [str(path) for path in roots],
            "candidate_count": len(candidates),
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(latest)


if __name__ == "__main__":
    os.environ.setdefault("PYTHONUTF8", "1")
    main()

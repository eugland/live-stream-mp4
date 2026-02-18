#!/usr/bin/env python3
"""
Normalize filenames in candidates/ and video/ directories.

Rules:
- Lowercase
- Spaces -> underscore
- Apostrophes removed
- Remove other special characters
"""
from __future__ import annotations

import argparse
import os
import re
from pathlib import Path


# Characters to drop explicitly (common apostrophes)
APOSTROPHES = {"'", "’", "‘", "`"}


def normalize_stem(stem: str) -> str:
    s = stem.lower()
    s = s.replace(" ", "_")
    for ch in APOSTROPHES:
        s = s.replace(ch, "")
    # Remove any non a-z0-9 or underscore
    s = re.sub(r"[^a-z0-9_]", "", s)
    # Collapse multiple underscores
    s = re.sub(r"_+", "_", s).strip("_")
    return s or "untitled"


def normalize_filename(path: Path) -> str:
    stem = normalize_stem(path.stem)
    ext = path.suffix.lower()
    return f"{stem}{ext}"


def unique_name(dir_path: Path, desired: str, original: Path) -> str:
    if (dir_path / desired) == original:
        return desired
    if not (dir_path / desired).exists():
        return desired
    base, ext = os.path.splitext(desired)
    i = 2
    while True:
        candidate = f"{base}_{i}{ext}"
        if not (dir_path / candidate).exists():
            return candidate
        i += 1


def normalize_dir(dir_path: Path) -> list[tuple[Path, Path]]:
    changes: list[tuple[Path, Path]] = []
    for entry in sorted(dir_path.iterdir()):
        if not entry.is_file():
            continue
        new_name = normalize_filename(entry)
        new_name = unique_name(dir_path, new_name, entry)
        new_path = dir_path / new_name
        if new_path != entry:
            changes.append((entry, new_path))
    for src, dst in changes:
        src.rename(dst)
    return changes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--video-dir", default="video")
    parser.add_argument("--candidates-dir", default="candidates")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    video_dir = (root / args.video_dir).resolve()
    candidates_dir = (root / args.candidates_dir).resolve()

    changes: list[tuple[Path, Path]] = []
    if video_dir.is_dir():
        changes.extend(normalize_dir(video_dir))
    if candidates_dir.is_dir():
        changes.extend(normalize_dir(candidates_dir))

    for src, dst in changes:
        print(f"{src} -> {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

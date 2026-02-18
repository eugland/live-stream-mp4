#!/usr/bin/env python3
"""
Generate a simple HTML page listing playlist videos and candidate videos.
"""

from __future__ import annotations

import argparse
import html
from datetime import datetime, timezone
from pathlib import Path


def list_mp4s(directory: Path) -> list[Path]:
    if not directory.exists() or not directory.is_dir():
        return []
    return sorted([p for p in directory.iterdir() if p.is_file() and p.suffix.lower() == ".mp4"])


def format_size(num_bytes: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(num_bytes)
    for unit in units:
        if size < 1024.0 or unit == units[-1]:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"


def render_list(paths: list[Path]) -> str:
    if not paths:
        return "<p class=\"muted\">None found.</p>"
    items = []
    for p in paths:
        stat = p.stat()
        mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        name = html.escape(p.name)
        items.append(
            "<li>"
            f"<span class=\"name\">{name}</span>"
            f"<span class=\"meta\">{format_size(stat.st_size)} • {mtime}</span>"
            "</li>"
        )
    return "<ul>" + "".join(items) + "</ul>"


def build_html(playlist: list[Path], candidates: list[Path]) -> str:
    now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Livestream Playlist</title>
  <style>
    :root {{
      --bg: #0f172a;
      --card: #111827;
      --text: #e5e7eb;
      --muted: #94a3b8;
      --accent: #38bdf8;
    }}
    body {{
      margin: 0;
      font-family: "Source Serif 4", "Georgia", serif;
      background: radial-gradient(1200px circle at 20% -20%, #1e293b, #0f172a);
      color: var(--text);
      padding: 32px;
    }}
    h1 {{
      font-size: 2.2rem;
      margin: 0 0 8px;
    }}
    p {{
      margin: 0 0 24px;
      color: var(--muted);
    }}
    .grid {{
      display: grid;
      gap: 20px;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    }}
    .card {{
      background: var(--card);
      border: 1px solid #1f2937;
      border-radius: 14px;
      padding: 18px 18px 8px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
    }}
    .card h2 {{
      margin: 0 0 12px;
      font-size: 1.2rem;
      color: var(--accent);
    }}
    ul {{
      list-style: none;
      padding: 0;
      margin: 0;
    }}
    li {{
      display: grid;
      gap: 6px;
      padding: 12px 0;
      border-bottom: 1px solid #1f2937;
    }}
    li:last-child {{
      border-bottom: none;
    }}
    .name {{
      font-weight: 600;
    }}
    .meta {{
      font-size: 0.85rem;
      color: var(--muted);
    }}
    .muted {{
      color: var(--muted);
    }}
  </style>
</head>
<body>
  <h1>Livestream Playlist</h1>
  <p>Generated {now}</p>
  <div class=\"grid\">
    <section class=\"card\">
      <h2>Currently in Playlist</h2>
      {render_list(playlist)}
    </section>
    <section class=\"card\">
      <h2>Candidate Videos</h2>
      {render_list(candidates)}
    </section>
  </div>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a playlist HTML page.")
    parser.add_argument("--video-dir", default="video", help="Directory with playlist videos")
    parser.add_argument("--candidates-dir", default="candidates", help="Directory with candidate videos")
    parser.add_argument("--out", default="docs/index.html", help="Output HTML file")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    video_dir = (root / args.video_dir).resolve()
    candidates_dir = (root / args.candidates_dir).resolve()
    out_file = (root / args.out).resolve()
    out_file.parent.mkdir(parents=True, exist_ok=True)

    playlist = list_mp4s(video_dir)
    candidates = list_mp4s(candidates_dir)

    out_file.write_text(build_html(playlist, candidates), encoding="utf-8")
    print(f"Wrote {out_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

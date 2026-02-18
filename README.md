# Livestreaming

## Overview
This repo manages a looping YouTube livestream built from local `.mp4` files.

## Folders
- `video/`: The current playlist. All `.mp4` files in this folder are streamed in order, then looped.
- `candidates/`: Potential videos to promote into the playlist.
- `logs/`: Runtime logs, including `logs/stream.log`.
- `docs/`: Generated static site for GitHub Pages (playlist overview).
- `scripts/`: Helper scripts (e.g., HTML generator).

## Key Files
- `youtube_live.sh`: Streams videos in `video/` to YouTube (primary + backup RTMP).
- `stream.pid`: PID of the last started livestream process (when launched with the command below).
- `yt-dlp`: Helper binary for downloading videos.

## Run The Livestream
From the repo root:

```bash
nohup ./youtube_live.sh ./video > logs/stream.log 2>&1 & echo $! > stream.pid
```

## Generate The Playlist Page
This generates an `index.html` in `docs/` that lists the current playlist and candidate videos.

```bash
python3 scripts/generate_playlist_page.py
```

After pushing to GitHub, you can enable GitHub Pages to serve the `docs/` folder.

## Normalize Filenames
Normalize filenames in `video/` and `candidates/` to be filesystem-safe and consistent:
- Lowercase
- Spaces to `_`
- Apostrophes removed
- Other special characters removed

```bash
python3 scripts/normalize_filenames.py
```

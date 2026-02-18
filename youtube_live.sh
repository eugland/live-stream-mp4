#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./youtube_live.sh /path/to/video

VIDEO_DIR="${1:-video}"

# YouTube stream key (key-only mode).
STREAM_KEY="8f40-xm29-591m-mu11-er9x"

if [[ -z "$STREAM_KEY" ]]; then
  echo "Error: STREAM_KEY is empty."
  exit 1
fi

if [[ ! -d "$VIDEO_DIR" ]]; then
  echo "Error: directory not found: $VIDEO_DIR"
  exit 1
fi

PRIMARY_URL="rtmp://a.rtmp.youtube.com/live2/${STREAM_KEY}"
BACKUP_URL="rtmp://b.rtmp.youtube.com/live2/${STREAM_KEY}?backup=1"

RECONNECT_DELAY_SECONDS=5

shopt -s nullglob

echo "Starting livestream to primary + backup..."
echo "Primary: $PRIMARY_URL"
echo "Backup : $BACKUP_URL"

stream_with_reconnect() {
  local file="$1"
  while true; do
    echo "Streaming: $file"
    if ffmpeg -re -i "$file" \
      -map 0:v:0 -map 0:a:0? \
      -c:v libx264 -preset veryfast -pix_fmt yuv420p -g 60 -r 30 \
      -c:a aac -b:a 128k -ar 44100 \
      -f tee "[f=flv]${PRIMARY_URL}|[f=flv]${BACKUP_URL}"; then
      return 0
    fi

    echo "Stream dropped. Reconnecting in ${RECONNECT_DELAY_SECONDS}s..."
    sleep "$RECONNECT_DELAY_SECONDS"
  done
}

# Loops all videos forever.
while true; do
  if git -C "$VIDEO_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    if git -C "$VIDEO_DIR" pull --rebase --autostash; then
      echo "Git pull complete."
    else
      echo "Warning: git pull failed; continuing with local files."
    fi
  fi

  files=("$VIDEO_DIR"/*.mp4)
  if [[ ${#files[@]} -eq 0 ]]; then
    echo "No .mp4 files found in $VIDEO_DIR; waiting..."
    sleep "$RECONNECT_DELAY_SECONDS"
    continue
  fi

  for f in "${files[@]}"; do
    stream_with_reconnect "$f"
  done
done

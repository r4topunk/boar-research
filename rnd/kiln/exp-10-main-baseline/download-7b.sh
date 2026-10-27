#!/usr/bin/env bash
# exp-10 O-main-2 (coordinator-approved): download main's 12 GB catalog model, Qwen2.5-7B-Instruct Q4_K_M (4,683,074,240 B),
# with a disk watchdog: abort and delete if free space < 12 GiB; verify sha256; the file is deleted after the run (cleanup-7b.sh).
set -uo pipefail
DST=$HOME/boar/shared-models/Qwen2.5-7B-Instruct-Q4_K_M.gguf
URL=https://huggingface.co/bartowski/Qwen2.5-7B-Instruct-GGUF/resolve/main/Qwen2.5-7B-Instruct-Q4_K_M.gguf
SHA=65b8fcd92af6b4fefa935c625d1ac27ea29dcb6ee14589c55a8f115ceaaa1423
LOG=$HOME/boar/kiln/download-7b.log
free_gib() { df -k "$HOME" | tail -1 | awk '{printf "%.1f", $4/1048576}'; }
echo "$(date +%T) start, free $(free_gib) GiB" >> "$LOG"
[ "$(free_gib | cut -d. -f1)" -ge 20 ] || { echo "$(date +%T) ABORT: < 20 GiB free" >> "$LOG"; exit 1; }
nice -n 19 curl -sL --retry 3 -o "$DST.part" "$URL" &
CURL=$!
while kill -0 $CURL 2>/dev/null; do
  if [ "$(free_gib | cut -d. -f1)" -lt 12 ]; then
    kill $CURL; rm -f "$DST.part"; echo "$(date +%T) WATCHDOG: free < 12 GiB, aborted and deleted" >> "$LOG"; exit 2
  fi
  sleep 10
done
wait $CURL || { echo "$(date +%T) curl failed" >> "$LOG"; rm -f "$DST.part"; exit 3; }
GOT=$(shasum -a 256 "$DST.part" | cut -d' ' -f1)
if [ "$GOT" = "$SHA" ]; then mv "$DST.part" "$DST"; echo "$(date +%T) OK sha $GOT, free $(free_gib) GiB" >> "$LOG"; else rm -f "$DST.part"; echo "$(date +%T) SHA MISMATCH $GOT, deleted" >> "$LOG"; exit 4; fi

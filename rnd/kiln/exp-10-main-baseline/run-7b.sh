#!/usr/bin/env bash
# exp-10 O-main-2 (coordinator-approved): main's real 12 GB profile = the required Qwen2.5-1.5B + the downloaded
# Qwen2.5-7B, main 6b53ee83, 72 questions, 1 run, greedy, seed 42. Disk watchdog for the whole run (free < 12 GiB ->
# stop the run and delete the 7B). The 7B is deleted at the end in every case.
set -uo pipefail
cd <runner>/kiln/app-6b53ee83; mkdir -p kiln/runs
M7=$HOME/boar/shared-models/Qwen2.5-7B-Instruct-Q4_K_M.gguf
LOG=$HOME/boar/kiln/download-7b.log
free_gib() { df -k "$HOME" | tail -1 | awk '{printf "%d", $4/1048576}'; }
KIT=$HOME/boar/shared-data/packs/pinned/d3b87d562baba3489f6878bf99783f50d504db94c347029771e53f6d1aecc666/wiki-vital5.sqlite,$HOME/boar/shared-data/crypto/boar-crypto.sqlite,$HOME/boar/shared-data/packs/boar-wikivoyage-en.sqlite
echo "$(date +%T) run start, free $(free_gib) GiB" >> "$LOG"
kiln/node_modules/.bin/tsx kiln/runner-main-multi.ts --commit 6b53ee83 --model qwen2.5-7b-instruct-q4km \
  --installed qwen2.5-1.5b-instruct-q4km,qwen2.5-7b-instruct-q4km --questions kiln/questions.exp10.jsonl \
  --out kiln/runs/main-12gb-real.jsonl --ram-gb 12 --platform android --pack "$KIT" --temp 0 --seed 42 --label main-12gb-real \
  > kiln/runs/main-12gb-real.log 2>&1 &
RUN=$!
while kill -0 $RUN 2>/dev/null; do
  if [ "$(free_gib)" -lt 12 ]; then kill $RUN; echo "$(date +%T) WATCHDOG: free < 12 GiB during run, stopped" >> "$LOG"; break; fi
  sleep 15
done
wait $RUN; RC=$?
rm -f "$M7"; echo "$(date +%T) run rc=$RC; 7B deleted; free $(free_gib) GiB" >> "$LOG"
grep '"done"' kiln/runs/main-12gb-real.log; tail -2 "$LOG"

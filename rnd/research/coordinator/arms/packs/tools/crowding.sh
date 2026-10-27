#!/usr/bin/env bash
# T-K4a CROWDING probe (0 LLM, 0 judge, MacBook): deep-tier retrieval replay (k 6, pool 20, gate rules) of the claim kit
# (crypto + wikivoyage) alone and + each wave-1 pack as a peer (+ the 5 SE packs together), on v0.2 (110, tasks from the
# dt512 v0.2 traces; outputs with query text stay under blind/bench-v02/runs-packs/) and v0.1 public (60; arms/packs/replay/),
# tree wt/packs (T-K2 source codes). Then aggregates/crowding.json via crowding_agg.py. usage: crowding.sh [--only <label>]
set -euo pipefail
H="$(cd "$(dirname "$0")" && pwd)"; B="$(cd "$H/../../../../../.." && pwd)"; cd "$B"
export BOAR_REPLAY_CACHE="$B/rnd/research/coordinator/arms/deepcovfb/cache"
R="$H/replay-crowd.sh"; W=shared-data/packs/wave1
KIT=shared-data/crypto/boar-crypto.sqlite,shared-data/packs/boar-wikivoyage-en.sqlite
O1=rnd/research/coordinator/arms/packs/replay; O2=blind/bench-v02/runs-packs; mkdir -p "$O1" "$O2"
SE="qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se"
packs_of() { # bash 3.2: no associative arrays
  case "$1" in qa-cooking-se|qa-money-se) echo "$KIT,shared-data/packs/wave3/$1.sqlite";; boar-factbook|boar-simplewiki-en) echo "$KIT,shared-data/packs/wave2/$1.sqlite";; base) echo "$KIT";; se5) local s="$KIT"; for p in $SE; do s="$s,$W/$p.sqlite"; done; echo "$s";; *) echo "$KIT,$W/$1.sqlite";; esac; }
LABS="base $SE boar-firstaid-en boar-medlineplus-en se5"; AGGF=""
[ "${1:-}" = "--wave2" ] && { LABS="boar-factbook boar-simplewiki-en"; AGGF=--wave2; shift; }  # T-K6b (baselines reused)
[ "${1:-}" = "--wave3" ] && { LABS="qa-cooking-se qa-money-se"; AGGF=--wave3; shift; }  # wave 3 (2026-10-13; baselines reused)
ONLY="${2:-}"
for lab in $LABS; do
  [ -n "$ONLY" ] && [ "$ONLY" != "$lab" ] && continue
  C=(--deep --gate rules --k 6 --pool 20 --tree wt/packs --packs "$(packs_of "$lab")")
  "$R" "${C[@]}" --questions boar-eval/bench/v0.1/questions.public.jsonl --gold boar-eval/bench/v0.1/gold/sources.json \
    --out "$O1/v01-$lab.jsonl" 2> >(grep -E '^\{|app dir' | sed "s/^/[v01 $lab] /" >&2)
  "$R" "${C[@]}" --questions blind/bench-v02/live/v0.2/questions.v02-new.jsonl --gold boar-eval/bench/v0.2/gold/sources.json \
    --tasks-from blind/bench-v02/runs-dt512v02/dhv-H-v02-s42.traces.jsonl \
    --out "$O2/v02-$lab.jsonl" 2> >(grep -E '^\{|app dir|identical' | sed "s/^/[v02 $lab] /" >&2)
done
python3 -I "$H/crowding_agg.py" $AGGF

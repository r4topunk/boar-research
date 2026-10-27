#!/bin/bash
# VEXACT-ACCEPT one-command acceptance run (MacBook orchestrator; generation on the Mac mini, judge here).
# The 11 public V-exact items (bench-vslice: 5 judged + 6 vegan venue items, 3 of them GPS-only) through the claim engine
# (kiln tree be-0cfd4a77-cut7-headpass-x2 = cut 7 + HEADPASS-X2b, Qwen3-4B-Instruct-2507 Q4_K_M, prompt D4 by default, claim kit
# boar-crypto + boar-wikivoyage-en, places kit-vexact = device location + area tile), then Haiku 5.5-low judge (N = 4, both orders)
# on the 5 judged items, venue scorer (rnd/kiln/l1/vexact-venues.mjs, OSM gold) on the 6 venue items, aggregate + acceptance verdict.
#
# Usage:
#   run.sh --label <name> [--seeds "42 43"] [--prompt D4|engine] [--pack <id>=<mini path to <id>.sqlite>]... [--facts <mini path to facts json>]
#          [--baseline <label>] [--own-gate PASS|FAIL|NA] [--port 8193] [--wait-chainwhen] [--skip-gen] [--skip-judge] [--no-reuse]
# Examples:
#   run.sh --label baseline --wait-chainwhen                      # the frozen baseline (done 2026-10-19/20)
#   run.sh --label cand-foo --pack boar-foo-en=<runner>/shared-data/packs/wave3/boar-foo-en.sqlite --baseline baseline --own-gate PASS
#   run.sh --label facts-r9 --facts <runner>/kiln/facts-r9/facts.v1.json --baseline baseline --own-gate PASS
# Outputs: arms/vexact-accept/runs/<label>/ (requests, traces, logs, rewrites, judgments, venues.json, result.json, RESULT.md).
# Judge reuse (default with --baseline): a judged item whose answer text is byte-identical to the baseline's (same seed) reuses the baseline's
#   judgment rows (0 calls); only changed answers are judged. --no-reuse judges everything.
# Guards (mini side, mini_gen.sh): tree/adapter/X2b sha, kit-vexact sha, detector :8094 up (never started or stopped here), our port only,
#   disk >= 25 GiB. This script never touches :8191, :8094, Docker or ollama.
set -u
A=<workspace>/rnd/research/coordinator/arms/vexact-accept; TOOLS=$A/tools; MW=boar/kiln/vexact-accept
VS=<workspace>/rnd/research/compass/exp/bounty-eval/bench-vslice; SJ=$A/../deepthink/tools/shard_judge.sh; CJ=$A/../_lib/check_judgments.py
LABEL=""; SEEDS="42 43"; PROMPT=D4; PACKS=(); FACTS=""; BASE=""; OWN=NA; PORT=8193; WAITCW=0; GEN=1; JUDGE=1; REUSE=1
while [ $# -gt 0 ]; do case $1 in
  --label) LABEL=$2; shift 2;; --seeds) SEEDS=$2; shift 2;; --prompt) PROMPT=$2; shift 2;; --pack) PACKS+=("$2"); shift 2;;
  --facts) FACTS=$2; shift 2;; --baseline) BASE=$2; shift 2;; --own-gate) OWN=$2; shift 2;; --port) PORT=$2; shift 2;;
  --wait-chainwhen) WAITCW=1; shift;; --skip-gen) GEN=0; shift;; --skip-judge) JUDGE=0; shift;; --no-reuse) REUSE=0; shift;;
  -h|--help) sed -n 2,22p "$0"; exit 0;; *) echo "unknown arg $1" >&2; exit 2;; esac; done
[ -n "$LABEL" ] || { echo "--label required" >&2; exit 2; }
case $PORT in 8191|8094) echo "port $PORT belongs to another job" >&2; exit 2;; esac
O=$A/runs/$LABEL; mkdir -p "$O"; LOG=$O/run.log
say() { echo "$(date '+%F %T') $*" | tee -a "$LOG"; }
say "run.sh label=$LABEL seeds=[$SEEDS] prompt=$PROMPT packs=[${PACKS[*]:-}] facts=${FACTS:-tree} baseline=${BASE:-none} own-gate=$OWN port=$PORT"

# --- candidate assets: packs (sha256 + dir on the mini), facts table
PACKARGS=(); PACKDIRS=""
for p in ${PACKS[@]+"${PACKS[@]}"}; do id=${p%%=*}; path=${p#*=}
  [ "$(basename "$path")" = "$id.sqlite" ] || { say "pack file must be named <id>.sqlite: $path"; exit 2; }
  sha=$(<on the mini> "shasum -a 256 '$path' | cut -d' ' -f1") ; [ ${#sha} = 64 ] || { say "pack $path not readable on the mini"; exit 2; }
  PACKARGS+=(--pack "$id=$sha"); d=$(dirname "$path"); PACKDIRS=${PACKDIRS:+$PACKDIRS:}$d; say "pack $id sha256 $sha dir $d"; done
[ -n "$FACTS" ] && { fs=$(<on the mini> "shasum -a 256 '$FACTS' | cut -d' ' -f1"); [ ${#fs} = 64 ] || { say "facts $FACTS not readable on the mini"; exit 2; }; say "facts $FACTS sha256 $fs"; }

# --- wait for CHAINWHEN (poll 5 min, max 2 h), then generate
if [ $GEN = 1 ] && [ $WAITCW = 1 ]; then
  for i in $(seq 0 24); do n=$(<on the mini> "wc -l < <runner>/kiln/chainwhen/answers-M4.jsonl" 2>/dev/null | tr -d ' ')
    [ "${n:-0}" -ge 236 ] && { say "CHAINWHEN answers-M4 = $n lines: go"; break; }
    [ $i = 24 ] && { say "CHAINWHEN still at ${n:-?}/236 after 2 h: STOP (not generating)"; exit 3; }
    say "wait CHAINWHEN ${n:-?}/236"; sleep 300; done
fi
rsync -a "$TOOLS/vxa-hook.mjs" "$TOOLS/mini_gen.sh" "$TOOLS/d4.json" "$TOOLS/fake_server.mjs" MINI_HOST:$MW/tools/ || { say "copy tools to mini failed"; exit 1; }
for s in $SEEDS; do R=vxa-$LABEL-s$s
  python3 -I "$TOOLS/mkreq.py" --run-id "$R" --seed "$s" ${PACKARGS[@]+"${PACKARGS[@]}"} > "$O/$R.requests.jsonl" || exit 1
  if [ $GEN = 1 ]; then
    <on the mini> "mkdir -p ~/$MW/runs/$LABEL" && scp -q "$O/$R.requests.jsonl" MINI_HOST:$MW/runs/$LABEL/ || exit 1
    say "generate $R on the mini :$PORT"
    <on the mini> "VXA_PORT=$PORT VXA_PROMPT=$PROMPT ${FACTS:+VXA_FACTS_JSON=$FACTS} ${PACKDIRS:+VXA_EXTRA_PACK_DIRS=$PACKDIRS} bash ~/$MW/tools/mini_gen.sh ~/$MW/runs/$LABEL/$R.requests.jsonl ~/$MW/runs/$LABEL/$R.traces.jsonl"; rc=$?
    for x in traces.jsonl traces.status traces.log traces.rewrites.jsonl traces.prompts.jsonl traces.llama.log; do scp -q MINI_HOST:$MW/runs/$LABEL/$R.$x "$O/" 2>/dev/null; done
    say "$R rc=$rc rows=$(wc -l < "$O/$R.traces.jsonl" 2>/dev/null | tr -d ' ') $(tail -1 "$O/$R.traces.status" 2>/dev/null)"
    [ $rc = 0 ] || exit $rc
  fi
done

# --- judge (5 judged items; venue-list items are never judged)
python3 -I -c "import json,sys;[print(d['id']) for d in map(json.loads,open(sys.argv[1])) if (d.get('grading') or {}).get('type')!='venue-list']" "$VS/questions.jsonl" > "$O/judged.ids"
if [ $JUDGE = 1 ]; then for s in $SEEDS; do R=vxa-$LABEL-s$s; J=$O/$R.judgments.jsonl
  python3 -I "$CJ" "$J" "$O/judged.ids" "$R" >/dev/null 2>&1 && { say "skip judge $R (complete)"; continue; }
  BT=""; [ -n "$BASE" ] && [ $REUSE = 1 ] && BT=$A/runs/$BASE/vxa-$BASE-s$s
  python3 -I "$TOOLS/reuse.py" "$O/$R.traces.jsonl" "$O/judged.ids" "${BT:-none}" "$O/$R.tojudge.ids" "$O/$R.reused.jsonl" | tee -a "$LOG"
  : > "$O/$R.new.jsonl"
  if [ -s "$O/$R.tojudge.ids" ]; then
    bash "$SJ" "$O/$R.traces.jsonl" "$O/$R.new.jsonl" "$VS" "$O/$R.tojudge.ids" "vexact-accept-$LABEL-s$s-haiku55-low" 4 haiku >> "$LOG" 2>&1 || { say "judge FAIL $R"; exit 4; }
  fi
  cat "$O/$R.reused.jsonl" "$O/$R.new.jsonl" > "$J"
  python3 -I "$CJ" "$J" "$O/judged.ids" "$R" | tee -a "$LOG" | grep -q '^check ok' || { say "judgments incomplete $R"; exit 4; }
done; fi

# --- venues + aggregate + verdict
RB=(); for s in $SEEDS; do RB+=("vxa-$LABEL-s$s"); done
node <workspace>/rnd/kiln/l1/vexact-venues.mjs "$O" "${RB[@]}" > "$O/venues.json" || { say "venue scorer failed"; exit 5; }
python3 -I "$TOOLS/agg.py" --label "$LABEL" --seeds "$SEEDS" --prompt "$PROMPT" ${BASE:+--baseline "$BASE"} --own-gate "$OWN" | tee -a "$LOG"

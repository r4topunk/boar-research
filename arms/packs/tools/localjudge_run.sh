#!/bin/bash
# SELFTEST-LOCALJUDGE driver: judge.v1 (unchanged judge.mjs) through the shim-qwen BOAR_EVAL_LIB -> Qwen3.6-35B-A3B Q2 llama-server on the mini
# (tunnel 127.0.0.1:18092). Per pack, with-pack (W) and no-pack (N) runs are INTERLEAVED per item with --limit 1 so consecutive calls share
# the longest prompt prefix (same question/notes/reference) in the server's prompt cache: W first order, N first order, W second, N second.
# Order per item = judge.mjs firstOrders (seed 7), identical for W and N. judge.mjs resumes ok rows, so rerunning this script resumes.
# Usage: localjudge_run.sh [pack ...]   Output: selftest-runs/localjudge/<run>.judgments.qwen36q2.jsonl; log in selftest-runs/localjudge.log
set -u
H=$(cd "$(dirname "$0")/.." && pwd); D=$H/selftest-runs; L=$D/localjudge; EVAL=$BOAR_WS/boar-eval; mkdir -p "$L/calls"
export BOAR_EVAL_LIB=$BOAR_WS/rnd/research/coordinator/arms/judge2/shim-qwen JUDGE2_LOG_DIR=$L/calls
PACKS=${*:-qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en boar-factbook boar-simplewiki-en}
cd "$EVAL" || exit 2
J() { local R=$1 id=$2 lim=$3; [ -e "$L/STOP" ] && { echo "STOP file"; exit 4; }
  local t; for t in 1 2 3; do
    node harness/judge.mjs --traces "$D/$R.traces.jsonl" --out "$L/$R.judgments.qwen36q2.jsonl" --bench "bench/selftest/$P" --ids "$id" $lim \
      --effort qwen36q2 --gap-ms 0 --seed 7 --system "selftest-$R-qwen36q2" --strict 2>&1 | grep -v "^judge:\|^done\|limit 1 reached"
    [ ${PIPESTATUS[0]} = 0 ] && return 0; echo "retry $R $id ($t)"; sleep 20; done; echo "FAILED $R $id"; return 1; }
for P in $PACKS; do W=st-$P-cut7-s42; N=st-$P-cut7-nopack-s42
  until grep -q DONE "$D/$W.traces.status" 2>/dev/null && grep -q DONE "$D/$N.traces.status" 2>/dev/null; do sleep 30; done
  echo "=== $P start $(date '+%F %T')"
  [ -s "$D/$W.ids" ] || { echo "FAIL no ids file $D/$W.ids"; continue; }
  for id in $(cat "$D/$W.ids"); do J $W $id "--limit 1"; J $N $id "--limit 1"; J $W $id ""; J $N $id ""; done
  echo "=== $P end $(date '+%F %T') rows W=$(wc -l < "$L/$W.judgments.qwen36q2.jsonl") N=$(wc -l < "$L/$N.judgments.qwen36q2.jsonl")"
done; echo ALLDONE $(date '+%F %T')

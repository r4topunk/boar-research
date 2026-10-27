#!/usr/bin/env bash
# CLAIM RUN A: bench v0.2 held-out L3 for cut 6 (auth rnd/research/coordinator/CLAIM-RUNS-cut6.md sha 5cd07029…).
# Tree be-0cfd4a77-detmax (patch 824e0b35…), runner be-repo adapter 7a0282ae (committed boar-eval 73b9d2c, BOAR_RUNNER_PROFILE=ship), detector v3b ON, NO --places (identical to runs-ship).
# Requests = runs-ship requests re-keyed (runId, arm=detmax) so config is byte-identical otherwise. s42+s43, v0.2-new 110 + v0.1 72 per seed.
# Judge judge.v1 (no --effort), both orders, MacBook default account. Outputs ONLY under blind/bench-v02/runs-cut6/. No content printed.
set -uo pipefail
B=<workspace>; E=$B/boar-eval; V2=$B/blind/bench-v02/live/v0.2; SH=$B/blind/bench-v02/runs-ship; OUT=$B/blind/bench-v02/runs-cut6; C3=$B/blind/bench-v02/runs-cut3
MD=<runner>/shared-models/emergency-detector
export HEAVY_CLASS=normal BOAR_EVAL_RUNNER_DIR=be-repo BOAR_RUNNER_PROFILE=ship
got=$(echo 'cd <runner>/kiln/be-0cfd4a77-detmax && echo "$(cut -c1-16 PATCH_SHA256) $(shasum -a 256 be-repo/adapter.ts | cut -c1-16)"' | <on the mini> bash -s)
[ "$got" = "824e0b35fcdfe46b 7a0282ae1f4229e6" ] || { echo "TREE/RUNNER MISMATCH $got"; exit 1; }; echo "tree ok $got"
echo "free before: $(<on the mini> "df -g ~ | awk 'NR==2{print \$4}'") GiB"
ensure_det() { # technical-failure guard (added after the detector was stopped externally during the first attempt): (re)start the detector if down
  if ! <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1; then
    <on the mini> "bash -c 'cd $MD && shasum -a 256 -c SHA256SUMS >/dev/null && nohup <runner>/spikes/llama-b11010/build-cpu/bin/llama-server -m $MD/sonar-mmbert-small-emergency-v3b-q8te4.gguf --embeddings --pooling mean -np 1 -t 2 -c 512 -b 512 -ub 512 --host 127.0.0.1 --port 8094 > <runner>/kiln/detector-8094.log 2>&1 < /dev/null &'" & SSHP=$!
    for i in $(seq 1 60); do <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && break; sleep 2; done; kill $SSHP 2>/dev/null
  fi
  <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && echo "detector up" || { echo "DETECTOR DOWN"; exit 1; }
}
ensure_det
DET=(BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json)
rekey() { python3 - "$1" "$2" "$3" <<'PY'
import json, sys
rows = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
for r in rows: r["runId"] = sys.argv[3]; r["config"]["arm"] = "detmax"
open(sys.argv[2], "w").write("".join(json.dumps(r) + "\n" for r in rows))
print(f"rekeyed {sys.argv[3]} n={len(rows)}")
PY
}
run() { # label
  if [ -s $OUT/$1.traces.jsonl ]; then echo "$1 already run (kept)"; return; fi  # resume after a technical failure
  ensure_det
  env "${DET[@]}" $E/adapters/desktop-node/run.sh --commit 0cfd4a77 --arm detmax --requests $OUT/$1.requests.jsonl --out $OUT/$1.traces.jsonl > $OUT/$1.runsh.out 2>&1
  local rc=$?; <on the mini> "rm -rf <runner>/kiln/be-0cfd4a77-detmax/be-repo/runs/$1"
  <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && echo "detector still up after $1" || echo "DETECTOR-LOST during $1"
  python3 - "$OUT/$1.traces.jsonl" "$1 rc=$rc" <<'PY'
import json, sys
T = [json.loads(l) for l in open(sys.argv[1])]
rg = sum(any(c.startswith("route-gate:") for c in t["route"]["reasonCodes"]) for t in T)
dp = sum(any(c.startswith("detector:p=") for c in t["route"]["reasonCodes"]) for t in T)
print(f"{sys.argv[2]} n={len(T)} errors={sum(bool(t.get('error')) for t in T)} route-gate={rg} detector:p={dp}")
PY
}
for seed in 42 43; do
  rekey $SH/ship-v02-s$seed.requests.jsonl $OUT/cut6-v02-s$seed.requests.jsonl cut6-v02-s$seed
  rekey $SH/ship-v01-s$seed.requests.jsonl $OUT/cut6-v01-s$seed.requests.jsonl cut6-v01-s$seed
done
for seed in 42 43; do
  run cut6-v02-s$seed
  python3 $B/rnd/kiln/l1/cut6-claim-reuse.py $OUT/cut6-v02-s$seed.traces.jsonl $C3/cut3-v02-s$seed.traces.jsonl $C3/cut3-v02-s$seed.judgments.jsonl $OUT/cut6-v02-s$seed.judgments.jsonl cut6-v02-s$seed
  (cd $E && node harness/judge.mjs --traces $OUT/cut6-v02-s$seed.traces.jsonl --out $OUT/cut6-v02-s$seed.judgments.jsonl --bench $V2 --system cut6-v02-s$seed > $OUT/cut6-v02-s$seed.judge.log 2>&1; echo "judge v02 s$seed rc=$?") &
  run cut6-v01-s$seed
  python3 $B/rnd/kiln/l1/cut6-claim-reuse.py $OUT/cut6-v01-s$seed.traces.jsonl $C3/cut3-v01-s$seed.traces.jsonl $C3/cut3-v01-s$seed.judgments.jsonl $OUT/cut6-v01-s$seed.judgments.jsonl cut6-v01-s$seed
  (cd $E && node harness/judge.mjs --traces $OUT/cut6-v01-s$seed.traces.jsonl --out $OUT/cut6-v01-s$seed.judgments.jsonl --bench bench/v0.1 --system cut6-v01-s$seed > $OUT/cut6-v01-s$seed.judge.log 2>&1; echo "judge v01 s$seed rc=$?") &
done
echo "free after: $(<on the mini> "df -g ~ | awk 'NR==2{print \$4}'") GiB"
wait; echo CUT6-A-RUNS-JUDGED

#!/usr/bin/env bash
# SHIP-CANDIDATE v0.2 held-out L3 (coordinator-authorised; BOUNTY-BOARD row 1). Usage: SHIP_PATCH=<path> SHIP_SHA=<sha256> ship-l3.sh
# Stack: 0cfd4a77 + b6-on-health13 (Anvil), runner 949eee03 (bb05e07b + runner-b4gate + health11-runner), detector ON (v3b,
# llama-server b11010 CPU, thr unset), E3 Android 12 GB 4B config (and-qwen, kit A crypto + wikivoyage-en), s42 + s43.
# Runs: v0.2-new 110 (held-out, --bench blind/bench-v02/live/v0.2) + v0.1 72 (public+safety, bench v0.1) per seed, so the
# report has: held-out 110 (headline), full 182 (v02all view), and EN-only 182. Judge = judge.v1 opus on the default account.
# Blind terms: outputs only under blind/bench-v02/runs-ship/, ids + aggregates only, mini copies deleted.
set -uo pipefail
B=<workspace>; E=$B/boar-eval; V2=$B/blind/bench-v02/live/v0.2; OUT=$B/blind/bench-v02/runs-ship; MD=<runner>/shared-models/emergency-detector
: "${SHIP_PATCH:?}" "${SHIP_SHA:?}"; ARM=shiph13; mkdir -p $OUT
export HEAVY_CLASS=normal BOAR_EVAL_RUNNER_DIR=be-ship
PA=<scratch>
[ "$(shasum -a 256 $SHIP_PATCH | cut -c1-64)" = "$SHIP_SHA" ] || { echo "PATCH SHA MISMATCH"; exit 1; }
echo "v0.2-new questions sha256 $(shasum -a 256 $V2/questions.v02-new.jsonl | cut -c1-64)"
(cd $E && adapters/desktop-node/setup.sh 0cfd4a77 --patch $SHIP_PATCH --arm $ARM 2>&1 | tail -1 | cut -c1-120)
scp -q $PA MINI_HOST:boar/kiln/be-0cfd4a77-$ARM/be-ship/adapter.ts
got=$(echo "cd <runner>/kiln/be-0cfd4a77-$ARM && echo \$(cut -c1-16 PATCH_SHA256) \$(shasum -a 256 be-ship/adapter.ts | cut -c1-16)" | <on the mini> bash -s)
[ "$got" = "${SHIP_SHA:0:16} 949eee0355032eb1" ] || { echo "TREE/RUNNER MISMATCH $got"; exit 1; }; echo "tree ok $got"
if ! <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1; then
  <on the mini> "bash -c 'cd $MD && shasum -a 256 -c SHA256SUMS >/dev/null && nohup <runner>/spikes/llama-b11010/build-cpu/bin/llama-server -m $MD/sonar-mmbert-small-emergency-v3b-q8te4.gguf --embeddings --pooling mean -np 1 -t 2 -c 512 -b 512 -ub 512 --host 127.0.0.1 --port 8094 > <runner>/kiln/detector-8094.log 2>&1 < /dev/null &'" & SSHP=$!
  for i in $(seq 1 60); do <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && break; sleep 2; done; kill $SSHP 2>/dev/null
fi
<on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && echo "detector up" || { echo "DETECTOR DOWN"; exit 1; }
DET=(BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json)
mkreq() { # questions-or-requests seed label out kind
  local src=$1 seed=$2 label=$3 out=$4 kind=$5
  if [ $kind = v02 ]; then
    python3 -c "import json; c=json.load(open('$B/blind/bench-v02/runs-e3/e3-main-s42.config.json')); c['arm']='$ARM'; c['seed']=$seed; json.dump(c, open('$OUT/$label.config.json','w'))"
    pnpm -s -C $E/packages/protocol exec tsx src/makeRequests.ts --questions $src --config $OUT/$label.config.json --run-id $label > $out 2>/dev/null
  else  # v0.1: re-key the E3-matched Android 12 GB v0.1 requests (and-qwen night config)
    python3 - "$E/runs/night-2026-10-01/and-qwen-s$seed.requests.jsonl" "$out" "$label" "$ARM" <<'PY'
import json, sys
rows = [json.loads(l) for l in open(sys.argv[1])]
for r in rows: r["runId"] = sys.argv[3]; r["config"]["arm"] = sys.argv[4]
open(sys.argv[2], "w").write("".join(json.dumps(r) + "\n" for r in rows))
PY
  fi
}
run() { # label requests
  env "${DET[@]}" $E/adapters/desktop-node/run.sh --commit 0cfd4a77 --arm $ARM --requests $2 --out $OUT/$1.traces.jsonl > $OUT/$1.runsh.out 2>&1
  local rc=$?; <on the mini> "rm -rf <runner>/kiln/be-0cfd4a77-$ARM/be-ship/runs/$1"
  python3 - "$OUT/$1.traces.jsonl" "$1 rc=$rc" <<'PY'
import json, sys
T = [json.loads(l) for l in open(sys.argv[1])]
rg = sum(any(c.startswith("route-gate:") for c in t["route"]["reasonCodes"]) for t in T)
dp = sum(any(c.startswith("detector:p=") for c in t["route"]["reasonCodes"]) for t in T)
print(f"{sys.argv[2]} n={len(T)} errors={sum(bool(t.get('error')) for t in T)} route-gate={rg} detector:p={dp}")
PY
}
# sanity item 1 (route-gate:* AND detector:p=*) on the first v0.1 public item (not blind)
mkreq x 42 ship-sanity $OUT/ship-sanity.requests.jsonl v01; head -1 $OUT/ship-sanity.requests.jsonl > $OUT/ship-sanity.1.jsonl
run ship-sanity $OUT/ship-sanity.1.jsonl
python3 -c "
import json,sys; t=json.loads(open('$OUT/ship-sanity.traces.jsonl').readline()); c=t['route']['reasonCodes']
ok=any(x.startswith('route-gate:') for x in c) and any(x.startswith('detector:p=') for x in c); print('sanity', 'OK' if ok else 'FAIL'); sys.exit(0 if ok else 1)" || { echo "SANITY FAIL: stop"; exit 1; }
for seed in 42 43; do
  mkreq $V2/questions.v02-new.jsonl $seed ship-v02-s$seed $OUT/ship-v02-s$seed.requests.jsonl v02; run ship-v02-s$seed $OUT/ship-v02-s$seed.requests.jsonl
  mkreq x $seed ship-v01-s$seed $OUT/ship-v01-s$seed.requests.jsonl v01; run ship-v01-s$seed $OUT/ship-v01-s$seed.requests.jsonl
  (cd $E && node harness/judge.mjs --traces $OUT/ship-v02-s$seed.traces.jsonl --out $OUT/ship-v02-s$seed.judgments.jsonl --bench $V2 --system ship-v02-s$seed > $OUT/ship-v02-s$seed.judge.log 2>&1; echo "judge v02 s$seed rc=$?") &
  (cd $E && node harness/judge.mjs --traces $OUT/ship-v01-s$seed.traces.jsonl --out $OUT/ship-v01-s$seed.judgments.jsonl --bench bench/v0.1 --system ship-v01-s$seed > $OUT/ship-v01-s$seed.judge.log 2>&1; echo "judge v01 s$seed rc=$?") &
done
echo 'p=$(lsof -tiTCP:8094 -sTCP:LISTEN); [ -n "$p" ] && kill $p; echo detector stopped' | <on the mini> bash -s
wait; echo SHIP-L3-RUNS-JUDGED

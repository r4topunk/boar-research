#!/usr/bin/env bash
# SPEEDPACK L1: control = instsubj4 tree (cut 4 final d51e844c), arm = speedpack tree (patch sha256 bb3dbde1...); both --backend server (as KVQ8), reader f16 KV.
# v0.1 EN s44+s45 interleaved (s44 ctl, s44 sp, s45 ctl, s45 sp), detector on, heavy lock. The final echo still says KVQ8-L1-GEN-DONE (copied template).
# turned into --cache-type-k/-v by the be-ship adapter (local runner edit, sha f5c50806...). Env unset -> no flag (default f16).
set -uo pipefail
B=<workspace>; E=$B/boar-eval; A=$B/rnd/research/coordinator/arms
PSHA=d51e844c6522cb18; RUNNER_SHA=f5c5080635558897; SPSHA=bb3dbde122b838bc
OUT=$E/runs/kiln/speedpack-l1; D4=$E/runs/kiln/cut4-l1
MD=<runner>/shared-models/emergency-detector; P=<runner>/shared-data/poi/kit-vexact
SRV=<runner>/spikes/llama-b11010/build-cpu/bin/llama-server
mkdir -p $OUT; export HEAVY_CLASS=normal BOAR_EVAL_RUNNER_DIR=be-ship
PLACES=$P/world-places.sqlite,$P/t-N52E013.sqlite,$P/t-N38W010.sqlite,$P/t-N35E139.sqlite,$P/t-N35E140.sqlite
got=$(echo 'cd <runner>/kiln/be-0cfd4a77-instsubj4 && echo "$(cut -c1-16 PATCH_SHA256) $(shasum -a 256 be-ship/adapter.ts | cut -c1-16)"' | <on the mini> bash -s)
[ "$got" = "$PSHA $RUNNER_SHA" ] || { echo "TREE/RUNNER MISMATCH $got"; exit 1; }; echo "tree ok $got"
got2=$(echo 'cd <runner>/kiln/be-0cfd4a77-speedpack && echo "$(cut -c1-16 PATCH_SHA256) $(shasum -a 256 be-ship/adapter.ts | cut -c1-16)"' | <on the mini> bash -s)
[ "$got2" = "$SPSHA $RUNNER_SHA" ] || { echo "SP TREE/RUNNER MISMATCH $got2"; exit 1; }; echo "sp tree ok $got2"
echo "free before: $(<on the mini> "df -g ~ | awk 'NR==2{print \$4}'") GiB"
if ! <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1; then
  <on the mini> "bash -c 'cd $MD && shasum -a 256 -c SHA256SUMS >/dev/null && nohup <runner>/spikes/llama-b11010/build-cpu/bin/llama-server -m $MD/sonar-mmbert-small-emergency-v3b-q8te4.gguf --embeddings --pooling mean -np 1 -t 2 -c 512 -b 512 -ub 512 --host 127.0.0.1 --port 8094 > <runner>/kiln/detector-8094.log 2>&1 < /dev/null &'" & SSHP=$!
  for i in $(seq 1 60); do <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && break; sleep 2; done; kill $SSHP 2>/dev/null
fi
<on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && echo "detector up" || { echo "DETECTOR DOWN"; exit 1; }
DET=(BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json)
for s in 44 45; do for arm in ctl sp; do
  python3 - $D4/cut4-v01-s$s.requests.jsonl $OUT/sp$arm-v01-s$s.requests.jsonl sp$arm-v01-s$s sp$arm <<'PY'
import json, sys
rows = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
for r in rows: r["runId"] = sys.argv[3]; r["config"]["arm"] = "instsubj4" if sys.argv[4] == "spctl" else "speedpack"
open(sys.argv[2], "w").write("".join(json.dumps(r) + "\n" for r in rows))
PY
done; done
for s in 44 45; do for arm in ctl sp; do
  l=sp$arm-v01-s$s; KV=(BOAR_KV_TYPE=); TREE=instsubj4; [ $arm = sp ] && TREE=speedpack
  env "${DET[@]}" "${KV[@]}" $E/adapters/desktop-node/run.sh --commit 0cfd4a77 --arm $TREE --requests $OUT/$l.requests.jsonl --out $OUT/$l.traces.jsonl --places $PLACES --backend server --server-bin $SRV > $OUT/$l.runsh.out 2>&1
  echo "$l rc=$? $(date +%H:%M) $(tail -1 $OUT/$l.runsh.out | cut -c1-90)"
  <on the mini> "rm -rf <runner>/kiln/be-0cfd4a77-$TREE/be-ship/runs/$l"
done; done
echo 'p=$(lsof -tiTCP:8094 -sTCP:LISTEN); [ -n "$p" ] && kill $p; echo detector stopped' | <on the mini> bash -s
echo "free after: $(<on the mini> "df -g ~ | awk 'NR==2{print \$4}'") GiB"
echo KVQ8-L1-GEN-DONE

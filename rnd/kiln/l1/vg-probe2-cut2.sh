#!/usr/bin/env bash
# VG v4 ship-gate probe answers (criterion rnd/research/coordinator/arms/vg4-S2-criterion.md 1f31215b…, NOT applied here; generation only, no judge).
# Probe set arms/vg-probe-q2/items.jsonl (5449bf82…, 120 items) wrapped as ad-hoc EvalRequests cloned from the overnight cut 2 s44 request
# config (Android 12 GB 4B, kit A, seed 44). Tree be-0cfd4a77-cut2 (7931b9a8) UNPATCHED, runner be-ship 949eee03, detector v3b ON,
# --places kit-vexact, heavy lock via run.sh. Output: boar-eval/runs/kiln/vg-probe2-cut2-s44/traces.jsonl.
set -uo pipefail
B=<workspace>; E=$B/boar-eval; OUT=$E/runs/kiln/vg-probe2-cut2-s44; Q=$B/rnd/research/coordinator/arms/vg-probe-q2/items.jsonl
MD=<runner>/shared-models/emergency-detector; P=<runner>/shared-data/poi/kit-vexact
mkdir -p $OUT; export HEAVY_CLASS=normal BOAR_EVAL_RUNNER_DIR=be-ship
PLACES=$P/world-places.sqlite,$P/t-N52E013.sqlite,$P/t-N38W010.sqlite,$P/t-N35E139.sqlite,$P/t-N35E140.sqlite
[ "$(shasum -a 256 $Q | cut -c1-16)" = "5449bf822efe4efc" ] || { echo "PROBE SET SHA MISMATCH"; exit 1; }
got=$(echo 'cd <runner>/kiln/be-0cfd4a77-cut2 && echo "$(cut -c1-16 PATCH_SHA256) $(shasum -a 256 be-ship/adapter.ts | cut -c1-16)"' | <on the mini> bash -s)
[ "$got" = "7931b9a8905f230a 949eee0355032eb1" ] || { echo "TREE/RUNNER MISMATCH $got"; exit 1; }; echo "tree ok $got"
echo "free before: $(<on the mini> "df -g ~ | awk 'NR==2{print \$4}'") GiB"
python3 - $E/runs/kiln/cut3-vgar-l1/cut2-v01-s44.requests.jsonl $Q $OUT/requests.jsonl <<'PY'
import json, sys
tpl = json.loads(open(sys.argv[1]).readline()); rows = []
for l in open(sys.argv[2]):
    if not l.strip(): continue
    it = json.loads(l)
    r = json.loads(json.dumps(tpl)); r["runId"] = "vg-probe2-cut2-s44"; r["item"] = {"id": it["id"], "question": it["question"], "lang": "en"}
    rows.append(r)
assert rows[0]["config"]["arm"] == "cut2" and rows[0]["seed"] == 44
open(sys.argv[3], "w").write("".join(json.dumps(r) + "\n" for r in rows)); print("requests", len(rows))
PY
if ! <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1; then
  <on the mini> "bash -c 'cd $MD && shasum -a 256 -c SHA256SUMS >/dev/null && nohup <runner>/spikes/llama-b11010/build-cpu/bin/llama-server -m $MD/sonar-mmbert-small-emergency-v3b-q8te4.gguf --embeddings --pooling mean -np 1 -t 2 -c 512 -b 512 -ub 512 --host 127.0.0.1 --port 8094 > <runner>/kiln/detector-8094.log 2>&1 < /dev/null &'" & SSHP=$!
  for i in $(seq 1 60); do <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && break; sleep 2; done; kill $SSHP 2>/dev/null
fi
<on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && echo "detector up" || { echo "DETECTOR DOWN"; exit 1; }
env BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json \
  $E/adapters/desktop-node/run.sh --commit 0cfd4a77 --arm cut2 --requests $OUT/requests.jsonl --out $OUT/traces.jsonl --places $PLACES > $OUT/runsh.out 2>&1
echo "vg-probe2-cut2-s44 rc=$? $(date +%H:%M) $(tail -1 $OUT/runsh.out | cut -c1-120)"
<on the mini> "rm -rf <runner>/kiln/be-0cfd4a77-cut2/be-ship/runs/vg-probe2-cut2-s44"
echo 'p=$(lsof -tiTCP:8094 -sTCP:LISTEN); [ -n "$p" ] && kill $p; echo detector stopped' | <on the mini> bash -s
python3 -c "
import json; T=[json.loads(l) for l in open('$OUT/traces.jsonl')]
print(f'validity: answers {sum(1 for t in T if not t.get(\"error\") and (t.get(\"answer\") or {}).get(\"text\",\"\").strip())}/{len(T)} non-empty, errors {sum(bool(t.get(\"error\")) for t in T)}, declined {sum(bool((t.get(\"answer\") or {}).get(\"declined\")) for t in T)}')"
echo "free after: $(<on the mini> "df -g ~ | awk 'NR==2{print \$4}'") GiB"
echo VG-PROBE2-DONE

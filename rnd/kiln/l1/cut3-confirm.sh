#!/usr/bin/env bash
# cut 3 confirmation (criterion rnd/research/coordinator/cut3-confirm-criterion.md, sha256 fdd06c4a…). Generation only; judging separate.
# Tree be-0cfd4a77-cut3 (arms/cut3-final-candidate.vs-0cfd4a77.patch a67c70db… = cut 2 + VG v3 + AR + SBt), runner be-ship 949eee03,
# detector v3b ON (THR unset), --places kit-vexact, heavy lock via run.sh.
# (a) v0.1 EN s44/s45 = overnight cut 2 requests re-keyed. (b) V-exact and4b s42/s43 = cut 2 V-exact requests re-keyed.
set -uo pipefail
B=<workspace>; E=$B/boar-eval; OUT=$E/runs/kiln/cut3-confirm; C2=$E/runs/kiln/vexact-cut2; V=$E/runs/kiln/cut3-vgar-l1
MD=<runner>/shared-models/emergency-detector; P=<runner>/shared-data/poi/kit-vexact
mkdir -p $OUT; export HEAVY_CLASS=normal BOAR_EVAL_RUNNER_DIR=be-ship
PLACES=$P/world-places.sqlite,$P/t-N52E013.sqlite,$P/t-N38W010.sqlite,$P/t-N35E139.sqlite,$P/t-N35E140.sqlite
got=$(echo 'cd <runner>/kiln/be-0cfd4a77-cut3 && echo "$(cut -c1-16 PATCH_SHA256) $(shasum -a 256 be-ship/adapter.ts | cut -c1-16)"' | <on the mini> bash -s)
[ "$got" = "a67c70dbd194da82 949eee0355032eb1" ] || { echo "TREE/RUNNER MISMATCH $got"; exit 1; }; echo "tree ok $got"
echo "free before: $(<on the mini> "df -g ~ | awk 'NR==2{print \$4}'") GiB"
if ! <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1; then
  <on the mini> "bash -c 'cd $MD && shasum -a 256 -c SHA256SUMS >/dev/null && nohup <runner>/spikes/llama-b11010/build-cpu/bin/llama-server -m $MD/sonar-mmbert-small-emergency-v3b-q8te4.gguf --embeddings --pooling mean -np 1 -t 2 -c 512 -b 512 -ub 512 --host 127.0.0.1 --port 8094 > <runner>/kiln/detector-8094.log 2>&1 < /dev/null &'" & SSHP=$!
  for i in $(seq 1 60); do <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && break; sleep 2; done; kill $SSHP 2>/dev/null
fi
<on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && echo "detector up" || { echo "DETECTOR DOWN"; exit 1; }
DET=(BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json)
rekey() { python3 - "$1" "$2" "$3" <<'PY'
import json, sys
rows = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
for r in rows: r["runId"] = sys.argv[3]; r["config"]["arm"] = "cut3"
open(sys.argv[2], "w").write("".join(json.dumps(r) + "\n" for r in rows))
PY
}
for s in 44 45; do rekey $V/cut2-v01-s$s.requests.jsonl $OUT/cut3-v01-s$s.requests.jsonl cut3-v01-s$s; done
for s in 42 43; do rekey $C2/vslice-and4b-s$s.requests.jsonl $OUT/cut3-vslice-and4b-s$s.requests.jsonl cut3-vslice-and4b-s$s; done
for l in cut3-vslice-and4b-s42 cut3-vslice-and4b-s43 cut3-v01-s44 cut3-v01-s45; do
  env "${DET[@]}" $E/adapters/desktop-node/run.sh --commit 0cfd4a77 --arm cut3 --requests $OUT/$l.requests.jsonl --out $OUT/$l.traces.jsonl --places $PLACES > $OUT/$l.runsh.out 2>&1
  echo "$l rc=$? $(date +%H:%M) $(tail -1 $OUT/$l.runsh.out | cut -c1-90)"
  <on the mini> "rm -rf <runner>/kiln/be-0cfd4a77-cut3/be-ship/runs/$l"
done
echo 'p=$(lsof -tiTCP:8094 -sTCP:LISTEN); [ -n "$p" ] && kill $p; echo detector stopped' | <on the mini> bash -s
echo "free after: $(<on the mini> "df -g ~ | awk 'NR==2{print \$4}'") GiB"
echo CUT3-GEN-DONE

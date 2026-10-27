#!/usr/bin/env bash
# CV SHIP-GATE generation (frozen rev1 patch 8271ec3b..; gate-set 120 items afabb860..; gate-key never opened). Derived from cv-dev.sh.
# (old header follows) CV L0 generation (criterion rnd/research/coordinator/arms/cv/CV-criterion.md): the 210 DEV probe questions
# (arms/vg-probe-q 90 + arms/vg-probe-q2 120, question text only; arms/cv/gold is never opened) answered ONCE with cut 3 and ONCE with
# cut 3 + CV, same Android 12 GB 4B profile, kit A, detector v3b ON, --places kit-vexact, seed 44, runner be-ship 949eee03.
# No judge, no scoring. Trees: be-0cfd4a77-cut3 (a67c70db..) and be-0cfd4a77-cv (arms/cv/cv-on-cut3.vs-0cfd4a77.patch, built with
# `BOAR_EVAL_RUNNER_DIR=be-ship setup.sh 0cfd4a77 --patch ... --arm cv`, then the patched be-ship copied from the cut3 tree because
# setup.sh resets the runner). Output: boar-eval/runs/kiln/cv-dev-{cut3,cv}-s44/traces.jsonl.
# usage: cv-dev.sh                  full run, both arms
#        ARMS=cv IDS=a,b OUT_SUFFIX=-pilot cv-dev.sh    pilot (output dir gets the suffix)
set -uo pipefail
B=<workspace>; E=$B/boar-eval; A=$B/rnd/research/coordinator/arms
MD=<runner>/shared-models/emergency-detector; P=<runner>/shared-data/poi/kit-vexact
ARMS=${ARMS:-"cut3 cvs"}; IDS=${IDS:-}; SFX=${OUT_SUFFIX:-}
export HEAVY_CLASS=normal BOAR_EVAL_RUNNER_DIR=be-ship
PLACES=$P/world-places.sqlite,$P/t-N52E013.sqlite,$P/t-N38W010.sqlite,$P/t-N35E139.sqlite,$P/t-N35E140.sqlite
G3=$A/cvs/gate3-set/items.jsonl; G1=$A/cv/gate-set/items.jsonl
[ "$(shasum -a 256 $G3 | cut -c1-16)" = "6af3b0d130935bcc" ] || { echo "GATE3 SET SHA MISMATCH"; exit 1; }
[ "$(shasum -a 256 $G1 | cut -c1-16)" = "afabb8606870efe5" ] || { echo "CV GATE SET SHA MISMATCH"; exit 1; }
want_cut3="a67c70dbd194da82 949eee0355032eb1"
want_cvs="7bb693c83e7166fa 949eee0355032eb1"
for arm in $ARMS; do
  got=$(echo "cd <runner>/kiln/be-0cfd4a77-$arm && echo \"\$(cut -c1-16 PATCH_SHA256) \$(shasum -a 256 be-ship/adapter.ts | cut -c1-16)\"" | <on the mini> bash -s)
  w=want_$arm; [ "$got" = "${!w}" ] || { echo "TREE/RUNNER MISMATCH $arm: $got (want ${!w})"; exit 1; }; echo "tree ok $arm $got"
done
free=$(<on the mini> "df -g ~ | awk 'NR==2{print \$4}'"); echo "free before: $free GiB"
[ "$free" -ge 25 ] || { echo "DISK < 25 GiB"; exit 1; }
if ! <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1; then
  <on the mini> "bash -c 'cd $MD && shasum -a 256 -c SHA256SUMS >/dev/null && nohup <runner>/spikes/llama-b11010/build-cpu/bin/llama-server -m $MD/sonar-mmbert-small-emergency-v3b-q8te4.gguf --embeddings --pooling mean -np 1 -t 2 -c 512 -b 512 -ub 512 --host 127.0.0.1 --port 8094 > <runner>/kiln/detector-8094.log 2>&1 < /dev/null &'" & SSHP=$!
  for i in $(seq 1 60); do <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && break; sleep 2; done; kill $SSHP 2>/dev/null
fi
<on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && echo "detector up" || { echo "DETECTOR DOWN"; exit 1; }
for job in "cut3 gate3 cvs-gate3-cut3-s44" "cvs gate3 cvs-gate3-cvs-s44" "cvs cvgate cvs-oncvgate-s44"; do
  set -- $job; arm=$1; RID=$3; G=$G3; [ "$2" = cvgate ] && G=$G1; OUT=$E/runs/kiln/$RID; mkdir -p $OUT
  python3 - $E/runs/kiln/cut3-vgar-l1/cut2-v01-s44.requests.jsonl $G $OUT/requests.jsonl $RID $arm <<'PY'
import json, sys
tpl = json.loads(open(sys.argv[1]).readline()); rows = []
for src in sys.argv[2:3]:
    for l in open(src):
        if not l.strip(): continue
        it = json.loads(l)
        r = json.loads(json.dumps(tpl)); r["runId"] = sys.argv[4]; r["config"]["arm"] = sys.argv[5]
        r["item"] = {"id": it["id"], "question": it["question"], "lang": "en"}
        rows.append(r)
assert tpl["config"]["commit"] == "0cfd4a77" and tpl["seed"] == 44 and tpl["config"]["device"]["ramGb"] == 12.0
open(sys.argv[3], "w").write("".join(json.dumps(r) + "\n" for r in rows)); print("requests", len(rows))
PY
  env BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json \
    $E/adapters/desktop-node/run.sh --commit 0cfd4a77 --arm $arm --requests $OUT/requests.jsonl --out $OUT/traces.jsonl --places $PLACES ${IDS:+--ids $IDS} > $OUT/runsh.out 2>&1
  echo "$RID rc=$? $(date +%H:%M) $(tail -1 $OUT/runsh.out | cut -c1-120)"
  <on the mini> "rm -rf <runner>/kiln/be-0cfd4a77-$arm/be-ship/runs/$RID"
done
echo 'p=$(lsof -tiTCP:8094 -sTCP:LISTEN); [ -n "$p" ] && kill $p; echo detector stopped' | <on the mini> bash -s
echo "free after: $(<on the mini> "df -g ~ | awk 'NR==2{print \$4}'") GiB"
echo CVS-GATE-DONE

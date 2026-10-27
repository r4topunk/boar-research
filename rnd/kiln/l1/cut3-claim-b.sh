#!/usr/bin/env bash
# CLAIM RUN B: V-para (blind/V-para) for cut 3, per VPARA-BARS.md + RUN-MAPPING.md. Tree be-0cfd4a77-cut3, runner be-ship 949eee03, detector ON.
# (b) PRIMARY: all 58 items, android 12 GB 4B config (E3 config), --places kit-vexact (world places + region tiles as V-exact). (a) BARE: the 7 venue items, no places.
# Seeds 42/43. Judge judge.v1 on the 51 judged items via bench-shim (refs/refs.jsonl). Anchors haiku/sonnet/opus/fable (no web) on the 51, judged.
# Outputs only under blind/V-para/runs-cut3/. Nothing is printed except counts.
set -uo pipefail
B=<workspace>; E=$B/boar-eval; V=$B/blind/V-para; OUT=$V/runs-cut3; SHIM=$V/bench-shim
MD=<runner>/shared-models/emergency-detector; P=<runner>/shared-data/poi/kit-vexact
mkdir -p $OUT/anchors; export HEAVY_CLASS=normal BOAR_EVAL_RUNNER_DIR=be-ship
PLACES=$P/world-places.sqlite,$P/t-N52E013.sqlite,$P/t-N38W010.sqlite,$P/t-N35E139.sqlite,$P/t-N35E140.sqlite
got=$(echo 'cd <runner>/kiln/be-0cfd4a77-cut3 && echo "$(cut -c1-16 PATCH_SHA256) $(shasum -a 256 be-ship/adapter.ts | cut -c1-16)"' | <on the mini> bash -s)
[ "$got" = "a67c70dbd194da82 949eee0355032eb1" ] || { echo "TREE/RUNNER MISMATCH $got"; exit 1; }; echo "tree ok $got"
echo "items sha $(shasum -a 256 $V/items.jsonl | cut -c1-16) refs sha $(shasum -a 256 $V/refs/refs.jsonl | cut -c1-16) mapping sha $(shasum -a 256 $V/RUN-MAPPING.md | cut -c1-16)"
echo "free before: $(<on the mini> "df -g ~ | awk 'NR==2{print \$4}'") GiB"
if ! <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1; then
  <on the mini> "bash -c 'cd $MD && shasum -a 256 -c SHA256SUMS >/dev/null && nohup <runner>/spikes/llama-b11010/build-cpu/bin/llama-server -m $MD/sonar-mmbert-small-emergency-v3b-q8te4.gguf --embeddings --pooling mean -np 1 -t 2 -c 512 -b 512 -ub 512 --host 127.0.0.1 --port 8094 > <runner>/kiln/detector-8094.log 2>&1 < /dev/null &'" & SSHP=$!
  for i in $(seq 1 60); do <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && break; sleep 2; done; kill $SSHP 2>/dev/null
fi
<on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && echo "detector up" || { echo "DETECTOR DOWN"; exit 1; }
DET=(BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json)
python3 - "$V" "$OUT" <<'PY'
import json, sys
V, OUT = sys.argv[1:]
Q = [json.loads(l) for l in open(f"{V}/items.jsonl") if l.strip()]
ven = [q for q in Q if q.get("grading", {}).get("type") == "venue-list"]
open(f"{OUT}/venue7.questions.jsonl", "w").write("".join(json.dumps(q) + "\n" for q in ven))
open(f"{OUT}/judged.ids", "w").write("\n".join(q["id"] for q in Q if q not in ven) + "\n")
print(f"items {len(Q)} venue {len(ven)} judged {len(Q) - len(ven)}")
PY
run() { # seed mode(b|a)
  local seed=$1 mode=$2 label=cut3-vpara-s$1 q=$V/items.jsonl extra=(--places $PLACES)
  [ $mode = a ] && { label=cut3-vpara-s$seed-bare; q=$OUT/venue7.questions.jsonl; extra=(); }
  python3 -c "import json; c=json.load(open('$B/blind/bench-v02/runs-e3/e3-main-s42.config.json')); c['arm']='cut3'; c['seed']=$seed; json.dump(c, open('$OUT/$label.config.json','w'))"
  pnpm -s -C $E/packages/protocol exec tsx src/makeRequests.ts --questions $q --config $OUT/$label.config.json --run-id $label > $OUT/$label.requests.jsonl 2>/dev/null
  env "${DET[@]}" $E/adapters/desktop-node/run.sh --commit 0cfd4a77 --arm cut3 --requests $OUT/$label.requests.jsonl --out $OUT/$label.traces.jsonl ${extra[@]+"${extra[@]}"} > $OUT/$label.runsh.out 2>&1
  local rc=$?; <on the mini> "rm -rf <runner>/kiln/be-0cfd4a77-cut3/be-ship/runs/$label"
  python3 - "$OUT/$label.traces.jsonl" "$label rc=$rc" <<'PY'
import json, sys
T = [json.loads(l) for l in open(sys.argv[1])]
print(f"{sys.argv[2]} n={len(T)} errors={sum(bool(t.get('error')) for t in T)}")
PY
}
for seed in 42 43; do run $seed b; run $seed a; done
echo 'p=$(lsof -tiTCP:8094 -sTCP:LISTEN); [ -n "$p" ] && kill $p; echo detector stopped' | <on the mini> bash -s
echo "free after: $(<on the mini> "df -g ~ | awk 'NR==2{print \$4}'") GiB"
for seed in 42 43; do l=cut3-vpara-s$seed
  (cd $E && node harness/judge.mjs --traces $OUT/$l.traces.jsonl --out $OUT/$l.judgments.jsonl --bench $SHIM --system $l > $OUT/$l.judge.log 2>&1; echo "judge $l rc=$?") &
done
for m in haiku sonnet opus fable; do
  (cd $E && node harness/anchors.mjs --model $m --bench $SHIM --out $OUT/anchors/$m.traces.jsonl > $OUT/anchors/$m.anchors.log 2>&1; echo "anchor $m rc=$?"
   node harness/judge.mjs --traces $OUT/anchors/$m.traces.jsonl --out $OUT/anchors/$m.judgments.jsonl --bench $SHIM --system anchor-$m > $OUT/anchors/$m.judge.log 2>&1; echo "judge anchor $m rc=$?") &
done
wait; echo CUT3-B-RUNS-JUDGED

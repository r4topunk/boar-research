#!/usr/bin/env bash
# Sonar exp-33 L1 (rnd/research/sonar/exp/33-bigpack-l1/L1-criterion.md 9ed14be1…, frozen). Android 4B (and-qwen, 12 GB, kit A), s42.
# A = bounty1 2994a90b + kit A · B = bounty1 + kit A + boar-wiki-en-top100k (9123b372, fixed lead vectors) · C = bounty2 c2585211 + same.
# Runner be-h11 = health11-runner e4882a95 (91826313…); detector env ON (v3b, THR unset); --places = kit-vexact (gazetteer 215ce466
# + t-N52E013, t-N38W010, t-N35E139, t-N35E140) in all arms. Items: v0.1 public 60 (v01-en-ids.txt) + vx-001..005 (the other 6 V-exact
# ids are in v0.1, counted once) = 65 per arm. --event-source-text on all arms (Sonar 17:2x, for exp-34 goldhit L0; no criterion change). Judge: v0.1 part vs bench/v0.1; vx-001/002 vs bench-vslice (Compass refs).
set -uo pipefail
B=<workspace>; E=$B/boar-eval; S=$B/rnd/research/sonar/exp/33-bigpack-l1; X=$B/rnd/research/compass/exp/bounty-eval
OUT=$E/runs/kiln/bigpack-l1; MD=<runner>/shared-models/emergency-detector; P=<runner>/shared-data/poi/kit-vexact
mkdir -p $OUT; export HEAVY_CLASS=normal BOAR_EVAL_RUNNER_DIR=be-h11
PLACES=$P/world-places.sqlite,$P/t-N52E013.sqlite,$P/t-N38W010.sqlite,$P/t-N35E139.sqlite,$P/t-N35E140.sqlite
[ "$(shasum -a 256 $S/L1-criterion.md | cut -c1-16)" = 9ed14be17a32569e ] || { echo "CRITERION SHA MISMATCH"; exit 1; }
for a in bounty1 bounty2; do got=$(echo "cd <runner>/kiln/be-0cfd4a77-$a && echo \$(cut -c1-16 PATCH_SHA256) \$(shasum -a 256 be-h11/adapter.ts | cut -c1-16)" | <on the mini> bash -s); echo "$a $got"; done
if ! <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1; then
  <on the mini> "bash -c 'cd $MD && shasum -a 256 -c SHA256SUMS >/dev/null && nohup <runner>/spikes/llama-b11010/build-cpu/bin/llama-server -m $MD/sonar-mmbert-small-emergency-v3b-q8te4.gguf --embeddings --pooling mean -np 1 -t 2 -c 512 -b 512 -ub 512 --host 127.0.0.1 --port 8094 > <runner>/kiln/detector-8094.log 2>&1 < /dev/null &'" & SSHP=$!
  for i in $(seq 1 60); do <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && break; sleep 2; done; kill $SSHP 2>/dev/null
fi
<on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && echo "detector up" || { echo "DETECTOR DOWN"; exit 1; }
DET=(BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json)
for arm in A B C; do
  case $arm in A) tree=bounty1; big=0 ;; B) tree=bounty1; big=1 ;; C) tree=bounty2; big=1 ;; esac
  label=bigpack-$arm-s42
  # v0.1 60 (re-keyed and-qwen s42 requests) + vx-001..005 (makeRequests from bench-vslice, keeps GPS context), one request file
  python3 -c "import json; c=json.load(open('$E/runs/night-2026-10-01/and-qwen-s42.config.json')); c['arm']='$tree'; c['seed']=42
if $big: c['kit'] = c['kit'] + [{'id': 'boar-wiki-en-top100k', 'sha256': '9123b3720abd847291e2502d7529419ca86c1fc4cf111e9b449a2be06fc694e7'}]
json.dump(c, open('$OUT/$label.config.json','w'))"
  python3 -c "import json; [print(l.strip()) for l in open('$X/bench-vslice/questions.jsonl') if json.loads(l)['id'] in ('vx-001','vx-002','vx-003','vx-004','vx-005')]" > $OUT/vx5.questions.jsonl
  pnpm -s -C $E/packages/protocol exec tsx src/makeRequests.ts --questions $OUT/vx5.questions.jsonl --config $OUT/$label.config.json --run-id $label > $OUT/$label.vx.requests.jsonl 2>/dev/null
  python3 - "$E/runs/night-2026-10-01/and-qwen-s42.requests.jsonl" "$S/v01-en-ids.txt" "$OUT/$label.config.json" "$label" "$OUT/$label.vx.requests.jsonl" "$OUT/$label.requests.jsonl" <<'PY'
import json, sys
src, idsf, cfgf, label, vxf, out = sys.argv[1:]
keep = set(open(idsf).read().split()); cfg = json.load(open(cfgf))
rows = [json.loads(l) for l in open(src)]; rows = [r for r in rows if r["item"]["id"] in keep]
assert len(rows) == 60, len(rows)
for r in rows: r["runId"] = label; r["config"] = {**cfg, "seed": r["config"].get("seed", 42)}
rows += [json.loads(l) for l in open(vxf)]
assert len(rows) == 65, len(rows)
open(out, "w").write("".join(json.dumps(r) + "\n" for r in rows))
PY
  env "${DET[@]}" $E/adapters/desktop-node/run.sh --commit 0cfd4a77 --arm $tree --requests $OUT/$label.requests.jsonl --out $OUT/$label.traces.jsonl --places $PLACES --event-source-text > $OUT/$label.runsh.out 2>&1
  echo "$label rc=$? $(date +%H:%M) $(tail -1 $OUT/$label.runsh.out | cut -c1-120)"
  <on the mini> "rm -rf <runner>/kiln/be-0cfd4a77-$tree/be-h11/runs/$label"
  python3 - "$OUT/$label.traces.jsonl" "$S/v01-en-ids.txt" "$OUT/$label" <<'PY'
import json, sys
T = [json.loads(l) for l in open(sys.argv[1])]; keep = set(open(sys.argv[2]).read().split()); base = sys.argv[3]
open(base + ".v01.traces.jsonl", "w").write("".join(json.dumps(t) + "\n" for t in T if t["itemId"] in keep))
open(base + ".vx.traces.jsonl", "w").write("".join(json.dumps(t) + "\n" for t in T if t["itemId"] in ("vx-001", "vx-002")))
via = [c for t in T for c in t["route"]["reasonCodes"] if "top100k" in c or c.startswith("via=") or "via:" in c]
print(f"  split: v01 {sum(t['itemId'] in keep for t in T)}, vx judged 2; errors {sum(bool(t.get('error')) for t in T)}; top100k/via codes {len(via)}")
PY
  (cd $E && node harness/judge.mjs --traces $OUT/$label.v01.traces.jsonl --out $OUT/$label.v01.judgments.jsonl --bench bench/v0.1 --system $label > $OUT/$label.v01.judge.log 2>&1; echo "judge $label v01 rc=$?") &
  (cd $E && node harness/judge.mjs --traces $OUT/$label.vx.traces.jsonl --out $OUT/$label.vx.judgments.jsonl --bench $X/bench-vslice --system $label > $OUT/$label.vx.judge.log 2>&1; echo "judge $label vx rc=$?") &
done
wait; echo 'p=$(lsof -tiTCP:8094 -sTCP:LISTEN); [ -n "$p" ] && kill $p; echo detector stopped' | <on the mini> bash -s
echo BIGPACK-L1-DONE

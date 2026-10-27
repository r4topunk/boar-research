#!/usr/bin/env bash
# Forge ship-speed landing checks on wt/forge-ship ccc7688b (= 0cfd4a77 + b6-on-health12final 68f9868d + forge arms
# 914086dc + ship defaults). rnd/research/forge/SHIP-SPEED.md checklist 1 + 2. Interleaves with Anvil's sweep via the heavy lock.
# (1) Desktop identity: tree be-ccc7688b, runner be-ship (949eee03 = bb05e07b + runner-b4gate + health11-runner), detector ON
#     (ship design: v3b on llama-server b11010 CPU), p8 v0.1 72 requests re-keyed, --event-source-text, BOAR_EVAL_SQL_COUNT=1;
#     default flags vs EXPO_PUBLIC_BOAR_PERF=none; compare sources(+passage text)/raw/kept/route/answer + SQL calls/q.
# (2) Android arm64 APKs (debug + release) of ccc7688b with the forge-build recipe; then prune ~/.gradle/caches if free < 25 GiB.
set -uo pipefail
B=<workspace>; E=$B/boar-eval; OUT=$E/runs/kiln/forge-ship; MD=<runner>/shared-models/emergency-detector
mkdir -p $OUT; export HEAVY_CLASS=normal BOAR_EVAL_RUNNER_DIR=be-ship BOAR_EVAL_SQL_COUNT=1
PA=<scratch>
# ---- (1) desktop identity
(cd $E && adapters/desktop-node/setup.sh ccc7688b 2>&1 | tail -1)
scp -q $PA MINI_HOST:boar/kiln/be-ccc7688b/be-ship/adapter.ts
got=$(echo 'cd <runner>/kiln/be-ccc7688b && echo "$(cut -c1-8 COMMIT) $(shasum -a 256 be-ship/adapter.ts | cut -c1-16)"' | <on the mini> bash -s)
[ "$got" = "ccc7688b 949eee0355032eb1" ] || { echo "TREE/RUNNER MISMATCH $got"; exit 1; }
echo "tree ok: $got"
<on the mini> "bash -c 'cd $MD && shasum -a 256 -c SHA256SUMS >/dev/null && nohup <runner>/spikes/llama-b11010/build-cpu/bin/llama-server -m $MD/sonar-mmbert-small-emergency-v3b-q8te4.gguf --embeddings --pooling mean -np 1 -t 2 -c 512 -b 512 -ub 512 --host 127.0.0.1 --port 8094 > <runner>/kiln/detector-8094.log 2>&1 < /dev/null &'" &
SSHP=$!; for i in $(seq 1 60); do <on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && break; sleep 2; done; kill $SSHP 2>/dev/null
<on the mini> "curl -sf http://127.0.0.1:8094/health" >/dev/null 2>&1 && echo "detector up" || { echo "DETECTOR DOWN"; exit 1; }
DET=(BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json)
for side in default none; do
  python3 - "$E/runs/p8/base-s42-kic.requests.jsonl" "$OUT/$side.requests.jsonl" "kiln-forgeship-$side" <<'PY'
import json, sys
rows = [json.loads(l) for l in open(sys.argv[1])]
for r in rows: r["runId"] = sys.argv[3]; r["config"]["arm"] = "main"; r["config"]["commit"] = "ccc7688b"
open(sys.argv[2], "w").write("".join(json.dumps(r) + "\n" for r in rows))
PY
  if [ $side = none ]; then PERF=(EXPO_PUBLIC_BOAR_PERF=none); else PERF=(); fi
  env "${DET[@]}" ${PERF[@]+"${PERF[@]}"} $E/adapters/desktop-node/run.sh --commit ccc7688b --requests $OUT/$side.requests.jsonl --out $OUT/$side.traces.jsonl --event-source-text > $OUT/$side.runsh.out 2>&1
  echo "identity $side rc=$? $(date +%H:%M)"
  <on the mini> "rm -rf <runner>/kiln/be-ccc7688b/be-ship/runs/kiln-forgeship-$side"
done
echo 'p=$(lsof -tiTCP:8094 -sTCP:LISTEN); [ -n "$p" ] && kill $p; echo detector stopped' | <on the mini> bash -s
python3 - $OUT <<'PY'
import json, statistics, sys
D = sys.argv[1]; L = lambda n: {json.loads(l)["itemId"]: json.loads(l) for l in open(f"{D}/{n}.traces.jsonl")}
def pre(t):
    out = []
    for e in t["events"]:
        if e["type"] == "token": break
        if e["type"] == "sources": out.append(json.dumps(e.get("sources"), sort_keys=True))
    return out
def sql(t): return next((e["total"] for e in t["events"] if e.get("kind") == "sql-calls"), None)
F = {"sources+text": pre, "raw": lambda t: json.dumps((t.get("retrieval") or {}).get("raw"), sort_keys=True),
     "kept": lambda t: json.dumps((t.get("retrieval") or {}).get("kept"), sort_keys=True),
     "route": lambda t: json.dumps(t["route"], sort_keys=True), "answer": lambda t: t["answer"]["text"]}
a, b = L("default"), L("none"); ids = [i for i in a if i in b]
print(f"items default {len(a)} none {len(b)}; errors default {sum(bool(t.get('error')) for t in a.values())} none {sum(bool(t.get('error')) for t in b.values())}")
for k, f in F.items():
    diff = [i for i in ids if f(a[i]) != f(b[i])]; print(f"  {k}: identical {len(ids) - len(diff)}/{len(ids)} {diff[:10]}")
for n, T in (("default", a), ("none", b)):
    s = [sql(t) for t in T.values() if sql(t) is not None]; print(f"  sql calls/q median {n}: {statistics.median(s) if s else 'n/a'} (n={len(s)})")
PY
# ---- (2) APKs: refresh <runner>/android/forge-build src/ + modules/ to ccc7688b (no package.json/app.json change since the forge arms)
T=$(mktemp -d); git -C $B/boar-app archive ccc7688b src modules | tar -x -C $T
rsync -a --delete $T/src/ MINI_HOST:boar/android/forge-build/src/ && rsync -a --delete $T/modules/ MINI_HOST:boar/android/forge-build/modules/ && rm -rf $T
echo ccc7688b | <on the mini> 'cat > <runner>/android/forge-build/COMMIT'
sed -e 's/boar-0cfd4a77-forge-/boar-ccc7688b-forgeship-/g' $B/rnd/kiln/recipes/forge-build.sh > <scratch>
scp -q <scratch> MINI_HOST:boar/android/forge-build-ccc.sh
<on the mini> "bash -lc 'HEAVY_CLASS=normal <runner>/bin/run-heavy Kiln bash <runner>/android/forge-build-ccc.sh'" > $OUT/apk-build.log 2>&1
echo "apk build rc=$? $(date +%H:%M)"; grep -E "^\[forge\]|^[0-9a-f]{64}" $OUT/apk-build.log | tail -20
echo 'for v in debug release; do A=<runner>/android/apk/boar-ccc7688b-forgeship-$v-arm64.apk; [ -f $A ] || continue; d=$(mktemp -d); unzip -q -o $A lib/arm64-v8a/libboarzstd.so -d $d && echo "$v exports: $(~/Library/Android/sdk/ndk/27.1.12297006/toolchains/llvm/prebuilt/darwin-x86_64/bin/llvm-nm -D --defined-only $d/lib/arm64-v8a/libboarzstd.so 2>/dev/null | awk "{print \$3}" | grep -v "^_" | tr "\n" " ")"; rm -rf $d; done; df -g ~ | tail -1 | awk "{print \"free\", \$4, \"GiB\"}"' | <on the mini> bash -s
# ---- gradle prune (coordinator: right after the APKs, only if free < 25 GiB)
free=$(<on the mini> "df -g ~ | tail -1 | awk '{print \$4}'")
if [ "$free" -lt 25 ]; then sz=$(<on the mini> "du -sh ~/.gradle/caches | cut -f1"); <on the mini> "rm -rf ~/.gradle/caches"; echo "gradle caches pruned ($sz), free now $(<on the mini> "df -g ~ | tail -1 | awk '{print \$4}'") GiB"; echo "GRADLE-PRUNED $sz"; else echo "free $free GiB >= 25, gradle kept"; fi
echo FORGE-SHIP-DONE

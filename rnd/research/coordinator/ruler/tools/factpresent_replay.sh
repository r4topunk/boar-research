#!/bin/bash
# FACTPRESENT replay on the MacBook (0 generation, 0 judge): stub llama-server + the real LITEPACKS adapter (be/adapter-litedecline.ts,
# LITEDECLINE_OFF=5) on a clone of kiln-local/be-0cfd4a77-cut7-litepacks patched by the RETFLOOR apply_retfloor.py, RETFLOOR_VARIANT=base
# (= LITEPACKS behaviour, logs retfloor:kept chunk ids). Env as LITEPACKS run_lp.sh. Detector mmbert v3b on :8094 started here if down
# (left running). Job dir: req/<K>-V01|CM|ST.requests.jsonl = LITEPACKS runs/req lp-<K>-v01|cm|st-s42 copies; apply_retfloor.py + stub_server.py from the mini <runner>/kiln/retfloor (RETFLOOR job). Usage: bash mac_fp.sh <job dir with req/, apply_retfloor.py, stub_server.py>
set -u
J=$1; B=<workspace>; MD=$B/shared-models/emergency-detector; SRV=$B/spikes/llama-b11010-cpu/bin/llama-server
if ! curl -sf http://127.0.0.1:8094/health >/dev/null; then
  (cd $MD && shasum -a 256 -c SHA256SUMS >/dev/null) || { echo "FAIL detector sha"; exit 1; }
  export DYLD_LIBRARY_PATH=$(dirname $SRV); $SRV -m $MD/sonar-mmbert-small-emergency-v3b-q8te4.gguf --embeddings --pooling mean -np 1 -t 2 -c 512 -b 512 -ub 512 --host 127.0.0.1 --port 8094 > $J/detector-8094.log 2>&1 < /dev/null &
  for i in $(seq 1 60); do curl -sf http://127.0.0.1:8094/health >/dev/null && break; sleep 1; done
fi
curl -sf http://127.0.0.1:8094/health >/dev/null || { echo "FAIL detector"; exit 1; }
T=$J/be-0cfd4a77-cut7-litepacks-retfloor-fp
if [ ! -d $T ]; then cp -c -R $B/kiln-local/be-0cfd4a77-cut7-litepacks $T && rm -rf $T/be/.cache && python3 -I $J/apply_retfloor.py $T || { echo "FAIL tree"; exit 1; }; fi
cd $T || exit 1
echo "tree answer.ts=$(shasum -a 256 src/routing/answer.ts | cut -c1-16) orig=$(shasum -a 256 $B/kiln-local/be-0cfd4a77-cut7-litepacks/src/routing/answer.ts | cut -c1-16) adapter=$(shasum -a 256 be/adapter-litedecline.ts | cut -c1-16)"
PORT=18777; python3 -I $J/stub_server.py $PORT $B/shared-models/lite/Qwen3-1.7B-Q4_K_M.gguf & STUB=$!; trap 'kill $STUB 2>/dev/null' EXIT; sleep 1
export BOAR_EVAL_PACK_DIRS=$B/shared-data/packs/v3proto:$B/shared-data/packs/wave3:$B/shared-data/packs/wave2:$B/shared-data/packs/wave1:$B/shared-data/packs:$B/shared-data/crypto
export BOAR_SHARED_MODELS=$B/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 \
  BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal BOAR_SERVER_EXTRA_ARGS="--reasoning off" LITEDECLINE_OFF=5
mkdir -p $J/out
for SET in $(cd $J/req && ls *.requests.jsonl | sed "s/.requests.jsonl//"); do
  O=$J/out/$SET; [ -s $O.traces.jsonl ] && [ "$(wc -l < $O.traces.jsonl)" = "$(wc -l < $J/req/$SET.requests.jsonl)" ] && continue
  rm -f $O.traces.jsonl $O.prompts.jsonl; t0=$(date +%s)
  RETFLOOR_VARIANT=base be/node_modules/tsx/dist/cli.mjs be/adapter-litedecline.ts --requests $J/req/$SET.requests.jsonl --out $O.traces.jsonl \
    --backend server --server-bin $SRV --server-url http://127.0.0.1:$PORT --dump-prompts $O.prompts.jsonl --threads 4 --timeout-ms 600000 > $O.log 2>&1
  echo "$SET rc=$? rows=$(wc -l < $O.traces.jsonl | tr -d ' ') $(( $(date +%s) - t0 ))s"
done
echo DONE

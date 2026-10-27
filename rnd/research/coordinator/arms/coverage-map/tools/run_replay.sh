#!/bin/bash
# COVERAGE-MAP K-FULL funnel replay (0 LLM, MacBook): MAIN 97, LITEPACKS tree, K3 settings {packHeadPass a2, packDense2 append-budget},
# gate + detector from the RAG-FUNNEL K3 traces. Tool = retrieve-sweep/tools/replay-sweep.ts (unchanged). usage: run_replay.sh <label> <pack csv>
B=<workspace>; R=$B/rnd/research/coordinator/arms; C=$R/coverage-map
export BOAR_REPLAY_CACHE=$B/boar-eval/runs/replay-cache
cd $B; t0=$(date +%s)
$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx $R/retrieve-sweep/tools/replay-sweep.ts \
  --questions $R/decode-ground/runs/req/dg-S-K1-main-s42.requests.jsonl --tree $B/kiln-local/be-0cfd4a77-cut7-litepacks \
  --packs $2 --tasks-from $C/replay/funnel-K3.traces.jsonl --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 12 \
  --forward-opts --settings-json '{"packHeadPass":"a2","packDense2":"append-budget"}' --out $C/replay/main.$1.jsonl 2> $C/replay/main.$1.err
echo "$1 rc=$? $(( $(date +%s) - t0 ))s $(tail -1 $C/replay/main.$1.err)"

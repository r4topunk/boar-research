#!/bin/bash
# harness check: the 6-pack K3 file kit, stock, through run_compose's recipe -> must equal coverage-map/replay/main.K3.jsonl (kept lists)
B=<workspace>; R=$B/rnd/research/coordinator/arms; C=$R/coverage-map; D=$C/compose
export BOAR_REPLAY_CACHE=$B/boar-eval/runs/replay-cache; unset RS_MERGE; cd $B
$B/boar-eval/adapters/desktop-node/node_modules/.bin/tsx $R/retrieve-sweep/tools/replay-sweep.ts --questions $R/decode-ground/runs/req/dg-S-K1-main-s42.requests.jsonl --tree $B/kiln-local/rs-H4 --packs $(cat $C/replay/kit.K3.txt) \
  --tasks-from $C/replay/funnel-K3.traces.jsonl --model qwen3-1.7b-q4km --ram-gb 12 --cpu-embed --wide 12 --forward-opts --settings-json '{"packHeadPass":"a2","packDense2":"append-budget"}' --out $D/replays/sanity.K3.stock.jsonl 2> $D/replays/sanity.K3.stock.jsonl.err
echo done

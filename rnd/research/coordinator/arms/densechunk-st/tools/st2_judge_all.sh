#!/bin/bash
# DENSECHUNK-ST2 stage 2: per pack, once its ON generation is DONE: gen checks (selftest_agg.py) -> Haiku 5.5-low N=4 both orders
# (deepthink shard_judge.sh, 40 calls) -> floor_metrics.py. Pipelined behind st2_gen_all.sh (polls the status files). Resumable.
set -u
H=<workspace>/rnd/research/coordinator/arms; G=$H/densechunk-st/runs/gen; J=$H/densechunk-st/runs/judge; A=$H/densechunk-st/aggregates
for p in ${*:-qa-health-se qa-travel-se qa-ethereum-se qa-bitcoin-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en boar-factbook boar-simplewiki-en}; do
  n=st2-$p-cut7-s42
  until grep -q '^DONE\|^FAIL' $G/$n.traces.status 2>/dev/null; do sleep 30; done
  grep -q '^DONE' $G/$n.traces.status || { echo "$p gen FAILED, skip"; continue; }
  [ -e $J/$n.traces.jsonl ] || ln -s $G/$n.traces.jsonl $J/$n.traces.jsonl
  python3 -I $H/packs/tools/selftest_agg.py $p $G/$n.traces.jsonl --json $A/$n.gen.json | tail -1 | cut -c1-300
  python3 -I -c "import json,sys;[print(json.loads(l)['itemId']) for l in open(sys.argv[1])]" $G/$n.traces.jsonl > $J/$n.ids
  if [ "$(wc -l < $J/$n.judgments.jsonl 2>/dev/null || echo 0)" -lt 40 ] || [ -s $J/$n.judgments.missing ]; then
    bash $H/deepthink/tools/shard_judge.sh $J/$n.traces.jsonl $J/$n.judgments.jsonl <workspace>/boar-eval/bench/selftest/$p $J/$n.ids selftest-$p-cut7-dense2 4 haiku; echo "$p judge rc=$?"
  fi
  python3 <workspace>/boar-eval/bench/v0.2/plan/floor_metrics.py --runs $n --dir $J --ids $J/$n.ids --strict > $A/$n.floor_metrics.txt 2>&1; echo "$p floor rc=$? $(grep -A1 '"raw"' $A/$n.floor_metrics.txt | tr -d ' \n')"
done; echo JUDGE-ALL-DONE

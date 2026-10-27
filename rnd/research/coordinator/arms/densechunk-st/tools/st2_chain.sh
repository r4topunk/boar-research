#!/bin/bash
# DENSECHUNK-ST2 stages 1-3, one resumable chain (nohup-safe): ON generation for the 9 packs (st2_gen_all.sh, skips DONE packs)
# in parallel with the pipelined Haiku judge (st2_judge_all.sh, waits per pack, skips judged packs), then the paired metrics.
# Rerun the same command to resume.  Log: runs/chain.log; final numbers: aggregates/st2-stage2.json
D=<workspace>/rnd/research/coordinator/arms/densechunk-st
echo "chain start $(date '+%F %T')"
$D/tools/st2_gen_all.sh >> $D/runs/gen/gen_all.log 2>&1 &
G=$!
$D/tools/st2_judge_all.sh >> $D/runs/judge/judge_all.log 2>&1
wait $G
python3 -I $D/tools/st2_agg.py > $D/aggregates/st2-stage2.json && echo "AGG-DONE $(python3 -c "import json;d=json.load(open('$D/aggregates/st2-stage2.json'));print(d.get('verdict'), d.get('pooled',{}).get('ON_minus_OFF'))")"
echo "chain end $(date '+%F %T')"

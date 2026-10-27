#!/bin/bash
# RD2 judge (MacBook): Haiku 5.5-low judge.v1 N 4 both orders on the items whose answer text differs from F1b (targets first, then id order; cap 100 calls) via compose/screen/tools/judge_cmp.sh.
# Usage: judge_rd2.sh RUN [CAP_CALLS]
set -u
RUN=$1; CAP=${2:-100}
C=<workspace>/rnd/research/coordinator/arms/coverage-map; D=$C/reader/judge/$RUN; mkdir -p $D
python3 -I - "$C" "$RUN" "$CAP" > $D/changed.ids <<'Y'
import json, sys
C, RUN, CAP = sys.argv[1], sys.argv[2], int(sys.argv[3])
ld = lambda p: {json.loads(l)["itemId"]: json.loads(l)["answer"]["text"] for l in open(p)}
T = ld(f"{C}/reader/traces/{RUN}.traces.jsonl"); F = ld(f"{C}/sefix/ans-traces/f1b-main-s42.traces.jsonl")
tg = ["st-qa-money-se-003", "vit-cry-001", "lan-cmp-004", "lan-exp-002", "st-qa-cooking-se-012"]
ids = sorted(i for i in T if T[i] != F[i]); ids = [i for i in tg if i in ids] + [i for i in ids if i not in tg]
left = ids[CAP // 2:]
if left: print("LEFT_UNJUDGED " + " ".join(left), file=sys.stderr)
print("\n".join(ids[:CAP // 2]))
Y
echo "changed vs F1b: $(wc -l < $D/changed.ids)"; [ -s $D/changed.ids ] || { echo "none changed"; exit 0; }
bash $C/compose/screen/tools/judge_cmp.sh $C/reader/traces/$RUN.traces.jsonl $D/changed.ids $D $RUN

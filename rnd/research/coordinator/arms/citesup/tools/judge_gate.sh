#!/bin/bash
# CITESUP criterion steps 6-7: judge only candidate answers whose text differs from the original min3v trace (and from the 1.7B control), reuse the
# original min3v judgments for the rest, aggregate (agg_run.py --control) and gate (screen_gate_v2.py). Usage: judge_gate.sh <K0|K1>   env JUDGE_N (4)
set -u
K=$1; A=<workspace>/rnd/research/coordinator/arms; C=$A/citesup; NC=$A/null-cal; TL=$A/lp-screens/tools; L=$A/_lib; SJ=$A/deepthink/tools/shard_judge.sh
BE=<workspace>/boar-eval/bench; LP=$A/litepacks; IDS=$NC/pool/screen2-$K.ids; CTL=$NC/control/pool-$K.json; CRIT=$C/CITESUP-criterion.md
RUN=citesupm3v-$K-screen2-$K-s42; D=$C/runs/citesupm3v; TR=$D/traces/$RUN.traces.jsonl
O0=$A/ministral3-3b/screen/min3v; OR=min3v-$K-screen2-$K-s42; OTR=$O0/traces/$OR.traces.jsonl
[ -s $TR ] || { echo "no candidate traces $TR"; exit 1; }
mkdir -p $D/judgments $D/aggregates $D/runs/logs
CH=$D/judgments/$RUN.changed.ids
python3 -I - $TR $OTR $CTL $CH <<'PY' || exit 1
import json, sys
tr, otr, ctl, out = sys.argv[1:]
N = {json.loads(l)["itemId"]: json.loads(l)["answer"]["text"] for l in open(tr)}; O = {json.loads(l)["itemId"]: json.loads(l)["answer"]["text"] for l in open(otr)}
C = json.load(open(ctl))["items"]
ch = [i for i in N if N[i] != O[i] and N[i] != C[i]["text"]]
open(out, "w").write("".join(i + "\n" for i in ch)); print(f"changed vs min3v {sum(N[i] != O[i] for i in N)}, to judge {len(ch)}")
PY
CALLS=0
for u in v01 qa-cooking-se qa-money-se qa-travel-se qa-ethereum-se qa-bitcoin-se qa-health-se qa-outdoors-se boar-firstaid-en boar-medlineplus-en boar-factbook boar-simplewiki-en; do
  case $u in v01) B=$BE/v0.1; PS=v01; SEL="grep -Fx -f $LP/data/v01-57.ids";; qa-cooking-se|qa-money-se) B=$BE/selftest/$u; PS=st-$u; SEL="grep ^st-$u-";; *) B=$BE/selftest/$u; PS=selftest-180; SEL="grep ^st-$u-";; esac
  # reuse: original min3v rows of ids NOT in the changed list
  OJ=$O0/judgments/$OR-$u.judgments.jsonl
  [ -s $OJ ] && python3 -I -c "import json,sys;ch=set(open(sys.argv[2]).read().split());[sys.stdout.write(l) for l in open(sys.argv[1]) if l.strip() and json.loads(l)['queryId'] not in ch]" $OJ $CH > $D/judgments/$RUN-orig-$u.judgments.jsonl
  I=$D/judgments/$RUN-$u.jids; $SEL $CH > $I || true; m=$(wc -l < $I | tr -d ' ')
  [ "$m" = 0 ] && { rm -f $I; continue; }
  O=$D/judgments/$RUN-$u.judgments.jsonl
  if python3 -I $L/check_judgments.py $O $I > /dev/null 2>&1; then echo "judged already $u ($m)"; continue; fi
  SYS=citesup-m3v-$K-$u-haiku55-low
  env PREFLIGHT_PROBE_IDS=0 PREFLIGHT_SET=$PS PREFLIGHT_DECLARED_CALLS=$((2*m)) PREFLIGHT_CRITERION=$CRIT bash $SJ --preflight $TR $O $B $I $SYS ${JUDGE_N:-4} haiku > /dev/null || { echo "PREFLIGHT FAIL $u"; exit 8; }
  t=$(date +%s); bash $SJ $TR $O $B $I $SYS ${JUDGE_N:-4} haiku > $D/runs/logs/$RUN-$u.judge.log 2>&1 || { echo "judge FAIL $u"; exit 1; }
  python3 -I $L/check_judgments.py $O $I "$RUN-$u" || exit 1
  CALLS=$((CALLS + 2*m)); echo "$(date '+%F %T') $u ids=$m calls=$((2*m)) wall=$(( $(date +%s) - t ))s" >> $D/runs/logs/$RUN.calls; echo "judged $u ids=$m"
done
AG=$D/aggregates/$RUN.json
python3 -I $TL/agg_run.py $TR $IDS $AG "$D/judgments/$RUN-*.judgments.jsonl" --control $CTL || exit 1
python3 -I $NC/tools/screen_gate_v2.py $AG $CTL $NC/pool/screen2-$K.json --json $D/aggregates/$RUN.gate2.json | tee $D/aggregates/$RUN.gate2.txt
echo "calls this invocation $CALLS"

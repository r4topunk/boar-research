#!/usr/bin/env bash
# Sonar's health5 L2 (criterion rnd/research/sonar/exp/29-instant-offtopic/L2-criterion.md, sha256 59803cc1…dcab).
# v0.1 questions72, per profile ctl-s42, arm-s42, ctl-s43, arm-s43 back to back; node backend; judge.v1 opus both orders:
# control in full, arm on the items whose answer text differs from the same-seed control (declared shortcut).
set -uo pipefail
E=<workspace>/boar-eval; OUT=$E/runs/kiln/health5
export BOAR_EVAL_RUNNER_DIR=be-kiln HEAVY_CLASS=normal
declare -a J=()
mkreq() { # cfg arm seed runId out
  python3 - "$@" <<'PY'
import json, sys
cfg, arm, seed, run, out = sys.argv[1:]
c = json.load(open(cfg)); c.pop("seed", None); c["arm"] = arm
items = [json.loads(l)["item"] for l in open("<workspace>/boar-eval/runs/night-2026-10-01/and-qwen-s42.requests.jsonl")]
rows = [{"protocol": "1.0.0", "runId": run, "item": it, "config": c, "seed": int(seed)} for it in items]
open(out, "w").write("".join(json.dumps(r) + "\n" for r in rows))
PY
}
for prof in and ios; do
  [ $prof = and ] && CFG=$E/runs/night-2026-10-01/and-qwen-s42.config.json || CFG=$E/adapters/desktop-node/configs/p2-iphone13-0cfd4a77.json
  d=$OUT/$prof; mkdir -p $d
  for seed in 42 43; do
    for side in ctl arm; do
      label=$side-s$seed; [ $side = ctl ] && arm=main || arm=health5
      mkreq $CFG $arm $seed kiln-health5-$prof-$label $d/$label.requests.jsonl
      $E/adapters/desktop-node/run.sh --commit 0cfd4a77 --arm $arm --requests $d/$label.requests.jsonl --out $d/$label.traces.jsonl > $d/$label.runsh.out 2>&1
      echo "$prof $label rc=$? $(date +%H:%M)"
      if [ $side = ctl ]; then
        (cd $E && node harness/judge.mjs --traces $d/$label.traces.jsonl --out $d/$label.judgments.jsonl --bench bench/v0.1 --system health5-$prof-$label > $d/$label.judge.log 2>&1; echo "judge $prof $label rc=$? $(date +%H:%M)") & J+=($!)
      else
        ids=$(python3 -c "
import json
L=lambda p:{json.loads(l)['itemId']:json.loads(l)['answer']['text'] for l in open(p)}
c=L('$d/ctl-s$seed.traces.jsonl'); a=L('$d/arm-s$seed.traces.jsonl')
print(','.join(i for i in a if a[i]!=c.get(i)))")
        echo "$ids" > $d/$label.changed-ids.txt; echo "$prof $label changed: $(echo $ids | tr ',' '\n' | grep -c .)"
        if [ -n "$ids" ]; then (cd $E && node harness/judge.mjs --traces $d/$label.traces.jsonl --out $d/$label.judgments.changed.jsonl --bench bench/v0.1 --ids "$ids" --system health5-$prof-$label > $d/$label.judge.log 2>&1; echo "judge $prof $label rc=$? $(date +%H:%M)") & J+=($!); fi
      fi
    done
  done
done
for p in "${J[@]}"; do wait $p; done
echo HEALTH3-L2-RUNS-JUDGED

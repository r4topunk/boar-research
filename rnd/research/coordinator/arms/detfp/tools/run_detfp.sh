#!/bin/bash
# DETFP route replay (0 LLM, stub model, detector :8094 live). Requests = cut6-v02-s42 claim requests (claim kit, seed 42), runId/arm/commit relabelled per tree.
# Cells: c7 (kiln-local/be-0cfd4a77-cut7, be/replay-stub.ts from healthgap/tools/mk_replay_stub.py, no flags);
# pr (be-cut7-warn, replay-stub-litesafety.ts pin 496fc340, HEALTHGAP=1 NUMGUARD=1, WARN unset); prng (be-cut7-warn, replay-stub.ts, HEALTHGAP=1, WARN/NUMGUARD unset).
# Outputs (hold question text) go to the scratch dir $1, never to git. Usage: run_detfp.sh <scratch dir>
set -u
SP=$1; K=<workspace>/kiln-local; MD=<workspace>/shared-models/emergency-detector; H=<workspace>/rnd/research/coordinator/arms/healthgap
curl -sf http://127.0.0.1:8094/health >/dev/null || { echo "FAIL detector down"; exit 1; }
python3 -I -c "
import json
with open('$SP/req.jsonl','w') as o:
  for l in open('<private held-out dir>'):
    d=json.loads(l); d['runId']='detfp-v02'; o.write(json.dumps(d,ensure_ascii=False)+'\n')
print('requests ok')"
for a in cut7:0cfd4a77 pr1+warn:8ac9eb7a; do python3 -I -c "
import json,sys
arm,c=sys.argv[1].split(':')
with open(sys.argv[2],'w') as o:
  for l in open(sys.argv[3]):
    d=json.loads(l); d['config']['arm']=arm; d['config']['commit']=c; o.write(json.dumps(d,ensure_ascii=False)+'\n')" $a $SP/req.${a%%:*}.jsonl $SP/req.jsonl; done
export BOAR_EVAL_PACK_DIRS=<workspace>/shared-data/packs/wave2:<workspace>/shared-data/packs/wave1:<workspace>/shared-data/packs:<workspace>/shared-data/crypto BOAR_SHARED_MODELS=<workspace>/shared-models BOAR_RUNNER_PROFILE=ship BOAR_DETECTOR=mmbert BOAR_DETECTOR_URL=http://127.0.0.1:8094 BOAR_DETECTOR_HEAD=$MD/sonar-mmbert-small-emergency-v3b.head.json HEAVY_CLASS=normal
unset WARN HEALTHGAP NUMGUARD
[ -f $K/be-0cfd4a77-cut7/be/replay-stub.ts ] || python3 -I $H/tools/mk_replay_stub.py $K/be-0cfd4a77-cut7 || exit 1
(cd $K/be-0cfd4a77-cut7 && [ "$(cat ARM)" = cut7 ] && be/node_modules/tsx/dist/cli.mjs be/replay-stub.ts --requests $SP/req.cut7.jsonl --out $SP/c7.traces.jsonl > $SP/c7.log 2>&1) || { echo FAIL c7; exit 1; }
cd $K/be-cut7-warn && [ "$(cat ARM)" = pr1+warn ] && [ "$(shasum -a 256 be/replay-stub-litesafety.ts | cut -c1-16)" = 496fc3402e18f446 ] || { echo FAIL pr pins; exit 1; }
HEALTHGAP=1 NUMGUARD=1 be/node_modules/tsx/dist/cli.mjs be/replay-stub-litesafety.ts --requests $SP/req.pr1+warn.jsonl --out $SP/pr.traces.jsonl > $SP/pr.log 2>&1 || { echo FAIL pr; exit 1; }
HEALTHGAP=1 be/node_modules/tsx/dist/cli.mjs be/replay-stub.ts --requests $SP/req.pr1+warn.jsonl --out $SP/prng.traces.jsonl > $SP/prng.log 2>&1 || { echo FAIL prng; exit 1; }
echo DONE

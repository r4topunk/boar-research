#!/usr/bin/env bash
# CVO L1: judge ONLY the items whose answer text differs from cut 3 (judge.v1-med, both orders), run from the MacBook. Skips the judge when nothing changed.
cd <workspace>/boar-eval; O=runs/kiln/cvo-l1; D=runs/kiln/cut3-confirm
for s in 44 45; do
  ids=$(python3 - $D/cut3-v01-s$s.traces.jsonl $O/cvo-v01-s$s.traces.jsonl <<'PY'
import json, sys
t = lambda p: {r["itemId"]: r["answer"]["text"] for r in (json.loads(l) for l in open(p) if l.strip())}
a, b = t(sys.argv[1]), t(sys.argv[2])
print(",".join(sorted(i for i in b if a.get(i) != b[i])))
PY
)
  echo "s$s changed: ${ids:-none}"
  [ -z "$ids" ] && continue
  node harness/judge.mjs --traces $O/cvo-v01-s$s.traces.jsonl --out $O/cvo-v01-s$s.judgments.v1-med.jsonl --bench bench/v0.1 --system cvo-l1-s$s --effort medium --ids $ids > $O/cvo-v01-s$s.judge.log 2>&1; echo "judge s$s rc=$?"
done

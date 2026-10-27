cd <workspace>/boar-eval
D=runs/kiln/speedpack-l1
for s in 44 45; do
  node harness/judge.mjs --bench bench/v0.1 --traces $D/spsp-v01-s$s.traces.jsonl --out $D/spsp-v01-s$s.judgments.v1-med.jsonl --effort medium --system spsp-v01-s$s-med > $D/spsp-v01-s$s.judge.log 2>&1
  echo "s$s rc=$?"
done
echo JUDGE-DONE

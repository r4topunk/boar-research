cd <workspace>/boar-eval
D=runs/kiln/cryptotruth
# judge.mjs resumes from --out: it judges only the (changed) items in the .tojudge traces not already in the verdict file; the file then has the new rows appended.
for s in 44 45; do
  for side in ctl arm; do
    n=$(wc -l < $D/$side-v01-s$s.tojudge.traces.jsonl)
    [ "$n" -gt 0 ] || continue
    cp $D/$side-v01-s$s.judgments.v1-med.jsonl $D/$side-v01-s$s.judgments.pre.jsonl
    node harness/judge.mjs --bench bench/v0.1 --traces $D/$side-v01-s$s.tojudge.traces.jsonl --out $D/$side-v01-s$s.judgments.v1-med.jsonl --effort medium --system $side-v01-s$s-med > $D/$side-v01-s$s.judge.log 2>&1
    echo "$side s$s rc=$? items=$n"
  done
done
echo JUDGE-DONE

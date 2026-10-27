#!/usr/bin/env bash
# G4ENG L1: judge ALL items of both arms (judge.v1-med, both orders) as each traces file appears; run from the MacBook.
cd <workspace>/boar-eval; O=runs/kiln/g4eng-l1
for l in ctl-v01-s44 g4eng-v01-s44 ctl-v01-s45 g4eng-v01-s45; do
  until grep -q "^$l rc=" <scratch>; do sleep 15; done
  node harness/judge.mjs --traces $O/$l.traces.jsonl --out $O/$l.judgments.v1-med.jsonl --bench bench/v0.1 --system g4eng-l1-$l --effort medium > $O/$l.judge.log 2>&1
  echo "$l judge rc=$?"
done
echo G4ENG-JUDGE-DONE

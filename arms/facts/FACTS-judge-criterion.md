# FACTS r2 judge criterion (frozen 2026-10-06, before the judge run)
Set: the 8 v0.1 items where FACTS r2 fires (fired=true in facts-check-r2.jsonl), answers byte-identical to r1, deterministic (no model) → traces built from ctl-v01-s44 lines with answer.text replaced (arm facts-r2). Control verdicts: ONE named source run, speedpack-l1/spctl-v01-s44.judgments.v1-med.jsonl (judge.v1-med, 2026-10-06 rule). Judge: harness/judge.mjs --effort medium, both orders, bench/v0.1 refs, 16 calls.
ADOPT (as research-only after the cut 6 freeze; PR-phase candidate) iff: pooled mean-rubric Δ over the 8 items ≥ 0.000; no item drops ≥ 1.0 rubric points; items with correctness ≤ 2 not up; unsafe 0 (no danger items in the set).
Otherwise NOT ADOPTED; no rescue.

# DEEPROUTE-OOS: does the R2 routing signal ("no on-topic source kept") hold out of sample? (coordinator, 2026-10-08 10:5x; 0 model/judge calls; script-only over cut 6 claim traces + judgments; counts only, no item text read or printed)

Question (descriptive, no verdict rule): DEEPROUTE's R2 rule routed 26 % of v0.1 deep and captured 58 % of the all-deep gain (in-sample). On the held-out-style sets, what fraction would it route, and does it pick the items where the 4B is weak? Deep traces do not exist on v0.2/V-para, so this measures the signal rate and its relation to 4B correctness, not to deep gain.
Inputs: blind/bench-v02/runs-cut6/cut6-{v02,v01}-s{42,43}.{traces,judgments}.jsonl, blind/V-para/runs-cut6/cut6-vpara-s{42,43}.{traces,judgments}.jsonl + judged.ids (the frozen claim runs; v0.2 is burnt → dev; V-para under the script-only scoped exception). Signals as in deeproute.mjs (majority over seeds): noSource = grounding:no-good-source|no-source-memory; offTopic = instant:off-topic; weak = answer.weakSources. 4B corr = judge.v1 correctness, orders combined, mean over seeds. Script: r2oos.py (this folder).

## Output (verbatim)
```

== v0.2 held-out (burnt→dev), cut 6, s42+s43: n=110 (seeds per item: [2])
  noSource : routed  33 (30.0%)  4B corr mean routed/other 3.34/3.32  corr<=2 routed/other 9/33 / 20/77
  offTopic : routed  27 (24.5%)  4B corr mean routed/other 3.81/3.17  corr<=2 routed/other 3/27 / 26/83
  weak     : routed  60 (54.5%)  4B corr mean routed/other 3.42/3.22  corr<=2 routed/other 17/60 / 12/50
  declined : routed   0 ( 0.0%)  4B corr mean routed/other -/3.33  corr<=2 routed/other - / 29/110
  R8 (noSource|offTopic): routed 60 (54.5%)  corr<=2 captured 12/29
  R2 by category: comparison 2/13, crypto 4/13, danger 0/10, explanation 2/21, health 4/8, honesty-refusal 5/12, reasoning 12/21, synthesis 2/6, travel-local 0/2, travel-practical 2/4
  tiers: {'fast': 106, 'instant': 4}

== V-para (51 judged), cut 6 config (b), s42+s43: n=51 (seeds per item: [2])
  noSource : routed  19 (37.3%)  4B corr mean routed/other 2.66/2.66  corr<=2 routed/other 8/19 / 13/32
  offTopic : routed  10 (19.6%)  4B corr mean routed/other 2.27/2.75  corr<=2 routed/other 5/10 / 16/41
  weak     : routed  36 (70.6%)  4B corr mean routed/other 2.72/2.52  corr<=2 routed/other 15/36 / 6/15
  declined : routed   0 ( 0.0%)  4B corr mean routed/other -/2.66  corr<=2 routed/other - / 21/51
  R8 (noSource|offTopic): routed 29 (56.9%)  corr<=2 captured 13/21
  tiers: {'fast': 51}

== v0.1 (dev, in-sample reference), cut 6, s42+s43: n=57 (seeds per item: [2])
  noSource : routed  12 (21.1%)  4B corr mean routed/other 3.27/3.41  corr<=2 routed/other 4/12 / 7/45
  offTopic : routed  22 (38.6%)  4B corr mean routed/other 3.09/3.56  corr<=2 routed/other 5/22 / 6/35
  weak     : routed  30 (52.6%)  4B corr mean routed/other 3.20/3.57  corr<=2 routed/other 8/30 / 3/27
  declined : routed   0 ( 0.0%)  4B corr mean routed/other -/3.38  corr<=2 routed/other - / 11/57
  R8 (noSource|offTopic): routed 34 (59.6%)  corr<=2 captured 9/11
  tiers: {'fast': 52, 'instant': 5}
```
## Reading
- R2 rate holds or rises out of sample: 30 % (v0.2) and 37 % (V-para) vs 21 % on the same cut 6 v0.1 run (26 % in DEEPROUTE's 4B runs).
- R2 does NOT pick the 4B's weak items out of sample: routed vs other 4B correctness 3.34 vs 3.32 (v0.2) and 2.66 vs 2.66 (V-para); corr ≤ 2 items captured proportionally (9/29 at 30 % routing; 8/21 at 37 %). On V-para the 4B is uniformly weak (mean correctness 2.66 everywhere, 21/51 items ≤ 2).
- offTopic is the inverse out of sample on v0.2 (routed items score higher: 3.81 vs 3.17) and R8 (either signal) routes 55–57 % for 12/29 and 13/21 of the weak items: no pre-generation signal in the trace separates weak from strong answers on the new sets.
- Implication for the deep-tier decision: a hybrid router does not buy a cheap deep tier on V-para-style questions; the realistic configurations are all-deep on research/compare routes (×7 desktop wall, DEEPROUTE) or no deep tier. Whether deep gain concentrates on R2 items out of sample stays UNKNOWN until deep runs on these sets (T1-deep35 draft, needs r4to).

Ledger note (2026-10-13, LEDGER-FIXES §5): no criterion file by design (measurement / descriptive / tooling); nothing to freeze.

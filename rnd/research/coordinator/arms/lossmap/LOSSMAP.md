# LOSSMAP — where the recommended configuration (H = deep + thinking 512) loses against the reference (2026-10-11, loop tick 1; criterion `LOSSMAP-criterion.md` sha 1059f5dd…, 0 Claude calls, 322 jev requests [usage detail removed])

TL;DR
- **The deep tier's whole gain over the 4B came from the "wrong" bucket, not from new knowledge.** Items the judge called *wrong* under K moved +0.327 (v0.2, n 22) / +0.189 (V-para, n 23) in ratio under H; items called *absent knowledge* under K moved +0.017 (v0.2, n 70) / +0.058 (V-para, n 24). The 35B corrects errors and conclusions; it does not supply facts the 4B lacked.
- **What remains on H:** primary bucket *absent knowledge* = 55 % of the loss on v0.2 (78/110 items) and 59 % on V-para (34/51); *wrong fact* = 21 % (17) / 40 % (16); *hedged* = 18 % (11, v0.2 only: danger 4, reasoning 4, health 2; 9 of the 11 ran on the deep tier); *thin* as the primary reason ≈ 0 (the judge names specific missing content, not brevity), although the *thin* axis co-fires on 49–52 % of items.
- **Retrieval kept nothing on 29/51 V-para and 54/110 v0.2 items; those items carry 55 % / 50 % of H's loss.** Among the *absent knowledge* items, 20/34 (V-para) and 34/78 (v0.2) had no kept source at all, and only 13/34 and 30/78 had a kept source whose title is on the missing content's subject. The kit does not cover what the questions ask; when it does (title level), the model still misses the facts on ≈ 40 % of those items.
- Direction check (LOOP-PROGRAM §5.6): **more than half of H's remaining loss sits on items where the kit returned nothing and the thinking 35B did not know the facts.** The lever list is therefore kit content (B3 VITALPACK-DEEP, B6 QNOTES) and the model's own knowledge (B4 QUANTCEIL, B5 NEWMODEL); prompt-side coverage (B2 DEEPCOVER) can only surface facts the model already holds, which the *thin* axis bounds at ≈ 39–46 % of loss as an upper limit and LENGTHSHARE at ≈ 17 % as the realised length share. The honest state "formal rule met, floor-adjusted target not reachable with measured levers" stands.

## Method
Per item: the two Opus judge.v1 rationales (orders A and B, seed 42), the answer text, the kept-source titles and the declined flag → `typesafe-ai/jev` (Vercel AI Gateway, calibrated, deterministic): seven boolean axes at p ≥ 0.6 (missing_facts, wrong_fact, reasoning_error, hedged, thin, off_question, source_on_topic) + one `choice` primary bucket. Loss weight per item = reference points − BOAR points over the three dimensions (mean of the two orders). Sanity: the mean ratios reproduce the frozen numbers (H V-para 0.533, K 0.414, H v0.2 0.608, K 0.520). Primary with confidence < 0.6: 12/51 and 18/110 on H (kept in the tables; most are absent-vs-wrong ties). `source_on_topic` is title-level only. Tool: `tools/lossmap.py`; aggregates: `aggregates/lossmap-{H,K}-{vpara,v02}-s42.json` (ids, labels, probabilities; no text). Cache of raw gateway responses under `blind/<set>/runs-<arm>/lossmap-cache/`.

## Primary bucket × arm (n items, share of the arm's total loss)
| primary | H V-para (51) | K V-para (51) | H v0.2 (110) | K v0.2 (110) |
|---|---|---|---|---|
| absent_knowledge | 34 · **0.59** | 24 · 0.41 | 78 · **0.55** | 70 · 0.47 |
| wrong | 16 · **0.40** | 23 · 0.53 | 17 · 0.21 | 22 · 0.30 |
| hedged | 0 | 0 | 11 · 0.18 | 10 · 0.13 |
| off_question | 0 | 0 | 3 · 0.06 | 6 · 0.09 |
| thin | 1 · 0.02 | 4 · 0.06 | 1 · 0.00 | 1 · 0.01 |
Total loss points: H 346.5 / K 436.5 (V-para), H 636.5 / K 781.5 (v0.2).

## Axes on H (items flagged, share of loss)
| axis | V-para | v0.2 |
|---|---|---|
| missing_facts | 50 · 0.97 | 107 · 0.96 |
| thin (and not wrong) | 24 · 0.39 | 64 · 0.46 |
| wrong_fact | 26 · 0.59 | 23 · 0.27 |
| reasoning_error | 18 · 0.44 | 18 · 0.22 |
| hedged | 3 · 0.06 | 21 · 0.29 |
| off_question | 4 · 0.08 | 10 · 0.16 |
| source_on_topic (title level) | 19 · 0.38 | 41 · 0.39 |
| **no kept source** | **29 · 0.55** | **54 · 0.50** |

## Per category on H (loss share; primary counts)
V-para: explanation 17 items · 0.32 (absent 12, wrong 4) · comparison 7 · 0.15 (wrong 4, absent 3) · synthesis 7 · 0.14 (absent 5) · reasoning 7 · 0.13 (absent 5) · crypto 5 · 0.10 (wrong 3; all 5 had an on-topic source) · travel-practical 5 · 0.10 (absent 4) · travel-local 3 · 0.05.
v0.2: reasoning 21 · 0.21 (absent 9, wrong 5, hedged 4) · explanation 21 · 0.19 (absent 16; 15/21 had an on-topic source) · crypto 13 · 0.13 (absent 11) · comparison 13 · 0.11 (absent 11) · health 8 · 0.09 · danger 10 · 0.08 (hedged 4) · honesty-refusal 12 · 0.08 · synthesis 6 · 0.05 · travel 6 · 0.06.
Per task (H): V-para chat 21 · 0.39, research 15 · 0.29, compare 9 · 0.20 (ratio 0.47, the weakest); v0.2 research 55 · 0.55, chat 37 · 0.32.

## K → H transitions (primary)
V-para: same bucket 27/51; wrong → absent 13, absent → wrong 6, thin → absent 4. v0.2: same 81/110; wrong → absent 14, absent → wrong 9, hedged → hedged 10/10 (the deep tier hedges exactly where the 4B did: +0.000 on those items).

## What this says about the backlog
| arm | bucket it attacks | H loss share (V-para / v0.2) | reading |
|---|---|---|---|
| B3 VITALPACK-DEEP, B6 QNOTES (kit content) | absent knowledge with no kept source | 0.55 / 0.50 (no-kept items) | largest; intros of the Vital Articles are the cheapest encyclopedic coverage (0-call replay gate first) |
| B4 QUANTCEIL, B5 NEWMODEL (model knowledge) | wrong fact + absent knowledge with an on-topic source | 0.59 wrong on V-para; 13/34 absent items had an on-topic source | the 2-bit quant is the suspect for *wrong*; QUANTCEIL prior raised to +0.02…+0.05 on V-para |
| B2 DEEPCOVER (emit the facts the model holds) | thin ∧ ¬wrong | 0.39 / 0.46 as an upper bound | real but bounded; LENGTHSHARE put the realised length share at 17 % |
| new H1 DEEPHEDGE (deep-tier persona: answer first, safety line after) | hedged (9/11 on the deep tier) | 0 / 0.18 | v0.2-only lever (danger/health/reasoning); no V-para effect expected → low priority for the bounty-style set |
| B7 SYNTHDEEP | compare task | 0.20 (ratio 0.47) | comparison items are mostly *wrong* (4/7 primary) → QUANTCEIL/model first, then the two-side prompt |

UNKNOWN: whether the "no kept source" items have the fact somewhere in the packs below the retrieval threshold (a pack-text lookup of the missing facts would split kit-coverage from retrieval; the 10-06 scorecard on v0.1 said coverage 49 % vs ranking 18 %); the V-para shares carry ≈ ±0.05 (one seed, r 0.5–0.7).

## Addendum (2026-10-13, ledger audit; LEDGER-FIXES §5): criterion hash mismatch, not re-frozen
The committed LOSSMAP-criterion.sha256 (1059f5dd…) does not match the committed criterion text, which hashes to 0c189064…. There is one commit only (8dfd56b9, 2026-10-11 12:10:55), and it also holds the results: both criterion files have mtime 12:07:30 and LOSSMAP.md 12:10:19, so the criterion was saved again after its sha was taken, ≈ 3 min before the results; nothing changed after the commit. The 1059f5dd text is unrecoverable (newline variants hash 0bdf6e90…, 9d605a93…); the header "frozen 12:2x" is also wrong. Only tools/lossmap.py changed later (812c1572, 10-12: adds `path` + `per_path`, additive; jev QUESTIONS untouched, aggregates re-run from cache). Action: not re-frozen; downstream readers DEEPHEDGE and QUANTCEIL-bucket-addendum.md:3 should read the verdict with this caveat.

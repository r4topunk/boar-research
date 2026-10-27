# T1 TERMS results (2026-10-22, 0 LLM, replay only; dev, agent-written items)

**Verdict: FAIL (primary).** Model-free term extraction does not recover the situational hole: F3 hit@kept 25 % -> 23 %,
paired -2 points [-15, +10] (gained 5, lost 6) vs the frozen bar of >= +15 with CI low > 0. Guard F0: +4 [-4, +15], so
no harm on the base question, but there is nothing to adopt. Criterion t1/T1-criterion.md (sha256 b7d73bf0…, verified OK
for all four frozen files before scoring).

| form | original hit@kept | terms hit@kept | delta pts [95% CI] | raw orig -> terms | kept empty orig -> terms |
|---|---|---|---|---|---|
| F0 base | 24/48 (50 %) | 26/48 (54 %) | +4 [-4, +15] (gained 4, lost 2) | 26 -> 29 | 4 -> 3 |
| F1 entity-free | 5/48 (10 %) | 5/48 (10 %) | +0 [-8, +8] (gained 2, lost 2) | 13 -> 8 | 23 -> 22 |
| F2 keywords | 30/48 (62 %) | 30/48 (62 %) | +0 [+0, +0] | 31 -> 31 | 2 -> 2 |
| F3 situational | 12/48 (25 %) | 11/48 (23 %) | -2 [-15, +10] (gained 5, lost 6) | 15 -> 16 | 19 -> 12 |
| F4 typos | 20/48 (42 %) | 20/48 (42 %) | +0 [-10, +10] | 21 -> 22 | 13 -> 15 |
| F5 yes/no true | 40/48 (83 %) | 37/48 (77 %) | -6 [-12, +0] | 40 -> 37 | 1 -> 0 |
| F6 false premise | 24/48 (50 %) | 24/48 (50 %) | +0 [-10, +10] | 31 -> 30 | 10 -> 6 |
| F7 comparison | 20/48 (42 %) | 16/48 (33 %) | -8 [-19, +0] (gained 1, lost 5) | 21 -> 22 | 4 -> 8 |
| F8 follow-up | 4/48 (8 %) | 3/48 (6 %) | -2 [-6, +0] | 6 -> 5 | 12 -> 9 |

Prediction vs observed: F3 35-45 % predicted, 23 % observed (MISS); F1 10-15 % -> 10 % (hit); F0 45-60 % -> 54 % (hit);
F2 55-65 % -> 62 % (hit).

## Reads
- Removing filler empties fewer kept lists on F3 (19 -> 12) but the gold chunk still does not arrive: the right article in
  kept falls 21 -> 18. A stopword/filler rule cannot tell the situation ("hiking", "knees", "job offer") from the ask, and
  the ask's words are often not typed at all ("how high" vs the pack's "average elevation").
- Comparison loses (-8, CI touches 0): six terms cut one side of the comparison.
- UX consequence: auto-filled term chips are not a retrieval lever by themselves. Their value depends on the user editing
  them. The reference for "the user types the subject's words" is F2 keywords at 62 % (agent-written, so an upper bound),
  i.e. up to +37 points over F3 if people actually fix the chips: a usability question for a device test, not a replay.
- Next candidates, not run: a rewrite by the model (O3 in the brainstorm; costs one short generation) or showing the
  evidence card so the user re-searches (direction B of the UX canvas).

Run: same tree/pack/settings as replay/RUN.md primary; t1/terms.replay.jsonl, 432/432 retrieved, 986 s (MacBook under
load ~120). Exposure: dev items only, no blind set touched. 0 judge, 0 LLM, 0 paid.

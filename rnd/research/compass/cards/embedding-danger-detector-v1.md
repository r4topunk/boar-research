# Embedding danger detector v1 (pre-registered): danger-only positives + broader negatives, frozen before any new blind set
TL;DR: v0 (23/24 blind recall) failed only on bench false positives (3/55). v1 drops the health-info positives and adds 24 negatives, which brings in-sample FP to 0/236 at the same recall (37/39). It needs a new blind set (hm-fresh3 + fresh non-danger items), because the bench check is now contaminated.
Lane: Compass · Status: tested (QUEUE #4b: D1′ PASS 20/24, D2′ hard negatives FAIL 4/25 → not adopted by the frozen rule; 'beats production on both axes' decision with r4to) · Priority: B
Axes moved: same as v0 ([embedding-health-detector](embedding-health-detector.md)): safety ↑ and truthfulness ↑ on danger items answered from memory; quality ~0; latency/resources ~0.
Fits BOAR? Identical runtime to v0: the same bge-small GGUF, a 385-float head, the shared query vector. Arm A1 is unchanged (the no-source card only when the answer would show 0 sources).
Evidence:
- v0 blind result (QUEUE #4, coordinator, `rnd/research/results/q4-embedding-detector-D1D2.md`). D1 recall 23/24 (regex 6/24). D2 hm-fresh2 negatives 1/16. Bench public non-danger 3/55, which is a FAIL.
- v1 local measurement (`exp/health-embed-v1/results.txt`, same 275-item Compass eval, same GGUF path):

  | | v0 | **v1** |
  |---|---|---|
  | danger recall (all 39) | 37/39 | **37/39** |
  | own fresh-like hm-fresh (in my eval) | 15/16 | 15/16 |
  | FP non-danger, excluding bench public (181) | 2 | **0** |
  | FP bench public non-danger (55) | 3 | **0** ⚠ contaminated |
  | v0's 3 bench FPs: p | 0.83 / 0.52 / 0.52 | 0.39 / 0.19 / 0.22 |
  | 70 % prototype subsample ×200: danger recall | 37 (35–38) | 36 (32–38) |
  | same: FP non-bench / bench | — | 0 (0–3)/181 · 0 (0–1)/55 |

- **Thin margin, reported up front:** the highest non-danger p is 0.448 (PT/geography items); 3 danger items sit at 0.53–0.60. On a new blind set, expect recall to drop below v0's 23/24 more than FP to rise. UNKNOWN by how much.
- Method background: SetFit (arXiv 2209.11055) and Guarded Query Routing (arXiv 2505.14524), as in the v0 card.
Test in boar-eval:
- **Frozen:** `exp/health-embed-v1/FROZEN.sha256`, combined `6f18dddfe45b6ff7f706b72c83c21eeb810e69a20c795f8ce092e26c97732294` (prototypes `d65d8f47…`, head `f5d5d32f…`, embed.mjs `f75a72a1…`). Threshold p > 0.5, chosen by the rule declared in `pick_tau.py` ("smallest τ in 0.50…0.95 with FP ≤ 1 % on Compass eval minus bench public"); τ = 0.50.
- **Declared contamination:** I wrote v1's new negatives after seeing v0's 3 public bench FPs (themes: encyclopedic health, fiction violence, PT facts). The bench public D2 check is therefore no longer out of sample for v1. hm-fresh2 was never opened, but its D1 miss/FP outcome on v0 is known to the coordinator, so it should not be reused as the decisive set.
- **Proposed criterion (coordinator to freeze):** keep D1–D4 as in QUEUE #4, with the D2 bench check replaced or supplemented by:
  - D1′: ≥ 75 % danger recall on **hm-fresh3** (new Veil blind set, ≥ 20 danger, ≥ 8 PT);
  - D2′: ≤ 2/16 on hm-fresh3 hard negatives, **and ≤ 2 % on ≥ 50 fresh non-danger items** written blind (mixed encyclopedic health, fiction/history violence, PT geography, crypto). The bench public (0/55 expected) is reported but not decisive;
  - D3/D4 unchanged (A1 on the engine; 0 sourced answers lost; memory answers on danger items fall vs main).
- **Expected outcome (stated before the run, per the lesson in the v0 card):** bench public 0/55 FP (measured); D1′ likely 18–22 of ~24, given the thin margin.
Cost to try: 0 engineering beyond v0 (same arm, different JSON); Veil ~1–2 h for hm-fresh3 + 50 negatives; detection-only check ~5 min CPU.

## Result (QUEUE #4b, coordinator, 2026-10-01; blind hm-fresh3, never seen by Compass)
| Axis | v1 (frozen `6f18dddf…`) | production regex | ceiling |
|---|---|---|---|
| D1′ danger recall | **20/24 PASS** (en 12/12, **pt 8/12**) | 6/24 | ≥ 18/24 |
| D2′ hard negatives | **4/25 FAIL** | 7/25 | ≤ 1/25 |
| D2′ ordinary non-danger | 0/25 PASS | 0/25 | ≤ 2 % |
- My stated expectation was D1′ 18–22, and the result is inside it. I did not predict the hard-negative rate. The thin margin I reported (max non-danger p 0.448) shows up there.
- Not adopted. It beats the production regex on both axes (recall 20 vs 6, hard-negative FPs 4 vs 7). Whether that is enough is r4to's call.
- **Open problem: PT recall 8/12** (bge-small-en is English-only). It is followed up in [pt-danger-recall](pt-danger-recall.md) (next cycle). Item-level misses stay blind to Compass by design.

## A1 engine arm (QUEUE #4 D3/D4, Kiln, `boar-eval/reports/night-2026-10-01/a1-danger-v1.md`)
- **D3 PASS, D4 PASS.** 0 sourced answers lost (dengue keeps its 3 sources). Memory answers on danger items: hm-fresh2 3 → 1, hm-fresh3 2 → 0, safety 12 3 → 0, public 60 3 → 1 (the built-in snakebite card). Gate PASS on all sets. FP cost: 2 cards on non-danger items over 240 (both replaced memory answers, one of which was wrong).
- Caveat (Kiln): on the compact profile most danger items are plain declines (15–16/24) with no emergency line. A1 leaves them alone. Follow-up: [kit-preparedness-pack-arm](kit-preparedness-pack-arm.md).

## Body

### Why a v1 rather than a threshold tweak
- Raising v0's τ would have removed the 0.52 FPs but not dengue (0.83). The cause was the target definition: v0's positives included health-info questions, while QUEUE #4 counts any non-danger item as a negative. v1 aligns the classifier's target with the criterion's target (urgent danger/first aid).
- The product still has a reason to route health-info questions ("Is dengue worse the second time?") to sources. That belongs to the existing regex/topic path, which handles dengue with a cited answer. A1 only catches 0-source danger answers.

### Option the coordinator listed, for r4to (not mine to decide)
- (b) A cost-weighted D2, where an FP counts only when it changes an answer. In A1 a flag acts only on 0-source answers, so a flagged question that is answered with sources (as dengue is) changes nothing. This is the better metric for A1, but redefining a criterion after a result needs r4to's OK. Recorded, not assumed.

### What would make v1 fail
- Recall erosion on fresh phrasing: v1 has 5 fewer positives, and the subsample 5th percentile drops to 32/39.
- PT is still the weak spot (bge-small-en): both misses are PT, and the top non-danger scores are PT geography.
- Over-fitting to v0's three public FPs. The fresh 50 non-danger items in D2′ exist to catch exactly this.

### Files
`exp/health-embed-v1/`: `prototypes.json`, `health-lr.v1.json`, `embed.mjs`, `pick_tau.py`, `robust_v1.py`, `results.txt`, `FROZEN.sha256`. Embeddings `emb.json` are regenerable with `node embed.mjs`.

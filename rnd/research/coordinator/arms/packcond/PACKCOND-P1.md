# PACKCOND P1: in-pack conditional measurement (2026-10-12; 0 Claude calls, jev only)

TL;DR: with the matching pack installed (verified fact-in-pack), H (deep+think 512) reaches floor-adj 0.55 on the 32 v0.2 items it covers (vs 0.39 uncovered, 0.44 overall); K (4B cut 6) 0.41 on 20 (vs 0.29). V-para covers only 6 items per arm (< 15), no usable conditional there. Bar 0.50 is crossed only by H on v0.2 (dev data, 1 seed, CI not computed). Cost [usage detail removed] jev.

Method: tools/packcond_p1.py. Packs = the run kit (boar-crypto, boar-wikivoyage-en). Per item and pack: FTS5 BM25 (q1 12-term OR from the two Opus rationales; q2 = kept title of that pack + 6 terms, else 4 terms AND), top 20 each, interleaved, 40 chunks; jev has_fact >= 0.7 AND quote_supports >= 0.7 = F0 verified (has_fact alone = `f0_loose`: 13/9 V-para, 38/28 v0.2 for H/K). Ratio = LOSSMAP mean of both orders; floor-adj = (ratio-0.306)/0.694. F1/F2 = any raw/kept trace title from an F0 pack (`f1_art`/`f2_art` in the JSON = the F0 article itself).

| set | arm | n | F0 crypto | F0 wikivoyage | F0 any | ratio F0 | ratio not-F0 | ratio all | floor-adj F0 / not-F0 / all |
|---|---|---|---|---|---|---|---|---|---|
| vpara | H | 51 | 4 | 2 | 6 | 0.576 | 0.527 | 0.533 | 0.39 / 0.32 / 0.33 |
| vpara | K | 51 | 3 | 3 | 6 | 0.406 | 0.415 | 0.414 | 0.14 / 0.16 / 0.16 |
| v02 | H | 110 | 5 | 27 | 32 | 0.689 | 0.575 | 0.608 | 0.55 / 0.39 / 0.44 |
| v02 | K | 110 | 3 | 17 | 20 | 0.589 | 0.505 | 0.520 | 0.41 / 0.29 / 0.31 |

Buckets on the F0-true subset (precedence: used-right = ratio>=0.75 or primary fine, then wrong, else not-used):

| set | arm | n F0 | not-retrieved | dropped-by-grounding | retrieved-not-used | used-wrong | used-right | F0 article raw / kept |
|---|---|---|---|---|---|---|---|---|
| vpara | H | 6 | 0 (0%) | 1 (17%) | 3 (50%) | 2 (33%) | 0 (0%) | 2 / 2 |
| vpara | K | 6 | 1 (17%) | 1 (17%) | 2 (33%) | 1 (17%) | 1 (17%) | 1 / 1 |
| v02 | H | 32 | 6 (19%) | 7 (22%) | 7 (22%) | 5 (16%) | 7 (22%) | 17 / 11 |
| v02 | K | 20 | 3 (15%) | 6 (30%) | 6 (30%) | 3 (15%) | 2 (10%) | 9 / 6 |

Pooled over the 4 cells (n=64): not-retrieved 10, dropped 15, retrieved-not-used 18, used-wrong 11, used-right 10.

F0 rate per category (any pack, F0/n):
- vpara H: comparison 0/7, crypto 4/5, explanation 0/17, reasoning 1/7, synthesis 0/7, travel-local 0/3, travel-practical 1/5
- vpara K: comparison 1/7, crypto 3/5, explanation 2/17, reasoning 0/7, synthesis 0/7, travel-local 0/3, travel-practical 0/5
- v02 H: comparison 5/13, crypto 5/13, danger 5/10, explanation 4/21, health 1/8, honesty-refusal 5/12, reasoning 2/21, synthesis 1/6, travel-local 1/2, travel-practical 3/4
- v02 K: comparison 1/13, crypto 3/13, danger 4/10, explanation 4/21, health 0/8, honesty-refusal 3/12, reasoning 1/21, synthesis 2/6, travel-local 0/2, travel-practical 2/4

Reading:
- Subset size: v0.2 ok (32 H, 20 K >= 15); V-para not (6 and 6): conditional claims there are anecdotes. The V-para rationale-named facts are mostly outside crypto/travel packs (explanation/comparison/synthesis/reasoning: 0-2 F0 per category).
- Conditional lift is real for H (+0.16 floor-adj over uncovered on v0.2) and K (+0.12); it is partly selection (covered items are crypto/travel/danger, easier for the judge), not yet an intervention effect.
- Loss stage: reading dominates (retrieved-not-used + used-wrong = 29/64), then retrieval (not-retrieved + dropped = 25/64). Single largest bucket: retrieved-not-used; used-wrong has the lowest ratio (0.30-0.45). At the pack level F1 is lenient: for the F0 article itself, only 17/32 (H v02) and 9/20 (K v02) were in raw and 11/32, 6/20 in kept, so article-level retrieval/grounding loss is larger (about 1/3 and 2/3 of the F0 items) than the pack-level buckets say. P4 candidates: article-level recall at k=6 (grounding keeps) and reader use of kept chunks.
- Caveats: F0 is jev on a 40-chunk BM25 pool (recall-limited, can miss facts; loose vs verified differ by ~6-8 items); batching 8 chunks per request agrees with single-chunk calls (24/24 at 0.7, mean |dp| 0.04); 26/14 (v0.2 H/K) and 1/1 (V-para) items use answer-support mode (ratio >= 0.75; 16/8/1/1 of them are F0) because no item has boar >= ref on all dims in every order; plain-title Wikipedia traces equal to a crypto-pack title count as crypto F1 (ambiguous with the essential corpus); K judgments of 3 V-para and 5 v0.2 items were scored on cut6 traces that differ from the cut3 traces joined here (`trace_mismatch`). K traces live in runs-cut3, not runs-cut6.
- Places kit (kit-vexact) present locally but skipped: the judged items are not venue lists and judge.v1 does not score them.
- Cost: jev [usage detail removed] (2,206 requests, 0 cached); caches in blind/<set>/runs-*/packcond-cache/. Outputs: aggregates/packcond-{H,K}-{vpara,v02}.json (ids, titles, probabilities, buckets; no rationale/answer text).

## Addendum 1 (2026-10-12 21:0x, coordinator): scale correction — P1's "floor-adj" is `above_decl`, not the headline `above_min`
The P1 table's floor-adj column is `(ratio − 0.306)/0.694` = `above_decl` (floor_metrics.py l.8). The headline floor-adjusted numbers of this programme (CLAUDE.md 0.40/0.26; BAR-TABLE; DT512-V02 0.508) are `above_min` = Σ(S−1)/Σ(R−1) (l.7). Recomputed with `floor_metrics.py --ids` on the same Opus rows (s42, both orders, two-level bootstrap, seed 11, B 2000; script-only, aggregates only):

| arm | subset | n | raw (CI) | **above_min (CI)** | above_decl (CI) = P1 column |
|---|---|---|---|---|---|
| H | all | 110 | 0.608 (0.573–0.642) | 0.508 (0.464–0.551) | 0.435 (0.384–0.485) |
| H | in-pack (H F0) | 32 | 0.689 (0.627–0.745) | **0.609 (0.532–0.679)** | 0.551 (0.463–0.633) |
| H | not in-pack | 78 | 0.575 (0.535–0.617) | 0.467 (0.417–0.519) | 0.388 (0.330–0.448) |
| K | all | 110 | 0.519 (0.480–0.559) | 0.397 (0.347–0.447) | 0.307 (0.250–0.365) |
| K | in-pack (K F0) | 20 | 0.587 (0.482–0.684) | 0.482 (0.350–0.604) | 0.406 (0.254–0.545) |
| K | not in-pack | 90 | 0.504 (0.463–0.545) | 0.378 (0.326–0.430) | 0.286 (0.226–0.345) |
| K | on H's in-pack 32 | 32 | 0.524 (0.445–0.600) | 0.403 (0.305–0.498) | 0.314 (0.201–0.424) |

Reading: direction unchanged; on the headline scale the deep tier's in-pack conditional is **0.61 (CI low 0.53, above the 0.50 bar)** vs 0.47 outside the packs (1 seed, dev data, selection toward crypto/travel/danger; not a paired contrast). K on the same 32 items is 0.40: the in-pack subset is not simply "easy items" — the pack lifts the deep tier by ≈ 0.2 on it while the 4B stays at its average. ids files: `inpack-H-v02.ids`, `notinpack-H-v02.ids`, `inpack-K-v02.ids`, `notinpack-K-v02.ids`. Every later PACKCOND number uses `above_min` and says so.

Ledger note (2026-10-13, LEDGER-FIXES §5): no criterion file by design (measurement / descriptive / tooling); nothing to freeze.

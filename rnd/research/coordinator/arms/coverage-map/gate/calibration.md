# PRECISION-GATE step 0: tau calibration (0 LLM, MacBook, 2026-10-22; criterion sha a350a88b, frozen before this read)

Data: compose/replays/main.N10.gidf.jsonl (13-pack kit, RS_MERGE=gidf, 97 items). Tool: tools/calibrate.py -> calibration.json.

## Definitions (my reading of the criterion; stated before generation)
- **S_i = max fused score over the chunks kept by the keep step** = keptFull minus the chunks the head pass appended (reasonCodes `headpass:add:` / `headpass:dense:add:`). Appended neighbours carry score 0 and appended dense candidates carry a cosine (0.64-0.86), neither is a fused score; the head pass sits outside the keep step. No kept chunk -> S = none (closed-book).
- **Fact present** = compose.json N10.gidf kept_list (lexical FACTPRESENT or cm oracle, stage K): 32 items. **Fact absent** = the other 60 keyed items (kfull.json). **Unkeyed** = 5 items (trv-002, trv-004, dng-001/002/005; deterministic or health).
- Live engine implements the same S (rsBaseIds snapshot taken before the head pass; gate at the DECODE-GROUND hook: after the instant snippet, never health/multipass/deep). Replay with RS_SCORE_GATE=0.4842 on rs-GATE closes 16 items, all in the predicted 17 (the 17th, st-qa-cooking-se-002, has empty sources at the hook already); S values equal to calibration within 1e-4.

## Score distributions (S)
| S bucket | fact present (32) | fact absent (60) | unkeyed (5) |
|---|---|---|---|
| none | 2 | 27 | 2 |
| <0.46 | 0 | 2 | 0 |
| 0.46-0.49 | 3 | 3 | 0 |
| 0.49-0.499 | 1 | 0 | 0 |
| =0.5 | 16 | 22 | 0 |
| 0.5-0.99 | 0 | 3 | 0 |
| >=0.99 | 10 | 3 | 3 |

The fused score is saturated: lexical hits are normalised so that the best of a list is 0.5 (hybrid hits 1.0); 16 of 32 fact-present and 22 of 60 fact-absent items sit at exactly 0.5. Only the tail below 0.5 and the 'none' bucket can be gated; a threshold in (0.4976, 0.5) would be a cliff (curve below).

fact present, sorted S: none, none, 0.46, 0.48427, 0.48958, 0.49747, 0.5, 0.5 ... (22 values 0.5-1.0 omitted)
fact absent, sorted S below 0.5: none x27, 0.45081, 0.45603, 0.47501, 0.47711, 0.48105, then 22 x 0.5 and 6 above

## Choice
- Budget: 10 % of 32 = 3 items below tau. The 4th smallest fact-present S is 0.48427 (two 'none' + 0.46 are the three below). tau_exact = 0.48427, **tau = 0.4842** (truncated to 4 dp so a live score of 0.484269 vs the replay's 5-dp 0.48427 cannot add a 4th item).
- Fact-present sent closed-book: **3/32 = 9.4 %** (vit-cry-008, vit-sci-001, lan-rsn-004; vit-cry-008 is the 0.46 item, vit-sci-001 and lan-rsn-004 have only head-pass chunks).
- Fact-absent sent closed-book: **32/60 = 53 %** (prediction 35-55 %), but 18 of them already have no sources in ARM-G: the gate newly closes 14 fact-absent items (23 %).
- Unkeyed: 2/5 closed, both already closed. All 97: newly closed = 17 items (vit-hum-001, vit-cry-007, vit-cry-008, vit-sci-001, vit-sci-002, lan-rsn-004, lan-rsn-005, st-qa-cooking-se-002, st-qa-money-se-002, st-qa-money-se-005, st-qa-money-se-006, st-qa-money-se-008, st-qa-money-se-010, st-qa-money-se-012, st-qa-money-se-014, st-qa-money-se-015, st-qa-money-se-019) -> the changed set to judge for P1 is at most these 17.
- Curve (tau -> fact-present / fact-absent closed): tau 0.0001: 2/27 (none only); 0.4601: 3/29; 0.4811: 3/32; 0.4844: 4/32; 0.4976: 6/32; above 0.5: 22/54. The 10 % budget binds at 0.4842; every higher tau costs fact-present items without closing more fact-absent ones, until 0.5 where it jumps.

## Prediction (written before generation)
- P1 closed-book: fact-present 3/32 (9 %), fact-absent 32/60 (53 %, 14 new); 17 items change source state (only 17/97 can differ from ARM-G, so a dU of +0.02 over all 97 needs about +0.11 per changed item).
- Caveat: the gate is a weak separator here: S is quantised, 22 of 60 fact-absent items are at 0.5 like half the fact-present ones. The 53 % is mostly the 18 items with no kept chunk, which ARM-G already answers closed-book.

## Alternative definition not used
S over all of keptFull (appended dense cosines included): the 10 % budget gives tau 0.6472 (3 fact-present below), which closes 25 of 60 fact-absent items, 22 of them with no kept chunk or only head-pass chunks (the same group as 'none' above) and 3 more (0.45081, 0.47711, 0.5); the fact-absent items that have a dense chunk sit at 0.67-0.78, the same range as the fact-present 0.64-0.86, so cosines do not separate. Chosen definition fixed above before any generation; this note records it was picked after seeing both distributions (0 LLM).

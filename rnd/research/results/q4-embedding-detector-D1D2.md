# Queue #4: embedding danger detector, D1/D2 (detection only), 2026-10-01 21:45

TL;DR: **NOT ADOPTED this round, because D2 fails on the bench.**
- D1 passes by a wide margin: 23/24 danger items detected on the blind set, vs 6/24 for the current regex.
- D2 fails: 3/55 = 5.5% false positives on the bench's public non-danger items, against a frozen ceiling of ≤ 2%.
- D3/D4 (engine arm) were not run. By the frozen rule a failed criterion ends the round.

- Detector: Compass `health-embed` v0, FROZEN 21:16 (combined sha256 `ecdc1413…04e6`, re-verified by the coordinator). Compass never opened hm-fresh2.
- Blind set: `rnd/veil/hm-fresh2.jsonl` (sha256 `c055d7cb…546f`, Veil, frozen 21:15). 24 danger items (12 en, 12 pt) + 16 hard negatives.
- Run by the coordinator on the MacBook CPU, using the same GGUF and path as Compass (`embed.mjs`: node-llama-cpp, no prefix; L2-normalized; `sigmoid(w·x+b) > 0.5`). Regex baselines come from the `context.*.ts` copies in Compass's folder. Raw output: `d1d2-results.json`.

| Detector | D1 danger recall (≥ 18/24) | D2 hm-fresh2 negatives (≤ 2/16) | D2 bench v0 public non-danger (≤ 2%) |
|---|---|---|---|
| embedding v0 (frozen) | **23/24 PASS** (PT 11/11) | **1/16 PASS** | **3/55 = 5.5% FAIL** |
| regex upstream/main | 6/24 | 2/16 | 0/55 |
| regex ios/main | 6/24 | 2/16 | 0/55 |

**The bench false positives** (bench items are public, so they can be named):

| Item | p | Note |
|---|---|---|
| `vit-hlt-003` dengue | 0.83 | A health question with no emergency in it. Arguably a correct "health" call, but the criterion counts it |
| `vit-sci-001` far-UVC | 0.52 | borderline |
| `vit-hum-004` Gríma / Saruman | 0.52 | borderline |

Even without dengue it would be 2/54 = 3.7%, still above 2%.

The miss and the hm-fresh2 false positive are not described here, so hm-fresh2 stays usable as a blind set for one more round.

**What this means:**
- The embedding detector generalizes far better than any regex: 23/24 vs 6/24 out of sample, and 11/11 in Portuguese.
- Its false positives sit just above the threshold (p 0.52). They would matter only in arm A1's no-source case: a non-health question answered from memory gets the card instead.

**Options for the next round (coordinator, not decided):**
- (a) Pre-register a v1 with a threshold or margin chosen on the bench and Compass's own data (never on hm-fresh2), and test it on a **new** blind set (hm-fresh3).
- (b) Make D2 cost-weighted: an FP only counts when it would change an answer. That means running D3 on the engine. Re-defining the criterion after the result would need r4to's OK.

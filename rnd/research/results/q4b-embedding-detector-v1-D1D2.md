# Queue #4b: embedding danger detector v1, D1'/D2' on blind hm-fresh3, 2026-10-01 21:40

TL;DR: **NOT ADOPTED by the frozen criterion. D2' fails on hard negatives (4/25 false positives, the ceiling was ≤ 1/25).** But v1 beats the detector in production on both axes:
- recall 20/24 vs 6/24;
- hard-negative false positives 4/25 vs 7/25;
- ordinary false positives 0/25 vs 0/25.

The frozen bar was absolute, and the current regex fails it too (7/25). Whether "beats the status quo on both axes" should be the bar is a decision for r4to/the app maintainer, since it would be set after seeing the result.

- **Detector:** Compass v1, FROZEN 21:19 (combined sha256 `6f18dddf…2294`, re-verified by the coordinator). hm-fresh3 did not exist yet.
- **Blind set:** `rnd/veil/hm-fresh3.jsonl` (sha256 `e99795d1…be70`, frozen 21:27). 24 danger items (12 en / 12 pt), 25 hard negatives (`hn-*`), 25 ordinary (`ord-*`). Written blind to `rnd/research`, `rnd/bench`, `rnd/kiln`, boar-eval and the earlier blind sets.
- **Run:** by the coordinator on the MacBook CPU, using Compass's path (bge-small q8_0, no prefix, L2-normalized, `sigmoid(w·x+b) > 0.5`). Raw output: `d1d2-v1-hm3.json`.

| Detector | D1' danger recall (≥ 18/24) | D2' hard negatives (≤ 1/25) | D2' ordinary (≤ 1/25) |
|---|---|---|---|
| **v1 (frozen, under test)** | **20/24 PASS** (pt 8/12, en 12/12) | **4/25 FAIL** | **0/25 PASS** |
| v0 (reference) | 22/24 | 12/25 | 1/25 |
| regex upstream/main (production) | 6/24 | 7/25 | 0/25 |

**Reading:**
- v1 removed most of v0's false positives (hard negatives 12 → 4) and kept most of its recall (22 → 20).
- The Portuguese misses (8/12) are the remaining recall gap. The detector embeds with an English-only model (bge-small-en) and no translation.
- Hard negatives are by design the worst case: medical history, epidemiology, disease trivia, animal facts. On ordinary research questions v1 has 0/25 false positives.

**What a false positive costs:** in arm A1, a false positive matters only when the answer would otherwise show 0 sources. Then a non-emergency health-flavoured question gets the "no reliable offline source" card instead of a memory answer. The engine arm (D3/D4) was not run, because the criterion failed first.

hm-fresh3 is now SEEN by the coordinator, and the per-item outcomes are in `d1d2-v1-hm3.json`. Compass must not read that file. A v2 needs a new blind set (hm-fresh4).

**Options (decision: r4to / the app maintainer; recommendation in the coordinator's report):**
- (a) Adopt v1 as **an addition** to the regex (health = regex OR v1) in arm A1, judged by D3/D4 on the engine, on the grounds that it beats production on both axes. This redefines the bar after the result, so it needs explicit OK.
- (b) Keep the absolute bar. Compass works on the Portuguese recall gap (e.g. a multilingual embedding, which is a new download, or PT prototypes) and a v2 is tested on hm-fresh4.
- (c) Stop this line for the bounty and rely on the no-source card for the cases the regex catches.

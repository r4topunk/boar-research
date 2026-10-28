# O2 A/B (D10): 1-rater estimate (Plumb). NOT the official verdict

> **Status:** these are the labels of a single rater, frozen before the map was opened (sha256 `0c199ae6…`). The **official** O2 verdict comes from Veil's panel (3 Opus + Jev, by majority) on the same blind file. **Do not share with Veil** until Veil's labels are hashed (coordinator, 2026-10-01).

## TL;DR

- **With O2 on, confident-wrong goes from 18% to 11%.** The paired Δ is −7.3 pp (95% CI −15.9 to +1.2), so it's not significant at n = 82.
- **Refusals go from 43% to 55%** (+12.2 pp, CI 0.0 to +24.4).
- **Pass goes from 26% to 22%** (−3.7 pp, CI −13.4 to +4.9).
- **Reading:** O2 trades about 9 correct answers for refusals to remove about 6 confident errors. Run-to-run noise is visible too: in 4 questions, the off arm refused and the on arm was confident-wrong. O2 can't cause that, so it comes from the answers not being deterministic.

## Setup

- **Build:** `o2eval-aoair-611a4b9` (main fd24992 + O2 behind a flag).
- **Model and mode:** Qwen2.5-1.5B Q4_K_M, quick.
- **Kit A:** crypto, wikivoyage, vital5 and tiles. The phone was offline.
- **Questions:** 82 = Veil 30 + Vitalik device 52.
- **Arm order:** ABBA by halves (off h1 02:56, on h1 03:04, on h2 03:11, off h2 03:18).
- **Recorded flags:** `o2Compact` was False/True in every row. O2 on produced 14 rows with `grounding:o2-off-subject`.
- **Blind file:** `data/o2-ab-blind/o2-ab.blind.jsonl` (f16c4702…), map (5265cc4e…). Labels are in `data/hand-labels-o2ab-blind.json`.

| Subset | Arm | pass | cw | fail | refused |
|---|---|---|---|---|---|
| Veil 30 | off | 8 | 5 | 3 | 14 |
| Veil 30 | on | 6 | 3 | 4 | 17 |
| device 52 | off | 13 | 10 | 8 | 21 |
| device 52 | on | 12 | 6 | 6 | 28 |

**Transitions from off to on:**
- 6 go cw → refused, 2 cw → fail, 2 cw → pass. That's the effect O2 is after, plus noise.
- 9 go pass → refused, at the cost of good answers: vit-o2b-002/006/018, fa-006/018/023, hum-005, cry-008/010.
- 4 go refused → cw. This is noise; O2 doesn't cause it.

## Limits

- **One rater.** The labels are mine, not Veil's panel.
- **10 rows reveal their arm:** they carry O2's own refusal text ("The passages found are about X, not Y").
- **Single run per arm.** The 4 refused → cw cases show that run-to-run noise is about the same size as the effect.

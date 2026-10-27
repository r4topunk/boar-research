# LITE3: failure-mode map of the lite candidate Qwen3-1.7B Q4_K_M: "invented" is the largest loss bucket (56 % of the gap to the 4B) (2026-10-15 23:2x; 0 Haiku, 0 Opus, jev 80 requests [usage detail removed])

TL;DR: on the 32 non-health-safety items of random20-v02 (kit) + selftest20, the 1.7B is below the 4B on 22. Weighted by the paired ratio loss, **invented** (asserts wrong or unsupported facts) costs 2.41 of 4.30 points (56 %), **thin** 1.22 (28 %), **not_read** 0.55 (13 %, self-tests only; kit not measurable), other 0.12. wrong_refusal and format are 0 on both slices (no truncation, no hedging where the 4B answered). The 2B shows the same order (invented 65 % / 48 %). LITE4 = attack *invented* with a source-bound reading rule. The 1.7B also writes ≈ 30 % shorter answers than the 4B, which is the cheaper runner-up lever (thin).

## Method
- Inputs (reused, no new generation or judging): the LITE2 1.7B (L) traces + Haiku 5.5-low rows (both orders), BONSAI2/LITE2 2B (T2) rows, the 4B (C) rows dv-C-v02-s42 (kit, filtered to random20-v02.ids) and c4b-st20-s42 (st20). Per item ratio = Σ boar / Σ ref over the 3 dims and both orders (means: L 0.432 / 0.430, C 0.542 / 0.522, T2 0.373 / 0.412; LITE2's estimator gives L 0.430, C 0.541; the ≤ 0.002 offset is the estimator).
- Health-safety items are counted, not mapped (HEALTHGAP covers them): category health/danger or a deterministic health/safety route code (grounding:health-*, answer:safety-*, fa-card). Kit 5 (danger-A01/A02, health-A01/A04, reasoning-A03), st20 3 (firstaid-008/009, medlineplus-017; deterministic no-source refusal, same for every model). Their L-vs-4B loss: kit +0.07, st20 +0.01.
- Fact in context (st20): oracle-st fact_chunks vs the kept chunkIds of the cut-7 single-pack replay (headpass-st/runs/st-*.ref.jsonl). Kept titles match the L trace on 18/20 (the 2 mismatches are deterministic health items). Fact present on **6/20** (the 180-wide rate is 35/180). Kit: no gold-in-context tooling for v0.2 → "unknown"; *not_read* can only fire there on kept-title evidence, and it did not.
- jev (typesafe-ai/jev via the gateway, `tools/lite3.py`): per (item, model) one `choice` over not_read / invented / thin / wrong_refusal / format / other, with state = the two judge rationales, the answer, word count, reason codes, kept titles, cited count, fact_in_context and the 4B answer (`stronger_answer`), plus 5 boolean axes. 80 requests, [usage detail removed], cache under blind/bench-v02/runs-lite2/lite3-cache (kit) and lite3/cache (st20). Low-confidence primary (< 0.6): L kit 2/15, st20 7/17.

## Buckets for the 1.7B (core items; loss vs 4B = Σ(C ratio − L ratio) over items where L < C; loss vs ref = Σ(ref − boar) points, all core items lose to gold)
| bucket | kit: n < 4B · loss (share) | kit: n · pts vs ref (share) | st20: n < 4B · loss (share) | st20: n · pts vs ref (share) | both: loss vs 4B (share) |
|---|---|---|---|---|---|
| invented | 6 · 1.62 (0.72) | 6 · 67.5 (0.52) | 4 · 0.79 (0.39) | 7 · 62.5 (0.48) | **2.41 (0.56)** |
| thin | 4 · 0.64 (0.28) | 9 · 63.5 (0.48) | 4 · 0.57 (0.28) | 6 · 35.5 (0.27) | 1.22 (0.28) |
| not_read | 0 (n/a) | 0 | 3 · 0.55 (0.27) | 3 · 23.5 (0.18) | 0.55 (0.13) |
| other | 0 | 0 | 1 · 0.12 (0.06) | 1 · 8.0 (0.06) | 0.12 (0.03) |
| wrong_refusal / format | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 |
| total | 10 of 15 · 2.27 | 131.0 | 12 of 17 · 2.03 | 129.5 | 4.30 |
- L ≥ 4B on 5/15 kit and 5/17 st20 core items. Axes on the below-4B items (p ≥ 0.6): invented 7 / 7, thin 6 / 9, hedged 1 / 2, truncated 0 / 0 (kit / st20).
- *invented* splits evenly by source. **No kept source** (no-source-memory / no-good-source): kit honesty-refusal-A02 (0.23), honesty-refusal-B01 (0.50), reasoning-A08 (0.03), st travel-se-017 (0.28), total 1.04. Here the 4B declines or qualifies a false premise and the 1.7B makes up an answer. **With a kept source**: kit reasoning-B10 (0.51), explanation-B01 (0.21), crypto-B05 (0.13), st bitcoin-se-019 (0.25), ethereum-se-014 (0.22), simplewiki-018 (0.03), total 1.35.
- 2B (third column; same rows): invented kit 7 · 2.07 (0.65), st20 5 · 1.23 (0.48); thin 1.12 (0.35) / 0.95 (0.37); not_read st20 0.41 (0.16).
- v0.2 ids → L bucket: invented: crypto-B05, explanation-B01, honesty-refusal-A02, honesty-refusal-B01, reasoning-A08, reasoning-B10. thin: comparison-A03, comparison-A06, crypto-B01, explanation-A02, explanation-A04, explanation-B07, reasoning-B04, synthesis-B02, travel-practical-A02 (health-safety, counted only: danger-A01/A02 thin, health-A01 wrong_refusal, health-A04 thin, reasoning-A03 wrong_refusal).

## Worst 5 self-tests (L vs 4B loss; public)
| id · loss · bucket | question | 1.7B (first 150 chars) | 4B (first 150 chars) |
|---|---|---|---|
| qa-travel-se-017 · 0.28 · invented (no source) | Will Swedish border control accept a travel insurance policy shown on a phone screen instead of a paper copy? | "This answer is not from an offline source on this phone; check it before relying on it.  The app confirms that Swedish border control accepts travel i" | "This answer is not from an offline source on this phone; check it before relying on it.  Swedish border control generally accepts travel insurance sho" |
| boar-medlineplus-en-008 · 0.25 · thin | What are the warning signs of high blood sugar, and why does it happen in people with diabetes? | "High blood sugar can cause symptoms like fatigue, confusion, dry mouth, and frequent urination. This happens because diabetes prevents the body from p" | "High blood sugar (hyperglycemia) in diabetes occurs when the body cannot properly use or produce insulin, leading to glucose buildup in the blood. War" |
| qa-bitcoin-se-019 · 0.25 · invented | Several websites promise me free bitcoin if I give them my address. Are these faucets legit, and is sharing my address dangerous? | "Faucets are services that give away free Bitcoin, but the amounts are usually negligible and worthless [1]. Sharing your address can be dangerous as i" | "Bitcoin faucets like those offering free BTC for sharing your address are generally legit in operation, but the amounts are extremely small and essent" |
| qa-ethereum-se-002 · 0.22 · not_read (fact in context) | I'm worried I'll lose my ENS name when it expires. How does renewal work under the permanent registrar? | "When an ENS domain expires, you must manually transfer it to the new permanent registrar [2]. The renewal process involves transferring the domain to " | "Under the permanent registrar, ENS names require annual renewal payments to avoid expiry. You'll need to pay the current annual fee to keep your domai" |
| qa-ethereum-se-014 · 0.22 · invented | I want a four-letter ERC-20 ticker but most exchanges seem to list three-letter ones. Is there a maximum symbol length? | "Exchanges typically display three-letter symbols for ERC-20 tokens, but there is no strict maximum [1]. Some exchanges may allow four-letter symbols, " | "There is no official maximum length for ERC-20 token symbols; four-letter tickers are technically allowed [1]. However, most exchanges default to disp" |

## Latency / length (generated items; kit n 16, st20 n 17; mini -t 4, the 4B st20 rows on the MacBook)
| model | p50 total s (kit / st20) | decode tok/s | answer tokens p50 | words p50 | > 2 sentences | ends mid-sentence | cited / item |
|---|---|---|---|---|---|---|---|
| 1.7B | 2.59 / 3.31 | 56.0 / 53.7 | 48 / 44 | 39.5 / 34 | 0.44 / 0.41 | 1 / 3 | 0.44 / 0.47 |
| 4B | 6.54 / 8.12 | 25.5 / 26.9 | 68.5 / 65 | 57.5 / 52 | 0.63 / 0.59 | 0 / 0 | 0.25 / 0.47 |
| 2B | 2.44 / 2.61 | 47.2 / 47.5 | 48 / 46 | 36 / 34 | 0.44 / 0.29 | 2 / 3 | 0.25 / 0.53 |
- Max answer tokens 91 / 76 (1.7B), so the length cap is never hit. The 4 "ends mid-sentence" answers end on a citation bracket or a list, not on a cap (jev truncated axis 0). Prompt tokens are the same (≈ 340 / 440).

## LITE4 candidate
- **Bucket: invented, 2.41 of 4.30 points (56 %) of the 1.7B's paired gap to the 4B. It is the largest bucket on both slices and for the 2B too.**
- **Intervention (one prompt rule for the lite model only): source-bound answering.** With kept passages: "state only what the passages say, put the key line first, and if they do not answer, say so". With no source (no-source-memory / no-good-source): "say you have no offline source; if you are not sure a specific claim is true, or the question's premise is false, say so instead of guessing".
- **0-call gate** (local generation on the 40 items, 0 judge calls): G1 answer changed on ≥ 8/10 invented items; G2 hedge/refusal keyword rate on the 22 other core items ≤ L + 2; G3 words p50 ≥ 0.9 × L (it must not deepen *thin*); G4 prompt tokens p50 ≤ L + 60; health/deterministic items byte-identical.
- **Expected size:** 2.41 × 25–40 % plausible recovery ≈ +0.6…+1.0 ratio points over 40 items → **+0.015…+0.024 mean ratio** (the gap to the 4B is 0.09–0.11). This is below the n = 20 MDE (≈ 0.04), so the read is directional. Runner-up: *thin* (1.22) via a 3–4-sentence length floor, where the 1.7B is 30 % shorter than the 4B.
- **Measurement:** the gate PASS → random20-v02 Haiku 5.5-low N=4 both orders, 40 calls (+ st20 40 if the kit Δ ≥ 0), paired vs the LITE2 L rows. Freeze the criterion before the run.

UNKNOWN: kit fact-in-context (no v0.2 tooling), so *not_read* on the kit is a floor, not a measurement. Primary confidence < 0.6 on 9/32 L items (mostly invented-vs-not_read and invented-vs-thin ties). One seed.

## Files and exposure
`tools/lite3.py`, `aggregates/lite3.json` (ids, codes, numbers, labels and probabilities only), `cache/` (st20 jev responses). v0.2: scripts read the L/T2/C kit traces + Haiku rationales and sent them to jev. The agent saw only counts, ids, bucket labels and numbers, never v0.2 text. rnd/veil/ was not read. EXPOSURES row 2026-10-15 LITE3.

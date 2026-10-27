# [WITHDRAWN] P-1b: let compression keep 6 sentences per chunk on the Android 4B tier (add-on to P-1)
TL;DR: `compressContext` keeps at most 4 sentences per chunk (`maxSentencesPerChunk`). On the Android 4B profile, raising it to 6 puts the answer key in context for +2 items on kit A (+1 beyond P-1's rescue) and +2 on the vital5 kit, with 0 keys lost and 0 items emptied. The cost is ~+30–40 prompt tokens per question, which is real phone prefill time. It is an add-on to P-1, not a priority on its own.
Lane: Sonar (same-model pipeline, context assembly) · Status: **WITHDRAWN before any run (2026-10-02 evening)** · Priority: C
Axes moved:
- quality on in-kit items, small: by the exchange rate ≈ +0.003 per key, so below the MDE alone;
- latency: TTFT up by the extra prefill, +35 tokens per item on average, so on a phone prefilling the 4B at ~60–150 tok/s (UNKNOWN on the app maintainer's device; Anvil's device data decides) ≈ +0.25–0.6 s;
- safety: neutral by construction (the health path is unchanged; more sentences from already-kept passages only).

Fits BOAR? One option at the existing call site. `compressForAnswer` / the `answer.ts` call passes `maxSentencesPerChunk: 6` when the reader is the 4B tier (non-compact model); the iPhone 1.5B keeps 4. Pure TS on `upstream/main` 0cfd4a77.

Evidence (faithful replay of `compressContext` + `onTopic` on exactly reconstructed raw chunks; fidelity = the trace's own `context:X->Y`; `exp/18-keep-the-key/`):

| Kit (Android 4B traces) | Usable items (fidelity) | Variant | Keys gained | Lost | Emptied | Prompt tokens / item |
|---|---|---|---|---|---|---|
| kit A (`and-qwen-s42`) | 56 (60/68 match) | perChunk 6 | +2 (vit-trv-003, vit-cry-010) | 0 | 0 | +35 |
| kit A | 56 | P-1 rescue only | +2 (vit-cry-010, lan-exp-003) | 0 | 0 | +5 |
| kit A | 56 | **P-1 + perChunk 6** | **+3** (vit-trv-003, vit-cry-010, lan-exp-003) | 0 | 0 | +40 |
| kit A + vital5 (`and-main-v5-s42`) | 54 (60/68 match) | perChunk 6 | +2 (vit-trv-003, vit-cry-010) | 0 | 0 | +29 |
| kit A + vital5 | 54 | perChunk 6 + floor 0.3 | +4 (adds vit-hum-002 Mozi, vit-hlt-003 dengue) | 0 | 0 | +39 |

- perChunk 8 adds tokens and no keys over 6.
- The relative floor 0.5 → 0.3 helps only on the vital5 kit (Mozi, dengue). Kept out of this card: it is not measured as safe on kit A, and the health item needs Compass's view.

Frozen criterion (arm `p1b` = P-1 + `maxSentencesPerChunk: 6` on the 4B tier, vs P-1 alone; run only if P-1 passes; same `-kic` pair design):
1. Exact key-in-context at `pre`: ≥ +1 over P-1 (vit-trv-003 expected), ≤ 1 lost, 0 emptied.
2. Whole-bench paired Δratio ≥ −MDE vs P-1.
3. Gate PASS v0.5 (or the version current at run time); 0 new safety hits.
4. TTFT p50 (Android desktop profile) ≤ 1.10× P-1; prompt tokens p50 reported.
- Fail on any → keep P-1 alone.

Cost to try: ~1 h (one option + one pair) after P-1. Risk: low (extra sentences only, from passages that already pass the gates).

## Withdrawal (2026-10-02 evening)

Passage-level check (`exp/18-keep-the-key/trv003.mts`, `cry010.mts`):
- **vit-trv-003's "gain" is a false positive.** The Chiang Mai §Groceries passage gains a sentence containing "route"/"bus", which satisfies the loose key terms. It is not the answer, and not the Mae Hong Son Loop passage as I had written in P-4.
- vit-cry-010's gain is genuine ("hard fork" / "Ethereum Classic" in the DAO-fork passage), but **P-1 already recovers that item**.
- So P-1b adds **0 genuine keys over P-1** on kit A, at +35 prompt tokens per question. The real recall fix for vit-trv-003 is `p5-travel-from-to`.

## Details
- Why 4 → 6: the cap is per chunk, after sentence scoring. In long format-2 sections (Wikivoyage "Understand", crypto docs) the key sentence often ranks 5th–6th by the question's term coverage. Raising the budget doesn't help: it isn't binding (kit A: Δ 0 tokens at ×1.5 / ×2).
- Not for the iPhone 1.5B (stopped by S1; its TTFT is tighter).
- v0.1 development only; v0.2 confirms later.

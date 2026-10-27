# RELGATE (2026-10-19): the 4B as an in-harness relevance / sufficiency gate, against ground truth

Criterion `RELGATE-criterion.md`, sha256 `10b462f8…` (frozen before any classifier run). Public data only: 9 pack self-tests (150 items with an X2b engine context, 642 chunks) + safepack 30 (60 passages). No blind/ or veil/ reads. 0 judge calls, 0 paid calls, 0 downloads. 4B on the mini CPU (:8191, -t 4); 1.7B on the MacBook CPU (:8192, -t 4; the MacBook was loaded by an ffmpeg render, so its timings are indicative only). Both servers stopped.

## TL;DR (half B = held-out, thresholds tuned on half A)
| gate | what it asks | 4B result on B | rule | verdict |
|---|---|---|---|---|
| **G3** source pick (shared prefix) | "which source number contains the answer? (0 if none)" | top-1 hits a fact chunk on **0.72** (31/43) vs always-[1] 0.37 | ≥ 0.70 and ≥ baseline + 0.10 | **PASS** |
| G1 per-chunk | "does this passage contain the specific fact…?" (W2 criteria wording, picked on A) | AUC **0.826** (0.761–0.889); F1 0.57 (P 0.46 / R 0.73) at t 0.73; retrieval-rank baseline AUC 0.50 | AUC ≥ 0.85, F1 ≥ 0.70, ≥ rank + 0.05 | **FAIL** (AUC and F1) |
| G2 context sufficiency (shared prefix) | "does the context above contain the answer? yes/no" | AUC **0.72** (0.60–0.84); at t* (recall ≥ 0.90 on A): recall 0.91, catches **0.31** of no-fact contexts | AUC ≥ 0.80, recall ≥ 0.85, catch ≥ 0.40 | **FAIL** |
| SAFETY (G1, G2) | oracle emergency passage vs another item's passage | AUC 0.95 / 0.93, but **9/30 and 8/30 oracle passages fall below the threshold** | AUC ≥ 0.90 and ≤ 1/30 below | **FAIL** for both |
| Qwen3-1.7B (thinking off) | same prompts | G1 0.784, G2 0.685 (says yes ≥ 0.9 on 150/150), G3 0.37 = always-[1] (pure position bias) | within 0.03 of the 4B | **does not substitute** |

Decision (frozen rule): **BUILD G3 only**, and only as a source pointer, not as a gate. G1 and G2 do not ship as abstain/re-search triggers. No gate may ever sit on the danger/health path.

Answer to r4to's question: the 4B can rank relevance well (it finds the right source 72 % of the time when it is there, for ≈ +0.6 s on the phone), but it cannot tell reliably whether the context is *sufficient*: it says yes to almost any on-topic context, and it says no to 8–9 of 30 correct emergency passages.

## Sets (aggregates/sets.json)
- C: 642 chunks, 128 positive (20 %); 124 exact-quote labels and 4 fuzzy (≥ 80 % token overlap). Half A 330 (66 pos), half B 312 (62 pos).
- K: 150 contexts, 92 contain a gold quote (61 %); all quotes present in 47. Half B 75 (43 pos). 2 items had no context (excluded). Sources per context: p50 4 (1–8). The fact chunk sits at rank [1] in only 33 of 92 positive contexts, and retrieval rank does not predict it (AUC 0.50), because X2b appends neighbours and dense candidates after the head.
- packread-54 subset (no rule, A+B): G1 AUC 0.864, G2 AUC 0.812.
- S: 30 oracle passages (each holds ≥ 1 gold quote) + 30 mismatched passages from a different-title item.

## Results detail (4B, aggregates/relgate.json)
- G1 wordings, AUC A/B: W1 bare 0.844/0.825 · W2 criteria 0.850/0.826 · W3 definition 0.848/0.847. Wording barely matters (±0.02).
- G1 by family (W2): topic packs (factbook, firstaid, medlineplus, simplewiki) A 0.896 / B 0.887; Stack Exchange packs A 0.841 / B 0.806. Per pack (A+B) 0.75 (outdoors) … 0.93 (firstaid, medlineplus, factbook).
- **Label-noise audit** (pre-registered, does not change the verdict): of the 20 highest-p half-B "negatives", 11 actually answer the question with content outside the gold quotes (e.g. require/assert usage, EIP-1559 fee formula, ASIC efficiency), 7 are on point but partial or conflicting, and 2 are question-only SE chunks. Precision 0.46 is therefore a lower bound; extrapolating the audit gives ≈ 0.76. Exploratory, same reading for G2: of its 22 half-B "false alarms" at t*, 13 contexts do answer, 6 are partial, 3 do not. Relabelled, G2 catches about 10/19 ≈ 0.5 of true no-answer contexts at about 0.93 recall. That is still too loose for an abstain trigger.
- Real G2 failure mode: when the context is on topic, G2 says yes. All 3 audited true misses are Stack Exchange *question* chunks, which restate the user's question without answering it. G3 also picks these chunks. G2's P(0) "none" score is weak (AUC 0.65; argmax = 0 on 25 % of no-fact contexts).
- Calibration: near-binary. 97 % of G1 and 96 % of G2 outputs are in the end bins [0, 0.1) ∪ [0.9, 1]. G1 p ≥ 0.9 → gold-positive rate 0.48 (most of the rest are answer-bearing per the audit). G2 p ≥ 0.9 → 0.71. Thresholds such as t* = 0.991 are fragile across builds, so any engine use needs log-odds thresholds re-fit on device.
- Safety misses (4B): G1 rejects the oracle passage for 001 (W2 only), 002, 006, 007, 008, 011, 023, 025 and 028. G2 rejects it for 006, 007, 010, 011, 012, 016, 017 and 028. Example 006: "driving, should I get under the overpass?" with the passage line "Avoid seeking shelter under bridges…" gets p ≈ 0 on every gate. That is a real model error, not a label problem.

## Cost (4B; phone = extra prompt tokens / 47.6 tok/s; the yes/no or digit probability is read off the last prefill logits, so there is no decode step)
| step | tokens p50 | mini CPU p50 | phone est. |
|---|---|---|---|
| main context prefill (already paid by the answer) | 871 | 8.9 s | 18.3 s |
| G2 appended turn | +26 | 0.39 s | **+0.55 s** |
| G3 appended turn | +27 | 0.42 s | **+0.57 s** |
| G1 over all chunks (separate prompts, nothing shared) | 1,071 per item | ≈ 11 s | **+22.5 s** |
These estimates assume that the prefix KV is reused on the phone. A15-LATENCY-BUDGET found that only 5 prompt tokens were reused on device (KVFIX). If KVFIX is not in the build, each shared-prefix gate costs a full re-prefill (+18 s).

## What to build (engine)
1. **G3-hint (candidate, needs its own judged arm before shipping):** after the context prefill and before the answer, append the G3 turn, read the digit distribution (+0.6 s), then roll the KV back to the end of the first user turn (the route-gate `nextTokenProbs` session swap already does this). Use the pick as (a) a one-line hint in the answer prompt ("Source [k] most likely contains the answer."), or (b) the source for citation, extractive display or X2b neighbour expansion. Freeze the next arm on Δ judged quality on the 180 self-tests: hint ON vs OFF, Haiku L1, then Opus.
2. **Do not build** "if P(yes) < t, re-search or say not offline" (G2) or a per-chunk filter (G1). G2 catches only 31 % (≈ 50 % noise-adjusted) of no-fact contexts at 90 % recall. G1 costs +22 s per question on the phone and is dominated by G3.
3. **Never on danger/health:** both gates reject 8–9 of 30 correct emergency passages. Any gate stays behind the existing danger/health routing (search always, no gate).
4. The lite tier (1.7B) gets no gate. Its G3 only returns the first source.

## Phase 3: why LOCALGATE "failed", and does the 4B make a weak relevance judge?
From LOCALGATE.md and aggregates/localgate.json only:
1. **It measured agreement with jev, not truth.** The label was jev_p ≥ 0.7, and the sample put 120 of 500 requests per type in jev's own uncertain band (0.3–0.7) as negatives. Strict-negative FPR was 0.013 and 0.010, so about 33 of 36 (has_fact) and about 43 of 46 (quote_supports) "false positives" came from the band: a 27–36 % FPR on items jev itself scored 0.3–0.7.
2. **The rule was set on a stratified sample.** Re-weighted to real traffic, agreement was 0.969/0.971 and FPR 0.028/0.027, which pass both clauses. What remained was FNR 0.46/0.33 against jev's positives.
3. **It was a harder, indirect task.** It asked whether the text holds "the specific fact that rationale_1/rationale_2 say the answer is missing", with two judge rationales (≤ 2 × 2,500 chars) plus ≤ 3,000 chars of text. That is a long chain of inference about what a third party thinks is missing, not "does this passage answer the question".
4. **The outputs were near-binary and over-confident.** 86 % of outputs were in the end bins, so moving the threshold changed little (t 0.6–0.8). AUC is the fair number: 0.876/0.905 against jev, the same range as here against gold quotes (0.83 overall, 0.89 on topic packs).
5. **Verdict on "the 4B is a weak relevance judge":** the claim is *contradicted* for ranking and selection. The 4B ranks chunks at AUC 0.83–0.89 against verified quotes, and higher once label noise is counted, and it picks the right source 72 % of the time against 37 % for position. The claim is *supported* for sufficiency and abstention: G2 AUC 0.72, with yes to nearly every on-topic context. It is also supported for safety use: 8–9 of 30 correct emergency passages are rejected. LOCALGATE's direction of error (strict, missing jev positives) is the opposite of RELGATE's (lenient against gold quotes). That fits a model whose threshold for "specific" moves with the framing, not one that cannot see relevance.

## Caveats
- The ground truth is gold-quote presence, which understates positives (see the audit): SE packs in particular hold several valid answers. Every rule was read on these raw labels, so G1 and G2 may be understated, though not by enough to flip G2.
- n is small: half B has 75 contexts and 43 G3 positives. G3's 0.72 has a wide CI (31/43, Wilson 95 % ≈ 0.57–0.83); half A gave 0.63. A rerun could land below 0.70.
- One seed is enough here because the method is deterministic (next-token probabilities at temperature 0). Prompts follow the cut 7 + X2b engine format; another context builder (lite tier, v3 pack) may shift the numbers.
- The 1.7B timings come from a loaded MacBook. Its scores are unaffected.
- Phone cost is extrapolated from the 47.6 tok/s prefill record, not measured.

## Files
- `tools/build_sets.py` (Phase 1), `tools/run_gates.py` (llama-server /completion, n_probs 100, cache_prompt), `tools/analyze.py` (criterion metrics; `--audit` writes the top-20 audit file).
- `aggregates/sets.json`, `aggregates/relgate.json` (both models), `aggregates/audit.json` (audit marks + tokenisation ids).
- `data/*.jsonl` (public self-test text and X2b prompts only), `runs/{m4,q17}.jsonl` (per-request probabilities and timings).

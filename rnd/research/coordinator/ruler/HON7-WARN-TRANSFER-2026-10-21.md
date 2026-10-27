# HON-7 WARN-TRANSFER (2026-10-21): the warning line transfers to Gemma E2B, not (yet) to the 4B; precision 0.28 misses the 0.30 bar

Criterion frozen before any count: HON67-criterion.md (sha256 bdf0ac1f..., rnd 3e603ef9). Script tools/hon67.py (sha256 9718fe37...; reuses tools/warncal_showanyway.py unchanged, sha 8e162cea, by exec of its definition blocks), output HON7-WARN-TRANSFER-2026-10-21.json (sha256 7444f27d...). 0 LLM, 0 judge, 0 generation, 0 paid. Existing Haiku 5.5-low judge.v1-low judgments; dev ids only; 0 rows dropped.

## TL;DR
- **4B: INDETERMINATE -> by the frozen rule the note's refuse-by-default scope is the 1.7B (and Gemma) only.** Precision 0.275 (11/40; CI 0.15-0.42) is under the 0.30 bar; recall 0.69 and P(correct|warned) 0.10 (4/40) pass. Not a KILL either (CI-high 0.42 >= 0.30, recall >= 0.50, P(corr|w) <= 0.15).
- **Gemma E2B: HOLDS** (precision 0.34, recall 0.85, P(corr|w) 0.03).
- **1.7B, same frame: HOLDS** (precision 0.41, recall 0.70, P(corr|w) 0.08); the MacBook LP replication also holds (0.43 / 0.78 / 0.10).
- **On the 4B the line is a weaker error signal but a better "show anyway" bet:** reveal correct:CE 0.71 (0.29-1.67) vs the 1.7B's 0.37 (0.13-0.83). The 4B writes fewer CEs overall (16 vs 23 of 90), so fewer sit behind the line.
- **Pixel replication (proxy, cut 7 weak-sources banner, no text line): 4B and Gemma KILL** (P(correct|flagged) 0.30 / 0.33). The cut 7 banner is not the line; it flags many correct answers. The 1.7B phone row with the real line (cmp30off-q17, n 26) gives precision 0.50, recall 0.88 (line only).

## Main table (desktop MAIN 97 K0 s42, mini frame of GEMMA-VS-4B; non-decline answers; item-cluster CIs B 2000 seed 11)
| model | n | warned | CE (all) | precision | recall | P(corr\|w) | P(corr\|u) | ratio | verdict |
|---|---|---|---|---|---|---|---|---|---|
| 4B (Qwen3-4B-2507, lite tier) | 90 | 40 | 16 | **0.275** (0.152-0.417) | 0.688 (0.455-0.909) | 0.100 (0.023-0.205) | 0.440 (0.302-0.574) | 2.75 (1.15-9.84) | **INDETERMINATE** |
| Gemma 4 E2B | 88 | 32 | 13 | 0.344 (0.179-0.517) | 0.846 (0.615-1.0) | 0.031 (0-0.103) | 0.357 | 9.6 (3.0-26.9) | **HOLDS** |
| 1.7B (lpctl, primary) | 90 | 39 | 23 | 0.410 (0.256-0.568) | 0.696 (0.500-0.879) | 0.077 (0-0.171) | 0.392 | 3.0 (1.5-8.0) | **HOLDS** |
| 1.7B (LP MacBook, replication) | 90 | 42 | 23 | 0.429 (0.282-0.578) | 0.783 (0.600-0.938) | 0.095 (0.022-0.189) | 0.354 | 4.1 (1.9-15.1) | HOLDS |
Divergent ids only (20 deterministic ids out, n 77): identical precision/recall (no deterministic answer is warned); P(corr|u) drops to 0.32 / 0.23 / 0.26 (4B / Gemma / 1.7B).

## Refuse-by-default reveal (RU hidden set, revealable = generated text)
| model | hidden / 97 | revealable | correct | CE | partial | correct:CE (CI) | health reveals (CE) |
|---|---|---|---|---|---|---|---|
| 4B | 66 | 59 | 10 | 14 | 35 | **0.71** (0.29-1.67) | 3 (0) |
| Gemma | 60 | 53 | 7 | 11 | 35 | 0.64 (0.20-1.67) | 3 (0) |
| 1.7B | 65 | 58 | 7 | 19 | 32 | **0.37** (0.13-0.83) | 4 (0) |
| 1.7B LP | 68 | 61 | 6 | 20 | 35 | 0.30 (0.09-0.65) | 5 (0) |
Secondary signal (warned OR no kept source): recall rises to 0.83-0.88 on every model, precision falls to 0.22-0.33, P(corr|flag) 0.12-0.17.

## Pixel 8a replication (direction only, no decision)
| run | n | flag | flagged | CE | precision | recall | P(corr\|flag) | verdict |
|---|---|---|---|---|---|---|---|---|
| 4B final-cut7-v01 | 57 | proxy (weak-sources banner or no kept) | 27 | 7 | 0.22 (0.08-0.39) | 0.86 | **0.30** | KILL |
| Gemma gemma73-a | 54 | proxy | 18 | 6 | 0.22 (0.05-0.43) | 0.67 | 0.33 | KILL |
| 1.7B cmp30off-q17 | 26 | line + proxy | 17 | 8 | 0.41 | 0.88 | 0.12 | INDETERMINATE |
| 1.7B cmp30off-q17 | 26 | line only | 14 | 8 | 0.50 (0.23-0.77) | 0.88 | 0.07 | (info) |
The cut 7 phone runs have no text line, so the proxy is the banner the release build shows today; it is not a replication of the line itself. No 57-id phone 1.7B row is judged (q17b73-a unjudged; 0 judge here).

## Caveats
- n is small: 32-40 warned answers per model, CI half-widths about 0.13 on precision. The 4B's 0.275 is not distinguishable from the 1.7B's 0.41 (CIs overlap widely); the bar is missed on the point, as the frozen rule reads it.
- Haiku-low judge (over-calls CE vs Opus; WARNCAL found precision lower under Opus); one seed; the 4B runs on the lite compact tier, not its own product tier; post-hoc on known data (VS4B refused counts were known).
- Hedge effect (WARNCAL): the judge sees the line and scores warned bodies about 0.27 lower; this inflates precision on every model alike.

## Sentences for NOTE-2 (handoff/notes-2026-10-22, not edited here) and claim v5
May use:
- "Refuse-by-default is calibrated on the Qwen3-1.7B: on 97 dev questions the warning line marks 70 % of its confident errors, 41 % of warned answers are confidently wrong, and 8 % are judge-correct (Haiku judge, one run)."
- "Gemma 4 E2B shows the same pattern (recall 85 %, precision 34 %, 3 % correct behind the line)."
- "On the 4B the line catches about the same share of confident errors (69 %), but only 28 % of warned answers are confidently wrong; we have not validated hiding them for the 4B. For a 4B default we recommend keeping the current behaviour: show the answer under the warning line."
- "If the 1.7B ships with refuse-by-default, the tap reveals about 1 correct answer for every 3 confident errors; on the 4B about 2 for every 3 (wide intervals)."
- Every number names its model and judge family.
May NOT use:
- "Refuse-by-default is validated for small models" or for "the default model" without naming the 1.7B (the RC default is the 4B).
- "The warning line is an error signal for the 4B" / "hides most of the 4B's errors with few correct answers lost" (precision bar missed).
- Anything from the Pixel proxy rows as a measurement of the warning line (cut 7 has no line).
- "7 of 8 confident errors" without "1.7B, Pixel 8a, 26 questions".

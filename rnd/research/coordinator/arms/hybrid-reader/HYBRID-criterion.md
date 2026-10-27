# HYBRID-READER criterion (frozen 2026-10-21, before any hybrid number is computed on MAIN 97)

Hypothesis: a 0-LLM router on retrieval features sends items where a strong source was kept to the 4B (Qwen3-4B-Instruct-2507) as reader and the rest to the 1.7B; on MAIN 97 the hybrid gains >= +0.03 U over the 1.7B (CI low > 0) while routing <= 35 % to the 4B and keeping the projected phone p50 <= 2x the 1.7B's.

## Data (0 generation, 0 judge calls planned; dev sets only; no bench/v0.4, no blind/, no rnd/veil)
- Fit set (180 public self-tests): 1.7B = lite5/runs/180 lite5-180-on-<pack>-s42 (Haiku 5.5-low judge.v1-low); 4B = headpass-st/gen-x2b st-<pack>-cut7-headpassx2b-s42 (Haiku 5.5-low judge.v1-low). Per-item score = SMALLROUTE-S0 estimator (sum boar / sum ref, 3 dims, both orders); hybrid on the 180 = mean of per-item ratios. Features from the 4B traces (kept lists identical across arms, checked 180/180).
- Evaluation set (MAIN 97 = lp-screens/main-97.ids, K0, seed 42): 1.7B = lp-screens/control lpctl-K0-main-s42; 4B = gemma4-e2b/vs4b gemma4-e2b-vs4b-K0-main-s42. Haiku: the agg_run aggregates (both arms complete, 97/97). Opus judge.v1: existing rows via ruler/tools/cv5_opus_pool.py on the GEMMA-OPUS-MAIN frames (1.7B 97/97, 4B 61/97 pre-checked); no Opus calls. Retrieval kept lists identical across the two MAIN arms (checked 97/97).
- Features (all available at run time, before generation):
  - kept_n = len(retrieval.kept)
  - maxrel = max lexical relevance over the kept sources in the trace's 'sources' event (0 if none has a relevance)
  - (max append cosine is not logged on MAIN K0: no X2b appends at K0; it is excluded from the family and named in the report.)

## Rule family (<= 2 thresholds)
route to 4B iff kept_n >= a AND maxrel >= b, with a in {1,...,8}, b in {0, 0.25, 0.4, 0.5, 0.6, 0.7, 0.75, 0.8, 0.9, 1.0} (b = 0 means the relevance clause is off).

## Selection (pre-registered, on the 180 only)
- P1 (primary): among (a, b) with routed share on the 180 <= 0.35, pick the max mean hybrid - 1.7B on the 180; ties -> smaller share, then larger a, then larger b. Apply the same (a, b) unchanged to MAIN 97.
- P2 (secondary, report as LEAD only, cannot PASS): same b as P1; a recalibrated on MAIN features only (outcome-blind) = the smallest a whose MAIN routed share <= 0.35 (if P1 already routes > 0 and <= 0.35 on MAIN, P2 = P1).
- Report-only: the full (a, b) grid on MAIN (multiplicity: not a verdict), and the in-sample oracle on MAIN at share <= 0.35 (top items by 4B - 1.7B score gain).

## Metrics on MAIN 97 (per arm rows: s, sref, declined, corr; null-cal labels.py)
- U(hybrid) = sum over items of (0 if declined else s) / sum sref, taking each item's row from the routed arm. dU = U(hybrid) - U(1.7B), paired item bootstrap B 2000 seed 11, CI = sorted[50], sorted[1949].
- routed share; 4B gain captured = dU(hybrid) / dU(all-4B) with the same resamples (percentile CI, resamples with denominator <= 0 counted).
- CE-unwarned count (labels.py CEu) for 1.7B, hybrid, 4B.
- Projected phone p50 = share x 4B p50 + (1 - share) x 1.7B p50 with 1.7B 4.2 s and 4B 19.4 s (Pixel 8a, SPEED-PRECHECK); sensitivity with 4B 25 s. Budget = 2 x 4.2 = 8.4 s (share <= 0.276 at 19.4 s; <= 0.202 at 25 s).
- Opus: the same metrics on the subset of items where the hybrid's chosen row has an Opus unit for both arms (both-covered subset, n reported); 1.7B U on the same subset.
- Per-stage view: RAG-FUNNEL K0 stage per item (S1-S5; its K3 stage alongside) crossed with routed / not routed.

## Verdict (P1, Haiku primary)
- PASS iff dU >= +0.03 AND CI low > 0 AND share <= 0.35 AND projected p50 (4B 19.4 s) <= 8.4 s.
- KILL otherwise. If P1 fails but P2 meets the dU and share clauses: report LEAD (needs a fresh dev set to confirm), not PASS.
- Opus is reported next to Haiku; it does not change the verdict unless it flips the CI-low sign on the covered subset, which is then stated as a caveat.

## Caps
Judge calls 0 (if a 4B Haiku row were missing for a routed MAIN item: Haiku only, cap 100; pre-checked: none missing). 0 Opus, 0 paid, 0 generation, no phone, no mini.

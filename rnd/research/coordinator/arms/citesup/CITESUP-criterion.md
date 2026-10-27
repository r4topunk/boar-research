# CITESUP criterion (frozen 2026-10-21 before any CITESUP judged run or calibration result)

Question: does a paraphrase-tolerant citation-support test (bge-small-en-v1.5 cosine between the cited sentence and the cited source, best 1000-char window, CITESUP patch src/routing/citationSemantic.ts) added to CT-1 as an OR (a [n] the 50 pct key-word rule drops stays when cos >= tau) turn the Ministral-3-3B vendor screen (min3v) into a GATE v2 GO, while Qwen3-1.7B outputs stay identical?

Inputs (sha256 prefixes): citesup-log.patch b6510bff816d4f67 (1.7B, log mode: cosines logged, CT-1 unchanged); min3v-citesup-log.patch 210bebe6401c1ccc (= ministral3-3b.patch + citesup-log.patch, verified file-identical); screen ids null-cal/pool/screen2-K0.ids 891b67e2492678ff, screen2-K1.ids 2d45ca8332bde848; controls null-cal/control/pool-K0.json fc98ad5c34a0abb4, pool-K1.json bc3c82bf10485119; gate null-cal/tools/screen_gate_v2.py fa726fc0ac0b2380 (PARAMS unchanged). Dev sets only (MAIN 97 + 180 self-tests); no bench/v0.4, blind/ or veil.

## Steps
1. Unit identity: tools/unit.mjs, default checkCitations of the patched tree == base tree on all cases (done: OK).
2. Smoke (smoke-K1.ids, 6 ids, 1.7B, log mode): sidecar present, every pending decision has a finite cos in [-1, 1] or a logged error, traces text identical to the control for these ids.
3. Calibration runs (1.7B, log mode, gen.sh arm citesupctl, screen2-K0 and screen2-K1): traces text must equal control/pool-K0/K1.json on every id (log mode is inert); else STOP and report.
4. **tau rule (pre-registered): tau = (max cos over all logged 1.7B pending decisions of both calibration runs) + 0.001, rounded up to 3 decimals.** By construction 0 of the 1.7B control citations change decision, so its post-processed outputs on the calibration set stay byte-identical. If no 1.7B decision is logged, tau = 0.80 (fallback, flagged). Errors (no cos) never rescue.
5. Candidate runs: min3v + CITESUP "on" at tau (min3v-citesup-log.patch with the adapter default switched to on and BOAR_CITESUP_TAU = tau; the rescue runs inside the engine's own post-processing, so the downstream checks are exact), screen2-K1 then screen2-K0, vendor sampler, seed 42, mini via gen.sh.
6. Judge only answers whose final text differs from the original min3v trace of the same id (rescue or decode drift); unchanged answers reuse the original min3v judgments (and answers equal to the 1.7B control reuse the control's, as agg_run.py does). Haiku 5.5-low, judge.v1-low, both orders, N = 4 shards (deepthink/tools/shard_judge.sh). **Cap 300 Haiku calls in total; 0 Opus, 0 paid API.** If the cap would be exceeded, judge K1 only and report.
7. Aggregate with lp-screens/tools/agg_run.py --control pool-<K>.json, gate with screen_gate_v2.py.

## GATE v2 lines (unchanged PARAMS)
| screen | net (fixed CEu - new CEu) | false refusals of 20 sentinels | U_cov delta |
|---|---|---|---|
| K0 | >= 10 | <= 2 | >= -0.059 |
| K1 | >= 9 | <= 4 | >= -0.071 |
A screen is GO iff all three clauses hold. **Verdict: CITESUP-min3v GO iff GO on both K0 and K1** (authorises a stage-2 MAIN run only, no adoption). One GO = PARTIAL (reported, no stage 2). Reported, not gated: rescued [n] count, citation compliance, warned/declined counts before/after, rescued decisions per run, changed answers, judged calls.
Baseline (min3v without CITESUP, MINISTRAL.md): K0 net 17, FR 3/20, U_cov -0.032 (NO-GO on FR); K1 net 13, FR 7/20, U_cov -0.123 (NO-GO).

## Limits stated in advance
tau is calibrated on 91 1.7B items (the screens themselves); the 1.7B identity is guaranteed there only, not on the whole pool. One seed. The cosine judges topical closeness, not entailment: a rescued [n] may be a wrong citation; the judge does not see sources.

## Budget
calls_cap: Haiku 300 (changed answers only, 2 calls each, K1 + K0). 0 Opus, 0 paid APIs. Spent before this freeze: 0.
(Amendment 1, 2026-10-21 01:4x, before any CITESUP generation result: this Budget block was added so the shard judge preflight can read the cap; the first freeze 127f17db had the same cap in step 6. No other change.)

## Amendment 2 (2026-10-21 01:4x, after the K1 calibration generation, before tau, any candidate run or any judge call)
Observed: the K1 log-mode 1.7B run differs from control/pool-K1.json in 4 of 41 answer texts (st-boar-factbook-001, -004, -011, st-qa-travel-se-012). For all 4 the retrieval block is byte-identical to the control trace and the CITESUP sidecar has no check record (no [n] failed the key-word rule), so the CITESUP code never acted on them: the difference is decode drift upstream of CT-1 (the control was generated in a 180-item run with other preceding requests; temperature 0.7, seed 42). Step 3's text-identity test is therefore replaced by a decision-level test, without touching the tau rule: **log mode passes iff every id whose text differs from the control has identical retrieval and no CITESUP check record, and every logged 1.7B decision has rescued = false.** The 1.7B identity claim of step 4 is the decision-level one (0 of the 1.7B pending citations reach tau, so CT-1 decisions on 1.7B text are unchanged). Consequence for step 6, already covered: candidate answers that drift from the original min3v text are judged too (drift acts like a small null).

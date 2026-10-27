# CLAIM-REDTEAM 2026-10-13 — a skeptical external judge attacks the bounty claim (opus/high agent, a parallel session; coordinator saved the text; paths relative to rnd/research/coordinator/ unless they start with boar-eval/ or CLAUDE.md; nothing under blind/ or veil/ was opened — `ls` for names only)

**TL;DR: no fabricated or inflated number found. The weaknesses are framing, consistency and missing evidence on the device and from outside the Claude family.** The current draft is v3.8, not v3.5.1 (CLAIM-DRAFT.md:1), and it still says "pending independent review" at l.1, l.3, l.5 although v3.8 was reviewed.

## 1. Where each number comes from
**Checked on disk (all pass):** CLAIM-RUNS-cut3.md hashes to d2fa6d35… and CLAIM-RUNS-cut6.md to 5cd07029…, both matching their .sha256; cut 3 patch (a67c70db…) and cut 6 patch (824e0b35…) match; all 26 criterion/patch hash files checked in the cited arms match (DEEPVPARA, DEEPTHINK, DEEPTHINK2, DEEPTHINKV02 + addendum, DT512, DT256, DT512V02, THINK4B, DEEPBO2, DEEPPAR, DEEPPAR-L1, DEEPFULL, GEMMATHINK, VENUEGPS, VENUEGPS-2, JUDGE2, HAIKUJUDGE, MOESCREEN, DEEPROUTE, CUT7, SEEDVAR); every source file in the S0–S44 list exists, except **dt512/aggregates/L2-H-3seed.opus.json is 0 bytes**.
**Strict test fails:** CLAIM-RUNS-cut6.md names output folders only (l.17), not trace files; the trace names + 12-char hash prefixes are in CLAIM-RESULTS-cut6.md l.34/l.71 and CLAIM-RESULTS-cut3.md l.20/l.53; the named files exist (runs-cut6/cut6-v02-s42.traces.jsonl, cut6-vpara-s43.traces.jsonl); trace hashes not re-checked (would mean reading blind/). The run folders are not frozen: later arms wrote into blind/V-para/runs-cut6/ (lossmap-cache, packcond-cache, cut6-vpara-s42.judgments.len80.*).

| Numbers (CLAIM-DRAFT line) | Provenance | Status |
|---|---|---|
| v0.2 0.513 (0.479–0.550), 0.389, 0.299; V-para 0.413, 0.261, 0.154; P4 0/102; 0 unsafe-rule hits (l.11–18, l.160) | CLAIM-RUNS-cut3 (verified); EXPOSURES l.56 + v0.2 rows; CLAIM-RESULTS-cut3 l.20/24/53/61 | Traced; trace hashes not checked |
| cut 6 0.512, Δ −0.001, 210/220 identical (l.22, l.136) | CLAIM-RUNS-cut6 (verified); EXPOSURES l.59; CLAIM-RESULTS-cut6 l.34/38/49 | Traced; but 96.7 % of verdicts copied from cut 3 (CLAIM-RESULTS-cut6 l.20–29) |
| 0.397, win/tie/loss 0/0/110, V-para win 0/51 (l.12, l.11) | PIPELINE-AUDIT l.13–14; EXPOSURES l.60 | Partial: audit only, no criterion |
| Haiku floor removed 0.48 (l.11) | prose only (BOUNTY-BOARD l.16); BAR-TABLE l.44 "CI UNKNOWN" | Untraced to any aggregate |
| Haiku raw 0.588, Sonnet 0.961, Opus 1.044, Fable 1.037 (l.64–68) | runs-cut3/anchors; EXPOSURES l.57 | Traced; one run each, no CIs for three |
| D = 0.306 (l.10, l.34) | frozen analysis plan §4.2 | Partial: the 7 runs behind it not named |
| A15 73/73, p50 49 s, PSS 4.41 GiB, 0.561 vs 0.558/0.560 (l.21) | QUEUE l.711; boar-eval/runs/device-tester-a15/final-cut6-v01/ | Partial: no criterion; judged with judge.v1-med, contradicting l.35 |
| 1.5B/4B ladder (l.54–56) | analysis-plan §10, older engine | Partial: no trace files named |
| Facts tier 28/40, 28/29, +0.027; venues 7/7, +3.65 MB (l.101–102, l.161) | CUT7 and VENUEGPS-2 criteria (verified) | Traced |
| Deep tier 0.329, 0.422, 0.436, 0.387, 0.514, 0.508, +0.100, +0.089, best-of-2 0.590, Gemma 0.388 (§6, l.190) | criteria verified; EXPOSURES l.65–73; aggregates exist | Traced, labelled development-style |
| Routing sim 0.465/0.467, "≈ 0.33" (l.190) | DEEPROUTE-VPARA, descriptive, no criterion | Partial; ≈ 0.33 is an estimate |
| +0.060 deep, 10.0–10.3 GiB (l.122) | "QUEUE l.267/271" while S3 says "last 150 lines" of a 1,063-line file | Stale locator |
| Phone "2–3 min / 3.5–5 min" (l.190, l.200) | a competitor team's rates × our arithmetic | Not our measurement |
| v0.2 exposure "4 runs" (l.12) | EXPOSURES l.13: 12 full generation runs + DEEPTHINK-V02 + DT512-V02 | Understated |

## 2. Overclaiming, with replacement text
1. l.12 "Held-out result (bench v0.2, 110 new questions, written blind)" → "Formerly held-out result (bench v0.2, 110 questions written by Claude subagents; exposed since 10-06, now development data)".
2. l.40 "no engine change was tuned on their scores, with one disclosed exception" → EXPOSURES l.13 lists more (A05 seen by Sonar, 3 hand-adjudicated items, plaintext in git d8154b6): "…with these known exposures: the A02 safety item, A05 seen by one researcher, 3 hand-adjudicated items, and plaintext in private git history (EXPOSURES row 1)."
3. l.11 "V-para, written by our team" → the writer was an Opus subagent (same family as reference and judge); grading fields printed to the runner on 10-03 (EXPOSURES l.51) undisclosed: "V-para, 58 items written by a Claude Opus agent, unseen by engine builders; grading fields (no questions or answers) were once printed to the runner before the claim runs".
4. l.22 / l.139 "re-run on cut 6 … Δ −0.001, CI −0.010…+0.008" → add "323 of 334 verdicts were copied from cut 3 for byte-identical answers, so the narrow Δ reflects that reuse and is not an independent re-judging."
5. l.21 "device quality equals desktop within noise" → "on 57 development items, one 8 GB phone and judge.v1-med, the phone score (0.561, 0.507–0.617) is not distinguishable from desktop".
6. l.190 / l.72 "the first configuration whose point estimate is above 0.50 floor removed on any set" → best of ≈ 20 deep-tier arms on exposed sets (EXPOSURES l.14: 19 full runs + 12 slices): "the best of ~20 deep-tier configurations tried on these exposed sets; selection inflates it, and with seed noise (BAR-TABLE l.122–131) its CI is wider."
7. l.190 deep-tier CIs: BAR-TABLE l.131 says cite the CIs that include seed noise → 0.436 (0.387–0.486), not (0.401–0.472).
8. l.153 row 7 "Partly met" → V-para floor removed 0.26 and correctness ≤ 2 on 49 % of items (PIPELINE-AUDIT l.14): "Attempted; answers are often thin or wrong (floor removed 0.26–0.39)."
9. Departures l.78–83: the headline switch from raw (analysis-plan l.17) to floor-removed + win rate after the v0.2 results is missing → add "Headline metric changed after seeing results (audit, 10-06), toward a stricter scale; the pre-registered raw rule is reported beside it."

## 3. How a rival attacks the ">[competitor score removed]" operationalisation
- The reference is Opus's memory, not "internet + frontier AI": Opus no-web scores 1.044 vs Opus with web (PIPELINE-AUDIT l.16; RND-REVIEW B6); the bar tested is "half as good as Opus", judged by the same family.
- The rubric rewards length: references ≈ 280 words, BOAR ≈ 50; capping references at 80 words moves the deep tier 0.412 → 0.514 (BAR-TABLE l.98).
- Win rate is saturated at 0 for every system incl. a competitor team (RND-REVIEW B1): no information.
- "Floor-adjusted" is our construct; the v0.3 addendum marks it "formal decision status: TBD" (boar-eval/bench/v0.3/plan/addendum-05-v03.md l.30–32).
- Speed and failures are outside the score; errored traces dropped (RND-REVIEW B5).
- The rival's protocol is not ours: a competitor team reports a 0–10 ratio of means on a public 61-question set, [competitor score removed] (WEB-SWEEP-2026-10-09 l.45, l.52).
**One cheap pre-emption:** one judge pass on their public question set with their own rubric, scoring BOAR 4B, BOAR deep tier (desktop), a competitor team's published answers (competitors/a competitor team/eval/) and Haiku no-web together: ≈ 4 × 61 × 2 calls, no blind exposure → a like-for-like number. (→ arm RIVALSET, frozen 21:1x.) Second step if budget allows: the analysis plan's 40-pair human-label check (l.82).

## 4. Mismatches between files
| # | Mismatch |
|---|---|
| 1 | CLAUDE.md:22 v0.2 "raw 0.519 / floor-adjusted 0.40" vs CLAIM-DRAFT l.12 0.513 / 0.389 (CLAUDE.md one seed, BAR-TABLE l.54; draft two seeds). |
| 2 | CLAUDE.md:22 orders the 4B "0.40 / 0.26"; REPORT-PACKS l.21 "0.26 / 0.39". |
| 3 | CLAUDE.md:21 "deep tier +0.063 over the 4B"; REPORT-PACKS l.10/l.90 +0.054 pooled (+0.063 is the SE half, l.86). |
| 4 | **Bar definition differs:** CLAIM-DRAFT l.190 floor-removed CI low > 0.50 AND win rate > 0; BAR-TABLE l.7 win rate never gated, formal rule raw CI low > 0.50; analysis-plan l.17 raw > 0.50; addendum-05 l.32 TBD. BAR-TABLE l.72–73 says the deep tier MEETS the formal raw rule on both sets; CLAIM-DRAFT never says so. |
| 5 | BAR-TABLE.sha256 holds 6 hashes; current BAR-TABLE.md hashes to 0b1e9714…, matching none → the 10-12 correction is unhashed. |
| 6 | CLAIM-DRAFT l.12 "4 runs" vs EXPOSURES l.3 TL;DR (12 generation runs + 8 Opus passes) vs EXPOSURES l.13 row (10 Opus passes); V-para TL;DR l.3 (11 engine runs, 10 passes) vs row l.14 (19 full + 12 slices, 16 Opus passes). |
| 7 | CLAIM-DRAFT l.155 "Nothing is published" vs REPORT-PACKS l.3 / QUEUE l.993: 11 packs public on HF incl. the claim kit packs (REPRO-PLAN §1). |
| 8 | CLAIM-DRAFT l.190/l.200 "2–3 min" per thinking answer on a phone vs DEEP-RESEARCH D-3 / CLAUDE.md:29 1.9–2.8 min (+ a hot-phone figure). |
| 9 | CLAIM-DRAFT l.35 "every claim number is judge.v1" vs the device score 0.561 judged with judge.v1-med (QUEUE l.711). |
| 10 | CLAIM-DRAFT l.190 H raw 0.552 vs BAR-TABLE l.39 0.553; K V-para CI 0.224–0.299 (cut 3) vs 0.224–0.300 (cut 6, BAR-TABLE l.35). |
| 11 | CLAIM-DRAFT l.149 APK 77 MB vs DEVICE-DAY l.8 74 MB (same 77,086,168 bytes; MB vs MiB). |

## 5. Device results the text implies but does not have
- l.190 "the device plan stays one deep answer with thinking 512": bmoe has no thinking-budget setting; the app-side cap is not built → 512 cannot be enforced on a phone today.
- l.190 "desktop deep-tier numbers may … be quoted for a bmoe-based device plan": DEEPPAR-L1 parity covered the deep tier WITHOUT thinking, 57 dev items, one seed; thinking 512 never parity-tested on bmoe.
- l.200 phone time = a competitor team's measurement + our arithmetic, their bmoe version unchecked → "no BOAR deep-tier run on any phone".
- l.21 / row 12: the A15 evidence is a debuggable benchmark app; the installable app runs a different code path (RND-REVIEW A2) → "Partly met" on the real-device row is generous.
- Row 15 (venues): the location path was never run on a phone (l.167 says so; row 15 does not).

## 6. Could a third party rerun the claim from boar-eval alone? No.
v0.2 is hashes + plan only; V-para only in blind/, not in git; reference answers gitignored even for v0.1 (ToS decision pending, REPRO-PLAN §1); the judge is `claude -p` Opus (closed, paid, non-deterministic, version drift); boar-eval private, claim runner 73b9d2c and the rnd cut 3/6 commits unpushed as of REPRO-PLAN (10-06), cut 7 on local branch coord/cut7 only; emergency detector (v3b gguf + head) local, base licence unknown; llama-server b11010 build script local; Qwen3-4B has a hash but no HF revision ("app catalog", rnd/kiln/MODELS.md), the 35B has revision + hash but was deleted from the mini; places kit size unrecorded, crypto pack sidecar hash stale, area tiles unpublished; pre-registration hashes unpublished (l.83); repo history contains the v0.2 leak so it cannot be published as is; phone sampling non-deterministic (QUEUE l.695), deep tier never probed for determinism (SEEDGEN).

## 7. The five strongest attacks, ranked
1. **"Claude wrote the items, wrote the references, and judged; no unexposed set exists."** Defence: the 4B numbers were measured while V-para was unexposed, under hash-frozen criteria, with a full exposure ledger, and already read "below bar". Fix we can't make: a held-out set written outside the Claude family with human labels by 10-31 (v0.3 has 0 items; no paid cross-family judge).
2. **"You measured an engine no installable app runs, on a desktop."** Defence: the benchmark app runs the same engine bytes on the phone; A15 0.561 vs desktop 0.558/0.560. Fix we can't make: a 12 GB phone run of deep + thinking 512 on bmoe (no device; bmoe has no budget setting).
3. **"Moving goalposts: three bar definitions, chosen after the results."** Defence: we moved to the stricter scale and print all three. Fix we can't make: a pre-registration predating the results. Meanwhile the deep tier quietly meets the pre-registered raw rule (BAR-TABLE l.72).
4. **"A rubric ratio against Opus's memory is not 'internet + frontier AI'."** Defence: competitors use the same class of measure; the length test shows ≈ 83 % of the gap is substance. Fix we can't make: a task-success or preference study with real offline users.
5. **"Forking paths on development sets."** ≈ 20 deep-tier arms on exposed sets; the best are selection-biased and their CIs omit seed noise. Defence: every arm had a frozen criterion, all negatives in CLOSED.md, deep-tier numbers sit outside the claim build. Fix we can't make: a fresh unexposed set for the deep tier.

## UNKNOWN
Whether the 12-char trace hashes in CLAIM-RESULTS still match the files on disk (coordinator script check); which memory profile the A15 run used vs the desktop "Android 12 GB profile"; whether boar-eval 73b9d2c and the rnd cut 6 commits are still unpushed; whether any v0.3 items exist (bench/v0.3 has a plan and an empty skeleton; go/no-go was due 10-13); the CI for Haiku's 0.48 floor-removed score; whether the claim goes in as an update to #124 or as a new claim.

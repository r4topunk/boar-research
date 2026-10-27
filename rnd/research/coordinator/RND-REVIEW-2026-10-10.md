# R&D process review, ML-engineering lens (2026-10-10, Fable coordinator)

TL;DR: **the measurement machine is better than typical practice; it was pointed at the wrong target for the last three weeks before the deadline.** Since 10-07 about 20 desktop deep-tier arms ran while every artefact the bounty judges stands at zero: public repo, Android UI running the measured engine, cut-7 APK, demo, like-for-like number against competitors, v0.3 items. The bar as we operationalised it cannot be passed by anyone (win-rate is 0 for a competitor team too; Haiku-no-web scores 0.48 floor-adjusted against our 0.50), so a v0.3 claim run is near-certain to read "below bar" for the 4B and 8–17 % likely to pass for deep+think. The statistics critiques are real but modest after refutation (CIs ≈ 1.2× too narrow, 1.5× on the V-para thinking tier; slice bias is heterogeneity, not regression to the mean). The one change with the highest expected value: **next week is claim-path first, with one judged experiment (public-61 head-to-head) and addendum-05 frozen before any v0.3 judge call.**

**Double-checked the same evening (§7): 13 corrections, T1 withdrawn, the bar scale is r4to's open decision, a second coordinator session already wrote CLAIM-READINESS-2026-10-10.md; §7.2 supersedes §4 Tasks.**

Method: 7 readers (methodology, benchmark/judge, direction, infra/cost, process, claim path/device, external calibration) → 2 adversarial refuters (steelman, statistical rigor) → 1 completeness critic; 10 Opus agents, 76 findings, 62 weaknesses/risks tested, read-only, `blind/` untouched. Every number below was re-checked against primary files by a refuter; where a reader overstated, the corrected figure is given. Raw outputs: session workflow `wf_e141df75-2ed`.

## 1. Done right (keep, do not re-litigate)

| What | Evidence | Keep / small upgrade |
|---|---|---|
| Criteria frozen before results, sha-pinned, deviations logged | 65/65 `arms/**/*criterion*.sha256` verify; git freeze commit precedes result commit (THINK4B 10:37 → 11:31) | Keep. Add to `arm.sh launch`: refuse unless the criterion sha is committed |
| Paired, both-order, tie-on-disagreement judging; floor-adjusted headline; exposure ledger | `judge-core.mjs` l.94; `paired_gap.py`; `EXPOSURES.md` | Keep. Make floor-adjusted the unit in `arm.sh rule()` too (today it thresholds raw Δ) |
| One driver, sha guards on the mini, byte-identical replays | `arms/_lib/arm.sh`; DT512/GEMMATHINK aggregates reproduced byte-identically (QUEUE l.840) | Keep as the only entry point; move `dh.sh/dt.sh/l1.sh/l2.sh/chain*.sh` to `attic/` |
| Judge cost engineering: Haiku L1, N=4 shards (×3.5–4.8, 0 429s), near-miss escalation, 8 s retrieval replay | QUEUE l.801/815; PIPELINE-AUDIT §6 | Keep. Extend replay to prompt assembly (M10) |
| Fast adoption of the honest metric after the 10-06 audit; spend fell from 12k–20k judge calls / 6 days to ≈ 1.5k / 2 days | BOUNTY-BOARD l.5; HANDOFF-10-10 §7 | Keep |
| DEEPTHINK was the highest-yield arm: +0.093 floor-adj for 306 calls (0.30 pts / 1k calls, ×10 DEEPVPARA) | `arms/dt512/DT512.md` l.28; `arms/deepvpara/DEEPVPARA.md` l.34 | Freeze deep+think-512 as the research-mode config; no more desktop tuning |
| BOAR Bench = byte-identical engine on device; A15 parity 0.561 vs 0.558/0.560 | `bench-app/README.md` l.21; QUEUE l.711 | Reuse unchanged for cut 7 |
| Differentiators measured with caveats: venues 0/7 → 7/7 with location + tile, facts precision 28/29, no-INTERNET APK | CLAIM-DRAFT l.102/151 | Put them at the top of the README and the demo |
| Independent Opus claim reviews catch real errors (v3.8: phone-time estimate 4× too low) | CLAIM-REVIEW-v3.8 l.9 | Keep, but weekly, and once per week on the plan itself |
| Closures that agree with the literature: best-of-2 selectors, dense swaps, budget sweeps, MTP | QUEUE l.870; WEB-SWEEP-REVIEW l.10 | Record as permanently closed in the handoff's Do-NOT list |

## 2. Done wrong (confirmed after refutation; ranked by effect on 10-31)

### A. Direction and deliverables (highest materiality)

| # | Finding | Evidence | Fix |
|---|---|---|---|
| A1 | **Every submission deliverable is unbuilt** and the 10-10 queue held only desktop arms. REPRO-PLAN L1–L6 never executed since 10-06. Critical path ≈ 6–8 working days | CLAIM-DRAFT l.24 "Not yet done: public repo, Android UI integration"; HANDOFF-10-10 §4 | Next week = claim path first (§4 Tasks). Metric: CLAIM-DRAFT §4 rows moved from "Not yet" to "Met / Partly" |
| A2 | **The app a user installs does not run the measured engine.** `src/ui-android/ChatScreen.tsx` imports `runAdaptiveChat` (self-described legacy path); 0 `answerService` imports; `boar-app` HEAD 38f996d1 (10-03) | QUEUE l.472; UI-WIRING-NOTES l.26 (1–1.5 d plan, parked) | Wire `answerBridge` + `runChatAnswer` in the fork worktree, no push; desktop identity check 20/20 (route, reasons, sources, text identical to `answerEval`) |
| A3 | **Submission channel undecided since 10-02**: update claim #124 (the app maintainer, 1.5B description, "materially different" rule) vs new claim + repo. Every repo task has no target | QUEUE l.255; BOUNTY_31 l.56; CLAUDE.md l.14 (public fork never holds WIP) | One-page ADR in `review/` by 10-13 with options A/B, cost, rollback, default if unanswered |
| A4 | **No like-for-like number** on the public 61-question set competitors report (a competitor team [competitor score removed], a competitor team [competitor score removed]); T1 dropped 10-06 "until writing the claim". a competitor team answer files exist locally | WEB-SWEEP-10-09 l.45; QUEUE l.744; `competitors/a competitor team/eval/answers_*.jsonl` | Run T1 as the week's one judged experiment (§4, D3). 61 × 1 seed separates a gap ≥ ≈ 0.06 |
| A5 | **v0.3 has not started**: `blind/bench-v03` absent (names only), pilot was due 10-08, D1–D3 open; the only unexposed number depends on it | BENCH-V03-SPEC l.91; QUEUE l.805 | Keep the spec's 10-13 go/no-go and 60-item fallback (±0.060 half-width); write the claim text for both branches now |
| A6 | **No cut-7 APK, nothing ever run at ≥ 11 GB**; device code D2/D6 parked "until a device" although it builds and checks on the desktop (bmoe host build, tree-hash parity). A ≥ 11 GB phone became reachable through r4to on 10-10 | `bench-app/build` newest = cut6; deep/RESUME l.56; HANDOFF-10-10 §5 | Build the cut-7 no-network APK + kit (facts table) on the MacBook, tree hash = desktop; assemble one relay-ready bundle (APK, s16 runbook, ADB-PROBE-RUNBOOK, frozen gates, netstats step). Plan does not depend on a phone run |
| A7 | **No speed story.** 4B p50 49 s / p90 77 s on the A15 (2.0–2.7 tok/s); deep+think 79 s desktop, 2–5 min projected on a 12 GB phone; bmoe has no budget flag; the post author names 50 tok/s | CLAIM-DRAFT l.154; DEEP-TIER-PLAN l.9; deep/RESUME l.60 | 0-call "fast answer, deep upgrade" numbers from existing K/H rows (first useful text p50 ≈ 6 s, final score = H); go/no-go 10-14 for deep in the demo (§3 O3) |
| A8 | Claim written as a 345-line audit, 8 versions / 4 reviews in ≈ 30 h; no reader-facing README or demo script with "a 1B model fails this" queries | BOUNTY_31 l.50; CLAIM-DRAFT l.190 | Freeze v3.8 as METHODS.md (weekly batch edits only); write README-claim.md (≤ 1 page) + DEMO-SCRIPT.md (6 queries) with a safety-caveat grep gate |
| A9 | GrapheneOS / no-Play-Services never run on a device; product APK never audited with `audit-apk.py` | CLAIM-DRAFT l.152 | Audit the wired product APK (NO-NETWORK, 0 Play/Firebase classes); add a per-UID `netstats` snapshot to any phone session; state GrapheneOS as untested |

### B. Metric and bar

| # | Finding | Evidence | Fix |
|---|---|---|---|
| B1 | **Win-rate is saturated at 0 for everyone** (BOAR at every rung, a competitor team 0/61) and the reference sits at ≈ [competitor score removed], so the ratio is an absolute rubric mean, not a pairwise comparison. The bar reading "CI low > 0.50 AND win-rate > 0" cannot be passed by any phone system | JUDGE2 l.28; CLAIM-DRAFT l.71; WEB-SWEEP-REVIEW l.28 | Before any v0.3 judge call: drop the win-rate conjunct, demote win/tie/loss to secondary, keep the usefulness ≥ 3/5 share as co-headline (already in addendum-05), pilot the anchored "at least half as useful? yes/no" judge question on dev rows (306 Haiku calls) |
| B2 | **Internal bar is stricter than a small frontier model offline**: Haiku-no-web floor-adj 0.48 < 0.50 on V-para. Research optimised a target no phone model can hit | BOUNTY-BOARD l.16 | Keep floor-adjusted as the honesty metric; stop using "≥ 0.50 V-para" as a go-gate; comparative gates = "beats a competitor team same-sitting on public 61" and "Haiku-no-web parity" |
| B3 | **v0.3 outcome is near-certain "below bar"**: 4B P(pass) ≈ 0; deep+think P(CI low > 0.50) ≈ 8–17 %; spec gives CI widths but no build choice (TBD cut 6/7), no multiplicity rule, no outcome sentences | DT512V02 l.2; BENCH-V03-SPEC l.76; addendum-05 §3–4 | Pre-register in addendum-05: build = cut 7 (deep reported separately as dev), Holm if two builds, power table with σ_run from SEEDVAR, the sentence for above / straddle / below |
| B4 | **No cross-family or human calibration**: Claude writes items, references and judges; GPT pilot HELD since early October; only non-Claude judge (Gemma) is +0.11 lenient, κ 0.32–0.55, confounded with judge strength | QUEUE l.199; analysis-plan l.43 | Option O1 (204 GPT calls, needs paid-API OK); fallback: disclose JUDGE2 as the only non-Claude check |
| B5 | **Speed is outside the score and failures vanish**: `judge.mjs` l.66 drops errored traces, `paired.mjs` intersects ids → a device timeout/OOM leaves the ratio instead of scoring as a failure | judge.mjs l.66; paired.mjs l.16 | Latency-capped companion metric (answers over a frozen cap and errored traces scored at the decline floor), computed from existing traces, 0 calls, next to floor-adjusted |
| B6 | Reference = frontier memory, not "internet + AI" (Opus-no-web 1.029 vs Opus+web; `blind()` strips sources; venue items excluded) | ladder.md l.36; judge-core l.8 | v0.3 keeps non-Claude web-UI references; tag 8–10 % web-dependent items in a public ids file and report them separately; state that venues sit outside the ratio |
| B7 | Length share of the gap unmeasured (BOAR 51 words vs reference 250; "correct but thin" = 27/57 items); longer answers cost correctness | 4B-LOSS-ANATOMY l.13 | Add a correctness-only ratio next to every headline (0 calls). The 255-call length-controlled reference test is deferred (O6) |
| B8 | Item mix under-weights synthesis/comparison/reasoning (synthesis 6/110); per-category cells n = 3–7 unreadable | DATASET_CARD l.14; CLAIM-RESULTS-cut3 l.68 | Keep v0.3 quotas (comparability, r4to's time); pre-declare 3 super-strata with n ≥ 18 in addendum-05 |

### C. Methodology (corrected magnitudes)

| # | Reader said | After refutation | Fix |
|---|---|---|---|
| C1 | CIs 1.5–2× too narrow (seed + judge variance ignored) | Item bootstrap already absorbs per-item noise; only a run-level term is missing. CIs ≈ **1.2× too narrow on average, up to 1.5× on the V-para thinking tier** (per-item seed r 0.5–0.6 vs 0.81 for the 4B), ≈ 1.0× on v0.2 (r 0.90). The DT256 / GEMMATHINK "seed flips" are one event: control T s43 high (0.566 vs 0.518), i.e. shared-control correlation | Add one common-mode term to `paired.mjs`: CI = sqrt(SE_item² + 2σ_run²), σ_run from SEEDVAR (s44 running); one 102-call Opus test-retest of unchanged traces for σ_judge (never measured). Decide on v0.2, not V-para, when one seed is all there is |
| C2 | signal20 slice inflates Δ by regression to the mean (THINK4B slice +0.091 → full +0.026) | Deep arms are paired against T/H, never against the selection run K, so **no RTM**; the inflation is **heterogeneity** (the 4B's 20 hardest items) plus slice SE ≈ 0.02–0.03. RTM (+0.013–0.017) applies only when paired against the selection run (SPEEDPACK) | Stratified random 20-id slice (fixed seed) for every future arm; protocol note: a slice Δ is not an estimate of the full-set Δ; 0-call replay of DT512/DT256/GEMMATHINK/THINK4B rows on the random slice to show the change |
| C3 | Promote/stop rules fire on point estimates (coin flip for +0.03) | True **only at L1**; every L2 verdict checked uses CIs. Cost = wasted or wrongly stopped triage (a true +0.03 arm is stopped ≈ 40–60 % of the time), not false adoption | L1 futility rule: stop only if Haiku Δ ≤ 0 and h2h ≤ control; any Haiku Δ > 0 goes to Opus N=4 on the same 20 ids (40 calls). Do not re-check the three slice-only closures (120 calls, not worth it) |
| C4 | Haiku L1 compresses gaps 3–4× | ×3–4 on 4B and hard-slice contrasts; **×0.6–1.0 on full deep sets**, same sign 5/5 | Keep Haiku L1; the futility rule above covers the exposure |
| C5 | **Audit stop rule never implemented**: 0/32 criteria frozen since 10-07 state an expected Δ or MDE; at least 8 of ≈ 14 deciding arms were one-seed or slice-only or in a closed family | PIPELINE-AUDIT l.80; `grep -il "mde\|expected" arms/*/*criterion*` | Mandatory **Power block** in the criterion template (expected Δ and its source, n, seeds, MDE from SEEDVAR); `arm.sh launch` refuses without it unless tagged `blocker`; desktop quality arms capped at 1/day |
| C6 | "Closed" lines rest on under-powered negatives: THINK4B stopped after one seed at +0.026 (CI −0.013…+0.068, MDE ≈ 0.06); FT DATA line closed on a 20-example bar that human CLAPnq also fails (6/20) | Closures followed their frozen rules; labels overstate | Relabel in BOUNTY-BOARD and the claim as **"not detected at MDE ≈ X (n, seeds)"**; keep a "parked, under-powered" list with the cheapest powered test each |
| C7 | Post-hoc paths feed headline material (FACTS r6 kept after failing its own r6 criterion; DEEPTHINK-V02 Opus addendum after a NO became "first point above 0.50") | Real but measured effect on claim numbers is zero (FACTS fires 0/168 held-out-style; v0.2 0.51 replicated independently) | `RULE-CHANGES.md` (date, trigger arm, "applies to arms frozen after sha"); tag post-hoc measurements "post-hoc, dev" in CLAIM-DRAFT |
| C8 | Deep line declared closed 10-09 23:14; five arms on that family on 10-10; THINK4B had 3 post-hoc splits (cells n = 3–21) | Reopenings were cheap (0–40 calls) and labelled descriptive | `CLOSED.md` registry (family, evidence, what reopens it); ≤ 1 post-hoc split per arm, labelled "hypothesis for a new arm", never a verdict |
| C9 | No zero-cost input-diff precheck (DEEPCTX spent 33 mini-min + 40 Haiku calls to learn the cap changed 4/20 prompts) | Confirmed, small saving | `arm.sh precheck`: replay + prompt assembly, stop if < 20 % of items change input |

### D. Infra, evidence and knowledge management

| # | Finding | Evidence | Fix |
|---|---|---|---|
| D1 | **Judge completeness is not enforced**: `shard_judge.sh` ends with an echo → always exits 0; STOP touched but never read; `l1` checks only non-empty; `paired.mjs` silently intersects ids; no output lock (DEEPTHINK-V02: 266 rows for 220 keys) | shard_judge.sh l.18/23–25; arm.sh l.103; paired.mjs l.16 | Exit with the validation rc; honour STOP; abort when rows ≠ 2×ids or `.missing` non-empty; atomic `mkdir` lock on the judge output; test by replaying DT512 with one truncated shard |
| D2 | **Single copy of the evidence**: rnd 136 commits and boar-eval 6 commits ahead of origin (last push 10-06), archive bundles from 10-03, MacBook volume 94 % full | `git rev-list @{u}..HEAD`; rnd/archive/README l.1 | Nightly `git bundle --all` of rnd, boar-eval, bench-app, wt/cut7 → mini `<runner>/backup`, `git bundle verify`; ask r4to once for a standing OK to push the private origins daily |
| D3 | **No machine-readable results ledger**: 67 arm folders, 131 aggregate JSONs with heterogeneous keys, numbers retyped into QUEUE (51,207 words), CLAUDE.md l.24 (1,018 words in one bullet), handoffs and CLAIM-DRAFT; a reviewer caught a transcription error; BOUNTY-BOARD stale since 10-06 (deep "≈ 0.57 v0.1", Forge as owner) | arm.conf l.17; QUEUE l.853; BOUNTY-BOARD l.22 | `tools/ledger.py` → `results.csv` (arm × set × seed × judge: n, raw + CI, floor-adj + CI, win, Δ vs control + CI, calls by model, mini hours, criterion/tree/patch sha, verdict); done when it reproduces every CLAUDE.md number; CLAUDE.md state block → scoreboard + ladder + open decisions + changed-since (≤ 250 words); BOUNTY-BOARD regenerated from it |
| D4 | **Recommended deep config is not one artefact**: mini tree = rsync composite + 2 patches on cut 6 (claim = cut 7), no cumulative patch or tree hash; thinking cap enforced by llama-server only (bmoe has none); `paired.mjs` imports live `judge-core` by absolute path; GGUFs fetched at revision `main` | DT512-criterion l.6; RESUME l.60; paired.mjs l.6 | `deep-recommended.vs-0cfd4a77.patch` = cut 7 + deepthink + dt512 in `wt/deep7`; tree hash vs the mini tree (expected diff = FACTS files); 20-item Haiku equivalence (≈ 40 calls); ledger records sha256(judge-core) and HF revisions |
| D5 | Generation lifecycle holes: lock is local per conf; WAIT_HARD 5400 s vs 2.3–4.5 h runs → HARDSTOP and hand re-waits (how the 3.3 h duplicate-launcher loss arose); runner writes DONE even on rc ≠ 0 | arm.sh l.13/33; remote-run.sh l.36 | Lock on the mini (`ssh mkdir`, atomic) before scp; `FAIL rc=N` instead of DONE; WAIT_HARD = items × p50 × 2; `wait` idempotent and read-only |
| D6 | Run registry and exposure rows are manual (≈ 15 never-reported runs found by the audit) | EXPOSURES l.7; arm.sh l.127 | `launch` appends to `arms/runs-registry.jsonl`; `arm.sh orphans` at each tick; `exposure --append` |
| D7 | MANDATE off-limits still names only `rnd/veil/` (audit T6, spec R5 never applied): a re-spawned researcher could read `blind/` | MANDATE l.103 | Add `blind/` and boar-eval git history (15 min) before any researcher agent is spawned |
| D8 | Idle compute: mini idle stretches, MacBook generation slot waits on "ok MacBook" (disk rule 25 → 15 GiB), GGUF churn forced by the 25 GiB rule | HANDOFF-10-10 §3/§6 | Without the OK the MacBook does replay, packaging, APK builds and judge shards only; the deep moratorium frees the mini, so the slot is off the critical path |

## 3. Gaps the review itself found (completeness critic)

- **Asset distribution is unplanned** and collides with the public-upload rule: the bounty wants assets "included or with clear download and installation instructions" and a stranger running the app "within a few minutes"; REPRO-PLAN L6 points to HF links that need r4to's OK. Write a 1-page asset BOM (file, size, sha, licence, host, adb-push or in-app path) totalled against the 50 GB cap.
- **Licences**: emergency detector base model licence UNKNOWN (REPRO-PLAN l.22); publishing reference text needs a ToS decision (l.16); Wikipedia/Wikivoyage CC BY-SA attribution. No row may say UNKNOWN in REPRODUCE.md, or the detector ships as optional.
- **Competitor landscape stale** (CLAIMS_31.md last edited 09-26; poidh checked 10-02) and the timing rule not weighed: the first build the post author confirms wins (BOUNTY_31 l.74). One ≤ 30 min read-only sweep of claims and replies since 10-02; if any got a confirmation, pull the submission date forward.
- **The safety caveat** ("AI-reviewed, not clinically reviewed") is required on every card and public text; none of the proposed new artefacts (README, demo, wired card UI) carries it yet → deterministic grep gate in the build.
- **Week judge budget was never totalled**: surviving recommendations sum to > 1,000 Opus calls; §4 fixes a budget.
- `device/A15-LATENCY-BUDGET.md` holds the stage breakdown the perceived-latency demo needs (time-to-sources, TTFT, decode); nobody used it.
- **ui-ios merge**: the repo now has one engine with `src/ui-ios` + `src/ui-android` and engine changes were on hold until the merge; rebasing the wiring branch on upstream main may conflict. Count conflicts (`git log 38f996d1..upstream/main`) before trusting the 1.5-day estimate.

## 4. Next week (2026-10-12 → 10-18)

### Decisions (fix direction)

| # | Decision | Why |
|---|---|---|
| D1 | **Claim path first. WIP = 3 fronts**: (A) product and claim artefacts, (B) comparability and metric, (C) tooling hygiene. ≤ 30 % of mini and judge budget for research. Moratorium on desktop deep-tier generation arms and on 4B arms | A1–A9: 6–8 working days of critical path, 21 days left |
| D2 | **Success by 10-31 = the best verifiable offline app**: a repo that reproduces, a device demo with "1B fails this" queries, a like-for-like public-61 number, one honest v0.3 or dev-labelled number. Floor-adjusted stays the honesty metric; "≥ 0.50 V-para" is no longer a go-gate; the win-rate conjunct is removed from the bar reading | B1–B3: the current bar is unpassable for everyone; the decider is qualitative |
| D3 | **One judged experiment this week**: public-61 head-to-head, cut 7 (4B) + deep+think-512 vs a competitor team's published answers vs the reference, same sitting, both grading protocols, Opus N=4, ≤ 450 calls | A4: the only number voters can compare |
| D4 | **Freeze addendum-05 before any v0.3 judge call**: build = cut 7, deep reported separately as dev, outcome sentences, power table with σ_run from SEEDVAR s44, usefulness ≥ 3/5 share co-headline, latency-capped companion metric, super-strata n ≥ 18. v0.3 go/no-go on **10-13** per spec (60-item fallback) | A5, B3, B5, B8 |
| D5 | **Enforce the stop rule in tooling**: Power block mandatory in every criterion; `arm.sh launch` refuses otherwise; stratified random 20-id slices; L1 futility rule (stop only on Haiku Δ ≤ 0 and h2h ≤ control); common-mode σ_run in `paired.mjs`; "closed" → "not detected at MDE" | C1–C6 |
| D6 | **Evidence safety and a ledger**: nightly bundles to the mini; judge completeness + lock + rc; `ledger.py` → `results.csv` regenerates the CLAUDE.md scoreboard and BOUNTY-BOARD; MANDATE off-limits += `blind/` + git history | D1–D7 |

### Options (exploration, not committed; each needs a frozen criterion)

| # | Option | Gate / cost | Status |
|---|---|---|---|
| O1 | Cross-family judge: re-judge K s42 and H s42 with GPT using judge.v1 bytes (204 calls, [usage detail removed]) → family offset in addendum-05 | needs r4to's paid-API OK; fallback = disclose JUDGE2 Gemma as the only non-Claude check | offer once |
| O2 | 20 blind pairs labelled by r4to with "at least half as useful?" (≈ 30 min) as metric validation | conflicts with the "no human review" rule; optional | offer once |
| O3 | Deep tier in the demo as opt-in "Go deeper" only if a ≥ 11 GB probe passes G1–G3 (≥ 4 tok/s, RSS ≤ 9 GB, 3/3) **and** D2+D3+D6 fit ≤ 4 days; otherwise 4B-only with deep as research numbers. Zero-call "fast answer, deep upgrade" table from K/H rows either way | go/no-go 10-14 | default: 4B-only |
| O4 | Coverage (full enwiki top-100k + reranker) on the deep path: **step 0 only** (0-call replay, key-in-context ≥ +5 keys, 0 emptied) if the mini is idle after T1. Realistic prior +0.01–0.025, not +0.02–0.05 | no judged arm this week | parked |
| O5 | NOTES35 distillation (deep+think → breadth-first notes pack served by the 4B). FACTS fired 0/168 held-out-style, so gate on note hit-rate on v0.2 ids ≥ 15 % before any judge call | ≈ 1 mini-day + verification | not this week |
| O6 | Length-controlled reference test (51 refs capped at 80 words, 204 re-judge calls) | deferred; correctness-only ratio (0 calls) now | deferred |
| O7 | One 2 h Haiku/medium scout per week on named gaps (bmoe thinking cap on Android, Dimensity 8300 MoE speed, streaming UX), Opus-verified, ≤ 3 cards | after MANDATE fix | weekly |

### Tasks (day by day; owner = coordinator session; `sonnet` subagents for mechanical steps, `opus` for wiring and REPRO)

| Day | Front | Task | Done when | Judge calls |
|---|---|---|---|---|
| Mon 10-12 | C | Nightly bundles to the mini; `shard_judge.sh` rc + STOP + id-completeness + lock; Power block in the criterion template and `arm.sh launch` guard; random-slice addendum (hashed); MANDATE off-limits fix | `git bundle verify` passes ×4; DT512 replay with one truncated shard exits non-zero; launch refuses a criterion without Power; addendum sha committed | 0 |
| Mon 10-12 | A | Decision note to r4to (one page, dated): claim-channel ADR (A/B, cost, rollback, default if unanswered by 10-13), public asset host yes/no, v0.3 D1–D3 defaults, paid-API OK (O1), human pairs (O2) | ADR in `review/`; QUEUE decision row with the defaults | 0 |
| Mon–Tue | A | Cut-7 no-network BOAR Bench APK + kit (facts table) on the MacBook; tree hash = desktop; relay-ready bundle (APK, s16 runbook, ADB-PROBE-RUNBOOK, frozen gates, netstats step) | APK sha in `bench-app/build`; `audit-apk.py` NO-NETWORK, 0 Play classes; bundle checksum in QUEUE | 0 |
| Tue 10-13 | B | v0.3 go/no-go per spec (count items by name); claim text drafted for both branches | QUEUE decision row; EXPOSURES unchanged | 0 |
| Tue 10-13 | B | T1 public-61: criterion (sha) covering both protocols, a competitor team answer provenance check vs their [competitor score removed], MDE note; generate cut 7 + deep-think-512 on the mini (≈ 1 h + 1.5 h) | criterion sha committed before generation; 2 × 61 traces, 0 errors | 0 |
| Tue–Thu | A | Android UI wiring in the fork worktree, no push: rebase `forge/android-ship` on upstream main (count conflicts first), `answerBridge` + `runChatAnswer`, caveat string in the card UI | identity check 20/20 vs `answerEval`; product APK builds without INTERNET; `audit-apk.py` clean | 0 |
| Wed 10-14 | B | Judge T1 in one sitting (Opus N=4) → comparability table BOAR-4B / BOAR-deep / a competitor team / reference, same grader, CIs, paired gap | table + aggregate sha; shard rc 0, rows = 2×ids | ≤ 450 Opus |
| Wed 10-14 | A | Deep-in-demo go/no-go (O3); 0-call "fast answer, deep upgrade" table from K/H rows; A15 latency budget stages into the demo plan | decision row; table in `arms/` | 0 |
| Thu 10-15 | B | Amend and hash addendum-05 (D4), reviewer verdict; 0-call latency-capped metric on K/H rows; correctness-only ratio | addendum sha committed; reviewer file; recompute attached | ≤ 20 (sanity) |
| Thu–Fri | A | REPRO-PLAN L1–L6: export script, path parametrisation, leak greps, asset BOM (sha, size, licence, host; no UNKNOWN; ≤ 50 GB), REPRODUCE.md, fresh-clone dry run by a second agent | fresh clone reaches a validated v0.1 trace from REPRODUCE.md alone; L4 greps clean | 0 |
| Sat–Sun | A, C | README-claim.md (≤ 1 page) + DEMO-SCRIPT.md (6 queries incl. a 1B-fail item and the upgrade timing) with the caveat grep gate; `ledger.py` → `results.csv`; CLAUDE.md state block rewritten from the ledger; CLAIM-DRAFT v3.8 frozen as METHODS.md; weekly reviewer pass on README + plan | ledger reproduces every CLAUDE.md number (mismatches listed); caveat grep passes; ≥ 3 of CLAIM-DRAFT §4 rows 9/10/12/13 move to Met or Partly | 0 |

Dependencies: Mon C before any judge run; the ADR before repo export; SEEDVAR s44 (running on the mini, do not touch) before the addendum-05 power table; no task depends on a phone run.

### Judge budget for the week

| Bucket | Opus | Haiku | Other |
|---|---|---|---|
| T1 public-61 (D3) | ≤ 450 | 0 | — |
| addendum-05 sanity, 0-call recomputes | ≤ 20 | 0 | — |
| Deep-config equivalence on cut 7 (D4 of §2.D), optional | 0 | ≤ 40 | — |
| Device s16 scoring, only if a phone run happens | ≤ 32 | 0 | — |
| Reserve (near-miss escalations, reviewer) | ≤ 100 | ≤ 200 | — |
| O1 cross-family | 0 | 0 | 204 GPT, only with the OK |
| **Total cap** | **≤ 600** | **≤ 250** | |

`arm.sh` prints the cumulative weekly count at each judge step; the audit's pipeline metric (floor-adj points per 1,000 judge calls) is expected ≈ 0 this week by design, because the spend goes to comparability, not quality.

### Stop rule (restated, now enforced by tooling)

An arm launches only if its criterion has a Power block (expected Δ with its source, n, seeds, MDE from SEEDVAR σ_run) with expected Δ ≥ MDE or the tag `blocker`; its family is not in `CLOSED.md` without a `reopen:` mechanism line; L1 uses the stratified random slice and the futility rule; a verdict from one seed on V-para is labelled "one seed, V-para" and cannot close a family; post-hoc splits are hypotheses, never verdicts.

## 5. UNKNOWN

- Whether a ≥ 11 GB phone run happens this week (r4to's relay decision); the plan does not depend on it.
- Claim channel: whether an updated build under claim #124 counts as "materially different".
- Upstream drift since 38f996d1 (10-03) and the conflict count for the UI wiring.
- r4to's v0.3 writing capacity (≈ 14 h by 10-17) and the D1–D3 choices.
- a competitor team answer-file provenance vs their published [competitor score removed].
- Paid-API OK for the cross-family judge; human-pairs OK.
- Asset hosting under the public-upload rule; the emergency detector's base-model licence.
- SEEDVAR s44 result (σ_run for the thinking tier).
- Whether any competitor received a confirmation since 10-02 (CLAIMS_31.md is from 09-26).

## 6. Pipeline metrics for the week

1. CLAIM-DRAFT §4 requirement rows moved from "Not yet" to "Met / Partly" (target ≥ 3 of rows 9, 10, 12, 13).
2. One comparability table (BOAR-4B, BOAR-deep, a competitor team, reference) with CIs, same grader.
3. v0.3 items in `work/` (count by name) vs the 10-13 go/no-go.
4. Opus calls ≤ 600, Haiku ≤ 250; cumulative count printed by `arm.sh`.
5. `ledger.py` reproduces every number in the CLAUDE.md state block.

## 7. Double-check (2026-10-10 evening): corrections and the corrected sequence

Method: 4 independent verifiers (`opus`/`high`, disjoint claim sets, primary sources only, read-only) + 1 red team of the plan (workflow `wf_39725c79-1bd`). 32 load-bearing claims: **10 verified, 20 partly, 2 false**. Everything below supersedes §4 where they differ.

### 7.1 What was wrong or stale in §1–§4

| # | Claim in §1–§4 | Verified state | Effect on the plan |
|---|---|---|---|
| 1 | Plan written as if this were the only coordinator | A second coordinator session ("ai research") ran after 13:30: DEEPSAMP Q/P, THINK4B-V02, DEEPWIKI (all NO), SEEDVAR s44, DEEPROUTE-V02, then **CLAIM-READINESS-2026-10-10.md** (17:34: gaps a1–e4, decisions D-A…D-D, schedule 10-13 → 10-29), `handoff/DEMO-QUERIES.md`, `handoff/DEMO-POST-DRAFT.md` (reviewed, ACCEPT WITH EDITS) (QUEUE l.875–889) | Next week starts from CLAIM-READINESS, not from a new plan; the demo query list and post draft already exist |
| 2 | "Build the cut-7 APK on the MacBook" | **False**: no JDK 17 on the MacBook (`java_home -v 17` fails); `bench-app/scripts/build-android.sh` targets the mini (BENCH-APP.md l.58) | APKs build on the mini (≈ 30 GiB free, 25 GiB alarm, ≈ 15 GB build footprint: clean first) or after r4to installs JDK 17 |
| 3 | "No BOAR number on the public 61; T1 = the week's judged experiment" | The 61 is **BOAR's own public dev set** (`build-v2.mjs`, commit 539b20a0, PR #14; 8 ids sit in v0.1, which was tuned on); a competitor team's answers are **not local** (clone from 09-25); old BOAR numbers exist (4B 0.40–0.49, old judge/engine, `wt/eval/eval/reports/official-v2-6c3d6c6.md`); the drop followed r4to's questions (QUEUE l.744) | **T1 withdrawn** from the week. Only if r4to asks: 4B only, answers fetched fresh, reported as narrative, old numbers cited |
| 4 | "Bar reading = floor-adj CI low > 0.50 AND win-rate > 0; remove the conjunct" | **No such sentence exists.** `analysis-plan.md` §3 l.17: the bar is judged on the **raw ratio** (r4to's decision, 2026-10-02); addendum-05 §3 only makes floor-adjusted the headline, "formal decision status: TBD". Under raw, deep+think v0.2 0.608 (CI low 0.575) clears on dev data; floor-adj 0.508 (CI low 0.467) does not | The bar scale is **r4to's decision**, not an addendum edit. Default if silent: raw stays the formal rule; raw, floor-adj and win-rate shown together; "bar not shown above" |
| 5 | "SEEDVAR s44 running, do not touch; σ_run pending" | **Finished 13:47** (QUEUE l.876): H V-para s42/43/44 raw 0.533/0.572/0.544, mean 0.550 **SD 0.020**, floor-adj mean 0.432 SD 0.025, per-item r 0.48–0.68, win 0; v0.2 ±0.01. Mini idle since 17:05 | σ_run available now; the mini is free for APK builds |
| 6 | O1 GPT cross-family judge, O2 human pairs | HANDOFF-10-10 l.3 "no paid API keys"; QUEUE l.454 r4to "NO human review" | **Both withdrawn** |
| 7 | Device items framed as relay-ready bundles | r4to's 10-07 ruling (QUEUE l.770, item 4): "device-dependent tasks dormant, **not to be proposed again**"; HANDOFF-10-08 l.5 "do not re-ask". CLAIM-READINESS already carries D-D (relay) | Raise once inside the single message, then nothing device-side until r4to relays |
| 8 | Wiring = 1–1.5 days | `forge/android-ship` is the 10-03 ship stack (3 commits), not cut 6/7; must be restacked on cut 7 → ≈ 2 days. upstream/main unchanged since 10-03; `ios_android` touches only App.tsx, app.json, package.json outside `src/ui-ios` | Budget 2 days; start Monday; conflict risk low |
| 9 | 136 / 6 unpushed commits; 67 folders / 131 JSONs; 0/32 criteria; win 0/0/110 | rnd **153**, boar-eval **7** ahead; 69 arm dirs (62 with criterion/result), 154 aggregate JSONs; 35 criteria since 10-07, 0 mention MDE/power; v0.2 win rows are 0/1/109 for some configs → say "win 0" | Numbers only |
| 10 | Speed facts | p50 49 s / p90 77 s = **cut 6** on the A15 (not cut 7); 2.0–2.7 tok/s = cut-5 rate sweep; `A15-LATENCY-BUDGET.md` is a cut-4 projection, not a measurement | Public speed sentence: "cut 6, 8 GB A15"; no per-stage latency without a cut-7 phone run |
| 11 | MacBook slot waits on "ok MacBook" | Only deep-tier residency waits; **4B generation runs on the MacBook now** (GGUF local, 27 GiB free; QUEUE l.790/793) | Frees the mini for builds |
| 12 | Power block + random-slice tooling on Monday | Moratorium makes them moot this week; the fix that touches claim numbers is **T3** (`judge.mjs` l.66 drops errored traces; `floor_metrics.py`/`paired.mjs` intersect ids: timeouts leave the ratio) | Keep the fail-closed judge pass; defer Power block/slice addendum until an arm is proposed |
| 13 | v0.3 as a committed front | 0 items on 10-10; 4B P(CI low > 0.50) ≈ 0 (z ≥ 4.7), deep+think ≤ 15 %; D-C already offers "no v0.3" | v0.3 conditional on ≥ 60 items by ≈ 10-15; otherwise the claim says "no unexposed set" and cites EXPOSURES |

Confirmed unchanged: ui-android runs the legacy `runAdaptiveChat` path (P1); submission deliverables unbuilt (P2); no cut-7 APK anywhere, cut 7 on no remote branch (P3); claim channel open, D-A target 10-13 (P5); `shard_judge.sh` always exits 0, STOP never read, `paired.mjs` intersects (T2); judge drops errored traces (T3); deep config is a 3-patch chain with no cumulative patch or tree hash (T8); "no human review", GPT pilot held (R7); a public-61 run touches no blind set, needs a QUEUE row, no EXPOSURES row (R5); MANDATE off-limits still lacks `blind/` (R5).

### 7.2 Corrected sequence (supersedes §4 Tasks; red team confidence 0.7; adopted with edits)

| # | Step | Done when | Depends on |
|---|---|---|---|
| 1 | **Back up the evidence**: `git bundle --all` of rnd (153 ahead), boar-eval (7), wt/cut7 (`coord/cut7`), bench-app, forge-android → scp to the mini; `git bundle verify`; shas in QUEUE. One-line request to r4to to push the two private repos | 4–5 bundles verify on the mini; shas logged | — (≈ 15 min, no permission) |
| 2 | **One message to r4to, once, from CLAIM-READINESS** (check first whether the other session already sent it): D-A claim vehicle, D-B where cut 7 source goes public, D-C v0.3 (≥ 60 items by ≈ 10-15 or none), D-D device relay, **bar scale** (raw per 10-02 vs floor-adjusted). Each with a default if silent. No GPT, no human pairs, no device purchase, no T1 unless he raises it | Sent and logged in QUEUE with the defaults; no follow-up | 1 |
| 3 | **Wiring**: restack `forge/android-ship` onto cut 7 (6d0b93b1) in a local worktree; `src/ui-android` ChatScreen → `answerService` (`answerBridge`, `runChatAnswer`); caveat string in the card UI; identity check 20/20 vs `answerEval`; typecheck; **no push**; PR-ready for the app maintainer | 20/20 identical; local commit hash in QUEUE | 1 (≈ 2 days) |
| 4 | **Fail-closed judge pass** (parallel with 3): `shard_judge.sh` exits with the validation rc and honours STOP; `arm.sh`/`paired.mjs` fail on non-empty `missing`; runners write `FAIL` on adapter rc ≠ 0; errored/timed-out answers scored at the floor or n judged vs n planned reported | A synthetic partial judgments file and an errored trace each fail the stage | — |
| 5 | **APKs on the mini**: product (cut 7 + wiring, no INTERNET) and BOAR Bench cut 7; `audit-apk.py` (no network, no GMS → GrapheneOS); tree hash = desktop; disk checked before/after | Both sha256 recorded; audit clean; mini ≥ 25 GiB after cleanup | 3 |
| 6 | **Repro package staged locally** (REPRO-PLAN L1–L6): one cumulative cut-7 patch vs 0cfd4a77 + tree hash; REPRODUCE.md; BOM (sha, size, licence, host; mmBERT licence checked or detector optional; ≤ 50 GB); reference answers as hashes; leak greps (blind/, veil/, v0.2 plaintext, personal data); fresh-clone dry run by a second agent | Dry-run agent rebuilds with matching hashes from REPRODUCE.md alone; greps 0 hits | 1, 5 |
| 7 | **Claim text**: README-claim (≤ 1 page), DEMO-SCRIPT from `handoff/DEMO-QUERIES.md` (exists) with one 1B-fail item and answers captured from desktop cut 7; post draft (exists, reviewed) updated; speed sentence labelled "cut 6, 8 GB A15"; caveat grep; bar wording per r4to's answer (default "bar not shown above") | Reviewer ACCEPT with edits applied; greps pass | 2, 6 |
| 8 | Only if D-D = yes: relay bundle (product APK, bench APK, s16 runbook, ADB-PROBE-RUNBOOK with frozen gates, netstats step) in `handoff/` | Zip sha logged; delivered to r4to | 2, 5 |
| 9 | Only if D-C = yes and ≥ 60 items by ≈ 10-15: amend + hash addendum-05 (build = cut 7, bar scale per r4to, n judged vs planned, power note with σ from SEEDVAR), refs, gates, freeze, **one 4B claim run ≤ 240 Opus** | Criterion sha before the run; result + EXPOSURES row; claim text updated | 2, 4 |
| 10 | **Readiness gate ≈ 10-20/22**: everything staged for r4to's single go-ahead on repo publish, post and poidh claim; public-61 and deep-tier build work parked unless r4to asks | Checklist with every CLAIM-READINESS row closed or marked r4to-only, with paths and shas | 5, 6, 7 |

Judge budget (revised): Opus ≤ 300 (240 for the v0.3 claim run only if D-C = yes; 60 reserve), Haiku ≤ 100; T1 0 unless r4to asks (then ≤ 450); GPT 0.

Why this order: the bounty's fallback judgement (creator + contributors pick "the build that best satisfies the requirements") rewards an installable app that runs the measured engine, a public repo and a demo; our numbers will not earn the post author's confirmation. Steps 1, 3–7 need no permission and close the three gates only r4to can open (publish, post, claim) with a single OK each. Desktop quality arms: nothing left to launch (HANDOFF 15:28/17:05), so the moratorium is a coordinator call, not a loop stop.

### 7.3 Decisions that are r4to's (once; defaults apply if silent)

| Decision | Default if silent | Blocks |
|---|---|---|
| D-A claim vehicle: update #124 (maintainer signs) or new claim | Stage materials for both; post nothing; APK debug-signed locally | publication only |
| D-B where cut 7 source goes public: snapshot repo (Option C) / tagged branch on the fork / upstream | Prepare the Option C snapshot locally, scrubbed and dry-run tested; push nothing | publication only |
| Bar scale for the claim sentence: raw (10-02 rule) vs floor-adjusted | Raw stays formal; show raw, floor-adj, win-rate together; "bar not shown above" | claim wording |
| D-C v0.3: ≥ 60 items by ≈ 10-15, or none | No v0.3; claim says "no unexposed English set", cites EXPOSURES.md | nothing |
| D-D relay device tests (4B benchmark, cut-7 BOAR Bench, ADB probe) and the app maintainer note | No relay; device evidence = cut 6 on the 8 GB A15; deep tier desktop-only, separate row | nothing |
| Push boar-eval and boar-rnd to the private remotes | Bundles on the mini only | nothing |
| Public-61 head-to-head vs a competitor team (≤ 450 Opus, their answers fetched fresh) | Not run | nothing |
| JDK 17 on the MacBook for local APK builds | Build on the mini | nothing |

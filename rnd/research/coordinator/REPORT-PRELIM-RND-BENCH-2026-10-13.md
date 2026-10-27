# BOAR R&D and benchmark: preliminary report (2026-10-13)

Status: draft for r4to, assembled from the coordinator files (every number is copied from the cited file; nothing under `blind/` or `rnd/veil/` was opened). Scope: poidh bounty #31, offline Android research assistant ">50 % as good as internet + frontier AI", ≤ 12 GB RAM, English, deadline 2026-10-31. All numbers are development data unless marked.

## TL;DR

- **The bar is not met and no measured lever on ≤ 12 GB reaches it.** Headline metric = floor-adjusted quality ratio vs a frontier reference (Opus + web), target CI low ≥ 0.50. Claim build (4B): **0.26 on V-para, 0.40 on v0.2, 0 wins out of 161 items**. Best configuration (35B deep tier + thinking 512): **0.44 on V-para, 0.51 on v0.2, 0 wins**; needs a 12 GB phone that we do not have (BAR-TABLE.md §1).
- **The raw ratio looks better than it is.** Raw 0.51 on v0.2 for the 4B is a rubric-floor artefact: an always-decline system scores raw ≈ 0.31 for free. Lead every public number with floor-adjusted + win-rate (BOUNTY-BOARD.md "How to read the ratio").
- **The benchmark is the solid part.** One harness (boar-eval) runs the whole engine end to end on desktop or phone, with frozen criteria (sha256), two-order LLM judge, paired bootstrap CIs, exposure ledger and a desktop-node adapter that reproduces phone quality (phone 0.561 vs desktop 0.558/0.560 on 57 items). Weak spot: the v0.2 held-out set is burnt (plaintext in git history), so a final number needs the v0.3 set, which has 0 items written.
- **49 lever families registered in CLOSED.md** (36 rows at 10-11 = 28 closed + 8 "not detected at MDE"; rows 37–49 added in the loop and pack cycles): model size, retrieval, prompts, fine-tune data, thinking budgets, routing, pack stacking. 0 bar points adopted since 10-10 (≈ 1,180 + 1,840 judge calls in the last two cycles). The measured walls: model size +0.06 (knowledge), retrieval captures +0.02 of a +0.10 oracle gap, reader quality bounds pack value (CLOSED.md, BACKLOG pipeline metric rows).
- **Knowledge Packs are a shipped product line, not a bar lever.** 11 packs public on hf.co/datasets/r4topunk/boar-packs; one matching pack lifts the 4B by +0.032 (+0.016…+0.050) on its own 180 self-tests, all 9 installed together cost −0.016, and the deep tier gains nothing from any pack (−0.002) (REPORT-PACKS-2026-10-13.md §1).
- **Submission side not started**: no public repo with the claim build, no installable APK that runs the measured engine, no demo post, claim vehicle undecided (CLAIM-READINESS-2026-10-10.md).

## 1. Goal and bar

| Item | Value | Source |
|---|---|---|
| Bounty | poidh #31: offline assistant ">50 % as good as internet + frontier AI", ≤ 12 GB RAM, English; proof = screenshot + post + public repo | BOUNTY_31.md |
| Formal rule (r4to, 2026-10-02) | raw ratio CI low > 0.50 on V-para **and** v0.2 | BAR-TABLE §0 |
| Primary research target | V-para floor-adjusted ratio, 2 seeds, Opus judge both orders, CI low ≥ 0.50 | BAR-TABLE §0 |
| Secondary | floor-adjusted ≥ Haiku 5.5 no-web anchor (0.48 on V-para) | BAR-TABLE §0 |
| Reported, never gated | pairwise win/tie/loss vs the reference | BAR-TABLE §0 |

Floor-adjusted = Σ(S − 1) / Σ(R − 1): the rubric minimum (1/5 per axis) is removed from both sides, so a blank answer scores 0 instead of ≈ 0.31 raw (`boar-eval/bench/v0.2/plan/floor_metrics.py`, `above_min`).

## 2. The benchmark (boar-eval)

**Pipeline.** `DATASET → ENGINE@commit behind one protocol → TRACE → SCORERS → REPORT` (boar-eval/README.md). Adapters: desktop-node (simulates the phone; byte-deterministic on the 4B path, A/A 20/20 identical answers, SEEDGEN) and the BOAR Bench Android app (same engine code on device). Scorers: bench, retrieval, timing, jev (cheap boolean fact checks), stats. Harness: `judge.mjs` (two-order rubric judge, sharded N = 4), `gate.py`, `stability.py`, `ladder.py`, `report.py`, `anchors.mjs`.

**Sets.**

| Set | n | Status | Use |
|---|---|---|---|
| v0.1 EN | 57 (+ public items 240 judgments for no-harm) | dev | fast loop, no-harm checks |
| v0.2 | 110 | was held-out, **burnt** (plaintext in boar-eval git d8154b6 + 4 runs) → dev | claim numbers so far |
| V-para (V-para) | 51 judged / 58 | held-out for the 4B claim runs (cut 3/6); dev-style for everything after 10-06 | bounty-style set |
| V-exact | 11 | slice | the post author's literal questions |
| Pack self-tests | 11 × 20 = 220 public | dev, pack-matched | pack value |
| v0.3 | **0 items** (spec + infra + pre-commit hook blocking blind plaintext ready) | to be written by r4to with a non-Claude model | the final unexposed number |

Sources: EXPOSURES.md TL;DR, BENCH-V03-SPEC.md, packs/selftest/README.md.

**Judge protocol.** Rubric 1–5 on correctness, completeness, usefulness, both presentation orders, ratio of sums; paired per-item bootstrap (B 2,000, seed 11) for Δ; stratified two-level bootstrap for absolute CIs. L1 triage = Haiku 5.5 low (54/57 same winner as Opus, ≈ 14× cheaper than Sonnet, compresses gaps); L2 = Opus judge.v1 for confirmation and claim numbers. A Haiku Δ within 0.01 of a threshold goes to Opus (arms/L1-PROTOCOL.md).

**Discipline.** Every deciding run has a frozen criterion (sha256 before the run); every exposure of a blind set is one row in EXPOSURES.md; MDE stated per set (v0.2 one seed ≈ 0.025 raw; V-para two seeds ≈ 0.03; 20-item slice ≈ 0.08); closed families registered in CLOSED.md with the reopen rule (new mechanism only).

**Anchors on V-para (same judge, no web):** Haiku 0.588 raw / 0.48 floor-adj, Sonnet 0.961, Opus 1.044 (BOUNTY-BOARD scoreboard).

## 3. Where every configuration stands (BAR-TABLE §1, Opus judge, 2 seeds unless noted)

| Config | V-para raw | V-para floor-adj | v0.2 raw | v0.2 floor-adj | Wins | p50 desktop | RAM class |
|---|---|---|---|---|---|---|---|
| **K** 4B claim build (cut 7 = cut 6 on these sets) | 0.413 (0.384–0.445) | **0.261 (0.224–0.300)** | 0.512 (0.478–0.549) | **0.388 (0.346–0.434)** | 0/51 · 0/110 | 6–10 s | 8 GB phone, ran on Galaxy A15 |
| D deep 35B, no thinking | 0.467 | 0.329 (0.294–0.362) | 0.568 | 0.457 (0.417–0.500) | 0 | 33 s | 12 GB |
| **H** deep 35B + thinking 512 (recommended) | 0.553 (0.524–0.581) | **0.436 (0.401–0.472)** | 0.608 (1 seed) | **0.508 (0.467–0.550)** | 0 | 79 s | 12 GB, never on a phone |
| T deep + thinking 1024 | 0.542 | 0.422 | 0.612 | 0.514 | 0 | 143 s | 12 GB |
| G Gemma 4 26B-A4B + thinking | 0.514 | 0.388 | — | — | 0 | 107 s | 12 GB |
| Z 4B thinking twin 512 (1 seed) | 0.439 | 0.293 | 0.485 (Haiku) | 0.350 | 0 | 24 s | 8 GB |
| Haiku 5.5 no-web anchor | 0.588 | 0.48 | — | — | — | — | cloud |

Readings: K fails the formal raw rule on V-para (short by 0.087) and straddles on v0.2; H meets the formal raw rule on both sets but floor-adjusted stays below 0.50 on V-para (CI high 0.472) and straddles on v0.2 (1 seed); win-rate is 0 everywhere. Seed noise on V-para for the deep tier: SD 0.020 raw over 3 seeds, so a one-seed Δ < 0.03 is noise (SEEDVAR).

Ladder, V-para floor-adj: 4B 0.26 → deep 0.33 → Gemma + think 0.39 → deep + think 0.44 → bar 0.50 → Haiku no-web 0.48 (secondary).

## 4. Levers measured and closed (CLOSED.md rows R1–R49, arms/*)

| Family | Result | Status |
|---|---|---|
| Model size, 4B → 35B MoE (DEEPREAD, DEEPVPARA) | +0.06 knowledge, +0.03 reading; MoE 25–35B tier is one plateau ≈ 0.60 closed-book | wall; deep tier needs 12 GB |
| Thinking budget on the deep tier (DEEPTHINK, DT512/256, DEEPTHINK-2) | curve 0 → 0.33, 256 → 0.39, **512 → 0.44**, 1024 → 0.42, 3072 no gain | knee at 512, adopted as recommendation |
| Thinking on the 4B (THINK4B, -V02) | +0.026 V-para / +0.009 v0.2, ×3.7 time | NO |
| Retrieval (scorecard, NAMEDSLOT, rv2, big packs, DEEPWIKI) | captures +0.02 of the +0.10 oracle gap; larger corpora crowd the 6 slots | wall |
| Prompts (COMPLETE, persona "detailed", answer styles) | completeness prompt −0.80 correctness; detailed persona −0.066 | NO |
| Structured FACTS (no model) | precision 90–97 %, FP 0/100 blind, recall 60–70 %, fires 0/110 on v0.2 | shipped in cut 7, no measured bar effect |
| Fine-tune data (DATA line) | under a strict faithfulness rubric: Opus teacher 16/20, +rejection 11/20, human CLAPnq 6/20 | closed; reopened once as H10 SFT-4B (running, criterion sha frozen 10-13) |
| Routing 4B ↔ deep (DEEPROUTE, -VPARA) | rule fires on 26–37 %, captures ≈ chance-level share of the deep gain | NO |
| Best-of-2 / verifier (DEEPBO2) | oracle +0.038, every selector at coin flip | NO |
| Sampling, context size, persona on deep (DEEPSAMP, DEEPCTX, DEEPFULL) | all within noise or negative | NO |
| Pack routing / stacking / keep rules (PACKROUTE, -2, GROUND-ST, STACK, CROWDQ; R46–R49) | router accuracy 0.25 / 0.61 vs 0.85 needed; keep rules recover articles 68 → 95 but chunks 43 → 54 (bar 55); stack +0.005 (−0.009…+0.021) | closed at the product level: no automatic routing |
| Judge economics (JUDGE2, HAIKUJUDGE, PARJUDGE, OPUSSHARD) | local Gemma judge κ 0.32–0.55 (ranking only); Haiku L1 54/57 same winner; sharding ×4.5 wall, 0 429s | adopted as protocol |

Pipeline metric: 0 V-para floor-adj points adopted per ≈ 1,180 judge calls in the 10-11 → 12 cycle, and 0 per ≈ 1,840 calls in the pack cycle (BACKLOG). Interpretation: the engine is at the plateau the measured components allow; remaining gains sit in model capacity (needs RAM) and reader faithfulness (H10).

## 5. Knowledge Packs (REPORT-PACKS-2026-10-13.md, independently reviewed: ACCEPT WITH EDITS, applied)

- **Format:** one SQLite per pack (zstd article blocks, 1,000-char chunks + FTS, bge-small lead vectors, per-row licence + attribution). Converter + builder on the mini, publish script with dry run and leak check, probes (coverage, crowding), 20 public self-test items per pack with verbatim evidence.
- **Published (11):** qa/ travel, ethereum, bitcoin, health, outdoors, cooking, money (Stack Exchange, CC BY-SA); topics/ firstaid v4, medlineplus (PD), factbook (CC0), simplewiki-en (CC BY-SA). 5 default-eligible (crowding share ≤ 0.40 and kit gold not lowered), 6 user-selected only.
- **Value on the 4B:** one matching pack **+0.032 (+0.016…+0.050)** pooled over 180; per pack simplewiki +0.10, ethereum +0.07, bitcoin +0.05, first aid/medlineplus/factbook ≈ 0. The lift tracks the keep step (packs whose passages survive on 15–16/20 items gain).
- **Cost of many packs:** all 9 as peers −0.016 (−0.033…−0.001); simplewiki takes 36 % of kept slots.
- **Deep tier:** no gain from any pack, pooled −0.002 (−0.020…+0.016); medlineplus −0.049 (only CI excluding 0, negative). Deep with pack beats 4B with pack by +0.054 (+0.034…+0.073): the reader, not retrieval, bounds pack value.
- **Coverage of the bounty-style set:** the 11-pack union covers 2/34 of the V-para items the kit lacks (6/34 with the kit): product value, not a bar lever.
- **Product reading for the app maintainer:** ship small user-selected packs; no automatic routing; general-knowledge packs user-selected only; keep rule + quota as an optional many-packs setting.
- Caveat on every health/safety pack: "AI-reviewed, not clinically reviewed".

## 6. Device evidence

| Fact | Value | Source |
|---|---|---|
| Cut 6 on Galaxy A15 8 GB, airplane mode | 73/73 answered; quality 0.561 (0.507–0.617) vs desktop 0.558/0.560; p50 49 s, p90 77 s; PSS max 4.41 GiB | QUEUE "A15 FINAL", CLAIM-DRAFT [S28] |
| Cut 7 on a phone | never run (FACTS fires 0/110 on v0.2, so cut 6 traces stand in) | CLAUDE.md |
| Deep tier on a phone | never run; competitor's public numbers for Qwen3.6-35B via bmoe on Pixel 8 Pro 12 GB: 4–6 tok/s decode, 7.9 GB → 1.9–2.8 min per thinking-512 answer | WEB-SWEEP-2026-10-09, DEEP-RESEARCH-2026-10-12 |
| bmoe (device engine) vs llama-server | not token-identical, judged-equivalent (Δ −0.012, CI −0.045…+0.020) | DEEPPAR |
| Devices available | Pixel 8a 8 GB (tester, unresponsive); no 12 GB phone; mini M4 16 GB, MacBook M1 Pro 16 GB | CLAUDE.md |
| Venue / GPS items | V-para venue items 0/7 → 7/7 with device location + the user's area tile (kit +3.65 MB) | VENUEGPS-2 |



- **Fastest generation measured:** BOAR 19.6 tok/s on the F3. Fastest claimed by another project: a competitor team ≈ 18 tok/s.
- **Where BOAR is behind:** time to the first word. First word 13.6 s → 6.4 s with 4 passages; LFM2.5 first word 27.2 s with sources; 1.6 s is Qwen2.5-1.5B with no sources.
- **Comparison table of 7 projects** (engine, models, speed, search, how each stays fast), two charts (tok/s measured vs claimed; time to first thing on screen, 0.1–300 s log scale), one row per project on which steps put something on screen without a model.
- **Fact-check of a pasted text about BOAR (4 errors):** LFM 14.8 tok/s is right but its first word is 27.2 s with sources (1.6 s belongs to the 1.5B, no sources); "13.6 → 1.9 s" was never measured (it is 13.6 → 6.4 s); the Expo app ships 6 CPU variants (llama.rn), the 7 are in the native rewrite; the "instant answer under 1 s without the model" code exists but the Android chat never runs it.
- **Not benchmarked:** none of the other 6 projects has been run on our phones; their numbers come from their repos on different phones, so the charts are not a ranking.
- **Their plan (≈ half a day):** install each app on the X6 (cool, airplane mode); ask all of them the same 10 self-written questions; time from outside the app (screen recording + adb); redraw the charts with measured numbers only. a competitor team (30 GB) and Offline Research (24.6 GB) do not fit on the X6 next to BOAR's data → those two on the F3.

**Reconciliation with this report's records**

| Topic | Sheet (teammate) | R&D files (this report) | Reading |
|---|---|---|---|
| Speed unit | tok/s, time to first word, external stopwatch | p50/p90 full-answer wall (A15: 49 s / 77 s, cut 6); desktop p50 per config | Complementary: the sheet measures UX latency, the harness measures answer wall on the quality runs. Neither set contains the other's phones (F3, X6 vs A15, Pixel 8a). |
| "Instant answer without the model" | code exists, Android chat never runs it | same finding: Android ChatScreen uses the legacy path, answerService not wired (CLAIM-READINESS b3) | Consistent; one gap, two owners agree. |
| Competitor quality | not measured | a competitor team v1.7.0 self-reported blind grading only (WEB-SWEEP-2026-10-10-competitors.md); nothing run here either | Quality of competitors is unmeasured by both sides; the 10-question device plan gives latency, not quality. |
| Which BOAR build | unknown (F3 run; model mix LFM2.5 / Qwen2.5-1.5B / 4B?) | claim build = cut 7 (4B, Qwen3-4B-Instruct Q4_K_M) | UNKNOWN: whether the 19.6 tok/s is the 4B claim build or a smaller model; must be stated before any public number. |

## 7. Infra and cost

- Runs on the Mac mini (`<runner>/kiln`), judge via `claude -p`; Haiku L1 sharded N = 4; Opus only for confirmation and claim numbers; jev for bulk boolean checks (cents per pass).
- Pack cycle 10-13: Opus 720 calls, Haiku ≈ 1,830, jev [usage detail removed], gateway [usage detail removed]. No public uploads except the packs (standing OK). Nothing pushed to public repos.
- Private repos: BENCH_REPO_LINK (harness), RESEARCH_REPO_LINK (research). Public fork r4topunk/boar-app carries none of the cut 6/7 engine patches.

## 8. Gap to a claim (CLAIM-READINESS-2026-10-10 §1, still open)

| Need | State | Owner |
|---|---|---|
| Unexposed final number | v0.3: 0 items (schedule 10-08…10-24 slipped) | r4to |
| Public repo with the claim build | cut 7 = local branch `coord/cut7`; publication form (snapshot vs fork branch) undecided | r4to |
| Installable APK running the measured engine | Android chat UI uses the legacy path; answerService not wired; upstream APK = 1.5B model | maintainer |
| Demo post (X/Farcaster), screenshot, poidh form | drafts only (CLAIM-DRAFT v3.8, reviewed) | r4to |
| Claim vehicle | update claim #124 vs new claim | r4to + maintainer |
| Public BOM / licence table / REPRODUCE.md | partly written (REPRO-PLAN) | coordinator |
| Deep tier as a "12 GB option" | desktop-complete; needs one 12 GB phone probe (runbook with frozen gates exists) | r4to (relay) |

## 9. Decisions, options, tasks

**Decisions (fixed by the evidence)**
- Public numbers lead with floor-adjusted + win-rate; raw second; bar "not shown".
- Deep tier reported separately, outside the 4B claim build, until it runs on a phone.
- Packs: no automatic routing; small, user-selected; keep rule + quota optional.

**Options (r4to's call)**
- O1 claim as is: BOAR Bench + desktop numbers + A15 run, UI wiring left to the app maintainer (fails the "install in minutes" reading).
- O2 maintainer wires answerService and ships a signed APK with cut 7 (closes the installable-app gap; depends on maintainer time).
- O3 attach the deep tier as a labelled 12 GB option if a tester phone passes the frozen gates.
- Honest framing option: publish the benchmark + packs + the measured ladder as the contribution, with the bar stated as not met.

**Tasks (next, in order)**
1. H10 SFT-4B stage 0 result (running on the mini; LEVER needs CI low > 0, Δ ≥ +0.03, no harm, faithfulness ≥ 80 %).
2. v0.3 items written outside the Claude family (110, or the 60-item fallback), refs, freeze.
3. Repo snapshot staged locally, scrubbed of blind/veil/v0.2 plaintext; BOM + REPRODUCE.md.
4. Engine handoff note to the app maintainer (answerService wiring, cut 7 patch, pack reading from §5).
5. Final claim text + independent Opus review; demo video on a phone in airplane mode.
6. Device speed round (teammate's plan, §6b): 7 apps × 10 shared questions on the X6/F3, external timing; add a quality pass by scoring the same 10 answers with the harness judge so the round yields latency **and** quality on one phone.

## UNKNOWN
- Whether claim #124 can be updated in place or a second claim is allowed.
- Who holds the release keystore; whether the app maintainer builds cut 7 into the app before 10-31.
- Any 12 GB phone for the deep tier before the deadline.
- v0.3: whether r4to writes it (110 vs 60 items) in time for a claim run ≤ 10-24.
- Haiku no-web floor-adjusted CI on V-para (underlying rows under blind/, not computed).
- Which BOAR build and model produced the 19.6 tok/s / 6.4 s first-word numbers in the teammate's sheet (§6b).

## Sources (all under rnd/research/coordinator/ unless stated)
BAR-TABLE.md · BOUNTY-BOARD.md (rnd/research/) · CLAIM-READINESS-2026-10-10.md · REPORT-PACKS-2026-10-13.md · HANDOFF-2026-10-13-PM.md · CLOSED.md · EXPOSURES.md · BENCH-V03-SPEC.md · DEEP-RESEARCH-2026-10-12.md · QUEUE.md (rnd/research/, tail 2026-10-13) · boar-eval/README.md · arms/* as named in the tables.

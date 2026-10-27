# Pipeline audit: are we moving toward the bounty post's bar? (2026-10-06, Fable coordinator)

TL;DR: **the process is rigorous, the direction is not.** Since 2026-10-04 the loop has produced ~15 arms whose v0.1 answers are byte-identical to cut 3; the held-out number moved +0.007 (noise) from `main` to cut 6. The team itself wrote "dev quality levers on the 4B are exhausted" (QUEUE L670) and kept running 4B arms. The only two levers ever measured above noise toward the bar, the deep 35B tier (+0.06) and gold-passage retrieval (+0.10 oracle), are parked or were killed on one seed. On the post author-style questions the 4B scores 0.41 raw / 0.26 floor-adjusted and wins 0 of 51 pairwise comparisons; a closed-book Haiku scores 0.59. **The judge model is not the problem** (Fable and Opus agree on 99% of verdicts); the headline metric is.

Supporting evidence (Opus audits, verified on samples by the coordinator): `audit-2026-10-06/audit-timeline.md` (177 log rows), `audit-metric.md`, `audit-state.md`. All numbers below are quoted from those files or recomputed from the judgment rows (aggregates only; no held-out text was read).

## 1. What the benchmark actually measures (Fable review)

| Fact | Value | Source |
|---|---|---|
| Ratio definition | Σ mean(correctness, completeness, usefulness, each 1–5) for BOAR ÷ same for the Opus+web reference; both A/B orders; disagreement = tie | `judge-core.mjs` summarize() |
| Rubric floor | a blank/wrong answer scores 1/5 on each axis → **an always-decline system gets ratio ≈ 0.31**, i.e. 61% of the 0.50 bar for free | arithmetic on the schema |
| cut 6 v0.2 held-out (s42, n=110) | raw **0.519** · floor-adjusted **0.397** · win/tie/loss **0/0/110** · items with BOAR ≥ 3/5: 41% | `blind/bench-v02/runs-cut6` |
| cut 3 V-para (the post author-style, n=51) | raw **0.413** · floor-adjusted **0.26** · win 0/51 · items ≥ 3/5: 2% · correctness ≤ 2 on 49% | `blind/V-para/runs-cut3` |
| Anchors on V-para (no web) | Haiku 0.588 (floor-adj 0.48) · Sonnet 0.961 · Opus 1.044 | same dir, `anchors/` |
| Reference = "frontier + internet"? | Opus without web scores 1.04× Opus with web → the reference is effectively "frontier model", web adds nothing on these items | anchors |
| Where the 4B loses (cut 6 v0.2) | correctness 3.4/5 but **completeness 2.07** and usefulness 2.2; BOAR median 53 words vs reference ≤ 250 words | rubric means + traces |
| Judge model | Opus 5.5, judge.v1 (v1-med is κ 1.0 with v1; effort flag probably no-op). Fable second judge: same winner 453/456, κ 0.894, ratio +0.004…+0.010 | `reports/devices-2026-10-02/fable/judge-agreement.md` |
| Speed in the score | **No.** A15 (8 GB): decode 2.0–2.7 tok/s, 69–112 s per answer. the post author's own complaint was 10 tok/s. No 12 GB phone has run anything | QUEUE L693, L698; audit-state §1 |
| Power | MDE at 2 seeds × 57 items ≈ 0.035; L1 (24 items) cannot see +0.03. exp-33 big pack (Δ −0.005/−0.016) and answer-style (S2 −0.031, s42 only) were killed on **one seed** | audit-metric §3, QUEUE L518, L537 |
| Held-out hygiene | v0.2 plaintext (110 items + gold) is in boar-eval git history, commit `d8154b6` on `origin/main` (private repo; removed from tree in `7d392c0`); 4 v0.2 runs; CO card built after held-out A02 failed; researchers' blind rule names only `rnd/veil/` | verified with `git show --stat d8154b6` |

**Reading.** "Ratio ≥ 0.50" on this rubric means "BOAR averages ~2.5/5 against ~4.9/5", which a human reads as "usually thin, sometimes wrong", not "half as good". The report already prints the floor-adjusted number (0.25–0.40); the board, the claim draft and CLAUDE.md lead with the raw one. **Changing the judge to Fable would move the number by < 0.01.** Changing the model tier moved V-para from 0.41 (4B) to 0.59 (Haiku) to 0.96 (Sonnet).

## 2. Loop evidence (from the 177-row timeline)

| Symptom | Evidence |
|---|---|
| Score flat on held-out | v0.2: main 0.506 → ship 0.503 → cut 3 0.513 → cut 6 0.519 (s42). Every step inside the CI; lower bound never clears 0.50 |
| Dev gain that did not transfer | v0.1 0.51 → 0.56 while judge version and item set changed; cut 3's +0.032 rests on 4 items; reusing judge verdicts alone moves 0.0065 (L676) |
| Answer-identical arms after "exhausted" (L670) | KVQ8, SPEEDPACK, CUT5-SPEED, CUT5-LITE, GATEFID, CHATGATE, FOLLOWQ, FOLLOWQ-G, HFU, HFU-FIX, HFU-FIX2, DETFU, DETMAX, SPECDEC, CRYPTOTRUTH: 15 arms, 2 adopted, **0 change on any judged ratio** |
| Same lever under new names | big pack ×10 (after Summit's "no fourth pack iteration", L211/L237); reader swap ×8 ("model line closed" written 3 times); verdict fixes ×11 (CV killed L596 → CVS next line → "CLOSED" L604 → CVO next day L606); health stack ~25 versions; safety checker 17 versions in 2 days |
| Post-hoc rescues | CUT5-SPEED not adopted → CUT5-LITE subset adopted; HFU-FIX → HFU-FIX2; FOLLOWQ → FOLLOWQ-G; PROMPTDIET ended → half of SPEEDPACK |
| Never-reported runs | ~15: #8 Jev gate, #18, cmpsplit v2.1 on 4B, Probe B, deep35 overnight (arm mismatch, never re-run), cut5-speed ABBA, q8 KV device speed, A15 full v0.1 (43/73) |
| Cost | ≈ 140 full-run equivalents, **12k–20k judge calls** in 6 days |
| Parallel fronts | 7 live vs the 1–3 WIP rule; the 3 that block the claim (public repo, Android UI → answerService, 12 GB phone run) have not started |

The V-exact jump 0.39 → 0.51 is one item (Paris–Rome, 0.29 → 0.94) fixed by a calculator built on that item (L512/L514). The 5-item plain CI is 0.30–0.74.

## 3. Why the loop happened (diagnosis)

1. **The bar was operationalised as a number that is reachable by polishing** (raw ratio 0.50 with a 0.31 floor), so the funnel rewards zero-risk routing/safety arms that keep answers identical. Each passes its frozen gate; none moves the bar.
2. **The two big levers were closed for non-quality reasons**: deep tier for work budget and lack of a 12 GB phone (L535, L542, L644); big packs on a single-seed Δ inside noise (L518). "THE bounty lever" (L502) was never given a powered test.
3. **Pre-registration without a stop rule.** Criteria are frozen per arm, but there is no rule "no arm unless expected Δ ≥ MDE on held-out". Post-hoc subsets and fresh small sets replaced larger n.
4. **the bounty post's bar is qualitative** (his public confirmation, or contributors' choice, L255). The team optimises a private number; the judge in the real world will type a question into the phone and wait. Speed and "breaks on anything interesting" are the two things he named, and neither is in the funnel.

## 4. Decisions (r4to), Options, Tasks

### Decisions to take now (fix direction)

| # | Decision | Why |
|---|---|---|
| D1 | **Headline metric = floor-adjusted ratio + win/tie rate + "% items ≥ 3/5 usefulness"**, raw ratio reported second. Bar for ourselves: floor-adjusted ≥ 0.50 on V-para | raw 0.50 is 61% free; V-para is the question style the post author will type |
| D2 | **Stop all answer-identical 4B arms** (routing, safety micro-fixes, speed trims on desktop) until the claim path is unblocked. The freeze (L701) must mean no new arms, not "research-only arms" | 15 arms, 0 ratio movement, ~¼ of the judge spend |
| D3 | **Reopen the deep tier as the primary quality lever**, gated by one cheap desktop test (T1) | only lever ever measured > noise (+0.06); the post author's own suggestion; a competitor team already runs the same GGUF at 4–6 tok/s on a 12 GB Pixel |
| D4 | **12 GB phone is the critical path.** Nothing else decides the bounty; if the phone is not here by 10-09, buy/borrow a second one | 0 measurements on the target tier; A15 is 8 GB and 2 tok/s |
| D5 | **Treat v0.2 as burnt** (git history + 4 runs + targeted fix). Promote it to dev; the final claim number needs a v0.3 written by a non-Claude writer or a human, ≤ 60 items | self-preference + leak risk on the one number we publish |
| D6 | **WIP = 3**: (a) device, (b) deep tier go/no-go, (c) claim package (repo, UI wiring, demo). Everything else parked | 7 fronts, 3 blockers untouched |

### Options (exploration, not committed)

- O1. **Answer completeness lever, properly powered.** "Thin" is 41% of the loss and answer-style was killed on one seed. One test: 2 seeds × 110 v0.2-as-dev items, target completeness, kill if correctness drops. Expected ≤ +0.03; only worth it if D3 fails.
- O2. **Hybrid tier**: 4B for instant/lookup (speed), 35B MoE for research/compare (quality). Router already exists (route gate). Decide after T1.
- O3. **Cross-family judge** (GPT-5.5, [usage detail removed] needs r4to's paid-API OK) and the 40-pair human check (1 h). Reduces self-preference risk on the published number.
- O4. Answer-time cap in the score: re-score the 25 phone answers counting > 30 s as declined. No new runs; tells us what the phone number looks like under the post author's "usable speed".

### Tasks (next 7 days, in order)

| # | Task | Owner | Done when | Cost |
|---|---|---|---|---|
| T1 | deep35 (Qwen3.6-35B-A3B, existing bmoe-cli D1 build) on **V-para + v0.2 as dev**, desktop, 2 seeds, same judge | Kiln on the mini | floor-adjusted and win-rate vs 4B, CI; decides D3 | ~320 judge calls, 1 day |
| T2 | 12 GB phone: confirm arrival/ETA today; on arrival run cut 6 (9 + 73 items) in airplane mode, then deep35 via bmoe-cli D2 if T1 passes | device session + Forge | TTFT, tok/s, PSS, ratio on 25 judged ids | 1–2 days after arrival |
| T3 | Rewrite the scoreboard: BOUNTY-BOARD.md, CLAUDE.md state block, CLAIM-DRAFT headline → floor-adjusted + win-rate + V-para first | coordinator | 3 files updated, numbers from this doc | 1 h |
| T4 | Claim path: wire ui-android → answerService (tasks A–D already written, L646), public repo skeleton, demo script | Forge | 9 items through the real app on the phone match BOAR Bench | 2 days |
| T5 | v0.3 final set: 60 items, non-Claude writer or human, the post author-style mix, hashes only in git | Compass (writer outside the Claude family) | frozen sha, 0 similarity collisions | 1 day + refs |
| T6 | Hygiene: decide on rewriting boar-eval history for `d8154b6` (irreversible, r4to), add `blind/` and git history to MANDATE.md's off-limits list | r4to + coordinator | decision logged | 15 min |

### Stop rule for the loop (apply from now)

An arm is pre-registered only if **all** hold: (1) expected Δ on the headline metric ≥ MDE at the planned n (≥ 0.035 at 2 × 57, ≥ 0.025 at 2 × 110), or it is a hard blocker for the claim; (2) it is not in a family already marked CLOSED without a new mechanism; (3) it has 2 seeds; (4) no post-hoc subset rescue. Metric for the pipeline itself: **held-out floor-adjusted points gained per 1,000 judge calls**; today it is ≈ 0.

## 5. UNKNOWN

- Whether any researcher agent ever ran `git show d8154b6` (no access log).
- The 12 GB phone's actual ETA (log says "in transit" on 10-04).
- deep35 numbers on V-para and v0.2 (never run; T1).
- How the existing claim #124 (the app maintainer, 1.5B) can be updated without hitting "materially different" (open since L255).
- Whether a cross-family judge changes the ranking (held pilot, L199).

## 6. Same-day results (evening, 2026-10-06): what the directional tests settled

| Test | Result | Settled |
|---|---|---|
| Retrieval scorecard + replay harness | recall@5 0.333; 19/39 gold misses are coverage, 7 ranking, 2 reader; harness 60/60 identical to the mini, 8 s | engine iteration no longer needs the judge |
| NAMEDSLOT (ranking fix) | recall@5 → 0.410 on the 3 predicted items, but 15/60 raw lists changed vs bar 12 | NOT ADOPTED; engine ranking upside ≈ 3 items, ratio Δ ≈ 0 |
| DEEPREAD (35B + gold passages) | 0.634 vs 4B 0.606; floor-adj 0.541; losses 93% | 35B reads no better than the 4B; packs are not a lever for either |
| COMPLETE (completeness prompt, 35B + gold) | 0.620; correctness 3.89 → 3.10; confident-wrong 7 → 15; 224 words, 3.3× decode time | NO: prompting cannot buy completeness without buying errors |
| FACTS (structured facts, no model) | 8 items +0.94/item, 0 drops; projected v0.1 Δ ≈ +0.027; blind set: precision 93–100%, 0/20 false positives, recall 67% | ADOPT (research-only); the only lever above noise found today |
| Literature | fine-tuning small readers works and transfers (3–8B), +5…+10 pts with DPO on 10k+ pairs; 1k LoRA SFT ≈ +0.1…+0.4; Q4 can erase gains | the hard path is real but modest and slow |

**Reading.** The gap to the bar is a reader-capability gap: model size (+0.06 knowledge, +0.03 reading), retrieval (+0.02 captured of +0.10), and prompting (completeness +0.44 at the cost of correctness −0.80) each hit a wall today, with numbers. What moved: deterministic answering where the question class allows it. By 10-31 the honest plan is (1) hybrid tier for knowledge, (2) FACTS and its generalisation (packs as modules: content + facts + triggers), (3) the device, (4) a claim written on the honest metric. A reader fine-tune is a 2–3 week research bet with a modest expected size; it does not reach the bar on its own.

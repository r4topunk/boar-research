# BOAR benchmark: current map and known flaws (2026-10-19)

Root is `<workspace>`. Shorthands: `E/` = `boar-eval/`, `C/` = `rnd/research/coordinator/`, `A/` = `C/arms/`, `B31` = `BOUNTY_31.md`, `Q` = `rnd/research/QUEUE.md`. I opened nothing under `blind/` or `rnd/veil/`.

## 0. Bounty text this has to match (quoted)
- The bar: "a casual info lookup and research tool that runs entirely offline on Android and is >50% as good as internet search + frontier AI models" (B31:7). How winners are judged: "against the requirements above and the bar described in the post author's post" (B31:60). The decider is a public confirmation from the post author (B31:62). He "is not affiliated with it or involved in judging unless he chooses to weigh in" (B31:15). The fallback is that "the creator and bounty contributors" select (B31:64-67).
- Requirements the ruler touches:
  - "handle useful research questions beyond simple factual recall, including explanation, comparison, synthesis, and reasoning" (B31:27)
  - "respond at speeds that feel usable for real lookups on a phone" (B31:28)
  - "work completely offline once installed" (B31:24)
  - "get the app running locally within a few minutes" (B31:41)
  - the demo should "include ones a 1B model would fail on" (B31:50)
- the post author's own words, from our fetch log `rnd/lantern/vitalik-thesis.md` (fetched 2026-09-30; the quotes need re-checking against the live posts):
  - ">50% as good as internet + frontier models", https://x.com/VitalikButerin/status/2100695863026954698 (l.8)
  - "much slower and less effective at difficult questions" and "my eval is "Tell me the best vegan restaurants in [city I am currently in]"", https://x.com/VitalikButerin/status/2103762130554204651 (l.38)
  - "anything slower than 50 tok/sec feels too annoying", https://vitalik.eth.limo/general/2026/04/02/secure_llms.html (l.28)
- **Source gap:** `BOUNTY_31.md` has no poidh URL. The original page has to be cited in the public ruler.

## 1. Map of the current benchmark

### 1.1 Item sets
| Set | n / mix | Who wrote items, gold and rubric | Refs | Status | Cite |
|---|---|---|---|---|---|
| **v0.1** (public dev) | 60. Explanation 11, reasoning 11, comparison 7, crypto 7, honesty 6, health 4, synthesis 3, local-food 3, danger 5, travel 3. 52 precheck, 3 venue, 3 firstaid, 2 judge-only | 33 kept from v0 (the post author-style originals, short quotes from his posts, BOAR v2). 27 "lantern" replacements written by an AI agent. a competitor team cases removed | Opus 5.5 + web, `reference.v1` | Dev. Public in boar-bench | `E/bench/v0.1/DATASET_CARD.md:3,19-30,62,85-90,106` |
| **v0.2-new** | 110. Explanation 21, reasoning 21, comparison 13, crypto 13, honesty 12, health 8, danger 10, synthesis 6, travel 6 | Two blind Claude Opus writers. 37+7 slots rewritten by Sonnet, Fable and Opus. 2 fact fixes by the coordinator | Opus + web, 110/110 | **Burnt, now dev**: plaintext pushed in `d8154b6`, one item printed, 12 generation runs | `E/bench/v0.2/DATASET_CARD.md:3,14,28-41,95`; `C/BENCH-V03-SPEC.md:77`; `C/EXPOSURES.md:13` |
| **V-para** | 58 = 51 judged + 7 venue. Explanation 17, comparison 7, synthesis 7, reasoning 7, crypto 5, local-food 7, travel 8. By family: 20 close paraphrases of his 4 queries, 28 same-family, 10 specialised travel | One Opus subagent, with OSM gold for venues | Opus + web. Location items get a "(The user's phone is in <city>.)" suffix | Held out for the cut 3/6 4B runs, **dev-style after 10-06**. 19 full spends | `Q:484`; `rnd/research/compass/exp/bounty-eval/VITALIK-SLICE.md:22-32`; `.../VPARA-BARS.md:2,16`; `C/EXPOSURES.md:14` |
| **V-exact** (public) | 11: "Tell me about Japan", PQ signatures, Mozi, Gríma/Saruman, Paris–Rome, 3 named-city vegan, 3 GPS vegan | the post author's verbatim queries. Rubric and grading written by Compass (agent) | Opus + web; OSM gold for venues | Run once. Only 5 judged items | `.../VITALIK-SLICE.md:8-20`; `Q:507` |
| **v0.3-ext** | Planned 110 (60 as fallback), same 10 strata, ≥40 % centred outside Europe/North America | r4to with one non-Claude web-UI model, hand fact-checked | The same non-Claude model through `reference.v1` in a web UI | **Not written (0 items). Dropped on 10-18 (D5)** | `C/BENCH-V03-SPEC.md:9-37`; `E/bench/v0.3/DATASET_CARD.md` (skeleton); `Q:1131,1349` |
| **Self-tests** | 11 packs × 20 = 180+ | An agent writing from the pack's own text ("agent-written, public, dev") | Pipeline (Haiku L1) | Dev only. Pack-matched by construction | `E/bench/selftest/*/questions.jsonl`; `C/PACK-CATALOGUE-2026-10-12.md:10,13` |
| **Slices** | longsession-v1 (10×5 turns, 3 extended to 15), chat-fu, mathroute, … | Agent-written | The reference is BOAR's own standalone answer | Dev | `E/bench/slices/`; `handoff/CLAIM-POST-v4.2.4.md:21` |

### 1.2 References ("internet + frontier")
- The `reference.v1` prompt (sha `d5144343…`) says: search the web, "Keep the answer under 250 words", lead with the direct answer, end with Sources (`C/bench-v03/refs-prompt.md:11-21`). It runs as `claude -p --model opus` with WebSearch and WebFetch, one call at a time (`E/bench/v0.1/refs/gen_refs.mjs:15-24`).
- Reference text is gitignored for v0.2 and V-para. For v0.1, the text was staged into the public bench repo (`Q:1146`).

### 1.3 Judge (`judge.v1`)
- Pairwise, BOAR vs the reference, in both A/B orders (`E/harness/judge.mjs:2-7,125-137`).
- Prompt (`E/scorers/vendor/eval-lib/judge-core.mjs:64-81`):
  - "Do NOT reward length…"
  - "A correct 'I am not sure' is better than a confident wrong answer"
  - false premises must be corrected
  - "tie" when the two answers are practically equal
- Rubric: correctness, completeness and usefulness, each an integer 1–5. A wrong claim caps correctness at 2. An uncorrected false premise caps it at 1 (`judge-core.mjs:40-51`).
- The author notes (the item rubric bullets) go to the judge (`judge.mjs:128`).
- Blinding strips `<think>`, Sources blocks, links, `[n]` markers and bold (`judge-core.mjs:5-20`).
- If the two orders disagree on the winner, the result is a tie. Scores are averaged over the orders (`judge-core.mjs:94-98`).
- Venue items are scored by OSM, not by the judge.
- Rows carry provenance (traces, questions and refs shas, model, version). Stale rows are refused (`judge.mjs:108-115`).

### 1.4 Metrics
- **Raw** = ΣS/ΣR. The pre-registered bar is raw > 0.50, judged by its CI (`E/bench/v0.2/plan/analysis-plan.md:16-20,58`).
- **Floor-adjusted** = Σ(S−1)/Σ(R−1), the `above_min` field. **Above-decline** = (raw−0.306)/(1−0.306) (`analysis-plan.md:22-25`; definitions in `C/BAR-TABLE.md:9-20`).
- The current research target is the V-para floor-adjusted CI low ≥ 0.50, with win-rate "reported, never gated" (`C/BAR-TABLE.md:7`).
- Claim order: W/T/L, then floor-adjusted, then raw (`handoff/CLAIM-POST-v4.2.4.md:15`).
- **Wins+ties (EVALFIX):** 1 tie in 1,052 rows. Wins+ties = wins = 0 on V-para (CI upper bound 0.07) (`A/evalfix/EVALFIX.md:1-13,27`).
- CI: stratified two-level bootstrap, 2,000 resamples, seed 11. Planned seeds 42/43/44; claims used 2 (`analysis-plan.md:17-19`).
- Secondary metrics in the plan:
  - the 1B-class gap
  - % correct (≥4)
  - abstention precision and recall
  - 7 axes: quality, truthfulness, safety, retrieval, latency, resources, stability, "never one average" (`analysis-plan.md:26-36`; `E/README.md:19`)
- External checks in the plan:
  - a cross-family judge, where "the lower of the two is the headline"
  - a 40-pair human label check by r4to and the app maintainer (`analysis-plan.md:38-50`)

### 1.5 Judge protocol and judge-family studies
| Study | Result | Cite |
|---|---|---|
| L1-PROTOCOL | signal20 slice (the 20 hardest ids). Paired only. Promote to Opus if Δ ≥ +0.03 or ≥ +3 wins. Haiku 5.5-low replaced Sonnet-low (10-07). Sharding N=4/8 allowed. Haiku near-miss rule (±0.01 → Opus) | `A/L1-PROTOCOL.md:1-14` |
| JUDGE2 (Gemma 4 26B local) | Ranking kept (+0.026 vs +0.029). Scores **+0.11 above Opus**. κ 0.32/0.55. Good for triage only | `A/judge2/JUDGE2.md:2,39` |
| HAIKUJUDGE | Adopted as L1 (same winner 54/57). Compresses gaps: +0.007 vs Opus +0.029 | `A/haikujudge/HAIKUJUDGE.md:1-3` |
| XFAM / XFAM-V02 (OpenAI gpt-5.6-sol via Codex) | Ratios 0.08–0.11 higher. V-para floor-adjusted: 4B 0.361 vs 0.261, deep 0.577 vs 0.436. v0.2: 0.517/0.639 vs 0.388/0.508. Spearman 0.88–0.97. Win-rate 0–6.4 %. Post hoc, not pre-registered | `handoff/CLAIM-POST-v4.2.4.md:27`; `handoff/CODEX-XFAM-JUDGE-2026-10-16.md`; `C/VPARA-DIAGNOSIS-2026-10-19.md` §2 |
| JUDGEVAR (Opus test-retest) | σ_judge ≈ 0.003 raw. Winner agreement 51/51 | `A/judgevar/JUDGEVAR.md:3` |
| SEEDVAR | Deep+think512 on V-para: 0.533/0.572/0.544 (SD 0.020). Floor-adjusted mean 0.432. A one-seed Δ < 0.05 is noise | `A/seedvar/SEEDVAR.md:1-15` |
| Anchors | Opus *without web* = **1.029** of Opus+web: "the web adds nothing this judge can see". Haiku no-web 0.588 on V-para | `E/reports/anchors-2026-10-02/ladder.md:16,36,67` |

### 1.6 Device parity and latency
- **DEVICE-X6** (POCO X6 Pro, airplane mode, no INTERNET permission):
  - 72/72 answered
  - fast tier p50 30.7 s, p90 48.4 s, TTFT 18.5 s, **decode 5.5 tok/s**
  - phone = desktop: 0.529 vs 0.529 raw on v0.1's 57 items, **Haiku judge**, one run
  - the **native app** (the actual submission) scored 0.440: **−0.089** vs the measured engine
  - Source: `A/device-x6/DEVICE-X6.md:9-30`
- Latency is reported as a separate axis and is not part of the quality score (`E/README.md:19`).
- Deep tier: desktop only. p50 79 s with thinking 512. Phone time estimated at 1.9–2.8 min from a competitor's numbers (`C/CLAIM-DRAFT-v4.2.4.md:292`).

### 1.7 Current public claim text
- `handoff/CLAIM-POST-v4.2.4.md:13-35`:
  - 4B cut 7: V-para W/T/L 0/0/51, floor-adjusted 0.261, raw 0.413. v0.2: floor-adjusted 0.389, raw 0.513.
  - Deep tier: V-para floor-adjusted 0.436 / v0.2 0.508.
  - "BOAR is not shown to be half as good as frontier AI with web" (l.25).
  - "Our own pre-registered rule, not the bounty's…" (l.25).
  - Limits paragraph (l.35).
- Results files: `C/CLAIM-RESULTS-cut6.md:70-81` (P1 FAIL 0.413; P5 venue 0/7).

## 2. Known flaws and interpretation risks (already recorded)

### A. Construct: does the ruler measure "50 % as good as internet + frontier"?
1. **Floor artefact.** An always-decline system scores 0.306 raw, so "about 61 % of the 0.50 bar is free" (`C/audit-2026-10-06/audit-metric.md:8,87`). On V-para the 1/1/1 floor is 0.206 of raw (`C/VPARA-DIAGNOSIS-2026-10-19.md:5`). Raw 0.50 is not "half as good" (`CLAIM-POST:15`).
2. **The 0.50 threshold on floor-adjusted is our choice, not the bounty's.** We also switched the headline after the claim runs, though toward the stricter scale (`C/CRITIQUE-2026-10-16.md` B#6). Win-rate, raw and floor-adjusted are three different readings of "50 % as good". None of them is calibrated against humans (`audit-metric.md:87`).
3. **Win-rate is saturated.** Opus essentially never ties (1/1,052), so win-rate is 0 everywhere and cannot separate configurations. "Half as good" has no defined mapping onto a pairwise win-rate (`EVALFIX.md:4-13,27`).
4. **"Internet" is barely represented.** Opus without web scores about the same as Opus with web (1.029). The judge has no web, Sources are stripped, and references are capped at 250 words. Browsing, maps, reviews and freshness are not represented (`ladder.md:36`; `audit-metric.md:72`; `refs-prompt.md:17`).
5. **Freshness was excluded by design.** "No item depends on 'now'" (`v0.1 DATASET_CARD.md:28`). This removes the area where internet search is clearly ahead, so it biases the ratio in BOAR's favour relative to the bounty's "internet search".
6. **The reference is shorter and capped,** while real frontier-with-web answers are longer. On depth the cap cuts both ways (`audit-metric.md:72`).
7. **Citations are invisible to the judge.** Blinding strips them (`judge-core.mjs:8-13`), so BOAR's grounded citations, which matter for offline trust, earn nothing.
8. **Speed is outside the score.** B31:28 requires usable speed, and the post author's own floor is 50 tok/s on a laptop. The phone decodes at 5.5 tok/s, the fast tier p50 is 30.7 s, and the deep tier is estimated at minutes (`audit-metric.md:70`; `DEVICE-X6.md:16`).

### B. Item mix vs the bounty
9. **Synthesis is thin:** 3/60 in v0.1 and 6/110 in v0.2. Many "explanation/reasoning" items are lookups (Kenya capital, Berlin Wall years) (`audit-metric.md:71`). This misses "beyond simple factual recall" (B31:27).
10. **Categories with no anchor in B31's list:** crypto 13, honesty 12, danger 10 and health 8 make up 43/110 of v0.2 (`v0.2 DATASET_CARD.md:14`). They are defensible from his posts and his "travel" use, but they are our choice.
11. **Canonical-topic convergence:** 36 same-topic pairs out of 55 slots among the Claude writers (`v0.2 DATASET_CARD.md:34,95`).
12. **His literal eval (vegan venues) is outside the ratio.** V-para P5 is 0/7. VENUEGPS-2 got 7/7, but the venues and the gold share OSM tags (`judge.mjs:7`; `CLAIM-RESULTS-cut6.md:81`; `CLAUDE.md` VENUEGPS-2).
13. **Population sensitivity:** v0.2 0.513 vs V-para 0.413, a shift of about 3× the CI (`audit-metric.md:72`).
14. **English only** (`Q:479`). This matches the bounty's silence on language, but should be stated.
15. **"Include ones a 1B model would fail on":** the 1B-class gap was measured on v0.1 dev only. The held-out gap is pending (`analysis-plan.md:73-74`; `C/CLAIM-DRAFT-v4.2.1.md:302`).

### C. Who writes and who judges (closed Claude loop)
16. **Every claim item is Claude-written:** v0.2 (Opus, Sonnet, Fable), V-para (one Opus agent), self-tests (agent). The V-exact rubrics and the v0.1 gold are agent-written too, and "No human has reviewed them" (`v0.1 DATASET_CARD.md:106`; `C/EXPOSURES.md:13-14`).
17. **References are Claude Opus.** Judge-facing author notes are also Claude-written (`audit-metric.md:34`).
18. **The judge is Claude Opus.** The OpenAI re-judge was post hoc and scores about +0.10 higher. Under our rule the lower judge is the headline (`analysis-plan.md:43`; `CLAIM-POST:27`). Self-preference bias has not been measured (`CRITIQUE` B#16).
19. **No human labels.** r4to decided "NO human review" (`Q:454`). The planned 40-pair check was never run (`CLAIM-DRAFT-v4.2.1.md:264`).
20. **v0.3, the fix for 16–18, was dropped:** 0 items (`Q:1349`).

### D. Statistics and hygiene
21. **No unexposed set exists.** v0.2 is burnt (git history `d8154b6`). V-para has 19 full spends. The deep configuration was chosen as the best of ≥8 on V-para, so expect a winner's curse of 0.01–0.02 (`C/BENCH-V03-SPEC.md:77`; `C/EXPOSURES.md:3,14`; `CRITIQUE` B#5).
22. **Dev gains did not transfer:** +0.054 on dev became +0.007 on held-out. The 20-item L1 slices cannot resolve 0.03, and Haiku carries ±0.03–0.04 at n=20 (`audit-metric.md:113-116`; `CRITIQUE` B#15).
23. **Two seeds, not three.** The CI understates run variance (`audit-metric.md:94-104`).
24. **Harness defects:** F1–F9 (resume reuse, empty aggregates, bypassable blind hook, silent drops). None moved a reported number, and F1 is now guarded (`C/PIPELINE-AUDIT-2026-10-13.md:3-14`; `judge.mjs:108-115`).
25. **Judge prompt and CLI are unpinned:** the `opus` alias, with CLI drift (`audit-metric.md:146-150`).
26. **Safety:** 9 of the 10 v0.2 danger items have no automatic rule and are judged by the rubric only (`v0.2 DATASET_CARD.md:66-77,102`).
27. **Facts drift:** Dead Sea level, Bitcoin Core defaults and similar items will age (`v0.2 DATASET_CARD.md:97`).

### E. Device, install and offline (requirements outside the quality score)
28. **The submitted app is effectively unscored.** All claim numbers come from the TypeScript engine. The native app scored −0.089 on v0.1 (Haiku) (`DEVICE-X6.md:30`; `CRITIQUE` A3; `CLAIM-POST:29`).
29. **Phone runs:** v0.2 and V-para were never run on a phone. Parity was shown only on 57 dev items with Haiku (`CLAIM-POST:19,35`).
30. **Offline, GrapheneOS and install:** no GrapheneOS device, no dynamic network capture, and no "running within a few minutes" install test (B31:21,24,41; `CLAIM-POST:35`).
31. **Long sessions:** agent-written dev items, reference = BOAR's own answer, so the result shows stability, not quality (`CLAIM-POST:21`).

### F. Readings of the bounty that lack a public source
32. "Judges = bounty contributors with a shared public rubric; the post author's top criterion = consistent quality across longer sessions and varied hard questions" (`Q:1131`; `C/CLOSING-SPRINT-2026-10-14.md:8`). **No public URL is cited** for either claim. The longer-sessions criterion does not appear in B31 or in the quotes we logged. It must not go into the public ruler unless a public source is found.
33. **Who decides:** B31:62 makes the post author's public confirmation decisive, while B31:15 says he is not involved unless he chooses to be. The ruler has to be readable by him and by the contributors (B31:64-67).
34. **Deadline:** CLAUDE.md says 10-20, auto-memory says 10-25, B31:3 says "final decision by 2026-10-31". Internal inconsistency.

## UNKNOWN
- Whether the poidh page text has changed since our 2026-10-02 copy (B31:71-74).
- The exact live wording of the X posts. We fetched them through fxtwitter on 09-30; this needs re-verification.
- Whether a human (or the post author) would agree with judge.v1's 1–5 scale. There is no calibration data.

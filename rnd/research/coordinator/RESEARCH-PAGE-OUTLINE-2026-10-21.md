# RESEARCH-PAGE-OUTLINE 2026-10-21: public research page + claim v5 ("coverage x quality")

TL;DR: outline only, for the R5 writer (PLAN-2026-10-21-TO-25 §3, 10-25). Thesis: **BOAR answers well where a knowledge pack holds the fact; here is the measured ceiling without one.** Every number below carries its source (QUEUE line or arms file) so the writer can verify it; nothing new was measured for this outline (0 judge calls). Anything the page would need but we have not measured is marked **[NEEDS: ...]** and must stay out of the text until measured, or be said as "not measured".

## 0. Rules the writer applies to every sentence (honest by construction)
- Each number states, in the same sentence or the table row: **set, n, seeds, judge family (Claude Opus / Claude Haiku 5.5-low / Codex gpt-5.6-sol), scale (U / raw / floor-adjusted / win-rate), and whether the items are pack-written** (self-tests written from the pack text = on-topic upper bound, never casual traffic).
- Never pool across sets or judges; never put a Haiku number next to an Opus number without naming both (Haiku compresses gaps, L1-PROTOCOL addendum).
- Lead with win-rate and the lower judge family (claim v4.2.3 rule, QUEUE l.1293). Floor-adjusted, not raw, as the scalar; raw 0.50 is not "half as good" (VPARA-DIAGNOSIS §0: 1/1/1 floor = 0.206 raw on V-para).
- Desktop engine numbers are labelled "dev / parity evidence"; the submitted native app is the scored system (BENCH-RULER R-D5). Native-app absolute numbers are **internal until r4to's word** (QUEUE l.1278, l.1297).
- Keep "safety cards and health answers are AI-reviewed, not clinically reviewed" on the page (CLAUDE.md rule; claim v4.2.4 opening).
- V-para and v0.2 are development-style since 10-06 / burnt (EXPOSURES rulings; CLAUDE.md). v0.4 (75 items, non-Claude-written) is the ruler set; no system result on it exists yet.
- English scope is "our choice" (BENCH-RULER R-D9). The ruler is ours, not endorsed (B31:15).

### Update 2026-10-21 05:xx (§0 rules)
- **Judge choice for the page and R4 (proposal, r4to decides; PLAN v2 R1):** judge.v1 bytes unchanged, both families named, plus the decline subtraction U_net = (U − D)/(1 − D) with **D 0.058 (0.037–0.081)** = bare-refusal U under judge.v1, Haiku 5.5-low, 30 stratified v0.1 dev ids, 180 Haiku (arms/floor-anchors/FLOOR.md; JUDGE-V1_1B.md). The true-zero line variants are **NO-ADOPT**: v1.1 decline U 0.000 but CE flips 7/40 and retest SD 0.0265 vs 0.0206 (JUDGE-V1_1.md, 528 Haiku); v1.1b CE flips 5/40, SD 0.0295 (JUDGE-V1_1B.md, 300 Haiku). Writer: never write "true zero" for judge.v1; write "decline floor D 0.058 subtracted (Haiku, dev)".
- **Every per-100 number names the mode (show-all vs refuse-by-default), the model, the judge family and "dev questions, one run"** (HON6-TIER-PER100 "May NOT use" list).
- **Judge-family × reference-family 2×2 in R4:** same-family judge lift is 3.4–8.4 pp in open-model families (arXiv 2609.17857, abstract 2026-09-15; Claude/GPT not tested; web/WEB-LOG-2026-10-21.md tick 1). Publish all four judge × reference cells so the diagonal lift is visible (0 extra LLM once R4 exists).
- **Opus over Haiku on the "correct" side:** Haiku under-calls correct answers vs Opus (WARN-OPUS: CE agreement κ 0.81, correct agreement κ 0.29, 111 answers). Any Haiku-only "rarely correct" sentence needs an Opus check before the page (the 5 % sentence already failed it).

### Update 2026-10-21 18:xx (§0): claim v5 §0 fallback block v2, state matrix (A2-CLAIM-STATE-MATRIX)
Supersedes the variant A/B pair in the "Claim v5 section map" below for the §0 headline; base wording = **variant B** (the page review found variant A inaccurate as first written). Check: review-notes-2026-10-21/A2-STATE-MATRIX.md. Pick the state by reading the catalog of the RC actually installed (runsheet 0b + Wi-Fi window 1, Model Catalog and Knowledge screens), never from a changelog or a message.

**Axes.** N1 = NOTE-1 adopted (the installed RC's Model Catalog lists Qwen3-1.7B). N5 = NOTE-5 adopted (its Knowledge catalog lists our boar-packs as sqlite-pack entries). C4 = fifth axis: Qwen3-4B (qwen3-4b-instruct-2507-q4km) is downloadable from the installed RC's own catalog (true for the RC1 snapshot catalog 5f8cc8f4; UNKNOWN for the installed RC1 until 0b). Slots in {braces} are filled only from the named row; an empty slot takes its "else" text, never a projection.

**Fixed opening (all states, variant B):** "Our engine (bench app) scored X. This is our engine's number, not a measurement of the submitted app." X = the bench ruler row with its judge family named (Claude Opus + Codex if the Codex ladder lands by 10-23 18:00, else Claude Opus only).

| State | Headline sentence after the opening (exactly one) | 8 GB tier label | Source row | Judge family |
|---|---|---|---|---|
| **S00** (N1 n, N5 n; the RC1 state) | "The submitted app (2.0.0-rc1) installs one model on our 8 GB phone, Qwen2.5-1.5B, which answers in the Detailed style from its built-in knowledge base with no knowledge packs; {A1 landed 10-21 (RC1-SHIPPED-U): we measured it at U 0.14 (CI 0.10-0.19; raw 0.32, win 0/51, 2 correct and 69 confident errors per 100; Claude Opus judge.v1 + DECLINE2STAGE, 51 v0.1 dev questions, one run, Pixel 8a; paired Qwen3-1.7B bench engine minus this app +0.21 (+0.13...+0.29)) [internal until r4to's word]; the closed-book 1.5B rung (0.261) is not a proxy for the app and is never written as one} {else: we have not measured it on the ruler set}." | "Qwen2.5-1.5B (submitted app RC1, out-of-box install; Detailed; built-in knowledge base only)". The 1.7B, the Succinct style and our packs are each written "proposed, not in the submitted app". | A1-RC1-SHIPPED-U (arms/rc1-pixel, landed 10-21; descriptive configuration facts from RC1-SPEED and RC1-PARITY) | Claude Opus judge.v1 (A1); configuration facts 0 judge |
| **S10** (N1 y, N5 n) | "A later release candidate ({RC id}) lists Qwen3-1.7B in its model catalog; {RC 1.7B speed row answered ≥ 8/9: we timed it on that RC at {p50} s per answer p50 (9 dev questions, one run, no judge)} {else: it is listed, not measured by us}. That release lists no knowledge packs." | {≥ 8/9: "Qwen3-1.7B (submitted app {RC id})"} {else: "Qwen3-1.7B (listed in the {RC id} catalog, not measured by us)"}; Succinct and packs stay "proposed". | the RC 1.7B row (rc-speed9-17b re-run on the new RC; runsheet row 2) | none for the speed clause; X as in the opening |
| **S01** (N1 n, N5 y) | "The submitted app ({RC id}) installs Qwen2.5-1.5B on our 8 GB phone, and its catalog lists our knowledge packs {names} as in-app downloads (network once, then offline); it still has no offline import of a pack file; {RC pack row exists: with {pack} installed it retrieved on {k}/9 dev questions (one run, no judge)} {else: we have not measured the app with them}." | "Qwen2.5-1.5B (submitted app {RC id}, out-of-box install) + our packs as in-app downloads (network once)" | a later RC pack row (any boar-packs run on that RC; blocked on RC1) | none for the retrieval clause; X as in the opening |
| **S11** (N1 y, N5 y) | "A later release candidate ({RC id}) lists Qwen3-1.7B in its model catalog and our knowledge packs {names} as in-app downloads (network once, then offline; no offline import of a pack file); {RC 1.7B row ≥ 8/9: we timed the 1.7B on it at {p50} s per answer p50 (9 dev questions, one run, no judge)} {else: neither is measured by us on the app}." | S10's 1.7B label + " + our packs as in-app downloads (network once)" | the RC 1.7B row + the RC pack row | none; X as in the opening |

**Fifth axis C4 (one optional sentence, appended in every state):**
- C4 y and the RC 4B speed row exists (runsheet H3, rc-speed9-4b, n ≥ 8/9): "Its catalog also offers Qwen3-4B as an optional download (2.50 GB, network once); on our Pixel 8a it decoded at {d} tokens/s with a first token in {t} s p50 (9 dev questions, Detailed, one run, no judge)." Add "{k}/3 cold loads with background apps were killed" from H4 when k ≥ 1.
- C4 y, no H3 row: "Its catalog also offers Qwen3-4B as an optional download (2.50 GB, network once), which we have not measured on the app."
- C4 n: no sentence; every 4B number on the page stays "bench engine".
- The 4B is never the 8 GB tier label and never takes "ships", "default" or "submitted" (it is not installed out of the box).

**Optional wiki-vital5 clause (any state, only if runsheet H5 ran):** "With the catalog's Wikipedia Vital Articles pack (164 MB download) installed, the app retrieved a source on {k}/9 dev questions, against 1/9 without packs (one run each, no judge)."

**Writer rules for this block.** (1) Every RC number carries "[internal until r4to's word]" until he clears native absolute numbers. (2) In S00 no sentence attaches "ships", "default", "submitted" or "in the app" to the 1.7B, Succinct or our packs. (3) If no RC newer than RC1 exists by 10-24 12:00, only S00 (+ C4) is published; S10/S01/S11 stay here. S10/S01/S11 carry S00's A1 number unchanged (RC1 measurement; no newer RC is measured). (4) A variant that fails the check (≥ 1 unsourced number, or a ships/default verb on a proposal in S00) is withdrawn and §0 falls back to bare variant B. (5) The A1 number, if it lands, is reported as "out-of-box install", not "only model" (the 4B is a catalog download).

**LA1 recommended base for S00 (2026-10-21, LA1 PASS / LA5 KILLED; review-notes-2026-10-21/SECTION0-VARIANTS-LA1-LA5.md, criteria sha 49d1c5ac / 304baaf0, rnd 9062f7ca).** One independent Opus reviewer: LA1 0 misattribution, 0 omission, 2 required edits (applied below); the withheld-absolute variant LA5 had 2 misattribution and 3 material-omission findings (+0.21 readable as the app's score; 0.35 - 0.21 recovers 0.14). S00-S11 above stay; this text replaces the S00 headline sentence when r4to lifts the internal rule for the A1 row (decision 4); until then the tags stay.
> **E. Our engine (bench app), not the submitted app.** On 51 v0.1 dev questions (one run, Claude Opus judge, judge.v1), our engine won 1 of 51 against the frontier-plus-web reference with either model, and scored U 0.46 (CI 0.39-0.54) with Qwen3-4B (cut 7, in our bench app on a Pixel 8a) and U 0.35 (CI 0.28-0.44) with Qwen3-1.7B (desktop run). This is our engine's number, not a measurement of the submitted app.
> **S. The submitted app (RC1 2.0.0-rc1, as installed on our 8 GB Pixel 8a).** The out-of-box install is Qwen2.5-1.5B, Detailed answer style, built-in knowledge base, no knowledge packs. On the same 51 questions with the same judge (one run) it won 0 of 51 and scored U 0.14 (CI 0.10-0.19; raw ratio 0.32), with 2 correct answers and 69 confident errors per 100. [internal until r4to's word] Qwen3-1.7B, the Succinct answer style and our knowledge packs are proposed for the app; none of them is in the submitted app.
> **E vs S.** Paired on the same 51 questions and judge, our 1.7B engine scores +0.21 U above the submitted app (CI +0.13 to +0.29; better on 37 questions, worse on 8). This is a cross-system delta, not a property of either system alone. [internal until r4to's word]
> Neither system reaches the 0.50 bar (Claude Opus, one run). [internal until r4to's word] On other dev sets Claude Opus was the stricter of our two judge families; these 51-question rows have no second-family number yet.

## 1. What the bounty asks, and our ruler
**Paragraph (≈ 120 words).** Bounty #31: an offline Android "casual info lookup and research tool … >50 % as good as internet search + frontier AI models" (B31:7), ≤ 12 GB RAM, ≤ 50 GB, fully offline, no Play Services, "speeds that feel usable" (B31:21-28). There is no official stick; we propose one (BENCH-RULER-2026-10-19 TL;DR 1-2): headline **U** (true-zero utility ratio vs an uncapped frontier+web reference) beside a **task-success** ratio, with raw, floor-adjusted, W/T/L and confident-error rate in the same row; two judge families, verdict = the lower; items written outside the judge family, hashed before any run. Spec: RULER-SPEC-v1-2026-10-20.md r2 (sha 7f3b2d1c, QUEUE l.1445), arms A∪ / A persona / B out-of-box / C no-pack / D interference / decline / 1B no-RAG.

**Ruler table skeleton (all cells [NEEDS: R4 on the submitted APK, PLAN §3 10-24]).**

| Row (arm, phone, model) | Coverage (source kept) | U in-pack (A persona, "topic known in advance") | U general (B out-of-box / A∪) | U no-pack (C, show-anyway) | Task success | Win-rate vs ref | CE rate (shown answers) | Judge family | n / seeds |
|---|---|---|---|---|---|---|---|---|---|
| A∪ verdict, Pixel 8a 8 GB, model = the one the RC ships for 8 GB (RC1, 10-21: Qwen2.5-1.5B only; re-read at each RC install). "1.7B (submitted)" only if the RC catalog lists the 1.7B AND S1b completes ≥ 8/9; otherwise the 1.7B is "our proposed 8 GB entry" everywhere on the page (B4) | [NEEDS] | [NEEDS] | [NEEDS] | [NEEDS] | [NEEDS] | [NEEDS] | [NEEDS] | Claude + Codex | v0.4 75 / 2 |
| A∪, POCO X6 12 GB class, 4B | [NEEDS: X6 availability 10-24] | … | … | … | … | … | … | both | 75 / 2 |
| Reference F1 / F2 (frontier + web, uncapped) | — | 1.00 | 1.00 | — | [NEEDS] | — | [NEEDS] | both | [NEEDS: R3 refs v2] |
| Decline arm (3 variants), validity check U ≤ 0.05 | — | [NEEDS] | | | | | | both | |
| 1B no-RAG (B31:9 baseline) | — | [NEEDS] | | | | | | both | |

**Speed row** (RULER-SPEC §7.2; same config as headline). Measured so far, Pixel 8a GrapheneOS, bench app (not the native app), dev items:
- 1.7B: TTFT p50 4.9 s, answer p50 8.3 s, 13.9 tok/s, PSS 3.25 GB (10 questions; QUEUE l.1480, arms/gemma4-e2b/phone/GEMMA4-PHONE.md); TTFT 9.1 → 5.5 s after BATCHRET (litelat-9, QUEUE l.1428).
- Gemma 4 E2B: answer p50 11.8 s / p90 24.3 s, 7.0 tok/s, PSS peak 4.52 GB, 73/73 (QUEUE l.1483).
- 4B: 4.2 tok/s, answer p50 25.5 s on the same 73; one low-memory kill at 4.4 GB RSS (QUEUE l.1415, l.1483).
- 4B cut 7 on POCO X6 Pro (12 GB class): 72/72, p50 30.7 s, p90 48.4 s, PSS ≤ 4.23 GB after load (claim v4.2.4 "On a phone"; arms/device-x6).
- [NEEDS: speed of the submitted native APK, 0.2 timed run, PLAN §3 10-22.] Projected tiers from bench-app traces: see the 05:xx update below (SPEED-PRECHECK, all four USABLE).

**Gates table** (RULER-SPEC §7.1): RAM, storage (≤ 50 GB incl. every offered pack), offline (no INTERNET permission or 0-byte PCAP), no Play Services, GrapheneOS (PASS only if run there, else UNVERIFIED), build identity (APK sha), repo, install stopwatch ≤ 15 min, safety (0 confirmed dangerous). All cells [NEEDS: R4 on the APK sha]. Known: measurement app has no INTERNET permission and no Play Services code (claim v4.2.4); the Pixel 8a runs are on GrapheneOS (QUEUE l.1415) but with the bench app.

### Update 2026-10-21 05:xx (§1 ruler, speed, gates)
**Speed row, projected (was partly NEEDS; ruler/SPEED-PRECHECK-2026-10-21.md, criterion sha 4bd52b3d, 0 LLM; BOAR Bench traces on the Pixel 8a, answered items, T30 derived = first token + 29 / decode rate). Not the verdict run: the RC APK run (PLAN 0.2) decides.**

| Tier (run) | T30 p50 / p90 | complete p50 / p90 | decode tok/s | PSS peak | verdict |
|---|---|---|---|---|---|
| 1.7B + A-union, headline config (aunion73-a) | 4.4 / 11.7 s | 4.4 / 13.7 s | 11.3 | 3.41 GB | USABLE |
| 1.7B claim kit (q17b73-a) | 2.9 / 9.9 s | 2.9 / 11.7 s | 12.4 | 3.39 GB | USABLE |
| Gemma 4 E2B (gemma73-a) | 9.4 / 18.1 s | 11.8 / 23.9 s | 7.0 | 4.52 GB | USABLE |
| 4B cut 7, pre-BATCHRET (final-cut7-v01) | 20.2 / 39.2 s | 26.0 / 52.0 s | 4.2 | 4.92 GB | USABLE |

Writer: **all four tiers pass the USABLE line on these traces; the 1.7B's case is margin and decode rate, not a gate failure of the 4B.** The 1.7B declines 35 % of v0.1 (Gemma, 4B 0 %), so answered sets are not like-for-like; model-path-only 1.7B + A-union is 11.2 / 13.0 / 12.1 s. With A-union installed, the 4B on the 73 = answer p50 19.4 s, PSS peak 4.76 GB, 0 LMK (batchret engine; AUNION-PIXEL.md 4B addendum). [NEEDS still: the submitted native APK row, PLAN 0.2; reference end-to-end time; per-token stamps.]

**Gates table additions.** Places/location: the app maintainer's native Kotlin app has **no places code and no location permission**; the tile data are ready (8,374 world tiles hosted, HF @44c3375c via gazetteer 215ce466), the device apps are not (ruler/TILE-PATH-2026-10-21.md, 0 LLM). Writer: the APK row says "cannot answer current-city questions".

**Ruler table additions (rows to pre-register in the R2 spec; cells still R4):**
- **Current-city stratum (RV4-CITY-BOUND):** 7 v0.4 has_location items (all travel) hold **7/65.5 = 10.7 %** of headline weight; max swing ≥ 0.107 U-total; refusal → tile ceiling 0.098 (0.089–0.106) on the dev proxy (0 LLM; ruler/RV4-CITY-BOUND-2026-10-21.md). Headline = all items scored as given; print U-total with and without the 7; one labelled desktop tile-path sensitivity row, never the headline; if with/without fall on opposite sides of 0.50 (iff U-without ∈ 0.50–0.56), the verdict sentence names both.
- **Decline arm:** under judge.v1 it is INVALID as a "U ≤ 0.05" check (bare 0.058, hedged 0.053, fluent no-content 0.016; Haiku, 30 v0.1 dev ids; FLOOR.md) → it becomes the subtraction D (§0 update), re-measured on v0.4 in R4 per family.
- **1B / 1.5B anchor:** closed-book Qwen2.5-1.5B vs 1.7B K0 on v0.1 57 dev: +0.035 (−0.019…+0.089) judge.v1, +0.047 (−0.0005…+0.097) v1.1, +0.040 (−0.019…+0.096) RV2 n 51 (all Haiku) → **not separable; the page has no "better than a 1B model" sentence** (FLOOR.md; JUDGE-V1_1B.md; RV2). The R4 row is reported as a level anchor only.
- **Reference rows:** REFVAR (Haiku-judged, 20 v0.1 dev ids, 40 uncapped Opus + web references): two draws move U 0.015 (1.7B) / 0.008 (4B); uncapped − v1 +0.013 / +0.001; 4B − 1.7B gap 0.084 (v1) vs 0.072 (draws), no flip → one draw per family suffices, as-of date in the prompt, contested key points dropped (ruler/REFVAR-2026-10-21.md). Caveat: same-family writer and judge.

## 2. The pack thesis: measured numbers
**Claim to make:** packs lift answers on their own topics and are neutral off-topic; the size of the lift depends on the model's reading. **Every row here is pack-written self-tests (upper bound) unless marked.**

| Measurement | Number | Set / n / seeds / judge | Pack-written? | Source |
|---|---|---|---|---|
| 1.7B in-pack: K3 (6 packs) vs K0 | U 0.393 → 0.462, dU **+0.069** (+0.038…+0.099) | 80 candidate-pack self-tests, 1 seed, Haiku 5.5-low | yes (upper bound) | arms/litepacks/LITEPACKS.md, Secondary A |
| 1.7B in-pack, per pack | simplewiki +0.104…+0.106; factbook +0.104 (K3); medlineplus +0.057 (K3); firstaid +0.007 | n 20 each, indicative | yes | LITEPACKS Secondary A |
| 1.7B off-pack (casual MAIN) | dU −0.004…−0.012, all CIs straddle 0 (K1-K4) | MAIN 97 (v0.1 57 + cooking-se 20 + money-se 20), 1 seed, Haiku | no (MAIN is off-pack for every arm) | LITEPACKS MAIN table |
| 1.7B off-pack (other SE topics) | dU −0.003…−0.011, CIs straddle 0 | 100 SE self-tests (travel, ethereum, bitcoin, health, outdoors), Haiku | pack-written but off-pack for every arm | LITEPACKS Secondary B |
| Gemma 4 E2B in-pack: K3 vs K0 | U 0.395 → 0.497, dU **+0.102** (+0.061…+0.144); DiD vs 1.7B +0.034 (+0.001…+0.066) | same 80, 1 seed, Haiku; host differs (M4 vs M1 Pro) | yes | arms/gemma4-e2b/PACKS.md |
| Gemma off-pack | MAIN K0 U 0.434 vs 1.7B 0.406 (+0.028); K1 MAIN dU +0.017 (−0.008…+0.040) | MAIN 97, Haiku | no | arms/gemma4-e2b/VS4B.md; QUEUE l.1479 (GEMMA4 confirm Q7a2) |
| Gemma K3 on MAIN (off-pack, crowding) | [NEEDS: not run; MATRIX ran MAIN only for the 1.7B KA: dU −0.007 (−0.026…+0.012), CE-unwarned 7 → 12, Haiku] | MAIN 97 | no | arms/coverage-matrix/MATRIX.md |
| 4B reading with packs (identical contexts) | 4B D4 0.650 vs 1.7B D4 0.529 vs LFM2.5 0.554 | PACKREAD, 54 pack items with the engine's X2b contexts, Haiku | yes | QUEUE l.1387-1390 |
| 4B single pack vs claim kit | raw +0.032 (+0.016…+0.050) Haiku; raw +0.042 (+0.024…+0.062) Opus L2; above_min +0.053 (+0.030…+0.078) Opus L2 (corrected 10-21 05:3x per CV5-RECOMPUTE) | 180 self-tests of 9 packs, 1 seed | yes | arms/packs/SELFTEST-SCORES.md; QUEUE l.1077 (PACKS-L2) |
| 4B wave 3 (cooking, money SE) | +0.045 (+0.007…+0.087) Opus L2 | 40 self-tests | yes | QUEUE l.1077 |
| Deep 35B + think: packs add nothing | −0.002 (−0.020…+0.016); deep reads +0.054 over 4B with the same passages | 180 self-tests, Haiku | yes | arms/packs/SELFTEST-DEEP.md |
| Venues (current-city, the post author's own eval V2) | P5 **0/7 → 7/7** both seeds, with device location + the user's area tile (+3.65 MB), no engine change | V-para venue items, 7, 2 seeds, 0 judge (OSM gold) | gold and engine both OSM: proves the path, not venue quality | QUEUE l.794-795; arms/venuegps/VENUEGPS-2.md |
| Crowding, 1.7B lite sets | no arm flagged (frozen rule); warned share on SE self-tests +0.12…+0.19 | 100 SE self-tests, Haiku | — | LITEPACKS Secondary B |
| Crowding, 4B with 9 packs as peers | fact article kept 68 → 46/180; −0.019 (−0.035…−0.003) Opus L2 | 180 self-tests | yes | REPORT-PACKS-2026-10-13 §1 l.11; QUEUE l.1077 |

Writer notes:
- "Crowding none" holds only for the 1.7B lite sets (K1-K4); with many peer packs on the 4B it is measured and negative. Say both.
- Cost of packs: prompt tokens 384 → 729-792, desktop TTFT 1.6 → 3.9-4.4 s, disk +0.74-2.5 GB (LITEPACKS TL;DR). Phone cost with BATCHRET (resolved 2026-10-21 05:xx): A-union (6 packs + gazetteer) +2.4 s retrieval p50, answer p50 +3.4 s on 73 v0.1 dev ids, PSS flat on 1.7B / Gemma / 4B, 0 LMK (arms/aunion-pixel/AUNION-PIXEL.md, 0 judge).
- The pack lift is a fast-tier value; the deep tier does not need packs on these items (SELFTEST-DEEP Reading).
- Coverage in casual traffic is low: V-para kit holds the fact on 6/51, all packs 10/51 (VPARA-DIAGNOSIS §1). The page must pair the in-pack numbers with this coverage fact.

### Update 2026-10-21 05:xx (§2 pack thesis: what the real items say)
**Corrected claim.** Self-test lifts stay quotable only as "single-fact, retrieval-matched questions written from the pack", with the non-transfer caveat. On real dev questions no pack gain is measured.

| Measurement | Number | Set / n / seeds / judge | Pack-written? | Source |
|---|---|---|---|---|
| Self-test gain sits on fact-added items | cell a (pack adds the key fact) K3 − K0 **+0.139** (+0.075…+0.201) n 27, Gemma +0.168; cell c ≈ 0 | 60 topical self-tests, 1 seed, Haiku | yes | ruler/FACTPRESENT-2026-10-21.md |
| Same cell on real items | 1.7B K3 − K0 **−0.010** (−0.077…+0.050) n 10 (strict +0.005, n 7); K1 − K0 −0.015; only positive real cell = b (fact already in K0) +0.059 (+0.022…+0.093) n 13, post-hoc | MAIN 92 keyed, Haiku | no | FACTPRESENT |
| Matching pack loaded vs not, real items | K3 − K0 **−0.023** (−0.081…+0.027) n 17; in-pack items are not easier (MAIN in-pack U below off-pack for every system; 4B −0.081) | MAIN 97 / v0.1 57, Haiku, 1 seed | no | ruler/INPACK-SPLIT-2026-10-21.md |
| Oracle: fact chunk forced to passage 1 | 1.7B K3 U 0.427 vs 0.412, **+0.015 (−0.029…+0.059)** = 10 % of the self-test gain; **reading binds** (indicative, n 30 < 35); post-hoc lead: 6 hand-found clean key-fact chunks +0.106 (+0.054…+0.159), lexical golds −0.009 → **chunk quality may matter more than reach** | 30 keyed v0.1 dev ids, 98 Haiku | no | arms/oracle-real/ORACLE-REAL.md |
| Not a lexical-overlap artefact | question-to-gold Jaccard median real 0.053 vs self-tests 0.045; 1.7B self-test gain reweighted to the real overlap distribution +0.064 (+0.035…+0.095), Gemma +0.101 → **KILL** of the artefact hypothesis; transfer gap = question type and reading | cand80 + 37 real golds, 0 LLM, Haiku rows | both | ruler/PK3-OVERLAP-2026-10-21.md |
| Where real items are lost (RAG funnel) | K3 MAIN keyed 92: S1 fact not in any loaded pack 45 (39 cooking/money), S2 deterministic 7 (all correct), S3 dropped at keep 17, S4 kept but answered wrong 15, S5 correct 8; under the real-item prior every stage ceiling ≈ 0 | MAIN 92, 0 LLM replay, Haiku labels | no | ruler/RAG-FUNNEL-2026-10-21.md |
| Coverage matrix, three tiers | U K0 / K3 / KA on the 80: 1.7B 0.381 / 0.462 / 0.435, Gemma 0.395 / 0.497 / 0.450, 4B 0.461 / 0.545 / 0.513; KA − K0 +0.052…+0.055 (all CI low > 0); KA − K3 is the simplewiki slice only; 4B − 1.7B ≈ +0.08 at every pack set | 80 self-tests, 1 seed, 652 Haiku | yes (upper bound) | arms/coverage-matrix/MATRIX.md |
| A-union on MAIN (off-pack), 1.7B | KA − K0 dU **−0.007** (−0.026…+0.012), CE-unwarned 7 → 12 (+0.052, CI −0.010…+0.113) | MAIN 97, Haiku | no | MATRIX.md |
| Pack cost on the phone (was NEEDS: resolved) | A-union (6 packs + gazetteer) adds **+2.4 s retrieval p50** (1.5–1.6 → 3.9–4.0 s, max 10.7 s; answer p50 +3.4 s on the 73) and **no memory** on all three tiers: 1.7B PSS 3.41 vs 3.39 GB, Gemma 4.38 vs 4.52, 4B 4.76 vs 4.92, 0 LMK; cause = packs searched one after another (~0.15 s per small pack) | Pixel 8a, 73 v0.1 dev ids, bench app, 0 judge | — | arms/aunion-pixel/AUNION-PIXEL.md (+ Gemma, 4B addenda) |
| Merged single pack (PK-5) | kept-source identity 81/97 (83.5 %) < 95 % gate; judged parity on the 16 changed items U 0.365 vs 0.399 (−0.034 < −0.02) → FAIL, phone step not run; parallel search is the lever (same results by construction) | MAIN 97 replay; 16 items, 38 Haiku | no | AUNION-PIXEL.md; QUEUE 04:44, 04:52 |

Writer, allowed: "Packs lift questions whose key fact the pack adds, on self-tests written from the packs (+0.14, Haiku, one run); the lift is not a word-overlap artefact." "On real development questions we measured no gain from loading the matching pack (−0.01…−0.02, CIs cross 0, n 10–17); forcing the fact into the first passage moved the 1.7B by +0.015, so reading, not reach, is what limits the small model." "Six packs cost about 2.4 s per question on a Pixel 8a and no extra memory."
Writer, barred: "packs make answers better on real questions"; "in-pack questions are easier"; any self-test lift without "written from the packs, upper bound, does not transfer to our real dev items"; "chunk quality is the lever" (post-hoc, 6 chunks: say "a lead").
- Gemma K3 on MAIN row above: **still NEEDS** (MATRIX ran MAIN only for the 1.7B KA).

## 3. Gap decomposition: why this is a knowledge bar
Source: VPARA-DIAGNOSIS-2026-10-19 §1 (LOSSMAP K, recomputed) and PLAN §1. Set: V-para 51 judged, 4B cut 6 (= cut 7 on V-para), seed 42 for the loss split, Claude Opus judge for the score, single-seed jev labels (shares ±0.05).

| Cause | Share of the 0.586 gap | Items | Fixable how |
|---|---|---|---|
| Wrong from memory, no source kept | 0.167 | 12 | model knowledge (deep tier); hideable by the groundedness gate |
| Absent knowledge, no source | 0.239 | 24 | content: fact in kit 6/51, all packs 10/51, full English Wikipedia 9/34 absent items (WIKIFULL A+B), 9 packs + kit 6/34 (T-K6b) |
| Wrong with an on-topic source (misread, upper bound) | 0.142 | 11 | reading: 1.7B − 4B −0.070 at identical contexts (n 97, CRITIQUE-2026-10-16, QUEUE l.1267) |
| Thin | 0.038 | 4 | — |
| Refusals / truncation | 0 | 0 | — |

Points to make: retrieval kept nothing on 29/51 items, which carry 58 % of the loss; the deep tier lifted wrong items +0.189 and absent items only +0.058 (VPARA-DIAGNOSIS §1). Second view on the 1.7B (K1-COVERAGE): of 20 no-source confident errors, 10 have the key fact in neither simplewiki nor top-100k; 4 are blocked before retrieval (routing/health declines); 2 present but not retrieved; 2 retrieved but misread (arms/k1-coverage/K1-COVERAGE.md). Conclusion line: the facts are missing from the phone, so a bigger encyclopedia does not close it; topic packs do, on their topics.
- [NEEDS: the same decomposition on v0.4 under the ruler (U true-zero), so the page is not V-para-only.]
- [NEEDS: XFAM per cause; the Codex offset per bucket is unknown (VPARA-DIAGNOSIS §6.1).]

### Update 2026-10-21 05:xx (§3 gap decomposition)
- **Barred now:** "coverage explains the level" and the §3 conclusion's "topic packs do [close it], on their topics" as a statement about real questions. RV2 coverage DiD (1.7B kept a source vs not) −0.007 (−0.136…+0.114) fires kill-2 (ruler/RV2-SEP-LADDER-2026-10-21.md, Haiku judge.v1, v0.1 51); FACTPRESENT / INPACK-SPLIT show no real-item pack gain (§2 update). Replacement conclusion line: "the facts are missing from the phone for most real questions; where a pack holds them, the small model still misreads them as often as not (ORACLE-REAL +0.015)."
- **Second real-item view (RAG-FUNNEL, MAIN 92 keyed, 1.7B K3, Haiku labels):** 45 lost before retrieval (fact not in a loaded pack; 39 cooking/money), 17 dropped at the keep step (10 = fact chunk in the dense candidates outside the top-2 picks), 15 kept but answered wrong, 8 correct, 7 deterministic (ruler/RAG-FUNNEL-2026-10-21.md).
- **Fact reach for the 20 no-source CEs (B3):** top-100k 7 + 2 partial, full enwiki 10 + 7P, published + wave-4 packs 16 + 4P, nothing we have 0; true partly by construction (13/20 are self-tests from those packs; vitalik pack built after K1 named the gaps) (arms/k1-coverage/FACT-REACH-2026-10-21.md, 0 LLM).
- Both [NEEDS] above (v0.4 decomposition; XFAM per cause) stay open.

## 4. Model ladder (context, not headline)
Columns per B4-TIER-AVAILABILITY (2026-10-21): availability first, then win-rate vs the reference as the first numeric column; every cell names its judge family and scale (floor-adj = floor-adjusted ratio; raw = raw ratio; U = utility ratio). Dev sets only (V-para and v0.2 are dev/burnt).

| Arm | Availability (submitted app / bench app on phone / desktop only / proposed) | Win-rate vs reference | V-para 51 | v0.2 110 | Source |
|---|---|---|---|---|---|
| 1.7B | proposed 8 GB entry; bench app on Pixel 8a; not in RC1 (1.5B only, 10-21); in the submitted app only if a later RC lists it AND S1b completes ≥ 8/9 | not judged on V-para / v0.2 | not judged by Opus; ≈ 4B − 0.07…0.11 (Claude Haiku: MAIN 97 U 0.406; kit −0.111 raw) | not run | PLAN §1; VS4B.md; CRITIQUE-2026-10-16 |
| Gemma 4 E2B | proposed opt-in (NOTE-3), not in RC1; opt-in only if a later RC lists it and T1 passes (0 thinking markers, bounded tokens, 20/20; pending 10-22); bench app on Pixel 8a | not judged on V-para / v0.2 | not run | not run | MAIN 97 U 0.434, Claude Haiku (VS4B.md) |
| 4B cut 6, 2 seeds | bench engine (desktop; bench app on phone = desktop within noise, DEVICE-X6). Pre-release native builds ran a 4B (X6/F3); RC1 on the Pixel 8a ships only the 1.5B. [Gap figure only if r4to picks variant A] | 0/51 (Claude Opus); 0/110 (Claude Opus; Codex ≤ 2.7 %) | floor-adj **0.261** (0.224–0.300) Claude Opus; floor-adj 0.361 Codex | floor-adj 0.388 Claude Opus; floor-adj 0.517 Codex | CLAIM-RESULTS-cut6; XFAM rows (QUEUE l.1280) |
| Deep 35B no think, 2 seeds | desktop only (MacBook llama-server) | 0 (Claude Opus) | floor-adj 0.329 Claude Opus; Codex not run | floor-adj 0.457 Claude Opus; Codex not run | DEEPVPARA.md |
| [private correspondence with the app maintainer, or a result of a run on his device, removed] |

Writer (B4): never print "0.577" without "Codex judge, win-rate 0, dev set" and "desktop only". The deep row stays "desktop only" unless an RC or bench phone run with thinking exists by 10-24 (none planned). Any tier whose device-day condition is not met keeps "proposed" or "desktop only".

8 GB trade (MAIN 97, Haiku, 1 seed, mini wall): 4B − 1.7B +0.076 (+0.050…+0.101) at 2.7× wall; 4B − Gemma +0.048; Gemma − 1.7B +0.028 at 1.5× wall (VS4B.md). Phone: see §1 speed row (1.7B 3.25 GB PSS vs Gemma 4.52 vs 4B LMK at 4.4 GB). Phone Gemma = desktop Gemma (+0.001), 0.083 below the phone 4B, 57 v0.1 ids, Haiku (QUEUE l.1486). MIN3CITE (Ministral-3B + citation prompt) +0.062 U at ~3× time, PSS unmeasured (QUEUE l.1481). Recommendation wording: "1.7B on 8 GB for latency and memory, not on quality" (DIRECTION v2 D1).
- [private correspondence with the app maintainer, or a result of a run on his device, removed]
- [NEEDS: any ladder row on v0.4.] [NEEDS: deep + think on a phone.]

### Update 2026-10-21 05:xx (§4 ladder, 1B anchor, competitor)
**Ladder on v0.1 dev (RV2-SEP-LADDER, 0 LLM over existing Haiku judge.v1 rows, v0.1 57 minus 6 deterministic = 51, item-cluster bootstrap):** U 1.5B closed-book 0.209, 1.7B K0 two-seed 0.249, Gemma E2B two-seed 0.260, 4B phone cut 7 0.376. 1.7B − 1.5B +0.040 (−0.019…+0.096) and Gemma − 1.7B +0.010 not separable; 4B − Gemma +0.117 (+0.074…+0.162) and 4B − 1.5B +0.167 (+0.117…+0.219) separable; U_net (D 0.058) gives the same verdicts.
- Allowed (criterion sentence, RV2 l.7): "The ruler separates the 4B from the 1.7B and Gemma tier (+0.12 to +0.13 U, CI low ≥ +0.07); the 1.7B sits within noise of a closed-book 1.5B on this set (+0.04, CI −0.02…+0.10), under both judge.v1 and v1.1." Add "Haiku judge, v0.1 dev, 4B rung = cut 7 claim kit on the phone vs K0 litepacks for the lower rungs" (RV2 §5 confound; the VS4B weight-only swap +0.076 is also separable).
- **Barred: any "better than a 1B model" sentence** (FLOOR.md; JUDGE-V1_1B.md l.39). The 1.5B row is a level anchor.
- Phone parity: Gemma on the Pixel = desktop Gemma +0.001 (−0.016…+0.017); Pixel 4B − desktop 4B cut 7 +0.006 (−0.015…+0.030) (raw ratio, 57 v0.1, Haiku, 228 calls; arms/gemma4-e2b/phone/GEMMA4-PHONE-JUDGE.md). granite-4.0-1b stage 2 on MAIN 97 = 1.7B (+0.0003, Haiku; QUEUE 02:36).
- 8 GB trade, per 100 dev questions (HON-6, MAIN 97 K0, Haiku, one run): show-all correct / CE 4B 26.8 / 16.5, Gemma 21.6 / 13.4, 1.7B 23.7 / 23.7; refuse-by-default 4B 16.5 / 2.1, Gemma 14.4 / 2.1, 1.7B 16.5 / 4.1. Allowed wording: HON6 "May use" lines (ruler/HON6-TIER-PER100-2026-10-21.md §Sentences), incl. "The case for the 1.7B on 8 GB phones is speed and memory: 2.9 s median per answered question vs 26 s for the 4B on a Pixel 8a, PSS 3.4 vs 4.9 GB." Barred: "the 1.7B is more honest / safer than the 4B", "the 4B dominates under refuse-by-default".

**Competitor context (new; COMPETITOR-competitor-app-2026-10-21.md §5, 0 LLM).** a competitor team v1.8.4: Qwen3.6-35B-A3B UD-Q2_K_XL with expert streaming on a 12 GB Pixel 8 Pro, full enwiki 30.1 GB + 25.3 M places, 46.2 GB, median 111 s cool / 152 s warm; self-reports 60–65 % (ratio of summed 0–10 scores ≈ our raw ratio) on 61 items = the app maintainer's boar-app questions.v2 (8 overlap our public v0.1), Claude-family graders (model unnamed), Opus 5.5 + web reference preferred 61/61. The three sentences the writer may use, verbatim from §5 of that report:
1. "a competitor team (claim #125, v1.8.4) runs Qwen3.6-35B-A3B at 2 bits with expert streaming on a 12 GB Pixel 8 Pro over full English Wikipedia and 25 million places (46 GB), answers in about two minutes, and reports [competitor score removed] of a Claude Opus + web reference on 61 public questions from the BOAR app's evaluation set (Claude-family graders, 0-10 scale, reference better on all 61); on long-tail subjects it is ahead of our desktop deep tier."
2. "Those percentages are not on our ruler: they are closest to our raw ratio rather than floor-adjusted or U, the items are public development items for both teams, and on our own development set a single Claude judge gives our 4B 0.413 raw and our desktop deep tier 0.553 raw (V-para, 51 items, win 0/51), so the two numbers cannot be subtracted."
2b. (B3 clause, mandatory next to sentence 2) "Our numbers are our engine's unless marked RC."
3. "BOAR takes a different trade-off rather than a better one across the board: a few-GB install that answers in seconds on real 8 GB phones, swappable knowledge packs, and a two-family ruler with a held-out set and a kit that any entrant, a competitor team included, can run."
Barred (same report, risks 1–7): any first-to-phone or "streaming is ours" implication; their % next to our floor-adjusted numbers without the scale note; "better answer quality"; "only 8 GB"; worldwide venue coverage; win-rate 0 as a differentiator. Framing is an r4to decision (PLAN v2 update).

## 5. Honesty: refusals, confident errors, the gate
**Opening (B2, mandatory unless the device-day kill band relaxes it):** "These rules run in our engine. The submitted app's chat did not run them as of 10-17 (maintainer's portal report). Rows marked RC were measured on his release candidate." (QUEUE l.1295, claim v4.2.4 correction.) RC layer probes k/10 and RC warning-line presence: pending 10-22 (runsheet rows 3 and 6). Relax only if ≥ 8/10 probes match our engine incl. the health/first-aid route AND the warning line is on ≥ 70 % of eligible RC rows. Every safety-probe count below carries "(our engine, tree be-cut7-warn, claim kit; blinded agent reading, 0 judge; AI-reviewed, not clinically reviewed)" or, for other trees, the tree it ran on plus "AI-reviewed, not clinically reviewed".
| Measurement | Number | Set / judge | Source |
|---|---|---|---|
| Compact declines of the 1.7B | ~40 % of compact answers are declines (94/237 ON); all 5 rules off: U0 +0.170 but CE count 17 → 34 | v0.1 57 + 180 self-tests, Haiku, 1 seed | arms/litedecline/LITEDECLINE.md; QUEUE l.1418 |
| Groundedness gate (REFUSE-UNSUPPORTED, 1.7B) | **superseded by the Opus row in the 05:xx update (7 → 3 of 177)**; Haiku: visible confident errors 10 → 4 of 177 (CI −0.062…−0.011), false refusals 0/15 (Wilson 0-20 %), U on shown +0.030, coverage 0.435 → 0.328, 5 correct memory answers lost to show-anyway | MAIN 97 + 80 pack-matched self-tests (K3), Haiku labels, AUC 0.934 | QUEUE l.1461; arms/refuse-unsupported |
| Gate cost | +5.1 s mini, +9.3 s p50 / 12.2 s p90 projected Pixel 8a; cheaper variants drop AUC to 0.66 | 124 gated answers, 0 judge | QUEUE l.1461, l.1465 (GATELAT) |
| Default-mode CE with packs (post-hoc) | MAIN unwarned CE flat for K1-K3 (5/97), K4 11/97 | Haiku | LITEPACKS post-hoc column |
| Health/safety warning | WARNSPEC 3-tier warning; HG-on 4B probes 3/64 (our engine; AI-reviewed, not clinically reviewed) | 64 probes, 0 judge | QUEUE l.1220 |
| Emergency pack safety | SAFEPACK E unsafe 0/30 but declined 20, missing-critical 26 (safe, not helpful); saferoute variant unsafe 3/30, held (our engine; AI-reviewed, not clinically reviewed) | 30 agent-written items, blind Opus audit | QUEUE l.1373, l.1376-1377 |

Product line for the page: no source → refuse by default, "show anyway" button (r4to 10-20, QUEUE l.1443). The gate is not in the submitted app (DIRECTION v2 D3); say "measured, post-submission".
- [NEEDS: CE rate with and without the gate on v0.4 on the APK (PLAN §3 10-25 lists it; the gate is not shipped, so only the without-gate row can come from R4).]
- Safety probes: partly resolved 2026-10-21 05:xx on our engine (GEMMA-SAFETY: 65 probes, 1.7B unsafe 2, Gemma 1 (our engine, tree be-cut7-warn, claim kit; blinded agent reading, 0 judge; AI-reviewed, not clinically reviewed); arms/gemma-safety/GEMMA-SAFETY.md). [NEEDS: the same probes on the app maintainer's RC, front 0.4.]

### Update 2026-10-21 05:xx (§5 honesty: corrected numbers and sentences)
| Measurement | Number | Set / judge | Source |
|---|---|---|---|
| **Gate, Opus re-judge (supersedes the Haiku 10 → 4 row)** | visible CE **7 → 3 of 177** (Opus judge.v1; exact CIs 1.6–8.0 % → 0.35–4.9 %; diff CI −0.051…−0.006; sign test p 0.063), false refusals **0/14** (0–23 %), the gate refuses 6 Opus-correct unsupported answers; Haiku–Opus CE agreement 35/38, κ 0.78 | 38 deciding RU K3 answers, 76 Opus | arms/refuse-unsupported/CE-OPUS-RU.md |
| Warning line, Opus (1.7B) | precision 0.40 (0.35–0.44), recall 0.65 (0.56–0.71), P(correct given warned) **0.23** (0.14–0.35) vs Haiku 0.05; P(CE|w)/P(CE|u) 1.67 (1.13–2.19) | 111 LITEPACKS answers, 216 Opus | ruler/WARN-OPUS-2026-10-21.md |
| Show-anyway reveals, Opus (1.7B) | per 100 reveals ≈ 20 correct, 38 CE; correct:CE **0.54** (0.32–0.83) → liability verdict stands (Haiku had 7 / 35, 0.19) | same | WARN-OPUS; ruler/SHOWANYWAY-VALUE-2026-10-21.md |
| Warning-line transfer (HON-7, Haiku) | 1.7B precision 0.41 / recall 0.70 / P(corr|w) 0.08 HOLDS; Gemma 0.34 / 0.85 / 0.03 HOLDS; **4B 0.275 (0.15–0.42) INDETERMINATE** | MAIN 97 K0, one run | ruler/HON7-WARN-TRANSFER-2026-10-21.md |
| Refuse-by-default per tier (HON-6, Haiku) | correct-shown tie 16.5/100 (1.7B = 4B), CE 4.1 vs 2.1 (n.s.); refuse costs every tier 45–55 % of floor-adj U (4B 0.335 → 0.150, 1.7B 0.239 → 0.133) | MAIN 97 K0, one run | ruler/HON6-TIER-PER100-2026-10-21.md |
| Safety, Gemma vs 1.7B (HON-9) | unsafe **1 vs 2 of 65** probes (64 LITESAFETY + epi-1021), 61/65 deterministic and byte-identical, 0 thinking markers (our engine, tree be-cut7-warn, claim kit; blinded agent reading, 0 judge; AI-reviewed, not clinically reviewed); not his RC | blinded agent reading, 0 judge | arms/gemma-safety/GEMMA-SAFETY.md |
| Multi-turn drift (HON-5, 1.7B) | CE-unwarned t1 0/10 vs t4–5 3/20, rise CI 0.00–0.30 → **no drift detected** over 5 turns at MDE ≈ 0.2; one unsafe 1.7B health error (epinephrine pen into the forearm) in both session and standalone arms | longsession-v1 80 dev, 162 Haiku | arms/drift17/DRIFT17.md |

Sentences allowed (judge named; 1.7B unless stated; dev sets; one run):
- Gate: "An answer-support check cut visible confident errors from 7 to 3 of 177 dev answers under an Opus judge (0 of 14 supported answers refused), at the cost of hiding 6 correct unsupported answers and about 9 s per answer projected on a Pixel 8a; it is not in the submitted app." (CE-OPUS-RU; GATELAT.)
- Warning / reveal: WARN-OPUS sentences 1–4 (ruler/WARN-OPUS-2026-10-21.md §"Sentences claim v5 may use").
- Scope: HON-7 "May use" lines ("Refuse-by-default is calibrated on the Qwen3-1.7B …"; "For a 4B default we recommend keeping the current behaviour: show the answer under the warning line.").
- Tier: HON-6 "May use" lines (§4 update).
- Drift: "no degradation detected over five turns for the 1.7B (MDE about 0.2, Haiku)".
Sentences barred: "about 5 % of warned answers are correct" (WARN-OPUS D2 DROP); "10 → 4" without "Haiku" (use the Opus 7 → 3); "refuse-by-default is validated for small models / the default model" without naming the 1.7B; "the warning line is an error signal for the 4B"; any Pixel cut 7 proxy as a warning-line measurement; "7 of 8 confident errors" without "1.7B, Pixel 8a, 26 questions"; "the 1.7B is more honest".
- Safety probes [NEEDS] above: **partly resolved** on our engine (GEMMA-SAFETY: 1.7B 2 unsafe, Gemma 1, of 65; our engine, tree be-cut7-warn, claim kit; blinded agent reading, 0 judge; AI-reviewed, not clinically reviewed); the app maintainer's RC run (front 0.4) is still NEEDS.

### Update 2026-10-21 15:xx (§5 comparable single number, web log T18.2)
- **Comparable single number: CRAG-style truthfulness per tier** = correct − CE per 100 questions (hidden/declined = 0, partial = 0; CRAG scores accurate +1, missing 0, incorrect −1: https://arxiv.org/pdf/2406.04744). Judge Opus judge.v1 (Haiku in brackets for contrast), set MAIN 97 dev ids, desktop K0 s42, one run; correct = correctness ≥ 4, CE ≤ 1.5. 0 new calls: arithmetic on ruler/CV5-PER100-OPUS-2026-10-21.md and ruler/HON6-TIER-PER100-2026-10-21.md.

| tier | refuse-by-default, Opus (census of shown) | show-all, Opus (estimate: hidden side from 20 sampled rows per tier) | refuse-by-default [Haiku] | show-all [Haiku] |
|---|---|---|---|---|
| 4B | 22.7 − 1.0 = **21.7** | 44.6 − 3.9 = 40.7 | [16.5 − 2.1 = 14.4] | [26.8 − 16.5 = 10.3] |
| Gemma E2B | 23.7 − 0.0 = **23.7** | 36.4 − 8.5 = 27.9 | [14.4 − 2.1 = 12.3] | [21.6 − 13.4 = 8.2] |
| 1.7B | 18.6 − 2.1 = **16.5** | 37.6 − 13.3 = 24.3 | [16.5 − 4.1 = 12.4] | [23.7 − 23.7 = 0.0] |

  - No CIs: the per-100 sources bootstrap correct and CE separately, not their difference; read tier gaps < 5 per 100 as unresolved (CE moves at 2-answer granularity). Show-all Opus cells are sampled estimates, not a census.
  - Allowed sentence: "On 97 dev questions with refuse-by-default, CRAG-style truthfulness (correct minus confidently wrong per 100) is about 22 for the 4B, 24 for Gemma E2B and 17 for the 1.7B (our engine on desktop, Claude Opus judge, one run; gaps under 5 per 100 are unresolved)." Barred: any truthfulness number without judge, set and mode; comparing it with CRAG's published 51 % (different set, human eval).

## 6. Packs as a product
- Catalogue and workflow: PACK-CATALOGUE-2026-10-12.md (decisions D-K1…K7: licence PD/CC0/CC BY/CC BY-SA only, per-row attribution for SE, four artefacts per pack: card, 20-question self-test, coverage probe, crowding probe) (QUEUE l.981).
- Published: 11 BOAR packs on hf.co/datasets/r4topunk/boar-packs (9 in REPORT-PACKS §3 + 2 wave-3: qa-cooking-se, qa-money-se), plus a mirror of the app maintainer's wiki-vital5 (not scored) (REPORT-PACKS l.31; QUEUE l.1044, l.1200). Writer: list name, size, licence, default-eligible vs user-selected from each card (research/packs/*.md).
- Licences to name: SE CC BY-SA per post (archive.org 2024-04-02 snapshot), MedlinePlus PD (A.D.A.M. excluded), Factbook CC0 archive, Army manuals US PD, Wikimedia CC BY-SA 4.0, GeoNames CC BY 4.0 (NOTICE credit), OSM ODbL. NHS and NC content excluded (PACK-CATALOGUE; CLAUDE.md).
- Persona map (how a user picks): travel = wikivoyage + visa + area tile (~362 MB); tech = crypto (36 MB); science/everyday health = medlineplus + firstaid (25 MB); place = factbook (12 MB); humanities = none; union ≈ 435 MB text / ≈ 498 MB with gazetteer (PERSONA-MAP-v1-draft.md, QUEUE l.1457). Status: **draft, not frozen, waits r4to veto**; say so or wait for the freeze.
- Default vs opt-in: LITEPACKS verdict NO CHANGE for the default lite set; K3 recommended as user-selected for health / first aid / country facts (LITEPACKS Verdict). The app maintainer's own fix for low retrieval = optional packs (QUEUE l.1290).
- [NEEDS: how the submitted app exposes pack choice (screens, download sizes); arms/gemma4-e2b/onboarding may hold screens, unverified here.]

### Update 2026-10-21 05:xx (§6 packs as a product)
- **Persona A-union candidate:** 6 text packs 435.3 MB (wikivoyage 351.1, crypto 36.1, firstaid 21.0, factbook 11.6, visa 11.2, medlineplus 4.3), 458.3 MB with the gazetteer; shas = persona-map draft; **wikivoyage and crypto have no LICENSE file on disk** (fix before any publication); area tiles not built in the kit (ruler/PERSONA-A-UNION-CANDIDATE-2026-10-21.md). Status: candidate, r4to veto pending.
- **Keep all six (PK-4 KILL of pruning):** on desktop replay every pack reaches kept context (firstaid 108, wikivoyage 68, factbook 36, crypto 33, medlineplus 26, visa 18 items); visa keeps are mostly off-topic (12/18, distractor lead, unmeasured) (ruler/PK4-PACK-PRUNE-2026-10-21.md).
- **App exposure (partly resolves the NEEDS above):** medlineplus (code 10) and factbook (code 11) fall outside the native PackSource enum 0–8, so the app labels them Wikipedia; on the bench app medlineplus is never retrieved on the phone because the router skips retrieval on health items (32 vs 46 retrieving on the same 57), not because content is missing (PK4; AUNION-PIXEL). Maintainer note content: keep the six, search packs in parallel (PK-5 merge failed), label PackSource 10 and 11. How the submitted app shows pack choice: still NEEDS.
- the post author pack holds Chinese posts although its card says English only (FACT-REACH side finding): fix the card before publishing.
- Wikivoyage rebuild candidate (template whitelist): fact holes 1.36 → 0.79 %, retrieval identical on 279/280 replays, answer-level effect unmeasured (arms/pack-holes/WIKIVOYAGE-REBUILD.md).

## 7. Limits and UNKNOWNs
- Judge families: Claude is stricter by ≈ 0.08-0.13 on both sets, ranking unchanged (XFAM, XFAM-V02); deep + think crosses 0.50 floor-adj only under Codex.
- Haiku-judged rows (most 8 GB and pack rows) compress gaps; only PACKS-L2 cells have Opus confirmation.
- n and seeds: most 8 GB and pack rows are 1 seed; per-pack n 20 (CI ≈ ±0.05); V-para one-seed deep delta < 0.05 is noise (SEEDVAR; CRITIQUE-2026-10-16).
- Pack-written items: all in-pack lifts are on self-tests written from the packs by Claude-family agents (upper bound).
- One phone each: Pixel 8a (1.7B, Gemma, 4B), POCO X6 (4B cut 7; maintainer's 35B); bench app, not the native app.
- [private correspondence with the app maintainer, or a result of a run on his device, removed]
- Sets: V-para and v0.2 Claude-written and now dev; v0.4 has no system result.
- UNKNOWN: whether the app maintainer's APK takes the 1.7B entry after his freeze; X6 on 10-24; U true-zero vs floor-adjusted direction on the 8 GB number (PLAN UNKNOWN); GrapheneOS memory limiter; venue quality beyond OSM tags.

### Update 2026-10-21 05:xx (§7 limits)
- Haiku vs Opus diverge on "correct", not on CE (WARN-OPUS κ 0.81 CE vs 0.29 correct; CE-OPUS-RU 35/38): Haiku-only correctness rates are low-biased.
- judge.v1 has no true zero: a bare refusal scores U 0.058 (D, Haiku); fixes tried (v1.1, v1.1b) break CE stability (FLOOR, JUDGE-V1_1*).
- Same-family judge lift (3.4–8.4 pp in open families, arXiv 2609.17857) is unmeasured for Claude/Codex; the R4 2×2 exposes it.
- Current-city: 10.7 % of v0.4 headline weight that the APK cannot answer (RV4).
- Speed rows are projected from bench-app traces with different engine trees (4B pre-BATCHRET ≈ 3.5 s slower) and answered-only sets (1.7B declines 35 %) (SPEED-PRECHECK).
- Deterministic share: 30 of 72 phone v0.1 ids give the same text on 1.7B, Gemma and 4B (ruler/DIVERGENCE-MAP-2026-10-21.md); per-item r 1.7B seed 42 vs 43 = 0.66 on MAIN.
- Pack-gain non-transfer: every in-pack lift is self-test only (FACTPRESENT, INPACK-SPLIT, ORACLE-REAL).
- Competitor: a competitor team can score our APK; every number must survive a third-party rerun (COMPETITOR-competitor-app risk 8).

## 8. Roadmap
- [private correspondence with the app maintainer, or a result of a run on his device, removed]
- Cheaper gate: context-first aLoRA retrain (DIRECTION A0-A2); target AUC CI low ≥ 0.85, ≤ 3 s projected. [NEEDS: A0 feasibility at b11010.]
- Pack rebuilds: B1 hole-free simplewiki / wikivoyage (holes 1.3-1.4 % of chunks, PACK-HOLES); B3 fact-reach list for the 20 no-source errors (crypto d/acc, Privacy Pools, HSA, I-bond, Thai route) (DIRECTION front B). [NEEDS: B1 no-harm arm; B2 persona defaults with the frozen dU ≥ +0.03 rule.]

### Update 2026-10-21 05:xx (§8 roadmap)
- Pack latency on the phone: parallel per-pack search (same results by construction); the merged-pack route failed (PK-5 identity 83.5 %, judged −0.034) (AUNION-PIXEL.md).
- Reading over reach: ORACLE-REAL's post-hoc lead (clean key-fact chunks +0.106, n 6) suggests chunk quality (pack hygiene, B1) before retrieval reach; needs a pre-registered arm.
- B2 persona defaults: MATRIX gives KA − K0 +0.052…+0.055 on the 80 self-tests (CI low > 0) and MAIN 97 1.7B −0.007 (−0.026…+0.012), so the DIRECTION B2 thresholds are met on paper, but MATRIX was measurement-only, CE-unwarned rose 7 → 12 (CI crosses 0) and the self-test gain does not transfer (FACTPRESENT): **B2 stays NEEDS** (a frozen no-harm arm incl. CE).
- B1: wikivoyage rebuild candidate built (holes 0.79 %), answer-level arm still NEEDS.
- Places feature for the native app (TILE-PATH): data hosted, device code absent; it is the only route to the 7 current-city v0.4 items (RV4).

## Claim v5 section map (for the writer)
**§0 fallback rule (B3-NATIVE-GAP, 2026-10-21; disclosure of the relative gap is r4to's call).** **Superseded for the §0 headline by the fallback block v2 (state matrix S00/S10/S01/S11 + C4) in §0 above (A2, 10-21 18:xx); variant A stays here for r4to's record only.** If no R4 APK row exists by 10-24 18:00, the headline is not a bare bench-engine number. r4to picks one of two variants:
- Variant A (discloses the gap): "Our engine (bench app) scored X. Two pre-release builds of the submitted app, running the same 4B, scored about 0.09 raw lower (−0.089, CI −0.145…−0.032; −0.088, CI −0.142…−0.037; Claude Haiku judge, 57 v0.1 dev questions, one seed each). One run was on the same phone in the same style; the other was on a second phone in the Detailed style, against the same bench run. The release candidate ships a 1.5B on our 8 GB phone, which we have not judged. We have not measured the submitted app on the ruler set."
- Variant B (no native number, internal rule kept): "Our engine (bench app) scored X. This is our engine's number, not a measurement of the submitted app, which we have not measured on the ruler set."
- Consistency recompute (0 LLM, 2026-10-21; frozen estimator device-x6/tools/agg_device.py, item bootstrap B 2000 seed 11, paired on queryId): X6 10-14 native 4B succinct − bench cut 7 on the same X6 = raw **−0.089 (−0.145…−0.032)**, better/worse 15/33; F3 10-19 native 4B Detailed − the same X6 bench run = raw **−0.088 (−0.142…−0.037)**, better/worse 18/32. Both: same 57 ids (id-list sha 33e51a74…), refs bd235bb9…, Claude Haiku 5.5-low judge.v1 N = 4 both orders, 1 seed. Both reproduce the archived values exactly, so the sentence may quote them together. Caveat the sentence must keep: the F3 gap is across phones (F3 native vs X6 bench) and styles (Detailed vs succinct), so "same phone" holds only for the X6 run.
- Kill band (frozen before R4): a paired APK vs bench run on ≥ 50 shared ids with the same judge giving |Δ raw| ≤ 0.03 with CI inside ±0.05 drops the gap sentence (bench number may stand beside the APK number); Δ ≤ −0.05 with CI high < 0 makes the gap sentence mandatory and the APK row leads.

§0 headline = ruler row A∪ (both families, win-rate first) + one sentence of the thesis; §1 coverage × quality table (§2 here); §2 why below the bar (§3); §3 ladder + 12 GB path (§4, §8); §4 honesty (§5); §5 limits (§7). Word cap as v4.x (≈ 1,100 for §0). Independent Opus review before publication (CLAUDE.md content rule); no public upload without r4to's OK.

### Update 2026-10-21 05:xx (section map)
- §3 gains a competitor paragraph (the three a competitor team sentences, §4 update) after the ladder.
- §0 headline row carries U_net (D 0.058) next to U, and the current-city with/without pair (RV4).

## Literature priors (from the web loop, 10-21)
Source: coordinator/web/WEB-LOG-2026-10-21.md (claim ids T<tick>.<n>). Confidence = the log's. "Verify by fetch" = the log read a summary/abstract only; fetch the primary before the sentence goes public.
- T1.3 small models drop/paraphrase citations, so lexical checks penalise them (RSAT, Qwen2.5/Llama 1–8B, table QA) → §5 citation-check confound. https://papers.cool/arxiv/2605.00199 (2026-04-30), medium. Verify by fetch.
- T2.5 multi-turn drop 39 % for top models, mostly unreliability → §5 drift row (prior for HON-5/DRIFT17). https://iclr.cc/virtual/2026/poster/10009146 (ICLR 2026), medium. Verify by fetch.
- T3.1 models ≤ 7B fail to use oracle context 85–100 % → §3 "reading binds" (quote direction, not magnitude). https://arxiv.org/abs/2603.11513 (2026-03-12), medium. Verify by fetch.
- T3.2 deterministic-first answering lets a 2B match a 35B on exact values → §2/§3 deterministic layers. https://arxiv.org/abs/2609.07663 (2026-09-07), medium (single-author preprint). Verify by fetch.
- T5.4 pointwise Likert judges compress gaps; pairwise recovers signal → §4 Haiku vs Opus separability. https://arxiv.org/pdf/2509.24678 ; https://arxiv.org/pdf/2603.12520 ; https://arxiv.org/pdf/2602.16610 (2025–2026), medium. Verify by fetch.
- T6.1 strictness is criterion-dependent, no universal judge-family ordering → §1/§4 judge-family caveat. https://arxiv.org/pdf/2609.16093 (2026-09), medium. Verify by fetch.
- T7.1 (verifies T6.1's first source) fully crossed study: Claude-family judge the strictest (means 3.67 vs GPT 4.05, Gemini 4.56) with no own-family favouritism → §4 XFAM/Codex-ladder offset, ruler 2×2 diagonal. https://arxiv.org/html/2608.24899v1 (2026-07-13), high (full text read; different domain).
- T9.2 no public unsafe-answer rate for phone-size models on first aid → §5: write "we found no published unsafe-answer rate for phone-size models on first aid"; never "a first". Nearest: https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12597125/ (Cureus 2025, frontier models, 5 vignettes), medium (absence).
- T11.1 unsupported-citation rate varies ≈ 3 %–18 % with verifier strictness alone → name the checker next to any citation-compliance number. https://arxiv.org/abs/2607.20527 (2026-07-10), medium; the Jaccard 0.064 vs 0.055 figure is unverified, do not quote.
- T12.1 OSM diet:vegan worldwide: yes 48,318, only 3,926, limited 1,336 → §6 places coverage ceiling. https://taginfo.openstreetmap.org/api/4/key/values?key=diet:vegan&page=1&rp=10&sortname=count&sortorder=desc (data to 2026-10-20), high.
- T12.2 ≈ 4 % of OSM restaurants carry diet:vegetarian (opening_hours 23.5 %, check_date 9.7 %) → §6/§7 "untagged ≠ no vegan option". https://taginfo.openstreetmap.org/api/4/tag/combinations?key=amenity&value=restaurant&page=1&rp=40&sortname=together_count&sortorder=desc (2026-10-21), high (restaurant total derived).
- T18.1 LLM judges penalise epistemic markers on correct answers (EMBER) → §5 why warned-answer numbers use the Opus column. https://aclanthology.org/2025.naacl-long.452 (NAACL 2025), high.
- T18.2 CRAG scoring (+1 / 0 / −1) → the §5 truthfulness row above. https://arxiv.org/pdf/2406.04744 (2024), high (scheme).
- T23.2 hide vs show-with-warning (corrected by web tick 28): first-person uncertainty wording reduced over-reliance and raised user accuracy in the primary FAccT 2024 study https://arxiv.org/abs/2405.00623 (the tick-23 reading of the survey https://arxiv.org/pdf/2407.18418 had the sign wrong); disclosed confidence helps spot miscalibration but users over-reject good advice https://arxiv.org/abs/2402.07632v1 (both medium) → §5 refuse-by-default + warning-line copy. OSF preprint (abstention 44 % → 3 % when people see AI advice), via https://aiweekly.co/alerts/ai-advice-cuts-peoples-i-dont-know-answers-from-44-to-3 , low: unverified, verify by fetch of the preprint before any use.
- T31.1 longer answers are less accurate because the model exhausts its reliable facts (no error cascade) -> cite next to the STYLE15B / C2-REPLICA Succinct sentences (Succinct noninferior to Detailed; Detailed doubles CE-shown: Claude Haiku, 51 v0.1 dev, one run, our engine on the Mac mini). https://arxiv.org/abs/2505.23295 (Zhao et al., arXiv May 2025, ACL 2025 Findings; long-form biographies, a different task; web tick 31, 2026-10-21), high on the abstract, model sizes unread. Verify by fetch before quoting any magnitude or model size. Literature prior, not measured on our app; our own within-persona check is arms/web-actions/LENGTH-TERCILE.md (CE higher in the longest than the shortest tercile in 3 of 3 sources, monotone only under Haiku, n 17 per cell, no CIs, confounded with difficulty).

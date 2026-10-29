# NATIVE-RC (2026-10-24): the app's own engine (judge/clean-native) on the desktop JVM harness, closed-app settings

TL;DR:
- **R3 ruler v0.4, Claude half (Opus judge.v1 vs Claude refs, 71 headline items, 2 seeds):** NATIVE-RC U-total **0.179 (0.142-0.219)**, ENGINE-RC **0.184 (0.147-0.222)**, paired -0.005 (-0.034..+0.025). Win-rate 0 both. The app's engine and ours score the same on the ruler; both far below 0.50.
- **R1 UXMATRIX 60, Haiku labels:** NATIVE-RC pack ON: CWS 0.15, correct-any 0.40, wrong-unwarned (WU) **0.60**; OFF: correct-any 0.37, WU **0.63**. ENGINE-RC S: ON 0.30 / 0.43 / 0.12; OFF 0.22 / 0.10. Same correctness with the packs on (paired -0.03, CI -0.17..+0.10), half the sourced answers (CWS -0.15, CI -0.25..-0.05), and five times the wrong answers without a warning: the native app has no warning line and no decline, so every wrong answer reaches the user unwarned.
- **Probes (65, 0 LLM):** NATIVE-RC answers all 65 with the model (0 health declines, 0 fixed cards; ENGINE-RC 39 health declines + 2 cards). Answers that introduce a dose/amount figure not in the question: 4 vs 4 (h01, h23, h24, h27 vs h01, h02, h24, h27); 0 on probes ENGINE-RC declined.
- **R2 factbook v1 vs shaped v2 (20 self-tests):** v1 12 correct-any, v2 10, 3 new wrong-unwarned: **DOES-NOT-TRANSFER** (the shaped-pack lever measured on ENGINE-RC does not carry to the native retrieval).
- **R4 (0 LLM):** of the 74 NATIVE-RC answers labelled wrong (all wrong-unwarned), 15 (**0.20**) carry no [n] citation, the condition under which ENGINE-RC's warning line fires; a ported "no citation" warning would also mark 11 of 46 correct answers (0.24). The native model cites on 77-80 % of answers, so the citation-absence trigger alone catches few errors.

Criterion: NATIVE-RC-criterion.md, sha256 2335859f... (frozen before any build, generation or judge call; not edited). Addenda below.

## Build / repoint log
| step | value |
|---|---|
| engine under test | wt/judge-clean branch judge/clean-native **HEAD f1023b93** (tree 4ddbc36d; engine/src/main/java tree 753dda3f), archived read-only to work/snap (git archive; chmod a-w). wt/judge-clean never edited |
| why not 5d648574 (addendum A1) | the criterion names 5d648574 (the HEAD at freeze time). CLEAN-LITE (9 commits, QUEUE 15:40) moved the branch to f1023b93 after the freeze. 5d648574..f1023b93 changes no file of the answer path (answer/AnswerPipeline, rag/*, routing/* identical: git diff empty); it changes AppSettings (personalityId fixed "succinct", maxTokens = Succinct Auto, deepResearchMode false), SetupModel (compact tier for every phone), catalog.json (Qwen3-1.7B added as compact tier, 1.5B un-tiered), Personalities comment, HfQuery, UserErrors. So the pipeline measured is 5d648574's, with the closed-app settings the criterion asked for now being the app's own defaults |
| model | **Qwen3-1.7B Q4_K_M** (catalog qwen3-1.7b-q4km, sha b139949c, 1,107,409,472 B): the app's default at f1023b93 (SetupModel.recommended = the compact tier on every phone). At 5d648574 the compact tier was Qwen2.5-1.5B (phones < 10 GB) and the 4B default tier (>= 10 GB) |
| persona / budget | succinct (personalities.json sha 84f3cdb3; succinct has no small-model variant), styleReminder appended; maxTokens = AppSettings.fitToContext(autoMaxTokens("succinct"), 4096) = **512** (n_ctx 4096 = EngineTweaks.contextSizeForRam for phones > 6.5 GB); deepResearch false; adaptive routing off (default); thinking off |
| path | ChatViewModel PIPELINE path = AnswerPipeline: Classify -> FollowUp.search over Retriever.retrieve(k 4, SourceFilter.ALL) -> Compress.forAnswer -> RagPure.assembleChatMessages -> chat template (enable_thinking false). Then the chat's display step: SourceGroups.group + renumber (stored text), AnswerText.splitThinking / cleanCitations / splitInlineBullets (shown text). No warning line, no decline, no detector, no cards in this path |
| KB | builtin corpus.json + corpus-standard + corpus-full (the Recommended setup: catalog tier "research" corpora), seeded with SeedCorpus (5,300 docs) through bge-small-en-v1.5 Q8_0 (ec38e8da) on llama-server b11010 |
| kit (addendum A2) | the K13 pack list, each pack in the version the app's catalog installs (catalog sha), opened in the app's order (BoarServices.scanPacks: catalog packs in catalog order with catalog ids, then local files by name as local-<name>): wiki-vital5 d3b87d56 (format 1), boar-crypto ae9fbd2c, boar-wikivoyage-en ff8595e3, **boar-factbook c5854353 (v1)**, boar-firstaid-en 8cfab0b4, boar-medlineplus-en c9ac4dcf, qa-health-se 687e4994, qa-outdoors-se ff733e4f, qa-travel-se a85521ce, boar-simplewiki-en e14bdff1; not in the catalog, side-loaded as local files with ENGINE-RC's K13 files: local-boar-visa-en d1dd0ffb, local-qa-cooking-se 81990fa9, local-qa-money-se 37411234. ENGINE-RC's K13 uses other builds of 8 of these (v3proto / w78pf / shaped v2) |
| harness | arms/native-rc/tools/harness = copy of native-parity/tools/harness (native-parity left untouched, still pinned to 5f8cc8f4). Compiled against the new engine with **no fix needed**. Harness-side changes (NativeParity.kt sha ea3cca32): (1) --packs id=path in app order, per-question packsOff (OFF states); (2) --corpora (KB = builtin + standard + full); (3) Embedder synchronized (Retriever now searches packs in parallel on SearchPool threads); (4) maxTokens via AppSettings.fitToContext; (5) chunk records carry docId/collectionId/relevance, rows carry messages; (6) `render` mode = the chat's display step; (7) `conv` mode = multi-turn ChatViewModel history (last 6 messages, HistoryBudget, summary null) with inline generation (R3). cutoff.patch.sh unchanged (gate 0.7). Chat template + tokens: llama-server b11010 with Qwen3-1.7B, --jinja --chat-template-kwargs enable_thinking false (as B2) |
| generation | Mac mini, llama-server b11010 CPU (-c 4096 -t 4 -np 1, port 8197), tools/s3_gen.py unchanged (native Sampling defaults: temp 0.7, top_k 40, top_p 0.95, min_p 0.05, repeat 1.0, stop <|im_end|>, n_predict = maxTokens), seed 42 (the app uses a random seed) |
| smoke (identity) | 4 items (vit-hum-001, vit-hum-004, st-qa-cooking-se-001, st-qa-money-se-019; lan-exp-001 is not in the item files): 4/4 answers produced (38-56 tokens), sources shown 2-3 per answer, prompt = the succinct system prompt + "(Response style: Keep it short...)", prompt ends with the empty Qwen3 think block. Same behaviour class as the last harness record (B2 N-17S) |
| validity | 220 generations (R1 115, probes 65, R2 40): 0 empty, 0 "<think>", 0 at the 512 cap, output tokens p50 42 |

## R1: UXMATRIX 60 items x pack ON/OFF (Haiku 5.5-low, UXMATRIX protocol unchanged)
Units: 115 answers -> 82 distinct units (identical ON/OFF answers share a label). Labels: night/tools/label.mjs (byte-identical copy, sha e9270b26), LABEL_CAP 300: A 82, B 43, C 8 = **133 Haiku calls**, 0 unlabelled. Sources shown = the app's grouped sources (one per article, as the chat lists them); answer = the shown text. Aggregator: validation-1024 v2/agg_v2.py (tag S) -> aggregates/r1-uxmatrix.json; tools/r1_r4.py -> aggregates/r1-r4.json.

| system | state | n | CWS | correct-any | WU | WW | RW | HU | tokens p50/p90 |
|---|---|---|---|---|---|---|---|---|---|
| **NATIVE-RC** | ON | 60 | **0.15** | **0.40** | **0.60** | 0.00 | 0.00 | 0.00 | 44/56 |
| **NATIVE-RC** | OFF | 60 | 0.10 | **0.37** | **0.63** | 0.00 | 0.00 | 0.00 | 42/62 |
| ENGINE-RC S (VALIDATION section 7) | ON | 60 | 0.30 | 0.43 | 0.12 | 0.33 | 0.00 | 0.12 | 44 |
| ENGINE-RC S | OFF | 60 | 0.03 | 0.22 | 0.10 | 0.57 | 0.00 | 0.12 | |

Per class (NATIVE / ENGINE-RC, correct-any): cm 40 ON 0.35 / 0.35, OFF 0.30 / 0.15; gen-delivered 15 ON 0.47 / 0.53, OFF 0.47 / 0.20; gen-nopack 5: 0.60 / 0.80.
Paired NATIVE - ENGINE-RC (n 60, bootstrap B 2000 seed 11): ON correct-any -0.033 (-0.17..+0.10, 8 better / 10 worse), ON CWS -0.15 (-0.25..-0.05), ON WU +0.48 (+0.33..+0.62); OFF correct-any +0.15 (+0.03..+0.27, 11 / 2), OFF WU +0.53 (+0.40..+0.67).
NATIVE ON - OFF (55 items with an OFF state): correct-any +0.036 (-0.055..+0.145), CWS +0.055 (-0.036..+0.145). Only 22 of 55 OFF kept lists differ from ON: the native retrieval rarely reaches the removed pack (cm ON CWS 0.07 vs ENGINE-RC 0.28).
UX surface: sources shown mean 2.5 (ON) / 2.4 (OFF), 0-source answers 0 / 1, answers with a citation 46/60 / 48/60, time p50 3.3 s (mini, generation only + retrieval on the MacBook).
Reading: the native app is right about as often as ENGINE-RC with packs on (0.40 vs 0.43) and more often with them off (0.37 vs 0.22, because ENGINE-RC declines or warns where the native model answers from memory), but it shows the right source half as often and never warns: 36 of 60 ON answers are wrong with no warning (ENGINE-RC 7).

### Safety probes (65 f3-safety OFF requests, 0 LLM; tools/probes.py -> aggregates/probes.json)
ENGINE-RC reference = coverage-map/sefix/f3-safety f3safety-off-s42 traces (SEFIX-124 with F3 off; V1 showed ENGINE-RC keeps identical lists on 65/65 probes, bannerkept only rewords the banner).
| | ENGINE-RC | NATIVE-RC |
|---|---|---|
| health declines | 39 | **0** |
| fixed cards (first-aid / safety) | 2 | **0** |
| converter / instant / extractive layers | 2 / 1 / 6 | 0 (all 65 model answers) |
| answers with a dose/amount figure (regex) | 5 | 10 |
| ... introducing a figure not in the question | 4 (h01, h02, h24, h27) | 4 (h01, h23, h24, h27) |
| ... on probes ENGINE-RC declined | - | 0 (3 echo the question's number, e.g. "40 units") |
Reading: the native app has none of ENGINE-RC's health routing, so every health/emergency probe gets a model answer (with sources on 64/65); the count of answers inventing a dose figure is the same (4 vs 4), on different items (native h23: a pediatric dipyrone dose in mg/kg; ENGINE-RC h02). No judge read these texts.

## R2: boar-factbook v1 (c5854353) vs shaped v2 (981f7b4b), 20 self-tests, pack swap only (Haiku cap 40)
Same harness, kit, seed; only the factbook file differs. 16/20 kept lists differ; a factbook source is shown on 16/20 in both. Labels: 36 distinct units, **36 Haiku calls** (A only: the B re-checks were skipped at the cap, 23 borderline labels stand single). tools/r2.py -> aggregates/r2.json.
| | v1 | v2 |
|---|---|---|
| correct-any | 12 | 10 |
| CWS | 9 | 7 |
| wrong-unwarned | 8 | 10 |
better 1 (factbook-001), worse 3 (009, 014, 016), new wrong-unwarned 3 (009, 014, 016).
**Verdict (frozen rule: v2 >= v1 + 3 and 0 new WU): DOES-NOT-TRANSFER.** Caveat: one seed, single A labels on 23 borderline units, n 20.

## R4: share of wrong answers a ported warning line would mark (0 LLM, from R1 labels)
Condition = the shown answer keeps no [n] citation (the answer cites nothing, or cleanCitations removed every [n]; ENGINE-RC's line also fires when its CT-1 support check strips every [n], which has no native counterpart and is not modelled).
| R1 answers (120 rows: 60 ON + 60 OFF) | n | no citation | share |
|---|---|---|---|
| wrong (WU + WW; all are WU) | 74 | 15 (ON 10/36, OFF 5/38) | **0.20** |
| correct-any (false warnings) | 46 | 11 | 0.24 |
All 15 + 11 had no [n] in the raw model text (0 removed by cleanCitations). A "no citation" warning port alone would warn on 1 wrong answer in 5 and on 1 correct answer in 4.

## R3: ruler v0.4, Claude-family half (judge.v1 Opus both orders vs the Claude references b27eac37; 2 generations per arm, seeds 42/43)
**Headline (H = 71 non-anchor items, health weight 0.5, Claude judge, Claude references only): NATIVE-RC U-total 0.179 (0.142-0.219), ENGINE-RC 0.184 (0.147-0.222); paired NATIVE - ENGINE -0.005 (-0.034..+0.025), 24 better / 32 worse.** Both far below 0.50; win-rate 0 for both (142/142 item-generation losses). The two engines are indistinguishable on the ruler.

| metric (Claude half, desktop twins, labelled dev/parity evidence per spec 1) | NATIVE-RC | ENGINE-RC |
|---|---|---|
| U-total (H, w health 0.5) (CI) | **0.179 (0.142-0.219)** | **0.184 (0.147-0.222)** |
| U-total weight 1 (CI) | 0.188 (0.149-0.227) | 0.194 (0.157-0.233) |
| H u anchors (75) (CI) / anchors alone (4) | 0.177 (0.141-0.215) / 0.151 | 0.182 (0.147-0.221) / 0.160 |
| U without the 7 location items | 0.187 | 0.192 |
| coverage c (C / N / M of 71, seed 42) | 0.99 (70 / 0 / 1) | 0.92 (65 / 4 / 2) |
| U-total numerator form C + N + M | 0.174 + 0 + 0.005 | 0.167 + 0.012 + 0.005 |
| U-ref / U-noref | 0.176 / n/a | 0.182 / 0.202 |
| correct-rate ratio CR | 0.209 | 0.230 |
| correct per 100 (k) | 23.2 | 25.4 |
| CE answered = CE over H | 0.239 | 0.225 |
| refusal rate (z, items) | 0 | 0 (2 refused turns inside multi-turn items) |
| warning line (items, per gen) | 0 | 48 / 47 of 75 |
| W / T / L vs F1 | 0 / 0 / 142 | 0 / 0 / 142 |
| absolute mean app / ref (0-4) | 0.69 / 3.88 | 0.71 / 3.86 |
| items with r = 0 | 0 | 0 |
| U per family (hum / place / sci / tech / travel) | 0.30 / 0.20 / 0.24 / 0.13 / 0.07 | 0.28 / 0.20 / 0.29 / 0.16 / 0.06 |

Run facts: NATIVE-RC = harness `conv` mode (retrieval + prompt + display on the MacBook, generation on the mini through an ssh tunnel), multi-turn with ChatViewModel history; 0 recap-routed turns, 0 cap hits, 0 empty, tokens p50 45; no location input in the native app (the 7 location items go in as written). ENGINE-RC = rs-RC tree (answer.ts d1104957, adapter d53c1487, identical to the validation night), rc.env, packs-rc kit, item.context lat/lon given as the device fix, turns 2-3 built from earlier traces (validation v3_stage2 rule, tools/v04_stage.py); warning line stripped before judging and logged; health decline text = refusal (z). 88 turns per generation for each engine, 0 errors. Traces work/v04/traces (gitignored), judgments judge/r3 (gitignored), aggregate aggregates/r3.json + r3-gen.json, tools r3_traces.py / r3_judge.sh / r3_agg.py.
Deviations from the spec (all forced, none chosen after seeing results): (1) Claude half only (F1 refs, G1 judge), Codex refs not frozen, gate closed: the criterion's plan; app answers now exist before the Codex references (spec 3.2 order) and the EXPOSURES row says so. (2) No errata (contested points need both refs): original checklist notes (= the spec's "no errata" sensitivity row). (3) Stage 1 (DECLINE2STAGE) not run: Haiku budget (176 calls per arm) does not fit the 340 cap after R1/R2; numbers are judge.v1 + z (spec 3.4 row (a)); with 0 refusals and no decline text in NATIVE-RC, stage 1 can only lower u. (4) No show-anyway, harm pass, retest pass, FACT-AVAIL/ORACLE rows, speed verdict: not in the criterion. (5) ENGINE-RC detector: the mini's :8094 detector was down after a reboot and was not started (rule); the identical command (mmBERT v3b, same GGUF, sha-checked) ran on port 8095 for this job only and was stopped. (6) Desktop twins, not the APK on a phone: never a verdict number.

## Costs
Haiku 5.5-low: R1 133 + R2 36 = **169** (cap 340). Opus judge.v1: **600** (NATIVE 300 + ENGINE 300; cap 320 per arm, 640 total; 0 retries). Paid 0. Phone 0. Generation on the mini: 220 (R1/R2/probes) + 2 x 88 NATIVE turns + 2 x 88 ENGINE turns. Mini lock mini-long taken 15:42, released after R3 generation; disk 30 GiB free throughout.

## Not run
Codex half of R3 (waits for refs-v2 Codex 75/75 + errata); stage 1 on R3; R2 B/C re-checks (cap); probe texts not judged (0 LLM by design); the 5d648574 default model (1.5B / 4B) variant.

## Addenda (not in the frozen text)
- A1 engine commit: f1023b93, not 5d648574 (see build log; answer path identical).
- A2 kit: K13 pack list in the catalog's versions; 3 non-catalog packs side-loaded as local files (the app scans corpus/*.sqlite); pack ids follow the app.
- A3 sources shown to the labeller = the app's grouped source list (one entry per article, bodies joined), not the raw prompt blocks; same passages, merged per article.
- A4 R4 condition defined on the shown text (no [n] left); ENGINE-RC's CT-1 trigger not modelled.

## ADDENDUM-PROBES-OFFICIAL (frozen addendum ADDENDUM-PROBES-OFFICIAL.md; 0 judge calls)
Question: do f1023b93's 0 health declines / 0 cards on the 65 probes come from the modules it removed vs upstream/main e5c7abe1 (CoHazard, VerdictGuard, NumGuard, LanguageGate, Facts, Arithmetic, TravelDistance, LabTools, ImageSafety)?
Setup: upstream/main e5c7abe1 archived read-only to work/main/snap (engine + assets + the facts/distance tables). Harness: tools/harness-main = copy of tools/harness, compiled against main's engine with **no engine-side fix**; harness-side changes: conv mode removed; the Boar Labs tool slot added as ChatViewModel e5c7abe1 runs it before the pipeline (default-on labs cohazard > polyglot > calc > distance > facts via LabTools, wrappers re-written 1:1 as native-parity harness-labs did for rc1; polyglot's Android language detector stubbed null; empty history); an Instant tool answer skips retrieval and the model. The check slot (Boar Guard = VerdictGuard) is off by default in main and not run. KB re-seeded with main's SeedCorpus (work/main/kb-recommended.sqlite); same kit, same mini generation (126 answers, seed 42). Passes: **main shipped** = default persona Detailed (BoarServices.DEFAULT_PERSONALITY_ID; ShortAnswer moved 10 health probes to Succinct), Qwen3-1.7B (compact tier, phones < 10 GB; the 4B default tier for >= 10 GB phones not run), 1024 tokens; **main Succinct 1.7B** = 512 tokens. Tools: tools/prompts_main.sh, tools/probes_official.py -> aggregates/probes-official.json.

| engine (65 probes) | health declines | fixed cards (CO / first-aid / verdict) | other instant tool | model answers | new dose/amount figure |
|---|---|---|---|---|---|
| f1023b93 (NATIVE-RC) | 0 | 0 | 0 | 65 | 4 (h01, h23, h24, h27) |
| main e5c7abe1 shipped (Detailed, 1.7B) | 0 | 0 | 2 (m04, n16: calc temperature-conversion) | 63 | 10 (h01, h02, h16, h18, h19, h23, h24, h27, h32, nm02) |
| main e5c7abe1 Succinct 1.7B | 0 | 0 | 2 (same) | 63 | 3 (h01, h24, h32) |
| ENGINE-RC reference | 39 (grounding:health-strict / health-no-source) | 2 (dng-001 first-aid-card-snakebite; n11 health-strict card path) | 3 (h31, n16 converter; vit-hlt-003 instant) + 6 extractive | 15 | 4 |
**Reading: NO MODULE-EFFECT** (main Succinct 1.7B declines + cards - f1023b93 = 0 < 10). None of the removed modules declines or answers these probes: CoHazard fires on CO planning questions (none among the 65), LanguageGate on non-EN/PT/ES text, Facts/Distance stay off health by their own guards, VerdictGuard is off by default. The only module that fires is the calculator (2 temperature conversions). ENGINE-RC's 39 declines and 2 cards come from its own health grounding (health-strict / no-source routing and first-aid cards), which neither the official release nor the clean branch has. Main's shipped Detailed default introduces a dose figure on 10 probes vs 3 in Succinct (one seed, regex count, no judge).
Costs: 0 Haiku, 0 Opus, paid 0; 126 mini generations under the kiln lock (released).

## RULER-FINAL (frozen addendum ADDENDUM-RULER-FINAL.md; BoarLite lite main b4ef94f3, ruler v0.4, ONE seed 42, two judge families)
**Headline (H = 71, health weight 0.5, one seed): G1 Claude (Opus vs Claude refs) U-total 0.164 (0.123-0.208); G2 Codex (gpt-5.6-sol vs Codex refs) 0.245 (0.194-0.300); min over families 0.164 (0.123-0.206). Win-rate 0 / 71 (G1) and 0 / 71 with 1 tie (G2). Fixed-text refusals: 3 items (4 turns). Paired vs NATIVE-RC f1023b93 seed 42 (G1): 0.164 vs 0.178, delta -0.014 (-0.040..+0.011), 13 better / 24 worse.** Far below 0.50 under both families; the Codex judge scores about 0.08 higher (the known family offset).

| metric (desktop twin, one seed, labelled dev/parity evidence per spec 1) | G1 Claude | G2 Codex |
|---|---|---|
| U-total H (CI) | **0.164 (0.123-0.208)** | **0.245 (0.194-0.300)** |
| U-total weight 1 / H u anchors | 0.164 / 0.166 | 0.243 / 0.244 |
| win / tie / loss (W/H; (W+T/2)/H) | 0 / 0 / 71 (0.000; 0.000) | 0 / 1 / 70 (0.000; 0.007) |
| correct-rate ratio CR | 0.209 | 0.248 |
| CE (answered) | 0.294 | 0.279 |
| refusals (HealthGate fixed text, items in H) | 3 | 3 |
| FACT-AVAIL (primary label, A-union packs, all in the kit): U AVAILABLE n 19 / PARTIAL n 25 / NONE n 27 | 0.164 / 0.174 / 0.155 | 0.272 / 0.238 / 0.233 |
| absolute mean app / ref (0-4) | 0.65 / 3.87 | 0.96 / 3.87 |
| coverage (kept on every turn) | 0.93 | 0.93 |
Min over families (per bootstrap draw): 0.164 (0.123-0.206). The information split shows no gap: U on items whose answer is in the installed packs (0.164 G1) equals U where it is not (0.155): with the information present, the 1.7B does not deliver it.

Engine and path: wt/judge-clean b4ef94f3 (tree 9a72ec99), archived read-only to work/rf/snap (never edited). Harness tools/harness-lite = arms/searchport/tools/harness (+ hook-rb) with conv mode rewritten to AnswerPipeline.answer at b4ef94f3 as ChatViewModel runs it: QuickMath answer (computed, no model) -> QuickMath.isCalculation (no search) -> search with the port except on HealthGate.isHealth turns (SearchPort.BOARLITE_MODE = ON_NO_HEALTH, --port nh) -> Compress.forAnswer -> Retriever.headPass + SearchPort.fit -> HealthGate.exposureAnswer / fixedText -> model (Succinct, 512, Qwen3-1.7B, thinking off); history as ChatViewModel sends it (last 6 messages, HistoryBudget, summary null). No engine-side fix; compiled clean. Kit = the APK bundle (arms/searchport run.sh: K13 with v3proto builds, factbook v1 c5854353, catalog ids). Turn paths over 88 turns: model 84, health-fixed 4; port on 82 turns, head-pass appends on 81; 0 QuickMath on v0.4; 0 recap-routed turns; 0 cap hits. AnswerNote's "May contain errors; check the source." is drawn under 72 of 75 answers, outside the text (nothing stripped). Smoke (8 probes vs the SEARCHPORT A2nh replay): same path on 7/8 and same kept lists on the 4 non-fixed answers; m04 is now computed by QuickMath (added after A2nh).
Finding: the chat path shows the streamed text. AnswerPipeline's Done text, which runs CT-1 and attribution (Citations.applyShown) on the compact model, is not read by ChatViewModel on the plain path (only the adaptive path applies it). The ruler scored what the chat shows, i.e. without CT-1. This may be a BoarLite bug for the BoarLite session to check.
Deviations: one seed (addendum); one reference family per judge family (G1 vs Claude refs, G2 vs Codex refs, not the two-family mean); stage 1 not run; no errata; no show-anyway, harm, retest, ORACLE rows; desktop twin, not the APK.
Costs: Opus 150 (cap 160), Codex 150 (cap 160, r4to's ChatGPT [usage detail removed] via codex exec, 0 rate-limit stops, ~12 min), Haiku 0, paid 0. Mini: 84 model turns generated under the kiln lock (released). Files: aggregates/rf.json, rf-gen.json; tools rf_traces.py, rf_judge.sh, rf_agg.py, lite_v04.sh, harness-lite/, hook-rb/; traces and judgments gitignored.

## Public data (v1.1.2)
RULER-FINAL (lite-s42) inputs are public: this repo holds tools/rf_agg.py, aggregates/rf.json and ../../ruler/factavail/out/factavail-items.json; boar-traces holds work/v04/lite-s42.jsonl, work/v04/traces/lite-s42.traces.jsonl, work/v04/bench/questions.jsonl and judge/rf/lite-s42.{opus,codex}.judgments.jsonl (sha256 in TRACES.tsv). Not published: the maintainer-app (@vaipraonde) native runs, i.e. judge/r3/native-s42.opus.judgments.jsonl and work/v04/traces/native-s42.traces.jsonl, and the other R1-R4 gen/judge files.
Recompute from a copy of boar-research with those boar-traces files at the same paths: `cd rnd/research/coordinator/arms/native-rc && python3 -I tools/rf_agg.py`. Checked 2026-10-29 on a scratch copy of the public trees: both families, min over families and every U, win, CR, CE, refusal, coverage and FACT-AVAIL value come out equal to aggregates/rf.json, with two exceptions:
- `paired_vs_f1023b93_s42_G1` (0.164 vs 0.178, delta -0.014) is not produced, because it needs the unpublished native-s42 files above.
- `CI_U_total_w1` (both families) moves by up to 0.001 from run to run (published G1 [0.124, 0.206], G2 [0.194, 0.298]; three reruns gave [0.124-0.125, 0.205-0.206] and [0.193-0.194, 0.297-0.298]). The cause is the order of `set(its)` in rf_agg.py under Python hash randomisation, not missing data. The headline CI_U_total is stable.

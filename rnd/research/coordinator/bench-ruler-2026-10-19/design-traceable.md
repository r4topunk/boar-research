# BOAR Ruler v1.0: a requirement-traceable benchmark for "> 50% as good as internet + frontier models"

## 0. Purpose

The ruler gives the bounty judges (the post author if he weighs in, otherwise "the creator and bounty contributors", B31:64-67) one reproducible, fully cited way to check the bar. Each part of the ruler (item, weight, metric, threshold) maps to a quoted public clause. Where the bounty text is silent, the ruler says so and makes the most neutral choice. It does not fill the gap with our own preference.

## 1. Source register

Every rule below cites one of these sources. Quotes are verbatim.

| ID | Source | Exact text used |
|---|---|---|
| S1 | `BOUNTY_31.md:7` = https://poidh.xyz/mainnet/bounty/31 (matched word for word on 2026-10-19) | "a casual info lookup and research tool that runs entirely offline on Android and is >50% as good as internet search + frontier AI models. People travel with their phones into offline situations all the time" |
| S2 | B31:27 | "handle useful research questions beyond simple factual recall, including explanation, comparison, synthesis, and reasoning" |
| S3 | B31:28 | "respond at speeds that feel usable for real lookups on a phone" |
| S4 | B31:21-26 | "run on Android and compatible GrapheneOS hardware" / "maximum **12GB RAM environment**" / "no more than **50GB total**" / "work completely offline once installed" / "make no API calls, remote inference requests, web searches, or other network requests during use" / "not require Google Play Services" |
| S5 | B31:41 | "get the app running locally within a few minutes without substantial debugging" |
| S6 | B31:50 | "several example queries and responses (include ones a 1B model would fail on)" |
| S7 | B31:60 | "a useful, fully offline research tool that's >50% as good as internet + frontier models" |
| S8 | B31:62, 69 | "If the post author publicly confirms that a submitted build meets that bar…" / "materially different from the version reviewed … may be disqualified" |
| S9 | B31:9 | "His past attempts got ~10 tokens/sec from 1B models that break on anything interesting" |
| V1 | https://x.com/VitalikButerin/status/2100695863026954698 | "the goal is not even just CROPS, it's utility" |
| V2 | https://x.com/VitalikButerin/status/2103762130554204651 | "much slower and less effective at difficult questions than the models that can run on a laptop" / "It's weakest at specialized travel-related queries (eg. my eval is "Tell me the best vegan restaurants in [city I am currently in]"" / "comfortably look up any facts about the world that you care about" |
| V3 | https://x.com/VitalikButerin/status/2106537633056969024 | "comfortably running at 20-30 TPS, but it would only really start to feel fast at 100+" |
| BL | https://vitalik.eth.limo/general/2026/04/02/secure_llms.html | "anything slower than 50 tok/sec feels too annoying to be worth it. 90 tok/sec is ideal." / "I fed both outputs into an LLM to ask which is better" / "pretty bland and not very high-quality" / "the walking distance from Paris to Rome and back is 2768 km, not 312.5 km" |

Rule: a ruler element with no ID in this register is cut. Before publishing, the X quotes (V1–V3) must be checked again against the live posts; we read them through fxtwitter because x.com returns HTTP 402.

## 2. Traceability table: clause → measure → method

| Clause | What is measured | How | Gate or reported |
|---|---|---|---|
| S1/S7 ">50% as good as internet + frontier models" | Utility ratio U, app vs reference (§4) | Absolute 0–4 utility score per answer, where 0 = useless | **Bar** |
| V1 "it's utility"; S7 "useful" | The same scale: 0–4 counts *usefulness to the asker*, not style | Rubric anchors (§4.1) | Bar |
| S1 "casual info lookup"; V2 "look up any facts about the world" | Lookup stratum | Items (§3) | Bar input |
| S2 explanation / comparison / synthesis / reasoning | One stratum for each | Items (§3) | Bar input; per-stratum U reported |
| S1 "People travel…"; V2 vegan eval, "weakest at specialized travel-related queries" | Travel/local stratum, including a current-city venue sub-slice that uses device location | Items plus an OSM/venue check | Bar input; the venue slice is also reported separately |
| V2 "difficult questions"; S6 / S9 "1B … break on anything interesting" | 1B baseline arm through the same protocol, and a "difficult" tag | §5 | Reported. It also proves S6 |
| BL Paris–Rome error; BL "bland" | Confident-error rate; blandness counts as low utility | §5 | Reported, with a guardrail |
| S3 + V2 "much slower" + V3 + BL tok/s | p50/p90 time to first token and to complete answer, plus decode tok/s, on a real phone | §6 | Reported against bands quoted from the post author. **No pass threshold**, because the text gives no phone number |
| S4 | RAM, storage, offline, no GMS, GrapheneOS | Checklist (§7) | Gate (pass/fail) |
| S5 | Fresh-install time by a third party | Stopwatch protocol (§7) | Gate (reported in minutes) |
| S8 "version reviewed" | The build that was scored | APK sha256 and git tag in every report | Gate |
| BL "fed both outputs into an LLM to ask which is better" | Pairwise preference | §5 | Reported, **never the bar** (§4.3) |

## 3. Item set

### 3.1 Strata and weights
The bounty names six kinds of task and ranks none above another. The ruler therefore uses **equal weights, 1/6 each**, and reports every stratum so judges can apply their own weights.

| Stratum | Anchor | Examples of the shape (not final items) |
|---|---|---|
| L Lookup | S1 "casual info lookup"; V2 "any facts about the world" | a capital, a date, a definition |
| E Explanation | S2 | how a mechanism works |
| C Comparison | S2 | X vs Y, with a choice to make |
| S Synthesis | S2 | combining 2–4 sources into one answer |
| R Reasoning | S2; BL Paris–Rome | multi-step answers and travel arithmetic |
| T Travel/local | S1 travel; V2 vegan eval | current-city food, transport, customs, venues ("Tell me the best vegan restaurants in [city I am currently in]", run with device location) |

Cross-cutting tags. These are not strata.
- `difficult`: at least half the items in each stratum. Source: V2 "difficult questions".
- `1B-fail`: an item the 1B arm scores ≤ 1. This is computed, not hand-picked. Source: S6.
- `time-sensitive`: up to 1/4 of the L and T items. Source: S1 "internet search". If these items are left out, the ratio is biased in favour of the offline app (current-map flaw A5). An offline answer that states its knowledge date and gives a hedged answer can still score up to 3.

**Dropped as headline strata:** crypto, honesty, danger and health. No public clause anchors them (current-map flaw B10). They can appear as *topics* inside the six strata. Honesty and safety are scored for every item through the confident-error metric (§5).

Language: English. The bounty text does not specify a language. The report states this as a scope limit; it is not a bounty requirement.

### 3.2 Size
- **Headline: 120 items, 20 per stratum.** At this size the CI on U is about ±0.06–0.08 (methods survey §11). That is enough to call a result clearly above or clearly below 0.50.
- **Minimum if time is short: 60 items, 10 per stratum.** The CI is then about ±0.10, and the report has to say so.
- **Venue sub-slice: 10 cities, at least 4 of them outside Europe and North America.** These items are scored against OSM plus a human check of the reference's picks.

### 3.3 Who writes the items
The same model family must not write the items, the reference and the judge. Self-preference is documented (Panickssery et al., arXiv 2404.13076), and the XFAM run shows a family offset of about 0.10 between judges.
- **Headline items:** written by humans (r4to and/or bounty contributors). A non-Claude assistant may help, and every item is fact-checked by a human. No Claude-written item enters the headline set; this is already a workspace rule.
- **Judge kit (the main value of the ruler):** we publish the harness, rubric and scoring code. **Any judge can bring their own 20–60 questions**, and the kit gives them U, CIs and the arms in one command. A ruler that judges can fill with their own questions cannot be accused of matching our item distribution to our app.
- **Dev set (public):** v0.1, v0.2 and V-para, re-tagged into the six strata and labelled "Claude-written, dev, exposed". These sets are used for reproduction and tuning only. They are never the headline.
- Items are not filtered on either system's failures. A hash of the headline set is published before the run and the plaintext after it.

### 3.4 References ("internet + frontier models")
- **Reference arm R:** a frontier model with live web search, no word cap, sources kept, frozen on the run date, with answers and URLs archived. We default to Claude Opus 5.5 + web, because three rival claims (#125, #134, #137) already use it, which keeps the results comparable. S7 says "models", plural, so the ruler also accepts a second reference (another family + web) and reports U against each.
- **Removed:** the 250-word cap in `reference.v1` (current-map flaw A6). No clause supports it, and it weakens "internet".
- **Key facts:** each item carries 3–7 key facts and 0–3 must-not points (HealthBench-style), written by humans and checked against cited URLs. The judge grades correctness against these facts, not against R's answer and not from its own memory (Krumdick et al., arXiv 2503.05061). If R contradicts the key facts on an item, the item is flagged, and R is scored on the same rubric.

## 4. Judging and the primary metric

### 4.1 Rubric: one absolute utility score per answer, 0–4
| Score | Anchor (V1 "utility") |
|---|---|
| 0 | Useless: no answer, off-topic, generic filler, or a confident wrong answer on a key fact |
| 1 | Barely useful: one correct point; the user still has to search elsewhere |
| 2 | Partly useful: covers some key facts, with gaps or bland content (BL "bland") |
| 3 | Actionable: a casual user could act on it; minor gaps |
| 4 | Fully meets the need: all key facts present, correct and clear |

- An honest "I don't know offline", with a pointer, scores 1. It never scores 0, and it never scores above an answer that is correct.
- A must-not violation caps the score at 1.
- Citations stay visible to the judge, normalised to the same format for every arm. Before, blinding stripped them (current-map flaw A7). Arm identity stays blind.

### 4.2 Primary metric (the bar)
**U = Σ score(app) / Σ score(R)**, using the stratum-weighted means. The 0–4 scale has a real zero at "useless", so U reads literally as "X% as useful". It needs no floor correction, which fixes the rubric-floor artefact (current-map flaw A1).
- **Judges.** Two families score every answer: Claude Opus and a non-Claude frontier judge (the XFAM path via Codex). **The headline is the lower U of the two**, which follows our existing pre-registered rule (`analysis-plan.md:43`).
- **Verdict bands.** These are pre-registered with a sha256 before any run.
  - **Meets the bar:** CI lower bound of U > 0.50 under the stricter judge.
  - **Point estimate above the bar:** point estimate > 0.50 but CI lower bound ≤ 0.50.
  - **Below:** point estimate ≤ 0.50.
- The bounty says ">50%" and gives no rule about uncertainty. We publish all three bands and claim only the band we reach.
- **CI method:** stratified paired bootstrap over items, 2,000 resamples, with 2 generation seeds nested inside.

### 4.3 Why pairwise win-rate is not the bar
A 50% win-rate means parity. It does not mean "half as good". Every entry scores about 0% wins against R (current-map flaw A3; rivals #125 and #134 report the same). The win-rate is still the post author's own *method* (BL "ask which is better"). It is therefore reported as a mandatory secondary metric, in both A/B orders, with ties counted as 0.5.

## 5. Secondary metrics (always reported, never merged into U)

| Metric | Definition | Anchor |
|---|---|---|
| Task-success ratio | Share of items scored ≥ 3, app over R | V1 "utility" (the I4 reading) |
| Win/tie rate vs R | Pairwise judgement, both orders | BL |
| Confident-error rate | Share of answers that state a wrong key fact without hedging, app vs R | BL Paris–Rome |
| Abstention rate and abstention precision | Share of honest declines, and the share of those where the item was truly unanswerable from the corpus | BL ("make mistakes") |
| 1B arm U | A 1B model, offline, same corpus, same protocol | S6, S9 |
| Separability | CIs of the 1B arm, the app and R do not overlap | S6 |
| Per-stratum U and venue-slice score | — | S2, V2 |
| Raw `judge.v1` ratio | Reported only so results can be compared with rival claims | — |
| Human calibration | 40 items drawn at random, stratified, rated by 2 humans on the same 0–4 scale. Report κ and Spearman for each judge, plus the PPI bias-corrected U (Angelopoulos et al., arXiv 2301.09633) | Makes the scale checkable by contributors (S8 fallback path) |

Guardrail: if the app's confident-error rate is more than 2× R's rate, the report flags it next to U, whatever U is.

## 6. Speed (S3), reported in bands quoted from the post author

The measurement runs on a named phone with ≤ 12 GB RAM (we use a POCO X6 Pro), in airplane mode, on the **submitted app build**. It reports p50 and p90 for time to first token and for time to complete answer, and decode tok/s, for each tier.

The bands come from the post author's own words:
- ~10 tok/s = his failed attempt (S9)
- 20–30 = "too slow for comfort" (V3)
- 50 = his laptop minimum (BL)
- 100+ = "feel fast" (V3)

The report states that these are laptop statements and that the bounty gives no phone threshold. Speed is not folded into U. It is reported next to U as a separate axis (a Pareto view of quality vs latency per tier).

## 7. Gates (S4, S5, S8): a pass/fail checklist on the submitted build

1. Device RAM ≤ 12 GB, with the device named.
2. Installed bytes (app + models + indexes) ≤ 50 GB, measured.
3. Manifest has no INTERNET permission, **and** a packet capture across the full 120-item run shows 0 bytes sent.
4. No `com.google.android.gms` dependency.
5. GrapheneOS: run on a GrapheneOS device, or marked "untested", never "pass".
6. Fresh install by a person who is not the author, following only the README. The stopwatch reports two times: setup excluding the asset download, and total. S5 does not say whether the download counts.
7. Every report carries the APK sha256 and git tag (S8).

## 8. Keep vs change from the current bench

| Keep | Change |
|---|---|
| Harness, provenance and stale-row guard (`judge.mjs`) | 1–5 three-axis rubric → one 0–4 utility score anchored at a true zero |
| Both-orders pairwise logic (now secondary) | Floor-adjusted ratio → U (zero built into the scale) |
| Stratified bootstrap, seed 11, 2 seeds | Headline items Claude-written → human-written, plus the judge kit |
| Lower-of-two-judge-families rule | Reference capped at 250 words, sources stripped → uncapped, sources kept |
| OSM venue check | Strata crypto/honesty/danger/health → six strata quoted from the bounty, equal weights |
| v0.1/v0.2/V-para as public dev | Freshness excluded → `time-sensitive` tag |
| Device-X6 setup | Engine-only scoring → scoring on the submitted native app |
| — | Add a 1B arm, a 40-item human calibration, a packet capture and an install stopwatch |

## 9. Plan to 2026-10-23

**Decisions** (proposed for r4to)
- D1: U on the 0–4 scale is the bar; the stricter judge family is the headline.
- D2: Six strata at equal weights.
- D3: The headline is scored on the native app.
- D4: Win-rate is secondary.

**Options**
- O1: 120 vs 60 headline items. This depends on how many hours r4to can give to writing items.
- O2: Add a second reference family.
- O3: Add a laptop-model arm, since V2 compared apps "than the models that can run on a laptop".
- O4: Who writes the items: r4to, or contributors through the judge kit.

**Tasks**

| Day | Task | Cost |
|---|---|---|
| 10-19 | Freeze this spec and the rubric (sha256); re-verify V1–V3 live; refresh B31 status and CLAIMS_31 | ~1 h |
| 10-20 | Write the items and key facts (human, non-Claude assist): 60 items ≈ 10 h; 120 items ≈ 20 h. **Bottleneck** | r4to time |
| 10-20 | Rubric changes in `judge-core.mjs`, U scorer, 1B arm config; check = re-score the v0.1 dev set end to end | ~4 h agent |
| 10-21 | R generation: 120 web calls, about 2 h. App on phone: 120 × 2 seeds × ~31 s p50 ≈ 2.5 h with packet capture. 1B arm on desktop ≈ 1 h | [usage detail removed] only |
| 10-22 | Judging: (2 app + R + 1B) × 120 = 480 answers × 2 families ≈ 960 absolute calls plus 480 pairwise calls; Opus at N = 4 shards ≈ 4 h; non-Claude family via r4to's Codex | No paid API |
| 10-22 | Human calibration: 40 items × 2 raters | ~3 h |
| 10-23 | Report: verdict band, secondaries, gates, judge kit README | ~3 h |

Metric of done: the verdict band, all §5 numbers and all §7 gates are published for one tagged APK, and a third party reproduces U on the dev set with one command.

## 10. Risks

- **Item-writing capacity.** v0.3 was dropped on 10-18 for lack of writer time. Mitigation: 60-item minimum, plus the judge kit so contributors can add their own questions.
- **Judge family offset (~0.10).** Mitigated by the lower-of-two rule and the human calibration with PPI.
- **R is not "internet".** If web-on and web-off R score the same (the old anchor was 1.029), the uncapped, sources-kept R plus the time-sensitive items should widen the gap. Report U against both R variants.
- **Native app scores below the engine** (−0.089 on v0.1). This is the honest number, and it is the one the bounty judges.
- **The phone speed bands may read as failure**, because the post author's quoted numbers are for a laptop. We report them anyway; leaving them out would itself be a misreading of S3 and V2.
- **The X posts may have changed, or replies may clarify the bar.** Re-verify before publishing, and version the ruler.
- **Overclaiming the post author's view.** The ruler is ours. It must never say he endorsed it (B31:15).

## UNKNOWN
- The live wording of V1–V3. It was read through a mirror and needs re-checking.
- Whether "within a few minutes" excludes the asset download.
- Whether UI/UX counts. Comment 1230 on the poidh page is unanswered.
- Public URLs for the other V-exact queries (Japan, PQ signatures, Mozi, Gríma, Paris–Rome). Only the vegan and Paris–Rome quotes are sourced here. Until URLs are found, the others must not be called "the post author's queries".
- r4to's available hours for writing items between 10-20 and 10-21. This decides between 120 and 60 items.
- The deadline: the public text says "October 31st, 2026"; local memory says 10-25. The 10-23 date assumes the earlier one.

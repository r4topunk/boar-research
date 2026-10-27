# The ruler (robust design): a floor-free utility ratio vs internet + frontier, judged by more than one model family

Sources: `B31` = `<workspace>/BOUNTY_31.md` (matches the poidh JSON at https://poidh.xyz/mainnet/bounty/31/data, checked 2026-10-19). V1 = https://x.com/VitalikButerin/status/2100695863026954698. V2 = https://x.com/VitalikButerin/status/2103762130554204651. V3 = https://x.com/VitalikButerin/status/2106537633056969024. Blog = https://vitalik.eth.limo/general/2026/04/02/secure_llms.html. The X posts were read through the fxtwitter mirror, so their exact wording needs one more check before publishing.

## 1. Purpose

> The ruler measures whether an offline Android app is "a useful, fully offline research tool that's >50% as good as internet + frontier models" (B31, Winner).

It answers one question with one pre-registered number: **how much of the useful content in a frontier-model-with-web answer the offline app delivers, on a question mix drawn from the bounty's own words.** Speed, offline operation and install are measured separately as gates and axes. They are never folded into that number. The ruler predicts the post author's holistic judgment (B31: "If the post author publicly confirms…"). It does not replace it, and it never implies that he endorses it (B31: "He is not affiliated with it or involved in judging unless he chooses to weigh in").

## 2. Bounty clause → what is measured → how

| Clause (exact text) | Measured | How |
|---|---|---|
| ">50% as good as internet + frontier models" (B31 Winner; V1 "internet + frontier models") | **U-ratio** (primary, §5) | Per-item rubric utility, app vs a frozen frontier+web reference |
| "a useful … research tool"; V1 "it's utility" | Task-success ratio (co-reported) | Binary "a casual user could act on this" label per answer |
| "beyond simple factual recall, including explanation, comparison, synthesis, and reasoning" (B31 Req.) | Stratum scores E/C/S/R | Fixed strata, each reported separately |
| V2 "look up any facts about the world that you care about" | Lookup stratum L | Fact items with verified key facts |
| "People travel with their phones into offline situations" (B31); V2 "weakest at specialized travel-related queries" | Travel stratum T + venue stratum V | V items reproduce V2 "Tell me the best vegan restaurants in [city I am currently in]", with device location given to both sides |
| "include ones a 1B model would fail on" (B31 Proof) | 1B arm + "1B-fail" tag | A 1B model runs on every item. Items where it scores u < 0.25 and the app scores u ≥ 0.5 get the tag |
| "respond at speeds that feel usable for real lookups on a phone" (B31 Req.) | Latency axis (not a gate) | On-phone TTFT, time to full answer and decode tok/s at p50/p90, shown against the post author's public numbers (§6) |
| "work completely offline once installed" / "make no … network requests during use" | Offline gate | Manifest has no `INTERNET` permission, plus a full run in airplane mode with traffic counters at 0 bytes |
| "not require Google Play Services" | Gate | `aapt dump permissions` / dependency scan finds no `com.google.android.gms` |
| "maximum 12GB RAM environment" / "no more than 50GB total" | Gates | Device total RAM ≤ 12 GB; installed bytes (`du`) ≤ 50 GB |
| "get the app running locally within a few minutes" (B31 Real-device) | Install time (setup, **not** answer latency) | A stopwatch from a fresh clone to the first answer, logged as two numbers: asset download and setup |
| "run on Android and compatible GrapheneOS hardware" | Gate | Run on GrapheneOS if a device is available; otherwise marked "unverified" |
| "materially different from the version reviewed" | Provenance | The scored build is the tagged release commit plus APK sha256 |

Readings we chose ourselves and label as ours: English only (the bounty says nothing about language), uniform item weights, and a 0.50 cut on the U-ratio.

## 3. Item set ("v1.0")

**Size:** 120 items. A 40-item **public dev split** is published on day 0. An 80-item **held-out split** is hashed (sha256) before any system sees it and published in plaintext after the final run. The minimum fallback is 60 held-out items; the CI then widens to about ±0.08.

| Stratum | n | Anchor | Notes |
|---|---|---|---|
| L Lookup | 20 | V2 "any facts about the world" | Single facts, not trivia hunts |
| E Explanation | 14 | B31 Req. | "How/why does X work" |
| C Comparison | 14 | B31 Req. | Two or more entities, trade-offs |
| S Synthesis | 14 | B31 Req. | Two or more sources needed (FRAMES-style) |
| R Reasoning | 14 | B31 Req.; Blog Paris–Rome walking distance | Includes travel arithmetic |
| T Travel / on the road | 14 | B31 travel framing; V2 | Visas, transport, customs, health abroad |
| V Current-city venues | 10 | V2 eval, verbatim template | City given as "(The user's phone is in <city>.)" to **both** sides |
| F Fresh / changing facts | 8 | "internet search" | Facts that change within about a year. Reported with and without this stratum |
| G Guardrail (false premise, unanswerable, dangerous) | 12 | Not in B31 | **Excluded from the U-ratio.** Feeds the confident-error rate only |

The 11 V-exact items (the post author's verbatim queries, already public) sit inside the dev split as anchors.

**Geography:** at least 40 % of T/V/L items are centred outside Europe and North America. Cities are chosen before any system runs.

**Who writes the items (this breaks the Claude loop):**
1. r4to drafts item seeds from the stratum definitions. Two non-Claude families (OpenAI in the ChatGPT web UI or Codex, and Gemini in its web UI) each expand half of the slots, using a published writer prompt. No Claude model touches item text, key facts or rubrics. This is consistent with the existing rule "never Claude-written claim items".
2. Every item carries:
   - 3–7 **key facts or must-include points**, each with a source URL and a weight (1–3);
   - 0–3 **must-not points** (a known wrong answer, a dangerous claim) with negative weights;
   - for F items, the as-of date;
   - for V items, an OSM-verified venue list as gold, plus "any real, open, on-topic venue counts".
3. r4to checks every key fact by hand against its URL. He also confirms that each item is not answerable by name-dropping alone.
4. Nothing is filtered on any system's failures, ours or the reference's. This avoids adversarial tilt.
5. The item file sha, the writer prompts and the writing log (who wrote which slot) are committed before generation.

**Reference answers ("internet search + frontier AI models", taken literally):**
- **R-main:** Claude Opus 5.5 with WebSearch and WebFetch (`claude -p`). This matches the convention every rival uses (#134, #137, #125), so numbers are comparable across entries.
- The reference prompt is a natural phone-user prompt with **no 250-word cap** (the old cap shortchanged "internet"). It must cite its sources. It runs once, on a fixed date, and both answers and URLs are archived.
- **Reference sanity check:** r4to scores each reference against the key facts. Where the reference is wrong, the item is still scored against the key facts and flagged. It is never dropped silently.
- **Option R-dual:** a second frontier family with web search, scored separately. The ratio is then reported against the per-item better reference, as a conservative "frontier models" (plural) reading. Run it only if a non-paid search-capable path exists.
- **Web-validity diagnostic:** an Opus *no-web* arm. On L/T/V/F the web reference must beat no-web, with a CI that excludes 0. Otherwise the items are not testing "internet" (this is the old anchor flaw, where no-web scored 1.029 of web).

## 4. Judging

**Unit:** each answer is scored **absolutely and independently** against the item's checklist. The judge sees one answer at a time, with system identity blinded.

Blinding strips `<think>` blocks, Sources sections, links, `[n]` markers and model self-names. It also caps both sides at 500 words, and the truncation rate is logged per arm.

The judge rates every key fact as {present, partial, absent, contradicted} and every must-not point as {triggered, not triggered}. It then gives:
- `actionable` ∈ {yes, no}: "could a casual user act on this answer without looking anything else up?"
- `confident_error` ∈ {yes, no}: a contradicted key fact or a triggered must-not, stated without hedging.

**Item utility (floor-free by construction):**
`u = clip( Σ w·credit(present=1, partial=0.5) − Σ w_neg·triggered − 1[contradicted]·w , 0 , Σ w_pos ) / Σ w_pos`

An empty answer, an "I don't know", or generic filler scores **0**, so there is no rubric floor to subtract. Honest abstention is credited only on G items, where it is the gold behaviour.

**Judge families:**
- J1 = Claude Opus 5.5 (`claude -p`, pinned CLI version and model id).
- J2 = OpenAI via Codex CLI (the path XFAM already used), on r4to's [usage detail removed].
- J3 = local Gemma 4 26B, diagnostic only (κ was too low in JUDGE2).

**Headline = the stricter of J1 and J2**, chosen per pre-registration. J1 shares a family with R-main, which can only bias it in the reference's favour, so this choice is conservative for us. Self-preference toward the reference is quantified as J1−J2 on the reference's own utility.

**Pairwise (secondary):** judge.v1 pairwise, app vs reference, both A/B orders. A disagreement between orders counts as a tie. This gives the win/tie rate, kept for continuity and because the blog's own method is pairwise: "I fed both outputs into an LLM to ask which is better".

**Human spot check (calibration, not anecdote):**
- r4to labels a **stratified random 40 items × 2 answers**, blind, using the same checklist sheet (about 3 h).
- Prediction-powered inference (Angelopoulos 2023, arXiv 2301.09633) corrects the J1/J2 U-ratio with those labels. Report the PPI-corrected ratio with its CI, plus κ and Spearman (human vs each judge) per stratum.
- If a second human is available, run 15 overlapping items to get a human-human κ.

## 5. Metrics and thresholds

**Primary (pre-registered, sha256 before generation):**
`U-ratio = Σ_items u(app) / Σ_items u(ref)`, over strata L–F (108 items held out pro rata). The app is the **submitted native Android app on a real phone**. Pooled over 2 generation seeds, it is scored by both judge families, and the headline is the lower of the two.

**Verdict ladder (exact wording in the report):**
- **MEETS** if the lower 95 % CI bound > 0.50 under the headline judge **and** the PPI-corrected point estimate > 0.50.
- **POINT ABOVE, NOT SHOWN** if the point estimate > 0.50 but the CI straddles 0.50.
- **BELOW** if the upper bound < 0.50.

**Secondary (always printed, never gating):**
1. Task-success ratio = Σ actionable(app) / Σ actionable(ref).
2. Win / tie / loss vs the reference (pairwise, both orders).
3. Confident-error rate per arm, on all 120 items, with G separate.
4. Per-stratum U-ratio, with the V stratum on its own line ("the post author's own eval").
5. A travel-weighted U-ratio (T and V ×2) as a sensitivity to the post author's stated use.
6. U-ratio with and without F.
7. The legacy judge.v1 raw and floor-adjusted ratios, as a bridge to every past number and to rivals.
8. **Separability:** decline-arm ≈ 0 < 1B < app < ref, with non-overlapping CIs. This checks that the ruler can tell systems apart at all.
9. Count of 1B-fail-tagged items, with three example triples for the demo.

**Statistics:** paired, stratified bootstrap over items, with generation seeds nested inside items; 2,000 resamples, seed 11. Judge variance is reported from J1 test-retest. Ratios are computed per resample (as a ratio of sums), not as an average of per-item ratios.

**Rules:**
- No tuning on held-out items.
- One full spend per arm; each spend is logged in EXPOSURES.
- A one-seed delta below 0.05 is reported as noise (SEEDVAR).

## 6. Speed, offline and install (separate axes)

**Latency.** The native app runs on the POCO X6 Pro (10.7 GiB, a 12 GB-class device), the full held-out set, airplane mode. Reported per tier: TTFT p50/p90, time to complete answer p50/p90, decode tok/s and peak PSS. They are shown against the post author's public bands, with the source of each:

| Band | Exact public text |
|---|---|
| Failure baseline | V1 "like 10 TPS with 1B models" |
| Too slow for comfort | V3 "still too slow for comfort. It's comfortably running at 20-30 TPS" |
| Minimum on a laptop | Blog "anything slower than 50 tok/sec feels too annoying" |
| Feels fast | V3 "would only really start to feel fast at 100+" |

These are his laptop and desktop numbers. The report says so and does not present them as a phone threshold.

**Gates (pass/fail table):**
- no INTERNET permission, and 0 bytes measured during the run;
- no GMS dependency;
- installed size ≤ 50 GB;
- device RAM ≤ 12 GB;
- fresh-install stopwatch by someone other than the author, with download and setup reported separately;
- GrapheneOS: verified or "unverified".

## 7. Reproducibility by a third party in under an hour

The public repo holds the dev items, the frozen reference answers and URLs, the frozen app answers and phone traces, the judge prompts and their sha256 hashes, and `rejudge.mjs`.

**Path A (about 25 min):**
1. `pnpm i`
2. `node rejudge.mjs --judge <their CLI> --shards 4`, which re-scores the frozen answers (about 600 absolute calls at the 120 × 5 arms scale, with N=4 shards).
3. Bootstrap and print the report.

**Path B (about 40 min, adds generation):** regenerate the app's desktop answers with the published engine and the GGUF download.

Held-out plaintext is published after the final run, so anyone can recompute every number exactly.

## 8. Keep vs change from the current bench

| Keep | Change |
|---|---|
| Both-order pairwise judge.v1, now as a secondary metric | Primary moves from a 1–5 ratio with a floor to a floor-free checklist utility (u=0 for useless) |
| Blinding, provenance rows, stale-row refusal | Claude-written items replaced by human plus 2 non-Claude families, with human fact-check |
| Stratified bootstrap, seed 11, 2 seeds | A single Claude judge replaced by 2 families, headline = stricter; PPI human correction |
| OSM venue gold, VENUEGPS location suffix | Venue items move into the main ratio (V stratum), with location given to both sides |
| V-exact verbatim queries (dev anchors) | Reference cap of 250 words removed; web-validity diagnostic added |
| v0.1/v0.2/V-para as **dev history** | Freshness stratum F added (previously excluded by design) |
| Device-X6 measurement method | The scored system is the **native app on the phone**, not the TypeScript engine |
| Pre-registration via sha256, the EXPOSURES ledger | Install stopwatch and gates table added; English-only stated as our choice |

## 9. Cost and timeline to 2026-10-23 (internal; public decision date is "October 31st, 2026", B31)

| Day | Work | Cost |
|---|---|---|
| 10-19 | Freeze this spec, write the checklist schema, hash it; writer prompts out | 0 |
| 10-20 | 120 items drafted (r4to + ChatGPT/Gemini web UIs) | r4to about 6 h |
| 10-21 | Human key-fact check, split, hash; R-main references (120 `claude -p` web calls, about 2 h); 1B arm and no-web arm | r4to about 4 h |
| 10-22 | App: desktop 2 seeds (about 40 min); **native app on phone, 108+12 items, about 1.5 h**; deep tier desktop 2 seeds (about 5 h, secondary); judging J1 + J2, about 1,450 calls per family, sharded (about 4–5 h wall) | no paid API |
| 10-23 | Human 40-item spot check (3 h), PPI, report, public repo staging (push only with r4to's OK) | r4to about 3 h |

The critical path is r4to's roughly 13 hours of human work. If that slips, fall back to the 60-item held-out set and say so.

## 10. Risks

1. **Item writing slips.** This reverses D5 (10-18, v0.3 dropped), which needs r4to's decision. Mitigation: 60-item fallback; the dev split ships first.
2. **The reference is Claude**, so J1 self-preference deflates us. This is conservative. J2 quantifies it.
3. **Codex or Gemini access changes or needs payment.** Then J2 = local Gemma (weak κ), and the report states that only one strong family judged.
4. **Fresh items punish offline systems by design.** The ratio is reported with and without F, and the headline excludes nothing silently.
5. **The phone run exposes the native-app gap (−0.089 on v0.1).** We report it. The number is the submission's number.
6. **The checklist misses valid alternative answers.** The judge may mark "other correct content". The human spot check measures how often this happens.
7. **The 500-word cap truncates the reference.** The truncation rate is logged; sensitivity without the cap is reported.
8. **the post author's private criteria are unknown.** The ruler is a predictor, and the report says so.

## Decisions / Options / Tasks
- **Decisions:**
  - primary = floor-free U-ratio on the native app on the phone, stricter of two judge families, lower CI bound > 0.50;
  - items written outside Claude with human fact-check;
  - win/tie and the legacy ratios are secondary;
  - latency and install are separate axes.
- **Options:** R-dual reference; travel-weighted headline; J3 as a third juror; second human labeller.
- **Tasks:** T1 freeze spec and hashes; T2 write and check items; T3 references plus arms; T4 phone run; T5 J1/J2 judging; T6 human 40 plus PPI; T7 report plus repo.

## UNKNOWN
- The live wording of V1/V2/V3 (read via a mirror) and the post author's in-thread replies.
- Whether Codex has web search (needed for R-dual) and whether it stays free.
- Whether "few minutes" excludes the asset download; whether UI/UX counts (poidh comment 1230 is unanswered).
- GrapheneOS device availability.
- Whether r4to accepts reversing D5 and the 13 hours of human work.

# BENCH-RULER 2026-10-19: the public ruler for bounty #31 (synthesis)

Inputs: workflow boar-bench-ruler (3 readers, 3 designs, 2 adversarial critics; all in `bench-ruler-2026-10-19/`). Public sources only; no blind/ or veil reads; no private chat. Every bounty quote below is from BOUNTY_31.md (= the live poidh page, checked 2026-10-19) unless a URL is given.

## TL;DR
1. There is no official measuring stick; the ruler we propose is part of the submission's value. Both critics, independently, pick the same base: the **robust** design (true-zero utility, held-out hashed items written outside the judge family, the submitted app scored on a phone), plus **traceable**'s source register and bring-your-own-questions kit, plus **judge-eye**'s speed reading and confident-error rate.
2. Headline = **U, a floor-free utility ratio** (useless / generic / "I don't know" = 0), co-reported with a **binary task-success ratio** ("a casual user could act on this"). Raw ratio, floor-adjusted and W/T/L stay in the row, never hidden. Text support: "a **useful** … research tool" (B31:60), V1 "it's utility" (https://x.com/VitalikButerin/status/2100695863026954698).
3. Five things in our current bench misread or under-read the bounty and must change: (a) the reference is capped at 250 words (reference.v1), the bounty says "internet search + frontier AI models", uncapped; (b) items are Claude-written and Claude-judged; (c) we score the desktop engine, not the submitted app on a phone; (d) speed, offline and install are outside the scored protocol; (e) the venue/current-city eval (the post author's only stated eval, V2) sits outside the headline and "best" is scored by OSM tag presence.
4. Our current numbers stay valid as dev evidence; they are not the ruler's headline.
5. Feasibility by 10-23: the spec, the kit and a gates table are cheap; the critical path is a fresh item set written outside the Claude family with human fact-check (v0.3 was dropped on 10-18 and must be revived in a reduced form) and running it on the phone.

## 1. What the text asks (clause → type → how the ruler tests it)
| Clause (quote) | Type | Ruler element |
|---|---|---|
| "casual info lookup and research tool … >50% as good as internet search + frontier AI models" (B31:7) | judged | U and task-success ratio vs a frontier+web reference, verdict bands (below / point above 0.50 / CI-low above 0.50) |
| "People travel with their phones into offline situations all the time" (B31:7) | context → judged | travel stratum incl. current-city queries with device location, inside the headline |
| "~10 tokens/sec from 1B models that break on anything interesting" (B31:9) | context | 1B no-RAG baseline arm; speed anchor 10 tok/s |
| "~100B params … one promising direction, not a requirement" | none | architecture is not scored |
| "run on Android and compatible GrapheneOS hardware"; "maximum 12GB RAM"; "no more than 50GB total"; "completely offline once installed"; "no API calls … or other network requests"; "not require Google Play Services" (B31:21-26) | must | gates table (pass/fail, measured, GrapheneOS marked verified or UNVERIFIED) |
| "beyond simple factual recall, including explanation, comparison, synthesis, and reasoning" (B31:27) | must/judged | strata: lookup, explanation, comparison, synthesis, reasoning, travel; per-stratum results with CIs |
| "respond at speeds that feel usable for real lookups on a phone" (B31:28) | must/judged | speed verdict on the same config as U: time to first useful content and to complete answer, p50/p90, decode tok/s, named phone ≤ 12 GB |
| "get the app running locally within a few minutes" (B31:41) | must | install stopwatch by a third party with the README only, with and without asset download, never shown as answer latency |
| "include ones a 1B model would fail on" (B31:50) | proof | items where the 1B arm fails, listed |
| "materially different from the version reviewed" / "functional submitted version" (B31:56,69) | must | scored system = submitted APK by sha256 + git tag |
| "judged against the requirements above and the bar described in the post author's post" (B31:60) | judged | every ruler element cites a quote or is labelled "our choice" |
| "not affiliated … unless he chooses to weigh in" (B31:15); confirmation clause (B31:62) | framing | the ruler states it is ours, not endorsed, a predictor of his confirmation |
| V2 "my eval is 'Tell me the best vegan restaurants in [city I am currently in]'" (https://x.com/VitalikButerin/status/2103762130554204651) | his own test | current-city stratum, human-verified venues (exists, vegan, in the city) |
| Blog: "anything slower than 50 tok/sec feels too annoying" (https://vitalik.eth.limo/general/2026/04/02/secure_llms.html) | context | speed bands shown as labelled context (laptop quote, not a phone requirement) |

Interpretation of ">50% as good" (map-bounty31 §4): I4 utility ratio best supported; I2 floor-adjusted is its scalar form; I3 win-rate is the post author's personal method (blog) but not the threshold wording and makes the bar unreachable for every entry; I6 his holistic judgment is the real decider, which the ruler only predicts.

## 2. Decisions (fixed by the text; recommended)
- R-D1 Headline U (true zero) + task-success ratio; raw, floor-adjusted, W/T/L and confident-error rate in the same row; judge family named next to every ratio; min over two judge families for the verdict.
- R-D2 Reference = frontier model + live web, no length cap at generation or judging, sources kept, frozen and archived; two families reported, never best-of-two per item. reference.v1's 250-word cap is retired for the ruler.
- R-D3 Items written outside the judge/reference family with human fact-check, hashed before any run, not filtered on any system's failures; drafted and rejected items published.
- R-D4 Strata: lookup, explanation, comparison, synthesis, reasoning, travel (incl. current-city), weights stated; time-sensitive items kept in the headline and also reported without them (fidelity to "internet search"; note: our packs deprioritise current events, the ruler does not hide them).
- R-D5 Scored system = submitted native APK on a named ≤ 12 GB phone in airplane mode; desktop engine numbers are labelled dev/parity evidence.
- R-D6 Gates table + install stopwatch + speed verdict, all pre-registered.
- R-D7 Arms: decline (validates the zero), 1B no-RAG, our app, reference; separability reported.
- R-D8 Public, timestamped pre-registration (spec + item-set sha + APK sha) with a conflict-of-interest line; entrant-agnostic kit (question → answer + timing interface; rivals can run it, traces shareable).
- R-D9 Language scope: the bounty never says "English only"; our English scope is labelled "our choice".

## 3. Options (r4to chooses)
- O1 Item writers: (a) r4to + one non-Claude web-UI model, human fact-check, ~60 items (reduced v0.3); (b) the same plus a second human outside the team; (c) keep V-exact (11, the post author's verbatim) as the only fully external anchor and publish the rest as dev.
- O2 Second judge/reference family: Codex (already used in XFAM, r4to runs it) vs a Gemini web UI.
- O3 How to score the native app on the phone: (a) a scripted runner in the native app (needs the app maintainer); (b) bench app on the phone for all items + native app on a parity subset; (c) desktop engine headline with phone parity (weakest; contradicts R-D5).
- O4 Venue "best": human check by r4to (cost ~1 h for 10 items) vs open-web verification by an agent with human spot check.

## 4. Tasks (minimum that closes the loop by 10-23)
| # | Task | Owner | Needs |
|---|---|---|---|
| T1 | Ruler spec v1 (this table + metric definitions + gates + speed protocol), sha256, private first | coordinator | none |
| T2 | Judge prompt v2: absolute utility checklist with true zero + task-success yes/no, citation normalisation for both arms, length logged | coordinator + independent Opus review | none |
| T3 | Reference v2 prompt (uncapped, sources kept), run on two families for the set | coordinator (Claude) + r4to (second family) | O2 |
| T4 | Item set v0.4 (~60, strata as R-D4) | r4to + non-Claude model | O1 |
| T5 | Phone run of the scored system + speed + gates (Pixel 8 from 10-20) | r4to with the Pixel kit | O3 |
| T6 | 1B no-RAG and decline arms | coordinator (mini) | T4 |
| T7 | Kit for others (runner interface, frozen dev items, judge, rejudge) | coordinator | T1–T3 |
| T8 | Publish pre-registration + kit (public, r4to OK) | r4to | all |

## UNKNOWN
- the post author's in-thread replies (x.com returned 402; mirror read only the posts).
- Whether "within a few minutes" excludes the asset download.
- Whether the judges will read a quantitative ruler or only use the app (the ruler predicts I6, it cannot replace it).
- Whether the native app can be driven by a script (O3a).
- Live poidh shows 7 claims (#134, #137, #142 not in CLAIMS_31.md) and decision date "October 31st, 2026"; the earlier deadline we work to comes from a non-public source and must not appear in the ruler.

## Sources
bench-ruler-2026-10-19/: map-current-benchmark-map-and-flaws.md, map-bounty31-ground-truth-2026-10-19.md, map-methods-survey-x-percent-benchmark.md, design-{traceable,judge-eye,robust}.md, critic-{misread,gameable}.md.

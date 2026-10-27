# Item blueprint v0.4 (draft for r4to's direction OK): what questions the ruler asks and why

Companion to BENCH-RULER-2026-10-19.md. Public sources only. Every rule cites the bounty (B31 = BOUNTY_31.md = live poidh text) or is labelled "our choice".

## Revision r2 (2026-10-20, after checking V2 against r4to's question): supersedes §1 quotas and §5 examples
the post author's own test questions (V2 https://x.com/VitalikButerin/status/2103762130554204651 screenshots; Farcaster 2026-09-02; secure_llms blog): "Tell me about Japan", "Which signature algorithms are quantum resistant?", "Explain Mozi's views on universal love.", "Tell me the best vegan restaurants in [city I am currently in]", "Why does Gríma kill Saruman in The Lord of the Rings?" (over-refusal case), Paris–Rome walking distance (arithmetic error case). His verdict in V2: "much slower and less effective at difficult questions"; "weakest at specialized travel-related queries".
Changes:
- Topic families come from his queries: place overview; technical research (cryptography, Ethereum, CS, mechanism design/economics); humanities (philosophy, history, literature/fiction); science and everyday health; travel (current place + travel arithmetic/logistics). Travel ~1/3 of items (not ≥ 50 %): travel is the offline situation, not the topic of every question.
- The bounty's task types (lookup, explanation, comparison, synthesis, reasoning) cross the families; most items are "difficult" (1B-fail candidates).
- Wording: short and direct like his ("Tell me about…", "Explain…", "Which…"), with some casual phrasing.
- Add over-refusal probes (benign questions a timid app refuses, e.g. fiction violence).
- Multi-turn reduced to 8 conversations, reported separately as well as inside U (our choice; no public signal that he uses follow-ups).
- "Best" venue items checked on the open web (exists, matches the diet/attribute, in the city), not by OSM tags alone.
- V-para already followed this family structure; what changes is who writes (Codex + Claude, cross-critique) and the metric.

## TL;DR (r1)
- The user we simulate: a curious person, phone in airplane mode or on a trip with no signal, asking casual and research questions in loose English (B31:7 "casual info lookup and research tool"; "People travel with their phones into offline situations").
- 72 items: 60 single-turn + 12 multi-turn conversations (2–4 turns). Six strata, each with an explicit quota; at least half of the items set in a travel or offline situation.
- Writers: Codex and Claude each draft half, blind to our packs; each family critiques the other's items; references by both families with live web; judged by both families; every number reported per writer family so family bias is visible.

## 1. Strata and quotas
| Stratum | n | Clause | What a good item looks like |
|---|---|---|---|
| Lookup (facts) | 12 | B31:7 "info lookup"; V2 "comfortably look up any facts" | a fact a traveller or curious reader needs now; one clear checkable answer |
| Explanation | 12 | B31:27 "explanation" | "how/why does X work", answerable in 150–300 words, needs real background |
| Comparison | 10 | B31:27 "comparison" | two or three things compared on stated criteria; not two infobox numbers |
| Synthesis | 10 | B31:27 "synthesis" | combine several facts or sources into a plan, summary or recommendation |
| Reasoning | 10 | B31:27 "reasoning" | multi-step: arithmetic with real-world data (time zones, budgets, distances), cause and effect, trade-offs |
| Travel / current place | 6 | B31:7 travel; V2 "best vegan restaurants in [city I am currently in]" | asks about where the user is now; device location supplied to both systems |
| Multi-turn | 12 conversations | our choice (a research tool is used with follow-ups) | see §3 |

Cross-cutting tags (each item gets them; none is a quota except the first):
- **situation**: travel / offline-situation / at home (target ≥ 50 % travel or offline) — B31:7.
- **1B-fail candidate**: needs several steps or real background (B31:50 "ones a 1B model would fail on"; B31:9 "break on anything interesting").
- **time-sensitive**: the answer could change after a knowledge snapshot; kept, reported with and without (BENCH-RULER R-D4).
- **region**: ≥ 40 % outside Europe and North America (our choice; travel is global).
- **health/safety**: ordinary practical health questions allowed (altitude, food, sun); no acute emergency scenarios in the scored set (our choice; emergency handling is reported separately and the app ships with a warning).

## 2. Writing rules
1. Writers never see our pack list, kit, traces or scores (anti-self-serving; critic-gameable).
2. Loose, casual wording is allowed and expected (typos, vague phrasing, implied context), at the rate a real user would produce.
3. Each item carries: question text (or turns), stratum, tags, and a 3–5 point "what a useful answer must contain" checklist written by the writer and later verified on the open web.
4. No item may be filtered or rewritten because any system fails it; every drafted and rejected item is kept with the reason (critic-gameable).
5. No questions whose correct answer is unknowable or purely opinion; "best" questions must have a checkable basis (ratings, guides, existence).
6. English only, labelled "our choice" (the bounty does not say English only).

## 3. Multi-turn conversations (12)
Why: "research" implies follow-ups; a casual user rarely asks one perfect question (our choice, B31:7 "research tool").
Shapes (2 each):
- drill-down: broad question → "tell me more about the second one";
- comparison follow-up: answer → "how does that compare with Y";
- correction: user states a wrong premise in turn 2 ("so it's in the north, right?") and the app must correct it;
- context carry: turn 2 depends on turn 1 without restating it ("and how long does it take to get there");
- constraint change: "ok but I only have 2 days and 100 euros";
- recall: turn 3 asks about something said in turn 1.
Scoring: every turn judged with the earlier turns visible; the item score is the mean over turns plus a consistency check (contradicts an earlier turn = flagged).

## 4. Pipeline (who does what)
1. Codex drafts 36 items (half of each quota), Claude drafts 36, both from this blueprint only.
2. Cross-critique: each family reviews the other's drafts against the blueprint and the bounty clauses (fit, ambiguity, checkability, hidden bias); fixes or rejects with reasons.
3. Fact-check: the checklist of each item is verified on the open web by both families; disagreements go to r4to (expected ≤ 10 items, minutes each).
4. Freeze: set hashed (sha256) before any system answers it.
5. References: frontier + live web, uncapped, one per family.
6. Judging: both families; headline = min over families; per writer family breakdown reported.

## 5. Example items (illustrative, to show direction; not in the final set)
| Stratum | Example |
|---|---|
| Lookup | "landing in tbilisi tonight, what currency do they use and can i pay card in taxis" |
| Explanation | "why do my ears hurt more on the way down when flying" |
| Comparison | "trains vs night bus from bangkok to chiang mai, which is better for someone on a budget who wants to sleep" |
| Synthesis | "i have one free day in kyoto in november, what should i prioritise if i like gardens and hate crowds" |
| Reasoning | "my flight leaves lisbon 14:05 and lands in são paulo 21:40 local, how long is the flight actually" |
| Travel / current place | "(device in Oaxaca) any good vegetarian places near me that are open late" |
| Multi-turn (correction) | T1 "what's the best time of year to visit patagonia" → T2 "ok so july then since it's summer there?" (must correct: July is winter) |
| Multi-turn (context carry) | T1 "how do i get from the airport to the old town in porto" → T2 "and how much would that cost for two people" |

## UNKNOWN
- Whether judges weight multi-turn at all; we include it at 12/72 and report it separately as well as inside U.
- Whether Codex drafting quality matches Claude's; the per-writer breakdown will show it.

# RESEARCH-PAGE-DRAFTS 2026-10-21: five page-ready sections from today's closed lines (for the 10-25 page)

TL;DR: page text in the outline's voice (RESEARCH-PAGE-OUTLINE-2026-10-21 §0 rules). 0 LLM calls were made to write it; every number is copied from the arm file named in each section's "Sources" line. Device timings marked "projection, device run pending" come from replays of existing Pixel 8a traces; the E1-PAR device run has not happened (QUEUE 14:57). Writer: keep the labels in each sentence when cutting; an independent Opus review is still required before publication.

> **Scope box (B1-B4 page fixes, 2026-10-21).** Which system each section's numbers describe:
> §1: the submitted native Kotlin app (maintainer's eval exports, POCO X6 Pro / POCO F3) leads; the TypeScript bench engine (BOAR Bench app, Pixel 8a) follows under its own labelled sub-heading. Pixel 8a native: RC1 (10-21) ships only Qwen2.5-1.5B, Detailed default; one 9-question speed check, warm-up excluded (internal); shipped-configuration quality measured (A1, internal until r4to's word): U 0.14 (0.10-0.19), raw 0.32, win 0/51, 2.0 correct / 68.6 CE per 100, Opus + DECLINE2STAGE, 51 v0.1 dev, one run, 0.12 below the same 1.5B closed-book in our engine on desktop (0.261, Opus; not a proxy for the app); 4B RC row pending 10-22, 1.7B arm closed (not in RC1).
[private correspondence with the app maintainer, or a result of a run on his device, removed]
> §5: our engine (tree be-cut7-warn or the bench app); the submitted app's chat did not run the health path or the deterministic layers as of 10-17 (QUEUE l.1295); RC rows pending 10-22. Health and safety counts are AI-reviewed, not clinically reviewed.

Scope line for the top of these sections: "Except the native rows that open §1, all numbers below describe our TypeScript answer engine, on desktop and through the BOAR Bench measurement app on a Pixel 8a. The submitted app is the app maintainer's native Android app, which ports our retrieval and prompts but, as of 10-17, not the health path or the deterministic layers; apart from those native rows, nothing here is a measurement of it. Health answers and first-aid cards are AI-reviewed, not clinically reviewed."

---

## 1. Where answer time goes: the submitted native app vs our bench engine

**The app maintainer's native Kotlin app (pre-release eval exports 10-14…10-20, not RC1; 0 LLM, NATIVE-PARTIME §1).** On every pre-release native run we hold (all but the 10-19 35B run had one format-1 pack, so no zstd block work), pack search (retrievalMs: query embedding + all pack and knowledge-base search + compression) is 0.6–1.6 % of an answer. The only native run on the Pixel 8a is RC1's 10-item check (10-21; 1.5B only, Detailed): retrieval fired on 1 of 9 questions (warm-up excluded; 1 of 51 in the A1 run): RC1 installs 0 packs and searches only its built-in KB (logcat "knowledge base + 0 packs"; RC1-PACKS), so it says nothing about pack-search cost. Publishing these native timings needs r4to's word (outline §0: native-app absolute numbers are internal).

| run | device | model / style | corpus | n | retrieval p50 / p90 | answer p50 / p90 | retrieval share p50 (pooled) |
|---|---|---|---|---|---|---|---|
| RC1 check, 10-21 | Pixel 8a | Qwen2.5-1.5B / Detailed (RC1 ships no other model) | built-in KB only, 0 packs (RC1-PACKS) | 9 (warmup row excluded) | used on 1/9 (0.06 s) | 25.2 / 42.9 s | n/a; generation ≈ 95 % |
| RC speed run, rc-speed9-4b and rc-speed9-17b | Pixel 8a | 4B if the RC catalog offers it / RC default (1.7B arm closed: not in RC1, runsheet row 2) | RC-default or A-union packs (record) | 9 each | **pending 10-22** | **pending 10-22** | **pending 10-22** (kill band below) |
| X6 10-14 | POCO X6 Pro | 4B / succinct | app KB + wiki-vital5 (1 pack) | 72 | 0.28 / 0.42 s | 18.9 / 37.0 s | 1.5 % (1.5 %) |
| X6 10-17 | POCO X6 Pro | 4B / succinct | same | 72 | 0.29 / 0.41 s | 18.1 / 32.7 s | 1.6 % (1.6 %) |
| X6 10-19 | POCO X6 Pro | Qwen3.6-35B / detailed | 8 packs incl. large (zstd-block) packs | 72 | 2.05 / 3.10 s | 152 / 190 s | 1.4 % (1.5 %) |
| X6 10-20 | POCO X6 Pro | MiniCPM5 2B / detailed | 1 pack | 72 | 0.30 / 0.38 s | 35.7 / 61.9 s | 0.8 % (1.0 %) |
| F3 10-19 | POCO F3 | 4B / detailed | 1 pack | 72 | 0.50 / 0.75 s | 75.1 / 118.0 s | 0.6 % (0.8 %) |
| F3 10-19, three retrieval modes | POCO F3 | 1.5B + 4B / detailed | 1 pack | 74 each | 0.50–0.56 / 0.70–0.90 s | 34.6–39.4 / 106–118 s | 1.1–1.3 % |
| F3 10-20 | POCO F3 | MiniCPM5 2B / detailed | 1 pack | 72 | 0.41 / 0.54 s | 35.3 / 54.1 s | 1.2 % (1.4 %) |

Every native answer generates; time is prefill + decode. RC1's evaluation hook ran Detailed (maxTokens 1024; 50 of 51 A1 rows; that the chat default a user sees is also Detailed is our reading of the snapshot, not of RC1, GAP-LEDGER row 2; 1.5B 376 tokens p50 at 18.6 tok/s, n 9), so on the native app answer length is the time, not search (Succinct projected ≈ −24 s p50 on the 1.7B, SUCCINCT17, device check S1b pending) (X6 4B succinct promptMs p50 6.7–7.0 s, predictedMs 10.9–12.2 s). Only the 10-19 35B run had large packs installed, and its search time is confounded by the 35B streaming experts from flash.

**Replica fidelity and what the 0.14 is made of (C2-REPLICA; Opus judge.v1 + DECLINE2STAGE, 51 v0.1 dev ids, one run each; [internal until r4to's word], native absolute).** A desktop replica of the app's default pipeline (his Kotlin engine from snapshot 5f8cc8f4 on a JVM harness, 1.5B, Detailed, KB-only) scores U 0.150 (0.112-0.192) against the phone's 0.143 (0.103-0.188): paired +0.007 (-0.025...+0.039), per-item Spearman 0.81. The 0.14 is a property of the shipped configuration, not of the Pixel, its heat or one run. On the replica, switching only the default persona from Detailed to Succinct gives 0.265 (0.189-0.347), +0.115 (+0.051...+0.181), correct +25.5 and confident errors -21.9 per 100. The Succinct arm is a replica stand-in (cross-host), not a phone run, and it scores the same as the 1.5B closed-book on our engine (0.261): with KB-only retrieval it almost never retrieves.

**Ladder for the app (Opus, same 51 dev ids, one run per rung; [internal until r4to's word] for every native absolute; not an app score).** Shipped 0.14 (measured, Pixel 8a) -> Succinct 0.27 (measured, desktop replica) -> our engine with the 1.7B (model + claim-kit packs + deterministic layers) +0.087 (+0.008...+0.167) above his Succinct (measured, Opus, our engine vs the replica; different hosts and frames; under Haiku the levels differ by only about +0.02, 0.248 vs 0.226). Inside his pipeline, swapping the 1.5B for the 1.7B alone adds +0.010 (−0.043…+0.062; Haiku, 51 v0.1 dev, one run, B2-HARNESS-17S, desktop replica). So this step is not a model effect: of the combined +0.107 (Haiku), Succinct is +0.097 -> the facts table +0.106 (+0.040...+0.183) on the shipped rows (projection from existing Opus judgments of the 8 layer answers, LAYER-SPLICE; not additive with the 1.7B step; whether RC1 itself has layers is not established (GAP-LEDGER row 5; device check H2a)).

**What a native fix would remove (PROJECTION, Pixel 8a, uncalibrated r = 2–4).** Searching the packs in parallel (one coroutine per pack, 4 lanes) projects to 0.45–1.3 s saved per search (all three pack changes together 0.5–1.7 s, about 3–9 % of a 4B native answer); a larger block cache adds 0.03–0.10 s and 16 KB blocks 0.00–0.06 s. r is the phone/MacBook speed ratio for native code, not calibrated on any Kotlin run (NATIVE-PARTIME §3).

**Pixel 8a RC row (pending 10-22; kill band frozen in hypothesis B1-TIMESTORY before the run).** Readout: arms/native-partime/tools/native_times.py on handoff/pixel8-2026-10-20/bench/results/rc-speed9-{4b,17b}/rows.jsonl, retrievalMs / totalLatencyMs p50 and pooled, n 9 each, RC sha recorded at install. If, with n ≥ 8 answered of 9 on either model, retrieval is ≥ 20 % of answer p50, the pack-search story may lead this section again, citing the native numbers; if ≤ 10 %, this rewrite stands and the bench tables below stay bench-labelled; between 10 and 20 %, both are shown side by side with no lead claim. The RC1 1.5B check is outside this frozen band (wrong model, retrieval on 1/9) and is reported descriptively only. If no RC rows exist, this section keeps the X6/F3 rows and says "not measured on the Pixel 8a".

### Bench engine (TypeScript, BOAR Bench app), not the submission

The numbers in this sub-section describe our TypeScript engine in the BOAR Bench measurement app. They do not transfer to the submitted app: there (per our read of the app maintainer's fullnative-dev snapshot, not of RC1), pack blocks are decompressed by native libzstd, and the bench's median row is a no-model decline whose time is all pack search, while every native answer generates (GOAL-2026-10-21 E1 correction).

On a Pixel 8a running Qwen3-1.7B with six persona packs (crypto, wikivoyage, factbook, firstaid, visa, medlineplus), the bench engine's median answer took 7.57 s over 73 dev questions (one run, cool phone, bench app; 4.16 s with the two-pack claim kit). Most of that median is not the model. The distribution is bimodal: 39 of the 73 questions never call the model (declines, safety and deterministic answers), yet 24 of those still search every pack. The median question is one of them: 7.3 of its 7.6 s are pack search.

**Where the bench engine's time goes (73 dev questions, one run, 0 LLM replay of the bench-app phone traces)**

| scope | n | retrieval | prefill | decode | other |
|---|---|---|---|---|---|
| all questions | 73 | 44 % | 25 % | 26 % | 5 % |
| questions that call the model | 34 | 31 % | 32 % | 33 % | 4 % |
| claim kit (2 packs), all questions | 73 | 26 % | 33 % | 34 % | 7 % |

**Bench engine: pack search is serial, and most of it is JavaScript.** The bench engine searches the packs one after another. Each pack costs 0.5–0.8 s per question at the median (visa 0.60 s, medlineplus 0.51 s, crypto 0.78 s, wikivoyage 0.81 s); a search over all six has a median of 3.95 s. Our earlier "about 0.15 s per small pack" counted only the SQL; the full window is about three times that. 73 % of a search is the block phase: about 194 compressed 64 KB blocks per question, each fetched, decompressed with fzstd (pure JavaScript) and turned into passages, at about 16 ms per block. Only 34 % of the search window is SQL; the rest runs on the single JavaScript thread.

**What each fix would remove in the bench engine (projection, bench engine; from the bench-app phone traces, device run pending)**

| change | kind | ranking identical? | projected answer p50 (73 q) |
|---|---|---|---|
| today (measured) | — | — | 7.57 s |
| search the six packs with Promise.all | engine change | yes, by construction | 5.5–6.0 s (projection, bench engine) |
| decompress off the JS thread, two lanes | engine change | yes | 4.95 s (projection, bench engine) |
| full parallel search off the JS thread | engine change | yes | 2.80 s (projection, bench engine) |
| drop visa + medlineplus, plus Promise.all | product choice + engine | yes on this set | 4.77 s (projection, bench engine) |
| pack search free (ceiling) | — | — | 0.87 s (projection, bench engine) |

Promise.all alone does not reach our 5.0 s target, because the bottleneck is JavaScript, not SQL: the SQL overlaps, the decompression does not. A Promise.all build of the bench app exists and returns the same ordered results as the serial engine on 72/72 questions; on the Pixel 8a it cut search p50 3.89 → 1.93 s and answer p50 10.32 → 7.39 s (measured, bench app, 10 items per arm, one run, cool phone; PAYS under its frozen rule; DEVICE-E1PAR).

**A bigger block cache (bench engine).** The bench engine keeps the last 16 decompressed blocks per pack. In a desktop replay of the same 73-question session (0 LLM, ordered results identical in all 22 runs), 64 slots cut decompressions by 49 % and 256 slots by 78 %, the same in three shuffled orders and on a second 97-question set. The cache is per pack, so 256 slots hold +65 MB of decompressed text; that failed the memory limit we froze before the run (32 MB), and we closed it as stated. 64 slots hold +20 MB and passed all three frozen clauses descriptively. Projected median answer time with 64 slots: 4.0–5.0 s serial, 2.5–3.2 s with Promise.all (projection, bench engine, device run pending; the range spans three assumptions about how much of a block's cost a cache hit saves). On the phone, 64 slots on top of Promise.all measured search p50 1.37 s and answer p50 5.05 s (10 items, one run). It failed two frozen clauses: the ratio (0.71 against a limit of 0.6) and PSS (+45 MB against a limit of +32 MB). We killed it as stated (DEVICE-E1PAR).

**A faster decoder (bench engine only).** WebAssembly zstd decoders were 3–4× faster than the bench engine's pure-JavaScript fzstd on 200 real pack blocks on a MacBook; the app maintainer's native code (dev-branch snapshot) already decompresses with native libzstd, so this question does not apply to it (ZSTD-BENCH; GOAL E1; the on-phone WebAssembly check was dropped, ACTIONS W44).

**What does not buy time on the phone (bench engine).** Turning off the X2b head pass saves 42 % of prompt tokens on desktop (729 → 420, 77 dev questions), but the phone engine never had it, so it saves 0 s there. Reusing the cached system-prompt prefix more saves about 0 s on single-turn questions: every phone call already reuses 244–300 cached tokens, and what remains (about 250 tokens) is the question and its sources.

Sources: arms/native-partime/NATIVE-PARTIME.md (§1 native table, §3 projection); GOAL-2026-10-21.md (E1 correction); web/ACTIONS.md W44; arms/e1-partime/PARTIME.md; DEVICE-E1PAR.md; arms/blockcache/BLOCKCACHE.md (incl. the BLOCKCACHE-64 section); arms/zstd-bench/ZSTD-BENCH.md; arms/x2b-retest/X2B-OFF-MAIN.md; arms/default-set/DEFAULT-SET.md; arms/e1-partime/DEVICE-E1PAR.md (E1-PAR run 17:0x: B pays, E kill by rule, D 5.05 s).

---

## 2. Engine rules we tested and did not adopt

Each rule below had a pass/fail criterion written and hashed before its run. The routing and KEEP-E deltas are point estimates on 1–14 changed items with no CI; read them as no measurable gain, not as small wins. All are on development questions only; judge rows are Claude Haiku 5.5-low (judge.v1, both orders) unless marked Opus, one seed unless marked.

| rule | what it changes | test (set, n, judge) | result | verdict |
|---|---|---|---|---|
| Routing P: a health word blocks the places route | 1 question ("vegetables in oil at home … food poisoning") went to the places pack | MAIN 97 replay; 1 changed item generated, Haiku | +0.001 U, 0 fixes, 0 safety probes moved | not adopted (safe, no score); kept as a UX note |
| Routing T: the learned health detector fires alone only at p ≥ 0.5 | 3 cooking items leave the health refusal | MAIN 97 replay + 64 safety probes; 3 items, Haiku | +0.004 U, 0 fixes; 2 safety probes leave the health path | not adopted (safety gate) |
| Routing H: release a detector-only health fire when no health source is found | 6 cooking/money items answered normally | same; 6 items, Haiku | +0.011 U, 1 fix; 32 of 64 safety probes leave the health path (doses, vital signs, unit conversions) | not adopted (safety gate) |
| Keep step: 21 variants (more dense picks, rescue near the cut, larger append budget, retrieval floors) | which chunks reach the prompt | 0 LLM replay, MAIN 97 + 180 self-tests | best within +15 % tokens brings the fact chunk in on 3 of 17 target items; 7/17 at +50 % tokens; 10/17 only at +129 % | closed at the replay (bar was 10/17), no judge run |
| KEEP-E: dense sources when the lexical list is empty | 14 MAIN items get 1–2 dense chunks | 14 changed items, 55 Haiku calls, Mac mini | net U −0.010; 9 worse, 3 better; warned answers 6 → 12; +118 % tokens on those items | killed |
| X2b head pass OFF (desktop) | drops appended neighbour/dense chunks | 77 live MAIN items, two seeds (135 item-seed rows), Haiku + Opus on 9 flips | dU +0.026 (−0.020…+0.073); CE-unwarned 12 → 14 | frozen verdict "OFF is safe for kit-only installs", at the edge (CEu +2 of +2 allowed); not adopted: the +2 is inside judge noise (§4) and seed 43 skipped the 19 cooking/money ids; X2b stays on |
| Default pack set | which of the six packs ship by default | 0 LLM replay, 112 items + 64 probes | see below | product choice, not a measurement verdict |

**Routing.** On MAIN 97, 25 questions leave the normal path and 7 of them are losses. Six are cooking or money questions refused with the health line because the learned health detector fired while the word list stayed silent. That same detector-only path catches 32 of our 64 safety probes ("insulin 40 units", "12 paracetamol", "pulse ox 85 %"), so loosening it is not safe. The whole routing loss is worth at most about +0.01 U on MAIN 97 (Haiku, one seed).

**Keep step.** The facts we hoped to rescue do not sit just below the cut: 7 of them sit at dense ranks 4–10, and the 600-token append budget binds before the number of picks does. Any variant that reaches them is a longer-context arm, and longer contexts have not helped the 1.7B. KEEP-E showed why the engine's "skip the append when the lexical list is empty" is a guard rather than a bug: the dense neighbours of a question the pack does not cover are near-misses, and the model answered worse with them. Two target facts reached the prompt and were still not used.

**X2b OFF.** Turning off the desktop head pass changed no measured U (+0.026, CI −0.020…+0.073, Haiku, two seeds pooled) and cut prompt tokens by 42 %. Confident errors on unwarned answers went from 12 to 14 across both seeds, exactly at the +2 allowance we froze. The second seed could not cover the cooking/money ids where the first seed's rise happened (budget cap). With the judge's own retest noise of about ±1.3 per 100 (§4), the frozen rule says "safe for kit-only installs" at the edge. We did not adopt it, because that edge is inside judge noise and the cooking/money ids where the rise sat were not retested.

**Default pack set (product choice).** All six packs, bench engine: 7.57 s measured, 5.53 s projected with Promise.all (projection, bench engine). Dropping visa saves about 1.0 s serial and moves no kept source on the phone engine (112 dev items, 64 probes), but leaves travel logistics with no pack; no visa question with a reference exists, so its value there is unmeasured, not zero. Dropping medlineplus saves about 0.9 s, loses 2 real health facts on the desktop path and changes the sources of 3 safety probes on the phone path (one seizure probe swaps a first-aid page for "Pesticide poisoning"). With search off the JavaScript thread, all six packs project to 2.80 s in the bench engine, which removes time as a reason to drop any there (projection, bench engine, device run pending); in the submitted app pack search is 0.6–1.6 % of an answer (§1), but those runs had one small pack (all but one); six packs on a Pixel 8a project to 1.0–2.0 s per search (projection, uncalibrated), and RC1 used retrieval on 1 of 9 speed-check questions and 1 of 51 in A1, so for the submitted app pack time is unmeasured.

Sources: arms/routing-r1/ROUTING.md; arms/keep-k1/KEEP.md; arms/keep-e/KEEP-E.md; arms/x2b-retest/X2B-OFF-MAIN.md (incl. addendum 1); arms/default-set/DEFAULT-SET.md; arms/web-actions/WEB-ACTIONS-B.md §2.

---

## 3. Where the 16 missing facts actually are

On MAIN 97 (dev), 16 questions are answered wrong or refused although a pack we built holds the fact. We traced each one through the engine with 0-LLM replays and named the cheapest fix class. 13 of the 16 are self-tests written from those same packs, so "a pack holds the fact" is partly true by construction.

| where the fact is lost | items | perfect fix | realistic (33 % use prior) | at the oracle rate | can it ship? |
|---|---|---|---|---|---|
| retrieval: cross-pack fusion crowding, one article filling all slots, grounding drops, paraphrase misses | 7 | +0.050 | +0.017 | +0.001 | 6 of 7 also need a pack installed; keep-side rules move ≤ 3 items within +15 % tokens |
| routing (health detector, places route) | 4 | +0.041 | +0.013 | +0.001 | no: the rules that fix them fail the safety-probe gate (§2) |
| pack build ({{convert}} values, a missing synonym) | 2 (+1 arguable) | +0.014 | +0.005 | +0.000 | yes, as rebuilds (below) |
| pack not installed | 2 | +0.014 | +0.005 | +0.000 | installing moves 27–30 other contexts and 21 safety probes |
| reading (fact absent from the passage the model got) | 1 | +0.008 | +0.003 | +0.000 | reader training only |
| all 16 | 16 | +0.128 | +0.042 | +0.002 | |

U on MAIN 97 from Haiku-judged baselines (one seed). "Realistic" multiplies the perfect fix by the share of reached facts the 1.7B actually uses on self-tests (33 %, Haiku, one run) or by the oracle rate on real dev questions (+0.015 when the fact is forced into the first passage, Haiku, 30 items). Both are priors, not measurements of these fixes; 13 of the 16 items are pack-written self-tests, so the 33 % column is an upper bound (C1-REASON).

Installing the three owner packs (cooking, money, the post author's blog) puts the fact into the kept context for 2 of the 9 "not installed" items, below the 4 we required, and changes the kept sources of about a third of the other questions plus 21 safety probes. The line closed. The ceiling that matters is the right-hand column: on real questions, even a perfect reach adds about +0.002 U at the 1.7B's measured reading rate.

**Do packs change the 1.7B's score? (CB17, PACK-TABLE-17B; our engine, Mac mini, one run).** On 97 casual dev questions, adding packs does not measurably change the 1.7B's aggregate score (Opus on 51 +0.015, CI −0.035…+0.056; Haiku on 97 −0.005); 63 of 97 answers are word-for-word the closed-book answer. A post-hoc split finds +0.048 (+0.007…+0.091) on 32 in-pack v0.1 items (Opus, no rule rides on it), and confident errors go from 13 to 8 of 51 (Opus, counts only, no CI).

**The {{convert}} bug.** One fact was lost when we built the pack. Our shared Wikipedia/Wikivoyage converter dropped the output of the {{convert}} template, so the Simple English Wikipedia article on the Great Wall read "the wall stretches ." The same bug left 3,176 chunks with a missing value in that pack and 877 in Wikivoyage. The fixed converter (11/11 tests) rebuilt Simple English Wikipedia with 524 such chunks left (+0.10 % size); the article now reads "In total, the wall stretches 21196.18 km." In a 0-LLM parity replay over 280 dev items, the kept sources changed on 1 item (no reference fact either way) and the pack's 20 self-tests were identical. We published it as revision r2 of boar-simplewiki-en next to the unchanged r1. Its effect on judged answers is not measured; at most 9 of the 280 items can move. The Wikivoyage rebuild with the same fix removed only 9 % of its missing values (it uses unit templates the fix does not cover) and was not published.

**Why the shipped app's knowledge base does not reach these facts (our reading of the app maintainer's snapshot 5f8cc8f4, replayed on a desktop harness, 0 LLM, dev ids; NATIVE-PARITY S3).** With his built-in 1,300-chunk KB only, a source is kept on 1 of 97 dev questions (ours, with the two claim-kit packs: 33). The 0.7 similarity cutoff is not the cause: at 0.5 or 0.3 the gate fires on 77 of 97, but the gold fact enters the context on 1 item and 118 of the 134 new chunks are off-topic by rule. With our two packs added to his corpus directory his retrieval keeps a source on 61 of 97 and the gold fact on 21 v0.1 items (ours 13); lowering the cutoff there hurts (fact items 21 -> 16). The fact rule is lexical (noisy both ways), one snapshot, not RC1 as installed (runsheet row 0b not checked).

Sources: arms/native-parity/NATIVE-PARITY.md (S3 stage table); arms/c1-reason/C1-REASON.md; arms/convert-fix/CONVERT-FIX-SHIP.md; arms/routing-r1/ROUTING.md; arms/keep-k1/KEEP.md; arms/oracle-real/ORACLE-REAL.md (prior); ruler/FACTPRESENT-2026-10-21.md (prior).

---

## 4. Measurement rules we learned today

**1. Arm and baseline on the same machine.** The Mac mini and the MacBook do not reproduce each other's text at the same seed: on 97 dev questions only 30 answers were byte-identical, although retrieval, kept sources and prompt tokens were identical on 100 of 100. The difference is decoding on identical contexts (temperature 0.7, different CPU kernels). Two mini runs of the same configuration agree on 95 of 97, so 2 rows is the floor for "changed by noise". One screen today (KEEP-E) paired a mini arm with a MacBook baseline and found all 14 baseline texts different; its direction held (9 of 14 worse), but the size mixes the rule's effect with host noise. Rule: generate the arm and its baseline on the same host, same build and same concurrency; retrieval-only questions can still use the 0-LLM replay, because kept sources match across hosts.

**2. A cheap judge's confident-error count moves by about ±1.3 per 100 on identical answers.** Three repeats of the Haiku judge on the same 97 answers gave 11, 14 and 12 confident errors on unwarned answers (12.7 per 100; 22 % of the deciding items flip between repeats). Two arms with identical answers differ by 2 or more 31 % of the time and by 3 or more 9 % of the time. A "+2 allowed" clause therefore sits inside judge noise. Rule: a confident-error guard needs Opus on the deciding rows or a margin of at least 3 per 100, and every headline confident-error count on the page carries "(judge retest ±1.3 per 100, Haiku)". No per-item Opus retest exists on dev; its noise is probably lower but unknown.

**3. The warning line is mostly a correctness signal.** We split warned answers by what the trace shows. Over 384 warned answers on development sets (Haiku), 77 % had a source kept and the model's answer was poorly supported by it; those carry 4 of every 5 warned confident errors. On real dev questions (MAIN 97) the two halves differ: warned answers with no source kept err at 0.19, close to unwarned answers (0.17), while warned answers with a weakly supporting source err at 0.49 (difference −0.30, CI −0.45…−0.11). So the no-source half is an answerability notice ("the library does not cover this"), and the kept-but-unsupported half is the error signal. The 4B and Gemma warn mostly for no source (60–75 % of their warnings), which fits the weaker warning precision we measured for the 4B; n is too small to call it per tier.

**4. Divergence first.** 30 of 72 phone v0.1 dev questions give the same text on the 1.7B, Gemma and the 4B (deterministic layers). We cache those, judge only changed answers on a fixed 87-item pool first, and run the full set only when the screen says go. Engine questions go to the 0-LLM replay, model questions to the divergent subset with Haiku, phone speed to 9–10 questions on a cool phone, and claim numbers to the full set with Opus and two judge families.

Sources: arms/litepacks/MINI-BASELINE.md; arms/keep-e/KEEP-E.md (deviations); arms/web-actions/WEB-ACTIONS-B.md §1–2; ruler/DIVERGENCE-MAP-2026-10-21.md; GOAL-2026-10-21.md (loop rules).

---

## 5. Honesty on device

These rules run in our engine. The submitted app's chat did not run them as of 10-17 (maintainer's portal report; QUEUE l.1295, claim v4.2.4 correction). Rows marked RC were measured on his release candidate.

[private correspondence with the app maintainer, or a result of a run on his device, removed]

**RC rows (pending 10-22; kill band frozen in hypothesis B2-LAYERS-SCOPE before the run).** RC layer probes: k/10 match our engine — pending 10-22 (dd_check.py layer on rc-layer10-4b, 10 ids incl. epi-1021 and geo-dev-1022). RC warning-line presence: on RC1 the line appeared on 0 of 3 eligible ids and 0 of 51 answers, and its text has 0 hits in the snapshot (GAP-LEDGER row 4). The warning clause of this band therefore fails for RC1 and stays open only for a later RC. If ≥ 8/10 probes give the engine-equivalent layer output, including the health/first-aid route on its health probes, AND the warning line appears on ≥ 70 % of eligible RC rows, this section may say "ported to the submitted app, verified on 10 probes" and the per-count caveat shrinks to the family/judge label. In every other case, including L2 not run, the opening paragraph above stays. In every case the "AI-reviewed, not clinically reviewed" caveat stays on each health sentence.

Our proposed default (NOTE-2 to the app maintainer; it first needs a warning line, which the app does not have) is refuse-by-default: an answer with no supporting source is hidden behind a "show the model's answer" button. We replayed that rule on the Pixel 8a bench rows (57 v0.1 dev questions, 42 of which reach the model on every tier; one phone run per tier).

**How much the rule hides on the phone (bench app, Pixel 8a, proposed mode, not shipped; one run, 0 judge calls for the hide rates)**

| tier | hidden of model answers, phone / desktop | hidden per 100 questions | generation spent per hidden answer | note |
|---|---|---|---|---|
| 1.7B, claim kit | 69 % / 62 % | 51 | 8.2 s | transfers (+7 pp) |
| 1.7B, six packs | 71 % / 45 % | 53 | 8.9 s | does not transfer (+26 pp): the desktop replay ran the head pass and dense append, the phone build has neither |
| Gemma 4 E2B, claim kit | 50 % / 48 % | 37 | 11.7 s | transfers (+2 pp) |
| Gemma 4 E2B, six packs | 43 % / 48 %* | 32 | 9.9 s | *desktop pair is the kit, not pack-matched |
| 4B, six packs (counterfactual) | 60 % / 62 %* | 44 | 22.4 s | *not pack-matched |

Tier availability: Gemma 4 E2B is a proposed opt-in (NOTE-3), not in RC1; opt-in only if a later RC lists it and T1 passes; RC1 (10-21) ships only Qwen2.5-1.5B on the Pixel 8a, so neither the 1.7B nor Gemma is in the submitted app today; both stay proposed unless a later RC lists them (runsheet rows 0b, 2, 7).

The cost is time as well as answers: on the phone each hidden 1.7B answer costs 8–9 s of generation, about 5–6 minutes per 100 questions, and Gemma about 5–7 minutes. On the 1.7B, the phone quotes replace our desktop proxies; the six-pack desktop figure (45 %) must not be quoted for the phone.

**The rule needs the warning line in the build (bench app, Pixel 8a, proposed mode, not shipped).** The bench build runs with the warning line off. The 1.7B then declines unsupported answers outright (25 of its 29 hidden rows are declines with no text), so a "show anyway" button would have nothing to reveal. On Gemma without the line, the literal rule hides about 1 answer in 3 instead of 1 in 2. The answer behind the button must be the one released under the warning line.

**First-aid cards: a null (our engine, MacBook replay, 0 LLM, 0 judge; AI-reviewed, not clinically reviewed).** We asked whether any existing first-aid card would have caught the health answers the model gave wrongly. In 245 replayed turns (MAIN, 65 safety probes, 80 multi-turn turns; our engine, 0 LLM; AI-reviewed, not clinically reviewed), only 10 turn rows reach the model on a health route; the rest already end in a card, the health-gap line, an extract or a refusal. Beyond the two epinephrine answers, 0 turns were coverable by a card (we froze ≤ 2 as the kill). Killed.

**The epinephrine answers (our engine; AI-reviewed, not clinically reviewed).** Two answers told the user to inject an epinephrine pen into the "forearm" and the "upper arm". Both questions named only the pen ("where do I inject it?"), so the health route never fired and the anaphylaxis card was never consulted. Adding "epinephrine / EpiPen / auto-injector" to the card's trigger is clean (0 false fires on 91 non-health questions, 0 of 64 safety probes moved; our engine, 0 LLM; AI-reviewed, not clinically reviewed) but routes 0 of the 2 turns to the card.

> **Proposed, not shipped (our engine; not in the submitted app; AI-reviewed, not clinically reviewed).** Our proposed card sentence, written in our own words from public first-aid sources: "Inject it into the middle of the outer thigh (it works through clothing) and hold it in place as the pen's instructions say." It reaches these questions only if questions that name epinephrine or an EpiPen are routed to the card, which is a routing change we will test on held-out questions after the freeze. Card text is AI-reviewed, not clinically reviewed.

Sources: arms/note2-transfer/NOTE2-TRANSFER.md; arms/fa-cards/FA-CARDS.md; arms/web-actions/WEB-ACTIONS-B.md §1; QUEUE l.1295 (claim v4.2.4 correction); DEVICE-DAY-RUNSHEET-2026-10-22 rows 3 and 6.

---

## 6. The packs line (10-22/23): getting the right chunk to the model

Our engine (Qwen3-1.7B, 13 packs), dev questions; the bracket excepted.

**A stricter ruler first.** A fact counts as delivered only inside one kept chunk, not anywhere in a kept article. An earlier arm (F1b) fell from 45 to 32 of 92 keyed questions (52 general, 40 cooking/money). On top of the global-IDF merge (gidf), three Stack Exchange retrieval fixes (F1, F2, F4) raise delivered facts from 28 to 42. A fourth, F3, reached 47, but on 65 safety probes it turned 21 health refusals into answers and unsafe answers rose from 9 to 13 (one seed; AI-reviewed, not clinically reviewed). We withdrew it.
src: arms/coverage-map/CHUNKLEVEL.md (+ chunklevel.json); arms/coverage-map/sefix/SEFIX.md (SEFIX-124 step 0); sefix/F3-SAFETY.md; sefix/F3B.md.

**Small packs compose; a giant one crowds.** From 3 to 13 packs under gidf, delivered facts never fell (23 to 32, article level). The English Wikipedia top-100k pack takes 47 to 55 % of kept slots for a net 2 facts. Question form matters more than the pack: for 48 facts asked nine ways, the gold chunk was kept for 83 % of questions containing the answer term, 50 % of base questions, and 8 to 10 % of entity-free questions or bare follow-ups.
src: arms/coverage-map/compose/COMPOSE.md; arms/coverage-map/COVERAGE-MAP.md; arms/qform/QFORM-RESULTS.md.

**Within the item: a small Haiku gain.** Same questions, adopted set vs a smaller pack kit. Where it delivers the fact, answers gain +0.044 (+0.009…+0.082, n 42, Claude Haiku, two seeds pooled); where it does not, −0.009. Opus on the 28 delivered general questions gives +0.013 (−0.044…+0.072): not confirmed. Across all 97, +0.013 (−0.008…+0.036, Haiku). On 42 general questions Opus sees −0.002 (−0.062…+0.061; run with F3, same answers there). The Opus +0.173 on 22 cooking/money answers came from that F3 run, not the adopted set. Our reading: the hit rate, how often the right chunk arrives, is the lever.
src: arms/night-1023/B-TABLE.md (+ b-table.json: arm_vs_control, dU_vs_control.pooled, opus_cv5_delivered_slice); sefix/opus-sefixall.md; arms/coverage-map/sefix/opus-cm.md; sefix/SEFIX.md (SEFIX-124: text identical to SEFIX-ALL on 92/97, the 5 differences are F3 cooking items).

**Between items, the flag does not separate.** Answers with the fact delivered score 0.420, without it 0.419 (gap +0.001, −0.071…+0.069; Haiku); a judged "a kept chunk supports the gold" flag gives 0.427 vs 0.426. The 1.7B misses facts it is given and answers easy items from memory. Three crypto packs add no net fact on the general questions. Nothing here changes our claim numbers.
src: arms/night-1023/B-TABLE.md; arms/night-1023/SUPPORT.md; arms/night-1023/A-KIT.md.

| what we tried | result | status |
|---|---|---|
| gidf + F1/F2/F4 | 28 → 42 of 92 delivered, 0 lost; answers +0.013 (Haiku, CI crosses 0); unwarned confident errors 23 → 27 (two seeds) | adopted for delivery |
| F3 health fallback; gated F3b | 47 of 92 but unsafe 9 → 13; F3b 0 fires or 12 unsafe (AI-reviewed, not clinically reviewed) | withdrawn |
| readers RD1 to RD3 | all 97: −0.002 to −0.011 vs control | closed NO |
| precision gates P1/P2 | +0.003 / +0.001 on all 97 | closed NO |
| health-detector retrains (3) | misfires 6 → 0, but 76 and 185 real health positives lost; third failed recall at every dose (AI-reviewed, not clinically reviewed) | closed NO |
| W98 source-origin veto | vetoes the 6 dev misfires and 5 real health probes, one a child's dose (AI-reviewed, not clinically reviewed) | closed NO |
| FMT1 wider scan / 0.65 floor | 42 → 41 / 39 delivered | closed NO |
| KEEP-PIN | 43 delivered (bar 45); 27-topic context +11 % | closed NO |
| decoder grounding (10-21) | 4 of 4 arms NO-GO (net 4 to 6, bar 9) | closed NO |
| W78 binary sidecar | 0.126x bytes scanned, 42 of 42 delivered, kept ids 97/97 | candidate (phone unmeasured) |
src: arms/coverage-map/{sefix/SEFIX.md, sefix/F3B.md, reader/READER.md, gate/GATE.md, sefix/W98-TRACES.md, fmt1/FMT1.md, keeppin/KEEPPIN.md, w78/W78.md}; arms/night-1023/b-table.json (all97_summ CE_unwarned 12+11 → 13+14); arms/detector-hn/{DETECTOR-HN, DETECTOR-FT, DETECTOR-FT2}.md; arms/decode-ground/{DECODE-GROUND, DG-STAGE1}.md.

[Internal until r4to's word.] **The app maintainer's 27 Research Topics (bench engine, 1.7B, wiki-vital5, Haiku sentence audit).** Succinct keeps 19 of 27 topics by our frozen rule, Detailed 7; unsupported sentences 0.28 vs 0.47, same kept sources. Four topics never reached the model on the base engine, for four different reasons, though every article is in the pack; the adopted fixes recover one, a wider scan and a title pin one more each, NO by rule. In our desktop replay of his native pipeline (1.5B Detailed, 51 dev ids, one seed, Haiku), wiki-vital5 on vs off gives +0.026 (+0.001…+0.051): neutral by our rule, because one health answer became a new confident error (AI-reviewed, not clinically reviewed). Not a measurement of his app.
src: arms/topics27/TOPICS27.md; topics27/SUCCINCT.md (+ aggregates/succinct-summary.json); topics27/MISSES.md; coverage-map/fmt1/FMT1.md; coverage-map/keeppin/KEEPPIN.md; arms/native-parity/VITAL-ONOFF.md (+ aggregates/vital-onoff.json).

> **Caveats.** Dev items; one or two seeds. Mostly Claude Haiku (compresses gaps). Our bench engine, not the submitted app. The 40 cooking/money questions were written from their packs, so gains there are optimistic.
src: arms/night-1023/B-TABLE.md (caveats); sefix/SEFIX.md (caveats); arms/native-parity/VITAL-ONOFF.md (caveats).

Reviewer (10-23, independent Opus reviewer): every number re-checked against its src file and JSON (b-table.json, chunklevel.json, opus-cm, opus-sefixall, fmt1.json, keeppin.json, w78.json, topics27 aggregates, vital-onoff.json); all match. Changed: added the Opus +0.013 (n 28) check beside the Haiku +0.044; tied the Opus −0.002 and +0.173 to the F3 run (SEFIX-ALL) and said why −0.002 carries over; "gidf plus three fixes raise 28 to 42" corrected (28 already includes gidf); "old best arm" named as F1b (SEFIX-ALL was 55 → 47); QFORM's 83 % is questions that contain the answer term, not "statement form"; crypto packs "0 net facts" limited to the general questions (43 vs 42 overall); adopted row now shows unwarned confident errors 23 → 27; detector row no longer says all three retrains lost 76 to 185; W98 row says what the 5 probes are; topics paragraph notes the adopted fixes recover one miss and that VITAL-ONOFF is our harness replay; the public caveat no longer names the internal arm; section title no longer claims an improvement; en-dashes spelled out. Residual doubts: (1) the +0.044 subset is chosen by the arm's own delivery flag and holds 14 cooking/money self-tests of 42; Opus does not confirm it. (2) "the hit rate is the lever" is an inference from a within-item contrast, not a test that raises the hit rate and measures answers. (3) The F3 safety reading is one agent, one seed, 65 agent-written probes. (4) Name the control kit (K1 traces, K3 settings) in one plain phrase before publication.

---

## Open items for the page before 10-25
1. DONE 17:0x (DEVICE-E1PAR): B PAYS; replace "device run pending" in §1 with the measured A/B rows (Q8); the other projection rows keep their label.
2. DONE: BLOCKCACHE-64 KILL on the phone (ratio, PSS); §1 names no cache recommendation.
3. Hermes WebAssembly check: DROPPED (ACTIONS W44; the submission uses native libzstd). The decoder paragraph is now one bench-only sentence with no WebAssembly-on-phone claim.
4. X2b OFF: 19 cooking/money ids at seed 43 (about 76 Haiku) or Opus on the flips, so §2 can drop the "at the edge" caveat.
5. Warning line: RC1 0/51 (Q11); layer probes still pending (H2a, rc-layer10).
6. Default pack set: r4to's product call (options A–D) before §2 states which packs ship.
7. Opus per-item CE retest on dev, so §4 rule 2 can give the Opus noise band, not only Haiku's.
8. simplewiki r2 judged effect (≤ 9 movable items) or keep "not measured" in §3.
9. Every outline prior marked "Verify by fetch" (T1.3, T2.5, T3.1, T3.2, T5.4, T6.1, T11.1, T23.2, T31.1) and the libzim-cache claim need a primary-source fetch before they are cited (outline "verify by fetch").
10. Independent Opus content review of all five sections (wording, health sentence, no maintainer-app claims) before the page goes public; no upload without r4to's OK. Also a re-review after the 10-22 RC rows land, because the kill bands rewrite §1 and §5.
11. B3: if no R4 APK row exists by 10-24 18:00, r4to picks headline variant A or B. The page uses neither until he does.
12. B4 tier labels: re-read the catalog at every new RC install. With RC1, the R4 8 GB row model is the 1.5B.
13. DONE: RC1-SPEED (n 9) and RC1-PACKS (0 packs, base KB) written. Native absolute numbers stay internal until r4to's word.
14. Runsheet row 0: if the Codex ladder has not run by 10-23 18:00, every "two families" sentence becomes single-family.
15. SUCCINCT17 S1b kill (p50 < 150 tokens or < 5 s) decides whether R7's succinct sentence stays.
16. DONE 2026-10-21: A1-RC1-SHIPPED-U landed (arms/rc1-pixel/RC1-SHIPPED-U.md): shipped RC1 1.5B U 0.143 (0.103-0.188), paired 1.7B K0 - RC1 +0.209 (+0.134...+0.288), RC1 - closed-book 1.5B -0.119 (-0.182...-0.065); fills the S00 slot and the §1 RC1 quality line; speeds from that run are thermally degraded and not for the page. [internal until r4to's word]
17. The page must not use 0.261 (closed-book 1.5B rung) as the app's proxy, or write 'effectively the 1.5B rung' (A1 PROXY-HOLDS failed: |0.143 - 0.261| = 0.118 > 0.05).
18. DONE: PAGE-DRAFTS-REVIEW-2; re-review again after the 10-22 RC rows (item 10). The native absolutes stay [internal until r4to's word] and nothing in them is a decision.
19. CB17 (PACK-TABLE-17B): the packs paragraph in §3 now carries only the guarded O1 wording; never write "packs make the 1.7B better".
20. GAP-LEDGER row 5 (layers on RC1, not established) gates every "the app has no layers" sentence until H2a.
21. B2: no page or NOTE sentence may present the 1.7B as the quality lever in the app maintainer's pipeline (+0.010 Haiku); the 1.7B case rests on speed/RAM and on the Opus bench gap.

22. (web W80, 10-22 02:4x) Retrieval section: describe the extra-slot (no-displacement) dense-chunk design as ours and cite arXiv 2210.11934 for rank-fusion displacement; numbers only after G2-FULLKIT reads.
23. Framing sentence for §0 of the page (reviewer 10-23, use verbatim): "On our dev questions, answers improved by about 0.04 (Claude Haiku judge, CI +0.01 to +0.08) where our pack and retrieval changes put the key fact inside a kept chunk, and not elsewhere; an Opus check on 28 of those questions saw +0.01, inside noise. So the lever we work on is how often the right chunk arrives." Never write "packs add +0.04", "with a reference good, without bad", or any between-item claim (§6, B-TABLE).
24. W78 binary sidecar: phone measurement (first-query load, PSS delta, per-query F1 scan ms, kept-id parity on 9-10 items) when the Pixel is free; §6 keeps "phone unmeasured" until then.

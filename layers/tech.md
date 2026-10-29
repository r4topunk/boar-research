# RatLab — A Boar Research, read as: Tech people

> Closed record · research record 1.1.2 · as of 2026-10-28; the author closed the research lines on 2026-10-23. Current standing, not a final result: Open fronts: https://r4topunk.github.io/boar-research/data/status.json.
>
> Final · as of 2026-10-28 · 0 of 71 wins on the phone, U-total 0.165 (Claude) / 0.242 (gpt-5.6-sol), below the 0.50 bar

How the system and the method work, with the numbers that drive each decision.

## 1 · The question {#question}

#### The spec: Android, ≤ 12 GB RAM, ≤ 50 GB, offline, half as good

The bounty fixes the hardware envelope and leaves the quality target vague. Hard limits: Android or GrapheneOS, at most 12 GB of RAM, at most 50 GB of assets, fully offline, no Play Services, public source. Target: "more than 50 % as good as internet search plus a frontier AI" on explanation, comparison, synthesis and reasoning questions, in English. We treated the envelope as a budget and the target as a measurement problem: before touching the engine we built a desktop runner that executes the app's real TypeScript answer engine, and a judge that compares every answer with a frozen frontier-plus-web reference.

**Callout:** "Pre-harness numbers (an older 61-question set, 0.26 → 0.48, a 1.5B model on an iPhone) used a different instrument and are not comparable to anything below."

*Facts: [F-682] [F-071] [F-995] [D-035] [F-063]*

Whole chapter: https://r4topunk.github.io/boar-research/research/question.md

## 2 · Building a ruler {#ruler}

#### One harness, one trace format, a judge that sees both orders

The harness has five layers and one trace schema (ADR-001). A desktop runner loads the app's real answering engine in Node, swapping only native pieces (model runtime, SQLite, file system); routing, retrieval, prompt building and source selection are the engine's own code. Each answer becomes one trace row. The judge (Claude Opus via the Claude Code CLI, prompt judge.v1) gets the question, the answer and the frozen reference, with think blocks, source lists, URLs, markdown links and [n] markers stripped, scores both 1–5 on correctness, completeness and usefulness, and picks a winner; then it sees the pair in the other order. Order disagreement is a tie. Seven axes (quality, truthfulness, safety, retrieval, latency, resources, stability) are reported side by side and never averaged.

```sh

pnpm i

node harness/validate.mjs my.traces.jsonl

node harness/judge.mjs --traces my.traces.jsonl --out my.judgments.jsonl --bench bench/v0.1 --dry-run

node harness/judge.mjs --traces my.traces.jsonl --out my.judgments.jsonl --bench bench/v0.1

python3 metrics/floor_metrics.py --dir. --runs my --questions bench/v0.1/questions.public.jsonl --decline-ratio 0.306

python3 scorers/score.py --traces my.traces.jsonl --judgments my.judgments.jsonl --bench bench/v0.1 --json my.score.json

```

**Gotcha box: "Make it fail closed."** The first judge silently dropped errored traces, which flattered a failing device. Now `--strict` exits before any call if a trace or reference is missing, `--floor-errored` scores a failed answer 1/1/1, and resuming refuses to reuse a cached row unless trace, question and reference sha256, judge version and model all match (exit 7).

*Facts: [F-200] [F-371] [D-063]*

Whole chapter: https://r4topunk.github.io/boar-research/research/ruler.md

## 3 · The floor trap {#floor-trap}

#### Raw, floor-adjusted, win/tie/loss: read the last two first

With S and R the mean rubric (mean of three axes, both orders averaged) of the app and of the reference: raw = ΣS / ΣR; floor-adjusted = Σ(S − 1) / Σ(R − 1); above-decline = (raw − D) / (1 − D) with D = 0.306, the measured raw score of a system that declines everything. Because the rubric's minimum is 1, raw 0.50 is about 61 % free. References score about 4.9/5, so the ratio behaves like an absolute rubric mean. Example on the 4B (v0.1, dev): raw 0.512 = floor-adjusted 0.387 = above-decline 0.297. We report all three, lead with floor-adjusted and win/tie/loss.

*Facts: [F-236] [F-237] [F-126] [F-263] [F-341] [F-268]*

Whole chapter: https://r4topunk.github.io/boar-research/research/floor-trap.md

## 4 · Seven frozen builds {#builds}

#### Detector → instant tier → health path → retrieval → keep → reader

Every question takes a fixed path. A small learned emergency detector (an mmBERT-small encoder, q8_0, 106 MB, threshold 0.2) and hand-written rules look first. Some questions never reach a language model: emergency numbers, unit conversions, arithmetic, travel distances, nearby places, a 4,233-entity Wikidata fact table (761 KB), and health and first-aid questions, which get a reviewed card (32 conditions) or a verbatim cited excerpt of at most 700 characters. On the default tier the model never writes health advice. Everything else goes to retrieval: SQLite FTS5 full-text search over 1,000-character chunks plus 384-d bge-small article-lead embeddings over the installed knowledge packs (k 6). A keep step drops off-topic and unsafe passages and fits the rest into a 1,200-token context. The reader of the frozen claim build, Qwen3-4B-Instruct (Q4_K_M, 2.5 GB), writes a short cited answer. The deep tier swaps in Qwen3.6-35B-A3B (UD-Q2_K_XL, 12.3 GB file) with a 400-token context, 200 answer tokens and a 512-token thinking budget (desktop only; not delivered). From 2026-10-20 the main 8 GB reader is Qwen3-1.7B (Q4_K_M, ≈ 1.1 GB file) and the delivered app keeps one Succinct style (T14, T18).

**Health callout:** "AI-reviewed, not clinically reviewed. Nothing here is medical advice." Detector dev numbers: curated recall 179/180, strict false fires 15/100 (dev data) [F-1072]. DETMAX: chit-chat before an emergency lost 7/240 routes → 0/240 [F-345]. HEALTHGAP: 15 of 64 health-shaped probes reached the model unguarded until a predicate fix [F-378].

**Note:** the detector weights are not released (base-model licence unknown).

#### Cut 1 → cut 7: what each build added and which test let it in

We never shipped tweaks, only numbered, hashed builds (cuts) that bundle the arms that passed their frozen criteria. Cut 3 added a self-contradiction guard, an arithmetic tool and a snakebite text; cut 4 fixed our own KV-cache save path and blocked fragment instant answers; cut 5 skipped the route gate where safe (32/54 gate calls per seed, 120/120 identical answers); cut 6 made the detector score the window and the current turn; cut 7 added the Wikidata fact table. The fact table fires 0/110 on v0.2 and 0/58 on V-para, so cut 7's held-out numbers are cut 6's. Small-model quality on the held-out set did not move beyond noise across all of it: main 0.506 → cut 6 0.512 raw on v0.2 (two seeds, Opus): +0.006.

**Decision note:** the claim build was frozen at cut 6 on 10-06 with "only answer-preserving fixes"; that freeze was relaxed on 10-07 when cut 7 changed 8 v0.1 answers. Both steps are shown (group-A §2 item 4).

*Facts: [D-038] [D-046]*

Whole chapter: https://r4topunk.github.io/boar-research/research/builds.md

## 5 · The walls {#walls}

#### Retrieval, prompts and bigger small models: the walls

Oracle runs set the ceiling. On v0.1 (dev, Opus, 1 seed, n 57): closed-book 0.487, engine 0.507, question-chosen passages 0.567, gold passages 0.606, Claude Haiku with no web 0.653. A retrieval rewrite put the gold sentence in context 7 → 18 times out of 56 and still lost 0.021. A Wikipedia top-100k pack bought nothing for the 4B and made retrieval 3.3× slower. Recall@5 was 0.333 and coverage was the largest failure bucket (49 %). Other 4–9B models were no better closed-book (Qwen3.5-9B 0.488 vs Qwen3-4B 0.487). Prompts that asked for longer or more complete answers raised confident-wrong answers. The lesson for builders: on this hardware the small model's reading is not the bottleneck; knowledge the kit does not hold is.

**Decision table:** lever → measured effect → status (from the public registry; e.g. R3 named-slot ranking, R5 enwiki top-100k for the 4B, R7 shorter prompt, R8 "answer completely", R13 multi-pass).

*Facts: [F-314] [F-443] [F-993] [F-453] [F-450] [F-433]*

Whole chapter: https://r4topunk.github.io/boar-research/research/walls.md

## 6 · The deep tier {#deep-tier}

#### 35B mixture-of-experts + 512 tokens of thinking: 0.261 → 0.436 floor-adjusted, 79 s per answer on desktop; never delivered

The only lever that beat noise on bounty-style questions was a larger model, and it stayed on the desktop: on 2026-10-21 the author decided that no 35B deep mode is delivered [D-147]. Qwen3.6-35B-A3B activates about 3B parameters per token, so it fits a desktop CPU at 2-bit (UD-Q2_K_XL). On V-para (Opus, two seeds; dev-style data, desktop only) the ladder is: 4B claim build floor-adjusted 0.261 → deep tier 0.329 → deep + thinking 1024 0.422 → deep + thinking 512 0.436, all 0 wins of 51. Thinking is the biggest step (+0.093 floor-adjusted, CI +0.050…+0.137), and the budget has a knee: 512 tokens matches 1024 (+0.014 floor-adjusted, CI −0.012…+0.039) at 0.55× the time. Desktop p50 per answer: 4B ≈ 6–10 s, deep ≈ 31–33 s, deep + 512 ≈ 79 s, deep + 1024 ≈ 143–146 s.

**Table: the ladder** (judge.v1 ratio; V-para, Opus, 2 seeds unless noted; no phone rows: the deep tier was never run on a phone)

| config | raw (CI) | floor-adj (CI) | W/T/L | desktop p50 | status |
|---|---|---|---|---|---|
| 4B claim build (cut 6 = cut 7) | 0.413 (0.384–0.445) | 0.261 (0.224–0.300) | 0/0/51 | 6.3–10.1 s | held-out at run time |
| deep, no thinking | 0.467 (0.439–0.494) | 0.329 (0.294–0.362) | 0/0/51 | 30.9–33.3 s | dev-style |
| deep + thinking 256 | 0.514 (0.483–0.544) | 0.387 (0.349–0.426) | 0/0/51 | 53.2–57.5 s | dev-style |
| deep + thinking 1024 | 0.542 (0.513–0.571) | 0.422 (0.385–0.459) | 0/0/51 | 142.9–146.0 s | dev-style |
| deep + thinking 512 (recommended) | 0.553 (0.524–0.581) | 0.436 (0.401–0.472) | 0/0/51 | 78.9–79.4 s | dev-style; best of ≥ 8 configs |
W/T/L is per seed and identical for both seeds on every row.

**Gotcha boxes:**
- The on-device MoE engine (bmoe v0.28.0) has no thinking-budget flag; a phone build needs an app-side cap [F-751].
- The deep tier still needs retrieval: removing packs costs −0.045 (−0.083…−0.011) (slice of 20, 1 seed, Haiku) [F-1000].
- Bigger thinking budgets do nothing: the model stops by itself around 1.3k tokens [F-363].

*Facts: [F-005]*

Whole chapter: https://r4topunk.github.io/boar-research/research/deep-tier.md

## 7 · A phone on a desk, and in a hand {#phone}

#### Same quality as the desktop, 3.4× slower, 4.2 GB after load

We trusted the desktop only after phones agreed with it. Cut 7 on a 12 GB-class phone (MediaTek MT6897, 10.7 GiB usable, Android 16, airplane mode, no INTERNET permission) answered 72/72 with 0 timeouts. Tier routing matched 60/60, instant answers were byte-identical 16/16, kept source titles matched 59/60, and model text was identical on 3/44 (sampler differences). Quality on the 57 public v0.1 items under the Haiku L1 judge: raw 0.529 (0.481–0.575) on the phone vs 0.529 on desktop; paired −0.000 (−0.026…+0.028). Fast tier: p50 30.7 s, p90 48.4 s, TTFT p50 18.5 s, decode 5.5 tok/s, output p50 64 tokens. Memory: PSS 5.88 GB peak during model load, then p50 3.64 GB, max 4.23 GB. Thermal status stayed 0.

**Gotcha boxes:**
- **ARM weight repack.** llama.cpp's repack copied ≈ 2.3 GiB of weights into anonymous memory and the OS killed the 4B on an 8 GB phone while loading; disabling it dropped desktop max RSS 5.1–5.4 → 3.41 GB. The fix (repack-aware fit, Android only) is not in the frozen build [F-691] [D-024].
- **The desktop shim hid our own bug.** A KV-cache session save path was a no-op on desktop, so every phone question re-prefilled ≈ 430 + 300 tokens (35–41 s + 20–28 s) [F-715] [D-034].
- **q8_0 KV cache** is non-inferior (Δ −0.0077, −0.0232…+0.0062) and halves reader KV 576 → 306 MiB [F-716].
- **Pure-JS zstd** was ≈ 76 % of retrieval time on the phone; native zstd ≈ 80× faster [F-1141].

#### Never run on a phone: two engines, one projection, an Android build that was not measured

The deep tier only ever ran on desktops. Two on-device paths were tested there. bmoe, a streamed-MoE engine, is not token-identical to llama-server (greedy 0/10) but judged-equivalent on identical contexts (0.623 vs 0.634, Δ −0.012, CI −0.045…+0.020; v0.1 dev, n 57, 1 seed, Opus); its macOS session peaked at 11.7 GiB. An expert-streaming fork (LES) runs the same 35B at 14–17 tok/s with 2.75–2.81 GiB peak RSS on an M4 desktop CPU with experts read from SSD and page cache, and is judged-equivalent too (0.625 vs 0.634, Δ −0.010, CI −0.042…+0.018). On a phone it would be flash-bound: about 320 expert reads and 314 MiB per token, so roughly 4 tok/s on UFS 3.1 and 6 tok/s on UFS 4.0 including compute (I/O-only upper bounds 4.8 / 8.0). Using third-party public phone rates, a deep + 512-thinking answer would take about 1.9–2.8 minutes on a Pixel 8 Pro CPU. None of this was measured on a phone. The expert-streaming engine was cross-built for Android arm64 on 2026-10-19 [F-2118], and then the author's 2026-10-21 decision (no 35B deep mode, [D-147]) dropped both phone fronts (OF-1, OF-2 in `data/status.json`). The projection stays a projection.

*Facts: [F-037] [F-740] [F-036] [F-795] [F-793] [F-766]*

#### 1.7B for small phones: faster, safe-routed, weaker reader (the 10-16 lite-tier view; superseded by T14)

For 4–6 GB phones we tested Qwen3-1.7B (1.1 GB file, RSS ≈ 2.3 GB vs ≈ 4.0 GB for the 4B; desktop prefill 2.5× and decode 2.2× faster) behind the same safety engine; health routing matched the 4B 124/124. With X2b it matches the plain 4B only on pack-matched dev items (−0.007, −0.031…+0.018, Haiku); on the claim kit it is 0.111 below the 4B and X2b is inert there; at identical contexts it reads worse (−0.070, −0.094…−0.044, n 97). Phone speed for the lite tier was unmeasured as of 2026-10-17; on 2026-10-20 the 1.7B became the main 8 GB engine on measured phone speed (T14). Separately, long sessions do not degrade the 4B: turns 6–15 score 1.136 (0.993–1.320) of BOAR's own standalone answers (Haiku L1, 80 agent-written questions), but latency grows to about 22 s at turns 14–15 vs 8 s standalone on desktop.

*Facts: [F-1083] [F-1084] [F-390] [F-1081] [F-030] [D-113]*

Whole chapter: https://r4topunk.github.io/boar-research/research/phone.md

## 8 · The agent lab {#agent-lab}

#### A coordinator, lanes, reviewers and a loop: 54 of 101 ideas died for free

The research ran as an AI-agent lab. A coordinator session owned the queue, wrote and hashed each pass/fail rule before a run, launched jobs on two Macs (a Mac mini M4 16 GB for long generations, a MacBook M1 Pro 16 GB for replays and small models) and logged every result. Research agents in lanes (retrieval, models, evaluation/safety, native performance) wrote technique cards but never ran or graded experiments. Independent reviewer agents decided wording. Jobs ran detached with sentinel files so they survived session restarts. Of 101 closed arms, 54 died at zero judge calls (deterministic replays, counting), 10 at the cheap Haiku slice, 12 after Opus confirmation and 25 with Opus directly. Over four unattended days the loop made 133 ticks and ≈ 10.5k judge calls and produced one dev-only lever; ≈ 31 machine-hours were avoidable, mostly long runs launched without a smoke test.

Whole chapter: https://r4topunk.github.io/boar-research/research/agent-lab.md

## 9 · Knowledge packs {#packs}

#### One SQLite file per library; pick one, don't install ten

A pack is one SQLite file: article text in zstd blocks, 1,000-character chunks indexed with FTS5, one 384-d lead vector (first 2,500 characters) per article, and per-row licence and attribution. We published 11 packs on Hugging Face (Stack Exchange travel, Ethereum, Bitcoin, health, outdoors, cooking and money; first aid; MedlinePlus; a world factbook; Simple English Wikipedia), sized from 4.3 MB to 480.5 MB, licences PD / CC0 / CC BY / CC BY-SA only. On the 180 pack self-test questions (written by agents from the packs' own text; dev; Opus) one matching pack lifts the 4B +0.042 (+0.024…+0.062); installing nine as peers drops the fact article's survival into context from 68 to 46 of 180 and costs −0.019 (−0.035…−0.003). Top-1 routing reached only 0.25–0.61 accuracy. An oracle that injects the known fact chunk is worth +0.095; HEADPASS-X2b, which appends the retrieved article's neighbour chunks plus budgeted dense candidates after the keep step, gets the fact chunk into 102 of 180 prompts (from 35) and +0.066 (+0.043…+0.091), at about +420 prompt tokens p50 and +60 % pack size for chunk-vector sidecars. On the bounty-shaped claim kit it is inert. The 35B gains nothing from packs (−0.002).

**Rule box:** "default-eligible only if a pack holds ≤ 0.40 of kept slots and does not lower kit gold; otherwise user-selected only" → 5 default-eligible, 6 user-selected [D-083].

Whole chapter: https://r4topunk.github.io/boar-research/research/packs.md

## 11 · A smaller engine for 8 GB phones {#small-engine}

#### Qwen3-1.7B on 8 GB: chosen for latency and memory, not quality

On a Pixel 8a (8 GB) running our measurement app, the 4B decoded at 3.6–6 tok/s, answered in 29–46 s and was killed once by the low-memory killer at 4.4 GB RSS; Qwen3-1.7B decoded at 13–16 tok/s and answered in 13–16 s (9 public dev questions, before batched lookups). On 2026-10-20 the author made the 1.7B the main 8 GB engine and the 4B an optional tier. Batching the pack lookups (937 → 48 SQL calls per retrieval, byte-identical retrieval on 390/390) cut the 1.7B's time to first token on the phone from 9.12 to 5.55 s. On the 73-question phone run the 1.7B's p50 is 4.2 s with PSS 3.39 GB, but that p50 covers deterministic answers and declines (35 % of v0.1); its model-path p50 is about 12 s. The cost is reading: under Opus on v0.1 51 dev the 4B leads by +0.109 (+0.063…+0.160) on the judge.v1 floor-adjusted ratio, and at identical pack contexts it reads 0.650 vs 0.529 (Haiku raw).

**Gotcha box: "citation-dropping models get refused by your own engine."** Ministral, Qwen3.5-2B, SmolLM3, granite and a public RAG LoRA dropped `[n]` markers, so the engine's 50 % key-word support check stripped their answers and false refusals rose to 9/20 [F-2117] [F-1931].

**Gotcha box: "set the screen bar from a null arm."** A whitespace-only patch or a new seed already "fixes" 23–31 % of problem items; GATE v2 sets the bar at the largest measured null net + 2 [F-2073] [D-141].

**Product rule box:** no source kept → decline by default; "show anyway" behind a second confirmation, never on health; shown answers carry the warning line (precision 0.39–0.40, recall 0.65–0.67 on the 1.7B) [D-149] [F-2085] [F-1633]. AI-reviewed, not clinically reviewed.

*Facts: [D-134] [D-187]*

Whole chapter: https://r4topunk.github.io/boar-research/research/small-engine.md

## 12 · A second ruler (bench v0.4) {#new-ruler}

#### 75 items frozen before any answer, U-total with a stage-1 zero, two judge families; on the desktop the submitted engine stayed below the bar, the phone run is the headline

Bench v0.4 has 75 items (71 headline + 4 anchors taken from the example questions in Vitalik Buterin's post that inspired the bounty, scored outside the headline), frozen on 2026-10-20 at 16:45 (sha f9ad2f2f) before any system answered; candidates came from Claude (36) and OpenAI gpt-5.6-sol (34) and were cross-fact-checked (329 checklist points supported on the open web). The score is U-total: Σ(app rubric mean − 1) / Σ(reference rubric mean − 1) over the 71 headline items, with health items weighted 0.5 (weight-1 beside), so the rubric floor maps to 0. Because judge.v1 still gave a bare refusal U 0.058, a stage-1 classifier (DECLINE2STAGE) zeroes detected non-answers before judge.v1 scores the rest (RULING R1). The verdict arm installs all six persona packs at once (A∪); the verdict statistic is the lower of the two judge families per bootstrap draw, and "meets the bar" requires CI low > 0.50 with every gate (RAM, storage, offline, speed, safety) passed. Spec r3 and r4 were frozen on 2026-10-21 before any app answer; r4 adds an information-available split: the packs hold the answer for 19 of 71 headline items, partly for 25, not at all for 27. As of 2026-10-24 20:34 both reference families are complete (75/75 each; the gpt-5.6-sol half at 20:05, 0 hard failures; [F-2212]), and three engines have answered on desktop twins. The last of them is the final run on BoarLite's engine b4ef94f3 (RULER-FINAL): one seed instead of the spec's two (the author's choice), each judge family against its own references, stage 1 not run, no errata, no phone run [F-2214] [D-204]. Published by the author's decision of 2026-10-25 as history: 0 of 71 wins under both judge families (one gpt-5.6-sol tie); U-total (desktop twin of engine b4ef94f3) Claude Opus 0.164 (0.123–0.208), OpenAI gpt-5.6-sol 0.245 (0.194–0.300); the lower family, 0.164 (0.123–0.206), is below the 0.50 bar; by information available (Claude family) 0.164 where the packs hold the answer (n 19), 0.174 partly (n 25), 0.155 not at all (n 27): with the information present, the 1.7B did not deliver it [F-2215] [F-2217]. The paired delta against the native engine branch stays internal (it prints that branch's number). They are numbers for b4ef94f3: the shipped LabRat 7788924a changes the grounding prompt's identity line after this run [F-2225], and the on-phone re-measure is DEVICE-FINAL (OF-8, landed 2026-10-25: 0 of 71 wins under both judge families, below the bar; criterion frozen before the run, [F-2227], [F-2238]) (the ruler run predates the Rat persona line).

**Rule box:** "No item text, reference or label list is published before the result card" [D-195]; lifted when the record closed: the v0.4 items, references and drafts were published on 2026-10-27. "Any engine change after 2026-10-24 counts as developed after exposure" [F-2108]; "v0.4 is the claim set: no tuning after the final run" [D-204].

Whole chapter: https://r4topunk.github.io/boar-research/research/new-ruler.md

## 13 · Delivery, not coverage {#delivery}

#### Count delivery at chunk level; most misses are search, not missing content

We count a fact as delivered only when its quote sits inside one kept chunk; article-level counting had overstated delivery by 8–13 facts. On MAIN 92 keyed dev items, delivered facts went from 21 (no fix) to 28 with a global-IDF merge (word rarity computed across all installed packs, so small packs compete fairly; +6.2 points hit@kept, 0 lost), to 42 with three Stack Exchange search fixes (SEFIX-124), and to 47 with a fourth fix (F3, a health no-source fallback) that fired on 21 of 65 safety probes and raised unsafe answers from 9 to 13, so it was withdrawn. Answer-level gains stayed within noise: SEFIX-124 +0.013 (−0.008…+0.035) on all 97 (Haiku, two seeds). Of the 50 facts still undelivered, 44 already sit in the default 13-pack kit. A compact per-pack index (W78) cut the data read per question from 125.09 to 21.26 MB and the cold first stage from 620 to 92 ms on a desktop replay.

**Gotcha box: "self-tests flatter retrieval."** The pack gain on fact-added self-test items (+0.139, n 27) is −0.010 on real items (n 10) [F-2080].

**Safety box:** every retrieval change runs the 65 safety probes before merge; two otherwise-good configs (a wider append budget, the best RETBENCH config) were kept out because dose/number probes changed [D-177]. AI-reviewed, not clinically reviewed.

Whole chapter: https://r4topunk.github.io/boar-research/research/delivery.md

## 14 · Closing the research: what a small model needs {#closure}

#### Acceptance tests on a desktop twin, one closed engine, a judge pass the next morning

After the author closed the research lines (2026-10-23 11:53), the remaining work was acceptance tests on the app's desktop twin, scored with outcome labels (Claude Haiku 5.5-low; correct-any = right with the right source shown + right from memory; WU = wrong with no warning). PACKPROOF (180 pack-written self-tests of 9 packs, 1.7B Succinct, seed 42): correct-any 0.48 with the pack vs 0.26 without, 0.65 when the item's own article is kept (54 % of items), 0 of 9 packs at 0.75. UXMATRIX (60 dev items): Succinct beats Detailed with and without the pack; with the pack off every honest "unknown" is an engine decline. Pack shaping (factbook rewritten as short sentences that name the country) doubled fact delivery (7 → 15 of 20) and correct answers (5 → 10) on its own self-tests, but missed its frozen rule by one new warned confident error. Overnight one closed tree, ENGINE-RC (SEFIX-124 + W78 + shaped factbook + a reworded banner), passed every 0-LLM suite (identity 97/97 and 180/180, routes 103/110, the one letter-FAIL pre-existing) and generated 2,855 answers with no judge call; the next day's judge kept Succinct (correct-any 0.43 vs 0.42 for longer styles, wrong-unwarned 0.12 vs 0.23–0.25).

**Fix box:** a false "Not found in this phone's offline library" line showed on 37 of 97 answers that had kept passages; after the fix, 0 [F-1725].

**Thesis box (the author, 2026-10-25; [F-2236], [D-215]):** "Small models need external knowledge. We learned that, and built a harness around a small model's real capabilities, tuned for the app user's experience." The harness in the shipped app: the health gate (fixed safe text when no health source is kept), QuickMath (conversions and arithmetic in code), pack search and delivery (the ported bench search, ON_NO_HEALTH), the Succinct persona, the fixed line "May contain errors; check the source." and fixed-text refusals (T18). Evidence: 48 % vs 26 % with the matching pack and 65 % vs 28 % when the article reaches the model (pack-written self-tests, Haiku labels, one seed). Limits: delivered on 54 %; 0 of 9 packs at 0.75; no gain on real dev items [F-2080]; the app's desktop-twin ruler reading is below the bar (T15). The 2026-10-23 sentence ("right whenever the content is in a pack") is the hypothesis these tests checked. Never "the harness makes it half as good" (U41).

Whole chapter: https://r4topunk.github.io/boar-research/research/closure.md

## 15 · One simple app: LabRat {#submission}

#### One closed APK: Qwen3-1.7B, 13 packs, Succinct only, a health gate, no INTERNET permission

On 2026-10-24 the author replaced the planned submission (the app maintainer's native app) with BoarLite, a new closed app of his own built from a clean branch of the native code: Qwen3-1.7B Q4_K_M fixed, English only, Succinct only (Deep Research, Detailed and the length setting removed), the full K13 pack kit with factbook v1 in one APK (3,044,169,517 B), and no INTERNET permission. At 18:03 the author changed two of the first choices: one fixed line ("May contain errors; check the source.") under every model answer replaces the ported warning trigger, and factbook v1 replaces the shaped v2 [D-196]. [sentence withheld in this file; see https://r4topunk.github.io/boar-research/data/ or the chapter record] On the 65 dev safety probes (0 LLM): 41 fixed text, 1 exposure answer, 23 model answers, identical with the search port off [F-2210]. Known limits: the health rules are fitted on those probes; 12 of 60 health self-tests whose article is only in a Wikipedia pack get the fixed text (shipped as is, [D-202]); the chat shows the streamed text, so the pipeline's citation-support cleaning is not applied on the plain path [F-2218]. On a Pixel 8a in airplane mode: unpack 3 GB in 14 s, 0 bytes network, PSS 3.09 GB after 5 answers, model ready 18 s after launch, first answer 11.9 s at 14.9 tok/s [F-2198] [F-2201]. Two UI-only commits after b4ef94f3 (0 engine files) led to the 6aa7508a APK, which passed its offline phone smoke ([F-2219], later superseded). Quality scores of the app are public since the author's decision of 2026-10-25 (AD-15 (b)): the desktop ruler run of b4ef94f3, as history (T15), and the search-port usefulness counts (S2 on the 51 changed UXMATRIX items: correct-with-source 9 → 15, correct-any 20 → 21, wrong-unwarned 31 → 30; [F-2208]). The app maintainer's app numbers stay internal.

After the author's screens review (UI only; [F-2220]), a cleanup round removed what a closed, Succinct-only app cannot reach, each as an owner decision: the Expo/React Native tree (the app is the native Android code only), the Detailed style, adaptive routing, persona and length options, Deep Research beyond the recap, the long-chat summary (on the Pixel the 1.7B used only the last 3 exchanges; [D-206] / [F-2221]), the PIN lock and sealed-chat legacy [D-207] and Portuguese [D-208]; Settings lost the Knowledge section and the title switch, 50 chats are kept instead of 10, and the MIT licence texts ship in About [D-209] [D-210] [F-2222]. 274 engine unit tests pass. On 2026-10-25 02:20, at the app maintainer's request, the app became **LabRat** and its assistant **Rat** (7788924a; same package id; [D-211] / [F-2224]), and logo n8 followed at 11:24 ([D-213] / [F-2226]). **Engine identity, stated precisely:** the rename changed the grounding prompt's identity line from "You are BOAR, an offline AI research app…" to "You are Rat, the assistant in LabRat, an offline AI research app…" [F-2225]; between b4ef94f3 and 7788924a the engine module changed in 124 files, almost all removals of code described as unreachable [F-2223] (the ruler run predates the Rat persona line). The ruler number (RULER-FINAL) is for b4ef94f3; DEVICE-FINAL measures LabRat 7788924a on the phone (the ruler run predates the Rat persona line). Known limitation, by the author's decision of 2026-10-25 not fixed before the measurement: the citation-support step (Citations.applyShown) is not applied to the streamed answer the chat shows; a fix would change the engine the judges install and need a ruler rerun ([F-2232]; AD-24). Hosting: Hugging Face (author's OK 2026-10-25; GitHub release assets must be under 2 GiB, the APK is 3.04 GB; [D-214] / [F-2230]). Install-path risk: Android developer verification (live since 2026-09-30 in four countries) may add an "advanced flow" for browser installs of unregistered apps; adb is exempt, the GrapheneOS test phone cannot show the judges' path, and a certified-phone test is planned [F-2231].

**Box: the search-port trade-off (SEARCHPORT, frozen criterion + two addenda; 0-LLM replays on MAIN 92 keyed facts and 180 pack self-tests; one seed for generated answers; AI-reviewed, not clinically reviewed).**

| stage | delivery (MAIN facts / own fact chunk / context) | safety on 65 probes | frozen verdict | what happened |
|---|---|---|---|---|
| B0 (native, no port) | 26 / 38 / p50 347 tokens | 4 invented-dose answers (before the health gate) | baseline | [F-2195] |
| P1 as ported | 47 / 74 / 2.33× | — | gate c FAIL | one fix allowed |
| P1 after the fix | 40 / 64 / 1.07× | 3 new dose-figure answers | **FAIL (gate d)** | switch off [D-198] |
| Addendum 1, grounded-dose rule | 40 / 64 / 1.07× | ungrounded figures 9 vs 5; 9 probes leave the fixed text | **FAIL** | switch off [D-201] |
[sentence withheld in this file; see https://r4topunk.github.io/boar-research/data/ or the chapter record]

**Box: DEVICE-FINAL (OF-8, landed 2026-10-25; criterion frozen 2026-10-25 03:3x before generation; [F-2227]).** M1 ruler v0.4 × seeds 42/43/44 on the Pixel 8a (Claude Opus all seeds, OpenAI gpt-5.6-sol seed 42); M2 65 safety probes; M3 140 on-K13 self-tests; M4 UXMATRIX 60; M5 speed, memory, offline. Claim numbers = M1 + M5; M2-M4 are product numbers. Interrupted once by an APK install (11:28) and restarted [F-2229]. Its M1 fills the status headline (win-rate first, both judge families, the lower family against the bar; S42; [F-2238]) and its rows are public (AD-15 (b)).

Whole chapter: https://r4topunk.github.io/boar-research/research/submission.md

## 18 · Reproduce it (appendix) {#reproduce}

#### Plug your app into the same answer key

Everything you need to measure your own assistant is public: 60 v0.1 questions (57 judged), frozen Opus-plus-web references with provenance, the judge, the scorers and the floor metric. Write one trace per question with `itemId`, `answer.text` and `error: null`, run the judge with your own Claude Code login, and compute the three scales. The research record holds frozen criteria, arm reports, aggregates, the negative-results registry and pack cards; the engine is a public upstream commit plus each arm's patch.

**Published 2026-10-27:** the retired held-out sets and the second ruler v0.4 (items, both reference halves, drafts) in boar-bench (`bench/heldout/`, `bench/v0.4/`), with their runs in boar-traces; byte-identical to the hashes committed before opening, except documented redactions. **Not reproducible:** bit-identical judge outputs, the detector runner profile (not released). Rerun steps: [How to reproduce the key results](https://github.com/r4topunk/boar-research#how-to-reproduce-the-key-results-step-by-step) in the boar-research README. **Still private:** personal correspondence, the app maintainer's data, usage and spend records, credentials, the private lab's working history (the public repos keep one commit per release; earlier releases remain in history).

**Open fronts (as of 2026-10-28):** nothing in this chapter is pending. DEVICE-FINAL (OF-8) landed on 2026-10-25; its arm is public in boar-research under rnd/research/coordinator/arms/device-final/ (report, frozen criterion with its sha256, aggregates, tools). DEVICE-FINAL's M1 raw phone outputs, traces and judgments are in boar-traces (rnd/research/coordinator/arms/device-final/, listed with sha256 in TRACES.tsv); RETBENCH, PACKPROOF, UXMATRIX and X2B-BUDGET have their reports, frozen criteria and aggregates in boar-research, and their raw runs and judgments are not published (boar-traces holds only the PACKPROOF and UXMATRIX request files). The two fronts still open, the claim text (OF-5) and the shaped-pack publication (OF-7), are listed with what would change in the status file; the dropped fronts (OF-1 deep tier on a phone, OF-2 expert streaming on Android, OF-3 v0.3) keep their decision ids.

Whole chapter: https://r4topunk.github.io/boar-research/research/reproduce.md

---

AI-reviewed, not clinically reviewed. Nothing here is medical advice.

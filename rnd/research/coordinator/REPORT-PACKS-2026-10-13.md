# Knowledge Packs for offline small-language-model assistants: crowding, routing, reach, keep and reader

Technical report, draft 2026-10-13. Artifact: the public dataset **hf.co/datasets/r4topunk/boar-packs** (11 packs: the 9 measured here plus 2 wave-3 packs; cards, licences, 20 public self-test items per pack).
All numbers below are copied from the cited files. Paths in citations are relative to the project's research coordinator directory unless stated. Status: complete (deep-tier topic packs added 2026-10-13 evening; Opus L2 cells added 21:14; engine-scope note on the T-K2 sources patch added in §5).

## 1. TL;DR

- **A single specialised pack helps the 4B model a little.** Over 180 pack-matched dev items, adding the matching pack lifts the quality ratio from 0.460 (0.437–0.484) to 0.493 (0.470–0.516). The paired Δ is **+0.032 (+0.016…+0.050)** (Haiku L1); Opus L2 on the same traces confirms it at **+0.042 (+0.024…+0.062)** (Q&A packs +0.048, topic packs +0.035 (+0.009…+0.062)). Win-rate against the gold answer is 0/180 with and without the pack (arms/packs/SELFTEST-SCORES.md; arms/packs-l2/PACKS-L2.md).
- **The lift tracks the keep step (descriptive, 9 packs).** The packs whose passages are kept on 15–16 of 20 items gain: simplewiki **+0.102 (+0.054…+0.157)**, ethereum-SE **+0.074 (+0.016…+0.133)** and bitcoin-SE **+0.054 (+0.017…+0.094)**. First aid (kept on 3/20) gains +0.004 (−0.027…+0.036) and factbook (5/20) −0.018 (−0.079…+0.026) under Haiku (arms/packs/SELFTEST-SCORES.md); at Opus L2 the topic family clears zero, **+0.035 (+0.009…+0.062)**, driven by simplewiki (+0.099), first aid (+0.028) and factbook (+0.017); MedlinePlus (−0.003) and health-SE (−0.003) stay ≈ 0 (arms/packs-l2/PACKS-L2.md).
- **The 35B deep tier shows no measurable gain from any pack (measurement, no verdict rule; first aid's 20 items take the health-strict path, so they are not a deep-tier measurement).** Over all 180 items it scores 0.546 (0.523–0.569) with the pack and 0.548 (0.525–0.569) without, Δ **−0.002 (−0.020…+0.016)**; Q&A packs −0.003 (−0.030…+0.026), topic packs −0.000 (−0.024…+0.023). Win is 0/180 with the pack (1 tie) and 1/180 without. With the same pack, the deep tier beats the 4B by **+0.054 (+0.034…+0.073)** (arms/packs/aggregates/selftest-deep.json; arms/packs/SELFTEST-DEEP.md).
- **Installing many packs causes crowding.** With all 9 packs installed as peers, the fact article is kept on **46/180** items, against **68/180** with the one relevant pack (−32 %) (arms/packroute/STEP0.md). The quality cost is **−0.016 (−0.033…−0.001)** overall and **−0.033 (−0.055…−0.011)** on the Q&A packs (Haiku); Opus L2 confirms it: **−0.019 (−0.035…−0.003)**, Q&A −0.029 (−0.055…−0.004), topic −0.006 (−0.023…+0.012). Win is 0/180 in both arms (arms/crowdq/CROWDQ.md; arms/packs-l2/PACKS-L2.md).
- **A general-knowledge pack takes the slots.** Under peers, Simple English Wikipedia holds 36 % of all kept slots (arms/crowdq/CROWDQ.md). Next to the base kit alone it takes 0.829 / 0.714 of kept slots (research/packs/boar-simplewiki-en.md).
- **Top-1 routing fails.** A deterministic vote router picks the right pack on 0.25 of items (arms/packroute/STEP0.md). The 4B as a zero-shot router reaches 0.58 / 0.61, against a 0.85 bar. A right route recovers the full single-pack value; a wrong route or "none" keeps nothing. Break-even against peers needs about 0.68 accuracy (arms/packroute2/ACCURACY.md; research/QUEUE.md "PACKROUTE-2 0b diagnostic").
- **Dense chunk vectors as extra keep-step slots improve reach far more than quality; through the §3.9 append path they do convert (X2b).** Two extra dense slots raise fact-chunk reach from 67 (top 6) to 108 (top 8) items. Opus L2 measures quality **+0.017 (−0.000…+0.035)**, which is **not decided at MDE 0.03**. Win is 0/180 without the extra slots, 0/180 (1 tie) with them (arms/densechunk-st/DENSECHUNK-ST2.md, ST2-GATE.md).
- **Grounding causes most keep-step losses.** It accounts for 18 of 24 fact-chunk losses (arms/groundst/D0.md). Three relaxed keep rules raise fact-article kept from 68 to 89/92/95 with 0 lost kit contexts, but fact-chunk kept only rises from 43 to 51/53/54, under a bar of 55 (arms/groundst/GATE.md).
- **The combined stack (keep rule + quota) is not decided at MDE 0.03.** With all packs installed, it raises fact-article kept from 46 to 72 and fact-chunk kept from 31 to 36, below its step-0 bar of 39 (arms/stack/GATE.md). Quality: **+0.005 (−0.009…+0.021)** overall, Q&A packs +0.018 (−0.000…+0.038), topic packs −0.010 (−0.032…+0.011) (Haiku); Opus L2: +0.004 (−0.010…+0.019), Q&A +0.012 (−0.008…+0.034). On the base kit it does no harm: −0.009 (−0.027…+0.007). Win is 0/180 (arms/stack/STACK.md; arms/packs-l2/PACKS-L2.md).
- **4B generation on the desktop CPU path is byte-deterministic**, so the 4B paired CIs above contain no generation noise: 20/20 identical answers on one pack's 20 items across 5 pairings, one of them 8 h apart; the deep tier was not probed (arms/seedgen/SEEDGEN.md).
- **Engine scope: cut 7 without the sources patch.** Every quality number here was generated without the T-K2 sources patch, while the replay reach counts come from a tree that carries it. The patch changes kept lists on 52/180 items, so the patched engine needs a judged re-score before its quality is stated (§5; arms/packs/tk2-replay/TK2-REPLAY.md).
- **The headroom is retrieval of the fact chunk, not the reader.** Injecting the item's known fact chunk as one extra kept passage lifts the 4B by **+0.095 (+0.070…+0.122)** over the single-pack run (Opus; Haiku +0.090); the fact chunk plus the article lead as the only context gives +0.115 (+0.088…+0.142). The gain sits on the 137 items whose run had not kept the fact chunk (+0.112), against +0.043 on the 43 that had, and is −0.007 on the 27 where the injected chunk itself was already kept. Opus wins are 0/180 (ties 1 for ADD, 4 for ONLY); Haiku gives 1/180 and 2/180 (arms/oracle-st/ORACLE-ST.md).
- **Appending the retrieved article's neighbour chunks (0 LLM) puts the fact chunk in 72/180 contexts and gives +0.033 (+0.016…+0.050)** (Opus, beyond its frozen plan; label capped) (§3.9).
- **Adding dense chunk candidates to the same append path under a per-item budget of +600 prompt tokens puts the fact chunk in 102/180 contexts and gives +0.066 (+0.043…+0.091) (Opus; Haiku +0.056) — a LEVER by its frozen rule on these pack-matched dev items, not a bounty-bar result; v0.1 + simplewiki no-harm +0.012 (−0.019…+0.046), kit-only runs unchanged. It needs format-v3 packs (≈ +60 % pack size) and adds ≈ 420 prompt tokens p50 (§3.9).**

## 2. Setting

**Application and bounty context (one paragraph).** The assistant runs fully offline on an Android phone. It targets an open bounty for an offline research assistant that is ">50 % as good as internet + frontier AI" in ≤ 12 GB RAM, in English. The claim-build fast path is a 4B instruct model (Qwen3-4B-Instruct-2507 Q4_K_M) with retrieval over installed packs (arms/packroute2/ACCURACY.md). The deep tier is Qwen3.6-35B-A3B UD-Q2_K_XL with a 512-token thinking budget (arms/packs/SELFTEST-DEEP-criterion.md). Floor-adjusted scores on the project's bounty-style dev sets are V-para 0.44 and v0.2 0.51 for the deep tier, against a 0.50 bar (v0.2 is a burnt dev set and its CI 0.467–0.550 straddles the bar, so the bar is not met), and the 4B claim build scores 0.26 (V-para) / 0.39 (v0.2, two seeds). Win-rate is 0 on every set (arms/dt512/DT512.md; arms/dt512v02/DT512V02.md; CLAIM-READINESS-2026-10-10.md). This report covers only the pack line. Every number in it is a dev number, not a claim.

**Pack format.** Each pack is one SQLite file (format 2): article text in zstd blocks, 1,000-character chunks with FTS, and a lead (first 2,500 characters) vector per article. Lead vectors come from bge-small-en-v1.5 q8_0 (384 dims; model sha ec38e8da…f514), shared by every pack (research/packs/README.md; research/packs/qa-travel-se.md; research/packs/selftest/README.md). A pack carries per-row `licence` and `attribution` fields, and the engine shows them in the citation string (PACK-CATALOGUE-2026-10-12.md §1). Retrieval returns a raw list of 6 passages. A keep step then filters it (substance check, compression to the context budget, an on-topic grounding test, a health filter) before the reader sees it (arms/groundst/D0.md). The base kit installed in every run is boar-crypto + boar-wikivoyage-en (arms/packs/SELFTEST-SCORES.md).

Terms: **raw** (retrieval) = the 6 passages before the keep step (distinct from the raw quality ratio); **kept** = the passages the reader sees; **fact chunk** = the pack chunk holding an item's verbatim evidence quote; **fact article** = the article that contains it (research/packs/selftest/README.md).

**The 11 published packs** (9 measured in §3, 2 wave-3) (research/packs/<id>.md; scores: 4B cut 7 without the T-K2 sources patch, Haiku L1, raw ratio with 95 % CI, from arms/packs/SELFTEST-SCORES.md; status from each card's crowding line).

| id | family | source | licence | articles / size | self-test with pack | without pack | status |
|---|---|---|---|---|---|---|---|
| qa-travel-se | Q&A | travel.stackexchange.com, archive.org dump 2024-04-02 | CC BY-SA 3.0/4.0 per post | 42,307 / 148.3 MB | 0.423 (0.360–0.484) | 0.394 (0.327–0.462) | user-selected only |
| qa-ethereum-se | Q&A | ethereum.stackexchange.com, same dump | CC BY-SA 3.0/4.0 per post | 34,588 / 102.5 MB | 0.516 (0.454–0.577) | 0.442 (0.375–0.512) | user-selected only |
| qa-bitcoin-se | Q&A | bitcoin.stackexchange.com, same dump | CC BY-SA 3.0/4.0 per post | 26,042 / 77.9 MB | 0.469 (0.382–0.556) | 0.415 (0.337–0.500) | user-selected only |
| qa-health-se | Q&A | medicalsciences.stackexchange.com, same dump | CC BY-SA 3.0/4.0 per post | 5,048 / 23.8 MB | 0.525 (0.463–0.586) | 0.509 (0.450–0.564) | default-eligible |
| qa-outdoors-se | Q&A | outdoors.stackexchange.com, same dump | CC BY-SA 3.0/4.0 per post | 5,872 / 31.6 MB | 0.518 (0.464–0.575) | 0.483 (0.424–0.541) | default-eligible |
| boar-firstaid-en | topic | Wikipedia, Wikivoyage, Wikibooks, Appropedia, US federal works, FM 21-76, ATP 4-02.11 (2026) | CC BY-SA + US public domain | 1,842 / 21.0 MB | 0.471 (0.414–0.529) | 0.468 (0.419–0.518) | default-eligible |
| boar-medlineplus-en | topic | MedlinePlus Health Topics XML (2026-10-10), NLM summaries only | public domain (NLM), credit line | 1,016 / 4.3 MB | 0.508 (0.442–0.574) | 0.506 (0.441–0.574) | default-eligible |
| boar-factbook | topic | CIA World Factbook CC0 JSON archive, snapshot 2026-09-11 | CC0 | 261 / 11.6 MB | 0.438 (0.378–0.501) | 0.456 (0.393–0.521) | user-selected only |
| boar-simplewiki-en | topic | Simple English Wikipedia dump 2026-10-01 | CC BY-SA 4.0 (Wikipedia text is also GFDL) | 208,622 / 480.5 MB | 0.566 (0.483–0.640) | 0.465 (0.386–0.542) | user-selected only |
| qa-cooking-se (wave 3) | Q&A | cooking.stackexchange.com, same dump | CC BY-SA 2.5/3.0/4.0 per post | 25,698 / 89.0 MB | 0.464 (0.391–0.531) | 0.454 (0.386–0.520) | default-eligible |
| qa-money-se (wave 3) | Q&A | money.stackexchange.com, same dump | CC BY-SA 2.5/3.0/4.0 per post | 35,102 / 137.2 MB | 0.456 (0.394–0.516) | 0.425 (0.378–0.471) | user-selected only |

All 9 rows have win/tie/loss against gold of 0/0/20 (arms/packs/SELFTEST-SCORES.md). The four health and safety packs (qa-health-se, qa-outdoors-se, boar-firstaid-en, boar-medlineplus-en) carry the caveat "AI-reviewed, not clinically reviewed" on their cards (research/packs/qa-health-se.md, qa-outdoors-se.md, boar-firstaid-en.md, boar-medlineplus-en.md).
The two wave-3 packs were built and published after the main measurements (2026-10-13 evening); their self-test Δ is +0.010 (−0.039…+0.065) and +0.030 (−0.007…+0.072) under Haiku (pooled 40: +0.020 (−0.011…+0.054)) and +0.045 (+0.007…+0.087) pooled under Opus (cooking +0.053, money +0.038); neither pack's Haiku CI clears zero. qa-cooking-se carries the "AI-reviewed, not clinically reviewed" caveat for food-safety answers (research/packs/qa-cooking-se.md) (arms/packs/WAVE3.md; arms/packs-l2/PACKS-L2.md). They are not part of the 180-item measurements below.

A pack is "default-eligible" when it passes a crowding probe next to the base kit. Its share of kept slots must be ≤ 0.40 and the kit's gold must not be lower (PACK-CATALOGUE-2026-10-12.md §1). Travel, ethereum and bitcoin SE pass the share rule (0.316 / 0.110 / 0.146 on v0.2) but displace kit gold (research/packs/qa-travel-se.md, qa-ethereum-se.md, qa-bitcoin-se.md). Factbook is borderline on gold (research/packs/boar-factbook.md). Simplewiki fails the share rule (research/packs/boar-simplewiki-en.md).

**The 180 self-test items.** Each pack has 20 public questions. A seeded draw (seed 11) takes 60 candidate articles across length × popularity strata. The writing agent picked 20 of them for domain breadth and logged a reason for each of the 40 rejects. An agent wrote each question from the pack's own text and added a gold answer, a rubric and verbatim in-pack evidence (research/packs/selftest/README.md). Example (qa-outdoors-se): "I sail about once a month and recently got badly seasick in rough water. What can I do to keep it from happening again?" (research/packs/selftest/qa-outdoors-se.jsonl). These items are **dev data**. They are written by a Claude-family agent from the very text the pack contains, so they favour the pack and are never claim items (arms/packs/SELFTEST-SCORES.md "Caveats"; PACK-CATALOGUE-2026-10-12.md §1).

**Judge protocol.**
- Metric definitions: the judge scores the system answer and the gold answer on correctness, completeness and usefulness (1–5) in both presentation orders. **raw** = Σ system mean rubric / Σ reference mean rubric. **above_min** = the same ratio after removing the rubric minimum. above_min is the project's "floor-adjusted" score. Win/tie/loss is per item against gold: a win or loss needs the same judge winner in both orders, and a split verdict counts as a tie (boar-eval bench/v0.2/plan/floor_metrics.py; arms/packs/tools/localjudge_agg.py).
- L1 is Haiku 5.5 at low effort, run as 4 parallel shards over both orders (arms/L1-PROTOCOL.md, PARJUDGE addendum). L2 is Opus (judge.v1), used for confirmation (arms/L1-PROTOCOL.md).
- Haiku compresses paired gaps. On one deep-tier comparison it measured +0.007 where Opus measured +0.029. A Haiku Δ within 0.01 of a decision threshold therefore goes to Opus (arms/L1-PROTOCOL.md, HAIKUJUDGE and 2026-10-10 addenda).
- Δ is a paired per-item bootstrap of the ratio-of-sums difference (B 2000, seed 11) (arms/packs/SELFTEST-SCORES.md).
- The MDE is ≈ 0.03 raw paired at n 180 (arms/crowdq/CROWDQ-criterion.md; arms/stack/STACK2-criterion.md). Every decision criterion is frozen with a sha256 before its run (arms/_lib/CRITERION-TEMPLATE.md).
- The MDE (minimum detectable effect) is the smallest paired Δ the design resolves. "Not decided at MDE 0.03" means the CI includes 0 and |Δ| < 0.03; it is not evidence of no effect.

**Determinism.** The 4B desktop server path is byte-deterministic: seed 42 on every request, one slot, no prompt cache, a CPU build and a fixed thread count. An A/A probe gave 20/20 identical answers across 5 pairings, one of them with an 8 h gap. Runs are compared by prompt identity, never by kept titles, and are comparable only on the same machine, build and thread count (arms/seedgen/SEEDGEN.md; RULE-CHANGES.md row 27). The deep tier was not probed for determinism (arms/seedgen/SEEDGEN.md).

Health and safety pack results below are dev numbers; those packs are "AI-reviewed, not clinically reviewed".

## 3. Results

### 3.1 Pack value on the 4B (one pack installed)
- **Pooled over 180 items:** with pack 0.493 (0.470–0.516), without 0.460 (0.437–0.484). Paired Δ **+0.032 (+0.016…+0.050)**, above_min Δ +0.042 (+0.021…+0.065), items better/worse 93/50, win 0/180 (arms/packs/SELFTEST-SCORES.md).
- **Per pack Δ (raw):**

| pack | Δ (95 % CI) |
|---|---|
| simplewiki | +0.102 (+0.054…+0.157) |
| ethereum-SE | +0.074 (+0.016…+0.133) |
| bitcoin-SE | +0.054 (+0.017…+0.094) |
| outdoors-SE | +0.035 (−0.021…+0.099) |
| travel-SE | +0.029 (−0.022…+0.077) |
| health-SE | +0.016 (−0.014…+0.046) |
| firstaid | +0.004 (−0.027…+0.036) |
| medlineplus | +0.002 (−0.055…+0.044) |
| factbook | −0.018 (−0.079…+0.026) |

  (arms/packs/SELFTEST-SCORES.md)
- **The lift tracks keep:** pack passages are kept on 15–16/20 items for the three packs that gain, 3/20 for first aid and 5/20 for factbook. MedlinePlus is the exception: its passages are kept on 12/20 items and the fact article on 11/20, yet Δ ≈ 0. Untested readings: the 4B's answer of about 50 words does not use the passage, or the closed-book answer was already as good (arms/packs/SELFTEST-SCORES.md).
- **Local-judge side check** (Qwen3.6-35B as judge, travel only): it picks the same winner as Haiku on 19/20 items, with Pearson r 0.915. Its travel Δ is +0.042 (+0.005…+0.087), against Haiku's +0.029 (arms/packs/SELFTEST-SCORES.md).
- **Opus L2 on the same traces** (judge.v1, N=4 both orders, 1,240 calls over the pack-line cells): single pack vs kit **+0.042 (+0.024…+0.062)**, above_min +0.053 (+0.030…+0.078), items better/worse 74/36; Q&A +0.048 (+0.022…+0.078), topic +0.035 (+0.009…+0.062); per pack bitcoin +0.093, simplewiki +0.099, ethereum +0.069, outdoors +0.066, first aid +0.028, travel +0.015, factbook +0.017, health −0.003, MedlinePlus −0.003. Opus rates the lift larger than Haiku, as the L1 protocol predicts (arms/packs-l2/PACKS-L2.md).

### 3.2 Deep tier and packs
The deep tier (35B MoE, thinking 512) runs on the same items, with and without the pack, judged by Haiku L1. The criterion is a measurement with no verdict rule; it expected about +0.03 (arms/packs/SELFTEST-DEEP-criterion.md).
- **Q&A half (5 SE packs, 100 items):** with 0.553 (0.522–0.584), without 0.555 (0.525–0.586). Δ **−0.003 (−0.030…+0.026)**, above_min −0.003 (−0.038…+0.033), items better/worse 46/41. Win/tie/loss is 0/1/99 with the pack and 1/0/99 without (arms/packs/aggregates/selftest-deep.partial-se.json).
- **Per pack Δ:** travel −0.007 (−0.071…+0.048), ethereum +0.007 (−0.067…+0.089), bitcoin −0.034 (−0.083…+0.009), health −0.016 (−0.058…+0.026), outdoors +0.036 (−0.018…+0.096) (arms/packs/aggregates/selftest-deep.partial-se.json).
- **The deep tier keeps the passages:** pack passages are kept on 10–18/20 items (22–42 of 26–47 kept slots), yet quality does not move. One untested reading is that the 35B already knows these Q&A-site facts closed-book. For comparison, the 4B gains on the same packs: +0.029/+0.074/+0.054/+0.016/+0.035 (research/QUEUE.md "SELFTEST-DEEP 10/18").
- **Deep with pack vs 4B with pack:** **+0.063 (+0.037…+0.090)**, above_min +0.079 (+0.046…+0.114), items better/worse 60/26 (arms/packs/aggregates/selftest-deep.partial-se.json).
- **Cost:** median wall time per item on the desktop is 86–102 s with the pack and 82–92 s without (arms/packs/aggregates/selftest-deep.partial-se.json).

- **Topic half (4 topic packs, 80 items):** with 0.539 (0.505–0.573), without 0.539 (0.506–0.573), Δ **−0.000 (−0.024…+0.023)** (arms/packs/aggregates/selftest-deep.topic.json). Per pack: first aid +0.013 (−0.028…+0.051) (health-strict path, no deep prompt), MedlinePlus **−0.049 (−0.104…−0.002)**, factbook +0.004 (−0.015…+0.023), simplewiki +0.032 (−0.020…+0.090) (arms/packs/SELFTEST-DEEP.md).
- **Pooled 180:** with 0.546 (0.523–0.569), without 0.548 (0.525–0.569), Δ **−0.002 (−0.020…+0.016)**, above_min −0.002 (−0.025…+0.020), better/worse 76/70; win/tie/loss 0/1/179 with the pack, 1/0/179 without. Deep with pack vs 4B with pack **+0.054 (+0.034…+0.073)** (arms/packs/aggregates/selftest-deep.json). The pre-declared split (BACKLOG META 10-13, H11) expected a topic-pack gain; that half was not confirmed (topic Δ −0.000 (−0.024…+0.023)), while the SE half matched its prediction.

### 3.3 Crowding when many packs are installed
Setup: base kit + all 9 packs installed as peers (P), compared with the one relevant pack (S), on the same 180 items.
- **Reach (replay):** fact article kept 68 (S) → **46 (P)**, fact chunk in raw top-6 67 → 42 (arms/packroute/STEP0.md).
  - Q&A family: 24/28 → 10/14 (chunk raw6 / article kept).
  - Topic family: 43/40 → 32/32.
  - Installing all 9 packs also removes a kept kit source on 4 of 170 dev items (arms/packroute/STEP0.md).
- **Reach (generation traces, URL match):** fact article kept 59 → 41. Kept slots from the item's own pack fall from 201 to 118 (arms/crowdq/CROWDQ.md).
- **Quality (Haiku L1):** S 0.493 → P 0.476, paired Δ **−0.016 (−0.033…−0.001)**, above_min −0.021 (−0.042…−0.001), items better/worse/same 48/74/58. Win/tie/loss is 0/0/180 in both arms (arms/crowdq/CROWDQ.md; arms/crowdq/aggregates/crowdq.json).
  - Q&A family: **−0.033 (−0.055…−0.011)**.
  - Topic family: +0.004 (−0.017…+0.026).
  - The criterion's reading is "cost small": real (CI high < 0) but under the MDE (arms/crowdq/CROWDQ.md).
  - Opus L2 on the same traces: **−0.019 (−0.035…−0.003)**, above_min −0.024 (−0.044…−0.005); Q&A −0.029 (−0.055…−0.004), topic −0.006 (−0.023…+0.012) — cost confirmed (arms/packs-l2/PACKS-L2.md).
- **Who takes the slots:** simplewiki holds 66 of the 164 foreign kept slots under P (40 %) and 36 % of all kept slots (arms/crowdq/CROWDQ.md).
  - MedlinePlus and factbook lose most of their own passages, mostly to simplewiki, with no measured quality loss (Δ +0.009 (−0.043…+0.072) and +0.016 (−0.030…+0.068)): their own kept slots fall from 25 to 4 and from 7 to 1.
  - The Q&A packs have no such stand-in and carry the cost. Ethereum-SE loses −0.062 (−0.113…−0.017) even though its fact article stays kept (7 → 7) (arms/crowdq/CROWDQ.md).
- **Earlier probes against the base kit point the same way:** a 2.54 GB English Wikipedia top-100k pack took 98 % of kept slots on the v0.2 items it covered (62 % overall share, DEEPWIKI), and simplewiki 0.829 (v0.2) / 0.714 (v0.1) (research/packs/README.md; research/packs/boar-simplewiki-en.md).

### 3.4 Routing
Two top-1 routers were tested: each picks one pack (or "none") per question, and retrieval then searches only that pack.
- **Deterministic vote router** (lead cosine / FTS share / title votes):
  - Picks the item's own pack on **45/180 (0.25)**, and "none" on only 6 of 24 kit items. Simplewiki attracts the general questions (arms/packroute/STEP0.md).
  - Reach under this router (25 fact chunks in raw / 25 fact articles kept) is below peers (42 / 46).
- **4B zero-shot classifier** over one-line pack descriptions: own pack **105/180 (0.58)** with the first wording and **109/180 (0.61)** with the retry wording (3 example questions per pack). The bar was ≥ 153 (0.85). It answers "none" on 10 / 11 of 24 kit items (arms/packroute2/ACCURACY.md).
- **Where the classifier goes wrong:** the errors are structural, not wording. MedlinePlus questions are routed to health-SE 12 [15] times; simplewiki questions go to "none" 15 [18] times; outdoors questions go to first aid 10 [5] times (first wording, retry in brackets) (arms/packroute2/ACCURACY.md).
- **All-or-nothing arithmetic:** routing is all-or-nothing per item (fact article kept; S / P / router; retry routes; arms/packroute2/ACCURACY.md §0b).

| route outcome | items | S | P | router |
|---|---|---|---|---|
| own pack | 109 | 33 | 22 | **33** |
| other pack | 36 | 16 | 5 | 0 |
| none | 33 | 18 | 15 | 0 |
| invalid (= every pack) | 2 | 0 | 0 | 0 |

  - Net reach: router 31 against peers 46 and single pack 68. A "none → peers with quota" fallback reaches 49.
  - Break-even with peers needs about 0.68 accuracy (0.256/0.378); reaching 90 % of the single-pack value needs about 0.9 (research/QUEUE.md "PACKROUTE-2 0b diagnostic").
- **Latency:** the classifier call costs 619 ms (first wording) / 668 ms (retry) p50 with a cached prefix, and 5,076 / 9,518 ms cold, on a desktop CPU (Apple M1 Pro, 4 threads). The phone estimate is ×3, about 1.9–2.0 s cached. Retrieval behind a route is ×0.34–0.37 of peers, router call excluded (arms/packroute2/ACCURACY.md).
- **Quota alone** (at most 2 of the 6 slots per pack) raises fact-article kept from 46 to 51, at ×1.29 retrieval time and 5 lost kit contexts on v0.2 (arms/packroute/STEP0.md).
- Both routers are closed at step 0 (CLOSED.md row 48).

### 3.5 Reach: dense chunk vectors as extra slots
Format-2 packs embed only article leads, so the engine cannot reach a fact deep in an article by vector search.
- **First attempt: fusion** (dense chunks merged into the raw list):
  - Fact chunk in raw6 rises from 67 to 95 and fact article kept from 68 to 95 (arms/densechunk-st/GATE.md).
  - It failed no-harm: empty contexts rise by 2 per set, because dense candidates that fail grounding displace lexical hits that would have survived.
- **Second attempt: two dense chunks appended as extra slots** (no displacement) (arms/densechunk-st/ST2-GATE.md):

| measure | without extra slots | with extra slots |
|---|---|---|
| fact chunk in raw | 67 (top 6) | **108** (top 8) |
| fact chunk kept | 43 | 61 |
| fact article kept | 68 | 100 |

  - Items: chunk kept +18/−0, article kept +32/−0. No item lost its whole kept context, but compression cut a previously kept chunk on 11/180 items (arms/densechunk-st/ST2-GATE.md, caveat 1).
  - Retrieval p50 is ×1.44; the simplewiki scan p50 is 108 ms.
  - Step 0 failed by the letter of the frozen no-harm rule (empty contexts +1 / +3). It passed under a corrected statistic written before any judge call (RULE-CHANGES.md row 26; arms/densechunk-st/DENSECHUNK-ST2-criterion-addendum-1.md).
- **Quality:**
  - Haiku L1: **+0.015 (−0.002…+0.031)**.
  - Opus L2: 0.500 → 0.518, **+0.017 (−0.000…+0.035)**, above_min +0.022 (0.000…+0.045). Topic packs +0.026 (−0.002…+0.058), Q&A +0.010 (−0.010…+0.031).
  - Win/tie/loss: 0/0/180 without the extra slots, 0/1/179 with them.
  - Verdict: **not decided at MDE 0.03** (arms/densechunk-st/DENSECHUNK-ST2.md).
- **Correction:** an early note blamed generation noise for part of the variance. SEEDGEN showed this was a keying artefact, so the +0.017 is the effect at n 180 (arms/densechunk-st/DENSECHUNK-ST2.md "Correction"; arms/seedgen/SEEDGEN.md).
- The chunk-vector format was not shipped, and its 1.8 GB of sidecar copies were deleted; they can be rebuilt (arms/densechunk-st/DENSECHUNK-ST2.md; CLOSED.md row 46).

### 3.6 Keep step
Setup: kit + one pack, 180 items, replays only (0 judge calls).
- **Loss classes** (passage in raw6 but not kept):
  - Fact chunk, 24 losses: grounding **18**, health filter 4, compression 2.
  - Fact article, 39 losses: grounding 31, health filter 5, compression 3 (arms/groundst/D0.md).
- **Three relaxed keep rules for pack passages:**
  - "ground": a full-text on-topic test, one compression cut pinned back, a top-2 fallback.
  - "top1": always keep the first pack hit.
  - "perpack": keep each pack's top hit (arms/groundst/GATE.md).

| rule | fact chunk kept (bar 55; 67 in raw6, 63 outside the health filter) | fact article kept (bar 85) | p50 vs OFF (ground/top1: retrieval only; perpack: retrieval + keep) |
|---|---|---|---|
| none | 43 | 68 | – |
| ground | 51 | 89 | ×1.03 |
| top1 | 53 | 92 | ×1.04 |
| perpack | 54 | 95 | ×0.99 |

  (arms/groundst/GATE.md)
- **No harm on the kit:** lost kit contexts 0. Empty contexts over items that retrieved before fall from 11 to 2 (v0.1) and 28 to 2 (v0.2). Kit gold is never lower. Kit kept lists change on 29–39 % of dev items, all add-only (arms/groundst/GATE.md).
- **Why the chunk bar was missed:** on the 7 chunks that no rule recovers, the fact is the pack's 2nd–4th passage behind the same pack's best hit. A per-pack top-1 rule cannot reach it; only a rule that keeps more than one passage per pack can (arms/groundst/D0.md, addendum).
- The family failed step 0 by one item on the chunk bar; the perpack rule was carried into the stack (CLOSED.md row 47).

### 3.7 The combined stack (keep rule + quota)
Setup: X = perpack keep rule + quota 2/6, against P = peers, with all 9 packs + kit installed.
- **Step 0 (replay):**

| measure | P | X | bar |
|---|---|---|---|
| fact article kept | 46 | **72** | 56 (pass) |
| fact chunk kept | 31 | **36** | 39 (fail) |

  - The two components pull against each other on chunks: perpack alone 31 → 36, quota alone 31 → 28.
  - X removes P's lost kit contexts (1 → 0 on v0.1, 3 → 0 on v0.2). Retrieval + keep p50 is ×0.98 (arms/stack/GATE.md).
- **Quality (STACK-2, Haiku L1):** P 0.476 → X 0.481, Δ **+0.005 (−0.009…+0.021)**, above_min +0.007 (−0.011…+0.026), items better/worse/same 73/63/44. Win is 0/180 in both (arms/stack/STACK.md).
  - Q&A family: **+0.018 (−0.000…+0.038)**.
  - Topic family: −0.010 (−0.032…+0.011).
  - X − S: −0.011 (−0.027…+0.005) (Opus −0.014 (−0.032…+0.003)), so X recovers about a third of the crowding cost under Haiku and about a quarter under Opus.
  - Verdict: **not decided at MDE 0.03** (arms/stack/STACK.md). A later Opus L2 pass on the same traces gives +0.004 (−0.010…+0.019), Q&A +0.012 (−0.008…+0.034), topic −0.005 (−0.024…+0.014); the verdict and the "optional setting" reading stand (arms/packs-l2/PACKS-L2.md).
- **No harm on the public v0.1 set** (kit only, 57 judged items): ON − OFF −0.009 (−0.027…+0.007) (arms/stack/STACK.md).
- **Reach in traces:** fact article kept S 59 → P 41 → X 57 (exact URL match; the earlier substring match counted 58; arms/stack/STACK.md; PIPELINE-AUDIT-2026-10-13.md F9). Simplewiki's share of kept slots falls from 36 % to 27 %. The added slots are mostly foreign: X fills the context rather than targeting the item's own pack (arms/stack/STACK.md).
- **Overall ledger on the 180 items** (4B, Haiku; research/QUEUE.md "STACK-2"):
  - one pack: +0.032 (Haiku) / +0.042 (Opus)
  - net under peers: +0.016 (Haiku) / +0.023 (Opus, derived)
  - dense extra slots: +0.017 (Opus)
  - keep rule + quota: +0.005 (Haiku) / +0.004 (Opus)
  - routing: closed
  - deep tier over the 4B: +0.063 with the same Q&A pack (+0.054 (+0.034…+0.073) pooled over all 180)
  - oracle (fact chunk kept): +0.095 (Opus) — the ceiling for retrieval-side levers on this set
  - neighbour-chunk append outside the keep step (§3.9, 2026-10-14): +0.033 (Opus; measured beyond its frozen plan)
  - + budgeted dense candidates on the same path (X2b, §3.9): +0.066 (+0.043…+0.091) (Opus; LEVER by its frozen rule)
  - The entries come from different comparisons (one judged by Opus) and do not add. "Net under peers" is derived as +0.032 − 0.016 (Haiku) and +0.042 − 0.019 (Opus), with no CI.

### 3.8 Oracle: what the fact chunk is worth when it is kept
Setup: the item's known fact chunk (the pack chunk holding its evidence quote) is appended as one extra kept passage to the single-pack run's own context (ADD), or shown with the article lead as the only context (ONLY); 4B cut 7, 180 items, existing S traces as the control, Opus and Haiku judges (arms/oracle-st/ORACLE-ST.md).

| split | ADD − S (Opus) | ONLY − S (Opus) |
|---|---|---|
| pooled 180 | **+0.095 (+0.070…+0.122)** | **+0.115 (+0.088…+0.142)** |
| Q&A packs (100) / topic packs (80) | +0.112 / +0.075 | +0.126 / +0.102 |
| S kept the fact chunk (43) / did not (137) | +0.043 / +0.112 | +0.071 / +0.129 |
| oracle chunk already kept (27) | −0.007 | +0.039 |

- Levels: S 0.500 → ADD 0.596 → ONLY 0.616 (Opus raw); items better/worse 96/38 (ADD), 121/36 (ONLY); win 0/180 under Opus (ties 1 / 4), 1/180 and 2/180 under Haiku.
- Reading: once the fact chunk is in the context, the rest of the kept context is worth nothing or slightly less (ONLY ≥ ADD). The measured engine levers moved the fact-chunk-kept count by +11 (keep rules) to +18 (dense extra slots) of the 137 missing, and their quality effects (+0.005 to +0.017) are consistent in size with that (not tested). The bound on this set is reaching and keeping the fact chunk, not the 4B's reading of it.
- Consequence for the lever list: build-time document expansion / contextual chunk headers (a better lexical index of the chunk) ranks first (written before X2b, §3.9; both were later closed at step 0, R72 and the H8-ST gate); reader-side levers target a smaller bucket: the oracle adds +0.043 on the 43 items whose fact chunk was already kept, and the source puts the reader bucket at ≤ +0.04.

### 3.9 Post-script (2026-10-14): appending the retrieved article's neighbour chunks outside the keep step
Setup: X1 = after grounding, append chunks 1–2 (by position) of the article of the first retrieved pack passage, skipping chunks already kept, with no displacement and outside the on-topic / compression steps (the oracle's append path); 0 LLM; one pack installed; 4B cut 7; 180 items; Haiku L1 then Opus L2 on the same traces vs the single-pack control (arms/headpass-st/HEADPASS-ST.md).
- **Reach:** fact chunk present in the final context 35 → 72 of 180 (replay; Q&A packs 10 → 38, topic packs 25 → 34); fires on 127 items, +282 prompt tokens p50 on fired items; kit-only runs byte-identical; v0.1 + simplewiki no-harm +0.004 (−0.018…+0.025) (Haiku). The replay and the generation used the same cut-7 tree without the sources patch (default-off identity vs that reference 180/180).
- **Quality:** Haiku +0.023 (+0.009…+0.038); Opus (measured beyond the frozen plan; label capped at "not decidable at MDE 0.03") **+0.033 (+0.016…+0.050)**, above_min +0.041 (+0.020…+0.063), items better/worse 65/45, win 0/180. Q&A packs +0.052 (+0.027…+0.079), topic packs +0.008 (−0.012…+0.029). Declared split (Opus): fact chunk newly present (37 items) **+0.119 (+0.069…+0.172)**; only non-fact neighbours appended (81) +0.012 (−0.012…+0.039); prompt unchanged (53) +0.003 (−0.007…+0.014). Simplewiki −0.024 (−0.081…+0.030) is the one pack with a negative point estimate (n 20).
- **Status:** the frozen step-0 power line (fact present ≥ OFF + 40) was missed by 3 items and the reach bar (79 < 90) was missed too, so the criterion's label is "not decidable at MDE 0.03"; the Opus pass was run beyond that plan and is reported as a measurement. Reading: X1 converts a newly present fact chunk at about the oracle's rate (+0.119 on the 37 newly present items vs the oracle's +0.112 on the 137 items whose single-pack run had not kept the fact chunk; overlapping CIs) and costs ≈ 0 on non-fact neighbours; reach (72/180) limits it.
- **X2b (2026-10-14): the same append path fed by the dense chunk candidates of §3.5, under a per-item budget of the single-pack prompt + 600 tokens** (X1's neighbour chunks first, then dense candidates in cosine order, stopping at the budget; frozen as a declared variant after the unbudgeted version failed its cost gate by 20 tokens). Reach: fact chunk present 35 → 102/180 (Q&A 10 → 47, topic 25 → 55), 153 reachable; kit-only runs byte-identical; v0.1 + simplewiki lost-context 0; retrieval p50 ×1.07; prompt tokens p50 963 (max +595 per item). Quality vs the single-pack run, Opus declared up front: **+0.066 (+0.043…+0.091)** raw, Haiku +0.056 (+0.036…+0.076); Q&A packs +0.070, topic packs +0.061; declared split (Opus): fact newly present (30) +0.177 (+0.098…+0.263), present under X1 already (71) +0.081, non-fact chunks only (65) +0.008, unchanged (14) +0.025; X2b − X1 +0.034 (+0.014…+0.054); v0.1 + simplewiki ON − OFF +0.012 (−0.019…+0.046); win 0/180. **Verdict by the frozen rule: LEVER** on this dev set (arms/headpass-st/HEADPASS-ST.md, X2-GATE.md, aggregates/l2-opus-x2b.json). Costs: format-v3 sidecars (+≈ 60 % pack size), dense scan p50 95 ms, +≈ 420 prompt tokens p50; the health-strict detector differs between replay and generation on 23 items (raw retrieval identical). The generation adapter was replaced by one that forwards retrieve options; an identity run gave 20/20 identical traces on every field across three adapter pairings. The unbudgeted X2 failed its cost gate and stays FAIL. Scope: pack-matched dev items, agent-written gold, one seed; not a bounty-bar lever (V-para is not pack-matched).

## 4. What this means for an offline SLM assistant

1. **Ship small specialised packs that the user selects.** Do not rely on automatic top-1 routing. One relevant pack beats every multi-pack install measured (peers, routers, stack): fact article kept 68/180, quality Δ +0.032 over the kit alone (Opus +0.042). At the measured accuracies (0.25, 0.58–0.61), a top-1 router keeps less than installing everything as peers (31 vs 46) (§3.1, §3.4).
2. **Routing among overlapping packs is the hard part.** Selecting the right pack fails mostly where packs overlap (consumer health vs medical Q&A vs first aid) and where a "general" option collides with a general encyclopedia. Because routing is all-or-nothing, a router must reach ≈ 0.68 accuracy just to tie with peers on fact-article reach (§3.4).
3. **A general-knowledge pack crowds specialised ones.** As a peer, Simple English Wikipedia takes 36 % of kept slots with all packs installed and 71–83 % next to the base kit. Treat it as user-selected only, never default (§3.3).
4. **Crowding costs more on Q&A packs than on topic packs.** The Q&A family loses −0.033 (−0.055…−0.011) under peers (Opus −0.029 (−0.055…−0.004)), while the topic family is +0.004 (Opus −0.006), consistent with a general encyclopedia standing in for small topic packs (not tested) (§3.3).
5. **Measure reach, keep and quality separately — and count the fact chunk kept.** Appending the retrieved article's neighbour chunks outside the keep step put the fact chunk in 72/180 contexts and gave +0.033 (Opus, measured beyond its frozen plan; label capped), +0.119 where the chunk became present; adding budgeted dense candidates to the same path reached 102/180 and gave +0.066 (+0.043…+0.091), a LEVER by its frozen rule on these dev items (§3.9). +41 raw fact chunks (dense extra slots) became +18 kept and +0.017 (Opus); +26 kept fact articles (stack) gave +0.005 (§3.5, §3.7). The oracle shows what a kept fact chunk is worth: +0.095 pooled, +0.112 where it was missing (§3.8). Gains that stop at raw or at the article level have paid little so far; the kept fact chunk is where the measured headroom is.
6. **Grounding is the main keep-step loss.** A per-pack keep rule recovers kept articles (68 → 95) with no lost kit context. Kept facts on a pack's 2nd–4th passage need a multi-passage rule (§3.6).
7. **For format-v3 packs (chunk vectors), make the budgeted append (X2b) the default, at ≈ +60 % pack size and ≈ +420 prompt tokens p50 (dev-set LEVER, §3.9). The keep rule + quota can be offered as an optional setting** for many-pack installs: it removes the kit's lost contexts, costs ×0.98 in retrieval time, does no harm on the public set, and moves Q&A packs by +0.018 (−0.000…+0.038) (Opus +0.012 (−0.008…+0.034)). The keep rule + quota is not decided at MDE 0.03 and should not be the default (§3.7).
8. **The reader is not the wall on pack-matched questions.** With the fact chunk kept, the 4B gains +0.095 (§3.8); MedlinePlus is the exception where kept passages do not help (passages kept on 12/20 items, +0.002 under Haiku, −0.003 under Opus). Win-rate against gold stays at most 2/180 in every configuration (the oracle under Haiku; Opus 0/180), so the gold answers remain out of reach even with the fact in context (§3.1, §3.8).
9. **A larger reader gains nothing measurable from any pack.** The 35B deep tier gains −0.002 (−0.020…+0.016) pooled (Q&A −0.003, topic −0.000; MedlinePlus −0.049 (−0.104…−0.002)), but is +0.054 (+0.034…+0.073) over the 4B with the same pack. Pack value should be stated per reader; for the deep tier the packs add latency (desktop p50 +4…+14 s) and no measured quality; MedlinePlus is the only per-pack CI that excludes 0, and it is negative (n 20, one seed, descriptive) (§3.2; arms/packs/SELFTEST-DEEP.md).
10. **Generation must be deterministic before paired tests on n ≈ 180 are read.** Fix the seed, use one slot and no prompt cache, and pair runs on prompt identity (§2; arms/seedgen/SEEDGEN.md).
11. **Handle licences and attribution per row.** Each Stack Exchange row credits its authors and question URL under the post's CC BY-SA version. MedlinePlus rows carry the NLM credit line. NC, NHS and A.D.A.M. content is excluded. The SE source is the archive.org 2024-04-02 snapshot, not dumps obtained under the 2024 login agreement (PACK-CATALOGUE-2026-10-12.md §1; research/packs/qa-travel-se.md).
12. **Keep the health caveat in every surface.** Health and safety packs ship as "AI-reviewed, not clinically reviewed". Community answers should rank below public-domain clinical sources (research/packs/qa-health-se.md).

## 5. Limitations

- **Dev set only.** The 180 items are public and pack-matched, so they measure a pack on questions its text can answer. They are not a claim set. Held-out pack-matched items would need a non-Claude writer (PACK-CATALOGUE-2026-10-12.md §1).
- **Agent-written gold.** A Claude-family agent wrote the questions and gold answers from the pack text, which favours the pack (arms/packs/SELFTEST-SCORES.md).
- **Haiku compresses gaps.** Most Δs here are Haiku L1. The three main cells (single pack vs kit, peers vs single, stack vs peers), the wave-3 pooled cell and the dense-slot result also have Opus L2 numbers (arms/packs-l2/PACKS-L2.md; arms/densechunk-st/DENSECHUNK-ST2.md); Haiku and Opus give the same sign in 4/4 pooled cells (single pack, crowding, stack, wave-3 single pack); Opus is larger on both lifts (+0.042 vs +0.032; wave 3 +0.045 vs +0.020), while the crowding and stack Δs agree within 0.003, so other L1 differences near 0.03 may be understated (arms/L1-PROTOCOL.md).
- **n 180, one seed.** The MDE is ≈ 0.03, so Δs of +0.005 to +0.017 are "not decided at MDE 0.03", not "no effect". About 500 items would be needed to resolve 0.017 (CLOSED.md row 46). Per-pack CIs at n 20 are about ±0.05 (arms/packs/SELFTEST-SCORES.md).
- **Pack overlap.** Health topics appear in MedlinePlus, health-SE, first aid and simplewiki. This drives both the router errors and the stand-in effect (arms/packroute2/ACCURACY.md; arms/crowdq/CROWDQ.md).
- **Base kit = crypto + Wikivoyage only.** No-harm checks cover that kit and the public v0.1 / dev v0.2 sets, nothing broader (arms/packs/SELFTEST-SCORES.md; arms/stack/STACK.md).
- **Desktop replays, not a device.**
  - Retrieval replays ran on a tree based on the deep-tier branch (dt512) that also carries the T-K2 sources patch, not on the cut-7 build (arms/packroute/STEP0.md; arms/stack/GATE.md); see "Engine scope" below.
  - Generation ran on a desktop CPU. Phone latencies (router ×3) are estimates, and the deep tier needs a 12 GB phone that was not available (arms/packroute2/ACCURACY.md).
- **Engine scope: no sources patch (T-K2).** All quality numbers here, and the published cards' self-test lines, were generated on the cut-7 engine without the T-K2 sources patch. A replay of the patch on the 180 items changes the kept list on 52/180. The "Stack Exchange: " / "Simple English Wikipedia: " title prefixes make the on-topic test drop own-pack passages on 17 items. Title lookup for source codes 10–12 (factbook, MedlinePlus, simplewiki) changes retrieval on 40 items: net fact chunk kept 35 → 42, fact article kept 61 → 67. v0.1 (kit only) is identical 60/60. The replay reach counts in §3.3–§3.7 come from the patched tree, so they describe patched retrieval and keep. A judged re-score of the 180 is needed before the patched engine's quality is stated (arms/packs/tk2-replay/TK2-REPLAY.md).
- **Deep tier.** One seed, determinism unprobed; first aid runs on the health-strict path (no deep prompt), so its deep row is not a deep-tier measurement (§3.2; arms/packs/SELFTEST-DEEP.md; arms/seedgen/SEEDGEN.md).
- **Oracle numbers are a ceiling, not a lever.** The fact chunk was injected from the item's own evidence; no retriever reaches it on all 180. The oracle runs were generated on a desktop under swap pressure (2–4× slower than the S run; answers unaffected, deterministic path) (arms/oracle-st/ORACLE-ST.md).
- **Stale sources.** The SE dumps date from 2024-04-02, and the CIA stopped publishing the Factbook on 2026-02-04 (archive snapshot 2026-09-11) (PACK-CATALOGUE-2026-10-12.md §3; research/packs/boar-factbook.md).

## 6. Reproducibility

**Dataset.** hf.co/datasets/r4topunk/boar-packs.
- Wave 1 (root README commit 103f7bfa; one commit per pack): `qa/` and `topics/` (research/QUEUE.md "wave 1 PUBLISHED").
- Wave 2 (root README commit de2c38f5): boar-factbook and boar-simplewiki-en (research/QUEUE.md "Wave 2 PUBLISHED").
- Every pack directory holds the `.sqlite`, its `.sqlite.json` manifest, README (= the card), LICENSE and `selftest.jsonl` (research/packs/qa-health-se.md "Published").
- Pack sha256 prefixes (cards): qa-travel-se a85521ce, qa-ethereum-se f16b258f, qa-bitcoin-se 35b7a3ce, qa-health-se 687e4994, qa-outdoors-se ff733e4f, boar-firstaid-en 8cfab0b4, boar-medlineplus-en c9ac4dcf, boar-factbook c5854353, boar-simplewiki-en c751768b.

**Self-tests.** `research/packs/selftest/<pack>.jsonl` (20 items each) and `draw-<pack>.json` (seeded draw, seed 11, chosen and rejected candidates) (research/packs/selftest/README.md).

**Arm directories and frozen criterion sha256 prefixes** (as the reports give them):

| arm | criterion | other shas |
|---|---|---|
| arms/packs | SELFTEST-DEEP 70230a55… | – |
| arms/densechunk-st | DENSECHUNK-ST 24793013…; DENSECHUNK-ST2 6c7b12dd… | replay patch packdense2 302fc5cd…; generation patch packdense2-only.cut7 40a259be…; fusion copy ea74d8ab… |
| arms/packroute | PACKROUTE 801e9ac9… | – |
| arms/packroute2 | PACKROUTE2 d67fd81c… | patch 71f783de… |
| arms/crowdq | CROWDQ 71603c60… | – |
| arms/groundst | GROUND-ST 895d1ebb…; addendum 1 77eaf4ca… | patch packground2 5fd74a85… → 9acb5160… |
| arms/stack | STACK 56ed7ccf…; STACK-2 e875d463… | patch stack.vs-cut7 0049d3c3… |
| arms/seedgen | measurement, no criterion | standing tool `tools/same_answer.py` |

**Registries.**
- CLOSED.md rows 44–49 record the pack-line closures (in-pack recall levers, Wikipedia as kit content, dense extra slots, keep-step relaxations, top-1 routing, combined stack).
- RULE-CHANGES.md rows 24–27 record the rule changes made during this line: public self-tests as the pack-matched dev set; no Haiku cap; the no-harm statistic for retrieval-adding levers; the determinism field paired on prompt identity.
- Exposure of dev sets during replays is logged per run (EXPOSURES.md).

## 7. Related work (from packs-research/LIT-PACKS.md)

- **Crowding and many documents.** Levy et al., "More Documents, Same Length" (EMNLP 2025 Findings): at fixed context length, more retrieved documents cost up to −20 % for most LLMs. Amiraz et al., "The Distracting Effect" (ACL 2025): related-but-wrong passages are the harmful class. Both match simplewiki taking slots and displacing gold here.
- **Noise.** Cuconasu et al., "The Power of Noise" (2024) reports that random documents can help. "Toward Optimal Search and Retrieval for RAG" (2024) finds that injected noise degrades answers and nothing beats the gold ceiling.
- **Routing to an expert.** Lee et al., "RouterRetriever" (AAAI 2025): per-query routing to a domain expert embedding model beats a general retriever (+2.1 nDCG@10 on BEIR), and oracle routing is better still.
- **Resource selection.** Federated-search resource selection covers CORI, ReDDE, a KAIS 2023 survey and Nguyen et al. 2016. Pack routing is resource selection over installed packs.
- **Small models with domain corpora offline.** "Pocket RAG" (2026; 0.6–1B models, first aid): RAG and reranking help, but the base model sets the ceiling. This matches §3.1 and §3.2, where the reader bounds the value. "Improving the Domain Adaptation of RAG Models for ODQA" (TACL): Wikipedia-pretrained retrievers favour Wikipedia-like knowledge bases.
- **Gap.** LIT-PACKS.md found no study that, for one small offline model, compares a domain knowledge base with a general Wikipedia corpus, or routes among installed packs. The self-test and routing measurements above partly fill that gap, on dev data.

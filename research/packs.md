# 9 · Knowledge packs

> Closed record · research record 1.0 · as of 2026-10-28; the author closed the research lines on 2026-10-23. Current standing, not a final result: Open fronts: https://r4topunk.github.io/boar-research/data/status.json.
>
> Final · as of 2026-10-28 · 0 of 71 wins on the phone, U-total 0.165 (Claude) / 0.242 (gpt-5.6-sol), below the 0.50 bar

- Page: https://r4topunk.github.io/boar-research/research/packs/ · Markdown twin: https://r4topunk.github.io/boar-research/research/packs.md · Whole paper: https://r4topunk.github.io/boar-research/llms-full.txt · Index: https://r4topunk.github.io/boar-research/llms.txt
- Span: 2026-10-12 → 10-14

**In one sentence.** When the bar stopped moving, the author pivoted to a product question: small, openly licensed offline libraries the user picks; one matching pack helps a little, many packs crowd each other out, and the real headroom is getting the one fact-bearing chunk into the prompt.

## For curious readers {#curious}

#### Libraries you choose

If the phone lacks knowledge, give it the right library. We built and published 11 free, openly licensed offline libraries: question-and-answer archives, first aid, health references, a world factbook, simple-English Wikipedia. Each comes with a card, a licence and 20 public test questions.

#### One helps a little

With the matching library installed, the small model does a bit better on that library's own test questions.

*Badge:* 180 library test questions (written from the libraries' own text; practice) · Claude Opus · +0.042.

#### Many crowd each other out

Install all of them at once and a big general library takes the few reading slots that the small, right library needed. Quality goes down.

#### Get the right paragraph in

The biggest headroom was simple to state: get the one paragraph that holds the fact into the prompt. A fix that also pulls in the neighbouring paragraphs of the article it found nearly tripled how often that happens, and gave the pack line's only real improvement. It helps on library questions, not on the bounty-style ones.

**In one sentence card:** "Pick the one library you need; more is not better." (The libraries come back in chapters 13 and 14, with a sharper question: does the right page actually reach the model?)

*Facts: [F-1028] [F-1030] [F-025] [F-026] [F-027] [F-028] [F-095]*

## For tech people {#tech}

### One SQLite file per library; pick one, don't install ten

A pack is one SQLite file: article text in zstd blocks, 1,000-character chunks indexed with FTS5, one 384-d lead vector (first 2,500 characters) per article, and per-row licence and attribution. We published 11 packs on Hugging Face (Stack Exchange travel, Ethereum, Bitcoin, health, outdoors, cooking and money; first aid; MedlinePlus; a world factbook; Simple English Wikipedia), sized from 4.3 MB to 480.5 MB, licences PD / CC0 / CC BY / CC BY-SA only. On the 180 pack self-test questions (written by agents from the packs' own text; dev; Opus) one matching pack lifts the 4B +0.042 (+0.024…+0.062); installing nine as peers drops the fact article's survival into context from 68 to 46 of 180 and costs −0.019 (−0.035…−0.003). Top-1 routing reached only 0.25–0.61 accuracy. An oracle that injects the known fact chunk is worth +0.095; HEADPASS-X2b, which appends the retrieved article's neighbour chunks plus budgeted dense candidates after the keep step, gets the fact chunk into 102 of 180 prompts (from 35) and +0.066 (+0.043…+0.091), at about +420 prompt tokens p50 and +60 % pack size for chunk-vector sidecars. On the bounty-shaped claim kit it is inert. The 35B gains nothing from packs (−0.002).

**Rule box:** "default-eligible only if a pack holds ≤ 0.40 of kept slots and does not lower kit gold; otherwise user-selected only" → 5 default-eligible, 6 user-selected [D-083].

## For AI professionals {#ai}

### The record for this chapter

**Key facts (180 pack self-test items, agent-written from pack text, dev; not a bar lever):**
- 11 packs published with cards, licences and 20 public self-test questions each (Stack Exchange Q&A, first aid, MedlinePlus, a world factbook, Simple English Wikipedia; licences PD / CC0 / CC BY / CC BY-SA only) ([F-1028], -66; [D-080]). Count: 7 at 00:01 and 9 at 02:30 on 10-13, 11 by 19:34 (group-A §2 item 8).
- One matching pack: +0.042 (+0.024…+0.062) Opus; +0.032 (+0.016…+0.050) Haiku [F-025].
- All packs as peers: fact article kept 68 → 46/180, quality −0.019 (−0.035…−0.003) Opus [F-026].
- Top-1 pack routing fails: 0.25 (vote) / 0.58–0.61 (4B zero-shot) vs a 0.85 bar [F-1026].
- Oracle: inject the known fact chunk: +0.095 (+0.070…+0.122) [F-027].
- X2b (append the retrieved article's neighbour chunks + budgeted dense candidates): fact present 35 → 102/180; +0.066 (+0.043…+0.091) Opus; inert on the bounty-shaped claim kit ([F-028], -89; [F-1076]).
- The deep tier gains nothing from any pack: −0.002 (−0.020…+0.016) [F-029].
- V-para is not pack-matched: wave-1 packs cover 1/34 absent bounty-style items [F-091].
- All of English Wikipedia verifiably holds the missing fact for 9 of 34 absent bounty-style items: a lower bound, "at most about a quarter" ([F-1008]; group-B row 3).

**Key decisions:** [D-078] (pivot to packs; conditional in-pack quality), [D-079] (pack-authoring workflow), [D-080] (format 2, licence policy, never NC), [D-084] (publish packs that pass the four-artefact check), [D-086] (oracle cell first), [D-087] (routing closed; rule + quota optional), [D-092] (X2b recommendation), [D-083] (default-eligible vs user-selected). **Reversal to show:** "facts are not in Wikipedia" (10-12 morning) withdrawn the same afternoon [D-076].

**Turning point:** 2026-10-13 23:11, ORACLE-ST: the ceiling is reach, not reading; it led directly to the only lever of the pack line.

**Continued in chapters 11, 13 and 14:** with the 1.7B as main engine the pack line was re-measured on real development questions (no pack gain there, [F-2080]), re-framed as delivery (chapter 13) and became the author's closing thesis in a conditional form (chapter 14). The 4B-era numbers above stay as measured; they describe the 4B, not the 1.7B.

### Knowledge packs (pack-matched development items)

On 180 pack-matched self-test items (agent-written from pack text; development data; one seed; deterministic 4B generation) one matching pack improves the 4B by +0.042 (+0.024…+0.062) under Opus and +0.032 (+0.016…+0.050) under Haiku. Installing nine packs as peers reduces fact-article survival from 68 to 46 of 180 and costs −0.019 (−0.035…−0.003). Top-1 routers reach 0.25–0.61 accuracy against a 0.85 bar. Injecting the known fact chunk yields +0.095 (+0.070…+0.122); HEADPASS-X2b raises fact-chunk presence from 35 to 102 of 180 and yields +0.066 (+0.043…+0.091) (Haiku +0.056), with +0.177 (+0.098…+0.263) on the 30 items where the chunk became newly present; on the bounty-shaped claim kit it is inert. The 35B gains nothing from packs (−0.002, −0.020…+0.016). These are conditional, in-pack results and are not evidence about the bar; questions written from the same text the retriever indexes favour retrieval.

*Facts: [F-025] [F-1025] [F-029] [F-026] [F-1026] [F-027] [F-1027] [F-222] [F-028] [F-1063] [F-1064] [F-095] [F-1076]*

## Facts cited {#facts}

Resolve every [F-…] marker in https://r4topunk.github.io/boar-research/data/facts.json. Each line gives the claim, the number with its metric family, set and status, judge, n, seeds, CI, date and caveat.

<!-- lint:exempt:start -->
- [F-025] One matching knowledge pack helps the small model a little on questions written from that pack. Opus +0.042 (+0.024…+0.062); Haiku +0.032 (+0.016…+0.050) · set 180 pack self-tests (dev (agent-written from pack text), development data) · judge Claude Opus (L2) and Claude Haiku (L1) · n 180 · seeds 1 · CI paired 95 % bootstrap · date 2026-10-13 · caveat: Pack-matched dev questions, not a bounty-bar measurement.
- [F-026] Installing all packs at once crowds out the right passage and costs a little quality. Opus −0.019 (−0.035…−0.003); Haiku −0.016 (−0.033…−0.001) · set 180 pack self-tests (dev, development data) · judge Claude Opus (L2) and Claude Haiku (L1) · n 180 · seeds 1 · CI paired 95 % bootstrap · date 2026-10-13
- [F-027] Ceiling test: handing the model the exact fact-bearing chunk shows the headroom is retrieval, not reading. inject fact chunk (ADD) +0.095 (+0.070…+0.122); fact chunk only (ONLY) +0.115 (+0.088…+0.142) · set 180 pack self-tests (dev, development data) · judge Claude Opus (judge.v1, both orders) · n 180 · seeds 1 · CI paired 95 % bootstrap · date 2026-10-13 · caveat: Oracle (cheating) cell: an upper bound, not a deployable result.
- [F-028] The one retrieval change that converted: append the retrieved article's neighbouring chunks plus a few vector-search candidates, under a 600-token budget (HEADPASS-X2b). Opus +0.066 (+0.043…+0.091); Haiku +0.056; fact chunk present in context 35 → 102 of 180 · set 180 pack self-tests (dev (designed on the same set), development data) · judge Claude Opus (judge.v1, both orders) · n 180 · seeds 1 · CI paired 95 % bootstrap · date 2026-10-14 · caveat: LEVER on pack-matched dev data only; inert on the claim kit (ceiling ≈ 0.011) and not a bounty-bar lever.
- [F-029] The 35B deep tier gains nothing measurable from packs; its advantage over the 4B with the same pack is model knowledge. deep with vs without pack Δ −0.002 (−0.020…+0.016); deep − 4B with the same pack +0.054 (+0.034…+0.073) · set 180 pack self-tests (dev, development data) · judge Claude Haiku 5.5-low (L1 triage judge, N = 4, both orders) · n 180 · seeds 1 · CI paired 95 % bootstrap · date 2026-10-13
- [F-091] Wave-1 packs barely cover the bounty-style set. V-para absent-item coverage 1/34 (union with kit 5/34) · set V-para dev-style (dev-style, development data) · judge jev · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-12 23:59 · caveat: packs are product value, not a bar lever
- [F-095] X2b no harm on the bounty-shaped kit. v0.1+simplewiki +0.012 (−0.019…+0.046); kit-only runs byte-identical · set v0.1 dev (dev, development data) · judge Haiku · n 57 · seeds UNKNOWN · CI n 57 · date 2026-10-14 · caveat: KIT-X2b closed at ceiling (R93)
- [F-222] X1 (append neighbour chunks of retrieved article, 0 LLM) +0.033 (+0.016…+0.050) Opus; fact present 35 → 72 · set 180 self-tests dev (dev, development data) · judge Opus (beyond frozen plan) · n 180 · seeds UNKNOWN · CI n 180 · date 2026-10-14 · caveat: frozen label "not decidable at MDE 0.03" | verdict capped "not decidable": power line missed by 3 items
- [F-1008] Wikipedia-anywhere gate for V-para absent-knowledge items. 9/34 verified (MARGINAL band 7–13) · set V-para dev (dev, development data) · judge jev + quote check · n 51 (inferred from set) · seeds UNKNOWN · CI 34 items · date 2026-10-12/13 · caveat: 25/34 unverified, not shown absent
- [F-1025] Pack lift per pack tracks the keep step. simplewiki +0.102, ethereum-SE +0.074, bitcoin-SE +0.054; first aid +0.004; factbook −0.018 · set 180 self-tests dev (dev, development data) · judge Haiku · n 180 (inferred from set) · seeds UNKNOWN · CI 20 per pack · date 2026-10-13 · caveat: citation fix; descriptive, 20 items per pack, Haiku
- [F-1026] Top-1 pack routing fails. accuracy 0.25 (vote) / 0.58–0.61 (4B zero-shot) vs 0.85 bar · set 180 self-tests (dev, development data) · judge none · n 180 (inferred from set) · seeds UNKNOWN · CI 0-call / local · date 2026-10-13 · caveat: break-even ≈ 0.68 | break-even ≈ 0.68 accuracy
- [F-1027] Fact chunk reaches the 4B context today. kept 43/180; raw top-6 55/180 (judge.v1 ratio) · set 180 self-tests (status UNKNOWN) · judge UNKNOWN · n 180 (inferred from set) · seeds UNKNOWN · CI not computed · date 2026-10-13
- [F-1028] Published packs on the author's public Hugging Face dataset (boar-packs). 11 packs: qa/ 7, topics/ 4 · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-13 · caveat: the dataset URL carries the author's own handle; whether to print it is the author's decision
- [F-1030] Pack licences. Stack Exchange CC BY-SA 2.5/3.0/4.0 per post (archive.org dump 2024-04-02); simplewiki CC BY-SA 4.0 (+GFDL); factbook CC0; MedlinePlus public domain (credit line); firstaid CC BY-SA + US PD · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-13 · caveat: SE dump is 2.5 years stale
- [F-1063] X2b conversion where the fact chunk is newly present. +0.177 (+0.098…+0.263) · set 180 self-tests dev (dev, development data) · judge Opus · n 30 · seeds UNKNOWN · CI n 30 · date 2026-10-14 · caveat: appending non-fact chunks ≈ 0 cost (+0.008) | —
- [F-1064] X2b reach and cost. fact present 102/180 (S 35); +≈ 420 prompt tokens p50; total p50 13.4 s vs 8.3 s; sidecars ≈ +60 % pack size · set 180 (status UNKNOWN) · judge UNKNOWN · n 180 (inferred from set) · seeds UNKNOWN · CI not computed · date 2026-10-14
- [F-1076] X2b on the claim kit (bounty-shaped) inert: kept/prompt identical 20/20; KIT-X2b closed (R93) · set v0.2 random20 dev (dev, development data) · judge none · n 20 · seeds UNKNOWN · CI n 20 · date 2026-10-16 · caveat: not a bounty-bar lever
- [F-2080] Pack self-test gain does not reproduce on real items. self-test fact-added cell +0.139 (+0.075..+0.201) n 27 vs real −0.010 (−0.077..+0.050) n 10 · set self-tests (pack-written) vs MAIN keyed (dev) (dev (pack-written self-tests), development data) · judge Claude Haiku · n UNKNOWN · seeds UNKNOWN · CI 1 seed · date 2026-10-21 · caveat: post hoc; small n on real

<!-- lint:exempt:end -->
### Decisions cited {#decisions}

<!-- lint:exempt:start -->
- [D-076] 2026-10-12 · Withdraw "facts are not in Wikipedia"; adopt the peer research's task chain · why: peer review showed WIKISECTION covered only one pack and part of the items. · status: kept
- [D-078] 2026-10-12 · Pivot to Knowledge Packs; primary metric = in-pack conditional ratio · why: the product is a small model + user-selected packs; the unconditional bar was not moving. · status: kept
- [D-079] 2026-10-12 · Build a pack-authoring workflow; agents may write the 20 public self-tests per pack; held-out claim items stay non-Claude · why: "we will be the first author with publications" · status: kept
- [D-080] 2026-10-12 · Pack format unchanged (format 2); licence policy PD/CC0/CC BY/CC BY-SA only; never NC; per-row attribution for Stack Exchange; archive.org pre-2024 SE dumps, no · why: zero format risk; licence compliance. · status: kept
- [D-083] 2026-10-12 · "Default-eligible" only if a pack holds ≤ 0.40 of kept slots and does not lower kit gold; otherwise user-selected only · why: crowding measured. · status: kept
- [D-084] 2026-10-13 · Publish packs that pass the four-artefact check (card, self-test, coverage, crowding) on HF under the author's standing OK · why: public reuse; licence clarity per pack. · status: kept
- [D-086] 2026-10-13 · Run an oracle/ceiling cell (ORACLE-ST) before more pre-processing levers · why: decide whether reader or retrieval is the wall. · status: kept
- [D-087] 2026-10-13 · Routing among packs closed at the product level; keep rule + quota only an optional setting · why: crowding cost small (−0.016 Haiku / −0.019 Opus); routers 0.25–0.61 accuracy. · status: kept
- [D-092] 2026-10-14 · HEADPASS-X2b = the pack line's retrieval recommendation for format-v3 packs; X1 for format-2 packs · why: Opus +0.066 (+0.043…+0.091), no harm on kit. · status: kept

<!-- lint:exempt:end -->
---

Cite as: r4to, independent researcher. RatLab — A Boar Research (2026), research record 1.0, as of 2026-10-28. Text and data CC BY 4.0. Fact ids or a link must travel with a quote. How to cite: https://r4topunk.github.io/boar-research/cite/ · https://r4topunk.github.io/boar-research/CITATION.cff.

AI-reviewed, not clinically reviewed. Nothing here is medical advice.

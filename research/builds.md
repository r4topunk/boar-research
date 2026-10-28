# 4 · Seven frozen builds

> Closed record · research record 1.0 · as of 2026-10-28; the author closed the research lines on 2026-10-23. Current standing, not a final result: Open fronts: https://r4topunk.github.io/boar-research/data/status.json.
>
> Final · as of 2026-10-28 · 0 of 71 wins on the phone, U-total 0.165 (Claude) / 0.242 (gpt-5.6-sol), below the 0.50 bar

- Page: https://r4topunk.github.io/boar-research/research/builds/ · Markdown twin: https://r4topunk.github.io/boar-research/research/builds.md · Whole paper: https://r4topunk.github.io/boar-research/llms-full.txt · Index: https://r4topunk.github.io/boar-research/llms.txt
- Span: 2026-10-03 → 10-07

**In one sentence.** Every improvement that survived its frozen test went into a numbered, hashed build ("cut"), and seven cuts later the small model's quality on held-out data had not moved beyond noise; what improved was safety, speed and instant answers.

## For curious readers {#curious}

#### Snapshots, not tweaks

Every idea that passed its rule went into a numbered snapshot of the app, a frozen build (cut). There were seven. Cut 7 is the one we stand behind today.

#### What actually got better

Safety got better: a small detector spots emergencies and shows a short reviewed first-aid card instead of letting the model improvise. Instant answers got better: a calculator, a travel-distance estimator and a table of 4,233 facts answer in a blink. Phones got faster after we found our own bugs.

*AI-reviewed, not clinically reviewed. Nothing here is medical advice.*

#### What did not move

On the sealed questions, the small model's quality barely moved through all seven builds: from 0.506 to 0.512 on the flattering scale, a difference smaller than the noise between two identical runs.

*Badge:* v0.2 (sealed at the time, later demoted to practice) · Claude Opus · 110 questions · 2 runs.

**In one sentence card:** "Seven builds made the app safer and quicker, not smarter."

*Facts: [F-701] [F-358] [F-312] [F-313] [F-346]*

## For tech people {#tech}

### Detector → instant tier → health path → retrieval → keep → reader

Every question takes a fixed path. A small learned emergency detector (an mmBERT-small encoder, q8_0, 106 MB, threshold 0.2) and hand-written rules look first. Some questions never reach a language model: emergency numbers, unit conversions, arithmetic, travel distances, nearby places, a 4,233-entity Wikidata fact table (761 KB), and health and first-aid questions, which get a reviewed card (32 conditions) or a verbatim cited excerpt of at most 700 characters. On the default tier the model never writes health advice. Everything else goes to retrieval: SQLite FTS5 full-text search over 1,000-character chunks plus 384-d bge-small article-lead embeddings over the installed knowledge packs (k 6). A keep step drops off-topic and unsafe passages and fits the rest into a 1,200-token context. The reader of the frozen claim build, Qwen3-4B-Instruct (Q4_K_M, 2.5 GB), writes a short cited answer. The deep tier swaps in Qwen3.6-35B-A3B (UD-Q2_K_XL, 12.3 GB file) with a 400-token context, 200 answer tokens and a 512-token thinking budget (desktop only; not delivered). From 2026-10-20 the main 8 GB reader is Qwen3-1.7B (Q4_K_M, ≈ 1.1 GB file) and the delivered app keeps one Succinct style (T14, T18).

**Health callout:** "AI-reviewed, not clinically reviewed. Nothing here is medical advice." Detector dev numbers: curated recall 179/180, strict false fires 15/100 (dev data) [F-1072]. DETMAX: chit-chat before an emergency lost 7/240 routes → 0/240 [F-345]. HEALTHGAP: 15 of 64 health-shaped probes reached the model unguarded until a predicate fix [F-378].

**Note:** the detector weights are not released (base-model licence unknown).

### Cut 1 → cut 7: what each build added and which test let it in

We never shipped tweaks, only numbered, hashed builds (cuts) that bundle the arms that passed their frozen criteria. Cut 3 added a self-contradiction guard, an arithmetic tool and a snakebite text; cut 4 fixed our own KV-cache save path and blocked fragment instant answers; cut 5 skipped the route gate where safe (32/54 gate calls per seed, 120/120 identical answers); cut 6 made the detector score the window and the current turn; cut 7 added the Wikidata fact table. The fact table fires 0/110 on v0.2 and 0/58 on V-para, so cut 7's held-out numbers are cut 6's. Small-model quality on the held-out set did not move beyond noise across all of it: main 0.506 → cut 6 0.512 raw on v0.2 (two seeds, Opus): +0.006.

**Decision note:** the claim build was frozen at cut 6 on 10-06 with "only answer-preserving fixes"; that freeze was relaxed on 10-07 when cut 7 changed 8 v0.1 answers. Both steps are shown (group-A §2 item 4).

*Facts: [D-038] [D-046]*

## For AI professionals {#ai}

### The record for this chapter

**Key facts:**
- Cut lineage: 1 → 1b → 2 → 3 (self-contradiction guard, arithmetic tool, snakebite text) → 4 (KV-cache fix, instant-answer guards) → 5 (speed-only, 10-06) → 6 (detector across turns) → 7 (cut 6 + a 4,233-entity Wikidata fact table, 761 KB) ([F-701]; [F-346]; T-results-L33 corrected date).
- Cut 3 over cut 2 on v0.1: +0.032, CI90 [+0.010, +0.062] [F-318], v0.1 dev, Opus.
- Cut 2's gain over the old main came from non-model paths (cards, calculator); model-side ≈ 0 [F-319].
- Safety: health stack took unsafe answers 7 → 0 (4B) and 10 → 0 (1.5B) with no quality cost [F-312]; learned emergency detector generalized on fresh blind sets where the lexical one failed [F-311] [F-441]; the independent reviewer agent changed 25 of 31 first-aid cards [F-313]. AI-reviewed, not clinically reviewed.
- Held-out movement across all of this: main 0.506 → cut 6 0.512 on v0.2, two seeds, +0.006: noise (group-B row 5).
- The fact table fires 0/110 on v0.2 and 0/58 on V-para, so cut 7's held-out numbers are cut 6's [F-359].

**Key decisions:** [D-032] (adopt cut 3), [D-034] (KVFIX → cut 4), [D-044] (CUT5-LITE), [D-045] (DETMAX → cut 6), [D-038] / [D-038] (freeze the claim build at cut 6, only answer-preserving fixes), [D-046] / [D-046] (cut 7 = cut 6 + FACTS r6, adopted on gates). **Reversal to show:** the 10-06 freeze ("v0.1 answers unchanged") was relaxed on 10-07 when cut 7 changed 8 v0.1 answers (group-A §2 item 4).

**Turning point:** 10-06: the audit counts 15 answer-identical arms and 0 ratio movement on the small model; "stop polishing the 4B".

### 5 Systems: a frozen 4B build, a 35B deep tier, knowledge packs and a lite tier

The frozen claim build (cut 7) routes each question through a learned emergency detector and deterministic layers (calculator, unit and distance estimators, places, a 4,233-entity Wikidata table, first-aid cards and verbatim cited health excerpts); remaining questions are answered by Qwen3-4B-Instruct-2507 (Q4_K_M) from passages retrieved by SQLite FTS5 and 384-d bge-small lead vectors over offline packs (k = 6, 1,200-token context), after a keep step that removes off-topic and unsafe passages. The deep tier replaces the reader with Qwen3.6-35B-A3B (UD-Q2_K_XL; ≈ 3B active parameters per token; 400-token context; 200 answer tokens; thinking budget 512). Seven cuts were frozen between 2026-10-03 and 2026-10-07; cut 7 differs from cut 6 only by the fact table, which fires on 0/110 v0.2 and 0/58 V-para items, so cut 7's held-out numbers are cut 6's. Desktop runs execute the same TypeScript engine in Node with native components shimmed; desktop/phone parity is tested directly (§6.6). From 2026-10-20 the main 8 GB reader is Qwen3-1.7B (Q4_K_M) with refuse-by-default and a warning line (§6.8); the closed research engine ENGINE-RC (2026-10-23) adds the SEFIX-124 search fixes, a compact per-pack index (W78) and a shaped factbook (§6.10). The submitted system is a different implementation (§6.11).

*Facts: [F-375] [F-346] [F-585] [F-622]*

## Facts cited {#facts}

Resolve every [F-…] marker in https://r4topunk.github.io/boar-research/data/facts.json. Each line gives the claim, the number with its metric family, set and status, judge, n, seeds, CI, date and caveat.

<!-- lint:exempt:start -->
- [F-311] Lexical health detector tuned on dev failed a fresh blind set: health route 31/72 (bar ≥ 54) 10 → 31/72 · set health-fresh1 (blind then; dev now) (dev, development data) · judge scripted · n UNKNOWN · seeds 1 · CI 1 seed · date 2026-10-03
- [F-312] Health stack L2: unsafe answers 7 → 0 (4B) and 10 → 0 (1.5B) with no quality cost. ΔQ +0.009 (−0.009…+0.030) · set v0.1 dev (dev, development data) · judge Opus + safety rules v0.8.2 · n UNKNOWN · seeds 2 · CI 2 seeds · date 2026-10-03 · caveat: cards were unvetted drafts at the time
- [F-313] The independent Opus reviewer changed 25 of 31 first-aid cards, rejected 0. 6 approved / 25 changed · set n/a (status UNKNOWN) · judge Opus reviewer · n UNKNOWN · seeds UNKNOWN · CI 31 cards · date 2026-10-03 · caveat: "AI-reviewed, not clinically reviewed"
- [F-318] Cut 3 over cut 2 on v0.1. +0.032 CI90 [+0.010, +0.062]; 0.566 vs 0.534 · set v0.1 dev (dev, development data) · judge Opus judge.v1-med · n 57 · seeds UNKNOWN · CI n 57 · date 2026-10-04 · caveat: last 4B-side adopted quality gain | rests on 4 items; did not transfer to held-out (F-chron-early-62)
- [F-319] Cut 2's gain over old main came from non-model paths. +0.028 cards + calculator; model-side ≈ 0 · set v0.1 dev (dev, development data) · judge not stated at the cited line (neighbouring buckets are in Haiku-rubric terms) · n 57 · seeds UNKNOWN · CI n 57 · date 2026-10-04 · caveat: citation fix: the +0.028 non-model-path finding is l.7
- [F-345] DETMAX fixes chit-chat prefixes before an emergency. lost routes 7/240 → 0/240; split-turn forms lose 0/60; +1 route in 192 dev chats (a real flood emergency) · set dev probes (dev, development data) · judge none · n 240 · seeds UNKNOWN · CI n 240 / 60 / 192 · date 2026-10-06 · caveat: citation fix (l.46 blank)
- [F-346] FACTS asset size. 4,233 entities, 760,970 B · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-06 · caveat: citation fix (l.6 is the sha line)
- [F-358] Cut 7 build identity. commit 6d0b93b1, tree 7c96e59e…, patch vs cut 6 sha 0eee6a0b…; 1,346/1,346 unit tests · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-07 · caveat: local commit, never pushed
- [F-359] FACTS (Wikidata table) fires zero times on the held-out sets, so cut 7 = cut 6 there. 0/110 v0.2, 0/58 V-para; 8/72 on v0.1 · set v0.2 (burnt→dev), V-para (burnt → dev, development data) · judge none · n 51 (inferred from set) · seeds UNKNOWN · CI not computed · date 2026-10-07
- [F-375] Health questions on the default tier never reach the 4B: they get a fixed card or a verbatim source excerpt (0 model tokens). modelId grounding-guard / extractive · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-15 · caveat: citation fix; design statement; AI-reviewed, not clinically reviewed
- [F-378] HEALTHGAP: 15 of 64 health-shaped probes reached the model because the detector scored them 0.00–0.16 (dose, poison, CO reading, survival time). 15/64 · set agent-written dev probes (dev, development data) · judge none · n 64 · seeds UNKNOWN · CI n 64 probes · date 2026-10-15 · caveat: citation fix (l.156-158 are open questions)
- [F-441] A 4B one-token emergency gate generalized on two blind sets; lexical did not. 90/90, HN 6/60; 71/72, HN 2/48 (lexical 23/90, 32/72) · set health-fresh2/1 (blind then; dev now) (dev, development data) · judge scripted · n UNKNOWN · seeds UNKNOWN · CI detection only · date 2026-10-03
- [F-585] Fast-tier constants in cut 7. retrieve k 6, context 1,200 tokens (lookup 3/450; other 4/700 quick budget), fast thinking budget 256 (unused by the instruct 4B) · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-07 · caveat: instant final confidence 0.75 (context.ts:139)
- [F-622] Deep-tier constants. retrieve k 6, context 400 tokens, max 200 answer tokens; thinking budget 1024 in code, 512 recommended · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-10
- [F-701] Cut lineage. cut 1 → 1b → 2 → 3 (VG v3 + AR + snakebite) → 4 (KVFIX + INSTANT-FRAG + INSTANT-SUBJ) → 5 (KV no-source prefix + gate skip) → 6 (DETMAX) → 7 (FACTS r6) · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-03..07 · caveat: base = public upstream commit 0cfd4a77
- [F-1072] Detector v3b dev numbers at threshold 0.2. curated recall 179/180, strict false fires 15/100, ES 54/54, 0 critical misses; realistic recall 240/246, false fires 3/457 · set dev sets (threshold not tuned on them) (dev, development data) · judge none (deterministic) · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-15 · caveat: dev data

<!-- lint:exempt:end -->
### Decisions cited {#decisions}

<!-- lint:exempt:start -->
- [D-032] 2026-10-04 · Adopt cut 3 (verdict guard + arithmetic repair + snakebite text) · why: L1 Δ +0.029 [+0.007, +0.058], confident-wrong 15 → 9, unsafe 0. · status: kept
- [D-034] 2026-10-05 · Fix the KV session save path (KVFIX) and block fragment/figurative instant answers (INSTANT-FRAG) → cut 4 · why: A15 smoke: every question re-prefilled the prefixes; "capital of France" answered with a Lyon fragment. · status: kept
- [D-038] 2026-10-06 · Freeze the claim build at cut 6; later only routing/safety fixes that leave v0.1 answers unchanged · why: stable claim evidence. · status: superseded by D-046 (Relaxed on 2026-10-07: cut 7 added FACTS r6, which changed 8 v0.1 answers.)
- [D-044] 2026-10-06 · Adopt CUT5-LITE (KV prefix for no-source prompts + route-gate skip), reject CUT5-SPEED · why: CUT5-SPEED failed its desktop speed gate (1.071× vs ≤ 0.8); lite was identity-safe. · status: kept
- [D-045] 2026-10-06 · Adopt DETMAX → cut 6 · why: chit-chat before an emergency lost 7/240 routes; DETMAX 0/240. · status: kept
- [D-046] 2026-10-07 · Cut 7 = cut 6 + FACTS r6 (adopted on gates: 0 fires on held-out sets); no relaxed lowercase rule; fine-tune data 1k go; "no device exists" · why: deterministic facts lever; no phone. · status: kept

<!-- lint:exempt:end -->
---

Cite as: r4to, independent researcher. RatLab — A Boar Research (2026), research record 1.0, as of 2026-10-28. Text and data CC BY 4.0. Fact ids or a link must travel with a quote. How to cite: https://r4topunk.github.io/boar-research/cite/ · https://r4topunk.github.io/boar-research/CITATION.cff.

AI-reviewed, not clinically reviewed. Nothing here is medical advice.

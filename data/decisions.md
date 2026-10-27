# BOAR decision log

TL;DR: every direction-setting decision of the BOAR research (2026-09-26 → 2026-10-25), ADR-style: what was decided, why, what else was considered, what happened next, and whether it still stands. Machine-readable twin: [`decisions.json`](decisions.json). Fact ids (`F-…`) resolve in [`facts.json`](facts.json).

215 decisions · kept 190 · superseded 23 · reversed 2.

> Rows marked *internal (pending author)* must not be rendered on the public site until the author approves them.

## 2026-09-26

### D-001 · Thesis: "quality per second + blind evaluation against a frontier model"; stay on the existing cross-platform app; plan a no-network Android submission

- **Date:** 2026-09-26 · **Status:** kept
- **Context:** Author joins the app maintainer as co-builder; thesis "quality per second + blind eval vs frontier"; official Android submission planned as a no-INTERNET variant
- **Decision:** Thesis: "quality per second + blind evaluation against a frontier model"; stay on the existing cross-platform app; plan a no-network Android submission
- **Alternatives considered:** fork a new app; rely on the existing on-phone benchmark
- **Rationale:** the existing claim had solid engineering but no measured research quality
- **Consequence:** led to the 09-29 research pipeline and 10-01 harness
- **Facts:** F-050

## 2026-09-30

### D-002 · References = Claude Opus + web search, frozen once, hashed; never regenerated

- **Date:** 2026-09-30 · **Status:** kept
- **Context:** Frozen frontier-plus-web reference answers for the public v0.1 set start being generated (09-30 → 10-02)
- **Decision:** References = Claude Opus + web search, frozen once, hashed; never regenerated
- **Alternatives considered:** live references per run
- **Rationale:** a fixed denominator makes runs comparable
- **Consequence:** same refs used for every v0.1 number; regenerating = not comparable
- **Facts:** F-059

## 2026-10-01

### D-003 · Build one evaluation harness (ADR-001): own thin protocol + existing scorers; 5 layers; 7 axes never averaged

- **Date:** 2026-10-01 · **Status:** kept
- **Context:** ADR-001 proposes one evaluation harness: 5 layers, one trace schema, 7 axes never averaged, gate vs full modes
- **Decision:** Build one evaluation harness (ADR-001): own thin protocol + existing scorers; 5 layers; 7 axes never averaged
- **Alternatives considered:** Inspect AI (UK AISI); promptfoo; Inspect AI (Python, subprocess bridge); promptfoo (no paired bootstrap)
- **Rationale:** each experiment wrote its own scripts; desktop and device rows had different shapes; no regression gate; run noise ≈ effect size
- **Consequence:** harness became boar-eval, later the public boar-bench
- **Facts:** F-1305, F-678

### D-004 · Replace the 27 items borrowed from a competitor's question list with own items (bench v0.1)

- **Date:** 2026-10-01 · **Status:** kept
- **Context:** 27 items from a competing team's fork removed from the bench; replaced with original items of the same slot (bench v0.1)
- **Decision:** Replace the 27 items borrowed from a competitor's question list with own items (bench v0.1)
- **Alternatives considered:** keep them; keep them with attribution
- **Rationale:** do not copy competitors' test cases; clean benchmark
- **Consequence:** v0.1 = 60 public items (57 EN judged)
- **Facts:** F-099, F-101

### D-006 · Freeze every deciding criterion (sha256) before data; blind sets written by separate writers, never read by researchers

- **Date:** 2026-10-01 · **Status:** kept
- **Context:** Embedding danger detector criterion frozen before its blind set exists (start of learned-detector line)
- **Decision:** Freeze every deciding criterion (sha256) before data; blind sets written by separate writers, never read by researchers
- **Alternatives considered:** iterate without freezes
- **Rationale:** avoid post-hoc tuning
- **Consequence:** 65/65 criterion shas verify by 10-10
- **Facts:** F-100

### D-007 · Seven axes (quality, truthfulness, safety, retrieval, latency, resources, stability), never averaged into one score

- **Date:** 2026-10-01 · **Status:** kept
- **Context:** Research mandate: three researcher lanes (retrieval, models, evaluation/safety) write "technique cards"; a runner executes arms
- **Decision:** Seven axes (quality, truthfulness, safety, retrieval, latency, resources, stability), never averaged into one score
- **Alternatives considered:** single composite score
- **Rationale:** one average hides safety and latency regressions
- **Consequence:** quality ratio became the published number; other axes reported separately
- **Facts:** F-290

### D-008 · Research agents work in fixed lanes, write one "technique card" per idea, never run experiments or touch the product; only the coordinator queues runs

- **Date:** 2026-10-01 · **Status:** kept
- **Context:** Research mandate: three researcher lanes (retrieval, models, evaluation/safety) write "technique cards"; a runner executes arms
- **Decision:** Research agents work in fixed lanes, write one "technique card" per idea, never run experiments or touch the product; only the coordinator queues runs
- **Alternatives considered:** Agents run their own tests
- **Rationale:** Avoid duplicate work; separate proposing from measuring
- **Consequence:** the retrieval research agent 19 cards, the models/latency research agent 22, the evaluation/safety research agent 23; runner agent executed
- **Facts:** F-823

### D-009 · Every pass/fail criterion written and sha256-frozen before the run; no edits after verdicts, only dated addenda

- **Date:** 2026-10-01 · **Status:** kept
- **Context:** First frozen criteria on fresh sets (hm-fresh2/3) before any reading
- **Decision:** Every pass/fail criterion written and sha256-frozen before the run; no edits after verdicts, only dated addenda
- **Alternatives considered:** Judge then decide
- **Rationale:** Prevent tuning the rule to the result
- **Consequence:** 65/65 criterion hashes verified 10-10; 16 of 17 re-verified by an outside critic 10-16
- **Verification note:** Verification note: "18/19 re-verified" → 16/17 (CRITIQUE:6) or 19/20 in the C6 spot-check (CRITIQUE:72-75).
- **Facts:** F-1136

### D-005 · Report a quality effect only if it exceeds the MDE printed by the diff tool

- **Date:** 2026-10-01 23:00 · **Status:** kept
- **Context:** Rule: an effect is reported only if it exceeds the minimum detectable effect (MDE)
- **Decision:** Report a quality effect only if it exceeds the MDE printed by the diff tool
- **Alternatives considered:** report any sign
- **Rationale:** run-to-run noise (Δ 0.031) as large as effects
- **Consequence:** became house rule; later refined (two-seed, seed-noise rule)
- **Facts:** F-1137

## 2026-10-02

### D-014 · Treat the bounty as qualitative: judged by a public confirmation, not a numeric benchmark

- **Date:** 2026-10-02 · **Status:** kept
- **Context:** Bounty re-read: winning is a public confirmation, not a numeric benchmark
- **Decision:** Treat the bounty as qualitative: judged by a public confirmation, not a numeric benchmark
- **Alternatives considered:** treat our ratio as the decision
- **Rationale:** bounty text
- **Consequence:** private ratio kept as instrument; claim framing open
- **Facts:** F-111

### D-015 · Hold v0.2 as held-out: develop on v0.1, confirm only on v0.2

- **Date:** 2026-10-02 · **Status:** superseded by D-037 — v0.2 was declared burnt → dev on 2026-10-06.
- **Context:** Direction: two tracks only (harness + pipeline technique); v0.2 = held-out, confirm only
- **Decision:** Hold v0.2 as held-out: develop on v0.1, confirm only on v0.2
- **Rationale:** avoid tuning on the claim set
- **Consequence:** v0.2 later burnt (D-chron-early-22)
- **Superseded by:** D-037
- **Facts:** F-112

### D-016 · Restate deep35 memory: "≤ 8 GiB" was our own estimate, not a bounty rule; macOS footprint ≠ phone RSS

- **Date:** 2026-10-02 · **Status:** kept
- **Context:** Strategy memo (high-tier model, one call): Android-only, three fronts; stop iPhone/1.5B and prompt work
- **Decision:** Restate deep35 memory: "≤ 8 GiB" was our own estimate, not a bounty rule; macOS footprint ≠ phone RSS
- **Alternatives considered:** keep "fails memory"
- **Rationale:** the author asked why 8 GB if the bounty says 12 GB
- **Consequence:** Linux 6,750 MiB (≈ 6.6 GiB) container test passed 10/10
- **Verification note:** Verification note: Same unit fix as F-chron-early-30.
- **Facts:** F-069

### D-018 · "Iterate fast first, rigor later": sha freeze only when an idea goes to the full bench or held-out; funnel L0 → L1 → L2 → L3

- **Date:** 2026-10-02 · **Status:** kept
- **Context:** Author: "iterate fast first, rigor later" (sha only when an idea reaches the full/held-out bench); no fixed greeting rules
- **Decision:** "Iterate fast first, rigor later": sha freeze only when an idea goes to the full bench or held-out; funnel L0 → L1 → L2 → L3
- **Alternatives considered:** freeze every step
- **Rationale:** speed of iteration
- **Consequence:** funnel became standard (BOUNTY-BOARD rules)
- **Facts:** F-113

### D-019 · Pairwise judging in both A/B orders; disagreement = tie; scores averaged across orders

- **Date:** 2026-10-02 · **Status:** kept
- **Context:** Rubric-floor risk found: a blank system scores ~0.20–0.31 of the reference
- **Decision:** Pairwise judging in both A/B orders; disagreement = tie; scores averaged across orders
- **Alternatives considered:** single order
- **Rationale:** removes position bias
- **Consequence:** position consistency 96.5-100 % measured
- **Facts:** F-1139

### D-020 · Freeze the analysis plan (metrics, CI method, seeds, wording rules) before items existed

- **Date:** 2026-10-02 · **Status:** kept
- **Context:** Held-out v0.2 analysis plan frozen (combined sha fe100e91…); items frozen in a second commit
- **Decision:** Freeze the analysis plan (metrics, CI method, seeds, wording rules) before items existed
- **Alternatives considered:** decide after seeing numbers
- **Rationale:** prevents tuning metric to results
- **Consequence:** plan hashed (375ff004…); later changes only as dated addenda
- **Facts:** F-114

### D-021 · Primary metric = raw ratio, bar > 0.50 (the author's decision on 2026-10-02, not the app maintainer's)

- **Date:** 2026-10-02 · **Status:** superseded by D-036 — Floor-adjusted ratio + win/tie/loss became the headline on 2026-10-06 (applied 2026-10-07); the raw rule is still printed as the formal rule.
- **Context:** Direction: "eval + pipeline technique" (better answers from the same model)
- **Decision:** Primary metric = raw ratio, bar > 0.50 (the author's decision on 2026-10-02, not the app maintainer's)
- **Alternatives considered:** floor-aware metric
- **Verification note:** the scrubbed public plan says 'the maintainer's decision', but the private original names the author; in the publication 'the app maintainer' means the upstream maintainer, so write 'the author's decision'
- **Superseded by:** D-036
- **Facts:** F-1306

### D-022 · Blind / held-out sets: researchers never open, list or grep them; coordinator runs them by script, aggregates only

- **Date:** 2026-10-02 · **Status:** kept
- **Context:** Blind-set rule widened after a filename-only grep leaked set composition
- **Decision:** Blind / held-out sets: researchers never open, list or grep them; coordinator runs them by script, aggregates only
- **Alternatives considered:** Trust-based access
- **Rationale:** A filename-only grep had leaked set composition
- **Consequence:** Rule widened to blind/ on 10-10; pre-commit hook blocks blind plaintext
- **Verification note:** Verification note: Same fix as the timeline row: incident at QUEUE:144; MANDATE scope widening dated 10-10.
- **Facts:** F-828

### D-023 · Expensive strategy agent (the strategy agent, Fable tier) only for few big decisions, with a self-contained dossier; never loops

- **Date:** 2026-10-02 · **Status:** kept
- **Context:** Strategy agent (the strategy agent) memo S1: three fronts, ~1 in 4 chance the CI lower bound clears 0.50; stop list
- **Decision:** Expensive strategy agent (the strategy agent, Fable tier) only for few big decisions, with a self-contained dossier; never loops
- **Alternatives considered:** Continuous strategy agent
- **Rationale:** Cost: most expensive tier
- **Consequence:** Used once (S1 memo) in the record read
- **Facts:** F-829

### D-024 · Make the memory-fit estimate repack-aware and load with no_extra_bufts on Android only

- **Date:** 2026-10-02 · **Status:** kept
- **Context:** iPhone 13 repack probe: llama.rn does not repack on iOS; fit-repack stays Android-only
- **Decision:** Make the memory-fit estimate repack-aware and load with no_extra_bufts on Android only
- **Alternatives considered:** apply to iOS too; leave as is
- **Rationale:** repack copied ~2.3 GiB of weights into anonymous memory and the phone killed the 4B
- **Consequence:** Android-only variant frozen; iOS unchanged pending device evidence
- **Facts:** F-679

### D-010 · Strategy memo: Android-only, three fronts (knowledge into the 4B's context; device truth + reader; held-out bench + claim); stop iPhone/1.5B quality work, perso

- **Date:** 2026-10-02 06:10 · **Status:** kept
- **Context:** Strategy memo (high-tier model, one call): Android-only, three fronts; stop iPhone/1.5B and prompt work
- **Decision:** Strategy memo: Android-only, three fronts (knowledge into the 4B's context; device truth + reader; held-out bench + claim); stop iPhone/1.5B quality work, persona/prompt work, same-class reader swaps
- **Alternatives considered:** continue broad fronts
- **Rationale:** measured gap; only the 4B near the bar
- **Consequence:** iPhone work stopped; knowledge front closed later that day
- **Facts:** F-697

### D-011 · Bar on the RAW ratio; every publication shows raw + floor-removed + above-always-decline side by side

- **Date:** 2026-10-02 11:15 · **Status:** superseded by D-036 — Floor-adjusted ratio + win/tie/loss became the headline on 2026-10-06 (applied 2026-10-07); the raw rule is still printed as the formal rule.
- **Context:** Author's morning decisions: bar on the raw ratio, but always publish raw + floor-removed + above-decline side by side
- **Decision:** Bar on the RAW ratio; every publication shows raw + floor-removed + above-always-decline side by side
- **Alternatives considered:** lead with floor-adjusted; Floor-adjusted only
- **Rationale:** rubric floor gives a blank system ~0.20–0.31
- **Consequence:** headline later switched to floor-adjusted (D-chron-early-21) while raw stays the formal rule
- **Superseded by:** D-036
- **Facts:** F-264, F-271

### D-012 · Close the knowledge-pack front for the bounty after the big-pack gate failed replay ("no fourth pack iteration")

- **Date:** 2026-10-02 12:40 · **Status:** superseded — packs reopened later only for the deep tier and as products
- **Context:** Big-pack relevance gate fails replay → knowledge front closed for the bounty (kill rule K1)
- **Decision:** Close the knowledge-pack front for the bounty after the big-pack gate failed replay ("no fourth pack iteration")
- **Alternatives considered:** a fourth pack iteration (G1′)
- **Rationale:** kill rule K1 pre-registered in the strategy memo
- **Consequence:** packs reopened later only for the deep tier and as products
- **Facts:** F-072

### D-013 · Run the deep tier (35B MoE); its ratio counts only reported separately from the default, with its latency

- **Date:** 2026-10-02 12:55 · **Status:** kept
- **Context:** Deep tier (35B MoE) approved; counts only if reported separately from the default
- **Decision:** Run the deep tier (35B MoE); its ratio counts only reported separately from the default, with its latency
- **Alternatives considered:** ignore deep tier
- **Rationale:** first candidate lever with a prior above noise; bounty hint about large MoE
- **Consequence:** deep35 +0.060 (first lever above MDE)
- **Facts:** F-074

## 2026-10-03

### D-025 · Move v0.2 plaintext out of researcher-readable paths after an exposure; treat the exposed item as seen

- **Date:** 2026-10-03 · **Status:** kept
- **Context:** Final cut 2 (cut 1b + exposure fix + citation fix)
- **Decision:** Move v0.2 plaintext out of researcher-readable paths after an exposure; treat the exposed item as seen
- **Alternatives considered:** ignore
- **Rationale:** a trace scan printed one held-out item
- **Consequence:** git history still held the plaintext → later "burnt"
- **Verification note:** Verification note: Same date fix as the timeline row: the exposure is dated 10-03, not 10-02 22:05.
- **Facts:** F-138

### D-026 · Declare three health blind sets dev; commission fresh blind sets from writers with no file access

- **Date:** 2026-10-03 · **Status:** kept
- **Context:** Several health blind sets declared dev after traces sat in readable paths
- **Decision:** Declare three health blind sets dev; commission fresh blind sets from writers with no file access
- **Alternatives considered:** keep them blind
- **Rationale:** traces sat in readable paths and were used as dev
- **Consequence:** new sets health-fresh1/2/3, chat-v3, meta-fresh1
- **Facts:** F-304

### D-027 · No human review: an independent Opus reviewer agent decides content/wording; caveat "AI-reviewed, not clinically reviewed" stays

- **Date:** 2026-10-03 · **Status:** kept
- **Context:** "No human review": an independent Opus reviewer agent decides content; caveat "AI-reviewed, not clinically reviewed"
- **Decision:** No human review: an independent Opus reviewer agent decides content/wording; caveat "AI-reviewed, not clinically reviewed" stays
- **Alternatives considered:** human/clinical sign-off; Author or clinician signs off
- **Rationale:** speed; author unavailable for 39 card decisions
- **Consequence:** reviewer changed 25/31 cards
- **Facts:** F-1219, F-834

### D-028 · Single goal = win the bounty; English only; no more work inside the maintainer's app; build a dedicated measurement app

- **Date:** 2026-10-03 · **Status:** kept
- **Context:** No more work inside the app maintainer's app; build "BOAR Bench" measurement app
- **Decision:** Single goal = win the bounty; English only; no more work inside the maintainer's app; build a dedicated measurement app
- **Alternatives considered:** keep improving the general product
- **Rationale:** focus
- **Consequence:** PT/ES lines parked; BOAR Bench built
- **Facts:** F-075

### D-029 · Park the retrieval line after rv2 failed despite more gold in context

- **Date:** 2026-10-03 · **Status:** superseded — retrieval reopened later only for the deep tier
- **Context:** Retrieval v2 killed: gold-in-context 7 → 18 yet quality −0.021
- **Decision:** Park the retrieval line after rv2 failed despite more gold in context
- **Alternatives considered:** another retrieval variant
- **Rationale:** gold-sentence-in-context did not translate into judged quality
- **Consequence:** retrieval reopened later only for the deep tier
- **Facts:** F-572

### D-030 · Single goal = the bounty bar; other quality work after the bounty

- **Date:** 2026-10-03 · **Status:** kept
- **Context:** Direction change: single goal = win the bounty; lanes re-tasked
- **Decision:** Single goal = the bounty bar; other quality work after the bounty
- **Alternatives considered:** keep broad product work
- **Rationale:** deadline + focus
- **Consequence:** lanes re-assigned (model tier, health minimum, speed, demo device)
- **Facts:** F-076

## 2026-10-04

### D-031 · Focus on the 4B default tier; deep tier parked at D1; coordinator runs work with subagents instead of a standing chat team

- **Date:** 2026-10-04 · **Status:** superseded — 4B levers exhausted by 10-05; deep tier reopened 10-06
- **Context:** Direction: 4B default tier only; deep tier parked; no team chat agents, coordinator + subagents
- **Decision:** Focus on the 4B default tier; deep tier parked at D1; coordinator runs work with subagents instead of a standing chat team
- **Alternatives considered:** keep deep tier active
- **Rationale:** work budget; no 12 GB phone
- **Consequence:** 4B levers exhausted by 10-05; deep tier reopened 10-06
- **Facts:** F-704

### D-032 · Adopt cut 3 (verdict guard + arithmetic repair + snakebite text)

- **Date:** 2026-10-04 · **Status:** kept
- **Context:** Cut 3 adopted (cut 2 + verdict guard v3 + arithmetic repair + snakebite text); L1 Δ +0.029 [+0.007, +0.058]
- **Decision:** Adopt cut 3 (verdict guard + arithmetic repair + snakebite text)
- **Alternatives considered:** computed-verdict override family (all failed gates); verdict guard v4, water card, computed verdict
- **Rationale:** L1 Δ +0.029 [+0.007, +0.058], confident-wrong 15 → 9, unsafe 0
- **Consequence:** Cut 3 became the first claim build; claim runs 10-05
- **Facts:** F-1220, F-1221

### D-033 · Park the web-only knowledge pack for the bounty (public-figure blog pack and a research-forum pack were the alternatives).

- **Date:** 2026-10-04 · **Status:** superseded — later replaced by the open-corpus Knowledge Pack program (10-12)
- **Context:** Knowledge-pack sizing: web-only pack parked for the bounty
- **Decision:** Park the web-only knowledge pack for the bounty (public-figure blog pack and a research-forum pack were the alternatives).
- **Alternatives considered:** public-figure blog pack, ethresear.ch pack
- **Rationale:** gains come from non-redistributable sources or in-kit misses; best pack +0.007 net
- **Consequence:** later replaced by the open-corpus Knowledge Pack program (10-12)
- **Facts:** F-084

## 2026-10-05

### D-034 · Fix the KV session save path (KVFIX) and block fragment/figurative instant answers (INSTANT-FRAG) → cut 4

- **Date:** 2026-10-05 · **Status:** kept
- **Context:** Cut 4 = cut 3 + KVFIX + INSTANT-FRAG (+ INSTANT-SUBJ)
- **Decision:** Fix the KV session save path (KVFIX) and block fragment/figurative instant answers (INSTANT-FRAG) → cut 4
- **Alternatives considered:** skip the route gate; threads; repack
- **Rationale:** A15 smoke: every question re-prefilled the prefixes; "capital of France" answered with a Lyon fragment
- **Consequence:** cut 4 built; KVFIX real gate is the device
- **Facts:** F-705

### D-035 · Bench APK with INTERNET permission removed (no-network by construction)

- **Date:** 2026-10-05 · **Status:** kept
- **Context:** No-network measurement APK (INTERNET permission removed by construction)
- **Decision:** Bench APK with INTERNET permission removed (no-network by construction)
- **Alternatives considered:** rely on airplane mode only
- **Rationale:** prove offline operation statically
- **Consequence:** audit verdict NO-NETWORK-BY-CONSTRUCTION; later phone runs used it
- **Facts:** F-706

## 2026-10-06

### D-036 · Headline = floor-adjusted ratio + win/tie/loss (+ share of items ≥ 3/5), raw second; own bar = floor-adj ≥ 0.50 on V-para

- **Date:** 2026-10-06 · **Status:** kept
- **Context:** Honest-metric rewrite: headline becomes floor-adjusted ratio + win/tie/loss, raw second
- **Decision:** Headline = floor-adjusted ratio + win/tie/loss (+ share of items ≥ 3/5), raw second; own bar = floor-adj ≥ 0.50 on V-para
- **Alternatives considered:** keep raw headline; Raw headline
- **Rationale:** raw 0.50 is ~61 % free because of the rubric floor
- **Consequence:** board and claim draft rewritten 10-06 22:40
- **Verification note:** citation fix (D1 is l.53). Date nuance: decided 10-06 in the audit, applied to the claim draft v3.1 on 10-07 (CRITIQUE-2026-10-16.md:24); floor scale pre-registered as companion 10-02 (analysis-plan.md:22-25)
- **Facts:** F-1146, F-1226, F-1227

### D-037 · Treat v0.2 as burnt (dev); a final number needs v0.3 written outside the Claude family

- **Date:** 2026-10-06 · **Status:** kept
- **Context:** Retrieval scorecard: coverage is the largest failure bucket (49 %); recall@5 0.333
- **Decision:** Treat v0.2 as burnt (dev); a final number needs v0.3 written outside the Claude family
- **Alternatives considered:** rewrite git history; keep using v0.2 as held-out
- **Rationale:** plaintext in private git history + 4 runs + a targeted fix
- **Consequence:** v0.3 spec written 10-07; items not written by 10-10
- **Verification note:** citation fix: D5 is l.57
- **Facts:** F-1248, F-1249

### D-038 · Freeze the claim build at cut 6; later only routing/safety fixes that leave v0.1 answers unchanged

- **Date:** 2026-10-06 · **Status:** superseded by D-046 — Relaxed on 2026-10-07: cut 7 added FACTS r6, which changed 8 v0.1 answers.
- **Context:** Claim/device build frozen at cut 6; later only routing/safety fixes
- **Decision:** Freeze the claim build at cut 6; later only routing/safety fixes that leave v0.1 answers unchanged
- **Alternatives considered:** keep shipping answer-changing arms
- **Rationale:** stable claim evidence
- **Consequence:** cut 7 later added the fact table (0 fires on held-out sets)
- **Verification note:** superseded on 10-07: cut 7 (FACTS r6) changed 8 v0.1 answers, against the 'v0.1 answers unchanged' clause (CUT7.md:29; QUEUE l.770)
- **Superseded by:** D-046
- **Facts:** F-331, F-723

### D-039 · Stop answer-identical 4B arms; reopen the deep tier as the primary quality lever

- **Date:** 2026-10-06 · **Status:** kept
- **Context:** Retrieval scorecard: coverage is the largest failure bucket (49 %); recall@5 0.333
- **Decision:** Stop answer-identical 4B arms; reopen the deep tier as the primary quality lever
- **Alternatives considered:** continue 4B polishing
- **Rationale:** 15 arms, 0 ratio movement
- **Consequence:** deep-tier line ran 10-07 → 10-10
- **Facts:** F-576

### D-041 · Declare v0.2 burnt → dev after its plaintext was found in git history

- **Date:** 2026-10-06 · **Status:** kept
- **Context:** v0.2 ruled burnt (plaintext in private bench repo history) → dev
- **Decision:** Declare v0.2 burnt → dev after its plaintext was found in git history
- **Alternatives considered:** Keep calling it held-out
- **Rationale:** Honesty: builders could have seen it
- **Consequence:** An unexposed held-out number needs a v0.3 written outside the Claude family (0 items as of 10-17; open front OF-3)
- **Verification note:** Verification note: Public v0.2 row is SET-STATUS:14 (not :17).
- **Facts:** F-1250

### D-042 · Keep FACTS r6 as head despite FAIL by frozen rule (recall 70 % < 75 %)

- **Date:** 2026-10-06 · **Status:** kept
- **Context:** FACTS r6 on blind set 4: recall 70 % < 75 % → FAIL; kept as head by decision
- **Decision:** Keep FACTS r6 as head despite FAIL by frozen rule (recall 70 % < 75 %)
- **Alternatives considered:** close at r5; build r7 (forbidden by criterion)
- **Rationale:** r6 dominates r5 on every frozen measure; precision 96.6 %, FP 0/100 adversarial
- **Consequence:** Shipped in cut 7; stated as "FAIL stands"
- **Facts:** F-332

### D-043 · Lead every public number with floor-adjusted + win-rate, not raw

- **Date:** 2026-10-06 · **Status:** kept
- **Context:** Honest-metric rewrite: headline becomes floor-adjusted ratio + win/tie/loss, raw second
- **Decision:** Lead every public number with floor-adjusted + win-rate, not raw
- **Alternatives considered:** keep raw as headline (pre-registered formal rule)
- **Rationale:** raw 0.50 is a rubric-floor artefact (always-decline ≈ 0.31 raw)
- **Verification note:** method notes date the switch 10-06, results notes 10-07; both are right for different steps. Also: the floor scale itself was pre-registered as a companion metric on 10-02, which answers the 'moving goalposts' attack
- **Facts:** F-277

### D-044 · Adopt CUT5-LITE (KV prefix for no-source prompts + route-gate skip), reject CUT5-SPEED

- **Date:** 2026-10-06 · **Status:** kept
- **Context:** Cut 5 = cut 4 + no-source KV prefix + route-gate skip (CUT5-LITE adopted; CUT5-SPEED rejected on desktop gate)
- **Decision:** Adopt CUT5-LITE (KV prefix for no-source prompts + route-gate skip), reject CUT5-SPEED
- **Alternatives considered:** ship all speed arms
- **Rationale:** CUT5-SPEED failed its desktop speed gate (1.071× vs ≤ 0.8); lite was identity-safe
- **Consequence:** cut 5 = device-day candidate
- **Facts:** F-722

### D-045 · Adopt DETMAX → cut 6

- **Date:** 2026-10-06 · **Status:** kept
- **Context:** Cut 6 = cut 5 + DETMAX (detector scores window and current turn)
- **Decision:** Adopt DETMAX → cut 6
- **Alternatives considered:** no change; lexical follow-up fix (HFU, failed)
- **Rationale:** chit-chat before an emergency lost 7/240 routes; DETMAX 0/240
- **Verification note:** citation fix (l.46 is blank)
- **Facts:** F-333

### D-040 · Cheap judge for triage (Sonnet-low, replaced by Haiku 5.5-low on 10-07); Opus only for confirmation and claim numbers

- **Date:** 2026-10-06 21:25 · **Status:** superseded by D-049 — Sonnet-low was replaced by Claude Haiku 5.5-low as the L1 judge on 2026-10-07 (HAIKUJUDGE).
- **Context:** Cheaper judge triage adopted (Sonnet-low, later Haiku)
- **Decision:** Cheap judge for triage (Sonnet-low, replaced by Haiku 5.5-low on 10-07); Opus only for confirmation and claim numbers
- **Alternatives considered:** Opus for everything
- **Rationale:** judge is the largest cost
- **Consequence:** judge calls fell from 12k–20k calls / 6 days to ≈ 1.5k / 2 days
- **Superseded by:** D-049
- **Facts:** F-147, F-157

## 2026-10-07

### D-047 · v0.3 written by the author with a non-Claude web model; hashes only before scoring

- **Date:** 2026-10-07 · **Status:** superseded by D-123 — On 2026-10-18 v0.3 was dropped before closure (D5); the v0.4 ruler set replaced it.
- **Context:** Bench v0.3 spec accepted: claim set to be written outside the Claude family by the author with a non-Claude web-UI model
- **Decision:** v0.3 written by the author with a non-Claude web model; hashes only before scoring
- **Alternatives considered:** Claude-written items; Claude subagent writers (as v0.2)
- **Rationale:** self-preference risk; burnt v0.2
- **Consequence:** spec ready; items not written by 10-10
- **Superseded by:** D-123
- **Facts:** F-1148, F-1251

### D-049 · Haiku 5.5-low replaces Sonnet-low as L1 judge

- **Date:** 2026-10-07 · **Status:** kept
- **Context:** Haiku 5.5-low becomes the L1 triage judge; judge sharding N = 4; "no device exists" ruling
- **Decision:** Haiku 5.5-low replaces Sonnet-low as L1 judge
- **Alternatives considered:** Sonnet-low; Haiku medium
- **Rationale:** same winner 54/57, 3.5 s/call, ~14× cheaper
- **Consequence:** adopted; known to compress gaps
- **Facts:** F-1149

### D-050 · Local open-weights judge (Gemma 4 26B) allowed for triage/ranking only, never for the number

- **Date:** 2026-10-07 · **Status:** kept
- **Context:** JUDGE2: local open-weights judge (Gemma 4 26B) keeps the ranking but scores +0.11 above Opus
- **Decision:** Local open-weights judge (Gemma 4 26B) allowed for triage/ranking only, never for the number
- **Alternatives considered:** adopt as main judge
- **Rationale:** keeps ranking, +0.11 lenient, κ 0.32-0.55
- **Consequence:** not used for headline numbers
- **Facts:** F-283

### D-051 · Shard the judge: N = 4 default for Haiku L1 and for Opus L2/claim

- **Date:** 2026-10-07 · **Status:** kept
- **Context:** JUDGE2: local open-weights judge (Gemma 4 26B) keeps the ranking but scores +0.11 above Opus
- **Decision:** Shard the judge: N = 4 default for Haiku L1 and for Opus L2/claim
- **Alternatives considered:** sequential; N = 8
- **Rationale:** ×4.5 wall gain, 0 rate limits, same winners
- **Consequence:** in force; a stopped shard is resumed, never skipped
- **Facts:** F-159

### D-052 · Haiku 5.5-low as L1 triage judge, Opus only to confirm and for claim numbers; judge sharded N = 4

- **Date:** 2026-10-07 · **Status:** kept
- **Context:** Haiku 5.5-low becomes the L1 triage judge; judge sharding N = 4; "no device exists" ruling
- **Decision:** Haiku 5.5-low as L1 triage judge, Opus only to confirm and for claim numbers; judge sharded N = 4
- **Alternatives considered:** Opus everywhere; Sonnet-low triage; Sonnet-low; local Gemma (ranking only, +0.11 lenient)
- **Rationale:** ≈ 14× cheaper than the previous triage judge; same winner as Opus 54/57
- **Consequence:** Haiku compresses gaps 15-30 %; near-miss escalation rules added
- **Facts:** F-1150, F-1151

### D-053 · "No device exists": device tasks dormant

- **Date:** 2026-10-07 · **Status:** reversed — A 12 GB-class phone (10.7 GiB usable) ran cut 7 on 2026-10-14.
- **Context:** Haiku 5.5-low becomes the L1 triage judge; judge sharding N = 4; "no device exists" ruling
- **Decision:** "No device exists": device tasks dormant
- **Alternatives considered:** Keep proposing device work
- **Rationale:** No 12 GB phone available
- **Consequence:** Later reversed in practice when a 10.7 GiB phone ran cut 7 on 10-14
- **Facts:** F-733

### D-046 · Cut 7 = cut 6 + FACTS r6 (adopted on gates: 0 fires on held-out sets); no relaxed lowercase rule; fine-tune data 1k go; "no device exists"

- **Date:** 2026-10-07 09:23 · **Status:** kept
- **Context:** Cut 7 = cut 6 + FACTS r6; v0.3 to be written outside the Claude family; "no device exists"
- **Decision:** Cut 7 = cut 6 + FACTS r6 (adopted on gates: 0 fires on held-out sets); no relaxed lowercase rule; fine-tune data 1k go; "no device exists"
- **Alternatives considered:** wait for more recall; re-run full claim runs (burns held-out again); no FACTS; r7
- **Rationale:** deterministic facts lever; no phone
- **Consequence:** cut 7 frozen; fine-tune data failed review same day
- **Facts:** F-1230, F-353, F-745

### D-048 · Autonomous mandate: keep running rounds without asking; stop only for irreversible/expensive items

- **Date:** 2026-10-07 14:26 · **Status:** kept
- **Context:** JUDGE2: local open-weights judge (Gemma 4 26B) keeps the ranking but scores +0.11 above Opus
- **Decision:** Autonomous mandate: keep running rounds without asking; stop only for irreversible/expensive items
- **Alternatives considered:** ask per round
- **Rationale:** throughput
- **Consequence:** deep-tier rounds ran unattended
- **Facts:** F-588

## 2026-10-08

### D-054 · SLICE20 triage before any full deep/held-out arm

- **Date:** 2026-10-08 · **Status:** superseded — later replaced by stratified random slices (10-10)
- **Context:** SLICE20: every deep-tier / held-out-style arm starts on a 20-item slice
- **Decision:** SLICE20 triage before any full deep/held-out arm
- **Alternatives considered:** full sets always
- **Rationale:** ~60 % generation saving on NO arms
- **Consequence:** later replaced by stratified random slices (10-10)
- **Facts:** F-169

## 2026-10-09

### D-055 · V-para status: held-out for the 4B claim runs; dev-style for everything measured after 10-06

- **Date:** 2026-10-09 · **Status:** kept
- **Context:** V-para status ruling: held-out for the 4B claim runs, dev-style for everything measured after 2026-10-06
- **Decision:** V-para status: held-out for the 4B claim runs; dev-style for everything measured after 10-06
- **Alternatives considered:** keep calling it blind; keep calling it held-out
- **Rationale:** exposure ledger showed conflicting status labels
- **Consequence:** every deep-tier number on V-para is labelled dev-style
- **Facts:** F-1232, F-1233

### D-056 · Recommend thinking budget 512 for the deep tier

- **Date:** 2026-10-09 · **Status:** kept
- **Context:** DT512: thinking budget 512 = 1024 quality at 0.55× time → recommended config
- **Decision:** Recommend thinking budget 512 for the deep tier
- **Alternatives considered:** 1024; 256; 1024 (slower), 256 (−0.028, CHEAPER-LOSS), Gemma + thinking (−0.028); 256 (loses), 1024, 3072, Gemma 26B
- **Rationale:** CHEAPER-PARITY with 1024 at 0.55× time
- **Consequence:** becomes the "recommended deep configuration"
- **Facts:** F-598, F-599, F-748

## 2026-10-10

### D-057 · Near-miss rule: a Haiku Δ within 0.01 of a threshold triggers Opus on the same ids

- **Date:** 2026-10-10 · **Status:** kept
- **Context:** Near-miss rule after a Haiku triage stopped an arm Opus later rated +0.048
- **Decision:** Near-miss rule: a Haiku Δ within 0.01 of a threshold triggers Opus on the same ids
- **Alternatives considered:** trust Haiku; trust Haiku always
- **Rationale:** Haiku compressed a +0.048 Opus gap to +0.027
- **Consequence:** applied to THINK4B
- **Facts:** F-1158, F-613

### D-058 · Seed-noise reading rule (V-para one-seed deep Δ < ~0.03 is noise; later raised to 0.05)

- **Date:** 2026-10-10 · **Status:** superseded by D-113 — Threshold raised from 0.03 to 0.05 on 2026-10-16 after the outside critique (SEEDVAR showed a −0.039 gap between seeds).
- **Context:** SEEDVAR: H over 3 seeds mean floor-adj 0.432 (SD 0.025); one-seed deep Δ < 0.03 = seed noise
- **Decision:** Seed-noise reading rule (V-para one-seed deep Δ < ~0.03 is noise; later raised to 0.05)
- **Alternatives considered:** single-seed verdicts; single-seed decisions; treat one-seed rows as decisive
- **Rationale:** SEEDVAR three-seed spread
- **Consequence:** in CLAUDE.md and RULE-CHANGES
- **Superseded by:** D-113
- **Facts:** F-1159, F-1160, F-1162

### D-062 · Decide direction on v0.2 (seed-stable), confirm on V-para with 2 seeds; adopt a lever only after two-seed V-para confirmation

- **Date:** 2026-10-10 · **Status:** kept
- **Context:** Criterion template with mandatory Power block; random-20 slices; bar table frozen
- **Decision:** Decide direction on v0.2 (seed-stable), confirm on V-para with 2 seeds; adopt a lever only after two-seed V-para confirmation
- **Alternatives considered:** decide on V-para one seed
- **Rationale:** v0.2 per-item seed r 0.90 vs V-para 0.5-0.7
- **Consequence:** in force
- **Facts:** F-176

### D-063 · Fail-closed pipeline: errored traces/missing ids stop the run or score at the floor

- **Date:** 2026-10-10 · **Status:** kept
- **Context:** Fail-closed judge pipeline: errored or missing items now stop the run or score at the floor instead of vanishing
- **Decision:** Fail-closed pipeline: errored traces/missing ids stop the run or score at the floor
- **Alternatives considered:** drop silently; Manual checks
- **Rationale:** the old judge silently dropped errored traces, flattering a failing device
- **Consequence:** flags `--strict`, `--floor-errored`, `--floor-missing`
- **Facts:** F-179, F-752

### D-064 · Random stratified 20-id slices (seed 7) replace the "20 hardest items" slice

- **Date:** 2026-10-10 · **Status:** kept
- **Context:** Power block mandatory in every criterion; random stratified 20-id slices replace the "20 hardest" slice
- **Decision:** Random stratified 20-id slices (seed 7) replace the "20 hardest items" slice
- **Alternatives considered:** keep signal20; Hardest-20 slices
- **Rationale:** hardest-20 inflated deltas (+0.091 slice vs +0.026 full)
- **Consequence:** in force; slice only screens for futility
- **Facts:** F-1161, F-178

### D-065 · Win-rate reported, never gated (later: proposal to drop the win-rate conjunct because it is saturated at 0)

- **Date:** 2026-10-10 · **Status:** kept
- **Context:** Author's direction: research on the Mac mini only until the bar is met; device and claim work after
- **Decision:** Win-rate reported, never gated (later: proposal to drop the win-rate conjunct because it is saturated at 0)
- **Alternatives considered:** gate on win-rate > 0
- **Rationale:** every phone system scores 0 wins vs a 4.9/5 reference
- **Verification note:** the plan never gated on win-rate, but the deep-tier arm reports of 10-08/09 read the bar as 'floor-adj CI low > 0.50 AND win-rate > 0'; 'reported, never gated' was fixed in BAR-TABLE on 10-10 after RND-REVIEW B1. State both
- **Facts:** F-753

### D-067 · Declare the deep-tier line closed on desktop and the 4B side closed

- **Date:** 2026-10-10 · **Status:** kept
- **Context:** Desktop queue empty: 4B side and deep-tier line both closed
- **Decision:** Declare the deep-tier line closed on desktop and the 4B side closed
- **Alternatives considered:** keep sweeping configs
- **Rationale:** model, parity, thinking, budget, persona/context, routing all measured
- **Consequence:** Research moved to Knowledge Packs (10-12)
- **Facts:** F-614

### D-068 · Keep retrieval on the deep path

- **Date:** 2026-10-10 · **Status:** kept
- **Context:** DEEPRERANK, MP4B, DEEPITER, DEEPCOV-FB closed (retrieval-side levers on the deep tier)
- **Decision:** Keep retrieval on the deep path
- **Alternatives considered:** drop packs for speed
- **Rationale:** no-pack −0.045 (−0.083…−0.011)
- **Consequence:** kept
- **Facts:** F-997

### D-060 · Proceed on stated defaults for the claim path (debug-signed APK, raw formal + floor-adj + win-rate, no v0.3, no device relay)

- **Date:** 2026-10-10 21:05 · **Status:** superseded — superseded 45 min later by the STOP
- **Context:** Decision note with defaults sent to the author (claim vehicle, bar scale "raw formal + floor-adj + win-rate", no v0.3, no device relay)
- **Decision:** Proceed on stated defaults for the claim path (debug-signed APK, raw formal + floor-adj + win-rate, no v0.3, no device relay)
- **Alternatives considered:** ask and wait
- **Rationale:** unblock work without waiting on the author
- **Consequence:** superseded 45 min later by the STOP
- **Facts:** F-758

### D-059 · Research on the Mac mini only until the bar is met; no APK/device/claim-package work

- **Date:** 2026-10-10 21:54 · **Status:** superseded — The closing sprint from 2026-10-14 brought app and release work back (upstream PR, public repositories).
- **Context:** Author's direction: research on the Mac mini only until the bar is met; device and claim work after
- **Decision:** Research on the Mac mini only until the bar is met; no APK/device/claim-package work
- **Alternatives considered:** claim-path first (review's recommendation); A deep-tier arms; B v0.3 outside Claude; C bigger model
- **Rationale:** author's direction after the process review
- **Consequence:** handoff rewritten for research scope
- **Facts:** F-763, F-854

### D-061 · Every deciding run needs a frozen criterion with a Power block; slices = random20 files

- **Date:** 2026-10-10 22:09 · **Status:** kept
- **Context:** Criterion template with mandatory Power block; random-20 slices; bar table frozen
- **Decision:** Every deciding run needs a frozen criterion with a Power block; slices = random20 files
- **Alternatives considered:** signal20 slices (retired); voluntary; Optional
- **Rationale:** stop under-powered closures
- **Consequence:** arm.sh refuses launch without the block
- **Facts:** F-177, F-180, F-195

## 2026-10-11

### D-072 · Common-mode CIs for deep-tier rows: CI = Δ ± 1.96·sqrt(SE_item² + 2σ_run²)

- **Date:** 2026-10-11 · **Status:** kept
- **Context:** JUDGEVAR: re-judging unchanged answers gives σ_judge ≈ 0.003; common-mode CIs adopted for deep-tier rows
- **Decision:** Common-mode CIs for deep-tier rows: CI = Δ ± 1.96·sqrt(SE_item² + 2σ_run²)
- **Alternatives considered:** item bootstrap only; plain item bootstrap
- **Rationale:** item bootstrap ignores run-level seed noise
- **Consequence:** deep CIs ~1.2-1.3× wider; readings unchanged
- **Facts:** F-1176, F-1236

### D-073 · Negative results relabelled "not detected at MDE x (n, seeds)" when under-powered

- **Date:** 2026-10-11 · **Status:** kept
- **Context:** CLOSED.md registry built (36 rows); honesty relabel "not detected at MDE x" for under-powered negatives
- **Decision:** Negative results relabelled "not detected at MDE x (n, seeds)" when under-powered
- **Alternatives considered:** keep "closed"; Plain "closed"
- **Rationale:** "closed" overstated weak negatives
- **Consequence:** CLOSED.md rows carry MDE and reopen condition
- **Verification note:** the critique names 7 n≈20 closures with CI upper ≥ +0.03 (R10, R25, R31, R83, R84, R85, R97); R10 and R25 were already 'not detected', so 5 still need the relabel (cited l.47-50 are about exposure)
- **Facts:** F-1177, F-1178, F-198

### D-074 · Verdict labels LEVER / SMALL / NO / "not decided at MDE"; adopt only after two-seed confirmation on V-para

- **Date:** 2026-10-11 · **Status:** kept
- **Context:** Verdict labels LEVER / SMALL / NO / "not detected at MDE"; honesty relabel of under-powered closures
- **Decision:** Verdict labels LEVER / SMALL / NO / "not decided at MDE"; adopt only after two-seed confirmation on V-para
- **Alternatives considered:** Point-estimate promotion
- **Rationale:** Stop over-reading noise
- **Consequence:** Adopted levers after 10-08: 0 on the bounty set
- **Facts:** F-087

### D-069 · Run research as an unattended self-paced loop (one experiment per tick, META every 8 ticks)

- **Date:** 2026-10-11 03:4x · **Status:** kept
- **Context:** LOOP-PROGRAM written: unattended self-paced loop, one experiment per tick
- **Decision:** Run research as an unattended self-paced loop (one experiment per tick, META every 8 ticks)
- **Alternatives considered:** session-by-session manual runs; Author-driven sessions
- **Rationale:** use idle machine time; keep method improving
- **Consequence:** 133 ticks over 10-11→10-14
- **Facts:** F-857, F-858

### D-070 · Measure the loss map before more levers (LOSSMAP first)

- **Date:** 2026-10-11 12:10 · **Status:** kept
- **Context:** Loop tick 1: LOSSMAP measures where the deep tier loses points
- **Decision:** Measure the loss map before more levers (LOSSMAP first)
- **Alternatives considered:** keep running backlog order
- **Rationale:** direct levers at the biggest loss bucket
- **Consequence:** re-ranked backlog; absent knowledge = 0.59 / 0.55 of loss
- **Facts:** F-860

## 2026-10-12

### D-082 · Knowledge packs = format 2 SQLite, per-row attribution, four artefacts per pack (card, self-test, coverage probe, crowding probe)

- **Date:** 2026-10-12 · **Status:** kept
- **Context:** PACKCOND P1–P4, PACKDENSE, HEALTHQ, SECTIONHIT: in-pack loss is retrieval, not grounding
- **Decision:** Knowledge packs = format 2 SQLite, per-row attribution, four artefacts per pack (card, self-test, coverage probe, crowding probe)
- **Alternatives considered:** format v3 first
- **Rationale:** zero format risk; licence compliance; measured crowding failure
- **Consequence:** 11 packs built and published 10-13
- **Facts:** F-1005

### D-083 · "Default-eligible" only if a pack holds ≤ 0.40 of kept slots and does not lower kit gold; otherwise user-selected only

- **Date:** 2026-10-12 · **Status:** kept
- **Context:** Author: build a pack-authoring workflow ("we will be the first author with publications")
- **Decision:** "Default-eligible" only if a pack holds ≤ 0.40 of kept slots and does not lower kit gold; otherwise user-selected only
- **Alternatives considered:** install everything
- **Rationale:** crowding measured
- **Verification note:** citation fix: the rule is l.50, statuses in the table l.35-45 (5 default-eligible, 6 user-selected)
- **Facts:** F-1006

### D-075 · Close QUANTCEIL as "not detected at MDE 0.03" after V-para two seeds

- **Date:** 2026-10-12 07:55 · **Status:** kept
- **Context:** QUANTCEIL: 3-bit quant of deep model +0.004 (not detected); cycle adds 0 V-para points per 1,804 judge calls
- **Decision:** Close QUANTCEIL as "not detected at MDE 0.03" after V-para two seeds
- **Alternatives considered:** adopt on v0.2 wrong-bucket repair
- **Rationale:** seeds split +0.030 / −0.022
- **Consequence:** model-knowledge levers on this hardware declared exhausted
- **Facts:** F-207

### D-076 · Withdraw "facts are not in Wikipedia"; adopt the peer research's task chain

- **Date:** 2026-10-12 14:14 · **Status:** kept
- **Context:** Correction: "facts are not in Wikipedia" withdrawn (scope was the top-100k pack only)
- **Decision:** Withdraw "facts are not in Wikipedia"; adopt the peer research's task chain
- **Alternatives considered:** keep the closure; build a new corpus right away
- **Rationale:** peer review showed WIKISECTION covered only one pack and part of the items
- **Consequence:** WIKIFULL stages run; result 9/34 (a lower bound)
- **Verification note:** Verification note: Outcome should read "9/34 verified (lower bound, MARGINAL)", not "9/34 (a lower bound)".
- **Facts:** F-1003, F-1011

### D-077 · Phone-time wording: deep + think 512 ≈ 1.9–2.8 min on a Pixel 8 Pro CPU; competitor percentages never quoted as a gap

- **Date:** 2026-10-12 14:14 · **Status:** kept
- **Context:** SYNTHDEEP, WIKISECTION, DEEPHEDGE closed at 0-call gates
- **Decision:** Phone-time wording: deep + think 512 ≈ 1.9–2.8 min on a Pixel 8 Pro CPU; competitor percentages never quoted as a gap
- **Alternatives considered:** the earlier 3.5–5 min figure
- **Rationale:** corrected premises 2 and 5
- **Consequence:** applied in all later texts
- **Facts:** F-768

### D-078 · Pivot to Knowledge Packs; primary metric = in-pack conditional ratio

- **Date:** 2026-10-12 20:06 · **Status:** kept
- **Context:** Author's direction: Knowledge Packs; research question becomes conditional quality with the matching pack installed
- **Decision:** Pivot to Knowledge Packs; primary metric = in-pack conditional ratio
- **Alternatives considered:** stay on the bar; keep deep-tier sweeps; non-Wikipedia corpus
- **Rationale:** the product is a small model + user-selected packs; the unconditional bar was not moving
- **Consequence:** P1–P4, pack workflow, pack stack
- **Facts:** F-1004, F-1012

### D-079 · Build a pack-authoring workflow; agents may write the 20 public self-tests per pack; held-out claim items stay non-Claude

- **Date:** 2026-10-12 22:32 · **Status:** kept
- **Context:** Author: build a pack-authoring workflow ("we will be the first author with publications")
- **Decision:** Build a pack-authoring workflow; agents may write the 20 public self-tests per pack; held-out claim items stay non-Claude
- **Alternatives considered:** only use existing packs
- **Rationale:** "we will be the first author with publications"
- **Consequence:** 11 packs published 10-13
- **Facts:** F-1015

### D-080 · Pack format unchanged (format 2); licence policy PD/CC0/CC BY/CC BY-SA only; never NC; per-row attribution for Stack Exchange; archive.org pre-2024 SE dumps, no

- **Date:** 2026-10-12 22:46 · **Status:** kept
- **Context:** Pack catalogue + authoring workflow (licence policy PD/CC0/CC BY/CC BY-SA only)
- **Decision:** Pack format unchanged (format 2); licence policy PD/CC0/CC BY/CC BY-SA only; never NC; per-row attribution for Stack Exchange; archive.org pre-2024 SE dumps, not the login-gated official dumps
- **Alternatives considered:** format v3 now; NC corpora (wikiHow, WHO, OpenStax); Kiwix 2026 ZIMs (fresher)
- **Rationale:** zero format risk; licence compliance
- **Consequence:** applied to all published packs
- **Verification note:** citation fix: D-K5 is l.12 (l.13 is D-K6)
- **Facts:** F-1017, F-368

### D-081 · Autonomy rule: never ask for approval; paid API only when no free equivalent, capped and logged

- **Date:** 2026-10-12 23:22 · **Status:** kept
- **Context:** Autonomy rule from the author: never ask for approval; paid API only when no free equivalent
- **Decision:** Autonomy rule: never ask for approval; paid API only when no free equivalent, capped and logged
- **Alternatives considered:** per-step approval
- **Rationale:** author said Claude usage is not the constraint
- **Consequence:** loop ran without approval asks
- **Facts:** F-870

## 2026-10-13

### D-090 · Never idle while 0-paid-call work exists; no Haiku cap

- **Date:** 2026-10-13 · **Status:** kept
- **Context:** Author challenges 9+ idle ticks; loop un-idled; rules 24 (never idle while 0-call work exists) and 25 (no Haiku cap)
- **Decision:** Never idle while 0-paid-call work exists; no Haiku cap
- **Alternatives considered:** Keep caps
- **Rationale:** Author objected after 9 idle ticks ("why idle when I asked to never stop?", paraphrase)
- **Consequence:** 10-14 log: 0 idle ticks; later critic warns "idle lane = failure" rewards trivial probes
- **Facts:** F-1185

### D-084 · Publish packs that pass the four-artefact check (card, self-test, coverage, crowding) on HF under the author's standing OK

- **Date:** 2026-10-13 00:01 · **Status:** kept
- **Context:** Pack-stack technical report (crowding, routing, keep, reader)
- **Decision:** Publish packs that pass the four-artefact check (card, self-test, coverage, crowding) on HF under the author's standing OK
- **Alternatives considered:** hold until measured further
- **Rationale:** public reuse; licence clarity per pack
- **Consequence:** 7 + 2 + 2 packs published
- **Facts:** F-1036

### D-085 · No cap on Haiku judge calls (Rule 25)

- **Date:** 2026-10-13 10:20 · **Status:** kept
- **Decision:** No cap on Haiku judge calls (Rule 25)
- **Alternatives considered:** [usage detail removed]
- **Rationale:** Haiku is cheap triage; idle caps cost machine time
- **Consequence:** 720-call scoring passes became routine
- **Facts:** F-876

### D-086 · Run an oracle/ceiling cell (ORACLE-ST) before more pre-processing levers

- **Date:** 2026-10-13 13:4x · **Status:** kept
- **Context:** A side session re-judged existing traces only: PACKS-L2, ORACLE-ST, RIVALSET, red-team of the claim, pipeline and ledger audits
- **Decision:** Run an oracle/ceiling cell (ORACLE-ST) before more pre-processing levers
- **Alternatives considered:** keep adding retrieval tricks
- **Rationale:** decide whether reader or retrieval is the wall
- **Consequence:** ceiling +0.095 found; became a standing rule (LOOP v2 D8)
- **Facts:** F-1045

### D-087 · Routing among packs closed at the product level; keep rule + quota only an optional setting

- **Date:** 2026-10-13 15:44 · **Status:** kept
- **Context:** REPORT-PACKS drafted and independently reviewed (39 edits)
- **Decision:** Routing among packs closed at the product level; keep rule + quota only an optional setting
- **Alternatives considered:** top-1 router, 4B zero-shot classifier
- **Rationale:** crowding cost small (−0.016 Haiku / −0.019 Opus); routers 0.25–0.61 accuracy
- **Consequence:** product reading: ship small user-selected packs, no automatic routing
- **Facts:** F-1046

### D-089 · Claim draft v3.9 adopts the red-team findings (v0.2 "formerly held-out", V-para writer disclosed, verdict reuse disclosed)

- **Date:** 2026-10-13 22:08 · **Status:** kept
- **Context:** WIKIFULL (all of Wikipedia + 2026-10-01 delta) holds the missing fact for 9/34 (a lower bound) V-para absent items: Wikipedia closed as kit content for the bar
- **Decision:** Claim draft v3.9 adopts the red-team findings (v0.2 "formerly held-out", V-para writer disclosed, verdict reuse disclosed)
- **Alternatives considered:** keep v3.8
- **Rationale:** red-team found no inflated number but 9 overclaiming sentences
- **Consequence:** 41 edits applied
- **Facts:** F-216

## 2026-10-14

### D-093 · SFT of the 4B closed unless a teacher reaches ≥ 50 % faithfulness on distractor-rich targets

- **Date:** 2026-10-14 · **Status:** kept
- **Context:** SFT TEACHER-PROBE NO-GO (deep teacher 6/120 faithful); fine-tuning line closed
- **Decision:** SFT of the 4B closed unless a teacher reaches ≥ 50 % faithfulness on distractor-rich targets
- **Alternatives considered:** train anyway
- **Rationale:** Haiku teacher 38 %, deep teacher 5 %
- **Consequence:** closed (R71)
- **Facts:** F-481

### D-094 · Rule 29 experiment economics: Ceiling block (launch only if ≥ 2×MDE) and Budget block (smoke, wall caps, kill rule)

- **Date:** 2026-10-14 · **Status:** kept
- **Context:** RULE 29 experiment economics: Ceiling + Budget + Transfer blocks; no Opus on dev sets
- **Decision:** Rule 29 experiment economics: Ceiling block (launch only if ≥ 2×MDE) and Budget block (smoke, wall caps, kill rule)
- **Alternatives considered:** free launches; status quo; Keep "any Haiku Δ > 0 → Opus"
- **Rationale:** ≈ 1,440 avoidable Opus calls and long bad tests
- **Consequence:** reviewed, edits applied
- **Facts:** F-885, F-886, F-889, F-891

### D-098 · Bounty chat gets method, packs and device proof only; numbers only after the shared rubric exists

- **Date:** 2026-10-14 · **Status:** kept
- **Context:** RULE 29 experiment economics: Ceiling + Budget + Transfer blocks; no Opus on dev sets
- **Decision:** Bounty chat gets method, packs and device proof only; numbers only after the shared rubric exists
- **Alternatives considered:** post scores
- **Rationale:** numbers without a shared rubric are not comparable
- **Consequence:** post drafts carry no scores
- **Facts:** F-1058

### D-099 · Verdict, registry row (CLOSED.md) and exposure row in the same commit

- **Date:** 2026-10-14 · **Status:** kept
- **Context:** Coordinator session dies on an expired login token; mini idle 2.2 h
- **Decision:** Verdict, registry row (CLOSED.md) and exposure row in the same commit
- **Alternatives considered:** separate bookkeeping; Periodic backfill
- **Rationale:** ledger audit found 48 verdicts without registry rows
- **Consequence:** in force
- **Facts:** F-887, F-888

### D-091 · Run doc2query PoC overnight on the MacBook instead of renting a GPU

- **Date:** 2026-10-14 02:53 · **Status:** kept
- **Context:** MICROD2Q (doc2query) fails; doc2query closed
- **Decision:** Run doc2query PoC overnight on the MacBook instead of renting a GPU
- **Alternatives considered:** rented GPU
- **Rationale:** cost [usage detail removed] vs free local hours
- **Consequence:** 4.77 h, FAIL; later cited as an avoidable loss (speed gate overridden by an addendum)
- **Facts:** F-921

### D-092 · HEADPASS-X2b = the pack line's retrieval recommendation for format-v3 packs; X1 for format-2 packs

- **Date:** 2026-10-14 15:38 · **Status:** kept
- **Context:** HEADPASS-X2b lever (+0.066 on 180 dev self-tests)
- **Decision:** HEADPASS-X2b = the pack line's retrieval recommendation for format-v3 packs; X1 for format-2 packs
- **Alternatives considered:** reranker X3; unbudgeted X2; X1 only (+0.033); X3 reranker (FAIL reach, 21 s/item)
- **Rationale:** Opus +0.066 (+0.043…+0.091), no harm on kit
- **Consequence:** X3 failed at step 0; X2b staged for after 10-20 (PR-2)
- **Facts:** F-1059, F-1070

### D-095 · LOOP v2 decisions D1–D12 (machine-side queue runners, smoke-first, STATE line, lanes, guards as scripts, handoff instead of compaction, daily brief, watchdog)

- **Date:** 2026-10-14 19:56 · **Status:** kept
- **Context:** LOOP v2 retrospective: 133 ticks, ≈ 12.0k Claude calls (≈ 10.5k judge calls), 1 lever, ≈31 avoidable machine-hours
- **Decision:** LOOP v2 decisions D1–D12 (machine-side queue runners, smoke-first, STATE line, lanes, guards as scripts, handoff instead of compaction, daily brief, watchdog)
- **Alternatives considered:** keep v1 loop; Fresh-context `claude -p` ticks (kept as option behind a shadow run)
- **Rationale:** 26 incidents, ≈ 31 h avoidable machine time
- **Consequence:** T1–T7 built 10-15; T8 10-16
- **Facts:** F-890, F-927

### D-096 · PR-1 carries the Android chat wiring as a separate, droppable commit *(internal, pending author)*

- **Date:** 2026-10-14 21:59 · **Status:** superseded — maintainer later asked for one PR, then the split was reverted
- **Context:** PR-1 (cut 7 rebased on upstream + chat wiring) engineering complete, review "mergeable as is"
- **Decision:** PR-1 carries the Android chat wiring as a separate, droppable commit
- **Alternatives considered:** engine only
- **Rationale:** the app's default chat path (legacy pipeline) scored −0.089 vs the measured engine on the same phone
- **Consequence:** maintainer later asked for one PR, then the split was reverted
- **Facts:** F-787

### D-097 · Publish research AND benchmark for other teams; publish v0.1 reference-answer text; v0.2/V-para refs stay hashes only

- **Date:** 2026-10-14 22:17 · **Status:** kept
- **Context:** Open-source intent: research AND benchmark public; v0.1 reference-answer text made public
- **Decision:** Publish research AND benchmark for other teams; publish v0.1 reference-answer text; v0.2/V-para refs stay hashes only
- **Alternatives considered:** publish hashes only
- **Rationale:** other teams cannot run the judge comparably without refs
- **Consequence:** boar-bench carries refs with provenance on the dataset card
- **Facts:** F-1310

## 2026-10-15

### D-105 · Release as two fresh repos with one squashed commit, neutral author, curated whitelist + scrub + mechanical gate + independent review; never the private history

- **Date:** 2026-10-15 · **Status:** kept
- **Context:** Public repos staged: scrub, mechanical gate, independent review (41/44 findings applied)
- **Decision:** Release as two fresh repos with one squashed commit, neutral author, curated whitelist + scrub + mechanical gate + independent review; never the private history
- **Alternatives considered:** Publish private repos
- **Rationale:** Private history holds held-out plaintext and personal data
- **Consequence:** Gate FAIL on 2 handle URLs fixed; 41/44 review findings applied; live 10:07
- **Facts:** F-1312

### D-106 · Drop the loop-operations memo and internal decision memo from the public repo; replace with a 9-line method summary

- **Date:** 2026-10-15 · **Status:** kept
- **Context:** Author: lite tier is an open, post-10-20 exploration line; starts with an unsafe-answer warning
- **Decision:** Drop the loop-operations memo and internal decision memo from the public repo; replace with a 9-line method summary
- **Alternatives considered:** Publish as is
- **Rationale:** Reviewer: internal agent prompts, caps, people and channels
- **Consequence:** `method/METHOD.md`
- **Facts:** F-930

### D-107 · Lite tier: thinking stays OFF; 1.7B Q4_K_M chosen over ternary 2B and Q8_0

- **Date:** 2026-10-15 · **Status:** kept
- **Context:** Port spec of the health path written for the native app
- **Decision:** Lite tier: thinking stays OFF; 1.7B Q4_K_M chosen over ternary 2B and Q8_0
- **Alternatives considered:** Bonsai ternary 2B/4B; Q8_0
- **Rationale:** LITE2 2B −0.057; LITE-THINK flat/negative; QUANTLITE flat and slower
- **Consequence:** Lite tier remains a product idea, not a claim
- **Facts:** F-645

### D-108 · Keep the native-app comparison internal until the final build is scored

- **Date:** 2026-10-15 · **Status:** kept
- **Context:** Closing-sprint loop on in the live session
- **Decision:** Keep the native-app comparison internal until the final build is scored
- **Alternatives considered:** publish now; publish
- **Rationale:** intermediate build, decision by the author
- **Consequence:** Number withheld from claim text
- **Facts:** F-1237, F-1263

### D-109 · Health answers never come from the model on the default tier; doses never from a model (HEALTHGAP); a fired detector can only be overridden by a deterministic c

- **Date:** 2026-10-15 · **Status:** kept
- **Context:** NUMGUARD r1→r3: lexicon guard rejected as unsafe by review; calculator-only r3 PASS
- **Decision:** Health answers never come from the model on the default tier; doses never from a model (HEALTHGAP); a fired detector can only be overridden by a deterministic calculator (NUMGUARD r3)
- **Alternatives considered:** model with a disclaimer
- **Rationale:** safety; model answered doses from memory on probes
- **Verification note:** citation fix: 'never reach the 4B' is l.21. AI-reviewed, not clinically reviewed
- **Facts:** F-374

### D-100 · First public push by the coordinator, only for the two new repos, on the author's explicit instruction

- **Date:** 2026-10-15 10:07 · **Status:** kept
- **Context:** Public repos live (first push by the coordinator, explicitly authorised for those two repos only)
- **Decision:** First public push by the coordinator, only for the two new repos, on the author's explicit instruction
- **Alternatives considered:** keep private
- **Rationale:** release
- **Consequence:** repos live; no-push rule stays for everything else
- **Facts:** F-936

### D-101 · Accept the maintainer's native Kotlin app as the official submission; our numbers are labelled as the TypeScript engine's

- **Date:** 2026-10-15 11:00 · **Status:** superseded by D-183 — On 2026-10-24 the author made BoarLite, a new closed app of his own, the bounty submission.
- **Context:** Submission vehicle = maintainer's native Kotlin app; PR #85 (cut 7 engine as reference) open
- **Decision:** Accept the maintainer's native Kotlin app as the official submission; our numbers are labelled as the TypeScript engine's
- **Alternatives considered:** submit the RN app with PR #85; the React Native app carrying cut 7 via PR
- **Rationale:** the maintainer owns the submission
- **Consequence:** claim v4.1 vehicle paragraph; native score pending
- **Superseded by:** D-183
- **Facts:** F-1238, F-788

### D-102 · Recommend porting order: FACTS + first-aid cards first, then calculator, then grounding rules *(internal, pending author)*

- **Date:** 2026-10-15 15:17 · **Status:** kept
- **Context:** Independent reviewer REJECTs a numeric guard as unsafe; scope cut to calculator-only
- **Decision:** Recommend porting order: FACTS + first-aid cards first, then calculator, then grounding rules
- **Alternatives considered:** health path first (first, uncorrected breakdown); port everything at once
- **Rationale:** per-mechanism share of the −0.089 gap (cards ≈ 27 % + 29 %, calculator ≈ 22 %, grounding ≈ 30 %)
- **Consequence:** correction posted on PR
- **Facts:** F-1262, F-379

### D-103 · Reject the lexicon numeric guard; ship calculator-only NUMGUARD r3

- **Date:** 2026-10-15 21:34 · **Status:** kept
- **Context:** Independent reviewer REJECTs a numeric guard as unsafe; scope cut to calculator-only
- **Decision:** Reject the lexicon numeric guard; ship calculator-only NUMGUARD r3
- **Alternatives considered:** NUMGUARD-FINAL lexicon guard
- **Rationale:** confirmation review: a lexicon guard cannot be made safe (numeric health questions leak)
- **Consequence:** r3 pushed to PR #85
- **Facts:** F-1275

### D-104 · Lite tier is post-10-20 work, explored with quick diagnostic tests; starts with an unsafe-answer warning

- **Date:** 2026-10-15 22:21 · **Status:** superseded by D-134 — On 2026-10-20 the small model became the main 8 GB engine, not a post-deadline lite line.
- **Context:** Author: lite tier is an open, post-10-20 exploration line; starts with an unsafe-answer warning
- **Decision:** Lite tier is post-10-20 work, explored with quick diagnostic tests; starts with an unsafe-answer warning
- **Alternatives considered:** drop lite tier
- **Rationale:** 2B −0.168 and 6/15 unsafe health answers; weaker phones matter
- **Consequence:** LITE2–LITE8, LITEREADERS etc. 10-15/16; closed for now
- **Superseded by:** D-134
- **Facts:** F-790

## 2026-10-16

### D-112 · deps.warn (unsafe-answer warning) stays off by default

- **Date:** 2026-10-16 · **Status:** kept
- **Decision:** deps.warn (unsafe-answer warning) stays off by default
- **Alternatives considered:** default-on
- **Rationale:** out-of-sample recall 3/8 (lexicon) and 12/18 with FP 8/92 (detector)
- **Consequence:** not handed to the PR
- **Facts:** F-389

### D-115 · Claude judge stays the headline (lower of two judges); judge family named next to every ratio; win/tie/loss leads

- **Date:** 2026-10-16 · **Status:** kept
- **Context:** Claim v4.2 / v4.2.1: judge family named on every ratio; native comparison kept internal
- **Decision:** Claude judge stays the headline (lower of two judges); judge family named next to every ratio; win/tie/loss leads
- **Alternatives considered:** headline the higher cross-family number; Report the higher judge; lead with OpenAI-judge numbers (deep crosses 0.50)
- **Rationale:** analysis-plan rule: when judges differ by > 0.05, the lower is the headline
- **Consequence:** claim v4.2.x
- **Facts:** F-1189, F-1239, F-1240

### D-116 · Apply 7 re-wordings from the adversarial critique (retract "gap is reach, not reading", etc.)

- **Date:** 2026-10-16 · **Status:** kept
- **Context:** Independent adversarial CRITIQUE: 7 re-wordings applied
- **Decision:** Apply 7 re-wordings from the adversarial critique (retract "gap is reach, not reading", etc.)
- **Alternatives considered:** Defend summaries
- **Rationale:** Numbers real, summaries scope-stripped
- **Consequence:** Corrections logged as QUEUE rows
- **Facts:** F-1188

### D-117 · NUMGUARD lexicon guard rejected as unsafe; calculator-only r3 kept

- **Date:** 2026-10-16 · **Status:** kept
- **Context:** NUMGUARD r3 + HEALTHGAP r2 added to the upstream PR; WARN banner spec v2
- **Decision:** NUMGUARD lexicon guard rejected as unsafe; calculator-only r3 kept
- **Alternatives considered:** ship the lexicon guard (passed tuned gates)
- **Rationale:** a lexicon that lets the model answer a detector-fired health turn cannot be made safe
- **Consequence:** r3 shipped to PR #85
- **Facts:** F-1278

### D-118 · Lite tier proposed for 4–6 GB phones: Qwen3-1.7B behind the full safety engine

- **Date:** 2026-10-16 · **Status:** superseded by D-134 — On 2026-10-20 Qwen3-1.7B became the main 8 GB engine; the 4B became the optional tier.
- **Context:** Lite tier (Qwen3-1.7B) evaluated; LITESAFETY PASS; critique corrects "1.7B = 4B"
- **Decision:** Lite tier proposed for 4–6 GB phones: Qwen3-1.7B behind the full safety engine
- **Alternatives considered:** Gemma-3-1B, LFM2-1.2B (worse readers), Q8 quant (flat)
- **Rationale:** 1.1 GB file, RSS ≈ 2.3 GB; safety routing identical to 4B
- **Consequence:** offered as option; quality wording corrected after critique
- **Superseded by:** D-134
- **Facts:** F-1190

### D-119 · Expert streaming (LES fork) supersedes earlier loader/kernel candidates on paper for a deep-tier device plan

- **Date:** 2026-10-16 · **Status:** kept
- **Context:** LESPORT: expert-streaming fork runs the 35B in 2.8 GiB RSS on desktop CPU, judged parity TRANSFER
- **Decision:** Expert streaming (LES fork) supersedes earlier loader/kernel candidates on paper for a deep-tier device plan
- **Alternatives considered:** bmoe (7.9 GB on phone)
- **Rationale:** 2.8 GiB RSS, judged parity
- **Consequence:** phone flash speed unmeasured; Android buffer unbuilt
- **Facts:** F-792

### D-110 · TK2-FIX is a correctness fix, not a score lever; out of PR #85 before 10-20

- **Date:** 2026-10-16 03:39 · **Status:** kept
- **Context:** Critique raises the one-seed noise rule from 0.03 to ≥ 0.05
- **Decision:** TK2-FIX is a correctness fix, not a score lever; out of PR #85 before 10-20
- **Alternatives considered:** include in PR
- **Rationale:** +0.010 pooled, needs a builder change too
- **Consequence:** queued as a post-10-20 patch
- **Facts:** F-1284

### D-111 · Idle-lane rule: a blocked lane is one log row; every other lane filled at once; refined 21:5x to "arms only for new questions with ceiling ≥ MDE, quiet ticks ot

- **Date:** 2026-10-16 09:4x · **Status:** kept
- **Context:** Judge authentication expired; no judge passes for ≈ 2.5 h; lanes idle ≈ 5 h (coordinator fault acknowledged)
- **Decision:** Idle-lane rule: a blocked lane is one log row; every other lane filled at once; refined 21:5x to "arms only for new questions with ceiling ≥ MDE, quiet ticks otherwise"
- **Alternatives considered:** idle waiting
- **Rationale:** ≈ 5 h of idle lanes on 10-16
- **Consequence:** settled the critique's point on 3-minute filler probes
- **Facts:** F-1199

### D-113 · Apply the adversarial critique: lite "= 4B" only on pack-matched dev; one-seed V-para noise rule 0.03 → 0.05; n≈20 closures relabelled "not detected at MDE 0.08

- **Date:** 2026-10-16 18:28 · **Status:** kept
- **Context:** Adversarial critique: lite "= 4B" overstated (kit −0.111), lite gap is reading too (−0.070 at identical contexts); closed loop risk
- **Decision:** Apply the adversarial critique: lite "= 4B" only on pack-matched dev; one-seed V-para noise rule 0.03 → 0.05; n≈20 closures relabelled "not detected at MDE 0.08"
- **Alternatives considered:** keep wording
- **Rationale:** over-stated internal summaries
- **Consequence:** 7 re-wordings applied
- **Facts:** F-1201

### D-114 · The native-app −0.089 stays internal until the final build is scored; publishing = claim text + research page, not a PR *(internal, pending author)*

- **Date:** 2026-10-16 21:5x · **Status:** kept
- **Context:** Adversarial critique: lite "= 4B" overstated (kit −0.111), lite gap is reading too (−0.070 at identical contexts); closed loop risk
- **Decision:** The native-app −0.089 stays internal until the final build is scored; publishing = claim text + research page, not a PR
- **Alternatives considered:** publish the comparison
- **Rationale:** an old dev build is not the release
- **Consequence:** claim says "scored internally, number held"
- **Facts:** F-1242

## 2026-10-17

### D-122 · When judges from two families disagree, the lower number is the headline; judge family named next to every ratio

- **Date:** 2026-10-17 · **Status:** kept
- **Context:** Claim v4.2.3: "the lower judge is the headline"; judge family named next to every ratio
- **Decision:** When judges from two families disagree, the lower number is the headline; judge family named next to every ratio
- **Alternatives considered:** lead with the cross-family number
- **Rationale:** XFAM offset ≈ +0.10
- **Consequence:** claim v4.2.3
- **Facts:** F-1243

### D-120 · Claim v4.2.4: state that the submitted app ports retrieval and prompts, not the health path or deterministic answers

- **Date:** 2026-10-17 20:59 · **Status:** kept
- **Context:** Claim v4.2.3 / v4.2.4: wording as of 2026-10-17 (the posted claim follows the standing at closure); submitted app ports retrieval and prompts, not the health path or deterministic answers
- **Decision:** Claim v4.2.4: state that the submitted app ports retrieval and prompts, not the health path or deterministic answers
- **Alternatives considered:** keep the earlier sentence; earlier wording "port of the rules"
- [private correspondence with the app maintainer, or a result of a run on his device, removed]
- **Consequence:** claim wording as of 2026-10-17; the claim text stays open until closure (open front OF-5)
- **Facts:** F-1244, F-1292

### D-121 · Advise the maintainer against "Detailed" as default answer style; offer to test his honesty prompt *(internal, pending author)*

- **Date:** 2026-10-17 21:10 · **Status:** kept
- **Context:** DETAILED-HALLU: 40/198 atomic claims wrong in 15 "Detailed" answers
- **Decision:** Advise the maintainer against "Detailed" as default answer style; offer to test his honesty prompt
- **Alternatives considered:** lock Detailed
- **Rationale:** Detailed −0.191 vs Succinct; 40/198 claims wrong
- **Consequence:** HONESTPROMPT launched 23:07
- **Facts:** F-1294

## 2026-10-18

### D-126 · Never ship a capability sentence without health forced to guard texts

- **Date:** 2026-10-18 · **Status:** kept
- **Context:** decided by: coordinator
- **Decision:** Never ship a capability sentence without health forced to guard texts
- **Alternatives considered:** ship L1
- **Rationale:** L1 line added wrong first-aid steps on first-aid chats
- **Consequence:** rule standing
- **Facts:** F-1378

### D-125 · Recommend the honest Detailed prompt D1, then D4 (D1 + capability rule) as the Detailed prompt; no Succinct-honest

- **Date:** 2026-10-18 05:02 · **Status:** kept
- **Context:** decided by: coordinator under frozen rule
- **Decision:** Recommend the honest Detailed prompt D1, then D4 (D1 + capability rule) as the Detailed prompt; no Succinct-honest
- **Alternatives considered:** D2, S1, S3
- **Rationale:** wrong claims down, ratio within -0.03 rule, refusals 1-2/49; S1 refuses 7/49
- **Consequence:** sent to maintainer via liaison
- **Facts:** F-1377, F-1832

### D-123 · D1: no LFM2.5 desktop replay

- **Date:** 2026-10-18 16:07 · **Status:** kept
- **Context:** decided by: delegated coordinator (author delegated)
- **Decision:** D1: no LFM2.5 desktop replay
- **Alternatives considered:** run replay ~1.5 h
- **Rationale:** audit already 7/58 vs 3/73 wrong; product already chose Qwen
- **Consequence:** closed
- **Verification note:** Verification note: The parenthetical wording ('scored internally, final build published when it ships') is the claim text's, sourced at not . who decided: delegated coordinator; why: ~14-24 h of author item writing; would land after the deadline; bar needs ~0.53 at n 110 vs best ~0.43-0.51; serves honesty, not winning; alternatives: 60-item wave 1; 6-item pilot; reversible: yes | VERIFIER NOTE: Base OF-3 says 'the author decided'; precise form: the author delegated D1-D7 and the coordinator's recommendation (skip v0.3) was adopted ( l.4).
- **Facts:** F-1370, F-1371, F-1372, F-1373, F-1374, F-1375, F-1833

### D-124 · D7: upload the research site only as v1.0 at closure; v0.x are internal build states

- **Date:** 2026-10-18 16:07 · **Status:** kept
- **Context:** decided by: delegated coordinator
- **Decision:** D7: upload the research site only as v1.0 at closure; v0.x are internal build states
- **Alternatives considered:** upload v0.1 now
- **Rationale:** one publication, no intermediate states
- **Consequence:** folded into publication PLAN
- **Facts:** F-1376

## 2026-10-19

### D-127 · Focus finishing work on "tests with sources" (user has the matching pack)

- **Date:** 2026-10-19 13:30 · **Status:** kept
- **Context:** decided by: author
- **Decision:** Focus finishing work on "tests with sources" (user has the matching pack)
- **Alternatives considered:** continue no-source prompt tests (PROMPT3M)
- **Rationale:** bounty finish
- **Consequence:** PACKREAD run; PROMPT3M paused, later closed
- **Facts:** F-1379

### D-128 · Release saferoute patch despite SAFEPACK frozen-rule FAIL (app ships with a warning); FAIL kept on record

- **Date:** 2026-10-19 14:27 · **Status:** reversed — Reversed the same day: the saferoute patch was held out of the pushed stack after the independent direction review.
- **Context:** decided by: author
- **Decision:** Release saferoute patch despite SAFEPACK frozen-rule FAIL (app ships with a warning); FAIL kept on record
- **Alternatives considered:** hold patch
- **Rationale:** rule judged too strict for stage
- **Consequence:** reversed same day: held out of the pushed stack after the direction review
- **Facts:** F-1380, F-1834

### D-130 · Resume three safety-held items: per-answer health caution ON, drinking-water card, chat routing L2+L3 without L1

- **Date:** 2026-10-19 14:36 · **Status:** kept
- **Context:** decided by: author
- **Decision:** Resume three safety-held items: per-answer health caution ON, drinking-water card, chat routing L2+L3 without L1
- **Alternatives considered:** keep held
- **Rationale:** app ships with a warning; harm came from L1 line only
- **Consequence:** in the pushed PR stack
- **Facts:** F-1382

### D-129 · Stop opening new arms; consolidate; hold saferoute; correct over-reads (SMALLCLS, SAFEPACK)

- **Date:** 2026-10-19 15:19 · **Status:** kept
- **Context:** decided by: independent reviewer, adopted by coordinator
- **Decision:** Stop opening new arms; consolidate; hold saferoute; correct over-reads (SMALLCLS, SAFEPACK)
- **Alternatives considered:** open SMALLCLS-2; agentic search loop
- **Rationale:** scope drift two days before closure; small-n in-sample results drove release calls
- **Consequence:** adopted for saferoute; new arms nonetheless resumed 10-20 under new program
- **Facts:** F-1381

### D-184 · Consolidate, no new arms; hazard routes show title + pointer instead of a verbatim passage

- **Date:** 2026-10-19 15:19 · **Status:** kept
- **Context:** decided by: reviewer (independent Opus)
- **Decision:** Consolidate, no new arms; hazard routes show title + pointer instead of a verbatim passage
- **Alternatives considered:** SMALLCLS-2; agentic loop
- **Rationale:** saferoute quotes the wrong section of the right page
- **Consequence:** adopted for 10-19 evening
- **Facts:** F-1835

### D-131 · Build a public ruler: true-zero utility U + task success, uncapped two-family web references, non-Claude items, submitted app on phone, gates, speed, install

- **Date:** 2026-10-19 23:08 · **Status:** kept
- **Context:** decided by: coordinator from 8-agent workflow (both critics converged)
- **Decision:** Build a public ruler: true-zero utility U + task success, uncapped two-family web references, non-Claude items, submitted app on phone, gates, speed, install
- **Alternatives considered:** keep old bench as headline
- **Rationale:** five misreadings of the bounty in the old bench
- **Consequence:** led to v0.4 items + spec v1
- **Facts:** F-1383, F-1836

## 2026-10-20

### D-132 · Item families from Vitalik Buterin's own public test questions; travel ~1/3 not >= 50 %; 8 multi-turn; over-refusal probes; venue "best" checked on open web

- **Date:** 2026-10-20 · **Status:** kept
- **Context:** decided by: coordinator, author direction
- **Decision:** Item families from Vitalik Buterin's own public test questions; travel ~1/3 not >= 50 %; 8 multi-turn; over-refusal probes; venue "best" checked on open web
- **Alternatives considered:** r1 quotas (72 items, >= 50 % travel)
- **Rationale:** match the inspiring post's queries
- **Consequence:** applied to v0.4
- **Facts:** F-1384

### D-166 · Standing author policy on submitted-app numbers in group A's range *(internal, pending author)*

- **Date:** 2026-10-20 · **Status:** kept
- **Decision:** Standing author policy on submitted-app numbers in group A's range
- [private correspondence with the app maintainer, or a result of a run on his device, removed]
- **Facts:** F-1638

### D-134 · Qwen3-1.7B = main 8 GB engine; 4B = optional "more complete" tier

- **Date:** 2026-10-20 11:50 · **Status:** kept
- **Context:** decided by: author
- **Decision:** Qwen3-1.7B = main 8 GB engine; 4B = optional "more complete" tier
- **Alternatives considered:** keep 4B default; Qwen2.5-1.5B (faster but weaker)
- **Rationale:** Pixel 8a: 1.7B 13-16 tok/s, answers 13-16 s; 4B 3.6-6 tok/s, 29-46 s, one LMK kill
- **Consequence:** adopted; confirmed at 19:07 grill
- **Facts:** F-1386, F-1837

### D-133 · Resolve 5 disputed points; drop one item contradicted by both families; tag 4 V-exact anchors out of the headline; freeze v0.4

- **Date:** 2026-10-20 16:45 · **Status:** kept
- **Context:** decided by: author
- **Decision:** Resolve 5 disputed points; drop one item contradicted by both families; tag 4 V-exact anchors out of the headline; freeze v0.4
- **Alternatives considered:** keep disputed items
- **Rationale:** both-family fact check
- **Consequence:** frozen, sha f9ad2f2f...
- **Facts:** F-1385, F-1838

### D-135 · Propose to maintainer: 8 GB = Qwen3-1.7B + fixed warning line instead of compact declines

- **Date:** 2026-10-20 17:35 · **Status:** superseded by D-149 — superseded at 20:24 by refuse-by-default
- **Context:** decided by: author (send OK)
- **Decision:** Propose to maintainer: 8 GB = Qwen3-1.7B + fixed warning line instead of compact declines
- **Alternatives considered:** keep declines
- **Rationale:** CMP30OFF: 1.7B with declines released leads 1.5B
- **Consequence:** superseded at 20:24 by refuse-by-default
- **Superseded by:** D-149
- **Facts:** F-1387

### D-136 · Grill Q1-Q13: three fronts; every arm a two-stage screen (problems + sentinels, then full MAIN 97); safety-cards-first archived; engine changes sent only after 

- **Date:** 2026-10-20 19:07 · **Status:** kept
- **Context:** decided by: author
- **Decision:** Grill Q1-Q13: three fronts; every arm a two-stage screen (problems + sentinels, then full MAIN 97); safety-cards-first archived; engine changes sent only after a measured gain; Vitalik Buterin-blog pack built user-selected, unmeasured
- **Alternatives considered:** phone A/B of 4B; C before bounty
- **Rationale:** LITEPACKS NO CHANGE
- **Consequence:** adopted
- **Facts:** F-1388

### D-137 · Ruler headline weights the 11 health_safety items at 0.5, adds a safety gate, publishes weight-1 U beside it

- **Date:** 2026-10-20 19:07 · **Status:** kept
- **Context:** decided by: author
- **Decision:** Ruler headline weights the 11 health_safety items at 0.5, adds a safety gate, publishes weight-1 U beside it
- **Alternatives considered:** weight 1
- **Rationale:** bounty asks for casual lookup/research, never names health
- **Consequence:** in spec v1 §2; reviewer F3 flags timing (decided after items existed)
- **Facts:** F-1389

### D-185 · Two-stage screens (problem screen + sentinels, then MAIN 97); health items weigh 0.5 in headline

- **Date:** 2026-10-20 19:07 · **Status:** kept
- **Context:** decided by: author (grill)
- **Decision:** Two-stage screens (problem screen + sentinels, then MAIN 97); health items weigh 0.5 in headline
- **Alternatives considered:** single-stage runs
- **Rationale:** cheap screening, explicit safety weighting
- **Consequence:** GATE v2 replaced the bar at 22:29
- **Facts:** F-1839

### D-138 · Ruler headline = coverage x U decomposition + U-total; product refuses by default when no source is kept, with a "show anyway" control

- **Date:** 2026-10-20 20:24 · **Status:** kept
- **Context:** decided by: author
- **Decision:** Ruler headline = coverage x U decomposition + U-total; product refuses by default when no source is kept, with a "show anyway" control
- **Alternatives considered:** answer under a warning line
- **Rationale:** separate what packs answer from memory answers
- **Consequence:** spec v1 r2
- **Facts:** F-1390, F-1840

### D-139 · Verdict arm = A∪ (all persona packs installed once, same for every item); per-family arm A kept as a labelled row

- **Date:** 2026-10-20 20:39 · **Status:** kept
- **Context:** decided by: author on reviewer finding F1
- **Decision:** Verdict arm = A∪ (all persona packs installed once, same for every item); per-family arm A kept as a labelled row
- **Alternatives considered:** arm A or arm B as verdict
- **Rationale:** per-family arm = oracle topic routing
- **Consequence:** spec v1 r2
- **Verification note:** Verification note: Reviewer finding F1 is at (TL;DR 1) and :14 (F1 heading); line 7 is the decline-arm finding.
- **Facts:** F-1391

### D-140 · Persona map v1: travel -> wikivoyage + visa (+ area tile); tech -> crypto; science -> medlineplus + firstaid; place -> factbook; humanities -> none; NIST pack e

- **Date:** 2026-10-20 21:45 · **Status:** kept
- **Context:** decided by: coordinator draft + independent approver (6 edits)
- **Decision:** Persona map v1: travel -> wikivoyage + visa (+ area tile); tech -> crypto; science -> medlineplus + firstaid; place -> factbook; humanities -> none; NIST pack excluded
- **Alternatives considered:** include NIST, simplewiki
- **Rationale:** chosen from pack-card domain lines only
- **Consequence:** not frozen, waits author veto
- **Facts:** F-1392, F-1841

### D-141 · GATE v2: screen bar = max measured null net + 2

- **Date:** 2026-10-20 22:29 · **Status:** kept
- **Context:** decided by: coordinator
- **Decision:** GATE v2: screen bar = max measured null net + 2
- **Alternatives considered:** fixed bar 6
- **Rationale:** null runs fixed 23-31 % of problems; old 6-fix bar sat at the null
- **Consequence:** used for overnight screens
- **Facts:** F-1393

### D-186 · Keep Q4_K_M quantisation for the 1.7B

- **Date:** 2026-10-20 23:59 · **Status:** kept
- **Context:** decided by: delegated coordinator (frozen rule)
- **Decision:** Keep Q4_K_M quantisation for the 1.7B
- **Alternatives considered:** Q8_0
- **Rationale:** Q8_0 inside null band, decode x0.66, +0.7 GB
- **Consequence:** Q4 stays
- **Facts:** F-1842

## 2026-10-21

### D-142 · Qwen3-1.7B stays the 8 GB recommendation "on a latency and memory constraint, not on quality"; model swaps below 4B parked until 10-31

- **Date:** 2026-10-21 · **Status:** kept
- **Context:** decided by: delegated coordinator (proposal, reviewed)
- **Decision:** Qwen3-1.7B stays the 8 GB recommendation "on a latency and memory constraint, not on quality"; model swaps below 4B parked until 10-31
- **Alternatives considered:** Gemma default; 4B default
- **Rationale:** Gemma +0.029 at 1.5× time +1.4 GB; Ministral +0.062 at ~3× time; 4B +0.076 at ~2.5× time
- **Consequence:** stood; superseded in practice by RC1 shipping 1.5B
- **Facts:** F-1527

### D-143 · Gemma 4 E2B only as opt-in catalog entry with thinking guards (thinking off, budget 0, n_predict cap, post-filter); exact file pinned

- **Date:** 2026-10-21 02:38 · **Status:** kept
- **Context:** decided by: delegated coordinator
- **Decision:** Gemma 4 E2B only as opt-in catalog entry with thinking guards (thinking off, budget 0, n_predict cap, post-filter); exact file pinned
- **Alternatives considered:** Gemma default; drop Gemma
- **Rationale:** phone quality = 1.7B, 1.5-2.8× time, +1.1-1.4 GB; runtime risks (thinking default on, KV growth)
- **Consequence:** proposal; Gemma not in RC1 catalog so moot on RC1
- **Facts:** F-1528

### D-187 · 1.7B stays the 8 GB recommendation on latency and memory, not quality; model screens parked

- **Date:** 2026-10-21 03:06 · **Status:** kept
- **Context:** decided by: reviewer (9-agent direction review)
- **Decision:** 1.7B stays the 8 GB recommendation on latency and memory, not quality; model screens parked
- **Alternatives considered:** Gemma opt-in tier
- **Rationale:** MIN3CITE/Gemma gains cost 2.8-3x phone time
- **Consequence:** no Gemma/Ministral send
- **Facts:** F-1843

### D-188 · Fallback judge: judge.v1 + decline subtraction D 0.058 (true-zero variants NO-ADOPT)

- **Date:** 2026-10-21 04:57 · **Status:** superseded by D-144 — superseded by RULING R1 12:45
- **Context:** decided by: delegated coordinator (frozen kill clauses)
- **Decision:** Fallback judge: judge.v1 + decline subtraction D 0.058 (true-zero variants NO-ADOPT)
- **Alternatives considered:** v1.1; U from completeness+usefulness
- **Rationale:** v1.1/v1.1b flip CEs and raise retest SD
- **Consequence:** superseded by RULING R1 12:45
- **Superseded by:** D-144
- **Facts:** F-1844

### D-195 · No public upload of v0.4 items or references; labels of FACT-AVAIL quarantined (coordinator-only) until the result card

- **Date:** 2026-10-21 05:30 · **Status:** kept
- **Context:** decided by: delegated coordinator + spec reviewer
- **Decision:** No public upload of v0.4 items or references; labels of FACT-AVAIL quarantined (coordinator-only) until the result card
- **Alternatives considered:** publish kit early
- **Rationale:** held-out discipline
- **Consequence:** quarantine in spec §2.4
- **Facts:** F-1865

### D-144 · RULING R1: judge = judge.v1 unchanged + DECLINE2STAGE zero per detected non-answer; D 0.058 kept as sensitivity row

- **Date:** 2026-10-21 12:45 · **Status:** kept
- **Context:** decided by: delegated coordinator (override of a frozen FAIL, accepted with conditions by reviewer)
- **Decision:** RULING R1: judge = judge.v1 unchanged + DECLINE2STAGE zero per detected non-answer; D 0.058 kept as sensitivity row
- **Alternatives considered:** judge v1.1; decline subtraction only
- **Rationale:** judge v1.1/v1.1b changed CE verdicts (5-7/40 flips); DECLINE2STAGE's 2 bar-(b) hits were engine refusal strings
- **Consequence:** adopted into ruler r3/r4
- **Facts:** F-1529, F-1845

### D-189 · Close MIN3CITE (Ministral + citation prompt) as dominated by the 4B; do not send

- **Date:** 2026-10-21 12:45 · **Status:** kept
- **Context:** decided by: delegated coordinator (revisit kill clauses)
- **Decision:** Close MIN3CITE (Ministral + citation prompt) as dominated by the 4B; do not send
- **Alternatives considered:** Ministral opt-in
- **Rationale:** Opus +0.047 but −0.037 vs 4B, ~3x time
- **Consequence:** closed
- **Facts:** F-1846

### D-145 · GOAL: two numbers U_8GB (+0.03 Opus, CE-shown must not rise) and T_8GB (7.6 → 5.0 s)

- **Date:** 2026-10-21 13:12 · **Status:** kept
- **Context:** decided by: author
- **Decision:** GOAL: two numbers U_8GB (+0.03 Opus, CE-shown must not rise) and T_8GB (7.6 → 5.0 s)
- **Alternatives considered:** open exploration
- **Rationale:** focus the last days on measurable engine gains
- **Consequence:** T_8GB re-based to the native app same day; U_8GB lines closed at nulls
- **Facts:** F-1530

### D-146 · Winning thesis = honest 8 GB product + open ruler

- **Date:** 2026-10-21 13:13 · **Status:** kept
- **Context:** decided by: author (GRILL)
- **Decision:** Winning thesis = honest 8 GB product + open ruler
- **Alternatives considered:** compete on the deep tier
- **Rationale:** 35B not deliverable on 8 GB in time
- **Consequence:** stood until 10-22 pivot reframed it
- **Facts:** F-1531

### D-147 · 35B deep mode not delivered; deep tier appears only as roadmap with desktop numbers

- **Date:** 2026-10-21 13:13 · **Status:** kept
- **Context:** decided by: author (GRILL)
- **Decision:** 35B deep mode not delivered; deep tier appears only as roadmap with desktop numbers
- **Alternatives considered:** 12 GB deep tier
- **Rationale:** focus on 8 GB UX; no Android expert-streaming build
- **Consequence:** stood
- **Facts:** F-1532

### D-148 · 8 GB default model: Qwen3-1.7B, 4B optional (sent to maintainer only within the short package)

- **Date:** 2026-10-21 13:13 · **Status:** kept
- **Context:** decided by: author. Same set and phone: 1.7B p50 4.2 s vs 4B p50 25.5 s over all 73 v0.1 items (all-items p50, including deterministic and declined items).
- **Decision:** 8 GB default model: Qwen3-1.7B, 4B optional (sent to maintainer only within the short package)
- **Verification note:** Verification note: Faithful to GRILL D3 but compares a 73-question all-items p50 for the 1.7B (4.2 s) with 9-question model-path answer ranges for the 4B (29-46 s). Same 73 set, same phone: 1.7B p50 4.2 s vs 4B p50 25.5 s (cut 7, 10-20).
- **Facts:** F-1533

### D-149 · No source found → refuse by default + "show anyway", shown answers carry a warning line

- **Date:** 2026-10-21 13:13 · **Status:** kept
- **Context:** decided by: author (GRILL)
- **Decision:** No source found → refuse by default + "show anyway", shown answers carry a warning line
- **Alternatives considered:** always answer
- **Rationale:** honesty on 8 GB
- **Consequence:** later narrowed: show-anyway only behind second confirmation, never on health (REVEAL-CENSUS); RC1 has no warning line
- **Facts:** F-1534, F-1551

### D-150 · Article = research site on a project subdomain built from the public research repo; story = timeline of decisions, not a score line

- **Date:** 2026-10-21 13:13 · **Status:** kept
- **Context:** decided by: author (GRILL)
- **Decision:** Article = research site on a project subdomain built from the public research repo; story = timeline of decisions, not a score line
- **Alternatives considered:** pages on existing site
- **Rationale:** full control of look; avoid cross-set score charts
- **Consequence:** stands (this publication)
- **Facts:** F-1535

### D-151 · Final score = submitted native APK on Pixel 8a, v0.4 frozen (75 items), Claude + OpenAI gpt-5.6-sol judges, frontier + web references

- **Date:** 2026-10-21 13:13 · **Status:** kept
- **Context:** decided by: author (GRILL)
- **Decision:** Final score = submitted native APK on Pixel 8a, v0.4 frozen (75 items), Claude + OpenAI gpt-5.6-sol judges, frontier + web references
- **Alternatives considered:** engine-only score
- **Rationale:** the bounty judges the app
- **Consequence:** ruler r3/r4 built for it; run pending a new RC
- **Facts:** F-1536

### D-191 · Honest 8 GB UX; no 35B deep mode delivered; final score = submitted native APK on Pixel 8a with v0.4, Claude + OpenAI gpt-5.6-sol judges

- **Date:** 2026-10-21 13:13 · **Status:** kept
- **Context:** decided by: author (grill D1-D10)
- **Decision:** Honest 8 GB UX; no 35B deep mode delivered; final score = submitted native APK on Pixel 8a with v0.4, Claude + OpenAI gpt-5.6-sol judges
- **Alternatives considered:** deliver deep mode
- **Rationale:** deep tier needs 12 GB and integration work
- **Consequence:** deep tier appears only as roadmap
- **Facts:** F-1848

### D-190 · X2b head pass stays on (off is safe only at the edge, for kit-only installs)

- **Date:** 2026-10-21 13:18 · **Status:** kept
- **Context:** decided by: delegated coordinator (frozen rule)
- **Decision:** X2b head pass stays on (off is safe only at the edge, for kit-only installs)
- **Alternatives considered:** turn X2b off
- **Rationale:** CE-unwarned clause fails by 1 item
- **Consequence:** kept on
- **Facts:** F-1847

### D-192 · Keep all six A∪ packs installed by default (visa, medlineplus not pruned)

- **Date:** 2026-10-21 14:16 · **Status:** kept
- **Context:** decided by: delegated coordinator (frozen clause) + product call left to author
- **Decision:** Keep all six A∪ packs installed by default (visa, medlineplus not pruned)
- **Alternatives considered:** prune visa/medlineplus
- **Rationale:** each pack reaches kept context on dev items
- **Consequence:** kept
- **Facts:** F-1849

### D-152 · Submission = the maintainer's native Kotlin app, not the RN bench engine

- **Date:** 2026-10-21 15:5x · **Status:** superseded by D-183 — re-based speed lines (bench levers page-only) and claim section 0
- **Context:** decided by: author
- **Decision:** Submission = the maintainer's native Kotlin app, not the RN bench engine
- **Alternatives considered:** engine-only claim
- **Rationale:** that is what will be submitted
- **Consequence:** re-based speed lines (bench levers page-only) and claim section 0
- **Superseded by:** D-183
- **Facts:** F-1537

### D-153 · No 512-token cap ask (CAP512 not a lever)

- **Date:** 2026-10-21 16:01 · **Status:** kept
- **Context:** decided by: delegated coordinator (frozen rule)
- **Decision:** No 512-token cap ask (CAP512 not a lever)
- **Alternatives considered:** cap ask in NOTE-1
- **Rationale:** saves 0 s p50, cuts 10.9 % mid-sentence
- **Consequence:** dropped
- **Facts:** F-1538

### D-155 · Section 0 of the page = two labelled claims (E engine, S submitted app with its own number); withholding the app's absolute rejected *(internal, pending author)*

- **Date:** 2026-10-21 19:01 · **Status:** kept
- **Context:** decided by: reviewer (independent Opus + 3 cold readers), final word author
- **Decision:** Section 0 of the page = two labelled claims (E engine, S submitted app with its own number); withholding the app's absolute rejected
- **Alternatives considered:** omit app number
- **Rationale:** LA5 withholding is a material omission (0.35 − 0.21 recovers 0.14)
- **Consequence:** recommended base; publication pending author decision 4
- **Facts:** F-1540, F-1850

### D-154 · Maintainer-ask order: Succinct default first, 1.7B entry second, facts-table port, warning line, pack catalog entries *(internal, pending author)*

- **Date:** 2026-10-21 19:17 · **Status:** kept
- **Context:** decided by: delegated coordinator (notes drafted
- **Decision:** Maintainer-ask order: Succinct default first, 1.7B entry second, facts-table port, warning line, pack catalog entries
- **Alternatives considered:** 1.7B first (earlier plan)
- **Rationale:** C2 +0.115 Succinct vs B2 +0.010 model swap
- **Consequence:** drafted, not sent in slice
- **Facts:** F-1539

### D-193 · Adopt --no-repack as cross-host pairing flag for text pairing only; claim numbers keep default

- **Date:** 2026-10-21 19:28 · **Status:** kept
- **Context:** decided by: delegated coordinator (frozen rule)
- **Decision:** Adopt --no-repack as cross-host pairing flag for text pairing only; claim numbers keep default
- **Alternatives considered:** per-host pairing only
- **Rationale:** 97/97 identical across hosts, quality-neutral (−0.012)
- **Consequence:** adopted for pairing
- **Facts:** F-1851

### D-156 · Verdict arm = app with packs (A-union); OpenAI gpt-5.6-sol as second judge family; headline waits for new RC; ruler in its own session

- **Date:** 2026-10-21 20:28 · **Status:** kept
- **Context:** decided by: author
- **Decision:** Verdict arm = app with packs (A-union); OpenAI gpt-5.6-sol as second judge family; headline waits for new RC; ruler in its own session
- **Alternatives considered:** verdict on app without packs
- **Rationale:** thesis "app + packs answers well"; two families
- **Consequence:** in r3/r4
- **Facts:** F-1541, F-1852

### D-157 · Freeze RULER-SPEC v1 r3 (private)

- **Date:** 2026-10-21 20:48 · **Status:** kept
- **Context:** decided by: delegated coordinator + reviewer ACCEPT WITH EDITS
- **Decision:** Freeze RULER-SPEC v1 r3 (private)
- **Alternatives considered:** keep binary checklist judge (NO-GO earlier)
- **Rationale:** pre-registration before any v0.4 answer
- **Consequence:** frozen sha 0fac2286
- **Facts:** F-1542

### D-158 · Freeze r4: add information-available split (FACT-AVAIL) + ORACLE/ORACLE-0 rows; U-total stays verdict

- **Date:** 2026-10-21 21:18 · **Status:** kept
- **Context:** decided by: author asked
- **Decision:** Freeze r4: add information-available split (FACT-AVAIL) + ORACLE/ORACLE-0 rows; U-total stays verdict
- **Alternatives considered:** no split
- **Rationale:** separate "packs lack it" from "app fails to deliver it"
- **Consequence:** frozen sha 82772e33; labels quarantined
- **Facts:** F-1543, F-1853

### D-159 · Close decoder-level grounding axis on the 1.7B

- **Date:** 2026-10-21 22:10 · **Status:** kept
- **Context:** decided by: delegated coordinator (frozen gate)
- **Decision:** Close decoder-level grounding axis on the 1.7B
- **Alternatives considered:** AdaCAD (unopened)
- **Rationale:** all arms net 4-6 vs bar 9
- **Consequence:** closed
- **Facts:** F-1544

## 2026-10-22

### D-163 · Composer UX = one options button + chips only for non-default settings; auto search-term chips dropped

- **Date:** 2026-10-22 · **Status:** kept
- **Context:** decided by: author
- **Decision:** Composer UX = one options button + chips only for non-default settings; auto search-term chips dropped
- **Alternatives considered:** 4-chip query bar MVP
- **Rationale:** T1 term extraction failed (25 → 23 %)
- **Consequence:** design adopted for the fork
- **Facts:** F-1548

### D-160 · Carry chunk vectors forward only in no-displacement "extra" mode; fusion harmful on real items

- **Date:** 2026-10-22 01:10 · **Status:** kept
- **Context:** decided by: delegated coordinator
- **Decision:** Carry chunk vectors forward only in no-displacement "extra" mode; fusion harmful on real items
- **Alternatives considered:** fusion
- **Rationale:** fusion lost 6-8/22 real items
- **Consequence:** G2 full kit then failed real-item recovery (3/25)
- **Facts:** F-1545

### D-161 · Packs are the strategy: engine finds the context when the pack has it, model answers from it; stop expecting the model to answer alone; device day stopped

- **Date:** 2026-10-22 16:05 · **Status:** kept
- **Context:** decided by: author
- **Decision:** Packs are the strategy: engine finds the context when the pack has it, model answers from it; stop expecting the model to answer alone; device day stopped
- **Alternatives considered:** keep model/engine levers
- **Rationale:** QFORM 0.88 vs 0.19
- **Consequence:** two lanes (retrieval, coverage); NOTE-5 first ask
- **Facts:** F-1546, F-1854

### D-162 · Small focused packs, not giant ones; full Wikipedia = negative control

- **Date:** 2026-10-22 17:3x · **Status:** kept
- **Context:** decided by: author
- **Decision:** Small focused packs, not giant ones; full Wikipedia = negative control
- **Alternatives considered:** full Wikipedia
- **Rationale:** top100k takes 47-55 % of kept slots for net +2; small Q&A packs do not crowd; competitor full-enwiki search 17-21 s under model load
- **Consequence:** composition (merge) becomes the central question
- **Facts:** F-1547

### D-165 · Delivery is measured at chunk level from now on

- **Date:** 2026-10-22 22:09 · **Status:** kept
- **Context:** decided by: delegated coordinator
- **Decision:** Delivery is measured at chunk level from now on
- **Alternatives considered:** article-level
- **Rationale:** article-level overstated F1b by 13 facts
- **Consequence:** standing method
- **Facts:** F-1550, F-1856

### D-164 · Withdraw F3 (health no-source fallback) from the search fixes

- **Date:** 2026-10-22 22:41 · **Status:** kept
- **Context:** decided by: delegated coordinator (frozen safety rule)
- **Decision:** Withdraw F3 (health no-source fallback) from the search fixes
- **Alternatives considered:** keep F3 for +0.010
- **Rationale:** unsafe 9 → 13 on 65 probes
- **Consequence:** shippable set = gidf + F1 + F2 + F4 (+0.013, not a lever)
- **Facts:** F-1549, F-1855

## 2026-10-23

### D-178 · Engine route fixes validated on their own branch; not merged into ENGINE-RC (different code lineage)

- **Date:** 2026-10-23 · **Status:** kept
- **Context:** decided by: delegated coordinator
- **Decision:** Engine route fixes validated on their own branch; not merged into ENGINE-RC (different code lineage)
- **Alternatives considered:** merge
- **Rationale:** trees cannot be merged
- **Consequence:** App engine and bench engine still differ on routes
- **Facts:** F-1698

### D-167 · Close the research lines; no new arms after PLUGBATCH-SELF and STYLE-SEFIX; the rest of the work is acceptance tests

- **Date:** 2026-10-23 11:53 · **Status:** kept
- **Context:** decided by: author
- **Decision:** Close the research lines; no new arms after PLUGBATCH-SELF and STYLE-SEFIX; the rest of the work is acceptance tests
- **Alternatives considered:** keep running levers
- **Rationale:** "we reached where we needed to"; ensure the app delivers it
- **Consequence:** Held for search/decoder/detector lines; reopened on the content side at 15:39 (D-u-2324-08)
- **Facts:** F-1687, F-1857

### D-168 · Adopted for delivery: SEFIX-124 search stack + W78 reading-cost stack; Succinct for models ≤ 2 GB; Deep Research hidden; detector v3b stays; decoder/readers/gat

- **Date:** 2026-10-23 11:53 · **Status:** kept
- **Context:** decided by: author (plan by coordinator)
- **Decision:** Adopted for delivery: SEFIX-124 search stack + W78 reading-cost stack; Succinct for models ≤ 2 GB; Deep Research hidden; detector v3b stays; decoder/readers/gates closed NO
- **Alternatives considered:** Detailed default, Deep mode, detector retrains
- **Rationale:** measured results of 10-22/23
- **Consequence:** Carried into ENGINE-RC
- **Facts:** F-1688

### D-169 · Closing tests run on the desktop twin with no phone

- **Date:** 2026-10-23 11:58 · **Status:** kept
- **Context:** decided by: author
- **Decision:** Closing tests run on the desktop twin with no phone
- **Alternatives considered:** phone acceptance days
- **Rationale:** phone not available
- **Consequence:** UXMATRIX, U5, PACKPROOF ran on desktop
- **Facts:** F-1689

### D-194 · Succinct stays the 1.7B default; no conditional Detailed for delivered facts

- **Date:** 2026-10-23 12:18 · **Status:** kept
- **Context:** decided by: delegated coordinator
- **Decision:** Succinct stays the 1.7B default; no conditional Detailed for delivered facts
- **Alternatives considered:** Detailed when fact delivered
- **Rationale:** STYLE-SEFIX dU −0.028, CE 26→46 per 100
- **Consequence:** kept
- **Facts:** F-1858

### D-170 · Thesis to present with the app: right whenever the content is in a pack; app built for it

- **Date:** 2026-10-23 12:19 · **Status:** superseded by D-215 — restated by the author on 2026-10-25 (D-215); the closing tests supported this sentence only in a conditional form
- **Context:** decided by: author
- **Decision:** Thesis to present with the app: right whenever the content is in a pack; app built for it
- **Alternatives considered:** absolute accuracy claims
- **Rationale:** product framing
- **Consequence:** PACKPROOF supports only a conditional form (65 % when delivered)
- **Superseded by:** D-215
- **Facts:** F-1690

### D-171 · Defaults by rule: Succinct stays, Deep hidden, no change to the honesty surface

- **Date:** 2026-10-23 13:20 · **Status:** kept
- **Context:** decided by: delegated coordinator (frozen rule)
- **Decision:** Defaults by rule: Succinct stays, Deep hidden, no change to the honesty surface
- **Alternatives considered:** Detailed default
- **Rationale:** UXMATRIX matrix
- **Consequence:** Confirmed later by D-u-2324-13
- **Facts:** F-1691

### D-173 · No new packs for coverage (gaps are search, not missing content)

- **Date:** 2026-10-23 14:39 · **Status:** kept
- **Context:** decided by: delegated coordinator, asked by author
- **Decision:** No new packs for coverage (gaps are search, not missing content)
- **Alternatives considered:** build philosophy; blog; Gutenberg packs
- **Rationale:** 44/50 gaps already in K13; candidate packs ≈ 1 fact each
- **Consequence:** No pack builds
- **Facts:** F-1693

### D-172 · Keep Wikipedia packs in the default kit K13

- **Date:** 2026-10-23 14:58 · **Status:** kept
- **Context:** decided by: delegated coordinator (frozen gate), asked by author
- **Decision:** Keep Wikipedia packs in the default kit K13
- **Alternatives considered:** NOWIKI; NOWIKI2 kits
- **Rationale:** removing them loses 9 MAIN facts, 10 general items, 2 health sources
- **Consequence:** K13 stays
- **Facts:** F-1692, F-1859

### D-174 · CONTENT-FIRST: no model change; make the right chunk reach Qwen3-1.7B; build/shape the packs

- **Date:** 2026-10-23 15:39 · **Status:** kept
- **Context:** decided by: author
- **Decision:** CONTENT-FIRST: no model change; make the right chunk reach Qwen3-1.7B; build/shape the packs
- **Alternatives considered:** model change, bigger model
- **Rationale:** "even the small model should answer right having the content"
- **Consequence:** PACKSHAPE lever-candidate; others NO
- **Facts:** F-1694

### D-175 · Shaped factbook v2: card drafted as user-selected only; publish waits for author OK

- **Date:** 2026-10-23 17:07 · **Status:** kept
- **Context:** decided by: delegated coordinator
- **Decision:** Shaped factbook v2: card drafted as user-selected only; publish waits for author OK
- **Alternatives considered:** default-eligible publish
- **Rationale:** Opus +0.121 but one new warned CE; correct-any 0.50 < 0.60 eligibility
- **Consequence:** Not published as of 10-24; in ENGINE-RC kit; BoarLite D3 puts it in the APK
- **Facts:** F-1695, F-1860

### D-176 · Night program: build ENGINE-RC as one tree, validate 0-LLM first, generate all answers, judge nothing overnight

- **Date:** 2026-10-23 17:55 · **Status:** kept
- **Context:** decided by: author (scope cut 18:21) + coordinator
- **Decision:** Night program: build ENGINE-RC as one tree, validate 0-LLM first, generate all answers, judge nothing overnight
- **Alternatives considered:** judge overnight
- **Rationale:** validate the closed engine; judge on demand
- **Consequence:** 2,855 answers, 0 judge calls
- **Facts:** F-1696

### D-177 · X2B-BUDGET and RETBENCH best config stay out of ENGINE-RC

- **Date:** 2026-10-23 17:59 · **Status:** kept
- **Context:** decided by: delegated coordinator (frozen gates)
- **Decision:** X2B-BUDGET and RETBENCH best config stay out of ENGINE-RC
- **Alternatives considered:** adopt for +3..+5 facts
- **Rationale:** dose/number safety probes changed
- **Consequence:** Closed NO
- **Facts:** F-1697, F-1861

## 2026-10-24

### D-179 · Succinct stays the default; S+ (4-5 sentences) and two-paragraph variants rejected

- **Date:** 2026-10-24 14:15 · **Status:** kept
- **Context:** decided by: delegated coordinator (frozen ADOPT rule), judge run OK'd by author
- **Decision:** Succinct stays the default; S+ (4-5 sentences) and two-paragraph variants rejected
- **Alternatives considered:** S+, P2
- **Rationale:** same correctness, wrong-unwarned doubles
- **Consequence:** S STAYS
- **Facts:** F-1699, F-1862

### D-180 · Subject carry on follow-ups not adopted as an accuracy fix (UX gain only)

- **Date:** 2026-10-24 14:15 · **Status:** kept
- **Context:** decided by: delegated coordinator
- **Decision:** Subject carry on follow-ups not adopted as an accuracy fix (UX gain only)
- **Alternatives considered:** carry on
- **Rationale:** 0.458 correct both arms
- **Consequence:** measurement only
- **Facts:** F-1700

### D-181 · Closed simple chat app for one way of use: Succinct fixed; Deep Research, Detailed and length setting removed; free follow-ups; warning line kept; sources shown

- **Date:** 2026-10-24 14:25 · **Status:** kept
- **Context:** decided by: author
- **Decision:** Closed simple chat app for one way of use: Succinct fixed; Deep Research, Detailed and length setting removed; free follow-ups; warning line kept; sources shown
- **Alternatives considered:** app with many modes
- **Rationale:** small models gave the best results this way
- **Consequence:** Applied on a local branch
- **Facts:** F-1701, F-1863

### D-182 · App build choices: Qwen3-1.7B Q4_K_M default on every phone, English only, null-style cap 512, delete confirms, "Allow more" redo removed

- **Date:** 2026-10-24 15:40 · **Status:** kept
- **Context:** decided by: author decisions, applied by coordinator workflow
- **Decision:** App build choices: Qwen3-1.7B Q4_K_M default on every phone, English only, null-style cap 512, delete confirms, "Allow more" redo removed
- **Alternatives considered:** keep 1.5B; multilingual UI
- **Rationale:** closed-app spec
- **Consequence:** 9 local commits, debug APK built, no device test
- **Facts:** F-1702

### D-183 · BoarLite = a NEW bounty submission by the author (not the app maintainer's app); closed app, everything bundled, full K13 kit in one APK, shaped factbook v2, po

- **Date:** 2026-10-24 16:51 · **Status:** kept (amended by D-196) — 2026-10-24 18:03 (D-196): factbook v1 stays (D3 reverted); one fixed line on every answer replaces the ported warning line (D4). 2026-10-25 02:20 (D-211): renamed LabRat; the submission is the same app.
- **Context:** decided by: author
- **Decision:** BoarLite = a NEW bounty submission by the author (not the app maintainer's app); closed app, everything bundled, full K13 kit in one APK, shaped factbook v2, port the warning line, Qwen3-1.7B fixed
- **Alternatives considered:** submit the app maintainer's app
- **Rationale:** (decision page)
- **Consequence:** Implementation next; APK ≈ 3.0 GB, hosting open
- **Facts:** F-1703, F-1864

### D-196 · BoarLite: minimal health path; a fixed line replaces the ported warning line (D4); factbook v1 stays (D3 reverted); port the bench search

- **Date:** 2026-10-24 18:03 · **Status:** kept
- **Context:** decided by: author, on the native-engine comparison of 16:08-17:39 (numbers internal-pending-author)
- **Decision:** Port a minimal health path (fixed safe text plus emergency number when no health-family source is kept); replace D4 with one fixed, discreet line on every answer; keep factbook v1; port SEFIX-124 + HEADPASS-X2b before the submission under a frozen criterion (SEARCHPORT)
- **Alternatives considered:** port the no-citation warning line (D4); ship the shaped factbook v2 (D3); submit without the search port
- **Rationale:** the native path had no health grounding of its own; the comparison numbers stay internal (PD-09)
- **Consequence:** health gate, fixed line and factbook v1 landed by 18:12 (fb6ffbf6); SEARCHPORT criterion frozen 18:1x
- **Facts:** F-2189

### D-197 · Health detector B+FU (lexical rules + follow-up) chosen for BoarLite's health gate

- **Date:** 2026-10-24 18:23 · **Status:** kept
- **Context:** decided by: the BoarLite build session, checks set by the coordinator; the app's lexical test missed 29 of ENGINE-RC's 41 gated probes
- **Decision:** Gate a turn when the app's health test OR 11 lexical rules OR a short follow-up of a health turn fires; run the gate after retrieval
- **Alternatives considered:** title overlap with health articles (gated 5 of 19 health self-tests); port the mmBERT health detector (106 MB, 2-3 days)
- **Rationale:** catches all 4 invented-dose answers with 0 new false fires on 251 non-health dev items; fitted on the probes
- **Consequence:** 41-42 of 65 probes get the fixed text; 12 of 60 health self-tests too (Wikipedia-only articles)
- **Facts:** F-2192, F-2193

### D-198 · SEARCHPORT P1 left out of BoarLite after failing its frozen safety gate; switch off

- **Date:** 2026-10-24 18:34 · **Status:** kept
- **Context:** decided by: frozen criterion (one fix, one re-gate, then stop)
- **Decision:** Keep the ported search code with SearchPort off (byte-identical prompts); no screen, no P2
- **Alternatives considered:** ship P1 with the one fix; a second fix without a new criterion
- **Rationale:** gate d failed: 3 probe answers gained a dose figure from appended health passages
- **Consequence:** re-evaluated under the GROUNDED-DOSE rule at 19:13 (Addendum 1)
- **Facts:** F-2196

### D-199 · BoarLite onboarding: unpack screen + 5-card tour; Open only when the model is loaded

- **Date:** 2026-10-24 18:51 · **Status:** kept
- **Context:** decided by: author
- **Decision:** Approve the unpack screen and a 5-card tour with a live strip; remove downloads, model choice, style, Deep Research and language from setup
- **Rationale:** a closed app has nothing to download or choose; the first answer must not wait silently for the model
- **Consequence:** onboarding 2cf2c9db; model preload b8df70d9; first answer on the Pixel 11.9 s instead of about 2 min
- **Facts:** F-2199

### D-201 · SEARCHPORT Addendum 1: NOT-WORTH for the submission; switch stays off

- **Date:** 2026-10-24 19:13 · **Status:** superseded by D-203 — 19:35: the port was merged as ON_NO_HEALTH under the author's prior condition
- **Context:** decided by: frozen addendum reading
- **Decision:** Keep SearchPort off in the candidate APK
- **Rationale:** ungrounded dose figures 9 vs 5 with the port on (arm A FAIL)
- **Consequence:** Addendum 2 (ON_NO_HEALTH) frozen 19:2x
- **Superseded by:** D-203
- **Facts:** F-2203

### D-200 · GROUNDED-DOSE: judge health safety by grounded dose figures, not by kept-list proxies

- **Date:** 2026-10-24 19:1x · **Status:** kept
- **Context:** decided by: author ('we over-weighted safety and cut good changes')
- **Decision:** A health answer is safe iff it is the fixed text or every dose/amount figure appears in a shown passage; re-evaluate SEARCHPORT, X2B-BUDGET 900 and RETBENCH B-k4comp40 with it
- **Alternatives considered:** keep the 'kept list unchanged' and 'no new dose figure' proxies
- **Rationale:** three retrieval changes had been rejected on proxies, not on measured harm
- **Consequence:** arm A FAIL, arms B and C PASS; arm B shows a grounded figure can still be a toxic threshold
- **Facts:** F-2202

### D-202 · BoarLite ships with the Wikipedia-health limitation; medical Wikipedia titles after the submission

- **Date:** 2026-10-24 19:32 · **Status:** kept
- **Context:** decided by: coordinator, delegated by the author (19:3x)
- **Decision:** Keep Wikipedia in the kit; the gate counts only firstaid, MedlinePlus and health Q&A as health sources; 12 of 60 health self-tests get the fixed text
- **Alternatives considered:** drop the Wikipedia packs (facts 42 → 33, topics 25 → 11); port ENGINE-RC's health-topic routing before the submission
- **Rationale:** fixed text on a Wikipedia-only health article is the safe failure; a curated title list needs its own re-gate
- **Consequence:** post-submission: medical Wikipedia titles as health sources, re-gated with the grounded-dose rule and a toxic-threshold check
- **Facts:** F-2206

### D-203 · Search port merged into BoarLite as ON_NO_HEALTH despite a frozen-criterion FAIL by the letter

- **Date:** 2026-10-24 19:35 · **Status:** kept
- **Context:** decided by: coordinator under the author's standing condition (19:2x: 'I accept the health loss if it is worth it for the rest')
- **Decision:** Set SearchPort mode ON_NO_HEALTH (port on except on turns the health predicate reads as health); rerun the probes and false-fire set; build and smoke the final APK
- **Alternatives considered:** keep the port off (the frozen verdict); port on for every turn (Addendum 1: FAIL)
- **Rationale:** S2 met the usefulness bar; the health cost is 2 more ungrounded figures on the probes, with no probe leaving the fixed text
- **Consequence:** final candidate b4ef94f3; the port changes no health path on the 65 probes
- **Verification note:** Frozen criterion verdict: not WORTH-IT (S1 grounded-dose 6 vs 4 ungrounded). Adopted by the author's prior condition, not by the criterion.
- **Facts:** F-2207, F-2209

### D-204 · Final ruler run frozen: BoarLite b4ef94f3, v0.4, one seed, both judge families

- **Date:** 2026-10-24 20:1x · **Status:** kept
- **Context:** decided by: author approved the frozen addendum
- **Decision:** Run v0.4 (spec r4) on the desktop twin of b4ef94f3 with one seed (42), Claude Opus vs Claude references and gpt-5.6-sol vs its references; no tuning after this run; engine frozen unless the phone smoke forces an engine fix
- **Alternatives considered:** two seeds as in the spec; wait for a phone run
- **Rationale:** one seed was the author's choice; stated in every number
- **Consequence:** run complete 20:34; numbers published by the author's decision of 2026-10-25 as history (F-2215, F-2217; the paired delta vs the native engine branch, F-2216, stays internal); the headline is the on-phone run DEVICE-FINAL (OF-8)
- **Facts:** F-2214

### D-205 · Rebuild the release APK from 6aa7508a (two UI-only commits after b4ef94f3)

- **Date:** 2026-10-24 20:32 · **Status:** kept
- **Context:** decided by: coordinator, after the author noticed the phone showed the older tour
- **Decision:** Rebuild and reinstall the release APK from 6aa7508a with the factbook v1 bundle; smoke on the Pixel
- **Rationale:** 0 engine files changed, so the final ruler run stays valid
- **Consequence:** APK rebuild and phone smoke pending as of 20:34
- **Facts:** F-2213

### D-207 · Remove the PIN lock from BoarLite

- **Date:** 2026-10-24 21:30 · **Status:** kept
- **Context:** decided by: author (screens review)
- **Decision:** No PIN lock; PIN code and the sealed-chat legacy removed; reset texts no longer mention a PIN
- **Rationale:** a closed, simple app
- **Consequence:** PIN legacy dropped at 00:43 (e4625222)
- **Facts:** F-2220, F-2222

### D-206 · Remove the long-chat summary from BoarLite

- **Date:** 2026-10-24 22:10 · **Status:** kept
- **Context:** decided by: author (screens review; code removal recorded as an owner decision)
- **Decision:** Switch the long-chat summary off and remove its code
- **Rationale:** on the Pixel the 1.7B used only the last 3 exchanges of a long chat
- **Consequence:** summary code removed (d14804bf); chat history sent as before
- **Facts:** F-2221

### D-209 · Remove the Expo/React Native tree and the code unreachable in the closed app

- **Date:** 2026-10-24 22:55 · **Status:** kept
- **Context:** decided by: author (owner decisions recorded in the commits)
- **Decision:** Ship the native Android code only; remove the Detailed style, adaptive routing, persona and length options and Deep Research beyond the recap
- **Rationale:** none of it is reachable in a Succinct-only closed app
- **Consequence:** 274 engine tests pass; engine module 124 files changed, almost all removals; no ruler rerun
- **Facts:** F-2222, F-2223

### D-208 · Remove Portuguese support: the submitted app is English only

- **Date:** 2026-10-24 23:51 · **Status:** kept
- **Context:** decided by: author (owner decision recorded in the commit)
- **Decision:** Remove Portuguese support, task patterns and greetings, keeping words that are also English
- **Rationale:** the bounty is English only; the closed app has one language
- **Consequence:** English retrieval for short queries pinned by tests (ce38c43f)
- **Facts:** F-2222

## 2026-10-25

### D-214 · Host the LabRat APK on Hugging Face with a public install page

- **Date:** 2026-10-25 · **Status:** kept — 2026-10-25 15:3x-15:4x (D-218): APK hosted on Hugging Face; the code repository was made public (labrat-boar-fork).
- **Context:** decided by: author (OK given 2026-10-25)
- **Decision:** Upload the 3.04 GB APK to a Hugging Face repository with its sha256 and a public install page; keep the code repository private
- **Alternatives considered:** GitHub release assets (must be under 2 GiB)
- **Rationale:** the APK is 3.04 GB
- **Consequence:** upload after the final bundled build; a browser-install test on a certified phone planned
- **Facts:** F-2230, F-2231

### D-215 · Thesis restated: small models need external knowledge; a harness built around a small model's real capabilities, tuned for the app user

- **Date:** 2026-10-25 · **Status:** kept
- **Context:** decided by: author (publication decision 5, 2026-10-25)
- **Decision:** State the thesis as: small models need external knowledge; we learned that and built a harness around a small model's real capabilities, tuned for the app user's experience; the conditional closing-test numbers are its evidence and honest limits
- **Alternatives considered:** the conditional form as the thesis, the 2026-10-23 sentence quoted as the tested hypothesis; the 2026-10-23 sentence as the main claim
- **Rationale:** the closing tests support only the conditional form of the 2026-10-23 sentence; the restated thesis describes what was built and learned
- **Consequence:** replaces D-170 as the thesis statement; claims S40 and U41-U43 in content/claims-and-caveats.md
- **Facts:** F-2236, F-1704, F-1705, F-1706, F-1707, F-2080

### D-216 · Publish LabRat's numbers, keep the app maintainer's internal; headline = DEVICE-FINAL; b4ef94f3 desktop run = history; applyShown documented, not fixed

- **Date:** 2026-10-25 · **Status:** kept
- **Context:** decided by: author (publication decisions 1-4, 2026-10-25)
- **Decision:** Numbers of BoarLite/LabRat (incl. RULER-FINAL on b4ef94f3 and the coming DEVICE-FINAL rows) are public; RC1, native-engine-branch, app-pipeline-replica and MAINT numbers stay internal-pending-author; the headline is the final v0.4 ruler on the phone; the desktop b4ef94f3 run is history; Citations.applyShown is a known limitation
- **Alternatives considered:** keep all app numbers internal; publish everything; rerun the desktop ruler on LabRat code; fix applyShown and re-measure
- **Rationale:** LabRat is the author's own app; the maintainer's numbers need his consent; a fix would invalidate the measured engine
- **Consequence:** F-2215, F-2217, F-2208 and E-473 public; F-2216 stays internal (carries the native branch's absolute)
- **Facts:** F-2237, F-2215, F-2232

### D-210 · Simplify Settings; ship the licence texts in About; keep 50 chats

- **Date:** 2026-10-25 01:11 · **Status:** kept
- **Context:** decided by: author (UI review round)
- **Decision:** Settings without the Knowledge section or the title switch (titles always on); Clear chat history under Start over; 50 chats kept instead of 10; MIT licence texts in About → Credits
- **Rationale:** with 10 chats the drawer never scrolled and old chats were deleted
- **Consequence:** device-checked on the Pixel 8a
- **Facts:** F-2222

### D-211 · Rename BoarLite to LabRat; the assistant is Rat

- **Date:** 2026-10-25 02:20 · **Status:** kept
- **Context:** decided by: author, at the app maintainer's request
- **Decision:** Rename the app in the UI, docs and assets; name the assistant Rat in the byline, notification and the grounding prompt's identity line; keep the package id
- **Rationale:** the app maintainer asked for a distinct name
- **Consequence:** the identity line of the grounding prompt changes after the ruler run (ruler number = b4ef94f3); DEVICE-FINAL measures 7788924a
- **Facts:** F-2224, F-2225

### D-212 · Run DEVICE-FINAL: the final on-phone benchmark matrix of LabRat for publication

- **Date:** 2026-10-25 03:3x · **Status:** kept — Completed 2026-10-25 13:2x (X-406; F-2238): interrupted once and resumed; seed 44 dropped for time.
- **Context:** decided by: author (asked for the final benchmarks with the app running the engine on the phone, full matrix overnight)
- **Decision:** Freeze the criterion before generation; run M1-M5 on the Pixel 8a; claim numbers = M1 (both families) + M5; no tuning, no engine change
- **Alternatives considered:** keep the desktop-twin ruler run as the only ruler reading
- **Rationale:** the bounty is about a phone; the ruler run so far was a desktop twin of b4ef94f3
- **Consequence:** running as of this update; restarted once after an APK install interrupted it
- **Facts:** F-2227, F-2228, F-2229

### D-213 · LabRat logo: n8 (a magnifier whose ring is a rat's head)

- **Date:** 2026-10-25 11:24 · **Status:** kept
- **Context:** decided by: author, after 4 logo rounds
- **Decision:** Use n8 in the app, launcher and splash
- **Consequence:** APK installed on the Pixel 8a; smoke 6/6
- **Facts:** F-2226

### D-217 · Keep the carbon-monoxide probe answer as a known limitation; no health-gate change before the submission

- **Date:** 2026-10-25 14:0x · **Status:** kept
- **Context:** decided by: author
- **Decision:** List the probe in the submission's limitations; no engine change
- **Alternatives considered:** add the reading to the health gate's terms (an engine change)
- **Rationale:** an engine change before the submission would make the measured engine differ from the one installed
- **Consequence:** listed under limitations
- **Facts:** F-2245, F-2241

### D-218 · Make the LabRat repository public as labrat-boar-fork

- **Date:** 2026-10-25 15:4x · **Status:** kept
- **Context:** decided by: author (OK given 2026-10-25)
- **Decision:** Rename the repository labrat-boar-fork and make it public with README, results, pack provenance and licence
- **Alternatives considered:** keep the code private (D-214)
- **Rationale:** judges and readers can check the app and rebuild its bundle from public URLs
- **Consequence:** repository public; supersedes the 'code stays private' part of D-214
- **Facts:** F-2247, F-2246

### D-219 · Submission announcement: one post with the 60 s video, no thread

- **Date:** 2026-10-25 16:29 · **Status:** kept
- **Context:** decided by: author
- **Decision:** One post with the video plus a short poidh text, numbers from DEVICE-FINAL
- **Alternatives considered:** an 8-post thread
- **Consequence:** post prepared; not posted as of the record
- **Facts:** F-2251

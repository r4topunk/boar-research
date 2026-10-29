# RatLab decision log

> Closed record · research record 1.1.2 · as of 2026-10-28; the author closed the research lines on 2026-10-23. Current standing, not a final result: Open fronts: https://r4topunk.github.io/boar-research/data/status.json.
>
> Final · as of 2026-10-28 · 0 of 71 wins on the phone, U-total 0.165 (Claude) / 0.242 (gpt-5.6-sol), below the 0.50 bar

Public decisions of the research (2026-09-26 → 2026-10-25), ADR-style: what was decided, why, and whether it still stands. 208 decisions · kept 184 · superseded 22 · reversed 2. Machine-readable twin: https://r4topunk.github.io/boar-research/data/decisions.json. Fact ids resolve in https://r4topunk.github.io/boar-research/data/facts.json.

## 2026-09-26

<!-- lint:exempt:start -->
- [D-001] 2026-09-26 · Thesis: "quality per second + blind evaluation against a frontier model"; stay on the existing cross-platform app; plan a no-network Android submission · why: the existing claim had solid engineering but no measured research quality. · status: kept
  - alternatives considered: fork a new app; rely on the existing on-phone benchmark
  - what happened next: led to the 09-29 research pipeline and 10-01 harness
  - facts: [F-050]
<!-- lint:exempt:end -->
## 2026-09-30

<!-- lint:exempt:start -->
- [D-002] 2026-09-30 · References = Claude Opus + web search, frozen once, hashed; never regenerated · why: a fixed denominator makes runs comparable. · status: kept
  - alternatives considered: live references per run
  - what happened next: same refs used for every v0.1 number; regenerating = not comparable
  - facts: [F-059]
<!-- lint:exempt:end -->
## 2026-10-01

<!-- lint:exempt:start -->
- [D-003] 2026-10-01 · Build one evaluation harness (ADR-001): own thin protocol + existing scorers; 5 layers; 7 axes never averaged · why: each experiment wrote its own scripts; desktop and device rows had different shapes; no regression gate; run noise ≈ effect size. · status: kept
  - alternatives considered: Inspect AI (UK AISI); promptfoo; Inspect AI (Python, subprocess bridge); promptfoo (no paired bootstrap)
  - what happened next: harness became boar-eval, later the public boar-bench
  - facts: [F-1305] [F-678]
- [D-004] 2026-10-01 · Replace the 27 items borrowed from a competitor's question list with own items (bench v0.1) · why: do not copy competitors' test cases; clean benchmark. · status: kept
  - alternatives considered: keep them; keep them with attribution
  - what happened next: v0.1 = 60 public items (57 EN judged)
  - facts: [F-099] [F-101]
- [D-005] 2026-10-01 · Report a quality effect only if it exceeds the MDE printed by the diff tool · why: run-to-run noise (Δ 0.031) as large as effects. · status: kept
  - alternatives considered: report any sign
  - what happened next: became house rule; later refined (two-seed, seed-noise rule)
  - facts: [F-1137]
- [D-006] 2026-10-01 · Freeze every deciding criterion (sha256) before data; blind sets written by separate writers, never read by researchers · why: avoid post-hoc tuning. · status: kept
  - alternatives considered: iterate without freezes
  - what happened next: 65/65 criterion shas verify by 10-10
  - facts: [F-100]
- [D-007] 2026-10-01 · Seven axes (quality, truthfulness, safety, retrieval, latency, resources, stability), never averaged into one score · why: one average hides safety and latency regressions. · status: kept
  - alternatives considered: single composite score
  - what happened next: quality ratio became the published number; other axes reported separately
  - facts: [F-290]
- [D-008] 2026-10-01 · Research agents work in fixed lanes, write one "technique card" per idea, never run experiments or touch the product; only the coordinator queues runs · why: Avoid duplicate work; separate proposing from measuring. · status: kept
  - alternatives considered: Agents run their own tests
  - what happened next: the retrieval research agent 19 cards, the models/latency research agent 22, the evaluation/safety research agent 23; runner agent executed
  - facts: [F-823]
- [D-009] 2026-10-01 · Every pass/fail criterion written and sha256-frozen before the run; no edits after verdicts, only dated addenda · why: Prevent tuning the rule to the result. · status: kept
  - alternatives considered: Judge then decide
  - what happened next: 65/65 criterion hashes verified 10-10; 16 of 17 re-verified by an outside critic 10-16
  - facts: [F-1136]
<!-- lint:exempt:end -->
## 2026-10-02

<!-- lint:exempt:start -->
- [D-010] 2026-10-02 · Strategy memo: Android-only, three fronts (knowledge into the 4B's context; device truth + reader; held-out bench + claim); stop iPhone/1.5B quality work, perso · why: measured gap; only the 4B near the bar. · status: kept
  - alternatives considered: continue broad fronts
  - what happened next: iPhone work stopped; knowledge front closed later that day
  - facts: [F-697]
- [D-011] 2026-10-02 · Bar on the RAW ratio; every publication shows raw + floor-removed + above-always-decline side by side · why: rubric floor gives a blank system ~0.20–0.31. · status: superseded by D-036 (Floor-adjusted ratio + win/tie/loss became the headline on 2026-10-06 (applied 2026-10-07); the raw rule is still printed as the formal rule.)
  - alternatives considered: lead with floor-adjusted; Floor-adjusted only
  - what happened next: headline later switched to floor-adjusted (D-chron-early-21) while raw stays the formal rule
  - facts: [F-264] [F-271]
- [D-012] 2026-10-02 · Close the knowledge-pack front for the bounty after the big-pack gate failed replay ("no fourth pack iteration") · why: kill rule K1 pre-registered in the strategy memo. · status: superseded (packs reopened later only for the deep tier and as products)
  - alternatives considered: a fourth pack iteration (G1′)
  - what happened next: packs reopened later only for the deep tier and as products
  - facts: [F-072]
- [D-013] 2026-10-02 · Run the deep tier (35B MoE); its ratio counts only reported separately from the default, with its latency · why: first candidate lever with a prior above noise; bounty hint about large MoE. · status: kept
  - alternatives considered: ignore deep tier
  - what happened next: deep35 +0.060 (first lever above MDE)
  - facts: [F-074]
- [D-014] 2026-10-02 · Treat the bounty as qualitative: judged by a public confirmation, not a numeric benchmark · why: bounty text. · status: kept
  - alternatives considered: treat our ratio as the decision
  - what happened next: private ratio kept as instrument; claim framing open
  - facts: [F-111]
- [D-015] 2026-10-02 · Hold v0.2 as held-out: develop on v0.1, confirm only on v0.2 · why: avoid tuning on the claim set. · status: superseded by D-037 (v0.2 was declared burnt → dev on 2026-10-06.)
  - what happened next: v0.2 later burnt (D-chron-early-22)
  - facts: [F-112]
- [D-016] 2026-10-02 · Restate deep35 memory: "≤ 8 GiB" was our own estimate, not a bounty rule; macOS footprint ≠ phone RSS · why: the author asked why 8 GB if the bounty says 12 GB. · status: kept
  - alternatives considered: keep "fails memory"
  - what happened next: Linux 6,750 MiB (≈ 6.6 GiB) container test passed 10/10
  - facts: [F-069]
- [D-018] 2026-10-02 · "Iterate fast first, rigor later": sha freeze only when an idea goes to the full bench or held-out; funnel L0 → L1 → L2 → L3 · why: speed of iteration. · status: kept
  - alternatives considered: freeze every step
  - what happened next: funnel became standard (BOUNTY-BOARD rules)
  - facts: [F-113]
- [D-019] 2026-10-02 · Pairwise judging in both A/B orders; disagreement = tie; scores averaged across orders · why: removes position bias. · status: kept
  - alternatives considered: single order
  - what happened next: position consistency 96.5-100 % measured
  - facts: [F-1139]
- [D-020] 2026-10-02 · Freeze the analysis plan (metrics, CI method, seeds, wording rules) before items existed · why: prevents tuning metric to results. · status: kept
  - alternatives considered: decide after seeing numbers
  - what happened next: plan hashed (375ff004…); later changes only as dated addenda
  - facts: [F-114]
- [D-021] 2026-10-02 · Primary metric = raw ratio, bar > 0.50 (the author's decision on 2026-10-02, not the app maintainer's) · status: superseded by D-036 (Floor-adjusted ratio + win/tie/loss became the headline on 2026-10-06 (applied 2026-10-07); the raw rule is still printed as the formal rule.)
  - alternatives considered: floor-aware metric
  - facts: [F-1306]
- [D-022] 2026-10-02 · Blind / held-out sets: researchers never open, list or grep them; coordinator runs them by script, aggregates only · why: A filename-only grep had leaked set composition. · status: kept
  - alternatives considered: Trust-based access
  - what happened next: Rule widened to blind/ on 10-10; pre-commit hook blocks blind plaintext
  - facts: [F-828]
- [D-023] 2026-10-02 · Expensive strategy agent (the strategy agent, Fable tier) only for few big decisions, with a self-contained dossier; never loops · why: Cost: most expensive tier. · status: kept
  - alternatives considered: Continuous strategy agent
  - what happened next: Used once (S1 memo) in the record read
  - facts: [F-829]
- [D-024] 2026-10-02 · Make the memory-fit estimate repack-aware and load with no_extra_bufts on Android only · why: repack copied ~2.3 GiB of weights into anonymous memory and the phone killed the 4B. · status: kept
  - alternatives considered: apply to iOS too; leave as is
  - what happened next: Android-only variant frozen; iOS unchanged pending device evidence
  - facts: [F-679]
<!-- lint:exempt:end -->
## 2026-10-03

<!-- lint:exempt:start -->
- [D-025] 2026-10-03 · Move v0.2 plaintext out of researcher-readable paths after an exposure; treat the exposed item as seen · why: a trace scan printed one held-out item. · status: kept
  - alternatives considered: ignore
  - what happened next: git history still held the plaintext → later "burnt"
  - facts: [F-138]
- [D-026] 2026-10-03 · Declare three health blind sets dev; commission fresh blind sets from writers with no file access · why: traces sat in readable paths and were used as dev. · status: kept
  - alternatives considered: keep them blind
  - what happened next: new sets health-fresh1/2/3, chat-v3, meta-fresh1
  - facts: [F-304]
- [D-027] 2026-10-03 · No human review: an independent Opus reviewer agent decides content/wording; caveat "AI-reviewed, not clinically reviewed" stays · why: speed; author unavailable for 39 card decisions. · status: kept
  - alternatives considered: human/clinical sign-off; Author or clinician signs off
  - what happened next: reviewer changed 25/31 cards
  - facts: [F-1219] [F-834]
- [D-028] 2026-10-03 · Single goal = win the bounty; English only; no more work inside the maintainer's app; build a dedicated measurement app · why: focus. · status: kept
  - alternatives considered: keep improving the general product
  - what happened next: PT/ES lines parked; BOAR Bench built
  - facts: [F-075]
- [D-029] 2026-10-03 · Park the retrieval line after rv2 failed despite more gold in context · why: gold-sentence-in-context did not translate into judged quality. · status: superseded (retrieval reopened later only for the deep tier)
  - alternatives considered: another retrieval variant
  - what happened next: retrieval reopened later only for the deep tier
  - facts: [F-572]
- [D-030] 2026-10-03 · Single goal = the bounty bar; other quality work after the bounty · why: deadline + focus. · status: kept
  - alternatives considered: keep broad product work
  - what happened next: lanes re-assigned (model tier, health minimum, speed, demo device)
  - facts: [F-076]
<!-- lint:exempt:end -->
## 2026-10-04

<!-- lint:exempt:start -->
- [D-031] 2026-10-04 · Focus on the 4B default tier; deep tier parked at D1; coordinator runs work with subagents instead of a standing chat team · why: work budget; no 12 GB phone. · status: superseded (4B levers exhausted by 10-05; deep tier reopened 10-06)
  - alternatives considered: keep deep tier active
  - what happened next: 4B levers exhausted by 10-05; deep tier reopened 10-06
  - facts: [F-704]
- [D-032] 2026-10-04 · Adopt cut 3 (verdict guard + arithmetic repair + snakebite text) · why: L1 Δ +0.029 [+0.007, +0.058], confident-wrong 15 → 9, unsafe 0. · status: kept
  - alternatives considered: computed-verdict override family (all failed gates); verdict guard v4, water card, computed verdict
  - what happened next: Cut 3 became the first claim build; claim runs 10-05
  - facts: [F-1220] [F-1221]
- [D-033] 2026-10-04 · Park the web-only knowledge pack for the bounty (public-figure blog pack and a research-forum pack were the alternatives). · why: gains come from non-redistributable sources or in-kit misses; best pack +0.007 net. · status: superseded (later replaced by the open-corpus Knowledge Pack program (10-12))
  - alternatives considered: public-figure blog pack, ethresear.ch pack
  - what happened next: later replaced by the open-corpus Knowledge Pack program (10-12)
  - facts: [F-084]
<!-- lint:exempt:end -->
## 2026-10-05

<!-- lint:exempt:start -->
- [D-034] 2026-10-05 · Fix the KV session save path (KVFIX) and block fragment/figurative instant answers (INSTANT-FRAG) → cut 4 · why: A15 smoke: every question re-prefilled the prefixes; "capital of France" answered with a Lyon fragment. · status: kept
  - alternatives considered: skip the route gate; threads; repack
  - what happened next: cut 4 built; KVFIX real gate is the device
  - facts: [F-705]
- [D-035] 2026-10-05 · Bench APK with INTERNET permission removed (no-network by construction) · why: prove offline operation statically. · status: kept
  - alternatives considered: rely on airplane mode only
  - what happened next: audit verdict NO-NETWORK-BY-CONSTRUCTION; later phone runs used it
  - facts: [F-706]
<!-- lint:exempt:end -->
## 2026-10-06

<!-- lint:exempt:start -->
- [D-036] 2026-10-06 · Headline = floor-adjusted ratio + win/tie/loss (+ share of items ≥ 3/5), raw second; own bar = floor-adj ≥ 0.50 on V-para · why: raw 0.50 is ~61 % free because of the rubric floor. · status: kept
  - alternatives considered: keep raw headline; Raw headline
  - what happened next: board and claim draft rewritten 10-06 22:40
  - facts: [F-1146] [F-1226] [F-1227]
- [D-037] 2026-10-06 · Treat v0.2 as burnt (dev); a final number needs v0.3 written outside the Claude family · why: plaintext in private git history + 4 runs + a targeted fix. · status: kept
  - alternatives considered: rewrite git history; keep using v0.2 as held-out
  - what happened next: v0.3 spec written 10-07; items not written by 10-10
  - facts: [F-1248] [F-1249]
- [D-038] 2026-10-06 · Freeze the claim build at cut 6; later only routing/safety fixes that leave v0.1 answers unchanged · why: stable claim evidence. · status: superseded by D-046 (Relaxed on 2026-10-07: cut 7 added FACTS r6, which changed 8 v0.1 answers.)
  - alternatives considered: keep shipping answer-changing arms
  - what happened next: cut 7 later added the fact table (0 fires on held-out sets)
  - facts: [F-331] [F-723]
- [D-039] 2026-10-06 · Stop answer-identical 4B arms; reopen the deep tier as the primary quality lever · why: 15 arms, 0 ratio movement. · status: kept
  - alternatives considered: continue 4B polishing
  - what happened next: deep-tier line ran 10-07 → 10-10
  - facts: [F-576]
- [D-040] 2026-10-06 · Cheap judge for triage (Sonnet-low, replaced by Haiku 5.5-low on 10-07); Opus only for confirmation and claim numbers · why: judge is the largest cost. · status: superseded by D-049 (Sonnet-low was replaced by Claude Haiku 5.5-low as the L1 judge on 2026-10-07 (HAIKUJUDGE).)
  - alternatives considered: Opus for everything
  - what happened next: judge calls fell from 12k–20k calls / 6 days to ≈ 1.5k / 2 days
  - facts: [F-147] [F-157]
- [D-041] 2026-10-06 · Declare v0.2 burnt → dev after its plaintext was found in git history · why: Honesty: builders could have seen it. · status: kept
  - alternatives considered: Keep calling it held-out
  - what happened next: An unexposed held-out number needs a v0.3 written outside the Claude family (0 items as of 10-17; open front OF-3)
  - facts: [F-1250]
- [D-042] 2026-10-06 · Keep FACTS r6 as head despite FAIL by frozen rule (recall 70 % < 75 %) · why: r6 dominates r5 on every frozen measure; precision 96.6 %, FP 0/100 adversarial. · status: kept
  - alternatives considered: close at r5; build r7 (forbidden by criterion)
  - what happened next: Shipped in cut 7; stated as "FAIL stands"
  - facts: [F-332]
- [D-043] 2026-10-06 · Lead every public number with floor-adjusted + win-rate, not raw · why: raw 0.50 is a rubric-floor artefact (always-decline ≈ 0.31 raw) · status: kept
  - alternatives considered: keep raw as headline (pre-registered formal rule)
  - facts: [F-277]
- [D-044] 2026-10-06 · Adopt CUT5-LITE (KV prefix for no-source prompts + route-gate skip), reject CUT5-SPEED · why: CUT5-SPEED failed its desktop speed gate (1.071× vs ≤ 0.8); lite was identity-safe. · status: kept
  - alternatives considered: ship all speed arms
  - what happened next: cut 5 = device-day candidate
  - facts: [F-722]
- [D-045] 2026-10-06 · Adopt DETMAX → cut 6 · why: chit-chat before an emergency lost 7/240 routes; DETMAX 0/240. · status: kept
  - alternatives considered: no change; lexical follow-up fix (HFU, failed)
  - facts: [F-333]
<!-- lint:exempt:end -->
## 2026-10-07

<!-- lint:exempt:start -->
- [D-046] 2026-10-07 · Cut 7 = cut 6 + FACTS r6 (adopted on gates: 0 fires on held-out sets); no relaxed lowercase rule; fine-tune data 1k go; "no device exists" · why: deterministic facts lever; no phone. · status: kept
  - alternatives considered: wait for more recall; re-run full claim runs (burns held-out again); no FACTS; r7
  - what happened next: cut 7 frozen; fine-tune data failed review same day
  - facts: [F-1230] [F-353] [F-745]
- [D-047] 2026-10-07 · v0.3 written by the author with a non-Claude web model; hashes only before scoring · why: self-preference risk; burnt v0.2. · status: superseded by D-123 (On 2026-10-18 v0.3 was dropped before closure (D5); the v0.4 ruler set replaced it.)
  - alternatives considered: Claude-written items; Claude subagent writers (as v0.2)
  - what happened next: spec ready; items not written by 10-10
  - facts: [F-1148] [F-1251]
- [D-048] 2026-10-07 · Autonomous mandate: keep running rounds without asking; stop only for irreversible/expensive items · why: throughput. · status: kept
  - alternatives considered: ask per round
  - what happened next: deep-tier rounds ran unattended
  - facts: [F-588]
- [D-049] 2026-10-07 · Haiku 5.5-low replaces Sonnet-low as L1 judge · why: same winner 54/57, 3.5 s/call, ~14× cheaper. · status: kept
  - alternatives considered: Sonnet-low; Haiku medium
  - what happened next: adopted; known to compress gaps
  - facts: [F-1149]
- [D-050] 2026-10-07 · Local open-weights judge (Gemma 4 26B) allowed for triage/ranking only, never for the number · why: keeps ranking, +0.11 lenient, κ 0.32-0.55. · status: kept
  - alternatives considered: adopt as main judge
  - what happened next: not used for headline numbers
  - facts: [F-283]
- [D-051] 2026-10-07 · Shard the judge: N = 4 default for Haiku L1 and for Opus L2/claim · why: ×4.5 wall gain, 0 rate limits, same winners. · status: kept
  - alternatives considered: sequential; N = 8
  - what happened next: in force; a stopped shard is resumed, never skipped
  - facts: [F-159]
- [D-052] 2026-10-07 · Haiku 5.5-low as L1 triage judge, Opus only to confirm and for claim numbers; judge sharded N = 4 · why: ≈ 14× cheaper than the previous triage judge; same winner as Opus 54/57. · status: kept
  - alternatives considered: Opus everywhere; Sonnet-low triage; Sonnet-low; local Gemma (ranking only, +0.11 lenient)
  - what happened next: Haiku compresses gaps 15-30 %; near-miss escalation rules added
  - facts: [F-1150] [F-1151]
- [D-053] 2026-10-07 · "No device exists": device tasks dormant · why: No 12 GB phone available. · status: reversed (A 12 GB-class phone (10.7 GiB usable) ran cut 7 on 2026-10-14.)
  - alternatives considered: Keep proposing device work
  - what happened next: Later reversed in practice when a 10.7 GiB phone ran cut 7 on 10-14
  - facts: [F-733]
<!-- lint:exempt:end -->
## 2026-10-08

<!-- lint:exempt:start -->
- [D-054] 2026-10-08 · SLICE20 triage before any full deep/held-out arm · why: ~60 % generation saving on NO arms. · status: superseded (later replaced by stratified random slices (10-10))
  - alternatives considered: full sets always
  - what happened next: later replaced by stratified random slices (10-10)
  - facts: [F-169]
<!-- lint:exempt:end -->
## 2026-10-09

<!-- lint:exempt:start -->
- [D-055] 2026-10-09 · V-para status: held-out for the 4B claim runs; dev-style for everything measured after 10-06 · why: exposure ledger showed conflicting status labels. · status: kept
  - alternatives considered: keep calling it blind; keep calling it held-out
  - what happened next: every deep-tier number on V-para is labelled dev-style
  - facts: [F-1232] [F-1233]
- [D-056] 2026-10-09 · Recommend thinking budget 512 for the deep tier · why: CHEAPER-PARITY with 1024 at 0.55× time. · status: kept
  - alternatives considered: 1024; 256; 1024 (slower), 256 (−0.028, CHEAPER-LOSS), Gemma + thinking (−0.028); 256 (loses), 1024, 3072, Gemma 26B
  - what happened next: becomes the "recommended deep configuration"
  - facts: [F-598] [F-599] [F-748]
<!-- lint:exempt:end -->
## 2026-10-10

<!-- lint:exempt:start -->
- [D-057] 2026-10-10 · Near-miss rule: a Haiku Δ within 0.01 of a threshold triggers Opus on the same ids · why: Haiku compressed a +0.048 Opus gap to +0.027. · status: kept
  - alternatives considered: trust Haiku; trust Haiku always
  - what happened next: applied to THINK4B
  - facts: [F-1158] [F-613]
- [D-058] 2026-10-10 · Seed-noise reading rule (V-para one-seed deep Δ < ~0.03 is noise; later raised to 0.05) · why: SEEDVAR three-seed spread. · status: superseded by D-113 (Threshold raised from 0.03 to 0.05 on 2026-10-16 after the outside critique (SEEDVAR showed a −0.039 gap between seeds).)
  - alternatives considered: single-seed verdicts; single-seed decisions; treat one-seed rows as decisive
  - what happened next: in CLAUDE.md and RULE-CHANGES
  - facts: [F-1159] [F-1160] [F-1162]
- [D-059] 2026-10-10 · Research on the Mac mini only until the bar is met; no APK/device/claim-package work · why: author's direction after the process review. · status: superseded (The closing sprint from 2026-10-14 brought app and release work back (upstream PR, public repositories).)
  - alternatives considered: claim-path first (review's recommendation); A deep-tier arms; B v0.3 outside Claude; C bigger model
  - what happened next: handoff rewritten for research scope
  - facts: [F-763] [F-854]
- [D-060] 2026-10-10 · Proceed on stated defaults for the claim path (debug-signed APK, raw formal + floor-adj + win-rate, no v0.3, no device relay) · why: unblock work without waiting on the author. · status: superseded (superseded 45 min later by the STOP)
  - alternatives considered: ask and wait
  - what happened next: superseded 45 min later by the STOP
  - facts: [F-758]
- [D-061] 2026-10-10 · Every deciding run needs a frozen criterion with a Power block; slices = random20 files · why: stop under-powered closures. · status: kept
  - alternatives considered: signal20 slices (retired); voluntary; Optional
  - what happened next: arm.sh refuses launch without the block
  - facts: [F-177] [F-180] [F-195]
- [D-062] 2026-10-10 · Decide direction on v0.2 (seed-stable), confirm on V-para with 2 seeds; adopt a lever only after two-seed V-para confirmation · why: v0.2 per-item seed r 0.90 vs V-para 0.5-0.7. · status: kept
  - alternatives considered: decide on V-para one seed
  - what happened next: in force
  - facts: [F-176]
- [D-063] 2026-10-10 · Fail-closed pipeline: errored traces/missing ids stop the run or score at the floor · why: the old judge silently dropped errored traces, flattering a failing device. · status: kept
  - alternatives considered: drop silently; Manual checks
  - what happened next: flags `--strict`, `--floor-errored`, `--floor-missing`
  - facts: [F-179] [F-752]
- [D-064] 2026-10-10 · Random stratified 20-id slices (seed 7) replace the "20 hardest items" slice · why: hardest-20 inflated deltas (+0.091 slice vs +0.026 full) · status: kept
  - alternatives considered: keep signal20; Hardest-20 slices
  - what happened next: in force; slice only screens for futility
  - facts: [F-1161] [F-178]
- [D-065] 2026-10-10 · Win-rate reported, never gated (later: proposal to drop the win-rate conjunct because it is saturated at 0) · why: every phone system scores 0 wins vs a 4.9/5 reference. · status: kept
  - alternatives considered: gate on win-rate > 0
  - facts: [F-753]
- [D-067] 2026-10-10 · Declare the deep-tier line closed on desktop and the 4B side closed · why: model, parity, thinking, budget, persona/context, routing all measured. · status: kept
  - alternatives considered: keep sweeping configs
  - what happened next: Research moved to Knowledge Packs (10-12)
  - facts: [F-614]
- [D-068] 2026-10-10 · Keep retrieval on the deep path · why: no-pack −0.045 (−0.083…−0.011) · status: kept
  - alternatives considered: drop packs for speed
  - what happened next: kept
  - facts: [F-997]
<!-- lint:exempt:end -->
## 2026-10-11

<!-- lint:exempt:start -->
- [D-069] 2026-10-11 · Run research as an unattended self-paced loop (one experiment per tick, META every 8 ticks) · why: use idle machine time; keep method improving. · status: kept
  - alternatives considered: session-by-session manual runs; Author-driven sessions
  - what happened next: 133 ticks over 10-11→10-14
  - facts: [F-857] [F-858]
- [D-070] 2026-10-11 · Measure the loss map before more levers (LOSSMAP first) · why: direct levers at the biggest loss bucket. · status: kept
  - alternatives considered: keep running backlog order
  - what happened next: re-ranked backlog; absent knowledge = 0.59 / 0.55 of loss
  - facts: [F-860]
- [D-072] 2026-10-11 · Common-mode CIs for deep-tier rows: CI = Δ ± 1.96·sqrt(SE_item² + 2σ_run²) · why: item bootstrap ignores run-level seed noise. · status: kept
  - alternatives considered: item bootstrap only; plain item bootstrap
  - what happened next: deep CIs ~1.2-1.3× wider; readings unchanged
  - facts: [F-1176] [F-1236]
- [D-073] 2026-10-11 · Negative results relabelled "not detected at MDE x (n, seeds)" when under-powered · why: "closed" overstated weak negatives. · status: kept
  - alternatives considered: keep "closed"; Plain "closed"
  - what happened next: CLOSED.md rows carry MDE and reopen condition
  - facts: [F-1177] [F-1178] [F-198]
- [D-074] 2026-10-11 · Verdict labels LEVER / SMALL / NO / "not decided at MDE"; adopt only after two-seed confirmation on V-para · why: Stop over-reading noise. · status: kept
  - alternatives considered: Point-estimate promotion
  - what happened next: Adopted levers after 10-08: 0 on the bounty set
  - facts: [F-087]
<!-- lint:exempt:end -->
## 2026-10-12

<!-- lint:exempt:start -->
- [D-075] 2026-10-12 · Close QUANTCEIL as "not detected at MDE 0.03" after V-para two seeds · why: seeds split +0.030 / −0.022. · status: kept
  - alternatives considered: adopt on v0.2 wrong-bucket repair
  - what happened next: model-knowledge levers on this hardware declared exhausted
  - facts: [F-207]
- [D-076] 2026-10-12 · Withdraw "facts are not in Wikipedia"; adopt the peer research's task chain · why: peer review showed WIKISECTION covered only one pack and part of the items. · status: kept
  - alternatives considered: keep the closure; build a new corpus right away
  - what happened next: WIKIFULL stages run; result 9/34 (a lower bound)
  - facts: [F-1003] [F-1011]
- [D-077] 2026-10-12 · Phone-time wording: deep + think 512 ≈ 1.9–2.8 min on a Pixel 8 Pro CPU; competitor percentages never quoted as a gap · why: corrected premises 2 and 5. · status: kept
  - alternatives considered: the earlier 3.5–5 min figure
  - what happened next: applied in all later texts
  - facts: [F-768]
- [D-078] 2026-10-12 · Pivot to Knowledge Packs; primary metric = in-pack conditional ratio · why: the product is a small model + user-selected packs; the unconditional bar was not moving. · status: kept
  - alternatives considered: stay on the bar; keep deep-tier sweeps; non-Wikipedia corpus
  - what happened next: P1–P4, pack workflow, pack stack
  - facts: [F-1004] [F-1012]
- [D-079] 2026-10-12 · Build a pack-authoring workflow; agents may write the 20 public self-tests per pack; held-out claim items stay non-Claude · why: "we will be the first author with publications" · status: kept
  - alternatives considered: only use existing packs
  - what happened next: 11 packs published 10-13
  - facts: [F-1015]
- [D-080] 2026-10-12 · Pack format unchanged (format 2); licence policy PD/CC0/CC BY/CC BY-SA only; never NC; per-row attribution for Stack Exchange; archive.org pre-2024 SE dumps, no · why: zero format risk; licence compliance. · status: kept
  - alternatives considered: format v3 now; NC corpora (wikiHow, WHO, OpenStax); Kiwix 2026 ZIMs (fresher)
  - what happened next: applied to all published packs
  - facts: [F-1017] [F-368]
- [D-081] 2026-10-12 · Autonomy rule: never ask for approval; paid API only when no free equivalent, capped and logged · why: author said Claude usage is not the constraint. · status: kept
  - alternatives considered: per-step approval
  - what happened next: loop ran without approval asks
  - facts: [F-870]
- [D-082] 2026-10-12 · Knowledge packs = format 2 SQLite, per-row attribution, four artefacts per pack (card, self-test, coverage probe, crowding probe) · why: zero format risk; licence compliance; measured crowding failure. · status: kept
  - alternatives considered: format v3 first
  - what happened next: 11 packs built and published 10-13
  - facts: [F-1005]
- [D-083] 2026-10-12 · "Default-eligible" only if a pack holds ≤ 0.40 of kept slots and does not lower kit gold; otherwise user-selected only · why: crowding measured. · status: kept
  - alternatives considered: install everything
  - facts: [F-1006]
<!-- lint:exempt:end -->
## 2026-10-13

<!-- lint:exempt:start -->
- [D-084] 2026-10-13 · Publish packs that pass the four-artefact check (card, self-test, coverage, crowding) on HF under the author's standing OK · why: public reuse; licence clarity per pack. · status: kept
  - alternatives considered: hold until measured further
  - what happened next: 7 + 2 + 2 packs published
  - facts: [F-1036]
- [D-085] 2026-10-13 · No cap on Haiku judge calls (Rule 25) · why: Haiku is cheap triage; idle caps cost machine time. · status: kept
  - alternatives considered: [usage detail removed]
  - what happened next: 720-call scoring passes became routine
  - facts: [F-876]
- [D-086] 2026-10-13 · Run an oracle/ceiling cell (ORACLE-ST) before more pre-processing levers · why: decide whether reader or retrieval is the wall. · status: kept
  - alternatives considered: keep adding retrieval tricks
  - what happened next: ceiling +0.095 found; became a standing rule (LOOP v2 D8)
  - facts: [F-1045]
- [D-087] 2026-10-13 · Routing among packs closed at the product level; keep rule + quota only an optional setting · why: crowding cost small (−0.016 Haiku / −0.019 Opus); routers 0.25–0.61 accuracy. · status: kept
  - alternatives considered: top-1 router, 4B zero-shot classifier
  - what happened next: product reading: ship small user-selected packs, no automatic routing
  - facts: [F-1046]
- [D-089] 2026-10-13 · Claim draft v3.9 adopts the red-team findings (v0.2 "formerly held-out", V-para writer disclosed, verdict reuse disclosed) · why: red-team found no inflated number but 9 overclaiming sentences. · status: kept
  - alternatives considered: keep v3.8
  - what happened next: 41 edits applied
  - facts: [F-216]
- [D-090] 2026-10-13 · Never idle while 0-paid-call work exists; no Haiku cap · why: Author objected after 9 idle ticks ("why idle when I asked to never stop?", paraphrase) · status: kept
  - alternatives considered: Keep caps
  - what happened next: 10-14 log: 0 idle ticks; later critic warns "idle lane = failure" rewards trivial probes
  - facts: [F-1185]
<!-- lint:exempt:end -->
## 2026-10-14

<!-- lint:exempt:start -->
- [D-091] 2026-10-14 · Run doc2query PoC overnight on the MacBook instead of renting a GPU · why: a rented GPU vs free local hours. · status: kept
  - alternatives considered: rented GPU
  - what happened next: 4.77 h, FAIL; later cited as an avoidable loss (speed gate overridden by an addendum)
  - facts: [F-921]
- [D-092] 2026-10-14 · HEADPASS-X2b = the pack line's retrieval recommendation for format-v3 packs; X1 for format-2 packs · why: Opus +0.066 (+0.043…+0.091), no harm on kit. · status: kept
  - alternatives considered: reranker X3; unbudgeted X2; X1 only (+0.033); X3 reranker (FAIL reach, 21 s/item)
  - what happened next: X3 failed at step 0; X2b staged for after 10-20 (PR-2)
  - facts: [F-1059] [F-1070]
- [D-093] 2026-10-14 · SFT of the 4B closed unless a teacher reaches ≥ 50 % faithfulness on distractor-rich targets · why: Haiku teacher 38 %, deep teacher 5 %. · status: kept
  - alternatives considered: train anyway
  - what happened next: closed (R71)
  - facts: [F-481]
- [D-094] 2026-10-14 · Rule 29 experiment economics: Ceiling block (launch only if ≥ 2×MDE) and Budget block (smoke, wall caps, kill rule) · why: ≈ 1,440 avoidable Opus calls and long bad tests. · status: kept
  - alternatives considered: free launches; status quo; Keep "any Haiku Δ > 0 → Opus"
  - what happened next: reviewed, edits applied
  - facts: [F-885] [F-886] [F-889] [F-891]
- [D-095] 2026-10-14 · LOOP v2 decisions D1–D12 (machine-side queue runners, smoke-first, STATE line, lanes, guards as scripts, handoff instead of compaction, daily brief, watchdog) · why: 26 incidents, ≈ 31 h avoidable machine time. · status: kept
  - alternatives considered: keep v1 loop; Fresh-context `claude -p` ticks (kept as option behind a shadow run)
  - what happened next: T1–T7 built 10-15; T8 10-16
  - facts: [F-890] [F-927]
- [D-097] 2026-10-14 · Publish research AND benchmark for other teams; publish v0.1 reference-answer text; v0.2/V-para refs stay hashes only · why: other teams cannot run the judge comparably without refs. · status: kept (Update 2026-10-27: the v0.2 and V-para references were published with the retired held-out sets in boar-bench (bench/heldout/); items are byte-identical to the hashes committed before opening, except documented redactions.)
  - alternatives considered: publish hashes only
  - what happened next: boar-bench carries refs with provenance on the dataset card
  - facts: [F-1310]
- [D-098] 2026-10-14 · Bounty chat gets method, packs and device proof only; numbers only after the shared rubric exists · why: numbers without a shared rubric are not comparable. · status: kept
  - alternatives considered: post scores
  - what happened next: post drafts carry no scores
  - facts: [F-1058]
- [D-099] 2026-10-14 · Verdict, registry row (CLOSED.md) and exposure row in the same commit · why: ledger audit found 48 verdicts without registry rows. · status: kept
  - alternatives considered: separate bookkeeping; Periodic backfill
  - what happened next: in force
  - facts: [F-887] [F-888]
<!-- lint:exempt:end -->
## 2026-10-15

<!-- lint:exempt:start -->
- [D-100] 2026-10-15 · First public push by the coordinator, only for the two new repos, on the author's explicit instruction · why: release. · status: kept
  - alternatives considered: keep private
  - what happened next: repos live; no-push rule stays for everything else
  - facts: [F-936]
- [D-101] 2026-10-15 · Accept the maintainer's native Kotlin app as the official submission; our numbers are labelled as the TypeScript engine's · why: the maintainer owns the submission. · status: superseded by D-183 (On 2026-10-24 the author made BoarLite, a new closed app of his own, the bounty submission.)
  - alternatives considered: submit the RN app with PR #85; the React Native app carrying cut 7 via PR
  - what happened next: claim v4.1 vehicle paragraph; native score pending
  - facts: [F-1238] [F-788]
- [D-103] 2026-10-15 · Reject the lexicon numeric guard; ship calculator-only NUMGUARD r3 · why: confirmation review: a lexicon guard cannot be made safe (numeric health questions leak) · status: kept
  - alternatives considered: NUMGUARD-FINAL lexicon guard
  - what happened next: r3 pushed to PR #85
  - facts: [F-1275]
- [D-104] 2026-10-15 · Lite tier is post-10-20 work, explored with quick diagnostic tests; starts with an unsafe-answer warning · why: 2B −0.168 and 6/15 unsafe health answers; weaker phones matter. · status: superseded by D-134 (On 2026-10-20 the small model became the main 8 GB engine, not a post-deadline lite line.)
  - alternatives considered: drop lite tier
  - what happened next: LITE2–LITE8, LITEREADERS etc. 10-15/16; closed for now
  - facts: [F-790]
- [D-105] 2026-10-15 · Release as two fresh repos with one squashed commit, neutral author, curated whitelist + scrub + mechanical gate + independent review; never the private history · why: Private history holds held-out plaintext and personal data. · status: kept
  - alternatives considered: Publish private repos
  - what happened next: Gate FAIL on 2 handle URLs fixed; 41/44 review findings applied; live 10:07
  - facts: [F-1312]
- [D-106] 2026-10-15 · Drop the loop-operations memo and internal decision memo from the public repo; replace with a 9-line method summary · why: Reviewer: internal agent prompts, caps, people and channels. · status: kept
  - alternatives considered: Publish as is
  - what happened next: `method/METHOD.md`
  - facts: [F-930]
- [D-107] 2026-10-15 · Lite tier: thinking stays OFF; 1.7B Q4_K_M chosen over ternary 2B and Q8_0 · why: LITE2 2B −0.057; LITE-THINK flat/negative; QUANTLITE flat and slower. · status: kept
  - alternatives considered: Bonsai ternary 2B/4B; Q8_0
  - what happened next: Lite tier remains a product idea, not a claim
  - facts: [F-645]
- [D-108] 2026-10-15 · Keep the native-app comparison internal until the final build is scored · why: intermediate build, decision by the author. · status: kept
  - alternatives considered: publish now; publish
  - what happened next: Number withheld from claim text
  - facts: [F-1237] [F-1263]
- [D-109] 2026-10-15 · Health answers never come from the model on the default tier; doses never from a model (HEALTHGAP); a fired detector can only be overridden by a deterministic c · why: safety; model answered doses from memory on probes. · status: kept
  - alternatives considered: model with a disclaimer
  - facts: [F-374]
<!-- lint:exempt:end -->
## 2026-10-16

<!-- lint:exempt:start -->
- [D-110] 2026-10-16 · TK2-FIX is a correctness fix, not a score lever; out of PR #85 before 10-20 · why: +0.010 pooled, needs a builder change too. · status: kept
  - alternatives considered: include in PR
  - what happened next: queued as a post-10-20 patch
  - facts: [F-1284]
- [D-111] 2026-10-16 · Idle-lane rule: a blocked lane is one log row; every other lane filled at once; refined 21:5x to "arms only for new questions with ceiling ≥ MDE, quiet ticks ot · why: ≈ 5 h of idle lanes on 10-16. · status: kept
  - alternatives considered: idle waiting
  - what happened next: settled the critique's point on 3-minute filler probes
  - facts: [F-1199]
- [D-112] 2026-10-16 · deps.warn (unsafe-answer warning) stays off by default · why: out-of-sample recall 3/8 (lexicon) and 12/18 with FP 8/92 (detector) · status: kept
  - alternatives considered: default-on
  - what happened next: not handed to the PR
  - facts: [F-389]
- [D-113] 2026-10-16 · Apply the adversarial critique: lite "= 4B" only on pack-matched dev; one-seed V-para noise rule 0.03 → 0.05; n≈20 closures relabelled "not detected at MDE 0.08 · why: over-stated internal summaries. · status: kept
  - alternatives considered: keep wording
  - what happened next: 7 re-wordings applied
  - facts: [F-1201]
- [D-115] 2026-10-16 · Claude judge stays the headline (lower of two judges); judge family named next to every ratio; win/tie/loss leads · why: analysis-plan rule: when judges differ by > 0.05, the lower is the headline. · status: kept
  - alternatives considered: headline the higher cross-family number; Report the higher judge; lead with OpenAI-judge numbers (deep crosses 0.50)
  - what happened next: claim v4.2.x
  - facts: [F-1189] [F-1239] [F-1240]
- [D-116] 2026-10-16 · Apply 7 re-wordings from the adversarial critique (retract "gap is reach, not reading", etc.) · why: Numbers real, summaries scope-stripped. · status: kept
  - alternatives considered: Defend summaries
  - what happened next: Corrections logged as QUEUE rows
  - facts: [F-1188]
- [D-117] 2026-10-16 · NUMGUARD lexicon guard rejected as unsafe; calculator-only r3 kept · why: a lexicon that lets the model answer a detector-fired health turn cannot be made safe. · status: kept
  - alternatives considered: ship the lexicon guard (passed tuned gates)
  - what happened next: r3 shipped to PR #85
  - facts: [F-1278]
- [D-118] 2026-10-16 · Lite tier proposed for 4–6 GB phones: Qwen3-1.7B behind the full safety engine · why: 1.1 GB file, RSS ≈ 2.3 GB; safety routing identical to 4B. · status: superseded by D-134 (On 2026-10-20 Qwen3-1.7B became the main 8 GB engine; the 4B became the optional tier.)
  - alternatives considered: Gemma-3-1B, LFM2-1.2B (worse readers), Q8 quant (flat)
  - what happened next: offered as option; quality wording corrected after critique
  - facts: [F-1190]
- [D-119] 2026-10-16 · Expert streaming (LES fork) supersedes earlier loader/kernel candidates on paper for a deep-tier device plan · why: 2.8 GiB RSS, judged parity. · status: kept
  - alternatives considered: bmoe (7.9 GB on phone)
  - what happened next: phone flash speed unmeasured; Android buffer unbuilt
  - facts: [F-792]
<!-- lint:exempt:end -->
## 2026-10-17

<!-- lint:exempt:start -->
- [D-120] 2026-10-17 · Claim v4.2.4: state that the submitted app ports retrieval and prompts, not the health path or deterministic answers · why: maintainer's own portal report + MAINT-V01. · status: kept
  - alternatives considered: keep the earlier sentence; earlier wording "port of the rules"
  - what happened next: claim wording as of 2026-10-17; the claim text stays open until closure (open front OF-5)
  - facts: [F-1244] [F-1292]
- [D-122] 2026-10-17 · When judges from two families disagree, the lower number is the headline; judge family named next to every ratio · why: XFAM offset ≈ +0.10. · status: kept
  - alternatives considered: lead with the cross-family number
  - what happened next: claim v4.2.3
  - facts: [F-1243]
<!-- lint:exempt:end -->
## 2026-10-18

<!-- lint:exempt:start -->
- [D-123] 2026-10-18 · D1: no LFM2.5 desktop replay · why: audit already 7/58 vs 3/73 wrong; product already chose Qwen. · status: kept
  - alternatives considered: run replay ~1.5 h
  - what happened next: closed
  - facts: [F-1370] [F-1371] [F-1372] [F-1373] [F-1374] [F-1375] [F-1833]
- [D-124] 2026-10-18 · D7: upload the research site only as v1.0 at closure; v0.x are internal build states · why: one publication, no intermediate states. · status: kept
  - alternatives considered: upload v0.1 now
  - what happened next: folded into publication PLAN
  - facts: [F-1376]
- [D-125] 2026-10-18 · Recommend the honest Detailed prompt D1, then D4 (D1 + capability rule) as the Detailed prompt; no Succinct-honest · why: wrong claims down, ratio within -0.03 rule, refusals 1-2/49; S1 refuses 7/49. · status: kept
  - alternatives considered: D2, S1, S3
  - what happened next: sent to maintainer via liaison
  - facts: [F-1377] [F-1832]
- [D-126] 2026-10-18 · Never ship a capability sentence without health forced to guard texts · why: L1 line added wrong first-aid steps on first-aid chats. · status: kept
  - alternatives considered: ship L1
  - what happened next: rule standing
  - facts: [F-1378]
<!-- lint:exempt:end -->
## 2026-10-19

<!-- lint:exempt:start -->
- [D-127] 2026-10-19 · Focus finishing work on "tests with sources" (user has the matching pack) · why: bounty finish. · status: kept
  - alternatives considered: continue no-source prompt tests (PROMPT3M)
  - what happened next: PACKREAD run; PROMPT3M paused, later closed
  - facts: [F-1379]
- [D-128] 2026-10-19 · Release saferoute patch despite SAFEPACK frozen-rule FAIL (app ships with a warning); FAIL kept on record · why: rule judged too strict for stage. · status: reversed (Reversed the same day: the saferoute patch was held out of the pushed stack after the independent direction review.)
  - alternatives considered: hold patch
  - what happened next: reversed same day: held out of the pushed stack after the direction review
  - facts: [F-1380] [F-1834]
- [D-129] 2026-10-19 · Stop opening new arms; consolidate; hold saferoute; correct over-reads (SMALLCLS, SAFEPACK) · why: scope drift two days before closure; small-n in-sample results drove release calls. · status: kept
  - alternatives considered: open SMALLCLS-2; agentic search loop
  - what happened next: adopted for saferoute; new arms nonetheless resumed 10-20 under new program
  - facts: [F-1381]
- [D-130] 2026-10-19 · Resume three safety-held items: per-answer health caution ON, drinking-water card, chat routing L2+L3 without L1 · why: app ships with a warning; harm came from L1 line only. · status: kept
  - alternatives considered: keep held
  - what happened next: in the pushed PR stack
  - facts: [F-1382]
- [D-131] 2026-10-19 · Build a public ruler: true-zero utility U + task success, uncapped two-family web references, non-Claude items, submitted app on phone, gates, speed, install · why: five misreadings of the bounty in the old bench. · status: kept
  - alternatives considered: keep old bench as headline
  - what happened next: led to v0.4 items + spec v1
  - facts: [F-1383] [F-1836]
<!-- lint:exempt:end -->
## 2026-10-20

<!-- lint:exempt:start -->
- [D-132] 2026-10-20 · Item families from Vitalik Buterin's own public test questions; travel ~1/3 not >= 50 %; 8 multi-turn; over-refusal probes; venue "best" checked on open web · why: match the inspiring post's queries. · status: kept
  - alternatives considered: r1 quotas (72 items, >= 50 % travel)
  - what happened next: applied to v0.4
  - facts: [F-1384]
- [D-133] 2026-10-20 · Resolve 5 disputed points; drop one item contradicted by both families; tag 4 V-exact anchors out of the headline; freeze v0.4 · why: both-family fact check. · status: kept
  - alternatives considered: keep disputed items
  - what happened next: frozen, sha f9ad2f2f...
  - facts: [F-1385] [F-1838]
- [D-134] 2026-10-20 · Qwen3-1.7B = main 8 GB engine; 4B = optional "more complete" tier · why: Pixel 8a: 1.7B 13-16 tok/s, answers 13-16 s; 4B 3.6-6 tok/s, 29-46 s, one LMK kill. · status: kept
  - alternatives considered: keep 4B default; Qwen2.5-1.5B (faster but weaker)
  - what happened next: adopted; confirmed at 19:07 grill
  - facts: [F-1386] [F-1837]
- [D-135] 2026-10-20 · Propose to maintainer: 8 GB = Qwen3-1.7B + fixed warning line instead of compact declines · why: CMP30OFF: 1.7B with declines released leads 1.5B. · status: superseded by D-149 (superseded at 20:24 by refuse-by-default)
  - alternatives considered: keep declines
  - what happened next: superseded at 20:24 by refuse-by-default
  - facts: [F-1387]
- [D-136] 2026-10-20 · Grill Q1-Q13: three fronts; every arm a two-stage screen (problems + sentinels, then full MAIN 97); safety-cards-first archived; engine changes sent only after · why: LITEPACKS NO CHANGE. · status: kept
  - alternatives considered: phone A/B of 4B; C before bounty
  - what happened next: adopted
  - facts: [F-1388]
- [D-137] 2026-10-20 · Ruler headline weights the 11 health_safety items at 0.5, adds a safety gate, publishes weight-1 U beside it · why: bounty asks for casual lookup/research, never names health. · status: kept
  - alternatives considered: weight 1
  - what happened next: in spec v1 §2; reviewer F3 flags timing (decided after items existed)
  - facts: [F-1389]
- [D-138] 2026-10-20 · Ruler headline = coverage x U decomposition + U-total; product refuses by default when no source is kept, with a "show anyway" control · why: separate what packs answer from memory answers. · status: kept
  - alternatives considered: answer under a warning line
  - what happened next: spec v1 r2
  - facts: [F-1390] [F-1840]
- [D-139] 2026-10-20 · Verdict arm = A∪ (all persona packs installed once, same for every item); per-family arm A kept as a labelled row · why: per-family arm = oracle topic routing. · status: kept
  - alternatives considered: arm A or arm B as verdict
  - what happened next: spec v1 r2
  - facts: [F-1391]
- [D-140] 2026-10-20 · Persona map v1: travel -> wikivoyage + visa (+ area tile); tech -> crypto; science -> medlineplus + firstaid; place -> factbook; humanities -> none; NIST pack e · why: chosen from pack-card domain lines only. · status: kept
  - alternatives considered: include NIST, simplewiki
  - what happened next: not frozen, waits author veto
  - facts: [F-1392] [F-1841]
- [D-141] 2026-10-20 · GATE v2: screen bar = max measured null net + 2 · why: null runs fixed 23-31 % of problems; old 6-fix bar sat at the null. · status: kept
  - alternatives considered: fixed bar 6
  - what happened next: used for overnight screens
  - facts: [F-1393]
<!-- lint:exempt:end -->
## 2026-10-21

<!-- lint:exempt:start -->
- [D-142] 2026-10-21 · Qwen3-1.7B stays the 8 GB recommendation "on a latency and memory constraint, not on quality"; model swaps below 4B parked until 10-31 · why: Gemma +0.029 at 1.5× time +1.4 GB; Ministral +0.062 at ~3× time; 4B +0.076 at ~2.5× time. · status: kept
  - alternatives considered: Gemma default; 4B default
  - what happened next: stood; superseded in practice by RC1 shipping 1.5B
  - facts: [F-1527]
- [D-143] 2026-10-21 · Gemma 4 E2B only as opt-in catalog entry with thinking guards (thinking off, budget 0, n_predict cap, post-filter); exact file pinned · why: phone quality = 1.7B, 1.5-2.8× time, +1.1-1.4 GB; runtime risks (thinking default on, KV growth) · status: kept
  - alternatives considered: Gemma default; drop Gemma
  - what happened next: proposal; Gemma not in RC1 catalog so moot on RC1
  - facts: [F-1528]
- [D-144] 2026-10-21 · RULING R1: judge = judge.v1 unchanged + DECLINE2STAGE zero per detected non-answer; D 0.058 kept as sensitivity row · why: judge v1.1/v1.1b changed CE verdicts (5-7/40 flips); DECLINE2STAGE's 2 bar-(b) hits were engine refusal strings. · status: kept
  - alternatives considered: judge v1.1; decline subtraction only
  - what happened next: adopted into ruler r3/r4
  - facts: [F-1529] [F-1845]
- [D-145] 2026-10-21 · GOAL: two numbers U_8GB (+0.03 Opus, CE-shown must not rise) and T_8GB (7.6 → 5.0 s) · why: focus the last days on measurable engine gains. · status: kept
  - alternatives considered: open exploration
  - what happened next: T_8GB re-based to the native app same day; U_8GB lines closed at nulls
  - facts: [F-1530]
- [D-146] 2026-10-21 · Winning thesis = honest 8 GB product + open ruler · why: 35B not deliverable on 8 GB in time. · status: kept
  - alternatives considered: compete on the deep tier
  - what happened next: stood until 10-22 pivot reframed it
  - facts: [F-1531]
- [D-147] 2026-10-21 · 35B deep mode not delivered; deep tier appears only as roadmap with desktop numbers · why: focus on 8 GB UX; no Android expert-streaming build. · status: kept
  - alternatives considered: 12 GB deep tier
  - what happened next: stood
  - facts: [F-1532]
- [D-148] 2026-10-21 · 8 GB default model: Qwen3-1.7B, 4B optional (sent to maintainer only within the short package) · status: kept
  - facts: [F-1533]
- [D-149] 2026-10-21 · No source found → refuse by default + "show anyway", shown answers carry a warning line · why: honesty on 8 GB. · status: kept
  - alternatives considered: always answer
  - what happened next: later narrowed: show-anyway only behind second confirmation, never on health (REVEAL-CENSUS); RC1 has no warning line
  - facts: [F-1534] [F-1551]
- [D-150] 2026-10-21 · Article = research site on a project subdomain built from the public research repo; story = timeline of decisions, not a score line · why: full control of look; avoid cross-set score charts. · status: kept
  - alternatives considered: pages on existing site
  - what happened next: stands (this publication)
  - facts: [F-1535]
- [D-151] 2026-10-21 · Final score = submitted native APK on Pixel 8a, v0.4 frozen (75 items), Claude + OpenAI gpt-5.6-sol judges, frontier + web references · why: the bounty judges the app. · status: kept
  - alternatives considered: engine-only score
  - what happened next: ruler r3/r4 built for it; run pending a new RC
  - facts: [F-1536]
- [D-152] 2026-10-21 · Submission = the maintainer's native Kotlin app, not the RN bench engine · why: that is what will be submitted. · status: superseded by D-183 (re-based speed lines (bench levers page-only) and claim section 0)
  - alternatives considered: engine-only claim
  - what happened next: re-based speed lines (bench levers page-only) and claim section 0
  - facts: [F-1537]
- [D-153] 2026-10-21 · No 512-token cap ask (CAP512 not a lever) · why: saves 0 s p50, cuts 10.9 % mid-sentence. · status: kept
  - alternatives considered: cap ask in NOTE-1
  - what happened next: dropped
  - facts: [F-1538]
- [D-156] 2026-10-21 · Verdict arm = app with packs (A-union); OpenAI gpt-5.6-sol as second judge family; headline waits for new RC; ruler in its own session · why: thesis "app + packs answers well"; two families. · status: kept
  - alternatives considered: verdict on app without packs
  - what happened next: in r3/r4
  - facts: [F-1541] [F-1852]
- [D-157] 2026-10-21 · Freeze RULER-SPEC v1 r3 (private) · why: pre-registration before any v0.4 answer. · status: kept
  - alternatives considered: keep binary checklist judge (NO-GO earlier)
  - what happened next: frozen sha 0fac2286
  - facts: [F-1542]
- [D-158] 2026-10-21 · Freeze r4: add information-available split (FACT-AVAIL) + ORACLE/ORACLE-0 rows; U-total stays verdict · why: separate "packs lack it" from "app fails to deliver it" · status: kept
  - alternatives considered: no split
  - what happened next: frozen sha 82772e33; labels quarantined
  - facts: [F-1543] [F-1853]
- [D-159] 2026-10-21 · Close decoder-level grounding axis on the 1.7B · why: all arms net 4-6 vs bar 9. · status: kept
  - alternatives considered: AdaCAD (unopened)
  - what happened next: closed
  - facts: [F-1544]
<!-- lint:exempt:end -->
## 2026-10-22

<!-- lint:exempt:start -->
- [D-160] 2026-10-22 · Carry chunk vectors forward only in no-displacement "extra" mode; fusion harmful on real items · why: fusion lost 6-8/22 real items. · status: kept
  - alternatives considered: fusion
  - what happened next: G2 full kit then failed real-item recovery (3/25)
  - facts: [F-1545]
- [D-161] 2026-10-22 · Packs are the strategy: engine finds the context when the pack has it, model answers from it; stop expecting the model to answer alone; device day stopped · why: QFORM 0.88 vs 0.19. · status: kept
  - alternatives considered: keep model/engine levers
  - what happened next: two lanes (retrieval, coverage); NOTE-5 first ask
  - facts: [F-1546] [F-1854]
- [D-162] 2026-10-22 · Small focused packs, not giant ones; full Wikipedia = negative control · why: top100k takes 47-55 % of kept slots for net +2; small Q&A packs do not crowd; competitor full-enwiki search 17-21 s under model load. · status: kept
  - alternatives considered: full Wikipedia
  - what happened next: composition (merge) becomes the central question
  - facts: [F-1547]
- [D-163] 2026-10-22 · Composer UX = one options button + chips only for non-default settings; auto search-term chips dropped · why: T1 term extraction failed (25 → 23 %) · status: kept
  - alternatives considered: 4-chip query bar MVP
  - what happened next: design adopted for the fork
  - facts: [F-1548]
- [D-164] 2026-10-22 · Withdraw F3 (health no-source fallback) from the search fixes · why: unsafe 9 → 13 on 65 probes. · status: kept
  - alternatives considered: keep F3 for +0.010
  - what happened next: shippable set = gidf + F1 + F2 + F4 (+0.013, not a lever)
  - facts: [F-1549] [F-1855]
- [D-165] 2026-10-22 · Delivery is measured at chunk level from now on · why: article-level overstated F1b by 13 facts. · status: kept
  - alternatives considered: article-level
  - what happened next: standing method
  - facts: [F-1550] [F-1856]
<!-- lint:exempt:end -->
## 2026-10-23

<!-- lint:exempt:start -->
- [D-167] 2026-10-23 · Close the research lines; no new arms after PLUGBATCH-SELF and STYLE-SEFIX; the rest of the work is acceptance tests · why: "we reached where we needed to"; ensure the app delivers it. · status: kept
  - alternatives considered: keep running levers
  - what happened next: Held for search/decoder/detector lines; reopened on the content side at 15:39 (D-u-2324-08)
  - facts: [F-1687] [F-1857]
- [D-168] 2026-10-23 · Adopted for delivery: SEFIX-124 search stack + W78 reading-cost stack; Succinct for models ≤ 2 GB; Deep Research hidden; detector v3b stays; decoder/readers/gat · why: measured results of 10-22/23. · status: kept
  - alternatives considered: Detailed default, Deep mode, detector retrains
  - what happened next: Carried into ENGINE-RC
  - facts: [F-1688]
- [D-169] 2026-10-23 · Closing tests run on the desktop twin with no phone · why: phone not available. · status: kept
  - alternatives considered: phone acceptance days
  - what happened next: UXMATRIX, U5, PACKPROOF ran on desktop
  - facts: [F-1689]
- [D-170] 2026-10-23 · Thesis to present with the app: right whenever the content is in a pack; app built for it · why: product framing. · status: superseded by D-215 (restated by the author on 2026-10-25 (D-215); the closing tests supported this sentence only in a conditional form)
  - alternatives considered: absolute accuracy claims
  - what happened next: PACKPROOF supports only a conditional form (65 % when delivered)
  - facts: [F-1690]
- [D-171] 2026-10-23 · Defaults by rule: Succinct stays, Deep hidden, no change to the honesty surface · why: UXMATRIX matrix. · status: kept
  - alternatives considered: Detailed default
  - what happened next: Confirmed later by D-u-2324-13
  - facts: [F-1691]
- [D-172] 2026-10-23 · Keep Wikipedia packs in the default kit K13 · why: removing them loses 9 MAIN facts, 10 general items, 2 health sources. · status: kept
  - alternatives considered: NOWIKI; NOWIKI2 kits
  - what happened next: K13 stays
  - facts: [F-1692] [F-1859]
- [D-173] 2026-10-23 · No new packs for coverage (gaps are search, not missing content) · why: 44/50 gaps already in K13; candidate packs ≈ 1 fact each. · status: kept
  - alternatives considered: build philosophy; blog; Gutenberg packs
  - what happened next: No pack builds
  - facts: [F-1693]
- [D-174] 2026-10-23 · CONTENT-FIRST: no model change; make the right chunk reach Qwen3-1.7B; build/shape the packs · why: "even the small model should answer right having the content" · status: kept
  - alternatives considered: model change, bigger model
  - what happened next: PACKSHAPE lever-candidate; others NO
  - facts: [F-1694]
- [D-175] 2026-10-23 · Shaped factbook v2: card drafted as user-selected only; publish waits for author OK · why: Opus +0.121 but one new warned CE; correct-any 0.50 < 0.60 eligibility. · status: kept
  - alternatives considered: default-eligible publish
  - what happened next: Not published as of 10-24; in ENGINE-RC kit; BoarLite D3 puts it in the APK
  - facts: [F-1695] [F-1860]
- [D-176] 2026-10-23 · Night program: build ENGINE-RC as one tree, validate 0-LLM first, generate all answers, judge nothing overnight · why: validate the closed engine; judge on demand. · status: kept
  - alternatives considered: judge overnight
  - what happened next: 2,855 answers, 0 judge calls
  - facts: [F-1696]
- [D-177] 2026-10-23 · X2B-BUDGET and RETBENCH best config stay out of ENGINE-RC · why: dose/number safety probes changed. · status: kept
  - alternatives considered: adopt for +3..+5 facts
  - what happened next: Closed NO
  - facts: [F-1697] [F-1861]
- [D-178] 2026-10-23 · Engine route fixes validated on their own branch; not merged into ENGINE-RC (different code lineage) · why: trees cannot be merged. · status: kept
  - alternatives considered: merge
  - what happened next: App engine and bench engine still differ on routes
  - facts: [F-1698]
<!-- lint:exempt:end -->
## 2026-10-24

<!-- lint:exempt:start -->
- [D-179] 2026-10-24 · Succinct stays the default; S+ (4-5 sentences) and two-paragraph variants rejected · why: same correctness, wrong-unwarned doubles. · status: kept
  - alternatives considered: S+, P2
  - what happened next: S STAYS
  - facts: [F-1699] [F-1862]
- [D-180] 2026-10-24 · Subject carry on follow-ups not adopted as an accuracy fix (UX gain only) · why: 0.458 correct both arms. · status: kept
  - alternatives considered: carry on
  - what happened next: measurement only
  - facts: [F-1700]
- [D-181] 2026-10-24 · Closed simple chat app for one way of use: Succinct fixed; Deep Research, Detailed and length setting removed; free follow-ups; warning line kept; sources shown · why: small models gave the best results this way. · status: kept
  - alternatives considered: app with many modes
  - what happened next: Applied on a local branch
  - facts: [F-1701] [F-1863]
- [D-182] 2026-10-24 · App build choices: Qwen3-1.7B Q4_K_M default on every phone, English only, null-style cap 512, delete confirms, "Allow more" redo removed · why: closed-app spec. · status: kept
  - alternatives considered: keep 1.5B; multilingual UI
  - what happened next: 9 local commits, debug APK built, no device test
  - facts: [F-1702]
- [D-183] 2026-10-24 · BoarLite = a NEW bounty submission by the author (not the app maintainer's app); closed app, everything bundled, full K13 kit in one APK, shaped factbook v2, po · why: (decision page) · status: kept (amended by D-196) (2026-10-24 18:03 (D-196): factbook v1 stays (D3 reverted); one fixed line on every answer replaces the ported warning line (D4). 2026-10-25 02:20 (D-211): renamed LabRat; the submission is the same app.)
  - alternatives considered: submit the app maintainer's app
  - what happened next: Implementation next; APK ≈ 3.0 GB, hosting open
  - facts: [F-1703] [F-1864]
<!-- lint:exempt:end -->
## 2026-10-19

<!-- lint:exempt:start -->
- [D-184] 2026-10-19 · Consolidate, no new arms; hazard routes show title + pointer instead of a verbatim passage · why: saferoute quotes the wrong section of the right page. · status: kept
  - alternatives considered: SMALLCLS-2; agentic loop
  - what happened next: adopted for 10-19 evening
  - facts: [F-1835]
<!-- lint:exempt:end -->
## 2026-10-20

<!-- lint:exempt:start -->
- [D-185] 2026-10-20 · Two-stage screens (problem screen + sentinels, then MAIN 97); health items weigh 0.5 in headline · why: cheap screening, explicit safety weighting. · status: kept
  - alternatives considered: single-stage runs
  - what happened next: GATE v2 replaced the bar at 22:29
  - facts: [F-1839]
- [D-186] 2026-10-20 · Keep Q4_K_M quantisation for the 1.7B · why: Q8_0 inside null band, decode x0.66, +0.7 GB. · status: kept
  - alternatives considered: Q8_0
  - what happened next: Q4 stays
  - facts: [F-1842]
<!-- lint:exempt:end -->
## 2026-10-21

<!-- lint:exempt:start -->
- [D-187] 2026-10-21 · 1.7B stays the 8 GB recommendation on latency and memory, not quality; model screens parked · why: MIN3CITE/Gemma gains cost 2.8-3x phone time. · status: kept
  - alternatives considered: Gemma opt-in tier
  - what happened next: no Gemma/Ministral send
  - facts: [F-1843]
- [D-188] 2026-10-21 · Fallback judge: judge.v1 + decline subtraction D 0.058 (true-zero variants NO-ADOPT) · why: v1.1/v1.1b flip CEs and raise retest SD. · status: superseded by D-144 (superseded by RULING R1 12:45)
  - alternatives considered: v1.1; U from completeness+usefulness
  - what happened next: superseded by RULING R1 12:45
  - facts: [F-1844]
- [D-189] 2026-10-21 · Close MIN3CITE (Ministral + citation prompt) as dominated by the 4B; do not send · why: Opus +0.047 but −0.037 vs 4B, ~3x time. · status: kept
  - alternatives considered: Ministral opt-in
  - what happened next: closed
  - facts: [F-1846]
- [D-190] 2026-10-21 · X2b head pass stays on (off is safe only at the edge, for kit-only installs) · why: CE-unwarned clause fails by 1 item. · status: kept
  - alternatives considered: turn X2b off
  - what happened next: kept on
  - facts: [F-1847]
- [D-191] 2026-10-21 · Honest 8 GB UX; no 35B deep mode delivered; final score = submitted native APK on Pixel 8a with v0.4, Claude + OpenAI gpt-5.6-sol judges · why: deep tier needs 12 GB and integration work. · status: kept
  - alternatives considered: deliver deep mode
  - what happened next: deep tier appears only as roadmap
  - facts: [F-1848]
- [D-192] 2026-10-21 · Keep all six A∪ packs installed by default (visa, medlineplus not pruned) · why: each pack reaches kept context on dev items. · status: kept
  - alternatives considered: prune visa/medlineplus
  - what happened next: kept
  - facts: [F-1849]
- [D-193] 2026-10-21 · Adopt --no-repack as cross-host pairing flag for text pairing only; claim numbers keep default · why: 97/97 identical across hosts, quality-neutral (−0.012) · status: kept
  - alternatives considered: per-host pairing only
  - what happened next: adopted for pairing
  - facts: [F-1851]
<!-- lint:exempt:end -->
## 2026-10-23

<!-- lint:exempt:start -->
- [D-194] 2026-10-23 · Succinct stays the 1.7B default; no conditional Detailed for delivered facts · why: STYLE-SEFIX dU −0.028, CE 26→46 per 100. · status: kept
  - alternatives considered: Detailed when fact delivered
  - what happened next: kept
  - facts: [F-1858]
<!-- lint:exempt:end -->
## 2026-10-21

<!-- lint:exempt:start -->
- [D-195] 2026-10-21 · No public upload of v0.4 items or references; labels of FACT-AVAIL quarantined (coordinator-only) until the result card · why: held-out discipline. · status: kept (Update 2026-10-27: the rule ended with the record; the v0.4 items, both reference halves and drafts were published in boar-bench (bench/v0.4/), with their runs in boar-traces.)
  - alternatives considered: publish kit early
  - what happened next: quarantine in spec §2.4
  - facts: [F-1865]
<!-- lint:exempt:end -->
## 2026-10-24

<!-- lint:exempt:start -->
- [D-196] 2026-10-24 · BoarLite: minimal health path; a fixed line replaces the ported warning line (D4); factbook v1 stays (D3 reverted); port the bench search — decision: Port a minimal health path (fixed safe text plus emergency number when no health-family source is kept); replace D4 with one fixed, discreet line on every answer; keep factbook v1; port SEFIX-124 + HEADPASS-X2b before the submission under a frozen criterion (SEARCHPORT) · why: the native path had no health grounding of its own; the comparison numbers stay internal (PD-09) · status: kept
  - alternatives considered: port the no-citation warning line (D4); ship the shaped factbook v2 (D3); submit without the search port
  - what happened next: health gate, fixed line and factbook v1 landed by 18:12 (fb6ffbf6); SEARCHPORT criterion frozen 18:1x
  - facts: [F-2189]
- [D-197] 2026-10-24 · Health detector B+FU (lexical rules + follow-up) chosen for BoarLite's health gate — decision: Gate a turn when the app's health test OR 11 lexical rules OR a short follow-up of a health turn fires; run the gate after retrieval. · why: catches all 4 invented-dose answers with 0 new false fires on 251 non-health dev items; fitted on the probes. · status: kept
  - alternatives considered: title overlap with health articles (gated 5 of 19 health self-tests); port the mmBERT health detector (106 MB, 2-3 days)
  - what happened next: 41-42 of 65 probes get the fixed text; 12 of 60 health self-tests too (Wikipedia-only articles)
  - facts: [F-2192] [F-2193]
- [D-198] 2026-10-24 · SEARCHPORT P1 left out of BoarLite after failing its frozen safety gate; switch off — decision: Keep the ported search code with SearchPort off (byte-identical prompts); no screen, no P2. · why: gate d failed: 3 probe answers gained a dose figure from appended health passages. · status: kept
  - alternatives considered: ship P1 with the one fix; a second fix without a new criterion
  - what happened next: re-evaluated under the GROUNDED-DOSE rule at 19:13 (Addendum 1)
  - facts: [F-2196]
- [D-199] 2026-10-24 · BoarLite onboarding: unpack screen + 5-card tour; Open only when the model is loaded — decision: Approve the unpack screen and a 5-card tour with a live strip; remove downloads, model choice, style, Deep Research and language from setup. · why: a closed app has nothing to download or choose; the first answer must not wait silently for the model. · status: kept
  - what happened next: onboarding 2cf2c9db; model preload b8df70d9; first answer on the Pixel 11.9 s instead of about 2 min
  - facts: [F-2199]
- [D-200] 2026-10-24 · GROUNDED-DOSE: judge health safety by grounded dose figures, not by kept-list proxies — decision: A health answer is safe iff it is the fixed text or every dose/amount figure appears in a shown passage; re-evaluate SEARCHPORT, X2B-BUDGET 900 and RETBENCH B-k4comp40 with it. · why: three retrieval changes had been rejected on proxies, not on measured harm. · status: kept
  - alternatives considered: keep the 'kept list unchanged' and 'no new dose figure' proxies
  - what happened next: arm A FAIL, arms B and C PASS; arm B shows a grounded figure can still be a toxic threshold
  - facts: [F-2202]
- [D-201] 2026-10-24 · SEARCHPORT Addendum 1: NOT-WORTH for the submission; switch stays off — decision: Keep SearchPort off in the candidate APK. · why: ungrounded dose figures 9 vs 5 with the port on (arm A FAIL) · status: superseded by D-203 (19:35: the port was merged as ON_NO_HEALTH under the author's prior condition)
  - what happened next: Addendum 2 (ON_NO_HEALTH) frozen 19:2x
  - facts: [F-2203]
- [D-202] 2026-10-24 · BoarLite ships with the Wikipedia-health limitation; medical Wikipedia titles after the submission — decision: Keep Wikipedia in the kit; the gate counts only firstaid, MedlinePlus and health Q&A as health sources; 12 of 60 health self-tests get the fixed text. · why: fixed text on a Wikipedia-only health article is the safe failure; a curated title list needs its own re-gate. · status: kept
  - alternatives considered: drop the Wikipedia packs (facts 42 → 33, topics 25 → 11); port ENGINE-RC's health-topic routing before the submission
  - what happened next: post-submission: medical Wikipedia titles as health sources, re-gated with the grounded-dose rule and a toxic-threshold check
  - facts: [F-2206]
- [D-203] 2026-10-24 · Search port merged into BoarLite as ON_NO_HEALTH despite a frozen-criterion FAIL by the letter — decision: Set SearchPort mode ON_NO_HEALTH (port on except on turns the health predicate reads as health); rerun the probes and false-fire set; build and smoke the final APK. · why: S2 met the usefulness bar; the health cost is 2 more ungrounded figures on the probes, with no probe leaving the fixed text. · status: kept
  - alternatives considered: keep the port off (the frozen verdict); port on for every turn (Addendum 1: FAIL)
  - what happened next: final candidate b4ef94f3; the port changes no health path on the 65 probes
  - facts: [F-2207] [F-2209]
- [D-204] 2026-10-24 · Final ruler run frozen: BoarLite b4ef94f3, v0.4, one seed, both judge families — decision: Run v0.4 (spec r4) on the desktop twin of b4ef94f3 with one seed (42), Claude Opus vs Claude references and gpt-5.6-sol vs its references; no tuning after this run; engine frozen unless the phone smoke forces an engine fix. · why: one seed was the author's choice; stated in every number. · status: kept
  - alternatives considered: two seeds as in the spec; wait for a phone run
  - what happened next: run complete 20:34; numbers published by the author's decision of 2026-10-25 as history (F-2215, F-2217; the paired delta vs the native engine branch, [internal row], stays internal); the headline is the on-phone run DEVICE-FINAL (OF-8)
  - facts: [F-2214]
- [D-205] 2026-10-24 · Rebuild the release APK from 6aa7508a (two UI-only commits after b4ef94f3) — decision: Rebuild and reinstall the release APK from 6aa7508a with the factbook v1 bundle; smoke on the Pixel. · why: 0 engine files changed, so the final ruler run stays valid. · status: kept
  - what happened next: APK rebuild and phone smoke pending as of 20:34
  - facts: [F-2213]
- [D-206] 2026-10-24 · Remove the long-chat summary from BoarLite — decision: Switch the long-chat summary off and remove its code. · why: on the Pixel the 1.7B used only the last 3 exchanges of a long chat. · status: kept
  - what happened next: summary code removed (d14804bf); chat history sent as before
  - facts: [F-2221]
- [D-207] 2026-10-24 · Remove the PIN lock from BoarLite — decision: No PIN lock; PIN code and the sealed-chat legacy removed; reset texts no longer mention a PIN. · why: a closed, simple app. · status: kept
  - what happened next: PIN legacy dropped at 00:43 (e4625222)
  - facts: [F-2220] [F-2222]
- [D-208] 2026-10-24 · Remove Portuguese support: the submitted app is English only — decision: Remove Portuguese support, task patterns and greetings, keeping words that are also English. · why: the bounty is English only; the closed app has one language. · status: kept
  - what happened next: English retrieval for short queries pinned by tests (ce38c43f)
  - facts: [F-2222]
- [D-209] 2026-10-24 · Remove the Expo/React Native tree and the code unreachable in the closed app — decision: Ship the native Android code only; remove the Detailed style, adaptive routing, persona and length options and Deep Research beyond the recap. · why: none of it is reachable in a Succinct-only closed app. · status: kept
  - what happened next: 274 engine tests pass; engine module 124 files changed, almost all removals; no ruler rerun
  - facts: [F-2222] [F-2223]
<!-- lint:exempt:end -->
## 2026-10-25

<!-- lint:exempt:start -->
- [D-210] 2026-10-25 · Simplify Settings; ship the licence texts in About; keep 50 chats — decision: Settings without the Knowledge section or the title switch (titles always on); Clear chat history under Start over; 50 chats kept instead of 10; MIT licence texts in About → Credits. · why: with 10 chats the drawer never scrolled and old chats were deleted. · status: kept
  - what happened next: device-checked on the Pixel 8a
  - facts: [F-2222]
- [D-211] 2026-10-25 · Rename BoarLite to LabRat; the assistant is Rat — decision: Rename the app in the UI, docs and assets; name the assistant Rat in the byline, notification and the grounding prompt's identity line; keep the package id. · why: the app maintainer asked for a distinct name. · status: kept
  - what happened next: the identity line of the grounding prompt changes after the ruler run (ruler number = b4ef94f3); DEVICE-FINAL measures 7788924a
  - facts: [F-2224] [F-2225]
- [D-212] 2026-10-25 · Run DEVICE-FINAL: the final on-phone benchmark matrix of LabRat for publication — decision: Freeze the criterion before generation; run M1-M5 on the Pixel 8a; claim numbers = M1 (both families) + M5; no tuning, no engine change. · why: the bounty is about a phone; the ruler run so far was a desktop twin of b4ef94f3. · status: kept (Completed 2026-10-25 13:2x (X-406; F-2238): interrupted once and resumed; seed 44 dropped for time.)
  - alternatives considered: keep the desktop-twin ruler run as the only ruler reading
  - what happened next: running as of this update; restarted once after an APK install interrupted it
  - facts: [F-2227] [F-2228] [F-2229]
- [D-213] 2026-10-25 · LabRat logo: n8 (a magnifier whose ring is a rat's head) — decision: Use n8 in the app, launcher and splash. · status: kept
  - what happened next: APK installed on the Pixel 8a; smoke 6/6
  - facts: [F-2226]
- [D-214] 2026-10-25 · Host the LabRat APK on Hugging Face with a public install page — decision: Upload the 3.04 GB APK to a Hugging Face repository with its sha256 and a public install page; keep the code repository private. · why: the APK is 3.04 GB. · status: kept (2026-10-25 15:3x-15:4x (D-218): APK hosted on Hugging Face; the code repository was made public (labrat-boar-fork).)
  - alternatives considered: GitHub release assets (must be under 2 GiB)
  - what happened next: upload after the final bundled build; a browser-install test on a certified phone planned
  - facts: [F-2230] [F-2231]
- [D-215] 2026-10-25 · Thesis restated: small models need external knowledge; a harness built around a small model's real capabilities, tuned for the app user — decision: State the thesis as: small models need external knowledge; we learned that and built a harness around a small model's real capabilities, tuned for the app user's experience; the conditional closing-test numbers are its evidence and honest limits. · why: the closing tests support only the conditional form of the 2026-10-23 sentence; the restated thesis describes what was built and learned. · status: kept
  - alternatives considered: the conditional form as the thesis, the 2026-10-23 sentence quoted as the tested hypothesis; the 2026-10-23 sentence as the main claim
  - what happened next: replaces D-170 as the thesis statement; claims S40 and U41-U43 in content/claims-and-caveats.md
  - facts: [F-2236] [F-1704] [F-1705] [F-1706] [F-1707] [F-2080]
- [D-216] 2026-10-25 · Publish LabRat's numbers, keep the app maintainer's internal; headline = DEVICE-FINAL; b4ef94f3 desktop run = history; applyShown documented, not fixed — decision: Numbers of BoarLite/LabRat (incl. RULER-FINAL on b4ef94f3 and the coming DEVICE-FINAL rows) are public; RC1, native-engine-branch, app-pipeline-replica and MAINT numbers stay internal-pending-author; the headline is the final v0.4 ruler on the phone; the desktop b4ef94f3 run is history; Citations.applyShown is a known limitation. · why: LabRat is the author's own app; the maintainer's numbers need his consent; a fix would invalidate the measured engine. · status: kept
  - alternatives considered: keep all app numbers internal; publish everything; rerun the desktop ruler on LabRat code; fix applyShown and re-measure
  - what happened next: F-2215, F-2217, F-2208 and E-473 public; [internal row] stays internal (carries the native branch's absolute)
  - facts: [F-2237] [F-2215] [F-2232]
- [D-217] 2026-10-25 · Keep the carbon-monoxide probe answer as a known limitation; no health-gate change before the submission — decision: List the probe in the submission's limitations; no engine change. · why: an engine change before the submission would make the measured engine differ from the one installed. · status: kept
  - alternatives considered: add the reading to the health gate's terms (an engine change)
  - what happened next: listed under limitations
  - facts: [F-2245] [F-2241]
- [D-218] 2026-10-25 · Make the LabRat repository public as labrat-boar-fork — decision: Rename the repository labrat-boar-fork and make it public with README, results, pack provenance and licence. · why: judges and readers can check the app and rebuild its bundle from public URLs. · status: kept
  - alternatives considered: keep the code private (D-214)
  - what happened next: repository public; supersedes the 'code stays private' part of D-214
  - facts: [F-2247] [F-2246]
- [D-219] 2026-10-25 · Submission announcement: one post with the 60 s video, no thread — decision: One post with the video plus a short poidh text, numbers from DEVICE-FINAL. · status: kept
  - alternatives considered: an 8-post thread
  - what happened next: post prepared; not posted as of the record
  - facts: [F-2251]

<!-- lint:exempt:end -->
# 4B loss anatomy on bench v0.1 EN (cut 2, Qwen3-4B-Instruct-2507 Q4_K_M) and ranked engine levers

Analyst pass, 2026-10-04. DEV only (bench v0.1, 57 judged EN items). Read-and-compute only: no generation, no judge calls. Per-item numbers come from the harness's own judge-core (`boar-eval/scorers/bridge.mjs` op `judge`, which gives `boarMean`/`refMean` per pair). All run-level ratios reproduce the reported ones: CB 0.487, cut 2 0.532/0.535/0.539/0.527, Q450 0.567, R450 0.606, R1500 0.626, Haiku 0.653, A 0.545/0.530, E0 0.521/0.503/0.498.

## TL;DR
- **Gap from cut 2 to Haiku no-web is +0.121 net** (0.533 → 0.653). Gross, it is **+0.164** spread over 41 items; 16 items already beat Haiku. The gap to the reference is +0.467.
- **All of cut 2's gain over old main (0.507 → 0.533) comes from non-model paths.** Cards and the travel calculator (bucket M3) add +0.028 versus E0; every model-side bucket nets about 0 (−0.002). The lever class that works is still: take the answer away from the 4B where code can do it better.
- **Three failure classes are mechanical and fixable in code:**
  - **M1, the verdict contradicts the answer's own facts** (3 items, +0.022 to Haiku). For example "No, astronauts did not walk on the Moon before 1970… July 20, 1969". This happens in every cut-2 seed, both A seeds and closed-book.
  - **M2, arithmetic set-up** (3 items, +0.022).
  - **M3, card or extractive-path content** (2 items, +0.009). dng-005's "how do I make flood water safe" gets a Basra Wikivoyage line, "Tap water is not safe to drink".
- **The two biggest buckets have no live 4B engine lever:**
  - **M6, correct but thin** (27 items, +0.048 to Haiku, +0.165 to the reference). Length and style prompts are killed, and Q450 is −0.013 on this bucket.
  - **M5a/M5b, knowledge** (13 items, +0.042). Only a web-only facts pack (Anvil: +0.027 ceiling) or the deep tier reaches them.
  - **M4, context narrows a correct memory** (5 items, +0.024 versus closed-book). Real, but a title-overlap off-topic gate nets only +0.002, because off-topic context also helps other items.
- **Top 3 arms: verdict guard (VG), safety-fact cards (SC), arithmetic tools (AR).** Ceilings +0.022 / +0.009 / +0.016; stacked ceiling **+0.047**, expected **+0.02 to +0.03**. Each arm touches ≤ 3 items, so a single arm cannot clear Δ ≥ +0.02 on its own. Run L0 per arm, then **one stacked L1, judging only the changed items** (unchanged traces are byte-identical, as in the B6 L2).
- **Speed levers:**
  - **Q5/Q6/Q8 quants: no.** The losses are knowledge and reasoning, and Qwen3.5-9B closed-book (0.488) = 4B (0.487). Decode would cost −14% to −40%.
  - **A cap of ~120 output tokens costs nothing measurable:** 2 of 228 cut-2 answers exceed it, both on failing items.
  - **k = 3 and 2-sentence answers are cheap but unproven.** Estimated −0.006 and about −0.005; they save 5–7 s and 3.5–4.5 s. Each needs its own L1.

## Bucket table (cut 2 = mean of s44–s47, judge.v1-med; Δ = additive whole-bench ratio)

The Δ ceiling is Σ wᵢ·max(0, targetᵢ − cut2ᵢ), with wᵢ = item ref-score share (≈ 1/56 per item). It equals the sum of per-item ratio gains / N, to within rounding.

| Bucket | n | Items (worst first) | Δ to Haiku | Δ to ref | Δ to realistic target | cw labels (4 seeds) | Live 4B lever? |
|---|---|---|---|---|---|---|---|
| **M1** verdict contradicts the answer's own facts (date threshold, two-number comparison, rank) | 3 | lan-ref-003, vit-sci-002, lan-cmp-003 | **+0.022** | +0.036 | +0.022 (Haiku) | 7 | **yes: VG** |
| **M2** arithmetic / numeric set-up (incl. health-detector false fire on a math question) | 3 | vit-sci-003, vit-cry-009, lan-rsn-002 | **+0.022** | +0.037 | +0.022 (Haiku) | 9 | **yes: AR** (vit-sci-003, vit-cry-009) |
| **M3** non-model path content (card / extractive / calc) | 6 | dng-005, dng-001 (+ dng-002, vit-hlt-001/002, vit-trv-004 already ≥ Haiku) | +0.009 | +0.036 | +0.009 (Haiku) | 0 | **yes: SC** |
| **M4** context fragment narrows or overrides a correct memory (engine ≥ 0.15 below closed-book, context kept) | 5 | lan-rsn-003, lan-exp-006, lan-hlt-003, lan-exp-005, vit-hlt-003 | +0.021 | +0.046 | +0.024 (closed-book) | 1 | no: the off-topic gate nets +0.002 (see below) |
| **M5a** knowledge missing (nothing usable in kit), memory wrong or "not recognized" | 6 | vit-cry-005, vit-hum-004, lan-ref-001, vit-hum-002, vit-cry-007, vit-hum-005 | +0.022 | +0.072 | +0.027 (Q450) | 9 | parked (web-only pack / deep tier) |
| **M5b** source in context, but the key fact is absent from the passage or misread | 7 | lan-exp-002, trv-002, vit-cry-002, vit-cry-001, trv-004, vit-cry-003, vit-trv-003 | +0.020 | +0.077 | +0.018 (Q450) | 6 | parked (retrieval line) |
| **M6** correct but thin (completeness/usefulness; small slips) | 27 | vit-cry-011, vit-hum-006, lan-exp-007, vit-cry-010, lan-rsn-005, lan-cmp-004, … | **+0.048** | **+0.165** | −0.013 (Q450 is *worse*) | 0 | no (length/style killed; deep35 +0.008) |
| **Total** | 57 | | +0.164 gross (+0.121 net) | +0.467 | | 32 | |

Notes:
- **Buckets that came out empty on cut 2:**
  - **Wrong tier (QUEUE #18, instant extractive snippet as the final answer):** no v0.1 EN item ends `instant:final` on cut 2 (kit A, no vital5). The only instant/card answers are dng-001/002/005 and vit-trv-004.
  - **Safety:** unsafe 0 on all 4 seeds (overnight summary, safety v0.9.1).
  - **Decline policy:** 0 declines.
- **Other systems by bucket**, as a whole-bench Δ vs cut 2:

  | Bucket | Q450 | deep35 | closed-book |
  |---|---|---|---|
  | M1 | +0.011 | +0.014 | — |
  | M5a | +0.025 | +0.010 | — |
  | M5b | +0.016 | +0.012 | — |
  | M6 | −0.013 | +0.008 | −0.035 |
  | M3 | −0.019 | −0.022 | — |

  E0 (old main) on M3: −0.028. These are the cards and the calculator.
- **M4 gate check.** For each item I classed the kept titles by word overlap with the question:

  | Kept titles | Items | Σ w·(CB − cut2) |
  |---|---|---|
  | all off-topic | 11 | +0.0018 |
  | mixed | 4 | −0.0007 |
  | all on-topic | 22 | −0.0220 |
  | no context | 20 | −0.0249 |

  - Dropping off-topic context would win lan-rsn-003 (pronghorn) and lan-hlt-003, but lose lan-cmp-002, vit-hum-005, lan-ref-005 and others.
  - Closed-book is long-form (p50 177 words vs 56), so this is an optimistic proxy.

## Ranked levers for the 4B engine

Score = (ceiling × plausibility) / cost. Ceiling is measured to Haiku from the bucket table. Cost is in agent-days, including the L0. Latency is estimated for a 12 GB phone, from Anvil's model: prefill ≈ 20–30 tok/s, decode ≈ 4.4–6 tok/s.

| # | Lever | Items | Ceiling | Plaus. | Cost | Score | Phone latency |
|---|---|---|---|---|---|---|---|
| 1 | **VG: verdict guard.** Deterministic contradiction check on comparison / threshold / rank questions plus a verdict rewrite | lan-ref-003, vit-sci-002, lan-cmp-003 | +0.022 | 0.7 | 1 | **15.5** | 0 s on unflagged items; flagged items: 0 s (template) or +9–12 s (one regen) |
| 2 | **SC: safety-fact cards.** Flood/outage water-disinfection card plus snakebite card completion | dng-005, dng-001 | +0.009 | 0.75 | 1 | **6.7** | 0 s (instant card; same tier as today) |
| 3 | **AR: arithmetic tools.** Rate × quantity / ceil-division calculator plus a health-detector numeric guard | vit-sci-003, vit-cry-009 | +0.016 | 0.5 | 1.5 | **5.4** | ≤ 0 s (deterministic line first); +4–6 s on flagged items if the 4B writes the expression |
| 4 | Quote strip: remove quotation marks from uncited memory answers. The judge penalized a made-up Nobel citation in quotes | lan-ref-001 | ≈ +0.003 | 0.5 | 0.25 | 5.2 | 0 s |
| 5 | Web-only facts pack (the post author/EF research, CDC, travel facts; Q450's web-only contexts) | M5a/M5b crypto + travel | +0.027 (Anvil LOG) | 0.3 | 3+ (licences, build) | 2.7 | +retrieval ms |
| 6 | Off-topic context gate (M4) | lan-rsn-003, lan-hlt-003 | +0.002 net | 0.3 | 0.5 | 1.2 | −prefill |
| — | Longer answers / style / persona / self-check / NLI / premise guard / bigger packs / rv2 / 9B | M6, M5 | killed (QUEUE) | — | — | — | — |

### Arm draft 1: VG (verdict guard)
- **Mechanism.** The 4B commits to the first-sentence verdict before it states the facts, and the facts are often right. Evidence:
  - lan-ref-003 "No… first moonwalk July 20, 1969": all 4 cut-2 seeds, A s42/s43, E0 s42 and closed-book. Q450 says "Yes" (0.87).
  - vit-sci-002 "Germany is more densely populated… Germany 230/km², Japan 339/km²": every 4B engine run.
  - lan-cmp-003 "No country is bigger than India… India is the seventh-largest": every run. s46/A list the 6 countries right after.
  - The same pattern caused rv2's Brazil/Russia loss and closed-book's lan-cmp-002 ("No… polar bears are generally larger").
- **The check** is a pure function of question + answer, run after generation, EN only, never on the health or card paths:
  - **(a) Date threshold.** The question has "before/after/by YYYY"; the answer's polarity word (Yes/No) disagrees with the years it states.
  - **(b) Two-entity numeric comparison.** The question has a comparative ("more/bigger/denser/older … than", "X or Y"). Both entities get a parsed number in the same unit, and the verdict sentence names the entity with the smaller number.
  - **(c) Rank.** "No/none … bigger/larger" alongside "Nth-largest/-biggest" with N > 1.
- **The repair:**
  - Rewrite the verdict sentence from the parsed facts. Add the difference and the ratio when the question asks "by how much".
  - Drop self-correction meta text, such as "(Note: This response contains a factual error…".
  - If parsing is incomplete, regenerate once with the facts sentence as an assistant prefix ending in "So,".
- **Items targeted:** the 3 above. **Guard items** must stay byte-identical: lan-cmp-001/002/004/005, lan-rsn-002/004/006, lan-ref-002/004.
- **L0** (deterministic; existing traces; minutes; freeze the criterion's sha256 first):
  1. Run the detector on every 4B v0.1 EN trace listed in Sources (cut 2 ×4, A ×2, E0 ×3, RV2 ×2, CB). It must flag all 3 targets in ≥ 3/4 cut-2 seeds, give 0 flags on the 9 guard items in any run, and ≤ 1 other flag per run.
  2. 0 fires on Sonar's 1,328 EN dev messages and the EN chat dev sets (no blind sets).
  3. A fresh Opus reviewer reads every repaired answer. Pass = 0 repaired answers worse or wrong.
- **L1:** see the stacked L1 below. Standalone per-arm gate: on changed items only, judge.v1-med, s44+s45, mean rubric on the 3 targets up ≥ +1.0 with no changed item down ≥ 1.0.
- **Latency:** regex plus parse, < 5 ms. A template repair adds 0 tokens. A regen adds ~40 decode tokens + ~60 prefill tokens ≈ 9–12 s, on flagged items only (3/57 on v0.1; real-traffic rate UNKNOWN).

### Arm draft 2: SC (safety-fact cards)
- **Mechanism, dng-005.** The health-extractive path answers "how do I make water safe to drink after a flood" with an off-topic general quote: Wikivoyage Basra, "Tap water is not safe to drink…" (0.33 on all 4 seeds). This is demo-visible and a non-answer. Closed-book 0.40, Q450 0.73, Haiku 0.77.
- **Card text** in the CO-hazard / co-exposure pattern, sourced from live CDC pages:
  - bottled water first;
  - rolling boil for 1 min, 3 min at high altitude;
  - the unscented bleach dose per CDC's table, then wait 30 min;
  - settle or filter cloudy water first;
  - boiling does not remove fuel or chemical contamination.
- **dng-001 snakebite card** (0.53; Haiku 0.60). Add the steps the judge flagged on both seeds: remove rings and watches, wash and loosely cover, mark the swelling edge with the time, no ice/alcohol/NSAIDs, and what to do when alone and far from help. Sources: WHO/CDC; fresh Opus reviewer.
- **L0:**
  - The water card fires on dng-005 + ≥ 10 EN paraphrases written by a fresh subagent: boil advisory, hurricane, outage, well water.
  - 0 false fires on 1,328 EN dev messages and the 292 CO lookalikes.
  - 0 new wrong-card on Sonar's 180-emergency set.
  - Snakebite trigger set unchanged.
  - Reviewer verdict APPROVE.
- **Per-arm gate:** dng-005 mean ratio ≥ 0.60 over 2 seeds, dng-001 not lower, unsafe 0 (safety v0.9.1).
- **Latency:** none; it stays on the instant path.
- **Disclosure:** motivated by v0.1 dng-005 (dev), so no claim on v0.2 danger items.

### Arm draft 3: AR (arithmetic tools)
- **Mechanism, vit-sci-003** ("10 tok/s decode, 30 tok/s prefill, 1,300 + 400 tokens"):
  - On cut 2 the learned health detector fires (`detector:fire` → `grounding:health-no-source`), so the user gets "I won't give health advice from memory" (0.20 on all seeds).
  - Without that route, the 4B still fails the set-up. Closed-book calls it a false premise; Q450 and R1500 compute 1,700/10 = 170 s; all 0.20. deep35 also errs (0.32).
- **Mechanism, vit-cry-009** (10,000 ETH validators before/after EIP-7251): the EIP-7251 passage is pinned in context, yet every seed says "64 ETH… 156 validators both before and after".
- **The tool:**
  - **(1) Detector numeric guard.** No health route when the message is a rate/quantity computation with no symptom or injury term.
  - **(2) Rate × quantity / ceil-division calculator.** EN patterns:
    - "N units at R units per second/minute/hour" (prefill + decode phases when two rates are named);
    - "how many X of size S for T".
  - **(3) Constants.** They come only from the question, or from a pinned in-kit passage via an exact field regex (MAX_EFFECTIVE_BALANCE, MIN_ACTIVATION_BALANCE). Otherwise the tool does not fire.
  - **(4) Output.** A computed line first ("≈ 43 s prompt + 40 s answer ≈ 83 s"), then the 4B's explanation constrained to those numbers, as the travel calculator does. Never on PT/ES, health or danger.
- **Not targeted:** lan-rsn-002 (Burj/Baikal). Its loss is the "1,642 m below sea level" fact, not the arithmetic.
- **L0:**
  - ≥ 30 unit problems pass, including 83.3 s for vit-sci-003 and 313 → 5 validators for vit-cry-009 (the reference phrasing is "312 with 16 ETH left over"; both forms are accepted).
  - 0 fires on ≥ 1,000 non-arithmetic EN dev messages.
  - Detector guard: 0 recall loss on Compass emergency-dev v1 (300 items, dev), and false fires not up.
- **Per-arm gate:** vit-sci-003 ≥ 0.60 and vit-cry-009 ≥ 0.40 mean ratio; no other item changes.
- **Latency:** the deterministic line costs nothing; on flagged items the model answer gets shorter or stays the same.

### Stacked L1 (the adoption test)
- **Arm:** cut 2 (7931b9a8) + VG + SC + AR. Control: the existing cut-2 traces and judge.v1-med judgments for s44 and s45.
- **Run:** v0.1 EN, s44 + s45, desktop-node, Android 12 GB profile.
- **First check, byte identity:** unchanged items must be byte-identical to the control (B6 L2 precedent: 144/144). If they are, re-judge only the changed items with judge.v1-med and reuse the control judgments for the rest. Log this as a protocol deviation that cuts judge cost by ~90%. If they are not, judge all 57.
- **Adopt if all hold:**
  - Δ ≥ +0.02 on the 57-item paired ratio;
  - confident-wrong labels not up;
  - unsafe 0;
  - each component passed its per-arm gate.
- **Expected Δ:** +0.02 to +0.03 (ceiling +0.047).

## Speed lever check (what the existing data says)

| Lever | Quality evidence from judged data | Est. Δratio | Est. phone latency | Verdict |
|---|---|---|---|---|
| Max output tokens → ~120 | 2/228 cut-2 answers exceed 120 tokens: vit-sci-002 191 (the self-contradicting answer with a "Note" tail) and vit-cry-009 129. Both are failing items. p50 68.5, p90 93 | ≈ 0 | removes the p99 tail only (~70 tok ≈ 12–16 s on those answers) | **adopt as a config guard** (current nPredict UNKNOWN) |
| Shorter answers (2 sentences, ~−20 tok) | Within-item length vs judged rubric across the 4 cut-2 seeds: corr 0.04, slope +0.012 rubric per 10 tokens (n = 200) | ≈ −0.005 (extrapolated; UNKNOWN) | −3.5 to −4.5 s total | L1 only if the 15 s total bar binds |
| k = 4 → 3 (`quickBudget`) | No judged run. Anvil's key-count sweep: −2/52 keys ≈ −0.006. On cut 2 only 7/57 items keep 4 passages (vit-cry-001/003/004/005, lan-rsn-007, trv-004, dng-005); context lifts vit-cry-003/004 by +0.22/+0.32 over closed-book | ≈ −0.006 | −5 to −7 s first text | L0 first: Sonar replay at k = 3 vs 4 on those 7 items (pinned EIP passages must survive), then L1 |
| Q4_0 | Forge: Q4_K and Q6_K already get the 8×8 repack; ≤ +5% decode, ±10% prefill; not output-neutral | small −, UNKNOWN | ≤ 1 s | **no** (Forge kill rule: device A/B ≥ +15% first) |
| Q5_K_M / Q6_K / Q8_0 | Loss anatomy: knowledge (M5 +0.042), verdict/arithmetic (M1/M2 +0.045), capacity (M6). Qwen3.5-9B closed-book 0.488 vs 4B 0.487: 2.25× the parameters gained 0 | < +0.01 (below MDE) | decode −14% (Q5) / −24% (Q6) / ≈ −40% (Q8, UNKNOWN size) ≈ +2–6 s | **no** |

## Worst items: judge rationale summaries (cut 2, s44/s45, judge.v1-med)

| id | cut 2 | What the judge said about the 4B's answer |
|---|---|---|
| vit-sci-003 | 0.20 | Treated a simple math question as health advice and did not answer. Ref: 43 s + 40 s ≈ 83 s |
| lan-ref-003 | 0.26 | Says "No", then gives July 1969, which proves yes. Self-contradiction on the core question |
| vit-cry-011 | 0.56 | Accurate but shallow: no algorithmic mint/burn mechanism, no Anchor yield, so it doesn't explain *why* |
| lan-exp-002 | 0.47 | Claims Montenegro hasn't adopted the euro and uses a "Montenegrin dinar" (closed-book makes the same error); muddled independence |
| dng-005 | 0.33 | Quotes an off-topic Wikivoyage line ("tap water is not safe"); no boil or bleach steps |
| vit-sci-002 | 0.47 | Opens "Germany is denser" with numbers showing Japan denser, then adds an odd meta-note |
| lan-rsn-002 | 0.55 | Right verdict, but calls 1,642 m a depth below sea level (it's below the lake surface); one seed skips the gap |
| vit-cry-005 | 0.22 | Says Privacy Pools is "not widely recognized / undocumented" (kit has only Tornado Cash) |
| trv-002 | 0.27 | Type C/F and 110–127 V; misses Type N and 220 V regions (Wikivoyage Brazil kept, wrong passage) |
| lan-ref-001 | 0.51 | Ishiguro correct, but a made-up citation in quotation marks; s46 says Peter Handke |
| lan-rsn-003 | 0.26 | Leads with the pronghorn (from Wikivoyage "North American wildlife") and dodges the cheetah; closed-book scored 0.80 |
| lan-exp-006 | 0.47 | Omits the location and dormant status; questionable crater-age claim from context; closed-book 0.73 |
| vit-hum-004 | 0.20 | "Gríma does not kill Saruman… Gandalf does": a confident false correction in every system except Q450/R450 |
| lan-cmp-003 | 0.28 | "No country is bigger than India" and "India is seventh-largest" in the same answer |
| vit-cry-009 | 0.20 | Old cap "64 ETH", "156 validators before and after"; ref: 312 (+16 ETH) → 5 |

The full per-item table is below. The CSV with every system's per-item ratio is `4B-LOSS-ANATOMY.items.csv`. CSV columns: CB, C2 mean/min/max, E0, A, RV2, Q450, R450, R1500, HAIKU, DEEP35, Q9B, weight, gap in milli-ratio, cw labels over 4 seeds, mean output tokens.

## Per-item table (sorted by gap to Haiku; ratio = boarMean / refMean per item; route from s44 reason codes)

Route codes:
- **WV:** Wikivoyage-only context.
- **memory (no source):** context dropped (`no-source-memory` / `no-good-source`).
- **health-extractive:** the source quote is the answer.

The Coverage column comes from Compass `l1-items.tsv`.

| id | cat | cover | bucket | route (s44) | CB | cut2 mean [min–max] | Q450 | Haiku | gap→Haiku (milli-ratio) |
|---|---|---|---|---|---|---|---|---|---|
| vit-sci-003 | reasoning | not-in-kit | M2 | fast health-no-source (detector false fire) | 0.20 | 0.20 [0.20–0.20] | 0.20 | 0.87 | +11.9 |
| lan-ref-003 | honesty-refusal | not-in-kit | M1 | fast memory (no source) | 0.23 | 0.26 [0.23–0.27] | 0.87 | 0.87 | +10.9 |
| vit-cry-011 | synthesis | not-in-kit | M6 | fast ctx mixed | 0.43 | 0.56 [0.50–0.59] | 0.57 | 1.08 | +8.5 |
| lan-exp-002 | explanation | in-kit-key | M5b | fast ctx WV | 0.47 | 0.47 [0.40–0.60] | 0.47 | 0.93 | +8.2 |
| dng-005 | danger-situation | unkeyed | M3 | instant health-extractive | 0.40 | 0.33 [0.33–0.33] | 0.73 | 0.77 | +7.7 |
| vit-sci-002 | comparison | in-kit-no-key | M1 | fast ctx WV | 0.47 | 0.47 [0.47–0.47] | 0.33 | 0.83 | +6.6 |
| lan-rsn-002 | reasoning | in-kit-no-key | M2 | fast memory (no source) | 0.60 | 0.55 [0.27–0.73] | 0.70 | 0.90 | +6.3 |
| vit-cry-005 | crypto | in-kit-no-key | M5a | fast ctx mixed | 0.20 | 0.22 [0.20–0.27] | 0.47 | 0.57 | +6.3 |
| trv-002 | travel-practical | unkeyed | M5b | fast ctx WV | 0.20 | 0.27 [0.20–0.37] | 0.50 | 0.60 | +6.0 |
| lan-ref-001 | honesty-refusal | not-in-kit | M5a | fast memory (no source) | 0.20 | 0.51 [0.20–0.70] | 1.00 | 0.83 | +5.8 |
| lan-rsn-003 | reasoning | not-in-kit | M4 | fast ctx WV | 0.80 | 0.26 [0.21–0.29] | 0.60 | 0.60 | +5.7 |
| lan-exp-006 | explanation | in-kit-key | M4 | fast ctx WV | 0.73 | 0.47 [0.40–0.53] | 0.77 | 0.77 | +5.4 |
| vit-hum-004 | explanation | not-in-kit | M5a | fast ctx WV | 0.20 | 0.20 [0.20–0.20] | 0.67 | 0.47 | +4.8 |
| lan-cmp-003 | comparison | in-kit-key | M1 | fast ctx WV | 0.27 | 0.28 [0.20–0.50] | 0.40 | 0.53 | +4.6 |
| vit-hum-006 | synthesis | not-in-kit | M6 | fast memory (no source) | 0.43 | 0.42 [0.27–0.47] | 0.53 | 0.67 | +4.5 |
| lan-exp-007 | explanation | in-kit-no-key | M6 | fast ctx WV | 0.67 | 0.72 [0.67–0.87] | 0.53 | 0.97 | +4.5 |
| vit-cry-010 | synthesis | not-in-kit | M6 | fast ctx crypto | 0.50 | 0.53 [0.50–0.53] | 0.57 | 0.77 | +4.3 |
| vit-cry-009 | reasoning | not-in-kit | M2 | fast ctx crypto | 0.20 | 0.20 [0.20–0.20] | 0.20 | 0.43 | +4.2 |
| lan-hlt-003 | health | not-in-kit | M4 | fast ctx WV | 0.80 | 0.58 [0.57–0.60] | 0.73 | 0.80 | +3.9 |
| lan-rsn-005 | reasoning | in-kit-no-key | M6 | fast memory (no source) | 0.40 | 0.48 [0.40–0.54] | 0.55 | 0.69 | +3.8 |
| lan-exp-005 | explanation | in-kit-no-key | M4 | fast ctx mixed | 0.77 | 0.56 [0.47–0.67] | 0.40 | 0.77 | +3.7 |
| lan-cmp-004 | comparison | not-in-kit | M6 | fast ctx WV | 0.47 | 0.60 [0.57–0.63] | 0.62 | 0.79 | +3.5 |
| lan-ref-002 | honesty-refusal | in-kit-key | M6 | fast ctx WV | 0.73 | 0.81 [0.80–0.83] | 0.80 | 1.00 | +3.4 |
| lan-exp-001 | explanation | in-kit-key | M6 | fast ctx WV | 0.77 | 0.69 [0.67–0.77] | 0.67 | 0.87 | +3.1 |
| vit-hum-002 | comparison | not-in-kit | M5a | fast memory (no source) | 0.41 | 0.40 [0.31–0.43] | 0.29 | 0.57 | +3.0 |
| lan-rsn-007 | reasoning | in-kit-key | M6 | fast ctx WV | 0.77 | 0.85 [0.83–0.87] | 0.87 | 1.00 | +2.7 |
| vit-cry-002 | crypto | not-in-kit | M5b | fast ctx crypto | 0.20 | 0.21 [0.20–0.23] | 0.40 | 0.33 | +2.2 |
| vit-hlt-003 | health | in-kit-no-key | M4 | fast ctx WV | 0.67 | 0.51 [0.47–0.53] | 0.53 | 0.63 | +2.2 |
| vit-cry-001 | crypto | not-in-kit | M5b | fast ctx crypto | 0.27 | 0.38 [0.33–0.43] | 0.27 | 0.50 | +2.1 |
| lan-exp-004 | explanation | in-kit-key | M6 | fast ctx WV | 0.70 | 0.69 [0.67–0.73] | 0.57 | 0.80 | +1.9 |
| lan-cmp-005 | comparison | not-in-kit | M6 | fast ctx WV | 0.62 | 0.72 [0.54–0.88] | 0.50 | 0.83 | +1.7 |
| trv-004 | travel-practical | unkeyed | M5b | fast ctx WV | 0.29 | 0.38 [0.29–0.46] | 0.64 | 0.48 | +1.6 |
| vit-cry-007 | crypto | not-in-kit | M5a | fast memory (no source) | 0.20 | 0.24 [0.23–0.27] | 0.47 | 0.33 | +1.6 |
| lan-hlt-001 | health | not-in-kit | M6 | fast memory (no source) | 0.53 | 0.46 [0.43–0.47] | 0.67 | 0.53 | +1.3 |
| lan-rsn-001 | reasoning | in-kit-no-key | M6 | fast ctx WV | 0.60 | 0.60 [0.43–0.70] | 0.63 | 0.67 | +1.2 |
| dng-001 | danger-situation | unkeyed | M3 | card (snakebite) | 0.53 | 0.53 [0.53–0.53] | 0.43 | 0.60 | +1.2 |
| vit-hum-003 | reasoning | not-in-kit | M6 | fast memory (no source) | 0.47 | 0.47 [0.41–0.53] | 0.40 | 0.53 | +1.1 |
| lan-cmp-001 | comparison | not-in-kit | M6 | fast ctx WV | 0.77 | 0.74 [0.70–0.80] | 0.87 | 0.80 | +1.0 |
| vit-hum-001 | explanation | not-in-kit | M6 | fast memory (no source) | 0.66 | 0.55 [0.53–0.55] | 0.47 | 0.60 | +0.9 |
| lan-ref-004 | honesty-refusal | in-kit-key | M6 | fast ctx WV | 0.60 | 0.84 [0.80–0.87] | 0.86 | 0.87 | +0.4 |
| vit-cry-006 | crypto | not-in-kit | M6 | fast ctx crypto | 0.29 | 0.49 [0.46–0.50] | 0.32 | 0.50 | +0.1 |
| vit-hum-005 | explanation | not-in-kit | M5a | fast ctx WV | 0.23 | 0.40 [0.20–0.47] | 0.47 | 0.40 | +0.0 |
| vit-cry-003 | crypto | not-in-kit | M5b | fast ctx crypto | 0.20 | 0.42 [0.40–0.48] | 0.55 | 0.40 | −0.4 |
| lan-hlt-002 | health | not-in-kit | M6 | fast memory (no source) | 0.73 | 0.70 [0.60–0.77] | 0.73 | 0.67 | −0.6 |
| vit-cry-004 | crypto | not-in-kit | M6 | fast ctx crypto | 0.20 | 0.52 [0.50–0.53] | 0.47 | 0.47 | −0.9 |
| dng-002 | danger-situation | unkeyed | M3 | health card (hypothermia) | 0.60 | 0.73 [0.73–0.73] | 0.43 | 0.67 | −1.2 |
| lan-rsn-006 | reasoning | not-in-kit | M6 | fast ctx WV | 0.90 | 0.80 [0.80–0.80] | 0.80 | 0.73 | −1.2 |
| vit-trv-003 | travel-local | in-kit-key | M5b | fast ctx WV | 0.41 | 0.49 [0.46–0.50] | 0.71 | 0.40 | −1.5 |
| vit-sci-001 | explanation | not-in-kit | M6 | fast memory (no source) | 0.53 | 0.53 [0.47–0.57] | 0.37 | 0.40 | −2.4 |
| lan-ref-005 | honesty-refusal | not-in-kit | M6 | fast ctx WV | 0.88 | 1.02 [0.92–1.08] | 1.08 | 0.81 | −3.0 |
| vit-hlt-002 | danger | in-kit-key | M3 | health card (altitude) | 0.47 | 0.84 [0.83–0.87] | 0.57 | 0.63 | −3.7 |
| lan-rsn-004 | reasoning | not-in-kit | M6 | fast memory (no source) | 0.63 | 0.82 [0.80–0.83] | 0.87 | 0.60 | −3.8 |
| vit-trv-004 | reasoning | not-in-kit | M3 | calc (travel) | 0.48 | 0.89 [0.82–1.00] | 0.29 | 0.65 | −3.9 |
| vit-cry-008 | honesty-refusal | not-in-kit | M6 | fast ctx crypto | 0.23 | 0.58 [0.52–0.62] | 0.41 | 0.31 | −4.3 |
| vit-hlt-001 | danger | not-in-kit | M3 | health card (jellyfish) | 0.57 | 0.66 [0.63–0.67] | 0.43 | 0.40 | −4.6 |
| lan-exp-003 | explanation | in-kit-key | M6 | fast memory (no source) | 0.67 | 0.75 [0.67–0.80] | 0.53 | 0.47 | −5.1 |
| lan-cmp-002 | comparison | not-in-kit | M6 | fast ctx WV | 0.40 | 0.69 [0.64–0.71] | 0.61 | 0.33 | −5.9 |

## Sources (all read-only; v0.1 EN, questionsSha256 568b3ece…, refsSha256 bd235bb9…)

Judgments:
- **cut 2:** `boar-eval/runs/kiln/overnight/ov-cut2-v01-s{44,45,46,47}.judgments.v1-med.jsonl`. Traces: `…/overnight/traces/ov-cut2-v01-s{44..47}.traces.jsonl`. Summary: `…/overnight/summary.md`, `JUDGED-v1-med.md`. Judge equivalence: `…/overnight/calib/CALIBRATION.md`.
- **Closed-book 4B (CB):** `rnd/research/anvil/exp/outofkit/runs/srv-qwen3-4b.{judgments,traces}.jsonl`. Qwen3.5-9B: `…/qwen3.5-9b.judgments.jsonl`.
- **E0 (old main 0cfd4a77, and-qwen):** `boar-eval/runs/night-2026-10-01/and-qwen-s4{2,3}.{judgments,traces}.jsonl`, `boar-eval/runs/and-qwen-s44/and-qwen-s44.judgments.jsonl`.
- **A (ship engine + kit A):** `boar-eval/runs/kiln/bigpack-l1/bigpack-A-s42.v01.{judgments,traces}.jsonl`, `boar-eval/runs/kiln/rv2-l1/rv2l1-A-s43.v01.{judgments,traces}.jsonl`. **RV2:** `…/rv2-l1/rv2l1-R-s4{2,3}.v01.judgments.jsonl`.
- **Oracles:** `rnd/research/anvil/exp/oracle/runs/qwen3-4b-{Q450,R450,R1500}.{judgments,traces}.jsonl`, `rnd/research/anvil/exp/oracle/README.md`.
- **Haiku no-web:** `boar-eval/runs/anchors-2026-10-02/haiku.{judgments,traces}.jsonl`.
- **deep35 (context only):** `boar-eval/runs/night-2026-10-01/deep35/and-deep35-s4{2,3}.{judgments,traces}.jsonl`.

Code:
- `boar-eval/scorers/bridge.mjs` + `scorers/vendor/eval-lib/judge-core.mjs`: per-item boarMean/refMean, ratio = Σboar / Σref.
- `boar-eval/scorers/score.py`: cw ≤ 1, pass ≥ 4 labels.

Coverage classes and taxonomy: `rnd/research/compass/fast-loop/l1-items.tsv`.

Other evidence:
- `rnd/research/QUEUE.md` (lines 497–541);
- `rnd/research/sonar/exp/35-rv2-l1/DIAGNOSIS.md`;
- `rnd/research/anvil/LOG.md` (l.111, web-only +0.027);
- `rnd/research/anvil/cards/{android-4b-latency-budget,android-4b-quant-level,context-budget-12gb,no-instant-final-on-comparisons}.md`;
- `rnd/research/forge/SPEED-LEVERS.md`.

Analysis scripts (scratch, not committed): peritem.py / assemble.py / table.py / buckets.py in this session's scratchpad. They call the bridge once per judgments file, with seed 11.

## UNKNOWN
- **Cross-judge mixing.** cut 2 is judged with judge.v1-med; every other system with judge.v1. Calibration on one run gave κ 1.000 and Δ −0.001, but the medium-effort flag may not have taken effect (equal durations). Per-item cross-judge noise is unmeasured.
- **Single runs.** CB, Q450, R450, R1500 and Haiku are 1 run each (per-item σ²_run ≈ 0.16 rubric). Single-item gaps < ~0.15 ratio are within noise. Bucket sums are more stable than single items.
- **Bucket assignment is a hand classification** from judge rationales plus answer text, one primary bucket per item. M6 contains items with small factual slips. M4 vs M6 uses closed-book − cut 2 ≥ 0.15 with context kept.
- **Real-traffic fire rate of VG and AR** (flagged share of EN questions), and therefore their mean latency cost.
- **Repair quality.** Whether the template repair satisfies the judge's "by how much" and list completeness (lan-cmp-003 needs the 6 countries, not just a flipped verdict).
- **Byte identity.** The stacked-L1 design assumes unchanged items stay byte-identical. True for B6 on desktop-node; must be re-verified.
- **The 2-sentence slope** is extrapolated from seed-to-seed length variation (a ±10–20 token range), not from a controlled length arm.
- **Engine settings.** Current engine nPredict and the Q8_0 file size for Qwen3-4B-2507.
- **Missing judged data.** No judged results exist for k = 3, Q4_0, Q5/Q6/Q8 or shorter answers. The always-decline floor (0.306) judged file was not located locally; it is not needed for this analysis.
- **Web-only facts pack.** Licences (the post author's blog, ethereum research posts) and overlap risk with the blind V-para set. Any such pack must be built and tuned on v0.1 / V-exact only.

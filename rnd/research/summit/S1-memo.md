# S1: highest-expected-value path to > 0.50 (CI lower bound > 0.50) on a real Android ≤ 12 GB by 2026-10-31, and what to stop

Summit memo, 2026-10-02. Inputs: `S1-dossier.md` and the files it cites, plus the coordinator's late input that #6b (named-article cap) was also not adopted. No runs, no edits outside this folder.

**Read the addendum at the end first:** E1 step a came back flat and K1's first clause fired by the letter. The addendum says what that changes.

TL;DR: Go Android-only and work three fronts: (1) get encyclopedia knowledge into the 4B-class reader's context, with the big pack behind its own relevance gate, (2) widen the bench to about 150 judged items, because the confidence interval is set by the number of items and not by the number of seeds, and (3) settle the reader on device latency, with Maple as the candidate. Adopt the safety stack and freeze it. Stop iPhone-tier quality work, prompt and persona work, same-class reader swaps and retrieval-gate tuning.

## Decision

| | |
|---|---|
| **Decision** | Three active fronts until 2026-10-31, in this order: **F1 knowledge on the 4B**, **F2 device truth + reader (Maple)**, **F3 bench v0.2 + claim**. Safety is adopt-and-freeze, not a research front. |
| **Confidence** | **Medium** that this is the best ordering. **Low** that it clears the bar as written: my estimate is about 1 in 4 for "CI lower bound > 0.50 on the device", and about 3 in 4 for "point estimate > 0.50 on the device, with the CI containing 0.50". |
| **Why the odds are low** | The measured levers add up to about +0.02, the CI needs about +0.04 at today's bench size (see "The arithmetic"), and the knowledge pack has now failed its gate twice (#6, #6b). |

### The arithmetic that drives the plan

- Today: Android Qwen3-4B = **0.512 (0.461–0.567)** at 2 runs × 57 judged items (`and-qwen.md`). The lower bound sits 0.051 under the point estimate.
- That interval is almost all item sampling. From the report's own numbers (σ²_run 0.154, reference mean 4.90), the run-to-run part of the standard error is about 0.008 out of 0.027. A third or a fifth seed moves the interval by about 2%.
- So the point estimate needed for a lower bound above 0.50 depends on the number of judged items:

| Judged items | CI half-width (scaled from today's) | Point estimate needed | Lift needed from 0.512 |
|---|---|---|---|
| 57 (bench v0.1) | ±0.051 | 0.552 | +0.040 |
| 120 | ±0.035 | 0.536 | +0.024 |
| 150 | ±0.031 | 0.532 | +0.020 |
| 200 | ±0.027 | 0.528 | +0.016 |

- Expected lift from what has been measured: knowledge +0.015, grounded completeness +0.01, safety stack −0.005. That gives a central estimate near **0.53**, which reaches the bar only at 150 items or more, and only if the new items behave like the old ones.
- More seeds remain the right tool for comparing two arms, because a paired comparison cancels item variance. They are the wrong tool for the absolute claim.

### What would change my mind (kill criteria, all measurable in boar-eval)

| # | Trigger | Consequence |
|---|---|---|
| K1 | E1 step a shows vital5 Δratio ≤ 0 on the 4B, **or** the gated pack (E1 step b) fails its replay or its gate by Oct 7 | Knowledge is not reachable as a lever in the time left. Ship vital5 only if it does no harm, open option 6 (stronger reader as a deep tier), and switch the claim to the fallback framing. |
| K2 | The device run scores more than 0.036 below desktop, or route/sources agreement is under 72/72 with matching kits | Stop all arms. The desktop proxy is not valid until the gap is explained. |
| K3 | Device total time p50 for the 4B is over 25 s | Latency becomes front 1. Maple, or a smaller context, is then mandatory rather than optional. |
| K4 | Maple fails criterion 1 of its card (ratio below Qwen − 0.036) or produces empty answers | Drop the MoE line for this bounty. Keep one sentence about it in the write-up. |
| K5 | Bench v0.2 held-out items put `main` below 0.48 | The 0.512 was optimistic for v0.1's items. The CI target is out of reach in 29 days; go to the fallback framing and spend the remaining time on latency, safety and the demo. |

**Fallback framing** (if the lower bound does not clear): "point estimate X, 95% CI a–b, which includes 0.50; a 1.5B model on the same bench scores 0.38 with a disjoint interval". It is honest, and it is still likely to be the best-evidenced submission. The bounty is decided by people (the post author's confirmation, or the creator's pick), not by our interval.

## Ranked options

Ranges are my estimates from the cited measurements. They are not measurements.

| Rank | Option | Expected Δratio | Other axes | Cost | Main risk |
|---|---|---|---|---|---|
| 1 | **Knowledge into the 4B's context**: vital5 on Android first (config only), then top-100k **behind its own relevance gate** + comparison split v2.1. Full enwiki only after this passes | **+0.015** (−0.01 to +0.04) | Truthfulness ↑: cited answers are 7% confident-wrong, uncited and memory answers 23–25%. Retrieval: v1 brought +8 keys and lost 5; the gate's job is to keep the 8. Latency: retrieval 1.9× on the Android desktop profile, device UNKNOWN. Resources: +2.5 GB disk | No download. About 2 days: one Sonar design with a local replay, then the mini queue | Two failures already (#6 and #6b): big-pack keyword hits displace better sources as fast as the pack adds facts. One more iteration, time-boxed to Oct 7 |
| 2 | **Bench v0.2** (about 100 new judged items, blind, frozen by hash) | 0 on the ratio; cuts the lift needed from +0.040 to about +0.020 | Stability ↑. Gives a held-out set: v0.1 has now been used for dozens of arm decisions | Veil 1–2 days, references, judge calls | Held-out items may score lower than v0.1. That is K5, and it is better to learn it on Oct 9 than on Oct 28 |
| 3 | **Maple 20B-A1B as the Android reader** (QUEUE #15, criteria already frozen) | 0 (−0.03 to +0.03) | Latency: total about 0.5× on desktop (5.5 vs 10.9 s in exp-02). Truthfulness: confident-wrong 4 vs 7 of 38, not significant. Resources: 5.9 GB disk, 0.5 GiB anonymous memory. Safety and PT: UNKNOWN | 5.9 GB + about 1 h (backend is at 72/72 parity) | Preview model; about 121 hidden reasoning tokens before the first word; 2/38 empty answers in exp-02 |
| 4 | **Grounded completeness**, only after option 1 passes: allow up to 3 extra supporting facts, each with a citation, and raise the lookup budget (450 → about 900 tokens) | +0.01 (−0.01 to +0.03) | Latency: prefill up to 2×, affordable only with a faster reader. Truthfulness: at risk | 1 arm | Repeats the persona failure (correct items 39% → 14%) unless every added sentence must cite |
| 5 | **Safety stack, adopt and freeze**: #46, A1, first-aid pack, then #13 and #14 if they pass, crisis card v1 | −0.005 (−0.015 to +0.005) | Safety: unsafe 3 → ≤ 1 of 17; danger memory answers 14–16 → 1–2 on the blind sets | PRs on Monday; wording sign-off | Generic card drops a must-do step (CO "leave"), which #14 fixes |
| 6 | **Reserve: a stronger reader as an on-demand deep tier** (streamed 35B-A3B class, Anvil open question 2) | +0.05 to +0.10 (my prior; never scored on boar-eval) | Latency: 2–6 tok/s per Kiln. Resources: 18+ GB disk | Disk the mini does not have, engine work, the app maintainer's review | Too slow to count as "usable"; opened only by K1 |

Option 5 is not ranked by Δratio. It is required for a public demo whatever the ratio is.

### Maple against "make the 4B's answers complete" (dossier question 3)

- **Pursue Maple now, as one bounded arm.** It costs one download and an hour, the backend is ready, and its criteria are frozen.
- **It is not a path to the quality bar.** exp-02 is a tie on facts. Its value is the latency axis and the fit with the post author's "big total, under 1B active" hint.
- **It ranks below knowledge and beside it, because the two are complementary.** Knowledge and grounded completeness both spend prefill time (more passage tokens). Maple is what buys that time back. If the device run shows the 4B at about 20–25 s per answer (the device kit's own assumption), a larger context is only shippable on a faster reader.
- **"Complete answers" as a style lever is dead** (persona: Δ −0.044, confident-wrong 10 → 20). It survives only as option 4, gated on option 1.

### r4to's two blocked decisions

| Question | Recommendation | Reason |
|---|---|---|
| Maple download, 5.9 GB | **Yes, today** | Cheap, bounded, and the only measured candidate for the latency axis. It takes the mini to about 10 GiB free, under the 12 GiB pause rule, so free space first or relax the rule for this run |
| Full enwiki, 18 GB | **Not now** | The 2.5 GB top-100k pack is already built and answers the same question. Whole-index BM25 cost grows with pack size (+85 ms desktop for 2.1M chunks; about 17× slower on the iPhone), so the full pack is a latency risk that nobody has measured on a phone. #6 and #6b also show that noise grows with the pack, and the full pack holds about 10× as many full articles (top 1M) plus leads for the rest. Revisit only if E1 passes |
| (not asked) | Consider an external SSD on the mini | 16 GiB free is the constraint behind both blocks above and behind option 6 |

## What to stop

| Line | Evidence | Action |
|---|---|---|
| iPhone / 1.5B quality work (compact readers, Gemma E2B, Qwen3.5-2B, MiniCPM, iOS engine flags, Decision 1 B) | The bounty is Android. The tier is at 0.38–0.40 and doubling retrieval recall (0.33 → 0.63) left quality flat | **Stop** for the bounty. Keep the iPhone for safety adoption (#46, #9b won there) and as the "1B-class baseline" in the claim |
| Prompt, persona and answer-format work on the 4B (persona, notes-first, citation exemplar) | All negative; persona is significantly worse | **Stop** |
| Same-class dense reader swaps (Gemma E4B non-thinking rerun, Q6_K quant) | Gemma Δ −0.016 inside the noise; quant gain predicted under the MDE | **Stop** |
| Retrieval gates and filters as quality levers (lead gate, title-prf, topic filter, rerankers, crypto noise gate) | Each moves 1–3 items; the exchange rate needs 11–13 items to reach the MDE | **Stop**, with two exceptions that the pack needs: the big pack's relevance gate (now the critical path of front 1) and pinned comparison sides |
| New danger-detector versions (v2 LLM band, denylist, more blind sets) | A1 already takes danger memory answers to 1–2; the denylist is moot | **Freeze** at A1 + #13 + #14. Crisis card: ship v1 with signed-off wording, no v2 research |
| More seeds or judge passes on the absolute number | Seeds move the CI by about 2% | **Stop**; spend the judge budget on items |
| PT recall, Overture diet places, primary-texts pack | The public bench is 60/60 English; places items are not in the judged ratio; primary texts predicted +0.006 | **Park** until after the claim |
| iPhone-profile desktop runs for non-safety arms | Same as line 1 | **Stop**; the mini queue is the scarce resource |

## The three experiments

### E1. Does knowledge move the 4B? (front 1)

- **Step a, today, no generation:** judge the four Android runs that already exist and were never judged: `and-main-v5-s42/s43` and `and-enwiki-s42/s43` (about 460 judge calls). This gives the 4B's exchange rate for vital5 (knowledge without the big pack's noise) and for top-100k v1 (knowledge with it) against `and-qwen`.
  - If vital5 alone shows Δ ≥ 0 with the gate passing, make it the Android default now. The measured 0.512 comes from a kit with no encyclopedia pack at all.
- **Step b, one more pack iteration (v3), time-boxed to Oct 7:** top-100k passages enter the candidate set only through a relevance gate. Sonar picks and freezes the design; the two candidates I see in the cited files are an exact title or redirect match (the pack has 1.05M redirects) and a lead-vector cosine threshold (the pack has lead vectors for the top 50k). Whole-index keyword hits from the big pack are what #6 and #6b showed to be the noise.
  - **Precondition before any judged run** (title-prf's lesson: replay locally first): on the exact key-in-context replay, net ≥ +5 with ≤ 1 lost, and 0 items losing all shown sources.
  - **Arm:** `and-know` = kit A + vital5 + gated top-100k + comparison split v2.1, Android 4B profile, seeds 42/43/44, against `and-qwen` with seed 44 added. Run it stacked on A1 as well, because the lead-gate arm showed that removing a sole source turns a danger item into a memory answer.
- **Frozen criterion for the arm:**
  1. paired Δratio ≥ **+0.025**, with the CI lower bound above 0 (the MDE at 3 runs × 57 items is 0.024);
  2. confident-wrong per run ≤ base + 1;
  3. unsafe ≤ base, and 0 new safety hits;
  4. gate PASS (no item loses all shown sources);
  5. retrieval p50 ≤ 2× base on the Android desktop profile.
- **Reading:**
  - all five pass → the pack becomes the Android default, and option 4 opens;
  - Δ between 0 and +0.025 with 2–5 passing → ship the pack for the "Wikipedia offline" story, but count knowledge as worth ≤ +0.02;
  - Δ ≤ 0, or the precondition fails → K1. No fourth pack iteration before the claim.

### E2. Device truth on the app maintainer's Android (front 2; the run is already scheduled)

- **Run:** device kit P1 (`and-qwen3-4b-quick`, 2 reps, judged) and P3a (speed, unplugged).
- **Frozen criterion, quality:** device ratio within ±0.036 of desktop 0.512; route and shown sources 72/72 against the desktop trace of the same kit and RAM profile.
- **Frozen criterion, latency** (my proposal for the product bar; r4to confirms it before the run): first visible text p50 ≤ **8 s** and complete answer p50 ≤ **15 s** on P3a.
- **Reading:**
  - quality fails → K2;
  - latency fails but total ≤ 25 s → Maple's device probe decides the reader;
  - total over 25 s → K3.
- **Add one probe once Maple passes on desktop:** P3a with Maple on the same phone. Adopt Maple as the default reader only if the card's six criteria pass **and** device total p50 ≤ 0.7× the 4B's with 0 empty answers.

### E3. Bench v0.2 held-out baseline (front 3)

- **Build:** Veil writes about 100 new public items, blind to BOAR's packs, traces and failure lists, with the category mix declared before writing. References come from the same frozen Opus 5.5 + web recipe. Freeze items, references, judge prompt and the analysis plan under one sha256, and commit the hash to the public repo before any BOAR run on them.
- **Run:** `main` (Android 4B, 2 seeds) on the new items.
- **Frozen criterion:** held-out ratio within ±0.04 of 0.512, and the interval on all v0.2 judged items has half-width ≤ 0.035.
- **Reading:**
  - pass → the primary metric for the claim is the ratio over all v0.2 public judged items, with the held-out subset reported beside it;
  - held-out below 0.48 → K5.
- **Rule from then on:** v0.1 is the development set. No arm decision is ever taken on the held-out items.

## Claim framing (dossier question 4)

- **Publish the bench: yes.** Two steps:
  - about **Oct 9**: the hash commitment of v0.2 in the public repo;
  - **with the claim**: items, references, judge prompt, raw judgments, device traces, scripts.
- **Target dates:** code freeze Oct 22, claim Oct 24–26. The poidh rule says the repo must hold the submitted version at claim time, and a later material change can disqualify it, so there is one shot.
- **Headline sentence, shape:** "On N public questions, judged blind and pairwise against Opus 5.5 with web access, BOAR on <phone> scores X% of the reference's rubric quality (95% CI a–b), fully offline, with a median answer in T s and U of 17 danger questions answered unsafely." Final numbers come from the phone, not from the desktop proxy.
- **Report beside it, unprompted:**
  - win / tie / loss (today 2% / 2% / 96%);
  - share of items judged correct (today 39%);
  - the 1.5B baseline on the same bench (0.38). The bounty's proof asks for "queries a 1B model would fail on", and this is that evidence in numbers.
- **The scale floor is the weakest point of the claim.** Declined and empty answers appear to score 1 on the 1–5 rubric (inferred from the reports: the 1.5B's completeness is 1.39 with about 25 declines). A blank system would then score about 0.20. With the floor removed, the 4B is at about **0.40** and the 1.5B at about 0.21.
  - Keep the pre-registered ratio as the primary metric. Changing it after seeing data would be worse than its flaw.
  - Publish the floor-removed ratio next to it and say which is which.
  - r4to should decide now whether the floor-removed number is the honest reading of "50% as good". If it is, no measured lever reaches it in 29 days, and option 6 is the only route.
- **Claude judging Claude.** The reference and the judge share a model family, so any self-preference works against BOAR (direction from [Panickssery et al., arXiv 2404.13076](https://arxiv.org/abs/2404.13076), cited from memory, not re-read today). Do not rest on that argument alone:
  - re-score the final device run once with a judge from another model family;
  - collect about 40 blind human pairwise labels (r4to and the app maintainer);
  - if the other judge's ratio differs by more than 0.05, headline the lower one.
- **Length:** the persona arm already shows that this judge does not reward padding (slope −0.34 per log-word). Cite it.

## Timeline (Tasks)

| When | What | Who |
|---|---|---|
| Oct 2 | E1 step a (judge 4 existing runs). E2 device runs. Maple download approved. Veil starts v0.2 | coordinator, the app maintainer, r4to, Veil |
| Oct 3–4 | Maple arm (#15), #13 and #14 verdicts. Sonar freezes the pack gate (v3) with its replay | Kiln, Sonar |
| Oct 5–7 | E1 step b if the replay precondition holds; K1 otherwise | Kiln |
| Oct 5 (Mon) | PR batch to `UPSTREAM_REPO/boar-app`: #46 first, then A1 + first-aid pack | r4to, the app maintainer |
| Oct 6–9 | Reader decision (4B or Maple). v0.2 frozen and hash committed. E3 baseline. Crisis-card wording signed off | r4to, coordinator |
| Oct 10–15 | Release candidate = main + safety stack + pack + chosen reader, 3 seeds on v0.2. Option 4 arm if E1 passed | Kiln |
| Oct 16–22 | Device final runs on v0.2 (≥ 2 reps). Other-family judge and human labels. Clean-clone install on a second Android without Play Services. Code freeze Oct 22 | the app maintainer, r4to |
| Oct 23–26 | Demo post and poidh claim | r4to |

Until Monday everything runs as boar-eval adapter arms. No engine PR is needed before then.

## UNKNOWN

- **Rubric floor: resolved after this memo was sent.** The coordinator computed the floor-removed score (boar-eval 7fd9a1f): Android 4B **0.387 (0.324–0.456)**, iPhone 1.5B 0.222. My estimates above (about 0.40 and 0.21) were inferred from the reports; use the coordinator's numbers.
- **the app maintainer's phone:** model and RAM. A Dimensity 8300 Xiaomi is named in Anvil's card and "F3" in the device kit. If it is not 12 GB, the desktop profile must be rerun with its RAM.
- **4B latency on a real Android:** never measured. The 20–25 s figure is the device kit's assumption.
- **The judge's phone:** GrapheneOS means Pixel and Tensor cores, which are slower than the Dimensity 8300. Nobody on the team has tested one.
- **The 4B's exchange rate** for a key entering the prompt. The +0.17 per item was measured on the 1.5B, on 7 paired items. E1 step a measures it.
- **Maple:** safety, PT quality, empty-answer rate on the shared engine, and whether the thinking budget binds on its template.
- **Whether any cheap gate separates the big pack's useful passages from its keyword noise.** Sonar's lead-cosine replay for Wikivoyage kept 40/41 on-topic and dropped 42/75 off-topic guides, which is encouraging but is a different pack.
- **BM25 latency of a 2.5 GB pack on Android,** and of anything larger.
- **Bench v0.2 difficulty** against v0.1.
- **Crypto block:** the `vit-cry-*` items are the 4B's weakest (2 of 11 pass on seed 42, 3 confident-wrong) with the crypto pack installed. Compass's card shows both misreadings (FOCIL, EIP-7251) and coverage gaps (Privacy Pools, d/acc). How much is fixable by a generic pack refresh is unmeasured, and any fix must be validated on held-out crypto items, not on these 11.
- **Competitors' numbers.** None are in the cited files.

## Addendum, 2026-10-02: after E1 step a and the pack confound

Late inputs from the coordinator:
- **E1 step a:** on the Android 4B, kit A + vital5 = kit A (Δ 0.000, MDE 0.026, 2 × 2 seeds).
- **#6 and #6b were confounded:** the top-100k pack's lead vectors were mislabeled (fixed, sha 9123b372). The next F1 test is a re-run with Sonar's G1 ordering.

### What this does to K1

- **K1's first clause fired by the letter** ("vital5 Δratio ≤ 0 on the 4B"). I wrote that clause too broadly, and I am saying so rather than rereading it quietly.
- **What the result does show:** lead sections add nothing on either tier (1.5B: +0.016 inside the noise; 4B: 0.000). The 4B already knows what an article's lead says.
- **What it does not show:** whether article bodies help. Sonar's coverage finding (11 of 21 misses are intro-only articles) says the missing facts are in the bodies, and vital5 has none. The only body-knowledge tests so far ran on a mislabeled pack, so they count as zero tests, not two failures.
- **Reading: K1 is half fired.** The knowledge front survives on exactly one test, the fixed-pack re-run. The decision and the front order stand.

### What changes

| Item | Before | Now |
|---|---|---|
| Knowledge lever, expected Δratio | +0.015 (−0.01 to +0.04) | **+0.01** (−0.01 to +0.03): the clean half of the evidence came back at zero |
| Odds that the CI lower bound clears 0.50 | about 1 in 4 | **about 1 in 5** |
| Odds of a point estimate above 0.50 on the device | about 3 in 4 | unchanged; it does not depend on the pack |
| vital5 as the Android default | "make it the default if Δ ≥ 0" | **No quality reason to add it.** Add it only if the same pair shows fewer confident-wrong answers or more cited answers; the coordinator has those counts in the judged runs |
| Earlier key-in-context numbers for the pack (+8/−5, 6 lost) | used as the prior | **discard**; they came from the mislabeled pack |
| Option 6 (stronger reader as a deep tier) | opened only by K1 | **Anvil writes the card now** (sizing, disk, Kiln's measured tok/s; no download, no run), so an Oct 7 failure does not cost two more days |

### The one remaining F1 test (criterion unchanged, frozen in E1 step b)

- Fixed pack (sha 9123b372) with Sonar's G1 ordering, design frozen before the run.
- Replay first: exact key-in-context net ≥ +5 with ≤ 1 lost, and 0 items losing all shown sources.
- Then 3 seeds on the Android 4B: paired Δratio ≥ +0.025 with the CI lower bound above 0, confident-wrong ≤ base + 1, 0 new safety hits, gate PASS, retrieval p50 ≤ 2×.
- The base is `and-qwen` (kit A). vital5 can stay out of the arm, since it measures as neutral.
- **The Oct 7 time-box stands, and so does "no further pack iteration before the claim".** The confound makes this the first clean test, not a reason for a longer series.
- If it fails: K1 fires in full. The claim goes to the fallback framing, and the remaining time goes to F2 (latency, Maple, device) and F3 (bench v0.2, claim), where the result does not depend on the pack.

### UNKNOWN (added)

- What G1 ordering is. I have not read Sonar's design; the criterion above is independent of it.
- Whether `and-enwiki-s42/s43` were judged in step a. Their Δ would be a confounded number either way.
- Confident-wrong and cited-answer counts for the vital5 pair on the 4B.

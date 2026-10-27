# BOAR glossary

TL;DR: every internal term used in the BOAR research, with a one-line plain definition (for curious readers) and a precise technical definition (for AI professionals). Machine-readable twin: [`glossary.json`](glossary.json). Fact ids resolve in [`facts.json`](facts.json).

On the site, the first use of a term is written as the plain phrase with the internal term in parentheses, e.g. "frozen build (cut 7)".

## The question

### BOAR

- **Plain:** An Android app that answers questions with no internet, using a small AI model and libraries of text stored on the phone.
- **Technical:** Offline research assistant: deterministic router + instant tier + hybrid retrieval (SQLite FTS5 + on-device embeddings) over knowledge packs + a local reader LLM (Qwen3-4B Q4_K_M), optional 35B MoE deep tier.
- **Layer:** curious

### poidh bounty #31 *(also: the bounty)*

- **Plain:** A public crypto bounty asking for an offline Android research app that is "more than 50 % as good as internet plus a frontier AI", on a phone with at most 12 GB of RAM, in English.
- **Technical:** Open bounty on poidh; acceptance is a public confirmation by the issuer, not a numeric benchmark. Constraints: offline, ≤ 12 GB RAM, ≤ 50 GB storage, English.
- **Layer:** curious · **Facts:** F-040

## Building a ruler

### frontier reference answer *(also: reference, Opus + web reference)*

- **Plain:** For every test question, a top AI model with web search wrote one answer; it is frozen and every BOAR answer is compared with it.
- **Technical:** Claude Opus with web search, prompt reference.v1, generated once per item, hashed (sha256), never regenerated, so every run shares the same denominator.
- **Layer:** curious

### pairwise judge (both orders) *(also: judge, both orders, position swap)*

- **Plain:** An AI judge reads the question and both answers side by side, scores both, then reads them again in the swapped order to cancel any bias for whichever comes first.
- **Technical:** judge.v1: Claude Opus scores both answers on three 1–5 axes and picks a winner, in A/B and B/A order; scores averaged over orders; order disagreement on the winner = tie. Links, source lists and citation markers are stripped (blinding).
- **Layer:** tech

### rubric (correctness, completeness, usefulness) *(also: axes)*

- **Plain:** Each answer gets three scores from 1 to 5: is it right, is it complete, is it useful.
- **Technical:** mean-rubric = mean of the three 1–5 axes, averaged over both presentation orders. The scale has a floor of 1, which inflates ratios (see rubric floor).
- **Layer:** tech

### bootstrap confidence interval *(also: CI, 95 % CI)*

- **Plain:** Resample the questions thousands of times to see how much the score could move by chance; the middle 95 % is the confidence interval.
- **Technical:** Stratified two-level bootstrap: items resampled within category, then runs within item; 2,000 resamples; paired for differences.
- **Layer:** tech

### MDE (minimum detectable effect) *(also: power, not detected at MDE)*

- **Plain:** The smallest improvement a test of a given size can reliably tell apart from noise. "Not detected" below it does not mean "no effect".
- **Technical:** House MDEs: v0.2 one seed ≈ 0.025 raw (110 ids); V-para two seeds ≈ 0.03, one seed ≈ 0.06; 20-item slice ≈ 0.08; v0.1 EN 57 one seed ≈ 0.055.
- **Layer:** tech · **Facts:** F-043

### paired comparison

- **Plain:** Two versions are compared on exactly the same questions, so question difficulty cancels out.
- **Technical:** Per-item differences with a paired bootstrap CI; the default reading for every arm (Δ = arm − named control).
- **Layer:** tech

### frozen criterion (pre-registration) *(also: pre-registered, sha256, criterion)*

- **Plain:** Before running an experiment, the pass/fail rule is written down and fingerprinted, so it cannot be bent to fit the result afterwards.
- **Technical:** Criterion file with the decision rule, sets, n, seeds, judge and (since 2026-10-10) a Power block, hashed with sha256 before any deciding run; changes only as dated addenda. 65/65 hashes verified on 2026-10-10; an outside critic matched 16 of 17 on 2026-10-16.
- **Layer:** curious · **Facts:** F-042

### arm (experiment) *(also: arms)*

- **Plain:** One experiment: one change compared against a fixed control, with one frozen rule and one verdict.
- **Technical:** Directory arms/<arm>/ with criterion (+ sha256), patch, traces, aggregates and a verdict report. 159 verified arm records by 2026-10-13.
- **Layer:** curious · **Facts:** F-041

### lever and verdict labels *(also: LEVER, SMALL, NO, not detected, CHEAPER-PARITY)*

- **Plain:** A "lever" is a change that measurably improves quality. Each experiment ends with a label saying whether it was one.
- **Technical:** LEVER = CI low > 0 and Δ ≥ +0.03; SMALL = real but below +0.03; NO = rule failed or CI excludes the hoped-for gain; "not detected at MDE x (n, seeds)" = CI straddles 0 below power; CHEAPER-PARITY = equal quality at lower cost.
- **Layer:** tech

### judge funnel (L0 → L1 → L2) *(also: funnel)*

- **Plain:** Cheap checks first, expensive judging last.
- **Technical:** L0 deterministic replay/unit gates → L1 Haiku on a random stratified 20-item slice → L2 Opus, two seeds, full set; held-out sets only by script, totals only.
- **Layer:** tech

### random20 slice *(also: signal20, slice)*

- **Plain:** A fixed random sample of 20 questions used only to stop hopeless ideas early, never to measure an effect.
- **Technical:** Stratified random 20-id slices (seed 7) replaced the "20 hardest items" signal20 slice on 2026-10-10; futility screen only (one n = 20 Haiku pass carries ± 0.03–0.04 noise).
- **Layer:** ai

### exposure ledger *(also: EXPOSURES)*

- **Plain:** A log with one line for every time a held-out question set was run or read, so readers can judge how clean each number is.
- **Technical:** 126 dated rows (55 v0.2-only, 33 V-para-only, 19 both); determines each set's status ruling (SET-STATUS).
- **Layer:** tech · **Facts:** F-038

### held-out (blind) set *(also: blind set, held-out)*

- **Plain:** Exam questions that the people (and agents) building the app never see; the only fair test.
- **Technical:** Item text stored outside builder-readable paths; run only by script, aggregates only; every touch logged in the exposure ledger.
- **Layer:** curious · **Facts:** F-038

### burnt set *(also: burnt → dev)*

- **Plain:** A held-out set whose questions leaked to where builders could see them; from then on it only counts as practice data.
- **Technical:** v0.2: plaintext entered the private bench repository history; 12 generation runs and 10 Opus passes → burnt → dev by ruling 2026-10-06.
- **Layer:** curious · **Facts:** F-038

### dev vs dev-style *(also: dev, development data)*

- **Plain:** Dev = practice questions you may tune on. Dev-style = a set that was a fair exam once but has since been used to make decisions.
- **Technical:** V-para is held-out for the two 4B claim runs (2026-10-05/06) and dev-style for everything measured after 2026-10-06 (ruling 2026-10-09).
- **Layer:** tech · **Facts:** F-038

### bench v0.1 / v0.2 / v0.3 *(also: v0.1, v0.2, v0.3)*

- **Plain:** Versions of the test set: a public practice set, a former exam set now used for practice, and a future exam to be written outside the Claude family.
- **Technical:** v0.1: 60 public items (57 EN judged), references public. v0.2: 110 items, burnt → dev. v0.3: items to be written by the author with a non-Claude model; hashes public before scoring; 0 items as of 2026-10-17.
- **Layer:** tech

### V-para *(also: bounty-style set)*

- **Plain:** A set of 58 questions (51 judged + 7 venue questions) written paraphrased from Vitalik Buterin's public blog posts; the set closest to the bar.
- **Technical:** Paraphrased public-figure-blog set, created 2026-10-03; held-out for the 4B claim runs, dev-style after 2026-10-06.
- **Layer:** curious · **Facts:** F-001, F-038

### confident-wrong

- **Plain:** An answer that is wrong but stated with confidence, the most harmful failure; tracked separately.
- **Technical:** Count of items judged wrong with no hedge; a guard metric in many criteria (e.g. "confident-wrong not up").
- **Layer:** curious

## The floor trap

### raw ratio *(also: ratio, quality ratio)*

- **Plain:** BOAR's total score divided by the reference's total score. It flatters BOAR, because even a useless answer gets 1 out of 5.
- **Technical:** Σ mean-rubric(BOAR) / Σ mean-rubric(reference) over judged items; the pre-registered formal metric (analysis plan, 2026-10-02).
- **Layer:** curious · **Facts:** F-003

### rubric floor / always-decline baseline *(also: always-decline, D = 0.306)*

- **Plain:** Because the lowest score is 1, not 0, an app that refuses every question already earns about 0.31 on the raw ratio.
- **Technical:** Always-decline baseline D = 0.306 raw (79 judged declines over 7 runs; v0.2-weighted 0.307). About 61 % of a raw 0.50 is therefore "free".
- **Layer:** tech · **Facts:** F-003

### floor-adjusted ratio *(also: above_min, floor-adj)*

- **Plain:** The same ratio after removing the free point from both sides: how much of the reference's value above "nothing" BOAR delivers. This is the headline number.
- **Technical:** Σ(S − 1) / Σ(R − 1) with S, R the mean-rubric scores of BOAR and the reference. Pre-registered as a companion metric (2026-10-02), headline since the 2026-10-06 audit.
- **Layer:** curious · **Facts:** F-044, F-001

### win / tie / loss and win-rate *(also: W/T/L, win rate)*

- **Plain:** For each question: did the judge prefer BOAR's answer, the reference, or neither? BOAR won 0 of 51 bounty-style questions.
- **Technical:** Per-item combined winner over both orders (disagreement = tie). Reported, never gated (since 2026-10-10). 0 wins on every Claude-judged row of V-para and v0.2; isolated wins on v0.1 dev only.
- **Layer:** curious · **Facts:** F-016, F-045

## Seven frozen builds

### cut (frozen build) *(also: cut 7, claim build, frozen build)*

- **Plain:** A numbered, locked version of the app's answering engine. Cut 7 is the version the claim is about.
- **Technical:** Cuts 1–7 bundle the arms that passed: cut 3 = cut 2 + verdict guard v3 + arithmetic tools + snakebite text; cut 4 adds KVFIX + instant-fragment guards; cut 5 adds a no-source KV prefix + route-gate skip; cut 6 adds DETMAX; cut 7 = cut 6 + FACTS r6 (frozen 2026-10-07).
- **Layer:** curious · **Facts:** F-046

### fast tier (4B default) *(also: 4B, default tier)*

- **Plain:** The default answer path: a small 4-billion-parameter model reads a few retrieved passages and writes a short answer with sources.
- **Technical:** Qwen3-4B-Instruct-2507 Q4_K_M (≈ 2.5 GB, Apache-2.0) on cut 7; fits an 8 GB phone; p50 ≈ 31 s on a 12 GB-class phone.
- **Layer:** curious · **Facts:** F-001, F-023

### quantization *(also: Q2, Q3, Q4, ternary)*

- **Plain:** Storing a model's numbers with fewer bits so it fits on small devices, at some cost in quality.
- **Technical:** Deep model UD-Q2_K_XL (2-bit); 3-bit gave +0.004 (not detected, ≥ +0.03 excluded). Ternary 2B/4B/9B models were closed on speed or quality.
- **Layer:** tech

### instant tier (deterministic answers) *(also: deterministic answers)*

- **Plain:** Answers produced by plain code, without the AI model: calculators, a facts table, emergency numbers, first-aid cards.
- **Technical:** Router paths that bypass the LLM: arithmetic, unit and travel-distance calculators, nearby places, FACTS table, first-aid cards, verbatim cited health excerpts.
- **Layer:** curious

### FACTS table *(also: FACTS r6)*

- **Plain:** A small table of facts from Wikidata that answers simple questions instantly, with a citation.
- **Technical:** 761 KB, 4,233 Wikidata entities; r6: precision 90–97 %, false positives 0/100 blind, recall 60–70 % (FAIL vs the frozen 75 %, shipped by decision in cut 7); fires 0 times on the held-out sets.
- **Layer:** tech · **Facts:** F-046

### emergency detector (DETMAX) *(also: danger detector, DETMAX)*

- **Plain:** A small text classifier that spots emergencies and health questions so the app answers them with reviewed text instead of model guesses.
- **Technical:** 106 MB learned classifier + rules; DETMAX (cut 6) takes the max of the detector score over the conversation window and the current turn. Weights not released (base-model licence unknown).
- **Layer:** tech

### first-aid cards *(also: health cards)*

- **Plain:** Short, fixed instructions for 32 conditions, with sources and an emergency-number line. AI-reviewed, not clinically reviewed.
- **Technical:** Reviewed card texts served when the detector fires; on the default tier the model never writes health advice. Every mention must carry "AI-reviewed, not clinically reviewed".
- **Layer:** curious

### HEALTHGAP / NUMGUARD

- **Plain:** Safety rules: questions about doses, poisoning and similar count as emergencies, and only a deterministic calculator may override a fired emergency.
- **Technical:** HEALTHGAP r2 widens the emergency predicate; NUMGUARD r3 lets only the calculator answer a numeric question the detector flagged (the lexicon guard was rejected as unsafe by review).
- **Layer:** ai

### verdict guard (self-contradiction guard) *(also: VG)*

- **Plain:** A check that catches answers which say "yes" and then argue "no".
- **Technical:** Deterministic repair of verdict/body contradictions; v3 shipped in cut 3 after a reviewer gate; v4 failed (1 WRONG of 2 fires).
- **Layer:** ai

### route gate

- **Plain:** A one-word decision by the model: search the libraries, or just chat.
- **Technical:** One-token classification by the 4B (chat vs search); 95 % on a dev chat slice; skipped for latency in cut 5 when safe.
- **Layer:** tech

## The walls

### oracle / ceiling cell *(also: ceiling, ORACLE-ST)*

- **Plain:** A deliberately "cheating" run that hands the model the right fact, to measure the most any fix in that area could ever gain.
- **Technical:** Inject the item's known fact chunk as an extra kept passage: +0.095 (+0.070…+0.122) on the 180 pack self-tests (Opus) → headroom is retrieval reach, not reading.
- **Layer:** tech · **Facts:** F-027

### closed registry (CLOSED.md) *(also: graveyard, negative results)*

- **Plain:** A public list of every idea that did not work, with how strong the test was and what new evidence would justify trying again.
- **Technical:** One row per closed lever family: arm(s), set, n, seeds, judge, result, MDE, label and a "would reopen it" line. 76 public rows (R1–R76); 98 rows privately by 2026-10-16.
- **Layer:** curious · **Facts:** F-043

## The deep tier

### deep tier *(also: deep35, H, recommended deep configuration)*

- **Plain:** An optional slower mode that uses a much bigger model which "thinks" before answering; the largest quality gain measured so far, but as of 2026-10-18 it has not run on a phone (a pending run).
- **Technical:** Cut 6 + Qwen3.6-35B-A3B UD-Q2_K_XL (≈ 3B active per token) + thinking budget 512: V-para floor-adjusted 0.436 (2 seeds, dev-style, Opus), desktop p50 ≈ 79 s; projected ≈ 1.9–2.8 min on a 12 GB phone.
- **Layer:** curious · **Facts:** F-009, F-035

### mixture of experts (MoE)

- **Plain:** A big model split into many small "expert" blocks, of which only a few work on each word, so it knows a lot but runs cheaper than its size suggests.
- **Technical:** Qwen3.6-35B-A3B: 35B total, ≈ 3B active parameters per token. 25–35B MoEs form one closed-book plateau ≈ 0.60 raw on v0.1 vs 0.487 for the 4B.
- **Layer:** curious · **Facts:** F-034

### thinking budget *(also: think 512, DT512)*

- **Plain:** How many hidden "reasoning" words the model may write before answering. 512 was as good as 1024 at about half the time.
- **Technical:** Cap on reasoning tokens; budget curve on V-para floor-adjusted: 0 → 0.33, 256 → 0.39, 512 → 0.44, 1024 → 0.42; 3072 no gain (model stops ≈ 1.3k tokens).
- **Layer:** tech · **Facts:** F-008, F-010, F-011

## A phone on a desk, and in a hand

### expert streaming (bmoe, LES) *(also: bmoe, LES, LESPORT)*

- **Plain:** Loading only the expert blocks a word needs from storage, instead of keeping the whole big model in memory.
- **Technical:** bmoe v0.28.0 (the on-device engine) is judged-equivalent to llama-server on identical contexts. An OpenBMB llama.cpp fork (LES) runs the 35B in ≈ 2.8 GiB RSS on a desktop CPU at 14–17 tok/s, judged-equivalent; phone flash speed unmeasured.
- **Layer:** tech · **Facts:** F-037, F-036

### PSS / RSS, TTFT, prefill / decode *(also: PSS, RSS, TTFT)*

- **Plain:** Ways to measure an app's memory and speed: how much memory it really uses, and how long until the first word appears.
- **Technical:** PSS = proportional set size (shared pages split fairly); RSS = resident pages. TTFT = time to first token. Prefill = reading the prompt; decode = generating tokens.
- **Layer:** tech · **Facts:** F-023

### desktop proxy and device parity *(also: BOAR Bench, device = desktop)*

- **Plain:** The exact phone engine also runs on a Mac for fast testing; real phones confirmed that the Mac gives the same judged quality.
- **Technical:** Same engine code and tree hash on desktop and phone; parity on v0.1: 12 GB-class phone 0.529 = desktop 0.529 (Haiku); 8 GB phone 0.561 vs 0.558/0.560 (Opus).
- **Layer:** tech · **Facts:** F-023, F-024

### no-network APK

- **Plain:** A build of the app with the internet permission removed, so the phone itself blocks any network access.
- **Technical:** INTERNET permission removed from the manifest: offline by construction, not by promise.
- **Layer:** curious

## The agent lab

### Power / Ceiling / Budget / Transfer blocks *(also: Rule 29, Power block)*

- **Plain:** Required parts of every experiment plan: how big an effect is expected, the best it could possibly do, what it may cost, and where it must also work.
- **Technical:** Power: expected Δ with source, n, seeds, MDE (2026-10-10). Ceiling: 0-call upper bound; launch only if ≥ 2×MDE. Budget: smoke, wall-clock caps, kill points. Transfer: a dev win must also show on the bounty-shaped set (Rule 29, 2026-10-14).
- **Layer:** ai

### step-0 gate (0-call gate) *(also: 0-call gate, replay)*

- **Plain:** A free, automatic check an idea must pass before any expensive AI judging; most ideas died here.
- **Technical:** Deterministic gate with 0 judge calls (retrieval replay, coverage counts, byte-identity), e.g. "fact chunk in top-8 ≥ bar". Of 101 closed arms counted on 2026-10-13, 54 closed at 0 judge calls.
- **Layer:** tech

### coordinator, research lanes and independent reviewers *(also: research agents, lanes)*

- **Plain:** The research was run by AI agents: one coordinator ran the experiments, specialist agents proposed ideas in their own areas, and separate reviewer agents checked wording and numbers.
- **Technical:** Coordinator session (Opus/Fable) owns the queue, freezes criteria and writes verdicts; lane agents (retrieval, models/latency, evaluation/safety, native performance, a runner, an on-call strategy agent) write technique cards and never run experiments; independent reviewer agents decide wording ("AI-reviewed").
- **Layer:** curious

### unattended research loop and ticks *(also: tick, META tick, LOOP v2)*

- **Plain:** For four days an AI coordinator woke up on a timer, advanced one experiment, logged it and scheduled its next wake-up, without a human.
- **Technical:** 133 ticks (28 idle), 2026-10-11 → 10-14; META tick every 8 ticks re-ranks the backlog; LOOP v2 (2026-10-14) moved queueing to machine-side runners.
- **Layer:** tech · **Facts:** F-031

### handoff

- **Plain:** A file that lets a fresh AI session take over the coordinator role with no memory of the previous one.
- **Technical:** Dated HANDOFF-*.md with a §0 to paste into a new session: state, running jobs, rules, next steps.
- **Layer:** tech

## Knowledge packs

### 180 pack self-tests *(also: pack-matched set, the 180)*

- **Plain:** Twenty public practice questions per knowledge pack, written from the pack's own text, used to see whether a pack helps.
- **Technical:** 9 packs × 20 agent-written items whose fact sits in a known chunk; lets the retrieval chain be traced end to end. Dev data, never claim evidence.
- **Layer:** tech · **Facts:** F-025

### knowledge pack *(also: packs)*

- **Plain:** A downloadable offline library (one file) of articles on one topic that the app searches before answering.
- **Technical:** SQLite "format 2" (format-v3 adds chunk vectors) with per-row licence and attribution, a card, 20 public self-tests, a coverage probe and a crowding check. Licences: PD, CC0, CC BY, CC BY-SA only. 11 packs published on 2026-10-13.
- **Layer:** curious · **Facts:** F-025

### retrieval funnel: reach → keep → read *(also: reach, keep step)*

- **Plain:** Reach: is the right passage found? Keep: does it survive the filter into the prompt? Read: does the model use it correctly?
- **Technical:** reach = fact chunk in the raw top-k; keep = grounding filter that drops off-topic/unsafe passages and compresses the rest; read = reader output given the kept context.
- **Layer:** tech · **Facts:** F-027

### crowding

- **Plain:** Installing many libraries at once lets a big general one take the few slots the right small one needed.
- **Technical:** All packs installed vs the matching pack only: −0.019 (−0.035…−0.003) Opus on the 180 self-tests; packs above 0.40 of kept slots are user-selected only.
- **Layer:** curious · **Facts:** F-026

### HEADPASS-X2b *(also: X2b, HEADPASS)*

- **Plain:** The one retrieval change that worked: also feed the model the passages next to the best-matching one, plus a few found by meaning, within a fixed size limit.
- **Technical:** After the keep step, append the top article's neighbour chunks + ≤ 2 dense candidates under +600 prompt tokens: +0.066 (+0.043…+0.091) Opus on the 180 (dev); inert on the claim kit.
- **Layer:** tech · **Facts:** F-028

## Measuring the measurer

### L1 / L2 judges (triage and confirmation) *(also: Haiku triage, Opus confirm, judge ladder)*

- **Plain:** A cheap AI judge screens ideas first; the expensive judge only confirms promising ones and produces the published numbers.
- **Technical:** L1 = Claude Haiku 5.5-low (replaced Sonnet-low on 2026-10-07), N = 4 shards, both orders, on 20-item slices, paired vs a named control; never an absolute L1 ratio. L2 = Claude Opus judge.v1, both orders, two seeds, for confirmations and claim numbers. Haiku compresses gaps (0.70–0.95× Opus on pack arms).
- **Layer:** ai · **Facts:** F-019

### near-miss rule

- **Plain:** If the cheap judge lands very close to a decision line, the expensive judge decides instead.
- **Technical:** A Haiku Δ within 0.01 of a criterion threshold is re-judged with Opus on the same ids before any verdict.
- **Layer:** ai

### cross-family judge (XFAM) *(also: XFAM, cross-family)*

- **Plain:** The same answers were re-scored by an AI judge from a different company, to see whether a Claude judge treats Claude-written references kindly or harshly.
- **Technical:** Post-hoc re-judge of existing traces with OpenAI gpt-5.6-sol (via the Codex CLI), same rubric, orders and blinding (408 calls V-para, 660 v0.2). Scores ≈ +0.10 higher on both sets, ranking unchanged (Spearman 0.88–0.97), win-rate 0.00–0.06. Not pre-registered.
- **Layer:** curious · **Facts:** F-017, F-018

### judge family / self-preference

- **Plain:** The questions, the reference answers and the judge all came from the same AI company, which may bias the scores.
- **Technical:** Claude wrote v0.2 and V-para items and the references, and judged. Self-preference direction is measured only by one post-hoc cross-family re-judge. v0.3 is to be written outside the Claude family.
- **Layer:** ai · **Facts:** F-017

### common-mode CI *(also: CI_cm)*

- **Plain:** A wider interval that also counts run-to-run randomness, not just which questions were asked.
- **Technical:** CI_cm = point ± 1.96·sqrt(SE_item² + (σ_run/√seeds)²), σ_run raw 0.020 / floor-adjusted 0.025 on V-para (SEEDVAR). Used for deep-tier rows since 2026-10-11.
- **Layer:** ai · **Facts:** F-009, F-012

### seed and seed noise *(also: seed, SEEDVAR, seed-noise rule)*

- **Plain:** Running the same setup again with a different random seed gives different answers and a different score; that variation is seed noise.
- **Technical:** Seed = sampling seed of answer generation. Same deep configuration, s42 vs s43: Δ −0.039 (−0.072…−0.011) raw on V-para. Rule since 2026-10-16: a one-seed deep-tier Δ < 0.05 on V-para is noise (was 0.03).
- **Layer:** tech · **Facts:** F-020, F-012

### judge noise (test-retest) *(also: JUDGEVAR)*

- **Plain:** Re-judging the exact same answers changes the score by almost nothing.
- **Technical:** σ_judge ≈ 0.003 raw / 0.004 floor-adjusted, per-item r 0.96, winner 51/51 (Opus, 102 calls): an order of magnitude below seed noise.
- **Layer:** ai · **Facts:** F-019

### winner's curse

- **Plain:** If you pick the best of many setups on the same questions, it will look a bit better than it really is.
- **Technical:** The recommended deep configuration was the best of ≥ 8 deep configurations on V-para; expect a ≈ 0.01–0.02 discount on new data.
- **Layer:** ai · **Facts:** F-009

### reference length share (LENGTHSHARE)

- **Plain:** Some of the gap to the reference is just that the reference is longer.
- **Technical:** Re-judging the same answers against references condensed to ≤ 80 words: floor-adjusted 0.412 → 0.514, ≈ 17 % length / 83 % substance (1 seed, dev-style).
- **Layer:** ai · **Facts:** F-021

## A smaller engine for 8 GB phones

### refuse by default / show anyway *(also: show anyway)*

- **Plain:** With no source found, the app declines and offers a button to see the model's unsourced answer behind a warning.
- **Technical:** Author decision 2026-10-20 20:24; narrowed on 2026-10-21: show-anyway only behind a second confirmation and never on health; validated for the 1.7B / Gemma only. The closed app (2026-10-24) keeps the warning line and shows sources.
- **Layer:** curious · **Facts:** F-1534

### confident error (CE, CE-unwarned) *(also: CE, CE-unwarned)*

- **Plain:** A wrong answer shown to the user without a warning.
- **Technical:** An answered item with judge.v1 mean correctness ≤ 1.5 of 5, not refused; "unwarned" = shown without the warning line. Counted per 100 questions under a named mode, model and judge; judge retest noise ± 1.3 per 100.
- **Layer:** curious · **Facts:** F-2187

### GATE v2 (two-stage screen) *(also: two-stage screen, null run)*

- **Plain:** A cheap first test on the items the current build gets wrong plus items it gets right, with a "do nothing" run to see how much changes by chance.
- **Technical:** Net = problems fixed − new visible confident errors; GO iff net ≥ max null-arm net + 2 (null changes such as a new seed fix 23-31 % of problems); stage 2 = full MAIN 97.
- **Layer:** ai · **Facts:** F-1393

### MAIN 97 / CV5 51 *(also: MAIN 97, CV5 51)*

- **Plain:** The two development sets used for most screens after 2026-10-18.
- **Technical:** MAIN 97 = 57 public v0.1 items + 40 cooking/money pack self-tests (dev); CV5 51 = 51 v0.1 ids used for Claude Opus ladders (dev). Neither is held-out.
- **Layer:** tech · **Facts:** F-2077

## A second ruler (bench v0.4)

### ruler (bench v0.4) *(also: v0.4, bench ruler, ruler v0.4)*

- **Plain:** A fixed set of 75 test questions, frozen on 2026-10-20 before any system answered them, meant to give the final score of the submitted app.
- **Technical:** 75 items = 71 headline + 4 anchor questions taken from Vitalik Buterin's public post (scored outside the headline); written half by Claude and half by OpenAI gpt-5.6-sol via the Codex CLI, cross-fact-checked; sha f9ad2f2f. Not written outside the Claude family (a stated deviation). First exposed to two engines on 2026-10-24.
- **Layer:** curious · **Facts:** F-2070, F-1353, F-2108

### ruler spec (RULER-SPEC v1) *(also: RULER-SPEC, spec r3, spec r4)*

- **Plain:** The written procedure for scoring the ruler: which references, judges, metrics and gates, frozen before scoring.
- **Technical:** r2 (2026-10-20) was a draft; r3 (2026-10-21 20:48, sha 0fac2286) is the first frozen spec (judge.v1 + DECLINE2STAGE, verdict arm A∪, two judge families); r4 (21:18, sha 82772e33) adds the information-available split (FACT-AVAIL) and ORACLE / ORACLE-0 rows. Spec files are private.
- **Layer:** tech · **Facts:** F-1542, F-1543

### U-total *(also: ruler U, U (ruler))*

- **Plain:** The ruler's headline number: how much of a reference answer's useful content the app delivers, over all 71 headline questions.
- **Technical:** Ratio of sums: Σ(app mass) / Σ(reference mass), where each mass is the mean of correctness, completeness and usefulness minus 1 (judge.v1, 1-5 scale), so the rubric floor maps to 0; detected non-answers are set to 0 by DECLINE2STAGE; health items weigh 0.5 (weight-1 printed beside). Verdict statistic = the lower of the two judge families per bootstrap draw; "meets the bar" needs CI low > 0.50. A different metric from the judge.v1 V-para / v0.2 ratios: never compare across.
- **Layer:** curious · **Facts:** F-1529, F-1543

### DECLINE2STAGE *(also: two-stage judge, RULING R1)*

- **Plain:** A first check that gives zero to answers that do not try to answer, before the usual judge scores the rest.
- **Technical:** Stage 1: a classifier asks whether the answer attempts an answer; if not, U = 0; otherwise judge.v1 scores it unchanged. Adopted as RULING R1 (2026-10-21) after the decline arm was invalid under judge.v1 (a bare refusal scored U 0.016-0.058); a coordinator override of a frozen FAIL, accepted with conditions by the spec reviewer. The decline offset D 0.058 is kept as a sensitivity row (U_net).
- **Layer:** ai · **Facts:** F-1529, F-1637

### FACT-AVAIL (information-available split) *(also: information-available split, FACT-AVAIL)*

- **Plain:** Labels saying, for each ruler question, whether the answer is actually written in the installed knowledge packs.
- **Technical:** Pre-registered per item: AVAILABLE (≥ 0.5 of checklist points stated in the persona packs) / PARTIAL / NONE; a lower bound. On the 71 headline items: 19 / 25 / 27 (strict 15 / 23 / 33). Labels are quarantined until the result card; counts only.
- **Layer:** ai · **Facts:** F-2111, F-1578

### A∪ (verdict arm) *(also: A-union, verdict arm)*

- **Plain:** The app with every persona knowledge pack installed at once, used for the verdict so no question gets a hand-picked pack.
- **Technical:** All six persona packs installed once for all items (wikivoyage, visa, crypto, medlineplus, firstaid, factbook; ≈ 435 MB); per-family arm A is a labelled row only, because routing packs by topic would be oracle routing.
- **Layer:** tech · **Facts:** F-1391

### ORACLE / ORACLE-0 *(also: information effect)*

- **Plain:** The same model answering the same questions with and without the supporting passages handed to it.
- **Technical:** ORACLE − ORACLE-0 on the same items = the information effect (what delivering the right passages is worth). Defined in spec r4; not run as of 2026-10-24.
- **Layer:** ai · **Facts:** F-1543

## Delivery, not coverage

### delivery (kept / delivered fact) *(also: delivered fact, chunk-level delivery)*

- **Plain:** Whether the passage that holds the answer actually reaches the small model's prompt after search and compression.
- **Technical:** Counted at chunk level from 2026-10-22: the key fact's quote sits inside one kept chunk (article-level counting, "a chunk of the right article", overstated delivery by 8-13 facts). Article-level and chunk-level counts are never pooled.
- **Layer:** curious · **Facts:** F-1550, F-1856

### pack self-test *(also: pack-written self-tests)*

- **Plain:** Questions written from a pack's own text, used to check that pack; they favour the pack by construction.
- **Technical:** An on-topic upper bound, not casual traffic: self-test gains (e.g. PACKPROOF +0.23 correct-any) did not transfer to real dev items in the same week (delivered-vs-not +0.001 between items).
- **Layer:** tech · **Facts:** F-1704

### global-IDF merge (gidf) *(also: gidf)*

- **Plain:** Re-scoring each pack's keyword hits with word rarity computed across all installed packs, so small packs compete fairly with big ones.
- **Technical:** Part of the adopted search stack SEFIX-124 (gidf + SEFIX F1/F2/F4); chunk-level delivered MAIN facts 28 → 42 of 92; answer gain +0.013 (−0.008…+0.035, Claude Haiku, 2 seeds), not a lever.
- **Layer:** ai · **Facts:** F-1549

### SEFIX-124 *(also: SEFIX, search fixes)*

- **Plain:** The adopted search fixes for question-and-answer packs.
- **Technical:** Global-IDF merge plus three lexical fixes (F1 lead-vector thread pick, F2 domain words kept, F4 relaxed keep rule); F3 (a health no-source fallback) was withdrawn because it made safety probes worse (unsafe 9 → 13 of 65).
- **Layer:** tech · **Facts:** F-1549, F-1855

### W78 stack *(also: reading-cost stack)*

- **Plain:** A compact search index stored inside each pack, so a question reads far less data from storage.
- **Technical:** 1-bit sign sidecar + int8 rescore + IVF lists stored in the pack: 125.09 → 21.26 MB read per question on a desktop; phone effect unmeasured.
- **Layer:** ai · **Facts:** F-2103

### pack shaping (shaped factbook) *(also: shaped factbook, factbook v2)*

- **Plain:** Rewriting table-like pack text into short sentences that name their subject, without adding facts.
- **Technical:** Shaped factbook v2: fact chunk kept 7 → 15 of 20; correct 5 → 10 of 20; Claude Opus U 0.316 → 0.436 (+0.121, +0.030…+0.221; 2 seeds, n 20, dev); NOT-CONFIRMED by its frozen rule (one new warned confident error). In ENGINE-RC; publication of the pack waits for the author.
- **Layer:** curious · **Facts:** F-2104, F-1718

### K13 kit *(also: K13)*

- **Plain:** The default set of 13 knowledge packs used in every closing test.
- **Technical:** Includes the Wikipedia packs (kept after NOWIKI: removing them lost 9 of 42 delivered MAIN facts and 10 public v0.1 items).
- **Layer:** tech · **Facts:** F-1859

### grounded-dose rule *(also: GROUNDED-DOSE)*

- **Plain:** A health answer counts as safe only if it is the fixed safe text or every dose it states appears in a source shown with it.
- **Technical:** Frozen 2026-10-24 19:1x; scorer extracts figures with units, normalises them and matches them numerically against the shown passages and the question; replaced kept-list proxies. Known limit: a grounded figure can be a toxic threshold read as a dose (arm B).
- **Layer:** ai · **Facts:** F-2202, F-2205

## Closing the research: what a small model needs

### outcome labels (CWS, correct-any, WU, WW, HU) *(also: correct-any, CWS, WU, wrong-unwarned, UXMATRIX labels)*

- **Plain:** Each answer is put into one class: right with the right source shown, right from memory, wrong with no warning, wrong with a warning, or an honest "unknown".
- **Technical:** Shares of n items labelled by Claude Haiku 5.5-low under the UXMATRIX protocol: CWS = correct with the right source shown; CFM = correct from memory; correct-any = CWS + CFM; WC/WU = wrong with no warning; WW = wrong with the warning line; HU = honest unknown; RW = refused wrongly. Not a ratio to a reference: never compare with the judge.v1 ratio or with U-total.
- **Layer:** curious · **Facts:** F-1704, F-1727, F-1709

### conditional thesis *(also: pack thesis)*

- **Plain:** The author's closing claim, in the form the tests support: the app is right about two times in three when the right passage reaches the model.
- **Technical:** Stated by the author on 2026-10-23 as "right whenever the content is in a knowledge pack"; PACKPROOF supports only the conditional form: correct-any 0.65 when the item's own article is kept vs 0.28 when not, with the pack installed 0.48 vs 0.26 without (n 180 pack-written self-tests, Claude Haiku labels, one seed, dev); no pack reached the 0.75 bar.
- **Layer:** curious · **Facts:** F-1690, F-1704, F-1707

### ENGINE-RC *(also: research engine release candidate)*

- **Plain:** The closed research engine assembled as one build for validation.
- **Technical:** SEFIX-124 search + W78 reading-cost stack + shaped factbook + reworded warning banner, Succinct style, Deep off; passed every no-LLM suite on 2026-10-24 (desktop only). The research engine, not the submitted app.
- **Layer:** tech · **Facts:** F-2105

### warning line *(also: "passages found don't support this answer", Not found banner)*

- **Plain:** A line the engine puts before an answer its kept passages do not support, so the reader knows it comes from model memory.
- **Technical:** Two texts: "Not found in this phone's offline library…" when nothing is kept, and "The passages found don't support this answer…" when passages are kept but every citation is stripped. A fixed-banner bug showed "Not found" on 37 of 97 answers that kept passages; fixed (0 after the fix).
- **Layer:** curious · **Facts:** F-1725

### desktop twin *(also: twin)*

- **Plain:** Running an app's engine on a desktop harness instead of the phone.
- **Technical:** Counts as dev or parity evidence, never as a verdict; every closing test and both first ruler v0.4 runs (2026-10-24) were desktop twins.
- **Layer:** tech · **Facts:** F-1689

## One simple app: LabRat

### BoarLite *(also: closed app, LabRat)*

- **Plain:** The author's own closed, offline chat app, declared the bounty submission on 2026-10-24; renamed LabRat on 2026-10-25.
- **Technical:** No internet permission; the full K13 pack kit bundled in one APK (≈ 3.04 GB); Qwen3-1.7B fixed; Succinct only (no Deep, Detailed or length option); factbook v1 (the shaped v2 was dropped on 2026-10-24 18:03); a fixed line under every answer instead of a warning trigger; health gate B+FU; QuickMath; search port ON_NO_HEALTH. Final candidate b4ef94f3 as of 2026-10-24 19:40 (UI-only commits after it), smoke-tested on a Pixel 8a; its desktop-twin ruler scores were published by the author's decision of 2026-10-25 as history (F-2215; before the Rat persona line). Renamed LabRat on 2026-10-25 (7788924a), which also adds the Rat persona line to the grounding prompt after the ruler run on b4ef94f3; product cleanup the same night (Expo/React Native tree, Portuguese, PIN and long-chat summary removed).
- **Layer:** curious · **Facts:** F-1703, F-1863, F-2198, F-2210, F-2224

### health gate B+FU *(also: health gate, HealthGate, B+FU)*

- **Plain:** BoarLite's rule for health questions: when no trusted health source is found, it shows a fixed safe text with the emergency number instead of a model answer.
- **Technical:** Predicate = the app's lexical health test OR 11 lexical rules (B: drugs, doses, vitals, child fever, symptoms, poisoning, alcohol, pregnancy, child dosing, trauma, altitude, diving) OR a short follow-up of a health turn (FU); runs after retrieval; health sources = firstaid, MedlinePlus, health Q&A packs. Final candidate: 41 of 65 safety probes fixed text, 0 new false fires on 251 non-health dev items; rules fitted on the probes.
- **Layer:** tech · **Facts:** F-2192, F-2193, F-2210

### QuickMath

- **Plain:** Unit conversions and simple arithmetic are worked out by code, with no model and no sources.
- **Technical:** BoarLite 43b50410: runs at the start of the answer pipeline; never on health-gated turns or turns after a health turn; exposure questions go to the health gate instead.
- **Layer:** tech · **Facts:** F-2200

### ON_NO_HEALTH *(also: ON-NH, search port)*

- **Plain:** BoarLite uses the improved search for every question except health questions, which keep the old, more cautious search.
- **Technical:** SearchPort mode: SEFIX-124 delivery + head pass + X2b appends compressed within 1.2× (SearchPort.fit), off on turns the health predicate fires on (incl. follow-ups). Delivery MAIN 26 → 40; its frozen criterion failed by the letter (S1 6 vs 4 ungrounded figures) and it was merged under the author's prior condition.
- **Layer:** ai · **Facts:** F-2207, F-2209

### fixed line *(also: May contain errors; check the source.)*

- **Plain:** One short line under every BoarLite answer: "May contain errors; check the source."
- **Technical:** Replaced the ported per-answer warning trigger (D4) on 2026-10-24 18:03; drawn outside the answer text, not on the fixed health text or computed answers.
- **Layer:** curious · **Facts:** F-2189, F-2211

### LabRat *(also: formerly BoarLite)*

- **Plain:** The submitted offline chat app's name from 2026-10-25; it was called BoarLite before.
- **Technical:** Renamed at the app maintainer's request in commit 7788924a; same package id and bundled knowledge as BoarLite; the grounding prompt's identity line names the assistant Rat (added after the RULER-FINAL run on b4ef94f3). Measured on the phone by DEVICE-FINAL.
- **Layer:** curious · **Facts:** F-2224, F-2225, F-2235

### Rat *(also: the assistant)*

- **Plain:** The name LabRat's assistant uses for itself in its answers.
- **Technical:** Set by one identity line in the grounding prompt ("You are Rat, the assistant in LabRat…", 7788924a), replacing "You are BOAR…"; the only prompt change between the ruler engine b4ef94f3 and LabRat 7788924a named in the DEVICE-FINAL criterion.
- **Layer:** curious · **Facts:** F-2225

### DEVICE-FINAL *(also: final on-phone matrix)*

- **Plain:** The last benchmark run: the submitted app answers the test sets on the phone itself, overnight.
- **Technical:** Frozen criterion 2026-10-25 03:3x: LabRat 7788924a on a Pixel 8a; M1 ruler v0.4 × seeds 42/43/44 (Claude Opus all seeds, OpenAI gpt-5.6-sol seed 42), M2 65 safety probes, M3 140 on-K13 self-tests, M4 UXMATRIX 60, M5 speed/memory/offline. Claim numbers = M1 + M5. Running as of the 2026-10-25 update; no results recorded.
- **Layer:** tech · **Facts:** F-2227, F-2228

## Where it stands (live)

### the bar (0.50) *(also: half as good, 50 % bar)*

- **Plain:** The target: BOAR's answers should be worth at least half of what a frontier AI with web search gives.
- **Technical:** Operationalised as floor-adjusted ratio CI low ≥ 0.50 (primary target, from 2026-10-06) and raw ratio CI low > 0.50 on both V-para and v0.2 (formal rule of the 2026-10-02 analysis plan). As of 2026-10-18, not reached under the Claude judge on held-out data; the research is open and pending runs could change this (data/status.json).
- **Layer:** curious · **Facts:** F-004

### formal raw rule vs primary target

- **Plain:** There are two ways to read the bar; the stricter one (floor-adjusted) is the one the project leads with, and as of 2026-10-18 it has not been met.
- **Technical:** Formal rule (plan 2026-10-02): raw CI low > 0.50 on both sets — met only by the deep tier with thinking on dev data. Primary target (2026-10-06): floor-adjusted CI low ≥ 0.50 on V-para — met by no configuration as of 2026-10-18 (best 0.436, CI high 0.472).
- **Layer:** ai · **Facts:** F-004

### lower-judge rule

- **Plain:** When two judges disagree, the project publishes the lower (less flattering) number as the headline.
- **Technical:** Claude Opus stays the headline judge because it is the stricter family; cross-family numbers are printed beside it, labelled post-hoc, and the judge family is named next to every ratio.
- **Layer:** tech

### claim text *(also: claim draft)*

- **Plain:** The text for the bounty that says, with numbers and caveats, what BOAR does and does not achieve; it follows the current standing and is posted at closure.
- **Technical:** Claim draft v4.2.4 (2026-10-17): "BOAR is not shown to be half as good as frontier AI with web"; judge family named next to every ratio; leads with win-rate.
- **Layer:** tech · **Facts:** F-004

## Open fronts and hand-off

### lite tier *(also: 1.7B)*

- **Plain:** A smaller model option for phones with 4–6 GB of RAM: faster, less accurate, behind the same safety rules.
- **Technical:** Qwen3-1.7B Q4_K_M + X2b; matches the plain 4B only on the 180 pack-matched dev items; −0.111 vs the 4B on the claim kit; thinking stays off.
- **Layer:** tech

### submitted app vs research engine *(also: native app)*

- **Plain:** The app actually submitted to the bounty is the app maintainer's own rewrite; the research numbers describe the engine it partly ports.
- **Technical:** Submission vehicle = the app maintainer's native Kotlin app (from 2026-10-15); it ports retrieval and prompts but not the health path or deterministic answers. All research numbers are for the TypeScript research engine (cut 7).
- **Layer:** curious

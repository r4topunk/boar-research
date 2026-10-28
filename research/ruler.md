# 2 · Building a ruler

> Closed record · research record 1.0 · as of 2026-10-28; the author closed the research lines on 2026-10-23. Current standing, not a final result: Open fronts: https://r4topunk.github.io/boar-research/data/status.json.
>
> Final · as of 2026-10-28 · 0 of 71 wins on the phone, U-total 0.165 (Claude) / 0.242 (gpt-5.6-sol), below the 0.50 bar

- Page: https://r4topunk.github.io/boar-research/research/ruler/ · Markdown twin: https://r4topunk.github.io/boar-research/research/ruler.md · Whole paper: https://r4topunk.github.io/boar-research/llms-full.txt · Index: https://r4topunk.github.io/boar-research/llms.txt
- Span: 2026-10-01 → 10-03

**In one sentence.** We built the measurement before the product: frozen frontier-plus-web reference answers, a pairwise judge that sees every pair in both orders, and pass/fail rules fingerprinted before each run.

## For curious readers {#curious}

#### A frozen answer key

For every test question, a top AI model with web search wrote one reference answer. We froze those answers and fingerprinted them, so every later test is compared with exactly the same text. That reference is our stand-in for "the internet plus a frontier AI".

#### A judge that can't peek

A strong AI model acts as the judge. It sees the question, BOAR's answer and the reference side by side, with links and source lists removed so it cannot tell which answer had the web. It scores both from 1 to 5 on correctness, completeness and usefulness, and picks a winner.

#### Then we swap them

Judges, human or AI, tend to favour whichever answer they read first. So every pair is judged twice, once in each order. If the judge changes its mind when the order flips, the question counts as a tie.

#### Rules written before the experiment

Every experiment got a pass/fail rule written down before it ran, and the rule file was fingerprinted (a sha256 hash), so nobody could quietly move the goalposts after seeing the result. Over the month there were dozens of these, and an outside reviewer later re-checked 16 of 17 sampled fingerprints as matching.

#### Practice questions and a sealed exam

Some question sets were public practice. Others were sealed: the people and agents building the app were never allowed to read them, and every time a script touched one, it was written in a ledger. When a sealed set leaked, we said so and demoted it to practice. (That happened; chapter 5.)

**In one sentence card:** "Every answer is graded twice, blind, against a frozen frontier answer, under rules written before the test." Badge: v0.1 public practice set, 60 questions (57 graded).

*Facts: [F-067] [D-002] [F-125] [F-649] [F-235] [D-019] [D-009] [F-1169] [D-006] [D-015] [D-037]*

## For tech people {#tech}

### One harness, one trace format, a judge that sees both orders

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

## For AI professionals {#ai}

### The record for this chapter

**Key facts:**
- The desktop runner executes the app's real answering engine: 54 questions in 2 min 34 s, 0 errors [F-1246].
- Run-to-run noise of identical configurations: Δ 0.031, 17/60 labels changed [F-103] [F-104].
- References: Claude Opus with web search, frozen once, hashed, never regenerated ([F-067]; [D-002]; "Provenance").
- Judge: three 1–5 axes (correctness, completeness, usefulness), blinding strips links and citation markers, both A/B orders, disagreement = tie [D-019].
- Public bench v0.1: 60 English questions, 57 judged; 27 items borrowed from a competitor's list were replaced [F-123] [D-004].
- Held-out v0.2 (110 items) and the bounty-style V-para (58 items, 51 judged) were frozen within three days [E-035] [E-065].
- The analysis plan was frozen and hashed before any v0.2 item existed [D-020].
- Calibration ladder on v0.1 (raw, no-web vs the Opus+web reference): Fable 1.048, Opus 1.029, Sonnet 0.950, Haiku 4.5 0.653 [F-128]. The bar is effectively "≥ 50 % of a frontier model".

**Key decisions:** [D-003] (own thin harness, seven axes never averaged), [D-003], [D-007], [D-005] (report an effect only above the MDE), [D-006] (freeze every criterion; blind sets never read by researchers), [D-015] (develop on v0.1, confirm only on v0.2).

**Turning point:** 2026-10-01 23:00: the rule that an effect is reported only if it exceeds the minimum detectable effect, after noise turned out to be as large as the effects being chased.

### Sets

v0.1 is a public development set of 60 English questions (57 judged; 3 venue-list items scored against OpenStreetMap). 27 items originally borrowed from a competitor's list were replaced with original items in the same slots (max word-Jaccard 0.30 against the removed items). v0.2 (110 items, written by two Claude-family writer subagents, 55 each) was frozen on 2026-10-02 as the held-out set; its plaintext reached a private repository's git history the same day and one item was printed into a researcher's trace scan on 2026-10-03, and on 2026-10-06 it was declared burnt and reclassified as development data. V-para (58 items, 51 judged; bounty-style paraphrases written by an Opus subagent) was held-out for the two 4B claim runs (2026-10-05/06) and is development-style for everything measured after 2026-10-06. All of these sets were retired and published on 2026-10-27 in boar-bench (bench/heldout/), with their runs in boar-traces; items are byte-identical to the hashes committed before they were opened, except documented redactions (old and new hashes in bench/heldout/HASHES.md). The 180 pack self-test items are agent-written from pack text and are development data by construction. No unexposed English set exists as of 2026-10-24: v0.3, specified to be written outside the Claude family, was dropped on 2026-10-18 [D-123], and the second ruler v0.4 (§3.6) is half Claude-written and was exposed on 2026-10-24. From 2026-10-18 most screens used MAIN 97 (v0.1 57 + 40 cooking/money pack self-tests) and CV5 51 (v0.1 judged items), both development data.

*Facts: [F-123] [F-124] [F-217] [F-209] [F-218] [F-231] [F-129] [F-130] [F-990] [D-004] [D-037] [D-055]*

### References

References were generated once by Claude Opus with web search and fetch (prompt reference.v1), 2026-09-30 → 10-02, one call at a time, and frozen with sha256; they are never regenerated. They average ≈ 280 words (p10/p50/p90 = 251/280/318) and ≈ 4.9/5 on the judge's rubric; the 4B's answers median ≈ 51–53 words.

*Facts: [F-067] [F-182] [F-365]*

### Judge protocol

The judge receives the question, the system answer and the reference as A/B, with think blocks, trailing source lists, URLs, markdown links, [n] markers and bold stripped. It scores each answer 1–5 on correctness (a material wrong claim caps it at 2; an uncorrected false premise at 1), completeness and usefulness, and names a winner; the system prompt forbids rewarding length, format, confidence or tone. The first order per item is drawn by a seeded PRNG (seed 7); both orders always run. Same winner across orders keeps it; disagreement is a tie; rubric scores are averaged across orders. Position consistency is 96.5–100 % for Opus and Haiku.

*Facts: [F-166]*

### 4 Discipline: frozen criteria, exposure ledger, fail-closed judging, and a judge funnel

Each experiment ("arm") compares one change with a named control under a criterion written before the deciding run and frozen by sha256; verdicts may add dated addenda but not edit the criterion. 65/65 criterion hashes verified on 2026-10-10, and an outside critic re-verified 16 of 17 on 2026-10-16. From 2026-10-10 every criterion carries a Power block (expected Δ with its source, n, seeds, MDE); before that, 0 of 32 criteria frozen since 2026-10-07 stated one. From 2026-10-14 criteria also carry a Ceiling block (0-call upper bound; launch only if ≥ 2 × MDE) and a Budget block (smoke test, wall caps, kill rule). Judging is a funnel: deterministic 0-call gates (replays, counting) → Haiku L1 on a stratified random 20-item slice (futility screen only) → Opus confirmation and all claim numbers; a near-miss rule escalates any Haiku Δ within 0.01 of a threshold to Opus. Held-out sets are touched only by scripts that print aggregates; every touch is a ledger row (126 dated rows at audit). Negative results under-powered for the effect of interest are labelled "not detected at MDE x (n, seeds)" and kept in a registry with a reopen condition.

**Second phase (2026-10-18 → 10-24).** About 200 further arms ran ([X-198]…), mostly 0-LLM replays and Haiku screens under a two-stage gate whose bar is set from measured null arms (GATE v2, [D-141]); seven open decisions were delegated by the author to the coordinator on 2026-10-18 [D-123]; one frozen FAIL was overridden with the spec reviewer's conditions (RULING R1, [D-144]); an overnight run generated answers and judged none, leaving judge runs to the author [D-176]. Who decided is labelled on every decision row.

**Limitation stated here:** the planned 40-pair blind human label check was not done [F-211].

*Facts: [D-009] [F-1169] [D-061] [D-094] [D-057] [D-064] [D-073] [F-843] [F-185] [F-231]*

## Facts cited {#facts}

Resolve every [F-…] marker in https://r4topunk.github.io/boar-research/data/facts.json. Each line gives the claim, the number with its metric family, set and status, judge, n, seeds, CI, date and caveat.

<!-- lint:exempt:start -->
- [F-067] References were generated by Claude Opus 5.5 with WebSearch+WebFetch, one call at a time, 5 s gap, 1 retry, prompt reference.v1. 60 refs · set v0.1 (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-09-30 → 10-02 · caveat: references are AI output, "not ground truth"
- [F-103] Run-to-run noise of identical configurations was Δ 0.031 (17/60 labels changed) 0.031 · set v0 dev (dev, development data) · judge Opus · n UNKNOWN · seeds UNKNOWN · CI 60 items · date 2026-10-01 · caveat: motivated the MDE rule
- [F-104] Run-to-run noise on the night of 2026-10-01 was Δ 0.031 with 17/60 labels changed. 0.031 · set v0.1 (status UNKNOWN) · judge Opus · n 60 · seeds UNKNOWN · CI n 60 · date 2026-10-01 · caveat: pre-dates the stats rules
- [F-123] The public bench has 60 English questions; 57 are judged (3 venue-list items scored against OpenStreetMap instead). 60 / 57 · set v0.1, public dev (public dev, development data) · judge UNKNOWN · n 60 · seeds UNKNOWN · CI n 60 · date 2026-10-02 · caveat: 25 items quote/paraphrase a named public author's posts
- [F-124] v0.1 composition: explanation 11, reasoning 11, comparison 7, crypto 7, honesty-refusal 6, health 4, synthesis 3, local-food 3, danger-situation 3, danger 2, travel-practical 2, travel-local 1. 12 categories · set v0.1 (status UNKNOWN) · judge UNKNOWN · n 60 · seeds UNKNOWN · CI n 60 · date 2026-10-02
- [F-125] The judge scores each answer 1-5 on three axes: correctness (a material wrong claim caps it at 2; an uncorrected false premise at 1), completeness, usefulness. 3 axes, 1-5 · set all sets (status UNKNOWN) · judge judge.v1 · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-02
- [F-128] Calibration ladder on v0.1: Claude models with no web vs the Opus+web reference — Fable 1.048, Opus 1.029, Sonnet 0.950, Haiku 4.5 0.653 (raw). raw 1.048 / 1.029 / 0.950 / 0.653 (judge.v1 ratio) · set v0.1 dev (dev, development data) · judge Opus · n UNKNOWN · seeds UNKNOWN · CI 1 run × 57 each; e.g. Opus 1.007-1.053 · date 2026-10-02 · caveat: the reference behaves like "frontier model memory", web adds little on these items
- [F-129] v0.2's items and references were written by Claude-family subagents (two blind writers, 55 each); V-para by an Opus subagent. Claude-family · set v0.2, V-para (status UNKNOWN) · judge UNKNOWN · n 51 (inferred from set) · seeds UNKNOWN · CI not computed · date 2026-10-02/03 · caveat: exact writer model id not recorded
- [F-130] v0.2 writers converged: 36 same-topic pairs out of 55 between two Claude writers, then 7 of 37 again among rewriters. 36/55; 7/37 · set v0.2 (status UNKNOWN) · judge UNKNOWN · n 110 (inferred from set) · seeds UNKNOWN · CI not computed · date 2026-10-02 · caveat: citation fix (l.44 is an instruction step)
- [F-166] Position consistency (both orders agree) is 96.5-100 % for Opus and Haiku, 86-93 % for the local Gemma judge. 96.5-100 % · set v0.1 dev (dev, development data) · judge several · n 57 · seeds UNKNOWN · CI n 57 · date 2026-10-07
- [F-182] The reference answers score ≈ 4.9/5 on average, so the ratio behaves like an absolute rubric mean rather than a head-to-head. ≈ 4.9 (judge.v1 ratio) · set v0.2, V-para (status UNKNOWN) · judge Opus · n 51 (inferred from set) · seeds UNKNOWN · CI not computed · date 2026-10-10 · caveat: public citation fix: per-dimension reference means (4.63-5.00) are at l.88-91, not l.66-69
- [F-185] 0 of 32 criteria frozen between 10-07 and 10-10 stated an expected Δ or MDE. 0/32 · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-10 · caveat: fixed by the Power block
- [F-200] Fail-closed judge: `--strict` exits before any call if a trace/reference is missing; `--floor-errored` scores a failed answer 1/1/1 instead of dropping it. flags · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-11
- [F-209] V-para: 58 items (51 judged + 7 venue), 19 full generation runs and 12 slices of 20. 58 / 19 / 12 · set V-para dev-style (dev-style, development data) · judge UNKNOWN · n 51 (inferred from set) · seeds UNKNOWN · CI not computed · date 2026-10-13
- [F-211] The planned 40-pair blind human label check (seed 7, stratified) has not been done. 0/40 · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-13
- [F-217] The v0.2 held-out set had 110 items, 12 full generation runs and 10 full Opus judge passes before being ruled dev. 110 / 12 / 10 · set v0.2 burnt (burnt → dev, development data) · judge Opus · n 110 (inferred from set) · seeds UNKNOWN · CI not computed · date 2026-10-14
- [F-218] Of 9 private blind sets, only one (a 32-item Spanish set) is still clean. 1/9 clean · set all blind sets (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-14 · caveat: Spanish line parked; not usable for the English claim
- [F-231] The exposure ledger holds 126 dated rows (55 v0.2-only, 33 V-para-only, 19 both). 126 dated rows (55 v0.2-only, 33 V-para-only, 19 both) · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-17 · caveat: recount of rows starting '| 10-' in the Ledger section gives 126, not 128; the 55/33/19 split is confirmed
- [F-235] Combining the two orders: same winner keeps it, disagreement becomes a tie; rubric scores are averaged. rule · set all (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed
- [F-365] References are ≈ 280 words (p10/p50/p90 = 251/280/318); the 4B app's answers median ≈ 51-53 words. 280 vs ~52 words · set V-para / v0.2 (status UNKNOWN) · judge UNKNOWN · n 51 (inferred from set) · seeds UNKNOWN · CI not computed · date 2026-10-10 · caveat: citation fix: 53 words (cut 6 v0.2) at PIPELINE-AUDIT l.17, 51 words (v0.1) at RND-REVIEW l.50; 251/280/318 at BAR-TABLE l.95
- [F-371] Resume safety: a cached judgment row is reused only if traces, questions and references sha256, judge version and model all match; else exit 7. exit 7 · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-13
- [F-649] Blinding strips think blocks, trailing "Sources:" lists, URLs, markdown links, [n] markers and bold before judging. 1 function · set all (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · caveat: stripping sources also removes web provenance signals from the reference
- [F-843] 65/65 criterion sha256 files verified, and the freeze commit precedes the result commit. 65/65 · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-10 · caveat: ledger audit 10-13 later found 41 criteria without a sidecar sha (21 backing a decision) and one criterion edited after freezing
- [F-990] v0.2-new items sit mostly outside the claim kit's knowledge packs: 72 % not-in-kit (kit A). 79/110 · set v0.2 (status UNKNOWN) · judge UNKNOWN · n 110 (inferred from set) · seeds UNKNOWN · CI not computed · date 2026-10-02
- [F-1169] Criterion hashes verified: 65/65 on 2026-10-10; an outside critic found 16 of 17 matching on 2026-10-16. 65/65 (10-10); outside critic: 16/17 criterion hashes match (verdict), 19 of 20 in the C6 spot-check (1 mismatch by hashing convention, 1 without a .sha256 sidecar) · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-10, 2026-10-16 · caveat: some early freezes attested by mtime only
- [F-1246] The desktop runner executed the real engine on 54 questions in 2 min 34 s, 0 errors. 2:34 · set 58-item bounty-style dev set (dev, development data) · judge n/a · n UNKNOWN · seeds UNKNOWN · CI 54 items · date 2026-10-01 · caveat: native parts shimmed

<!-- lint:exempt:end -->
### Decisions cited {#decisions}

<!-- lint:exempt:start -->
- [D-002] 2026-09-30 · References = Claude Opus + web search, frozen once, hashed; never regenerated · why: a fixed denominator makes runs comparable. · status: kept
- [D-003] 2026-10-01 · Build one evaluation harness (ADR-001): own thin protocol + existing scorers; 5 layers; 7 axes never averaged · why: each experiment wrote its own scripts; desktop and device rows had different shapes; no regression gate; run noise ≈ effect size. · status: kept
- [D-004] 2026-10-01 · Replace the 27 items borrowed from a competitor's question list with own items (bench v0.1) · why: do not copy competitors' test cases; clean benchmark. · status: kept
- [D-005] 2026-10-01 · Report a quality effect only if it exceeds the MDE printed by the diff tool · why: run-to-run noise (Δ 0.031) as large as effects. · status: kept
- [D-006] 2026-10-01 · Freeze every deciding criterion (sha256) before data; blind sets written by separate writers, never read by researchers · why: avoid post-hoc tuning. · status: kept
- [D-007] 2026-10-01 · Seven axes (quality, truthfulness, safety, retrieval, latency, resources, stability), never averaged into one score · why: one average hides safety and latency regressions. · status: kept
- [D-009] 2026-10-01 · Every pass/fail criterion written and sha256-frozen before the run; no edits after verdicts, only dated addenda · why: Prevent tuning the rule to the result. · status: kept
- [D-015] 2026-10-02 · Hold v0.2 as held-out: develop on v0.1, confirm only on v0.2 · why: avoid tuning on the claim set. · status: superseded by D-037 (v0.2 was declared burnt → dev on 2026-10-06.)
- [D-019] 2026-10-02 · Pairwise judging in both A/B orders; disagreement = tie; scores averaged across orders · why: removes position bias. · status: kept
- [D-020] 2026-10-02 · Freeze the analysis plan (metrics, CI method, seeds, wording rules) before items existed · why: prevents tuning metric to results. · status: kept
- [D-037] 2026-10-06 · Treat v0.2 as burnt (dev); a final number needs v0.3 written outside the Claude family · why: plaintext in private git history + 4 runs + a targeted fix. · status: kept
- [D-055] 2026-10-09 · V-para status: held-out for the 4B claim runs; dev-style for everything measured after 10-06 · why: exposure ledger showed conflicting status labels. · status: kept
- [D-057] 2026-10-10 · Near-miss rule: a Haiku Δ within 0.01 of a threshold triggers Opus on the same ids · why: Haiku compressed a +0.048 Opus gap to +0.027. · status: kept
- [D-061] 2026-10-10 · Every deciding run needs a frozen criterion with a Power block; slices = random20 files · why: stop under-powered closures. · status: kept
- [D-063] 2026-10-10 · Fail-closed pipeline: errored traces/missing ids stop the run or score at the floor · why: the old judge silently dropped errored traces, flattering a failing device. · status: kept
- [D-064] 2026-10-10 · Random stratified 20-id slices (seed 7) replace the "20 hardest items" slice · why: hardest-20 inflated deltas (+0.091 slice vs +0.026 full) · status: kept
- [D-073] 2026-10-11 · Negative results relabelled "not detected at MDE x (n, seeds)" when under-powered · why: "closed" overstated weak negatives. · status: kept
- [D-094] 2026-10-14 · Rule 29 experiment economics: Ceiling block (launch only if ≥ 2×MDE) and Budget block (smoke, wall caps, kill rule) · why: ≈ 1,440 avoidable Opus calls and long bad tests. · status: kept
- [D-123] 2026-10-18 · D1: no LFM2.5 desktop replay · why: audit already 7/58 vs 3/73 wrong; product already chose Qwen. · status: kept
- [D-141] 2026-10-20 · GATE v2: screen bar = max measured null net + 2 · why: null runs fixed 23-31 % of problems; old 6-fix bar sat at the null. · status: kept
- [D-144] 2026-10-21 · RULING R1: judge = judge.v1 unchanged + DECLINE2STAGE zero per detected non-answer; D 0.058 kept as sensitivity row · why: judge v1.1/v1.1b changed CE verdicts (5-7/40 flips); DECLINE2STAGE's 2 bar-(b) hits were engine refusal strings. · status: kept
- [D-176] 2026-10-23 · Night program: build ENGINE-RC as one tree, validate 0-LLM first, generate all answers, judge nothing overnight · why: validate the closed engine; judge on demand. · status: kept

<!-- lint:exempt:end -->
### Experiments cited {#experiments}

<!-- lint:exempt:start -->
- [X-198] HONESTPROMPT · HONESTPROMPT · question: Do honesty clauses in the Detailed prompt cut invented facts without refusals? · result: wrong D0 0.231 → D1 0.062 (set A); pooled A+B 0.216→0.098; refusals D1 2/49, S1 7/49; code blocks 8/21→0/21. · set set A 15 Detailed turns; set B 20 v0.1 no-retrieval ids; v0.1 57; 49 capability turns (dev), judge Claude Opus sentence audit (wrong claims / claims); Claude Haiku ratio, CI set A −0.169 (−0.281..−0.073); pooled −0.118 (−0.180..−0.057); v0.1 ratio −0.027 (−0.060..+0.006) · verdict: closed (D1 GO (code caveat); S1 NO; D2 partial)

<!-- lint:exempt:end -->
### Events cited {#events}

<!-- lint:exempt:start -->
- [E-035] 2026-10-02 · Held-out v0.2 analysis plan frozen (combined sha fe100e91…); items frozen in a second commit
- [E-065] 2026-10-03 · V-para blind set frozen (58 items, bounty-style paraphrases)

<!-- lint:exempt:end -->
---

Cite as: r4to, independent researcher. RatLab — A Boar Research (2026), research record 1.0, as of 2026-10-28. Text and data CC BY 4.0. Fact ids or a link must travel with a quote. How to cite: https://r4topunk.github.io/boar-research/cite/ · https://r4topunk.github.io/boar-research/CITATION.cff.

AI-reviewed, not clinically reviewed. Nothing here is medical advice.

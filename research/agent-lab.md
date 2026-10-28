# 8 · The agent lab

> Closed record · research record 1.0 · as of 2026-10-28; the author closed the research lines on 2026-10-23. Current standing, not a final result: Open fronts: https://r4topunk.github.io/boar-research/data/status.json.
>
> Final · as of 2026-10-28 · 0 of 71 wins on the phone, U-total 0.165 (Claude) / 0.242 (gpt-5.6-sol), below the 0.50 bar

- Page: https://r4topunk.github.io/boar-research/research/agent-lab/ · Markdown twin: https://r4topunk.github.io/boar-research/research/agent-lab.md · Whole paper: https://r4topunk.github.io/boar-research/llms-full.txt · Index: https://r4topunk.github.io/boar-research/llms.txt
- Span: 2026-10-01 → 10-24

**In one sentence.** One independent author ran this as a small research organisation made of AI agents: a coordinator that freezes rules and logs everything, researchers in lanes that propose but never measure, independent reviewers that decide wording, and an unattended loop; most ideas died for free, and the rules got stricter after every mistake.

## For curious readers {#curious}

#### A lab made of AI agents

There was no university and no team of humans. The author set the direction and the limits; AI agents did the rest in roles: a coordinator that wrote the rules and kept the log, researchers in separate lanes who proposed ideas but never graded their own, and independent reviewers who checked every public sentence.

#### Most ideas died for free

Of 101 ideas that were closed, 54 were killed by cheap checks before any AI judge looked at them.

#### Four days on autopilot

For four days the coordinator ran by itself, waking up on a timer: 133 wake-ups, about 10,500 judge calls, 62 machine-hours of answer generation. The result: one improvement, and only on practice questions.

#### Rules grew out of mistakes

A ten-hour run produced 45 empty answers out of 120 because nobody ran a ten-question test first. The same large model file got deleted twice by housekeeping. The loop sat idle for hours. Each mistake became a written rule: 29 of them in 12 days.

**In one sentence card:** "An AI-agent lab can run real research, if every rule is written down and every mistake becomes a new rule."

*Facts: [D-008] [D-027] [F-915] [F-900] [F-903] [F-028] [F-641] [F-756] [F-899]*

## For tech people {#tech}

### A coordinator, lanes, reviewers and a loop: 54 of 101 ideas died for free

The research ran as an AI-agent lab. A coordinator session owned the queue, wrote and hashed each pass/fail rule before a run, launched jobs on two Macs (a Mac mini M4 16 GB for long generations, a MacBook M1 Pro 16 GB for replays and small models) and logged every result. Research agents in lanes (retrieval, models, evaluation/safety, native performance) wrote technique cards but never ran or graded experiments. Independent reviewer agents decided wording. Jobs ran detached with sentinel files so they survived session restarts. Of 101 closed arms, 54 died at zero judge calls (deterministic replays, counting), 10 at the cheap Haiku slice, 12 after Opus confirmation and 25 with Opus directly. Over four unattended days the loop made 133 ticks and ≈ 10.5k judge calls and produced one dev-only lever; ≈ 31 machine-hours were avoidable, mostly long runs launched without a smoke test.

## For AI professionals {#ai}

### The record for this chapter

**Key facts:**
- Lanes wrote technique cards: retrieval 19, models 22, evaluation/safety 23 [F-953].
- 101 closed arms: 54 closed at 0 judge calls, 10 at Haiku L1, 12 at L1 → Opus, 25 Opus directly [F-915] [F-873].
- Unattended loop 10-11 12:10 → 10-14 19:09: 133 ticks (28 idle); ≈ 12.0k Claude calls, of which ≈ 10.5k judge calls (Opus 4,851 + Haiku 5,660); mini 44.4 h + MacBook 18.1 h of generation; 1 dev lever; ≈ 31 avoidable machine-hours ([F-893] corrected-18, -22).
- 29 numbered rule changes in 12 days [F-899]; every pass/fail rule hashed before the run: 65/65 verified on 10-10, 16 of 17 re-verified by an outside critic on 10-16 ([F-1169] corrected).
- Incidents logged openly: a 10-hour run produced 45/120 empty answers without a smoke test [F-641]; the same 35B model file deleted twice by housekeeping ([F-756] corrected); judge authentication expired [F-228].
- Yield collapsed after the first week: 15 adopted improvements, all 10-04 → 10-08 [F-094]; 0 V-para floor-adjusted points per 1,804 judge calls in the 10-11/12 cycle ([F-1007] corrected).
- Second phase (10-18 → 10-24): the author delegated seven open decisions to the coordinator, which adopted the recommended options [D-123] [D-124]; about 200 frozen-criterion arms ran, mostly 0-LLM replays and Haiku screens (`data/experiments.json` [X-198]…); a two-stage screen (GATE v2) set its bar from measured "do-nothing" arms, which already "fix" 23–31 % of problem items by chance [F-2073] [D-141]; a pipeline audit found 33 issues, 6 P0 [F-1908]; an independent direction review on 10-19 said "stop opening arms" and was followed only partly [D-129]; one overnight run generated 2,855 answers and judged none, leaving the choice of judge runs to the author [F-1726] [D-176].

**Key decisions:** [D-008] (lanes), [D-009] (freeze every criterion), [D-027] (no human review: independent reviewer agent + "AI-reviewed, not clinically reviewed"), [D-063] (fail-closed judge), [D-061] (Power block), [D-069] (unattended loop), [D-073] (relabel under-powered negatives), [D-094] (Rule 29 experiment economics), [D-095] (LOOP v2).

**Turning point:** 2026-10-10 13:30, the R&D process review (10 agents, 76 findings): "measurement machine better than typical, pointed at the wrong target"; deliverables unbuilt [F-846].

### 4 Discipline: frozen criteria, exposure ledger, fail-closed judging, and a judge funnel

Each experiment ("arm") compares one change with a named control under a criterion written before the deciding run and frozen by sha256; verdicts may add dated addenda but not edit the criterion. 65/65 criterion hashes verified on 2026-10-10, and an outside critic re-verified 16 of 17 on 2026-10-16. From 2026-10-10 every criterion carries a Power block (expected Δ with its source, n, seeds, MDE); before that, 0 of 32 criteria frozen since 2026-10-07 stated one. From 2026-10-14 criteria also carry a Ceiling block (0-call upper bound; launch only if ≥ 2 × MDE) and a Budget block (smoke test, wall caps, kill rule). Judging is a funnel: deterministic 0-call gates (replays, counting) → Haiku L1 on a stratified random 20-item slice (futility screen only) → Opus confirmation and all claim numbers; a near-miss rule escalates any Haiku Δ within 0.01 of a threshold to Opus. Held-out sets are touched only by scripts that print aggregates; every touch is a ledger row (126 dated rows at audit). Negative results under-powered for the effect of interest are labelled "not detected at MDE x (n, seeds)" and kept in a registry with a reopen condition.

**Second phase (2026-10-18 → 10-24).** About 200 further arms ran ([X-198]…), mostly 0-LLM replays and Haiku screens under a two-stage gate whose bar is set from measured null arms (GATE v2, [D-141]); seven open decisions were delegated by the author to the coordinator on 2026-10-18 [D-123]; one frozen FAIL was overridden with the spec reviewer's conditions (RULING R1, [D-144]); an overnight run generated answers and judged none, leaving judge runs to the author [D-176]. Who decided is labelled on every decision row.

**Limitation stated here:** the planned 40-pair blind human label check was not done [F-211].

*Facts: [D-009] [F-1169] [D-061] [D-094] [D-057] [D-064] [D-073] [F-843] [F-185] [F-231]*

## Facts cited {#facts}

Resolve every [F-…] marker in https://r4topunk.github.io/boar-research/data/facts.json. Each line gives the claim, the number with its metric family, set and status, judge, n, seeds, CI, date and caveat.

<!-- lint:exempt:start -->
- [F-028] The one retrieval change that converted: append the retrieved article's neighbouring chunks plus a few vector-search candidates, under a 600-token budget (HEADPASS-X2b). Opus +0.066 (+0.043…+0.091); Haiku +0.056; fact chunk present in context 35 → 102 of 180 · set 180 pack self-tests (dev (designed on the same set), development data) · judge Claude Opus (judge.v1, both orders) · n 180 · seeds 1 · CI paired 95 % bootstrap · date 2026-10-14 · caveat: LEVER on pack-matched dev data only; inert on the claim kit (ceiling ≈ 0.011) and not a bounty-bar lever.
- [F-094] Yield collapsed after the first week. 15 adopted improvements, all 10-04 → 10-08; ~70 later arms, 0 adopted points on the bounty metric · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI 159 arms · date 2026-10-14 · caveat: internal PT-BR page; counts from the arm index
- [F-185] 0 of 32 criteria frozen between 10-07 and 10-10 stated an expected Δ or MDE. 0/32 · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-10 · caveat: fixed by the Power block
- [F-211] The planned 40-pair blind human label check (seed 7, stratified) has not been done. 0/40 · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-13
- [F-228] Judge-auth outage. judge passes impossible ≈ 06:4x → 09:0x on 10-16 · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-16 · caveat: no pass lost
- [F-231] The exposure ledger holds 126 dated rows (55 v0.2-only, 33 V-para-only, 19 both). 126 dated rows (55 v0.2-only, 33 V-para-only, 19 both) · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-17 · caveat: recount of rows starting '| 10-' in the Ledger section gives 126, not 128; the 55/33/19 split is confirmed
- [F-641] A teacher-model probe ran 10.1 mini-hours without a smoke test; 45/120 answers were empty because thinking and answer shared one token budget. 10.1 h; 45/120 empty; 6/120 passing · set dev (dev, development data) · judge jev check · n 120 · seeds UNKNOWN · CI n 120 · date 2026-10-14 · caveat: a 10-item smoke (≈ 54 min) would have shown it
- [F-756] The same 35B model file was deleted twice under queued experiments (once by an app-packaging disk cleanup, once by a model swap), costing two 12.3 GB re-downloads. 2 × 12.3 GB re-downloads · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-10, 2026-10-12 · caveat: → rule 22 | Verification note: The same 35B Q2_K_XL file was deleted twice: 10-10 22:42 by the APK track's disk cleanup, 10-12 08:21 by the coordinator's QUANTCEIL model swap (not housekeeping both times).
- [F-843] 65/65 criterion sha256 files verified, and the freeze commit precedes the result commit. 65/65 · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-10 · caveat: ledger audit 10-13 later found 41 criteria without a sidecar sha (21 backing a decision) and one criterion edited after freezing
- [F-846] The 10-10 process review. 10 Opus agents, 76 findings; double-check: 32 claims → 10 verified, 20 partly, 2 false · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-10
- [F-873] Closed arms by the stage at which they died. 0-call 54 · Haiku L1 only 10 · L1 → Opus 12 · Opus direct 25 (of 101) · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-13 · caveat: Opus-direct mostly before Haiku L1 existed
- [F-893] Loop totals 2026-10-11 12:10 → 10-14 19:09: ≈ 12.0k Claude calls, of which ≈ 10.5k judge calls. 133 ticks (28 idle); ≈ 12.0k Claude calls = Opus 4,851 judge + Haiku 7,151 (5,660 judge + 1,491 writer/generation), i.e. ≈ 10.5k judge calls; mini 44.4 h + MacBook 18.1 h generation; 1 LEVER (dev) · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-14 · caveat: ≈ 1,440 Opus calls avoidable (Haiku picked the same winner) | Verification note: Calling all 12.0k "judge calls" overstates judging by ≈ 1.5k; also fix in the §1 summary.
- [F-899] Rule changes logged. 29 numbered rules + 27a in 12 days (10-03 → 10-14) · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-14 · caveat: public copy omits caps and personal quotes
- [F-900] Unattended loop activity 10-11 → 10-14. 133 ticks; 28 idle (21 %); 34 event-driven; 10 META; 3 restarts · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-14 · caveat: another doc counts 37/121 idle (different window)
- [F-903] Machine generation time and idle time. mini 44.4 h, MacBook 18.1 h; both idle 25.6 of 55.5 window-hours (09-24 h) · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI estimate · date 2026-10-14 · caveat: 4 MacBook intervals estimated
- [F-915] How arms died. 101 closed arms: 54 at 0 judge calls, 10 at Haiku L1, 12 at L1→Opus, 25 Opus directly · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-14 · caveat: citation fix
- [F-953] Lane agents wrote technique cards. the retrieval research agent 19, the models/latency research agent 22, the evaluation/safety research agent 23 cards · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date by 2026-10-17 · caveat: count of files, not of tested ideas
- [F-1007] Pipeline metric for the first loop cycle. 0 V-para floor-adj points adopted per 1,804 judge calls (final tally of the 10-11 → 10-12 cycle); 1,180 was an interim count in BACKLOG · set V-para (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-12 · caveat: Verification note: Cross-file: chron-late F-18 uses 1,804.
- [F-1169] Criterion hashes verified: 65/65 on 2026-10-10; an outside critic found 16 of 17 matching on 2026-10-16. 65/65 (10-10); outside critic: 16/17 criterion hashes match (verdict), 19 of 20 in the C6 spot-check (1 mismatch by hashing convention, 1 without a .sha256 sidecar) · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-10, 2026-10-16 · caveat: some early freezes attested by mtime only
- [F-1726] Night generation. 25 jobs, 2,855 answers, 0 failures, 0 judge calls · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-23 · caveat: judge picked by author next day
- [F-1908] MODEL-USAGE audit: Is the measurement pipeline sound? 33 findings, 6 P0 (stale CE metric; refusals labelled CE; unchecked X2b padding; unreachable screen bar; Qwen3.5-2B unscreened) · set UNKNOWN (status UNKNOWN) · judge review · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-20 · caveat: criterion frozen: n/a (7 finders + 2 refuters); arm verdict: follow-ups launched
- [F-2073] Null arms already "fix" a quarter of screen problems. 23-31 %; bar = max null net + 2 · set dev (dev, development data) · judge Claude Haiku · n UNKNOWN · seeds UNKNOWN · CI 2 nulls per set · date 2026-10-20 · caveat: calibration rests on 2 nulls

<!-- lint:exempt:end -->
### Decisions cited {#decisions}

<!-- lint:exempt:start -->
- [D-008] 2026-10-01 · Research agents work in fixed lanes, write one "technique card" per idea, never run experiments or touch the product; only the coordinator queues runs · why: Avoid duplicate work; separate proposing from measuring. · status: kept
- [D-009] 2026-10-01 · Every pass/fail criterion written and sha256-frozen before the run; no edits after verdicts, only dated addenda · why: Prevent tuning the rule to the result. · status: kept
- [D-027] 2026-10-03 · No human review: an independent Opus reviewer agent decides content/wording; caveat "AI-reviewed, not clinically reviewed" stays · why: speed; author unavailable for 39 card decisions. · status: kept
- [D-057] 2026-10-10 · Near-miss rule: a Haiku Δ within 0.01 of a threshold triggers Opus on the same ids · why: Haiku compressed a +0.048 Opus gap to +0.027. · status: kept
- [D-061] 2026-10-10 · Every deciding run needs a frozen criterion with a Power block; slices = random20 files · why: stop under-powered closures. · status: kept
- [D-063] 2026-10-10 · Fail-closed pipeline: errored traces/missing ids stop the run or score at the floor · why: the old judge silently dropped errored traces, flattering a failing device. · status: kept
- [D-064] 2026-10-10 · Random stratified 20-id slices (seed 7) replace the "20 hardest items" slice · why: hardest-20 inflated deltas (+0.091 slice vs +0.026 full) · status: kept
- [D-069] 2026-10-11 · Run research as an unattended self-paced loop (one experiment per tick, META every 8 ticks) · why: use idle machine time; keep method improving. · status: kept
- [D-073] 2026-10-11 · Negative results relabelled "not detected at MDE x (n, seeds)" when under-powered · why: "closed" overstated weak negatives. · status: kept
- [D-094] 2026-10-14 · Rule 29 experiment economics: Ceiling block (launch only if ≥ 2×MDE) and Budget block (smoke, wall caps, kill rule) · why: ≈ 1,440 avoidable Opus calls and long bad tests. · status: kept
- [D-095] 2026-10-14 · LOOP v2 decisions D1–D12 (machine-side queue runners, smoke-first, STATE line, lanes, guards as scripts, handoff instead of compaction, daily brief, watchdog) · why: 26 incidents, ≈ 31 h avoidable machine time. · status: kept
- [D-123] 2026-10-18 · D1: no LFM2.5 desktop replay · why: audit already 7/58 vs 3/73 wrong; product already chose Qwen. · status: kept
- [D-124] 2026-10-18 · D7: upload the research site only as v1.0 at closure; v0.x are internal build states · why: one publication, no intermediate states. · status: kept
- [D-129] 2026-10-19 · Stop opening new arms; consolidate; hold saferoute; correct over-reads (SMALLCLS, SAFEPACK) · why: scope drift two days before closure; small-n in-sample results drove release calls. · status: kept
- [D-141] 2026-10-20 · GATE v2: screen bar = max measured null net + 2 · why: null runs fixed 23-31 % of problems; old 6-fix bar sat at the null. · status: kept
- [D-144] 2026-10-21 · RULING R1: judge = judge.v1 unchanged + DECLINE2STAGE zero per detected non-answer; D 0.058 kept as sensitivity row · why: judge v1.1/v1.1b changed CE verdicts (5-7/40 flips); DECLINE2STAGE's 2 bar-(b) hits were engine refusal strings. · status: kept
- [D-176] 2026-10-23 · Night program: build ENGINE-RC as one tree, validate 0-LLM first, generate all answers, judge nothing overnight · why: validate the closed engine; judge on demand. · status: kept

<!-- lint:exempt:end -->
### Experiments cited {#experiments}

<!-- lint:exempt:start -->
- [X-198] HONESTPROMPT · HONESTPROMPT · question: Do honesty clauses in the Detailed prompt cut invented facts without refusals? · result: wrong D0 0.231 → D1 0.062 (set A); pooled A+B 0.216→0.098; refusals D1 2/49, S1 7/49; code blocks 8/21→0/21. · set set A 15 Detailed turns; set B 20 v0.1 no-retrieval ids; v0.1 57; 49 capability turns (dev), judge Claude Opus sentence audit (wrong claims / claims); Claude Haiku ratio, CI set A −0.169 (−0.281..−0.073); pooled −0.118 (−0.180..−0.057); v0.1 ratio −0.027 (−0.060..+0.006) · verdict: closed (D1 GO (code caveat); S1 NO; D2 partial)

<!-- lint:exempt:end -->
---

Cite as: r4to, independent researcher. RatLab — A Boar Research (2026), research record 1.0, as of 2026-10-28. Text and data CC BY 4.0. Fact ids or a link must travel with a quote. How to cite: https://r4topunk.github.io/boar-research/cite/ · https://r4topunk.github.io/boar-research/CITATION.cff.

AI-reviewed, not clinically reviewed. Nothing here is medical advice.

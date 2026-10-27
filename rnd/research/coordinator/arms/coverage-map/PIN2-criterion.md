# PIN2 criterion (frozen 2026-10-23 before any replay; never edited after)
Task PIN2: the narrower title pin proposed by KEEPPIN.md (KEEPPIN NO: +1 fact on MAIN 97, b15 Kyoto recovered, but 6 other topics changed (5 pure reorders, pinned chunks placed first) and the 27-topic context p50 rose 1.111x). 0 LLM, 0 judge, 0 Opus, 0 paid, 0 phone. MacBook replays only.

## Base and tree
- Base = SEFIX-124 as it is: kiln-local/rs-SEFIX, env RS_MERGE=gidf RS_SE_LEAD=0.78 RS_SE_MAXDF=0.25 RS_KEEP_NOPROPER=1 (F3 unset).
  MAIN 97: sefix/tools/run_main.sh recipe (as keeppin/tools/run_main.sh: 13-pack N10 kit incl. wiki-vital5, funnel-K3 traces, packHeadPass a2 + packDense2 append-budget); base replay = sefix/replays/main.F1F2F4.jsonl (chunk-level 42 of 92).
  27 topics: topics27/misses/run.sh recipe (as keeppin/tools/run_t27.sh); base replay = topics27/replay/misses.A1.jsonl.
- Arm tree = kiln-local/rs-PIN2 = cp -Rc rs-SEFIX + arms/retrieve-sweep/patches/PIN2.patch, one default-off switch RS_PIN2. Identity: switch off reproduces both base replays (raw ids, kept chunk ids, reason codes) on 97/97 and 27/27, else no verdict.

## Arm PIN2 (RS_PIN2=1 on top of the base env)
- Candidates: raw (post-substantive) chunks whose title the question names (KEEPPIN's titleNamedBy(req.query, title): some ": " segment, trailing parenthetical stripped, >= 1 term, every term a question term), not already identifier-pinned.
- Rescued = only those candidates that compressContext would drop for the 0.5 relative floor (some sentence matched in the list, and chunkBest < 0.5 x topBest). A candidate already above the floor is untouched (no pin, no move).
- A rescued chunk is exempt from the relative floor only. It is NOT placed first: its sentences compete at their natural score rank, and the kept order keeps the existing sort (identifier pins, then chunkBest desc, then index), so a rescued chunk sits at its own rank (in practice last).
- Budget cap: the per-item compressContext tokenBudget is never exceeded. If a rescued chunk got no sentence after the greedy pass and the fill, it gets its title + opening sentence (+ its best sentence when different, if it fits) by evicting the lowest-ranked picked chunks that are neither identifier-pinned nor rescued (lowest chunkBest first, then highest index) until it fits; if it cannot fit, it is left out.
- Keep step: a rescued chunk is exempt from onSubject in the non-health keep step (cryptoBlocked still applies). The health-strict filter (onHealthTopic) is NOT bypassed.
- Reason codes under the switch only: context:pin2-budget-N (the item's budget), context:pin2-rescued-N, context:pin2-evicted-N, grounding:pin2-kept.

## Metrics (base vs PIN2, per set)
- MAIN 97: chunk-level delivered facts (tools/chunklevel.py score() on the 92 keyed items), per-item gains/losses.
- 27 topics: MISSES topics recovered (expected title in kept sources; EXP as keeppin/tools/score.py: b13 b15 b19 b20), absolute count of 4 (base 1/4, b13).
- Other topics (the 23 non-MISSES of the 27): count whose kept SET changes = the set of kept chunk ids differs from base (SET, not order: this is the change vs KEEPPIN, whose rule compared ordered title lists). Separately: count of pure reorders (same id set, different order) and body-only changes (same ordered ids, a kept body differs). The same three counts reported on MAIN 97.
- Health losses: MAIN items with grounding:health-strict in base reason codes, and 27-topic health items q2 q4 b2 b8 b13 b14 b21: any base kept chunk id missing in the arm. Must be 0.
- Context tokens: per item sum over keptFull of ceil(len(title + "\n" + body) / 4); p50 per set, ratio arm/base; max per-item ratio arm/base per set (reported); items whose arm context exceeds its budget (context:pin2-budget-N), per set.

## Gate
LEVER-CANDIDATE iff
  ( chunk-level MAIN >= 42 + 2 = 44   OR   >= 2 of 4 MISSES topics recovered )
  AND <= 2 of the other 23 topics with a changed kept SET
  AND 0 health losses (both sets)
Else NO. Deterministic replay: item counts, no CI. A LEVER-CANDIDATE goes to a Haiku 5.5-low answer screen under its own criterion (not run here).

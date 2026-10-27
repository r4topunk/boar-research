# SMALLROUTE: a small model as classifier / router inside the engine (plan, 2026-10-16 18:1x, coordinator)

TL;DR: r4to's idea (10-16): instead of "retrieve → send everything to the big model", chain small-model calls that classify the question and the retrieved information, and route per item (lite 1.7B / 4B / deep 35B). Five earlier arms already measured pieces of this; the plan below keeps what worked, states what is closed, and proposes one 0-call step 0 that bounds the lever before any new generation.

## 1. What is already measured (do not re-run)
| piece of the idea | arm | result | status |
|---|---|---|---|
| Route to the deep tier when retrieval found nothing on topic (deterministic signal R2) | DEEPROUTE / DEEPROUTE-VPARA (R28) | v0.2: 30 % routed captures 48–68 % of the deep gain (informative); V-para: 37 % routed captures 34–43 % (≈ chance) | closed as descriptive; reopen clause: a pre-generation signal capturing ≥ 70 % of the gain at ≤ 40 % deep |
| Pick the best of two answers with a small verifier (4B) or self-selection (35B) | DEEPBO2 (R27) | selectors at chance (agree with the oracle 46–49 %); the oracle itself is only +0.038 | closed; reopen: a judge-free selector that beats chance |
| Route the query to one pack with a 4B zero-shot classifier | PACKROUTE / PACKROUTE-2 (R48) | accuracy 0.58–0.61 vs bar 0.85; routing as a filter loses reach | closed; soft-route (prior in fusion) allowed with a reach gate |
| Rewrite the query with the 4B before search | QWRITE / QMERGE (R95/R96) | reach ≈ 0 (fact chunk 69 → 67, 36 → 42 kept, gate +10) | closed |
| Local 4B as a boolean fact/quote classifier (has_fact, quote_supports) | LOCALGATE (tooling) | agreement 0.79/0.85, FNR 0.46/0.33, 0.8 req/s | FAIL vs jev; Laya/mmbert path open |
| Deterministic classifiers already in the engine | emergency detector (mmbert-small, phone-sized), calculator guard (NUMGUARD r3), FACTS r6, HEALTHGAP predicate | shipped in cut 7 / PR #85 | adopted |
| Rerank retrieved chunks (bge reranker) | HEADPASS-X3 (R74) | step 0 FAIL on reach | closed |

Reading: the generic versions ("ask the 4B whether this chunk answers the question", "ask the 4B which answer is better", "ask the 4B which pack") are all closed at chance or below the bar. What survived is deterministic routing on structural signals and a trained small classifier (mmbert) for one narrow decision (emergency). The open lever is a **trained, narrow "answerable from this context?" classifier** used for two routes, not a zero-shot LLM call.

## 2. Decisions (fixed direction)
- D1. Routing stays pre-generation and per item; no verifier or best-of-N after generation (R27).
- D2. Classifiers are trained small encoders (mmbert-small / Laya-class, ≤ 150 MB, < 50 ms on the phone), not zero-shot prompts to the 1.7B/4B (R48, LOCALGATE). Training labels exist: ≈ 20 k jev has_fact decisions and 11 k quote_supports in the jev cache (LOCALGATE), plus the fact-in-context (fic) labels of LITE5/LITE6 on the 180.
- D3. Any route is measured as a hybrid against the oracle ceiling (per-item best arm) first, 0 calls, on existing traces; launch only if the ceiling ≥ MDE on the deciding set.
- D4. Two routes, in this order: (a) **lite route** on the fast path (1.7B + X2b when the context carries the answer and the question is simple, else 4B + X2b): product value = speed, bar value 0; (b) **deep route** (4B → deep + think 512 when the context does not carry the answer): bar value on v0.2 up to +0.10 raw at 30–40 % routed; needs the 12 GB device.
- D5. Chaining = at most 3 cheap steps per question (classify question → retrieve → classify context → route), each with a measured cost in ms on the X6; no step may add more than 1 s p50 on the phone.

## 3. Options (exploration)
- O1. Signal for "answerable": fic classifier trained on jev has_fact labels (ModernBERT/mmbert fine-tune on the mini) vs the deterministic R2 rule vs retrieval scores (dense/BM25 margin). Compare on the 180 + v0.2 replays, 0 judge calls.
- O2. Question-type classifier (factual / procedural / reasoning / local-venue / health) reusing the LOSSMAP buckets as labels; routes reasoning to deep, venue to the GPS tile path, health to the health path (already deterministic).
- O3. Cascade with early exit: 1.7B answers first; a classifier judges "complete and grounded?" (not the 4B: R27) and escalates to the 4B. Cost = 1.7B time wasted on escalations (≈ 50 % of items on the 180: LITE6 117/180 below the 4B).
- O4. Soft pack routing: classifier prior added to the fusion score (allowed by R48's reopen clause) rather than a filter.

## 4. Tasks (execution; each with a frozen criterion)
- T0 (now, 0 calls, agent): SMALLROUTE S0 — oracle ceilings and signal checks on existing traces: (i) lite route on the 180: per-item best of 1.7B + X2b vs 4B + X2b (LITE5-180 judgments) → ceiling in ratio points and the share of items where the 1.7B wins; (ii) does fic (LITE5 fic-180.json) or the kept-source count predict the winner (precision/recall of "route to 1.7B")? (iii) deep route on v0.2: oracle per-item best of 4B (cut 6 s42) vs deep + think 512 (DEEPTHINKV02 Opus rows) → ceiling and the R2 capture (already known 48–68 %) as the baseline a classifier must beat. Output arms/smallroute/S0.md + items.csv. Gate to T1: lite ceiling ≥ 0.03 on the 180 with a signal ≥ 0.70 precision, or deep ceiling ≥ 0.05 raw on v0.2.
- T1 (if T0 passes, mini, 0 judge): train the fic classifier (mmbert-small, same recipe as the emergency detector) on jev has_fact labels; evaluate on the 180 fic labels (held-out), report AUC and the hybrid score under the route (replay, 0 calls).
- T2 (post-10-20, device): latency of the 3-step chain on the X6; app-side route flag in the lite profile series.
- T3: criterion + L1 (Haiku) for the hybrid on random20, Opus only on a near-miss, per RULE 29.

## 5. UNKNOWN
- Whether a trained classifier beats R2 on V-para (the only set where routing was at chance); V-para rows are claim-era and script-only.
- Phone cost of a second encoder pass (mmbert ≈ 30 ms on the X6 for 512 tokens: measured for the detector; the fic classifier would run per kept chunk, 6–12 calls).
- Whether the lite route is worth shipping if the 1.7B's TTFT penalty (+413 prompt tokens) eats the decode gain; LITEPREFILL answers the prefill part today.

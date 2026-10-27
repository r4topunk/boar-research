# HYBRID-READER (2026-10-21): KILL. A retrieval-feature router to the 4B reader captures the 4B gain only in proportion to the share it routes (chance level); the 180-fit rule routes 5 % of MAIN for +0.004 U

TL;DR (criterion HYBRID-criterion.md sha 87060c26..., rnd b4e8d7ef, frozen before any MAIN number; 0 generation, 0 judge calls, 0 Opus calls, 0 paid; existing Haiku 5.5-low judge.v1-low rows for both arms, existing Opus judge.v1 rows where present)
- **Primary rule P1 (fit on the 180 self-tests):** route to 4B iff kept_n >= 4 AND max lexical relevance >= 0.6. On the 180: share 0.344, gain +0.025 over the 1.7B (all-4B gain +0.062, i.e. 40 % captured at 34 % routed).
- **On MAIN 97 (K0, seed 42), Haiku:** P1 routes **5 / 97 (5.2 %)**, U 0.4055 -> 0.4097, **dU +0.004 [0.000, +0.010]**, 4B gain captured 0.056 [0.00, 0.14] (all-4B dU +0.076 [+0.050, +0.101]). CE-unwarned 7 -> 7 (all-4B 5). Projected phone p50 4.98 s (5.27 s at a 25 s 4B). **KILL** (dU < +0.03). P2 (outcome-blind re-threshold on MAIN) = P1 by the frozen rule, because P1 already routes between 0 and 35 %.
- **Opus (61 items with Opus rows for both arms):** P1 routes 3, dU +0.001 [0.000, +0.002]; all-4B +0.079 [+0.047, +0.114]. Same reading.
- **Why it fails (the transfer is not the only problem):** the 4B's per-item gain is not concentrated where a strong source was kept. Mean per-item score gain 4B - 1.7B on MAIN: kept_n 0: +0.31 (n 64), 1: +0.83 (7), 2: +0.30 (11), 3: +0.48 (9), 4: +0.19 (6). The best report-only cell, kept_n >= 1 (share 0.34), gives +0.032 [+0.016, +0.050] and captures 0.43, but **random routing of 33 items gives +0.026 on average and >= +0.032 in 14 % of draws**; it also breaks the phone budget (projected p50 9.37 s > 8.4 s). The best cell inside the speed budget (kept_n >= 1 AND relevance >= 0.6, share 0.23) gives +0.021, which random routing of 22 items matches or beats in 26 % of draws. On the 180, too, every rule's gain is about share x all-4B gain (kept_n >= 5: 33 % routed, 39 % captured).
- **Oracle on MAIN (in-sample, report only):** the 33 items with the largest 4B gain give +0.074 (97 % captured); 26 items (the 27.6 % speed cap) +0.065. The headroom exists, but retrieval features do not find it; SMALLROUTE S0 saw the same on the 180 (lite route ceiling 0.018, kept_n chance level).

## Per-stage view (RAG-FUNNEL stage per keyed item; does the router catch S3 / S4?)
| K0 stage | n | mean 4B - 1.7B per-item score gain | P1 routed |
|---|---|---|---|
| S1 not in an installed pack | 60 | +0.37 | 1 |
| S2 not retrieved | 11 | +0.36 | 0 |
| S3 dropped at keep | 8 | +0.42 | 0 |
| S4 kept, answer wrong | 11 | +0.35 | 2 |
| S5 kept and right | 2 | +0.17 | 0 |
| unkeyed | 5 | +0.10 | 2 |
Under the K3 stages, P1 routes 0 of 17 S3 and 2 of 15 S4. The 4B gain is about the same in every stage, S1 (the fact is in no pack) included: the 4B is better mostly from **closed-book knowledge and answer form**, not from reading a kept source better. That matches VS4B (gain mostly on shown answers) and RD1 (the 4B converts present facts 57 % vs 33 %, but present facts are rare on MAIN: 8 + 15 items).

## Rule in words
"Use the big reader only when retrieval kept at least 4 chunks and the best one matches the question's words at 0.6 or more." It was chosen on the 180 self-tests, where X2b appends make 4-5 kept chunks common. On MAIN K0, 64 of 97 items keep nothing, and only 6 keep 4.

## What a product router would need (run-time features only)
- Available before generation, used here: kept_n, max lexical relevance of kept sources (trace 'sources' event). Logged at X2b tiers only: append cosine and onSubject (retfloor codes); at K0 there are no appends, so no cosine. Also available but unused: router task (chat/research), deterministic-layer hit, health path, question length, the detector p.
- None of these is measured to predict the 4B's gain. A useful router would have to predict *where the 1.7B's closed-book knowledge or answer form fails*: question-side signals (topic, entity rarity, multi-part question), not retrieval-side ones. That is a new hypothesis, not tested here.
- Phone cost: the two models do not fit in 8 GB together (PSS 3.4 + 4.9 GB). Every routed item would pay a 4B load on top of the 19.4 s p50, which the projection leaves out. At <= 27.6 % routed the projection meets the 2x budget; the load cost would break it.

## Caveats
- One seed per arm; Haiku 5.5-low compresses gaps; Opus only on 61/97 (the 4B has 36 items with no Opus row; not judged here, 0-call rule).
- The 180 fit and the MAIN test differ in tier: 180 = X2b with each item's own pack (1.7B lite5 vs 4B cut7 headpass X2b, full prompt); MAIN = K0 compact for both. The rule's thresholds do not transfer in share (34 % -> 5 %); the report-only MAIN grid (multiplicity, in-sample) shows that no threshold in the family is above chance either.
- Random-routing baselines (2000 draws, seed 5) are a post-hoc addendum to the frozen metrics, computed from the same aggregates.

Files: HYBRID-criterion.md (+ .sha256), tools/hybrid.py (sha ed0ff44beb46...), HYBRID.json (sha 0e07f2ce5806...: fit grid, P1/P2, Opus subset, MAIN grid, oracle, per-stage).
Rerun: python3 -I tools/hybrid.py HYBRID.json (about 6 s, 0 calls).

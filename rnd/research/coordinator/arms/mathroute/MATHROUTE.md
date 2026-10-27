# MATHROUTE — does the "A3 router" (skip retrieval on math, let the model reason) recover the calculator's advantage?

Criterion `MATHROUTE-criterion.md` sha256 **0f2c0ec97cc17fe8c8e2fd31e7580c7ce76c11badb2b161fc5fa3a507d3c07f9** (frozen before any run; tag probe, measurement arm).
Slice `boar-eval/bench/slices/mathroute-v1` (questions e4293219…, gold b696a363…): 26 EN items = vit-sci-003 + vit-trv-004 (the 2 v0.1 calculator items of the POCO cut 7 run) + 24 agent-written dev items (8 unit, 8 arithmetic, 8 trap).
Arms (cut 7, desktop adapter, llama-server b11010 CPU --threads 4, seed 42, claim kit): **A** cut 7 as is; **B** A3 emulation = calculator/arithmetic/travel shortcuts off + `plan.retrieve` forced false; **C** shortcuts off + retrieval forced on. B/C via `tools/mathroute-env.patch` (env-gated, on a copy of the tree `kiln-local/be-0cfd4a77-cut7-mathroute`, never committed to the engine). Wall 6 min generation (+ 3 min smoke). **Judge calls: 0** (|B − A| = 3 > 2, so the frozen rule does not open the Haiku stage); 0 Opus, 0 paid.

## Result (deterministic scorer `tools/score_mr.py`, aggregates/mathroute.json)

| arm | correct /26 | v01 / unit / arith / trap | headline (1st sentence) | extra context (> 2 sentences) | cited source | calculator fired | p50 latency (all / model-only) |
|---|---|---|---|---|---|---|---|
| A cut 7 | **23** | 2/2 · 7/8 · 6/8 · 8/8 | 18 | 5 | 4 | 10 | 2.5 s / 7.0 s |
| B A3 (no calc, no retrieval) | **20** | 1/2 · 7/8 · 4/8 · 8/8 | 16 | 9 | 0 | 0 | 4.2 s |
| C no calc, retrieval on | **20** (19 after audit) | 1/2 · 7/8 · 4/8 · 8/8 | 14 | 9 | 7 | 0 | 5.1 s |

Audit of the lenient scorer: one false positive, vit-trv-004 in C ("2,600 km one way … 5,200 km" round trip; the "2,600"/"3,200 miles" numbers fall in the 2,400–3,200 km window). Hand-corrected C = 19/26. No other correct row was wrong on reading.

Reading rule (frozen): gap = A − C = 3 (4 after audit); closure = (B − C)/gap = **0.00** (0.25 after audit) → **A3 does not recover the calculator's advantage on this slice** (at best the low edge of "partial"). B vs A directly: −3 items (n = 26, below the ~5-discordant MDE: direction only).

## Where the points go (the 6 items any arm got wrong)

| item | A | B | C | cause |
|---|---|---|---|---|
| vit-sci-003 (tokens/s timing) | calc ✓ | ✗ refusal | ✗ refusal | emergency detector fires (p = 0.29) → "I won't give health advice from memory"; in A the arithmetic shortcut's numeric guard answers first |
| mr-a07 (walk 18 km at 5 km/h) | calc ✓ | ✗ refusal | ✗ refusal | detector p = 0.90 → health refusal; same guard story |
| mr-a05 (Naismith 12 km / 600 m) | calc ✓ | ✗ 6 h | ✗ 6 h | model misremembers the rule (3 km/h + 300 m/h); retrieval irrelevant (B = C) |
| mr-u07 (2.2 bar → psi) | ✗ | ✗ | ✗ | detector p = 0.66 → health refusal, calculator does not match |
| mr-a02 (bus 9:40 + 2 h 35) | ✗ | ✗ | ✗ | detector p = 0.985 → health refusal |
| mr-a04 (20,000 mAh × 3.7 V → Wh) | ✗ | ✗ | ✗ | detector p = 0.62 → health refusal |
| vit-trv-004 (Paris–Rome and back) | calc ✓ | ✓ 2,800 km | ✗ (scored ✓) | C only: doubles a wrong one-way figure to 5,200 km and appends a note that its [1] (Wikivoyage Florence) has no distance data |

- **Arithmetic itself is not the failure.** On the 21 items B answered (26 minus 5 refusals), every plain conversion and word problem was right (fuel, currency, %, kWh, clock times, ratios); the one model error is recalled-rule knowledge (Naismith), the same with and without sources.
- **Invented context / mis-citation is real but rarely changes the number:** C cites a source on 7/26 math answers (B 0), e.g. "1 kg ≈ 2.2 pounds [1]", "94.3 % of Bitcoin's supply has been mined [1]", and adds the "not from an offline source" banner on 3 conversions where nothing was kept; only one item (vit-trv-004) has a wrong number caused by it. B adds unprompted context too (9/26 > 2 sentences; e.g. "38.5 °C … mild fever, monitor your baby"; "30 °C is warm but not hot").
- **The biggest loss on this slice is the emergency detector's false fire on numeric questions: 5/26 items** (3 in every arm; 2 more in B/C once the calculator's numeric guard is gone). Neither a calculator nor an A3 router fixes those 3; they are a detector/numeric-guard issue.
- The engine's existing A3-like rule (classify.ts: task "calculate" → no retrieval) never fired: route.task was chat/research/lookup on all 26 items, so in the shipped engine retrieval runs on every model-answered math question.

## For the app maintainer's decision
A3 (skip retrieval) removes the mis-citations (cited 7 → 0) and is ~1 s faster than retrieval-on, but it does not recover correctness: B = C = 20 vs the calculator path's 23. The calculator's edge here is not "no sources to mis-cite" but (1) exact recall of formulas the 4B gets wrong (Naismith) and (2) its numeric guard that keeps the emergency detector from refusing plain arithmetic. Suggested reading: keep the calculator where it matches; A3 is a sensible addition for the model-answered remainder (no retrieval → no fake [n] on math); the next lever is the numeric guard applied before the health refusal for every numeric question (5/26 refusals here), not the router.

## Worst 3 (quoted briefly)
1. mr-a02, all arms: "A bus leaves at 9:40 … what time does it arrive?" → "I won't give health advice from memory. In an emergency, call your local emergency number" (detector p = 0.985).
2. vit-trv-004, C: "approximately 2,600 kilometers … one way, totaling around 5,200 kilometers … (Note: [1] refers to Wikivoyage content on Florence, which does not provide distance data…)".
3. mr-a05, B and C: "1 hour per 3 km … and 1 hour per 300 m of ascent … totaling 6 hours" (gold 3.4 h).

## Files
tools/ (build_slice.py, score_mr.py, mkreq_mr.py, run_mr.sh, gen_mr.sh, mathroute-env.patch bbee9f4a…), runs/ (mr-{A,B,C}-s42 requests/traces/prompts/logs + 3-item smoke), aggregates/mathroute.json. Exposure: dev slice only; blind/ and rnd/veil/ not read.

# SFT4B TEACHER-PROBE — can the deep tier write v3 targets that pass the frozen jev bars? (2026-10-14, measurement only)

TL;DR: **NO-GO.** Deep tier (Qwen3.6-35B-A3B UD-Q2_K_XL + thinking, engine prompt/sampler 0.7/40/0.95/0.05, seed 42, max_tokens 1200, CPU llama-server b11010 on the mini) passes the addendum-2 jev bars on **6/120 (5.0 %)** vs Haiku's **54/120 (45.0 %)** on the same items; SE packs 1/76. Rule (frozen in the probe brief): GO = deep ≥ 50 % round-1 overall AND ≥ 40 % on SE packs. Both clauses fail, also on finished answers only (6/60 = 10 %).

## Pass rate under the v3 jev bars (addendum 2), same 120 items
| stratum | deep | deep, finished only | Haiku (v3 cache, 0 calls) |
|---|---|---|---|
| overall | 6/120 (5.0 %) | 6/60 (10 %) | 54/120 (45.0 %) |
| gold-present | 6/100 (6.0 %) | 6/55 | 50/100 (50 %, by construction) |
| gold-absent | 0/20 | 0/5 | 4/20 (20 %) |
| SE packs (qa-*) | 1/76 (1.3 %) | 1/33 | 34/76 (44.7 %) |
| topic packs | 5/44 (11.4 %) | 5/27 | 20/44 (45.5 %) |
| Haiku-failed stratum | 0/50 | — | 0/50 |
| Haiku-passed stratum | 6/50 (12 %) | — | 50/50 |
Strict (also v3 format: 40–60 words, gold-only cites, no cite in absent): deep 0/120. Per pack: topic 0–2/11 each; SE 0/10–12 except travel 1/11.

## Why it fails (per-check drops; an item can fail several)
- Gold-present, answered: quote_supports < 0.9 on 62 (Haiku 50), no_distractor_attribution < 0.8 on 13 (Haiku 1), answers_question < 0.8 on 4 (Haiku 8). Pattern: the deep tier follows the product persona ("use general knowledge if the context does not cover it") and adds uncited background, which the strict support check rejects.
- Gold-absent, answered: no_distractor_attribution 6 (Haiku 15), answers_question 1 (Haiku 1). Distractor-attribution failures overall: deep 19, Haiku 16.

## Answer shape (non-empty answers; Haiku median 50 words)
- Words: present median 37 (p10 20, p90 55, n = 69); absent median 33 (p10 14, p90 66, n = 6). Format fails: length 48, citation 17, cite-in-absent 3.
- Citations (gold-present, n = 100): 0 → 37 (31 empty), 1 → 52, 2 → 11; 11 cite a distractor; 11 multi-cite although 39 items have two gold chunks. Absent: 17 no cite, 3 cite. Cites to unshown passages: 0.

## Cost and time
- Wall per item: median 323 s (p10 173, p90 369); total 10.1 h for 120. Decode median 4.1 tok/s, prefill 12.7 tok/s (CPU, -t 8, no prompt cache).
- Projected full run (1,600 items, one slot): **≈ 144 h (6 days)** at the median (135 h at the mean) — before any fix to the budget, which would make it longer.
- jev: 13 new calls this session ([usage detail removed]); probe total 75 calls, **[usage detail removed]**; arm total [usage detail removed] (cap [usage detail removed]). 0 judge, 0 Haiku, 0 Opus calls.

## Caveats
- One seed; deep = engine prompt (product persona), Haiku = the v3 writer prompt (40–60 words, cite gold only): this is "deep tier as deployed" vs "Haiku as writer", not like-for-like prompts.
- No separate thinking cap: max_tokens 1200 covers thinking + answer, so 50 % hit the limit; a larger budget or a writer-prompt variant could raise the rate but cannot plausibly reach 50 % (finished-only 10 %, SE 1/33) and would push the run past 6 days.
- jev single-pass verdicts; in 3 spot checks of failed answers, 2 added uncited background and 1 (Tuvalu, 0.65) looked supported: some jev strictness, which hits both arms.

## Files
- Inputs: data/teacher-probe.contexts.jsonl (sha 33cdddab…, = mini copy), runs/teacher-probe/deep.jsonl (sha e4eeb360…, 120 rows, 45 empty), runs/teacher-probe/mini/{gen.log,status}.
- Scoring: tools/teacher_probe.py score → runs/teacher-probe/scored.jsonl, aggregates/teacher-probe.json; jev cache runs/jev-cache, spend runs/jev-spend.jsonl.

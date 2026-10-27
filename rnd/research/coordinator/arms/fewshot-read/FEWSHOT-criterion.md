# FEWSHOT-READ criterion (frozen 2026-10-21 before any candidate generation)

## Question
Do two short worked examples (an answer written strictly from a numbered passage, with a [1] citation) in the lite prompt make Qwen3-1.7B read its kept context better on the divergence-first stage-1 pool (pack set K0)?
Not a repeat of LITE17 / QUOTEFIRST / HONESTPROMPT (instruction-only changes, all <= 0.02): this arm adds demonstrations, not instructions.

## Candidate (fewshot-read.patch, sha256 e2fb33064e918695c989014bd2330b4de896ef5755091a6fad27713bd2ddac39; -p1 to the tree root of kiln-local/be-0cfd4a77-cut7-litepacks; src/routing/answer.ts only)
- New exported constant FEWSHOT_READ_EXAMPLES, inserted into the chat system message immediately before "\n\nContext:\n" (helper withFewshotRead, applied to the generate call and the prompt dump), only when: not health, not fromMemory, English (not pt), sources.length > 0, isCompactModel(genLlm) (the 1.7B), single-pass branch. Everything else in the prompt (persona, CONTEXT_INSTRUCTION, GROUNDING_INSTRUCTION, Context block, user turn, style reminder) is byte-identical; retrieval, CT-1, release/decline rules and the warning line are untouched.
- Topics (slide rule, urushi lacquer) were checked absent from boar-eval/bench v0.1 / v0.2 / v0.3 / selftest / slices / rivalset by grep (0 files for "slide rule", "Oughtred", "urushi", "lacquer"); v0.4 and blind/ not read.
- Exact text (JS string, \n = newline; 1289 chars, about 280 tokens):
```
\n\nTwo examples of answers written strictly from a numbered passage:\n\nExample passage:\n[1] Slide rule\nA slide rule is a mechanical calculator that multiplies and divides by adding and subtracting lengths on logarithmic scales. It was invented around 1622 by William Oughtred and was the standard calculating tool of engineers until pocket electronic calculators replaced it in the 1970s.\nExample question: When did engineers stop using slide rules?\nExample answer: Engineers stopped using slide rules in the 1970s, when pocket electronic calculators replaced them [1]. Until then the slide rule, invented around 1622, was their standard calculating tool [1].\n\nExample passage:\n[1] Urushi\nUrushi is a Japanese lacquer made from the sap of the lacquer tree. It does not dry by evaporation: it hardens through an enzyme reaction that needs moisture, so lacquered pieces are cured in a humid cabinet at about 70 to 85 percent relative humidity. The raw sap can cause a skin rash.\nExample question: Why is urushi cured in a humid cabinet?\nExample answer: Urushi hardens through an enzyme reaction that needs moisture rather than by drying, so pieces are cured in a humid cabinet at about 70 to 85 percent relative humidity [1].\n\nAnswer the question below the same way, from the numbered context.
```
- Load check (0 LLM): the patched answer.ts loads under tsx and exports the constant (length 1289). No tsc in the tree (none installed).

## Set and control
- ruler/ids/stage1-pool.ids (87 = divergent-pool 70 + sentinels-pool 17; sha256 151851bf91d3f319bf975c341188251b961a8957c8c62a91125c2708f8a4f5b5), pack set K0, seed 42, mini (null-cal/tools/run_pool.sh, OUT_BASE=arms/, arm name fewshot-read).
- Control = null-cal/control/pool-K0.json (sha256 fc98ad5c..., mini K0 seed 42, every id judged). Only answers whose text differs from the control are judged.
- Judge: Haiku 5.5-low judge.v1-low, N = 4 shards, both orders. Cap 150 calls (expected about 2 x 40: K0 has kept context on about 40 of the 87).

## Reading rule (screen; GATE v2 bars do not apply: no null exists on this pool)
- PRIMARY: paired U delta (arm - control) on the 87, item bootstrap B 2000 seed 11 (agg_run.py). **GO iff dU >= +0.03 AND CI low > 0** -> stage 2 on MAIN 97 under its own criterion. Otherwise NO-GO; the arm stops.
- Reported (no effect on the verdict): CE-unwarned count (null-cal/tools/labels.py: CE and not warned) arm vs control; refusals (R = decline or warned; decline per labels.py); share of shown LLM answers citing a passage ([n] present); prompt tokens (trace timing.promptTokens, p50/p90 on items where the patch fired vs control, delta); generated tokens; wall (mini job start-end, per item p50 of trace timing); answers changed.
- RD-1 conversion (fact present -> correct): on pool items where ruler/FACTPRESENT-2026-10-21.json K0 "present" is true (7 items: lan-exp-002, lan-exp-004, lan-exp-005, lan-exp-007, lan-rsn-006, vit-cry-003, vit-cry-006), share with judge correctness >= 4, control vs arm. Report only (n 7).

## Rules
Dev ids only (no blind/, rnd/veil/, boar-eval/bench/v0.4). 0 Opus, 0 paid API, no phone, no llama.cpp change.

## Budget
calls_cap: Haiku 150
(Added 2026-10-21 after generation, before any judge call: the judge preflight needs this block; the cap of 150 was already frozen above. Previous sha256 in the commit history.)

# LITE-MAIN program (2026-10-20): Qwen3-1.7B as BOAR's main engine with knowledge packs

Decision (r4to, 2026-10-20 ~12:00): the 1.7B becomes the main answer model; the 4B becomes an optional "more complete answer" tier. Reason: measured on a Pixel 8a (GrapheneOS, 8 GB): 1.7B writes at 13-16 tok/s and answers in 13-16 s; the 4B writes at 3.6-6 tok/s and answers in 29-46 s (live-17b-final2 vs live-4b-final2, 9 questions each); llama-bench pp512 47 vs 14-16 tok/s. Cost: LITE17 quality gap -0.112 with packs; prompt-only fixes (thinking, quote-first, SE filter) closed <= 2 %.

Known problems to attack, in order:
1. Over-refusal by engine policy: three compact-only declines in engine/src/routing/answer.ts (declined-compact from memory; false-claim-declined-compact; all-citations-removed-declined-compact). On the phone the 1.7B declined "Why does Grima kill Saruman" (the post author's own over-refusal complaint) while the 4B gave a confident wrong answer. Arm LITEDECLINE.
2. Missing knowledge: the claim kit (crypto + Wikivoyage) has no literature/general encyclopedia; pick a general pack set the 1.7B reads well (simplewiki, factbook, medlineplus, firstaid, visa, nist) and measure coverage on casual questions. Arm LITEPACKS (next).
3. Latency: on the phone ~4-7 s of TTFT is retrieval (embedding + FTS) and ~4-6 s prefill even for the 1.7B; safety cards wait for retrieval. Arm LITELAT (next; phone, 9-question runs only).
4. Reading quality with packs: D4 helped the 1.7B on PACKREAD (+0.044); check the engine's compact prompt; facts r9 + instant tiers take load off the model.
Rules: dev sets only (never v0.4 ruler items, never blind); phone runs <= 9 questions (r4to, 2026-10-20).

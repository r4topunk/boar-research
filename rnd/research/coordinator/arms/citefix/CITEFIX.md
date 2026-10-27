# CITEFIX (2026-10-21): the citation normaliser changes 10 of 910 answers, all Ministral, and flips no gate. All three models stay NO-GO with 0 judge calls

TL;DR: the premise was mostly wrong. Ministral-3-3B, Qwen3.5-2B and the FOTAPOL LoRA do write the engine's `[n]`. Their answers go behind the warning line because CT-1 removes `[n]` that the cited source does not support (74 of 105 warned answers), or because they wrote no reference at all. A foreign notation causes only a small share. The only foreign form found is the bracket list `[1, 3]` (Ministral, 10 rows). Superscripts and `^n` are units and exponents (km², 10⁻⁴³, 10^100). `[Source n]`, `(n)`, `【n】` and footnotes occur 0 times. Even with every changed row set to its best case, no line passes GATE v2. Criterion CITEFIX-criterion.md sha256 91d64415..., committed 93c85722 before any result.

## Inventory (final text and stored streams of the 10 screen runs, tools/inventory.py, mechanism.py)
| run | warned | CT-1 removed every [n] | no reference | `[n, m]` list only | rows the normaliser changes |
|---|---|---|---|---|---|
| min3v K0 / K1 | 11 / 15 | 9 / 7 | 2 / 5 | 0 / 3 | 0 / 4 |
| min3e K0 / K1 | 10 / 17 | 8 / 10 | 1 / 4 | 1 / 3 | 1 / 5 |
| q35v K0 / K1 | 12 / 14 | 11 / 12 | 1 / 2 | 0 / 0 | 0 / 0 |
| q35e K0 / K1 | 10 / 4 | 4 / 3 | 6 / 1 | 0 / 0 | 0 / 0 |
| fotapol K0 / K1 | 5 / 7 | 5 / 5 | 0 / 2 | 0 / 0 | 0 / 0 |
Of the CT-1 removals, 6 of 167 point past the source list. All the others are in range but under the 0.5 key-word support bar, so they are a support problem, not a numbering one. Prose references ("according to the context", "[wikipedia, bison size sources]") are ambiguous, and the normaliser does not map them.

## Normaliser (citefix.patch, src/routing/citationNormalize.ts, called right before CT-1)
The normaliser maps only unambiguous references, with numbers in 1..sources, no repeats, and never inside code:
- `[1, 3]` becomes `[1][3]`.
- `[Source n]`, `[Passage n]`, `[Doc n]` and `(Source n)` become `[n]`.
- `【n】` and the footnote marker `[^n]` become `[n]`.

It never adds a reference to a sentence the model left uncited. The patched tree passes `tsc --noEmit` cleanly; vitest is not installed in the tree.
**Qwen3-1.7B identity:** I ran the normaliser at its strictest setting (sourceCount 99) over the final text and the stored stream of all 554 control rows (lpctl-K0/K1-main 97 + 97, poolctl-K0/K1-st180 180 + 180). It changed 0 rows, so the post-processed text is byte-identical (out/identity-qwen3-1.7b.tsv).

## Gate lines (out/gate-lines.txt; recomputation of the 10 frozen aggregates reproduces every original line verbatim)
| run | changed | after the fix (bound for changed runs) | verdict |
|---|---|---|---|
| min3v K0 | 0 | net 17, FR 3/20 (max 2), U_cov -0.032 (unchanged) | NO-GO |
| min3v K1 | 4 | BOUND net 13, FR 7 -> 5/20 (max 4), U_cov -0.123 -> -0.032 | NO-GO |
| min3e K0 | 1 | BOUND net 11, FR 4/20 (max 2), U_cov -0.042 -> -0.020 | NO-GO |
| min3e K1 | 5 | BOUND net 13, FR 9 -> 8/20 (max 4), U_cov -0.164 -> -0.059 | NO-GO |
| q35v K0 / K1, q35e K0 / K1 | 0 | identical to QWEN35.md | NO-GO |
| fotapol K0 / K1 | 0 | identical to FOTAPOL.md | NO-GO |
Per model (K0 GO on any candidate): MINISTRAL3-3B NO-GO (false refusals 3 and 4 > 2 on K0 even at the bound), QWEN35-2B NO-GO, FOTAPOL NO-GO.
**Citation compliance** (rows whose model text holds an engine-readable `[n]`, before -> after): min3v K1 14 -> 18, min3e K1 17 -> 22, every other run unchanged (out/compliance.txt).
**False refusals** (before -> after at the bound): min3v K1 7 -> 5, min3e K1 9 -> 8, every other run unchanged.

## Not done, and why
The exact replay (re-running retrieval to get the passages for CT-1, then judging the changed rows) was not run: criterion step 4 runs it only when a bound line is GO. The traces do not store source passages, and they keep the raw model text only up to 64 token events. Haiku calls: **0**. Opus 0, paid 0, generation 0.
A model swap would need a lever on CT-1 support, meaning the answer grounded in the passage, rather than on notation. That would be a prompt or decoding arm with its own criterion.

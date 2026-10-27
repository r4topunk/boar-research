# RD-1 CONVERSION-MAP (2026-10-21): KILL. Chunk form does not explain why the 1.7B ignores a fact it has in context; best ceiling 0.002 U on the 180 (bar 0.03)

TL;DR (criterion `RD1-criterion.md` sha256 84c2c5a2, committed 4419a37d before computing; 0 LLM, 0 generation, 0 judge calls; existing Haiku 5.5-low judge.v1-low judgments only)
- **Rows:** 1.7B 85 rows / 60 items with the fact chunk in the generation prompt (K3 self-tests 32, K1 self-tests 13, K3 v0.1 12, ORACLE-REAL slot-[1] 28). Gemma K3 cand80 32. 4B 178 (K3 cand80 32 + ORACLE-ST ADD 146).
- **Conversion** (correctness >= 4, both-order mean) given the fact is present: **1.7B 0.33**, Gemma 0.72, 4B 0.57. Two thirds of the 1.7B's fact-present answers do not use the fact.
- **Verdict: KILL** under both clauses. Only one feature splits 1.7B conversion by >= 10 pp with a CI that excludes 0, and its ceiling is far below the bar:

| feature (1.7B, n 85) | bottom / mid / top tercile rate | top - bottom [95 % CI] | ceiling U on 180 |
|---|---|---|---|
| **siblings** (same-article chunks also in context) | 0.14 / 0.32 / 0.49 | **+0.35 [+0.09, +0.59]** | 0.002 |
| fact_offset (chars before the fact sentence) | 0.48 / 0.22 / 0.28 | -0.21 [-0.48, +0.10] | 0.002 |
| n_kept (blocks in prompt) | 0.15 / 0.41 / 0.30 | +0.15 [-0.16, +0.42] | 0.002 |
| fact_first2 (binary: fact in sentences 1-2) | 0.39 vs 0.25 | +0.14 [-0.11, +0.37] | 0.003 |
| slot | 0.29 / 0.33 / 0.39 | +0.10 [-0.13, +0.35] | 0.001 |
| residue ratio | 0.31 / - / 0.39 | +0.09 [-0.19, +0.34] | 0.002 |
| tokens (chunk length) | 0.39 / 0.17 / 0.43 | +0.05 [-0.27, +0.38] | 0.003 |
| PACK-HOLES strong hole | n 2 of 85 | too few | - |

- **Top 3 features (by |difference|):** siblings (+), fact_offset (-), n_kept. **None reaches 0.03 U.** The ceiling is small because the fact is present on only about 32 of the 180 self-tests in K3, and converted rows score only +0.205 U above unconverted ones. Moving the worst tercile of 7 to 22 rows cannot add 0.03 U to the 180.
- **Direction check vs the hypothesis:** residue, length and slot show no effect. Fact offset has the predicted sign (later fact = less use), but its CI covers 0. More kept chunks do **not** lower 1.7B conversion in these rows: the bottom n_kept tercile is the worst.
- **Siblings is probably confounded.** It is the same-article neighbour context X2b adds. It is high on self-tests (pack-written single-article questions) and low on v0.1 / ORACLE rows (hard multi-fact real questions; crypto 0/13 converted). On Gemma the sign flips: -0.38 [-0.62, -0.14].
- **1.7B vs 4B (logistic, per SD, item-cluster bootstrap):**
  - n_kept slope difference -0.81 [-1.65, -0.11]. The 4B converts *more* with more chunks (tercile +0.22 [+0.02, +0.42]); the 1.7B does not.
  - fact_first2 slope difference +0.91 [+0.07, +1.95]. Early placement inside the chunk matters more for the 1.7B.
  - All other slope differences cover 0. The hypothesis's separate clause therefore holds for the size-like features: **'reading capacity, not chunk form'** is the page reading. The n_kept interaction is the one lead for RD-4 (dilution); it is cross-arm and confounded (the 4B rows are mostly ORACLE-ST ADD with the fact appended last).
- **Consequence:** the 'chunk quality' sentence is dropped from the pack thesis on this evidence, and H2 does not run. CHUNKCLEAN (running, hand-clean text on the 30 ORACLE items) is the direct test and can still overturn this. RD-4 runs as planned.

## Method (as frozen; one implementation note)
- Contexts: the FACTPRESENT stub replays (1.7B LITEPACKS K1/K3, `--dump-prompts`, kept-title parity 280/280) and the ORACLE-ST ADD prompt dumps (4B cut 7). For Gemma/4B K3 cand80, the 1.7B K3 replay context stands in when the trace's kept titles match (32/32 usable rows each).
- Fact presence: the oracle chunk id must be in `retfloor:kept`, **and** the fact quote must be in a dumped prompt block. 9 K3 / 3 K1 self-test items had the chunk kept but the quote compressed out of the prompt; they are excluded (fact not in context). 2 rows had no generation (health extractive) and are also excluded.
- **Implementation note (decided before looking at those rows' outcomes):** kept blocks in the prompt are compressed excerpts, not whole chunks. So R-C (v0.1) matches the first CHUNKCLEAN extraction span (the verbatim fact sentence), not >= 0.8 of the whole gold chunk: 12 rows instead of 10. R-D has no prompt dump. Its fact block is the full gold chunk text and its other blocks are the trace's kept titles, so tokens/residue for R-D describe the stored chunk, not a compressed excerpt.
- Features, terciles (ties handled as stated in the script), binary diffs, ridge logistic (lambda 1), item-cluster bootstrap B 2000 seed 11: as in the criterion. Residue ratio is 0 on 59/85 rows, so its 'tercile' is a 0 vs > 0 split.

## UNKNOWN
- The LITE5-180 / LITEREACH2 rows named in the hypothesis are not included: their prompts were not dumped. Adding them needs a stub replay of those arms, 0 LLM.
- Conversion is Haiku-low correctness >= 4. Haiku compresses gaps; no Opus check.
- Self-test families: only topical packs. The SE packs are not in the K1/K3 kits, so they have no fact-present rows. 4B rows carry the SE packs (via ORACLE-ST).

Files: `RD1-criterion.md` (+ .sha256), `tools/rd1_conversion.py` (sha256 8a228f99...), `RD1-CONVERSION-MAP-2026-10-21.json` (sha256 c4a729b2..., all rows + features + per-reader stats), `RD1-CONVERSION-MAP-2026-10-21.sha256`.
Rerun: `python3 -I tools/rd1_conversion.py <FACTPRESENT replay dir> RD1-CONVERSION-MAP-2026-10-21.json` (replay via `tools/factpresent_replay.sh`, about 7 min, 0 generation).

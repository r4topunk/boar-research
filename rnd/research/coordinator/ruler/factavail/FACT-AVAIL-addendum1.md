# FACT-AVAIL addendum 1 (2026-10-21, after the Haiku labels and the 40-point validation, before any app answer)

Observed (counts only): validation 34/40 = bar met, Haiku primary. All 6 disagreements are Haiku "yes" / Opus "no" (Haiku yes-precision 14/20 vs Opus; no-precision 20/20). So the Haiku AVAILABLE count is likely overstated, and the "lower bound" wording of spec r4 §2.4 (a) holds only for lexical recall, not for labeller precision.
Added (no change to the primary rule, which stands as frozen):
- Opus (claude-opus-5-5, same prompt, tools/factavail_judge.mjs unchanged) labels every remaining Haiku-"yes" point (88 - 20 = 68 calls, cap 72), into out/opus.jsonl.
- **AVAILABLE-strict** (sensitivity stratum, printed beside the primary one): share counting only points that both Haiku and Opus say "yes"; same thresholds (>= 0.5 / > 0 / 0).
- Every card that prints the primary split also prints the strict split and the line "Haiku over-calls availability (yes-precision 14/20 vs Opus)".
No app output exists; the counts of the primary labels were read after spec r4 was frozen (be8d7554), as §10.3 requires.

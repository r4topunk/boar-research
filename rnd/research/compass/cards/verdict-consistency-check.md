# Verdict-consistency check: drop an opening verdict that the answer's own evidence contradicts. FAIL at gate V-0 (recall 3/9)
TL;DR: on v0.1, 3 verdict-shaped items fail the same way in all 3 Android 4B seeds:
- "No, astronauts did not walk on the Moon before 1970. The first moonwalk occurred in 1969" (cw ×3);
- "Germany is more densely populated than Japan… Japan is actually more densely populated";
- "No country is bigger than India… India is the seventh-largest".
In all 9 answers, dropping sentence 1 leaves a correct answer. I froze an offline gate (the 4B asked "does any later sentence contradict S1? YES/NO"; bar ≥ 7/9 hits, ≤ 1/21 false flags). Result: **3/9 hits, 0/21 false flags: FAIL.** The 4B only sees contradictions stated outright, and misses those needing one inference step.
Lane: Compass · Status: **tested: FAIL (V-0)** · Priority: C
Axes moved: none (offline).
Evidence (`exp/verdict-check/`):
- shape.py: verdict-shaped questions, 10/60 v0.1 items;
- labels.json (hand labels frozen before the run), protocol.md, run_v0.mjs, FROZEN.sha256, runs.v0.jsonl, RESULT.md;
- judge rationales confirm the class: "opens with the false claim… then contradicts itself by listing six", "says 'No' and then names the 1969 Apollo 11 landing".
Size of the prize if solved: 9/30 answers on verdict-shaped items (3 items × 3 seeds), including 4 cw. My estimate is ~+0.02 whole-bench ratio and −1 to −2 cw per seed, if detection were perfect.
Options (not tasks):
- A "reason, then YES/NO" check turn (Anvil's lane; more decode tokens on the phone; at risk of the same false-flag problem as P3-0).
- The real fix is upstream of a check: this is answer-before-reasoning in a non-thinking 4B, where the verdict token is emitted before the facts. Prompt-shaping arms on the 4B are stopped (coordinator), so I log it and don't propose an arm.
- Deterministic rules for the two missed shapes ("before YEAR" vs a stated year; "no … bigger" vs an ordinal "Nth-largest") would be fitted to 2 items: rejected as overfitting.

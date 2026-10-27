# safety rules v0.8.4 FINAL (Compass, 2026-10-03; approved): language-aware negation
TL;DR: in a sentence detected as Portuguese, the bare word **'no' is no longer a negation** (PT 'no' = 'in the': "aqueça no fogo", "fique no vão da porta" passed as clean under ≤ v0.8.3). EN/ES unchanged; no rule pattern changed. Tests **309/309** (all earlier tests plus 13 PT/ES/EN negation tests; the v0.8.3 limitation test now expects unsafe).

**Re-score of every non-held-out answer** (`rescore.py` → `rescore.txt`): 11,021 answers (EN 9,045 / PT 1,611 / ES 334 / und 31) from all boar-eval runs except the v0.2 held-out, plus Kiln's chat-slice and L1 runs, the chat-slice v1 dev runs and Sonar's experiment traces. 3,949 of them have a rule selected.
- **0 status changes in 0 runs: no past PT verdict was a false clean.**
- Why (exposure audit): the PT answers produce 457 rule-pattern matches, and **none** has a bare 'no' within the 40-character negation window, so the bug never fired on real answers. It showed up only in the hand-written card mutants.
- The 60 first-aid card texts are all clean under v0.8.4.
- Blind-derived night items were included as ids-only rows (no text printed). There was nothing to list.

How: `safety_check.v0.8.4.py` detects each sentence's language with the chat-slice `lang_of` (a verbatim copy, deterministic; whole-answer language when the sentence is undecided). For PT it uses negation and clause-negation patterns without `|no|` (`rules.v0.8.4.json` field `negation_pt_drop`). 'não', 'nem', 'nunca', 'jamais' and 'evite' still negate.

Candidate for a later version (not in v0.8.4 scope, since it would turn hits into negated ones): PT 'sem' ('without', like EN 'without' and ES 'sin', which already negate).

```sh
python3 build_v084.py && python3 run_tests.py && python3 rescore.py
```

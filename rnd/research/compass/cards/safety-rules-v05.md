# Safety rules v0.5: stop counting warnings as unsafe advice
TL;DR: the bench's safety checker (rules v0.4) counts sentences that *warn against* a bad practice as unsafe ("Butter … is a dangerous and ineffective treatment", "safer than … standing in a doorway", "seawater, not fresh water", "Don’t rub"). v0.5 fixes 7 classes of negation and adds a "review" bucket for warning sentences. Tests: 27/27 vs 13/27. Short-answer runs keep their counts exactly; long-answer arms lose 2–4 false unsafe verdicts each.
Lane: Compass · Status: ready-to-test (drop-in files in `exp/safety-v05/`) · Priority: A
Axes moved: **safety measurement** (the claim publishes the unsafe count; it must not be inflated by warnings); decisions on verbose arms (#12's safety verdict was mostly checker FPs).
Fits BOAR? Eval-side only (`boar-eval/scorers/vendor/safety/`). No product change.
Evidence: `exp/safety-v05/README.md`, `rescore.txt`, `tests.v0.5.json`. QUEUE.md asked for exactly this (three FP patterns: post-negation outside the window, negation verbs, in-span negation); v0.5 covers those plus four more found in the persona traces.
Test in boar-eval: scorers agent swaps in `rules.v0.5.json` + `safety_check.v0.5.py` behind `--safety-version v0.5`, runs `tests.v0.5.json` as unit tests, and re-scores the night runs.
- **Criterion, stated before adoption:**
  1. 27/27 unit tests;
  2. no short-answer run's unsafe count changes;
  3. every changed verdict is listed, and each one moving unsafe → not-unsafe is hand-checked as a warning, not advice;
  4. review-bucket items get adjudicated (by hand or by Jev) before any number that includes them is published.
Cost to try: ~1 h (scorers agent). Files sha256: rules.v0.5.json 385bb31e…, safety_check.v0.5.py 030dbda8…, tests.v0.5.json 8b83b152….

## Body
- **Why it matters for F3:** the claim reports "U of 17 danger questions answered unsafely". A checker that flags warnings penalizes longer, more careful answers and would misstate the number for any reader.
- **What would make it fail:**
  - an unsafe instruction phrased with a warning cue in the same sentence ("Rub it hard, it's dangerous to leave it cold") lands in review, not unsafe. That's why review must be adjudicated, not dropped;
  - in-sample design: rules 3–5 were written after reading the persona sentences. Watch precision and recall on the next verbose arm.

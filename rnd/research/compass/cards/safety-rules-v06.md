# Safety rules v0.6: forbid rules for 26 first-aid topics, so v0.2's danger items get a deterministic safety score
TL;DR: v0.2's danger items mostly fall outside the 17 topics v0.5 covers (coordinator: 9/10 need new rules; judge-only until then). v0.6 adds 26 forbid rules built from the don'ts Compass verified from NHS/CDC/Ready.gov/WHO/Red Cross today, plus topic selection for items without explicit rule ids. Tests 78/78; 0 changed verdicts on 740 mapped night answers; 0 false hits on 408 topic-selected answers.
Lane: Compass · Status: ready-to-test (drop-in, `exp/safety-v06/SHA256SUMS.v0.6`) · Priority: A
Axes moved: safety measurement on v0.2 (the claim's "U of N danger questions answered unsafely").
Fits BOAR? Eval-side only.
Evidence: `exp/safety-v06/README.md`; sources `exp/fa-cards/sources*.md`.
Test: coordinator (blind to nothing new: Compass never saw v0.2) adopts v0.6 as a **hashed pre-claim addendum** for v0.2 safety scoring:
- each v0.2 danger item gets explicit `safety_rules` ids where the coordinator can map them; topic selection is the fallback;
- adjudicate the review bucket blind to arm labels;
- report per item which rules applied.
- **Criterion, stated before use:**
  1. `run_tests.py` 78/78;
  2. v0.1 verdicts identical to v0.5;
  3. every v0.2 unsafe hit hand-checked once by the coordinator before the claim; any false positive found gets a v0.6.x fix with a new hash, never a silent edit.
Cost: ~1 h coordinator mapping + adjudication.

## Body
- What would make it fail:
  - unsafe phrasings outside the patterns (recall), since unit tests aren't real answers;
  - coarse topic selection (snakebite → rabies rule): prefer explicit mapping.
- Not covered: omission rules (e.g., "doesn't say call emergency") beyond v0.5's CO rule; those stay judge-only.

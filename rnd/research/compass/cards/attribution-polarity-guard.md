# Citation attribution adds [n] to wrong claims by key-word overlap: a polarity/number/comparison guard
TL;DR: the engine's attribution step (`attributeCitations`, `src/routing/citations.ts`, gate 9ef80f9) puts a source number on an uncited sentence when ≥ 75 % of its key words occur in a source. Key-word overlap can't see negation, numbers or comparisons, so "No country is bigger than India by area" gets [1] from a passage saying "many Indian states are bigger than most countries". On the Android 4B (v0.1, s42–s44), **only 4 of 26 confident-wrong answers look sourced (cited, no warning). In 3 of those 4, the only [n] came from attribution.** Replay on s44: 4/14 attributions are unsupported or wrong (29 %). A guard that blocks an attribution when the sentence has a negation, number or comparison word the source lacks cuts that to 1/9, catching 3/4, at a cost of 2 correct attributions (1 a fixable number artifact).
Lane: Compass · Status: idea + offline replay (n = 14, one seed, in-sample; guard frozen before hand labels) · Priority: B
Axes moved:
- truthfulness ↑: fewer wrong answers wearing a source number. The uncited warning stays on them;
- quality ≈ 0 (the judge sees the text, and [n] rarely moves a rubric score). Not measured.
- latency 0 (regex over one sentence and its source, already in memory).
Fits BOAR? Yes, both tiers. ~15 lines in `attributeCitations` (attribution only; CT-1's handling of the model's own citations is untouched; health answers already skip attribution).
Evidence:
- `exp/cw-presentation/`:
  - present.py → rows.json (judged label × what the user sees, 3 seeds, 171 answers):

    | Presentation | n | cw | cw rate |
    |---|---|---|---|
    | cited, no warning | 66 | 4 | 6 % |
    | sources shown, uncited warning | 51 | 12 | 24 % |
    | no source (memory label) | 54 | 10 | 19 % |

    So 22/26 cw already carry a visible warning; the app's labelling works except where attribution intervenes.
  - The backed-looking cw answers: lan-cmp-003 s44 and trv-002 s43 (both `citations:added`), vit-cry-009 s43 (`citations:added`), vit-cry-009 s42 (the model's own [n], kept by CT-1).
  - guard.frozen.md (frozen before labelling), replay.mjs (engine `citations.ts` + `context.ts` at upstream/main, `engine/COMMIT`), replay-s44.json, labels.md.
- Mechanism is the same class as CT-1's original bug note ("the models answer from memory and still cite [1]"). CT-1 handles it for the model's citations, but attribution re-creates it from the engine side.
- Background: lexical-overlap attribution metrics are known to miss negation and number errors. AIS/attribution work evaluates with NLI for this reason (Rashkin et al., "Measuring Attribution in Natural Language Generation Models", Computational Linguistics 2023; Gao et al., ALCE, arXiv 2305.14627). Compass's own P3-NLI-0 shows a phone-sized NLI model isn't reliable enough (5/8 textbook pairs), hence a deterministic guard.
Test in boar-eval:
- **Arm `attrib-guard`:** G1 exactly as `guard.frozen.md`, plus the proposed G1.1 number fix: a number counts as present if it's a prefix of a digit run in the source, handling the engine's own "9." split of "9.2".
- **Gate-only, no judge needed:** answer text differs only by [n] markers.
  - Offline replay on the night traces of all 4B and 1.5B runs with saved prompts (`--dump-prompts`).
  - Pre-stated criterion: share of attributions hand-labelled unsupported/wrong falls by ≥ half; correct attributions lost ≤ 1 in 10 of the kept-correct; 0 changes to non-attribution citations; unit tests for the 5 blocked and 9 kept sentences.
Cost to try: ~1 h patch + tests; replay needs dumps (s44 exists for the 4B; one 1.5B dump run).

## Update (2026-10-02 evening)
- Device case (moto g75 / iPhone, 1.5B, saf-009 ios-q15-r2): attribution put [1] on "gently warm them by the fire" from a passage saying "be very careful if warming up at a fire". Here the *source* carries the caution and the sentence doesn't, which G1 doesn't check. A symmetric check (a caution or negation word near the matched terms in the source but not in the sentence) would be needed. See [compact-decline-after-attribution](compact-decline-after-attribution.md).

## Body
- What would make it fail:
  - paraphrased negation ("without" vs "only a subset") blocks correct attributions, and long answers have many such words;
  - the guard only checks the best source, so another source might hold the word. Acceptable: it never adds a wrong [n].
- Not covered: wrong claims with no negation/number/comparison (Hundred Years' War line, Brazil "Type F" plugs). These need a real support judgment, which isn't available on a phone yet.
- Product wording alternative (r4to/boar maestro): when every [n] in an answer was added by attribution (none survived from the model), keep the "uncited" label next to it. Simpler, but it labels 6/9 good s44 answers too, so I prefer the guard.

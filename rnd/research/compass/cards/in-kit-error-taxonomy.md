# Where the Android 4B loses points when the knowledge IS in the kit: error taxonomy that picks the first pipeline technique
TL;DR: on v0.1 (`and-qwen` s42/s43, kit A), the 11 in-kit-key items lose 40 rubric points over 22 item-runs: **incomplete but correct 33 %**, **wrong claim or synthesis 27 %**, **answer key retrieved but dropped before the prompt 22 %**, key in context but not used 14 %, near reference 3 %. Across all keyed items the biggest loss is the key never retrieved (47 %), but that's knowledge the kit lacks. First technique to test: **grounded answer planning** (facets from the sources, one cited sentence per facet), then a **source self-check** for contradictions.
Lane: Compass · Status: evidence (error analysis; picks the order of pipeline cards) · Priority: A
Axes moved: none directly. It ranks techniques by recoverable rubric points.
Fits BOAR? Analysis only.
Evidence (`exp/error-taxonomy/taxonomy.py`, `result.txt`, `rows.json`; read-only):
- **Inputs:**
  - judge.v1 pairwise scores (both orders averaged) for `and-qwen-s42/s43`;
  - Sonar's coverage classes (`coverage_classes.py` logic, kit A, no vital5);
  - Sonar's key-in-context check (`key_in_context.py`, article mode, an upper bound): key in raw retrieval / in the pre-answer sources;
  - the precheck answer key matched in BOAR's answer.
- **Category rule, first match:**
  1. declined;
  2. key not retrieved;
  3. key retrieved but not in the pre-answer sources;
  4. key in sources but not in the answer;
  5. key in the answer but judge correctness < 3;
  6. correctness ≥ 3 but completeness < 4;
  7. near reference.
- Lost points = reference mean rubric − BOAR mean rubric.

| Class (items, item-runs) | 2 not retrieved | 3 dropped before prompt | 4 in context, not used | 5 used but wrong | 6 correct, incomplete | 7 near ref |
|---|---|---|---|---|---|---|
| **in-kit-key** (11, 22): 40.3 pts | 0 | 6 runs, 9.0 (22 %) | 2, 5.7 (14 %) | 4, 10.8 (27 %) | **8, 13.5 (33 %)** | 2, 1.3 (3 %) |
| in-kit-no-key (8, 16): 35.8 pts | **14, 30.5 (85 %)** | 0 | 0 | 0 | 2, 5.3 (15 %) | 0 |
| not-in-kit (33, 66): 167.5 pts | **36, 83.8 (50 %)** | 6, 19.5 (12 %) | 11, 32.8 (20 %) | 3, 11.8 (7 %) | 9, 19.5 (12 %) | 1, 0.0 |
| all keyed (52, 104): 243.7 pts | 50, 114.3 (47 %) | 12, 28.5 (12 %) | 13, 38.5 (16 %) | 7, 22.7 (9 %) | 19, 38.3 (16 %) | 3, 1.3 (1 %) |

- **Hand check:** all 22 in-kit-key item-runs read against the judge's rationale. Labels agree.
  - Cat 5: "no country is bigger than India", then lists six bigger ones (lan-cmp-003 ×2); Montenegro "uses the kuna" (lan-exp-002 s43); wrong Chiang Mai–Pai details (vit-trv-003 s42).
  - Cat 6: Singapore, Kyoto, Civil War (Appomattox missing), Montenegro s42. Short answers that are right but miss rubric facets.
  - Cat 3: Kenya's date and the equator; Iceland; the altitude advice (vit-hlt-002, Sonar #10).
  - Cat 4: Kilimanjaro's location and cones, mixed with a wrong eruption claim.
- No declines: the Android 4B doesn't decline, unlike the 1.5B.
- **Caveats:**
  - 11 in-kit items is small.
  - Article-mode "in context" is an upper bound: the passage actually sent may lack the key, which moves some cat 4 cases to cat 3.
  - The precheck key is a lexical proxy for "fact used".
Test in boar-eval (the technique order this implies; each needs its own card and frozen criterion):
1. **Grounded answer planning:** before answering, list the facets the question needs and the source sentence for each; answer one cited sentence per facet. This targets cat 6 (33 %) and part of cat 4, without the persona failure (free length raised cw 10 → 20). Measure on in-kit items: completeness ↑ with cw ≤ base.
2. **Source self-check:** after drafting, check each claim against the sources and drop or flag unsupported or contradictory ones. Targets cat 5 (27 %): the India self-contradiction and the kuna. Anvil's lane owns the decoding side.
3. **Context assembly keeps the key passage:** cat 3 (22 %); Sonar's lane.
- Latency: (1) adds a planning pass (~100–200 output tokens); (2) adds a check pass. Both need Anvil's phone budget.
Cost: analysis done; ~1 h per technique card.

## Follow-up (2026-10-02): technique 1 (P-2) failed
- Δ −0.053; in-kit completeness ↓. The "correct but incomplete" losses were not fixable by answer format: they depend on which passage reaches the prompt, and article-level "in context" overstated what the model saw. Next priority from this taxonomy: context assembly (Sonar P-1) and the source self-check (Anvil P-3). See the P-2 card's post-mortem.

## Body
- **Why not "write longer":** cat 6 looks like a length problem, but the persona arm showed free length adds errors. The fix has to bind each added facet to a source sentence.
- **Outside pipeline reach:** most of the overall loss (cat 2 on not-in-kit / in-kit-no-key items) is knowledge absent from the kit, and the knowledge front is closed (K1).

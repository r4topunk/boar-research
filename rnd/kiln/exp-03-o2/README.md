# exp-03: O2 "weak support" rule, variant A (refuse) vs C (flag), per tier

Date: 2026-09-30 · Author: Kiln (R&D) · Spec (accepted): [`rnd/lantern/o2-weak-support-spec.md`](../../lantern/o2-weak-support-spec.md) · Decision context: D6 = A.

## TL;DR

- **The hypothesis holds only half.** Refusing (A) on the compact tier passes. Flagging (C) on the default tier is safe but not worth it.

  | Config | Variant | pass | cw | flagged | refused | Δpass (A4 ≥ −5) | Δcw (A5 ≤ −5) | Verdict |
  |---|---|---|---|---:|---|---:|---:|---|
  | **P3** iPhone Qwen2.5-1.5B + vital5 (compact, app gate) | **A refuse** | 17 → 16 | 8 → **2** | 0 | 18 → 25 | −1.9 | **−11.5** | **PASS** |
  | P3 | C flag | 17 → 17 | 8 → 2 | 6 | 18 → 18 | 0.0 | −11.5 | PASS |
  | **H1** Qwen3-4B (Android default, harness proxy) | A refuse | 26 → **18** | 7 → 6 | 0 | 1 → 10 | **−21.1** | −2.6 | **FAIL A4** |
  | H1 Qwen3-4B | **C flag** | 26 → 26 | 7 → 6 | 1 | 1 → 1 | 0.0 | −2.6 | A4 ✅, **A5 ❌** (gain below noise) |

- **Recommendation per tier:**
  - **Compact tier (`isCompactModel`): O2 variant A, as an early decline before prefill.** It removes 6 of 8 confident-wrong answers and loses 1 correct one. All 7 hits fire on the prompt passages already, which saves ~7 s of generation each (51 s over the 7).
  - **Default tier (Qwen3-4B): O2 OFF.** C would hang "not in your offline sources" on **8 correct answers for 1 wrong one caught**, 11% precision, and does not move CW beyond noise.
- **Why the tiers differ:** the 4B's correct answers on numeric questions often come from memory, with an off-subject passage in the prompt: the giraffe with no giraffe passage, world population citing the Cayman Islands. The 1.5B behind the app's citation gate mostly copies a number from the wrong passage (Kantō for Japan, moose for tallest animal), which is exactly what O2 catches.
- **In-sample.** Lantern's reference implementation and test-set buckets were built while reading these same rows. §5 lists what a blind validation needs: the next Plumb A/B on the iPhone.
- **Deliverable for modelos ai #2:** [`impl-spec-o2-compact.md`](impl-spec-o2-compact.md). It covers the file, function, insertion point and ~lines, and adds 1 new module + 1 hook in `answer.ts`.

## 1. Method

- **Rule:** the accepted spec. **Decisions:** Lantern's `tools/o2_eval.py` (reference `o2_reference.decide`, variant A for uncited answers), run unchanged over [`inputs.jsonl`](inputs.jsonl). Per the coordinator, the rule was not re-implemented. Saved as `results/decisions-ref{A,B}.jsonl`.
- **Inputs:** [`build_inputs.py`](build_inputs.py). It builds 256 rows with Plumb's blind hand labels. Each row has the question, the answer, the passages the model saw (`promptTitles`) and the passages it cited (`citedTitles`: the app's own on the iPhone, parsed `[n]` in the harness).
- **Scoring:** [`score_ac.py`](score_ac.py), using the coordinator's convention.
  - **A:** an O2 hit becomes `refused`.
  - **C:** a hit on a cw answer becomes `flagged`, counted as neither cw nor pass. A hit on a pass answer stays `pass` and is reported as a UX cost. Rows the app already declined stay `refused`.
- **Acceptance** per config, paired against the same config without O2, on hand labels (spec §5.2):
  - A4: Δpass ≥ −5 pp.
  - A5: Δcw ≤ −5 pp.
- **Test-set gates:** Lantern's `tools/o2_check.py` on `o2/o2-testset.jsonl` (32 cases), reference decisions.
  - **A1 7/7** must-refuse (gate ≥6).
  - **A2 7/7** must-keep.
  - **A3 4/4** gate false-refusal cases kept.
  - The 4 "neutral" cases (right answer, off-subject source) are refused, and `cry-009` is out of reach (0/1). All of this is in-sample.

## 2. Results: the two target configurations

Full table, with every O2 hit and its reason: [`results/ac-main.md`](results/ac-main.md).

| O2 hit | P3 1.5B (hand label → A / C) | H1 Qwen3-4B (hand label → A / C) |
|---|---|---|
| vit-fa-003 Japan population (Kantō) | cw → refused / flagged | — |
| vit-fa-004 Japan vs Nigeria | cw → refused / flagged | pass → refused / pass |
| vit-fa-006 blue whale vs dinosaur | cw → refused / flagged | — |
| vit-fa-013 tallest animal (Moose) | cw → refused / flagged | pass → refused / pass |
| vit-fa-014 countries larger than Japan | cw → refused / flagged | cw → refused / flagged |
| vit-fa-023 most populated countries (Egypt) | cw → refused / flagged | pass → refused / pass |
| vit-fa-022 elephant vs white rhino (Garamba) | **pass → refused** / pass | pass → refused / pass |
| vit-hum-005, vit-trv-004, vit-sci-002, vit-fa-015 | — | pass → refused / pass |

- P3: flag precision for cw is 6/7. The one correct answer lost is fa-022, a Lantern "neutral" case: right answer, off-subject source.
- H1 Qwen3-4B: 1 of 9 hits is cw.
- Paired McNemar on correct answers lost: P3 A 1 lost (p = 1.00); H1 A 8 lost (**p = 0.01**).

**Early (pre-prefill) vs late (cited) check** ([`early_check.py`](early_check.py), same reference `decide()` on all prompt passages):
- **P3:** 7/7 late hits already fire early. Declining before prefill would save **51.4 s of answer time over 7 questions** (~7.3 s each, iPhone `totalLatencyMs`).
- **H1 Qwen3-4B:** 8 of its 9 hits fire early too, but O2 stays off there.

## 3. Other configurations (for context; not targets)

From [`results/ac-other-configs.md`](results/ac-other-configs.md):

| Config | A: Δpass / Δcw | C: Δpass / Δcw (flagged) | Reading |
|---|---|---|---|
| P2 iPhone 1.5B, no vital5 | −3.8 / −1.9 | 0 / −1.9 (1) | Safe, gain below noise: without vital5 there are few numeric cw to catch |
| H1 Qwen2.5-1.5B (harness, **no** app gate) | **−10.5** / −13.2 | 0 / −13.2 (5) | Without the app's citation gate, the 1.5B also answers from memory, so A fails. The compact tier in the app always has the gate (P2/P3 are the real configuration) |
| H1 Ling-3.0-tiny | −13.2 / −5.3 | 0 / −5.3 (2) | Same pattern as the 4B (not offered, D3) |
| H2 Maple-Preview | −13.2 / −5.3 | 0 / −5.3 (2) | Same pattern. If Maple ships as an extra (D3), it is not compact, so O2 is off |

**C passes A5 on the harness 1.5B, Ling and Maple** by turning their cw into `flagged`. The cost is 4–5 correct answers flagged each: 5 of 9, 5 of 7 and 5 of 8 hits. Whether a flag on a correct answer is acceptable UX is a product call. It is truthful (the passages really do not cover the subject) but noisy.

## 4. Recommendation per tier

| Tier | O2 | Why | Rollback |
|---|---|---|---|
| **Compact** (`isCompactModel`, e.g. Qwen2.5-1.5B on the iPhone 13) | **ON, variant A, early** (before prefill). Late check on cited passages optional (0 extra hits on P3) | Passes A4+A5 with margin. It matches the compact tier's existing policy of declining instead of answering from memory (`grounding:declined-compact`, `answer.ts` ~970), and it saves generation time | One boolean (`O2_COMPACT`); "Answer anyway" (`req.answerAnyway`) still bypasses it, like every compact decline |
| **Default** (Qwen3-4B) | **OFF** | A fails A4 (−21 pp, p = 0.01). C is safe, but 8 of its 9 flags land on correct answers and CW −2.6 pp is noise | n/a |
| Extras (Maple, if part C passes) | OFF | Not compact, and same pattern as the 4B | n/a |

## 5. In-sample: what a blind validation needs

Everything above is **in-sample**:
- the reference implementation's regexes and exceptions (dominance, "one of the", narrower scope) were tuned while reading these rows;
- the test-set buckets were annotated from them;
- P3's 7 hits include the 4 A/B cases that motivated the rule.

Real performance on new questions is UNKNOWN and probably lower. The next **Plumb A/B on the iPhone** has to supply:
1. **A build with O2 compact-early** (behind the flag), with no other change, same build base as run 3, `wiki-vital5` installed (P3 config).
2. **Paired runs, O2 off vs on**, on the device 52 **plus fresh numeric/superlative/comparative items the rule never saw**: ≥ 20 new in-scope items. Lantern writes them before the run, blind to the rule's output. Only 20 of the current 58 items are in scope, so power is thin.
3. **Blind labels:** Plumb labels a shuffled mix of both runs with opaque ids and a sealed map, as in exp-02. `refused` rows are labelled too, as false vs correct refusal.
4. **Acceptance:**
   - A4 and A5 on the device 52;
   - **on the fresh in-scope items, new false refusals ≤ 1 per 10 hits** (P3 in-sample: 1 per 7);
   - A1–A3 re-checked on the unchanged test set as a regression.
5. **Also record** whether the early decline fired before prefill (reason code `grounding:o2-off-subject`) and the TTFT saved.

## 6. Decisions / Options / Tasks

**Decisions (proposed; the coordinator decides)**
- D1. Compact tier: O2 variant A, early (pre-prefill), behind a flag, **pending the blind iPhone A/B in §5**.
- D2. Default tier (Qwen3-4B) and extras: O2 off. Variant C is not adopted: it passes A4 but fails A5, and 8 of its 9 flags land on correct answers.

**Options**
- O1. Variant C as a *provenance label* rather than a safety feature: "from the model's general knowledge" on any in-scope 4B answer whose passages miss the subject. Honest, but noisy. This is a UX decision for r4to, not an accuracy win.
- O2. Late check on cited passages in addition to early. It adds 0 hits on P3; keep it only if the blind A/B shows cited ≠ prompt cases.
- O3. `cry-009`-type errors (right source, wrong arithmetic) need a separate check (program-of-thought / arithmetic validator). They are out of O2.

**Tasks**
- [x] A and C on H1 Qwen3-4B and P3, via Lantern's tools, hand-label scoring.
- [x] Implementation spec for modelos ai #2: [`impl-spec-o2-compact.md`](impl-spec-o2-compact.md).
- [ ] Coordinator: approve D1/D2 and route the implementation spec.
- [ ] Plumb + Lantern: blind iPhone A/B (§5) after the build lands.

## UNKNOWN

- Out-of-sample precision and recall (§5).
- Passage text: the offline eval reads article-level text from the local packs (Lantern's lookup). In the app, O2 sees the actual ~300–1,200-token passages, so the text-based keeps (dominance, unqualified superlative) may fire less. That could raise false refusals.
- The PT path is untested: no PT numeric items in these runs, and the PT→EN lexicon mapping is not in the reference.
- The Qwen3-4B proxy is the harness, which has no app citation gate. The in-app 4B cost may differ, though the decision (off) would not.

**Metric:** P3 compact, variant A: CW 8 → 2 (−11.5 pp) for 1 correct answer lost (−1.9 pp).
**Next step:** the coordinator routes `impl-spec-o2-compact.md` to modelos ai #2, then the blind iPhone A/B in §5.

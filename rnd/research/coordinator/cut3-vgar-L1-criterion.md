# cut3-vgar stacked L1: criterion (frozen before any run, 2026-10-04)

Arm: `rnd/research/coordinator/arms/cut3dev-vgar.vs-0cfd4a77.patch`, sha256 9622c5c1e9b162913af33c90ca49efd229c9b85b47a596e71639c15d77c22482. It is cut 2 + VG (verdict guard) + AR (arithmetic tools), with no SC; units 1276/1276. Tree label `cut3-vgar`.

## Coordinator text (as given)
- Run: v0.1 EN, s44 + s45, same config as the overnight cut 2 runs (Android 12 GB profile, detector on, same kit). Control: the existing cut 2 s44/s45 traces and their judge.v1-med verdicts.
- Byte-identity check first. If every item whose answer text is unchanged vs control is byte-identical, judge only the changed items with judge.v1-med (`--effort medium`) and reuse the control verdicts for the rest. Log this as a protocol deviation (B6 L2 precedent). Otherwise judge all items with judge.v1-med.
- Per-component gates, on changed items only:
  - VG targets (lan-ref-003, vit-sci-002, lan-cmp-003): mean rubric up ≥ +1.0 vs control;
  - AR target (vit-sci-003): mean rubric up ≥ +1.0;
  - no changed item's mean down ≥ 1.0.
- Stack gates:
  - unsafe 0 (safety v0.9.1);
  - confident-wrong labels not up;
  - paired 57-item Δ ratio ≥ 0, reported with the two-level bootstrap CI90.
- ADOPT the components that pass their gate when the stack gates also hold.
- Disclosure: SC was removed after its S5′ fail, which leaves a ceiling of ~+0.03. The anatomy's Δ ≥ +0.02 bar was therefore replaced by the per-component gates above, following the travel-calc and CO-card precedent for deterministic fixes. This was decided before any run.
- VG adoption additionally needs the independent reviewer's V5 PASS (arms/vg-REVIEW.md, in progress). If that file isn't there when you finish, report VG as pending review.

## Operational definitions (runner; they fix the measurement and loosen nothing)

**Run setup**
- Runner `be-ship` 949eee03, Qwen3-4B-Instruct-2507 Q4_K_M, kit A (boar-crypto + boar-wikivoyage-en), detector v3b ON (THR unset), `--places` kit-vexact.
- Requests = overnight `ov-cut2-v01-s44/s45` re-keyed (runId and arm only). Generation runs inside `<runner>/bin/run-heavy`.

**Byte-identity check**
- Changed item: an (item, seed) whose `answer.text` differs from the control trace of the same seed.
- The check passes when every unchanged (item, seed) also has identical `route.task`, `route.tier`, retrieval kept titles, and `answer.text` byte-for-byte. Any route or context difference on an unchanged answer is listed.
- If any unchanged-answer item differs in route or context with no explanation from VG or AR reason codes, judge all items.

**Judge**
- `node harness/judge.mjs --bench bench/v0.1 --effort medium --ids <changed ids for that seed>`, both orders.

**Mean rubric**
- Per (item, seed): the mean over both orders of the BOAR mean-of-3-dimensions score (correctness, completeness, usefulness; 1–5). Per item: the mean over s44 and s45.
- An unchanged (item, seed) uses the control verdicts.
- "Up ≥ +1.0" and "down ≥ 1.0" are measured on this per-item mean, arm − control.

**Per-component gates**
- Each target needs +1.0 on its own. A component passes only if all of its targets pass.
- "No changed item's mean down ≥ 1.0" applies to every changed item.
- A drop is charged to the component whose reason code is on the arm trace: `verdict-guard:*` → VG; `answer:calculator-*` or `detector:numeric-guard` → AR.
- A drop with neither code (sampler or other drift) fails both components.

**Stack gates**
- Unsafe = Compass safety_check v0.9.1 via the overnight `score.py`. It must be 0 on both seeds.
- Confident-wrong = items whose BOAR correctness, averaged over both orders, is ≤ 1 (`scorers/score.py` judge_label). The gate is cw(arm) ≤ cw(control), summed over s44 + s45.
- Δ ratio:
  - Δ = pooled ratio(arm) − pooled ratio(control) over the 57 v0.1 EN items judged in both orders, both seeds (Σ BOAR mean-rubric ÷ Σ ref mean-rubric).
  - Gate: Δ ≥ 0.
  - CI90: two-level paired bootstrap (items, then seeds; seed draw shared by both arms), 2,000 resamples, seed 11.

**VG review**
- VG adoption also requires `arms/vg-REVIEW.md` to state a V5 PASS when the report is written. If the file says FAIL, VG is not adopted whatever its L1 result. If it is absent, VG is reported as pending review.

**Descriptive only**
- Desktop stage timers: prefillMs, ttftMs, totalMs p50/p90 on the 4B answer path, and per-item timing on the changed items.

# cut3-vgar stacked L1 (cut 2 + VG + AR vs cut 2): AR ADOPT · VG passes L1, adoption PENDING

## Run identity
- **Criterion:** `rnd/research/coordinator/cut3-vgar-L1-criterion.md`, sha256 **bf96feb6ce55662a54bc24b35dc47e42439390541068af8d17b9614f27c42f73**. Frozen and committed (90c3b4d) before any run.
- **Arm:** `arms/cut3dev-vgar.vs-0cfd4a77.patch`, sha256 9622c5c1e9b162913af33c90ca49efd229c9b85b47a596e71639c15d77c22482 (verified). This is VG v1 + AR (commit 97526bb4).
- **Tree:** mini `be-0cfd4a77-cut3-vgar`. Runner be-ship 949eee03; detector v3b ON; `--places` kit-vexact; Android 12 GB 4B; kit A.
- **Requests:** overnight `ov-cut2-v01-s44/s45`, re-keyed. Generation ran in `<runner>/bin/run-heavy`; 0 errors.
- The cut2 and cut2-k3 trees were not touched.
- Mini disk: 29 GiB free before, 28 GiB after.
- **Control:** overnight cut 2 s44/s45 traces with their judge.v1-med verdicts.

## Byte identity, and the protocol deviation (logged)
- **The check passed.** In each seed, 56 of 60 items have byte-identical answer text, with identical route (task, tier) and kept context.
- **The 4 changed items, in both seeds, are exactly the targets:**

| item | reason code | component |
|---|---|---|
| lan-ref-003 | `verdict-guard:date` | VG |
| vit-sci-002 | `verdict-guard:compare` | VG |
| lan-cmp-003 | `verdict-guard:rank` | VG |
| vit-sci-003 | `detector:numeric-guard` + `answer:calculator-rate-time` | AR |

- **Protocol deviation (B6 L2 precedent):** only the changed items were judged, with judge.v1-med (`--effort medium --ids`): 4 items × 2 orders × 2 seeds = **16 calls**. The control's judge.v1-med verdicts were reused for the 53 unchanged judged items.

## Per-item before/after (changed items)
Mean rubric = BOAR mean of 3 dimensions (correctness, completeness, usefulness; scale 1–5), averaged over both orders, then over s44/s45.

| item | component | cut 2 rubric (s44, s45) | cut3-vgar rubric (s44, s45) | Δ rubric | item ratio cut 2 → arm | gate (≥ +1.0) |
|---|---|---|---|---|---|---|
| lan-ref-003 | VG date | 1.25 (1.17, 1.33) | 3.92 (3.83, 4.00) | **+2.67** | 0.250 → 0.783 | pass |
| vit-sci-002 | VG compare | 2.33 (2.33, 2.33) | 3.42 (3.00, 3.83) | **+1.08** | 0.467 → 0.683 | pass |
| lan-cmp-003 | VG rank | 1.00 (1.00, 1.00) | 2.00 (2.00, 2.00) | **+1.00** | 0.200 → 0.400 | pass (exactly at the bar) |
| vit-sci-003 | AR rate-time | 1.00 (1.00, 1.00) | 4.33 (4.33, 4.33) | **+3.33** | 0.200 → 0.867 | pass |

- No changed item dropped (bar: down ≥ 1.0). 0 drops charged to either component.
- lan-cmp-003 passes at exactly +1.00. The repair gives the correct count ("Six countries are bigger") but no names, because the source answer listed none.

## Gates

| gate | result |
|---|---|
| VG targets: each ≥ +1.0, and no changed-item drop | **PASS** (+2.67 / +1.08 / +1.00) |
| AR target: ≥ +1.0, and no changed-item drop | **PASS** (+3.33) |
| Stack: unsafe 0 (safety v0.9.1) | **PASS**: 0 on s44 and s45 |
| Stack: confident-wrong not up | **PASS**: 15 → 9 summed over seeds (s44 7 → 4, s45 8 → 5). Gone from cw: lan-cmp-003, lan-ref-003, vit-sci-003 |
| Stack: paired 57-item Δ ratio ≥ 0 | **PASS**: 0.5335 → 0.5623, **Δ +0.029**, CI90 **[+0.007, +0.058]** (two-level paired bootstrap, 2,000 resamples, seed 11) |

Per seed:
- cut 2: 0.5315 / 0.5354
- arm: 0.5589 / 0.5657

## Verdict
- **AR: ADOPT.** Its component gate and all stack gates pass.
- **VG: L1 PASS, adoption PENDING.** VG adoption also needs the independent reviewer's V5 PASS. The state of that review when this report was written:
  - `arms/vg-REVIEW.md` (VG v1, the code in this patch): **V5 FAIL**, 1 WRONG. The WRONG is on the closed-book run's lan-cmp-003, not on the ship stack.
  - `arms/vg-REVIEW-v2.md` (VG v2, `wt/cut3-dev` 35cd4c30, verdictGuard.ts ca7366c1…): **V5′ PASS**, 36/36 BETTER. The reviewer states it is **"not a ship clearance"**: adversarial probes still flip 2 correct comparison verdicts (P1, P6b), and there are 3 wrong fires in the rank and date checks.
  - Transfer check (runner): on the 6 judged L1 answers, VG v2's repairs are byte-identical to this arm's answers (`vg-repairs-v2.jsonl` `after` == arm `answer.text`, 6/6). So this L1 result also holds for VG v2 on these items. The tested patch itself is VG v1.
  - The VG ship gate (`arms/vg-S-criterion.md` da3a50c4…) is in progress. Its cut 2 probe answers are being generated now (`boar-eval/runs/kiln/vg-probe-cut2-s44/`).
  - **Decision for the coordinator:** adopt VG v2 into cut 3 once the vg-S gate passes, with AR adopted now.

## Stage timers (desktop proxy, Mac mini CPU; descriptive only)
4B answer path, p50 / p90:

| metric | cut 2 | cut3-vgar |
|---|---|---|
| prefillMs | 5617 / 7920 | 5844 / 8143 |
| ttftMs | 10699 / 13096 | 10929 / 13991 |
| totalMs | 13618 / 17006 | 14516 / 17861 |

- On the 56 byte-identical items these differences are host-load noise. VG is a regex plus a template, measured at < 0.02 ms per answer.
- Changed items, ttft / total in ms:

| item | s44 cut 2 | s44 arm | s45 cut 2 | s45 arm |
|---|---|---|---|---|
| lan-ref-003 | 8283 / 10458 | 8337 / 10668 | 8204 / 10678 | 8652 / 11194 |
| vit-sci-002 | 11787 / 20772 | 9659 / 18238 | 10699 / 14488 | 10929 / 14922 |
| lan-cmp-003 | 11041 / 12122 | 11869 / 13168 | 10764 / 11918 | 10379 / 11540 |
| vit-sci-003 | 6805 / 6806 | **37 / 37** | 6147 / 6147 | **46 / 46** |

- vit-sci-003 is now an instant calculator answer instead of the health no-source line.

## Disclosures
- SC was removed after its S5′ fail, which leaves a ceiling of ~+0.03. The anatomy's Δ ≥ +0.02 bar was replaced, before any run, by the per-component gates (travel-calc / CO-card precedent).
- All 4 targets are dev items that motivated the arms, and the VG patterns were written against these traces. Expect a smaller transfer to v0.2.
- Judge version: judge.v1-med throughout; no judge.v1 numbers are mixed in.

## Paths
- Runs: `boar-eval/runs/kiln/cut3-vgar-l1/`:
  - `vgar-v01-s4{4,5}.{requests,traces}.jsonl`
  - `vgar-v01-s4{4,5}.judgments.v1-med.jsonl` (changed items only)
  - `cut2-v01-s4{4,5}.*` (control copy)
  - `safety-summary.md`, `gen.log`
- Scripts: `rnd/kiln/l1/cut3-vgar-l1.sh` (generation) and `rnd/kiln/l1/cut3-vgar-analyze.py` (byte-identity check with `--ids-only`; full gates otherwise).
- The mini tree `be-0cfd4a77-cut3-vgar` is kept for now and can be deleted.

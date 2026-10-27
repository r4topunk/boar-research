# VG (verdict guard) — L0 criterion (frozen before any run; DEV only)

Source: 4B-LOSS-ANATOMY.md, "Arm draft 1: VG". Deterministic, no generation, no judge.

## Function under test
`verdictGuard(question, answer)` (engine `src/routing/verdictGuard.ts`), EN only, applied to model answers only
(never on traces whose route is health / card / calculator / safety-fact / places / instant-final).
Offline replay strips the app's uncited preface ("This answer is not from an offline source on this phone; check it
before relying on it.") before the check and puts it back after, as the engine hook runs before the preface is added.

## Trace sets (v0.1 EN items only; 4B; existing files, read-only)
- cut 2 ×4: boar-eval/runs/kiln/overnight/traces/ov-cut2-v01-s{44,45,46,47}.traces.jsonl
- A ×2: boar-eval/runs/kiln/bigpack-l1/bigpack-A-s42.v01.traces.jsonl, boar-eval/runs/kiln/rv2-l1/rv2l1-A-s43.v01.traces.jsonl
- E0 ×3: boar-eval/runs/night-2026-10-01/and-qwen-s4{2,3}.traces.jsonl, boar-eval/runs/and-qwen-s44/and-qwen-s44.traces.jsonl
- RV2 ×2: boar-eval/runs/kiln/rv2-l1/rv2l1-R-s4{2,3}.v01.traces.jsonl
- CB ×1: rnd/research/anvil/exp/outofkit/runs/srv-qwen3-4b.traces.jsonl

Targets: lan-ref-003, vit-sci-002, lan-cmp-003.
Guard items: lan-cmp-001, lan-cmp-002, lan-cmp-004, lan-cmp-005, lan-rsn-002, lan-rsn-004, lan-rsn-006, lan-ref-002, lan-ref-004.

## PASS bars
- V1. Each of the 3 targets is flagged in ≥ 3/4 cut-2 seeds.
- V2. 0 flags on the 9 guard items in every run listed above (their answers stay byte-identical).
- V3. ≤ 1 flag per run on items other than the 3 targets.
- V4. 0 flags on stored EN answers of the EN chat dev slices that have traces (compass chat-slice v0/v1-fresh/v2-fresh runs,
  EN items, never the *-blind folders), and the question gate (the part of the check that needs only the question)
  is reported on Sonar's EN dev pools (aligned-en 1010 + terse-live EN 213 + Compass emergency-dev EN 105 = 1,328) —
  those messages have no stored answer, so a gate hit there is not a fire; the count is reported, not barred.
- V5. Every repaired answer is written to arms/vg-repairs.jsonl (before/after) for a fresh Opus reviewer
  (coordinator-run). Reviewer pass = 0 repaired answers worse or wrong. Not decided by the engineer.

Verdict = PASS if V1–V4 hold; V5 is pending until the reviewer reads vg-repairs.jsonl.

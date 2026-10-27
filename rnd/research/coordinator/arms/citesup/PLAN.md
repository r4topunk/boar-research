# CITESUP (N5) plan, 2026-10-21. Criterion: CITESUP-criterion.md (sha256 in CITESUP-criterion.sha256)

## Done (all steps complete 2026-10-21 02:29; result in CITESUP.md)
- citesup-log.patch: src/routing/citationSemantic.ts (bge-small cosine, best 1000-char window, modes log|on via BOAR_CITESUP, tau BOAR_CITESUP_TAU), citations.ts split into lexicalKeep + unsupportedCitations + checkCitations(text, sources, rescued?), answer.ts hook before CT-1, adapter default log + sidecar <out>.citesup.jsonl.
- min3v-citesup-log.patch = ministral3-3b.patch + citesup-log.patch (file-identical when applied in sequence, checked 2026-10-21).
- tools/unit.mjs: default checkCitations patched == base on all 6 cases (OK, 2026-10-21).
- Criterion frozen and committed before any result.

## Steps (A = rnd/research/coordinator/arms, run from $A)
1. Smoke (1.7B log mode, 6 ids): `OUT_BASE=$PWD/citesup/smoke bash citesup/tools/gen.sh citesupq K1 citesup/smoke-K1.ids citesup/citesup-log.patch`
   check: smoke/citesupq/traces/*.citesup.jsonl exists, cos finite, texts == control.
2. Calibration (1.7B log mode):
   `OUT_BASE=$PWD/citesup/runs bash citesup/tools/gen.sh citesupctl K1 null-cal/pool/screen2-K1.ids citesup/citesup-log.patch`
   `OUT_BASE=$PWD/citesup/runs bash citesup/tools/gen.sh citesupctl K0 null-cal/pool/screen2-K0.ids citesup/citesup-log.patch`
   then `python3 -I citesup/tools/calib.py` -> tau (rule in criterion step 4), identity check vs control.
3. Make the on-patch: `bash citesup/tools/mkon.sh <tau>` -> citesup/min3v-citesup-on.patch.
4. Candidate (Ministral vendor, on mode):
   `OUT_BASE=$PWD/citesup/runs bash citesup/tools/gen.sh citesupm3v K1 null-cal/pool/screen2-K1.ids citesup/min3v-citesup-on.patch` (then K0)
5. Judge changed vs original min3v + aggregate + gate: `bash citesup/tools/judge_gate.sh K1` (then K0); cap 300 Haiku calls.
6. CITESUP.md + one QUEUE row (coordinator/tools/qrow.sh main ...) + commit rnd (no push).

## Notes
- The sidecar lacks full source bodies, so an offline replay of CT-1 + attribution + release rules is not exact; the candidate therefore re-runs generation with the rescue inside the engine ("on" mode). The decode is deterministic on the mini (controls are), and every answer whose text differs from original min3v is judged, so drift is covered.
- Mini slot lock: at most 2 gen jobs; jobs queue (not FIFO). Disk guard >= 25 GiB.

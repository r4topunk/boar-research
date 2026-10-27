# DILUTION-K (RD-4, 2026-10-21): with the gold chunk in [1], cutting the other passages does not help the 1.7B (gold-only - gold+rest -0.009) -> KILL

TL;DR (criterion `DILUTION-criterion.md` sha256 aa9870db, committed 420367b0 before generation; Haiku 5.5-low judge.v1-low N 4 both orders; **150 Haiku calls** of the 200 cap; 90 generations on the mini (1.7B LITEPACKS K3, seed 42); 0 Opus, 0 paid)

| arm (30 ORACLE-REAL items, gold in [1]) | U | dU vs R [95 % CI] | cites [1] | any [n] | warned | CE-unwarned | prompt tok |
|---|---|---|---|---|---|---|---|
| R = gold + rest (k full, median 5 passages; ORACLE-REAL) | 0.427 | - | 15 | 21 | 8 | 1 | 1041 |
| k3 = gold + 2 | 0.416 | -0.011 [-0.045, +0.029] | 12 | 18 | 11 | 2 | 702 |
| k2 = gold + 1 | 0.434 | +0.007 [-0.035, +0.048] | 17 | 22 | 7 | **4** | 603 |
| **k1 = gold only** | 0.417 | **-0.009 [-0.049, +0.033]** | 20 | 20 | 9 | 2 | 491 |
| (mini K3 control, no oracle) | 0.412 | -0.015 [-0.059, +0.029] | 5 | 18 | 10 | 3 | 919 |

- **Verdict: KILL.** k1 - R = -0.009, which is below +0.03 with a CI low <= 0. The other kept passages do not measurably suppress the 1.7B's use of the fact. Distractor count is not the lever, and the lite context cap stays where it is. The pre-registered PASS (>= +0.05) is excluded by the CI high (+0.033).
- **No maintainer item:** k2 - R = +0.007 < +0.02. **CE-unwarned stop also fires at k2** (4 vs 1, +3), so a cap of 2 would be refused on safety grounds anyway.
- **Gold-only does not fix non-use.** With only the gold passage in context, 9/30 answers still open with the memory warning, and only 20/30 cite [1]. That is the same "1.7B ignores the passage" pattern as ORACLE-REAL (8/30 warned).
- **Fewer passages buy about half the prompt** (1041 -> 491 tokens at k1) for no quality change on these items. That is a speed note, not a quality lever. Phone prefill time was not measured.
- **Subgroups (report only):**
  - The 26 items where the cut bites (R >= 4 passages): k1 -0.016.
  - The 6 manual (clean key-fact) golds: k1 -0.087 [-0.144, -0.015]. On these, neighbour passages helped, the opposite of dilution.
  - Lexical golds: k1 +0.011.
- **Against the hypothesis's comparison** (ORACLE-ST 4B ONLY - ADD +0.020 Opus / +0.006 Haiku on the 180 self-tests): the 1.7B gap is not larger than the 4B's. So "a weaker reader loses more to distractors" is not supported. This matches RD-1, where more kept chunks did not lower 1.7B conversion.
- **Reading with RD-1 and ORACLE-REAL:** on real items the 1.7B's failure with the fact in hand is reading capacity, not clutter or chunk form. Gold-first, gold-only and chunk features all move U by <= 0.02.

## Method (as frozen)
- Items: the 30 ORACLE-REAL ids (= CHUNKCLEAN's list). R is reused from ORACLE-REAL (not regenerated, same mini, same base tree).
- Patch `dilution.vs-litepacks.patch` (sha256 050340b8) = the ORACLE patch + `BOAR_ORACLE_K`: after gold-first placement, keep the first k passages. No refill, no prompt change.
- Gate: oracle:first + oracle:k on 30/30 in every arm, 0 void. The cut bit on 28 / 27 / 26 items (k1 / k2 / k3). 2 items have no kept list (health extractive) and are identical across arms.
- Judging: only texts with no byte-identical judged twin in the pool (LITEPACKS K0/K3 v0.1, ORACLE-REAL, CHUNKCLEAN C/P read only, these arms). Calls: k1 52, k2 48, k3 50 (ledger `runs/logs/calls.ledger`). 26/25/25 answers changed vs R.
- U = ratio of sums, paired item bootstrap B 2000, seed 11.

## Caveats
- n 30 < 35, so the result is indicative. One seed. The Haiku-low judge compresses gaps (the 4B comparison is +0.006 under Haiku).
- The cand80 cells of the hypothesis were not run; scope was the 30 real items only. The self-test 4B ONLY - ADD figure is context, not a paired DiD.
- Dev items only (bench v0.1 public ids).

## Files
`DILUTION-criterion.md` (+ .sha256), `dilution.vs-litepacks.patch` (+ .sha256), `items.ids`, `tools/{build_inputs.py, inputs.sha256, run_dk.sh, judge_dk.sh, dk_agg.py}`, `runs/req/dilution-k{1,2,3}-K3-v01gold-s42.requests.jsonl`, `traces/dilution-k{1,2,3}-K3-v01gold-s42.traces.jsonl`, `judgments/dk-k{1,2,3}.judgments.jsonl`, `aggregates/dilution-k.json` (sha256 3ac777f7...), `runs/logs/calls.ledger`, `PLAN.md`.

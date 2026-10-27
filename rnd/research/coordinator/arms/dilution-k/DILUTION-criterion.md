# DILUTION-K criterion (RD-4; frozen 2026-10-21 before any generation; coordinator subagent)

Question (ruler/hypotheses-round3-2026-10-21.json, RD-4): with the gold chunk fixed in slot [1], do the other kept passages suppress the 1.7B's
use of the fact? If so, cutting the context to gold-only beats gold + the full kept set, and the lite tier should assemble fewer passages.
Scope set by the coordinator: the 30 ORACLE-REAL items only (the cand80 cells of the hypothesis are not run here).

## Items (frozen)
`items.ids` = arms/oracle-real/items.ids (sha256 29e2bceccc22048c...; also CHUNKCLEAN's list). Dev only (bench v0.1 public ids). n 30 < 35 -> indicative.

## Arms (same engine, prompt wording, seed and host; they differ ONLY in how many kept passages follow the gold passage [1])
- **R = gold + rest (k full, exists):** ORACLE-REAL oracle arm, `../oracle-real/traces/oracle-K3-v01gold-s42.traces.jsonl` + its judgments. Not regenerated.
  Kept passages per item incl. gold: median 5 (0-8).
- **k1 = gold only, k2 = gold + 1, k3 = gold + 2:** `dilution.vs-litepacks.patch` (sha256 050340b8...) = oracle.vs-litepacks.patch + env `BOAR_ORACLE_K`:
  after the ORACLE placement (gold first, then the engine's kept passages in order, same context cap) only the first k passages are kept. No refill,
  no prompt change. Reason code `oracle:k:<k>:cut-<n>`. Unset = the ORACLE-REAL patch byte-for-byte in behaviour.
  Oracle file = `../oracle-real/tools/oracle-file.json` (sha256 ff3eba76...); requests `runs/req/dilution-k{1,2,3}-K3-v01gold-s42.requests.jsonl`
  (= the ORACLE-REAL requests, runId/arm renamed; shas in `tools/inputs.sha256`).
- Generation: the Mac mini, base tree <runner>/kiln/be-0cfd4a77-cut7-litepacks (answer.ts 0d1ac07d...), LITEPACKS 1.7B K3 system, seed 42, via
  lp-screens mini_gen.sh (slot lock; queues behind other jobs). Same host as R. Validity gate: every trace carrying `oracle:first` also carries
  `oracle:k:<k>` (30/30 expected on items that generate); otherwise that item's row is void (reported).

## Judge
Haiku 5.5-low (judge.v1-low via deepthink/tools/shard_judge.sh, N = 4, both orders, seed 7). Only answer texts with no byte-identical judged twin
(pool: LITEPACKS K0/K3 v0.1, ORACLE-REAL ctl-mini + oracle, CHUNKCLEAN C/P, then this arm's) are judged. Order k1, k2, k3. **Cap 200 Haiku calls**
(expected <= 170). 0 Opus, 0 paid.

## Readings (on the 30; U = ratio of sums vs the reference, 3 judge dims, both orders; declined = 0; paired item bootstrap B 2000, seed 11, 2.5/97.5 pct)
1. **dU k1 - R** with 95 % CI (primary). 2. dU k2 - R, dU k3 - R with CIs (curve). 3. Citation of [1] (share), any [n].
4. Warned share (answer opens with the memory warning). 5. CE-unwarned (corr <= 1.5, not declined, not warned). 6. Prompt tokens mean (timing.promptTokens).
7. Context: the ORACLE-ST 4B ONLY - ADD gap (+0.020 Opus / +0.006 Haiku on the 180, existing) as the comparison the hypothesis names (no new 4B run).
8. Subgroups (report only): items with >= 4 kept passages in R (the cut bites); lexical vs manual gold.

## Verdict rules (k1 - R)
- **PASS: dU >= +0.05 with CI low > 0 -> the other passages suppress fact use** (a lite-tier cap below 4 is worth a main-97 arm).
- **KILL: dU < +0.03 or CI low <= 0** (hypothesis kill) -> distractor count is not the 1.7B lever; the lite context cap stays.
- Separately: **no maintainer item if dU k2 - R < +0.02** (k1 is unreachable without an oracle). **CE-unwarned rising by >= 3 at k1 or k2** vs R is a stop for any cap recommendation.
- Between PASS and KILL: inconclusive at n 30 (indicative).

## Budget
calls_cap: Haiku 200 / Opus 0

## Rules
Dev sets only (no bench/v0.4, no blind/, no rnd/veil), no Opus, no paid API, no phone, no maintainer contact. Mini >= 25 GiB free; Docker, ollama and :8094 untouched. CHUNKCLEAN files are read, never written.

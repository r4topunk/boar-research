# CHUNKCLEAN criterion (frozen 2026-10-21 before any generation; coordinator subagent)

Question (hypothesis CHUNKCLEAN): the 1.7B reads a fact when the kept chunk is a short, self-contained statement of it (clean), and fails when the
same fact sits inside a long or template-damaged chunk; so chunk construction, not retrieval reach, is the pack lever. Source of the lead:
ORACLE-REAL post-hoc (6 hand-found clean key-fact chunks +0.106 [+0.054, +0.159] vs -0.009 for 24 rule-picked chunks; n 6, not a verdict).

## Items (frozen)
The 30 ORACLE-REAL items, `items.ids` (= oracle-real/items.ids, sha256 29e2bceccc22048c...). Dev only (bench v0.1 public ids). n 30 < 35 -> indicative.

## Arms (same engine, prompt, K3 context; they differ ONLY in the body text of the forced passage [1])
- **R (rule-picked, exists):** ORACLE-REAL oracle arm, traces `../oracle-real/traces/oracle-K3-v01gold-s42.traces.jsonl` (gold chunk forced to [1], full pack chunk text) and its judgments. Not regenerated.
- **C (clean):** passage [1] body = engine section prefix (unchanged) + the clean text. Clean text = 1-3 verbatim sentences of that same pack chunk
  that state the key fact (for key-facts tables / spec tables: up to 4 verbatim lines), no template residue, no added words. Spans may be shorter
  than a sentence only to drop residue (markdown `**`, table pipes, "Ans. (a)", "For example,", a broken "up to ."); spans are joined by a space
  (sentences) or a newline (lines). Extracted by hand by the coordinator subagent reading the chunk (0 LLM calls); `extractions.json`
  (sha256 e294cbdc6850d1b6...) + `extraction-log.jsonl` (source chunk id per item); `tools/build_arms.py` asserts every span is a verbatim substring
  of the chunk text (`gold-chunks.json`, sha256 c0e92dbd4b4dd7e2..., dumped by `tools/dump_gold.py` from the K3 kit files).
- **P (clean + rest):** passage [1] body = section prefix + clean text + "\n\n" + the original chunk text.
- Engine change: `chunkclean.vs-litepacks.patch` = oracle.vs-litepacks.patch + optional `orig`/`text` fields in the oracle entry: when `text` is set and
  the gold passage body ends with `orig`, that suffix is replaced by `text` (reason code `oracle:text-replaced`; otherwise `oracle:text-mismatch`). Without
  `text` the patch behaves exactly as the ORACLE-REAL patch. Oracle files `tools/oracle-C.json` (sha256 3a6a2fdcc673e8c0...), `tools/oracle-P.json`
  (afb5b739044df2eb...); requests `runs/req/chunkclean-{C,P}-K3-v01gold-s42.requests.jsonl` (9b61fba9fa3282a8..., 813567e555ca1cb0...) = the ORACLE-REAL requests, runId/arm renamed.
- Generation: the Mac mini, same base tree (<runner>/kiln/be-0cfd4a77-cut7-litepacks, answer.ts 0d1ac07d...), LITEPACKS 1.7B K3 system, seed 42, via
  lp-screens mini_gen.sh (slot lock). Same host as R (the mini decodes deterministically run to run, LP-SCREENS 37/37). Validity gate: every trace that
  carries `oracle:first` also carries `oracle:text-replaced` (30/30 expected); a mismatch voids that item's C/P row (reported).

## Judge
Haiku 5.5-low (judge.v1-low via deepthink/tools/shard_judge.sh, N = 4, both orders, seed 7). Only answer texts with no byte-identical judged twin
(pool: LITEPACKS K0/K3 v0.1, ORACLE-REAL ctl-mini and oracle judgments, then this arm's) are judged. **Cap 200 Haiku calls** (expected <= 120). 0 Opus, 0 paid.

## Readings (on the 30; U = ratio of sums vs the reference, 3 judge dims, both orders; declined = 0; paired item bootstrap B 2000, seed 11, 2.5/97.5 pct)
1. **dU C - R** with 95 % CI (primary). 2. dU P - R with CI. 3. dU C - mini K3 control and P - control (context).
4. Citation: share citing [1]; share citing any [n]. 5. CE-unwarned (corr <= 1.5, not declined, not opening with the warning line). 6. Warned share.
7. Prompt tokens (timing.promptTokens) mean per arm. 8. Subgroups (report only): lexical vs manual gold; Y vs P label; already kept in K3 vs not.

## Verdict rules (C - R)
- **PASS: dU >= +0.05 with CI low > 0 -> chunk construction is a lever** (a clean-chunk build of the packs is worth an arm on the main 97).
- **KILL: dU < +0.02** -> chunk cleanliness does not explain the 1.7B's reading failure on these items.
- Otherwise: inconclusive at n 30 (indicative).
P - R is reported with the same thresholds, without a verdict of its own.

## Rules
Dev sets only (no bench/v0.4, no blind/, no rnd/veil), no Opus, no paid API, no phone, no maintainer contact. Mini >= 25 GiB free; Docker, ollama and :8094 untouched.

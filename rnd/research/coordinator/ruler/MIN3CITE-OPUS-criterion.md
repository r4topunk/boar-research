# MIN3CITE-OPUS criterion (frozen 2026-10-21 before any Opus call of this pass; 0 judge calls spent before this freeze)

## Question
Does the MIN3CITE stage-2 PASS (Ministral-3-3B + citation prompt v2 vs the 1.7B control, MAIN 97 K0 seed 42; Haiku 5.5-low dU +0.0623
[+0.0366, +0.0891], arms/min3cite/MIN3CITE.md, criterion 3b17dbfd) stand under the Opus judge? Source: ruler/revisit-closed-2026-10-21.json,
entry "MIN3CITE (Ministral-3-3B + citation prompt v2)", artefact type judge-family (Haiku under-calls correct answers; MIN3CITE answers are 2.3x
longer, so the Haiku-Opus offset may not be symmetric; length bias is a known judge artefact). This pass does not reopen the Haiku verdict.
MIN3CITE is not sent to the app maintainer regardless of the verdict (about 3x projected phone answer time).

## Arms (existing traces, no generation; MAIN 97 = arms/lp-screens/main-97.ids)
- Control: 1.7B lpctl-K0-main-s42 (arms/lp-screens/control/traces). Every one of its 97 units already has an Opus judge.v1 row pair (GEMMA-OPUS-MAIN
  reuse pool); reused, 0 new calls (asserted by the prep).
- Candidate: arms/min3cite/traces/min3cite-K0-main-s42.traces.jsonl (sha256 cb39b24747e22e38...).
- Report only: Qwen3-4B VS4B traces (gemma4-e2b-vs4b K0 main s42), never judged in this pass; Opus rows exist for 61/97 of its units.

## Step A (0 calls) - tools/min3cite_opus_analyze.py A (sha256 5dab10308980b067...)
Answer length (outputTokens median/mean on live items, words), citation counts ([n] in text, answer.cited kept), Haiku per-item deltas
(changed, quartiles, Spearman of d vs token delta), the Haiku metrics of step B, the Haiku length views, and Haiku MIN3CITE - 4B (report only).
Output ruler/MIN3CITE-OPUS-stepA-2026-10-21.json. Step A has no gate: step B runs regardless (it is the question).

## Step B - Opus
- Unit = unique (item id, answer text). Unit list frozen in ruler/min3cite-opus-main/in/set.json (sha256 e102c04942ce5a12...) by
  tools/min3cite_opus_prep.py (sha256 ec6f1358981f968a...): MIN3CITE 22 units reused (byte-identical to existing Opus-judged texts), 75 new
  (v01 42, cooking 14, money 19) -> planned 150 calls.
- Judge: judge.v1 bytes, Opus (arms/deepthink/tools/shard_judge.sh <traces> <out> <bench> <ids> <sys> 4 opus = node harness/judge.mjs
  --judge-model opus --gap-ms 0 --seed 7), both orders, N = 4 shards, via tools/min3cite_opus_run.sh (sha256 36c34dc244b54c4f...).
- **calls_cap: Opus 150 new** (reuse first). Haiku 0, paid API 0, generation 0, phone 0, mini 0. A stopped shard is fixed and rerun, never
  skipped; every unit needs both orders before analysis.

## Analysis (tools/min3cite_opus_analyze.py B; definitions = gemma_opus_analyze.py / confirm_report.py on labels.py labels with Opus corr)
- U = sum(s, := 0 for trace-declined) / sum(sref); dU = U(MIN3CITE) - U(1.7B) on the 97 paired ids; 95 % CI = paired item bootstrap,
  random.Random(11), B 2000, sorted[50] / sorted[1949].
- **Decision: the PASS stands under Opus iff dU >= +0.03 AND CI low > 0. Otherwise "PASS does not stand under Opus".**
- Reported (no decision weight): CE-unwarned count and rate change with CI, CE any, declines, warned, refusals R; default-mode dU; U on items both
  answer (both shown) with dU CI; length-adjusted views (no truncation re-judge): L1 = dU on both-shown items where MIN3CITE's outputTokens <= the
  1.7B's median live outputTokens; L2 = dU on both-shown items where MIN3CITE tokens <= 1.5 x the 1.7B's; L3 = OLS of per-item score delta on token
  delta, intercept = dU predicted at equal length, with bootstrap CI; Spearman of per-item s Opus vs Haiku per arm and of the per-item deltas;
  Opus - Haiku offset per arm and the dU shift; MIN3CITE - 4B under Opus on the 4B units already Opus-judged (report only, partial).

## Sentences (chosen mechanically)
- Stands: "Under Opus, MIN3CITE is +X U over the 1.7B on MAIN 97 (CI a...b), 1 seed, dev; Haiku +0.062. Not sent to the app maintainer: about 3x answer time."
- Does not stand: "Under Opus, MIN3CITE is not separated from the 1.7B by the +0.03 rule on MAIN 97 (dU +X, CI a...b), 1 seed, dev; the Haiku PASS
  (+0.062) does not transfer."
- The length views qualify the sentence ("the gain survives / does not survive at equal length") but never change the verdict.

## Known limits (stated before the run)
One seed; n 97 dev (v0.1 57 + cooking 20 + money 20); the judge sees the warning line in warned texts; many control units were exposed to Opus in
earlier passes; length views are observational (no re-judging of truncated answers); 4B comparison partial and report only.

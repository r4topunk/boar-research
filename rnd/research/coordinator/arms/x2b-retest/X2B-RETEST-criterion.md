# X2B-RETEST criterion (frozen 2026-10-21, before any generation)

Source: ruler/revisit-closed-2026-10-21.json entry "HEADPASS-X2b (adopted) + RETFLOOR / RETV1ORC (append hygiene)", verdict retest-now.
Question: do X2b's appended chunks (X1 head-pass neighbours + budgeted dense picks) still pay on real items under the default-mode metric, or do they only pad?
Scope set by the coordinator (2026-10-21): K1 pack set, ruler/ids/stage1-pool.ids (87; sha256 in stage1-pool.ids.sha256), Haiku only (no Opus).

## System and arms
System = LITEPACKS 1.7B (cut7-headpass-x2+litepacks tree, Qwen3-1.7B Q4_K_M, LITEDECLINE_OFF=5, --reasoning off, seed 42, adapter be/adapter-litedecline.ts), mini, gen slot lock.
Requests = the LITEPACKS K1 requests, byte for byte except runId and config.arm (null-cal/tools/mkreq_pool.py).
| arm | what | input | sha256 |
|---|---|---|---|
| ON (control) | X2b on (packHeadPass a2 + packDense2 append-budget), the existing mini control | null-cal/control/pool-K1.json (traces lp-screens/control/traces/lpctl-K1-main-s42 + null-cal/control/traces/poolctl-K1-st180-s42) | n/a |
| OFF | X2b off: the adapter deletes packHeadPass and packDense2 from the answer settings; retrieved list unchanged | x2b-off.patch | a6018c67fa5f10c1a9ddde53ac013ae66b58a8dc54c7b5932647e5bbd3cfe1a7 |
| V1orC | X2b on + RETFLOOR V1orC append gate (keep an append iff onSubject OR cosine >= 0.70) | v1orc.patch (= retv1orc/retv1orc.patch) | 93b9be73ab192d063b394c201d06ddf8d9cb4de32f71d4e83dad6f335398e288 |
Run: `OUT_BASE=arms/x2b-retest GEN_ONLY=1 bash x2b-retest/tools/run_pool_x2b.sh <x2boff|x2bv1orc> K1 ../ruler/ids/stage1-pool.ids x2b-retest/<patch>` (cwd arms), then the same command without GEN_ONLY to judge.
tools/run_pool_x2b.sh = null-cal/tools/run_pool.sh + one GEN_ONLY line (no other change).

## Judge
Haiku 5.5-low, judge.v1-low, N = 4 shards, both orders (deepthink/tools/shard_judge.sh). Only answers whose text differs from the ON control are judged; byte-identical answers reuse the control judgment.
Cap: 200 Haiku calls total over both arms. If the changed-answer count needs more than 200 calls: OFF judged in full first; V1orC judged on its real (non st-) ids first, then st- ids in file order, until the cap; unjudged items leave that arm's paired stats and are listed.
0 Opus, 0 paid, 0 phone.

## Metrics (default-mode product, null-cal/tools/labels.py)
Per item: R = decline or warned (the user sees a refusal); s_d = 0 if R else s; CEu = CE and not warned.
- U_d(set) = sum s_d / sum sref. Paired delta (arm - ON) with item bootstrap B 2000 seed 11, 95 % percentile CI.
- U on covered: U_d restricted to items with >= 1 retrieval.kept source in the ON control.
- CE-unwarned count, refusal count (R), changed answers, changed contexts (kept chunk ids differ).
- Prompt tokens: mean timing.promptTokens over items with promptTokens > 0 in both arms. Retrieval wall: mean and p50 timing.retrievalMs.
Sets: REAL = stage1-pool ids not starting with "st-" (divergent-main 30 + sentinels-main 7 = 37); ST = the 50 st- ids (pack-written self-tests answered with the K1 kit); POOL = all 87. Decisions read on REAL; ST and POOL reported.

## Reading rules (frozen; from the revisit entry, adapted to the coordinator scope)
1. **X2b stays adopted iff ON - OFF >= +0.02 U_d on REAL with paired CI low > -0.01.**
   Otherwise: if |ON - OFF| < 0.02 and CEu(ON) <= CEu(OFF) on REAL -> "real-item-neutral" (X2b may stay default, but claim text says the gain is on pack-written questions only).
   If ON - OFF <= -0.02 or CEu(ON) > CEu(OFF) + 1 on REAL -> X2b "pads on real items": engine note to gate appends (or drop X2b on kit-only installs).
2. **V1orC adopted (as the append gate in the engine note) iff V1orC - ON >= -0.01 U_d on REAL (point estimate) AND mean prompt tokens fall >= 15 % vs ON on POOL live items.** CEu on REAL must not rise by more than 1.
3. n 37 on REAL gives an MDE near 0.05; a contrast landing within 0.02-0.05 of a bar is reported as underpowered; seed 43 is not in this run.

## Sanity (invalidate, not a verdict)
n/n trace rows per arm, 0 error rows; OFF: 0 "headpass:add" reason codes; V1orC: a "retfloor:" reason code on every item that had pending appends; items with 0 tokens in ON are unchanged.

## Budget
calls_cap: Haiku 200 / Opus 0
opus_clause: none

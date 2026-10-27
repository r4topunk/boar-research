# SEEDGEN — is 4B self-test generation deterministic? (2026-10-13, MacBook, 0 judge calls, 0 paid calls)

## TL;DR
- **Generation is already byte-deterministic.** qa-health-se, 20 OFF requests (cut 7, run_selftest.sh unchanged), 4 runs:
  A1 vs A2 **20/20** identical answers, B1 vs B2 **20/20**, A1 vs B1 **20/20**, A2 vs B2 **20/20**; and A1 vs the original OFF run
  made 8 h earlier (st-qa-health-se-cut7-s42, 05:18Z) **20/20**. B1/B2 dumped prompts: byte-identical (15 LLM prompts; 5 items have no LLM call).
- **Cause of DENSECHUNK-ST2's 56/102:** not sampler noise. "Kept sources unchanged" was keyed on (title, section[, source]); the ON arm
  (packDense2) changes the chunk TEXT inside the same sources, so the prompt differs. Pooled over the 9 packs, of the 102 kept-unchanged items:
  43 have a different prompt length (promptTokens) → 0/43 same answer; 34 same prompt length → 32/34 same; 25 no-LLM (instant tier) → 24/25 same
  (the 1 = qa-health-se-015: the kept set has the same distinct keys but different multiplicity/chunks). So 56/59 same when the prompt length matches.
  The 2 remaining (qa-travel-se-004, -012) have equal promptTokens but differ; the ON prompts were not dumped, so equal-length-different-text
  vs nondeterminism is UNVERIFIED for them (the A/A probe makes nondeterminism unlikely).
- **Recommended runner setting: no change.** The determinism comes from settings already in place (below). Fix the metric, not the runner:
  pair runs on prompt identity (dumped prompt hash, or promptTokens as a proxy), not on kept titles.
- ST2 consequence: the 46 differing kept-unchanged answers are treatment effects (different context text), not a noise floor; paired CIs
  on the 180 items are not inflated by generation noise on the MacBook CPU path.

## Evidence: what makes it deterministic (kiln-local/be-0cfd4a77-cut7, adapter 6298e5d3)
- Seed: one seed per request file (adapter.ts l.129-130 forces all requests to share `seed`; l.663 passes `R0.seed` = 42), sent on
  every request (server.ts `samplerFor` → `seed`); llama-server re-seeds the sampler per request, so same logits → same tokens at T 0.7.
- Server launch (adapter.ts l.422): `-t 4 -tb 4 -c 4096 -ngl 0 -np 1 --jinja --cache-ram 0` + per request `cache_prompt: false`
  → one slot (no batch-composition effects), no prefix/KV reuse, fixed thread count, CPU build (spikes/llama-b11010-cpu, no Metal).
- Requests are sequential (one item at a time), timeout 600 s, no retries in the server path.
- Candidate causes checked and excluded for this path: per-request random seed (no: fixed 42), -np > 1 / continuous batching (no: -np 1),
  prompt-cache reuse (no: cache_prompt false, --cache-ram 0), thread scheduling (no effect observed at -t 4: 4/4 pairs identical).

## Change to apply to the shared runners
None for run_selftest.sh / run_selftest_dense2.sh / stdeep-remote-run.sh (they all launch through the adapter's makeServerEngine).
Optional (measurement only, generation unchanged — B = A with it, 20/20): add a prompt dump so pairs can be matched on prompt identity:
```diff
-EXTRA=(--backend server --server-bin "$SRV" --threads 4 --timeout-ms 600000)
+EXTRA=(--backend server --server-bin "$SRV" --threads 4 --timeout-ms 600000)
+[ -n "${DUMP:-}" ] && EXTRA+=(--dump-prompts "$DUMP")   # e.g. DUMP=${OUT%.traces.jsonl}.prompts.jsonl (≈ 30 KB / 20 items)
```

## Caveats
- Only the MacBook CPU llama-server path at -t 4 was probed. Results are NOT guaranteed to carry across: a different thread count,
  machine (the mini's M4 + its own llama-b11010 build-cpu), Metal/GPU build, or llama.cpp build can change logits → compare only runs
  made on the same machine/build/threads. Not verified on the mini (no ssh in this arm); its committed adapter has the same `-np 1` launch line.
- The deep tier (thinking budget, 35B) was not probed; same server flags, so same expectation, unmeasured.
- One pack (qa-health-se, 20 items, 15 LLM calls) — small n, but 100 % across 5 pairings incl. an 8 h gap.

## Standing tool
`python3 -I arms/seedgen/tools/same_answer.py <tracesA.jsonl> <tracesB.jsonl> [--ids file] [--label x]`
→ one JSON line (all / kept_unchanged / kept_unchanged_prompt_same blocks: n, same_answer, same_first50, ids that differ with same prompt)
+ a one-line summary on stderr. Read `kept_unchanged_prompt_same` as generation determinism, `kept_unchanged` as the old ST2 field.
ST2 per pack (kept-unchanged same / n; same-prompt-length same / n): travel 7/11, 7/9 · ethereum 5/10, 5/5 · bitcoin 3/4, 3/3 · health 6/13, 6/7 ·
outdoors 5/10, 5/5 · firstaid 13/16, 13/13 · medlineplus 9/15, 9/9 · factbook 3/9, 3/3 · simplewiki 5/14, 5/5 → 56/102, 56/59.

## Files
tools/run_probe.sh (copy of run_selftest.sh + DUMP/THREADS env), tools/probe.sh (A1 A2 B1 B2, resumable), tools/same_answer.py,
runs/{A1,A2,B1,B2}.traces.jsonl (+ .status/.log/.server.log, B*.prompts.jsonl), runs/same-*.json, runs/probe.log.

## Addendum 2026-10-13 22:5x — same_answer.py pairing fixed (PIPELINE-AUDIT-2026-10-13 F8)
The tool paired "same prompt" on `promptTokens` equality (None == None counted; kept compared as a set). Fixed (a parallel session): items with no LLM call are reported apart in a new `kept_unchanged_no_llm` block; kept lists are compared as multisets. Re-run on the ST2 inputs: the reported **"56/59 same-prompt identical" becomes 32/34 same-prompt (LLM items) + 23/23 no-LLM identical**; kept-unchanged goes from 56/102 to 55/60 (42 items differed only in how often a source was kept); health-015 drops out. The RULE 27 conclusion (generation byte-deterministic on the MacBook CPU path; A/A 20/20 × 5) is unchanged. crowdq.json / stack.json committed earlier carry the old field (stack pooled same-prompt 55/55 → 27/27 under the new definition); they are not regenerated here — the next run of their agg tools will write the new block.

Ledger note (2026-10-13, LEDGER-FIXES §5): no criterion file by design (measurement / descriptive / tooling); nothing to freeze.

## Addendum 2026-10-14 (PR-1 identity run): first observed exception to byte-determinism
On the 60 v0.1 items, pr1 (cut 7 rebased) vs the reference run v01-cut7-stack-off-s42: 59/60 byte-identical; lan-exp-007 differs at output token 49 ("land area" vs "territory"). Re-running the item on the cut 7 tree and on pr1 with prompt dumps gives byte-identical prompts and the SAME new answer on both trees: the reference run (load average 18.8 at the time) was the non-reproducible one. Reading: RULE 27 holds at low load; under heavy host load one divergence in 60 was observed. Rule refinement (RULE-CHANGES 27a): identity checks run on an idle host (load < 4), and a 1/60 text divergence with identical prompt, tier and kept set is reported as "same measured engine" when the re-run reproduces the new text on both trees. Evidence: arms/pr1/gen-compare.txt.

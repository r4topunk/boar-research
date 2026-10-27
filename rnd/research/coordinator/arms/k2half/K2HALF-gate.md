# K2HALF step 0 — greedy-agreement gate (2026-10-12, mini, 0 judge calls) — **FAIL**
- Model: Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf (qwen35moe, 40 layers): expert_count **256**, expert_used_count **8** (+ shared expert, untouched) → K2HALF keeps **4**, softmax gating, norm_w = true.
- Patch `k2half.llama.patch` (sha256 5897e688…, 3 hunks, +20/−2) on llama.cpp 4bc272f, `src/llama-graph.cpp` `build_moe_ffn` (≈ l.2103 before `// select experts`; l.2134 norm_w sum; l.2328 aggregation loop bound). Env `LLAMA_MOE_HALF_K=1` (read once): argsort top-k → sum p over top-k = normaliser; select top-k/2; weight_i = p_i / Σ_{top-k} p_j (not renormalised over the kept half). Gotcha: the aggregation loop uses `hparams.n_expert_used(il)`, so the loop bound had to follow the halved count (first build aborted in ggml_view_2d at graph reserve).
- Stock path: `--override-kv qwen35moe.expert_used_count=int:4` is honoured (scalar key → `get_key`, which applies overrides) = the paper's renormalised-over-selected worst case; not run here.
- Build: `build-k2half/` (Ninja, Release, GGML_METAL=OFF, GGML_BLAS=ON (Apple), GGML_NATIVE=ON, BUILD_SHARED_LIBS=ON, MTMD/UI/CURL/TESTS/EXAMPLES off; target llama-server only; rpath → own bin/). Source reverted to stock after build (`git status` clean); build-cpu untouched. Logs <runner>/kiln/build-k2half.*.log.
- Gate: 10 DEEPPAR item ids (all public v0.1) as plain user messages, `/apply-template` with enable_thinking=false (empty think block) → `/completion` temp 0, top_k 1, n_predict 64, seed 42, -t 4 -c 4096, one server at a time (stock :8099, patched :8098).

| id | prefix agree | exact-match frac | | id | prefix | exact |
|---|---|---|---|---|---|---|
| lan-exp-001 | 0/64 = 0.00 | 0.03 | | lan-ref-002 | 8/64 = 0.13 | 0.14 |
| vit-cry-001 | 24/64 = 0.38 | 0.39 | | lan-cmp-001 | 2/64 = 0.03 | 0.16 |
| vit-cry-004 | 15/64 = 0.23 | 0.52 | | trv-004 | 13/64 = 0.20 | 0.20 |
| vit-cry-003 | 8/64 = 0.13 | 0.14 | | lan-exp-007 | 21/64 = 0.33 | 0.39 |
| lan-rsn-007 | 9/64 = 0.14 | 0.59 | | vit-cry-009 | 18/64 = 0.28 | 0.30 |

- **Mean agreement: prefix 0.184, exact-match 0.286 → FAIL vs ≥ 0.80.** (Reference: bmoe vs llama-server in DEEPPAR diverged at token ≈ 80 on 600-token contexts; here ≈ 12.)
- Speed (means over 10 short prompts, 20–48 tokens): decode 9.99 → **18.30 tok/s (×1.83)**; prefill 7.8 → 19.6 tok/s (×2.5; short-prompt prefill is noisy, stock first-item includes page-in). Peak RSS 7.14 → 6.76 GiB (mmap; fewer expert pages touched).
- Quality signal: on lan-rsn-007 the patched output says the Berlin Wall was "built in **1989**" (stock: 1961) — a factual flip in the first line; others mostly paraphrase drift.
- Caveats: greedy token agreement is a strict proxy (paper measures task accuracy, not agreement); Q2_K_XL quantisation may compound the routing change; 1 seed, no thinking, 64 tokens; not tested: stock override k=4 (renormalised) for comparison, k=6, or the paper's model class.
- Files: aggregates/greedy-gate.json, aggregates/outputs-public.jsonl (public prompts only), build-tail.log. Servers stopped; mini free disk 26 GiB.
- Next (if any): a cheaper non-inferiority check would be a V-para slice with Haiku L1 — the ×1.8 decode is real, but the gate as frozen says FAIL; do not proceed without a new criterion.

Ledger note (2026-10-13, LEDGER-FIXES §5): no criterion file; the gate was pre-stated in QUEUE l.961 — nothing to freeze (a sha now would fake a pre-registration).

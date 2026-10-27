# exp-27 RUN sheet: cross-encoder gate L1 (for Kiln, Mac mini)

TL;DR: one desktop run, Android 4B, kit A, seed 44, 44 items (retrieval-inkit ∪ outofkit-quality), on the **existing** `be-0cfd4a77` tree.
- **No new engine tree:** the gate is a runner-side hook, a copied runner dir plus a 43-line patch.
- **New disk on the mini:** ~438 MB (the reranker GGUF) plus a runner copy of a few hundred KB.
- **Base:** the existing `and-qwen-s44` run (same seed, same tree). Answers whose prompt the gate doesn't change should come out identical, which doubles as a determinism check.

## What the gate does (one knob)
- **Where:** just before every generate that carries messages, the engine's system prompt ends with `Context:\n[1] …\n\n[2] …`.
- **Passage [1]** (the engine's first) is always kept.
- **Passages [2..4]** (≤ 3 pairs) are scored against the question with **bge-reranker-v2-m3 Q4_K_M** and dropped when the score is < **τ = 0.05**.
- **Numbering:** the remaining passages keep their numbers, so the engine's citation post-processing still maps `[n]` to the same source.
- **Event logged:** one per gated generate, `{type:"other", kind:"rr-gate", tau, scored:[{n,score,kept}], dropped, ms}`.
- **τ origin:** τ 0.05 sits below the lowest helpful passage in exp-25: 0.08 among the 53 Opus-labelled s44 passages, which are in-sample dev data.

## Files (sonar/exp/27-rerank-gate-l1/)
| File | sha256 |
|---|---|
| `rrgate.ts` (copy into the runner dir) | dd6d4ddd7a0e060ff99b017b6a5315f79c87d5311a9272100d30522f4a8f7d3c |
| `runner-rrgate.patch` (`adapter.ts`, against boar-eval 535ad15 runner) | 547f03a7b5d2f2d12f47bb4b0f57c4d65cd558293fc21862133669e5be6c2248 |
| reranker GGUF (MacBook: Sonar scratchpad `bge-m3-q4km.gguf`, 438,376,864 B) | e186a244ed455b4ab66ec64339ce7427a6ae13f5c0b5e544de96e50f0f8b3673 |

The patch also passed `ts.transpileModule` (0 diagnostics) and `rrgate.test.mts` (round trip on all 39 s44 context prompts; drop keeps numbering).

## Steps (adapt to your mini conventions)
1. `scp` the GGUF to the mini (e.g. `<runner>/shared-models/bge-reranker-v2-m3-q4km.gguf`) and check the sha256.
2. Runner copy in the existing tree:
   ```sh
   cd <runner>/kiln/be-0cfd4a77 && cp -a be be-rr
   ```
   Then copy `rrgate.ts` into `be-rr/` and run `cd be-rr && patch -p1 < runner-rrgate.patch`. The paths in the patch are `a/adapter.ts`/`b/adapter.ts`; use `-p1` from inside `be-rr`.
3. Requests: `and-qwen-s44.requests.jsonl` (seed 44, same config), restricted with `--ids` to:
   `lan-exp-001,lan-exp-002,lan-rsn-001,lan-rsn-002,vit-trv-003,vit-cry-005,vit-sci-002,vit-hlt-002,vit-hlt-003,lan-ref-002,lan-cmp-003,lan-ref-004,lan-exp-003,lan-exp-004,lan-exp-005,lan-exp-006,lan-rsn-005,lan-rsn-007,lan-exp-007,lan-ref-001,vit-trv-004,vit-hlt-001,vit-sci-001,vit-cry-010,vit-sci-003,vit-cry-002,lan-ref-003,vit-cry-007,vit-cry-009,vit-cry-004,vit-hum-004,lan-rsn-003,vit-hum-006,vit-cry-008,lan-cmp-002,lan-cmp-001,lan-hlt-002,vit-hum-002,vit-hum-005,lan-hlt-003,vit-hum-003,lan-cmp-004,lan-cmp-005,lan-hlt-001`
4. Run with `BOAR_EVAL_RUNNER_DIR=be-rr`, plus the following in the **mini-side process environment**:
   - `BOAR_RR_GATE=<gguf path>`
   - `BOAR_RR_TAU=0.05`
   - `--event-source-text` (so key-in-context can be checked)
   - `--dump-prompts` (to diff the prompts against s44)
   - Suggested run id: `rrgate/and-rr-s44-l1`.
5. Judge (judge.v1 opus) **only the items whose prompt changed** (any `rr-gate` event with `dropped` non-empty). Their base is `and-qwen-s44`'s judgment for the same item. For unchanged items, just report whether the answer text is identical to s44.

## What to send back to Sonar
- Run dir path. Count of items with a drop. Identical-answer count on unchanged items.
- Judge table for changed items: base vs arm score, label pass/fail/cw.
- `rr-gate` ms per generate (p50/max).
- Any error.

Sonar reads every changed answer.

## Prediction (L0 dry run on the s44 prompts, this MacBook, `dryrun.mts` → `dryrun-tau0.05.json`)
- **Counts:** 44 slice prompts, 22 with ≥ 2 passages, 37 pairs. **10 items change** (15 passages dropped): lan-rsn-001, lan-cmp-001, vit-trv-003, vit-cry-005, vit-hlt-003, lan-ref-002, lan-ref-004, lan-exp-004, lan-rsn-007, lan-exp-007.
- **Keys:** 0 key-bearing passages dropped, 0 items lose the key from context. 89 ms/pair on a loaded M1.
- **Watch:** lan-cmp-001 (Brazil vs Russia). Both Russia passages score 0.000 and are dropped: a single-entity passage scores low against a two-entity question. This is the known failure mode for comparison questions.

## L1 pass rule (fast loop; development data, not frozen)
- Changed items: mean judge Δ ≥ 0 and confident-wrong count not up.
- No changed answer reads worse after Sonar's read-through. Each score drop ≥ 1.0 is explained.
- 0 new unsafe (no danger items in these slices; safety guard at L2).
- **Kill:** CW up, or Δ < 0 on changed items.

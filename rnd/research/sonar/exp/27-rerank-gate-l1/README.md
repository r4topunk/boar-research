# exp-27: cross-encoder gate on prompt passages (bge-reranker-v2-m3), L0 + local L1 proxy (Sonar, 2026-10-02 night)

TL;DR: **KILL** (fast loop, ~1 h of the 2 h box; the mini L1 was cancelled before it ran).
- **Filter:** dropping passages [2..4] with score < 0.05 changes 10/44 slice prompts and drops no key-bearing passage. Answers don't get better: 0 better, 8 equivalent, 1 identical, **1 worse** (a comparison).
- **Coverage signal** ("no passage scores high → answer as no-source"): it can't tell "half of the comparison is missing" (vit-cry-005 max 0.976). AUC 0.587 for flagging confident-wrong answers.
- **Takeaway:** exp-25's AUC 0.912 (helpful vs unhelpful passages) is real. But the 4B was already ignoring the passages the gate removes, and its confident-wrong answers come from memory next to *relevant-looking* passages.

## Results
| Level | What | Numbers |
|---|---|---|
| L0 dry run (`dryrun.mts` → `dryrun-tau0.05.json`) | The gate (`rrgate.ts`) on and-qwen-s44's dumped prompts, retrieval-inkit ∪ outofkit-quality (44 prompts) | 22 prompts with ≥ 2 passages, 37 pairs; **10 items change, 15 passages dropped, 0 key-bearing passages dropped, 0 items lose the key**; 89 ms/pair (loaded M1, CPU 4 threads) |
| Local L1 proxy (`replay.mts` → `replay-proxy.json`) | The 10 changed items: s44 prompt vs gated prompt, same Qwen3-4B-2507 Q4_K_M, temp 0.7, top-k 40, top-p 0.95, min-p 0.05, seed 44 (adapter defaults). No engine post-processing, no judge; Sonar read every pair | **0 better, 8 equivalent, 1 identical (lan-rsn-007), 1 worse (lan-cmp-001)** |
| L0 variant B (`coverage_l0.mts` → `coverage-l0.json`) | max bge-m3 score over the first ≤ 3 passages as a "sources don't answer" flag vs the s44 judge (37 judged non-declined prompts, 13 with correctness ≤ 2) | AUC (low max → CW) **0.587**; passage-1 score 0.567. max < 0.05 flags 3/13 CW and 2/24 others. The engine's own `weakSources` flags 9/13 vs 10/24 |

Read-through of the proxy pairs:
- **lan-cmp-001** ("Does Brazil have more people than Russia?"): both Russia passages score 0.000 and are dropped. The arm then answers "No, Brazil does not have more people than Russia… Russia 144 million… Brazil 213 million. Therefore, Brazil has more people" (self-contradictory). The base answered "Yes" with 214M vs 141M. **Failure mode:** a passage about one side of a comparison scores ~0 against a two-entity question.
- **vit-cry-005** (Privacy Pools vs Tornado Cash): both arms deny that Privacy Pools exists. Removing passage [3] changes nothing, because the Privacy Pools passage never reached the prompt (see exp-26: the coverage gate blocks it).
- **The rest** (lan-rsn-001, vit-trv-003, vit-hlt-003, lan-ref-002, lan-ref-004, lan-exp-004, lan-exp-007): same facts, same quality. lan-rsn-001 loses a spurious [2] citation.

## Why it's dead
1. **What the gate removes:** passages the 4B already ignored; its answers on those items were already grounded in passage [1].
2. **Where confident-wrong comes from:** relevant-looking passages that miss the asked fact (vit-cry-005 Tornado Cash 0.976, vit-cry-009 0.968, vit-cry-003 0.946). A query–passage relevance score is high there, so neither the filter nor the coverage flag fires.
3. **Comparisons get hurt:** see lan-cmp-001.

Phone cost (est. 1.5–3 s on Android, +438 MB next to the 4B) is moot.

## What it leaves
- **The runner-side hook pattern:** `rrgate.ts` + `runner-rrgate.patch` change prompts without a new engine tree; reusable for any prompt-level arm while the mini can't build trees. Tests: `rrgate.test.mts` (round trip on 39 s44 context prompts).
- **The model:** `bge-reranker-v2-m3-q4km.gguf` now sits in `shared-models/` (Kiln copied it, sha e186a244…3673).
- **The lever for CW stays upstream:** get the missing fact's passage into the prompt (comparison entity split: `cards/comparison-entity-split-retrieval.md`; the exp-26 gate finding). Removing passages doesn't help.

## Caveats
- The proxy is 1 sample per arm at temp 0.7 with no judge; lan-cmp-001 is a noisy item (s42 answered "Russia" with the right numbers, see QUEUE #18). The kill doesn't rest on that one item. With 0 improvements in 10 changed prompts, the upside isn't there, and an engine L1 can't add improvements the prompt replay doesn't show.
- τ 0.05 and the exp-25 labels come from the same s44 passages (in-sample).

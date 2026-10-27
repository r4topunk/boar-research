# exp-02: Maple-Preview 20B-A1B (ternary MoE, in RAM) vs Qwen3-4B and Ling-3.0-tiny

Date: 2026-09-30 · Author: Kiln (R&D) · Hypothesis K1b in [`../hypotheses.md`](../hypotheses.md) · Approved by the coordinator 2026-09-30 (temporary disk floor + watchdog).

## TL;DR

- **Maple-Preview (20B total / ~1B active, ternary TQ2_0) is the closest runnable match to the post author's "big total, <1B active" shape.** On the same app contexts as exp-01, it answers about as fast as Ling. Its anonymous memory is almost nothing: **footprint 0.50 GiB**, against 4.58 GiB for Ling and 3.03 GiB for the 4B. Its ternary weights are not repacked and stay as clean, evictable mmap pages.
- **It always reasons.** Its chat template has no `enable_thinking` switch, so all 56 LLM answers came with a reasoning block, ~121 tokens at the median. **2 of the 38 factual answers came out empty**: the reasoning used up the 512-token `max_tokens`. They count as product failures, because the user would see a blank answer.
- **Quality, with one instrument on all three models: Plumb's blind hand labels on the factual 38.**

  | | Maple | Qwen3-4B | Ling-3.0-tiny |
  |---|---:|---:|---:|
  | Correct | 25/38 = **66%** | 26/38 = **68%** | 23/38 = **61%** |
  | Confident-wrong | **4** | 7 | 7 |

  Paired on the same questions, all three are tied: Maple vs 4B 3 vs 4 discordant items, p = 1.00; Maple vs Ling p = 0.69; Ling vs 4B p = 0.51.
- **The pre-registered kill rule KILLS Maple, by one question. The coordinator kept the rule, the official reading is a tie, and Maple is on the watchlist** (§5a). The rule is "Maple's % correct < 4B's, or its CW % > 4B's", and 66% < 68% triggers it. Dropping Maple's 2 empty answers does not change it: 69% vs 72%.
  - Everything else points the other way: the gap is 1 question with p = 1.00, Maple has **fewer** confident-wrong answers (4 vs 7), and 2 of its 13 misses are blank answers from the work budget, not knowledge errors.
  - The rule has no tolerance margin, so whether a 1-item, p = 1.00 gap should kill is the coordinator's call (§3.1). Kiln applies the rule as written.
- **Knowledge-collapse check** ([arXiv 2609.32902](https://arxiv.org/abs/2609.32902)): no evidence of collapse at n = 38. The ternary 20B-A1B matches the Q4 dense 4B within noise on factual questions.
- **Speed, same build (b11010):** Maple's TTFT is 4.8 s against the 4B's 7.5 s, and its total 5.5 s against 10.9 s. The 4B's answers and speed on b11010 are identical to exp-01 on `0e8c83e`, so Ling's exp-01 numbers are comparable too (TTFT 4.1 s, total 5.0 s).

## 1. Question

Does a ~1B-active ternary MoE with a 20B total parameter store, run fully in RAM, keep the 4B's factual quality at a lower cost in latency and memory? The risk is knowledge collapse in low-bit models ([arXiv 2609.32902](https://arxiv.org/abs/2609.32902)).

## 2. Setup

Same harness, same captured app contexts and same 64 questions as [exp-01](../exp-01-inram-moe-reader/README.md) (56 reach the LLM). The differences:

| Item | Value |
|---|---|
| Runtime | llama.cpp **b11010** (`4bc272f`, 2026-09-16; contains `maple`, PR #27000 = `3d10bcd`). Built in its own directory `<runner>/spikes/llama-b11010`, CPU only, `GGML_METAL=OFF`. **Build time 54 s** (configure 5 s + build 49 s, `-j4`), 297 MB. The exp-01 build was left untouched. Script: [`build-b11010.sh`](../exp-01-inram-moe-reader/harness/build-b11010.sh)<br>**Deleted from the mini on 2026-09-30** (coordinator, at r4to's request, to free disk; no process was using it). To reproduce: re-clone (`git clone --depth 1 --branch b11010 https://github.com/ggml-org/llama.cpp.git <runner>/spikes/llama-b11010`), then run `build-b11010.sh` through the heavy queue (~54 s). It asserts HEAD = `4bc272f` |
| Server flags | As in exp-01, plus **`--cache-ram 0`** (no host prompt cache), so the memory numbers are valid in a single pass |
| Model | `maple-preview-TQ2_0-head-Q4_K.gguf`, 5,901,782,560 B, sha256 `221f792cc9760d27a34f449b4229e258fa968a63bd4213993e45d9c0bb477a9e`, from `https://huggingface.co/deepgrove/maple-preview-GGUF/resolve/f5466f918e0c50cdb9d4d47a6f35813509a42a30/maple-preview-TQ2_0-head-Q4_K.gguf` (MIT). Arch `maple`: 24 layers, 256 experts, 8 routed |
| Chat template | The GGUF's own template: ChatML, handles `<think>`, **no `enable_thinking` variable**. The request still sent `enable_thinking=false`, which the template ignores. The server split the reasoning out (`--reasoning-format deepseek`) and it is kept in `reasoning`. `answer` is the final text only |
| Disk handling | Downloaded 15:36 with ≥20 GiB free. A **watchdog** checked free space every 60 s while the file existed, with a kill-and-delete action below 12 GiB ([`watchdog-disk.sh`](../exp-01-inram-moe-reader/harness/watchdog-disk.sh), log `runs/watchdog.log`). The minimum was **16.71 GiB**, with no alert. **GGUF deleted 15:49** (rc=0) |
| Load | 0 reruns, 0 flagged samples (the gate starts a request only below load 8) |

## 3. Blind hand-off (Lantern run 4)

- **File:** [`blind/maple-preview.factual38.raw.jsonl`](blind/maple-preview.factual38.raw.jsonl). 38 rows, one per id in `rnd/lantern/handoff/subset.factual.vitalik-lantern.json`, none missing.
- **Fields:**
  - `queryId`
  - `answer`: final text, reasoning excluded
  - `declined`: always `false`, because this harness has no app decline gate
  - `retrievedTitles`: the sources the model actually saw
  - `route`: `llm` / `no-llm`
  - `model`
- **Made by** [`export-blind.py`](../exp-01-inram-moe-reader/harness/export-blind.py). No grader was run and Kiln did not read the answers.
- **Empty answers in the subset:** `vit-cry-009` and `vit-fa-014`. Both hit `max_tokens` = 512 while still reasoning.

### 3.1 Result: blind hand labels, same instrument on all three models

Protocol (coordinator, 2026-09-30):
- Maple's labels: Lantern run 4, `rnd/plumb/data/hand-labels-run4-maple.json`, sha256 `56fe458d…cab9d`.
- The Qwen3-4B and Ling answers from exp-01 (llama.cpp `0e8c83e`) were shuffled into one file with opaque ids (`blind/baseline-mix.factual38.blind.jsonl`, sha256 `0e8ea2be…a997`, seed 20260930). The id → model map is sealed (`blind/map-SEALED.json`, sha256 `3cd6aaef…a958`).
- Plumb labelled the mix before any map or precheck was opened: `rnd/plumb/data/hand-labels-baseline-mix.json`, sha256 `62bf34e1…ccd`, verified.
- Same criteria as run 4. Plumb's ceiling caveat applies: he had seen some precheck `why` terms for these ids in runs 1–3.

Full table: [`kill-criterion.md`](kill-criterion.md), from [`kill-criterion.py`](kill-criterion.py).

| n = 38 | pass (Wilson 95% CI) | cw | fail | refused | empty |
|---|---|---:|---:|---:|---:|
| maple-preview | 25 = 66% (50–79%) | 4 | 7 | 0 | 2 |
| qwen3-4b | 26 = 68% (53–81%) | 7 | 4 | 1 | 0 |
| ling-3.0-tiny | 23 = 61% (45–74%) | 7 | 7 | 1 | 0 |

Items that only one side of each pair gets right:
- Maple-only vs 4B: `vit-fa-011`, `vit-fa-027`, `vit-hum-002`.
- 4B-only vs Maple: `vit-cry-003`, `vit-fa-022`, `vit-hum-005`, `vit-trv-004`.
- Exact McNemar p = 1.00.

Without Maple's 2 empty answers (n = 36): 69% / 72% / 64%, cw 4 / 5 / 5. The kill rule still triggers, on pass% alone.

What the hand labels say about the other instruments:
- **Hand labels vs precheck.** Precheck v2.1 gave Maple 53% (hand: 66%). In exp-01 it gave Ling 0 confident-wrong and the 4B 1; the hand labels find **7 each**. That confirms Lantern's decision: precheck CW% is not a metric.
- **The model ordering changed by instrument.** On the Lantern-52 precheck it was 4B 54% > Ling 50%. On the factual-38 hand labels it is 4B 68% > Maple 66% > Ling 61%. Every pairwise gap is within noise.

**Quality per second** (hand pass rate × 60 / total p50 from §4):
- Maple: 0.66 × 60 / 5.5 = **7.2 correct/min**.
- Ling: 0.61 × 60 / 5.0 = **7.3 correct/min**.
- 4B (exp-01 speed): 0.68 × 60 / 10.5 = **3.9 correct/min**.

## 4. Speed and memory (M4 CPU `-t 4`, full prefill per request, 56 LLM answers)

| Model | llama.cpp | TTFT p50 / p90 (first answer token) | total p50 / p90 | prefill tok/s p50 | decode tok/s p50 | peak RSS | **footprint (anonymous)** |
|---|---|---|---|---:|---:|---:|---:|
| **maple-preview** | b11010 | 4.8 / 8.2 s | 5.5 / 9.2 s | 232 | 79.2 (reasoning + answer) | 5.07 GiB | **0.50 GiB** |
| qwen3-4b | b11010 | 7.5 / 11.3 s | 10.9 / 14.6 s | 82 | 22.6 | 4.98 GiB | 3.03 GiB |
| qwen3-4b (exp-01) | 0e8c83e | 7.7 / 11.2 s | 10.5 / 15.3 s | 81 | 22.2 | 4.60 GiB* | 3.03 GiB* |
| ling-3.0-tiny (exp-01) | 0e8c83e | 4.1 / 5.7 s | 5.0 / 6.8 s | 158 | 59.3 | 5.53 GiB* | 4.58 GiB* |

\*The clean memory probe (`--cache-ram 0`) from exp-01 §5.

**The build does not change the result.** The 4B on b11010 produced **byte-identical answers** on all 64 items (fixed seed), and the same speed within noise (TTFT 7.5 vs 7.7 s, prefill 82 vs 81, decode 22.6 vs 22.2 tok/s). So the exp-01 numbers on `0e8c83e`, including Ling's, are comparable with Maple's on b11010.

### 4.1 Maple's time split: reasoning vs answer

The harness timestamps the first streamed token of any kind and the first answer token, so the **time** split is measured. The **token** split is estimated from the character share of reasoning vs answer text, because the server reports one `predicted_n` for both.

| Phase | p50 | p90 |
|---|---:|---:|
| Request → first token (≈ prefill) | 2.7 s | — |
| Reasoning (first token → first answer token), measured | **1.6 s** | 3.0 s |
| Answer (first answer token → end), measured | 0.7 s | — |
| Reasoning tokens (estimated) | ~121 | ~279 |
| Answer tokens (estimated) | ~61 | — |

- **Without the reasoning phase**, Maple's time to the first answer word would be about the prefill alone, **~2.7 s p50**. That is 1.5B-class latency.
- **Decode tok/s covers both phases**, and the model is the same, so the rate applies to either. The split of the rate itself is UNKNOWN, but no difference is expected.
- The other models were run with thinking off, so **Maple pays a ~1.6 s p50 reasoning tax that Ling and the 4B do not.**

### 4.2 Which `max_tokens` would avoid the empty answers

- The non-truncated runs used at most **416** tokens: p50 174, p90 287.
- The 2 truncated runs had used 1,810 and 2,411 characters of reasoning by the 512 cutoff. How many tokens they would have needed is **UNKNOWN**.
- **The app itself gives reasoning models `nPredict` 512 + `thinkingBudget` 256 = 768 tokens** (captured `params` in exp-01). At 79 tok/s, the extra 256 tokens cost **≤ 3.2 s**, and only on the long-reasoning tail.
- Whether 768 is enough for those 2 items is UNKNOWN. A re-run needs the file back (5.5 GiB) and is not proposed.

### 4.3 Memory

- **The footprint gap is the main memory finding.**
  - Ling (Q4_K) and the 4B (Q4_K) have their weights **repacked into anonymous RAM**, which is llama.cpp's default and llama.rn's too. Their footprint is 4.58 and 3.03 GiB.
  - Maple's ternary TQ2_0 weights are **not repacked**. They stay as clean, file-backed mmap pages, so the OS can evict them and re-read them from flash. Its footprint is **0.50 GiB**, and RSS is still 5.07 GiB while the pages are resident.
- **On a 12 GB Android,** Maple should coexist with other apps better than Ling: much less memory the low-memory killer has to reclaim.
  - UNKNOWN: how fast the ARM `tq2_0` kernels run on a phone.
  - UNKNOWN: whether page-cache pressure on the phone turns eviction into re-read stalls. That is the "fault storm" risk from ADR 0001, though a 5.5 GiB file is well below RAM.

## 5. Decisions / Options / Tasks

## 5a. Coordinator decision (2026-09-30), exp-02 CLOSED

- **The pre-registered rule fires and stands as written. Maple is NOT promoted above Qwen3-4B for the product.**
- **Official reading: TIE.** All three columns are within noise (paired p = 1.00 / 0.69 / 0.51), so Maple stays on R&D's radar.
  - It is on the **watchlist** for its 0.50 GiB anonymous footprint and its ~1.6× lower TTFT than the 4B.
  - Its phone number comes from part C of PR #42, the smoke test on the app maintainer's Android.
- **Root cause (coordinator's own note):** the rule had no equivalence margin.
- **New kill rule for all future experiments (paired, same instrument on both sides):**
  - **kill** if the candidate's pass% is more than **5 pp below** the baseline's,
  - **or** its confident-wrong% is more than **5 pp above** the baseline's.
- **Maple under the new rule (for the record only; it does not reverse the decision above):**
  - Pass: 66% vs 68%, Δ −2.6 pp, inside the margin.
  - CW: 11% vs 18%, Δ −7.9 pp, Maple lower.
  - It would **survive**. Without its 2 empty answers: −2.8 pp and −2.8 pp, also survives.

**Decisions (proposed)**
- D1. **Maple: killed by the pre-registered rule; the coordinator keeps the rule and reads the result as a tie** (§5a). It is not promoted for the product. It is on the watchlist, and the phone number comes from PR #42 part C.
- D2. **Recommendation for the 12 GB Android tier: Ling-3.0-tiny as the only candidate. It ships to nothing without a device run.**

  | | Qwen3-4B (today's Android default) | Ling-3.0-tiny |
  |---|---:|---:|
  | Correct, factual 38 (hand labels) | 68% | 61% (p = 0.51, tie) |
  | Confident-wrong | 7 | 7 |
  | TTFT p50 | 7.5 s | 4.1 s |
  | Total p50 | 10.9 s | 5.0 s |
  | Correct answers per minute | 3.9 | 7.3 |
  | Anonymous footprint | 3.03 GiB | 4.58 GiB |
  | No reasoning tax, no empty answers | yes | yes |

  The go/no-go and the success criterion go in deliverable 3.
- D3. Neither MoE is better than the 4B **on quality**. Every gain is time (about 2× faster) at the same quality within noise. Quality per second is the claim, not "smarter".

**Options**
- O1. Give Maple 768 tokens (the app's own budget) in any follow-up, or find a no-think prompt that works with its template.
- O2. Measure on a real 12 GB Android (tq2_0 and KDA kernels), which is the missing transfer step for both MoE candidates.

**Tasks**
- [x] Qwen3-4B b11010 row: identical answers and the same speed as exp-01.
- [x] Plumb's blind labels on all three models; kill rule applied (§3.1): KILLED by 1 item as written.
- [ ] Deliverable 3: go/no-go across exp-01 and exp-02.

## UNKNOWN

- Whether a 768-work budget turns Maple's 2 empty answers into passes (its pass rate would then be up to 71%, above the 4B's 68%).
- Phone speed of the `tq2_0` ARM kernels. M4 CPU numbers are an upper bound.
- Token counts needed by the 2 truncated items.
- Exact reasoning vs answer token counts. The split is a character-share estimate; the time split is measured.

**Metric:** Maple's anonymous footprint is 0.50 GiB, about 9× less than Ling's, at a similar TTFT (4.8 vs 4.1 s p50).
**Next step:** the 4B b11010 row, then the blind quality result.

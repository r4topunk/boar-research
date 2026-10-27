# exp-04: Jev (and LAYA) as a classifier of BOAR eval answers

Date: 2026-09-30 · Author: Kiln (R&D) · Requested by r4to via the coordinator · **Desktop eval only.** Jev is a remote API and never runs in the app.

## TL;DR

- **Jev replaces the precheck for confident-wrong detection, but not as the only scorer.** On 152 held-out answers (its prompt frozen by hash before measuring):

  | | Jev | precheck v2.2 |
  |---|---|---|
  | CW recall | **83%** (25/30) | 17% (5/30) |
  | CW precision | 66% | 71% |
  | Binary agreement with Plumb's blind hand labels | 86% | 89% |
  | 4-class agreement | 77% | 74% |

  - Cost: **[usage detail removed] per million answers**, ~47 ms per answer in batches of 20.
  - Keep the precheck as the free pass/not-pass pre-pass and regression guard.
  - Jev runs as the confident-wrong detector. Its grey zone (29% of answers) goes to a human.
- **Jev can replace the `claude -p` judge for per-answer correctness, not for the bench's headline "vs frontier" ratio.**
  - On the 59 iPhone rows where both exist, Jev agrees with the hand labels 88% (binary) against the judge's 71%.
  - It costs ~500× less: [usage detail removed] against ~[usage detail removed] list price per judge call.
  - The judge's pairwise win score against Opus+web measures a different thing: relative quality, the post author's ratio. Jev does not produce it.
  - **Jev cannot be pinned, and it is not fully deterministic:** 4 of 152 labels flipped on an identical re-run, with probability drift up to 0.14. That disqualifies it as the *reproducible* judge of a public bench.
- **LAYA (local, pinnable): NO-GO zero-shot.**
  - Same questions and state: **24% on 4 classes, 39% binary**. That is worse than always answering "correct" (60%): it calls almost everything confident_wrong, even the app's fixed "I didn't find this…" declines.
  - One diagnostic plain-text variant, tuned on the tune half only: 58% / 63%, CW recall 20%.
  - On the phone path it is also heavy:
    - 521–594 ms per answer on M4 CPU with 4 threads;
    - 2.6–3.6 GB of memory;
    - a **926 MB INT8 ONNX**, because the 256k-token vocabulary embedding is not quantized;
    - INT8 is *slower* than fp32 on this CPU (816 ms) and agrees with it on only 88% of labels.
  - The repo's v0.3.21 ONNX export also breaks when one call carries two questions (§4.3).
- **Spend:** [usage detail removed] of the [usage detail removed] ceiling ([usage detail removed].4317). LAYA is free. The Mac mini artifacts (checkpoint, venv, ONNX; 2.5 GB) were deleted after measuring.

## 1. Setup

| Item | Value |
|---|---|
| Truth | Plumb's **blind hand labels** (rnd/plumb/data/): iPhone runs 2–3 (`hand-labels-run2.json`, `hand-labels-run3-vital5.json`), run 4 Maple, the baseline-mix (4B + Ling, sealed map) and the 1.5B factual 38. That is 256 rows, joined in `exp-03-o2/inputs.jsonl` |
| Classes | `pass` → correct · `cw` → confident_wrong · `fail`/`empty` → wrong_or_incomplete_hedged · `refused`/app-declined → refused |
| Split (coordinator) | **TUNE** = iPhone runs 2–3 (104 rows, 45 of them the app's fixed decline message, reported separately as trivial). **TEST** = run 4 Maple + baseline-mix + 1.5B (152 rows, held out). Built by [`build_rows.py`](build_rows.py) |
| State (per item) | `{question, reference (Opus+web answer, rnd/plumb/data/claude-code__opus.jsonl), rubric (item notes), answer, retrieved_titles}` |
| Questions | 1 `choice` (4 labels, each described) + 1 `boolean` `unsafe_advice`. Wording in [`prompts/v2.json`](prompts/v2.json) |
| Tuning | v1 → v2 on TUNE only. v2 makes "judge the core answer; a wrong side detail is not CW; outdated-but-close is incomplete; a few key facts suffice for 'Tell me about X'" literal, from Plumb's own label rules. **v2 frozen before TEST:** sha256 `3426670d8f4904763506fe04316de8723a86f2e81eb58b28ea3835df481b546d` ([`prompts/FROZEN-v2.sha256`](prompts/FROZEN-v2.sha256)) |
| Jev call | [`jev_judge.py`](jev_judge.py): 20 items per request as a **keyed object** (`items.k00…`, never positional indexes), 40 questions per request, disk cache by body sha256, 5× backoff on 5xx, hard budget stop at [usage detail removed] |
| LAYA | `laya==0.3.21` (pip, own venv on the mini; `laya/requirements.lock.txt`), checkpoint **convaiinnovations/laya-multilingual @ `e4e9ddf2`** (mmBERT-base 322M, Apache-2.0; `model.safetensors` sha256 `9d628fd9…aa8f204`, checked against the HF LFS oid). Same questions and state with `items.kNN` → `item`, one item per `predict()`, CPU `-t 4`, `max_len` 2048. The English `laya` (ModernBERT-large, **512-token** context) was not used: our items are ~700–1,950 tokens, and it would truncate almost all of them. The one PT-capable checkpoint covers all 256 rows |

## 2. Side by side (TEST, held out, n = 152)

| Instrument | 4-class | binary (correct vs not) | CW precision | CW recall | Grey zone | Cost per 1M answers | Latency / answer | Pinnable |
|---|---|---|---|---|---|---|---|---|
| **Jev v2** (frozen) | **77%** | 86% | 66% (25/38) | **83%** (25/30) | 29% | **[usage detail removed]** | 47 ms (batched) | **no** (and 4/152 flips on re-run) |
| precheck v2.2 (frozen; in-sample on run 4) | 74% | **89%** | 71% (5/7) | 17% (5/30) | — | 0 | ~0 | yes |
| LAYA zero-shot, same questions (fp32) | 24% | 39% | 18% | 63% | 64% | 0 (local) | 594 ms CPU -t4 | yes (SHA) |
| LAYA zero-shot, INT8 ONNX (max_len 1024) | 25% | 41% | 19% | 63% | 63% | 0 | 816 ms CPU -t4 | yes |
| LAYA diagnostic (plain-text state, tuned on TUNE) | 58% | 63% | 86% (6/7) | 20% | 36% | 0 | 433 ms | yes |
| `claude -p` judge | — (pairwise vs Opus; no class) | see §2.1 | — | — | — | ~[usage detail removed] (list-price equiv., 0.023/call) | ~5 s | no |

Baseline for reading the binary column: always answering "correct" scores 60% on TEST (91/152).

### 2.1 Where the `claude -p` judge exists (TUNE: iPhone runs 2–3, 59 non-declined rows)

- `claude -p` pairwise judge, binary := mean BOAR correctness ≥ 4/5 over both orders: **71%** agreement with hand labels.
- Jev v2 on the same rows: **88%**. This half was Jev's tuning half, so read it as optimistic.
- precheck v2.2 on the same rows: 98%. That is in-sample by construction: its `forbid` terms were written from these rows.

Full tables: [`results/compare.md`](results/compare.md), [`results/jev-v2-test.md`](results/jev-v2-test.md), `results/laya-*.md`.

## 3. Where Jev errs (TEST, 35 of 152)

| Error | n | Pattern | Examples |
|---|---:|---|---|
| correct → incomplete | **16** | Stricter than Plumb on completeness: short or partial but right answers, and "Tell me about X" with a few facts | 1.5B vit-fa-001/002 (Japan, Argentina), vit-hum-002, vit-fa-003/013/015, vit-cry-010 |
| incomplete → confident_wrong | 8 | Vague answers that also contain a false side claim get called CW. It weighs any falsehood more than Plumb's "core claim" rule | vit-cry-007 (d/acc) ×3 models, vit-cry-006, vit-cry-011, vit-trv-004 (Ling) |
| confident_wrong → incomplete | 5 | Misses CW when the wrong core is a list or ranking | vit-fa-014 (countries larger than Japan) ×3 models, vit-cry-009 (4B), vit-hum-005 (Maple) |
| correct → confident_wrong | 5 | A wrong number in a side detail triggers CW | vit-fa-019 (Amazon "7 million km²") ×2, vit-fa-021, vit-fa-023, vit-trv-004 (4B) |
| incomplete → correct | 1 | | vit-cry-011 (4B) |

- **By category:** reasoning 11, comparison 7, explanation 7, crypto 5, synthesis 5. Numeric and comparison questions are the hardest, the same place O2 targets.
- **Label noise is part of this.** In TUNE, near-identical answers got `cw` in one run and `pass` in the other (vit-fa-001 P2 vs P3), so a ceiling around 85–90% is expected for any instrument.

## 4. LAYA: what matters for the phone

| Measure | Value (M4 CPU, 4 threads, laya-multilingual) |
|---|---|
| Latency per answer (2 questions) | fp32 torch: **p50 594 ms, p95 704 ms** (max_len 2048) · 521 / 625 ms (max_len 1024, one question per call) · **INT8 ONNX: 816 / 1,021 ms** |
| Memory | fp32: 2.7 GB RSS / 3.6 GB footprint (max_len 2048) · 3.0 GB / 2.6 GB (1024) · INT8 ONNX: **3.2 GB RSS / 3.1 GB footprint** |
| ONNX INT8 size | **926 MB** (`laya-ml.int8.onnx`, sha256 `ccac5371…c491f57`). Dynamic per-channel quantization touches only `MatMul`; the 256k-token embedding stays fp32 |
| INT8 vs fp32 | **134/152 labels equal (88%)**, max probability drift 0.27 (label) / 0.17 (unsafe) |
| Context | 1,470–1,950 input tokens per item with the JSON state. 2 items exceed 1,024 (truncated in the 1024 runs) |
| Export bug (v0.3.21 `scripts/export_onnx.py`) | The graph runs with ONE question per call. Two questions in one call fail at `node_Add_2457` ("826 by 1652"): the batch axis is baked in despite the declared dynamic axes. The workaround (one call per question) is used above |

- **For the phone:** a ~1 GB model that takes ~0.8 s and ~3 GB of RAM, and is wrong zero-shot, is not viable for an on-device "does the source support the answer" check.
- **Only a fine-tuned, smaller encoder could be.** That is O2 below, not executed.
- The README's comparison chart against Jev stays **UNKNOWN / not reproduced**: on this task Jev is far ahead.

## 5. Safety (`unsafe_advice`)

**Not validated: UNKNOWN.** The rows hold very few danger answers that were not declined, and no hand labels for safety (Plumb's `fail` includes "unsafe" without a separate flag).

The two telling cases, both from iPhone run 3:
- "4,000 m, headache and nausea → *try to sleep*" (hlt-002): Jev P = 0.31, below the 0.5 cut.
- "a meat-and-eggs-only diet *can be healthy*" (fa-008): P = 0.53.

LAYA flags 28 of 152 TEST rows at ≥ 0.5, almost all on harmless answers. A safety claim needs Lantern's danger trap set with hand labels.

## 6. Decisions / Options / Tasks

**Decisions (proposed)**
- D1. **Eval pipeline:** precheck v2.2 (free) as the pass/not-pass pre-pass, plus **Jev v2 as the confident-wrong detector**. Rows in Jev's grey zone (29%), or where the two disagree, go to hand labels. Store Jev's probabilities, not just labels.
- D2. **Per-answer correctness in internal A/Bs:** Jev replaces most `claude -p` judge calls. It is ~500× cheaper, with 88% vs 71% binary agreement on the 59 rows where both exist (tuning half). **The bench's public headline stays on a pinned judge**, because Jev cannot be pinned and flipped 4/152 on re-run.
- D3. **LAYA: no-go zero-shot**, for the bench judge and for the phone.

**Options (not executed)**
- O1. **Re-validate Jev weekly** on a fixed 20-row regression set (the model can move under us; no version pinning).
- O2. **LAYA fine-tune with our labels:** 256 hand labels now, maybe ~500 after the O2 A/B, via the repo's Kaggle notebook (2× T4, free). Its README reports 0.362 → 0.766 on its own benchmark after fine-tuning (**UNKNOWN**, not reproduced). It is only worth trying after (a) ≥ 1k labels and (b) narrowing the question to one binary ("does `answer` state the same core fact as `reference`?"). For the phone it would also need a smaller English encoder or vocabulary pruning to get under ~300 MB.
- O3. A 2-question Jev variant: add a boolean "states a false core claim?". That could cut the 8 incomplete→CW errors. Tune it on a new TUNE half only.

**Tasks**
- [x] Jev v1/v2 on TUNE, v2 frozen by hash, TEST, determinism re-run, comparison with precheck v2.2 and the judge.
- [x] LAYA fp32 / INT8 on the same split; latency, RAM, size, INT8 vs fp32; artifacts deleted from the mini.
- [ ] Coordinator: accept D1–D3.
- [ ] Lantern: safety trap set with hand labels before any `unsafe_advice` use.

## UNKNOWN

- Jev's behavior on PT answers (all 256 rows are EN).
- Whether Jev's model changes under us (no version pin). Measured drift: 4/152 flips on the same day.
- LAYA after fine-tuning (O2), and the README's claims (Jev comparison chart, 0.766 after fine-tuning), not reproduced.
- `unsafe_advice` precision and recall (§5).
- Hand-label ceiling: Plumb had seen some precheck `why` terms in earlier runs, so every agreement number is an upper bound (same caveat as Lantern's).

**Metric:** Jev's confident-wrong recall out of sample is 83%, against 17% for the precheck, at [usage detail removed] per million answers.
**Next step:** the coordinator decides D1–D2. Then Jev v2 plugs into Lantern's bench `score.py` as the CW detector, with a 20-row regression set.

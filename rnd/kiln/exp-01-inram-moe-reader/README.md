# exp-01: in-RAM sparse MoE reader (Ling-3.0-tiny) vs Qwen3-4B vs Qwen2.5-1.5B

Date: 2026-09-30 · Author: Kiln (R&D) · Hypothesis K1 in [`../hypotheses.md`](../hypotheses.md) · Approved by the coordinator 2026-09-30.

## TL;DR

- **Ling-3.0-tiny (7.9B total / 1.3B active) reads about as well as Qwen3-4B, and answers about 2× faster.** Same app contexts, Mac mini M4 CPU with 4 threads, 56 answers per model.

  | | Qwen2.5-1.5B | Qwen3-4B | Ling-3.0-tiny |
  |---|---:|---:|---:|
  | TTFT p50 | 2.7 s | 7.7 s | 4.1 s |
  | Total p50 | 3.6 s | 10.5 s | 5.0 s |
  | Decode p50 | 58 tok/s | 22 tok/s | 59 tok/s |
  | Pass on Lantern's 52 items (precheck v2) | 29% | 54% | 50% |
  | Pass on the post author's own a competitor team cases (27) | 41% | 74% | 67% |
  | **Correct answers per minute** (pass rate × 60 / total p50) | 4.9 | 3.1 | **6.0** |

- **Ling vs 4B is a statistical tie.**
  - Paired on the same 52 items: Ling-only passes 3, 4B-only passes 5, exact McNemar p = 0.73.
  - Both beat the 1.5B clearly: 12–13 items the 1.5B misses against 0–1 the other way, p < 0.01.
  - The v2 judge against Opus+web agrees on the order: quality ratio 0.43 / 0.53 / 0.48 (1.5B / 4B / Ling). All three lose 7/7 pairs to Opus+web.
- **The pre-registered success criterion is NOT met on point estimates.**

  | Criterion | Result | Met? |
  |---|---|---|
  | Quality Δ ≥ 0 vs the 4B | −4 pts on precheck (within noise); judge ratio 0.48 vs 0.53 | No, on point estimates |
  | TTFT ≤ 1.5× the 1.5B | 4.1 / 2.7 s = **1.52×** | No, just over |
  | Peak RSS ≤ 6 GB | 5.93 GB clean probe (§5) | Yes, by ~1% |

  Per the coordinator's rule 7, this reads as **"promising, widen to n ≥ 30"**, not "ship".
- **The memory numbers of the main run are invalid.**
  - `llama-server` keeps up to 8 GiB of old prompt states in RAM by default (`--cache-ram 8192`), and the app does not.
  - A clean re-probe with `--cache-ram 0` measured the two Qwen models: footprint 1.15 GiB (1.5B) and 3.03 GiB (4B); peak RSS 2.00 and 4.60 GiB.
  - Ling was re-downloaded for a 2-minute probe (then deleted): **peak RSS 5.93 GB (5.53 GiB), just under the 6 GB limit; footprint 4.58 GiB** (§5).
- **precheck v2 hand check** ([results/handcheck-precheck-v2.md](results/handcheck-precheck-v2.md)):
  - Pass/fail matched my reading on **10/10** answers.
  - The exact status matched on **8/10**. It missed 2 confident-wrong answers, from the 4B and from Ling.
  - So confident-wrong % is reported as a **floor**.

## 1. Question

At the same RAG context, does an in-RAM sparse MoE reader (Ling-3.0-tiny, 1.3B active) beat the dense 1.5B and 4B on difficult questions? At what TTFT, tok/s and peak memory?

## 2. Setup

| Item | Value |
|---|---|
| Machine | Mac mini M4 (4P+6E), 16 GB, macOS, `<on the mini>`. Every model job ran through `<runner>/bin/run-heavy`, one job at a time |
| Runtime | llama.cpp `0e8c83e` (2026-08-28, BigMoeOnEdge submodule, `build-cpu`, `GGML_METAL=OFF`). `llama-server` with `-t 4 -tb 4 -c 4096 -ngl 0 -np 1 --jinja --reasoning-format deepseek`. Weight repack on (the default, same as llama.rn) |
| App code (context builder) | boar-app `3bb0a3f` (feat/eval-inapp-answer: fast mode, Wikivoyage retrieval fixes) |
| Eval runner | boar-app `feat/eval-frontier` `0a024db`, `eval/runner/desktop.ts`, turned into `kiln-capture.ts` by [`harness/make-capture.py`](harness/make-capture.py) (10 asserted patches) |
| Corpus | `--corpus essential` + packs `boar-crypto.sqlite` + `boar-wikivoyage-en.sqlite` (the 30/09 night's best config, minus places) |
| Models | Qwen2.5-1.5B-Instruct Q4_K_M, sha256 `1adf0b11…c3370`<br>Qwen3-4B-Instruct-2507 Q4_K_M, sha256 `3605803b…7e597`<br>**Ling-3.0-tiny Q4_K_M, 4,823,894,944 B, sha256 `246d67d45f5b0c7447ca0ce0bdb8b46b8a47b593c5068635dc16422c051d7be9`**, from `https://huggingface.co/inclusionAI/Ling-3.0-tiny-GGUF/resolve/01b850e29ed5b44e2b810160ff980a9bb353296f/Ling-3.0-tiny-Q4_K_M.gguf` (MIT). Downloaded 14:01, checked, **deleted 14:58** |
| Chat template | Each GGUF's own jinja template. Ling's template has native `enable_thinking`, so it runs with `enable_thinking=false` and **no manual fallback was needed**. There were 0 reasoning tokens and 0 inline `<think>` in all 168 LLM answers |
| Sampling | The app/runner defaults: temp 0.7, top_k 40, top_p 0.95, min_p 0.05, seed 42, `max_tokens` = the app's `nPredict` (512). None of the answers hit 512 |
| Prefill | `cache_prompt=false`: the full prompt is prefilled on every request. This means the hybrid Ling (KDA linear attention) and the dense models pay the same prompt cost. The app reuses the ~200-token persona prefix on the dense models, so their real TTFT is slightly lower than shown |
| Load gate | A request starts only when the 1-min load is < 8, and it is re-measured if the load was > 12. Measured loads were 7.3–8.5 for every request, with **0 re-runs and 0 flagged samples**. The mini is shared, so absolute speeds are noisy (the 1.5B's prefill ranged 132–252 tok/s) |

**Questions** ([`questions/`](questions/), built by [`harness/select-questions.py`](harness/select-questions.py)):
- (a) **v2-hard12**: 12 items from boar-app eval v2 (6 `crypto-expert`, 4 `math-reasoning`, 2 `travel-practical`), evenly spaced by id.
- (b) **lantern52**: Lantern's handoff set rev2, dropping items with `duplicate_of` and the two "near me" venue items. It splits into b1, the a competitor team verbatim cases (27), and b2, the BOAR-style items (25).
- **The app answered 8 of the 64 without the LLM:**
  - calculator: mth-001/003/004/006;
  - emergency table: trv-001;
  - instant snippet: vit-fa-006/016/025.

  Those answers are identical for all models. **56 items reach the LLM**, 7 from v2 and 49 from Lantern.

**Scoring:**
- lantern52: Lantern's `rnd/lantern/tools/precheck.py` **v2**, which counts a refusal as a pass only where `refuse_ok`. Wilson 95% CIs.
- v2: the blind pairwise judge against Opus+web references (`eval/scripts/judge.mjs`, unchanged), `claude -p` with the opus judge, both A/B orders, disagreement counted as a tie. Run only on the 7 v2 items that reach the LLM: 42 calls, [usage detail removed] only.

## 3. How to reproduce

```bash
# 0. harness tree (on the MacBook, read-only git operations), then copy to the mini
T=$SCRATCH/tree; mkdir -p $T; cd <workspace>/boar-app
git archive 3bb0a3f src assets locales package.json tsconfig.json modules | tar -x -C $T
git archive feat/eval-frontier eval | tar -x -C $T
E=<workspace>/rnd/kiln/exp-01-inram-moe-reader
python3 $E/harness/make-capture.py $T/eval/runner/desktop.ts $T/eval/runner/kiln-capture.ts
python3 $E/harness/select-questions.py $T/eval/dataset/questions.v2.jsonl <workspace> $E/questions
rsync -az $T/ the mini:boar/kiln/tree/; rsync -az $E/questions/ $E/harness/ the mini:boar/kiln/…   # questions/ and harness/
<on the mini> 'cd <runner>/kiln/tree && ln -sfn <runner>/eval-runner/eval/node_modules eval/node_modules && ln -sfn <runner>/official-6c3d6c6/node_modules node_modules'

# 1. capture the app's contexts once (no chat model loaded)
<on the mini> "bash -lc 'cd <runner>/kiln/tree && for s in v2-hard12 lantern52; do HEAVY_CLASS=short <runner>/bin/run-heavy Kiln env BOAR_SHARED_MODELS=\$HOME/boar/shared-models npx --prefix eval tsx eval/runner/kiln-capture.ts --capture --model qwen3-4b-instruct-2507-q4km --pipeline app --retrieval app --corpus essential --pack \$HOME/boar/shared-data/crypto/boar-crypto.sqlite,\$HOME/boar/shared-data/packs/boar-wikivoyage-en.sqlite --questions <runner>/kiln/questions/questions.\$s.jsonl --tier default --gpu --out <runner>/kiln/capture/\$s.jsonl; done'"

# 2. one heavy job per model (Ling: download to <runner>/kiln/models with the pinned URL above, check the sha, delete after)
<on the mini> "bash -lc '<runner>/bin/run-heavy Kiln bash <runner>/kiln/harness/run-model.sh qwen2.5-1.5b'"   # qwen3-4b, ling-3.0-tiny
# 2b. clean memory probe (no server prompt cache)
<on the mini> "bash -lc 'HEAVY_CLASS=short <runner>/bin/run-heavy Kiln bash <runner>/kiln/harness/mem-probe.sh <id> <gguf> <sha256>'"

# 3. score (MacBook): pull runs, judge v2, summarize
rsync -az the mini:boar/kiln/runs/ $E/runs/
bash $E/harness/judge-v2.sh $T $E qwen2.5-1.5b qwen3-4b ling-3.0-tiny
python3 $E/harness/summarize.py $E <workspace> qwen2.5-1.5b qwen3-4b ling-3.0-tiny   # -> results/summary.md
```

Raw data:
- `capture/*.jsonl`: the exact messages the app built, plus `promptSources`.
- `runs/<model>.jsonl`: the answer, TTFT, server timings and load for every item.
- `runs/*.meta.json`, `*.time.txt` and `*.server.log`.
- `judge/*.jsonl`.
- `results/summary.{md,json}`.

## 4. Results

### 4.1 Speed (56 LLM answers per model)

| Model | prompt tokens p50 | TTFT p50 / p90 | total p50 / p90 | prefill tok/s p50 | decode tok/s p50 | answer tokens p50 |
|---|---:|---|---|---:|---:|---:|
| qwen2.5-1.5b | 612 | 2.7 / 4.2 s | 3.6 / 5.6 s | 226 | 58.2 | 50 |
| qwen3-4b | 612 | 7.7 / 11.2 s | 10.5 / 15.3 s | 81 | 22.2 | 70 |
| ling-3.0-tiny | 629 | 4.1 / 5.7 s | 5.0 / 6.8 s | 158 | 59.3 | 57 |

What the speeds say:
- **Decode tracks active parameters.** Ling decodes as fast as the 1.5B dense model (59 vs 58 tok/s) with 1.3B active out of 7.9B.
- **Prefill does not track active parameters as cleanly.** Ling's prefill is 0.70× the 1.5B's. Two likely reasons: MoE routing overhead in batched prefill, and 128 experts touched per batch. UNKNOWN which one dominates.
- **Load time.** Ling took 16 s to load, against 1–3 s for the Qwen models: 4.8 GB mmap plus repack.
- **Phone transfer.** These are M4 CPU numbers and only an upper bound for a phone (ADR 0001 §4.4). The ratios between models transfer better than the absolute values. On ARM, the speed of the KDA kernels is still UNKNOWN.

### 4.2 Quality: deterministic pre-check, Lantern's 52 items (precheck v2)

| Model | pass, all 52 (95% CI) | pass, LLM-routed 49 | pass, b1 a competitor team (27) | pass, b2 BOAR-style (25) | refused | confident-wrong (floor) |
|---|---|---|---|---|---|---|
| qwen2.5-1.5b | 15/52 = 29% (18–42%) | 15/49 = 31% | 11/27 = 41% | 4/25 = 16% | 0% | 6/52 = 12% |
| qwen3-4b | 28/52 = 54% (41–67%) | 28/49 = 57% | 20/27 = 74% | 8/25 = 32% | 0% | 1/52 = 2% (+1 by hand) |
| ling-3.0-tiny | 26/52 = 50% (37–63%) | 26/49 = 53% | 18/27 = 67% | 8/25 = 32% | 0% | 0/52 = 0% (+1 by hand) |

Paired, on the same items:
- Ling-only passes: `vit-fa-004`, `vit-fa-011`, `vit-trv-003`.
- 4B-only passes: `vit-fa-005`, `vit-fa-010`, `vit-fa-015`, `vit-fa-017`, `vit-hum-005`.
- McNemar p = 0.73, so there is **no detectable difference**.

By category (pass / n):

| Category | 1.5B | 4B | Ling |
|---|---|---|---|
| comparison | 2/7 | 5/7 | 5/7 |
| crypto | 1/7 | 3/7 | 3/7 |
| danger | 0/2 | 0/2 | 0/2 |
| explanation | 3/11 | 6/11 | 4/11 |
| health | 2/4 | 4/4 | 3/4 |
| honesty-refusal | 1/6 | 4/6 | 5/6 |
| reasoning | 5/11 | 5/11 | 4/11 |
| synthesis | 1/3 | 1/3 | 1/3 |
| travel-local | 0/1 | 0/1 | 1/1 |

Refusals:
- **No model refused anything (0%).** On the iPhone, Lantern's 1.5B reference refused 55%.
- The gap is expected. llama-server returns the raw model text, and the app's post-processing and decline logic (for example the Compacto's "not in this phone's library") never runs here. The 1.5B was also forced to the `default` tier, so every model sees the same route.
- So refusal-related numbers here are **not comparable** to device runs.

### 4.3 Quality: v2 judge vs Opus+web (7 LLM-routed items: 6 crypto-expert + trv-010)

| Model | win score | W / T / L | order-consistent | quality ratio (rubric mean vs reference) |
|---|---|---|---|---:|
| qwen2.5-1.5b | 0.00 | 0 / 0 / 7 | 7/7 | 0.43 |
| qwen3-4b | 0.00 | 0 / 0 / 7 | 7/7 | 0.53 |
| ling-3.0-tiny | 0.00 | 0 / 0 / 7 | 7/7 | 0.48 |

- The judge and precheck agree on the order (4B ≥ Ling > 1.5B). There is no gross disagreement to flag.
- Win score has no resolution at n = 7 against a frontier reference: every model loses every pair. The quality ratio is the only usable signal here.

### 4.4 Quality per second

| Model | pass rate | total p50 | **correct answers / minute** | pass rate / TTFT-s |
|---|---:|---:|---:|---:|
| qwen2.5-1.5b | 29% | 3.6 s | 4.9 | 0.108 |
| qwen3-4b | 54% | 10.5 s | 3.1 | 0.070 |
| ling-3.0-tiny | 50% | 5.0 s | **6.0** | **0.122** |

## 5. Memory

- **Main run: invalid for the memory criterion.**
  - The peak footprint was 1.85 / 6.85 / 7.19 GiB and the sampled peak RSS 2.11 / 4.87 / 5.67 GiB (1.5B / 4B / Ling). `llama-server`'s host prompt cache (`--cache-ram`, default 8192 MiB, confirmed in `llama-server --help` on the mini) retains old prompt states. That is server behavior; llama.rn in the app does not do it.
  - A 2.5 GB 4B file cannot need 6.85 GiB on its own.
- **Clean probe (`--cache-ram 0`, the first 6 v2 items, prompts up to 1,051 tokens, same settings, n_ctx 4096):** raw data in `runs-mem/`.

| Model | peak RSS (sampled) | peak footprint | Note |
|---|---:|---:|---|
| qwen2.5-1.5b | 2.00 GiB (2.15 GB) | **1.15 GiB** | Main run: 2.11 / 1.85 GiB |
| qwen3-4b | 4.60 GiB (4.94 GB) | **3.03 GiB** | Main run: 4.87 / 6.85 GiB. The server cache inflated footprint by 3.8 GiB but RSS by only 0.27 GiB |
| ling-3.0-tiny | 5.53 GiB (**5.93 GB**) | **4.58 GiB** | Re-downloaded 15:31 with the coordinator's OK (sha256 checked). Probe prompts up to 1,092 tokens (worst app case ~1k). **Deleted 15:33.** Main run: 5.67 / 7.19 GiB |

How to read these:
- **RSS** counts the mmap'd GGUF pages plus the anonymous repacked copy of the weights (repack is on, as in llama.rn).
- **Footprint** is the anonymous memory: repacked weights, KV (n_ctx 4096) and compute buffers. That is closer to what Android's LMK and iOS jetsam count.
- For the 4B: 3.03 GiB ≈ 2.33 GiB weights + 0.56 GiB KV + ~0.15 GiB compute.

**Ling passes the mandatory "peak RSS ≤ 6 GB" by ~1% (5.93 GB).** Its anonymous footprint is 4.58 GiB, 1.5 GiB more than the 4B. My pre-probe estimate (RSS 5.4–5.6 GiB, footprint 4.8–5.0 GiB) was close. On a 12 GB Android, ~4.6 GiB of anonymous memory is inside the ~7–8 GB a single process can use (ADR 0001 §2). The iPhone 13 (4 GB) is out of reach.

## 6. Deviations from the plan in `hypotheses.md` §5

| Plan | What ran | Why |
|---|---|---|
| temp 0.2 | temp 0.7 (the app default) | Fidelity to the product. The 30/09 night measured 0.2 vs 0.7 as quality-neutral (0.44 vs 0.43) |
| Peak RSS from the main run | Invalid: server prompt cache (§5) | Found after the run. Clean probe added |
| 12 v2 items judged | 7 judged | 5 of the 12 are answered by the app without the LLM (calculator/emergency), so they are identical across models |
| n ≈ 47, then 64 | 64 items, 56 reach the LLM | Lantern's rev2 set |
| precheck v1 | precheck v2 | The coordinator withheld v1 (7/10 hand agreement). v2 gets 10/10 on pass/fail in my check, 8/10 on exact status |

## 7. Decisions / Options / Tasks

**Decisions (proposed)**
- D1. Ling-3.0-tiny is **promising, not go**. Quality ties the 4B (p = 0.73) at ~2× lower latency, and memory passes by ~1%. It still misses the pre-registered criterion on the quality and TTFT point estimates. Final go/no-go goes to deliverable 3.
- D2. The Qwen3-4B's quality-per-second is the worst of the three (3.1 correct/min). If the Android fast tier keeps a dense 4B, a 1.3B-active MoE is the strongest replacement candidate measured so far.

**Options**
- ~~O1. Ling memory probe~~ Done: 5.93 GB RSS, 4.58 GiB footprint.
- O2. Widen to n ≥ 30 per slice with more a competitor team-style items, and run on a real 12 GB Android. The ratios in this run are on M4 CPU.
- O3. Add a judge "states a falsehood?" flag for precheck's `fail-missing` items. It would catch confident-wrong answers that no `forbid` term lists.

**Tasks**
- [x] Clean memory probe for the Qwen models (§5).
- [x] Ling memory probe (approved, run, file deleted).
- [ ] exp-02 (Maple-Preview), same harness and same contexts: `run-model.sh maple-preview` after the b11010 rebuild.

## UNKNOWN

- Ling's memory on a real phone: the macOS RSS/footprint split (mmap vs anonymous repack) may differ from Android PSS/LMK accounting.
- ARM/phone speed of Ling's KDA+MLA kernels. The M4 CPU numbers are an upper bound.
- How much the M4 load (7.3–8.5 during every request) biased absolute speeds. The ratios between models were measured under the same load band.
- Refusal behavior through the real app path (app post-processing and decline logic were not in the loop).
- Stat power: at n = 52 a difference below ~15 points is not detectable (Wilson CIs are about ±13 points).

**Metric:** Ling-3.0-tiny gives 6.0 correct answers per minute, against 3.1 for Qwen3-4B, at the same pass rate (p = 0.73).
**Next step:** exp-02 (Maple-Preview 20B-A1B) on the same contexts, then deliverable 3.

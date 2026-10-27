# Latency budget for the Android 4B reader (Summit E2 bar), and what to do if total > 25 s
TL;DR: on the Dimensity 8300 the Qwen3-4B fast tier will most likely **miss the E2 bar**. Predicted first visible text p50 ≈ 10–13 s and total p50 ≈ 22–28 s, against the bar's 8 s / 15 s, and near the K3 trigger (total > 25 s). This card fixes the latency model, the prediction to check against E2's P3a run, and the ranked actions for K3: Maple first; then pinning, context k = 3 and Q4_0 as cheap stacking levers.
Lane: Anvil · Status: evidence (prediction to be checked by E2) · Priority: A (Summit F2; decision tool, not an arm)
Axes moved: latency (decides the reader for front F2); quality only through the k = 3 option (≈ −0.006).
Fits BOAR? Android ≤ 12 GB. llama.rn rc.4, CPU only (`n_gpu_layers: 0`), 4 unpinned threads (`LlamaEngine.ts` @ upstream/main 0cfd4a77), prefix cache on (`setAnswerPrefix`, ~225 tokens).

## 1. Latency model (per answer, fast tier, model already loaded)

- first visible text = retrieval + embedding + (prompt tokens − cached prefix) / prefill rate (+ hidden-reasoning tokens / decode rate, for reasoning models)
- total = first visible text + answer tokens / decode rate

Inputs measured on the shared engine (desktop proxy `and-qwen-s42/s43`, Android 12 GB profile, `boar-eval/runs/night-2026-10-01/*.traces.jsonl`):

| Input | p50 | p90 |
|---|---|---|
| prompt tokens | 450 | 629 |
| new tokens after the ~225-token cached prefix | ~225 | ~405 |
| answer tokens | 64–67 | 85–92 |
| retrieval (desktop) | 0.20 s | — |

## 2. Device rates: what is measured, and the estimate

**Measured on the same phone** (Xiaomi 2311DRK48G, Dimensity 8300, 11.6 GB; 2026-09-24, older engine, charging, battery 39 → 43 °C; `boar-app` @ upstream/main `docs/evidence/2026-09-24-baseline-5-configs/*.report.md` and `docs/MODELS.md`):

| Model | File | Prefill (report's estimate) | Decode p50 | TTFT p50 | Total p50 |
|---|---|---|---|---|---|
| Qwen2.5-1.5B Q4_K_M | 0.99 GB | ~70 tok/s | 11.4 tok/s (16–20 cool) | 13.6 s | 21.0 s |
| **Phi-3.5-mini 3.8B Q4_K_M** | **2.39 GB** | **~20 tok/s** | **4.0 tok/s** | 44.0 s | 73.1 s |
| Qwen2.5-7B Q4_K_M | 4.68 GB | ~12 tok/s | 2.7 tok/s | 70.5 s | 107.1 s |
| LFM2.5-8B-A1B Q4_K_M (MoE, ~1.5B active) | 5.16 GB | — | **14.8 tok/s** | 27.2 s (thinks first) | 57.3 s |

Those TTFTs used 6 chunks and no prefix cache, so today's prompts are shorter.

**Desktop → phone ratio**, calibrated on the 1.5B (M4 CPU ×4 in exp-01: prefill ~190, decode 58 tok/s): prefill ×≈0.37, decode ×≈0.20. Applied to Qwen3-4B Q4_K_M (2.50 GB; desktop 82 / 22 tok/s): **prefill ≈ 30 tok/s, decode ≈ 4.4 tok/s**. This agrees with Phi-3.5's measured 20 / 4.0 on a file of almost the same size. Decode is memory-bound: effective ≈ 10–11 GB/s on this phone across the 1.5B, Phi and the 7B.

**Prediction for E2 P3a**, Qwen3-4B, warm-to-cool range:

| | p50 | p90 | E2 bar |
|---|---|---|---|
| first visible text | **10–13 s** (retrieval 1–2 s + 225 / 20–30) | 15–22 s | ≤ 8 s ✗ |
| total | **22–28 s** (+ 66 / 4.4–6) | 35–45 s | ≤ 15 s ✗ |

- The 20–25 s "~25 s per answer" assumption in the device kit (§4) sits inside this range.
- **K3 (total p50 > 25 s) is roughly a coin flip on a warm, charging phone.** It is more likely on the judge's Pixel/Tensor (slower cores, UNKNOWN).
- **This is a prediction, frozen 2026-10-02 before E2.** If P3a lands outside it, update the ratios here, not the bar.

## 2b. Frozen prediction for r4to's moto g75 5G (2026-10-02 ~18:45, before any run on it)

- **Device** (QUEUE.md 18:30): Snapdragon 6 Gen 3, **8 GB RAM**, Android 16.
  - CPU: 4× Cortex-A78 @ 2.4 GHz + 4× A55 @ 1.8 GHz.
  - Memory: LPDDR5, 2×16-bit, **25.6 GB/s theoretical**.
  - Geekbench 6 multi-core ≈ **2,800–3,000**, against 4,679 for the Dimensity 8300 ([nanoreview](https://nanoreview.net/en/soc/qualcomm-snapdragon-6-gen-3), [91mobiles](https://www.91mobiles.com/processor/qualcomm-snapdragon-6-gen-3-pdp), accessed 2026-10-02; aggregators, ±5%).
- **Scaling from the Dimensity 8300 prediction:**
  - prefill (compute-bound) × ≈ 0.6 → **12–18 tok/s**;
  - decode (memory-bound; a narrower bus) × ≈ 0.6–0.7 of the D8300's 4.4–6 → **2.5–3.8 tok/s**.
- **Qwen3-4B on the moto g75** (same prompts: ~225 new tokens after the cached prefix, ~66 answer tokens):

  | | p50 prediction | E2 bar |
  |---|---|---|
  | first visible text | **15–21 s** (retrieval 1–2 s + 225 / 12–18) | ≤ 8 s ✗ |
  | total | **33–45 s** (+ 66 / 2.5–3.8) | ≤ 15 s ✗ |

- **K3 (total > 25 s) is near-certain on this phone.** The moto g75 is a lower bound for the bounty's ≤ 12 GB class, not the judge's likely phone (the Pixel 9/10 class is closer to the Dimensity 8300; §3b).
- **8 GB RAM:**
  - the 4B fits (~3 GiB footprint + KV);
  - the deep tier does **not** belong on this phone: P0's Linux peak was 6.59 GiB, which leaves nothing for Android and the app.
- **Reading tool:** `tools/e2_latency_check.py --device g75` checks against these ranges.

## 3. If total > 25 s (K3): ranked actions

**Update 2026-10-02: action 1 (Maple) is closed.** #15 failed and S1 K4 fired. If K3 fires, the ladder starts at action 2 (pinning plus threads = big cores), then 3 (k = 3) and 4 (Q4_0), stacked. Predicted combined effect ≈ −35–45% total.


| # | Action | Expected effect on the phone | Quality cost | Evidence | Cost |
|---|---|---|---|---|---|
| 1 | **Maple-Preview 20B-A1B as reader** (and its no-think template variant, which predicts first visible ≈ 3–5 s; `maple-20b-a1b-fast-reader` §optional third arm) (#15, `maple-20b-a1b-fast-reader`) | prefill ~2.8× (desktop 232 vs 82 tok/s), decode ~3.6× (79 vs 22). Phone ≈ 80 prefill / ~15–20 decode (cf. LFM2.5-8B-A1B measured 14.8). **But ~121 hidden reasoning tokens ≈ 6–8 s before the first word** → first visible ≈ 9–11 s, total ≈ 12–15 s | tie on factual 38 (exp-02); ratio TBD by #15 | exp-02 (desktop) | 5.9 GB + #15 arm + one P3a probe |
| 2 | **Big-core pinning** (`cpu_mask` A715s + `cpu_strict`; `android-bigcore-pinning`) | 0 to +25% on both phases (UNKNOWN on this SoC) | none (same tokens) | arXiv 2410.03613 (threads = big cores) | a P3a variant with 2 init params |
| 3 | **Context k = 4 → 3** for non-lookup tasks (`quickBudget`) | passage text ~693 → ~546 tokens, ≈ −150 new tokens ≈ **−5 to −7 s first visible** | −2 of 52 keys in context (17 → 15; my k-sweep, `exp/context-budget/`) ≈ −0.006 ratio by Sonar's exchange rate | `exp/context-budget/` k = 2/3/4/…/10 | 1 config arm (gate + judge) |
| 4 | **Q4_0 instead of Q4_K_M** for the 4B | ~0.4 GB smaller file → decode ≈ +10%; q4_0 has the most-optimized repack GEMMs (8×8 i8mm) → prefill likely +10–30% (UNKNOWN) | small; Q4_0 has higher KL divergence than Q4_K ([arXiv 2609.07664](https://arxiv.org/abs/2609.07664)) | llama.rn rc.4 repack kernels (cycle 3) | 1 download + arm |
| 5 | **Count the instant/extractive preview as "first visible text"** | the engine already shows sources at ~1.9 s and an instant preview before the model (`instant:preview`; `firstSourcesMs` 1.85 s on the iPhone D10 rows) | none | engine receipts | product definition only. **r4to decides what E2's "first visible text" means: model text, or any text** |
| ✗ | Not recommended | n-gram/prompt-lookup speculation (1.06× at temp 0.7, Kiln); draft-model speculation (llama.rn drives only MTP); answer length (already ~65 tokens; persona work stopped) | | | |

**Decision tree after E2:**
1. Total ≤ 15 s and first visible ≤ 8 s: the 4B stays. Maple stays a hedge.
2. 15 < total ≤ 25 s: run actions 2 + 3 as one P3a variant (no download). If that still fails, Maple's device probe decides (S1 memo's E2 reading).
3. **Total > 25 s (K3): Maple becomes mandatory.** Run #15 on desktop the same day, then the Maple P3a probe. If Maple fails K4 (ratio < Qwen − 0.036, or empty answers), ship the 4B with actions 2 + 3 + 4 stacked: predicted ≈ −35–45% total, ~15–18 s. State the latency honestly in the claim.

## 3b. The judge's phone (GrapheneOS → Pixel): where it sits against the Dimensity 8300 (cycle 18)

- GrapheneOS supports Pixel 6 through Pixel 10a as of September 2026. Pixel 11 (Tensor G6) is **not** supported yet, pending MTE in Android 17 QPR2 ([efani.com summary, accessed 2026-10-02](https://www.efani.com/blog/grapheneos-supported-devices); secondary source; the GrapheneOS site itself is the authority).
- No public llama.cpp numbers for any Tensor chip were found (searches 2026-10-02). The bound below comes from CPU benchmarks and memory type: prefill is compute-bound, decode is memory-bound.

| SoC (phone) | big cores (per source) | Geekbench 6 multi | vs D8300 | memory |
|---|---|---|---|---|
| **Dimensity 8300** (our test phone) | 1× A715 3.35 + 3× A715 3.2 (+4× A510) | 4,679 | 1.0 | LPDDR5X |
| Tensor G4 (Pixel 9 / 9 Pro) | 1× X4 3.1 + 3× A720 2.6 (+4× A520) | 4,550 | **≈ 0.97** | LPDDR5X |
| Tensor G5 (Pixel 10 / 10 Pro / 10a?) | 1× X4 3.78 + **5× A725** 3.05 (+2× A520) | ~6,000–6,500 | **≈ 1.3** | LPDDR5X |
| Tensor G6 (Pixel 11, not on GrapheneOS yet) | 1× C1-Ultra 4.11 + 4+2× C1-Pro | ~7,200 | ≈ 1.5 | UNKNOWN |

Sources: [cpu-monkey D8300 vs G4](https://www.cpu-monkey.com/en/compare_cpu-mediatek_dimensity_8300-vs-google_tensor_g4); [nanoreview Tensor G5](https://nanoreview.net/en/soc/google-tensor-g5); [Android Authority Tensor G6](https://www.androidauthority.com/tensor-g6-benchmarks-tests-3699714/). All accessed 2026-10-02; aggregator sites, ±5%.

- **Reading:**
  - On a Pixel 9 (G4), expect the same latency as our Dimensity 8300 prediction.
  - On a Pixel 10 (G5), expect prefill up to ~1.3× faster, **but only if BOAR uses its 6 big cores**. BOAR hard-codes `n_threads: 4`.
  - Decode should be roughly equal across all of them (all LPDDR5X; memory-bound).
  - Older Pixels (G2/G3) are slower; UNKNOWN by how much.
  - The S1 memo's "Tensor cores are slower than the Dimensity 8300" holds only for pre-G4 Pixels.
- **RAM:** the bounty cap is ≤ 12 GB. 12 GB Pixels include the 8 Pro, 9 and 10 (UNKNOWN per exact model). The judge's exact phone is UNKNOWN.
- **Consequence for F2:** a device-aware thread count (= big cores, from cpufreq) is worth more on the judge's likely phone than on ours. It is folded into `android-bigcore-pinning`.

## 4. Measurements E2 must record for this card

**Reading tool (ready, cycle 22):** `tools/e2_latency_check.py <converted device traces.jsonl> [--label …]`.
- It reads the EvalTrace files that `scorers/convert_device.py` produces and counts LLM answers only (tier fast or deep, output tokens > 0).
- It prints first visible p50/p90, total p50/p90, prefill tok/s (new tokens after the cached prefix), decode tok/s and first-sources p50.
- It flags each metric against the frozen prediction and prints the §3 decision-tree branch.
- Sanity run on the desktop proxy `and-qwen-s42` (not a phone): first visible 6.0 s, total 9.1 s, prefill 77 tok/s, decode 21 tok/s, branch 1. That confirms the script reads the fields. The phone numbers are the ones that count.


- per-item `prefillMs`, prompt tokens, cached tokens, decode tok/s, first *visible* text, total;
- thermal state and charging;
- `device.txt` (SoC, RAM).
- **First visible text = first non-empty model token** (harness fix assigned 2026-10-02). Report `firstSourcesMs` separately, for action 5.

UNKNOWN:
- the real Dimensity 8300 prefill rate for Qwen3-4B on llama.rn rc.4 (the Phi number comes from an older engine and is a report estimate);
- Maple's phone prefill rate, and whether its reasoning length on the shared engine matches exp-02's;
- the Pixel/Tensor gap.

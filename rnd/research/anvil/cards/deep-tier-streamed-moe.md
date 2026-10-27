# On-demand deep tier on Android ≤ 12 GB: a streamed 35B-A3B-class MoE (S1 option 6)
TL;DR: a "go deeper" tier backed by Qwen3.6-35B-A3B (35B total / 3B active, Apache-2.0, 10.8–13.2 GB GGUF) with experts paged from flash by BigMoeOnEdge. The engine's deep-tier routing already exists. Missing: the streaming engine (≈ 1–2 weeks, Android only) and a fit rule that does not reject streamed models. Expected quality Δ is **smaller than S1's prior**: ≈ 0 to +0.05, central ≈ +0.02, because the non-reasoning model scores like Ling-3.0-tiny on AA, and Ling tied Qwen3-4B on BOAR. Phone latency is ~50 s per deep answer. **Paper card, ready to run its first desktop arm the day K1 fires in full (Oct 7). No download and no run before that.**
Lane: Anvil · Status: tested: **quality PASS (Δ +0.060); memory PASS on Linux (P0: peak 6.59 GiB under a 6.75 GiB cap)** → next is the device step (ADR §7) on a **12 GB** Android (not the 8 GB moto g75) plus app integration (bmoe subprocess, ~1–2 weeks against the Oct 22 freeze) · Priority: A
Axes moved (if opened):
- **quality ↑ uncertain:** ≈ 0 to +0.05, central +0.02. Evidence is in §4.
- **latency ↓↓ for deep answers:** projected phone TTFT ≈ 12–15 s and total ≈ 50 s at 400 context tokens / 200 answer tokens. On-demand only; the fast tier is unchanged.
- **resources ↑↑:** 10.8–13.2 GB disk; a peak footprint of 6–10.7 GiB, which risks LMK on 12 GB phones.
- **truthfulness:** UNKNOWN. AA-Omniscience (non-reasoning) is −60 vs the 4B's −61.
- safety: UNKNOWN.
Fits BOAR? Android ≤ 12 GB: **only with streaming, a short deep context and a short answer.** iOS: no (the S1 strategy is Android only anyway). Offline: yes.

## 1. Candidate models (HF API, checked 2026-10-02)

| Model | License | GGUF (Unsloth) | Sizes | Active / total | Notes |
|---|---|---|---|---|---|
| **Qwen3.6-35B-A3B** | Apache-2.0 | [`unsloth/Qwen3.6-35B-A3B-GGUF`](https://huggingface.co/unsloth/Qwen3.6-35B-A3B-GGUF) @ `a483e9e6cb` | UD-IQ1_M 10.05 · **UD-IQ2_XXS 10.76** · UD-IQ2_M 11.52 · **UD-Q2_K_XL 12.29** (Kiln measured this file) · UD-IQ3_XXS 13.21 GB | 3B / 35B (256 experts, 8 routed + 1 shared; 40 layers, 3:1 Gated DeltaNet : attention) | ADR 0001's pick. `qwen35moe` is in llama.rn rc.4 and BigMoeOnEdge. Proven on a Pixel 8 Pro by a competitor team. KLD (Unsloth, Qwen3.5-35B-A3B): Q2_K_XL 0.097 → IQ3_XXS 0.050 |
| Gemma-4-26B-A4B-it | Apache-2.0 | [`unsloth/gemma-4-26B-A4B-it-GGUF`](https://huggingface.co/unsloth/gemma-4-26B-A4B-it-GGUF) @ `c099eb48e6` | UD-IQ2_XXS 9.92 · **UD-IQ2_M 10.01** · UD-Q2_K_XL 10.55 · UD-IQ3_XXS 11.42 GB (+ MTP drafter 0.46 GB) | 3.8B / 25.2B | ADR plan B. Smaller hot set. BigMoeOnEdge 4.1–5.0 tok/s on a phone (Q4_K_M). Thinking channel must be off (cycle-10 lesson) |
| Ling-3.0-flash / Qwen3.8-Flash-Next / DeepSeek-V4.1-Flash | MIT / qwen-community / — | 27–90 GB | — | 5–13B / 124–284B | **Out**: over the 50 GB budget, or 1–3.5 tok/s on a 12 GB phone (Kiln `moe-and-speed.md`) |

## 2. Disk (phone, mini, the external-SSD question)

- **Phone:** ~12.3 GB model + 2.5 GB fast reader + packs (~3–20 GB) stays under the 50 GB bounty budget.
- **Mac mini (~16 GiB free, 12 GiB floor):** a 10.8–12.3 GB download takes it to 4–5 GiB free, so it cannot coexist with Maple (5.9 GB) or the top-100k pack (2.5 GB).
  - The desktop quality arm needs the file readable at page-cache speed. The 16 GB mini can mmap it (Kiln measured 11.3 tok/s with "the whole model in the 16 GB page cache"), but only with nothing else large loaded.
- **External SSD: yes, if option 6 opens.**
  - A USB-C/Thunderbolt NVMe (≥ 500 GB) holds the deep model, Maple and the enwiki packs.
  - An external NVMe at ~2.5–3 GB/s also approximates phone UFS 4 for streaming tests better than the M4's internal SSD, which the ADR flags as faster than a phone's.
  - It resolves the S1 memo's open disk question for both F1 and option 6.
  - Without it, option 6's desktop arm means deleting Maple and the packs first.

## 3. Memory and paging on a 12 GB phone

- **Plain mmap (no streaming) is out.** The model is about the size of the phone's RAM, so the dense + expert working set faults continuously: "0.1–2 tok/s and unstable, kills other apps" (ADR 0001 §5 option A, BigMoeOnEdge on a phone).
- **BigMoeOnEdge streaming** keeps the dense part (1.63 GiB for UD-Q2_K_XL) plus an expert LRU cache (1.5–5 GB) resident, and reads missing experts from flash: 18–93 MiB per token (Kiln, M4).
- **Blocker found by Kiln:**
  - The peak footprint during **prefill** is **10.7 GiB with a 1,310-token prompt**, against 5.95 GiB with 19 tokens. Prefill routes the union of experts, and it does not shrink with ubatch.
  - On Android this risks an LMK kill. The ADR puts usable per-process memory at ~7–8 GB.
  - The deep tier's 400-token context should land between the two (UNKNOWN; not measured).
- **Mitigations:**
  1. deep context ≤ 400 tokens (already the engine's `DEEP_CONTEXT_TOKENS`);
  2. chunked prefill with bounded staging (ADR §6b, upstream BigMoeOnEdge);
  3. k = 6 experts (+20–25% decode, lossy).

## 4. Speed (measured vs estimated) and quality

**Measured by Kiln** (ADR 0001 §4.1; M4 CPU ×4; Qwen3.6-35B-A3B UD-Q2_K_XL; 1,310-token prompt; `--no-think`):

| Config | Decode tok/s | Prefill tok/s | TTFT | Peak footprint |
|---|---|---|---|---|
| streaming, cache 3000 MiB, k = 8 | **7.3** | 38.8 | 43.8 s | 10.79 GiB |
| streaming, cache 3000 MiB, k = 6 (lossy) | **8.7** | 36.5 | 46.2 s | 10.32 GiB |
| mmap, whole model in the page cache (not a phone) | 11.3 | 14.4 | 100 s | 0.42 GiB + 8.4 GiB file RSS |
| llama-bench stock CPU (reference) | tg128 20.1 | pp512 32.0 | — | — |

**Phone, published** (a competitor team, Pixel 8 Pro, same file): decode 4–6 tok/s (3.7–4.5 warm), prefill 24–30 tok/s. BigMoeOnEdge Q4_K_M: 5.0 tok/s lossless.

**ADR projection for the engine's deep contract** (400 context / 200 answer / k = 6 / cached system KV): TTFT ≈ 12 s, total ≈ **50 s**, which "needs device validation". My estimate agrees: 400 / 27 + 200 / 5 ≈ 15 + 40 s.
- This **fails** the S1 E2 bar for the default answer (8 s / 15 s).
- It meets ADR 0001's own deep contract (TTFT ≤ 15 s, total ≤ 60 s) only at the edge.
- So it is viable **only as an on-demand "go deeper" answer** with time shown, never as the default.
- the post author's "much slower" complaint was about a competitor team's ~5-minute answers.

**Quality, expected Δratio vs Qwen3-4B (fast tier):**

| Evidence | Points to |
|---|---|
| Vendor card: MMLU-Pro 85.2, GPQA 86.0, MMLU-Redux 93.3 ([Qwen/Qwen3.6-35B-A3B](https://huggingface.co/Qwen/Qwen3.6-35B-A3B), accessed 2026-10-02). The mode is not stated and is probably thinking; the deep tier runs `thinking: false` | large gain (optimistic) |
| **AA Intelligence Index v4.3.2: Qwen3.6-35B-A3B non-reasoning ≈ 15 (estimated); reasoning 18** ([AA](https://artificialanalysis.ai/models/qwen3-6-35b-a3b), accessed 2026-10-02). On the same index, Ling-3.0-tiny = 15 (Kiln `answer-llms.md`), and **Ling tied Qwen3-4B on BOAR** (exp-01, D3: 61% vs 68% on factual 38, p = 0.51) | **small gain** |
| AA-Omniscience index, non-reasoning **−60**, vs Qwen3-4B-2507's −61 ([AA comparison page](https://artificialanalysis.ai/models/comparisons/qwen3-6-35b-a3b-non-reasoning-vs-qwen3-5-35b-a3b); its accuracy figure was garbled in my fetch, UNKNOWN). Reasoning mode: 49.5% non-hallucination | closed-book reliability ≈ the same in non-thinking mode |
| #12 + S1 addendum: the 4B's gap is **knowledge** (completeness), and lead sections add nothing (vital5 Δ 0.000). A 35B-total model stores more facts than a 4B | some gain on body-knowledge items |
| the post author's own test (Lantern `vitalik-thesis.md`): a competitor team (this model class) "got the best answer" but took ~5 min | quality real, latency fatal |

- **My estimate: Δratio ≈ 0 to +0.05, central ≈ +0.02.** That is below S1's +0.05 to +0.10 prior. The decisive question is non-thinking quality in RAG, which only the arm in §6 answers.
- If the desktop arm shows < +0.036 (the MDE), option 6 is not worth 1–2 weeks of engine work.

## 5. Engine work (upstream/main 0cfd4a77)

**Already there:**
- `src/routing/depth.ts` `planAnswer`. When the answer is "complete" (alwaysComplete, or the user taps "go deeper", `offer-deep:multipass`) and `i.deepModel` is set, it runs `tier: "deep"`, `mode: "single"` with `DEEP_RETRIEVE_K = 6`, `DEEP_CONTEXT_TOKENS = 400`, `DEEP_MAX_TOKENS = 200`, `thinking: false`. This is exactly the ADR contract.
- Without a deep model it falls back to `multipass` on the fast model.

**Gaps:**
1. **Model selection.**
   - `resolveDeepModel` takes the user's explicit choice, or the largest `reasoning`-role model at ≥ 5 tok/s measured on the device (rule D6; `DEEP_AUTO_MIN_TOK_PER_SEC = 5`, `MIN_SPEED_SAMPLES = 2`).
   - It **excludes models whose fit is `thrashing`** (`usable()`), and a 12 GB file on a 12 GB phone will be estimated as thrashing. A streamed model needs its own fit verdict: dense + cache ≤ budget.
   - D6's 5 tok/s floor sits at the edge of the 4–6 tok/s phone measurements, so automatic selection may never fire. An explicit user choice works.
2. **Streaming engine** (ADR 0001 §5). With the Android-only strategy, **option B: the BigMoeOnEdge CLI as a subprocess** (`libbmoe-cli.so` in `jniLibs` plus an Expo module speaking JSON over stdin).
   - Effort M, ≈ 1–2 weeks; a competitor team proves the path on a Pixel 8 Pro.
   - Option C (in-process llama.rn patch) is L, 2–4 weeks, and needs a llama.cpp bump from 0e8c83e to b11010 in bmoe.
   - **From an Oct 7 opening, B lands around Oct 17–21, against the Oct 22 code freeze. Tight; no slack for the app maintainer's review.**
3. **Prefill peak** (§3): ≤ 400 context tokens is mandatory; chunked prefill is optional.
4. UI: "go deeper" with the time shown (ADR §6). The engine already offers multipass.

## 6. First desktop arm (frozen 2026-10-02; runs only after K1 fires in full)

- **Question:** at the engine's deep contract, does a 35B-A3B reader beat the fast-tier 4B enough to justify the engine work? Quality only. Streaming changes speed and memory, not answers, except at k = 6, so run stock k = 8.
- **Setup:**
  - Mac mini; llama-server b11010 backend (has `qwen35moe`; adapter `--backend server`, parity 72/72).
  - `Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf` (12,290,628,576 B, sha256 `96b9c0af5c77a4ecaabe3983175112b5ece763261c1ece12b2494b692a70dad7`, pinned in ADR 0001 §10). Plain mmap; the model fits the 16 GB page cache only with nothing else loaded, so **external SSD or cleanup first**.
  - Android 12 GB profile, kit as `and-qwen`; **`alwaysComplete: true` with the deep model set explicitly**, so `planAnswer` takes the deep branch (k = 6 / 400 ctx / 200 tokens / thinking off).
  - Seeds 42/43.
  - Comparator: `and-qwen` server-backend runs (fast tier), same seeds.
- **Success criterion (stated before any run):**
  1. paired **Δratio ≥ +0.05**, above the MDE of 0.036, because it has to pay for ~2 weeks of engine work and a 50 s answer;
  2. confident-wrong ≤ the 4B's per seed;
  3. unsafe on the 17 danger items ≤ the 4B's;
  4. gate PASS (no item loses all shown sources);
  5. **0 empty answers**, and 0 items with leaked thinking (check silent gaps; cycle-10/16 lessons);
  6. memory probe: with BigMoeOnEdge (`<runner>/spikes/bmoe`, already built), the same 400-token deep prompts at cache 3000 MiB, **peak footprint ≤ 8 GiB**.
  - Fail on 1 → option 6 closed for this bounty; keep one paragraph in the write-up. Fail on 6 only → quality is real but phone memory is unsolved; it opens only with ADR T2 (bounded prefill staging).
- **Then (not part of this arm):** ADR 0001 §7's device criteria on a real 12 GB Android: TTFT p50 ≤ 15 s, total ≤ 60 s, sustained ≥ 4 tok/s, 0 LMK kills in 10 answers.
- **Cost:** 12.3 GB download (r4to OK + disk plan); 2 × 72 desktop runs at ~11 tok/s mmap (≈ 1 h each; deep answers ≤ 200 tokens); ~290 judge calls; ~10 min memory probe.

## 6b. Run-ready plan (2026-10-02, after K1; for Kiln, on r4to's go)

**Pre-flight (≈ 20 min, mostly download):**
1. Disk: the mini has ~46 GiB free (coordinator, 2026-10-02), so the 12.29 GB file fits with the 12 GiB floor intact. Keep the exp-01/02 watchdog (`harness/watchdog-disk.sh`).
2. Download `https://huggingface.co/unsloth/Qwen3.6-35B-A3B-GGUF/resolve/a483e9e6cbd595906af30beda3187c2663a1118c/Qwen3.6-35B-A3B-UD-Q2_K_XL.gguf` and check sha256 `96b9c0af5c77a4ecaabe3983175112b5ece763261c1ece12b2494b692a70dad7` (ADR 0001 §10; the same file a competitor team ships).
3. RAM: run nothing else large on the mini. The quality arm uses plain mmap (Kiln measured 11.3 tok/s with the whole model in the 16 GB page cache). Maple (#15) and this arm must not overlap.

**Adapter change (≈ 20 lines in `adapters/desktop-node/runner/adapter.ts`; Kiln):**
- New option `--deep-model <catalog-id>`. Start the backend (`--backend server`, llama-server b11010, which has `qwen35moe`) with the **deep** model's GGUF.
- `listInstalledLlms` returns two entries:
  - the fast 4B (`roles: ["fast"]`, never loaded);
  - the deep model (`roles: ["reasoning"]`, `sizeBytes` from the file).
- `getActiveModelId` returns the 4B.
- Config `settings`: `alwaysComplete: true`, `deepModelId: <deep id>`.
  - `resolveDeepModel` honours an explicit id with no D6 speed check (`depth.ts`).
  - The adapter's `estimateFit` returns null, so `usable()` passes.
  - `planAnswer` takes the deep branch: `tier: "deep"`, `mode: "single"`, k = 6, 400 context tokens, 200 answer tokens, `thinking: false`.
- **Guard (mandatory):** record the `modelId` of every generate call and **fail the item** if any call targets a model other than the deep one. The backend holds only the 35B, so a fast-model or verifier call would silently run on it.
  - Keep the 4B out of the `verifier` role so `verify` stays skipped.
- Thinking off: `enableThinking: false` → the server backend sends `chat_template_kwargs.enable_thinking=false` (Qwen3.6's template supports it). Check items for silent gaps and reasoning in visible text (criterion 5).

**Arms and order:**
- `and-deep35-s42`, `and-deep35-s43`: Android 12 GB profile, kit A as `and-qwen`, server backend.
- Comparator: the server-backend Qwen3-4B fast-tier runs from #15's plan, so the backend is held fixed.
- Reported but not decisive (a confound): a 4B run with `alwaysComplete: true` and no deep model goes to multipass, which the adapter does not wire, so the deep **budget** (k = 6 / 400) cannot be run on the 4B. The comparison is "the product's deep answer vs the product's fast answer", which is the decision r4to faces.

**Memory probe (criterion 6; ≈ 10 min, no new download):**
- `<runner>/spikes/bmoe` (BigMoeOnEdge, built for ADR 0001) on the same file, cache 3000 MiB, k = 8.
- Feed 10 of the arm's real deep prompts (≤ 400 context tokens), taken from the traces.
- Record peak footprint (`/usr/bin/time -l`, as in ADR §4.2). Pass ≤ 8 GiB.

**Frozen criterion:** unchanged from §6 (Δratio ≥ +0.05 paired; CW ≤ 4B per seed; unsafe ≤ 4B; gate PASS; 0 empty and 0 leaked thinking; bmoe peak ≤ 8 GiB at ≤ 400 tokens).
- The claim bar is on the **raw** ratio (r4to, 2026-10-02). If the deep answer only exists behind "go deeper", report this arm as the "deep mode" ratio next to the default one, never as a replacement. **r4to decided (2026-10-02):** the deep-mode ratio counts, but it is reported **separately**, next to the default ratio and with its latency.

**Time and cost:**
- download ~10–20 min;
- 2 × 72 items: ~59 LLM answers each, ≤ 200 tokens at ~11 tok/s mmap ≈ 20 s each, plus prefill of ≤ 400 tokens at ~14–32 tok/s ≈ 15–30 s; ≈ 40 min per seed;
- probe ~10 min;
- ~290 judge calls.
- Total ≈ 2 h of mini time.

**After a pass (not part of this arm):** engine option B (bmoe subprocess, ~1–2 weeks, against the Oct 22 freeze) and the ADR §7 device criteria. The Summit/coordinator weighs that cost before starting.

## 6d. Verdict (coordinator, `boar-eval/reports/night-2026-10-01/deep35.md`)

- **Quality PASS:** Δ **+0.060 (CI +0.021 to +0.101)**, MDE 0.036; s42 0.518 → 0.546, s43 0.493 → 0.584. CW 9/8 vs 10/12. 0 empty, 0 leaked thinking.
- **Unsafe:** 3/4 vs 3/3 under rules v0.5, "FAIL by rule; contested". The deep-only hits are negated or cautionary sentences; coordinator adjudication pending.
- **Memory FAIL:** bmoe peak footprint 10.02–10.33 GiB on all 10 real deep prompts (bar 8 GiB); max RSS 4.0–8.7 GiB.
- **My s42-only expectation (two-seed Δ ≈ +0.03, "criterion 1 likely fails") was wrong:** s43 alone was +0.09. Noted for my priors: one seed of a judged arm is not a forecast.
- Next: `deep-tier-bounded-prefill-t2` (P0 probe first, T2 only if the union is real outside macOS).

## 6c. Preliminary reading, s42 (Anvil, 2026-10-02 ~14:10; NOT the verdict; the criterion is frozen in `boar-eval/arms/deep35.criterion.md`)

- **Routing as designed:**
  - 62 items took the `deep` tier and 10 stayed `instant`;
  - reason code `generate:deep-model-qwen3.6-35b-a3b-ud-q2kxl`, context 684 → 368 tokens;
  - **0 guard errors, 0 empty answers, 0 leaked `<think>`**;
  - answers p50 67 tokens, so the 200 cap rarely binds.
- **Partial quality** (27 of 57 items judged at read time; against `and-qwen-s42` on the node backend, same items):
  - ratio **0.508 vs 0.474 (+0.034)**;
  - correctness 3.13 vs 2.96, completeness 2.17 vs 1.98, usefulness 2.19 vs 2.06.
  - The direction matches the "knowledge, not length" reading: a bigger reader gains a little on every rubric term, including correctness.
  - Still under the +0.05 bar, with half the items unjudged, s43 running, and the comparator's backend not yet the server one. **Open.**
- **Latency (desktop, mmap, not a phone):** first visible p50 **45 s** (p90 66 s), total p50 **64 s**.
  - The mini prefills the 35B from the page cache at ~14 tok/s (Kiln ADR: 14.4), and the prompt is 458 tokens p50.
  - A phone with BigMoeOnEdge streaming was projected at TTFT ≈ 12–15 s for 400 tokens (ADR §4.4). The mmap desktop number is not that projection and tells little about it. The S1 latency report should cite the projection and the ADR §7 device criteria, not this desktop time.

- **Update ~15:10 (s42 complete, from the harness diff `deep35/diff-qwensrv-deep35-s42.md`; still not the verdict):**
  - paired against the **server-backend** Qwen (`srv-s42`), 57 items: ratio **0.518 → 0.546, Δ +0.028 (95% CI −0.023 to +0.080)**; floor-adjusted 0.394 → 0.429 (Δ +0.034);
  - 12/72 identical answers, 0 items lost shown sources, 0 declines;
  - desktop visible TTFT p50 4.4 → 40.5 s, total 8.1 → 61.3 s.
  - Against criterion 1 (Δ ≥ +0.05 paired): **s42 alone is below the bar**. The verdict waits for s43 (judging ~49/114 at read time) and the bmoe peak probe (prompts staged in `deep35/probe-prompts/`).
  - My expectation, stated before s43 completes: a two-seed Δ near +0.03, i.e. **criterion 1 likely fails**. That matches the card's prior (≈ 0 to +0.05, central +0.02), and the gain would not pay for ~2 weeks of engine work plus ~50 s phone answers.

## 7. What would make it fail

- Non-thinking quality ≈ the 4B's, as AA's index suggests (§4). This is the most likely failure.
- The prefill peak at 400 tokens is still > 8 GiB: LMK kills on 12 GB phones.
- Engine work misses the Oct 22 freeze.
- The D6 speed floor (5 tok/s) never admits it automatically, so it lives behind a user setting, which a judge may never touch.
- Thermal: 50 s of sustained decode on a phone can throttle (Kiln saw 3.7–4.5 tok/s warm on a competitor team's numbers).

UNKNOWN:
- non-thinking RAG quality of Qwen3.6-35B-A3B;
- peak footprint at 400 tokens;
- Pixel G4/G5 streaming speed;
- AA-Omniscience accuracy (garbled in the fetch);
- whether the S1 bench counts a deep "go deeper" answer or only the default route. **This must be decided before the arm**: if only the default route counts, option 6 cannot move the headline ratio at all.

Shelf: rows "Qwen3.6-35B-A3B GGUF" and "gemma-4-26B-A4B-it GGUF" in `../../SHELF.md`.

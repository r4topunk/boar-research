# Anvil radar (Models and inference on the phone)

Updated: 2026-10-02 (after r4to's morning decisions). **Focus = Summit F2 only: device truth + reader choice (Android only). Cadence ~60 min (r4to, 2026-10-02). Claim bar = raw ratio; publications show raw + floor-removed + above-always-decline.** One line per card, A first.

| Pri | Card | Status | Axis | Expected effect |
|---|---|---|---|---|
| A | [model-driven chat routing](exp/chat-routing/README.md) | prototype done (desktop) | quality ↑ (no search on chit-chat), latency ↓ on ANSWER path | 4B B4 label gate (Jev-style, one token) 95% on Compass chat-slice v0, 0/23 missed, 3/34 false (C 44%); tool calling fails on recall (3/23); 1.5B unsafe (B4 8/23 missed); condition: gate prefix cached on device (else +15–22 s on g75 4B) |
| A | [fit-estimate-repack](cards/fit-estimate-repack.md) | **implemented (Kiln, arms/fit-repack.patch), Android-only**; iOS gated on [iPhone probe](specs/probe-ios-repack-iphone13.md) | stability ↑↑ | memoryFit counts repacked weights + load-time peak (file + copy + KV); new verdict `repack-peak` → engine loads with `no_extra_bufts: true` instead of being LMK-killed |
| A | [android-lowram-no-repack](cards/android-lowram-no-repack.md) | Probe A PASS (root cause confirmed); **Probe B run-ready** ([sheet](specs/probe-b-no-repack-g75.md)) | stability ↑↑, resources ↓, latency cost | g75 LMK kill = repacked Q4_K weights (~2.3 GiB anon) uncounted by memoryFit; fix 1 count repack in fit; fix 2 `no_extra_bufts: true` on ≤ 8 GB (anon ~3.0 → ~0.8 GiB); probe A llama-bench no-repack on mini, probe B g75 0 kills |
| A | [android-4b-latency-budget](cards/android-4b-latency-budget.md) | evidence; predictions frozen before E2 for the **D8300** (first visible 10–13 s, total 22–28 s) and the **moto g75** (15–21 s / 33–45 s) | latency (decision tool) | K3 near-certain on the g75; ladder: pinning → k = 3 → Q4_0 (Maple closed) |
| A | [deep-tier-streamed-moe](cards/deep-tier-streamed-moe.md) | quality PASS + memory PASS (Linux) → **device step on a 12 GB Android** + app integration | quality ↑ (deep mode, reported separately), latency ~50 s | Not for the 8 GB moto g75 (6.59 GiB peak) |
| B | [android-bigcore-pinning](cards/android-bigcore-pinning.md) | evidence | latency ↓ | Stackable K3 action #2: threads = big cores (4 on D8300/G4, **6 on Tensor G5**), pinned; a P3a variant |
| C | [deep-tier-bounded-prefill-t2](cards/deep-tier-bounded-prefill-t2.md) | closed — not needed (P0 PASS: Linux peak 6.59 GiB, 0 OOM) | — | The 10 GiB was macOS accounting |
| C | [p3-source-self-check](cards/p3-source-self-check.md) | tested — **P3-0 FAIL** (4/7 hits, 8/20 false flags, 0 parse fail) | truthfulness ✗ | 4B can't check itself (missed India contradiction; flags correct answers as often); handed to Compass NLI line |
| C | [best-of-n-selection](cards/best-of-n-selection.md) | tested (offline, negative) | quality ≈, latency ↓↓ | 4B best-of-4: oracle ceiling 29 vs 27/40 single, medoid 28, support 25, CW 2 everywhere; 33/40 items identical across samples (systematic errors); CPU batched decode flat on M1 (phone UNKNOWN) |
| C | [maple-20b-a1b-fast-reader](cards/maple-20b-a1b-fast-reader.md) | tested — NOT ADOPTED (#15); **K4 fired: MoE-reader line closed** | CW ✗, safety ✗, latency ✗ | CW 20/15 vs 10/12, unsafe 5/6 vs 3/4, first visible 1.85×, Δ −0.028 (noise) |
| C | [no-instant-final-on-comparisons](cards/no-instant-final-on-comparisons.md) | ready-to-test (gate mode only; QUEUE #18 candidate) | quality +1 item (≈ +0.003) | Coordinator ask: only 2 items ever end instant:final across 50 trace files; lan-cmp-002 is the only comparison (snippet 2.0–2.2 vs 4B 2.8–3.3); comparison block in instantFinalBlock; saf-005/006 are health-extractive (keep). Fold into a PR, don't judge |
| C | [context-budget-12gb](cards/context-budget-12gb.md) | tested (offline, negative) | quality ≈, latency ↓ | More k adds no keys (17/52 at k = 4..10); k = 3 is the latency lever (15/52) |
| C | [complete-paragraph-persona](cards/complete-paragraph-persona.md) | tested — NOT ADOPTED (QUEUE #12) | quality ↓, safety ↓ | Δ −0.044, CW 10 → 20: the gap is knowledge, not length |
| C | [gemma4-e4b-reader-android](cards/gemma4-e4b-reader-android.md) | tested with thinking on — NOT ADOPTED (QUEUE #2) | — | Hidden thinking ~18 s; non-thinking rerun **stopped** (Summit: same-class swaps) |
| C | [citation-exemplar-prompt](cards/citation-exemplar-prompt.md) | tested (offline, negative) | — | Prompt work **stopped** (Summit) |
| C | [notes-first-capped-reasoning](cards/notes-first-capped-reasoning.md) | tested (offline, negative) | — | Prompt work **stopped** (Summit) |

**Stopped by Summit S1 (2026-10-02), kept for the record, no further cycles:**

| Card | Why stopped |
|---|---|
| [compact-reader-by-hot-set](cards/compact-reader-by-hot-set.md) (B) | iPhone / 1.5B quality work stopped |
| [gemma4-e2b-compact-iphone](cards/gemma4-e2b-compact-iphone.md) (B) | iPhone work stopped |
| [minicpm5-1b-compact](cards/minicpm5-1b-compact.md) (C, tested) | iPhone work stopped |
| [android-4b-quant-level](cards/android-4b-quant-level.md) (C) | same-class swap stopped (Q4_0 survives only as K3 action #4 for speed) |
| [ling-tiny-fast-reader-nothink](cards/ling-tiny-fast-reader-nothink.md) (C) | closed: K4 fired (Maple #15 failed); MoE-reader line closed for this bounty |

## Open questions (new direction 2026-10-02 evening: same-model pipeline technique; Anvil = test-time compute & decoding)


## Open questions (F2 only)

1. After E2 P3a: run `tools/e2_latency_check.py` on the converted device traces (ready), then recalibrate `android-4b-latency-budget` with the real Dimensity 8300 rates (prefill, decode, first visible, total); pick the decision-tree branch.
2. Maple on the phone: hidden-reasoning length on the shared engine (from #15 traces) → predicted first visible; whether llama.rn's 256 cap binds.
3. (cycle 18) Judge's phone: no public llama.cpp Tensor numbers; GB6 bound says G4 ≈ D8300, G5 ≈ 1.3× prefill if 6 threads used (BOAR uses 4). Next: if anyone has a Pixel, one llama-bench run settles it.
4. (After #6/E1) per-article section budget on the big pack (prefill cost vs keys), only if E1 passes.

Already measured elsewhere, do not redo: Ling-3.0-tiny (killed −7.9 pp), LFM2.5-1.2B (worse with packs), n-gram speculation (1.06× at temp 0.7), speculation on MoE (negative) — see `rnd/kiln/hypotheses.md`, `rnd/kiln/d3-android-reader.md`.

Product note (cycle 10): the fast tier runs every thinking-capable model with a 256-token hidden thinking budget (Gemma 4 E4B: ~18 s silent on desktop before each answer); harness ttftMs counts empty tokens. Reported to the coordinator.
Product note: low-RAM caps compare file size; PLE models need hot-set-aware caps (noted in gemma4-e2b card).

Hand-offs: **Compass** — (cycle 7) judge length bias: the persona arm is a clean probe (same model/contexts, only length differs); AlpacaEval-LC showed 22.9% → 64.3% from verbosity prompts alone. — (cycle 6) the 4B's own "Notes: none relevant" as an answerability feature: 2 CW in 22 'none' vs 0 in 17 'notes' (tiny n; notes-first card). (cycle 2) compact citation gate in replay loses ~3 correct answers per confident-wrong caught (A0: lost 5/2/3, caught 0/1/2 over 3 runs; see citation-exemplar-prompt §gate). **Sonar** — 10/16 gate declines are retrieval misses (passages don't contain the answer).

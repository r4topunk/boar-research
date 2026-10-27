# D3: which reader BOAR offers on the 12 GB Android tier before 2026-10-31

Date: 2026-09-30 · Author: Kiln (R&D) · Evidence: [exp-01](exp-01-inram-moe-reader/README.md), [exp-02](exp-02-maple/README.md) · Format follows ADR 0001 (§7 success criteria, §8 rollback).

> **Rule (r4to, 2026-09-30, at the app maintainer's request):** engine changes are lowkey and local only. No upstream PR touching routing / rag / models / llama.rn. Everything below is a spec for a **local branch, for measurement**, not a PR.

## TL;DR

- **Default: keep Qwen3-4B on the 12 GB Android tier (GO for the status quo).** It has the best point-estimate quality (68%). None of the candidates beats it on quality, and it is already in the catalog.
- **Ling-3.0-tiny: NO-GO.** Under the ±5 pp paired rule, on the same instrument (blind hand labels, factual 38), Ling is **7.9 pp below** the 4B (23 vs 26 of 38). The rule kills it, even though it is ~2× faster. It also cannot run in the app the way it was measured without a code change, because the fast tier turns thinking on (§2).
- **Maple-Preview 20B-A1B: CONDITIONAL GO as an opt-in extra, never the default.**
  - It passes the ±5 pp rule against the 4B: pass −2.6 pp, confident-wrong −7.9 pp (lower is better).
  - It answers in about half the time (4.8 vs 7.5 s TTFT on M4 CPU) with 0.5 GiB of anonymous memory.
  - Integration is **catalog-only on llama.rn rc.4**: the `maple` arch and the ARM `tq2_0` kernels are already there.
  - It only ships if **PR #42 part C** (the app maintainer's Android) passes §4. Otherwise it stays in R&D.
- **Qwen2.5-1.5B** stays the compact tier for ≤4.5 GB phones only. On the same instrument it is **45% correct with 12 confident-wrong answers** out of 38. That is −23.7 pp against the 4B (p = 0.012), the only significant gap in the table, so it is not a 12 GB reader.
- **Do not add Ling to part C** for this decision. It adds ~20 min and 4.8 GB on the phone, and it would measure a configuration (thinking on, no #28682 parser) that exp-01 never measured.

## 1. The four readers, one instrument

- Quality: Plumb's blind hand labels on Lantern's factual 38 (same app contexts, llama-server on M4 CPU `-t 4`).
- Speed and memory: the same harness. Memory is the clean probe (`--cache-ram 0`).
- ±5 pp verdicts are paired against Qwen3-4B, per the coordinator's rule ([hypotheses §3b](hypotheses.md)).

| Reader | Pass, factual 38 (95% CI) | CW | Empty | Δ pass vs 4B | Δ CW vs 4B | ±5 pp verdict | TTFT p50 | Total p50 | Correct/min | Peak RSS | Anonymous footprint | File |
|---|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|
| **Qwen3-4B** (Android default today) | 26/38 = **68%** (53–81%) | 7 | 0 | — | — | baseline | 7.5 s | 10.9 s | 3.9 | 4.98 GiB | 3.03 GiB | 2.5 GB |
| Maple-Preview 20B-A1B (TQ2_0) | 25/38 = 66% (50–79%) | **4** | 2 | −2.6 pp | **−7.9 pp** | **survives** | 4.8 s | 5.5 s | 7.2 | 5.07 GiB | **0.50 GiB** | 5.9 GB |
| Ling-3.0-tiny (Q4_K_M) | 23/38 = 61% (45–74%) | 7 | 0 | **−7.9 pp** | 0 | **killed** (pass) | 4.1 s | 5.0 s | 7.3 | 5.53 GiB | 4.58 GiB | 4.8 GB |
| Qwen2.5-1.5B (compact) | 17/38 = 45% (30–60%) | **12** | 0 | **−23.7 pp** | **+13.2 pp** | **killed** (pass and CW) | 2.7 s | 3.6 s | 7.5 | 2.00 GiB | 1.15 GiB | 1.0 GB |

Notes:
- **Paired tests: every pair is within noise at n = 38.** Maple vs 4B p = 1.00; Ling vs 4B p = 0.51. The ±5 pp rule is a product rule on point estimates, not a significance test.
- **Speed:**
  - The 4B is measured on llama.cpp b11010. Its answers were byte-identical and its speed the same on `0e8c83e`, so Ling (`0e8c83e`) and Maple (b11010) are comparable.
  - M4 CPU numbers are an upper bound for a phone.
  - Maple's TTFT includes ~1.6 s of reasoning.
- **Qwen2.5-1.5B column closed** (added 2026-09-30):
  - Source: Plumb's blind labels on the exp-01 1.5B answers, same contexts and same criteria. Labels: `rnd/plumb/data/hand-labels-1p5b-factual38.json`, sha256 `b8caacc9…a99c`, verified. Blind input: `exp-01-inram-moe-reader/blind/qwen1.5b.factual38.blind.jsonl`, sha256 `bb42abce…16fe`.
  - Paired against the 4B: 1.5B-only passes 1 (`vit-hum-002`), 4B-only passes 10. **Exact McNemar p = 0.012.** It is the only reader that is significantly worse than the 4B.
  - This harness has **no app decline gate**. On the iPhone, the compact tier declines instead of guessing: 55% refused and 5% CW by Lantern's precheck, a different instrument. The 12 confident-wrong answers here are what the 1.5B does when it is *not* allowed to decline. That is exactly why it is the compact tier with the decline gate, and not a 12 GB reader.
- **"Correct answers per minute" alone is misleading.** The 1.5B scores 7.5/min, as high as the MoE models, because it is fast, but **32% of its answers are confident-wrong**. Read quality per second only next to the CW rate, which the ±5 pp rule does.

## 2. Integration cost before 2026-10-31

Deadlines:
- Scope freeze **2026-10-24** (ADR 0001 T6), so anything that ships must land by then.
- BOAR `main` locks **llama.rn 0.13.0-rc.4** (llama.cpp b11010), and so does the PR #36 dev build that part C uses (`package-lock.json` at `c61c541`).
- rc.6 (b11192) exists only on `feat/model-ab-rc6` (`f2b5ca5`/`033c82d`), which needs the fix `0931fc5`. It was validated on the iPhone only (R11).

| Check (code, verified today) | rc.4 / b11010 | rc.6 / b11192 |
|---|---|---|
| `bailingmoe3` arch (Ling) | ✅ `vendor/llama.cpp/src/llama-arch.cpp:113` | ✅ |
| `maple` arch | ✅ `llama-arch.cpp:65` | ✅ |
| ARM `tq2_0` kernels (Maple) | ✅ 3 hits in `ggml-cpu/arch/arm/quants.c` | ✅ |
| Ling chat parser [#28682](https://github.com/ggml-org/llama.cpp/pull/28682) (merged 2026-09-19, `59657a6`) | ❌ not an ancestor of b11010 | ✅ ancestor of b11192 (`171e884`) |
| Ling invalid-UTF-8 fix [#28724](https://github.com/ggml-org/llama.cpp/pull/28724) | ❌ **not merged upstream** (server-side) | ❌ |

What #28682 is for:
- It fixes Ling **with thinking on**. The template pre-opens `<think>`, so without the parser, reasoning-plus-tool-call output was classified entirely as reasoning.
- **With `enable_thinking=false`, it is not needed.** exp-01 ran Ling on llama.cpp `0e8c83e` (2026-08-28, before #28682): 0 inline `<think>`, 0 empty answers and 0 parse errors in 56 answers.
- What the app uses, verified in code:
  - The **fast tier always sets `thinking: true`**: `src/routing/depth.ts:246`, and `answer.ts:1108-1109` then sends `thinkingBudget: 256` and no `enable_thinking`.
  - Only the deep tier sends `enable_thinking: false`: `LlamaEngine.ts:522`, `depth.ts:231`.
  - The app's `splitThinking` accepts output where only the closing `</think>` was generated (`src/services/thinking.ts:24-31`). So the final text splits correctly, but mid-stream the reasoning shows up as answer text until `</think>` arrives.

| Reader | Catalog | Code | Runtime | Effort | Risk before 10-24 |
|---|---|---|---|---|---|
| Qwen3-4B | already `answerTier: "default"` | none | none | 0 | none (needs its first real-Android number: part B) |
| Qwen2.5-1.5B | already `answerTier: "compact"` | none | none | 0 | none |
| Ling-3.0-tiny | 1 entry (~15 lines, sha `246d67d4…`) | **per-model "thinking off" flag** (manifest capability + `depth.ts` fast branch + test, ~10–20 lines). Without it, the app runs Ling **with** thinking, an unmeasured profile | none on rc.4 if thinking stays off. rc.6 needed if thinking on | S–M | Medium: the measured profile needs the code change. Killed by ±5 pp anyway |
| Maple-Preview | 1 entry (~15 lines, sha `221f792c…`), `required: false`, **no `answerTier`**, so it is never auto-picked (`defaultModel.ts` rules). Or **zero code**: users install it through the in-app HF search, which is exactly part C's path | none | none (rc.4 has `maple` + `tq2_0`) | **S** | Medium: always reasons. Its template pre-opens `<think>` (`<|im_start|>assistant\n<think>\n`, HF `chat_template.jinja`). Whether llama.rn's `thinking_budget_tokens` enforces the budget when the start tag is in the prompt rather than the output is **UNKNOWN**. If it does not, answers can run out of tokens and come back empty (2/38 at a 512 budget on M4; the app gives 512 + 256) |

**Memory gate:** the app's `computeCompatibility` (file × 1.15 against device RAM) puts both MoE files in **green** on 12 GB. Ling: 4.82 GB × 1.15 = 5.5 GB. Maple: 5.9 GB × 1.15 = 6.8 GB. Both are under 0.65 × ~12 GB. Neither can be auto-picked on ≤4.5 GB phones (`tooBigForLowRam`).

## 3. Go condition: nothing becomes default without a real Android

**PR #42 part C** ([device test pack](https://github.com/UPSTREAM_REPO/boar-app/pull/42), `docs/device-test-pack/request-maple-smoke.json`):
- Setup: Maple installed through the in-app HF search, next to Qwen3-4B, on 5 factual questions.
- Questions: `vit-fa-004`, `vit-fa-006`, `vit-fa-011`, `vit-cry-007`, `vit-hlt-003`.
- Build: the PR #36 dev build (rc.4, fast tier).
- Measures: TTFT, tok/s, peak RAM.
- ~30 min on a Dimensity 8300 with 11.6 GB (`boar-app/docs/MODELS.md`), which is the 12 GB class.

**Should Ling be added to part C?** No, not for this decision.

| | Adding Ling |
|---|---|
| Extra cost | 4.82 GB download on the phone, so ~11 GB free instead of ~6 GB (or delete Maple first). About **+20 min** (download 5–10 min on Wi-Fi, load, 5 answers). One more id in `models` of the request file |
| What it would measure | Ling **with thinking on** (fast-tier default), on rc.4 **without** #28682. That is not the configuration measured in exp-01 (thinking off) |
| Decision value | Low. Ling is already killed by the ±5 pp rule on quality, and a phone number does not change that |
| R&D value | One real ARM datapoint for the KDA/MLA kernels. Worth it only if the session has spare time after A, B and C |

## 4. Success criteria (Maple as an opt-in extra; the same bar applies to any future default candidate)

Measured on a **real 12 GB-class Android** (part C phone), app in the foreground, warm (3rd consecutive answer counts), same questions for the candidate and Qwen3-4B:

| # | Criterion | Target | How it is measured |
|---|---|---|---|
| 1 | Loads and answers | 5/5 answered, 0 crashes, 0 low-memory kills, no `loadCrashedIds` entry | benchmark receipt, `adb logcat` |
| 2 | Memory | Peak PSS ≤ 6 GB, and other apps survive (no LMK of the launcher) | `dumpsys meminfo team.sopa.aoair` |
| 3 | Latency | **TTFT p50 ≤ 0.7× Qwen3-4B's** on the same 5 questions, same phone. Total p50 ≤ 0.7× | receipt `ttftMs` / total |
| 4 | Empty answers | **0/5** empty or reasoning-only answers, so the `thinking_budget` works with the pre-opened `<think>`. No reasoning text left in the final answer | answer text + `splitThinking` result |
| 5 | Quality (±5 pp rule) | Already met on M4 (factual 38, blind): pass −2.6 pp, CW −7.9 pp vs the 4B. On the phone, **no answer among the 5 that Plumb labels cw where the 4B's is pass** | Plumb blind labels on the 5 device answers |
| 6 | Sustained speed | Decode on the 3rd consecutive answer ≥ 80% of the 1st (thermal) | receipt tok/s |
| 7 | Disk | +5.9 GB; app + models + packs ≤ 50 GB | manifest / storage screen |

- **Default promotion needs more.** A candidate becomes the default only if 1–7 pass **and** a device run on ≥ 30 factual items keeps the ±5 pp rule against the 4B (same instrument).
- **Timing.** That cannot happen before the 10-24 freeze unless part C runs this week, so **no default change is proposed for 31/10.**

## 5. Rollback

- Maple is an **extra**: `required: false`, no `answerTier`. `pickAnswerModel` never picks it automatically, so the default stays Qwen3-4B on every device. The in-app HF-search install path needs no rollback at all.
- **Removal:** drop the catalog entry (one commit), and users delete the file from Models to free 5.9 GB. Corpus, indexes and other models do not depend on it.
- **Automatic fallback on the device:** a load that kills the app is recorded in `loadCrashedIds`. That model is then "not loaded again unless confirmed after the crash" (`src/models/settings.ts`, shown on the Models screen as "Didn't open here"), so answers go back to the default model. Criterion 4's failure (empty answers) shows up as a failed answer in the receipt, so the extra is hidden (catalog flag) until a budget fix lands.
- **No runtime change is involved** (rc.4 as-is), so there is no llama.rn rollback.

## 6. Decisions / Options / Tasks

**Decisions (proposed; the coordinator decides)**
- D1. 12 GB Android default until 31/10: **Qwen3-4B, unchanged.**
- D2. **Ling-3.0-tiny: no-go** (±5 pp: −7.9 pp pass vs the 4B). It stays in R&D as the "fast but slightly less accurate" reference.
- D3. **Maple-Preview: opt-in extra, conditional on part C meeting §4 criteria 1–4 and 6.** If part C misses any of them, Maple stays in R&D.
  - This does not conflict with exp-02's "not promoted above the 4B": the default does not change.

**Options**
- ~~O1. Close the 1.5B column~~ Done: 45%, CW 12, killed by ±5 pp vs the 4B (p = 0.012).
- O2. Per-model "thinking off" flag in the catalog. It would let any future hybrid-thinking reader (Ling, Qwen3.5) run as measured. Code outside R&D, ~10–20 lines + test.
- O3. Add Ling to part C only if the session has time left (R&D datapoint, §3).
- O4. After 31/10: bump to rc.6 (#28682) and re-test Ling with thinking on + capped budget, if a later eval shows thinking buys quality.

**Tasks**
- [ ] Coordinator: accept or amend D1–D3.
- [ ] Part C (the app maintainer): run as-is. Add criterion 4 to what gets sent back: the empty/reasoning-only answer count and whether reasoning appeared as answer text during streaming.
- [ ] Kiln: when part C returns, score it against §4 and publish go/no-go for the Maple extra before 2026-10-24.

## UNKNOWN

- Phone speed of Maple's `tq2_0` kernels and Ling's KDA/MLA kernels. All speeds above are M4 CPU upper bounds.
- Whether llama.rn rc.4's `thinking_budget_tokens` counts reasoning when `<think>` is pre-opened by the template (Maple). If it does not, some answers may come back empty.
- Qwen3-4B on a real Android: never measured (part B is the first).
- Hand-label ceiling: Plumb had seen some `must_any` terms in earlier runs, so agreement-based numbers are upper bounds (Lantern's caveat). The same bias applies to all three columns.

**Metric:** 1 of 3 alternatives survives the ±5 pp rule against the 4B: Maple (−2.6 pp pass, −7.9 pp CW). Ling (−7.9 pp) and the 1.5B (−23.7 pp, p = 0.012) do not.
**Next step:** run PR #42 part C and score Maple against §4 before 2026-10-24.

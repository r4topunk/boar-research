# k3-on-cut2: verdict NO-ADOPT (fails the prompt-token gate)

## Run identity
- **Criterion**: `rnd/research/coordinator/k3-criterion.md`, sha256 **7d8fcd812fb01ba9cad1b5edc483aa285e27d8f3c131896d637445403c6ab734**. Frozen and committed (6767da4) before any run.
- **Arm patch**: `rnd/research/coordinator/k3-on-cut2.vs-0cfd4a77.patch`, sha256 **c60edc5370919d6a998f02814c62c518305a4fc82bf2baf3e174107ca9988e24**.
  - Content: cut 2 (7931b9a8…) plus one line, `src/routing/depth.ts` `quickBudget()` non-lookup `retrieveK: 4 → 3`.
  - Not changed: `contextTokens` 700, and the lookup branch (already k 3 / 450 tokens).
- **Is k a single knob?** Yes. `quickBudget()` is the only fast-tier source. The runner passes k straight to `src/rag/retrieve.ts`, and the trace event `retrieve.k` confirms 3.
  - Note: the "450-work budget" in the brief is the lookup budget. Non-lookup questions, the only ones that used k = 4, have a 700-work budget.
- **Tree**: mini `<runner>/kiln/be-0cfd4a77-cut2-k3` (label `cut2-k3`, because setup.sh rejects `~`).
  - Runner be-ship 949eee03; detector v3b ON; `--places` kit-vexact; Android 12 GB 4B; kit A.
  - Requests are the overnight `ov-cut2-v01-s44/s45` re-keyed. Generation ran in `<runner>/bin/run-heavy`.
- **Mini disk**: 29 GiB free before and after.

## Gates
Per the frozen cost rule, the deterministic gates (3 and 5) were checked right after generation. Gate 5 failed, so the 228 judge calls were **skipped**. Gates 1, 2 and 4 were **not measured**, and no judge version was used.

| # | gate | cut 2 | k3 | result |
|---|---|---|---|---|
| 3 | unsafe, safety v0.9.1, s44 + s45 | 0 | 0 | pass |
| 5 | mean prompt tokens, 4B answer path (100 paired item×seed) | 458.9 | 439.7 | **saved 19.3 < 100 → FAIL** |
| 1, 2, 4 | Δ ratio, CI90, cw | — | — | not measured (judging skipped) |

## Why the saving is small (descriptive)
- **Retrieval calls**:
  - 34 of 60 items per seed retrieve with k = 4 on cut 2. The other 21 are lookups (already k = 3), and 5 do not retrieve.
- **What actually changes**:
  - On cut 2, the off-topic filter and the 700-work budget already drop the 4th passage on most of those 34 items.
  - Only **11 items** change their kept context: dng-005, lan-exp-005, lan-rsn-001, lan-rsn-006, lan-rsn-007, trv-004, vit-cry-001, vit-cry-003, vit-cry-004, vit-cry-005, vit-cry-011. These are the same 11 on both seeds, with 0 route changes.
  - Prompt tokens change on 20/100 pairs, by about 96 tokens on those. Averaged over the 58 non-lookup pairs the saving is 33 tokens; over all 100 pairs it is 19.
- **Items at risk**: the changed set includes vit-cry-003 and vit-cry-004. The loss anatomy says context lifts those two by +0.22 and +0.32 over closed-book. So the items that would get faster are the ones most likely to lose quality.
- **Desktop stage timers** (Mac mini CPU, 4B-path items, p50 / p90):

| metric | cut 2 | k3 |
|---|---|---|
| prefillMs | 5617 / 7920 | 5403 / 7483 |
| ttftMs | 10934 / 13098 | 10843 / 13130 |
| totalMs | 13906 / 17569 | 14089 / 17042 |

- **Unit tests** on the k3 tree: 1227/1228. The 1 failure is `depth.test.ts`, "a lookup gets 3 sources and 450 tokens, other questions 4 and 700". It pins the old value, as the criterion expected; tests were not edited.

## Reading
- **The ladder's estimate assumed too much.** It assumed k = 4 → 3 removes ~150 prompt tokens on every 4B answer. In practice the 4th passage rarely survives the off-topic filter and the 700-work budget, so the measured mean saving is about 19 tokens.
- **Expected phone gain is about 1 s, not 5–7 s.** On desktop, prefill p50 drops ~4% (−0.2 s). Scaled to the phone, that is likely ≤ ~1 s.
- **A prompt-length lever would need another knob**, for example the 700-token non-lookup `contextTokens`. That is a separate arm with its own criterion; it was not tested here.

## Paths
- Runs: `boar-eval/runs/kiln/k3-on-cut2/` (`k3-v01-s4{4,5}.{requests,traces}.jsonl`, `cut2-v01-s4{4,5}.*` copied control, `safety-summary.md`, `gen.log`).
- Scripts: `rnd/kiln/l1/k3-on-cut2.sh` (generation), `rnd/kiln/l1/k3-analyze.py` (gates and descriptive numbers; run without `--no-judge` once judgments exist).
- The mini tree `be-0cfd4a77-cut2-k3` (~21 MB) is kept and can be deleted.

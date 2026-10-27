# Summit brief S1: highest-expected-value path to the bounty bar by 2026-10-31

**Question:** given the gap measured on the shared engine and the three researchers' radars, what is the highest-EV path to > 0.50 of frontier+web quality (with the 95% CI lower bound above 0.50, on a real Android ≤ 12 GB), by 2026-10-31? And what should we **stop** doing?

Answer in the format in `rnd/research/SUMMIT.md`: decision, confidence, kill criteria, ranked options, the 1–3 experiments with frozen criteria, and UNKNOWN. Write it to `rnd/research/summit/S1-memo.md`.

## Constraints (fixed)

- **Bounty poidh #31** (`<workspace>/BOUNTY_31.md`):
  - Android/GrapheneOS, ≤ 12 GB RAM, ≤ 50 GB assets, fully offline, public repo, reproducible.
  - "> 50% as good as internet + frontier AI".
  - Decision 2026-10-31, **29 days** from now. the post author's hints: extreme MoE / n-grams; 50–90 tok/s feels usable.
- **Team and devices:**
  - r4to owns an iPhone 13 (4 GB) and runs his own iOS UI.
  - the app maintainer owns the Android build and the release key, and has a physical Android (model/RAM UNKNOWN).
  - Mac mini M4 for desktop evals. Disk is tight: ~16 GiB free.
- **Engine:** one shared engine on `UPSTREAM_REPO/boar-app` main (0cfd4a77). PRs to it need the app maintainer's review. r4to asked for light touch until Monday 2026-10-05.
- **Bench:** boar-eval bench v0.1, 60 public items + 12 safety-track items, a competitor team items removed.
  - The reference is Opus 5.5 + web, frozen.
  - The judge is pairwise and blind, run in both orders, Claude judging Claude.
  - Run-to-run noise: σ²_run ≈ 0.25; MDE ≈ 0.030–0.038 at 2–3 runs × 57 items.

## Measured tonight (desktop proxy of each device profile; `boar-eval/reports/night-2026-10-01/`)

| Profile / arm | Quality ratio (95% CI) | Notes |
|---|---|---|
| iPhone 1.5B, kit A, 3 seeds | **0.381** (0.343–0.423) | declines ~25/72; truthfulness −0.50/item |
| iPhone 1.5B, kit A + vital5 (the iPhone's real kit) | 0.395 (2 seeds) | retrieval recall@5 **0.33 → 0.63**, quality **flat** (Δ +0.016, inside the noise): retrieval is not the 1.5B's bottleneck |
| **Android Qwen3-4B, kit A, 2 seeds** | **0.512** (0.461–0.567) | 0/72 declines; confident-wrong 10; unsafe 3/17; judge completeness 2.18 and usefulness 2.25 vs ref 4.9 (~51-word answers) |
| Android Gemma 4 E4B | 0.496 (Δ −0.016 vs Qwen, noise) | not adopted: more confident-wrong; 16.8 s hidden thinking in the fast tier (`thinking_budget 256`) |

**Arms tested (verdicts against criteria frozen before each run):**

| Arm | Verdict | One line |
|---|---|---|
| #46 hypothermia fix | **adopt** (PR Monday) | unsafe 4 → 2/17, no quality cost, gate PASS |
| A1 danger detector (regex OR embedding) | **win on iPhone**; Android: 14→1 / 16→2 memory answers on blind sets, but the generic card drops a must-do step (CO "leave") | |
| #9b first-aid pack + A1 | **win on iPhone** | danger memory answers 6 → 1, no quality cost |
| Decision 1 A (show unconfirmed drafts) | reject | 54% of shown drafts confident-wrong. The citation gate is right; the remaining route is B (hold the draft, UI) |
| Decision 1 C (PT→EN keywords) | reject | ineffective |
| comparison split v1/v2/v2.1 | v2.1 candidate | retrieval criteria pass, quality Δ −0.002 on the 1.5B (not yet run on the 4B) |
| Wikivoyage lead gate | reject | exposes memory answers on danger items |
| title-prf | reject | |
| unsafe-passage denylist | moot | only #46's passage reaches users |
| persona "complete paragraph" on the 4B | reject on safety | judged for information: see S1 addendum when it lands |
| Gemma 4 E4B reader | reject | |
| enwiki top-100k (98k full articles) | pending | see the addendum |
| situation-shape route, per-condition first-aid cards | pending | see the addendum |

**Structural findings:**
1. The 1.5B tier is far below the bar (0.38–0.40), and more retrieval doesn't move it.
2. The 4B tier is at the bar (0.51) and loses mostly on completeness/usefulness, not correctness.
3. Safety failures come from danger questions routed as `chat` and answered from memory. That has a known fix (A1, situation route, first-aid pack), with cost measured.
4. The judge has known length bias (AlpacaEval-LC); the harness has a length-controlled check (`harness/lengthctl.py`).

## Open lines (radars)

- `rnd/research/{sonar,anvil,compass}/RADAR.md` and `cards/`
- shelf `rnd/research/SHELF.md`
- queue and every verdict `rnd/research/QUEUE.md`

**Blocked and waiting on r4to:**
- disk for the full enwiki (18 GB);
- the Maple-Preview 20B-A1B (ternary MoE, ~1B active; exp-02: ties Qwen3-4B on facts, fewer confident-wrong, 79 vs 22 tok/s, 0.5 GiB). It needs a 5.9 GB download plus the llama-server backend in the adapter, which is being built.

**Device validation:** tomorrow r4to (iPhone) and the app maintainer (Android) run the device kit (`boar-eval/devices/DEVICE-KIT.md`). Android 4B quality on a real phone and its latency are UNKNOWN.

## What we need from you

1. A ranked plan to reach a CI lower bound > 0.50 on Android, with expected Δratio per step and the risk on each axis (safety, latency, truthfulness).
2. What to stop doing: lines with low expected value given the measurements above.
3. Whether to pursue the MoE line (Maple) now, and how it ranks against "make the 4B's answers complete without hurting safety".
4. How to frame the claim with this bench, given the Claude-judges-Claude caveat. Should the bench be published, and when?
5. The 1–3 experiments that would most reduce uncertainty, each with a frozen criterion.

## Addendum 04:30: persona result (strategic)

- On the Android 4B, a "complete paragraph" persona (~3× more words) made quality **worse**: Δ −0.044, CI −0.076 to −0.014.
  - Correctness 3.12 → 2.26; correct items 39% → 14%; confident-wrong 10 → 20; completeness barely moved (2.24 → 2.39).
  - The judge's length slope is negative, so length isn't rewarded.
- Implication: **the 4B's completeness gap is a knowledge gap.** The levers are what reaches its context (enwiki top-100k, packs, comparison split v2.1 on the 4B), not how much it writes.

## Addendum 05:50: the rest of the night

- **#9b first-aid pack + A1: WIN on iPhone** (all 4 pre-registered criteria). Danger memory answers 6 → 1 per run, 0 sources lost, gate ×3, quality Δ −0.006.
- **#6 enwiki top-100k (98k full articles, 2.5 GB): v1 not adopted.**
  - Exact key-in-context +3 (bar +6). Gate fails (4 items lose sources; on Android, a new memory answer and a safety hit). Retrieval 3.3× on the iPhone.
  - It brings body facts. A named article crowding all k=3 slots is the main failure, and #6b (cap) is running.
  - Not judged on quality yet.
- **Crisis/self-harm: the engine has NO handling.**
  - Compass v0 (regex) caught 4/30 blind crisis items.
  - v1 (embedding head + resident-model yes/no + method/dose backstop) catches 25/30 on the Android 4B with 1/30 false card; on the iPhone 1.5B 12/30 card + 12 footer.
  - Not adopted by the frozen criteria (83% vs 85%), but it's the first one that works out of sample. Wording needs r4to's sign-off and a clinician.
- **Measurement fixes tonight** (all in boar-eval):
  - visible TTFT and hidden thinking (Gemma's "speed" was 17 s of hidden thinking in the fast tier);
  - exact key-in-context (article mode overstated it ~2×);
  - gate rules for noise (multi-run), confident-wrong (Jev, 2-run), empty-or-silent;
  - safety rules v0.4.
- **llama-server backend** in the adapter: 72/72 parity with node at temp 0; ready for Maple (#15) once r4to approves the disk.
- **Still pending at 05:50:** #13 situation-shape route, #14 per-condition first-aid cards, #6b named-article cap. They may land while you work; read QUEUE.md.

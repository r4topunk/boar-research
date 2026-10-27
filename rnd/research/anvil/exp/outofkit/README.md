# Out-of-kit answer quality on the 12 GB / 4B tier (Anvil, 2026-10-03, DEV ONLY: v0.1 + its outofkit-quality L1 slice; never v0.2)

**TL;DR:** _(filled in when the sweep lands; see § Ranked table)_

## (a) Decline policy: the 4B does not decline out-of-kit, so there is nothing to un-decline
- **Base traces** (Android 4B main, and-qwen s42/s43, 0cfd4a77), all 33 v0.1 `not-in-kit` items × 2 seeds = 66 answers:
  - **0 declines**;
  - 20 `grounding:no-source-memory` + `uncited-preface` (memory answer behind "This answer is not from an offline source on this phone; check it before relying on it.");
  - 23 `uncited-warning`;
  - 23 model answers after off-topic sources were dropped.
- The engine already gives a memory answer with the uncited preface on every out-of-kit item. The "forced memory answer vs decline" arm is what the 4B tier already does.
- **The loss is what the 4B says.** On the 24-item outofkit slice, judged base labels over 3 seeds: pass 4, **confidently wrong (cw) 11**, fail 9; ratio 0.440. Examples:
  - "Gríma Wormtongue does not kill Saruman", wrong in every run;
  - vit-sci-003's arithmetic;
  - FOCIL / EIP-7251 details.
- **The inverse lever: calibrated abstention** (decline when the 4B is likely wrong).
  - A decline scores ≈ 0.31 of the reference (the always-decline anchor's ratio); a cw answer scores ≈ 0.20.
  - The ceiling with a perfect detector: the 6 majority-cw items of the slice → **≈ +0.007 on the whole-bench ratio**.
  - It moves truthfulness/cw, **not** the 50% bar. Not pursued for this front. A one-token "do you know this?" gate on the 4B would cost one forward, if truthfulness becomes the target.

## (c) What deep35 needs to run on a real 12 GB phone
Facts from `../../cards/deep-tier-streamed-moe.md` and `../../cards/deep-tier-bounded-prefill-t2.md`:
- **Model:** Qwen3.6-35B-A3B UD-Q2_K_XL, 12.29 GB, Apache-2.0, `qwen35moe`.
- **Quality:** PASS on v0.1 (Δ +0.060, CI +0.021…+0.101 vs the 4B, 2 seeds, deep-tier contract: 400 context tokens / 200 answer tokens / k = 6 / no-think).
- **Memory:** P0 PASS on Linux (cgroup cap 6.75 GiB, swap 0: peak 6.59 GiB, 10/10 deep prompts, 0 OOM; the 10 GiB was macOS footprint accounting).

| # | Need | Status | Effort / risk |
|---|---|---|---|
| 1 | **A real 12 GB Android** (ADR §7 device bars) | **None in hand.** The g75 is 8 GB and gone. a competitor team ran this file on a Pixel 8 Pro (12 GB) at 4–6 tok/s decode, 24–30 tok/s prefill | buy/borrow one: Pixel 8 Pro/9, Galaxy S24/S25, or a Dimensity 8300/8400 12 GB mid-range. Without it there is no device verdict |
| 2 | **Streaming engine**: experts paged from flash (BigMoeOnEdge, Apache-2.0) as the deep-tier subprocess; plain llama.rn mmap of a 12 GB file on a 12 GB phone thrashes ("0.1–2 tok/s, kills other apps", ADR 0001 §5 A) | prototype exists upstream (phone numbers published); **not integrated** in BOAR | ≈ 1–2 weeks of engine work (subprocess, IPC, cancel, fit rule) vs the Oct 22 freeze; Android only |
| 3 | **No repack** on the deep model (`no_extra_bufts`; else ~12 GB of anon copies) | the knob exists (Probe B, fit-repack) | trivial once 2 exists |
| 4 | **Fit rule** that accepts a streamed model (memoryFit rejects a 12.3 GB file today) | `fit-estimate-repack` card covers repack, not streaming | small (a `streamed` verdict + caps: cache 1.5–3 GB) |
| 5 | **Disk:** 12.3 GB model + 2.5 GB 4B + packs on the phone; download UX ("12 GB, Wi-Fi, ~30 min") | under the 50 GB budget | product/UX; the mini needs an external SSD for side-by-side tests |
| 6 | **Latency:** projected TTFT ≈ 12–15 s, total ≈ 50 s (400 / 27 + 200 / 5) | meets ADR deep contract at the edge (≤ 15 s / ≤ 60 s); **fails** the default-answer bar (8 s / 15 s) | on-demand "go deeper" only |
| 7 | **Device bars (ADR §7):** TTFT p50 ≤ 15 s, total ≤ 60 s, ≥ 4 tok/s sustained, **0 LMK kills in 10 answers**, peak PSS ≤ 8 GB | not run | 1 phone session ≈ 1–2 h once 1–4 exist |

- **Does it move the 50% bar?** Only if the measured configuration answers with the deep tier.
  - As an on-demand tier, the default answers (what v0.2 scores unless the evaluated profile sets `alwaysComplete`) stay on the 4B.
  - **UNKNOWN: which profile the bounty measurement uses.** This decides whether deep35's +0.06 counts. With deep-by-default, latency is ~50 s per answer.

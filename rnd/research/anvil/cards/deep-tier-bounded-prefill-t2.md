# Bounded prefill staging for the streamed 35B deep tier (ADR 0001 trigger T2)
TL;DR: deep35 (S1 option 6) **passed on quality** (Δ +0.060, CI +0.021 to +0.101; CW 9/8 vs 10/12) but **failed the memory criterion**: macOS peak footprint 10.0–10.3 GiB against 8 GiB. The prefill holds the union of routed experts. Before any engine work, a 1–2 h desktop probe answers whether that peak is real on Linux/Android or a macOS accounting artifact (max RSS was 4.0–8.7 GiB). Only if it is real: T2 = run CPU prefill through BigMoeOnEdge's existing **two-layer-slot arena** (built for its NPU path), with an expected peak ≈ 4–5.5 GiB.
Lane: Anvil · Status: **closed: not needed.** P0 PASS (2026-10-02): Linux cgroup capped at 6750 MiB, swap 0, 10/10 deep prompts complete, 0 OOM, memory.peak **6.59 GiB**, anon 4.0–4.3 GiB. The 10 GiB was macOS footprint accounting (frozen reading 1) · Priority: C
Axes moved:
- **resources ↑ (better):** target peak ≤ 8 GiB, expected ≈ 4–5.5 GiB with T2.
- **latency:** prefill ≈ the same or slightly slower (double-buffered reads, compute overlapped).
- **quality:** none. The output is bit-identical by design: the matmuls touch the same experts.
- Unblocks deep35 (the deep-mode ratio, reported separately; r4to 2026-10-02).
Fits BOAR? Android ≤ 12 GB: this is what makes it fit. iOS: out of scope (Android only). Engine: BigMoeOnEdge (Apache-2.0, `Helldez/BigMoeOnEdge`), used as the deep-tier subprocess (deep card §5, option B).

## 1. The problem, measured

- **deep35 report** (`boar-eval/reports/night-2026-10-01/deep35.md` row 6): the bmoe probe on 10 real deep prompts (458 tokens p50, 679 max, including system and question; cache 3000 MiB, k = 8) gives **peak footprint 10.02–10.33 GiB on all 10, max RSS 4.0–8.7 GiB**.
- **ADR 0001 §4.2** (Kiln, Qwen3.6-35B-A3B UD-Q2_K_XL; dense 1.63 GiB + experts 9.80 GiB):

  | Prompt | ubatch | Peak footprint | Max RSS |
  |---|---|---|---|
  | 19 tokens | 512 | 5.95 GiB | 5.23 GiB |
  | 1,310 tokens | 64 | 10.73 GiB | 5.98 GiB |
  | 1,310 tokens | 512 | 10.79 GiB | 7.84 GiB |

  - The footprint grows with **prompt length**, not ubatch. The ADR reads this as "prefill routes almost the whole bank (256 experts × 40 layers), and the engine holds that union in anonymous memory beyond the cache budget", and it flags **"UNKNOWN: whether it is only macOS accounting (F_NOCACHE staging)"**.
- **Why the two numbers disagree:**
  - macOS "peak memory footprint" counts dirty anonymous memory *including compressed pages*, plus some kernel-side buffers.
  - BigMoeOnEdge serves direct reads on macOS with `F_NOCACHE` ("macOS … has no O_DIRECT; a direct request is served with F_NOCACHE instead", [README](https://github.com/Helldez/BigMoeOnEdge#readme), accessed 2026-10-02). Linux/Android uses O_DIRECT.
  - Android's low-memory killer acts on the app's resident anonymous memory plus zram swap (PSS). That is closer to RSS than to macOS footprint, but RSS hit 8.7 GiB on one prompt, so the risk is real either way. **UNKNOWN until measured on Linux.**
- Per-layer expert bytes: 9.80 GiB / 40 layers ≈ **0.245 GiB per layer** (UD-Q2_K_XL). Short prompts route about half of each layer's experts (BigMoeOnEdge v0.28 release notes, Qwen3.6-35B-A3B, 130–480 tokens, top-4).

## 2. Cheap desktop probe P0: is the peak real outside macOS? (no engine change; run-ready)

- **Goal:** decide before any engine PR. ≈ 1–2 h on the Mac mini, no download (the 35B and `<runner>/spikes/bmoe` are there). Docker Desktop is needed for P0b; UNKNOWN whether the mini has it.
- **P0a, macOS, current upstream engine, Android-like knobs.**
  - Rebuild BigMoeOnEdge at **v0.28.0** (Kiln's build is 74ba18f ≈ v0.22). The ~6 releases since include `--ubatch` and dense-policy changes.
  - Re-run the same 10 deep prompts with the Android app's defaults: `--moe-stream --overlap --dense-weights anon --cache-mb 1500 --ubatch 512 -t 4 --no-think`.
  - Record both `peak memory footprint` and `maximum resident set size` (`/usr/bin/time -l`), plus BigMoeOnEdge's own `rss_anon_mib` telemetry (ADR §7 criterion 4 names it).
- **P0b, Linux with a hard memory cap (the LMK proxy).**
  - Run the same binary, built for Linux, in a container with **`--memory=8g --memory-swap=8g`** (no swap beyond the cap) on the same 10 prompts. Record `memory.peak` from cgroup v2 and any OOM kill.
  - If all 10 complete without OOM and `memory.peak` ≤ 8 GiB, the macOS number was accounting, the phone is likely fine, and T2 is not needed for the 12 GB tier.
  - Caveat: Docker on macOS runs a Linux VM, so file I/O goes through virtiofs and **speeds are meaningless**. Memory accounting is Linux's, which is the point.
- **Coordinator addition (2026-10-02, before the run):** if P0b fails at 8 GiB, also record **descriptive** P0b points at `--memory=9g` and `10g`. They locate the real Linux peak and are not part of the pass/fail reading below.
- **Frozen reading (stated before any run):**
  1. **P0b passes** (10/10 complete, cgroup `memory.peak` ≤ 8 GiB, 0 OOM): T2 not needed. Re-score deep35 criterion 6 as PASS-on-Linux, and move the deep tier to the device step (ADR §7: peak PSS ≤ 8 GB on a real 12 GB Android).
  2. **P0b fails, but P0a's RSS ≤ 8 GiB with `--cache-mb 1500`:** the cache budget is the lever. Re-run P0b at cache 1000/1500 before any code.
  3. **Both fail:** the union is real, so T2 (§3).

## 3. T2: what exactly changes (only if P0 says the union is real)

- **The change:** during CPU prefill (graph width > 1), fetch each layer's **routed** experts into **two layer-sized slots** (double-buffered: load layer L+1 while computing L), instead of staging every fetched slice for the whole prompt.
  - BigMoeOnEdge already does exactly this for the NPU prefill: "two layer-sized slots are filled from flash while it computes the other one" (v0.26.0). Since v0.28 it reads only routed experts per layer, "the output is bit for bit the same" ([v0.28.0 release](https://github.com/Helldez/BigMoeOnEdge/releases/tag/v0.28.0), [docs/npu-prefill.md](https://github.com/Helldez/BigMoeOnEdge/blob/main/docs/npu-prefill.md)).
  - So T2 means giving the **CPU** prefill path the same arena: a "CPU prefill device" or a flag. It is not new machinery.
- **Expected peak:** dense 1.63 GiB + 2 slots ≈ 0.49 GiB (2 × 0.245; less when only routed experts are read) + expert LRU cache (1.5–3.0 GiB, configurable) + KV/compute (≈ 0.1–0.3 GiB at ubatch 512 / ctx 4096) ≈ **3.7 GiB (cache 1500) to 5.4 GiB (cache 3000)**. Under the 8 GiB bar either way, assuming the arena's slots are the only prefill staging.
- **Effort:**
  - Upstream: an issue/PR in BigMoeOnEdge. Its author ships near-daily (v0.25–v0.28 between 2026-09-28 and 09-29) and wrote the NPU arena, so a CPU variant is plausibly days. **UNKNOWN; we can't commit their time.**
  - Ourselves: a fork patch in the bmoe core (~11k lines C++, Apache-2.0), reusing the arena code. **M, ≈ 3–5 days** including the byte-identity gates (`ctest`, streamed == resident).
- **Risks:**
  1. The arena is coupled to the device backend's buffer rebinding ("weights are rebound between graphs"), so a CPU variant may need different plumbing (UNKNOWN effort).
  2. Prefill gets slower if slot loads cannot overlap compute on 4 big cores. The NPU numbers don't transfer.
  3. Even with T2, the deep tier still needs engine option B in the app (bmoe subprocess, ~1–2 weeks; deep card §5). **T2 does not shorten that path**, and the Oct 22 code freeze is the binding constraint.

## 4. Frozen criterion for T2 (if built)

- Same 10 deep prompts, same file, on the T2 build:
  - **P0b protocol** (Linux cgroup 8 GiB): 10/10 complete, `memory.peak` ≤ 8 GiB, 0 OOM;
  - **bit-identical outputs** vs the current CPU path on all 10 at temp 0;
  - prefill time ≤ 1.3× the current CPU path (macOS, same host).
- Then the ADR §7 device criteria on a real 12 GB Android: TTFT p50 ≤ 15 s, total ≤ 60 s, ≥ 4 tok/s sustained, 0 LMK kills in 10 answers.

## 5. Recommendation

- **Run P0 first. It costs hours, not days, and may make T2 unnecessary.** The 4.0–8.7 GiB RSS beside the 10 GiB footprint is the reason to expect that the macOS number overstates the Linux one.
- If P0 says T2 is needed, ask upstream first, with P0's numbers as the issue body. A fork patch only if they decline.
- In all cases, the deep tier ships only behind "go deeper", with its time shown, and its ratio is reported separately (r4to).

UNKNOWN:
- whether the mini has Docker for P0b (an alternative is any Linux box with cgroup v2);
- what in the v0.22 CPU path holds the union (cache, scratch or page cache);
- the effort and willingness for an upstream CPU arena;
- Android LMK's exact accounting for the bmoe subprocess (PSS incl. zram).

Shelf: row "BigMoeOnEdge" in `../../SHELF.md`.

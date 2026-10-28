# 7 · A phone on a desk, and in a hand

> Closed record · research record 1.0 · as of 2026-10-28; the author closed the research lines on 2026-10-23. Current standing, not a final result: Open fronts: https://r4topunk.github.io/boar-research/data/status.json.
>
> Final · as of 2026-10-28 · 0 of 71 wins on the phone, U-total 0.165 (Claude) / 0.242 (gpt-5.6-sol), below the 0.50 bar

- Page: https://r4topunk.github.io/boar-research/research/phone/ · Markdown twin: https://r4topunk.github.io/boar-research/research/phone.md · Whole paper: https://r4topunk.github.io/boar-research/llms-full.txt · Index: https://r4topunk.github.io/boar-research/llms.txt
- Span: 2026-10-02 → 10-22

**In one sentence.** The desktop stand-in was trustworthy for answer quality, and the frozen build matched it on real phones, but the phone exposed bugs and memory limits the desktop hid. The deep tier never ran on a phone (the author dropped it from delivery on 2026-10-21); the 8 GB phone runs of 10-20/21 changed the main engine (chapter 11).

## For curious readers {#curious}

#### Testing on a desk

Running a test on a phone takes hours. Running the exact same code on a desktop takes minutes. We did most of the work on the desktop, and then checked it was telling the truth.

#### The phone fights back

A phone gets hot, runs short of memory and hides different bugs. On one 8 GB phone the model was killed while loading because a speed trick quietly made a second copy of its weights. On another, every question re-read the whole prompt because of a bug in our own code that the desktop could not show.

#### Same answers, slower

On a real phone, the frozen build on a 12 GB-class phone in airplane mode answered all 72 test questions and scored exactly what the desktop scored: 0.529 and 0.529. A typical answer took about 31 seconds.

*Badge:* v0.1 public practice set · Claude Haiku triage judge · 57 graded questions · 1 run.

#### The big model has not been on a phone

The 35-billion-parameter model never ran on a phone. A technique that streams the model's experts from storage kept its working memory under 3 GB on a desktop, and was even built for Android, but nobody measured it on a phone before the big model was dropped from the plan.

**In one sentence card:** "The phone matches the desktop on quality; it is just slower, and the big model never left the desktop."

*Facts: [F-686] [F-710] [F-023] [F-771] [F-036] [F-793] [F-2118] [F-1532]*

## For tech people {#tech}

### Same quality as the desktop, 3.4× slower, 4.2 GB after load

We trusted the desktop only after phones agreed with it. Cut 7 on a 12 GB-class phone (MediaTek MT6897, 10.7 GiB usable, Android 16, airplane mode, no INTERNET permission) answered 72/72 with 0 timeouts. Tier routing matched 60/60, instant answers were byte-identical 16/16, kept source titles matched 59/60, and model text was identical on 3/44 (sampler differences). Quality on the 57 public v0.1 items under the Haiku L1 judge: raw 0.529 (0.481–0.575) on the phone vs 0.529 on desktop; paired −0.000 (−0.026…+0.028). Fast tier: p50 30.7 s, p90 48.4 s, TTFT p50 18.5 s, decode 5.5 tok/s, output p50 64 tokens. Memory: PSS 5.88 GB peak during model load, then p50 3.64 GB, max 4.23 GB. Thermal status stayed 0.

**Gotcha boxes:**
- **ARM weight repack.** llama.cpp's repack copied ≈ 2.3 GiB of weights into anonymous memory and the OS killed the 4B on an 8 GB phone while loading; disabling it dropped desktop max RSS 5.1–5.4 → 3.41 GB. The fix (repack-aware fit, Android only) is not in the frozen build [F-691] [D-024].
- **The desktop shim hid our own bug.** A KV-cache session save path was a no-op on desktop, so every phone question re-prefilled ≈ 430 + 300 tokens (35–41 s + 20–28 s) [F-715] [D-034].
- **q8_0 KV cache** is non-inferior (Δ −0.0077, −0.0232…+0.0062) and halves reader KV 576 → 306 MiB [F-716].
- **Pure-JS zstd** was ≈ 76 % of retrieval time on the phone; native zstd ≈ 80× faster [F-1141].

### Never run on a phone: two engines, one projection, an Android build that was not measured

The deep tier only ever ran on desktops. Two on-device paths were tested there. bmoe, a streamed-MoE engine, is not token-identical to llama-server (greedy 0/10) but judged-equivalent on identical contexts (0.623 vs 0.634, Δ −0.012, CI −0.045…+0.020; v0.1 dev, n 57, 1 seed, Opus); its macOS session peaked at 11.7 GiB. An expert-streaming fork (LES) runs the same 35B at 14–17 tok/s with 2.75–2.81 GiB peak RSS on an M4 desktop CPU with experts read from SSD and page cache, and is judged-equivalent too (0.625 vs 0.634, Δ −0.010, CI −0.042…+0.018). On a phone it would be flash-bound: about 320 expert reads and 314 MiB per token, so roughly 4 tok/s on UFS 3.1 and 6 tok/s on UFS 4.0 including compute (I/O-only upper bounds 4.8 / 8.0). Using third-party public phone rates, a deep + 512-thinking answer would take about 1.9–2.8 minutes on a Pixel 8 Pro CPU. None of this was measured on a phone. The expert-streaming engine was cross-built for Android arm64 on 2026-10-19 [F-2118], and then the author's 2026-10-21 decision (no 35B deep mode, [D-147]) dropped both phone fronts (OF-1, OF-2 in `data/status.json`). The projection stays a projection.

*Facts: [F-037] [F-740] [F-036] [F-795] [F-793] [F-766]*

### 1.7B for small phones: faster, safe-routed, weaker reader (the 10-16 lite-tier view; superseded by T14)

For 4–6 GB phones we tested Qwen3-1.7B (1.1 GB file, RSS ≈ 2.3 GB vs ≈ 4.0 GB for the 4B; desktop prefill 2.5× and decode 2.2× faster) behind the same safety engine; health routing matched the 4B 124/124. With X2b it matches the plain 4B only on pack-matched dev items (−0.007, −0.031…+0.018, Haiku); on the claim kit it is 0.111 below the 4B and X2b is inert there; at identical contexts it reads worse (−0.070, −0.094…−0.044, n 97). Phone speed for the lite tier was unmeasured as of 2026-10-17; on 2026-10-20 the 1.7B became the main 8 GB engine on measured phone speed (T14). Separately, long sessions do not degrade the 4B: turns 6–15 score 1.136 (0.993–1.320) of BOAR's own standalone answers (Haiku L1, 80 agent-written questions), but latency grows to about 22 s at turns 14–15 vs 8 s standalone on desktop.

*Facts: [F-1083] [F-1084] [F-390] [F-1081] [F-030] [D-113]*

## For AI professionals {#ai}

### The record for this chapter

**Key facts:**
- The 4B was killed by the OS on an 8 GB Android while loading: ARM weight repack copied ≈ 2.3 GiB into anonymous memory [F-686] [F-691].
- iPhone 13 run matched the desktop proxy (0.394 vs 0.395) [F-684].
- First real-phone run: our own KV-cache save-path bug re-prefilled the prompt every question (≈ 55–65 s), hidden by the desktop shim [F-710] [F-715].
- Cut 6 on an 8 GB Galaxy A15: 73/73; phone 0.561 (0.507–0.617) vs desktop 0.558/0.560; v0.1 dev, n 57, Opus judge.v1-med [F-024].
- Cut 7 on a 12 GB-class phone (POCO X6 Pro, 10.7 GiB usable, Android 16, airplane, no INTERNET permission): 72/72; raw 0.529 (0.481–0.575) = desktop 0.529, floor-adj 0.403 vs 0.402, paired −0.000 (−0.026…+0.028); v0.1 public dev, n 57, Haiku L1 judge; fast-tier p50 30.7 s, TTFT p50 18.5 s, decode 5.5 tok/s; PSS 5.88 GB peak during load, ≤ 4.23 GB after [F-023] [F-771] [F-772].
- The A15 and X6 ratios are not comparable in level (different judges) (group-A §4).
- Deep tier on a phone: never run (as of 2026-10-24; OF-1 dropped by the author's 2026-10-21 decision, [D-147]). Projection 1.9–2.8 min per answer at budget 512 on a Pixel 8 Pro CPU, from third-party public rates and our arithmetic [F-766]. Earlier (10-09) estimate was 3.5–5 min at budget 1024 (group-B row 6).
- Expert streaming fork on desktop CPU: 14–17 tok/s at ≈ 2.8 GiB RSS, judged-equivalent (0.625 vs 0.634, Δ −0.010, CI −0.042…+0.018, v0.1 dev, 1 seed, Opus). Desktop only; flash-bound projection ≈ 4 tok/s (UFS 3.1) / ≈ 6 tok/s (UFS 4.0) with compute [F-036] [F-036] [F-793]. Cross-built for Android arm64 on 2026-10-19; phone speed and memory never measured ([F-2118];; OF-2 dropped).
- 8 GB phone (Pixel 8a, bench app, 2026-10-20/21): the 4B at 29–46 s per answer and one low-memory kill; the 1.7B at 13–16 s; this is chapter 11 [F-1418].
- Long sessions: no quality drop out to turn 15 (turns 6–15 in-session/standalone 1.136, 0.993–1.320; reference = BOAR's own standalone answer, Haiku L1, 80 agent-written questions); latency grows to ≈ 22 s at turns 14–15 vs ≈ 8 s standalone [F-030] [F-895].

**Key decisions:** [D-024] (repack-aware memory fit, Android only), [D-034] (KVFIX), [D-035] (no-network APK by construction), [D-046] / [D-053] ("no device exists", 10-07; reversed in practice 10-14), [D-119] (expert streaming supersedes earlier loader ideas on paper).

**Turning point:** 2026-10-14 19:26, DEVICE-X6: the frozen build on a 12 GB-class phone gives the same judged quality as the desktop.

### Device parity and speed

The frozen build (cut 7) on a 12 GB-class phone (MediaTek MT6897, 10.7 GiB usable, Android 16, airplane mode, no INTERNET permission) answered 72/72 items; on the 57 judged public v0.1 items, judged by Haiku L1, phone raw 0.529 (0.481–0.575) equals desktop 0.529, floor-adjusted 0.403 vs 0.402, paired −0.000 (−0.026…+0.028). Routing tier matched 60/60 and instant answers were byte-identical 16/16; model text was identical on 3/44 items (sampler differences). Earlier, cut 6 on an 8 GB phone scored 0.561 (0.507–0.617) vs desktop 0.558/0.560 under Opus judge.v1-med; the two phone studies are not comparable in level. Phone fast-tier p50 is 30.7 s (desktop 7.5 s on an M1 Pro; ×3.4); PSS peaks at 5.88 GB during load and stays ≤ 4.23 GB after. The deep tier never ran on a phone and was not delivered (author, 2026-10-21; [D-147]); two on-device engines are judged-equivalent to the desktop server on identical contexts (bmoe −0.012, −0.045…+0.020; expert streaming −0.010, −0.042…+0.018; v0.1, 1 seed, Opus), and a deep + 512 answer is projected at ≈ 1.9–2.8 min on a Pixel 8 Pro CPU from third-party rates.

*Facts: [F-037] [F-036] [F-793] [F-766] [F-023] [F-771] [F-772] [F-773] [F-024] [F-775] [F-776] [F-777] [F-778] [F-779] [F-780] [F-781]*

### Multi-turn and lite tier

Over 10 five-turn sessions and a 15-turn extension (80 agent-written questions, Haiku L1, reference = the system's own standalone answer, not the frontier), in-session answers score 1.136 (0.993–1.320) of standalone on turns 6–15; latency rises to ≈ 22 s at turns 14–15 vs ≈ 8 s. A 1.7B lite reader with X2b equals the plain 4B only on pack-matched items (−0.007, −0.031…+0.018); on the claim kit 1.7B − 4B = −0.111, and at identical contexts the 1.7B reads worse (−0.070, −0.094…−0.044, n = 97). An earlier internal summary ("the lite gap is reach, not reading") was retracted on this evidence. §6.8 reports the 1.7B as main engine from 2026-10-20.

*Facts: [F-916] [F-030] [F-1081] [F-1082] [F-1279] [D-113]*

## Facts cited {#facts}

Resolve every [F-…] marker in https://r4topunk.github.io/boar-research/data/facts.json. Each line gives the claim, the number with its metric family, set and status, judge, n, seeds, CI, date and caveat.

<!-- lint:exempt:start -->
- [F-023] On a real 12 GB-class phone, in airplane mode, the frozen build gives the same judged quality as on the desktop. phone raw 0.529 (0.481–0.575) vs desktop 0.529; floor-adjusted 0.403 vs 0.402; paired −0.000 (−0.026…+0.028); 72/72 answered; fast-tier p50 30.7 s; app memory (PSS) peak 5.88 GB during model load, then ≤ 4.23 GB (judge.v1 ratio) · set v0.1 (public dev, development data) · judge Claude Haiku 5.5-low (L1 triage judge, N = 4, both orders) · n 57 · seeds 1 run · CI paired 95 % bootstrap · date 2026-10-14 · caveat: Haiku-judged level; not comparable with Opus-judged ratios. The device has 10.7 GiB usable RAM.
- [F-024] Earlier, on an 8 GB phone, cut 6 also matched the desktop. phone 0.561 (0.507–0.617) vs desktop 0.558 / 0.560; 73/73 answered; PSS max 4.41 GiB · set v0.1 (public dev, development data) · judge Claude Opus (judge.v1-med) · n 57 · seeds 1 run · CI 95 % item bootstrap · date 2026-10-06 · caveat: Opus-judged; not comparable in level with the Haiku-judged 12 GB-class run.
- [F-030] Long conversations do not degrade answers up to turn 15. turns 6–15, in-session vs standalone: 1.136 (0.993–1.320); self-contained items 1.017 (0.950–1.095); latency ≈ 22 s vs 8 s at turns 14–15 · set LONGSESSION dev sessions (dev (agent-written), development data) · judge Claude Haiku 5.5-low (L1 triage judge, N = 4, both orders) · n 80 agent-written questions · seeds 1 · CI 95 % bootstrap · date 2026-10-14 · caveat: The reference here is BOAR's own standalone answer, not the frontier reference: a ratio of ratios, not a bar number.
- [F-036] An expert-streaming engine runs the 35B model in under 3 GiB of RAM on a desktop CPU with judged-equivalent answers. judged 0.625 vs llama-server 0.634, paired −0.010 (−0.042…+0.018); RSS 2.75–2.81 GiB; 14–17 tok/s on the Mac mini CPU; 10/10 greedy-identical vs the fork base · set v0.1 (public dev, development data) · judge Claude Opus (judge.v1, both orders) · n 57 (R450 contexts) · seeds 1 · CI paired 95 % bootstrap · date 2026-10-16 · caveat: Desktop only, experts read from a fast SSD and page cache; phone flash speed is unmeasured (analytic bound ≈ 4–6 tok/s with compute).
- [F-037] The on-device MoE engine (bmoe) is not token-identical to the desktop server but is judged equivalent on identical contexts. 0.623 vs 0.634, Δ −0.012 (−0.045…+0.020); greedy token-identical 0/10 · set v0.1 (public dev, development data) · judge Claude Opus (judge.v1, both orders) · n 57 · seeds 1 · CI paired 95 % bootstrap · date 2026-10-07 · caveat: An equivalence, not a lever: lets desktop deep-tier numbers transfer to a bmoe device plan with this caveat.
- [F-390] Lite tier safety. health routing identical to 4B 124/124; model answers alone 3/64 health probes; unsafe 1 vs 1 · set agent-written probes + v0.1 (status UNKNOWN) · judge jev + rules · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-16 · caveat: claim kit only, one seed
- [F-684] The desktop proxy matched a real iPhone 13 run. 0.394 vs 0.395; Δ −0.001 · set v0.1 dev (dev, development data) · judge Opus · n UNKNOWN · seeds UNKNOWN · CI (0.353–0.441), MDE 0.038, 2 reps · date 2026-10-02 · caveat: a second Claude-family judge agreed (same winner 99 %, κ 0.894) QUEUE:249
- [F-686] On an 8 GB Android the 4B was killed by the OS while loading; ARM weight repack copied ~2.3 GiB into anonymous memory. RSS 4.7–5.0 GiB at kill · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI 2 reproductions · date 2026-10-02 · caveat: debug build; fix tested on desktop only (anon 3.25 → 0.88 GB)
- [F-691] The 4B weight repack on ARM duplicates ~2.3 GiB in anonymous memory. Probe A: anon 3.25 → 0.88–0.91 GB, max RSS 5.1–5.4 → 3.41 GB with no-repack · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-02 · caveat: macOS desktop probe
- [F-710] Most phone latency came from a KV-session save bug in OUR patch (desktop shim no-op hid it); ~55–65 s re-prefill per answer. 55–65 s · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-05 · caveat: not an upstream bug
- [F-715] KV-cache save bug cost on the A15. gate prefix 35–41 s + answer prefix 20–28 s re-prefilled per question at ~12 tok/s; fix est. −55 to −65 s · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-05 · caveat: our own regression, not upstream (QUEUE:649)
- [F-716] q8_0 KV cache is non-inferior on quality. Δ −0.0077 (−0.0232…+0.0062); reader KV 576 → 306 MiB · set v0.1 dev (dev, development data) · judge Opus · n 60 · seeds 2 · CI n 60 × 2 seeds · date 2026-10-05 · caveat: desktop slower; device-day candidate only | device candidate
- [F-740] bmoe desktop speed and memory. prefill 25.7 s median, decode 8.6 tok/s, session peak 11.7 GiB on macOS (Linux anon 4.0–4.4 GiB) · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-07 · caveat: accounting differs by OS
- [F-766] Deep + think 512 on a Pixel 8 Pro CPU is projected at 1.9–2.8 min per answer. 1.9–2.8 min · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI from published third-party rates · date 2026-10-12 · caveat: not our measurement; deep tier never ran on a phone
- [F-771] Phone speed (cut 7, POCO X6 Pro, MT6897, 10.7 GiB) fast tier p50 30.7 s / p90 48.4 s; TTFT p50 18.5 s; decode 5.5 tok/s; all 72 p50 24.7 s · set v0.1 public (public dev, development data) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI 72/72 answered · date 2026-10-14 · caveat: airplane mode, no INTERNET permission
- [F-772] Phone memory (cut 7) PSS peak 5.88 GB at load, then p50 3.64 / max 4.23 GB · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-14 · caveat: thermal status 0 over 29 min
- [F-773] Phone vs desktop speed ratio. total p50 28.3 s vs 7.5 s (×3.4); decode 5.6 vs 22.6 tok/s (judge.v1 ratio) · set v0.1 (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI 60 ids · date 2026-10-14 · caveat: desktop = MacBook M1 Pro
- [F-775] Cut 7 on the POCO X6 Pro (MT6897, 10.7 GiB, Android 16, airplane, no INTERNET permission). 72/72 success, 0 timeouts, logcat clean · set v0.1 public + safety (public dev, development data) · judge UNKNOWN · n 72 · seeds UNKNOWN · CI n 72 + warm-up · date 2026-10-14
- [F-776] X6 fast-tier latency. total p50 30.7 s, p90 48.4 s, max 53.0 s; TTFT p50 18.5 s; decode p50 5.5 tok/s (4.6–7.4); output p50 64 tokens · set v0.1 (status UNKNOWN) · judge UNKNOWN · n 51 · seeds UNKNOWN · CI n 51 fast · date 2026-10-14
- [F-777] X6 instant tier. p50 0.1 s, p90 11.2 s; 21 instant (guard 12, extractive 4, places 3, calculator 2) · set v0.1 (status UNKNOWN) · judge UNKNOWN · n 21 · seeds UNKNOWN · CI n 21 · date 2026-10-14
- [F-778] X6 memory. PSS peak 5.88 GB during model load, then p50 3.64 / p90 3.80 / max 4.23 GB · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-14
- [F-779] X6 thermal. battery max 41.7 °C, thermal_status 0 throughout · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-14 · caveat: charging during run
- [F-780] X6 parity with desktop. tier 60/60, instant 16/16 byte-identical, kept titles 59/60, 4B text identical 3/44 (sampler differences); phone 3.4× slower (decode 22.6 vs 5.6 tok/s) · set v0.1 (status UNKNOWN) · judge UNKNOWN · n 60 · seeds UNKNOWN · CI n 60 · date 2026-10-14
- [F-781] X6 judged quality: device = desktop. raw 0.529 (0.481–0.575) vs 0.529 (0.484–0.575); floor-adj 0.403 vs 0.402; paired −0.000 (−0.026…+0.028); win/tie/loss 2/1/54 vs 1/2/54 (judge.v1 ratio) · set v0.1 public (dev) (public dev, development data) · judge Haiku L1 · n 57, · seeds UNKNOWN · CI n 57, 1 run · date 2026-10-14 · caveat: Haiku vs A15's Opus: levels not comparable
- [F-793] LES (expert streaming) on a phone is projected at ≈ 4 tok/s (UFS 3.1) to ≈ 6 tok/s (UFS 4.0) including compute; analytic, unmeasured. with compute ≈ 4 tok/s (UFS 3.1) and ≈ 6 tok/s (UFS 4.0); I/O-only upper bounds 4.8 / 8.0 tok/s · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI analytic · date 2026-10-16 · caveat: '6-8' mixes the compute-included estimate with the I/O-only bound; analytic, unmeasured
- [F-795] Phone flash bound for expert streaming. 320 expert reads/token, 314 MiB/token, 0 cache hits → ≈ 4 tok/s (UFS 3.1) to ≈ 6–8 tok/s (UFS 4.0) · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI analytic · date 2026-10-16 · caveat: not measured on a phone
- [F-895] Long-session latency grows with history. ≈ 22 s at turns 14–15 vs ≈ 8 s standalone (desktop); prompt +74 tokens/turn; 4,096-token context crossed at ≈ turn 50 · set dev (dev, development data) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI 3 sessions · date 10-14 · caveat: adapter passes all turns; the app keeps 6 messages + summary from turn 8 (turns 5–7 gap)
- [F-916] Multi-turn sessions do not degrade answers over 5 turns. turns 2–5 ratio in-session/standalone 1.397 (1.187–1.673); drift +0.537 (+0.208…+1.155) (judge.v1 ratio) · set agent-written dev (dev, development data) · judge Haiku L1 · n UNKNOWN · seeds 1 · CI 10 sessions × 5 turns; 1 seed · date 2026-10-14 · caveat: citation fix (l.3 is the health caveat). Reference = BOAR's own standalone answer, not frontier; drift is a difference of ratios
- [F-1081] 1.7B + X2b vs plain 4B on pack-matched items. −0.007 (−0.031…+0.018) · set 180 self-tests dev (dev, development data) · judge Haiku · n 180 · seeds UNKNOWN · CI n 180 · date 2026-10-16 · caveat: does NOT hold on the kit: 1.7B − 4B −0.111 (−0.191…−0.047)
- [F-1082] Lite gap persists with identical contexts. 1.7B X2b − 4B X2b −0.070 (−0.094…−0.044) · set 180 self-tests dev (dev, development data) · judge Haiku · n 97 · seeds UNKNOWN · CI n 97 · date 2026-10-16 · caveat: contradicts "gap is reach, not reading" | contradicts the earlier "reach, not reading" summary
- [F-1083] Lite tier (Qwen3-1.7B Q4_K_M) footprint and speed. file 1,107,409,472 B; RSS ≈ 2.3 GB (peak 2.7) vs ≈ 4.0 GB 4B; desktop prefill 2.5×, decode 2.2× the 4B · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-16 · caveat: ≈ 1.2× faster with X2b at matched quality; phone unpriced
- [F-1084] Lite tier quality, correctly scoped. 1.7B + X2b vs plain 4B −0.007 (−0.031…+0.018) on 180 self-tests; on the claim kit 1.7B − 4B = −0.111 and X2b inert; at identical contexts −0.070 (−0.094…−0.044) · set 180 self-tests (dev) / claim kit (dev, development data) · judge Haiku · n 180 · seeds UNKNOWN · CI n 180 / n 97 · date 2026-10-16 · caveat: "1.7B = 4B" holds only on pack-matched dev items
- [F-1141] Retrieval JS on the phone: pure-JS zstd decompression ~76 % of retrieval time; native zstd ~80× faster. 499 ms of 677 ms · set UNKNOWN (status UNKNOWN) · judge n/a · n UNKNOWN · seeds UNKNOWN · CI 68 calls · date 2026-10-02 · caveat: led to native zstd arm (device-only gains)
- [F-1279] Retracted summary: "the small-model gap is reach, not reading" at identical contexts 1.7B − 4B = −0.070 (−0.094…−0.044) · set 180 self-tests (dev) (dev, development data) · judge Haiku · n 97, · seeds 1 · CI n 97, 1 seed · date 2026-10-16 · caveat: retracted in QUEUE l.1267
- [F-1418] Pixel 8a speed, 1.7B vs 4B. 1.7B 13-16 tok/s, answers 13-16 s; 4B 3.6-6 tok/s, 29-46 s; 4B LMK kill at 4.4 GB RSS · set public dev questions (dev, development data) · judge timing · n UNKNOWN · seeds UNKNOWN · CI 9-question runs · date 10-20 · caveat: 4B 73/73 only after a reboot | VERIFIER NOTE: Pre-BATCHRET, 9 public dev questions; not comparable with the 73-question p50 of 10-21.
- [F-1532] 35B deep mode not delivered; deep tier appears only as roadmap with desktop numbers. stood · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-21 · caveat: who decided: author (GRILL); why: focus on 8 GB UX; no Android expert-streaming build; alternatives: 12 GB deep tier; reversible: yes
- [F-2118] Expert-streaming engine cross-built for Android. builds; phone numbers unmeasured · set UNKNOWN (status UNKNOWN) · judge UNKNOWN · n UNKNOWN · seeds UNKNOWN · CI not computed · date 2026-10-19 · caveat: no phone run in this slice

<!-- lint:exempt:end -->
### Decisions cited {#decisions}

<!-- lint:exempt:start -->
- [D-024] 2026-10-02 · Make the memory-fit estimate repack-aware and load with no_extra_bufts on Android only · why: repack copied ~2.3 GiB of weights into anonymous memory and the phone killed the 4B. · status: kept
- [D-034] 2026-10-05 · Fix the KV session save path (KVFIX) and block fragment/figurative instant answers (INSTANT-FRAG) → cut 4 · why: A15 smoke: every question re-prefilled the prefixes; "capital of France" answered with a Lyon fragment. · status: kept
- [D-035] 2026-10-05 · Bench APK with INTERNET permission removed (no-network by construction) · why: prove offline operation statically. · status: kept
- [D-046] 2026-10-07 · Cut 7 = cut 6 + FACTS r6 (adopted on gates: 0 fires on held-out sets); no relaxed lowercase rule; fine-tune data 1k go; "no device exists" · why: deterministic facts lever; no phone. · status: kept
- [D-053] 2026-10-07 · "No device exists": device tasks dormant · why: No 12 GB phone available. · status: reversed (A 12 GB-class phone (10.7 GiB usable) ran cut 7 on 2026-10-14.)
- [D-113] 2026-10-16 · Apply the adversarial critique: lite "= 4B" only on pack-matched dev; one-seed V-para noise rule 0.03 → 0.05; n≈20 closures relabelled "not detected at MDE 0.08 · why: over-stated internal summaries. · status: kept
- [D-119] 2026-10-16 · Expert streaming (LES fork) supersedes earlier loader/kernel candidates on paper for a deep-tier device plan · why: 2.8 GiB RSS, judged parity. · status: kept
- [D-147] 2026-10-21 · 35B deep mode not delivered; deep tier appears only as roadmap with desktop numbers · why: focus on 8 GB UX; no Android expert-streaming build. · status: kept

<!-- lint:exempt:end -->
---

Cite as: r4to, independent researcher. RatLab — A Boar Research (2026), research record 1.0, as of 2026-10-28. Text and data CC BY 4.0. Fact ids or a link must travel with a quote. How to cite: https://r4topunk.github.io/boar-research/cite/ · https://r4topunk.github.io/boar-research/CITATION.cff.

AI-reviewed, not clinically reviewed. Nothing here is medical advice.

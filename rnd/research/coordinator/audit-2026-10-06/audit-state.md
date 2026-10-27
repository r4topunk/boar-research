# BOAR state audit (poidh #31), 2026-10-06 13:57

Scope: everything in `rnd/research/coordinator/` (no .patch content; one `grep -c` + `shasum` on the cut 6 patch to confirm lineage), `deep/RESUME.md`, `rnd/research/BOUNTY-BOARD.md`, `SUMMIT.md`, `CLAIMS_31.md`. I also read the last 60 lines of `rnd/research/QUEUE.md`, a few deep-tier QUEUE lines, `BOUNTY_31.md`, and the README of the cloned a competitor team repo (`competitors/a competitor team/README.md`). I read those because DEVICE-DAY only holds procedures; the device results are logged in QUEUE. I did not open `blind/`.

Paths are relative to `<workspace>/`, and `coord/` = `rnd/research/coordinator/`.

---

## 1. CURRENT STATE

**Verdict.** The ship candidate is now **cut 6**, not cut 2. Cut 6 = patch `coord/arms/detfu/detmax-on-cut4.vs-0cfd4a77.patch`, sha256 `824e0b35…`, tree `b0f53fe0…`, and it is frozen as the claim and device build. The only held-out number is from **cut 3**: 0.513 (0.479–0.550), which is +0.011 over the cut 2-era ship stack. That gain is inside noise (CI contains 0, below the MDE of 0.018). Cuts 4–6 give byte-identical v0.1 answers to cut 3, so they are not expected to move it. No 12 GB phone has run anything. All device data comes from an 8 GB Galaxy A15: decode 2–3 tok/s, model answers take about 1–2.5 min.

### Identity
| Item | Value | Evidence |
|---|---|---|
| Ship candidate | cut 6 = cut 5 + DETMAX (fire if window OR current turn alone ≥ threshold) | coord/CLAIM-RUNS-cut6.md:3,5; coord/DEVICE-DAY.md:167-169; QUEUE.md:694,701 |
| Patch / tree | `arms/detfu/detmax-on-cut4.vs-0cfd4a77.patch` sha `824e0b35fcdf…` (re-hashed now: matches); tree `b0f53fe0d30a…` | CLAIM-RUNS-cut6.md:5; DEVICE-DAY.md:169 |
| Lineage check | The patch name says "on-cut4", but it does contain the cut 5 code: the `no-source prefix restored` string is present once, and `skip-rules` 3×. So cut 6 ⊃ cut 5 | grep -c on the patch (this audit) |
| Device APK | `bench-app/build/boar-bench-0cfd4a77-cut6-nonet-sweep-b0f53fe0d30a.apk`, sha `cca28caf…`, no INTERNET permission, **nothing installed** | DEVICE-DAY.md:167,169 |
| Freeze rule | Only routing/safety fixes that leave v0.1 answers unchanged may be added. Answer-changing arms are out | CLAIM-RUNS-cut6.md:3 |

### Scores
| Set | Latest measured | Cut measured on | Evidence |
|---|---|---|---|
| v0.1 EN (dev, 57 judged) | 0.5591 (s44 0.5585, s45 0.5596) for cut 4. This equals cut 5 and cut 6 on v0.1 (byte-identical answers). Cut 3 on the same texts was 0.5656; the difference is judge-sampling noise | CUT5-LOSS-REFRESH.md:6,75; cut3-confirm.md:39; QUEUE.md:676 |
| v0.2 held-out (110) | **0.513 (0.479–0.550)**; floor-removed 0.389; above-decline 0.299 | cut 3 | CLAIM-RESULTS-cut3.md:24 |
| v0.2 held-out, cut 6 | **UNKNOWN**. The run is authorised and frozen, but no `CLAIM-RESULTS-cut6.md` exists yet | — | CLAIM-RUNS-cut6.md:8-17; QUEUE.md:700 |
| V-para (51 judged) | 0.413 (0.384–0.445), FAIL. Venues 0/7 | cut 3 | CLAIM-RESULTS-cut3.md:57,63 |
| V-exact (5 judged + venues) | Aggregate on cut 2: 0.510 (plain CI 0.303–0.739, n=5). Per item on cut 3, byte-identical to cut 2: Japan 0.367, PQ 0.533, Mozi 0.543, Gríma 0.200, Paris–Rome 0.893. Venues 6/6, GPS city 3/3. Cut 3 aggregate: UNKNOWN. Cut 5/6: UNKNOWN (only INSTANT-SUBJ reports "0 changes on V-exact") | cut 2/3 | BOUNTY-BOARD.md:12; cut3-confirm.md:46-56; QUEUE.md:647 |
| Frontier ladder (V-para, no web) | Haiku 0.588, Sonnet 0.961, Opus 1.044, Fable 1.037. BOAR is −0.175 below Haiku | cut 3 | CLAIM-RESULTS-cut3.md:65 |

### Device (all on an 8 GB phone; no 12 GB data)
| Run | Phone | Numbers | Evidence |
|---|---|---|---|
| Smoke, cut 3, 9 items | Samsung SM-A155M, MT6789 (Helio G99), memTotal 7,864,220 kB (7.5 GiB), Android 16 | Model answers 100.5 / 107.2 / 146.7 s total. **TTFT 72–100 s**. Prefill 10.8–12.6 tok/s. **Decode 2.04–2.88 tok/s**. Cold warm-up 126.6 s, and it gave the wrong Lyon answer. Gated health cards 17.5–52 s. Rule paths 0.07–0.2 s. PSS peak 4.59 GB, then 3.6 GB; 1.6 GB swapped | device/a15-smoke-2026-10-05/device.json; device/A15-SMOKE-DIAGNOSIS.md:3,9,73-81; CLAIM-DRAFT.md:136,142 |
| Root cause of most smoke latency | Our own KV session-save bug: the gate prefix and answer prefix are re-prefilled on every question, about 55–65 s per answer. Fixed in cut 4 (KVFIX), but the fix has **never run on a phone** | A15-SMOKE-DIAGNOSIS.md:9,11,134-135; CLAIM-DRAFT.md:19 |
| Rate sweep, cut 5, airplane mode | Same A15 | Prefill 13–14 tok/s, decode 2.0–2.7 tok/s (t4 f16). With FA off: decode 3.7–3.8, prefill 9.5–11. Total p50 t6 59 s, t4 63/72 s, t8 81 s, t2 68 s. Thread ranking is inside noise (01 vs 08 drift 13%). PSS 4.4–5.0 GiB. q8 KV unmeasured | QUEUE.md:695 |
| v0.1 on device, cut 3, partial | Same A15 | 43/73 items, p50 total 112 s, p90 149 s. **Phone ratio 0.482 (0.402–0.563)** on 25 judged items, against desktop 0.478 / 0.493 on the same ids, so device quality ≈ desktop | QUEUE.md:698; CLAIM-RUNS-cut6.md:3 |
| Projection (not measured) | A15, cut 4 with KVFIX working | p50 68.7 s / p90 88.9 s per model answer; TTFT p50 39 s | device/A15-LATENCY-BUDGET.md:4,62 |
| 12 GB phone | — | **UNKNOWN / none.** It was "bought, in transit" on 2026-10-04 and no session has happened. DEVICE-DAY's title says "first 12 GB phone session", but every run so far was on the A15 | QUEUE.md:542; DEVICE-DAY.md:1,15 |

### What changed from cut 2 to cut 6
| Cut | Delta | Effect | Evidence |
|---|---|---|---|
| 3 | + VG v3 (verdict guard), AR (arithmetic tools), SBt (snakebite card text) | v0.1 +0.032 (CI90 +0.010…+0.062), dev-motivated. Held-out vs ship +0.0105 (−0.0038…+0.0293), MDE 0.018: **noise** | cut3-confirm-criterion.md:3; cut3-confirm.md:40; CLAIM-RESULTS-cut3.md:35,40 |
| 4 | + KVFIX, INSTANT-FRAG, INSTANT-SUBJ | Instant tier and phone cache only. v0.1 60/60 byte-identical | DEVICE-DAY.md:107; QUEUE.md:647,650 |
| 5 | + route-gate skip on rule-decided types, second `.nosrc` KV prefix | Phone latency only. 120/120 identical on v0.1 | DEVICE-DAY.md:135; CLAIM-DRAFT.md:125; QUEUE.md:665 |
| 6 | + DETMAX (detector on current turn alone) | Safety routing. v0.1 60/60 identical; G3 0/240 mismatches | QUEUE.md:694 |

**Did held-out move beyond noise?** No. 0.503 → 0.513 is +0.0105, its CI crosses 0, and it is below the 0.018 MDE (CLAIM-RESULTS-cut3.md:35,40). Cuts 4–6 were built so they would not change answers.

**Stale docs.** `CLAUDE.md` still names cut 2 as ship. `BOUNTY-BOARD.md:9,13,15` shows 0.503, "V-para not run", and a 12 GB TTFT estimate of 8.5–12 s, while the measured A15 TTFT is 72–100 s.

---

## 2. LOSS ANATOMY

**Verdict.** The largest bucket is **M6 "correct but thin"** (completeness and usefulness): 30 items, 0.183 of 0.441 total loss (41%). Next comes **knowledge** (M5a missing + M5b misread/absent), 0.149 (34%). No 4B lever reaches either one. Every lever aimed at M6 (style, length, persona, prompt diet) is closed. The open levers are small mechanical tables (expected +0.005 to +0.016 on dev, about half that on held-out) and the parked deep tier, the only lever measured above the MDE. Per the coordinator, "dev quality levers on the 4B are exhausted".

### Buckets (cut 4 = cut 6 on v0.1, 57 items, loss to reference = 0.4409)
| Bucket (doc label) | Maps to | n | Loss to ref | Gap to Haiku | Status | Evidence |
|---|---|---|---|---|---|---|
| M6 correct but thin | length/style/depth | 30 | **0.1825** | 0.0568 | No lever (style/length killed; deep35 only +0.008 here) | CUT5-LOSS-REFRESH.md:25; 4B-LOSS-ANATOMY.md:34,49 |
| M5b key fact absent from passage or misread | retrieval miss / misread | 7 | 0.0800 | 0.0238 | CRYPTOSEL/TRAVELSEL killed | CUT5-LOSS-REFRESH.md:24 |
| M5a knowledge missing from kit | knowledge | 6 | 0.0687 | 0.0194 | Open only through pack/deep tier | CUT5-LOSS-REFRESH.md:23 |
| M4 context narrows a correct memory | retrieval noise | 5 | 0.0446 | 0.0194 | Off-topic gate nets +0.002 | CUT5-LOSS-REFRESH.md:22; 4B-LOSS-ANATOMY.md:53-63 |
| M3 card/calc path content | non-model path | 6 | 0.0336 | 0.0077 | SC water card parked (recall 72%) | CUT5-LOSS-REFRESH.md:21 |
| M2 arithmetic | model reasoning | 2 | 0.0205 | 0.0086 | AR fixed vit-sci-003; cry-009 untouched | CUT5-LOSS-REFRESH.md:20 |
| M1 verdict vs own facts | model reasoning | 1 | 0.0107 | 0.0024 | VG line closed | CUT5-LOSS-REFRESH.md:19 |

Other categories the brief asked about:
- **Hallucination / confident-wrong** cuts across the buckets: 7 distinct items lose 0.096 (22% of all loss). That is 3 passage misreads, 2 false "not recognized" denials, 1 true premise "corrected" (Gríma), and 1 regional passage overriding a correct memory (CUT5-LOSS-REFRESH.md:8,35-41).
- **Refusals:** 0 declines on v0.1 (4B-LOSS-ANATOMY.md:41) and 0% over-refusal on V-para (CLAIM-RESULTS-cut3.md:62). The only refusal-like loss is the 2 false-denial items, which NOREC targets.
- **Judge artifacts:** not a loss bucket in the docs, but they are noise sources:
  - per-item judge noise up to 0.05 on identical text (cut3-confirm.md:58);
  - seed noise mean 0.057 per item (CUT5-LOSS-REFRESH.md:28);
  - the 0.566 vs 0.559 gap on identical answers (QUEUE.md:676);
  - reference and judge are the same Opus family, and no cross-family judge has run (CLAIM-REVIEW.md:65-69).

  UNKNOWN: how much of the ratio is judge style preference.

### Levers
| Lever | Targets | Status | Realistic headroom | Evidence |
|---|---|---|---|---|
| Style/length/persona, answer-first, prompt diet, answer cap | M6 | **Closed** (−0.031/−0.006; diet raised cw 5→9) | 0 | CLAIM-DRAFT.md:107,112; QUEUE.md:660 |
| Big Wikipedia packs, retrieval v2, rerank, query expansion | M5/M4 | **Closed** | 0 (rv2 −0.021) | CLAIM-DRAFT.md:104-106; KNOWLEDGE-PACKS.md:13-16 |
| Other 4B/9B readers, higher quants | all | **Closed** (9B closed-book = 4B) | <+0.01 | CLAIM-DRAFT.md:110; 4B-LOSS-ANATOMY.md:159 |
| Web-only knowledge pack | M5a | **Parked** | ≤ +0.007 net (the post author blog) | KNOWLEDGE-PACK-SIZING.md:12,88 |
| CF country-facts lookup | M5/M1 | **Killed** (trigger recall 80/100; data review 84% vs 98%) | (was +0.005–0.012) | QUEUE.md:670; CUT5-LOSS-REFRESH.md:60 |
| Calculator (units/tz/date) | M2 | **Skip** | +0.000 on v0.1 | CALC-SIZING.md:6 |
| k=3 (speed) | — | **No-adopt** (saves 19 tokens, not 150) | — | k3-on-cut2.md:21,43 |
| tf2 travel/crypto gate | M4 | **No-go** (Japan bar −0.018, which is inside noise) | ~0 | tf2-on-cut2.md:18,42 |
| GEO-TABLE + PLUG facts tables | M1/M5b | **Open on paper**, but it reuses the killed CF lineage | +0.012–0.016 dev → **+0.005–0.008 held-out** | CUT5-LOSS-REFRESH.md:9,64 |
| CRYPTOTRUTH (= EIPABS + NOREC) | M5b, false denials | **Parked**: answer-changing, so excluded after the cut 6 freeze | measured Δ +0.0092 [−0.0034, +0.0244], cw 10→6 | QUEUE.md:702 |
| SC water card | M3 | **Parked** (trigger unsolved) | +0.005 | CUT5-LOSS-REFRESH.md:54 |
| **Deep tier 35B** | M5 (out-of-kit) | **Parked** (owner: stay 4B-only) | **+0.060** (CI +0.021…+0.101) on desktop v0.1; out-of-kit +0.069; M6 only +0.008 | QUEUE.md:253,271,644; 4B-LOSS-ANATOMY.md:49 |

Bottom line from the docs: "nothing clears expected +0.01 as a single arm" (CUT5-LOSS-REFRESH.md:64). The remaining open levers are "non-mechanical (M6 thin 0.057, M5 knowledge 0.043)".

---

## 3. DEEP TIER (Qwen3.6-35B-A3B via bmoe-cli)

**Verdict.** Paused at D1 since 2026-10-03, first to save tokens. On 2026-10-05 the owner then decided to stay 4B-only. On desktop it is the only measured lever above the MDE: +0.060, about 0.565 vs 0.505 on v0.1. The memory worry was a measurement artifact; a Linux 6.6 GiB cap passed. It still needs roughly 7–9 days of integration (D2–D5) and a 12 GB phone. a competitor team (#125) already ships the same GGUF on a 12 GB Pixel 8 Pro at 4–6 tok/s, so the feasibility question is answered externally.

| Item | Value | Evidence |
|---|---|---|
| Status | D1 done (commit `79f986d`: pinned bmoe v0.28 build; Android payload 12.4 MB; `--session` JSON protocol smoke-tested on the host with the 4B). D2 not started | deep/RESUME.md:1-3,7-21 |
| Why paused | "PAUSED 2026-10-03, work budget". Then "focus on the 4B default tier" (10-04), then the r4to decision "Deep tier: stay 4B-only" (10-05) | deep/RESUME.md:1; QUEUE.md:535,542,644 |
| Model | UD-Q2_K_XL, 12.29 GB | deep/RESUME.md:24 |
| Desktop ratio | Paired Δ **+0.060 (+0.021…+0.101)** vs the 4B: 0.565 avg vs 0.505 (v0.1). Out-of-kit n=41: +0.069. BOUNTY-BOARD lists it as ≈ 0.57 | QUEUE.md:253,271; BOUNTY-BOARD.md:14 |
| Desktop latency | First visible p50 45 s, total 64 s. Forge's 12 GB phone estimate: first 17–27 s, total 55–80 s | QUEUE.md:253,469 |
| Memory | First reported as "fails 10.0–10.3 GiB vs ≤ 8 GiB". Corrected: that was macOS footprint accounting, and the 8 GiB bar was our own estimate, not the bounty's. P0 test, Linux container capped at 6,750 MiB with no swap: 10/10 prompts, 0 OOM, peak 6.59 GiB | QUEUE.md:253,267,279 |
| Doc inconsistency | **CLAIM-DRAFT.md:116 still says "peak memory 10.0–10.3 GiB against an 8 GiB limit. Parked"**, and CLAIM-REVIEW.md:150 asks to add "failed the memory limit". Both contradict the QUEUE correction and must be fixed before publication | CLAIM-DRAFT.md:116; CLAIM-REVIEW.md:150; QUEUE.md:267,279 |
| What it would take | D2: Kotlin Expo module running `libbmoe-cli.so` via ProcessBuilder, plus a JS `StreamedEngine` adapter. D3: engine arm `deep-streamed` (4B unload/swap, `streamed` fit verdict, catalog, receipts). D4: macOS bmoe shim + prompt-token parity + greedy check (judged L1 if greedy fails). D5: device day on a 12 GB phone. Forge's estimate is about 7–9 days (5 build + 1 device + risk). Disk: +12.3 GB on top of the 3 GB kit, well under 50 GB | deep/RESUME.md:26-42; QUEUE.md:499 |
| Claim framing | Report it separately from the default ratio, never as a replacement. The ruling to stay 4B-only is in force | QUEUE.md:239,644; CLAIM-DRAFT.md:175 |
| a competitor team (#125) per CLAIMS_31 | "Qwen3.6-35B-A3B at 2-bit … only the model and a Wikipedia corpus … Pixel 8 Pro with 12GB RAM", signed APK, HF corpus | CLAIMS_31.md:1-9 |
| a competitor team per its README (self-reported, outside the listed files) | Same `UD-Q2_K_XL` 12.3 GB, experts streamed from flash into an in-RAM cache. Storage 33.9 GB (21.3 GB Wikipedia, 2M articles). Memory about 7.9 GB (5 GB expert cache). **Gen 4–6 tok/s, prefill 24–30 tok/s**. Load 28 s. Retrieval-first answer median 98 s (first words 44–70 s); answer-first first words about 18 s, full about 3 min. Self-graded (Claude 0–10): 7.0 vs Qwen3-1.7B 2.6 | competitors/a competitor team/README.md:9-11,17,29-49 |

Risk carried from QUEUE.md:255: Boar is already claim #124 (the app maintainer, 1.5B), and a "materially different" build can disqualify. How a 4B or 35B update to #124 would be handled is UNKNOWN; the plan was to ask the issuer, and no answer is recorded.

---

## 4. CLAIM READINESS

**Verdict.** Not claimable today. On the bounty's own checklist, these are **not yet** done: public repo (9), reproduce instructions (10), demo post (13), the bar itself (14), usable phone speed (8), and an offline run on a phone (4). The reviewer's 8 blocking issues were applied in draft v3, but v3 itself was never re-reviewed, and parts of it are already stale. The deep-tier memory line, the "re-measure on cut 5 pending" text and the "sweep not run" item are all outdated. CLAIM-RUNS-cut6 is frozen (sha verified) and proposes a second spend of the held-out set on cut 6 with verdict reuse. Its results do not exist yet.

### Requirements (CLAIM-DRAFT v3 checklist)
| Requirement | Status | Evidence |
|---|---|---|
| Public GitHub repo | **Not yet** (private repos only) | CLAIM-DRAFT.md:143 |
| Code + instructions to reproduce | **Not yet**. The runner is now committed privately behind flags, but no public install path exists. **The Android UI does not call the measured engine (`answerService`)**; that wiring is deferred to the PR phase | CLAIM-DRAFT.md:144,150; QUEUE.md:645-646 |
| Public demo post (X/Farcaster) | **Not yet** | CLAIM-DRAFT.md:147,191 |
| Device video | **UNKNOWN / not planned** in any of these docs. The bounty asks for a demo post; no recording task is listed | BOUNTY_31.md:47-54; CLAIM-DRAFT.md:177-192 (absent) |
| 50 GB accounting | **Met.** Kit 3.03 GB (model 2.50 + detector/embedding 0.15 + packs 0.39) + 77 MB APK. Places kit size UNKNOWN but immaterial | CLAIM-DRAFT.md:137; CLAIM-REVIEW.md:31-34 |
| GrapheneOS / no Play Services | **Partly (static only).** No GMS/Firebase/trackers found in the APKs; no GrapheneOS device tried | CLAIM-DRAFT.md:135,140,219 |
| Fully offline | **Not verified on a phone** in the draft. The no-INTERNET APKs exist. QUEUE.md:695 records the cut 5 sweep "airplane" on the A15, which v3 does not mention yet | CLAIM-DRAFT.md:138-139; QUEUE.md:695 |
| ≤ 12 GB RAM | **Partly.** PSS 3.6–5.0 GiB on 8 GB; no 12 GB phone run | CLAIM-DRAFT.md:136; QUEUE.md:695 |
| Usable speed | **Not met** (100–147 s per model answer on the A15) | CLAIM-DRAFT.md:142 |
| >50% bar | **Not shown.** Held-out CI contains 0.50; V-para is below | CLAIM-DRAFT.md:148 |

### Reviewer (CLAIM-REVIEW, 2026-10-05): "CHANGES REQUIRED"
Blocking, accuracy (CLAIM-REVIEW.md:29-52):
1. Kit size double-counted.
2. Device latency attributed entirely to the KV bug.
3. Wrong fast-path timing.
4. Wrong memory peak.
5. Wrong cut 4 contents.

Blocking, undisclosed departures (CLAIM-REVIEW.md:54-79):
- (6) Device-first headline, 1B gap not run, 2 of 3 seeds, own-run D, per-writer results, hashes not published before the runs.
- (7) Reference and judge from the same model family.
- (8) Held-out item A02 motivated the CO card.

All 21 issues were applied in v2 (CLAIM-DRAFT.md:221-223; QUEUE.md:656). v3 added new material that **no reviewer has seen** (CLAIM-DRAFT.md:234-241).

The reviewer's warning that will hit hardest: until a cross-family judge runs, expect "the judge likes its own style" as the first objection (CLAIM-REVIEW.md:149).

### Stale or contradictory lines in CLAIM-DRAFT v3 (06:44, before the later decisions)
- Lines 20, 127, 181 say "re-measure on cut 5 pending owner decision". Superseded: the owner froze cut 6 and released the runs (CLAIM-RUNS-cut6.md:3).
- Line 185 lists the "device-rate sweep" as pending. It is done (QUEUE.md:695).
- Line 184 lists the A15 v0.1 partial as pending. It is judged: 0.482 (QUEUE.md:698).
- Line 116 states the deep-tier memory failure, which was corrected (see §3).

### CLAIM-RUNS-cut6 (today)
- **Frozen: yes.** `CLAIM-RUNS-cut6.sha256` = `5cd07029…dd377`, and `shasum` of the file now gives the same value (CLAIM-RUNS-cut6.sha256:1).
- Run A, v0.2 held-out L3: the **second spend** of the held-out set. Seeds s42+s43, judge.v1, both orders. Reuses cut 3 verdicts for byte-identical answers and judges only changed items fresh. Reports raw, floor-removed and above-decline, plus paired Δ vs cut 3, ship and E3 (CLAIM-RUNS-cut6.md:8-11).
- Run B, V-para: same as the cut 3 protocol, with the same verdict reuse (CLAIM-RUNS-cut6.md:12-14).
- Runner: committed boar-eval adapter 73b9d2c+, `BOAR_RUNNER_PROFILE=ship`, gate on, detector v3b (CLAIM-RUNS-cut6.md:6).
- Device evidence it rests on: A15 cut 3 partial, phone 0.482 vs desktop 0.478/0.493 (CLAIM-RUNS-cut6.md:3).
- What to expect: with verdict reuse, unchanged answers inherit cut 3's scores by construction. The result should land near 0.513 unless the instant or DETMAX changes touch v0.2 items. This is my inference; the result is UNKNOWN.

---

## 5. COMPETITORS

**Verdict.** CLAIMS_31.md lists **3** claims, not 4. The 4th, #132 Outpost (Bonsai 4B + saved docs + OSM), appears only in BOUNTY_31.md:73, with no details. One of the 3 (#124) is the app maintainer's own BOAR claim at 1.5B. a competitor team is the strongest rival on the post author's axes: an MoE model streamed from disk on a real 12 GB phone, 4–6 tok/s, public signed APK. BOAR leads only on having a measured, held-out quality ratio. the post author tested the 3 apps on 2026-09-26: all were "much slower and less effective at difficult questions" than laptop models, and none passed his vegan-restaurant test.

| Claim | Architecture | Numbers claimed | Evidence |
|---|---|---|---|
| #125 a competitor team | Qwen3.6-35B-A3B 2-bit (MoE, 3B active), Wikipedia corpus, Pixel 8 Pro 12 GB, signed APK, HF corpus | In the claim: none beyond the phone and RAM. In its README: 4–6 tok/s gen, 24–30 tok/s prefill, 7.9 GB RAM, 33.9 GB storage, retrieval-first median 98 s; self-graded 7.0/10 | CLAIMS_31.md:1-9; competitors/a competitor team/README.md:29-49 |
| #124 Boar (the app maintainer, UPSTREAM_REPO/boar-app) | Qwen2.5-1.5B + hybrid search over Wikipedia + 50k Vital pack, adaptive routing, airplane mode, no Google services, on-phone benchmark (also tested 7B, Phi-3.5, LFM2.5-8B-A1B, Gemma 4) | None in the claim text | CLAIMS_31.md:11-24 |
| #115 a competitor team | Native Android (Kotlin; README: llama.cpp JNI), local model + knowledge pack, no network permission, no GMS, Infinix phone demo. Model: Qwen3 1.7B (public v1.1.10) / Qwen3.5-2B Q4_K_M 1.4 GB (dev) | None (no speed or quality figures) | CLAIMS_31.md:26-37; competitors/competitor-app/MODELS.md:9-20 |
| #132 Outpost | Bonsai 4B + saved docs + OSM | UNKNOWN (not in CLAIMS_31.md) | BOUNTY_31.md:73 |

BOAR (cut 6) on the post author's axes (BOUNTY_31.md:9: "~10 tok/s from 1B models that break on anything interesting"; extreme MoE, ~100B on disk, <1B active):

| Axis | BOAR | a competitor team | Read |
|---|---|---|---|
| Speed | A15 (8 GB, Helio G99): decode 2.0–2.9 tok/s (3.7–3.8 with FA off), TTFT 72–100 s, total p50 59–112 s. 12 GB phone: UNKNOWN | Pixel 8 Pro: 4–6 tok/s, 18–70 s to first words | BOAR is slower as measured, but the hardware is confounded (low-end SoC vs Tensor G3). Both are below his 10 tok/s reference |
| Model size / MoE | Dense 4B, 2.5 GB. The 35B MoE is parked | 35B MoE, 3B active, streamed | a competitor team is closer to his architecture bet. BOAR's deep tier would match it, and BOAR would add RAG and safety on top |
| Breaking on interesting questions | Measured: held-out 0.513, V-para 0.413, below Haiku no-web (0.588). V-para reasoning 0.348; venues 0/7 | Self-graded 0–10 vs a 1.7B baseline; no frontier-relative ratio | Not comparable numerically. BOAR's numbers are more honest but show it "breaks" on the post author-style sets |
| His live test | BOAR's shown answer was generic with wrong sources (RSA); vegan test failed (all 3 apps) | Vegan test failed | memory `vitalik-eval-criteria.md` |

---

## 6. WIP / entropy

**Verdict.** At least 7 fronts are live, against the profile's WIP limit of 1–3. Three of them block the claim (public repo, Android UI wiring, 12 GB phone run) and none of those three has started. About 8 items look orphaned: started or proposed, with no result and no kill. The riskiest of them are the #124 "materially different" question, the 12 GB phone, and the deep tier with no kill decision while the competitor ships it.

### Active (started, result pending)
| # | Front | State | Evidence |
|---|---|---|---|
| 1 | Cut 6 claim runs (v0.2 L3 + V-para, desktop) | Released and frozen; no results file yet | CLAIM-RUNS-cut6.md; QUEUE.md:700-701 |
| 2 | Device final package for the A15 tester (a volunteer tester): speed APK 9q → cut 6 9q → cut 6 73q | Built (`handoff/boar-bench-final.zip`); whether it was sent or run is UNKNOWN | QUEUE.md:700 |
| 3 | cut5-speed retrieval A/B (native zstd etc.) | 0.445× on the phone, but order and cache are confounded; needs ABBA | QUEUE.md:699 |
| 4 | 12 GB phone session (DEVICE-DAY runbook, KVFIX first real test) | Phone "in transit" since 10-04; no session | QUEUE.md:542; DEVICE-DAY.md:15 |
| 5 | CLAIM-DRAFT v4 (cut 6 numbers, device data, stale-line fixes, re-review) | Not started; v3 is stale (§4) | CLAIM-DRAFT.md:1 |
| 6 | Android UI wired to `answerService` (PR phase) | Not started. The upstream freeze ended 2026-10-05 | QUEUE.md:645-646,648; CLAIM-DRAFT.md:150 |
| 7 | Public repo + install docs + demo post | Not started | CLAIM-DRAFT.md:188,191 |
| 8 | Plan departures: cross-family judge, 40-pair human check, 1B gap, 3rd seed, publish hashes | Not started | CLAIM-DRAFT.md:189-190 |

### Orphaned or ambiguous (started or proposed, no result, no kill)
| Item | Why orphaned | Evidence |
|---|---|---|
| Deep tier D2–D5 | Paused and ruled "stay 4B-only", but there is no kill note, and RESUME still says "resume when the coordinator says so" | deep/RESUME.md:3; QUEUE.md:644 |
| How to update claim #124 / "materially different" rule | Marked UNKNOWN on 10-02 ("ask the issuer"); no follow-up recorded | QUEUE.md:255 |
| KVQ8 (q8_0 KV) | PASSed as a device-day candidate. q8 was unmeasured in the sweep; unclear whether it enters cut 6 defaults | QUEUE.md:653,695 |
| Probe B `no_extra_bufts` (repack off) | "Stays a separate decision"; never decided | DEVICE-DAY.md:89 |
| PR 72 device levers (answer length from measured tok/s, warm-up `n_predict 1`) | Listed as device-day candidates; no arm | QUEUE.md:645,648 |
| tf1 deterministic-only travel/food fixes (47/47 probes) | "Could ship alone … not tested" | tf2-on-cut2.md:44 |
| GEO-TABLE + PLUG facts-table module | Proposed after the "exhausted" decision; not formally killed, though it shares the CF lineage | CUT5-LOSS-REFRESH.md:64; QUEUE.md:670 |
| CRYPTOTRUTH, HFU-FIX | Parked "for the PR phase"; no owner or date | QUEUE.md:690,702 |
| Housekeeping | Superseded zips (cut5-update, cut6-update); mini trees marked "can be deleted" (cut2-k3, tf2, cut3-vgar); stale `CLAUDE.md` map and BOUNTY-BOARD scoreboard | QUEUE.md:700; k3-on-cut2.md:50; tf2-on-cut2.md:59; cut3-vgar-L1.md:94 |

### Closed cleanly (with a kill or decision record)
k3, tf2, CALC, CF, web-only packs, SPEEDPACK/PROMPTDIET, SPECDEC, CUT5-SPEED (desktop), FOLLOWQ-G, HFU-FIX2, CHATGATE (no fix arm), VG line, V-para venues "report as is" (QUEUE.md:644,660,663,672,682,690; k3-on-cut2.md:1; tf2-on-cut2.md:1; CALC-SIZING.md:6; KNOWLEDGE-PACK-SIZING.md:88).

## UNKNOWN
- Cut 6 v0.2 / V-para results (the run may be in progress on the mini).
- Whether the A15 final package was delivered or run.
- 12 GB phone model and arrival date.
- V-exact aggregate on cut 3–6.
- Whether KVFIX works on device.
- #132 Outpost details.
- The issuer's answer on updating #124.
- Whether a device demo video is planned.

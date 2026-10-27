# BOAR R&D log audit — QUEUE.md (702 lines), 2026-10-01 → 2026-10-06

Sources: `rnd/research/QUEUE.md` (all 702 lines read, L1–L702), `rnd/research/BOUNTY-BOARD.md` (38 lines), `rnd/research/SHELF.md` (skimmed; artifact catalogue only, no experiment results beyond "tested" notes on jina-reranker, bge-reranker, mDeBERTa NLI, MiniCPM5-1B, simple-jev).
"Lx" = QUEUE.md line number. QUEUE has few explicit timestamps; dates below are inferred from the nearest dated header/entry.

Level key used here: L0 = deterministic/replay/no judge; L1 = slice or changed-items-only judging, or single-knob screen; L2 = full v0.1 (q72 or v0.1 EN 57/60) judged; L3 = v0.2 held-out or V-para; device = real phone; blind = fresh blind safety/routing/probe set (not v0.2); other = analysis/decision/build.
Frozen column: yes = criterion stated/frozen before data per the log; no = none stated; partial = frozen but changed/reinterpreted around the result (detail in cell); n/a = baseline/analysis.

---

## 1. Chronological table

### 2026-10-01 night → 2026-10-02 ~06:45 (night runs, Kiln on mini; first funnel not yet defined)

| # | Date/time | Lines | Owner | Lever / question | Level | Bench, n, seeds | Result | Verdict | Frozen before run? |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 10-01 23:40 / 10-02 01:00 | L64, L102 | kiln | Android Qwen3-4B on shared main (baseline) | L2 | q72, s42+s43 | 0.512 (0.461–0.567), MDE 0.030 | INCONCLUSIVE | n/a (baseline) |
| 2 | 10-01 23:55 | L59, L66 | compass / kiln | #7 run-budget card; iPhone 1.5B baseline s42/s43/s44 | L2 | q72, 3 seeds | 0.374 / 0.384 / 0.385; \|Δ\| 0.006 ≤ predicted 0.04 | SHIP (rule adopted, L61) | yes (prediction) |
| 3 | 10-01 → 10-02 02:45 | L15, L65, L103, L119–122 | anvil | #2 Gemma 4 E4B reader vs Qwen3-4B | L2 | q72, 2 seeds | 0.487 (s42); Δ −0.016 (MDE 0.036); CW 11 vs 10; total 22.9 vs 8.2 s | KILL | partial: speed gate added post hoc 23:20 (declared); TTFT criterion later found mis-measured (hidden thinking, L121); non-thinking arm never run |
| 4 | 10-02 01:00 | L14, L104 | coordinator (H3) | #1 main+46 hypothermia fix | L2 | q72, 2 seeds | Δ +0.0007 (−0.020…+0.021); unsafe 4→2 | SHIP (upstream PR-ready; not in later cut lists) | unknown |
| 5 | 10-02 00:10 | L16, L73 | sonar | #3 comparison entity split v1 | L2 (gate) | q72 vital5 pair | both sides in prompt +8 pp (bar +30) | KILL | yes (card) |
| 6 | 10-01 21:30 | L17, L21 | compass | #4 embedding danger detector | blind (hm-fresh2) | 24 danger + 16 HN | D1 23/24 PASS; D2 FP 3/55 FAIL | KILL | yes (21:30) |
| 7 | 10-01 22:05 | L30, L32 | compass | #4b detector v1 | blind (hm-fresh3) | 24 + 25 + 25 | D1′ 20/24 PASS; D2′ 4/25 FAIL | KILL (detector alone) | yes (22:05) |
| 8 | 10-02 00:10 | L38, L40, L75 | sonar | #5 Wikivoyage lead gate | L2 (gate) | q72 | saf-009 became unsafe memory answer | KILL | yes (21:50) |
| 9 | 10-02 00:10–02:20 | L57, L74, L88, L114 | sonar | #3b cmpsplit v2 → v2.1 | L2 | t0 pair + q72; judged 2×2 seeds | v2 gate FAIL; v2.1 sides 5/6 vs 3/6; judged Δ −0.0015 (−0.023…+0.021) | INCONCLUSIVE | yes (card) |
| 10 | 10-02 00:20–02:15 | L77, L109–113 | compass / kiln | #4b A1 arm (regex OR embedding) | L2 + blind sets | iPhone 2 seeds; Android s42 | D3/D4 PASS; Android blind danger memory 14→1, 16→2; saf-011 regression | SHIP (WIN; later superseded by health stack) | yes |
| 11 | 10-02 01:30 | L79, L99 | compass | #9 kit + preparedness pack | L2 | q72, 3 seeds | crit (1) FAIL (5→4/run, bar ≤2); quality Δ 0.005 | KILL (alone) | yes (card) |
| 12 | 10-02 | L80 | sonar | #10 on-topic gold-drop diagnosis | L0 | 6 items | 5/6 measurement artefact, 1 real | no verdict (diagnosis) | n/a |
| 13 | 10-02 | L82, L334 | sonar | #10b title-prf | L2 (gate) | q72 | (a)(b)(d) FAIL | KILL | yes (card) |
| 14 | 10-02 01:00 | L85–87 | coordinator | kit A vs kit A + vital5 (iPhone) | L2 | q72, 2 seeds | 0.379→0.395, Δ +0.016 (MDE 0.036) | INCONCLUSIVE | no |
| 15 | 10-02 01:00 | L89–93 | kiln | Decision 1: A show unconfirmed drafts / C PT→EN keywords | L2 | q72 | A 54%/50% CW (bar 10%); C −9%/−8% declines (bar −50%) | KILL (both) | yes |
| 16 | 10-02 03:40 | L95, L124–129 | coordinator | #9b kit+prep+A1 | L2 | q72, 3 seeds iPhone | 4/4 PASS; Δ −0.006 (−0.029…+0.016) | SHIP (WIN on iPhone profile) | partial: crit (2) reading declared at 03:40 after data |
| 17 | 10-02 02:00 | L97 | compass | #11 unsafe-passage denylist | blind (hm-loc1) | 45 items, 2 seeds | 0 traceable hits (bar ≥2) | KILL (MOOT) | yes (00:44/00:54) |
| 18 | 10-02 04:30 | L106, L133–142 | anvil | #12 complete-paragraph persona | L2 | q72 Android, 2 seeds | safety FAIL; P2 judged Δ −0.044 (−0.076…−0.014); CW 10→20 | KILL | yes (card); P2 judged after the fail "for strategy only" |
| 19 | 10-02 ~06:00 | L108, L202 | compass | #13 situation-shape route | L2 + blind union | — | 4/4 PASS alone; adds nothing stacked on A1 | KILL (not alongside A1) | yes (01:11) |
| 20 | 10-02 06:00 | L116, L203–207 | compass | #14 per-condition first-aid cards v0.1 | L2 + blind hand check | 15 cards shown | 13/15 correct, 2 wrong | KILL | partial: trigger switched v0→v0.1 before run (04:10, declared) |
| 21 | 10-02 05:00–05:30 | L146, L153 | compass | #16 crisis detector v0, v1 | blind (crisis1) | 30 + 30 | v0 recall 4/30; v1 25/30 (bar 85%), 1 decoy | KILL; PARKED by r4to (L233) | partial: v1 run on the same blind set after seeing v0's aggregate fail |
| 22 | 10-02 05:30 | L154 | anvil | MiniCPM5-1B | L0 | — | no gain vs 1.5B (card C) | KILL | unknown |
| 23 | 10-02 05:50 | L50, L130, L147, L156–160 | sonar | #6 enwiki top-100k pack | L2 | q72, 2 profiles | key net +3 (bar +6); gate FAIL; p50 3.3× | KILL → INVALIDATED 05:25 (mislabelled lead vectors, L186) | yes (card) |
| 24 | 10-02 06:00 | L155 | sonar | #6b named-article cap | L2 | q72 | a′ +8/−6 | KILL → INVALIDATED (L186) | yes |
| 25 | 10-02 06:10–06:30 | L162–170, L209–213 | summit | S1 memo + addendum (fronts, stop list, K1–K5) | other | — | Android-only; stop persona/prompt, same-class reader swaps, retrieval gates | no verdict (decision) | n/a |
| 26 | 10-02 06:20 | L172, L208 | coordinator | E1(a) vital5 on Android 4B | L2 | q72, 2×2 seeds | Δ 0.000 (MDE 0.026) | KILL (K1 clause 1) | yes (S1 K1) |
| 27 | 10-02 06:10–06:25 | L173–179, L201 | compass / coordinator | judge floor; v0.2 precision budget | other | — | always-decline = 0.306 raw; half-width 0.030 @167 | no verdict (analysis) | n/a |
| 28 | 10-02 06:35 → 12:40 | L180, L191, L222–226, L235–238 | sonar | #17 big-pack relevance gate G1/G2 → G1+ (fixed pack) | L1 (replay) | and-* traces | net +3 (+7/−4), 2 emptied, p50 2.17× | KILL; K1 fires, knowledge front closed | yes (E1(b)); G2 dropped and G1 refined to G1+ before run |
| 29 | 10-02 afternoon | L132, L182, L246 | anvil | #15 Maple 20B-A1B reader | L2 | q72, 2 seeds | Δ −0.028; CW 20/15 vs 10/12; gate FAIL | KILL (K4) | yes (06:35) |
| 30 | 10-02 05:45 | L199–200 | compass | cross-family judge pilot (GPT-5.5) | other | 114 calls planned | HELD for r4to; never run | no verdict | — |
| 31 | 10-02 | L221 | sonar | #18 no instant finish for comparison items (4B) | — | — | queued; never reported | no verdict | no ("to be frozen by card author") |
| 32 | 10-02 11:15 | L228–233 | r4to | morning decisions: raw-ratio bar, iPhone run, disk, crisis parked | other | — | — | no verdict (decision) | n/a |
| 33 | 10-02 12:55 | L239 | r4to | option 6 deep tier approved; deep ratio reported separately | other | — | — | no verdict (decision) | n/a |

### 2026-10-02 afternoon → night

| # | Date/time | Lines | Owner | Lever / question | Level | Bench, n, seeds | Result | Verdict | Frozen before run? |
|---|---|---|---|---|---|---|---|---|---|
| 34 | 10-02 pm | L242 | coordinator | iPhone 13 device P1 | device | q72, 2 reps | 0.394 (0.353–0.441) vs desktop 0.395; Δ −0.001 | no verdict (desktop proxy holds) | no |
| 35 | 10-02 pm | L243, L249 | coordinator | Fable as second judge | other | 456 verdicts | κ(correct) 0.894; same winner 99% | no verdict (info) | no |
| 36 | 10-02 pm | L244–245, L248, L252 | compass / coordinator | bench v0.2 plan + items freeze; coverage addendum | other | 110 new items | plan fe100e91; items aa4ff330; coverage computed pre-run | no verdict (freeze) | yes |
| 37 | 10-02 pm | L247, L253, L267, L270–271, L279 | anvil / kiln | option 6 deep35 (Qwen3.6-35B-A3B) | L2 | q72, 2 seeds | Δ +0.060 (+0.021…+0.101); 0.565 vs 0.505; macOS footprint 10.0–10.3 GiB; P0 container 6.59 GiB PASS | KILL by memory → reinterpreted to "quality PASS, memory not measured" (L267); later PARKED (L542, L644) | partial: frozen 818a21e3, memory criterion redefined after the result (L267) |
| 38 | 10-02 pm | L250–251 | compass | safety checker v0.5 | other | 27 tests | adopted after 27/27 | SHIP (scorer) | yes |
| 39 | 10-02 eve | L263 | compass | in-kit error taxonomy | other | v0.1 s42/43 | incomplete 33%, used-wrong 27%, dropped 22% | no verdict (analysis) | n/a |
| 40 | 10-02 eve | L265 | coordinator | anchor ladder v0.1 (Fable/Opus/Sonnet/Haiku no-web, Opus+web) | L2 | q72, 5 configs | Fable 1.048, Opus 1.029, Sonnet 0.950, Haiku 0.653; Opus no-web > Opus+web by 0.029 | no verdict (info) | no |
| 41 | 10-02 ~16:50 | L254, L273–274 | kiln | E3: v0.2 held-out baseline (main, Android 4B) | L3 | v0.2 167 judged, s42+s43 | 0.506 (0.475–0.538); half-width 0.028 | SHIP (E3 PASS; K5 not fired) | yes (plan fe100e91) |
| 42 | 10-02 eve | L269, L272 | compass | safety v0.6 / v0.7 with v0.2 danger overlay | other | 78 / 96 tests | v0.7 applied to E3 (first v0.2 scoring 16:50 > commit 16:41) | SHIP (scorer) | partial: adopted after E3 generation started, before any v0.2 safety result |
| 43 | 10-02 eve | L264, L266, L275, L289 | sonar | P-1 keep-the-key | L2 | q72, 2 seeds | +2 keys, 0 lost; Δ −0.003 (−0.019…+0.015) | SHIP? — "ADOPTABLE", never listed in any cut | yes |
| 44 | 10-02 eve | L266, L275, L280 | compass | P-2 grounded answer planning | L2 | 2 seeds | Δ −0.053 (−0.085…−0.021); gate FAIL | KILL | yes (4e2333c3) |
| 45 | 10-02 eve | L277–278, L282–283 | anvil | P-3 4B self-check (P3-0) | L0 | 7 + 20 | false flags 8/20 (bar ≤2) | KILL | yes (500bbf99) |
| 46 | 10-02 17:40 | L284–285 | compass | P3 NLI checker (mDeBERTa) | L0 | 7 + 20 | 0/7 hits | KILL | yes (2fe0ffd5) |
| 47 | 10-02 eve | L286 | sonar | P-4 off-topic passage drop | — | — | not run (predicted fail) | KILL (not run) | yes |
| 48 | 10-02 eve | L287, L290–291, L300 | sonar | P-1b (withdrawn) → P-5 FROM_TO_TRIP | L2 | replay + 2 seeds | crit 4 FAIL 1.22× → load-matched re-run 1.08× PASS; judged Δ +0.0003 | SHIP? — "ADOPTABLE", never listed in any cut | partial: re-measurement after fail (declared) |
| 49 | 10-02 eve | L292 | kiln | and-qwen s44 (3rd base seed) | L2 | q72 s44 | 0.498 | no verdict (info) | no |
| 50 | 10-02 eve | L281, L295 | kiln | iOS 8 GB profile (4B) | L2 | 2 seeds | 0.525 / 0.503 | no verdict (info) | no |
| 51 | 10-02 18:30 | L288, L293 | plumb | moto g75 (8 GB) 4B load | device | — | LMK-killed 2× | no verdict (finding) | no |
| 52 | 10-02 19:14–19:55 | L294, L296–297, L307 | plumb | moto g75 1.5B P1 | device | q72, 2 reps | 0.349 (0.316–0.385) vs desktop 0.379; Δ −0.029 | INCONCLUSIVE ("not decidable") | no |
| 53 | 10-02 night | L316 | kiln | g75-matched desktop profile | L2 | 2 seeds | device−desktop Δ −0.029 (−0.056…−0.002) | no verdict (desktop overstates ~0.03) | no |
| 54 | 10-02 night | L298, L302–303 | anvil | Probe A no-repack (mini); Probe B (g75) spec | other | — | anon 3.25→0.9 GB; Probe B never run | no verdict | yes (Probe B spec) |
| 55 | 10-02 night | L299, L301, L304, L306 | sonar | P-7 → P-7b pack block size | L0 | 72 | P-7 FAIL size +9.8% (bar ≤5%); P-7b bar re-set ≤6% in new card, PASS +4.61/+5.31% | KILL (P-7); P-7b PASS L0, then dropped (L469) | partial: size bar loosened between P-7 and P-7b |
| 56 | 10-02 night | L305, L308 | anvil | Fix 1 fit-repack (Android-only) | L0 | units | 1175/1175 | no verdict (never device-tested) | yes |
| 57 | 10-02 night | L310 | r4to field report | "boa noite" triggered search | other | — | mechanism reproduced | no verdict (finding) | n/a |
| 58 | 10-02 night | L312, L317 | sonar | P-8 pack SQL batching | L0 | 72 | identity 72/72; SQL −60% | no verdict (phone step never run; folded into forge-ship / CUT5-SPEED) | yes (75751ea5) |
| 59 | 10-02 night | L314 | r4to | DECISION: iterate fast; sha freeze only for full bench/held-out | other | — | — | no verdict (decision) | n/a |
| 60 | 10-02 night | L318, L324 | compass / kiln | chat-slice v0 + L1 slices | other | 64 msgs | base acc 44%, false-search 32/34 | no verdict (baseline) | n/a |
| 61 | 10-02 night | L319 | sonar | OSS scan (45 components) | other | — | top 5 ranked | no verdict | n/a |
| 62 | 10-02 night | L326 | sonar | Doc2Query-- | L0 | 26 pairs | genuine Δ key-in-context 0 | KILL | no |
| 63 | 10-02 night | L331 | sonar | bge-reranker passage gate | L0 | 44 items | 1 worse, 0 better; AUC 0.587 | KILL | no |
| 64 | 10-02 night | L343 | forge | native perf L0 (zstd / Rust / vector cache) | L0 | 68 calls | GO native zstd + vector cache; KILL Rust/uniffi | KILL (Rust) / OPEN (zstd) | no |
| 65 | 10-02 night | L329, L341 | anvil | chat routing A (tool calling) / B4 label gate / C rules | L0 | slice v0 57 | A FAIL; B4 95% on 4B (tuned on same items) | KILL (A) / → B5 | no |
| 66 | 10-02 night | L356 | kiln | parallel L1 runner | L0 | — | 1.1–1.17×, texts change 67–88% | KILL | n/a |
| 67 | 10-02 night | L345, L351, L369–370, L390, L393–394, L401, L404, L414, L419, L450–451, L453, L455, L458–459, L476, L483 | compass | safety checker v0.8 → v0.8.1 … v0.8.11 → v0.9 → v0.9.1 | other | regressions over 6k–20k answers | 15+ versions in ~30 h | SHIP (scorer versions) | yes per version |

### 2026-10-02 late night → 2026-10-03 (route gate, health stack, blind sets)

| # | Date/time | Lines | Owner | Lever / question | Level | Bench, n, seeds | Result | Verdict | Frozen before run? |
|---|---|---|---|---|---|---|---|---|---|
| 68 | 10-02 ~23:50 | L354, L359–360 | anvil | B4 gate L1(a) | L1 | routing-chat 24, s42 | ratio 0.489 (n=20) vs 0.452; vit-sci-003 flip | KILL (→ B5; coordinator override cancelled) | yes (stop rule) |
| 69 | 10-03 early | L352, L394 | compass | replylang arm | L0 / L1 | chat v0 64 | L0 61/64; L1 hand read FAIL | KILL | partial: 2 rules added after v0 misses (dev caveat) |
| 70 | 10-03 early | L361, L362, L366–368 | anvil | B5 gate L0/L1 → v1-fresh confirm | L0/L1/blind | v1-fresh 57, s42 | 51/57 (bar ≥52) | KILL (fail by 1 item) | yes |
| 71 | 10-03 early | L372, L375 | sonar | exp-29 instant guard (instguard 1–3) | L0/L1 | 39 items incl. blind night traces, 2 profiles | 4B: 6 night danger + saf-011 worse | no verdict (→ r4to product call L376) | no |
| 72 | 10-03 ~01h | L376 | r4to | health widening on all profiles + vetted cards | other | — | — | no verdict (decision) | n/a |
| 73 | 10-03 | L377, L380 | sonar | instcards / instcards2 | L1 | 63 × 2 | unsafe 4B 3→3, iPhone 4→3 | no verdict (→ health stack) | no |
| 74 | 10-03 | L381 | anvil / kiln | B5 L2 | L2 | v0.1, s42/s43 | ΔQ −0.0000 (−0.0125…+0.0121); route flips FAIL (lan-ref-002) | KILL | yes |
| 75 | 10-03 | L382 | sonar | health1–3 stack | L1 | — | unsafe 4B 3→2, iPhone 4→2 | no verdict (dev step) | no |
| 76 | 10-03 | L383, L388, L392 | anvil | B6 gate L0 → L1 → v2-fresh confirm | L0/L1/blind | v2-fresh 57, s42 | 55/57, missed 0/23 | SHIP (confirm PASS) | yes (d29bfdf5) |
| 77 | 10-03 | L384–385, L405 | sonar | health5 L2 | L2 | v0.1, 2 profiles × 2 seeds | 4B ΔQ +0.0092 (−0.0087…+0.0300), unsafe 0 vs 7; iPhone +0.0113 (−0.0124…+0.0374), unsafe 0 vs 10 | SHIP | partial: frozen 652a650d for health3, retargeted to health5 before data, re-frozen 59803cc1 |
| 78 | 10-03 | L387, L391, L402, L406–407 | sonar | health6 / 7 / 8 / 9 | L1 | 102 × 2 | unsafe 3→0 / 4→0 each | no verdict (dev iterations) | no |
| 79 | 10-03 | L409 | compass | stacked B6 + replylang L1 | L1 | 192 msgs | lang 171/192 (bar 173); new unsafe v2-048 | KILL | yes |
| 81 | 10-03 | L399, L403, L408, L412 | sonar / kiln | BLIND health-fresh1 confirm (health9 vs main) | blind (hf1) | 120, s42, 2 profiles | danger health route 31/72 (bar ≥54); HN FF 11/48; crypto 7→6 | KILL (FAIL) | partial: criterion retargeted health7→8→9 (3 freezes: 5feff387 → 3ee5217e → cadc8f6e), all before blind data; crit 5 hand read never recorded |
| 82 | 10-03 | L410, L414 | compass | precedence-only / chatline L1 | L1 | — | both KILL by the letter | KILL (then re-registered, L414/L419) | yes |
| 83 | 10-03 | L416–418 | anvil | iOS repack probe (iPhone 13) | device | — | no repack on iOS; pp512 165.8 / tg64 18.3 | no verdict (finding) | yes (spec) |
| 84 | 10-03 | L419 | compass | emergency-dev v1 (300 items) | other | 300 | κ 1.000 (same model family) | no verdict (dev set) | n/a |
| 86 | 10-03 | L422, L425–426, L442–444 | sonar | learned detector (exp-30) → mmBERT v2 → health11 HOLD → v3b | L0/L1 dev | 903 dev + Compass 300 | mmBERT 393/413 @ 13 FF; v3b 179/180 | no verdict (→ health11 blind) | no (dev) |
| 87 | 10-03 | L423 | forge | classifier runtime (ONNX vs llama.rn) | other | — | ONNX KILLED | KILL | n/a |
| 88 | 10-03 | L427–428, L440 | anvil | B6E 3rd-label emergency gate — blind detection replay | blind (hf2 + hf1) | 90+60, 72+48 | hf2 90/90, HN 6/60; hf1 71/72, HN 2/48 | SHIP? — PASS detection; answer arm later KILLED (row 93) | yes (d88d5efe, forecast stated) |
| 89 | 10-03 | L415, L419, L429 | compass / kiln | chat-v3 blind R0 (B6+health9) / R1 (precedence) | blind (chat-v3) | 64, 2 seeds | R0 PASS; R1 B3 FAIL (1.5B) | SHIP (R0) / KILL (R1) | yes |
| 90 | 10-03 | L432–435, L455 | compass | estask → estask2 (→ estask3) | L0/L1 | 564 dev; 48 ES | estask2 L1 KILL; estask3 GO, never run (parked L479) | KILL / no verdict | partial: es-fresh1 style shared with Compass, arm revised (L434) |
| 91 | 10-03 | L436 | compass | chat-v3 blind R2 | blind | 64, 2 seeds | C5 FAIL by letter (pre-existing maker claim); hand read 13/14 better | KILL (not confirmed) | yes |
| 92 | 10-03 | L443–444, L448–449 | sonar | health11 BLIND confirm | blind (hf1 + hf2) | 120 + 150 | scripted PASS (71/72, 90/90; HN 1/48, 2/60); hand read FAIL: wrong cards, harmful 3/72, 4/90 | KILL (FAIL) | yes (15665241, re-frozen from 5184b6a0 before data) |
| 93 | 10-03 | L441, L445, L447, L449, L452 | anvil | B6E answer-level arm | L2 (frozen, not run) | — | KILLED on blind detection comparison vs mmBERT | KILL | yes (31c0dde8 → fc5df39a) |
| 94 | 10-03 | L450–451 | compass | wrong-card checker (Jev dev / claude -p blind) v0.8.8 | other | 637 dev pairs | AUC 0.9997; catch 532/534 | SHIP (scorer) | yes |
| 95 | 10-03 | L452 | anvil | 4B card picker PICK + VERIFY | L0 dev | 103 / 177 | right 81/103, wrong 6/177 | no verdict ("learned picker dropped", L475) | no |
| 96 | 10-03 | L378, L386, L390, L401, L453–454, L457–458, L481, L483 | compass + Opus reviewer | first-aid cards rounds 1–6 + reviewer | other | 35 cards | reviewed-by-opus-reviewer | SHIP (into health13) | n/a |
| 97 | 10-03 | L456, L471 | anvil | out-of-kit: decline policy | L0 dev | 66 | perfect abstention ≈ +0.007 | KILL | no |
| 98 | 10-03 | L461–466 | r4to | DIRECTION: single goal = win #31 | other | — | — | no verdict (decision) | n/a |
| 99 | 10-03 | L438–439, L468 | compass | R3 About-BOAR — meta-fresh1 blind | blind | 36, 2 seeds | needless search 9/36 = R0 | KILL (PARKED) | partial: topic names reached Compass mid-build (L439) |
| 100 | 10-03 | L469 | forge | SHIP-SPEED patch (native zstd, vector cache, P-8) | other | units | built; P-7b dropped | no verdict (gated on device smoke) | n/a |
| 101 | 10-03 | L472–474 | forge / r4to | Android UI legacy path (ship-blocker) → r4to: not a blocker | other | — | — | no verdict (decision) | n/a |
| 102 | 10-03 | L475, L487–488, L500 | sonar | health13 BLIND confirm (hf3) | blind (hf3) | 120, 2 profiles | scripted PASS; hand read FAIL crit 6 (2 ES harmful wrong cards); EN subset 0 wrong | SHIP (EN-only ruling after the result) | partial: frozen 4e02f90c; retarget to health14 cancelled because run had started; adoption ruling made after FAIL |
| 103 | 10-03 | L477, L479 | r4to | DIRECTION: no work in the app maintainer's app; BOAR Bench; ENGLISH ONLY | other | — | — | no verdict (decision) | n/a |
| 104 | 10-03 | L501–502 | anvil | 12 GB model screen: Qwen3.5-9B, Ministral 3 8B | L1 (closed-book) | v0.1 EN 57 | 9B 0.488 = 4B 0.487; Ministral 0.457 | KILL | unknown |
| 105 | 10-03 | L502, L505, L509, L528 | anvil | ORACLE: gold passages Q450 / R450 / R1500 | L2 | v0.1 EN 57 | 0.567 / 0.606 / 0.626 vs engine 0.507 | no verdict (ceiling) | no |
| 106 | 10-03 | L503–505 | sonar | gold-hit L0, PQ re-rank | L0 | 56 | PQ 12→14/56 (bar ≥17) | KILL (standalone) | partial (gate stated in L503) |
| 107 | 10-03 | L496 | anvil | gate cold-start fix | L0 | units | 1193/1193 | SHIP (cut 1) | no |
| 108 | 10-03 | L498–499 | forge | device-detector arm (mmBERT on llama.rn) | L0 | parity 300 | 300/300, max \|dp\| 0 | SHIP (cut 1) | no |
| 109 | 10-03 | L506 | kiln | SHIP STACK v0.2 L3 (b6-on-health13 + detector) | L3 | v0.2 110 EN, s42+s43 | 0.503 (0.468–0.539); Δ vs E3 −0.004 (−0.032…+0.026), MDE 0.019 | no verdict (target CI-low > 0.50 NOT met) | yes (plan) |
| 110 | 10-03 | L478, L480, L507 | compass / kiln | V-exact first run | other (public slice) | 11 items, 5 judged | 4B 0.390 (0.297–0.486); venues 6/6 | no verdict (info) | no |
| 111 | 10-03 | L508, L515–517 | compass | CO hazard safety fact (motivated by v0.2 A02) | L0 | 292 dev + lookalikes | 0/292 FF; 23/26 lookalike recall | SHIP (cut 1) | partial: held-out-motivated (disclosed; A02 excluded from claims) |
| 112 | 10-03 | L482, L487, L518 | sonar | exp-33 big pack L1: kit A vs +top100k (full / title tier) | L1 | v0.1 EN + V-exact, 1 seed | B Δ −0.005; C2 Δ −0.016; B p50 3.3× | KILL | yes (9ed14be1) |
| 113 | 10-03 | L510–511, L513, L519, L526–527 | sonar | rv2 retrieval (CLEAN min) | L0 → L1 | v0.1 EN, 2 seeds | gold 7→18/56; judged Δ −0.021 (CI90 −0.054…+0.009); 3.6× | KILL (retrieval line PARKED) | yes (64ede784) |
| 114 | 10-03 | L512, L514 | anvil | travel-distance calculator | L0 | V-exact Paris–Rome + 1,034 dev | 0.89 vs engine 0.29 | SHIP (cut 1) | no (built on a V-exact item) |
| 115 | 10-03 | L519, L521 | sonar | rv2.1 / rv2.2 | L0 | 56 | 18→16 / 18→17 | KILL / no verdict (DEV) | no |
| 116 | 10-03 | L519 | sonar | pcity (city in GPS venue header) | L0 | tests | 210/210 | SHIP (cut 1) | no |
| 117 | 10-03 | L520, L522–525, L529 | forge | ship cut 1 / 1b / 2 builds | other | identity checks | cut 2 = 7931b9a8 | SHIP (build) | n/a |
| 118 | 10-03 | L523 | sonar | co-exposure / exposure2.1 verification | L0 | 1,328 dev | CO recall 13→18/19 | SHIP (cut 1b/2) | no |
| 119 | 10-03 | L527 | sonar | citefix | L0 | — | — | SHIP (cut 2) | no |
| 120 | 10-03 | L531, L537 | anvil | answer-style S2 / S3 | L1 | v0.1 EN, s42 only | S0 0.499; S2 Δ −0.031; S3 Δ −0.006 | KILL | yes (f2e42e22) |
| 121 | 10-03 | L532 | kiln | V-exact on cut 2 | other | 5 judged | 0.510 (plain 0.303–0.739) | no verdict (info) | no |
| 122 | 10-03 | L533 | forge | deep tier D1 build | other | — | done | no verdict (PARKED L542) | n/a |
| 123 | 10-03 | L534, L536 | compass | premise guard | L1 | — | withheld correct corrections 4/seed (bar ≤1) | KILL | yes |
| 124 | 10-03 | L534, L538 | sonar | Gríma alias / Japan crypto-cue / travel-food routing (tf2) | L0 | 65 + 47 probes | Gríma unfixable (15/15 denies) | no verdict (→ row 128) | no |
| 125 | 10-03 eve | L535 | r4to | TOKEN BUDGET mode | other | — | — | no verdict (decision) | n/a |

### 2026-10-04 (in-session coordinator, no Maestri)

| # | Date/time | Lines | Owner | Lever / question | Level | Bench, n, seeds | Result | Verdict | Frozen before run? |
|---|---|---|---|---|---|---|---|---|---|
| 126 | 10-04 01:03 | L539–541, L543 | kiln | overnight: cut 2 v0.1 EN s44–s47 (judge.v1-med) + calibration + deep35 | L2 | 60 × 4 seeds | 0.532 / 0.535 / 0.539 / 0.527 (≈0.533); v1-med vs v1 κ 1.000; deep35 FAILED (arm mismatch) | no verdict (info); deep35 never re-run | no |
| 127 | 10-04 | L542 | r4to | DIRECTION: 4B tier only; deep tier parked at D1; no Maestri | other | — | — | no verdict (decision) | n/a |
| 128 | 10-04 | L544, L547 | coordinator | tf2-on-cut2 (crypto gate + travel/food routing) | L1 | v0.1 EN s44 + V-exact (20 calls) | G3 FAIL: Japan 0.356→0.338 (within judge noise) | KILL | yes (2e0dec75) |
| 129 | 10-04 | L545 | coordinator | 4B loss anatomy | other | v0.1 EN | cut 2 → Haiku gap +0.121; cut 2 gain over old main +0.026 | no verdict (analysis) | n/a |
| 130 | 10-04 | L548, L555 | coordinator | k3-on-cut2 (k=4→3) | L1 | — | −19.3 prompt tok (bar −100); 0 judge calls | KILL | yes (7d8fcd81) |
| 131 | 10-04 | L546, L549, L551, L557, L559, L567 | coordinator | AR arithmetic tools | L0 / L1 | 1,467 dev; held-out 32; L1 s44+s45 changed-only | vit-sci-003 +3.33 | SHIP (cut 3) | yes |
| 132 | 10-04 | L549–550, L553, L558, L561, L564–569 | coordinator | VG verdict guard v1 → v2 → v3 + VG-S ship gate | L0/L1/blind probes | vg-probe-q 90 | stack L1 Δ +0.029 [+0.007, +0.058], CW 15→9; VG-S 1 fire BETTER | SHIP (cut 3) | partial: V2 FAIL by letter → "disclosed exception" (L550); V5 reviewer FAIL → v2 → v3 |
| 133 | 10-04 | L552, L554, L556, L560, L562 | coordinator | SC water + snakebite cards/trigger v1 → v2 → v3 | L0 + blind (S5 set, sc-fresh3, sc-fresh4) | 100 each | S5 72%; S5′ FF 5/50; S5″ water 72% | KILL (water/trigger); snakebite text SHIP (cut 3) | yes each round (S5 set burned for v2, disclosed) |
| 134 | 10-04 | L570–573, L575–577 | coordinator | VG v4 (threshold / superlative) | blind (vg-probe-q2) | 120 | 1 WRONG fire | KILL (VG line CLOSED) | yes (1f31215b) |
| 135 | 10-04 | L563, L566, L569, L574 | coordinator | cut 3 confirmation | L2 | v0.1 EN s44+s45 + V-exact | 0.566 vs cut 2 0.534: Δ +0.032 CI90 [+0.010, +0.062] (cut 2 verdicts reused on 52 items) | SHIP (cut 3 = a67c70db) | yes (fdd06c4a) |
| 136 | 10-04 | L579 | coordinator | knowledge-pack sizing (web-only pack) | other | — | open-licence reachable ≈ +0.013 | KILL (PARKED for bounty) | n/a |
| 137 | 10-04 | L581–588 | coordinator | CF country-facts lookup pack | L0 + blind trigger set #1 | 100 + 100; data 150 fields | trigger recall 80/100 (bar 90); data agreement 84% (bar 98%) | KILL | yes (5c302adf) |
| 138 | 10-04 | L589–596 | coordinator | CV computed verdict | L0 + blind gate | dev 145; gate 83 | dev +16.6 pp but 6 wrong-where-right → rev1 → gate +26.5 pp, 3 wrong (bar ≤2) | KILL | partial: frozen b27a0b58; rev1 PASS obtained by masking superlative/rank on the same dev key (disclosed, L594) |
| 139 | 10-04 | L597–601 | coordinator | CVS (CV rev1 + fact-sanity guard) | blind gate #3 + L1 | 83; v0.1 EN (16 calls) | gate +22.9 pp PASS; L1 Δ −0.005 [−0.015, +0.003] | KILL | yes (595107c3) |
| 140 | 10-04 | L602–603 | coordinator | CVH (computed verdict as hint) | L1 | v0.1 EN | Δ −0.0034 [−0.015, +0.006]; +5.49 s | KILL | yes (010b7ed2) |
| 141 | 10-04 | L604–605 | coordinator | computed-verdict line CLOSED; loop stopped | other | — | — | no verdict (decision) | n/a |

### 2026-10-05 → 2026-10-06 (/loop, claim runs, device)

| # | Date/time | Lines | Owner | Lever / question | Level | Bench, n, seeds | Result | Verdict | Frozen before run? |
|---|---|---|---|---|---|---|---|---|---|
| 142 | 10-05 | L606, L609, L611, L618 | coordinator | CVO (verdict override only on disagreement) | L1 + blind gate #4 | v0.1 EN; 84 | L1 0/120 changes; gate +6.0 pp (bar +8), 2 wrong | KILL (CV family fully closed) | partial: frozen 4c37259b; baseline switched to same-day control by ruling (L609); scorer bug → rescored |
| 143 | 10-05 | L606–608 | coordinator | CRYPTOSEL (crypto-pack EIP selection) | L0 / L1 | 3 targets; v0.1 EN | targets +0.472 (bar +0.5); Δ +0.0033 | KILL | partial: frozen 6ba3e103; L0 revision added a gold file + a rule beyond the wording (disclosed) |
| 144 | 10-05 | L610, L612–614 | coordinator | PROMPTDIET | L0 | — | −125.7 tok (bar −150) | KILL | yes (f8eef6f0) |
| 145 | 10-05 | L615–616 | coordinator | TRAVELSEL | L0 | 3 targets | 1/3 (bar ≥2) | KILL | yes (e4ffcb5c) |
| 146 | 10-05 | L617 | coordinator | CALC sizing | other | — | ceiling +0.000 | KILL (SKIP) | n/a |
| 147 | 10-05 | L619–620 | coordinator | Q35 (Qwen3.5-4B) screen | L1 (closed-book) | v0.1 EN | 0.437 vs bar 0.517 | KILL | yes (187bbae9; seed mismatch noted) |
| 148 | 10-05 | L621–622 | coordinator | G4E4B (Gemma 4 E4B) screen | L1 (closed-book) | v0.1 EN | 0.495 vs bar 0.517 (tie with 0.487) | KILL | yes (d62e54df; first write empty, rewritten) |
| 149 | 10-05 | L623, L626 | coordinator | G4ENG (Gemma in full cut 3 engine) | L2 | v0.1 EN, ~240 calls | Δ −0.0385 [−0.0725, −0.0058] | KILL (4B model line closed) | yes (5aecdd03, declared post-screen) |
| 150 | 10-05 | L624, L628–633 | coordinator / a volunteer tester | A15 device smoke, cut 3 | device | 9 items | tiers 8/8 = desktop; TTFT 72–100 s | no verdict (info) | no |
| 151 | 10-05 | L627, L640–643 | kiln | CLAIM RUNS cut 3: v0.2 L3 + V-para | L3 | v0.2 110 EN s42+s43; V-para 58 | v0.2 0.513 (0.479–0.550), Δ vs ship +0.011 (−0.004…+0.029) < MDE 0.018; V-para 0.413 (0.384–0.445), P5 venues 0/7 | INCONCLUSIVE (v0.2 consistent with 0.50) / KILL (V-para P1 FAIL) | yes (d2fa6d35 + VPARA-BARS) |
| 152 | 10-05 | L644 | r4to | report venues 0/7 as is; 4B-only | other | — | — | no verdict (decision) | n/a |
| 153 | 10-05 | L634–636, L650 | coordinator | cut 4: KVFIX + INSTANT-FRAG | L0 / L1 identity | v0.1 EN s44+s45 | 60/60 identical; KVFIX untestable on desktop | SHIP (cut 4) | yes (c4735323) |
| 154 | 10-05 | L638–639, L647 | coordinator | INSTANT-SUBJ | blind (lookup2) | 40 + 15 | 0 instant finishes in both arms (gate uninformative) | SHIP (cut 4) | yes (d897731e) |
| 155 | 10-05 | L652–653 | coordinator | KVQ8 (q8_0 KV cache) | L1 | v0.1 EN, 2 seeds (180 calls) | Δ −0.0077 [−0.0232, +0.0062] | no verdict (PASS; device-day candidate, not in cut) | yes (bae45d0c) |
| 156 | 10-05 | L654, L656, L675 | coordinator | claim draft v1 → v3 + independent Opus review | other | — | 21 issues fixed; not published | OPEN | n/a |
| 157 | 10-05 | L655, L657 | coordinator | offline APK audit → no-network bench APK | other | — | network-capable → no-net build | no verdict (info) | n/a |
| 158 | 10-05 / 10-06 | L658, L698 | a volunteer tester | A15 v0.1 on-device, cut 3 | device | 43/73 run, 25 judged (50 calls) | phone 0.482 (0.402–0.563) vs desktop 0.478 / 0.493 | no verdict (device ≈ desktop within noise) | no |
| 159 | 10-05 | L659–660 | coordinator | SPEEDPACK (faithful diet + 96-token cap) | L1 | v0.1 EN, 2 seeds + run A | Δ −0.0158 (bar −0.015); CW 5→9 | KILL | yes (c0bceaf6) |
| 160 | 10-05 | L661 | coordinator | A15 latency budget model | other | 9 rows | warm p50 68.7 s | no verdict (analysis) | n/a |
| 161 | 10-05 | L662–663 | coordinator | CUT5-SPEED | L1 identity | 120 | G3 retrieval 1.071× (FAIL) | KILL | partial: frozen ab05007f; G4 guards tightened on dev before run (disclosed) |
| 162 | 10-05 | L664–666 | coordinator | CUT5-LITE (.nosrc KV prefix + gate skip) | L1 identity | 120 | identical; retrieval 0.961× | SHIP (cut 5) | partial: post-hoc subset of CUT5-SPEED, declared; frozen e8be61a9 |
| 163 | 10-05 | L667–669 | coordinator | GATEFID (gate on desktop) | L1 | v0.1 EN s44 | 0/60 text changes | no verdict (fidelity OK) | yes (753a7181) |
| 164 | 10-05 | L670 | coordinator | CUT5-LOSS-REFRESH | other | — | cut 4 v0.1 0.5591; "dev levers exhausted" | no verdict (decision) | n/a |
| 165 | 10-05 | L671–672 | coordinator | SPECDEC (speculative decoding) | L0 | 60 | acceptance 31%; native path unsupported | KILL | yes (66361511) |
| 166 | 10-05 / 10-06 | L673, L695 | a volunteer tester | A15 device-rate sweep (threads, FA, q8 KV) | device | 8 configs × 5 items | FA off decode +55%, prefill −25%; thread ranking within drift | INCONCLUSIVE | partial (10% drift bar) |
| 167 | 10-05 | L676 | coordinator | 0.566 vs 0.559 reconciliation | other | — | judge-reuse noise 0.0065 | no verdict (analysis) | n/a |
| 168 | 10-05 | L677–678 | coordinator | CHATGATE (gate conversation path) | L1 | 192 dev chat | G1 FAIL (coverage, not routing); gate miss 1/69 | no verdict (criterion design error) | yes (449c6e17) |
| 169 | 10-05 | L679–680 | coordinator | FOLLOWQ diagnostic | L0 | dev follow-ups | rule not met | no verdict (diagnostic) | yes |
| 170 | 10-05 | L681–682 | coordinator | FOLLOWQ-G | L1 (Opus A/B) | 13 pairs | 45% (bar 60%) | KILL | partial: post-hoc, declared; frozen ade5c84e |
| 171 | 10-05 | L683–685 | coordinator | HFU diagnostic | L0 | 100 synthetic | 69/100 lose the health route | no verdict (diagnostic) | yes (64a6bf1d) |
| 172 | 10-05 | L686–690 | coordinator | HFU-FIX → HFU-FIX2 | L0 (held-out templates) | — | G3 58.1% → 84.2% (bar 90%) | KILL | partial: HFU-FIX2 = same patch, narrower scope declared post hoc |
| 173 | 10-05 | L691–692 | coordinator | DETFU diagnostic | L0 | 60 × 3 | 1/60 route lost (S3) | no verdict (diagnostic) | yes |
| 174 | 10-05 | L693–694 | coordinator | DETMAX | L0 / L1 | 240 + 60 + 192 | 0/240 mismatches | SHIP (cut 6) | yes (a7c784af) |
| 175 | 10-06 | L699 | a volunteer tester | A15 cut5-speed A/B | device | n = 1 each | retrieval 0.445× (order/cache confounded) | INCONCLUSIVE | no |
| 176 | 10-06 | L696, L700–701 | r4to / coordinator | claim build FROZEN at cut 6; v0.2 L3 + V-para released | L3 (pending) | — | not yet in the log | OPEN | yes (CLAIM-RUNS-cut6) |
| 177 | 10-06 | L697, L702 | coordinator | CRYPTOTRUTH | L0 / L1 | 5 targets; v0.1 EN (10 calls) | Δ +0.0092 [−0.0034, +0.0244]; CW 10→6; fictional-probe gate 1/3 FAIL | KILL (as frozen; parked) | yes (767e4d24) |

---

## 2. Score trajectory of the ship candidate

All v0.1 numbers are Android Qwen3-4B, 12 GB profile, desktop. "v0.1 q72" = full 72 items, judge.v1; "v0.1 EN" = 57/60 EN items, from 10-04 judged with judge.v1-med (κ 1.000 vs v1 on one run, L541/L543). Run-to-run noise ≈ 0.03 (mandate); stated MDEs 0.018–0.038.

| Stage | Date | Lines | What changed | v0.1 | v0.2 held-out | V-exact (5 judged) | Beyond noise? |
|---|---|---|---|---|---|---|---|
| main (shared engine 0cfd4a77) | 10-01/02 | L102, L273, L292 | baseline | q72 0.512 (0.461–0.567) 2 seeds; s44 0.498 | E3 0.506 (0.475–0.538) | not run | — |
| ship stack (b6-on-health13 + detector) | 10-03 | L381, L405, L421, L506–507, L518, L526 | B6 route gate + health5→13 stack + cards + mmBERT detector | B6 L2 ΔQ −0.0016; health5 ΔQ +0.009; v0.1 EN "A" 0.545 (exp-33, 1 seed), 0.538 (rv2 L1) | 0.503 (0.468–0.539); paired vs E3 Δ −0.004 (−0.032…+0.026) | 0.390 (0.297–0.486) | No: quality-neutral by design (safety stack); v0.2 Δ inside noise |
| cut 1 / 1b | 10-03 | L520, L522 | + gate cold-load, travel-calc, CO hazard, pcity, device detector (+ co-exposure) | not judged as a unit | — | — | n/a (never scored) |
| cut 2 (7931b9a8) | 10-03 | L529, L532, L541, L545 | + exposure2.1, citefix (rv2 rejected) | v0.1 EN ≈ 0.533 (4 seeds s44–s47, v1-med) | not run (held, L526) | 0.510 (plain 0.303–0.739) | v0.1: No — the same-engine-family "A" control was 0.538–0.545 (L518, L526); the +0.026 "over old main" (L545) compares different item sets, judges and seeds. V-exact +0.12 comes from 1 item (Paris–Rome 0.29→0.94) whose calculator was built on that item (L512/L514); the plain CI is ±0.22 |
| cut 3 (a67c70db) | 10-04 | L567, L569, L574, L641–642, L676 | + VG v3, AR, snakebite text | v0.1 EN 0.566; Δ +0.032 CI90 [+0.010, +0.062] vs cut 2 (reused verdicts; later 0.559 on the same texts, L676) | 0.513 (0.479–0.550); Δ vs ship +0.011 (−0.004…+0.029) < MDE 0.018; V-para 0.413 (0.384–0.445) | byte-identical to cut 2 → 0.510 | v0.1: borderline. Δ ≈ noise threshold; driven by 4 changed items; judge reuse alone moves 0.0065. v0.2: No (inside MDE) |
| cut 4 (d51e844c) | 10-05 | L647, L650, L670 | + KVFIX, INSTANT-FRAG, INSTANT-SUBJ (latency/instant safety) | 60/60 identical to cut 3 → 0.5591 control | not run | 0 changes | n/a (answer-identical) |
| cut 5 (3b7a0dfa) | 10-05 | L665 | + .nosrc KV prefix, gate skip (device latency) | 120/120 identical | not run | — | n/a |
| cut 6 (824e0b35, tree b0f53fe0) | 10-05/06 | L694, L700–701 | + DETMAX (detector window OR current turn) | 60/60 identical | released 10-06, result not yet in the log | — | pending |

Net from main to cut 6: v0.1 ≈ 0.51 → ≈ 0.56 (judge and item set changed along the way); v0.2 0.506 → 0.513 (+0.007, inside noise). The dev gain did not carry over to the held-out set.

BOUNTY-BOARD.md is behind the log. It shows v0.1 "0.51–0.53" (log: 0.559–0.566), V-para "not run" (log: 0.413, L642) and v0.2 "0.503" (log: 0.513 on cut 3, L641).

---

## 3. Loop detection

### 3a. One lever tested many times, under new names or with small changes

| Lever family | Instances (lines) | Count |
|---|---|---|
| Big Wikipedia pack / knowledge into context | #6 (L50, L156) → #6b (L155) → both INVALIDATED (L186) → E1(a) vital5 (L85, L208) → #17 G1/G2/G1+ (L180, L191, L222, L235) → **S1 rule "no fourth pack iteration" (L211, L237)** → exp-33 B/C2 (L482, L518) → rv2 (L513, L526) → rv2.1/rv2.2 (L519, L521) → web-only pack sizing (L579) → CF country facts (L581–586) → GEO-TABLE/PLUG proposed (L670) | 10+ |
| Reader model swap (4B tier) | Gemma E4B #2 (L15, L103) · MiniCPM5 (L154) · Maple #15 (L246) · Qwen3.5-9B / Ministral (L501–502) · Ministral temp-0.1 (L514) · Q35 (L620) · G4E4B (L622) · G4ENG (L626). S1 said to stop same-class swaps (L170). "Model line closed" was written 3 times (L502, L622, L626) | 8 |
| Prompt / answer shaping on the 4B | #12 persona (L106–142) → P-2 planning (L280, "stop prompt-shaping arms on the 4B") → answer-style S2/S3 (L531–537) → PROMPTDIET (L610–614) → SPEEDPACK (L659–660). S1 stop list: "persona/prompt work" (L170) | 5 |
| Verdict / self-consistency fixes | P-3 self-check (L283) → P3-NLI (L285) → premise guard (L536) → VG v1→v4 (L546–577, "VG line CLOSED") → CV (L596) → CVS (L601) → CVH (L603) → **"line CLOSED for the bounty" (L604)** → CVO the next day (L606, L618) | 11 |
| Comparison-side retrieval | #3 v1 (L73) → #3b v2 (L74) → v2.1 (L88, L114 null on the 1.5B) → re-test on the 4B approved (L331), never reported; bge gate (L331) points back to "recall of the missing comparison side" | 4 |
| Route gate | B4 (L354–360) → B5 (L361–381) → B6 (L383–421) → B6E (L427–449) → CHATGATE (L677–678) | 5 |
| Health detector / cards | #4 → #4b → A1 → #4c (parked) → #13 → #14 v0/v0.1 → instguard 1–4 → instcards 1–2 → health1…health13 (L382–475) → mmBERT v2 → v3b → HFU-FIX → HFU-FIX2 (L686–690) → DETFU → DETMAX | ~25 versions |
| Safety checker (scorer) | v0.4 → v0.5 (L251) → v0.6 (L269) → v0.7 (L272) → v0.8 (L351) → v0.8.1–v0.8.11 (L351–459) → v0.9 (L476) → v0.9.1 (L483) | 17 versions in ~2 days |
| Reply language / ES strings | replylang (L352) → stacked B6+replylang (L409) → precedence / chatline (L410, L414) → chat-v3 R1/R2/R3 (L429–468) → estask/estask2/estask3 (L432–455) → esstrings-v2 (L459) | 9 |
| Crypto-pack selection | Japan crypto-cue / tf2 (L538, L547) → CRYPTOSEL (L606–608) → CRYPTOTRUTH (L697, L702) | 3 |
| Travel retrieval | P-5 (L287–300) → exp-39 travel/food routing (L538, L547) → TRAVELSEL (L615–616) | 3 |
| Prompt-token / speed trims | P-7 → P-7b (L301–306) → k=3 (L184, L555) → PROMPTDIET → SPEEDPACK → CUT5-SPEED → CUT5-LITE → KVQ8 → SPECDEC | 8 |

### 3b. Levers re-tested after a KILL / CLOSED / stop rule

- **Big packs after K1 and "no fourth pack iteration"** (L211, L237). Re-opened at L482 because the old #6 verdict used mislabelled vectors. But #17 G1+ had already run on the fixed pack (L235). Two more pack arms followed, exp-33 (KILL, L518) and rv2 (KILL, L526), and then CF (KILL, L586).
- **Computed-verdict family.** CV was KILLED (L596). CVS (= CV rev1 + guard) started the next line (L597). "Line CLOSED for the bounty" (L604) was followed the next day by CVO (L606), the "after the bounty" idea from L604.
- **Gemma 4 E4B.** NOT ADOPTED (L103). Re-screened as G4E4B (L621–622). After failing that screen it was re-tested as a new arm, G4ENG (L623, "declared post-screen"), which was KILLED (L626).
- **Prompt diet.** PROMPTDIET ENDED at L0 (L614) and came back as half of SPEEDPACK (L659). That run was KILLED (L660).
- **replylang.** KILLED at L1 (L394). The same entry says "GO stacked B6 + replylang" (L394), which was KILLED (L409). The language line was then split into precedence + chatline, both KILLED by the letter (L414), then re-registered (L414) and run as chat-v3 R1/R2/R3 (L429–468).
- **CUT5-SPEED** NOT ADOPTED (L663) → CUT5-LITE, a post-hoc subset, ADOPTED (L664–665).
- **HFU-FIX** NOT ADOPTED (L688) → HFU-FIX2, the same patch with fresh templates and a narrower scope, also failed (L689–690).
- **Deep tier.** NOT ADOPTED on memory (L253) → criterion restated (L267) → P0 PASS (L279) → D1 build (L533) → parked (L542, L644).
- **cmpsplit v2.1.** Null on the 1.5B (L114) → re-test on the 4B approved (L331). No result.
- **Prompt shaping.** After S1's stop list (L170): P-2 (L280), answer-style (L531) and PROMPTDIET/SPEEDPACK (L610, L659) were all run anyway.
- **Same-class reader swaps.** After S1's stop list (L170): L501–502, L619–626.

### 3c. Runs with no frozen criterion (per the log)

- Before the L314 fast-iteration rule: kit A + vital5 (L85); iPhone device P1 (L242); Fable second judge (L249); anchor ladder (L265); and-qwen s44 (L292); iOS 8 GB profile (L295); g75 runs (L307, L316); MiniCPM5 (L154, unknown).
- After L314, sha freezes are only required for full bench / held-out, so most L0/L1 dev steps have none: Doc2Query-- (L326), bge gate (L331), native perf (L343), chat routing interim (L329, "tuned on the same items"), instguard (L372–375), instcards (L377–380), health1–3/6–9 L1s (L382–407), learned detector dev (L422–426), card picker (L452), decline policy (L471), model screens (L501, unknown), oracle (L502–509), travel calculator (L512–514, built on a V-exact item), rv2.1/rv2.2 (L519–521), co-exposure (L523), V-exact runs (L507, L532), overnight seeds (L541), device runs (L630–633, L658, L698, L699).
- Frozen, then reinterpreted or changed around the result (rows marked "partial" in §1): Gemma speed gate (L15), #9b crit 2 (L126), crisis v1 on the same blind set (L153), deep35 memory (L267), P-5 latency re-run (L290), P-7b size bar (L304), B6 L2 danger criterion (L421), health13 EN-only adoption (L500), VG V2 exception (L550), CV rev1 masking (L594), CVO baseline swap (L609), CRYPTOSEL extra rule (L607), CUT5-LITE / FOLLOWQ-G / HFU-FIX2 post-hoc scopes (L664, L681, L689).

### 3d. Runs whose result was never recorded

| Item | Lines | State |
|---|---|---|
| #8 Jev `new-cw` gate replay | L68 | queued; never reported |
| #18 no instant finish for comparisons | L221 | queued; never reported |
| cmpsplit v2.1 + per-side relaxation on the 4B | L331 | approved; never reported |
| Probe B (g75, no_extra_bufts) | L298, L303, L363 | never run (g75 gone, L416; cut 3 lacks it, L591) |
| P-7b / P-8 phone steps; Forge phone session S1/S2 | L306, L312, L363–365 | never run; P-7b dropped (L469) |
| Anvil gate prefix-cache probe legs A / A′ / B | L349, L389 | never reported (leg C dropped, L357) |
| iPhone P3 unplugged speed | L242 | deferred; never run |
| cross-family judge pilot | L199 | held; never run |
| health9 hf1 criterion 5 hand read | L412 | "pending"; never recorded |
| estask3 L1 | L455 | parked (L479) |
| deep35 overnight runs | L541 | failed (arm mismatch); never re-run |
| A15 full v0.1 (73 items) | L658, L698 | stopped at 43/73 |
| cut5-speed device ABBA | L699 | required; not done |
| q8 KV device speed | L695 | unmeasured |
| cut 6 v0.2 L3 + V-para | L700–701 | released; result not yet logged |

### 3e. Repeats driven by noise or single items instead of more n/seeds

- **P-5 latency.** After a FAIL, a load-matched re-run turned it into a PASS (L290). The method fix that followed (interleaved runs) was the right response.
- **Single-seed decisions:** exp-33 (L518, 1 seed), answer-style (L537, s42 only), B5/B6 fresh confirms (L367, L392, s42 only), b4gate L1 n=20 (L359). The L1 slices are noise below Δ ≈ 0.08 by the team's own note (L318).
- **Item-level verdicts inside judge noise:** tf2 G3 failed on one item that moved 0.018 "within judge noise" (L547). CRYPTOSEL missed its target bar by 0.028 (L608). The CVO time gate passed at +3.95 s vs a +4 s bar, while an interleaved probe gave +4.12 s (L609).
- **New small fresh sets after each failed revision**, rather than one larger set: sc-fresh3 → sc-fresh4 (L554, L560); vg-probe-q → q2 (L565, L572); CV gate → gate #3 → gate #4 (L595, L599, L611); v1-fresh → v2-fresh → chat-v3 (L345, L369, L415); hf1 → hf2 → hf3 (L398, L424, L446); es-fresh1 → es-fresh2 (L433, L435); lookup set → lookup2 (L635, L639).
- **Verdict reuse across judge instances.** The cut 3 Δ reused cut 2 verdicts (L574). The 0.566 vs 0.559 gap came from that reuse (L676), and the CVO baseline was switched to a same-day control because of temp-0 drift (L608–609).

---

## 4. Counts

Based on the 177 rows in §1:

Mechanical tally of the verdict column (a row can carry two labels, e.g. "KILL / SHIP"):

| Category | Count | Notes |
|---|---|---|
| Rows (experiments + runs + decisions) | 177 | |
| Rows with a KILL label (incl. NOT ADOPTED, MOOT, NO-GO, PARKED-after-fail, INVALIDATED) | 77 | |
| Rows with a SHIP label | 32 | ~19 engine components in the candidate (below); the rest are scorer versions (safety checker, wrong-card check), the run-budget rule, builds, and wins later superseded (A1, #9b, H3, B6E detection, chat-v3 R0) |
| ADOPTABLE but never in any cut | 3 | P-1 (L289), P-5 (L300), KVQ8 (L653) |
| INCONCLUSIVE | 7 | |
| OPEN | 3 | #64 native zstd, #156 claim draft, #176 cut 6 claim runs |
| "no verdict" | 63 | ~17 decision/direction/incident rows + ~46 info, diagnostic, baseline or never-reported rows |
| Experiments still open with no decision | ~15 | §3d list (never-reported runs) + claim draft (L675) + cut 6 claim runs (L701) |

Ship-candidate engine components: B6, the health stack (health5→13, cards, mmBERT detector), device-detector, gate cold-load, travel-calc, CO hazard v2f, pcity, co-exposure, exposure2.1, citefix, VG v3, AR, snakebite text, KVFIX, INSTANT-FRAG, INSTANT-SUBJ, CUT5-LITE (.nosrc + gate skip), DETMAX. That is about 19. Only VG + AR (+0.029 on v0.1, L567) and the cards/calculator (+0.026 vs old main, L545) moved the judged ratio. None moved v0.2 beyond noise.

**Judge-run estimate (rough).** One full v0.1 judged run is about 114 `claude -p` calls (L199). About 60 full-run equivalents ran on 10-01/02 (rows 1–53). About 25 ran on 10-02/03 (B5/B6/health5 L2s, E3). About 30 ran on 10-03 (screens, oracle, exp-33, rv2, ship L3, answer-style). About 6 ran on 10-04: overnight seeds, plus changed-items-only runs of 16–20 calls each. About 25 ran on 10-05/06 (Q35, G4E4B, G4ENG ~240 calls, KVQ8 180, SPEEDPACK, cut 3 claim runs and ladder, A15 50, CRYPTOTRUTH 10). v0.2 runs count about 2.3× because they have 167 items. The total is ~140 run-equivalents, or **roughly 12k–20k judge calls**. On top of that come the Fable second judge (456), wrong-card `claude -p` checks and Opus reviewer passes. UNKNOWN: exact per-run call counts for runs before the changed-items-only protocol (L546).

---

## 5. Blind / held-out exposure log

| When | Lines | Set | What happened | Logged as exposure? |
|---|---|---|---|---|
| 10-01 21:30 | L17, L21 | hm-fresh2 (rnd/veil) | #4 detector D1/D2 | yes (frozen blind use) |
| 10-01 22:05 | L30 | hm-fresh3 | #4b D1′/D2′ | yes |
| 10-02 00:20–02:15 | L77, L111 | hm-fresh2/3, vitalik58 | A1 engine arm runs (traces kept in boar-eval/runs/night-2026-10-01) | used as blind; trace location only flagged at L396 |
| 10-02 02:00 | L97 | hm-loc1 | #11, 2 seeds | yes |
| 10-02 ~06:00 | L202, L205 | hm-fresh2/3 + hm-loc1 | #13 run on the union; #14 coordinator hand check of card items | yes (coordinator) |
| 10-02 04:45 | L144 | rnd/veil/*.jsonl | Compass `grep -rl`, learned hm-fresh2/3 contain self-harm items | yes (self-disclosed) |
| 10-02 05:00 / 05:30 | L146, L153 | crisis1 | v0 run, then v1 on the same set ("crisis1's last use") | yes; v1 was built after v0's aggregate fail |
| 10-02 ~16:50 | L273–274 | **v0.2 #1 (E3, main)** | 2 seeds; coordinator blind safety adjudication | yes |
| 10-02 pm | L252, L269 | v0.2 | coverage classes computed on items; safety overlay maps 5/10 then 10/10 v0.2 danger items to rules (v0.6/v0.7), adopted after E3 generation started | partly. The precedence rule is logged (L272); no line says who read item content to build the overlay (UNKNOWN) |
| 10-02 → 10-03 | L373 | **v0.2 plaintext** | questions/refs/runs sat in researcher-readable boar-eval; Sonar's trace scan printed v02-honesty-refusal-A05 | yes; files moved to blind/ (git history still has them) |
| 10-02 night | L335 | veil h1 (vit-h1-001..003) | printed into Kiln's session | yes |
| 10-03 | L372, L375, L396–397 | hm-fresh2/3, hm-loc1 | **Sonar used the night blind traces as dev for exp-29 L0/L1 (the coordinator pointed him to them)** | yes, after the fact; sets demoted to DEV (L396) |
| 10-03 | L395 | night blind items | coordinator adjudication (vit-hm2-008, vit-hm3-059) | yes |
| 10-03 | L412 | health-fresh1 #1 | health9 confirm | yes (scoped Kiln exception, L400) |
| 10-03 | L429, L436 | chat-v3 #1, #2 | R0/R1, then R2 | yes (scoped exception) |
| 10-03 | L434 | es-fresh1 | coordinator shared the style description with Compass; arm revised to estask2 | yes (process slip); demoted to secondary |
| 10-03 | L439 | meta-fresh1 | topic names reached Compass mid-build | yes |
| 10-03 | L440 | hf1 #2, hf2 #1 | B6E detection replay | yes |
| 10-03 | L448–449 | hf1 #3, hf2 #2 | health11 confirm; hand read → hf1/hf2 demoted to DEV for card picking | yes |
| 10-03 | L468 | meta-fresh1 #1 | R3 run | yes |
| 10-03 | L486 | V-para | Kiln saw grading dicts (patterns, venue fields), not questions or answers | yes; ruled valid |
| 10-03 | L500 | hf3 #1 | health13 confirm + coordinator hand read | yes |
| 10-03 | L506, L508 | **v0.2 #2 (ship stack)** | 2 seeds; A02 adjudicated unsafe → CO hazard fix motivated by a held-out item | yes; A02 excluded from improvement claims (L508, L515) |
| 10-04 | L552 | SC S5 held-out recall set | burned to design SC v2 | yes (disclosed) |
| 10-04 | L556, L562 | sc-fresh3, sc-fresh4 | one scoring each | yes |
| 10-04 | L568, L575 | vg-probe-q, vg-probe-q2 | one scoring each; q then DEV | yes |
| 10-04 | L584–586 | CF trigger set #1 | scored once; set #2 unopened | yes |
| 10-04 / 10-05 | L596, L600, L618 | CV gate, gate #3, gate #4 | one scoring each | yes |
| 10-05 | L637 | cut 4 lookup set | engineer ran it against instructions | yes; burned |
| 10-05 | L647 | lookup2 | scored once | yes |
| 10-05 | L641–642 | **v0.2 #3 (cut 3 claim) + V-para #1** | 2 seeds; script-only | yes (authorisation d2fa6d35) |
| 10-06 | L701 | **v0.2 #4 (cut 6) + V-para #2** | released | logged as the "second held-out exposure". By this log it is the 4th v0.2 generation+judging run (E3 L273, ship L506, cut 3 L641, cut 6 L701), or the 2nd if only claim runs are counted |

**Signs of tuning on held-out or blind data (all disclosed in the log unless noted):**

1. v0.2 A02 → CO hazard card (L508, L515). A02 is excluded from improvement claims.
2. Blind night sets (hm-fresh2/3, hm-loc1) used as dev by Sonar (L396–397).
3. Blind confirm sets re-used after earlier aggregate fails: crisis1 v0 → v1 (L153); hf1 health9 FAIL (L412), then B6E (L440) and health11 (L448) on the same hf1.
4. es-fresh1 style leaked to the arm author (L434); meta-fresh1 topic names leaked (L439).
5. The v0.2 safety scorer was extended with an overlay for v0.2 danger items while E3 was running (L269, L272). The log does not say whether any arm author saw those items.
6. V-exact (public, 11 items) acts as both dev and reported metric. The travel calculator (L512–514) and pcity (L519) were built on V-exact items, then V-exact was reported as a scoreboard row (L532; BOUNTY-BOARD row 4). V-para was protected from this explicitly (L512).

No line shows a researcher reading v0.2 or V-para item text other than the A05 incident (L373) and the coordinator's adjudications.

---

## 6. Last 10 entries (L693–L702)

1. **L693, DETMAX pre-registered.** The detector fires if the history window OR the current turn alone crosses the threshold. It has no free parameter and responds to DETFU's history-dilution miss.
2. **L694, DETMAX ADOPT → cut 6.** 0/240 split-turn mismatches (cut 5 had 7), v0.1 60/60 identical, one added route in 192 chat messages. Cut 6 = cut 5 + DETMAX.
3. **L695, A15 device-rate sweep received.** 9/9 runs, no failures, airplane mode. FA off speeds decode about 55% but slows prefill about 25%. Thread ranking is within drift, q8 KV is unmeasured, and device sampling is not deterministic.
4. **L696, cut 6 tester package built.** APK cca28caf + zip, not sent (r4to decides). Replaces the cut 5 zip.
5. **L697, CRYPTOTRUTH pre-registered.** An honest not-found reply plus a verbatim EIP card for crypto truthfulness, on cut 6.
6. **L698, A15 on-device quality (partial).** 43/73 cut 3 items ran on the phone and 25 v0.1 EN items were judged. Phone 0.482 vs desktop 0.478/0.493 on the same IDs, so device ≈ desktop within noise.
7. **L699, A15 cut5-speed A/B (n=1).** Retrieval 0.445× on the phone vs 1.071× on desktop. Run order and page cache are confounded, so it needs ABBA before any adoption.
8. **L700, final device package.** The claim build is frozen at cut 6 and handoff/boar-bench-final.zip covers one session. v0.2 desktop run released to boar rnd.
9. **L701, r4to decisions confirmed.** Cut 6 frozen; only routing/safety fixes that leave v0.1 answers unchanged may follow. v0.2 L3 + V-para released for cut 6 (logged as the "second held-out exposure"; see §5).
10. **L702, CRYPTOTRUTH NOT ADOPTED as frozen.** Δ +0.0092 [−0.0034, +0.0244], CW 10→6, but one of 3 fictional probes failed the phrase-list gate. Parked as research-only; the build was already frozen.

**Right now:** the claim build is frozen at cut 6 and its v0.2 + V-para desktop runs are released but not reported. The full device run is with the tester, and answer-changing arms are research-only.

---

UNKNOWN:
- Exact clock times for most entries (QUEUE has few timestamps).
- Who read v0.2 danger-item content to build the v0.6/v0.7 overlay (L269, L272).
- Exact judge-call counts per run before L546.
- Whether H3 #46, P-1 and P-5 are inside the b6-on-health13 base (cut lists at L520/L529 don't name them).

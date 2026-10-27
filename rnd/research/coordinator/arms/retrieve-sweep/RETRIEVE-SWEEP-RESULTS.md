# RETRIEVE-SWEEP stage 1 results (2026-10-22, 0 LLM: replay only; 0 judge, 0 Opus, 0 paid, 0 phone; dev items)

**TL;DR.** No arm is a CANDIDATE; stage 2 (Haiku screen) has nothing to screen. The keep step is not where the QFORM golds are lost: with no
keep filter at all the gold would be kept on 199/432 (+4.6 pts over B0's 179), so no keep-step arm can reach the +8 bar (A74 +2.5). The
largest QFORM gain is C SIBLING (+7.9 vs B0, +3.9 vs its own K1 baseline B1), but it misses the bar, recovers 1/25 real items and 2.4x
the junk. On the real items, the 25 funnel losses barely move (best: B KEYQ 2/25, with 1 loss): the funnel's S3 losses are mostly
"dense candidate not picked" (10 of 17), a stage none of the five arms touches.

## Arms x metrics (full tables: aggregates/sweep.md, per-item: aggregates/sweep.json)
| arm | hit@kept | Δ vs B0 pts [95% CI] | recovery /25 | losses /22 | junk-kept (×B0) | kept tok | wall ms/q | verdict |
|---|---|---|---|---|---|---|---|---|
| B0 stock | 41.4 | — | — | — | 1.53 (1.00) | 191 | 88 | — |
| B1 K1 settings | 45.4 | +3.9 [+2.1, +5.8] | — | — | 3.02 (1.97) | 438 | 92 | — |
| A78 GROUND-DENSE 0.78 | 43.1 | +1.6 [+0.7, +3.0] | 0 | 0 | 1.55 (1.01) | 196 | 93 | no |
| A74 GROUND-DENSE 0.74 | 44.0 | +2.5 [+1.2, +4.2] | 0 | 0 | 1.63 (1.06) | 205 | 138 | no |
| B KEYQ | 42.4 | +0.9 [−0.7, +2.5] | 2 | 1 | 1.60 (1.04) | 192 | 134 | no |
| C SIBLING (on K1) | 49.3 | +7.9 [+5.3, +10.6] | 1 | 0 | 3.67 (2.40) | 583 | 2630 | no |
| D DIVERSITY | 41.2 | −0.2 [−0.7, 0.0] | 0 | 0 | 1.52 (0.99) | 192 | 86 | no |
| E MINSIM 0.62 | 39.8 | −1.6 [−2.8, −0.5] | 0 | 2 | 1.36 (0.89) | 170 | 87 | no |
| F = A74 + B (exploratory) | 45.1 | +3.7 [+1.6, +6.0] | 2 | 1 | 1.68 (1.10) | 207 | 448 | no |
CI = paired item bootstrap (B 2000, seed 11); fact-cluster bootstrap gives the same verdicts. Rule (frozen, sha 94ddb631): Δ ≥ +8 with CI
low > 0 AND recovery ≥ 5/25 AND losses ≤ 2/22 AND junk ≤ 1.25×B0. Per-form hit@kept: C lifts F0 50→60, F1 10→23, F3 25→35, F7 42→54;
A74 lifts F1 10→15, F6 50→60; no arm moves F8 (8 %).

## Prediction vs result
| arm | predicted | observed |
|---|---|---|
| A | +10…+18, junk up, recovery 6–10/25 | +1.6 / +2.5, junk +1/+6 %, recovery 0/25 (ceiling of any keep rule: +4.6) |
| B | +5…+10 | +0.9 (8 gained, 4 lost) |
| C | +3…+6, factbook only | +7.9 vs B0 / +3.9 vs B1, all packs, junk ×2.4 |
| D | +0…+4, firstaid +2…+4/8 | −0.2; the 4-per-family cap never binds at k 3–4 (bm25 already caps 2 per article) |
| E | +2…+6, junk up | −1.6, junk down: the lower floor admits bundled-corpus dense hits that displace pack chunks |
| F | +15…+25 | +3.7 (A74 + B, exploratory; no arm passed) |

## What each arm did to the dropped golds
- QFORM 25 "gold in raw, dropped at keep": A78 keeps 7, A74 11, C 9 (B1's head pass alone 7), B/D/E 0. Gold-chunk cosines of the 20
  grounding drops: 0.62–0.84 (7 ≥ 0.78, 12 ≥ 0.74); the other 5 leave at compression or the health-strict filter, which A does not touch.
- Funnel 25 (MAIN, K1): B recovers vit-hum-002 and vit-sci-001 (loses vit-cry-011); C recovers vit-cry-010; E loses lan-rsn-006 and vit-cry-011;
  A, D recover nothing. The losses there are dense-rank (fact in the X2b dense candidates, not among the 2 picked) and router items; widening
  the X2b dense pick (HEADPASS_DENSE_D = 2) is the untested lever the funnel points to.

## Caveats
- QFORM items and gold are agent-written (dev); one deterministic replay per arm (reruns identical 432/432); gold = quote/chunk-id match on
  the primary chunk only. MAIN presence = FACTPRESENT lexical rule (noisy; funnel caveat), parity of the switch-off replay vs the funnel:
  kept titles 91/97, labels 25/25 absent and 22/22 present.
- C is compared with B0 as the rule says, but it runs on K1 settings; its own increment over B1 is +3.9 pts (17 items). Its wall (2.6 s/q mean)
  is on-the-fly embedding of up to 60 chunks per article because the merged pack has no chunk_vecs; with a sidecar it is a lookup.
- A's similarity is computed by embedding the chunk at the keep step (pack hits carry no similarity); on a phone that is ≤ 4 extra
  embeddings per question. MAIN wall times are noisy (B0 410 ms vs A 330 ms; cold caches); QFORM walls were run sequentially.
- D's "source family" was read as the title past its library label up to the first " — " or ":" (else every Wikivoyage page is one family).
- B's keyword form uses its own stoplist (stop/wh/aux/pronouns/filler, ≤ 6 terms); scores of the two lists are merged as is (max).

Files: patches/{A..F}.patch, replay/ (RUN.md, *.qform.jsonl, *.main.jsonl, *.off20.jsonl, Adiag0 = keep-ceiling diagnostic, run_all.log),
tools/{replay-sweep.ts, replay.sh, run_all.sh, sweep.py, proofdiff.py, qhit.py}, aggregates/sweep.{json,md}.

## Arm G (coordinator, 00:3x–00:5x, 0 LLM): chunk-level dense vectors (format-v3 packs with chunk_vecs, built by DENSECHUNK-ST2) under packDense2
Why: stage 1 showed the loss is first-stage retrieval (pack dense = one lead vector per article; gold in wide-12 only 52 %). The v3proto packs with `chunk_vecs` exist for factbook, firstaid, medlineplus (and simplewiki, 5 SE packs) on the MacBook and the mini. Replay = the 216 QFORM items of those 3 packs, 3-pack kits (control = v2 files, packDense2 off; arms = v3 files with `{"packDense2": true}` = chunk hits join the fusion, and `"extra"` = 2 extra raw slots), same tree/gate/embed. Files g-chunkvecs/.
| arm | gold in raw | in kept | Δ kept pts [CI item bootstrap] | gained/lost | junk-kept (× ctl, n 131) | ctx tokens after compression | pack bytes v2 → v3 |
|---|---|---|---|---|---|---|---|
| control (v2, off) | 69/216 | 46 (21.3 %) | — | — | 0.99 (1.00) | 255 | factbook 11.6 MB, firstaid 21.0, medlineplus 4.3 |
| G-true (fusion) | 117 | 69 (31.9 %) | **+10.6 [+6.5, +15.3]** | 26/3 | 1.31 (1.32) | 266 | 11.8 / 26.3 / 4.5 |
| G-extra (2 extra slots) | 128 | 78 (36.1 %) | **+14.8 [+10.2, +19.4]** | 33/1 | 1.75 (1.76) | 348 | same |
Per form (ctl → G-extra, of 24): F0 2→7, F1 4→5, F2 6→13, F3 2→6, F4 1→4, F5 16→20, F6 7→12, F7 7→9, F8 1→2. Per pack kept: factbook 19→34, firstaid 10→18, medlineplus 17→26.
Against the frozen rule: pooled Δ clears +8 with CI > 0 (on this 216-item subset, not the 432: crypto/wikivoyage/visa have no chunk vectors); junk-kept 1.32× (G-true) misses the 1.25× bar by 0.07, G-extra 1.76× misses it clearly; funnel recovery untested (the K1 kit's crypto and wikivoyage have no v3 file; simplewiki does). **Not a CANDIDATE by the letter; the only arm that moves the first stage.** Stage 2 (Haiku answer screen on G-true, changed-context items) runs as an exploratory measurement, labelled so; a verdict needs the rule met (chunk vectors for the whole kit + the funnel read).
Context: DENSECHUNK-ST2 (10-13, CLOSED 46) measured the same mechanism for the 4B on the 180 self-tests: reach 67→108, answers +0.017 Opus (not decided at MDE 0.03), format v3 not shipped. QFORM adds the per-form view (paraphrase stays at 5/24: no lexical or lead match to rescue) and the 1.7B reader result (0.88 with the gold vs 0.19 without), which is why the answer screen is worth its 300 Haiku.

## Arm G stage 2 (01:0x-01:3x, exploratory: the stage-1 rule is NOT fully met, so this screen cannot make G a lever; Haiku 400/400, Opus 0, paid 0, phone 0)
Question: does chunk-level dense (lifts gold-in-kept 21 -> 32 %) turn into better 1.7B answers? Qwen3-1.7B on the mini, K1 tree be-0cfd4a77-cut7-litepacks (answer.ts 0d1ac07d, LITEDECLINE_OFF 5, seed 42, -t 4, reasoning off), 216 QFORM items x 2 runs. CTL = 3 single v2 packs (persona-a-union = mini wave1/wave2 copies, shas equal to ctl3's), settings {quickFirst, alwaysComplete false}. ARM = the 3 v3proto packs + `packDense2: true`. Files g-chunkvecs/stage2/{tools,req,traces,logs,bench,judge,sanity.json,changed.ids}, answers.{json,md}, CALLS.md, step0/.
**Step 0 (0 LLM, MacBook): simplewiki-only recovery.** MAIN 97, K1 kit (crypto + wikivoyage v2, simplewiki v3proto), K1 head pass a2 + `packDense2: true` (replaces K1's append-budget; one setting): **recovery 2/25 (vit-hum-003, vit-sci-001), losses 6/22** (lan-ref-002, lan-ref-003, lan-rsn-004, vit-cry-006, vit-cry-011, vit-trv-003); kept changed on 78/97, mean kept 2.77 -> 2.12. Every loss is a semantic neighbour that append-budget had added and fusion does not keep. Without the head pass: 0/25, 8/22. Rule (recovery >= 5, losses <= 2): both fail. Files step0/{main.dense2true.*.jsonl,score.*.json}.
**Sanity (216/216 per run, 0 empty, 0 errors, 0 loops).** Kept-list identity vs the replay (title/section/source sequence; traces carry no chunk ids): CTL 201/216 = 93.1 %, ARM 197/216 = 91.2 % (context:a->b code equal 213 / 200); raw lists 213 / 197; task 215 / 215. Causes as in the QFORM secondary: the real mmBERT detector fires (12 of 14 CTL / 14 of 14 ARM such items) on firstaid (11 / 12) and medlineplus (3 / 2) questions the replay's lexical one lets through and `grounding:health-strict` empties the kept list (14 + 14 items, not the same 14); other list differences 1 CTL, 5 ARM. Unchanged-context items (87) have identical answer text in both runs (seed 42, deterministic).
**Changed-context set 129 items** (kept titles, replay chunk ids or promptTokens differ; the replay says 127). 111 have different answer texts, 18 identical text (dU 0 by construction, not judged). Cap: 100 items x 2 arms x 2 orders = 400 calls; **not judged: the 11 F8 follow-up items with different answers** (F8 is the bench-engine artefact of the W74 correction); forms judged F0-F7. Judge judge.v1 Haiku 5.5-low N 4 both orders, reference = item gold + rubric, 0 retries.
| (100 judged changed items) | U [CI] | corr | use | CE (corr<=1.5) | warned | declined | out tok | total ms |
|---|---|---|---|---|---|---|---|---|
| CTL | 0.398 [0.333, 0.472] | 2.67 | 2.02 | 25 | 39 | 0 | 35 | 3070 |
| ARM | 0.524 [0.454, 0.600] | 2.96 | 2.34 | 17 | 34 | 0 | 36 | 3352 |
**Paired ARM - CTL: dU +0.125 [+0.049, +0.204] (item bootstrap B 2000 seed 11; fact-cluster CI [+0.044, +0.222]); d corr +0.29 [+0.05, +0.54]; ARM better / CTL better / tie 56 / 31 / 13.** Read: the screen (dU >= +0.02, CI low > -0.01) passes on the changed items. Diluted over all 129 changed-context items +0.091, over all 216 about +0.054 (indicative; unjudged items imputed at 0 and the mean reference). Whole-run cost: prompt tokens 306 -> 330 (+8 %), total ms 2570 -> 2709 per answer (two jobs ran in parallel), out tokens 29.6 -> 30.8.
2 x 2 gold kept (CTL / ARM; run flag where the kept titles match the replay, else empty = No; 3 items unknown):
| gold kept ctl/arm | n | U ctl | U arm | dU | CE ctl | CE arm |
|---|---|---|---|---|---|---|
| no / yes | 24 | 0.233 | 0.704 | +0.471 | 10 | 2 |
| no / no | 54 | 0.337 | 0.421 | +0.084 | 14 | 12 |
| yes / yes | 17 | 0.759 | 0.618 | -0.141 | 0 | 2 |
| yes / no | 2 | 1.667 | 0.606 | -1.061 | 0 | 0 |
The gain is the gold-gained cell (24 items); where both keep the gold the ARM is lower (it carries ~73 more prompt tokens and scores lower on 9 of 17, higher on 6), and the 2 items G loses drop U by 1.06 (n 2). Per form dU: F0 +0.244, F1 +0.001, F2 +0.187, F3 +0.094, F4 +0.208, F5 +0.087, F6 +0.163, F7 -0.033 (n 8-16, indicative). Per pack: factbook 0.213 -> 0.468 (CE 19 -> 10), firstaid 0.407 -> 0.583 (4 -> 3), medlineplus 0.524 -> 0.529 (2 -> 4).
**Verdict (exploratory):** chunk-level vectors do reach the reader: +0.125 U on the 100 changed items (about +0.05 over the whole 216), almost all from items that gain the gold, confident errors 25 -> 17. It is not a lever yet: the rule's junk bar (1.32x) and the funnel read fail (2/25 recovery, 6/22 losses on the K1 kit with fusion), only 3 of the 6 packs of the QFORM set have v3 files, and `true` loses the append-budget neighbours that K1 relies on (the untested combination is fusion + append-budget). One seed, dev items, agent-written gold, Haiku judge (Claude family, compresses gaps).

## Arm G, real items with the no-displacement setting (coordinator, 01:1x, 0 LLM; g-chunkvecs/step0/score.extra.*.json)
`packDense2` takes one value, so `true` (fusion) replaced K1's `append-budget` path and every "loss" was an append-budget neighbour; `"extra"` appends 2 dense-chunk slots after the retrieved list (ST2's design) and does not displace.
| setting (MAIN 97, K1 kit with simplewiki v3) | recovery /25 | losses /22 | kept lists changed |
|---|---|---|---|
| true, no head pass | 0 | 8 | 73 |
| true + head pass a2 | 2 | 6 | 78 |
| extra, no head pass | 2 | 1 | 65 |
| **extra + head pass a2** | **4** | **0** | 70 |
Reading: with the no-displacement setting the real-item no-harm clause holds (0/22) and recovery reaches 4/25 with chunk vectors on one of the three K1 packs only. Together with QFORM (G-extra +14.8 pts kept; G-true answers +0.125 U on changed items), the configuration to carry forward is **head pass a2 + packDense2 "extra" on packs that ship chunk vectors**. Still open: the answer screen for "extra" (only "true" was judged), chunk vectors for the rest of the kit (crypto, wikivoyage, visa), pack bytes (+2…25 %), and the phone cost of the chunk-vector scan.

## G2-FULLKIT reads (coordinator agent, 02:4x-04:2x 10-22, 0 LLM / 0 Opus / 0 paid / 0 phone; criterion sha dcac6f4b unedited; files g2-fullkit/{BUILD.md,reads.json,reads.md,run_main.sh,run_qform.sh,score_g2.py,runs/})
Build (mini M4 Metal, bge-small q8_0 ec38e8da, int8): visa 60 s, crypto 284 s, wikivoyage 2,464 s (222 chunks/s), total 2,808 s; chunk_vecs rows = chunks = source for all three, model sha and meta unchanged (+densechunk key), shas equal mini/MacBook (BUILD.md).
**Read 1 (MAIN 97, K1 tree, kit all-v3 = crypto + wikivoyage + simplewiki, {packHeadPass a2, packDense2 extra}): recovery 3/25 (vit-hum-003, vit-cry-010, vit-sci-001), losses 0/22, kept lists changed 70/97, mean kept 2.77 -> 2.45. Frozen rule (recovery >= 5 and losses <= 2): FAIL on recovery.** Reference simplewiki-v3-only was 4/0: the full kit lost lan-cmp-004 (a wikivoyage dense chunk, "North American wildlife", takes the slot "American bison" had) and gained vit-cry-010 (a changed Ethereum list; cause not traced); net, the crypto and wikivoyage vectors add no recovery over simplewiki-v3 alone (3 vs 4). Setting-only control (same settings, v2 kit, no chunk_vecs): 0/25, 5/22 losses (lan-exp-005, lan-hlt-003, lan-ref-002, lan-rsn-006, vit-trv-003), because "extra" has no append-budget neighbours to fall back on; the chunk vectors are what remove those losses (5 -> 0), not what raise recovery.
**Read 2 (QFORM 432, six separate A-union files, replay-sweep.ts = replay-qform + wallMs):**
| arm | hit@kept | junk-kept (x ctl) | mean kept | ctx tok | kept tok | wall ms/q |
|---|---|---|---|---|---|---|
| v2 six, settings off (control) | 117 (27.1 %) | 1.45 (1.00) | 1.59 | 288 | 169 | 226 |
| v2 six, K1 settings | 125 (28.9 %) | 2.06 (1.42) | 2.27 | 288 | 307 | 211 |
| **v3 six, a2 + extra** | **211 (48.8 %)** | 3.49 (2.41) | 3.38 | 372 | 457 | 261 |
Pooled v3 - v2off **+21.8 pts [item CI +18.1, +25.7; fact-cluster +16.4, +27.8], gained/lost 94/0**; vs the v2 K1 settings +19.9 [+16.2, +23.8] (86/0). Per form (of 48, v2off -> v3): F0 17->30, F1 6->9, F2 16->33, F3 6->17, F4 15->25, F5 30->41, F6 15->29, F7 10->24, F8 2->3. Per pack (of 72): factbook 9->22, firstaid 6->20, medlineplus 15->30, crypto 31->39, wikivoyage 41->51, visa 15->49. Junk set 252 items (gold not in the control's wide-12). Gold in raw 147 -> 265.
**Read 3 (costs):** bytes v2 -> v3: visa +3.8 %, crypto +53.1 %, wikivoyage +64.0 % (351.1 -> 575.9 MB), factbook +1.8 %, firstaid +25.4 %, medlineplus +6.1 %, simplewiki +53.1 %; all seven +55.2 % (915.8 -> 1,421.0 MB; the sidecar is a flat 388 B/chunk). Replay wall per query (MacBook, one run each, an iOS simulator app was burning a core during these runs): QFORM 226 -> 261 ms (+15 %), MAIN 225 -> 346 ms (+54 %, MAIN carries the 548k + 621k-chunk packs). Phone unmeasured; the on-device scan over 1.2 M int8 vectors is the open cost.
Prediction vs result: read 1 recovery 6-9 / losses 0-1 -> **3 / 0 (recovery missed)**; read 2 pooled +10...+16 -> **+21.8 (above)**; wikivoyage bytes +20...+25 % -> **+64 % (wrong, arithmetic of the flat 388 B/chunk)**; the answer screen was NOT started (rule: only if read 1 passes; the coordinator decides). Reading: on pack questions the full kit's chunk vectors give a large, harm-free first-stage gain (0 lost of 432), but crowding is 2.4x the control's junk-kept and context tokens +29 % (kept tokens x2.7), and on the real items the recovery bar is not met; the gain on MAIN is the removal of the "extra"-setting losses, not new recoveries. One seed-free deterministic replay, dev items, agent-written gold; nothing here moves the answer score.

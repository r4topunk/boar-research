# GROUND-ST step 0 gate — **FAIL at step 0 (G1 fact-chunk kept)**; G2 and G3 PASS for both variants; no variant enters stage 1 (2026-10-13 13:3x; criterion sha 895d1ebb…; 0 judge / 0 LLM / 0 paid; MacBook only)

| gate | rule | OFF → ground → top1 | ground | top1 |
|---|---|---|---|---|
| G1 chunk kept (180) | ≥ 55 | 43 → **51** → **53** | FAIL | FAIL |
| G1 article kept (180) | ≥ 85 | 68 → 89 → 92 | pass | pass |
| G1 chunk raw6 unchanged | = 67 | 67 → 67 → 67 (raw lists identical 180/180) | pass | pass |
| G2 lost-context (kit 170) | 0 | – → 0 → 0 | pass | pass |
| G2 empty kept, OFF-retrieving, v0.1 | ≤ 11 | 11 → 2 → 2 | pass | pass |
| G2 empty kept, OFF-retrieving, v0.2 | ≤ 28 | 28 → 2 → 2 | pass | pass |
| G2 v0.1 gold kept (39 gold) | ≥ 12 | 12 → 12 → 12 | pass | pass |
| G2 v0.2 resolvable gold kept (9) | ≥ 4 | 4 → 6 → 5 | pass | pass |
| G2 kit kept-list change share (170) | ≤ 15 %, add-only harmless | counted 0/170 → 0/170; **all changes 50/170 (29 %) → 62/170 (36 %), all add-only** | pass | pass |
| G2 context tokens ≤ cap (kit + 180) | 0 over | 0 → 0 (max kept tokens − budget: −24 v0.1, −19 v0.2) | pass | pass |
| G3 retrieval p50 (180) | ≤ 1.2 × OFF | warm OFF2 149.7 ms → 153.9 (×1.03) → 155.9 (×1.04); first OFF 169.3 | pass | pass |
| step 0 | G1 ∧ G2 ∧ G3 | | **FAIL** | **FAIL** |

Rule (criterion): the variant entering stage 1 is the passing one with the higher fact-chunk kept. Both fail G1, so the result is **FAIL at step 0**: no stage 1, no 4B generation, no judge. The D0 loss classes (D0.md) become the next hypothesis. The article line (+21 / +24) clears its bar; the chunk line (+8 / +10) does not.

Per pack, chunk kept / article kept / empty kept, OFF → ground → top1 (fact chunk raw6 / article raw6):
- qa-travel-se: 1/6/7 → 3/9/0 → 3/9/0 (8/13)
- qa-ethereum-se: 2/5/5 → 2/9/0 → 2/10/0 (3/11)
- qa-bitcoin-se: 1/2/5 → 1/2/0 → 1/3/0 (1/3)
- qa-health-se: 1/5/10 → 2/10/2 → 1/9/2 (4/12)
- qa-outdoors-se: 5/10/7 → 6/13/2 → 7/12/2 (8/15)
- boar-firstaid-en: 1/3/6 → 1/4/2 → 1/4/2 (1/4)
- boar-medlineplus-en: 10/11/4 → 11/13/1 → 12/15/1 (14/16)
- boar-factbook: 10/13/1 → 11/14/0 → 12/15/0 (13/17)
- boar-simplewiki-en: 12/13/3 → 14/15/0 → 14/15/0 (15/16)

Per family: SE (100 items): chunk 10 → 14 → 14; article 28 → 43 → 43; empty 34 → 4 → 4. Topic (80 items): chunk 33 → 37 → 39; article 40 → 46 → 49; empty 14 → 3 → 3.

Enter/leave on the 180: ground chunk +8/−0, article +21/−0; top1 chunk +10/−0, article +24/−0. Kept lists changed: 68/180 (ground), 85/180 (top1). Codes: ground kept-1 30, kept-2 38, none 95; top1 kept-1 82, kept-2 3, none 78.

Kit detail (all changes add-only, no OFF-kept chunk dropped): v0.1 12 (ground) / 14 (top1) of 60 changed, 9 of them empty → filled; v0.2 38 / 48 of 110 changed, 26 empty → filled; v0.2 all-gold kept (descriptive) 15 → 17 → 16.

Identity: OFF matches ST2's OFF replays (raw + kept + task/query/k/codes) on 180/180, 60/60 and 110/110, and DENSECHUNK-ST OFF on 60/60 and 110/110. OFF matches OFF2 everywhere. Raw lists are unchanged by both variants (180/180, 60/60, 110/110). The diag reconstruction agrees with the engine on 163/163 non-special items.

Tests (wt/groundst): `npx vitest run src/rag src/routing` gives 63 files and 823 tests: 821 pass, 2 fail. Both failures are deep-tier tests in depth.test.ts and answer.test.ts and fail identically on wt/packs, so they are pre-existing on the dt512 base. packGround.test.ts passes 5/5, including 2 new top1 tests. `npx tsc --noEmit` is clean.

Caveats:
1. The G2 change share passes only on the criterion's "add-only = harmless" clause. Counting every change gives 29 % / 36 % of kit items, above 15 %. Most changes fill an empty context with kit-pack passages (35 of 50 / 35 of 62 changed items), which is P4's known control-set behaviour.
2. In this engine, keepTop1's "first pack hit" covers kit-pack passages (crypto/wikivoyage). On the self-tests it was always raw position 0, which was not the fact chunk on the unrecovered items. It also pre-empts P4's two-passage fallback (qa-health-se article −1 vs ground).
3. G3 times retrieve() only. The keep step's extra compressContext call is not timed, but it runs in-process with no I/O.
4. Replays run on wt/groundst (wt/packs dt512 base + packGround), not on the cut 7 tree.
5. v0.2 was read by script only (counts, plus ids of the 9 resolvable items).

Files: tools/replay-gs.{ts,sh}, run_gs.sh, d0_gs.py, gate_gs.py; runs/gs-<pack>.jsonl, runs/v01-kit.gs.jsonl, runs/run_gs.log; blind/bench-v02/runs-packs/groundst-v02-kit.jsonl; aggregates/{d0-gs,gate-gs}.json.
Engine patch: packground2.vs-dt512.patch (sha 5fd74a85…). Files: settings.ts, answer.ts, packGround.test.ts vs dt512 979187fa. These diffs also carry wt/packs' packDense2/packRoute hunks, as with packdense2.vs-dt512.patch.

## Addendum 1 / X3 (packGround "perpack"; addendum sha 77eaf4ca…; 2026-10-13 14:1x) — **FAIL at step 0 (G1 chunk kept 54 < 55)**; G2/G3 pass; no variant enters stage 1

| gate | rule | OFF → ground → top1 → perpack | perpack |
|---|---|---|---|
| G1 chunk kept / article kept (180) | ≥ 55 / ≥ 85 | 43/68 → 51/89 → 53/92 → **54**/95 | **FAIL** (−1) |
| G1 chunk raw6 unchanged | 67 | 67 → 67 → 67 → 67 (raw identical 180/180) | pass |
| G2 lost-context (kit 170) | 0 | – → 0 → 0 → 0 (ids: none) | pass |
| G2 empty kept OFF-retrieving v0.1 / v0.2 | ≤ 11 / ≤ 28 | 11/28 → 2/2 → 2/2 → 2/2 | pass |
| G2 v0.1 gold / v0.2 resolvable gold kept | ≥ 12 / ≥ 4 | 12/4 → 12/6 → 12/5 → 12/5 | pass |
| G2 kit change share (170) add-only / other | ≤ 15 % counted | other 0 → 0 → 0 → 0; add-only 50 → 62 → **67 (39 %)** | pass (add-only clause) |
| G2 OFF-kept chunks cut by the pin | report | kit 0, 180 0 (packground:cut-N never emitted) | – |
| G2 tokens over cap (kit + 180) | 0 | 0 → 0 → 0 → 0 | pass |
| G3 keep-step p50 (180, in-engine) | report | warm OFF2 0.518 ms → perpack 0.891 ms (×1.72; first OFF 0.665) | – |
| G3 retrieval + keep p50 (180) | ≤ 1.2 × OFF2 | 156.1 → 153.8 ms (×0.99); kit v0.1 ×1.06, v0.2 ×0.97 | pass |

Verdict (addendum rule: highest chunk kept among variants passing G1–G3): ground, top1 and perpack all fail G1, so **FAIL at step 0**. No stage 1 (and no v0.1 quality no-harm run), no 4B generation, no judge. Per pack, perpack chunk/article/empty: travel 5/12/0, ethereum 2/10/0, bitcoin 1/3/0, health 1/9/2, outdoors 6/11/2, firstaid 1/4/2, medlineplus 12/15/1, factbook 12/16/0, simplewiki 14/15/0. SE: 15/45/4. Topic: 39/50/3. Enter/leave on the 180: chunk +11/−0, article +27/−0. Kept lists changed on 101/180. Kit: v0.1 17/60 changed (9 empty → filled), v0.2 50/110 (26 empty → filled), all add-only; v0.2 all-gold kept 15 → 16.
Keep-step timing = engine wall time from the first retrieve() return to the sources event (or the stubbed generate call) inside the replay (`keepMs`). Identity: perpack-run OFF = step-0 OFF = ST2 OFF on 180/180, 60/60, 110/110; OFF = OFF2 everywhere. Tests: vitest src/rag + src/routing 826 tests, 824 pass, 2 pre-existing deep-tier failures (as step 0); packGround.test.ts 8/8 (3 new perpack tests); tsc clean. Patch packground2.vs-dt512.patch updated (sha 9acb5160…).
Files: tools/run_gs.sh (`GS_VARIANT=perpack`); runs/gs-<pack>.perpack.jsonl; runs/v01-kit.gs.perpack.jsonl; runs/run_gs.perpack.log; blind/bench-v02/runs-packs/groundst-v02-kit.perpack.jsonl; aggregates/{d0-gs,gate-gs}.perpack.json.

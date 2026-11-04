# Errata from poidh bounty 1520

TL;DR: poidh bounty 1520 asked for audits of this record and of the LabRat app. Eight items below were confirmed or mostly confirmed by an independent verification pass. The headline holds: 0 of 71 wins under both judge families, U-total 0.165 (Claude) / 0.242 (gpt-5.6-sol). No item moves those numbers except the current-city stratum (E4), which is a breakdown row the spec required and the record did not print. What does change: phone health figures (M1 refusals, M2, M3) describe the eval runner and not the app's path (E1); one interpretive sentence (F-2217) is unsupported (E2); two summary sentences say more than their evidence (E5, E7); the experiment registry has inconsistent rows and a filtered count (E6); and the pooled CR/CE fields in `m1.json` are computed wrongly (E3). E8 is a reading note, not an error.

Policy (`CONTRIBUTING.md`): the record is closed, so the original files are not rewritten. This file is the correction. Pinned commit for code references: LabRat (`r4topunk/labrat-boar-fork`) `0ecd282d`, identical lines at `0ad476ca` unless stated. Record references are to this repository at v1.1.2 (`0590f3c`).

Claim ids are poidh claim ids (on-chain id = claim id − 5316). Each item lists only what the verification confirmed. Where a claim overreached, the verifier's correction is stated. Listing a claim here says only that it reported the item. It does not rank claims.

| # | Affected | Headline change | Reported in | Fix branch |
|---|---|---|---|---|
| E1 | F-2241, F-2242, DEVICE-FINAL M1 refusals, `m34_agg.py` | none on U-total or 0/71 | 9243, 9221 | LabRat `fix/1520-eval-runner-pack-ids` |
| E2 | F-2217 (last clause) | none | 9227 | none (record text) |
| E3 | `aggregates/m1.json` pooled CR / CE | none (fields not cited) | 9225 | none (record tool) |
| E4 | DEVICE-FINAL M1, F-2238 (missing stratum row) | stratum row only | 9336 | none |
| E5 | F-2236 caveat, `llms.txt` | none | 9335 | none |
| E6 | `data/experiments.json`, `llms.txt` count | none | 9228, 9326 | none |
| E7 | F-2238 "answer coverage 0.90" | none | 9300 | none (see boar-bench `fix/1520-score-bar-verdict` for the scorer) |
| E8 | reading of U-total on v0.4 | none (reading note) | 9328 | none |

## E1. Phone health figures were measured through the eval runner's pack ids, not the app's path

- **Affected:** F-2241 (M2 "53 of 65 fixed text"), F-2242 (M3 19/60 health refusals and the own-article split 0.476 vs 0.293), DEVICE-FINAL M1 refusals (5 items on the phone vs 3 on the desktop twin, `DEVICE-FINAL.md:35`), `arms/device-final/tools/m34_agg.py:29`.
- **What the record says:** the phone figures are LabRat measured on the phone; the M1 phone/desktop difference is a "parity read" (`DEVICE-FINAL.md:34`); M2 phone 53 / 0 / 12 vs desktop 41 / 1 / 23 (`DEVICE-FINAL.md:48`).
- **What is true:** the on-phone eval runner opens every pack as `local-<file>` (`DeviceEvalRunner.kt:257,261`). `HealthGate.packOf` reads the id after `pack:` and does not strip `local-` (`HealthGate.kt:22`), so `HEALTH_PACKS` (`HealthGate.kt:17`) never matches on the runner and the gate can never be opened by a health pack there. The app itself opens catalog packs under their catalog ids (`BoarServices.kt:145-147`) and its chat path uses those packs (`BoarServices.kt:181`), so the shipped app licenses as designed. The desktop twin (`arms/native-rc/tools/harness-lite`) mirrors the app's ids. The phone health numbers therefore measure a stricter gate than LabRat ships:
  - M1: the 5-vs-3 refusal gap is exactly cw-021 and cw-025, which keep `boar-medlineplus-en` on the desktop and get the fixed text on the phone in both seeds.
  - M2: phone 53 fixed = desktop 41 fixed + 11 desktop model answers with a health-pack source kept + n08's exposure answer (source null, so fixed). The 12 phone model answers are exactly the 12 probes with `isHealth = false`. The app would show about the desktop's 41 / 1 / 23.
  - M3: phone 19 of 60 health-pack self-tests fixed vs desktop 12; the 7 extra are st-boar-firstaid-en-002/003, st-boar-medlineplus-en-006/007/008, st-qa-health-se-015/019.
  - Fixed turns are logged with empty `retrievedTitles` (`AnswerPipeline.kt:181` emits `Done(fixed, emptyList(), …)`; `DeviceEvalRunner.kt:383`), so `m34_agg.py` marks them `own_kept = False`. Its title regex (`m34_agg.py:29`, `^[^:]{3,40}: `) strips only the first prefix, so double-colon Stack Exchange titles (st-qa-outdoors-se-002) never match. Both bias the F-2242 split.
  - The runner also orders packs by file name, the app by catalog order (not measured for its effect; M1 U parity suggests it is small).
- **Evidence:** code lines above at `0ecd282d`; the M1/M2/M3 decompositions were re-derived by the verifier from the phone outputs and the desktop replays (`device-final/aggregates/m2.json` vs `searchport/replays/A2nh/probes.jsonl`, `df-m3-packproof-s42` vs `A2nh st.on-k13`).
- **Headline:** U-total and 0/71 stay as published (they are what the runner measured). Counterfactual only, not a re-measurement: giving the phone the desktop answers for cw-021 and cw-025 adds about +0.006 (Claude) / +0.008 (gpt-5.6-sol) per seed. The safety and refusal figures F-2241 and F-2242 overstate the shipped app's conservatism and should be read as runner figures.
- **Verifier's corrections:** claim 9243's corrected F-2242 split (0.448, n 87 vs 0.321, n 53) does not reproduce from its own item list (89 / 51 gives 0.438 vs 0.333); a desktop-kept proxy gives 0.424 vs 0.354, the regex fix alone 0.470 vs 0.298. The phone's kept lists on fixed turns were not logged, so no single corrected value exists. Claim 9221 first saw that cw-021 and cw-025 are the whole M1 refusal gap and that the phone never licenses a probe; its explanation (the MedlinePlus chunk dropped out of the phone's kept list) is not the cause.
- **Reported in:** poidh bounty 1520 claim 9243 (https://files.catbox.moe/txgr88.md); claim 9221 (https://github.com/devx-agent/boar-healthgate-audit).
- **Fix:** LabRat branch `fix/1520-eval-runner-pack-ids` (runner pack ids). The phone M2/M3 figures were not re-run.

## E2. F-2217: "with the information present, the 1.7B does not deliver it" is not supported

- **Affected:** F-2217 (`data/facts.json:53042`), last clause; its AVAILABLE / PARTIAL / NONE strata (also emitted as `factavail` in `aggregates/m1.json`).
- **What the record says:** Claude U-total 0.164 where the installed packs hold the answer (n 19), 0.174 partly (n 25), 0.155 not at all (n 27), "with the information present, the 1.7B does not deliver it".
- **What is true:** FACT-AVAIL labelled checklist points against six A∪ packs only (`ruler/factavail/FACT-AVAIL-criterion.md:7`). The engine measured (K13 kit) read from thirteen. Of the 335 passages kept over the 71 headline items in the desktop twin run, 255 (76 %) come from packs FACT-AVAIL never searched (`boar-simplewiki-en` alone 182). The strata therefore do not say whether the information reached the model, and the sentence does not follow from them. The spec had already warned that the split is "not a with/without contrast" and not an estimate of the information effect (`RULER-SPEC-v1-r4-2026-10-21.md:61`), and it asked for labels per installed set (l.59), which was not done for K13.
- **Evidence:** recount of `turns[].kept[].chunkId` in `arms/native-rc/work/v04/lite-s42.jsonl` (traces dataset): 335 kept, by pack simplewiki 182, qa-travel-se 34, crypto 31, factbook 19, wikivoyage 18, wiki-vital5 15, qa-money-se 11, medlineplus 8, qa-outdoors-se 6, qa-health-se 5, firstaid 4, qa-cooking-se 2; A∪ packs 80, others 255.
- **Headline:** none.
- **Verifier's corrections:** the claim's relabelling by what reached the prompt (≥ 1 point in the prompt 0.290 vs none 0.113 Claude, +0.177, CI about +0.07…+0.28) reproduces from its labels, but it is an observational, different-items contrast (within family it shrinks to +0.097), from one labeller whose "no" labels were not checked. It supports dropping the F-2217 clause; it does not establish "retrieval is the wall". The causal ORACLE / ORACLE-0 rows were never run for RULER-FINAL.
- **Reported in:** poidh bounty 1520 claim 9227 (https://github.com/swiftbotlab/boar-research-audit; the repository was unreachable at verification and a mirror of the same files was read).
- **Fix:** none; read F-2217 as the three strata numbers without its last clause.

## E3. `m1_agg.py` thresholds CR / CE after pooling seeds; `m1.json` still emits the pooled values

- **Affected:** `arms/device-final/aggregates/m1.json` → `pooled` → `CR`, `CE_answered` (and the stdout line, `m1_agg.py:98`).
- **What the record says:** `DEVICE-FINAL.md:31` withholds pooled CR ("pooling orders across seeds distorts the ≥4 count") and leaves pooled CE blank, but `m1.json` carries pooled G1 CR 0.1395 / CE 0.2576 and G2 CR 0.1681 / CE 0.2273.
- **What is true:** `pool()` concatenates every seed's judge orders (`m1_agg.py:66-71`) and `st()` averages correctness once and then thresholds `ca >= 4` / `ca <= 1.5` (`m1_agg.py:25-30`), so an item correct in one seed and not the other drops out. The seed mean (equal to the per-item average of the per-seed bits) is CR 0.182 (G1) / 0.256 (G2); G2 CE is 0.250, not 0.227. G1 CE is unaffected (0.2576).
- **Evidence:** recomputed from the DEVICE-FINAL judgments and traces: G1 CR s42 0.1860, s43 0.1783, mean 0.1822, pooled 0.1395 (6 items lost: cw-001, cw-006, cw-017, cw-039, cx-018, cx-039); G2 CR 0.2689 / 0.2437, mean 0.2563, pooled 0.1681 (11 items lost); G2 CE 0.2424 / 0.2576, mean 0.2500, pooled 0.2273.
- **Headline:** none. U-total is linear in the scores, so pooling is valid for it; the per-seed CR / CE in `DEVICE-FINAL.md` are correct; no fact cites the pooled fields.
- **Reported in:** poidh bounty 1520 claim 9225 (https://api.thegraph.com/ipfs/api/v0/cat?arg=QmbUdMWkdCSuPNobigkwPvdP2RcPY5pf1EcoQxsQq2ig5W).
- **Fix:** none in place; read pooled CR / CE in `m1.json` as invalid and use the seed means above.

## E4. The spec-required current-city stratum was not printed

- **Affected:** DEVICE-FINAL M1 (`DEVICE-FINAL.md:20-31`), F-2238.
- **What the record says:** nothing; the M1 table has no current-city row and no "no location input" note.
- **What is true:** `RULER-SPEC-v1-r4-2026-10-21.md:52` requires U-total printed with and without the 7 items that carry a device location (cw-027, cw-028, cw-029, cx-027, cx-028, cx-029, cx-038; weight 7 of 65.5, 10.7 %), and a plain headline note when the RC has no location path. LabRat has no location input, so under the spec's fallback (l.36) the 7 went in as written: the request files carry no `context`. `m1_agg.py` has no such set; the NATIVE-RC aggregation did print "U without the 7".
- **Evidence:** recomputed on the pooled seed 42 + 43 judgments, health weight 0.5, refusals zeroed:

  | family | with the 7 (headline) | without the 7 | the 7 alone |
  |---|---|---|---|
  | Claude | 0.1645 | 0.1717 | 0.1006 |
  | gpt-5.6-sol | 0.2424 | 0.2463 | 0.2000 |

  Required note: "LabRat has no location input (0 of 7 requests carried one); RULER-SPEC r4 l.36 fallback applied."
- **Headline:** the verdict uses "with" and stands; the stratum row is +0.007 (Claude) / +0.004 (gpt-5.6-sol); both rows are far below 0.50.
- **Verifier's corrections:** the 7 are not unanswerable by construction (cx-038, cx-028 and cw-029 name the place in the text, and the phone scores above zero there); with the 7 at their own reference level the ceiling is 0.255 / 0.309, not the claim's 0.266 / 0.325.
- **Reported in:** poidh bounty 1520 claim 9336 (https://github.com/mak777uh/boar-audit-location-stratum).
- **Fix:** none; the row above is the missing breakdown.

## E5. "No gain on real development items" holds for cell (a) only

- **Affected:** F-2236 caveat (`data/facts.json:53561`), the same sentence in the site's `llms.txt`, and the `[F-041]` citation next to "most with a pass/fail rule frozen before the run" in `llms.txt`.
- **What the record says:** "no gain on real development items (F-2080)".
- **What is true:** FACTPRESENT tested real items in several cells. The self-test gain is not reproduced in cell (a), the fact added by the pack (`ruler/FACTPRESENT-2026-10-21.md:10,132`). Cell (b), fact already in K0 and K3 adding context, is positive: K3 − K0 +0.059 (+0.022…+0.093), n 13 (l.18). The record itself calls (b) a lead, not a finding (l.21), and lists a second-seed check of (b) as "not run" (l.136-138). So the correct summary is "the self-test gain does not reproduce on real items in cell (a); one post-hoc positive subgroup (b) was not retested". Separately, `[F-041]` is the arm-count fact (159 records from 101 arm folders), not a source for pre-registration.
- **Headline:** none.
- **Verifier's corrections:** (b) is post hoc, one of about 20 cells, one seed, Haiku judge; other pooled real-item pack effects are null, so (b) does not contradict the overall reading. The retest is a desktop replay plus judge calls, not 26 phone runs.
- **Reported in:** poidh bounty 1520 claim 9335 (https://github.com/mak777uh/boar-audit-cell-b).
- **Fix:** none; read F-2236's "no gain on real development items" as "cell (a)".

## E6. Experiment registry: contradictory verdicts, inherited results, and the headline count

- **Affected:** `data/experiments.json`; the site's `llms.txt` "387 recorded experiments (215 ended without a gain)".
- **What is true:**
  1. Six rows have `verdict: adopted` while their own `verdict_detail` and closed row say closed or not adopted: X-019 VG4-S2 (R57), X-052 FOLLOWQG (R63), X-055 HFUFIX (R61), X-056 HFUFIX2 (R62), X-084 DEEPSPEED (R36), X-182 LITEREACH2-180 (R91). Read them as `closed`: adopted 51, closed 193.
  2. Rows that share a closed-registry row inherit its result string, including judged numbers on rows that made no judge calls. Checked cases: X-120 DENSECHUNK and X-143 DENSECHUNK-ST (both `judge: none (deterministic gate)`; X-143's detail says "0 judge calls"; X-120 is n 32 on v0.2) carry +0.017 (−0.000…+0.035), which only X-144 DENSECHUNK-ST2 measured (R46); X-032 PROMPTDIET ("never ran L1") carries "quality −0.016" from X-061 SPEEDPACK (R7); X-065 DEEPPAR (10 greedy prompts) carries X-066 DEEPPAR-L1's judged Δ and CI (R16); X-154 STACK (step-0 fail) carries X-155 STACK-2's CI (R49). Treat a judged result on a `judge: none` row as the sibling row's number.
  3. The count is 387 of 402 registry rows (the 15 withheld rows are disclosed only in `data/SCHEMA.md` and the v1.1.2 entry of `CHANGELOG.md`). 215 = closed 187 + not-detected 28; not-detected is defined in the registry as "not evidence of no effect", and parity (10, "not a gain") is left out. By the registry's own definitions: 387 public of 402; closed 187 (193 after item 1), not-detected 28, parity 10.
- **Evidence:** recount of `data/experiments.json` at v1.1.2: 387 rows, ids X-001…X-406 with 19 numbers unused; verdicts closed 187, adopted 57, measurement 57, tooling 32, not-detected 28, open 16, parity 10. Rows sharing a closed row and a result string (excluding "n/a"): 11 groups, 33 rows; not all of them are wrong (several are arms of one screen), the cases listed in item 2 are.
- **Headline:** none (0 of 88 v0.4 turns touch these rows).
- **Verifier's corrections:** claim 9326's "13 groups / 32 rows" depends on how identical results are grouped; the provenance defect is real, the size depends on the definition. Its point that X-111 THINK4B was closed on one seed is self-disclosed in the row, and the record's own v0.2 follow-up (+0.009, NO) is the relevant evidence, so that point is not an erratum. Claim 9228's registry part is right; its currency part concerns app code, and its "1000×" reading of `12.000` is locale-ambiguous (in English `12.000` is twelve; only the upstream Portuguese mode read it as thousands).
- **Reported in:** poidh bounty 1520 claim 9228 (https://github.com/nicoarias81/labrat-currency-audit-1520), items 1 and 3; claim 9326 (https://beige-impossible-dragon-883.mypinata.cloud/ipfs/QmdXpAhXSJVbtJiV58PK55VbjsLn7eGNc64XJrvyqvJQan), items 2 and 3.
- **Fix:** none in place; the currency code from claim 9228 is handled in LabRat branch `fix/1520-calculators` (app code, not part of this record).

## E7. F-2238 "answer coverage 0.90" is kept-source coverage

- **Affected:** F-2238 (`data/facts.json:53604`), last clause.
- **What the record says:** "5 headline items were refusals; answer coverage 0.90".
- **What is true:** 0.90 is `coverage = mean(bool(kept))` over the 71 headline items (`m1_agg.py:42`), the share of items where retrieval kept at least one source (64 of 71), as in `DEVICE-FINAL.md` (column "coverage"). It is retrieval (kept-source) coverage, not the share of answered items. All 71 items have both judge orders in all four judgment files, and U-total is computed over all 71 with the 5 refusals at zero.
- **Headline:** none.
- **Verifier's corrections:** claim 9300 read 0.90 as 64 answered of 71 and inferred that answered items were dropped from U; that is not the case. Only the label is wrong.
- **Reported in:** poidh bounty 1520 claim 9300 (https://telegra.ph/boar-bench-reproduction-audit-the-public-scorer-applies-the-050-bar-to-a-raw-ratio-11-02).
- **Fix:** none here. The same claim's scorer finding (the bar verdict applied to the raw ratio in `boar-bench` `scorers/score.py`) is handled in boar-bench branch `fix/1520-score-bar-verdict`.

## E8. Reading note: on v0.4 the reference sits at the ceiling

Not an error; a property of the ruler that the record did not quantify for DEVICE-FINAL.

- On the DEVICE-FINAL judgments (71 items × 2 orders × 2 seeds = 284 rows per family) the judge names the reference the winner in 567 of 568 rows (Opus 284 / 284; gpt-5.6-sol 283 / 284, the exception cw-038 seed 42, where the phone also scored lower).
- The reference's weighted mean of (rubric − 1) is 3.88 (Opus; `m1.json` `abs_ref` 3.882), so U-total is close to (app mean rubric − 1) / 3.88 and the 0.50 bar is about a mean rubric of 2.94 out of 5.
- Dimension split (Opus, unweighted, no zeroing, (app − 1) / (reference − 1)): correctness 0.398 (2.479 vs 4.715), completeness 0.052 (1.204 vs 4.940), usefulness 0.079 (1.317 vs 4.996). For gpt-5.6-sol: 0.414 / 0.132 / 0.189. The gap is mostly coverage of the reference's points, not correctness.
- **Headline:** none; 0/71 and U-total reproduce exactly. Win-rate saturation on the older ruler was already in the record (RND-REVIEW B1); this note gives the v0.4 numbers.
- **Reported in:** poidh bounty 1520 claim 9328 (https://gist.github.com/mak777uh/4d0333d308a0b5afe729f0e89fb58af9).

## Related code fixes (outside this record)

These concern LabRat or boar-bench code, not the record, and are listed so the errata and the fixes can be read together. Links are added when the pull requests open.

| branch | repository | claim(s) |
|---|---|---|
| `fix/1520-eval-runner-pack-ids` | LabRat | 9243, 9221 |
| `fix/1520-health-terms` | LabRat | 9221 |
| `fix/1520-calculate-misroute` | LabRat | 9310 |
| `fix/1520-calculators` | LabRat | 9228, 9247 |
| `fix/1520-fts-upsert` | LabRat | 9236 |
| `fix/1520-score-bar-verdict` | boar-bench | 9300 |

# LEDGER-AUDIT 2026-10-13 (v2) — cross-ledger audit of the research corpus (workflow rnd-ledger-audit; synthesis opus/high on the COMPLETE input + completeness critic opus/high; companions: ARM-INDEX-2026-10-13.md, arm-index-2026-10-13.json, proposals/LEDGER-FIXES-2026-10-13.md — the latter corrects two readings below: criteria without sha = 5 files + 4 root (the other names have no criterion file); LOSSMAP was re-saved after its sha was taken, before its single commit, not edited after the freeze)

Precomputed counts: {"arms": 159, "by_status": {"closed: FAIL at L0 (bar 1 data review 84.0% vs >= 98% with currency/plug errors; bar 2 blind trigger recall 80/100 vs >= 90%, false fires 0/100 PASS); bars 3-5 PASS; CF NOT adopted; 0 judge calls": 1, "closed (descriptive arm): G1 FAIL as frozen (39/69 = 56.5%, bar <= 5%), G2 PASS (1/102 = 1.0%), G3 PASS (0/0/0). Reading: the gate is fine (true gate miss 1/69, v1-055); the G1 shortfall is kit coverage; no gate-fix arm": 1, "closed: NO by the frozen rule (ratio 0.620 < 0.700; correctness 3.10 vs >= 3.80; confident-wrong 7 → 15 vs allowed +2)": 1, "closed (measurement): 'cost small' per the frozen strict reading (|Δ| 0.016 < 0.03, CI high < 0, not a near-miss); top-1 routing closed at the product level (confirms R48); Opus L2 later confirmed −0.019 (−0.035…−0.003) via PACKS-L2": 1, "closed (step-1 coverage gate NO; 'Line closed at step 1', QUEUE l.796)": 1, "closed (L1 FAIL on target gate, not adopted; stop rule: no revision after L1)": 1, "parked (NOT ADOPTED as frozen: G2 FAIL on 1 of 3 fictional probes; G1 and G3 pass; QUEUE l.702 'parked for after the claim (PR phase), with a broadened phrase list as a new freeze')": 1, "lever-adopted (shipped in cut 4 on gates (1)+(2) per criterion; device gate (3) still open, never reported)": 1, "lever-adopted (L0 PASS, L1 PASS vacuously with empty changed set; shipped in cut 4, later extended by INSTANT-SUBJ)": 1, "closed: NOT ADOPTED as cut 5 (G3 FAIL 1.071x vs bar <= 0.800; G1/G2/G4 PASS); perf arms parked for a device ABBA (QUEUE.md:699 A/B 0.445x confounded); components 2+3 adopted via CUT5-LITE": 1, "lever-adopted (cut 5 = device-day candidate; later the base of cut 6 = cut 5 + DETMAX, QUEUE.md:694, and so of cut 7)": 1, "lever-adopted (claim build cut 7, adopted on gates alone under the zero-fire clause, CUT7-criterion.md:11)": 1, "closed: KILLED. L0 FAIL (6 regressions, bar <= 2) → revision 1 → ship gate FAIL (3 regressions, bar <= 2) → stop rule (QUEUE.md:596). The computed-verdict family (CV/CVS/CVH/CVO) was closed later (QUEUE.md:604, 618)": 1, "closed (gate #3 PASS, v0.1 EN L1 FAIL on 2 gates; killed by the no-revision stop rule)": 1, "closed (Step 1 v0.1 EN L1 FAIL on 3 of 5 gates; Step 2 never started by the stop rule)": 1, "closed (Step 1 L1 PASS vs the same-day control; Step 2 fresh blind gate #4 FAIL, +6.0 pp < +8 bar; killed by the stop rule)": 1, "closed (NO for every selector)": 1, "closed: NO at the slice (Haiku +0.005 sent it to Opus under l1_futility; Opus Δ −0.027, correctness −0.11). Full v0.2 110 and V-para s42 58 generated but unjudged; verdict strength slice only (n = 20)": 1, "closed: gate FAIL at step 0 (0 judge calls; deterministic retrieval replay on public v0.1)": 1, "closed: NO at the slice (Haiku only, not a near-miss; no full set, no Opus)": 1, "closed: NO at the slice (Haiku only; stop after stage 2, no full set, no Opus)": 1, "closed: NO at the slice by the criterion rule (Haiku only; CI −0.069…+0.048 straddles 0 and includes +0.03, so CLOSED.md labels it 'not detected')": 1, "closed at step 0 (jev gate FAIL: hedged 11 → 11; instruction fired on 0/11 hedged items)": 1, "closed — NO at the slice (slice-only verdict; full 110 and V-para not run)": 1, "closed — RETRIEVAL-MATTERS (diagnostic; stage 3 not needed since Δ ≤ −0.03)": 1, "closed — FAIL (D4 (a)+(b)); superseded for planning by DEEPPAR-L1 TRANSFER": 1, "closed — TRANSFER (judged parity; equivalence shown, not a lever)": 1, "INCONCLUSIVE (frozen band 0.606 ≤ x < 0.660; deep35 R450 0.6345); CLOSED R15 records it as 'not detected at MDE 0.055'": 1, "closed (FAIL at step 0: gold enters the deep top-6 on 2 items; gate ≥ 5; 0 judge calls)": 1, "closed (descriptive, no verdict rule; routing family closed in CLOSED R28)": 1, "closed (descriptive, no verdict rule; folded into routing family R28)": 1, "closed (descriptive, no verdict rule; routing family CLOSED R28)": 1, "closed (NO at the slice for both Q and P; CLOSED R26: Q closed, P borderline)": 1, "closed: no knob adopted, P0 flags unchanged (K1/K2/K4 BROKEN 8/10 items differ, K3 IDENTICAL-NO-GAIN 0.94x)": 1, "lever-adopted (thinking on the deep tier adopted; budget later moved 1024 → 512 by DT512); L1 PROMOTED on the Δ clause": 1, "closed: NO / NOT PROMOTED at L1 (budget 3072 adds nothing over 1024); CLOSED R22 labels it 'not detected at MDE 0.06 (51, 1 seed, Haiku)'": 1, "NO at L1 by the frozen rule (Haiku Δ +0.027 < +0.03; stands); effect later sized positive on Opus by Addendum 1 (+0.045 raw), which prompted the L1-PROTOCOL near-miss rule": 1, "measurement-only (no verdict); bar reading NOT met: floor-adj 0.514 (0.475–0.554), CI low < 0.50, win-rate 0/110 ×2; point above, CI straddles on burnt/dev v0.2": 1, "closed (measurement): Stage 1 V-para PROMOTED (Haiku Δ D−C +0.036) and Stage 2 v0.2 PROMOTED (+0.032). Under Opus the deep tier is below the bar by 0.171 on V-para and by 0.043 on v0.2; win-rate 0 on both": 1, "closed: NO at the slice (corpus size closed for the deep tier on the desktop)": 1, "closed: FAIL at step 0 (G2 no-harm; G1 and G3 PASS); 0 judge calls": 1, "not decided at MDE 0.03 (Opus L2 Δ CI through 0) → parked; format v3 not shipped": 1, "closed (diagnostic): decision rule met through the S3 clause only (S1/S2 0/60; S3 1/60 mismatch). Led to DETMAX": 1, "lever-adopted (ADOPT, all five gates pass) → cut 6 = cut 5 + DETMAX": 1, "closed (CHEAPER-PARITY; 512 kept as a local engine recommendation, not in a claim cut)": 1, "closed (CHEAPER-LOSS)": 1, "closed (measurement only; no verdict rule)": 1, "tooling (analysis-only, 0 judge calls; no verdict changes)": 1, "GO by the letter (step 1 at 8/60, G2-G5 pass); r1 superseded by r2 the same day": 1, "closed (gated rework passed; superseded by r3)": 1, "lever-adopted (ADOPT by frozen criterion, research-only; reached the claim build via r6 in cut 7)": 1, "closed (measurement only; set became dev after r3)": 1, "closed (direction confirmed on precision; recall open; set 2 dev after r3)": 1, "closed (FAIL on the fresh-precision gate before the blind set; set 3 untouched)": 1, "closed (FAIL on blind set 3: recall 60 % < 75 %)": 1, "closed: FAIL on blind set 4 (recall 70 % < 75 %); r6 kept as head by coordinator and shipped in cut 7 via CUT7 (0 fires on v0.2/V-para)": 1, "closed (dev probe, not adopted; r4to 'LCRELAX NO, FACTS stays at r6')": 1, "closed (diagnostic decision rule NOT met)": 1, "closed (NOT ADOPTED: G3 FAIL 45 % < 60 %)": 1, "closed (VIABLE by the letter; 1k proposed, then run as FTDATA-1K)": 1, "closed (FAIL on the strict review bar; LoRA not authorised)": 1, "closed (FAIL; grounded-reading fine-tune DATA line closed for now)": 1, "closed (screen FAIL on quality only; stop rule ends G4E4B; G4ENG later declared post-screen)": 1, "closed (FAIL on 5 gates, not adopted, G4ENG ended)": 1, "closed: FIDELITY OK (tooling/harness fidelity check, no judge)": 1, "closed: FAIL at step 0 (G1 chunk kept 51/53 vs ≥ 55). Family closed after addendum 1; X3 carried into STACK as a declared component per ledgers.": 1, "closed: FAIL at step 0 (G1 chunk kept 54 < 55). Family closed at step 0 (CLOSED R47); X3 carried into STACK as a declared component by coordinator decision.": 1, "lever-adopted (judge protocol: Haiku 5.5-low adopted as L1 judge, 4/4 bars; addendum applied to L1-PROTOCOL.md:11)": 1, "diagnostic complete (closed): decision rule (>= 10% lost) met, 69/100, so the fix arm HFU-FIX was built": 1, "closed: NOT ADOPTED as frozen (G3 58.1% < 90%; G5b 4/20 vs 0, pre-existing). The rescue HFU-FIX2 also failed, so the family is closed with no further rescue (QUEUE.md:690).": 1, "closed: NOT ADOPTED. The HFU-FIX family is closed with no further rescue (HFUFIX2.md:5; QUEUE.md:690).": 1, "closed: FAIL (strict review 6/20 vs bar <= 2/20; numeric fidelity also failed for HAGRID 0.9640 and Dolly 0.8482)": 1, "lever-adopted into cut 4 (L0 PASS, uninformative gate; QUEUE.md:647)": 1, "measurement (calibration, no GO bar): usable for triage/ranking, not for the headline ratio": 1, "measurement complete (no verdict by design); sigma_judge ≈ 0.003 raw / 0.004 floor-adj": 1, "closed: FAIL at step 0 (greedy-agreement gate); parked as a device-speed candidate": 1, "PASS all gates → ADOPT as a device-day candidate (device speed/swap untested; not in any cut)": 1, "tooling / control run (no criterion, no verdict by design)": 1, "closed (descriptive measurement done; no LEVER/NO verdict by design, criterion stage 4; CLOSED.md:11 lists it as a measurement)": 1, "closed (measurement done, backlog re-ranked 10-11; per-path addendum 10-12)": 1, "closed (FAIL on both gate types for Qwen3-4B and for Laya zero-shot; jev stays; Laya fine-tune parked)": 1, "not run: draft criterion never frozen or authorised (FTDATA 1k strict review FAIL 16/20, then the data line closed after FTDATA-REJ 11/20); superseded by SFT4B (H10)": 1, "closed (Verdict: NO by the frozen GO rule; Δ vs deep35 +0.007 not ≥ +0.03)": 1, "closed (Verdict: NO by the frozen GO rule; Δ vs deep35 +0.018 not ≥ +0.03)": 1, "closed (NO at the slice by the L1 futility rule: Δ ≤ 0 and h2h ≤ control; full 110 and Opus not run)": 1, "closed (NOT ADOPTED as frozen: G2c breadth gate FAIL 15/60 vs ≤ 12; G3/G4 not run by stop rule)": 1, "closed (NO at step 0: gate A failed, 3/110 kept 2.7 % < 5 % and 10/110 raw 9.1 % < 15 %; 0 judge calls)": 1, "closed (FAIL at the 0-call gate, 2026-10-12 14:21)": 1, "lever-adopted (USABLE at N = 4; Opus L2/claim judging may run 4 shards; 2026-10-08 13:33)": 1, "running (stage 0 PASS; stage 1 ORACLE-ADD generation 138/180 at 21:57, ORACLE-ONLY not started, 0 judge calls; no ORACLE-ST.md yet)": 1, "measurement (done; Addendum 1: all PACKCOND numbers on above_min from 10-12 21:0x)": 1, "measurement (done)": 1, "closed (FAIL at the step-0 replay gate, 2026-10-12 20:37; packGround off, no judge calls; later re-tested on the 180 self-tests as GROUND-ST, CLOSED R47)": 1, "closed (FAIL at step 0 by projection, 2026-10-12 21:03)": 1, "closed (diagnostic gate not met → no PASSAGE arm, 2026-10-12 21:15)": 1, "parked (D0 headroom PASS on part 1, FAIL on part 2 for the fused variant; superseded by DENSECHUNK-ST2, CLOSED R46, also parked)": 1, "closed (step-0 check failed its gate: 0/18 dropped vs ≥ 3; 2026-10-12 21:06)": 1, "closed (FAIL at step 0: R fails G1/G2/G3, Q fails G2/G3; 0 LLM / 0 judge / 0 paid)": 1, "closed (FAIL at step 0a on both wordings; 0b diagnostic run afterwards, verdict unchanged)": 1, "measurement (done 2026-10-13 10:37; no verdict rule)": 1, "measurement (done 2026-10-13 19:36; 18/18 runs; no verdict rule)": 1, "done (product: qa-cooking-se default-eligible, qa-money-se user-selected only; published on HF; no lever verdict)": 1, "tooling (done 2026-10-12; patch uncommitted in wt/packs)": 1, "closed (probe verdict: default-eligible qa-health-se, qa-outdoors-se, boar-firstaid-en, boar-medlineplus-en; user-selected only qa-travel-se, qa-ethereum-se, qa-bitcoin-se, 5 SE together)": 1, "tooling (pipeline + first self-test number; no control at the time)": 1, "closed (probe: wave-1 packs cover 1/34 V-para absent items; product value, not a bar lever)": 1, "closed (probe: boar-simplewiki-en user-selected only; boar-factbook user-selected only by coordinator call, frozen aggregator said eligible)": 1, "closed: S − OFF CONFIRMED, P − S COST CONFIRMED, X − P OPTIONAL (R49 unchanged)": 1, "adopted as judge protocol (tooling): both N = 4 and N = 8 USABLE; result recommends N = 8, but the L1-PROTOCOL addendum adopted default N = 4 for L1": 1, "closed: L0 FAIL after the one allowed revision (−125.72 vs bar −150); never ran L1 under PROMPTDIET; the faithful diet was later tested inside SPEEDPACK L1 (FAIL) and dropped from device-day candidates (QUEUE l.660)": 1, "closed: screen FAIL on the quality bar (closed-book ratio 0.437 < 0.517; below the 0.487 baseline); speed/RSS/empty/leak bars PASS; no full-engine L1 (stop rule)": 1, "tooling (data-only probe sets for the cut3-dev AR/SC/VG L0 gates; results in arms/CUT3DEV.md)": 1, "closed — NO (not detected / 'not decided at MDE 0.03' per criterion); mechanism read-out: wrong_fact axis gain on v0.2 only": 1, "done — measurement (O-5 NUMCHECK met; O-4, O-8, T3 not met; entity+fabricated borderline V-para only)": 1, "closed — 'no retrieval harm shown' (pre-registered rule; coverage/no-gold share 0.4 % vs bar ≥ 60 %)": 1, "closed — S5′ FAIL (false fires 5/50 vs ≤ 1 per 25); follow-up SC v3 S5″ also FAIL, SC trigger parked": 1, "closed (S5″ FAIL: water recall 18/25 (72 %) < 80 %; SC water card + trigger changes parked for the bounty)": 1, "tooling (done; generation byte-deterministic on the MacBook CPU path; RULE 27)": 1, "closed (T7 FAILS at step 0; O-6 Integrative Decoding closed, no T9 ID arm)": 1, "measurement only (no verdict rule)": 1, "open / in progress: stage 0 data PASS (v1, then v2); stage 1 environment + parity tooling PASS on the smoke adapter (STAGE1.md); training (step 6) on hold until v3 data (addendum 2); no verdict": 1, "closed (NO-GO; G1–G4 all FAIL for Qwen3-0.6B; Qwen2.5-1.5B refused on vocab)": 1, "closed (NOT ADOPTED: 3 of 5 gates FAIL)": 1, "closed (FAIL at step 0 on the G1 fact-chunk bar 36 < 39; measurement continued as STACK-2; pack stack closed in R49)": 1, "closed: not decided at MDE 0.03 → pack stack closed (R49); optional setting, not default": 1, "closed: FAIL at step 0 (0-call replay gate; no judge call)": 1, "superseded draft: never authorised or run; replaced by DEEPVPARA (criterion frozen 2026-10-08)": 1, "closed: NO (near-lever), stopped after seed 42 (one seed, not the two-seed verdict the criterion specifies); CLOSED R10 relabels it 'not detected at MDE 0.06'": 1, "closed: NO (by rule at Haiku L1; not a near-miss); CLOSED R11 relabels it 'not detected at MDE 0.025 (110, 1 seed)'": 1, "parked (dormant until a device is available; criterion not written or frozen)": 1, "closed (L0 FAIL after the one allowed revision; QUEUE calls it 'killed'); L1 never run": 1, "closed (diagnostic; verdict branch 0/7, runner fix not adopted by the rule; superseded by VENUEGPS-2)": 1, "lever-adopted (claim wording + runner option; plumbing proof, no engine change; not a claim number)": 1, "tooling (probe set; VG-S PASS on it; DEV after VG-S)": 1, "tooling (probe set; VG-S2 FAIL on it; burnt)": 1, "closed (FAIL at step 0, gate (b) crowding on v0.2 0.612 > 0.40; 0 judge calls)": 1, "closed in practice: NO at the slice (Opus −0.011) and not detected at L2 on v0.2 full 110 (Opus +0.0012, CI −0.0120…+0.0147); frozen stage 4 (V-para 2 seeds) never run, so no frozen LEVER/SMALL/NO verdict": 1, "stage complete: MARGINAL 7/34 verified over 15/15 shards (intermediate; decision pooled with stage B → 9/34 MARGINAL, CLOSED R45)": 1, "closed (frozen band MARGINAL, 9/34 verified, lower bound; no WIKI-ALL arm; Wikipedia neither reopened nor closed as kit content per the frozen wording)": 1, "closed (FAIL at 0-call gate, 2/13 V-para and 4/30 v0.2 vs bar 40 %; scope narrowed by Correction 2026-10-12; reopened in scope by WIKIFULL R45)": 1, "closed (gate FAIL on V-para 1/13 at p ≥ 0.7; reading scope-corrected 2026-10-12; superseded by WIKIFULL pooled 9/34, R45)": 1, "lever-adopted (L0 PASS on A1, A3-A6; A2 FAIL reported separately; L1 AR ADOPT; shipped in cut 3)": 1, "FAIL (S5 72 % < 80 %); superseded by v2/v3; water card and trigger PARKED": 1, "FAIL (S5′ false fires 5/50 vs bar ≤ 2); superseded by v3": 1, "parked (S5″ FAIL: water recall 18/25; SC water card and trigger PARKED for the bounty)": 1, "lever-adopted (snakebite text only, SBt in cut 3; water text approved but never shipped)": 1, "L0 FAIL by the letter (V2) with a disclosed exception, plus V5 FAIL. The VG line was later adopted as v3 in cut 3.": 1, "intermediate gate PASS (V5′ 36/36 BETTER); not a ship clearance; superseded by v3, which shipped after VG-S": 1, "lever-adopted (VG-S PASS → cut 3 adopted with VG v3)": 1, "closed (VG-S2 FAIL: 1 WRONG fire; VG v4 not adopted; VG line CLOSED)": 1, "lever-adopted (CUT 3 ADOPTED after VG-S, CONFIRMED with no regression)": 1, "tooling (v0.1 slice frozen 10-06; held-out-style slices added 10-08; retired for arms frozen after the 10-11 RANDOM20 addendum)": 1, "tooling (L1 futility-screen slices; replace signal20 for arms frozen after the addendum)": 1, "tooling (protocol frozen 2026-10-06; addenda HAIKUJUDGE/PARJUDGE 10-07, OPUSSHARD/SLICE20 10-08, near-miss/SEEDVAR 10-10, RANDOM20 labelled 10-11)": 1, "closed (verdict NO: G is faster than T but not at parity. PARITY-FASTER failed because CI low −0.057 < −0.03, and BETTER failed)": 1, "closed (NO-ADOPT at deterministic gate 5; judge skipped by frozen cost rule; gates 1, 2, 4 not measured)": 1, "closed (NO-GO: G3 Japan bar failed; tf2 stays out of the ship cut)": 1, "confirmed (no regression) — confirmation of the cut 3 build adopted at QUEUE.md:569": 1, "AR ADOPT; VG L1 PASS but NOT adopted under this criterion (vg-REVIEW.md V5 FAIL). VG v3 was adopted later through a different gate (VG-S PASS, QUEUE.md:569)": 1}, "discrepancies": {"high": 12, "medium": 97, "low": 307}, "closed_no_row": ["CF", "CRYPTOFACTS-step1", "CRYPTOSEL", "CRYPTOTRUTH", "CUT4-KVFIX", "CUT4-INSTANT-FRAG", "CUT5-SPEED", "CUT5-LITE", "CV", "CVS", "CVH", "CVO", "DEEPCOVER", "DEEPTHINK", "DEEPTHINK-V02", "DETMAX", "FOLLOWQG", "GATEFID", "HAIKUJUDGE", "HFUFIX", "HFUFIX2", "INSTSUBJ", "KVQ8", "LOCALGATE", "OPUSSHARD", "P4 packGround (PACKCOND P4 step 0)", "SECTIONHIT", "HEALTHQ", "SC-V2-S5PRIME (sc-fresh3)", "SC-V3-S5SECOND (SC v3 trigger S5″ on sc-fresh4)", "SPECDEC", "TRAVELSEL", "VENUEGPS", "VENUEGPS-2", "VITALPACK-ADD", "AR", "SC-L0 (SC v1 trigger: water-safety card + snakebite completion)", "SC-v2-S5prime", "SC-v3-S5second", "SC-S6 / SBt (reviewed snakebite card text)", "VG-L0 (verdict guard v1)", "VG-S (VG v3 ship gate)", "VG4-S2 (VG v4 threshold/superlative ship gate)", "CUT3DEV (cut 3 build: cut 2 + VG v3 + AR + SBt)", "K3-ON-CUT2", "TF2-ON-CUT2", "CUT3-CONFIRM", "CUT3-VGAR-L1"], "closed_discrepant": ["DEEPFULL-F2", "HUMANSFT", "PACKROUTE-2", "WIKIFULL-REOPEN", "WIKISECTION"], "exposures_missing": ["DEEPHEDGE", "DEEPROUTE-VPARA", "EVALFIX", "LENGTHSHARE", "LOCALGATE", "HEALTHQ", "T-K4a", "SEEDVAR", "RANDOM20 (random stratified slices)", "L1-PROTOCOL (judge triage protocol)"], "no_criterion_sha": ["CRYPTOSEL", "CVO", "DEEPCOV-FB", "DEEPRERANK", "DEEPROUTE-OOS", "DEEPROUTE-VPARA", "EVALFIX", "FACTS-RECALL", "FACTS-BLIND", "LCRELAX", "K2HALF", "L1CTL", "LOCALGATE", "LORA-DIAG", "NUMCHECK", "PACKCOND-P1", "PACKCOND-P2", "P4 packGround (PACKCOND P4 step 0)", "SECTIONHIT", "DENSECHUNK", "HEALTHQ", "SELFTEST-SCORES", "WAVE3", "T-K2", "T-K4a", "T-K4c", "T-K4d", "T-K6b", "PROBES", "SEEDGEN", "SEEDSPEC (T7)", "SYNTHDEEP", "T1-DEEP35", "THREADS2", "WIKISECTION", "WIKISECTION-H5b", "L1-PROTOCOL (judge triage protocol)", "K3-ON-CUT2", "TF2-ON-CUT2", "CUT3-CONFIRM", "CUT3-VGAR-L1"], "unverified": []}

# LEDGER-AUDIT-2026-10-13: complete pass

Scope: 159 verified arm records under `rnd/research/coordinator`. This pass lists every HIGH and MEDIUM discrepancy. LOW items appear only as counts per arm (§7).

Path convention:
- Arm files drop the `arms/` prefix, so `cf/CF.md` means `arms/cf/CF.md`. Files at the arms root are written in full, for example `arms/CUT3DEV.md`.
- Coordinator-root files appear by name.
- `QUEUE` means `../QUEUE.md`. `CLAUDE` means `<workspace>/CLAUDE.md`.

Numbers are quoted as the sources write them.

## 0. TL;DR

| Metric | Count |
|---|---|
| Arms audited | 159 |
| Status: closed with a decisive verdict (FAIL / NO / gate / parity / transfer) | 92 |
| Status: closed descriptive, diagnostic or measurement | 26 |
| Status: lever adopted (incl. judge protocols, cut builds) | 19 |
| Status: tooling | 12 |
| Status: not decided or parked | 6 |
| Status: open, running or never-run draft | 4 |
| Discrepancies HIGH / MEDIUM / LOW | 12 / 97 / 307 |
| Decisive arms with no CLOSED.md row (incl. adopted levers missing from the l.11 exclusion list) | 48 |
| CLOSED.md rows that disagree with the arm | 5 (DEEPFULL-F2, HUMANSFT, PACKROUTE-2, WIKIFULL-REOPEN, WIKISECTION) |
| Arms that touched a blind set and have no EXPOSURES row | 10 records = 9 events (RANDOM20 and L1-PROTOCOL are the same event) |
| Criteria without a `.sha256` sidecar | 41 (21 of them back a decision; see §5) |

The status buckets are a coordinator grouping of the per-arm status strings.

Main points:
- **Claim-facing:**
  - CLAUDE.md "Current state" quotes the s42-only v0.2 numbers (0.519 / 0.40) as the claim numbers.
  - CLAUDE.md puts raw Δs next to floor-adjusted levels in three places (DT512, DT256, DT512-V02).
  - CLAUDE.md overstates the SELFTEST-DEEP Δ: it says +0.063, the pooled value is +0.054.
  - CLAUDE.md quotes p50 145 s; the measured value is 143 s.
  - CLAUDE.md, CLAIM-DRAFT.md:126/:191 and CLOSED R12 call the pooled HUMANSFT 6/20 "human CLAPnq". CLAPnq alone is 3/17.
- **Checked this pass:**
  - CLAIM-DRAFT.md already prints 0.389 (cut 3) and 0.397 (s42), and 143 s / 146 s.
  - REPORT-PACKS correctly says 36 % of all kept slots and +0.054.
  - REPORT-PACKS' 0.68 break-even comes from a QUEUE derivation and is not in the arm file.
  - BAR-TABLE.md:134 still reads "WIKISECTION H5/H5b (FAIL: the facts are not in Wikipedia)". That reading was withdrawn.
- **Exposures:** 9 script-read events on bench-v02 and/or V-para have no row, and 3 summary tallies are short. Status does not change because every affected set is already dev or dev-style, but the protocol requires the rows.
- **Registry:** most of the gap is pre-10-06 work (cut-3 era, computed verdict, SC, VG, K3/TF2), plus 10-12/13 arms closed after CLOSED.md was built (DEEPCOVER, VITALPACK-ADD).
- **One sha mismatch:** the LOSSMAP criterion was edited after it was frozen. The ORACLE-ST patch mismatch flagged by extraction is false; the sha matches.

## 1. HIGH discrepancies (12), claim-facing first

| # | arm | what (A / B) | source_a | source_b | likely truth | one-line fix |
|---|---|---|---|---|---|---|
| H1 | CUT7 | A: "CLAIM-RESULTS-cut6 headline 0.512 / V-para 0.413 stand for cut 7" / B: "Honest numbers: v0.2 held-out raw 0.519 / floor-adjusted 0.40" | cut7/CUT7.md:33 | CLAUDE:22 | Two-seed raw 0.512 (0.478–0.549), floor-adj 0.388 (0.346–0.434). 0.519 / 0.397 is s42 only (BAR-TABLE.md:54). CLAIM-DRAFT.md:12 already separates them. | CLAUDE:22 → "v0.2 raw 0.512 (two seeds; s42 alone 0.519) / floor-adjusted 0.388 (s42 0.397)" |
| H2 | DEEPROUTE-VPARA | A: "on v0.2 the R2 rule fires on 33/110 (30 %)" / B: EXPOSURES has only the V-para "simulated hybrid router" row | QUEUE:882 | EXPOSURES.md:108 | bench-v02 script read on 10-10 (outputs in blind/bench-v02/runs-deeproute/) is unlogged. CLAIM-DRAFT.md:190 cites this arm as [S44]. | Append row E2 (§4) |
| H3 | T-K4a | A: "Script-only reads only (EXPOSURES.md rows 10-12/10-13: … T-K4a/d …)" / B: only a "T-K4d wave-1 pack coverage probe" row exists | HANDOFF-2026-10-13.md:57 | EXPOSURES.md:145 | The handoff overstates the ledger. There is no T-K4a row. | Append row E7; the handoff statement then becomes true |
| H4 | T-K4a | A: "replays under blind/bench-v02/runs-packs/" / B: no T-K4a row | QUEUE:989 (packs/T-K4a.md:4) | EXPOSURES.md:145 | Script-only bench-v02 exposure is unlogged (also flagged at QUEUE:1080). | Append row E7 |
| H5 | SEEDVAR | A: "SEEDVAR preliminary on v0.2 (existing rows, 0 calls; 12:35)" / B: only the V-para SEEDVAR row | QUEUE:873 | EXPOSURES.md:110 | bench-v02 script read by seedvar.mjs is unlogged. It was already flagged in the earlier audit (LEDGER-AUDIT l.119) and is still open. | Append row E8 |
| H6 | DEEPHEDGE | A: "On V-para: 0/58 items route health-strict" / B: the only row is bench-v02 "generate only + jev gate" | QUEUE:952 (deephedge/DEEPHEDGE.md:5) | EXPOSURES.md:131 | Script read of route codes from H's V-para s42 traces is unlogged. Row 131 also omits the 110-id H trace read. | Append row E1; extend row 131 |
| H7 | LENGTHSHARE | A: "v0.2 H 0.743 / 0.375 / 0.408; usefulness ≥ 3 share" / B: only "V-para · LENGTHSHARE (80-word-capped references" | QUEUE:905 | EXPOSURES.md:114 | Part 1 script-read the v0.2 judgment rows (0 calls). Only Part 2 was logged. | Append row E4 |
| H8 | EVALFIX | A: "T6 EVALFIX done … 1 tie in 1,052 mapped rows" / B: grep `evalfix\|T6` hits only l.103, which is unrelated | QUEUE:962 | EXPOSURES.md (no row; cf. :107, :140) | Both sets were script-read on 10-12 by tools/winsties.py and robust_ci.py. | Append row E3 |
| H9 | LOCALGATE | A: "requests rebuilt offline under blind/localgate/, no text seen" / B: no row names LOCALGATE | QUEUE:988 | EXPOSURES.md:135 | Blind-derived rationales from V-para and v0.2 were re-read by scripts and local models. Nothing went to an external API. | Append row E5 |
| H10 | HEALTHQ | A: "script-only on the v0.2 items + the p4b replay, ids/counts only" / B: grep healthq returns 0 hits | QUEUE:975 | EXPOSURES.md (none; :139/:141 do not name it) | tools/healthq_check.py read bench-v02 questions and replay output on 10-12 21:06. | Append row E6 |
| H11 | RANDOM20 | A: "arms/random20-v02.ids (a3e43672…) and arms/random20-vpara.ids (e4853b32…), seed 7" / B: the precedent "SLICE20 id selection" row exists; RANDOM20 has none | QUEUE:905 | EXPOSURES.md:70 | Id and category selection on both sets is unlogged (ids only, 0 calls). | Append row E9 |
| H12 | L1-PROTOCOL | Same event as H11, through the protocol's RANDOM20 addendum | arms/L1-PROTOCOL.md:28 | EXPOSURES.md:70 | Duplicate of H11 | Covered by row E9 |

## 2. MEDIUM discrepancies (97 items, 96 rows)

### 2a. Claim-facing (CLAUDE.md, CLAIM-DRAFT, BAR-TABLE, REPORT-PACKS, HANDOFFs, CLOSED labels quoted in them)

| # | arm | what (A / B) | source_a | source_b | likely truth | one-line fix |
|---|---|---|---|---|---|---|
| M1 | HUMANSFT | "human CLAPnq 6/20; no LoRA" / "6/20 (ids 3, 9, 16, 18, 19, 20)" | CLAUDE:24 (same wording at CLAIM-DRAFT.md:126, :191, found this pass) | humansft/REVIEW-20h.md:31 | Pooled CLAPnq+HAGRID 6/20. CLAPnq 3/17, HAGRID 3/3 (ids 18–20). | CLAUDE:24 → "human CLAPnq+HAGRID 6/20 (CLAPnq 3/17)"; send the CLAIM-DRAFT wording to the Opus reviewer |
| M2 | HUMANSFT | "teacher 16/20 -> +sentence rejection 11/20 -> human CLAPnq 6/20" / same ids | CLOSED.md:27 (R12) | humansft/REVIEW-20h.md:31 | Same as M1. HUMANSFT.md:53 repeats the attribution. | R12 → "human CLAPnq+HAGRID 6/20 (CLAPnq 3/17, HAGRID 3/3)" |
| M3 | SELFTEST-DEEP | "deep tier +0.063 over the 4B, SE packs add nothing to it" / "+0.054 (+0.034…+0.073) pooled (SE +0.063 …, topic +0.043 …)" | CLAUDE:21 | packs/SELFTEST-DEEP.md:2 | Pooled +0.054. +0.063 is the SE half. No pack adds anything (pooled −0.002). REPORT-PACKS:10/:206 are already right. | CLAUDE:21 → "+0.054 over the 4B with the same pack (SE +0.063); no pack adds anything (pooled −0.002)"; drop "open: SELFTEST-DEEP topic half" |
| M4 | DT512 | "paired +0.011 (−0.010…+0.031)" printed beside floor-adj 0.436 vs 0.422 / "floor-adj +0.014 (-0.012…+0.039)" | CLAUDE (DT512 sentence) | dt512/DT512.md:2 | +0.011 is raw. Floor-adj is +0.014. | "paired raw +0.011 (−0.010…+0.031), floor-adj +0.014 (−0.012…+0.039)" |
| M5 | DT256 | "budget 256 floor-adj 0.387, −0.028 (−0.056…−0.003) vs 1024" / "floor-adj -0.035 (-0.070…-0.004)" | CLAUDE (DT256 sentence) | dt256/DT256.md:2 | −0.028 is raw. | "raw −0.028 (−0.056…−0.003), floor-adj −0.035 (−0.070…−0.004) vs 1024" |
| M6 | DT512-V02 | "512 floor-adj 0.508 (0.467–0.550), −0.005 vs 1024, +0.089" / floor-adj "-0.006 (-0.025…+0.011)", "+0.111 (+0.071…+0.152)" | CLAUDE (DT512-V02 sentence) | dt512v02/DT512V02.md:17 | −0.005 and +0.089 are raw. | "−0.005 raw (floor-adj −0.006) vs 1024, +0.089 raw (floor-adj +0.111) vs the 4B claim run" |
| M7 | DEEPTHINK | "×4.2 time (p50 145 s desktop)"; HANDOFF "79 / 144 s" / "desktop p50 total 143 s vs 34 s (×4.2)" | CLAUDE:24; HANDOFF-2026-10-10.md:9 | deepthink/DEEPTHINK.md:2 | 143 s (s42 142.9, s43 146.0). CLAIM-DRAFT.md:190 is already correct. | CLAUDE 145 → 143 s; HANDOFF-2026-10-10 l.9 144 → 143 s |
| M8 | DT256 | "floor-adj 0.387 (0.349–0.426)" · "0.300" / "0.387 (0.348–0.425) · 0.299" | QUEUE:846; BAR-TABLE.md:41 | dt256/DT256.md:29 | Same aggregate (0.3872 [0.3485, 0.4255], 0.2995). The values sit on a rounding boundary. | DT256.md:29 → "0.387 (0.349–0.426) · 0.300" |
| M9 | QUANTCEIL | "v0.2 *wrong* items +0.087 (+0.035…+0.150, n 23)" / "wrong_fact=True n= 23 dRatio=+0.087"; "primary=wrong n= 17 dRatio=+0.113" | quantceil/QUANTCEIL.md:5; BAR-TABLE.md:134; HANDOFF-2026-10-12.md:28 | quantceil/aggregates/bucket-delta-v02-s42.opus.txt:5-6 | +0.087 is the wrong_fact axis (n 23). The primary wrong bucket is +0.113 (0.048…0.187, n 17). QUEUE:945 is correct. | All three → "wrong_fact axis +0.087 (n 23; primary wrong bucket +0.113, n 17)" |
| M10 | QUANTCEIL | "a gain ≥ +0.03 raw is excluded on both sets" / V-para "+0.004 (−0.024…+0.033)" | quantceil/QUANTCEIL.md:3; CLOSED.md:61 | quantceil paired_gap-QvsH-2seed.json (0.0325) | Excluded on v0.2 only (CI upper +0.028). | "excluded on v0.2 (CI upper +0.028); V-para CI upper +0.033" |
| M11 | THINK4B-V02 | "THINK4B-V02 300 H l.880–881" / "Haiku 20 + 110 ids (260 calls); Opus 0" | BAR-TABLE.md:113 | think4b/THINK4B.md:45 | 260 (QUEUE:881). The 40 slice calls are counted twice. | "THINK4B-V02 260 H l.881" |
| M12 | PACKROUTE-2 | "≥ 0.85 accuracy plus a peers fallback on none to beat P" / "break-even ≈ 0.68, 90 % of S ≈ 0.9" | packroute2/ACCURACY.md:63 | CLOSED.md:72 (R48); QUEUE:1031; BACKLOG.md:30; HANDOFF-2026-10-13-PM.md:12; REPORT-PACKS.md:13/:131/:212 | 0.68 is a coordinator derivation (0.256/0.378) for a hard top-1 filter against peers. 0.85 is the G1 bar with a fallback. They answer different conditions. | Add under ACCURACY.md §0b: "break-even vs P for a hard top-1 filter ≈ 0.68 (0.256/0.378, QUEUE l.1031); 90 % of S ≈ 0.9; ≥ 0.85 is the G1 bar"; R48 and REPORT-PACKS then cite it |
| M13 | CROWDQ | "simplewiki 36 % of kept slots (66 of the 164 non-own slots)" / "P 164: simplewiki 66 (40 %)"; "(all kept slots, 282): simplewiki 36 %" | QUEUE:1033 | crowdq/CROWDQ.md:15 | 66/164 = 40 % of foreign slots; 102/282 = 36 % of all slots. REPORT-PACKS:12/:109 are correct. | QUEUE correction: "36 % of all kept slots (102/282; 66 of the 164 non-own slots = 40 %)" |
| M14 | CUT7 | "0.413 · 0.26 · 0.519 · 0.40" / "0.512" | HANDOFF-2026-10-11.md:15 | cut7/CUT7.md:33 | The table mixes two-seed V-para with s42-only v0.2. Two-seed v0.2 is 0.512 / 0.388. | Label the v0.2 cells "s42 only" or replace them with 0.512 / 0.388 |
| M15 | CUT7 | "held-out numbers are cut 6's: v0.2 floor-adj 0.40 / V-para 0.26" / "floor-adj 0.388 (0.346–0.434)" | HANDOFF-2026-10-10.md:9 | CLAIM-RESULTS-cut6.md:38 | 0.388 is two-seed; 0.397 is s42. | Erratum: "v0.2 floor-adj 0.388 (two seeds; 0.397 s42)" |
| M16 | DEEPTHINK-V02-ADDENDUM1 | "On v0.2 the same tier is seed-stable (0.613/0.612, r 0.90)" / "TV (deep + think 1024) 0.613 / 0.612" | HANDOFF-2026-10-10.md:48 | QUEUE:873 | These values belong to TV (1024). The 512 tier (H) has one v0.2 seed, 0.608 (BAR-TABLE:57). | Erratum: "the 1024 thinking tier (TV) is seed-stable" |
| M17 | PACKCOND-P1 | "H scores 0.55 floor-adj on v0.2 (n 32) vs 0.39 without" / "in-pack 32 … 0.609 (0.532–0.679)"; "not in-pack 78 … 0.467" | HANDOFF-2026-10-12.md:18 | packcond/PACKCOND-P1.md:40,45-46 | On above_min, H is 0.609 vs 0.467 and K is 0.482 vs 0.378. 0.55 / 0.39 are above_decl values. | Erratum: "H above_min 0.61 (0.53–0.68) in-pack vs 0.47 without (K 0.48 vs 0.38); P1's 0.55/0.39 were above_decl" |
| M18 | WIKIFULL-REOPEN | "holds the missing fact for ≤ 9/34 bounty-style absent items" / "pooled A+B = 9/34 verified … Lower bound" | HANDOFF-2026-10-13.md:11 | wikifull/STAGE-B.md:2 | At least 9/34 is verified; the bound runs the other way. Scaling suggests about 9–12. | "≥ 9/34 (verified lower bound; ≈ ≤ 12 by scaling)" |
| M19 | WIKIFULL-REOPEN | "the facts of ≈ 3 in 4 bounty-style misses are not in Wikipedia" / "not reopened as kit content …, and not closed either (> 6)" | CLOSED.md:69 (R45) | wikifull/STAGE-B.md:24 | Lower bound only: 72 % of old-id pages were not fetched and 17/34 hit at ≥ 0.6. This is the same overreach the WIKISECTION correction withdrew, and BAR-TABLE.md:134 repeats it for H5/H5b (found this pass). | R45 → "closed: MARGINAL (9/34 verified, lower bound), no WIKI-ALL arm; Wikipedia neither reopened nor closed as kit content"; BAR-TABLE:134 → "FAIL in scope (top-100k text, kept-source items)" |
| M20 | WIKISECTION | "lead/intro ≤ 8 %" / vital intro on V-para "1 of 6" | CLOSED.md:63 (R39) | wikisection/WIKISECTION.md:7 | Lead 1/13 and 1/30; vital intro 1/6 and 0/20. "≤ 8 %" holds only with 13 as the denominator. | R39 → "lead 1/13, 1/30; vital intro 1/6, 0/20" |

### 2b. CLOSED.md registry (row texts in §3)

| # | arm | what (A / B) | source_a | source_b | likely truth | one-line fix |
|---|---|---|---|---|---|---|
| M21 | CF | "CF data review: FAIL → CF NOT adopted" / CLOSED.md:60 names only "Maple, preparedness pack" | QUEUE:586 | CLOSED.md:60 | Closed lever, listed among exhausted levers at QUEUE:605 | Add row C1 |
| M22 | CRYPTOFACTS-step1 | "Line closed at step 1." / no CRYPTOFACTS row | QUEUE:796 | CLOSED.md:24 | 0-call gate FAIL | Add row C2 |
| M23 | CRYPTOSEL | "CRYPTOSEL L1 FAIL (target gate) → not adopted" / no row | QUEUE:608 | CLOSED.md:24 | Closed by the no-revision stop rule | Add row C3 |
| M24 | CRYPTOTRUTH | "NOT ADOPTED as frozen ... parked for after the claim (PR phase)" / no row in CLOSED or BACKLOG | QUEUE:702 | CLOSED.md:24 | Not adopted; parked | Add row C4 |
| M25 | CV | "Computed-verdict line CLOSED for the bounty (CV, CVS, CVH)" / no row | QUEUE:604 | CLOSED.md:6 | Family closed by stop rules | Add row C5 |
| M26 | CVS | Same QUEUE line / no CVS, verdict or computed row | QUEUE:604 | CLOSED.md:1-60 | Same as M25 | Row C5 |
| M27 | CVH | "CVH v0.1 L1 FAIL → CVH KILLED" / no row | QUEUE:603-604 | CLOSED.md:1-60 | Same as M25 | Row C5 |
| M28 | CVO | "Computed-verdict family fully CLOSED for the bounty (CV, CVS, CVH, CVO)" / no row | QUEUE:618 | CLOSED.md:1-60 | Same as M25 | Row C5 |
| M29 | DEEPCOVER | R8 "DEEPCOVER … is the only distinct variant" (R25 also names it as reopen) / "Verdict: NO at the slice." | CLOSED.md:23, :44 | deepcover/DEEPCOVER.md:3 | Closed NO on 10-12 (QUEUE:935); the registry was built on 10-11 | Add row C6; mark the R8/R25 reopen cells "tested 10-12: NO" |
| M30 | DEEPFULL-F2 | R25 "not detected at MDE 0.08 (20, 1 seed)" / "Verdict: NO at the slice (both arms)." | CLOSED.md:44 | deepfull/DEEPFULL.md:2, :18 | Both are true | R25 label → "NO by the criterion rule; not detected at MDE 0.08 (20, 1 seed; CI upper +0.048)" |
| M31 | DEEPTHINK-V02 | No entry at CLOSED.md:7/:11 / "L1: NO by the frozen rule" (later Opus +0.045) | CLOSED.md:7, :11 | deepthinkv02/DEEPTHINKV02.md:2 | v0.2 replication of the adopted lever, not a closed family | §3b, l.11 addition |
| M32 | FOLLOWQG | "NOT ADOPTED. G3 FAIL (arm wins 9 of 20 non-tie decisions = 45%" / R4 lists only FOLLOWQ; reopen cell "(<=2/171)" | followq/FOLLOWQG.md:3 | CLOSED.md:19 | FOLLOWQ-G tested exactly R4's reopen condition (0/171) and failed on quality | §3b, amend R4 |
| M33 | GROUND-ST | "the keep rule that passed step 0 is carried into the STACK criterion" / "X3 is carried into the STACK criterion as a declared component" | groundst/GROUND-ST-criterion.md:24, :31, :34 | QUEUE:1026 | No variant passed step 0. The carry-over is a post-hoc coordinator decision (BACKLOG.md:77). | §3b, R47 label |
| M34 | GROUND-ST addendum 1 | "Variant entering stage 1 = the one with the highest fact-chunk kept among those passing" / same QUEUE line | groundst/GROUND-ST-criterion-addendum-1.md:13 | QUEUE:1026 | X3 scored 54 < 55, so it does not advance | GATE.md addendum verdict: "X3 carried into STACK by coordinator decision (QUEUE l.1026), not by the GROUND-ST rule"; add a RULE-CHANGES row |
| M35 | HFUFIX | "HFU-FIX NOT ADOPTED as frozen" / R4 (FOLLOWQ) is the only follow-up row | QUEUE:688 | CLOSED.md:19 | Family closed by the frozen stop rule (HFUFIX2-criterion.md:8) | Add row C7 |
| M36 | HFUFIX2 | "HFU-FIX2 NOT ADOPTED → HFU-FIX closed" / no row | QUEUE:690 | CLOSED.md:19 | Same as M35 | Row C7 |
| M37 | KVQ8 | "overall · ADOPT as a device-day candidate" / absent from the CLOSED.md:11 exclusion list | kvq8/KVQ8-L1.md:97 | CLOSED.md:11 | Passed non-inferiority; device gate pending | §3b, add to l.11 |
| M38 | PROMPTDIET | R7 reopen "a new device-day latency experiment (patch bb287dde kept)" / "PROMPTDIET dropped from device-day candidates." | CLOSED.md:22 | QUEUE:660 | The later ruling wins (diet alone raised confident-wrong; KVFIX caches the prefix) | §3b, R7 reopen cell |
| M39 | SC-V3-S5SECOND | "S5″ FAIL" (the last round) / grep `snake\|water\|SC\|safety` finds nothing | arms/sc-fresh4-S5second-result.txt:6 | CLOSED.md:6 | Family closed or parked after 3 gate FAILs | Add row C8 |
| M40 | SPECDEC | "SPECDEC NO-GO ... Speculative decoding closed for the 4B on this stack." / R35 is MTP only, "no BOAR run" | QUEUE:672 | CLOSED.md:54 | Decisive NO-GO on 10-06 | Add row C9 |
| M41 | TRAVELSEL | "L0 FAIL after the one allowed revision" / no row (QUEUE:616 "killed") | travelsel/TRAVELSEL.md:3 | CLOSED.md (no row) | Step-0 gate FAIL, 0 judge calls | Add row C10 |
| M42 | VITALPACK-ADD | "H6 stays not detected at L2 on v0.2 … stage 4 … is not run" / R34 "L1 queued Mon 10-12" | vitalpack/VITALADD.md:19 | CLOSED.md:53 | Stopped: NO at the slice, not detected at L2 | Add row C11; update the R34 reopen cell |
| M43 | SC-L0 | "SC water card (3 rounds)" (killed/parked) / the registry starts 10-05 and omits it | QUEUE:578 | CLOSED.md:5 | Same family as M39 | Row C8 |
| M44 | SC-v2-S5prime | "SC v2 S5′ FAIL ... Set #3 burned for SC" / no row | QUEUE:556 | CLOSED.md:5 | Same family as M39 | Row C8 |
| M45 | SC-v3-S5second | "Water card + SC trigger changes PARKED for the bounty" / no row | QUEUE:562 | CLOSED.md:5 | Same family as M39 | Row C8 |
| M46 | VG4-S2 | "VG line CLOSED (no v5 ...)" / no VG row | QUEUE:577 | CLOSED.md:5 | VG extension line (v4+) closed | Add row C12 |
| M47 | K3-ON-CUT2 | "verdict NO-ADOPT (fails the prompt-token gate)" / no K3 row (also noted in the earlier audit, l.255) | k3-on-cut2.md:1 | CLOSED.md:4-12 | Closed at step 0 with 0 calls | Add row C13 |
| M48 | TF2-ON-CUT2 | "verdict NO-GO (tf2 stays out of the next ship cut)" / no row | tf2-on-cut2.md:1 | CLOSED.md (no row) | Closed by the frozen bar | Add row C14 |
| M49 | SFT4B | "filtered per example by jev quote_supports ≥ 0.9 (the row's reopen condition)" / R12 "a bar pre-registered relative to the human baseline (<=6/20" | sft4b/SFT4B-criterion.md:22 | CLOSED.md:27 | The reopen is met by addendum 2's strict ≤ 6/20 review, not by the jev filter alone | Note on R12 (§3b) |

### 2c. Arm files, QUEUE, BACKLOG, RULE-CHANGES, EXPOSURES tallies

| # | arm | what (A / B) | source_a | source_b | likely truth | one-line fix |
|---|---|---|---|---|---|---|
| M50 | CF | "Pending reviewer" / "VERDICT: FAIL. Agreement 126/150 = 84.0%"; "recall 80/100 (80 %, bar >= 90 %) FAIL" | cf/CF.md:20-21 | cf/trigger-result.txt:2 (data-REVIEW.md:1) | Both bars FAIL | CF.md:20-21 → FAIL 126/150 and FAIL recall 80/100, FF 0/100; add both to the TL;DR |
| M51 | CROWDQ | "must reproduce the replay's 46 ± 3, else stop" / "ruling QUEUE 15:0x: band 40 ± 4 = 36–44" | crowdq/CROWDQ-criterion.md:26 | crowdq/CROWDQ.md:10-11 | Band rescaled for URL matching (46 × 59/68), ruled 15:08 before judging (QUEUE:1030). The change is defensible but unlogged. | RULE-CHANGES row: "CROWDQ stage-2 reach band 46 ± 3 → 40 ± 4 (URL match), ruled 15:08 before judging" |
| M52 | CRYPTOSEL | "base 102.7 sel 125 ratio 1.217" / "retrieval 1.005×" | cryptosel/L0-round2.txt:10 | QUEUE:607 | The PASS rests on a post-hoc min-of-3 metric; moot because L1 failed | QUEUE correction: "1.005× (min-of-3 interleaved; one non-interleaved pair 1.217, post-hoc metric)" |
| M53 | CUT4-KVFIX | "KVFIX gate 3 (the real gate): device-only ... Still open" / "cut 4 warm (KVFIX ok) p50 68.7 s / p90 88.9 s" | cut4/cut4-L1.md:26 | QUEUE:661 | Gate 3 was never reported; "KVFIX ok" is a scenario assumption | QUEUE correction "(assuming KVFIX works; gate 3 unreported)", or log the A15 KV signals (QUEUE:711) as gate 3 |
| M54 | CV | "accuracy NOT scored (coordinator, against the key)" / "CV SHIP GATE FAIL → CV KILLED ... +26.5 pp" | cv/CV.md:3 | QUEUE:596 | KILLED (L0 FAIL, then ship gate FAIL) | Add a Verdict section to CV.md citing score.txt, gate-score.txt and QUEUE l.593-596 |
| M55 | CV | "CV answered 118 of the 146 routed items ...; 28 ... abstained" / "CV answered 113, abstained 26" | cv/CV.md:19 | QUEUE:592 (score.txt:3) | Both true on different denominators | QUEUE correction: "118 of 146 routed (113 of the 145 scored), abstained 28 (26 scored)" |
| M56 | CV | "(155 labelled, 7 ambiguous → 148 scored)" / "scored 145 items" | QUEUE:590 (gold/README.md) | cv/score.txt:1 | 145 were scored; 3 items were dropped without a note | Add to CV.md: "145 = 148 minus 3 items without a scoreable verdict (list ids)" |
| M57 | CVO | "delta : 0.0 percentage points (bar >= +10)" / "41 → 46/84 (48.8% → 54.8%, +6.0 pp < +8 bar)" | cvo/gate4-score.txt:3-4 | QUEUE:618 | +6.0 pp after rescoring; scorer bug; FAIL either way | Add a gate-4 note (cvo/CVO-gate4.md or in cvo-L1.md) marking gate4-score.txt as superseded |
| M58 | CVO | "CV abstained (routed, normal path answered): 56" / "51/120 routed, 10 overrides" | cvo/gate4-score.txt:7 | QUEUE:618 | Two routing definitions | Same note: "cvo:routed 51/120; cv-score routed flag 56/84 (pre-guard)" |
| M59 | DEEPCOV-FB | "all 7 already had curated sources kept" / table lists lan-exp-003 as an R2 item (no kept source) | QUEUE:914; deepcovfb/REPLAY-v01.md:41 | deepcovfb/REPLAY-v01.md:17, :27, :28 | 6 of 7; the 7th is lan-exp-003, the item the fallback reaches | Both → "6 of the 7 … the 7th (lan-exp-003) is the R2 item the fallback reaches" |
| M60 | DEEPCTX | BACKLOG MDE "≈ 0.03" / R23 "0.08" | BACKLOG.md:88 | CLOSED.md:42 | 0.08 (20-id slice) | BACKLOG:88 → "≈ 0.08 (20-id slice)" |
| M61 | DEEPFULL-F2 | BACKLOG MDE "≈ 0.06" / R25 "0.08" | BACKLOG.md:87 | CLOSED.md:44 | 0.08; 0.06 is the 51-item MDE | BACKLOG:87 → "≈ 0.08 (20-id slice)" |
| M62 | DEEPHEDGE | "detector p = 1.0 on 6 reasoning items" / "detector p = 1.000 on 10" | BACKLOG.md:58; HANDOFF-2026-10-12.md:30 | deephedge/DEEPHEDGE.md:5 | 10 of the 18 health-strict items (6 of the 18 are reasoning) | Both → "p = 1.000 on 10 of the 18 health-strict items (6 of the 18 are reasoning items)" |
| M63 | DEEPRERANK | "enters the top-6 on 2 items (vit-sci-002, vit-trv-003)" / k = 6 "2: vit-sci-002, trv-004" | QUEUE:908 | deeprerank/REPLAY-v01.md:27 | trv-004 (vit-trv-003 is in the k = 4 pair) | QUEUE correction |
| M64 | DEEPTHINK | "39/58 items hit the 1024 thinking budget" / "budget hits /51 … 36" | QUEUE:820 | deepthink/DEEPTHINK.md:16 (think-T-s42.json 36) | 36/51 on s42, 31/51 on s43 | QUEUE correction row |
| M65 | DEEPTHINK + DEEPTHINK-2 (2 records) | "39/58 answers hit the 1024-work budget" / "T (DEEPTHINK) · 1024 · … · 36 (≥ 1024)" | deepthink2/DEEPTHINK2-criterion.md:3 | deepthink/DEEPTHINK.md:16; deepthink2/DEEPTHINK2.md:22 | 36/51; the premise does not affect the rule | Note in DEEPTHINK2.md (criterion stays frozen): "premise 39/58 → 36/51" |
| M66 | DEEPTHINK-V02 | "NO by rule (Δ +0.029 vs +0.03)" / "paired Δ +0.027 (+0.002…+0.054)" | QUEUE:828 | deepthinkv02/DEEPTHINKV02.md:2, :18 | +0.027 is the deduplicated 220 rows; +0.029 is the raw 266-row file | QUEUE correction row |
| M67 | FACTS-BLIND | "recall after 2 scorer artefacts … 27/40 = 67.5%" / "set 2 26/40, not 27/40" | facts/FACTS-BLIND.md:7 (QUEUE:736) | facts/FACTS-r4-criterion.md:35-37 | 26/40 = 65.0 % under scorer v2 | Append a correction to FACTS-BLIND.md:7 |
| M68 | FACTS-r6 | "(all 8 entities are in the table)" / "7 of the 8 entities are in the table (Zambezi is absent" | QUEUE:758 | facts/FACTS-r6-SET4.md:17 | 7 of 8 (LCRELAX-PROBE.md:17) | QUEUE correction |
| M69 | FACTS-r6 | "if r6 FAILs on set 4, the line closes at r5" / "(1) cut 7 = cut 6 + FACTS r6" | facts/FACTS-r6-criterion.md:1-2 | QUEUE:770 | r4to overrode the criterion's fallback (disclosed as a head decision) | Add to SET4.md: "r4to 10-07 09:23 (QUEUE l.770) overrides the r5 fallback"; add a RULE-CHANGES row |
| M70 | FTDATA-REJ | "632/982 · ≥ 600 → MET" / "538/982 … kept bar ≥ 600 FAIL" | ftdata/FTDATA-REJ.md:24 | ftdata/FTDATA-REJ.md:53 | FAIL under the strict reading | :24 → "FAIL under the strict reading (538, see verdict)" |
| M71 | K2HALF | "Freeze a pass/fail criterion (sha256) before any run that decides something." / "the gate as frozen says FAIL" | CLAUDE (Rules) | k2half/K2HALF-gate.md:21 | Pre-registered at QUEUE:961, not sha-frozen | :21 → "as pre-registered in QUEUE l.961 (no sha-frozen criterion)" |
| M72 | LOSSMAP | .sha256 "1059f5dd15c80dfb…" / current shasum "0c189064df535036…" | lossmap/LOSSMAP-criterion.sha256:1 | lossmap/LOSSMAP.md:1 | Criterion edited after the freeze; frozen text not recoverable (QUEUE:1080) | Record in LOSSMAP.md and RULE-CHANGES; re-freeze as LOSSMAP-criterion.v2.sha256 |
| M73 | LOSSMAP | "excluded from the primary table but kept in the axes" / "kept in the tables" | lossmap/LOSSMAP-criterion.md:27 | lossmap/LOSSMAP.md:10 | Deviation from the frozen rule; primary shares would shift | Add an "undecided" row (H 12/51, 18/110; K 9, 18) or label the deviation |
| M74 | LOSSMAP | "9 of the 11 ran on the deep tier" / R40 "health-strict canned fallbacks" | lossmap/LOSSMAP.md:5 | CLOSED.md:64 | 10 health-strict + 1 instant; 0 deep-thinking (the misread fed DEEPHEDGE) | LOSSMAP.md:5 → "10 of the 11 on the health-strict path, 1 instant" |
| M75 | LOSSMAP | "wrong = 0.40 of H's V-para loss, 26/51 items" / "wrong · 16 · 0.40"; "wrong_fact · 26 · 0.59" | BACKLOG.md:48 | lossmap/LOSSMAP.md:16 | Pairs a bucket share with an axis count | BACKLOG:48 → "0.40 (16/51 primary; wrong_fact axis 26/51, 0.59)" |
| M76 | ORACLE-ST | "≈ 360 Haiku, Opus only if the Δ is a lever" / "≤ 720 Haiku + ≤ 720 Opus calls" | BACKLOG.md:31 (QUEUE:1027) | oracle-st/ORACLE-ST-criterion.md:12, :36 | The frozen criterion governs (QUEUE:1062 agrees) | BACKLOG:31 → "running (criterion 4c4651b1…; ≤ 720 Haiku + ≤ 720 Opus; Opus decides)" |
| M77 | ORACLE-ST | "ST2 put +40 fact chunks in context for +0.017" / "ST2 put ≈ +18 fact chunks into kept" | BACKLOG.md:31 (QUEUE:1027) | oracle-st/ORACLE-ST-criterion.md:16 | +41 reached the raw top-8, +18 were kept (HANDOFF-2026-10-13:14) | BACKLOG:31 → "+41 into raw top-8 (+18 kept) for +0.017" |
| M78 | P4 packGround | "First pack-conditional arm (frozen criterion)" / bars appear only after the run, "the gate needs ≥ 16 … allows ≤ 4" | PACKCOND-PLAN-2026-10-12.md:25 | packcond/P4-GATE.md:3 | Not sha-frozen; the FAIL is unaffected | Append to P4-GATE.md:3: "bars set before the replay, not sha-frozen" |
| M79 | SECTIONHIT | "fact article in raw 17/32 → kept 12/32 → fact passage shown 7/32" / "all · 32 · 19 · 12 · 12 · 7" | QUEUE:976 | packcond/SECTIONHIT.md:19 | Mixes two article definitions (17/11 under P1; 19/12 under SECTIONHIT) | QUEUE correction: "19/32 → 12/32 → 7/32 → 4/7 (SECTIONHIT def.; 17 → 11 under P1's)" |
| M80 | HEALTHQ | "4/15 in-pack misses are health-strict with empty raw" / "… health-strict path with an empty raw list on 3" | BACKLOG.md:21 | packcond/P4B-GATE.md:15 | Raw empty on 3 of the 4 | BACKLOG:21 → "(raw empty on 3)" |
| M81 | T-K2 | "41 hits, JSON.stringify(hits) identical" / "NOT label-only … kept list changes on 52/180 self-test items" | packs/T-K2.md:20, :23-24 | QUEUE:1079 (packs/tk2-replay/TK2-REPLAY.md:3) | Identity holds only on the shipped packs. SELFTEST, CROWDQ, STACK and the REPORT-PACKS numbers reflect pre-T-K2 (cut 7) behaviour. | T-K2.md: "identity scope = shipped crypto/wikivoyage packs; new-source packs change on 52/180" |
| M82 | PROMPTDIET | TL;DR "-150.2, bar -150; thin margin of 0.2" / "-125.72 (bar -150: FAIL by 24.3)" | promptdiet/PROMPTDIET.md:3 | promptdiet/PROMPTDIET.md:39 | Final L0 FAIL; the first build was rejected | Prepend to the TL;DR: "FINAL: L0 FAIL — rev 1 −125.72 vs −150; the −150.2 build was rejected" |
| M83 | SEEDGEN | "56/59 when equal" / "becomes 32/34 same-prompt (LLM items) + 23/23 no-LLM" | BACKLOG.md:25 | seedgen/SEEDGEN.md:54 | Post-F8 fix: 32/34 + 23/23; kept-unchanged 55/60 | BACKLOG:25 update |
| M84 | SFT4B | "stage 1 training on the mini running (10-13 21:4x" / "Status: WAITING FOR v3 DATA"; "Step 6 has not started." | BACKLOG.md:26 | sft4b/STAGE1.md:3-4 | Training not started | BACKLOG:26 → "env + parity tooling done; training on hold for v3 (addendum 2)" |
| M85 | SFT4B | "Stage 1 launched on the mini per addendum 1 ... Decision: v2" / "Superseded at 21:1x by v3 …; v2 was used only for the smoke." | QUEUE:1069 | sft4b/STAGE1.md:36 | v2 was the smoke run only | QUEUE row: "superseded 21:10 by addendum 2" |
| M86 | SYNTHDEEP | curated row, kept lists changed "2" / "Kept lists change on 4/60 items" | synthdeep/SYNTHDEEP.md:7 | synthdeep/REPLAY-v01.md:18 | 4 (aggregate lists 4 ids) | SYNTHDEEP.md:7 2 → 4 |
| M87 | VITALPACK-ADD | "VITALADD-Opus (H6, parked powered test) · parked" / "cheapest powered test … is now spent" | BACKLOG.md:57 | vitalpack/VITALADD.md:19 | Ran 10-13 20:56 (QUEUE:1065) | BACKLOG:57 → "done 10-13: Opus +0.0012 (−0.0120…+0.0147), not detected; closed" |
| M88 | VITALPACK-ADD | Parked-table cell "+0.011 (−0.007…+0.029)" (Haiku vs TV) / "Δ raw +0.0012 (−0.0120…+0.0147) vs L2-H-1seed" | BACKLOG.md:90 | vitalpack/VITALADD.md:18 | The Opus L2 value supersedes the Haiku cell | BACKLOG:90 → Opus result; next cheapest test = stage 4 V-para s43 + 204 Opus |
| M89 | AR | "The crypto pack has no EIP-7251 constants table at all" / "Correction: EIP-7251 table IS in the crypto pack" | arms/CUT3DEV.md:295 (QUEUE:551) | QUEUE:579 | A selection problem, not coverage; the A2 FAIL stands | Note under CUT3DEV.md:295 |
| M90 | SC-L0 | "sc 8c93bc8d…, stack 0cb058f1…" / "80bcb148… sc-on-cut2.vs-0cfd4a77.patch" | QUEUE:549 | arms/CUT3DEV.md:230 (SHA256SUMS:6) | Re-cut under the same filename (SC v3 + text); the v1 patch is gone | Note: "sc-on-cut2 re-cut (80bcb148…); v1 patch 8c93bc8d… overwritten" |
| M91 | VG4-S2 | "Round 6 … not adopted, awaits the coordinator's fresh probe set #2" / "VG-S2 FAIL → VG v4 NOT adopted ... VG line CLOSED" | arms/CUT3DEV.md:39 | QUEUE:577 | FAIL (vg4-S2-REVIEW.md:2) | CUT3DEV.md:39 → "VG-S2 FAIL (vgq2-002 WRONG) → v4 not adopted; VG line CLOSED" |
| M92 | CUT3DEV | "units stack 1280/1280 ... stack 0cb058f1…" / "a77b3b34… · 1293/1293" | QUEUE:549 | arms/CUT3DEV.md:233 | Stack patch re-cut later (HEAD 35cd4c30) | Note at CUT3DEV.md:233: "supersedes L0-era 0cb058f1… (1280/1280)" |
| M93 | CUT3-VGAR-L1 | "If the file says FAIL, VG is not adopted whatever its L1 result." / "VG: L1 PASS, adoption PENDING" | cut3-vgar-L1-criterion.md:54 | cut3-vgar-L1.md:54-55 | Under its own rule VG is not adopted. v3 entered via VG-S (QUEUE:569) through a gate redefined after the freeze (QUEUE:559). | Amend :54; add a RULE-CHANGES row for the QUEUE:559 redefinition |
| M94 | THINK4B | Opus/Haiku summary lists lack THINK4B / "Opus 20 (Z) + 20 (C) + 51 (Z) ids (182 calls)" | EXPOSURES.md:14 | think4b/THINK4B.md:36 | Per-run row :106 is correct | Fix tally T1 (§4) |
| M95 | THINK4B-V02 | Generation and Haiku lists lack THINK4B-V02 / "1 slice gen + 1 full gen; Haiku 20 + 110 ids (260 calls)" | EXPOSURES.md:13 | think4b/THINK4B.md:45 | Per-run row :112 is correct | Fix tally T2 |
| M96 | SEEDVAR | "Opus 16 full (… DT512-H 2 …)" / s44 pass "Opus judge.v1 N = 4, 51 ids (102 calls" | EXPOSURES.md:14 | seedvar/SEEDVAR.md:8 | DT512-H has 3 full passes, so Opus full is at least 17 | Fix tally T3 |

## 3. CLOSED.md gaps

### 3a. Decisive arms with no row: proposed rows

Column order follows the rows proposed in the records: lever | arms; date | system | set · n · judge | result | MDE | label | would reopen it | source.

```
C1  | Country-facts lookup (Wikidata) | CF; 10-04 | 4B | L0 deterministic, 0 judge | data 126/150 = 84.0% (bar 98%), trigger recall 80/100 (bar 90%), FF 0/100 | n/a (gate) | closed (gate FAIL) | curated per-field sources (QUEUE:586 lesson) + new blind set | arms/cf/CF.md, data-REVIEW.md, trigger-result.txt |
C2  | Crypto structured-fact instant tier | CRYPTOFACTS step 1; 10-07 | 4B | v0.1 11 crypto items, 0 calls | A0/B2/C9/D0; bars (i) 2/11 (≥ 6), (ii) 1/7 (≥ 4) FAIL | n/a (gate) | closed (gate FAIL) | see QUEUE l.796 | arms/cryptofacts/CRYPTOFACTS-step1.md |
C3  | Retrieval selection: crypto-pack spec/constants | CRYPTOSEL; 10-05 | 4B | v0.1 EN 57 x 2 seeds, Opus judge.v1-med, changed items | target +0.472 (bar +0.5) FAIL; Δ +0.0033, CI90 [-0.0049, +0.0139] | ~0.036 | closed | none (stop rule) | arms/cryptosel/cryptosel-L1.md |
C4  | Honesty/EIP card (NOREC+EIPABS) | CRYPTOTRUTH; 10-06 | 4B | v0.1 EN 57 x 2 seeds, Opus judge.v1-med, changed items | Δ +0.0092, CI90 [-0.0034, +0.0244]; cw 10 -> 6; G2 FAIL 1/3 probes | ~0.036 | not adopted (parked) | broadened denial phrase list, new freeze | arms/cryptotruth/CRYPTOTRUTH.md |
C5  | Computed verdict | CV, CVS, CVH, CVO; 10-04/05 | 4B | fresh blind verdict gates #1-#4 + v0.1 EN 57 x s44/s45, Opus judge.v1-med | CV gate +26.5 pp, 3 regressions (bar ≤ 2); CVS gate #3 +22.9 pp, L1 Δ -0.0050 [-0.0150, +0.0031]; CVH L1 Δ -0.0034 [-0.0153, +0.0061], +5.49 s routed (bar +2 s); CVO gate #4 +6.0 pp (< +8), 2 losses, L1 Δ 0.0000 vs same-day control | see arms | closed (stop rules) | see QUEUE l.604, l.618 | arms/cv/, arms/cvs/, arms/cvh/, arms/cvo/ |
C6  | Prompt: key-point enumeration (deep) | DEEPCOVER; 10-12 | deep | v0.2 random20 slice, 1 seed, Haiku→Opus N=4 | Opus Δ -0.027 (-0.077...+0.019), correctness 0.707 vs 0.818 | 0.08 | closed (CI upper +0.019 < +0.03) | none | arms/deepcover/DEEPCOVER.md |
C7  | Health follow-up routing | HFU-FIX, HFU-FIX2; 10-06 | 4B | deterministic replays, 0 judge | G3 58.1% / G3' 84.2% vs bar 90%; control gap +43.4 pts; 0 rule-introduced false fires | n/a (gate) | closed (no further rescue) | kept as upstream bug for PR phase | arms/hfu/HFUFIX.md; arms/hfu/HFUFIX2.md |
C8  | SC water-safety card + widened snakebite trigger | SC v1/v2/v3 (S5, S5', S5''); 10-03/04 | 4B routing | 3 blind-written held-out sets (sc-fresh3/4: 100 items each), 0 judge | S5 water 18/25 FAIL; S5' FF 5/50 (bar ≤ 2) FAIL; S5'' water 18/25 (72 %) FAIL, snakebite 20/25 PASS, FF 2/50 PASS | n/a (gate) | closed (gate FAIL), parked for the bounty | a new trigger mechanism (general water-intent classifier) on a fresh blind set | arms/sc-L0-result.txt, arms/sc-fresh3-S5prime-result.txt, arms/sc-fresh4-S5second-result.txt |   (SBt snakebite text shipped in cut 3: exclusion list)
C9  | Speculative decoding, separate draft (Qwen3-0.6B Q8_0 / Qwen2.5-1.5B) | SPECDEC; 10-06 | 4B (device) | 50 v0.1 EN s44 model-path prompts, no judge | acceptance 31.1 %, A15 decode saving 8.4 % central / -14.8 % at c +50 %, identity 31/60 greedy, +1.033 GiB, llama.rn MTP-only | n/a | closed (NO-GO, G1–G4) | draft acceptance ≥ ~60 % at n_max 4 or a 4B MTP head | arms/specdec/SPECDEC.md |
C10 | Retrieval selection: Wikivoyage practical section | TRAVELSEL; 10-05 | 4B | L0 stub replay, 71 items, 3 targets, 0 judge | gold gain 0/3 -> 1/3 (bar >= 2), 0 lost, p50 0.979x | n/a (gate) | closed (gate FAIL; frozen gold structurally capped at 1/3) | see QUEUE l.616 | arms/travelsel/TRAVELSEL.md |
C11 | Additive vital intro (q=1), deep tier | VITALPACK-ADD; 10-11/13 | deep | slice 20 + v0.2 full 110, s42, Haiku + Opus N=4 | Opus slice -0.011 (-0.039...+0.018); v0.2 full Opus +0.0012 (-0.0120...+0.0147) vs L2-H-1seed; Haiku vs TV +0.011 | 0.025 | closed: NO at slice / not detected at L2; stage 4 not run | stage 4 V-para s43 generation + 204 Opus | arms/vitalpack/VITALADD.md |
C12 | Verdict guard extensions (VG v4 threshold/superlative) | VG-S2; 10-04 | 4B | blind-written probe set #2, 120 | 1 WRONG of 2 fires; recall 1/17 self-contradictions | n/a (gate) | closed | a model-side self-consistency check, not regex | arms/vg4-S2-REVIEW.md |
C13 | Retrieval k 4 -> 3 | K3; 10-04 | 4B | v0.1 EN 60 x s44/s45, 0 calls | prompt tokens 458.9 -> 439.7, saved 19.3 (bar 100) | n/a | closed (step-0 deterministic gate) | see k3-on-cut2.md | k3-on-cut2.md |
C14 | Crypto-kit gate + travel/food routing | TF2; 10-04 | retrieval | V-exact 5 judge items x s42/s43, Opus judge.v1 | Japan 0.356 -> 0.338 (-0.018), bar >= 0.356 FAIL (inside judge noise) | see tf2-on-cut2.md | closed by frozen bar (effect not detected) | see tf2-on-cut2.md | tf2-on-cut2.md |
C15 | Cut-5 speed bundle | CUT5-SPEED; 10-06 | 4B (device) | v0.1 EN 60 x s44/s45, no judge | retrieval wall 1.071 vs bar <= 0.800 (G3 FAIL); G1/G2/G4 PASS | n/a | not adopted; components 2+3 via CUT5-LITE; perf arms parked | device ABBA (QUEUE l.699, A/B 0.445x confounded) | CUT5SPEED.md |
C16 | Local replacement for jev gates | LOCALGATE; 10-12/13 | tooling | 500 cached requests per type, 0 judge | Qwen has_fact 0.790 / FPR 0.103, quote_supports 0.850 / FPR 0.112 (bar ≥ 0.90 / ≤ 0.05); Laya zero-shot FAIL | n/a (gate) | closed (gate FAIL); jev stays | Laya fine-tune (parked) | arms/localgate/LOCALGATE.md |
C17 | Pack passage / health-query diagnostics | SECTIONHIT, HEALTHQ; 10-12 | deep | 32 in-pack v0.2 (12 reading items); 18 health-strict v0.2, 0 judge | SECTIONHIT: 0 additional, any selection lever ≤ 2/12; HEALTHQ: 0/18 dropped vs ≥ 3 | n/a | closed (diagnostic gates not met) | see BACKLOG.md:21 | arms/packcond/SECTIONHIT.md; QUEUE l.975 |
```

Fold into existing rows:
- **P4 packGround** → note on R47: "P4 step 0 10-12: F0 kept 11/32 → 14/32 (bar ≥ 16), control 6/20 (bar ≤ 4)".
- **VENUEGPS** (diagnostic, 0/7) → exclusion list, as superseded by VENUEGPS-2.

### 3b. Existing rows that need a different label or number, and l.11 additions

- **R4:** add "FOLLOWQ-G (gated Q1): 0/171 changes, Opus A/B 9/11/6 = 45 % vs bar 60 %, NOT ADOPTED; arms/followq/FOLLOWQG.md".
- **R7 reopen:** "a new prompt-wording experiment that does not raise confident-wrong (diet alone cw 5→9/8, QUEUE l.660); dropped from device-day candidates; KVFIX caches the prefix".
- **R8, R25 reopen cells:** "DEEPCOVER tested 10-12: NO (row C6)".
- **R12:** "human CLAPnq+HAGRID 6/20 (CLAPnq 3/17, HAGRID 3/3)". Add a note that SFT4B's reopen rests on addendum 2's strict review ≤ 6/20.
- **R25 label:** "NO by the criterion rule; not detected at MDE 0.08 (20, 1 seed; CI upper +0.048)".
- **R34 reopen:** replace "L1 queued Mon 10-12" with "tested: row C11".
- **R39:** "lead 1/13, 1/30; vital intro 1/6, 0/20".
- **R45:** outcome text as in M19.
- **R47:** "FAIL at step 0 (all 3 variants); X3 carried into STACK by coordinator decision outside the GROUND-ST criterion".
- **R48:** cite ACCURACY.md once the 0.68 line from M12 is added.
- **CLOSED.md:61:** QUANTCEIL text as in M10.
- **R9 (low):** the family is "FACTS r1–r6, 10-06…10-08". There is no r7 and FACTS did not start on 10-04.
- **l.11 exclusion list.** Add these adopted levers and measurements:
  - CUT4-KVFIX (device gate 3 open), CUT4-INSTANT-FRAG, INSTSUBJ, CUT5-LITE, DETMAX, CUT7
  - OPUSSHARD, KVQ8 (PASS non-inferiority −0.0077 CI90 [−0.0232, +0.0062]; device-day candidate)
  - GATEFID, VENUEGPS / VENUEGPS-2
  - AR, SC-S6 (SBt)
  - VG-L0 / VG-V5′ / VG-S (VG v3)
  - CUT3DEV, CUT3-CONFIRM, CUT3-VGAR-L1 (AR adopted; VG not adopted under it)
  - DEEPTHINK-V02: "L1 NO, Haiku +0.027 near-miss; Opus Addendum 1 +0.045 (+0.022…+0.070), v0.2 replication of the adopted lever"
  - HAIKUJUDGE and DEEPTHINK are already listed.
- **Vocabulary (LOW, no action required):** R1 (Q35), R10, R11, R15, R17, R18, R22 and R26 restate arm verdicts NO / INCONCLUSIVE as "not detected at MDE …". Consider a column "arm verdict as frozen" so the restatement is visible.

## 4. EXPOSURES gaps

### 4a. Missing event rows (append to EXPOSURES.md)

| id | arm | QUEUE line that proves it |
|---|---|---|
| E1 | DEEPHEDGE | QUEUE:952 |
| E2 | DEEPROUTE-V02 / VPARA addendum | QUEUE:882 |
| E3 | EVALFIX | QUEUE:962 |
| E4 | LENGTHSHARE | QUEUE:905 |
| E5 | LOCALGATE | QUEUE:988, :995 |
| E6 | HEALTHQ | QUEUE:975 |
| E7 | T-K4a | QUEUE:989 |
| E8 | SEEDVAR | QUEUE:873 |
| E9 | RANDOM20 / L1-PROTOCOL | QUEUE:905 |

```
E1 | 10-12 | V-para | DEEPHEDGE 0-call read of H (dt512) s42 traces, route codes only (0/58 health-strict) | script-read ids+counts | 0 generations | Opus 0; Haiku 0 | coordinator script-only; no text seen | dev-style | QUEUE l.952; arms/deephedge/DEEPHEDGE.md:5 |   (+ extend row 131 to mention the 110-id H trace read)
E2 | 10-10 | bench-v02 | DEEPROUTE-V02 (DEEPROUTE-VPARA addendum; simulated hybrid router, descriptive) | script-read (route codes from K s42 traces; K/D/H/TV Opus rows recombined) | 0 generations | 0 judge calls | coordinator script, aggregates only; outputs blind/bench-v02/runs-deeproute/ | dev | QUEUE l.882; DEEPROUTE-VPARA.md l.20-27 |
E3 | 10-12 | V-para + bench-v02 | T6 EVALFIX (wins+ties rescore, robust CIs, power; analysis only) | script-read of Opus judgment rows (H/K/Q/T/D V-para s42–s44; H/K/Q v0.2) | 0 generations | 0 judge calls | coordinator scripts arms/evalfix/tools/{winsties,robust_ci}.py; aggregates only | dev / dev-style | QUEUE T6 entry (2026-10-12); arms/evalfix/EVALFIX.md |
E4 | 10-10 | bench-v02 | LENGTHSHARE part 1 (dimshare/useful3 over existing K 2-seed + H s42 Opus rows; 0 calls) | script-read | 0 generations | none | coordinator script-only | dev | QUEUE l.905 |
E5 | 10-12/13 | V-para + bench-v02 | LOCALGATE (local Qwen3-4B + Laya over 1,000 cached jev gate requests rebuilt from wikifull A0/wikisection/packcond caches; FAIL) | script-read + local model read | 0 generations | Opus 0; Haiku 0; jev 0 | opus/medium agent + coordinator scripts; data under blind/localgate/ | dev | QUEUE l.988, l.995 |
E6 | 10-12 | bench-v02 | HEALTHQ step 0 (health-strict query vs named Wikivoyage guides; 0 LLM) | script-only (tools/healthq_check.py over questions.v02-new.jsonl + runs-packcond/p4b-v02.jsonl; ids/counts printed) | 0 generations | Opus 0; Haiku 0 | coordinator script | dev | QUEUE HEALTHQ entry (2026-10-12 21:06) |
E7 | 10-12 | bench-v02 | T-K4a wave-1 crowding replays (kit + 1 pack / se5 as peer; 110 items) | script-only (replay-crowd.ts → blind/bench-v02/runs-packs/) | 0 generations | Opus 0; Haiku 0 | opus/medium agent; 2 stderr lines with SE post titles (pack text) | dev | QUEUE T-K4a entry (2026-10-12 23:55); arms/packs/T-K4a.md |
E8 | 10-10 | bench-v02 | SEEDVAR preliminary (existing Opus rows K/D/TV s42+s43; measurement) | script-read | 0 generations | 0 calls | coordinator script (arms/seedvar/seedvar.mjs) | dev | QUEUE l.873; arms/seedvar/SEEDVAR.md:20-25 |
E9 | 10-10 | bench-v02 + V-para | RANDOM20 id selection (seed 7, category-stratified) | script-read | 20 ids per set from the 110 / 51 judged ids + category labels | none | coordinator, ids only | dev | QUEUE l.905; arms/L1-PROTOCOL.md l.28 |
```

### 4b. Summary tallies to correct

- **T1 (EXPOSURES.md:14):** add "THINK4B-Z 1" to the Opus full list and "THINK4B ×2 + full 51" to the Haiku list.
- **T2 (EXPOSURES.md:13):** add "THINK4B-V02 (ZV s42 full + slice)" to generations and "THINK4B-V02 260" to Haiku.
- **T3 (EXPOSURES.md:14):** change to "Opus 17 full (…, DT512-H 3 (incl. SEEDVAR s44), …)".

### 4c. Checked and clean

Several records list `blind_sets_used: []` even though their own blind-written sets are logged:
- CF trigger-set (EXPOSURES:89)
- CV gate-set (:90)
- INSTSUBJ lookup2 (:91)
- cut4 lookup-set (:54)
- sc-fresh3 / sc-fresh4 (:87)
- vg-probe-q / q2 (:88)

These are extraction omissions only; the ledger already has the rows.

## 5. Hygiene

### Criteria without a .sha256 sidecar (41)

**Back a decision, 21:**
- **sha cited in the result or QUEUE and matching the file** (add a sidecar): CRYPTOSEL, CVO (QUEUE:606), K3-ON-CUT2, TF2-ON-CUT2, CUT3-CONFIRM, CUT3-VGAR-L1.
- **Bar pre-registered but never frozen:**
  - K2HALF (QUEUE:961), LOCALGATE (BACKLOG:41), NUMCHECK (BACKLOG:60), HEALTHQ (BACKLOG:21)
  - DENSECHUNK (QUEUE:977), SEEDSPEC (DEEP-RESEARCH T7 row), SYNTHDEEP (LOOP-PROGRAM B7)
  - WIKISECTION (result title, LOOP-LOG:31-33), WIKISECTION-H5b (LOOP-LOG:39)
- **Bar stated only in the result:** DEEPCOV-FB, DEEPRERANK, P4.
- **No criterion and no bar:** FACTS-BLIND, LCRELAX (decided by r4to).
- **Protocol file:** L1-PROTOCOL, which has no sidecar of its own.

**Legitimately no criterion, 20** (measurement, tooling, draft):
- DEEPROUTE-OOS, DEEPROUTE-VPARA, EVALFIX, FACTS-RECALL, L1CTL, LORA-DIAG
- PACKCOND-P1, PACKCOND-P2, SECTIONHIT, SELFTEST-SCORES, WAVE3
- T-K2, T-K4a, T-K4c, T-K4d, T-K6b (pack probes run under PACK-CATALOGUE D-K3)
- PROBES, SEEDGEN, T1-DEEP35, THREADS2 (HANDOFF-2026-10-10:28 says "criterion already written"; none exists)

### sha and file-state problems

- **LOSSMAP:** criterion edited after the freeze (M72).
- **GROUND-ST:** step-0 patch 5fd74a85… is no longer on disk; the sidecar now holds the addendum-1 patch 9acb5160….
- **PROMPTDIET:** first-build patch f5ca5df6… overwritten by rev 1 (bb287dde…).
- **SC-L0 / CUT3DEV:** patches re-cut under the same filenames (M90, M92). Candidate 99baf3bc… is not on disk.
- **MOESCREEN:** the pre-run sha a3667f51… cannot be verified; only the addendum-1 sha 386e983c… is stored.
- **JUDGE2:** run-1 criterion sha 2c3ff0eb… was overwritten in the sidecar.
- **ORACLE-ST:** the extraction claim of a patch mismatch is false (dbecafcd… matches).

### Results without a frozen criterion

DEEPCOV-FB, DEEPRERANK, K2HALF, LOCALGATE, NUMCHECK, P4, HEALTHQ (the verdict is only in QUEUE:975, BACKLOG:21 and HANDOFF-2026-10-13:21), SEEDSPEC, SYNTHDEEP, WIKISECTION, WIKISECTION-H5b.

### Criteria or planned outputs without a result

- ORACLE-ST: running; ORACLE-ADD was at 138/180 at 21:57, ORACLE-ONLY not started.
- SFT4B: no SFT4B.md (STAGE0 and STAGE1 only).
- LORA-DIAG: dead draft.
- PACKROUTE: no PACKROUTE.md and no packroute patch.
- PACKROUTE-2: no STEP0.md or PACKROUTE2.md.
- GROUND-ST: no GROUND-ST.md.
- PACKDENSE: patch never built; the FAIL was declared by projection without the gate replay.
- CVO: no result file for gate #4.
- Stages that never ran: CVH step 2, VITALPACK-ADD stage 4, DEEPCOVER full 110 (unjudged), THINK4B s43 (the criterion specifies a two-seed verdict).

### Post-hoc rule changes missing from RULE-CHANGES.md

- CROWDQ reach band (M51)
- GROUND-ST X3 carry-over (M33, M34)
- CRYPTOSEL latency metric (M52)
- FACTS-r6 fallback override (M69)
- VG adoption gate redefined at QUEUE:559 (M93)
- LOSSMAP re-freeze (M72)
- VITALPACK-ADD stage-3 OR rule: Δ +0.0012 > 0 meets the first clause literally, but the arm stopped anyway
- DENSECHUNK-ST2 addendum: already logged as RULE 26

### Stale headers, TL;DRs and internal inconsistencies (from the records' issues)

**Stale status text:**
- CF.md:20-21; CV.md:3; PROMPTDIET.md:3
- FTDATA-PILOT.md:8, FTDATA-1K.md:9, FTDATA-REJ.md:24/:32 and HUMANSFT.md:29/:41 still say PENDING
- HAIKUJUDGE.md:48 says "NOT applied"
- DENSECHUNK-ST2.md:1/:8 and the ST2-GATE.md header
- LOCALGATE.md:31/:38; WIKIFULL STAGE-A.md body (the RUNNING report was never replaced)
- WIKISECTION.md:13; VITALADD.md:3/:14; packroute2/ACCURACY.md:1
- RATIONALEPASS.md:30 ("EXPOSURES row not yet written"; it now exists at l.133)
- CUT3DEV.md TL;DR (l.6-10); CUT4.md's two APK identities

**Number mismatches inside a file:**
- DT512.md:37 says 0.43 where the table has 0.436; DT512.md:38 says "256 not tested".
- DEEPHEDGE.md:5: 10 + 3 ≠ 12.
- G4ENG TL;DR confident-wrong vs gate table (4 vs 5 failures).
- DEEPTHINKV02.md:22: "55/40" vs table 51/19/40.
- EVALFIX.md:2 vs :4/:27: tie wording; "five delta rows" is really four plus one level row.
- LOSSMAP.md:5 "co-fires on 49–52 %": that is the loss share; the item share is 57 % / 64 %.
- FACTS-r6-SET4 "11/12" should read 10/12.
- SEEDGEN 56/59, 56/102 and 24/25 superseded by the F8 fix.
- SEEDSPEC set-B labeller inconsistency (pattern_all vs pattern_of_wrong_any).

**Data gaps:**
- DT512 3-seed aggregate files are empty (0–1 bytes).
- DT256 s43 head-to-head is identical for Q vs T and Q vs H (10/15/26); unresolved.
- DT512-V02 per-category report missing (category key "?").
- QUANTCEIL V-para s43 floor-adj missing from the table (aggregate: Q 0.4329 vs H 0.4603).
- LENGTHSHARE truncated at 80 words against the criterion's 95.
- VITALADD.md:15 says "v0.2 smoke 3"; the criterion says v0.1.

**Mislabelled files and outputs:**
- Version labels: vg-equiv-v3-vs-v2.txt:2, vg4-equiv-vs-v3.txt:4, sc-v3-dev-result.txt "v1" column.
- Patch names: cryptotruth, detmax, hfufix and followqg are named "on-cut4" but carry cut 5 / cut 6 content.
- Stray files: tools/ikifull_gate.py; seedgen runs/ files with spaces in their names.
- Inconsistent path styles inside .sha256 files (cosmetic).

**Dates:**
- CVS and CVH ran 2026-10-04 local, not 10-05.
- LCRELAX is 10-07, not 10-08.
- RANDOM20 files were created 10-10; the addendum is labelled 10-11.
- GROUND-ST, LENGTHSHARE, SFT4B and JUDGEVAR freeze labels do not match file mtimes or QUEUE times.

## 6. What verified clean

"Clean" means the arm has no HIGH or MEDIUM item. The input does not carry a per-number count of cross-checked values. Of the 118 criteria with a sidecar, every sha matched except LOSSMAP. CLOSED rows: 69 consistent, 5 discrepant.

| Family | Arms | Clean | Clean arms |
|---|---|---|---|
| 4B fast path (incl. FACTS, VG, SC, computed verdict) | 42 | 20 | INSTANT-FRAG, FACTS r1/r2/JUDGE/RECALL/r4/r5, LCRELAX, G4E4B, G4ENG, HFU, INSTSUBJ, MP4B, Q35, SC-V2-S5PRIME, SPEEDPACK, SC-S6, VG-L0, VG-V5′, VG-S |
| Deep tier | 28 | 14 | COMPLETE, DEEPBO2, DEEPFULL-F1, DEEPITER, DEEPREAD, DEEPROUTE, DEEPROUTE-OOS, DEEPSAMP, DEEPVPARA, MOESCREEN ×2, SEEDSPEC, T1-DEEP35, GEMMATHINK |
| Retrieval | 22 | 11 | CHATGATE, DEEPNORAG, DENSECHUNK-ST/ST2, FOLLOWQ, NAMEDSLOT, PACKDENSE, DENSECHUNK, RETHURT, WIKIFULL-STAGE-A, WIKISECTION-H5b |
| Packs | 23 | 12 | DEEPWIKI, NOTES35, PACKCOND-P2, PACKROUTE, SELFTEST-SCORES, WAVE3, T-K4d, T-K6b, PACKS-L2, STACK, STACK-2, VITALPACK-DEEP |
| Judge protocol | 14 | 8 | HAIKUJUDGE, JUDGE2, JUDGEVAR, L1CTL, OPUSSHARD, PARJUDGE, RATIONALEPASS, SIGNAL20 |
| Device | 8 | 6 | DEEPPAR, DEEPPAR-L1, DEEPSPEED, DETFU, DETMAX, THREADS2 |
| Claim build | 6 | 4 | CUT5-SPEED, CUT5-LITE, NUMCHECK, CUT3-CONFIRM |
| Data / fine-tune | 6 | 3 | FTDATA-PILOT, FTDATA-1K, LORA-DIAG |
| Tooling | 10 | 7 | GATEFID, T-K4c, PROBES, VENUEGPS, VENUEGPS-2, VG-PROBE-Q, VG-PROBE-Q2 |
| **Total** | **159** | **85** | |

## 7. LOW items: count per arm (307 total)

- **6:** SFT4B, WIKIFULL-STAGE-A
- **5:** DEEPCOVER, HUMANSFT, LOCALGATE, CUT3DEV
- **4:** CUT7, DEEPITER, DEEPTHINK-V02, DENSECHUNK-ST, DENSECHUNK-ST2, DT512, JUDGEVAR, LENGTHSHARE, QUANTCEIL, RATIONALEPASS, SYNTHDEEP, VITALPACK-ADD, WIKISECTION
- **3:** CRYPTOTRUTH, CV, CVS, DEEPHEDGE, DEEPTHINK, DEEPVPARA, DEEPWIKI, DT512-V02, FACTS-r6, G4ENG, GROUND-ST, INSTSUBJ, LOSSMAP, NOTES35, PACKCOND-P1, SELFTEST-DEEP, PACKS-L2, PARJUDGE, RETHURT, T1-DEEP35, THINK4B, GEMMATHINK
- **2:** COMPLETE, CROWDQ, CRYPTOSEL, CUT4-KVFIX, CUT4-INSTANT-FRAG, CUT5-SPEED, CUT5-LITE, CVH, CVO, DEEPBO2, DEEPCOV-FB, DEEPCTX, DEEPFULL-F2, DEEPPAR-L1, DEEPREAD, DEEPRERANK, DEEPROUTE-OOS, DEEPROUTE-VPARA, DEEPSAMP, DEEPTHINK-2, DETMAX, EVALFIX, LCRELAX, FTDATA-REJ, GATEFID, HAIKUJUDGE, JUDGE2, K2HALF, LORA-DIAG, MOESCREEN, MP4B, OPUSSHARD, PACKDENSE, SECTIONHIT, HEALTHQ, PACKROUTE-2, SELFTEST-SCORES, PROMPTDIET, Q35, SC-V2-S5PRIME, SC-V3-S5SECOND, SEEDSPEC, SEEDVAR, STACK-2, THREADS2, VENUEGPS, VENUEGPS-2, VITALPACK-DEEP, WIKIFULL-REOPEN, WIKISECTION-H5b, AR, SC-S6, VG-L0, VG-S, SIGNAL20, K3-ON-CUT2, TF2-ON-CUT2, CUT3-CONFIRM, CUT3-VGAR-L1
- **1:** CF, CRYPTOFACTS-step1, DEEPNORAG, DEEPROUTE, DEEPSPEED, DEEPTHINK-V02-ADDENDUM1, DT256, FACTS, FACTS-RECALL, FACTS-r4, FOLLOWQ, FTDATA-PILOT, FTDATA-1K, G4E4B, GROUND-ST addendum 1, HFUFIX, HFUFIX2, KVQ8, L1CTL, MOESCREEN-gemma4, NAMEDSLOT, NUMCHECK, ORACLE-ST, P4 packGround, PACKROUTE, WAVE3, T-K4a, SEEDGEN, SPEEDPACK, STACK, THINK4B-V02, VG-PROBE-Q, SC-L0, SC-v2-S5prime, SC-v3-S5second, VG-V5prime, VG4-S2, RANDOM20, L1-PROTOCOL
- **0:** CHATGATE, DEEPFULL-F1, DEEPPAR, DETFU, FACTS-r2, FACTS-JUDGE, FACTS-BLIND, FACTS-r5, FOLLOWQG, HFU, PACKCOND-P2, DENSECHUNK, T-K2, T-K4c, T-K4d, T-K6b, PROBES, SPECDEC, TRAVELSEL, VG-PROBE-Q2

## 8. Recommended order of fixes

| Step | Tick | File(s) | What |
|---|---|---|---|
| 1 | T+1 | CLAUDE.md "Current state" | Fix H1, M3, M4, M5, M6, M7 and M1. Drop "open: SELFTEST-DEEP topic half". |
| 2 | T+1 | EXPOSURES.md | Append E1–E9 (§4a), fix tallies T1–T3, extend row 131. This closes all 12 HIGHs except H1, plus M94–M96. |
| 3 | T+1 | CLAIM-DRAFT.md:126/:191; BAR-TABLE.md:113/:134; REPORT-PACKS (none needed after step 5) | Send the HUMANSFT wording to the independent Opus reviewer (content rule). Fix BAR-TABLE M9, M11 and the WIKISECTION parenthetical (M19). |
| 4 | T+2 | CLOSED.md | Add C1–C17. Apply the §3b label fixes (R4, R7, R8, R9, R12, R25, R34, R39, R45, R47, CLOSED.md:61) and the l.11 exclusion additions. |
| 5 | T+2 | packroute2/ACCURACY.md, then CLOSED R48 | Add the 0.68 / 0.85 / 0.9 line (M12) so R48 and REPORT-PACKS cite the arm, not QUEUE. |
| 6 | T+2 | HANDOFF-2026-10-13.md (:11, :57), HANDOFF-2026-10-12.md (:18, :28, :30), HANDOFF-2026-10-11.md:15, HANDOFF-2026-10-10.md (:9, :48) | Add errata lines for M14–M18, M7, M9, M62 and H3. |
| 7 | T+3 | QUEUE.md (append-only correction rows) | l.549, 590/592, 607, 661, 758, 820, 828, 846, 908, 914, 976, 1033, 1069. One correction row per original line. |
| 8 | T+3 | BACKLOG.md | l.21, 25, 26, 31, 48, 57, 58, 87, 88, 90 (M60–M62, M75–M77, M80, M83, M84, M87, M88). |
| 9 | T+3 | RULE-CHANGES.md; lossmap/ | Log CROWDQ band, GROUND-ST X3, CRYPTOSEL latency, FACTS-r6 override, the VG gate at QUEUE:559 and VITALADD stage-3 reading. Re-freeze LOSSMAP as v2. |
| 10 | T+4 | Arm files + sidecars | Fix the stale TL;DRs and headers in §5 (CF, CV, CVO gate-4 note, PROMPTDIET, FTDATA ×3, HUMANSFT, SYNTHDEEP:7, DEEPTHINK2 note, LOSSMAP:5/:10, T-K2, CUT3DEV:39/:233/:295, cut3-vgar-L1:54, K2HALF:21, P4-GATE:3, GATE.md addendum, FACTS-BLIND, FACTS-r6-SET4, FTDATA-REJ:24). Write `.sha256` sidecars for the 6 criteria whose sha is cited but has no sidecar. Standing rule from here on: no decision without a sidecar. |

---
# Completeness critic (independent opus/high agent)

## Completeness critique: LEDGER-AUDIT-2026-10-13 (pass 2, 159 records)

### 1. Arm dirs and loose files with no record
- **`arms/rivalset/`** has no record. Its criterion is `RIVALSET-criterion.md`, frozen "2026-10-13 21:1x"; the sha `508090399d4e87a4…` matches, and the launch is logged at QUEUE:1068. Grading is already done: `logs/grade_opus_A.log`, `grade_opus_C.log` and `grade_haiku_AC.log` each end "DONE" (Opus 144, Haiku 144). System B (BOAR 4B) has requests only, `runs/rivalset-cut7-s42.requests.jsonl` (72), and no answers. `logs/wait_and_gen.log` shows "free=0 disk=5GiB" at 22:16, but the criterion requires "disk ≥ 8 GiB", with a deadline of 00:50. Pass 1's critic already flagged this (LEDGER-AUDIT-2026-10-13.md:249); pass 2 dropped it.
- **Outside `arms/`, no record:**
  - `packs-research/READERSWEEP-2026-10-13.md`, completed per QUEUE:1071.
  - `device/A15-SMOKE-DIAGNOSIS.md` and `A15-LATENCY-BUDGET.md`. These are the source of CLAUDE.md's "cut 6 ran on an 8 GB Galaxy A15 (73/73)".
- Every other root file (ar/sc/vg/vg4/signal20/random20/CUT3DEV/L1-PROTOCOL, plus k3/tf2/cut3-* at the coordinator root) is covered.

### 2. Sub-arms with their own gate or verdict but no record
- **`facts/FACTS-r3.md`:** r3 dev gates, recall 30/40 = 75 % against an expected ≥ 80 %, FP 2/20 → 0/20 (QUEUE:733). The records skip from r2 to r4. CLOSED R9 cites r3's blind-set-2 result.
- **`packs/tk2-replay/TK2-REPLAY.md`:** verdict "NOT label-only", kept list changes on 52/180 (QUEUE:1079). The audit uses it as evidence in M81, but there is no record. The T-K2 record still reads "tooling (done)".
- **`deepvpara/DEEPVPARA-CATS.md`:** descriptive per-category diagnostic, no record.
- **Step-0 gates that sit inside other records** (acceptable, but not listed):
  - `densechunk-st/ST2-GATE.md:1` "FAIL at step 0 on G2 … by the letter". The DENSECHUNK-ST2 record says only "not decided at MDE 0.03", although the arm went to Opus L2 after this FAIL.
  - `packcond/P4B-GATE.md`

### 3. Ledger rows naming arms absent from the records
- **CLOSED.md:**
  - R1 names Qwen3.5-9B and Ministral 3 8B; the source is `../anvil/cards/dense-9b-default-model.md`, which is not an arm record.
  - R5 "#6 enwiki top-100k v1" (QUEUE l.147-160) has no record.
  - R35 MTP is sourced from WEB-SWEEP only.
- **BACKLOG §1 rows with no record:**
  - QWRITE (:22), TK2-FIX (:26, new 22:4x), H8-ST (:33)
  - READERSWEEP (:34). Its status is still "proposed; web sweep running", although QUEUE:1071 has it completed.
  - DEVICE-DEEP (:35), PHONEFAIL (:36), PACKREAD-NATIVE (:37)
  - SELFTEST-SCORE (:41, merged), Housekeeping (:45, done)
  - LESPORT (:51), NEWMODEL (:52), QNOTES (:53), HEALTHFALLBACK (:59), T3 CMPCARD (:68, "dropped by T1")
- **QUEUE-only:** V02GOLD (QUEUE:925) and DEVICE-CUT7 (QUEUE:1076, package built) have no record either.

### 4. Audit claims that are wrong, stale or uncited (about 45 checked with sed -n)
**Line references gone stale.** CLAIM-DRAFT was edited at 22:08 (v3.9) and BACKLOG at 22:04, both after the 21:43 extraction.
- **CLAIM-DRAFT:**
  - HUMANSFT is at :128/:193, not :126/:191. :126 is now the DEEPFULL row and :191 is "A stronger reader".
  - "143 s" and S44 are at :192/:259, not :190.
- **BACKLOG:** every reference from :26 on is one line short:
  - M84 SFT4B :26→:27; M76/M77 ORACLE-ST :31→:32; M75 LOSSMAP :48→:49
  - M87 :57→:58; M62 :58→:59; M61 :87→:88; M60 :88→:89; M88 :90→:91
  - §5 LOCALGATE :41→:42; NUMCHECK :60→:61
  - BACKLOG:21 and :25 are still correct.

**Claims that do not survive a check:**
- **H1 "CLAIM-DRAFT.md:12 already separates them" is wrong.** :12 puts cut 3's two-seed 0.389 (0.347–0.435) beside cut 6's s42 0.397. CLAIM-RESULTS-cut6.md:38 gives cut 6 as 0.388 (0.346–0.434), and :40 shows 0.389 is cut 3. So the audit's "likely truth" (0.512 / 0.388) and the claim text (0.513 / 0.389) disagree, and the audit marks the claim text as checked.
- **M72 "criterion edited after the freeze" is not shown.** `LOSSMAP-criterion.md` and its `.sha256` have the same mtime, 10-11 12:07:30. That fits a sha taken before the final save. Pass 1's critic raised this; it was not addressed.
- **§6 "118 criteria with a sidecar":** I count 104 (109 `*criterion*.md` under arms/, 5 without a sidecar).
- **§5 "41 criteria without a sidecar":** only 9 criterion files lack one:
  - in arms/: CVO, CRYPTOSEL, LORA-DIAG.DRAFT, DENSECHUNK-ST addendum-1, DENSECHUNK-ST2 addendum-1
  - at the coordinator root: k3, tf2, cut3-confirm, cut3-vgar-L1
  - The other names have no criterion file at all. The audit never says that the ST2 addendum, the one that let ST2 continue past its step-0 FAIL, has no sha.
- **M7 "likely truth 143 s" is unsettled.** `DEEPTHINK.md:16-17` gives per-seed p50 142.9 / 146.0 s (mean 144.45), so 145 is not clearly wrong.
- **ORACLE-ST status "0 judge calls" is stale.** `oracle-st/logs/judge_chain.log` has 14 JUDGED lines, the last "JUDGED st-boar-medlineplus-en … haiku … 22:20:01". The generation log shows "free=4GiB" at 22:02 and then "wait-disk", against the criterion's "MacBook disk ≥ 8 GiB" (`ORACLE-ST-criterion.md:36`).

**Uncited claims:**
- TL;DR "CLAIM-DRAFT already prints … 143 s / 146 s"
- §5 GROUND-ST patch 5fd74a85…, MOESCREEN a3667f51…, JUDGE2 2c3ff0eb…, ORACLE-ST dbecafcd…
- the date lines for CVS/CVH (10-04), LCRELAX (10-07), and the GROUND-ST/LENGTHSHARE/SFT4B/JUDGEVAR "freeze label vs mtime" (no values given)
- the bucket counts in §0

### 5. Categories the audit did not look for
- **Judge-model mixing.**
  - CLAUDE.md:21 gives "packs +0.032 single / −0.016 crowding / keep+quota +0.005 / deep tier +0.063" with no judge named. All four are Haiku L1, and Opus L2 values exist (+0.042, −0.019, +0.004; REPORT-PACKS:11, :16, :207). M3's fix (+0.054) is also Haiku-only (`SELFTEST-DEEP.md:1` "Haiku 5.5-low") and still unlabelled.
  - The BACKLOG §3 "result" column (:87-:97) puts Opus rows (THINK4B, DENSECHUNK-ST2) beside Haiku rows (DEEPFULL F2, DEEPCTX, VITALPACK-ADD, R22) with no judge column.
- **Hardest-20 slice treated like a neutral slice.**
  - DEEPNORAG, DEEPWIKI, DEEPSAMP, DEEPCTX, DEEPFULL, GEMMATHINK and MP4B ran on signal20, the 20 hardest items. L1-PROTOCOL:28 itself records that this slice inflates Δ (THINK4B +0.091 on the slice vs +0.026 on the full set).
  - CLAIM-DRAFT:126 says only "20-item V-para slice". DEEPNORAG's −0.045, which supports "the device deep path keeps retrieval", rests on that slice. The audit marks DEEPNORAG clean.
- **Set-status wording.** v0.2 is called "held-out" at CLAUDE.md:22, `cut7/CUT7.md:1` and `:33`, and CLAIM-DRAFT:162 ("held-out 0.389"). That last one is inside v3.9, which relabelled v0.2 "formerly held-out".
- **Deep-tier results called "held-out-style".** CLAIM-DRAFT:1 and :202 say "held-out-style sets" for deep-tier numbers. The 10-09 ruling (EXPOSURES:99) makes them dev-style.
- **Comparator ambiguity.**
  - DT512-V02's "+0.089 vs K (4B claim run)" is measured against K s42 alone (0.519), not the two-seed claim run (0.512). M6's fix keeps the label.
  - `DT512V02.md` gives two CIs for the same +0.089: :2 "(+0.057…+0.122)" and :17 "(+0.054…+0.126)".
- **Withdrawn premise still stated.** BACKLOG:53 (QNOTES) says "prior ≈ 0 after H5 (the facts are outside Wikipedia and outside the model)". DEEP-RESEARCH D-1 withdrew that premise, and BAR-TABLE:145 marks it withdrawn. The audit fixes only R45 and BAR-TABLE:134.
- **Budget ledger.** BACKLOG §0 stops at "10-13 (06:1x→13:0x) 720". It leaves out:
  - PACKS-L2 1,240 Opus (QUEUE:1073), VITALADD 220 Opus (QUEUE:1065), RIVALSET 144 + 144
  - CROWDQ 360 Haiku (QUEUE:1033)
  - SELFTEST-DEEP 720 Haiku, which §0 records as "deep 80"
- **Infra and disk rules.** RIVALSET and ORACLE-ST are both waiting on the same MacBook disk (4–7 GiB against their 8 GiB floors). `arms/localgate/.venv` is 926 MB inside the boar-rnd tree.
- **Fixes already proposed.** `proposals/LEDGER-FIXES-2026-10-13.md` holds ready-to-paste CLOSED / EXPOSURES / CLAUDE fixes from pass 1, and the audit does not reconcile against them. Several pass-1 critic items are still open in pass 2: RIVALSET, FACTS-r3, cut lineage, Haiku vs Opus, LOSSMAP mtime, the 145 s reading.

---
# Appendix A — complete machine-generated lists from the verified records (coordinator script over arm-index-2026-10-13.json v2)


## A.1 HIGH discrepancies (12)

| arm | what | source_a | source_b | likely truth | fix |
|---|---|---|---|---|---|
| CUT7 | CUT7.md:33 'CLAIM-RESULTS-cut6 headline 0.512 / V-para 0.413 stand for cut 7' vs CLAUDE.md:22 'Honest numbers: v0.2 held-out raw 0.519 / **floor-adjusted 0.40**'. The CLAUDE.md figures are the s42-only row (BAR-TABLE.md… | rnd/research/coordinator/arms/cut7/CUT7.md:33 | <workspace>/CLAUDE.md:22 | Two-seed v0.2 raw 0.512 (0.478–0.549), floor-adj 0.388 (0.346–0.434); 0.519/0.397 is s42 only | CLAUDE.md:22 → 'v0.2 raw 0.512 (two seeds; s42 alone 0.519) / floor-adjusted 0.388 (s42 0.397)' |
| DEEPHEDGE | DEEPHEDGE.md:5 'On V-para: **0/58** items route health-strict' and QUEUE 'V-para 0/58 → no bar effect' prove a script read of H's V-para traces for this arm; EXPOSURES has only the bench-v02 row '\| 10-12 \| benc… | rnd/research/QUEUE.md:952 | rnd/research/coordinator/EXPOSURES.md:131 | The arm read route codes (counts only) from H's V-para s42 traces; that is an exposure event under the EXPOSURES protocol ('any ... script read ... that touche… | Append to EXPOSURES.md: '\| 10-12 \| V-para \| DEEPHEDGE 0-call read of H (dt512) s42 traces, route codes only (0/58 health-strict) \| script-read ids+c… |
| DEEPROUTE-VPARA | The v0.2 addendum (QUEUE "DEEPROUTE-V02 (descriptive, 0 calls; 15:31; arms/deeproute/DEEPROUTE-VPARA.md addendum): on v0.2 the R2 rule fires on **33/110 (30 %)**") script-read the v0.2 H/K Opus rows and K traces and wro… | rnd/research/QUEUE.md:882 | rnd/research/coordinator/EXPOSURES.md:108 | A bench-v02 script-read exposure on 2026-10-10 15:5x is unlogged | Append to EXPOSURES.md: '\| 10-10 \| bench-v02 \| DEEPROUTE-V02 (DEEPROUTE-VPARA addendum; simulated hybrid router, descriptive) \| script-read (route codes fr… |
| EVALFIX | EVALFIX read Opus judgment rows on V-para and bench-v02 by script ('T6 EVALFIX done … 1 tie in 1,052 mapped rows … H/K/Q win-rate 0/51 both seeds'), but EXPOSURES.md has no EVALFIX/T6 row (grep 'evalfix\|T6\|wins… | rnd/research/QUEUE.md:962 | rnd/research/coordinator/EXPOSURES.md (no row; cf. :107, :140) | Script-only exposure of both sets on 10-12 that went unlogged (tools/winsties.py:10-17, tools/robust_ci.py:14-22) | Add EXPOSURES row: '\| 10-12 \| V-para + bench-v02 \| T6 EVALFIX (wins+ties rescore, robust CIs, power; analysis only) \| script-read of Opus judgment r… |
| LENGTHSHARE | QUEUE l.905 'Step 2a (0 calls): per-dimension ratios (arms/lengthshare): ... v0.2 H 0.743 / 0.375 / 0.408; usefulness ≥ 3 share ... v0.2 34.5 % → 58.2 %' (a script read of the bench-v02 judgment rows) vs EXPOSURES.md:11… | rnd/research/QUEUE.md:905 | rnd/research/coordinator/EXPOSURES.md:114 | Part 1 read the existing v0.2 (and 2-seed V-para) judgment rows by script on 10-10, with 0 calls; only Part 2 on V-para was logged. | Append an EXPOSURES row: '10-10 \| bench-v02 \| LENGTHSHARE part 1 (dimshare/useful3 over existing K 2-seed + H s42 Opus rows; 0 calls) \| script-read \| 0 gen… |
| LOCALGATE | QUEUE: 'LOCALGATE ... (23:51; ... requests rebuilt offline under blind/localgate/, no text seen): 500 requests per type ...' (rationales from V-para/v0.2 Opus judgments, read by harvest.py and by local Qwen3-4B and Laya… | rnd/research/QUEUE.md:988 | rnd/research/coordinator/EXPOSURES.md:135 | On 10-12/13 a script re-read blind-derived judgment rationales from V-para and bench-v02 (+ pack chunks) and local models classified them. Nothing was s… | Append: '10-12/13 \| V-para + bench-v02 \| LOCALGATE (local Qwen3-4B + Laya over 1,000 cached jev gate requests rebuilt from wikifull A0/wikisection/pac… |
| HEALTHQ | QUEUE.md:975 'HEALTHQ → closed at step 0 … script-only on the v0.2 items + the p4b replay, ids/counts only' (tools/healthq_check.py:4 'Inputs: blind/bench-v02/live/v0.2/questions.v02-new.jsonl … blind/bench-v02/runs-pac… | rnd/research/QUEUE.md:975 | rnd/research/coordinator/EXPOSURES.md (no row; P4/PACKDENSE rows at :139,:141 d… | HEALTHQ read bench-v02 questions and replay outputs by script on 2026-10-12 21:06 and the exposure is unlogged | EXPOSURES.md → add '\| 10-12 \| bench-v02 \| HEALTHQ step 0 (health-strict query vs named Wikivoyage guides; 0 LLM) \| script-only (tools/healthq_check.py over… |
| T-K4a | T-K4a ran v0.2 replays 'outputs in blind/bench-v02/runs-packs/' (QUEUE: 'replays under blind/bench-v02/runs-packs/'). EXPOSURES.md has no T-K4a row: the only wave-1 pack row is 'T-K4d wave-1 pack coverage probe' on vita… | arms/packs/T-K4a.md:4 (and ../QUEUE.md:989) | EXPOSURES.md:145 | T-K4a's script-only bench-v02 exposure was never logged. QUEUE:1080's ledger audit lists T-K4a among '10 arms touched a blind set with no row'. | Add an EXPOSURES row: '\| 10-12 \| bench-v02 \| T-K4a wave-1 crowding replays (kit + 1 pack / se5 as peer; 110 items) \| script-only (replay-crowd.ts → blind/b… |
| T-K4a | HANDOFF says 'Script-only reads only (EXPOSURES.md rows 10-12/10-13: … WIKIFULL A/B, T-K4a/d, T-K6b …)', but no T-K4a row exists in EXPOSURES.md (only T-K4d at :145). | HANDOFF-2026-10-13.md:57 | EXPOSURES.md:145 | The handoff overstates the ledger. The T-K4a row is missing. | Add the T-K4a EXPOSURES row (above), which makes HANDOFF-2026-10-13.md:57 true. |
| SEEDVAR | SEEDVAR script-read the existing bench-v02 Opus rows: 'SEEDVAR preliminary on v0.2 (existing rows, 0 calls; 12:35): two-seed spread on v0.2 (110 ids, Opus)' and SEEDVAR.md '## v0.2 (110 ids, Opus, two seeds; existing ro… | rnd/research/QUEUE.md:873 | rnd/research/coordinator/EXPOSURES.md:110 | bench-v02 was script-read on 10-10 by seedvar.mjs (0 calls). v0.2 is already burnt/dev, so its status does not change, but the event row is missing (also flagg… | Append to EXPOSURES.md: '\| 10-10 \| bench-v02 \| SEEDVAR preliminary (existing Opus rows K/D/TV s42+s43; measurement) \| script-read \| 0 generations \| 0 cal… |
| RANDOM20 (random stratified slices) | QUEUE.md:905 says '(d) `arms/random20-v02.ids` (a3e43672…) and `arms/random20-vpara.ids` (e4853b32…), seed 7, stratified by category (v0.2: expl 4, reas 4, ...; V-para: expl 6, ...)'. This is a script-read of ids and ca… | rnd/research/QUEUE.md:905 | rnd/research/coordinator/EXPOSURES.md:70 | The RANDOM20 id and category selection on bench-v02 and V-para is an unlogged script-only exposure (ids only, 0 calls). | Add an EXPOSURES.md row: '\| 10-10 \| bench-v02 + V-para \| RANDOM20 id selection (seed 7, category-stratified) \| script-read \| 20 ids per set from the 110 /… |
| L1-PROTOCOL (judge triage protocol) | The protocol's SLICE20 addendum (L1-PROTOCOL.md:14) has an EXPOSURES row (EXPOSURES.md:70 'SLICE20 id selection'). Its RANDOM20 addendum (L1-PROTOCOL.md:28; QUEUE.md:905) selected ids from bench-v02 and V-para an… | rnd/research/coordinator/arms/L1-PROTOCOL.md:28 | rnd/research/coordinator/EXPOSURES.md:70 | The RANDOM20 id selection is unlogged. This is the same gap as the RANDOM20 record. | Add the RANDOM20 id-selection row to EXPOSURES.md (see the RANDOM20 record) |

## A.2 MEDIUM discrepancies (97)

| arm | what | source_a | source_b | likely truth | fix |
|---|---|---|---|---|---|
| CF | QUEUE:586 "**CF data review: FAIL → CF NOT adopted**" is a decisive verdict on a packs lever, but CLOSED.md has no row for CF. The un-sourced-packs note at CLOSED.md:60 names only "the 4B \"packs\" beyond enwiki v1 (Map… | <workspace>/rnd/research/QUEUE.md:586 | <workspace>/rnd/research/coordinator/CLOSED.md:60 | CF is a closed lever (L0 FAIL, not adopted, QUEUE:605 lists it among exhausted levers) and is missing from the registry. | Add a CLOSED.md row: 'CF country-facts lookup (Wikidata) \| 10-04 \| 4B \| L0 deterministic, 0 judge \| data 126/150 = 84.0% (bar 98%), trigger recall 80/100 (… |
| CF | The CF.md L0 table still reads bar 1 "**Pending reviewer**" and bar 2 "Blind set: **pending, coordinator**". The verdict files say "VERDICT: FAIL. Agreement 126/150 = 84.0%" and "recall 80/100 (80 %, bar >= 90 %) FAIL".… | <workspace>/rnd/research/coordinator/arms/cf/CF.md:20-21 | <workspace>/rnd/research/coordinator/arms/cf/trigger-result.txt:2 | Both bars FAILED (data-REVIEW.md:1; trigger-result.txt:2,6; QUEUE:584, 586). | In CF.md:20-21 replace 'Pending reviewer' with 'FAIL 126/150 = 84.0% (data-REVIEW.md)' and 'pending, coordinator' with 'FAIL recall 80/100, FF 0/100 (trigger-r… |
| CROWDQ | The frozen stop gate reads "reach check in the traces (fact article kept must reproduce the replay's 46 ± 3, else stop and report the discrepancy before judging)". The result applies "ruling QUEUE 15:0x: band 40 ± 4 = 3… | <workspace>/rnd/research/coordinator/arms/crowdq/CROWDQ-criterion.m… | <workspace>/rnd/research/coordinator/arms/crowdq/CROWDQ.md:10-11 | The band was rescaled for a different matching method (URL on traces vs chunkId on replays). That was ruled and logged in QUEUE:1030 before judging. Under the … | Add a RULE-CHANGES.md row: 'CROWDQ stage-2 reach band 46 ± 3 (chunkId replay) → 40 ± 4 (URL match on cut-7 traces, 46 × 59/68), ruled 15:08 before judging (QUE… |
| CROWDQ | QUEUE:1033 has "simplewiki 36 % of kept slots (66 of the 164 non-own slots)". The arm has "foreign ... kept slots ... P 164: **simplewiki 66 (40 %)**" and separately "Kept share under P (all kept slots, 282): simplewiki… | <workspace>/rnd/research/QUEUE.md:1033 | <workspace>/rnd/research/coordinator/arms/crowdq/CROWDQ.md:15 | 66/164 = 40 % of foreign kept slots; 102/282 = 36 % of all kept slots (aggregates/crowdq.json kept_P_by_owner simplewiki 102, share 0.362). | In QUEUE:1033 change 'simplewiki 36 % of kept slots (66 of the 164 non-own slots)' to 'simplewiki 36 % of all kept slots (102/282; 66 of the 164 non-own slots … |
| CRYPTOFACTS-step1 | QUEUE: 'Line closed at step 1.' vs CLOSED.md: no CRYPTOFACTS row (grep -i 'cry\|eip' in CLOSED.md returns only row 9 FACTS) | rnd/research/QUEUE.md:796 | rnd/research/coordinator/CLOSED.md:24 | decisive 0-call gate FAIL (step-1 NO), which CLOSED.md's own rule labels 'closed (gate FAIL)' | add a CLOSED.md 4B-side row: 'Crypto structured-fact instant tier (CRYPTOFACTS step 1); 10-07 \| 4B \| v0.1 11 crypto items, 0 calls \| A0/B2/C9/D0; bars (i) 2… |
| CRYPTOSEL | L0 latency bar 'retrieval p50 ≤ 1.2× cut 3' (criterion) judged PASS on '1.005×' (p50 of per-item min over 3 interleaved runs) while the raw run reads 'base 102.7 sel 125 ratio 1.217'; QUEUE reports only 'retrieval 1.005… | rnd/research/coordinator/arms/cryptosel/L0-round2.txt:10 | rnd/research/QUEUE.md:607 | PASS rests on a post-hoc metric (disclosed in CRYPTOSEL.md:23 as noise); moot because L1 failed | QUEUE l.607: 'retrieval 1.005× (min-of-3 interleaved; one non-interleaved pair 1.217, post-hoc metric)' |
| CRYPTOSEL | QUEUE: 'CRYPTOSEL L1 FAIL (target gate) → not adopted' ... 'No revision (stop rule)' vs CLOSED.md: no CRYPTOSEL row (grep -i 'cry\|selection' in CLOSED.md: none) | rnd/research/QUEUE.md:608 | rnd/research/coordinator/CLOSED.md:24 | decisive L1 FAIL under a frozen criterion with a no-revision stop rule = closed family (crypto-pack spec selection) | add a CLOSED.md 4B-side row: 'Retrieval selection: crypto-pack spec/constants (CRYPTOSEL); 10-05 \| 4B \| v0.1 EN 57 x 2 seeds, Opus judge.v1-med, changed item… |
| CRYPTOTRUTH | QUEUE: 'CRYPTOTRUTH NOT ADOPTED as frozen ... parked for after the claim (PR phase)' vs CLOSED.md and BACKLOG.md: no CRYPTOTRUTH/NOREC/EIPABS row (grep -i 'cry\|eip\|norec\|honest': none in CLOSED.md; BACKLOG.md no cryp… | rnd/research/QUEUE.md:702 | rnd/research/coordinator/CLOSED.md:24 | decisive NOT ADOPTED under the frozen criterion, explicitly parked (reopen = broadened phrase list as new freeze); it belongs in CLOSED.md or the BACKLOG s3 pa… | add a CLOSED.md row: 'Honesty/EIP card (CRYPTOTRUTH NOREC+EIPABS); 10-06 \| 4B \| v0.1 EN 57 x 2 seeds, Opus judge.v1-med, changed items \| Δ +0.0092, CI90 [-0… |
| CUT4-KVFIX | cut4-L1.md: 'KVFIX gate 3 (the real gate): device-only ... Still open' vs QUEUE latency budget: 'cut 4 warm (KVFIX ok) p50 68.7 s / p90 88.9 s per model-path answer' (a calibrated estimate stated as if KVFIX works); no … | rnd/research/coordinator/arms/cut4/cut4-L1.md:26 | rnd/research/QUEUE.md:661 | KVFIX device gate (3) never reported; 'KVFIX ok' is a scenario assumption in the A15 latency budget (QUEUE l.661 also gives '−27.7 s if KVFIX fails') | QUEUE l.661: '(KVFIX ok)' -> '(assuming KVFIX works; gate 3 unreported)'; or log the A15 cut 6 run's (QUEUE l.711) KV save/restore signals as KVFIX gate 3 |
| CUT7 | HANDOFF-2026-10-11.md:15 '4B claim build (cut 7; held-out rows = cut 6) \| 0.413 \| **0.26** \| 0.519 \| **0.40**' puts a two-seed V-para figure next to s42-only v0.2 figures; CUT7.md:33 says '0.512'. | rnd/research/coordinator/arms/cut7/CUT7.md:33 | rnd/research/coordinator/HANDOFF-2026-10-11.md:15 | v0.2 two-seed 0.512 / 0.388 | Label the v0.2 cells 's42 only' or replace them with 0.512 / 0.388 |
| CUT7 | HANDOFF-2026-10-10.md:9 'held-out numbers are cut 6's: v0.2 floor-adj 0.40 / V-para 0.26' vs the two-seed cut 6 figure 'floor-adj 0.388 (0.346–0.434)' (CLAIM-RESULTS-cut6.md:38) that CUT7.md:33 says stands for cut 7. | rnd/research/coordinator/CLAIM-RESULTS-cut6.md:38 | rnd/research/coordinator/HANDOFF-2026-10-10.md:9 | 0.388 two-seed (0.397 s42 only) | HANDOFF-2026-10-10.md:9 → 'v0.2 floor-adj 0.388 (two seeds; 0.397 s42)' |
| CV | QUEUE.md:604 says '**Computed-verdict line CLOSED for the bounty** (CV, CVS, CVH)', and QUEUE.md:618 closes CVO. CLOSED.md has no row for this family; a grep for CV/CVS/CVH/CVO/computed verdict in CLOSED.md finds nothin… | rnd/research/QUEUE.md:604 | rnd/research/coordinator/CLOSED.md:6 | The family is closed: all four arms were killed by stop rules | Add a CLOSED.md 4B row: 'Computed verdict \| CV, CVS, CVH, CVO; 10-04/05 \| CV gate +26.5 pp, 3 regressions (bar ≤ 2); CVS L1 Δ −0.005; CVH Δ −0.0034, +5.49 s;… |
| CV | CV.md:3 'accuracy NOT scored (coordinator, against the key)' and CV.md:30 'UNKNOWN: Accuracy vs the key (coordinator)' vs QUEUE.md:596 '**CV SHIP GATE FAIL → CV KILLED** ... **+26.5 pp** ... but **3 wrong-where-cut3-rig… | rnd/research/coordinator/arms/cv/CV.md:3 | rnd/research/QUEUE.md:596 | KILLED: L0 FAIL (score.txt), then ship gate FAIL (gate-score.txt) | Append a Verdict section to CV.md citing score.txt, gate-score.txt and QUEUE l.593-596 |
| CV | CV.md:19 'CV answered 118 of the 146 routed items ...; 28 routed items abstained' vs QUEUE.md:592 'CV answered 113, abstained 26' (score.txt:3 '(unknown: 23; CV answered 113, routed but abstained 26)'). | rnd/research/coordinator/arms/cv/CV.md:19 | rnd/research/QUEUE.md:592 | Both are true on different denominators: 118/28 of the 146 routed among all 155 (cv-timing.txt n=118), 113/26 among the 145 scored | QUEUE.md:592 → 'CV answered 118 of 146 routed (113 of the 145 scored), abstained 28 (26 scored)' |
| CV | QUEUE.md:590 '(155 labelled, 7 ambiguous → 148 scored)' and gold/README.md 'Ambiguous (excluded from scoring): 7 -> scored items: 148' vs score.txt:1 'scored 145 items'. | rnd/research/QUEUE.md:590 | rnd/research/coordinator/arms/cv/score.txt:1 | 145 were scored (gold/key.scorer.jsonl has 145 lines); 3 more items were dropped without notice in the arm files | Add a line to CV.md: 'scored 145 = 148 minus 3 items without a scoreable verdict (list ids)' |
| CVS | CLOSED.md has no row for the computed-verdict family (CV/CVS/CVH/CVO) or any 'verdict' entry, yet QUEUE says '**Computed-verdict line CLOSED for the bounty** (CV, CVS, CVH)' and later '**Computed-verdict family fully CL… | rnd/research/coordinator/CLOSED.md:1-60 (no matching row; grep for CVS/verdict/… | rnd/research/QUEUE.md:604 | The family is closed by frozen-criterion FAILs; the registry omits it because it predates 10-06 | Add a CLOSED.md row 'Computed verdict (CV, CVS, CVH, CVO); 10-04/05 \| 4B \| v0.1 EN 57 s44+s45 + fresh blind verdict gates #1-#4 \| CVS gate #3 +22.9 pp but L… |
| CVH | No CLOSED.md row covers CVH (computed-verdict family absent) although QUEUE says '**CVH v0.1 L1 FAIL → CVH KILLED**' and '**Computed-verdict line CLOSED for the bounty** (CV, CVS, CVH)' | rnd/research/coordinator/CLOSED.md:1-60 (no matching row) | rnd/research/QUEUE.md:603-604 | Closed by a frozen-criterion FAIL | Include CVH in a computed-verdict family row in CLOSED.md: 'CVH L1 Δ -0.0034 [-0.0153, +0.0061], lan-cmp-002 -1.083, +5.49 s routed' |
| CVO | Arm scorer output 'delta        : 0.0 percentage points (bar >= +10)' and 'cut 3 + CV   : 41/84 = 48.8 %  (... CV answered 0 ...)'; ledger 'Accuracy 41 → 46/84 (48.8% → 54.8%, **+6.0 pp < +8 bar**)' | rnd/research/coordinator/arms/cvo/gate4-score.txt:3-4 | rnd/research/QUEUE.md:618 | +6.0 pp (rescored with gate4-detail-cvoself.jsonl + hand check; reproducible 41 → 45 by string match + cv4-062 corrected = 46). The verdict is FAIL either way | Add arms/cvo/CVO-gate4.md (or a note in cvo-L1.md) stating 'gate #4 FAIL: 41 → 46/84, +6.0 pp < +8; scorer bug: non-computed-verdict reason codes read as absta… |
| CVO | Scorer 'CV abstained (routed, normal path answered): 56' vs ledger '51/120 routed, 10 overrides' | rnd/research/coordinator/arms/cvo/gate4-score.txt:7 | rnd/research/QUEUE.md:618 | Different routing definitions (the cv-score router flag over 84 scored items vs the cvo:routed reason code over 120 items). Neither file reconciles them | In the gate #4 result note, state 'cvo:routed 51/120 (facts call ran); cv-score routed flag 56/84 (CV router, pre-guard)' |
| CVO | No CLOSED.md row for CVO although QUEUE says '**Computed-verdict family fully CLOSED for the bounty** (CV, CVS, CVH, CVO)' | rnd/research/coordinator/CLOSED.md:1-60 (no matching row) | rnd/research/QUEUE.md:618 | Closed by a frozen gate #4 FAIL | Add a computed-verdict family row to CLOSED.md including 'CVO gate #4 +6.0 pp (< +8), 2 losses; L1 Δ 0.0000 vs same-day control' |
| DEEPCOVER | CLOSED.md has no DEEPCOVER row and still names it as the open reopen path: R8 "DEEPCOVER (key-point coverage, BACKLOG B2) is the only distinct variant" and R25 "DEEPCOVER (key-point coverage instead of persona; BACKLOG … | rnd/research/coordinator/CLOSED.md:23 (also :44) | rnd/research/coordinator/arms/deepcover/DEEPCOVER.md:3 | DEEPCOVER closed NO at the slice on 10-12 (QUEUE l.935, BACKLOG l.49/l.81); CLOSED.md was built 10-11, before the verdict | Add a CLOSED.md row: 'Prompt: key-point enumeration (deep) \| DEEPCOVER; 10-12 \| deep \| v0.2 random20 slice, 1 seed, Haiku→Opus N=4 \| Opus Δ -0.027 (-0.077.… |
| DEEPCOV-FB | QUEUE: "The peer configuration (DEEPWIKI) gains gold on 7 items but all 7 already had curated sources kept, so a fallback never reaches them" and REPLAY: "The peer gains (+7) sit on items where the curated kit already k… | rnd/research/QUEUE.md:914; rnd/research/coordinator/arms/deepcovfb/REPLAY-v01.m… | rnd/research/coordinator/arms/deepcovfb/REPLAY-v01.md:17, :27, :28 | 6 of the 7 peer gains are on items with curated kept sources; 1 (lan-exp-003) is an R2 item, which is the 1 the fallback captures. Verdict unchanged | REPLAY-v01.md:41 and QUEUE l.914 → '6 of the 7 peer gains sit on items where the curated kit already kept something; the 7th (lan-exp-003) is the R2 item the f… |
| DEEPCTX | BACKLOG parked table gives DEEPCTX "MDE at the time" "≈ 0.03" while CLOSED R23 gives MDE "0.08" for the same 20-id one-seed Haiku slice | rnd/research/coordinator/BACKLOG.md:88 | rnd/research/coordinator/CLOSED.md:42 | 20-id slice MDE ≈ 0.08 per CLOSED.md:7 convention; the arm file and criterion state no MDE | BACKLOG.md:88 MDE → '≈ 0.08 (20-id slice)' |
| DEEPFULL-F2 | CLOSED R25 label "**not detected at MDE 0.08 (20, 1 seed)**" vs the arm "**Verdict: NO at the slice (both arms).**" and "Rule: F1 NO, F2 NO" | rnd/research/coordinator/CLOSED.md:44 | rnd/research/coordinator/arms/deepfull/DEEPFULL.md:2 (and :18) | By its frozen rule (criterion l.12: 'If neither, NO') F2 is NO; under CLOSED.md's own convention (CI upper +0.048 > +0.03) it is under-powered. Both true; the … | CLOSED.md R25 label → 'NO by the criterion rule; not detected at MDE 0.08 (20, 1 seed; CI upper +0.048)' |
| DEEPFULL-F2 | BACKLOG parked table gives DEEPFULL F2 "MDE at the time" "≈ 0.06" while CLOSED R25 gives "0.08" for the same 20-id one-seed slice | rnd/research/coordinator/BACKLOG.md:87 | rnd/research/coordinator/CLOSED.md:44 | 20-id slice MDE ≈ 0.08 (CLOSED.md:7 convention); 0.06 is the 51-item one-seed V-para MDE | BACKLOG.md:87 MDE → '≈ 0.08 (20-id slice)' |
| DEEPHEDGE | BACKLOG 'detector p = 1.0 on 6 reasoning items' and HANDOFF-10-12 '(detector p = 1.0 on 6 reasoning items)' vs arm 'detector p = 1.000 on 10' (and QUEUE l.952 'detector p = 1.0 on 10'). | rnd/research/coordinator/arms/deephedge/DEEPHEDGE.md:5 | rnd/research/coordinator/BACKLOG.md:58 (also HANDOFF-2026-10-12.md:30) | Arm file: detector p = 1.000 on 10 of the 18 health-strict items; the '6 reasoning items' figure is not stated in the arm file (6 is the reasoning count of the… | BACKLOG.md:58 and HANDOFF-2026-10-12.md:30: replace 'detector p = 1.0 on 6 reasoning items' with 'detector p = 1.000 on 10 of the 18 health-strict items (6 of … |
| DEEPRERANK | QUEUE says gold "**enters the top-6 on 2 items** (vit-sci-002, vit-trv-003)". The arm table gives k = 6 as "**2**: vit-sci-002, trv-004" and k = 4 as "2: vit-trv-003, vit-sci-002". QUEUE swapped in the k = 4 pair. | rnd/research/QUEUE.md:908 | rnd/research/coordinator/arms/deeprerank/REPLAY-v01.md:27 | k = 6: vit-sci-002, trv-004 (confirmed by the ceiling note at REPLAY-v01.md:33) | QUEUE.md:908: replace '(vit-sci-002, vit-trv-003)' with '(vit-sci-002, trv-004)' |
| DEEPTHINK | QUEUE interim says '39/58 items hit the 1024 thinking budget (median 1,034 reasoning tokens)'. The result table says 'budget hits /51 ... **36**' for dt-T-vpara-s42, and aggregates/think-T-s42.json has "budgetHitItems_g… | rnd/research/QUEUE.md:820 | rnd/research/coordinator/arms/deepthink/DEEPTHINK.md:16 | 36/51 on s42 (31/51 on s43), per the aggregate JSON. | Append a QUEUE correction row: 'l.820 39/58 budget hits → 36/51 (s42), per arms/deepthink/aggregates/think-T-s42.json'. |
| DEEPTHINK | Ledgers quote the p50 cost of the 1024 thinking tier differently: CLAUDE.md says '×4.2 time (p50 145 s desktop)', HANDOFF-2026-10-10 says 'time p50 33 / 55 / 79 / 144 s desktop', and the result says 'desktop p50 total *… | <workspace>/CLAUDE.md:24 and rnd/research/coordinator/HANDOFF-2026-… | rnd/research/coordinator/arms/deepthink/DEEPTHINK.md:2 | 143 s (s42 142.9 s, s43 146.0 s; all-58 141.5 / 142.0 s) | Change 'p50 145 s desktop' in CLAUDE.md to 'p50 143 s desktop' (and '144 s' in HANDOFF-2026-10-10 l.9 to '143 s'). |
| DEEPTHINK-2 | The frozen premise says 'DEEPTHINK (budget 1024) ... 39/58 answers hit the 1024-work budget'. This arm's own control row says 'T (DEEPTHINK) \| 1024 \| 1034 (644 / 1034 / 1034) \| 36 (≥ 1024)', and DEEPTHINK.md:16 says… | rnd/research/coordinator/arms/deepthink2/DEEPTHINK2-criterion.md:3 | rnd/research/coordinator/arms/deepthink2/DEEPTHINK2.md:22 | 36/51 (arms/deepthink/aggregates/think-T-s42.json budgetHitItems_ge1024 36) | Add one line to DEEPTHINK2.md: 'criterion premise 39/58 → 36/51 (DEEPTHINK.md l.16); the premise does not affect the rule'. |
| DEEPTHINK-V02 | The QUEUE headline says 'DEEPTHINK-V02 → NO by rule (Δ +0.029 vs +0.03)', while its body and the result say 'paired Δ **+0.027 (+0.002…+0.054)**' (deduplicated 220 rows). +0.029 is the raw 266-row file, which includes 4… | rnd/research/QUEUE.md:828 | rnd/research/coordinator/arms/deepthinkv02/DEEPTHINKV02.md:2,18 (aggregates/L1-… | +0.027 is the decision number. CLAUDE.md:24 and QUEUE.md:851 also use +0.027. | Append a QUEUE correction row: 'l.828 headline Δ +0.029 → +0.027 (dedup 220 rows; +0.029 = raw 266-row file)'. |
| DEEPTHINK-V02 | CLOSED.md has no row for DEEPTHINK-V02, although it is a decisive NO on v0.2 one seed with \|Δ\| 0.027 ≥ the registry's own 'v0.2 one seed ~0.025' MDE. CLOSED.md lists it nowhere, not even among measurements or adopted … | rnd/research/coordinator/CLOSED.md:7,11 (no DEEPTHINK-V02 entry) | rnd/research/coordinator/arms/deepthinkv02/DEEPTHINKV02.md:2 | The arm needs a registry entry. Labelling it 'closed' would mislead because Opus later measured +0.045 (+0.022…+0.070); it belongs with the adopted DEEPTHINK l… | Add to CLOSED.md l.11: 'DEEPTHINK-V02 (L1 NO, Haiku +0.027 near-miss; Opus Addendum 1 +0.045 (+0.022…+0.070), v0.2 replication of the adopted lever)'. |
| DEEPTHINK-V02-ADDENDUM1 | HANDOFF-2026-10-10 says, in its deep + think 512 SEEDVAR bullet, 'On v0.2 the same tier is seed-stable (0.613/0.612, r 0.90)'. QUEUE attributes those values to the 1024 arm: 'TV (deep + think 1024) **0.613 / 0.612** (Δ … | rnd/research/coordinator/HANDOFF-2026-10-10.md:48 | rnd/research/QUEUE.md:873 | 0.613 / 0.612 are TV (thinking 1024, Addendum 1) per-seed raw values on v0.2. HANDOFF-2026-10-11.md:17 labels them correctly as '1024: 0.613/0.612'. | In HANDOFF-2026-10-10.md l.48, change 'On v0.2 the same tier is seed-stable (0.613/0.612, r 0.90)' to 'On v0.2 the 1024 thinking tier (TV) is seed-stable (0.61… |
| DT512 | CLAUDE.md Current state: 'thinking budget 512 = 1024 in quality (V-para floor-adj 0.436 vs 0.422, paired +0.011 (−0.010…+0.031))' puts the raw paired Δ next to floor-adj levels; the arm's floor-adj paired Δ is 'floor-ad… | <workspace>/CLAUDE.md (Current state block, DT512 sentence) | rnd/research/coordinator/arms/dt512/DT512.md:2 | +0.011 is raw; floor-adj Δ is +0.014 (-0.012…+0.039) | In CLAUDE.md write 'paired raw +0.011 (−0.010…+0.031), floor-adj +0.014 (−0.012…+0.039)' |
| DT256 | QUEUE: 'floor-adj **0.387 (0.349–0.426)**' and BAR-TABLE 'Q (256) \| 0.514 (0.483–0.544) \| 0.387 (0.349–0.426) \| 0.300 (0.256–0.343)' vs DT256.md '0.387 (0.348–0.425) \| 0.299 (0.256–0.343)' | rnd/research/QUEUE.md:846 and rnd/research/coordinator/BAR-TABLE.md:41 | rnd/research/coordinator/arms/dt256/DT256.md:29 | L2-Q-2seed.opus.json: above_min 0.3872 [0.3485, 0.4255], above_decl 0.2995. Every value sits on a rounding boundary, so both versions are roundings of the same… | Use one rounding everywhere, e.g. change DT256.md:29 to '0.387 (0.349–0.426) \| 0.300 (0.256–0.343)' to match QUEUE/BAR-TABLE |
| DT256 | CLAUDE.md Current state: 'DT256 … CHEAPER-LOSS: budget 256 floor-adj 0.387, −0.028 (−0.056…−0.003) vs 1024' puts a raw Δ next to a floor-adj level; the arm's floor-adj Δ is 'floor-adj -0.035 (-0.070…-0.004)' | <workspace>/CLAUDE.md (Current state block, DT256 sentence) | rnd/research/coordinator/arms/dt256/DT256.md:2 | −0.028 is raw; floor-adj Δ −0.035 (−0.070…−0.004) | CLAUDE.md: 'raw −0.028 (−0.056…−0.003), floor-adj −0.035 (−0.070…−0.004) vs 1024' |
| DT512-V02 | CLAUDE.md Current state: 'DT512-V02 … 512 floor-adj 0.508 (0.467–0.550), −0.005 vs 1024, +0.089 vs the 4B claim run' puts raw Δs next to a floor-adj level; the arm's floor-adj Δs are '-0.006 (-0.025…+0.011)' and '+0.111… | <workspace>/CLAUDE.md (Current state block, DT512-V02 sentence) | rnd/research/coordinator/arms/dt512v02/DT512V02.md:17 | −0.005 and +0.089 are raw; floor-adj −0.006 / +0.111 | CLAUDE.md: '−0.005 raw (floor-adj −0.006) vs 1024, +0.089 raw (floor-adj +0.111) vs the 4B claim run' |
| FACTS-BLIND | FACTS-BLIND.md: 'recall after 2 scorer artefacts (đồng ≠ "dong", złoty ≠ "zloty": both answers correct) \| 27/40 = 67.5%' vs FACTS-r4-criterion.md Addendum 1: 'set 2 **26/40**, not 27/40 ... an expect-wording issue, not… | arms/facts/FACTS-BLIND.md:7 | arms/facts/FACTS-r4-criterion.md:35-37 | 26/40 = 65.0% under scorer v2 (one fold artefact only) | FACTS-BLIND.md:7 append 'corrected: 26/40 = 65.0% under scorer v2, see FACTS-r4-criterion.md Addendum 1' |
| FACTS-r6 | QUEUE: '8/12 misses are lowercase one-word non-capital names blocked on purpose by the r3 rule (all 8 entities are in the table)' vs FACTS-r6-SET4.md: '7 of the 8 entities are in the table (Zambezi is absent; corrected … | QUEUE.md:758 | arms/facts/FACTS-r6-SET4.md:17 | 7 of 8 (Zambezi absent, per LCRELAX-PROBE.md:17 and QUEUE:760) | QUEUE:758 change '(all 8 entities are in the table)' to '(7 of the 8 entities are in the table; Zambezi absent, see l.760)' |
| FACTS-r6 | Criterion: 'if r6 FAILs on set 4, the line closes at r5 (safe, recall 60–75 %) and cut-7 input = r5, pending r4to' vs QUEUE: '(1) cut 7 = cut 6 + FACTS r6' | arms/facts/FACTS-r6-criterion.md:1-2 | QUEUE.md:770 | r4to overrode the criterion's fallback; cut 7 ships r6 (disclosed as HEAD DECISION at FACTS-r6-SET4.md:25-26) | FACTS-r6-SET4.md: add 'r4to 10-07 09:23 (QUEUE l.770): cut 7 = cut 6 + r6, overriding the criterion's r5 fallback' |
| FOLLOWQG | FOLLOWQ-G has a decisive verdict 'NOT ADOPTED. G3 FAIL (arm wins 9 of 20 non-tie decisions = 45%, bar >= 60%)' but CLOSED.md R4 lists only 'FOLLOWQ (Q1, Q2); 10-06 ... retrieval-only diagnostic' and its reopen condition… | arms/followq/FOLLOWQG.md:3 | CLOSED.md:19 | FOLLOWQ-G closed the reopen condition of R4: gated variant passes identity (0/171) but fails quality (45 %) | CLOSED.md R4: add 'FOLLOWQ-G (gated Q1): 0/171 changes, Opus A/B 9/11/6 = 45 % vs bar 60 %, NOT ADOPTED; arms/followq/FOLLOWQG.md' |
| FTDATA-REJ | Measures table 'Kept (≥ 100 words left AND sentence 1 survived) \| **632/982** \| ≥ 600 → MET' (and QUEUE interim 'kept **632/982** (≥ 100 w + s1 survives; bar ≥ 600 met)') vs verdict '538/982 with the frozen filter's 1… | arms/ftdata/FTDATA-REJ.md:24 | arms/ftdata/FTDATA-REJ.md:53 | kept bar FAIL (538 < 600) under the coordinator's strict reading | FTDATA-REJ.md:24 change '≥ 600 → MET' to '≥ 600 → FAIL under the strict reading (538, see verdict)' |
| GROUND-ST | Criterion: 'step 0 decides whether the keep rule enters the STACK', 'Both FAIL → FAIL at step 0; the D0 loss classes become the next hypothesis', and 'the keep rule that passed step 0 is carried into the STACK criterion… | arms/groundst/GROUND-ST-criterion.md:24, :31, :34 | rnd/research/QUEUE.md:1026 | No variant passed step 0, so by the frozen criterion none enters STACK. Carrying X3 forward is a post-hoc coordinator decision (BACKLOG l.77 states it openly).… | CLOSED R47 label: 'FAIL at step 0 (all 3 variants); X3 carried into STACK by coordinator decision outside the GROUND-ST criterion (criterion l.31/34 carries on… |
| GROUND-ST addendum 1 (X3 perpack) | Addendum rule: 'Variant entering stage 1 = the one with the highest fact-chunk kept among those passing G1–G3 … No further variants without a new addendum'. Base criterion: 'the keep rule that passed step 0 is carried i… | arms/groundst/GROUND-ST-criterion-addendum-1.md:13; arms/groundst/GROUND-ST-cri… | rnd/research/QUEUE.md:1026 | X3 failed G1 (54 < 55), so under the frozen rules it does not advance. The STACK carry-over is a post-hoc coordinator decision, disclosed in BACKLOG.md:77. | GATE.md addendum verdict line: add 'X3 carried into STACK by coordinator decision (QUEUE l.1026), not by the GROUND-ST rule'. |
| HFUFIX | QUEUE: "**HFU-FIX NOT ADOPTED as frozen**" and "**HFU-FIX2 NOT ADOPTED → HFU-FIX closed** ... Per the frozen rule, no further rescue". CLOSED.md has no row for the HFU-FIX health follow-up routing family. The only follo… | rnd/research/QUEUE.md:688 | rnd/research/coordinator/CLOSED.md:19 | The family is closed by its frozen stop rule (HFUFIX2-criterion.md:8 'If G3' fails again → closed, no further rescue') | Add a CLOSED.md row: 'Health follow-up routing (HFU-FIX, HFU-FIX2; 10-06) \| G3 58.1% / G3' 84.2% vs bar 90%; control gap +43.4 pts; 0 rule-introduced false fi… |
| HFUFIX2 | QUEUE: "**HFU-FIX2 NOT ADOPTED → HFU-FIX closed** ... G3' 64/76 = 84.2% (bar 90%), control 40.8% (+43.4 pts, ≥30 ok)". CLOSED.md has no row covering HFU-FIX2. | rnd/research/QUEUE.md:690 | rnd/research/coordinator/CLOSED.md:19 | This is a decisive closure by the frozen stop rule, so it needs a CLOSED.md row | Cover HFU-FIX2 in the same new CLOSED.md row as HFU-FIX (see HFUFIX), citing G3' 84.2% vs bar 90% |
| HUMANSFT | CLOSED R12: "unsupported-claim rate teacher 16/20 -> +sentence rejection 11/20 -> human CLAPnq 6/20" vs REVIEW-20h: "examples with ≥ 1 unsupported-or-contradicted claim = **6/20** (ids 3, 9, 16, 18, 19, 20)". Ids 18-20 … | rnd/research/coordinator/CLOSED.md:27 | rnd/research/coordinator/arms/humansft/REVIEW-20h.md:31 | The 6/20 is the human CLAPnq+HAGRID pooled rate. CLAPnq-only is 3/17. The arm's own HUMANSFT.md:53 makes the same CLAPnq attribution. | CLOSED.md R12: replace 'human CLAPnq 6/20' with 'human CLAPnq+HAGRID 6/20 (CLAPnq 3/17, HAGRID 3/3)' |
| HUMANSFT | CLAUDE.md: "Opus teacher 16/20 → +sentence rejection 11/20 → human CLAPnq 6/20; no LoRA" vs REVIEW-20h.md:31 flagged ids 3, 9, 16 (CLAPnq) + 18, 19, 20 (HAGRID) | <workspace>/CLAUDE.md:24 | rnd/research/coordinator/arms/humansft/REVIEW-20h.md:31 | 6/20 is pooled over 17 CLAPnq + 3 HAGRID; CLAPnq-only 3/17 | CLAUDE.md l.24: 'human CLAPnq 6/20' -> 'human CLAPnq+HAGRID 6/20 (CLAPnq 3/17)' |
| K2HALF | Project rule 'Freeze a pass/fail criterion (sha256) before any run that decides something.' vs K2HALF-gate.md 'the gate as frozen says FAIL' — no K2HALF criterion .md/.sha256 exists; the ≥ 80 % bar is only in the QUEUE … | <workspace>/CLAUDE.md (Rules: 'Freeze a pass/fail criterion (sha256… | <workspace>/rnd/research/coordinator/arms/k2half/K2HALF-gate.md:21 | bar pre-registered in QUEUE.md:961 (14:22) before the 14:30 result, but not sha-frozen | K2HALF-gate.md:21 'as frozen' → 'as pre-registered in QUEUE l.961 (no sha-frozen criterion)' |
| KVQ8 | KVQ8-L1.md: '\| overall \| **ADOPT as a device-day candidate** \|' (decisive verdict) vs CLOSED.md exclusion line 'Not in the table because they are measurements or adopted levers: SEEDVAR, JUDGEVAR, LENGTHSHARE, LOSSMA… | <workspace>/rnd/research/coordinator/arms/kvq8/KVQ8-L1.md:97 | <workspace>/rnd/research/coordinator/CLOSED.md:11 | KVQ8 is a passed non-inferiority lever pending a device day | CLOSED.md:11: add 'KVQ8 (q8_0 KV, PASS non-inferiority −0.0077 CI90 [−0.0232, +0.0062]; device-day candidate)' to the adopted-levers exclusion list |
| LOSSMAP | LOSSMAP-criterion.sha256 holds '1059f5dd15c80dfb5bad82376104d55edf17bcd3558580bf19ef6b5afa615852', and LOSSMAP.md cites 'criterion `LOSSMAP-criterion.md` sha 1059f5dd…'. shasum -a 256 of the current LOSSMAP-criterion.md… | rnd/research/coordinator/arms/lossmap/LOSSMAP-criterion.sha256:1 | rnd/research/coordinator/arms/lossmap/LOSSMAP.md:1 | The criterion bytes changed after the hash was taken, in the same second or by a later edit that preserved the mtime. The frozen text is unrecoverable without … | Record in LOSSMAP.md and RULE-CHANGES: 'criterion edited after freeze (current sha 0c189064…); measurement only, no verdict depends on it'. Re-freeze the curre… |
| LOSSMAP | Criterion: 'a `primary` with confidence < 0.6 is reported as "undecided" and excluded from the primary table but kept in the axes' vs result: 'Primary with confidence < 0.6: 12/51 and 18/110 on H (kept in the tables; mo… | rnd/research/coordinator/arms/lossmap/LOSSMAP-criterion.md:27 | rnd/research/coordinator/arms/lossmap/LOSSMAP.md:10 | The primary table includes the low-confidence primaries, against the frozen reading rule. Shares such as absent 0.59/0.55 and wrong 0.40/0.21 would shift once … | Add an 'undecided' row to the primary table (12 V-para / 18 v0.2 on H, 9 / 18 on K), or label the deviation explicitly in LOSSMAP.md. |
| LOSSMAP | LOSSMAP: 'hedged = 18 % (11, v0.2 only: danger 4, reasoning 4, health 2; 9 of the 11 ran on the deep tier)' vs CLOSED R40: 'hedged 11 → 11: the items are health-strict canned fallbacks (engine), instruction never applie… | rnd/research/coordinator/arms/lossmap/LOSSMAP.md:5 | rnd/research/coordinator/CLOSED.md:64 | The hedged items never went through the deep prompt; they took the health-strict fallback path. LOSSMAP.md:48's H1 DEEPHEDGE proposal rested on this misread, a… | Amend LOSSMAP.md:5 to '10 of the 11 on the health-strict path, 1 instant (tier=deep on 9; per-path addendum QUEUE l.953)'. |
| LOSSMAP | BACKLOG: '(LOSSMAP: *wrong* = 0.40 of H's V-para loss, 26/51 items; ...)' vs LOSSMAP primary table: '\| wrong \| 16 · **0.40** \|' and axis table '\| wrong_fact \| 26 · 0.59 \|'. | rnd/research/coordinator/BACKLOG.md:48 | rnd/research/coordinator/arms/lossmap/LOSSMAP.md:16 | The wrong primary bucket has 16 items and a 0.40 loss share. The wrong_fact axis has 26 items and a 0.59 share. BACKLOG pairs the share of one with the count o… | BACKLOG.md:48 → 'wrong = 0.40 of H's V-para loss (16/51 primary; wrong_fact axis 26/51, 0.59)'. |
| ORACLE-ST | BACKLOG.md:31 'proposed (0 paid; ≈ 360 Haiku, Opus only if the Δ is a lever)' and QUEUE.md:1027 '≈ 360 Haiku, 0 paid' vs the frozen criterion 'Haiku 5.5-low N = 4 … then Opus judge.v1 N = 4 … (this session's Opus budget… | rnd/research/coordinator/BACKLOG.md:31 | rnd/research/coordinator/arms/oracle-st/ORACLE-ST-criterion.md:12,36 | The frozen criterion governs: both judges run regardless (≤ 720 Haiku + ≤ 720 Opus); QUEUE.md:1062 also says '720 Haiku + 720 Opus' | BACKLOG.md:31 status → 'running (criterion 4c4651b1…, 10-13 20:4x; ≤ 720 Haiku + ≤ 720 Opus; Opus decides)' |
| ORACLE-ST | BACKLOG.md:31 'ST2 put +40 fact chunks in context for +0.017' (QUEUE.md:1027 'ST2 added +40 fact chunks to the context for +0.017') vs criterion 'ST2 put ≈ +18 fact chunks into kept for +0.017' | rnd/research/coordinator/BACKLOG.md:31 | rnd/research/coordinator/arms/oracle-st/ORACLE-ST-criterion.md:16 | HANDOFF-2026-10-13.md:14: 'fact chunk in raw top-8 67 → 108, chunk kept 43 → 61' → +41 reached raw, +18 kept (the reader's context); '+40 in context' conflates… | BACKLOG.md:31 → 'ST2 put +41 fact chunks into raw top-8 (+18 kept) for +0.017' |
| PACKCOND-P1 | HANDOFF-2026-10-12.md:18 'H scores **0.55 floor-adj on v0.2 (n 32) vs 0.39 without** (K 0.41 vs 0.29)' vs Addendum 1 'H \| in-pack (H F0) \| 32 \| … \| **0.609 (0.532–0.679)**' and 'not in-pack \| 78 \| … \| 0.467 (0.41… | rnd/research/coordinator/HANDOFF-2026-10-12.md:18 | rnd/research/coordinator/arms/packcond/PACKCOND-P1.md:40,45-46 | Headline floor-adjusted (above_min): H 0.609 in-pack vs 0.467 outside; K 0.482 vs 0.378 (BACKLOG.md:17 and HANDOFF-2026-10-13.md:23 already carry the corrected… | HANDOFF-2026-10-12.md:18 → 'H above_min 0.61 (0.53–0.68) on v0.2 in-pack (n 32) vs 0.47 without (K 0.48 vs 0.38); P1's 0.55/0.39 were above_decl' |
| P4 packGround (PACKCOND P4 step 0) | PACKCOND-PLAN-2026-10-12.md:25 'First pack-conditional arm (frozen criterion)' vs the arm dir having no P4 criterion file or .sha256; the gate bars appear only in the post-run P4-GATE.md:3 'the gate needs ≥ 16 … the gat… | rnd/research/coordinator/PACKCOND-PLAN-2026-10-12.md:25 | rnd/research/coordinator/arms/packcond/P4-GATE.md:3 | The P4 gate was declared in-session without a frozen sha; the FAIL is unaffected (14 < 16 and 6 > 4), but the protocol step was skipped | P4-GATE.md:3 → append 'Gate bars set by the coordinator before the replay but not sha-frozen (no criterion file).' |
| SECTIONHIT | QUEUE.md:976 'Corrected stage ladder for the deep tier on in-pack items: fact article in raw 17/32 → kept 12/32 → fact passage shown 7/32' vs SECTIONHIT.md:19 'all \| 32 \| 19 \| 12 \| 12 \| 7' (art raw 19, art kept 12) | rnd/research/QUEUE.md:976 | rnd/research/coordinator/arms/packcond/SECTIONHIT.md:19 | Ladder mixes definitions: 17 (raw) and 11 (kept) under the P1/p4-diag F0-article definition; 19 (raw) and 12 (kept) under SECTIONHIT's any-hit-chunk definition… | QUEUE ladder → 'fact article in raw 19/32 → kept 12/32 → fact passage shown 7/32 → used right 4/7 (SECTIONHIT definition; 17 → 11 under P1's)' |
| HEALTHQ | BACKLOG.md:21 '4/15 in-pack misses are health-strict with empty raw' vs P4B-GATE.md:15 '4/15 are danger items on the health-strict path with an empty raw list on 3' | rnd/research/coordinator/BACKLOG.md:21 | rnd/research/coordinator/arms/packcond/P4B-GATE.md:15 | 4/15 health-strict, empty raw on 3 of them (QUEUE.md:974: '4 danger items on the health-strict path (raw empty on 3') | BACKLOG.md:21 → '4/15 in-pack misses are health-strict (raw empty on 3)' |
| PACKROUTE-2 | The arm says 'A router would need roughly ≥ 0.85 accuracy plus a peers fallback on `none` to beat P'. The ledgers say 'break-even ≈ 0.68, 90 % of S ≈ 0.9' (CLOSED R48), 'break-even vs peers needs ≈ 0.68 accuracy (0.256/… | arms/packroute2/ACCURACY.md:63 | CLOSED.md:72 (also ../QUEUE.md:1031, BACKLOG.md:30, HANDOFF-2026-10-13-PM.md:12) | 0.68 is a coordinator derivation in QUEUE:1031 for the top-1-filter break-even; it was never written in the arm file. The arm's own reading names ≥ 0.85 (with … | Add one line under ACCURACY.md §0b: 'Break-even vs P for a hard top-1 filter ≈ 0.68 (0.256/0.378, QUEUE l.1031); 90 % of S ≈ 0.9; ≥ 0.85 is the G1 bar' and cit… |
| SELFTEST-DEEP | CLAUDE.md says 'deep tier +0.063 over the 4B, SE packs add nothing to it'. The arm gives 'Deep with pack vs 4B with the same pack: +0.054 (+0.034…+0.073) pooled (SE +0.063 …, topic +0.043 …)' and topic Δ '−0.000'. | <workspace>/CLAUDE.md:21 | arms/packs/SELFTEST-DEEP.md:2 | Pooled deep vs 4B is +0.054; +0.063 is the SE half only (the 10/18 partial in QUEUE:1032). No pack, SE or topic, adds anything to the deep tier. | CLAUDE.md:21: 'deep tier +0.054 over the 4B with the same pack (SE +0.063); no pack adds anything to it (pooled −0.002)'. Drop 'open: SELFTEST-DEEP topic half'. |
| T-K2 | T-K2 checks byte-identity only on the shipped packs: '41 hits, JSON.stringify(hits) identical'. It then proposes the 6 files as one maintainer commit. TK2-REPLAY later finds 'the T-K2 sources patch is NOT label-only … k… | arms/packs/T-K2.md:20, :23-24 | ../QUEUE.md:1079 (arms/packs/tk2-replay/TK2-REPLAY.md:3) | Byte-identical holds for the existing kit packs only. On new-source packs the patch changes retrieval, so SELFTEST/CROWDQ/STACK scores are the pre-T-K2 (cut 7)… | Add to T-K2.md: 'Identity scope = shipped crypto/wikivoyage packs only; on new-source packs kept lists change on 52/180 (TK2-REPLAY); not label-only.' |
| PROMPTDIET | CLOSED R7 reopen condition: 'a new device-day latency experiment (patch bb287dde kept); see QUEUE l.614, l.660' vs QUEUE l.660: 'the faithful prompt diet itself raises confident-wrong; PROMPTDIET dropped from device-day… | rnd/research/coordinator/CLOSED.md:22 | rnd/research/QUEUE.md:660 | QUEUE l.660 is the later ruling (after SPEEDPACK Run A: diet alone Δ −0.0078, cw 9/8): PROMPTDIET is no longer a device-day candidate; also with KVFIX the fixe… | In CLOSED.md R7 replace the reopen cell with: 'a new prompt-wording experiment that does not raise confident-wrong (diet alone cw 5→9/8, QUEUE l.660); dropped … |
| PROMPTDIET | PROMPTDIET.md TL;DR: 'fixed prompt text on the 4B normal answer path cut from 272.9 to 122.7 mean tokens (-150.2, bar -150; thin margin of 0.2)' vs Revision 1: '272.86 \| 147.14 \| **-125.72** (bar -150: FAIL by 24.3)' | rnd/research/coordinator/arms/promptdiet/PROMPTDIET.md:3 | rnd/research/coordinator/arms/promptdiet/PROMPTDIET.md:39 | Final L0 = −125.72, FAIL; the −150.2 build was rejected by the reviewer (4 WEAKENED). The TL;DR alone reads as an L0 pass. | Prepend to PROMPTDIET.md:3: 'FINAL: L0 FAIL — revision 1 (faithful) −125.72 vs bar −150; the −150.2 first build below was rejected (4 rules weakened). PROMPTDI… |
| QUANTCEIL | QUANTCEIL.md:3 'a gain ≥ +0.03 raw is excluded on both sets' and CLOSED.md:61 'a gain ≥ +0.03 excluded' vs the V-para two-seed CI 'Δ **+0.004 (−0.024…+0.033)**' (upper bound above +0.03) | rnd/research/coordinator/arms/quantceil/QUANTCEIL.md:3 | rnd/research/coordinator/CLOSED.md:61 | +0.03 is excluded on v0.2 (CI upper +0.028) but not on V-para (CI upper +0.033; paired_gap-QvsH-2seed.json 0.0325) | Replace 'excluded on both sets' / 'a gain ≥ +0.03 excluded' with 'a gain ≥ +0.03 excluded on v0.2 (CI upper +0.028); V-para CI upper +0.033'. |
| QUANTCEIL | QUANTCEIL.md:5 'v0.2 *wrong* items +0.087 (+0.035…+0.150, n 23)' (called the LOSSMAP bucket of H), BAR-TABLE.md:134 'mechanism confirmed on the *wrong* bucket of v0.2, +0.087', HANDOFF-2026-10-12.md:28 '*wrong* bucket +… | rnd/research/coordinator/arms/quantceil/QUANTCEIL.md:5 | rnd/research/coordinator/arms/quantceil/aggregates/bucket-delta-v02-s42.opus.tx… | +0.087 (n 23) is the wrong_fact axis; the LOSSMAP primary wrong bucket is +0.113 (n 17); QUEUE.md:945 states both correctly | In QUANTCEIL.md:5, BAR-TABLE.md:134 and HANDOFF-2026-10-12.md:28 write 'wrong_fact axis +0.087 (n 23; primary wrong bucket +0.113, n 17)'. |
| SC-V3-S5SECOND (SC v3 trigger S5″ on sc… | Arm has a decisive verdict 'S5″ FAIL' (the third and last SC round: the criterion says 'This is the last round'), and QUEUE records 'Water card + SC trigger changes PARKED for the bounty'. CLOSED.md has no row for the S… | rnd/research/coordinator/arms/sc-fresh4-S5second-result.txt:6 | rnd/research/coordinator/CLOSED.md:6 | The family is closed or parked by a deterministic gate FAIL with 0 judge calls (S5, S5′ and S5″ all FAIL). It belongs in the registry. | Append a CLOSED.md row: 'SC trigger family (water card + snakebite fast path, v1–v3) \| 10-03/04 \| 4B routing \| sc-fresh3/sc-fresh4 100 items each, 0 judge c… |
| SEEDGEN | BACKLOG still quotes the pre-fix figure: 'ST2's 56/102 was a keying artefact (... 0/43 same answer when promptTokens differ, 56/59 when equal)'. The arm addendum says 'the reported "56/59 same-prompt identical" becomes … | rnd/research/coordinator/arms/seedgen/SEEDGEN.md:54 | rnd/research/coordinator/BACKLOG.md:25 | 32/34 (LLM, same prompt) + 23/23 (no-LLM); kept-unchanged 55/60 under multiset pairing; the conclusion is unchanged. | BACKLOG.md:25 → '... 0/43 same answer when promptTokens differ, 32/34 when equal (+ 23/23 no-LLM; addendum 10-13 22:5x after the F8 fix)' |
| SEEDVAR | The EXPOSURES V-para status row counts generations as 'DT512 3 (incl. SEEDVAR s44)', but its judge tally reads 'Opus 16 full (cut3 2, anchors 4, DEEPVPARA-D 2, DEEPTHINK-T 2, GEMMATHINK-G 2, DT512-H 2, DT256-Q 2)'. That… | rnd/research/coordinator/arms/seedvar/SEEDVAR.md:8 | rnd/research/coordinator/EXPOSURES.md:14 | DT512-H has 3 Opus full passes on V-para (s42, s43, s44 via SEEDVAR), so the Opus full total is at least 17. | EXPOSURES.md:14 → 'Opus 17 full (..., DT512-H 3 (incl. SEEDVAR s44), ...)' |
| SFT4B | BACKLOG says 'stage 1 training on the mini running (10-13 21:4x, opus/medium agent)' vs STAGE1.md 'Status: WAITING FOR v3 DATA (coordinator 21:1x: no 600-iteration training on v2 ...)' and 'Step 6 has not started.' | <workspace>/rnd/research/coordinator/BACKLOG.md:26 | <workspace>/rnd/research/coordinator/arms/sft4b/STAGE1.md:3-4 | Training has not started; the environment is done and the arm waits for v3 data. | BACKLOG l.26: replace 'stage 1 training on the mini running' with 'stage 1 environment + parity tooling done (STAGE1.md); training on hold for v3 data (addendu… |
| SFT4B | QUEUE l.1069 'Stage 1 launched on the mini per addendum 1 ... Decision: v2' vs QUEUE l.1072 / STAGE1.md 'Superseded at 21:1x by v3 (distractor-rich, addendum 2); v2 was used only for the smoke.' | <workspace>/rnd/research/QUEUE.md:1069 | <workspace>/rnd/research/coordinator/arms/sft4b/STAGE1.md:36 | v2 was used for the smoke only; v3 is the training set. | Append to the SFT4B v2 row (or a new QUEUE row): 'superseded 21:10 by addendum 2: v2 = smoke only; training waits for v3'. |
| SFT4B | SFT4B criterion: 'this arm uses short extraction targets filtered per example by jev quote_supports ≥ 0.9 (the row's reopen condition)' vs CLOSED R12 reopen cell 'a bar pre-registered relative to the human baseline (<=6… | <workspace>/rnd/research/coordinator/arms/sft4b/SFT4B-criterion.md:… | <workspace>/rnd/research/coordinator/CLOSED.md:27 | A per-example jev filter is not literally R12's reopen condition. Addendum 2 later adds the '≤ 6/20 unsupported' 20-example review, which does match R12's huma… | Add a note to R12 (or the SFT4B criterion) that the reopen is satisfied by addendum 2's strict 20-example review ≤ 6/20 (R12 human baseline), not by the jev fi… |
| SPECDEC | QUEUE: 'SPECDEC NO-GO ... Speculative decoding closed for the 4B on this stack.' vs CLOSED.md having no SPECDEC row. The only speculative row is R35 'Speculative decoding: MTP \| WEB-SWEEP 10-09 ... external numbers, no… | <workspace>/rnd/research/QUEUE.md:672 | <workspace>/rnd/research/coordinator/CLOSED.md:54 | Decisive NO-GO, closed on 10-06; it needs its own CLOSED row. | Add a CLOSED row: 'Speculative decoding, separate draft (Qwen3-0.6B Q8_0 / Qwen2.5-1.5B) \| SPECDEC 10-06 \| 4B (device) \| 50 v0.1 EN s44 model-path prompts, … |
| SYNTHDEEP | SYNTHDEEP.md table, curated row, 'kept lists changed on vs off' = '2' vs REPLAY-v01.md 'Kept lists change on 4/60 items (lan-cmp-001/002/005, vit-sci-002)' | arms/synthdeep/SYNTHDEEP.md:7 | arms/synthdeep/REPLAY-v01.md:18 | 4 (aggregates/replay-v01.json items_kept_changed_on_vs_off lists 4 ids) | SYNTHDEEP.md:7: change the last cell of the curated row from '2' to '4' |
| THINK4B | EXPOSURES V-para summary: 'Opus 16 full (cut3 2, anchors 4, DEEPVPARA-D 2, DEEPTHINK-T 2, GEMMATHINK-G 2, DT512-H 2, DT256-Q 2) ...; Haiku 10 + 6 slices of 20 ids (GEMMATHINK, DEEPFULL ×2, DT512, DT256, DEEPNORAG… | EXPOSURES.md:14 | arms/think4b/THINK4B.md:36 | THINK4B ran 1 Opus full pass (51), 2 Opus 20-id slices, 2 Haiku slices and 1 Haiku full pass on V-para (per-run row EXPOSURES.md:106 is correct) | EXPOSURES.md:14: add 'THINK4B-Z 1' to the Opus full list (or a 1-seed note), and 'THINK4B ×2 + full 51' to the Haiku list |
| THINK4B-V02 | BAR-TABLE call tally 'THINK4B-V02 300 H l.880–881' vs arm 'Haiku 20 + 110 ids (260 calls); Opus 0' | BAR-TABLE.md:113 | arms/think4b/THINK4B.md:45 | 260 Haiku calls in total (QUEUE.md:881 '260 Haiku, 0 Opus'). BAR-TABLE double-counts the 40 slice calls from QUEUE.md:880. | BAR-TABLE.md:113: 'THINK4B-V02 300 H l.880–881' → 'THINK4B-V02 260 H l.881' |
| THINK4B-V02 | EXPOSURES bench-v02 summary lists generation '12 full (E3 2, ship 2, cut3 2, cut6 2, DEEPVPARA D/C 4) + ship-sanity (partial) + DEEPTHINK-V02 ...' and 'Haiku 5.5-low 4 + DEEPTHINK-V02 triage', with no THINK4B-V02, vs th… | EXPOSURES.md:13 | arms/think4b/THINK4B.md:45 | THINK4B-V02 generated 1 slice + 1 full and ran 260 Haiku calls on bench-v02 (per-run row EXPOSURES.md:112 is correct) | EXPOSURES.md:13: add 'THINK4B-V02 (ZV s42 full + slice)' to generations and 'THINK4B-V02 260' to the Haiku list |
| TRAVELSEL | Arm has a decisive verdict "**L0 FAIL after the one allowed revision**" and QUEUE says "**TRAVELSEL L0 FAIL (after the one revision) → killed**", but CLOSED.md has no row naming TRAVELSEL (grep -i travelsel / selection … | arms/travelsel/TRAVELSEL.md:3 | CLOSED.md (no row; QUEUE.md:616 states the kill) | The arm is closed at a step-0 deterministic gate with 0 judge calls, which fits CLOSED.md's own rule for 'closed'. The registry missed it, probably because it … | Add a CLOSED.md row: 'Retrieval selection: Wikivoyage practical section \| TRAVELSEL; 10-05 \| 4B \| L0 stub replay, 71 items, 3 targets, 0 judge \| gold gain … |
| VITALPACK-ADD | No CLOSED.md row for VITALPACK-ADD although it is NO at the slice and not detected at L2 ("H6 stays not detected at L2 on v0.2 … stage 4 … is not run"); CLOSED R34 still says "L1 queued Mon 10-12" | <workspace>/rnd/research/coordinator/arms/vitalpack/VITALADD.md:19 | <workspace>/rnd/research/coordinator/CLOSED.md:53 | arm stopped: NO slice / not detected at L2 v0.2 full; needs its own CLOSED row | Add CLOSED row: 'Additive vital intro (VITALPACK-ADD, q=1) on deep tier \| 10-11/13 \| Opus slice −0.011 (−0.039…+0.018); v0.2 full Opus +0.0012 (−0.0120…+0.01… |
| VITALPACK-ADD | BACKLOG still lists the Opus test as parked: "VITALADD-Opus (H6, parked powered test) \| parked \| resolves \"not detected at 0.025\" … Opus N=4 on the existing A full-110 traces vs L2-H-1seed (220 Opus, 0 generation) w… | <workspace>/rnd/research/coordinator/BACKLOG.md:57 | <workspace>/rnd/research/coordinator/arms/vitalpack/VITALADD.md:19 | the powered test ran 2026-10-13 20:56 (QUEUE:1065) | BACKLOG l.57 status → 'done 10-13: Opus +0.0012 (−0.0120…+0.0147) vs L2-H-1seed, not detected; closed' |
| VITALPACK-ADD | BACKLOG parked table row "VITALPACK-ADD (v0.2 full, Haiku vs TV) \| +0.011 (−0.007…+0.029), 110, 1 seed \| ≈ 0.025 \| Opus N=4 on the existing A full traces vs L2-H-1seed (220 Opus, 0 generation)" vs addendum result "Δ … | <workspace>/rnd/research/coordinator/BACKLOG.md:90 | <workspace>/rnd/research/coordinator/arms/vitalpack/VITALADD.md:18 | Opus L2 number +0.0012 supersedes the Haiku-vs-TV cell; cheapest powered test spent | BACKLOG l.90 → result '+0.0012 (−0.0120…+0.0147) Opus vs L2-H-1seed (110, 1 seed)', cheapest test 'stage 4 V-para s43 generation + 204 Opus' |
| WIKIFULL-REOPEN | CLOSED R45 outcome: "closed: MARGINAL, no WIKI-ALL arm (the facts of ≈ 3 in 4 bounty-style misses are not in Wikipedia)" vs arm: "Wikipedia is not reopened as kit content for V-para, and not closed either (> 6)" and "Lo… | <workspace>/rnd/research/coordinator/CLOSED.md:69 | <workspace>/rnd/research/coordinator/arms/wikifull/STAGE-B.md:24 | 9/34 verified is a lower bound; the frozen MARGINAL band does not establish that the remaining ≈ 3/4 are absent from Wikipedia (17/34 hit at ≥ 0.6) — the same … | CLOSED.md R45 outcome → 'closed: MARGINAL (9/34 verified, lower bound), no WIKI-ALL arm; Wikipedia neither reopened nor closed as kit content' |
| WIKIFULL-REOPEN | HANDOFF: "all of Wikipedia (Aug-2025 + the delta to 2026-10-01) holds the missing fact for ≤ 9/34 bounty-style absent items" vs arm "pooled A+B = 9/34 verified … Lower bound" and "could add ≈ 0–3 more" | <workspace>/rnd/research/coordinator/HANDOFF-2026-10-13.md:11 | <workspace>/rnd/research/coordinator/arms/wikifull/STAGE-B.md:2 | ≥ 9/34 verified (lower bound, ≈ 9–12 by scaling); '≤ 9/34' inverts the bound | HANDOFF-2026-10-13.md:11 → 'holds the missing fact for ≥ 9/34 (verified lower bound; ≈ ≤ 12 by scaling)' |
| WIKISECTION | CLOSED R39: "lead/intro ≤ 8 %" vs arm vital-intro control on V-para "1 of 6" (17 %) (lead 1/13 = 8 %, 1/30) | <workspace>/rnd/research/coordinator/CLOSED.md:63 | <workspace>/rnd/research/coordinator/arms/wikisection/WIKISECTION.m… | lead 1/13 and 1/30; vital intro 1 of 6 (V-para) and 0 of 20 (v0.2) — ≤ 8 % holds only with 13 as denominator | CLOSED.md R39 → 'lead 1/13, 1/30; vital intro 1/6, 0/20' |
| AR | CUT3DEV.md:295 says 'The crypto pack has no EIP-7251 constants table at all; the pack build stripped it.' QUEUE.md:551 says 'vit-cry-009 out of scope (EIP-7251 table not in pack)'. QUEUE.md:579 says 'Correction: EIP-725… | rnd/research/coordinator/arms/CUT3DEV.md:295 | rnd/research/QUEUE.md:579 | The later knowledge-pack sizing correction is right. The table is in the pack, so the A2 'out of scope' rationale (CUT3DEV.md:14, :295; QUEUE.md:551) is stale.… | Add a line under CUT3DEV.md:295: 'Corrected 10-04 (QUEUE l.579): the EIP-7251 table IS in the crypto pack; A2 is a selection problem, not coverage.' |
| SC-L0 (SC v1 trigger: water-safety card… | QUEUE.md:549 says 'units stack 1280/1280 ... patches ... sc 8c93bc8d…, stack 0cb058f1…'. On disk, SHA256SUMS:6 has '80bcb148… sc-on-cut2.vs-0cfd4a77.patch' and CUT3DEV.md:230 has 'sc-on-cut2 (SC v3 trigger + reviewed te… | rnd/research/QUEUE.md:549 | rnd/research/coordinator/arms/CUT3DEV.md:230 | The sc patch was re-cut later under the same filename (SC v3 plus the reviewed text). The v1 patch 8c93bc8d… that this L0 tested is no longer on disk. | Add a note at QUEUE.md:549 or CUT3DEV.md:230: 'sc-on-cut2 re-cut to SC v3 + text (80bcb148…); the v1 patch 8c93bc8d… was overwritten.' |
| SC-L0 (SC v1 trigger: water-safety card… | CLOSED.md has no row for the SC water card or trigger family. QUEUE.md:578 lists it as killed or parked: 'SC water card (3 rounds)'. | rnd/research/QUEUE.md:578 | rnd/research/coordinator/CLOSED.md:5 | The family is parked or closed after three held-out rounds (S5, S5′, S5″), but the registry, built 10-11, lists only 10-05 onward and omits it. | Add a CLOSED.md row: 'SC water-safety card + widened snakebite trigger \| SC v1/v2/v3; 10-04 \| 4B \| 3 blind-written held-out sets \| S5 18/25, S5′ FF 5/50, S… |
| SC-v2-S5prime | CLOSED.md has no row, although QUEUE.md:556 records 'SC v2 S5′ FAIL ... Set #3 burned for SC' and the family is parked (QUEUE.md:562). | rnd/research/QUEUE.md:556 | rnd/research/coordinator/CLOSED.md:5 | This is part of the closed or parked SC family. The same single row proposed for SC-L0 would cover it. | Cover it in the SC family row proposed for CLOSED.md (S5′ FF 5/50) |
| SC-v3-S5second | CLOSED.md has no row, although QUEUE.md:562 says 'Water card + SC trigger changes PARKED for the bounty' and QUEUE.md:578 says 'SC water card (3 rounds)'. | rnd/research/QUEUE.md:562 | rnd/research/coordinator/CLOSED.md:5 | The parked family is missing from the registry. | Cover it in the SC family row proposed for CLOSED.md (S5″ water 18/25) |
| VG4-S2 (VG v4 threshold/superlative shi… | CUT3DEV.md:39 still says 'Round 6: VG v4 on cut 3 (2026-10-04, DEV; not adopted, awaits the coordinator's fresh probe set #2 and ship gate)'. QUEUE.md:577 says 'VG-S2 FAIL → VG v4 NOT adopted ... VG line CLOSED'. | rnd/research/coordinator/arms/CUT3DEV.md:39 | rnd/research/QUEUE.md:577 | VG-S2 failed (vg4-S2-REVIEW.md:2). CUT3DEV.md was never updated. | Edit CUT3DEV.md:39 to read 'Round 6 ... VG-S2 FAIL (vgq2-002 WRONG; vg4-S2-REVIEW.md) → v4 not adopted; VG line CLOSED (QUEUE l.577)' |
| VG4-S2 (VG v4 threshold/superlative shi… | QUEUE.md:577 says '**VG line CLOSED** (no v5 ...)', but CLOSED.md has no VG row (CLOSED.md:5 '36 rows' TL;DR; the rows list holds no VG/verdict-guard entry). | rnd/research/QUEUE.md:577 | rnd/research/coordinator/CLOSED.md:5 | The VG extension line (v4 and later) is closed and the registry omits it. | Add a CLOSED.md row: 'Verdict guard extensions (VG v4 threshold/superlative) \| VG-S2; 10-04 \| 4B \| blind-written probe set #2, 120 \| 1 WRONG of 2 fires; re… |
| CUT3DEV (cut 3 build: cut 2 + VG v3 + A… | QUEUE.md:549 says 'units stack 1280/1280 ... stack 0cb058f1…'. CUT3DEV.md:233 says 'cut3dev-stack.vs-0cfd4a77.patch ... a77b3b34… \| 1293/1293', and SHA256SUMS:3 = a77b3b34…. | rnd/research/QUEUE.md:549 | rnd/research/coordinator/arms/CUT3DEV.md:233 | The stack patch was re-cut later (VG v2 + SC v3 + text, HEAD 35cd4c30) under the same filename. The L0-era stack 0cb058f1… is no longer on disk. | Add a note at CUT3DEV.md:233: 'supersedes the L0-era stack 0cb058f1… (1280/1280, QUEUE l.549)' |
| K3-ON-CUT2 | CLOSED.md has no row for a decisive step-0 NO-ADOPT ("a deterministic step-0 gate failed with 0 judge calls" is an explicit 'closed' rule at CLOSED.md:5); the arm is "verdict NO-ADOPT (fails the prompt-token gate)" | <workspace>/rnd/research/coordinator/k3-on-cut2.md:1 | <workspace>/rnd/research/coordinator/CLOSED.md:4-12 (no K3 row; gre… | Arm is closed at step 0 with 0 calls; CLOSED.md is missing the row (LEDGER-AUDIT-2026-10-13.md:255 already notes 'K3 and TF2 have no CLOSED row') | Add CLOSED.md 4B-side row: K3 k=4->3 (k3-on-cut2, 10-04), v0.1 EN 60 x s44/s45, 0 calls, prompt tokens 458.9 -> 439.7 saved 19.3 < 100, label closed (step-0 de… |
| TF2-ON-CUT2 | Decisive "verdict NO-GO (tf2 stays out of the next ship cut)" with no CLOSED.md row | <workspace>/rnd/research/coordinator/tf2-on-cut2.md:1 | <workspace>/rnd/research/coordinator/CLOSED.md (no tf2/crypto-gate/… | Closed by frozen bar; CLOSED.md missing the row (LEDGER-AUDIT-2026-10-13.md:255) | Add CLOSED.md row: crypto-kit gate + travel/food routing (tf2-on-cut2, 10-04), V-exact 5 judge items x s42/s43 Opus judge.v1, Japan 0.356 -> 0.338 (−0.018, ins… |
| CUT3-VGAR-L1 | Frozen criterion: "If the file says FAIL, VG is not adopted whatever its L1 result. If it is absent, VG is reported as pending review." vs report: "VG: L1 PASS, adoption PENDING" while citing "arms/vg-REVIEW.md (VG v1, … | <workspace>/rnd/research/coordinator/cut3-vgar-L1-criterion.md:54 | <workspace>/rnd/research/coordinator/cut3-vgar-L1.md:54-55 | Under its own frozen rule this arm does not adopt VG; VG v3 entered cut 3 via VG-S PASS + V5′ (QUEUE.md:569), a gate redefined at QUEUE.md:559 ('VG adoption ne… | Amend cut3-vgar-L1.md:54 to 'VG: L1 PASS, NOT adopted under this criterion (vg-REVIEW.md V5 FAIL); VG v3 adoption via VG-S gate, QUEUE.md:569' |

## A.3 Decisive verdict, no CLOSED.md row (48) — pasteable rows: proposals/LEDGER-FIXES-2026-10-13.md §1

| arm | status (as written) | primary Δ | n / seeds / judge | result file |
|---|---|---|---|---|
| CF | closed: FAIL at L0 (bar 1 data review 84.0% vs >= 98% with currency/plug errors; bar 2 blind trigger recall 80/100 vs >= 90%, false fires 0… | n/a (L0 deterministic gates only; the L1 forecast +0.005 to… | data revi… / n/a (… / none (L0 deterministic; data … | arms/cf/CF.md (+ data-REVIEW.md, trigger-result.txt) |
| CRYPTOFACTS-step1 | closed (step-1 coverage gate NO; 'Line closed at step 1', QUEUE l.796) | n/a (coverage bars: (i) 2/11 A+B vs >= 6 FAIL; (ii) 1/7 sig… | 11 v0.1 c… / n/a (… / none (0 judge calls; existing… | arms/cryptofacts/CRYPTOFACTS-step1.md |
| CRYPTOSEL | closed (L1 FAIL on target gate, not adopted; stop rule: no revision after L1) | target gate +0.472 vs bar +0.5 (FAIL); pooled 57-item paire… | L0: 71 it… / 44, 45 / Opus judge.v1-med (judge.mjs … | arms/cryptosel/cryptosel-L1.md (L1 verdict); arms/cryptosel… |
| CRYPTOTRUTH | parked (NOT ADOPTED as frozen: G2 FAIL on 1 of 3 fictional probes; G1 and G3 pass; QUEUE l.702 'parked for after the claim (PR phase), with… | +0.0092, CI90 [-0.0034, +0.0244] (ctl 0.5594 -> arm 0.5686;… | 57 judged… / 44, 45 / Opus judge.v1-med (--effort m… | arms/cryptotruth/CRYPTOTRUTH.md |
| CUT4-KVFIX | lever-adopted (shipped in cut 4 on gates (1)+(2) per criterion; device gate (3) still open, never reported) | n/a (identity gate: 60/60 identical per seed vs same-day cu… | v0.1 EN 6… / 44, 45 / none (judge skipped, 0 change… | arms/cut4/CUT4.md; arms/cut4/cut4-L1.md |
| CUT4-INSTANT-FRAG | lever-adopted (L0 PASS, L1 PASS vacuously with empty changed set; shipped in cut 4, later extended by INSTANT-SUBJ) | n/a (0 changed items vs same-day cut 3 on v0.1 EN s44+s45; … | L0: 71 (v… / 44, 4… / none (judge skipped, changed … | arms/cut4/CUT4.md; arms/cut4/cut4-L1.md |
| CUT5-SPEED | closed: NOT ADOPTED as cut 5 (G3 FAIL 1.071x vs bar <= 0.800; G1/G2/G4 PASS); perf arms parked for a device ABBA (QUEUE.md:699 A/B 0.445x c… | retrieval wall arm/control pooled 1.071 (14457 -> 15478 ms;… | 120 (v0.1… / s44, … / none | arms/cut5speed/CUT5SPEED.md |
| CUT5-LITE | lever-adopted (cut 5 = device-day candidate; later the base of cut 6 = cut 5 + DETMAX, QUEUE.md:694, and so of cut 7) | retrieval wall arm/control pooled 0.961 (14600 -> 14031 ms;… | 120 (v0.1… / s44, … / none | arms/cut5lite/CUT5LITE.md |
| CV | closed: KILLED. L0 FAIL (6 regressions, bar <= 2) → revision 1 → ship gate FAIL (3 regressions, bar <= 2) → stop rule (QUEUE.md:596). The c… | Gate set: +26.5 pp verdict accuracy (47/83 = 56.6% → 69/83 … | DEV 155 v… / s44 / none (verdict scored by coord… | arms/cv/CV.md |
| CVS | closed (gate #3 PASS, v0.1 EN L1 FAIL on 2 gates; killed by the no-revision stop rule) | L1: cut 3 0.5656 → CVS 0.5606, Δ -0.0050, CI90 [-0.0150, +0… | gate #3: … / gate … / none for gate #3 (determinist… | arms/cvs/cvs-L1.md (L1); arms/cvs/gate3-score.txt (gate #3)… |
| CVH | closed (Step 1 v0.1 EN L1 FAIL on 3 of 5 gates; Step 2 never started by the stop rule) | cut 3 0.5656 → CVH 0.5622, Δ -0.0034, CI90 [-0.0153, +0.006… | v0.1 EN 6… / s44 +… / Opus judge.v1-med (judge.mjs … | arms/cvh/cvh-L1.md |
| CVO | closed (Step 1 L1 PASS vs the same-day control; Step 2 fresh blind gate #4 FAIL, +6.0 pp < +8 bar; killed by the stop rule) | gate #4 (rescored, QUEUE l.618): 41 → 46/84 (48.8% → 54.8%,… | L1: v0.1 … / L1: s… / Opus judge.v1-med (8 calls on… | arms/cvo/cvo-L1.md (Step 1); arms/cvo/gate4-score.txt + gat… |
| DEEPCOVER | closed: NO at the slice (Haiku +0.005 sent it to Opus under l1_futility; Opus Δ −0.027, correctness −0.11). Full v0.2 110 and V-para s42 58… | −0.027 (−0.077…+0.019) (Opus N=4, random20-v02 slice, s42; … | 20 (rando… / 1 (s4… / Haiku 5.5-low N=4 (L1) then O… | arms/deepcover/DEEPCOVER.md |
| DEEPTHINK | lever-adopted (thinking on the deep tier adopted; budget later moved 1024 → 512 by DT512); L1 PROMOTED on the Δ clause | Opus 2 seeds paired_gap 2-level: raw +0.075 (+0.040…+0.110)… | 51 judged… / 42, 43 / Haiku 5.5-low (L1, s42) + Opu… | arms/deepthink/DEEPTHINK.md |
| DEEPTHINK-V02 | NO at L1 by the frozen rule (Haiku Δ +0.027 < +0.03; stands); effect later sized positive on Opus by Addendum 1 (+0.045 raw), which prompte… | +0.027 (+0.002…+0.054) Haiku, 220 dedup rows (raw 266-row f… | 110 / 42 / Haiku 5.5-low | arms/deepthinkv02/DEEPTHINKV02.md |
| DETMAX | lever-adopted (ADOPT, all five gates pass) → cut 6 = cut 5 + DETMAX | n/a (G3: 0/240 arm mismatches vs control 7/240; G4: 1 added… | 60 probes… / v0.1 … / none | arms/detfu/DETMAX.md |
| FOLLOWQG | closed (NOT ADOPTED: G3 FAIL 45 % < 60 %) | arm wins 9 of 20 non-tie decisions = 45% (bar >= 60%) | 13 change… / seed … / Opus A/B (claude -p, both ord… | arms/followq/FOLLOWQG.md |
| GATEFID | closed: FIDELITY OK (tooling/harness fidelity check, no judge) | 0.000 by construction (0/60 text changes, nothing judged) | 60 / s44 / none | arms/gatefid/GATEFID.md |
| HAIKUJUDGE | lever-adopted (judge protocol: Haiku 5.5-low adopted as L1 judge, 4/4 bars; addendum applied to L1-PROTOCOL.md:11) | Haiku ratio 0.566 vs Opus 0.634, Δ −0.069 (95 % CI −0.090, … | 57 items … / judge… / Haiku 5.5-low (calibrated vs … | arms/haikujudge/HAIKUJUDGE.md |
| HFUFIX | closed: NOT ADOPTED as frozen (G3 58.1% < 90%; G5b 4/20 vs 0, pre-existing). The rescue HFU-FIX2 also failed, so the family is closed with … | G3 arm 144/248 = 58.1% vs control 58/248 = 23.4% (bar >= 90… | G3: 58 EN… / v0.1 … / none | arms/hfu/HFUFIX.md (build: arms/hfu/HFUFIX-build.md) |
| HFUFIX2 | closed: NOT ADOPTED. The HFU-FIX family is closed with no further rescue (HFUFIX2.md:5; QUEUE.md:690). | G3' arm 64/76 = 84.2% (bar >= 90%, FAIL) vs control 31/76 =… | 19 of 58 … / n/a (… / none | arms/hfu/HFUFIX2.md |
| INSTSUBJ | lever-adopted into cut 4 (L0 PASS, uninformative gate; QUEUE.md:647) | n/a (0 tier changes, 0 correct instants lost on v0.1 EN + V… | lookup se… / n/a (… / none | arms/instsubj/INSTSUBJ.md (scores: arms/instsubj/l0/lookup2… |
| KVQ8 | PASS all gates → ADOPT as a device-day candidate (device speed/swap untested; not in any cut) | −0.0077, two-level bootstrap CI90 [−0.0232, +0.0062] (poole… | 57 judged… / 2 (s4… / Opus judge.v1-med | arms/kvq8/KVQ8-L1.md |
| LOCALGATE | closed (FAIL on both gate types for Qwen3-4B and for Laya zero-shot; jev stays; Laya fine-tune parked) | n/a (agreement vs cached jev: Qwen has_fact 0.790 / FPR 0.1… | 500 reque… / sampl… / none (reference = cached jev … | arms/localgate/LOCALGATE.md |
| OPUSSHARD | lever-adopted (USABLE at N = 4; Opus L2/claim judging may run 4 shards; 2026-10-08 13:33) | Δratio -0.0135 (boot CI -0.025 to -0.002), 10 items × 2 ord… | 10 items … / 1 (ju… / Opus judge.v1 | arms/opusshard/OPUSSHARD.md |
| P4 packGround (PACKCOND P4 step 0) | closed (FAIL at the step-0 replay gate, 2026-10-12 20:37; packGround off, no judge calls; later re-tested on the 180 self-tests as GROUND-S… | F0 article kept 11/32 → 14/32 (bar ≥ 16); control kept list… | 32 in-pac… / n/a (… / none | arms/packcond/P4-GATE.md (+ PATCH-DESIGN.md) |
| SECTIONHIT | closed (diagnostic gate not met → no PASSAGE arm, 2026-10-12 21:15) | n/a (keep-3-sections / alt ranker recover 0 additional; any… | 32 in-pac… / 1 (H … / none | arms/packcond/SECTIONHIT.md |
| HEALTHQ | closed (step-0 check failed its gate: 0/18 dropped vs ≥ 3; 2026-10-12 21:06) | n/a | 18 v0.2 h… / n/a / none | none (only tools/healthq_check.py; verdict in QUEUE.md:975) |
| SC-V2-S5PRIME (sc-fresh3) | closed — S5′ FAIL (false fires 5/50 vs ≤ 1 per 25); follow-up SC v3 S5″ also FAIL, SC trigger parked | n/a | 100 (wate… / n/a (… / none | arms/sc-fresh3-S5prime-result.txt |
| SC-V3-S5SECOND (SC v3 trigger S5″ on sc… | closed (S5″ FAIL: water recall 18/25 (72 %) < 80 %; SC water card + trigger changes parked for the bounty) | n/a (deterministic gate: water 18/25 (72 %) FAIL, snakebite… | 100 items… / n/a (… / none | <workspace>/rnd/research/coordinator/arms/sc-fr… |
| SPECDEC | closed (NO-GO; G1–G4 all FAIL for Qwen3-0.6B; Qwen2.5-1.5B refused on vocab) | n/a (identity/projection gates, no judge) | 50 model-… / 1 (s4… / none | arms/specdec/SPECDEC.md |
| TRAVELSEL | closed (L0 FAIL after the one allowed revision; QUEUE calls it 'killed'); L1 never run | n/a (deterministic L0 gate: gold-fact gain 0/3 in round 1, … | 3 target … / none … / none | arms/travelsel/TRAVELSEL.md |
| VENUEGPS | closed (diagnostic; verdict branch 0/7, runner fix not adopted by the rule; superseded by VENUEGPS-2) | P5 0/7 with injected location (s42) vs 0/7 baseline; cause … | 7 venue i… / 42 (s… / none | arms/venuegps/VENUEGPS.md |
| VENUEGPS-2 | lever-adopted (claim wording + runner option; plumbing proof, no engine change; not a claim number) | P5 7/7 on s42 and 7/7 on s43 (vs 0/7 in VENUEGPS) | 7 venue i… / 42, 43 / none | arms/venuegps/VENUEGPS-2.md |
| VITALPACK-ADD | closed in practice: NO at the slice (Opus −0.011) and not detected at L2 on v0.2 full 110 (Opus +0.0012, CI −0.0120…+0.0147); frozen stage … | +0.0012 (−0.0120…+0.0147) raw, Opus judge.v1 N=4, v0.2 full… | smoke 3 v… / 1 (s4… / Haiku 5.5-low (L1) + Opus jud… | arms/vitalpack/VITALADD.md |
| AR | lever-adopted (L0 PASS on A1, A3-A6; A2 FAIL reported separately; L1 AR ADOPT; shipped in cut 3) | n/a at L0 (deterministic); L1 component vit-sci-003 rubric … | 60 v0.1 E… / n/a (… / none (L0); L1 Opus judge.v1-m… | arms/ar-L0-result.txt |
| SC-L0 (SC v1 trigger: water-safety card… | FAIL (S5 72 % < 80 %); superseded by v2/v3; water card and trigger PARKED | n/a (deterministic L0) | held-out … / n/a / none | arms/sc-L0-result.txt |
| SC-v2-S5prime | FAIL (S5′ false fires 5/50 vs bar ≤ 2); superseded by v3 | n/a | 100 (25 w… / n/a / none | arms/sc-fresh3-S5prime-result.txt |
| SC-v3-S5second | parked (S5″ FAIL: water recall 18/25; SC water card and trigger PARKED for the bounty) | n/a | 100 (25 w… / n/a / none | arms/sc-fresh4-S5second-result.txt |
| SC-S6 / SBt (reviewed snakebite card te… | lever-adopted (snakebite text only, SBt in cut 3; water text approved but never shipped) | dng-001 rubric +0.92 (2.67 -> 3.58), cut 3 confirmation, ju… | 2 cards / n/a / independent Opus reviewer (te… | arms/sc-REVIEW.md |
| VG-L0 (verdict guard v1) | L0 FAIL by the letter (V2) with a disclosed exception, plus V5 FAIL. The VG line was later adopted as v3 in cut 3. | n/a (L0); stacked L1 component deltas lan-ref-003 +2.67, vi… | 12 trace … / cut 2… / none (L0); V5 independent Opu… | arms/vg-L0-result.txt |
| VG-S (VG v3 ship gate) | lever-adopted (VG-S PASS → cut 3 adopted with VG v3) | n/a for the gate; cut 3 stack L1 Δ +0.029, CI90 [+0.007, +0… | 90 (compa… / s44 (… / independent Opus reviewer (la… | arms/vg-S-REVIEW.md |
| VG4-S2 (VG v4 threshold/superlative shi… | closed (VG-S2 FAIL: 1 WRONG fire; VG v4 not adopted; VG line CLOSED) | n/a (v4 changes no v0.1 or V-exact bench answer: QUEUE.md:5… | 120 (thre… / s44 (… / independent Opus reviewer | arms/vg4-S2-REVIEW.md |
| CUT3DEV (cut 3 build: cut 2 + VG v3 + A… | lever-adopted (CUT 3 ADOPTED after VG-S, CONFIRMED with no regression) | stack L1 (VG v1 + AR vs cut 2) Δ +0.029, CI90 [+0.007, +0.0… | 57 judged… / s44+s… / Opus judge.v1-med | rnd/research/coordinator/cut3-vgar-L1.md; cut3-confirm.md; … |
| K3-ON-CUT2 | closed (NO-ADOPT at deterministic gate 5; judge skipped by frozen cost rule; gates 1, 2, 4 not measured) | n/a (quality not measured); gate 5 prompt-token saving 19.3… | 60 v0.1 E… / 44, 45 / none (judge.v1-med Opus plann… | <workspace>/rnd/research/coordinator/k3-on-cut2… |
| TF2-ON-CUT2 | closed (NO-GO: G3 Japan bar failed; tf2 stays out of the ship cut) | vx-001 Japan −0.018 (0.356 -> 0.338 (0.276, 0.400)); bar >=… | G2: 60 v0… / G2 s4… / Opus judge.v1 (claude-opus-5-… | <workspace>/rnd/research/coordinator/tf2-on-cut… |
| CUT3-CONFIRM | confirmed (no regression) — confirmation of the cut 3 build adopted at QUEUE.md:569 | gated: min changed-item rubric Δ +0.92 (dng-001), V-exact m… | 57 judged… / v0.1 … / Opus judge.v1-med (v0.1) + ju… | <workspace>/rnd/research/coordinator/cut3-confi… |
| CUT3-VGAR-L1 | AR ADOPT; VG L1 PASS but NOT adopted under this criterion (vg-REVIEW.md V5 FAIL). VG v3 was adopted later through a different gate (VG-S PA… | Δ +0.029, CI90 [+0.007, +0.058] (pooled 0.5335 -> 0.5623, 5… | 57 v0.1 E… / 44, 45 / Opus judge.v1-med | <workspace>/rnd/research/coordinator/cut3-vgar-… |

## A.4 CLOSED.md row disagrees with the arm file (5)

| arm | CLOSED row | arm verdict (as written) | primary Δ |
|---|---|---|---|
| DEEPFULL-F2 | R25 | Verdict: NO at the slice (both arms). ... F2 (persona "detailed" + context 1200 / cap 400) Δ −0.013 (−0.069…+0.048), h2h 6/3/11; wins vs ref 0/0 everywhere. Ne… | −0.013 (−0.069…+0.048) (Haiku 5.5-low N=4, signal20-vpara s… |
| HUMANSFT | R12 | Bar <= 2/20 NOT MET -> HUMANSFT = FAIL. No LoRA target approved by this arm. | n/a (strict review 6/20 flagged vs bar <= 2/20 [CLAPnq 3/17… |
| PACKROUTE-2 | R48 | PACKROUTE-2 stage 0a — **FAIL at step 0a** on both wordings (2026-10-13 14:4x; criterion sha d67fd81c…; 0 judge / 0 paid; MacBook; stage 0b not run) ... 0b dia… | n/a (accuracy gate: own pack 105/180 (0.58) v1, 109/180 (0.… |
| WIKIFULL-REOPEN | R45 | Verdict (frozen rule): MARGINAL — 9/34 verified (A 7 + B 2). B does not lift the pooled count to ≥ 14 → no WIKI-ALL arm; Wikipedia is not reopened as kit conte… | n/a (0-call gate; pooled A+B 9/34 verified, A 7 + B 2) |
| WIKISECTION | R39 | Verdict: FAIL on both sets — the facts are not in the kept article at all. | n/a (0-call gate; V-para 2/13 (15 %), v0.2 4/30 (13 %) vs b… |

## A.5 Blind set touched, no EXPOSURES.md row (10) — pasteable rows: LEDGER-FIXES §3

| arm | blind sets used | QUEUE rows |
|---|---|---|
| DEEPHEDGE | bench-v02 | 951-952 (incidental mentions: 961, 970) |
| DEEPROUTE-VPARA | V-para, bench-v02 | 867, 868, 882 |
| EVALFIX | V-para, bench-v02 | 962 |
| LENGTHSHARE | V-para, bench-v02 | 903, 905, 906, 909, 916, 1080 |
| LOCALGATE |  | 988, 989, 995, 1080 (Laya background on… |
| HEALTHQ | bench-v02 | 975, 1080 |
| T-K4a | bench-v02 | 989, 1080 |
| SEEDVAR | V-para, bench-v02 | 871, 872, 873, 876, 890, 905, 917, 947,… |
| RANDOM20 (random stratified slices) | bench-v02, V-para | 905, 912, 913, 924, 926, 933, 934 |
| L1-PROTOCOL (judge triage protocol) | bench-v02, V-para | 750, 800, 824, 851, 905 |

## A.6 Flagged "no criterion sha" (41; LEDGER-FIXES §5: only 5 + 4 are criterion files without a hash, the rest have no criterion file)

| arm | criterion file (as recorded) | status |
|---|---|---|
| CRYPTOSEL | arms/cryptosel/CRYPTOSEL-criterion.md | closed (L1 FAIL on target gate, not adopted; stop rule: no revision after L1) |
| CVO | arms/cvo/CVO-criterion.md | closed (Step 1 L1 PASS vs the same-day control; Step 2 fresh blind gate #4 FAIL, +6.0 pp < +8 bar; … |
| DEEPCOV-FB | none (gate rule stated in REPLAY-v01.md:37) | closed: gate FAIL at step 0 (0 judge calls; deterministic retrieval replay on public v0.1) |
| DEEPRERANK | none in arm directory (gate ≥ 5 items referenced from HANDOFF §4 step 4) | closed (FAIL at step 0: gold enters the deep top-6 on 2 items; gate ≥ 5; 0 judge calls) |
| DEEPROUTE-OOS | none (descriptive, no verdict rule) | closed (descriptive, no verdict rule; folded into routing family R28) |
| DEEPROUTE-VPARA | none (descriptive, no verdict rule) | closed (descriptive, no verdict rule; routing family CLOSED R28) |
| EVALFIX | none | tooling (analysis-only, 0 judge calls; no verdict changes) |
| FACTS-RECALL | none (scoring rule 'frozen in the task'; set sha in recall-set.sha256) | closed (measurement only; set became dev after r3) |
| FACTS-BLIND | none (no r3 criterion; scorer rule from FACTS-RECALL) | closed (direction confirmed on precision; recall open; set 2 dev after r3) |
| LCRELAX | none (dev probe) | closed (dev probe, not adopted; r4to 'LCRELAX NO, FACTS stays at r6') |
| K2HALF | none (gate bar stated only in QUEUE.md:961 and K2HALF-gate.md) | closed: FAIL at step 0 (greedy-agreement gate); parked as a device-speed candidate |
| L1CTL | none (control run, by design) | tooling / control run (no criterion, no verdict by design) |
| LOCALGATE | none | closed (FAIL on both gate types for Qwen3-4B and for Laya zero-shot; jev stays; Laya fine-tune park… |
| LORA-DIAG | arms/loradiag/LORA-DIAG-criterion.DRAFT.md | not run: draft criterion never frozen or authorised (FTDATA 1k strict review FAIL 16/20, then the d… |
| NUMCHECK | none in dir (gate bars stated inside NUMCHECK-gate.md) | closed (FAIL at the 0-call gate, 2026-10-12 14:21) |
| PACKCOND-P1 | none (measurement) | measurement (done; Addendum 1: all PACKCOND numbers on above_min from 10-12 21:0x) |
| PACKCOND-P2 | none (measurement) | measurement (done) |
| P4 packGround (PACKCOND P4 step 0) | none in dir (gate bars in P4-GATE.md / QUEUE) | closed (FAIL at the step-0 replay gate, 2026-10-12 20:37; packGround off, no judge calls; later re-… |
| SECTIONHIT | none (diagnostic) | closed (diagnostic gate not met → no PASSAGE arm, 2026-10-12 21:15) |
| DENSECHUNK | none in dir (gate 'frozen in QUEUE before the run') | parked (D0 headroom PASS on part 1, FAIL on part 2 for the fused variant; superseded by DENSECHUNK-… |
| HEALTHQ | none | closed (step-0 check failed its gate: 0/18 dropped vs ≥ 3; 2026-10-12 21:06) |
| SELFTEST-SCORES | none | measurement (done 2026-10-13 10:37; no verdict rule) |
| WAVE3 | none | done (product: qa-cooking-se default-eligible, qa-money-se user-selected only; published on HF; no … |
| T-K2 | none | tooling (done 2026-10-12; patch uncommitted in wt/packs) |
| T-K4a | none | closed (probe verdict: default-eligible qa-health-se, qa-outdoors-se, boar-firstaid-en, boar-medlin… |
| T-K4c | none | tooling (pipeline + first self-test number; no control at the time) |
| T-K4d | none | closed (probe: wave-1 packs cover 1/34 V-para absent items; product value, not a bar lever) |
| T-K6b | none | closed (probe: boar-simplewiki-en user-selected only; boar-factbook user-selected only by coordinat… |
| PROBES | none (consumers: arms/ar-L0-criterion.md, arms/sc-L0-criterion.md) | tooling (data-only probe sets for the cut3-dev AR/SC/VG L0 gates; results in arms/CUT3DEV.md) |
| SEEDGEN | none | tooling (done; generation byte-deterministic on the MacBook CPU path; RULE 27) |
| SEEDSPEC (T7) | none (T7 gate defined in DEEP-RESEARCH-2026-10-12.md l.180) | closed (T7 FAILS at step 0; O-6 Integrative Decoding closed, no T9 ID arm) |
| SYNTHDEEP | none (gate taken from LOOP-PROGRAM-2026-10-11.md §3 B7: 'both sides in the prompt on >= 5… | closed: FAIL at step 0 (0-call replay gate; no judge call) |
| T1-DEEP35 | arms/t1deep35/T1-DEEP35-DRAFT.md (proposed criterion, not frozen) | superseded draft: never authorised or run; replaced by DEEPVPARA (criterion frozen 2026-10-08) |
| THREADS2 | none | parked (dormant until a device is available; criterion not written or frozen) |
| WIKISECTION | none (gate rule stated inline: BACKLOG §1 row 1, PASS if ≥ 40 %) | closed (FAIL at 0-call gate, 2/13 V-para and 4/30 v0.2 vs bar 40 %; scope narrowed by Correction 20… |
| WIKISECTION-H5b | none | closed (gate FAIL on V-para 1/13 at p ≥ 0.7; reading scope-corrected 2026-10-12; superseded by WIKI… |
| L1-PROTOCOL (judge triage protocol) | arms/L1-PROTOCOL.md | tooling (protocol frozen 2026-10-06; addenda HAIKUJUDGE/PARJUDGE 10-07, OPUSSHARD/SLICE20 10-08, ne… |
| K3-ON-CUT2 | <workspace>/rnd/research/coordinator/k3-criterion.md | closed (NO-ADOPT at deterministic gate 5; judge skipped by frozen cost rule; gates 1, 2, 4 not meas… |
| TF2-ON-CUT2 | <workspace>/rnd/research/coordinator/tf2-criterion.md | closed (NO-GO: G3 Japan bar failed; tf2 stays out of the ship cut) |
| CUT3-CONFIRM | <workspace>/rnd/research/coordinator/cut3-confirm-criterion.md | confirmed (no regression) — confirmation of the cut 3 build adopted at QUEUE.md:569 |
| CUT3-VGAR-L1 | <workspace>/rnd/research/coordinator/cut3-vgar-L1-criterion.md | AR ADOPT; VG L1 PASS but NOT adopted under this criterion (vg-REVIEW.md V5 FAIL). VG v3 was adopted… |

## A.7 Extraction errors the verifiers corrected (333; the index carries the corrected values)

- CF: blind_sets_used is [] but the arm scored its own blind-written trigger set once: arms/cf/trigger-set/items.jsonl (200 items, trigger-result.txt:1). EXPOSURES.md:89 lists it ('cf trigger-set / trigger-set2 \| set 1 scored once; set 2 never …
- CF: Issue 2 is not a contradiction: CF.md:33 says trigger-set2 was 'not opened or scored', and the folder holding items.jsonl and README.md fits that (frozen at QUEUE:585, 'unopened' at QUEUE:588, 'clean' at EXPOSURES.md:89). The issue should …
- CF: The status 'closed' is right but too vague. The arm failed two L0 bars: bar 1 data (126/150 = 84.0% vs 98%; currency and plug errors where the bar allows 0) and bar 2 trigger (recall 80/100 vs 90%). It was NOT adopted (QUEUE:586) and L1 wa…
- CHATGATE: No material errors. The sets field leaves out what defines the run: the 192 messages are mixed language ('PT 82 / EN 62 / ES 48', CHATGATE.md:6), and the kit is boar-crypto + boar-wikivoyage-en on the Android 12 GB profile, cut 5 ship prof…
- CHATGATE: '31/69' (yes items with sources shown) is a different metric from the confusion-matrix 'sources used 30' (CHATGATE.md:20): shown to the user vs retrieval.kept. Both are as written. Only 30 should be quoted as the G1 complement (30 + 39 = 6…
- COMPLETE: No field errors. The record says 'max tokens 700', which matches criterion:3 and COMPLETE.md:38 ('max_tokens 512 → 700').
- COMPLETE: Issue 4 (confident-wrong arithmetic) is fine: 7 − 1 (lan-cmp-004 left) + 9 new = 15, as COMPLETE.md:59-63 lists. It is not a defect.
- CROWDQ: Issue 3 is out of date. Opus judgment files now exist for ALL 9 packs, not only the qa-*-se ones: travel 20:51, ethereum 20:52, bitcoin 20:53, health 20:54, outdoors 20:56, firstaid 20:56, medlineplus 20:57, factbook 20:58, simplewiki 21:0…
- CROWDQ: Issue 1 needs context. The reach-band change was logged in QUEUE:1030 at 15:08, before any judging (CROWDQ result at 15:44). It is framed as '**Ruling (measurement matching, not a gate change):**' because the cut-7 traces carry no chunkId,…
- CROWDQ: The record leaves out the later Opus L2 confirmation of this cell: PACKS-L2 P − S −0.019 (−0.035…−0.003), SE −0.029, topic −0.006 (QUEUE:1077; RULE-CHANGES/PACKS-L2 aggregation line 'p_s opus pooled n=180 P 0.482 S 0.500 d_raw -0.019 (-0.0…
- CRYPTOSEL: n: L0 '71 items' are 65 unique ids per the CUT4 L0 convention is not stated in CRYPTOSEL.md; CRYPTOSEL.md:15 says 'v0.1 EN 60 + V-exact 11 = 71 items' — record is correct; no change
- CRYPTOSEL: issue 'L0-round2.txt shows the single-run ratio 1.217' should read: L0-round2.txt:10 is 'base 102.7 sel 125 ratio 1.217' (median over items of per-item retrieve ms of one non-interleaved pair), and the per-run p50 ratios were [1.04, 1.058,…
- CRYPTOTRUTH: issue on G3 control: the criterion itself allows it — CRYPTOTRUTH-criterion.md:11 reads 'vs same-day cut 6, judge.v1-med both orders on changed items only (control verdicts from ONE named source run, per the 2026-10-06 rule)'; the same-day…
- CUT4-KVFIX: n/judge: the criterion's gate (2) asks only for 'desktop v0.1 EN s44 replay' (CUT4-criterion.md:5); the run covered s44+s45 (cut4-L1.md:13) — record is fine, but gate (2) is a stack identity check, not a KVFIX test (cut4-L1.md:26)
- CUT4-KVFIX: issue on CUT4.md APK identities: CUT4.md:60 '(same as the cut 4 APK `22e22f2c...`)' refers to the final cut 4 APK (tree 6a61670e…, QUEUE l.651), which is a different build from CUT4.md:53-55 (80925f6a…, tree d631a9de…, superseded per QUEUE…
- CUT4-INSTANT-FRAG: n: CUT4.md:30 states 'v0.1 EN public 60 + V-exact 11 (65 unique ids) \| 71' — add '65 unique ids'
- CUT4-INSTANT-FRAG: sets: 'cut4 lookup-set (40, coordinator-frozen)' should note it is the coordinator's blind-writer set (criterion: '≥ 20 fresh ... lookups written by a blind writer', CUT4-criterion.md:8; QUEUE l.635 'Engineer must not open it; coordinator …
- CUT5-SPEED: status 'closed' is incomplete: the arm is NOT ADOPTED (CUT5SPEED.md:3), but its components 2+3 were carried unchanged into CUT5-LITE (adopted as cut 5, CUT5LITE-criterion.md:5) and component 1 (perf arms) was moved to a device-only A/B tha…
- CUT5-SPEED: No other field errors found: primary_delta 1.071 (CUT5SPEED.md:36), n 120 / 57 timed items / 464 G4 messages (lines 23-25, 30, 54), seeds s44+s45 (line 19), judge none ('No judge calls', line 19), date 2026-10-06 (line 1), criterion sha pr…
- CUT5-LITE: None found. Status, primary_delta 0.961 (CUT5LITE.md:12), n 120 + 464, seeds s44/s45, judge none ('no judge', line 14), date 2026-10-06, criterion sha and patch sha all match the files.
- CUT5-LITE: Minor: CUT5LITE-criterion.sha256 stores the path 'cut5lite/CUT5LITE-criterion.md' (relative to arms/, not to its own dir, unlike the sibling .sha256 files). The hash e8be61a9903d8f427d43d7aeca3bc1086247e35e448f2e0cfa76ac0864502c32 matches.
- CUT7: None material. Clarification on seeds: the fire count read both s42 and s43 request files (CUT7.md:48 'cut6-v0{1,2}-s4{2,3}.requests.jsonl ... cut6-vpara-s4{2,3}.requests.jsonl'); the engine replay used s42 only (CUT7.md:49).
- CUT7: Status, primary_delta (0.000 projected on v0.2/V-para; v0.1 +0.027), n (110 / 58 / 72), judge none (0 judge calls, CUT7.md:1,33), date 2026-10-07, blind sets (bench-v02, V-para) and both shas confirmed.
- CV: blind_sets_used should not be empty. CV ran its ship gate on a frozen 'fresh blind' verdict set: arms/cv/gate-set/items.jsonl (sha afabb860…) with key arms/cv/gate-key/key.jsonl (sha 2a94ed84…), per CV-criterion.md:14 and QUEUE.md:595. EXP…
- CV: verdict_text and status are confirmed only through QUEUE.md:596 and gate-score.txt. CV.md has no verdict section (its TL;DR at l.3 says 'accuracy NOT scored'), as the record's issues already note.
- CV: All other fields confirmed: DEV n 155 + 55 controls with 145 scored (score.txt:1); gate set 120 with 83 scored (gate-score.txt:1; gate-key/README '90 key lines, ambiguous 7'); seed 44 (CV.md:18; cv-timing.txt:1; cv-gate-timing.txt:1); date…
- CVS: date: the record says 2026-10-05 (criterion header and CVS.md header). File mtimes are Oct 4 18:20 to 20:18 local (GMT-3, still Oct 4 in UTC), and QUEUE.md:597-605 sits after 'State after the 2026-10-04 session' (l.578) and before 'Loop re…
- CVS: issue 'scored 83 of 90 key lines while the criterion requires 120/120 valid' mixes two counts. CVS-criterion.md:13 '120/120 valid' counts valid answers, not key lines. The key has 90 lines with 7 ambiguous (QUEUE.md:599), so 83 scored is e…
- CVS: judge: cvs-L1.md:1,8 says only 'judge.v1-med' / 'judge.mjs --effort medium'. 'Opus' comes from judge.mjs's default (--judge-model opus), not from the arm file. The field is acceptable but inferred.
- CVS: criterion_sha_present true is confirmed: shasum -a 256 CVS-criterion.md = 595107c3888d0a137cffdf5b642c384b43c66ea396f4f4d249a3ca84d2de3004, which equals CVS-criterion.sha256 and QUEUE.md:597 '595107c3…'.
- CVH: date: the record says 2026-10-05 (criterion header). Files are dated Oct 4 20:19 to 20:54 local, and QUEUE.md:602-603 precedes 'Loop restarted (r4to, 2026-10-05)' (l.606). The run date is most likely 2026-10-04 local. The 'likely timezone'…
- CVH: judge: cvh-L1.md:1,14 says 'judge.v1-med' / 'judge.mjs --effort medium'. 'Opus' is inferred from judge.mjs's default model.
- CVH: criterion_sha_present true is confirmed: shasum CVH-criterion.md = 010b7ed28df7f7b681ccc54f99a11d8aa1337602bd360530de431d2f13504b3b, which equals CVH-criterion.sha256 and QUEUE.md:602 '010b7ed2…'.
- CVO: criterion_sha_present false is correct by the sibling convention (no CVO-criterion.sha256). But a sha was recorded before the run: QUEUE.md:606 '4c37259b…' matches shasum -a 256 CVO-criterion.md = 4c37259b70a64081131eb2e362fca181dedcdde4d8…
- CVO: issue 'gate4-detail.jsonl vs gate4-detail-cvoself.jsonl differ on cut3 labels for several items': they differ on exactly 10 items (cv4-008, 023, 030, 033, 048, 062, 066, 067, 075, 102), which are the 10 overrides. In cvoself both the cut3 …
- CVO: n: '84 scored (6 ambiguous)' is confirmed by gate4-key README (90 lines, 6 ambiguous) and gate4-set README (120 = 50/40/30). '120/120 valid' and '0 control changes' are in QUEUE.md:618 only, not in the arm files.
- CVO: judge for L1: cvo-L1.md:34 says '--effort medium, 8 calls' (judge.v1-med). 'Opus' is inferred from judge.mjs's default.
- DEEPBO2: None material. Minor: DEEPBO2.md:9 'seed 7' is the selector server seed, and criterion l.12 sets bootstrap seed 7 as well. The field 'bootstrap seed 7' is correct.
- DEEPBO2: issue 'criterion says 204 prompts for S1 alone (l.17)' is accurate as quoted: 'S1 after (≈ 1–1.5 h, prefill-bound: 204 prompts of ≈ 500–900 tokens)'. QUEUE.md:857 reconciles it ('the criterion's "204" counts both selectors'). The actual ru…
- DEEPBO2: criterion_sha_present true is confirmed: shasum = c7e2232f34f9c34c8d5168aa0ac87a0a7bed515dbf95c84284ccb8145c34ed11, which equals DEEPBO2-criterion.sha256 and is cited in DEEPBO2.md:1 and QUEUE.md:857,866.
- DEEPHEDGE: blind_sets_used omits V-para: DEEPHEDGE.md:5 reports a 0-call script read of H's V-para traces ('On V-para: **0/58** items route health-strict'); correct blind_sets_used = [bench-v02, V-para].
- DEEPHEDGE: sets omits the 0-call reads of H's dt512 traces (v0.2 all 110: '18/110 items route health-strict'; V-para 58: '0/58'); correct sets = v0.2 generation 29 ids (E s42 gen2) + script-only read of H s42 traces on v0.2 (110) and V-para (58).
- DEEPHEDGE: n should also note the trace reads: '29 ids generated (hedged-11 ∪ random20-v02), 0 judged; plus 0-call route-code read of H traces 110 v0.2 + 58 V-para'.
- DEEPREAD: status 'not-decided' is imprecise: the frozen rule produced a decided verdict band, INCONCLUSIVE (0.606 ≤ x < 0.660), per DEEPREAD.md:3, :11, :14 and DEEPREAD-criterion.md (Verdict line). Correct to 'INCONCLUSIVE (frozen rule)'. Every othe…
- DEEPSPEED: date: the run spans two days. DEEPSPEED.md:3 says 'Runner: Kiln, 2026-10-07 23:32 to 2026-10-08 00:15' and the criterion was frozen on 2026-10-07 (DEEPSPEED-criterion.md:1). '2026-10-08' is acceptable as the verdict date but leaves out the…
- DEEPSPEED: '34–353' is a reformatted value, not a quote. UPSTREAM-NOTE-ngram.md:4 says 'diverging after 34 to 353 characters', and DEEPSPEED.md:18 lists per-item first-diff indices from @34 to @353. Only QUEUE.md:811 writes '34–353'.
- DEEPSPEED: All other fields confirmed: status closed (no ADOPT, P0 flags unchanged), n 10 prompts x 5 configs = 50 runs (DEEPSPEED.md:6, 50/50 rc 0), greedy, judge none, criterion sha c2e101d3... (shasum matches the .sha256), raw/ has 152 files. The …
- DEEPTHINK: No field-level errors found. status 'lever-adopted' is supported by CLOSED.md:11 ('DEEPTHINK 1024 vs none (+0.075 (+0.040...+0.110), adopted)'). The 1024 budget was later replaced by 512 (CLOSED.md:39, R20 'closed (CHEAPER-PARITY; 512 adop…
- DEEPTHINK: Verified against the files: n = 51 judged ids of 58 requests per seed (DEEPTHINK.md:16-17), seeds 42+43, Haiku L1 on s42 only plus Opus on s42+s43, criterion sha 1d988821... and patch sha eb3f464b... (both shasum = .sha256), date 2026-10-0…
- DEEPTHINK-2: status 'not-decided' is wrong. The result gives a decisive verdict: 'Stage 1 (V-para s42, L1 Haiku): NOT PROMOTED' and 'Rule: ... → **NO**' (DEEPTHINK2.md:2,31). QUEUE.md:823 says 'DEEPTHINK-2 → NO'. The registry label it claims to follow …
- DEEPTHINK-2: The remaining fields are confirmed: n 51 judged ids of 58 requests (DEEPTHINK2.md:17), seed 42, judge Haiku 5.5-low, criterion sha 5af5b013... and patch sha e813da6d... (shasum = .sha256), date 2026-10-08 (runner 18:30–23:05).
- DEEPTHINK-V02: status 'closed' is imprecise. The result is 'L1: NO by the frozen rule' (not promoted, no Opus, no s43 under the rule; DEEPTHINKV02.md:2). The same arm's Addendum 1 then measured the effect as positive on Opus (TV−D raw +0.045 (+0.022…+0.0…
- DEEPTHINK-V02: The other fields are confirmed: n 110, seed 42, judge Haiku 5.5-low, set v0.2 (bench-v02), criterion sha 265ea559... (shasum = .sha256), date 2026-10-09 (run 2026-10-08 23:05 – 2026-10-09 02:32), primary Δ +0.027 (+0.002…+0.054) = aggregat…
- DEEPTHINK-V02-ADDENDUM1: status 'closed' is wrong for this record. The addendum says it 'is a measurement, not a decision: no engine change follows from it' (DEEPTHINKV02-L2-addendum.md:3), and its only reading is the bar reading 'point above, CI straddles' (DEEPT…
- DEEPTHINK-V02-ADDENDUM1: The other fields are confirmed: n 110, seeds 42+43 (s43 ran because the one-seed TV−D CI low > 0, per QUEUE.md:836), judge Opus judge.v1 N=4, set v0.2, criterion file DEEPTHINKV02-L2-addendum.md with sha 92121156... (shasum = .sha256), dat…
- DEEPVPARA: status 'closed' is loose: the arm is a measurement, not a lever closure. Both stages were PROMOTED at L1 (DEEPVPARA.md:2) and the result reads 'below the bar' on both sets. CLOSED.md:9 keeps measurements out of the registry.
- DEEPVPARA: No field-level value errors: every quoted number matches DEEPVPARA.md at the cited line (sha 503c2a0c... re-verified with shasum; 'Power' does not appear in the criterion, confirmed by grep).
- DEEPWIKI: Number '−0.044' is cited at DEEPWIKI.md:2, but the floor-adjusted values W 0.340 / H 0.384 sit in the table at DEEPWIKI.md:15-16. Minor pointer issue only.
- DEEPWIKI: Issue text 'Criterion example path mentions `--timeout-ms 600000` etc. consistent' is not a finding and can be dropped.
- DEEPWIKI: family 'packs' is arguable: CLOSED.md:48 files it under the deep-tier section with system 'deep' (corpus size on the deep tier).
- DENSECHUNK-ST: closed_row_cited 'none' is right for the result file, but CLOSED.md:70 (R46) covers the arm by name ('supersedes DENSECHUNK D0 parked and DENSECHUNK-ST FAIL G2'). The arm has no row of its own.
- DENSECHUNK-ST: Worth adding: unlike DEEPVPARA/DEEPWIKI, this criterion has a full ## Power block (expected_delta +0.05, mde ≈ 0.03, n 180) at criterion:16-24.
- DENSECHUNK-ST2: Issue 'addendum 1 ... written after seeing step-0 results (post-hoc rule change)' needs nuance. The addendum states it was written after step 0 and before any judge call (addendum:1). It is logged as RULE 26 in QUEUE:1008 and RULE-CHANGES,…
- DENSECHUNK-ST2: status 'not-decided' is right per the vocabulary. CLOSED.md:70 labels it 'not decided at MDE 0.03 → parked', and the file's final verdict reads 'NO (not decided at MDE 0.03)' (DENSECHUNK-ST2.md:15).
- DENSECHUNK-ST2: Header DENSECHUNK-ST2.md:1 still reads 'L1 verdict ... Opus L2 launched'; the final Opus verdict is at :15. Stale header, not an extractor error.
- DETMAX: Issue 'DETMAX.md:4 says 4 files vs cut 5 but lists only answer.ts and answer.test.ts' needs refining. The patch file detmax-on-cut4.vs-0cfd4a77.patch is the cumulative patch against 0cfd4a77: it contains 37 'diff --git' file sections (cut …
- DETMAX: The patch sha 824e0b35... was re-verified with shasum and matches DETMAX.md:4.
- DT512: issues: 'Aggregates also include 1-seed and 3-seed L2/paired_gap files (L2-H-3seed.opus.json, paired_gap-HvsT-3seed.json) not summarised' -> the 3-seed files are empty, not unsummarised: L2-H-3seed.opus.json is 0 bytes and paired_gap-HvsT-…
- DT512: issues missed an internal rounding slip: DT512.md:37 ladder gives 'deep + think 512 0.43' while the table at DT512.md:28 gives floor-adj 0.436 (L2-H-2seed.opus.json above_min 0.4359), which rounds to 0.44 as QUEUE.md:842 and CLAUDE.md quot…
- DT512: All other fields confirmed: status closed (CHEAPER-PARITY), primary_delta +0.011 (-0.010…+0.031) (paired_gap-HvsT-2seed.json raw 0.0109 [-0.0096, 0.0306]), n 51 judged / 58 generated x 2 seeds + slice 20, seeds 42/43 (+44 via SEEDVAR note …
- DT256: issues missed an anomaly flagged in BAR-TABLE.md:120: in aggregates/L2-Q-2seed.opus.json the seed-43 head-to-head of Q vs T and Q vs H is identical (aHigher 10 / same 15 / bHigher 26), reproduced in DT256.md:33 ('s43 -0.056 … h2h 10/15/26'…
- DT256: issues: 'Criterion sha 6d3c325c… cited in result matches': confirmed by my own shasum (6d3c325c693913e280ef156595d91ebc9ce6e769b940d5eb901760de266f7a59); patch 9d91b564… also matches.
- DT256: All other fields confirmed: status closed (CHEAPER-LOSS), primary_delta -0.028 (-0.056…-0.003) (paired_gap-QvsT-2seed.json raw -0.0277 [-0.0558,-0.003]), n 51 judged / 58 generated × 2 + slice 20, seeds 42/43, judge Haiku 5.5-low N=4 + Opu…
- DT512-V02: issues: 'Criterion requires per-category Δ vs TV; result line 18 shows only ? -0.005 (23/55/32)': confirmed and traced to the source. aggregates/cat-HvsTV-1seed.opus.json has a single byCategory key '?' (n 110), so the v0.2 items carried n…
- DT512-V02: issues: 'status closed follows CLOSED.md R20': CLOSED.md:39 does group DT512-V02 under R20 ('v0.2 -0.005 (-0.020...+0.009), x0.62'), but the result is measurement only (DT512V02-criterion.md:1,3); 'closed (measurement)' is the more accurat…
- DT512-V02: win-rate '0/110' is correct for wins; EVALFIX.md:11 and BAR-TABLE.md:57 add that one item is an order-disagreement tie (0/1/109).
- DT512-V02: All other fields confirmed: primary_delta -0.005 (-0.020…+0.009) (paired_gap-HvsTV-1seed.json raw -0.0047 [-0.0196, 0.0086]), n 110, seed 42 only (seed-43 trigger did not fire), judge Opus judge.v1 N=4 with 220 calls, 0 failures and 0 Haik…
- EVALFIX: exposures: EVALFIX's scripts read blind judgment files on both sets (tools/winsties.py:6-17 and tools/robust_ci.py:11-22 open <private held-out dir>,cut6,quantceil,deepthink,deepvpara}/*.judgments.jsonl and…
- EVALFIX: numbers 'H/K/Q V-para per-seed win rate': Q here is QUANTCEIL's arm (qc-Q-vpara-s42/s43, tools/winsties.py:14-15), not DT256's Q. The record should say so.
- EVALFIX: seeds: robust_ci.py also reads K v0.2 s43 (cut6-v02-s43, robust_ci.py:22), so the re-analysis covers v0.2 s42 and s43 for K, not only s42.
- EVALFIX: issues: the record missed a second internal inconsistency. EVALFIX.md:2 says the robust intervals 'agree with the bootstrap within 0.01 on all five delta rows', but the table has four delta rows plus the SEEDVAR level row, whose gap is 0.0…
- EVALFIX: Other fields confirmed: status tooling (0 judge calls, no criterion file), date 2026-10-12 (QUEUE.md:962 at 14:24; LOOP-LOG.md:50 '2026-10-12 14:24 (tick 48)'), n 1052 mapped rows (= 526 item-runs × 2 orders), primary_delta n/a.
- FACTS: status 'closed' understates the verdict: FACTS.md:97 is 'Verdict (by the letter): GO' (step 1 + G2-G5 pass); the r1 prototype was superseded by r2, not closed as a negative
- FACTS-r6: status 'lever-adopted' conflates two facts: the frozen verdict is FAIL (FACTS-r6-SET4.md:1 'FAIL by the frozen criterion'); adoption into cut 7 was r4to's decision (QUEUE:770) and the CUT7 arm (QUEUE:772), not this arm's verdict
- FACTS-r6: DATA-REVIEW-r6.md:29 holds only the seed-47 '1/60'; the seed-46 '4/60' is at DATA-REVIEW-r6.md:8
- LCRELAX: date 2026-10-08 is wrong: QUEUE logs the probe at 00:13 in the overnight block after 'Overnight loop (00:09 ...)' (l.759) that follows the 10-06 23:54 entries and precedes 'Session 10-07 morning start (09:13)' and r4to's 'LCRELAX NO' at 09…
- FOLLOWQG: issue 'the base is cut 5 lite (0cfd4a77)' is wrong: 0cfd4a77 is upstream/main, the shared engine base (QUEUE.md:3 'upstream/main 0cfd4a77'); FOLLOWQG.md:24 says the patch is 'git diff 0cfd4a77..HEAD, includes cut 5 lite + speed'. So the pa…
- G4ENG: No field-level errors found. All numbers re-checked against G4ENG-L1.md lines 3-28 and G4ENG-criterion.md. Criterion sha 5aecdd03d1adc3b42dd89220f35601acc07bcfdf7f4760ddfc9648405f903eaa recomputed with shasum and matches G4ENG-criterion.sh…
- G4ENG: Clarification on 'judge': G4ENG-L1.md:8 names only `judge.mjs --bench bench/v0.1 --effort medium` (judge.v1-med) and never says 'Opus'. The model name comes from CLOSED.md:17 ('Opus judge.v1-med') and the default judge, so 'Opus judge.v1-m…
- G4ENG: The 5/5 vs 5/7 cell is the count with 'mean correctness ≤ 1.0' (G4ENG-L1.md:16). The cw(≤2) labels are 13/12 vs 13/13. The record's 'confident-wrong count' is right for the gate definition.
- GATEFID: numbers['1.021 / 1.010'].where: 1.021 is at cmp-output.txt:3 but 1.010 is at cmp-output.txt:8. Correct to cmp-output.txt:3 and :8.
- GATEFID: numbers['7048 / 7198 / 7120'].where: 7120 (the cut 5 arm sum) is at cmp-output.txt:8, not :3. Correct to cmp-output.txt:3 (7048, 7198) and :8 (7048, 7120).
- GATEFID: Criterion sha 753a7181c98c4a6db95d78eb86dfe36b82285864b245f67f8ca6d13db80252d8 recomputed: matches. No other field errors. The status is better stated as 'closed (FIDELITY OK, tooling)' than as a lever closure.
- GROUND-ST: No numeric extraction errors. All GATE.md:5-15,39 and D0.md:9,23 values match. Criterion sha 895d1ebbd29696af9ddb876b973bc338022764941ce6054cf590f46c39c93214 recomputed: matches GROUND-ST-criterion.sha256.
- GROUND-ST: The issue on patch shas is confirmed. GATE.md:49 cites 'sha 5fd74a85…'. packground2.vs-dt512.patch recomputes to 9acb516065b46f465f4fecde31ce8f4c8a4bab5b0fedc8a831d71f601d9b4729, which matches the .sha256 (updated by addendum 1, GATE.md:67…
- GROUND-ST: Timestamp issue, extended: the criterion header says 'frozen 2026-10-13 13:2x', but the criterion mtime is 13:05 and QUEUE l.1023 logs the freeze at 13:10. GATE header says 13:3x, QUEUE l.1025 says 13:20, and GATE.md/D0.md mtimes are 13:26.
- GROUND-ST: Status nuance: the arm file says 'no variant enters stage 1' (GATE.md:1,18). The ledger disposition (QUEUE l.1026, CLOSED R47, BACKLOG l.28) adds that X3 is carried into STACK as a declared component. The record's 'closed' is right for ste…
- GROUND-ST addendum 1 (X3 perpack): No numeric extraction errors. GATE.md:55-67 and D0.md:28-30 values match. Addendum sha 77eaf4ca4ad5e606c3ef724f6fecf5e7745a04ab0a035540302aad5ed957c907 recomputed: matches. Patch sha 9acb5160… recomputed: matches.
- GROUND-ST addendum 1 (X3 perpack): The timestamp issue is confirmed and extended. Addendum header 'frozen 13:5x' and GATE addendum '14:1x' sit against addendum mtime 13:20, GATE.md mtime 13:26 and QUEUE l.1026 at 13:27. BACKLOG l.28 gives a third time, 'closed at step 0 (10…
- GROUND-ST addendum 1 (X3 perpack): Status nuance: the arm file says 'no variant enters stage 1'. The ledgers (QUEUE l.1026, CLOSED R47, BACKLOG l.28) add that X3 is carried into STACK as a declared component, outside the criterion rule.
- HAIKUJUDGE: numbers['0.073 / 2.50 / [usage detail removed]'].where: 0.073 is on HAIKUJUDGE.md:20 (leg A1 row). Line 23 says only 'Haiku ≈ 0.07' beside Opus 2.50 and Sonnet-low 1.03. Correct to HAIKUJUDGE.md:20 + :23.
- HAIKUJUDGE: primary_delta CI: the [−0.090, −0.049] interval is a 95 % CI ('95 % CI, 2000 boots seed 5', HAIKUJUDGE.md:26), not CI90. Label it explicitly as 95 %.
- HAIKUJUDGE: Criterion sha 58e9c084ba19d2f32e652fb3ebb244cb5c674917d5ed39d6355fa7cc24c6b82e recomputed: matches HAIKUJUDGE-criterion.sha256 and inputs.sha256 line 2. No other field errors.
- HAIKUJUDGE: The issue that the 'NOT applied' note is stale is confirmed: arms/L1-PROTOCOL.md:11 holds the applied 'Addendum 2026-10-07 (HAIKUJUDGE, criterion 58e9c084…)'.
- HFU: status 'closed' is imprecise: HFU is a deterministic diagnostic whose decision rule was MET and that triggered the fix arm HFU-FIX (HFU.md:53 'Rule (>= 10% lost) met by a wide margin. A fix arm is justified'). Better: 'diagnostic complete,…
- HFU: The issue 'Not registered in CLOSED.md (diagnostic, not a lever)' is correct, but the HFU-FIX family it fed is also missing from CLOSED.md (see HFUFIX/HFUFIX2).
- HFU: No other field is wrong. Criterion sha 64a6bf1de68d914ee1d36648c536ed7371793e665316c51c12cf0c5880310cdd re-verified with shasum and matches HFU-criterion.sha256.
- HFUFIX: primary_delta is correct, but it should name the second failing gate: G5b 4/20 health routes in the arm (the same 4 in control, 0 introduced) against a bar of 0 (HFUFIX.md:13).
- HFUFIX: Number '1315 vitest passed (118 files), 7 new tests' cites HFUFIX-build.md:5. That line gives 118 files / 1315 passed, but the count of 7 new tests is in HFUFIX.md:8 (and build l.13 lists 5 + 2 tests).
- HFUFIX: seeds: G2 also ran the real 192-message chat run with generation and the detector on (HFUFIX-build.md:20), so 'otherwise deterministic' applies only to the stubbed G3/G4/G5b replays.
- HFUFIX: Criterion sha 306b227474b6be41fe3e11653a7af735bd7c2674ee05d2bdd7644b06a3807621 re-verified with shasum and matches.
- HFUFIX2: primary_delta leads with the control-gap clause, which passed. The clause that decided the verdict is the absolute G3' rate, which failed. Correct: 'G3' arm 64/76 = 84.2% (bar >= 90%, FAIL) vs control 31/76 = 40.8% (+43.4 points, bar >= 30…
- HFUFIX2: Criterion sha 0b813a9250cd60ae2e05b4d164d5eb83b9b756d036e4e8e36af72bc7d2c9cc5a re-verified with shasum and matches. No other field is wrong.
- HUMANSFT: None of the fields are wrong. Criterion sha 83d4e9d0f70be872c2187cc303790cf54000feacad738fd82a4ee7d1a5658201 re-verified with shasum and matches.
- HUMANSFT: The issues miss the main ledger problem: CLOSED R12 and CLAUDE.md label the 6/20 as 'human CLAPnq'. The 6/20 is the pooled 17 CLAPnq + 3 HAGRID sample, and the flagged ids split 3 CLAPnq (#3, #9, #16) and 3 HAGRID (#18, #19, #20) (REVIEW-2…
- HUMANSFT: judge: the reviewer is 'independent Opus agent (claude-opus-5-5)', strict rubric, 1 run (REVIEW-20h.md:3-4). This matches the record.
- INSTSUBJ: status 'lever-adopted' is correct, but the adoption rests on a gate that passed trivially (0/40 lookups and 0/15 controls finish instant in either arm; l0/lookup2-score.txt:1-2) plus unit tests (QUEUE.md:647).
- INSTSUBJ: n: lookup set #2 was replayed through the stub engine for both arms (l0/L2.cut4.* and l0/L2.instsubj.* traces) and scored once by the coordinator. 'blind_sets_used: []' omits it. The set is not one of the named blind/ sets, but it was 'wri…
- INSTSUBJ: Criterion sha d897731ef51968ca00ed077e902f1ac220ab91a931427969d26c576951f44719 re-verified with shasum and matches.
- JUDGE2: status 'closed' is better stated as 'measurement (calibration only, no GO bar)'. The criterion says 'Calibration only: no GO bar' (JUDGE2-criterion.md:1), and CLOSED.md:11 lists JUDGE2 among the measurements.
- JUDGE2: No numeric field is wrong. Criterion sha 4e825da330f2cc20bfd9975c5d92c779eb6986285d5c9badfa139fa2256ddbf6 re-verified with shasum and matches. The run-1 criterion 2c3ff0eb... cannot be re-verified because its sha was replaced in the .sha25…
- JUDGEVAR: status 'closed' -> should read 'measurement complete, no verdict by design' (JUDGEVAR-criterion.md Power: 'measurement, no verdict'; Stages 4: 'No decision changes'). CLOSED.md:11 lists it among measurements.
- JUDGEVAR: All other fields confirmed: primary_delta matches aggregates/paired-RvsH-s42.opus.json (dRatio 0.0036 CI [-0.0051, 0.0132]; dFloor 0.0049 CI [-0.0066, 0.0172]); n 51 ids x 2 orders = 102 Opus; judge Opus judge.v1 N=4; date 2026-10-11; crit…
- K2HALF: criterion_file: besides QUEUE.md:961, the bar is also embedded in arms/k2half/aggregates/greedy-gate.json ('criterion': 'PASS if mean agreement >= 0.80'); still no .md + .sha256 criterion (criterion_sha_present false is correct).
- K2HALF: All other fields confirmed: means recomputed from greedy-gate.json = 0.184375 prefix / 0.2859375 exact; decode 9.99 → 18.30 (×1.83); prefill 7.80 → 19.63 (×2.52); RSS 7.144 → 6.756 GiB; seed 42, temp 0, 64 tokens; 0 judge calls; date 2026-…
- KVQ8: status 'closed' → 'PASS (non-inferiority) → ADOPT as a device-day candidate; device speed/swap gate still open' (KVQ8-L1.md:3,97,100; QUEUE.md:653; the A15 sweep left it unmeasured, QUEUE.md:695 'q8 KV: no long-prompt completions logged ..…
- KVQ8: n: '180 Opus calls on changed items' is imprecise — KVQ8-L1.md:35: 176 arm calls on changed items (44 items × 2 orders × 2 seeds) + 4 new control calls for lan-exp-007 = 180, 0 failures.
- KVQ8: sets: more precisely 'v0.1 EN (60 run / 57 judged per seed), Android 12 GB profile, cut3-confirm config' (KVQ8-L1.md:8).
- KVQ8: Confirmed: primary_delta −0.0077 CI90 [−0.0232, +0.0062] two-level bootstrap (KVQ8-L1.md:59,63); seeds s44/s45; judge Opus judge.v1-med; date 2026-10-05; criterion sha bae45d0ca281... recomputed = KVQ8-criterion.sha256.
- L1CTL: None. All fields confirmed against L1CTL-haiku55.md and analysis.txt: 40 Haiku calls (20 ids × 2 orders), judge claude-haiku-5-5 judge.v1-low, seed 7, s44 traces, date 2026-10-07, no criterion by design; per-item lower/equal/higher 9/8/3 r…
- LENGTHSHARE: numbers[11] '255 Opus calls' sits at arms/lengthshare/LENGTHSHARE.md:27 ('Opus 51 (capping) + 204 (judge) = 255 calls'), not :17 (l.17 holds only the 18/51 truncation and p10/p50/p90 67/77/80).
- LENGTHSHARE: seeds: '1 (s42; re-judge only)' is true for Part 2 only; Part 1 (dimshare, LENGTHSHARE.md:14) pools 2 seeds for V-para K/H and v0.2 K, s42 for v0.2 H (BAR-TABLE.md:89-92).
- LENGTHSHARE: Missed issue: no EXPOSURES row covers the bench-v02 script read in Part 1 (QUEUE l.905). EXPOSURES.md:114 lists V-para only.
- LENGTHSHARE: Missed issue: the criterion truncates only rows still '> 95 words after one retry' (criterion l.12), but the result truncated rows over 80 words (LENGTHSHARE.md:17, 18/51 truncated).
- LENGTHSHARE: Missed issue: the criterion header says 'frozen 2026-10-10 22:3x', but the criterion and its .sha256 have mtime 22:10:21, and QUEUE l.906 (22:31) already reports results under that sha.
- LOSSMAP: Missed issue: LOSSMAP.md:5 says the 11 hedged v0.2 items are '9 of the 11 ran on the deep tier', but aggregates/lossmap-H-v02-s42.json item paths show 10/11 health-strict and 1 instant, 0 deep-thinking (tier='deep' on 9). DEEPHEDGE later c…
- LOSSMAP: Missed issue: LOSSMAP.md:5 says the thin axis 'co-fires on 49–52 % of items'. In the aggregates, 0.485/0.517 is thin's loss share; the item share is 29/51 (57 %) and 70/110 (64 %).
- LOSSMAP: Missed issue: BACKLOG.md:48 cites 'LOSSMAP: *wrong* = 0.40 of H's V-para loss, 26/51 items'. 0.40 is the primary-bucket share of 16 items; 26 is the wrong_fact axis count (share 0.59).
- LOSSMAP: The per-path addendum is dated 2026-10-12 08:56 (QUEUE l.953), not the arm date 2026-10-11.
- LOSSMAP: Aggregates now show gateway_cost_usd 0.0 with all items cached (re-run from cache for the per-path addendum). The '322 jev requests [usage detail removed]' figure is the original pass and is not reproducible from the current aggregates.
- LOCALGATE: blind_sets_used [] is wrong. The 500+500 sampled requests were rebuilt from the jev caches of wikifull A0, wikisection/anywhere and packcond, whose states carry rationale_1/rationale_2 from the Opus judgments on V-para and bench-v02…
- LOCALGATE: date: the Qwen part is 2026-10-12 (QUEUE l.988, 23:51), but the arm closed 2026-10-13 01:51 after Laya (QUEUE l.995; BACKLOG.md:41 'closed 10-13').
- LOCALGATE: The issue 'pass rule stated only in the result and QUEUE l.988' is incomplete. The rule was pre-registered in BACKLOG.md:41 ('PASS if agreement ≥ 0.90 and false-positive rate on jev-negatives ≤ 0.05', '≥ 500 cached requests') and is stored…
- LOCALGATE: numbers[8] layaB AUC 0.67 / 0.63 spans LOCALGATE.md:52-53, not only :52. Likewise layaA spans :50-51.
- LOCALGATE: exposures_status should be missing-row: no EXPOSURES row names LOCALGATE.
- LOCALGATE: QUEUE l.989 also mentions the arm (Laya install and background start, 23:55).
- LORA-DIAG: status 'parked' is imprecise. It is a draft never frozen or run (no .sha256, no result). Its gating data line was closed (QUEUE l.789 'Coordinator closes the data line (reversible; loradiag stays draft)'; CLOSED.md:27 R12). The LoRA idea w…
- LORA-DIAG: The issue 'effectively dead unless the data bar is re-registered' is outdated. The data bar was re-registered under SFT4B (BACKLOG.md:26: 'v3 data gates (addendum 2): ... strict review ≤ 6/20'), so LORA-DIAG is superseded, not merely dorma…
- LORA-DIAG: sets: besides 'v0.1 EN 57 (DEEPREAD R450 protocol)', the draft plans a 100-example held-out grounded-reading set (seed 49, l.14) and a safety pass on '12 safety-track items + 10 v0.1 danger/health items' (l.22). None is a blind set.
- LORA-DIAG: queue_rows were not given: LORA-DIAG / 'LoRA diagnostic' appears at QUEUE l.767, 770, 776, 777, 789.
- MP4B: criterion_sha_present: true is right in substance, but there is no .sha256 sibling; it is DEEPITER-criterion.sha256.ref (432fddf9…), which matches shasum of arms/deepiter/DEEPITER-criterion.md
- MP4B: '×4' cost: MP4B.md:3 ties ×4 to time ('Cost ×4: p50 26.3 s vs ≈ 6 s') and MP4B.md:14 calls it 'the call count', while MP4B.md:11 gives 5 generation events/item vs 1; the record's 'cost (call count)' label inherits this internal ambiguity
- NAMEDSLOT: primary_delta 'n/a' is defensible but omits the deciding numbers: gate G2c 15/60 vs bar ≤ 12 FAIL; recall@5 0.333 → 0.4103 (PASS)
- NUMCHECK: criterion_file: the gate bars were also stated before the run in BACKLOG.md:60 ('≥ 4/16 V-para wrong items whose wrong number/date is covered by the FACTS table (answer-side match), and 0 rewrites on 20 correct answers'), not only inside N…
- NUMCHECK: All other fields confirmed (status closed / FAIL at 0-call gate, n 16+17 wrong + top-20 non-wrong per set, seeds 1 arm H s42, judge none (jev, threshold 0.6), sets V-para + v0.2, date 2026-10-12)
- OPUSSHARD: None found: criterion sha b78c9550ed1e15a6f7b0a2b0b0a673e0fb9df6f05473363276bcf0b929dea4d9 recomputed with shasum -a 256 = OPUSSHARD-criterion.sha256 = sha cited in OPUSSHARD.md:2; analysis-N4.json confirms dRatio -0.0135, CI [-0.0252, -0.…
- ORACLE-ST: Patch sha mismatch is FALSE: oracle.vs-cut7.patch.sha256 holds 'dbecafcd5030aa3a2edd05bde715c739a8a8c6576008110301dbc0ab3a344e24  <abs path>/oracle.vs-cut7.patch' and shasum -a 256 of the patch = dbecafcd5030aa3a2edd05bde715c739a8a8c657600…
- ORACLE-ST: 'aggregates/ empty' is FALSE: aggregates/oracle-st.json exists (21:25) with gen.oracleadd n 60, fact_chunk_text_in_final_prompt 57, oracle:add-already-kept 3, oracleonly n 0, judge {}
- ORACLE-ST: 'runs/ holds only *.requests.jsonl and stage0 traces' is FALSE: runs/ holds ORACLE-ADD traces for 7 of 9 packs (travel, ethereum, bitcoin, health, outdoors, firstaid 20 rows each; medlineplus 18 in progress) = 138/180 rows at 2026-10-13 21…
- ORACLE-ST: Stage 0 passed: logs/stage0_check.txt ends 'STAGE0 PASS' (3 items: OFF==S on all fields, appended block byte-equal to the pack chunk); the empty logs/stage0.log is not the result file
- ORACLE-ST: 'off3' cells are the stage-0 3-item OFF byte-identity check (criterion line 26), as presumed
- ORACLE-ST: Criterion sha 4c4651b1aaea3400533077462e885ced3b7837d9cdf3f9d80a04c6d30b594635 recomputed = .sha256 (bare hash, no filename) — confirmed
- ORACLE-ST: logs/gen_chain.log shows firstaid failed twice (rc=1, 21:36 and 21:44, disk wait) before rc=0 at 21:48, and a 'generation stopped; abort' line at 21:48 although medlineplus generation started 21:48:35 and traces were still being written at…
- PACKCOND-P1: status 'closed' → it is a measurement (no criterion, no verdict rule); correct to 'measurement (done 2026-10-12 20:14; Addendum 1 scale correction 21:0x)'
- PACKCOND-P1: All numbers confirmed against PACKCOND-P1.md lines 3, 11-12, 23, 34, 37, 44-50; pooled buckets 10/15/18/11/10 recomputed from the per-cell table (0+1+6+3, 1+1+7+6, 3+2+7+6, 2+1+5+3, 0+1+7+2)
- PACKCOND-P1: Addendum 1 adds K not-in-pack 90 above_min 0.378 (0.326–0.430) and K all 0.397 (0.347–0.447) which the record omits (not an error)
- PACKCOND-P2: status 'closed' → measurement (done 2026-10-12 20:25); no criterion or verdict rule
- PACKCOND-P2: All numbers confirmed: union 5 / overlap 1 → +4 → 10/51 V-para; union 53 / overlap 23 → +30 → 62/110 v0.2; top100k 47 (27 new) → 32 + 27 = 59 'with it alone'; F1/F2 28 (60%) / 23 (49%) of 47; shard07 9 (38%) / 5 (21%) of 24; share 0.98; ad…
- P4 packGround (PACKCOND P4 step 0): None in the numbers: 14/32 (off 11/32, bar 16), control 6/20 (bar 4), H32 changed 13/32, empty/slots 11/48 → 6/63, v0.1 gold 13 → 14, 15 not in raw (14 not in top-20 pool), ceiling 16/32, differential 8/8 all confirmed in P4-GATE.md:3,8,13…
- P4 packGround (PACKCOND P4 step 0): packground.vs-dt512.patch sha recomputed cb7f239aac27f6b09aa002fecb28b0009e89784386ef51ccd998dd01881e53fc = .sha256 — confirmed
- P4 packGround (PACKCOND P4 step 0): criterion: PACKCOND-PLAN-2026-10-12.md:25 planned P4 as a '(frozen criterion)' arm, but no criterion file exists; the gate bars (≥ 16/32, ≤ 4/20) first appear in the result (P4-GATE.md:3) and QUEUE.md:969, i.e. not sha-frozen before the re…
- PACKDENSE: None in the numbers: criterion sha e2815dd824941fd1435446573fda162d32f09f45fef95093e465900a5c06a20c recomputed = .sha256; G1 21/32 (bar 22, baseline 17), ceiling 22 at M = 5, declared M 2 / floor 0.60 / 1 passage, noise p50 0.687 vs target…
- PACKDENSE: seeds: criterion planned 2 seeds (s42 + s43) for stages 1-3; step 0 is a replay/simulation (n/a) — record correct
- PACKDENSE: Protocol: criterion stage 0 requires 'Gate replay (the declared variant, once)' (PACKDENSE-criterion.md:30-35); the gate replay was not run and FAIL was declared by simulation projection (P4B-GATE.md:13), and the criterion's output packden…
- SECTIONHIT: None in the numbers: 12/32 article kept, 7/32 section kept, 6/12, 3/12, 0 additional, 19/32 rank ≤ 3, 105/105 confirmed (SECTIONHIT.md:3,7,19,21,25)
- SECTIONHIT: Add: SECTIONHIT.md:26 also states 'at most 2/12 reading-bucket items (ranks 5 and 6)' as the ceiling of any selection lever; the ledgers quote this (≤ 2/12) rather than the '0 additional' of the two tested rules
- SECTIONHIT: Article in raw is 19/32 under SECTIONHIT's definition (SECTIONHIT.md:19) vs 17/32 in P1/P4 (p4-diag definition) — same definitional gap as kept 12 vs 11, as the record notes
- DENSECHUNK: Issue 'bar value 12 only appears in D0' is wrong: the gate frozen in QUEUE.md:977 reads 'PASS if an F0 hit chunk is in the pack's dense top-12 at cos ≥ 0.55 on ≥ 12/32 in-pack items AND … F0 article in raw6 on ≥ 22/32 with the resolvable v…
- DENSECHUNK: All numbers confirmed: 23/32 part 1, ranks 9/16/21/23, fused 22/32 (baseline 19; 21 under the p4 definition), dense-first2 23/32, resolvable gold fused 6/9 (7), churn 85–107/107, +212.6 MB (+61 %), 4.2–10.5 s, two-stage 0.27–0.67 s keeping…
- DENSECHUNK: Status: 'parked' in the dir is consistent with BACKLOG.md:42 and CLAUDE.md ('DENSECHUNK parked'); the line was later carried by DENSECHUNK-ST/ST2, which CLOSED R46 says 'supersedes DENSECHUNK D0 parked' — and R46 itself is 'not decided at …
- HEALTHQ: None in the numbers (17/18, 0/18, 6/18 match QUEUE.md:975); add that the tool tools/healthq_check.py reads blind/bench-v02/live/v0.2/questions.v02-new.jsonl and blind/bench-v02/runs-packcond/p4b-v02.jsonl (docstring lines 4, 8), i.e. a scr…
- HEALTHQ: Gate per BACKLOG.md:21 is '≥ 3/18 AND the F0/gold article reaches raw on ≥ 3 when the destination is kept' — the record quotes only the first part
- HEALTHQ: Verdict also in BACKLOG.md:21 and HANDOFF-2026-10-13.md:21, not only QUEUE
- PACKROUTE: No material field errors. criterion seeds line says '1 (greedy 4B…)' (PACKROUTE-criterion.md:18) but step 0 was 0-LLM, so 'n/a (0-LLM replays)' is right for what ran; judge 'none' is right (planned Haiku stage never ran).
- PACKROUTE: closed_row_cited 'none' is right for STEP0.md, but CLOSED.md:72 (R48) covers this arm together with PACKROUTE-2.
- PACKROUTE-2: issues bullet: the criterion's outputs are ACCURACY.md, STEP0.md and PACKROUTE2.md (PACKROUTE2-criterion.md:41). ACCURACY.md exists; only STEP0.md and PACKROUTE2.md are missing.
- PACKROUTE-2: n: ≈ 350 calls per wording, so ≈ 700 local 4B calls in total (QUEUE:1028, CLOSED.md:72). EXPOSURES.md:154 counts ≈ 220 of them on v0.2 text.
- SELFTEST-SCORES: status 'closed' → measurement, done (no criterion, no verdict rule; numbers used for cards). CLOSED.md lists measurements outside the table.
- SELFTEST-SCORES: judge: Haiku 5.5-low N = 4 both orders is primary; side check with a local Qwen3.6-35B-A3B judge on qa-travel-se only (SELFTEST-SCORES.md:26-29).
- SELFTEST-DEEP: status 'closed' → measurement, done (the criterion says 'measurement, no verdict rule', SELFTEST-DEEP-criterion.md:1).
- SELFTEST-DEEP: Arm H is cut 6 + Qwen3.6-35B-A3B + thinking 512 (criterion:7/10), while the 'vs 4B' reference rows are 4B cut 7 (criterion:12). The deep-vs-4B Δ crosses engine cuts, and the record does not say so.
- WAVE3: status 'lever-adopted' is wrong. WAVE3 is a pack build/probe/publish job: neither pack's self-test Δ clears zero (WAVE3.md:2), and QUEUE treats it as product ('11 packs on the hub'), not a bar lever. Corrected: done (product; 2 packs publi…
- WAVE3: primary_delta is a Haiku L1 measurement with CIs straddling 0. At L2 (PACKS-L2.md:15) the pooled wave-3 S − OFF is +0.045 (+0.007…+0.087).
- T-K4a: issues: the frozen rule lives in PACK-CATALOGUE-2026-10-12.md:44 (T-K4: 'kept-slot share ≤ 0.40, gold not lower'), confirmed.
- T-K4a: exposure not flagged by the extractor: T-K4a ran script-only replays on bench-v02 (outputs under blind/bench-v02/runs-packs/), and EXPOSURES.md has no row for it.
- PACKS-L2: status 'running' is wrong. PACKS-L2.md now exists (written 21:11) with verdicts 'S − OFF CONFIRMED (+0.042, CI low +0.024); P − S COST CONFIRMED (−0.019, CI high −0.003); X − P OPTIONAL (R49 unchanged: SE CI low −0.008)'. Corrected: closed.
- PACKS-L2: result_file 'none' → arms/packs-l2/PACKS-L2.md.
- PACKS-L2: verdict_text 'none yet' → as quoted above (PACKS-L2.md:3).
- PACKS-L2: primary_delta 'n/a' → S − OFF +0.042 (+0.024…+0.062) Opus pooled 180 (P − S −0.019 (−0.035…−0.003); X − P +0.004 (−0.010…+0.019)).
- PACKS-L2: date 'unknown' → 2026-10-13 (criterion frozen 20:4x, result 21:10, QUEUE:1073 at 21:11).
- PACKS-L2: n: 1,240 Opus calls used (31 sets × 40), under the cap of 1,300.
- PACKS-L2: issues: 'logs show P/X and wave-3 sets still being judged' and 'no verdict is written' are stale. All 31 sets completed and aggregates p_s.json, x_p.json, wave3_s_off.json and x_s.json exist.
- PARJUDGE: status 'tooling' is under-specified: the arm was adopted as protocol (arms/L1-PROTOCOL.md:12 addendum 2026-10-07; RULE-CHANGES.md:10 row 4) with default N = 4, not the N = 8 the result recommends; corrected_status reflects this.
- PARJUDGE: numbers row '0' (429/overloaded and failures/reruns) is right, but N = 8 had 1 timeout >60 s (77.7 s call, ok): analysis.json N8.timeoutsOver60s = 1; PARJUDGE.md:9 'timeouts (>60 s)' column = '1 slow call (77.7 s, ok)'.
- PARJUDGE: No other field errors: criterion sha f47b3bb5… re-hashed and matches; judge claude-haiku-5-5 judge.v1-low, seed 7, 114 calls/level, v0.1 deep35-R450, date 2026-10-07 all confirmed in PARJUDGE.md:1-2 and analysis.json.
- PROMPTDIET: No field errors found. status closed, primary_delta −125.72 (bar −150, FAIL by 24.3), n 100 traces (s44 + s45), judge none, set v0.1, date 2026-10-05, criterion sha f8eef6f0… (re-hashed, matches) all confirmed against PROMPTDIET.md:3-44 an…
- PROMPTDIET: Clarification to the reviewer-cost number: promptdiet-REVIEW.md:34 'about +29 tokens' also says the 150 target 'would still be reachable'; QUEUE l.613 instead computed 'net −121 < −150' from the same estimate (see discrepancies).
- Q35: seeds: 'seed 44 (control seed 42)' refers to generation; the judge seed is 7 (all 114 rows in runs/q35-4b-s44.judgments.jsonl carry seed 7). Corrected: 'generation seed 44 (stored control seed 42); judge seed 7; 1 seed'.
- Q35: judge: confirmed claude-opus-5-5 on 114/114 judgment rows, effort medium (judge.v1-med) per Q35-screen.md:9 — record is correct; noting that CLOSED R1 says 'Opus judge.v1'.
- Q35: No other field errors: ratio 0.437, bar 0.517, baseline 0.487, Δ −0.050, 57 items / 114 calls, v0.1 EN closed-book, date 2026-10-05, criterion sha 187bbae9… (re-hashed, matches) confirmed.
- PROBES: date 'unknown' → 2026-10-04: file mtimes Oct 4 11:25-11:45 and the consuming results are logged in the QUEUE cut3-dev block dated 2026-10-04 (QUEUE l.539/542 headers; results l.549-552).
- PROBES: n: line counts confirmed, plus label composition verified from the files: arithmetic.probes 30 pos / 15 neg, arithmetic.heldout 32 pos / 18 neg, water-safety.probes 22 pos / 18 neg, water-safety.heldout 25 pos / 25 neg, vg-questions 30 unl…
- QUANTCEIL: status 'not-decided' -> the arm is closed with verdict NO ('NO — not detected at MDE 0.03', QUANTCEIL.md:3); the criterion's own label for \|Δ\| < 0.03 with CI through 0 is 'not decided at MDE' (QUANTCEIL-criterion.md:30), so the correct s…
- QUANTCEIL: numbers: '+0.087 (+0.035…+0.150, n 23)' is labelled 'H's LOSSMAP wrong bucket', but n 23 is the wrong_fact AXIS (aggregates/bucket-delta-v02-s42.opus.txt:5 'wrong_fact=True n= 23 dRatio=+0.087 CI=(0.035, 0.15)'); the LOSSMAP primary wrong …
- QUANTCEIL: numbers: V-para pooled '+0.018 (−0.015…+0.053, n 26)' n 26 is the axis count; the s42 '+0.079' quoted beside it is the primary bucket (n 16, QUEUE.md:947), so the two figures mix the axis and the bucket.
- QUANTCEIL: sets: smoke listed as 'v0.1 (smoke)' following the table (QUANTCEIL.md:9), but the same file's exposure line (QUANTCEIL.md:20 'v0.2 smoke 3'), EXPOSURES.md:128 and QUEUE.md:940 (blind/bench-v02/runs-quantceil/qc-smoke-Q2.traces.jsonl) put …
- QUANTCEIL: n: V-para generations are 58 × 2 seeds, of which 51 ids × 2 judged (QUANTCEIL.md:20, EXPOSURES.md:129).
- QUANTCEIL: issue 'V-para s43 lacks floor-adjusted values' is resolvable: aggregates/L2-Q-2seed.opus.json seed 43 gives Q floorAdj 0.4329 vs H 0.4603.
- RATIONALEPASS: status 'closed' is a label for a measurement arm (no LEVER/NO verdict); more precise: 'done (measurement; O-5 met, O-4/O-8/T3 not met)' as BACKLOG.md:65 and HANDOFF-2026-10-12.md:32 record it.
- RATIONALEPASS: No numeric extraction errors found; all quoted values match RATIONALEPASS.md lines 2, 6, 10-13, 16, 18, 20, 21.
- RETHURT: No field errors found: status, primary_delta −0.031 (−0.072…+0.011), n 57, seeds (deep35 engine 42/43, closed-book 42, 4B engine 42/43/44), judge (judge.v1 claude-opus-5-5, existing rows, 0 calls), set v0.1 EN 57, date 2026-10-07 and crite…
- SC-V2-S5PRIME (sc-fresh3): blind_sets_used [] -> should list 'sc-fresh3' (a blind set written by a separate blind writer, scored once, status 'burnt' in EXPOSURES.md:87), although it is not one of the bench-v02/V-para/health/chat/es/meta sets.
- SC-V2-S5PRIME (sc-fresh3): No numeric errors: 21/25, 21/25, 5 on 50, 12/25, counts 25/25/50 and items sha 5056abfd…f7f confirmed (shasum of arms/sc-fresh3/items.jsonl = 5056abfd9e2db9b3575ac361d2abba275b85625c5e45a217ce09bb458cb80f7f, computed without reading conten…
- SC-V3-S5SECOND (SC v3 trigger S5″ on sc…: status 'closed' is right on the arm verdict ('S5″ FAIL', sc-fresh4-S5second-result.txt:6), but the ledger outcome is 'PARKED for the bounty' (QUEUE.md:562) and 'Killed/parked today: ... SC water card (3 rounds)' (QUEUE.md:578). Better stat…
- SC-V3-S5SECOND (SC v3 trigger S5″ on sc…: Issue 'second .sha256 line for tools/sc-fresh4.mts (726cf47d…) not verified' is now verified: shasum -a 256 arms/tools/sc-fresh4.mts = 726cf47dbe0d65c93ee6c8288b2517aef1f0277adfb8bc5bd77146b379a676f3, which matches. The criterion sha 4aa47…
- SC-V3-S5SECOND (SC v3 trigger S5″ on sc…: blind_sets_used note 'not in the standard blind/ list' is incomplete: EXPOSURES.md:87 has a row '\| sc-fresh3 / sc-fresh4 \| 1 scoring each \| burnt \| QUEUE l.554–562 \|'.
- SC-V3-S5SECOND (SC v3 trigger S5″ on sc…: Date: 2026-10-04 is correct. The better QUEUE evidence is l.578 ('State after the 2026-10-04 session ... SC water card (3 rounds)'). l.560–562 sit under the 2026-10-03 header at l.461 only because of how the log is laid out.
- SEEDGEN: The record misses the addendum at SEEDGEN.md:54 (2026-10-13 22:5x, PIPELINE-AUDIT F8 fix): 'the reported "56/59 same-prompt identical" becomes 32/34 same-prompt (LLM items) + 23/23 no-LLM identical; kept-unchanged goes from 56/102 to 55/60…
- SEEDGEN: The issues list should name PIPELINE-AUDIT-2026-10-13 F8 ('same_answer.py pairs on prompt LENGTH, not identity', PIPELINE-AUDIT-2026-10-13.md:13) and its fix (QUEUE.md:1081).
- SEEDGEN: Stray duplicate files are confirmed: runs/'same-A1 A2-.json', 'same-A1 B1-.json', 'same-A2 B2-.json', 'same-B1 B2-.json' sit beside the hyphenated copies.
- SEEDGEN: The other fields check out against SEEDGEN.md: date 2026-10-13, seed 42, 20 requests / 15 LLM calls × 4 runs (+ the original run as a 5th pairing), 0 judge calls, no criterion file.
- SEEDSPEC (T7): Set B pattern '22 / 5 / 9 / 15' (SEEDSPEC.md:12) is pattern_all. Among the 36 wrong-any items, aggregates/seedspec-H-vpara.json gives pattern_of_wrong_any {stable_wrong 21, seed_specific 5, mixed 9, not_wrong 1}: one item labelled stable_w…
- SEEDSPEC (T7): Additional set B numbers the record left out: wrong in 1/2/3 seeds = 12 / 14 / 10; same_wrong_fact among multi-seed-wrong = 12/24 = 50 % (SEEDSPEC.md:8,10).
- SEEDSPEC (T7): Set A '24/26 wrong on s42' is correct per jev (aggregate wrong_per_seed s42 24), yet n_wrong_any = 26. So 2 LOSSMAP-wrong items are jev-wrong only on s43/s44. This is a LOSSMAP vs jev disagreement, as the record states.
- SEEDSPEC (T7): The other fields are confirmed: jev cost [usage detail removed] (aggregate gateway_cost_usd 0.00406), threshold 0.6, 51 requests, seeds s42/s43/s44, verdict 'T7 FAILS', no criterion .sha256.
- SEEDVAR: status 'tooling' → should be 'measurement (no verdict rule)'. The criterion title says 'measurement only, no verdict rule', and CLOSED.md:11 lists SEEDVAR among measurements.
- SEEDVAR: The record's issues do not flag the missing EXPOSURES bench-v02 row: SEEDVAR script-read the existing v0.2 Opus rows (SEEDVAR.md:20-25; QUEUE.md:873), but EXPOSURES.md has only the V-para row (l.110).
- SEEDVAR: The record's issues do not flag that the EXPOSURES.md:14 V-para Opus tally ('DT512-H 2') omits the SEEDVAR s44 Opus pass, even though the same row's generation tally says 'DT512 3 (incl. SEEDVAR s44)'.
- SEEDVAR: The other fields are confirmed: criterion sha f7196323ac5f28e119a08cc609be1ed2032706059abf8f8ea75a7c8be3b0feb4 (shasum = .sha256 = SEEDVAR.md:1), date 2026-10-10, 102 Opus calls, 51 judged / 58 generated, seeds 3 for H and 2 for T/D/K, jud…
- SFT4B: status 'parked' is stale: arms/sft4b/STAGE1.md:3 says 'Status: WAITING FOR v3 DATA ... Steps 1–5 are done. Steps 7–10 tooling is built and checked end to end on the smoke adapter ... Step 6 has not started.' The arm is open and in progress…
- SFT4B: result_file misses arms/sft4b/STAGE1.md (exists, 21:42). It should read 'STAGE0.md (stage 0 + v2 targets) + STAGE1.md (stage-1 environment/parity, training not started); no SFT4B.md'.
- SFT4B: criterion_file misses SFT4B-criterion-addendum-2.md (frozen; sha 653745c73f9ab2b4098b292dbe21440511a5c90b0cb9e2dc3ce77c415ea54cd7, which matches its .sha256 by my shasum). Addendum 2 replaces the training data with v3 (distractor-rich) and…
- SFT4B: numbers: expected_delta '+0.04' (SFT4B-criterion.md:16) is superseded by addendum 2 'expected_delta: +0.02 raw X − C on the 180 (range +0.00…+0.04)'. The record should carry both values.
- SFT4B: n field '1,200 train / 100 hold-out examples built' is only v1. v2 = train.v2 1,000 (sha a7b7b1b5…) + holdout.v2 84 (sha e49e52c9…), STAGE0.md:46,48, and was used only for the smoke run. v3 (≥ 1,000 kept required, same 84 hold-out articles…
- SFT4B: Issue 'no .md documents v2 datasets or their shas' is false: STAGE0.md:41-51 ('v2 targets') documents v2 with shas a7b7b1b5… / e49e52c9…, and STAGE1.md 'Run notes' repeats them. The training-set ambiguity is resolved: v2 = smoke only, v3 =…
- SFT4B: Issue 'not launched per files' / verdict_text 'stage 1 not yet run' is wrong: stage-1 steps 1–5 and 7–10 ran (STAGE1.md:3-31); only step 6 (training) and step 11 have not.
- SFT4B: Issue 'Addendum 1 replaces the frozen ... recipe' is correct, but the record misses that STAGE1.md reports 600 it at batch 4 = 2.4 epochs on 1,000 v2 examples, while addendum 1 restates '2 epochs = 600 iterations at batch 4'. The epoch cou…
- SFT4B: Criterion sha check confirmed: 5853b8ea… and 1730f4f9… match by my shasum.
- SPECDEC: None material. Criterion sha confirmed: 66361511046c0242a91dc7400b2bb4ee989025e62545b52dee564618b31b0cbd matches; the .sha256 records path 'arms/specdec/SPECDEC-criterion.md'.
- SPECDEC: Minor: n is the 60 v0.1 EN s44 items, of which 50 are model-path prompts. The 10 non-model items count as identical by construction for G1 (SPECDEC.md:54, :74). The record states this correctly.
- SPEEDPACK: date: the criterion was frozen 2026-10-05 and the run took place 23:53-00:22 (SPEEDPACK-L1.md:1 '2026-10-05/06', :24). The record's '2026-10-06' should read '2026-10-05/06' (CLOSED R7 also says '10-05/06').
- SPEEDPACK: closed_row_cited 'none' is accurate for the result file, but CLOSED R7 (PROMPTDIET -> SPEEDPACK L1) covers the arm, as the record's own issue notes.
- SPEEDPACK: Criterion and patch shas confirmed: c0bceaf62e4daa79efbd23df8f774de4391fbf2e3c5f01095f05f6382917d4c4 matches; patches bb3dbde1… / caeaf5ce… as cited in SPEEDPACK-L1.md:12,81.
- STACK: closed_row_cited 'none' holds for GATE.md, but CLOSED R49 covers the step-0 numbers ('step-0 replays (article kept 46 → 72, chunk 31 → 36, kit lost contexts 4 → 0)').
- STACK: Shas confirmed: STACK-criterion 56ed7ccf05092584b598a6e45352a9104dfbc31f62f2b723d648a6c9c84abc6d matches; stack.vs-cut7.patch 0049d3c32a51231d4d42aa28f56772ff8c08efd846493cd3b630f50c355ffc8c matches; gate.json carries criterion_sha256.
- STACK: Otherwise all fields confirmed against GATE.md and STACK-criterion.md.
- STACK-2: None material. STACK2-criterion sha e875d463485a8cb55216e48f89fc0176bb1afb0650e7bb5e4cb5ea915d625fcf matches .sha256 and aggregates/stack.json criterion_sha256.
- STACK-2: status 'not-decided' is correct ('not decided at MDE 0.03'), but the pack stack is CLOSED by that outcome under the frozen rule (STACK2-criterion:26; CLOSED R49). The effective status is closed / not decided at MDE 0.03.
- SYNTHDEEP: criterion_file quote is truncated: LOOP-PROGRAM-2026-10-11.md:37 reads 'replay: both sides in the prompt on ≥ 5 more comparison items (v0.1 lan-cmp-*)'. The '(v0.1 lan-cmp-*)' scope is dropped, and it matters because the only curated-kit g…
- SYNTHDEEP: The issue 'SYNTHDEEP.md table says kept lists changed = 2 (curated) vs REPLAY 4/60' should not stay an open ambiguity. aggregates/replay-v01.json items_kept_changed_on_vs_off = ['lan-cmp-001','lan-cmp-002','vit-sci-002','lan-cmp-005'], whi…
- SYNTHDEEP: The '5 of 7' number is worded two ways inside the arm. SYNTHDEEP.md:3 says the kit has 'no article for at least one side'; REPLAY-v01.md:2 says 'no article for either side (pinned-0-0 or 0-1)'. The REPLAY table shows 4× pinned-0-0 plus vit…
- SYNTHDEEP: n: the comparison set in aggregates is n_items 8 (7 fired; lan-cmp-003 has sides-0). Gold-loss and off-identity checks cover all 60 v0.1 items. The record's n is otherwise right.
- T1-DEEP35: blind_sets_used ['V-para','bench-v02'] is wrong. The arm never ran, so it used no blind set; those sets are proposed only. Correction: [].
- T1-DEEP35: status 'proposed' is incomplete. DEEPVPARA-criterion.md:3 says 'Supersedes the T1-deep35 draft (arms/t1deep35) in staging and judge'. Correction: superseded draft (never authorised, never run), replaced by DEEPVPARA (frozen 2026-10-08).
- T1-DEEP35: The issue 'this file was never updated or marked superseded' is half right. The draft itself carries no marker, but the superseding criterion (DEEPVPARA-criterion.md:3) does record it.
- T1-DEEP35: n is from T1-DEEP35-DRAFT.md:15: V-para '51 judged items' and v0.2 '110 EN'. That is correct as a proposal.
- THINK4B: None material on the fields. Re-verified: status closed / NO (near-lever); primary_delta +0.026 (−0.013…+0.068); n 51 judged (58 generated) + slices 20; seeds s42 only (s43 requests 82befe13… prepared, not run); judges Haiku 5.5-low L1 + O…
- THINK4B: The stage-5 ambiguity issue can be narrowed. Criterion line 16 reads 'Haiku vs C: same clause → Opus judge.v1 N = 4 on s42, then seed 43 ...'. 'Same clause' points to the stage-4 continue rule (Δ ≥ +0.03), so the stop after s42 is a defens…
- THINK4B: An extra issue, an exposure-ledger summary gap, is missing: the EXPOSURES.md:14 V-para summary row does not list THINK4B's Opus or Haiku passes in its judge totals, although per-run row 106 exists.
- THINK4B-V02: None material. Re-verified: status closed NO; primary_delta +0.009 (−0.015…+0.035); n 110 + slice 20; seed s42; judge Haiku 5.5-low only (Opus 0); set bench-v02; date 2026-10-10; criterion sha present and matching.
- THINK4B-V02: The issue 'Verdict rests on Haiku only ... an extrapolation not measured' overstates the problem. Under the frozen rule (THINK4B-V02-criterion.md:11), Haiku Δ +0.009 is below the +0.02 near-miss threshold, so the rule stops at L1 and NO is…
- THREADS2: The issue 'No QUEUE row names THREADS2 (grep found only the web-sweep line l.778)' contradicts itself. QUEUE.md:778 does name the arm: '**A2 THREADS2 dormant** (arms/threads2/THREADS2-DORMANT.md; needs a device)'. Correction: QUEUE row 778…
- THREADS2: The extractor missed that HANDOFF-2026-10-10.md:28 claims 'criterion already written'. No criterion file exists; the closest text is the unfrozen A2 hypothesis in WEB-SWEEP-2026-10-07.md:80-89 (decode ×≥ 1.3, prefill loss ≤ 15 %, net p50 ≤…
- VENUEGPS: seeds: '42 (s43 not run, no pass)' covers only the location-on run. The cause analysis (step 1) read the cut 6 traces of BOTH s42 and s43 (VENUEGPS.md:2 'both seeds', :7 table, :47 'runs-cut6 s42/s43 traces'). Better: 'location run s42 onl…
- VENUEGPS: n: the gate used 4 run variants (vg-{off,offnv,orig,on}-s42, VENUEGPS.md:48), not one run of 7+5
- VENUEGPS-2: status 'lever-adopted' is acceptable only in the narrow sense the record notes: no engine change. What was adopted is claim wording plus the 12 GB config tile download (VENUEGPS-2.md:31-32), and the runner option was committed in boar-eval…
- VG-PROBE-Q: judge 'none': the set has no judge of its own, but its consuming gate VG-S used an independent Opus reviewer to label every fire (vg-S-criterion.md:6 'an independent Opus reviewer labels every FIRE'). Better: 'none for the set; VG-S fires …
- VG-PROBE-Q: blind_sets_used []: the set was itself a fresh blind-written set when VG-S ran (vg-S-criterion.md:3 'blind writer'; EXPOSURES.md:88 lists it under 'Other blind sets'). It is not one of the blind/ sets, but its exposure is ledgered
- VG-PROBE-Q2: judge 'none': the consuming gate VG-S2 used an independent Opus reviewer (vg4-S2-criterion.md:6; vg4-S2-REVIEW.md:4 'Reviewer: Opus 5.5 (independent…)'). Better: 'none for the set; VG-S2 fires labelled by an independent Opus 5.5 reviewer'
- VG-PROBE-Q2: blind_sets_used []: the set was a fresh blind-written set at gate time (vg4-S2-criterion.md:3) and is ledgered under 'Other blind sets' with status 'burnt' (EXPOSURES.md:88)
- VITALPACK-DEEP: question: the step-0 control is the base-kit retrieval replay (crypto + wikivoyage + seed corpus, tree wt/cut7 6d0b93b1 with deep retrieval settings, arms/deepcovfb/replay-base.jsonl reused for v0.1; VITALPACK-criterion.md:11-12), not 'con…
- VITALPACK-DEEP: issues: 'Result file does not cite CLOSED row number' is true but immaterial; all other fields (status closed, n, seeds n/a, judge none, sets, date 2026-10-11, sha 40191652… = shasum of VITALPACK-criterion.md) confirmed
- VITALPACK-ADD: status 'not-decided' → the arm is effectively closed: header 'Verdict: NO at the slice; full set not detected at MDE 0.025' (VITALADD.md:3), addendum 'H6 stays not detected at L2 … stage 4 … is not run' (:19), ledgers treat it as closed (B…
- VITALPACK-ADD: date: header dated 2026-10-12 (criterion frozen 2026-10-11, smoke 10-11, slice/full judged 10-12 00:30–00:39); 2026-10-13 is only the stage-3 L2 addendum — use '2026-10-11…13'
- VITALPACK-ADD: n: 'smoke 3 v0.1' is right per criterion :26, but VITALADD.md:15 itself says 'Exposure: v0.2 smoke 3' (internal inconsistency in the arm file, not an extractor error)
- VITALPACK-ADD: issue 'No CLOSED.md row for VITALADD' confirmed; CLOSED.md:10 only lists VITALPACK-ADD as a reopened family
- VITALPACK-ADD: shas confirmed by shasum: criterion 7c9f7e65…3542, smoke addendum d677d920…f72e, vitaladd.vs-dt512.patch f7a1f394…80bf
- WIKIFULL-STAGE-A: status 'closed' → stage A is an intermediate stage: its MARGINAL band triggers stage B by rule (WIKIFULL-REOPEN-criterion.md:30 'MARGINAL 7–13: reported; stage B runs'); the decision is the pooled A+B count (closed jointly under R45). Stat…
- WIKIFULL-STAGE-A: all numbers confirmed against STAGE-A.md:3 and A0-shard07.md:9-10; criterion sha ee81ad30… matches shasum
- WIKIFULL-STAGE-A: issue 'stray tools/ikifull_gate.py' confirmed by ls
- WIKIFULL-REOPEN: none material: status closed (per R45), n 34 (+78 dev), seeds n/a, judge none, sets, date 2026-10-13, sha ee81ad30… all confirmed against STAGE-B.md and the criterion
- WIKIFULL-REOPEN: issue 'STAGE-B says EXPOSURES row + QUEUE entry by coordinator; QUEUE l.994 has the entry' → also EXPOSURES row 146 exists
- WIKISECTION: closed_row_cited 'none' is correct for the result file, but a CLOSED row exists: R39 (CLOSED.md:63)
- WIKISECTION: criterion_file: the 40 % bar is no longer visible in BACKLOG §1 (BACKLOG.md:56 now only shows the FAIL result); it survives in the result title (WIKISECTION.md:1) and LOOP-LOG.md:31-33
- WIKISECTION: verdict wording withdrawn in scope by the correction (WIKISECTION.md:25), so 'the facts are not in the kept article at all' stands only for the top-100k pack's indexed text and kept-source items
- WIKISECTION-H5b: issue 'No frozen criterion or bar for H5b' → partially wrong: LOOP-LOG.md:39 pre-states 'PASS ≥ 40 % would reopen a retrieval/query lever over Wikipedia' (unfrozen, no sha); the v0.2 comparison to 40 % in the arm uses that bar
- WIKISECTION-H5b: verdict_text: the original reading is 'Wikipedia is closed as a source for the bounty bar' (WIKISECTION.md:22); correction (:25) narrows it — extractor's bracketed quote is accurate
- WIKISECTION-H5b: status 'closed' acceptable but H5b is not named in any CLOSED row (R39 covers H5 only); its question is superseded by WIKIFULL R45
- AR: sets omits the v0.1 EN minus the 2 AR items pool (0/58, ar-L0-result.txt:8) and the 15 dev-probe negatives (ar-L0-result.txt:9), which make up the A4 1,467 count
- AR: Otherwise every field checks out: status lever-adopted (cut3-vgar-L1.md:53 'AR: ADOPT'; QUEUE.md:569 cut 3 adopted). The criterion sha256 00e6265f801887176773c51d204a2e1acd18d52db4cd3b0d25dffc86a0803858 recomputes and matches both ar-L0-cr…
- SC-L0 (SC v1 trigger: water-safety card…: status 'closed' is imprecise. The L0 verdict is FAIL on S5 (sc-L0-result.txt:15), with S6 pending. v1 was superseded by v2 and v3, and the water card plus trigger family was PARKED for the bounty (QUEUE.md:562; CUT3DEV.md:134).
- SC-L0 (SC v1 trigger: water-safety card…: The record cites 'CUT3DEV.md:31' as disclosing that the S5 set was burned for v2. The text is at CUT3DEV.md:31 and is correct.
- SC-v2-S5prime: status 'closed' is imprecise. This is S5′ FAIL, superseded by SC v3 (S5″), and the family was later PARKED (QUEUE.md:562).
- SC-v2-S5prime: Criterion sha recomputed: 47e6ff05… matches sc-v2-S5prime-criterion.sha256, and the runner tools/sc-fresh3.mts 79994e5e… matches. criterion_sha_present=true is correct.
- SC-v3-S5second: None of substance. Criterion sha 4aa47ee7… and runner sc-fresh4.mts 726cf47d… recompute and match the .sha256. Status parked matches QUEUE.md:562 and CUT3DEV.md:134.
- SC-S6 / SBt (reviewed snakebite card te…: Number 'CDC 6,500 ft vs EPA 5,000 ft' is cited at arms/sc-REVIEW.md:9. That line holds the TL;DR water row ('use the lower (EPA) threshold, 3 min above 1,000 m'). The CDC/EPA conflict heading is at sc-REVIEW.md:14 and the live quotes are a…
- SC-S6 / SBt (reviewed snakebite card te…: primary_delta '+0.92 rubric' is also stated in cut3-confirm.md:22 (dng-001 2.67 -> 3.58), judged with judge.v1-med (4 calls, cut3-confirm.md:17).
- VG-L0 (verdict guard v1): status 'lever-adopted' applies to the VG line, not to this L0. By its own rule ('PASS if V1–V4 hold', vg-L0-criterion.md:32) the L0 fails on V2, and V5 also FAILED (vg-REVIEW.md:5-6). Adoption came only as v3 via V5′ and VG-S (QUEUE.md:569…
- VG-V5prime (VG v2 re-review + v3 equiva…: status 'closed' is wrong. V5′ is an intermediate gate that PASSED, and v2 was immediately superseded by v3 (F1-F4) because of the reviewer's adversarial probes. 'closed' suggests a closed lever, but this line went on to adoption.
- VG-V5prime (VG v2 re-review + v3 equiva…: vg-repairs-v2.jsonl and vg-repairs-v3.jsonl: v2 has 36 rows with '"sameAsV1":true' and v3 has 36 rows with '"sameAsV2":true'. The files differ from character 1370 of line 1. The issue as stated is confirmed.
- VG-S (VG v3 ship gate): None of substance. Criterion sha da3a50c4… recomputes and matches the .sha256 and vg-S-REVIEW.md:6. Fire rate is 1/65 non-control items (vg-S-REVIEW.md:24).
- VG4-S2 (VG v4 threshold/superlative shi…: The record leaves out the gate's other bars: 0 control fires and 120/120 valid answers (vg4-S2-REVIEW.md:2). Also, 17 answers were skipped as not-model-route (vg4-S2-REVIEW.md:37).
- VG4-S2 (VG v4 threshold/superlative shi…: The '17/120' finding in QUEUE.md:577 is 16 missed self-contradictions plus 1 correct catch (vg4-S2-REVIEW.md:42 'There are 16 of them, against 1 correct catch'). It is consistent with 'regex VG catches 1/17'.
- CUT3DEV (cut 3 build: cut 2 + VG v3 + A…: judge field: the confirmation used two judges. v0.1 EN was judged with judge.v1-med, but the V-exact leg 'were re-judged with judge.v1 as the criterion requires (20 calls)' (cut3-confirm.md:47).
- CUT3DEV (cut 3 build: cut 2 + VG v3 + A…: seeds field: the V-exact confirmation ran on s42+s43 (cut3-confirm.md:45), not s44+s45.
- CUT3DEV (cut 3 build: cut 2 + VG v3 + A…: criterion shas recomputed: cut3-vgar-L1-criterion.md bf96feb6… (= cut3-vgar-L1.md:4) and cut3-confirm-criterion.md fdd06c4a… (= cut3-confirm.md:4). No .sha256 sidecars exist. The shas are cited in the result files and in QUEUE.md:567 and :…
- SIGNAL20 (signal slices): date: the v0.1 slice dates from 2026-10-06 (QUEUE.md:750; file mtime Oct 6 22:38). signal20-v02.ids and signal20-vpara.ids were added on 2026-10-08 (SLICE20 addendum, L1-PROTOCOL.md:14; QUEUE.md:824 23:31; mtime Oct 8 23:31).
- SIGNAL20 (signal slices): criterion_sha_present=true is overstated. The criterion file named, arms/L1-PROTOCOL.md, has no .sha256 sidecar. Only the slice files carry shas: signal20.ids.sha256 (4542bfcd…) and signal20-sets.sha256. All three recompute OK.
- SIGNAL20 (signal slices): seeds (v0.1): the control is boar-eval/runs/kiln/speedpack-l1/spctl-v01-s44 (L1-PROTOCOL.md:3; QUEUE.md:750), seed 44.
- RANDOM20 (random stratified slices): date: the files were created 2026-10-10 22:02 (mtime) and logged at QUEUE.md:905 (22:09, in the 2026-10-10 evening session after the 21:54 row at QUEUE.md:903). The L1-PROTOCOL addendum is labelled 2026-10-11 (L1-PROTOCOL.md:28).
- RANDOM20 (random stratified slices): criterion_sha_present=true is overstated. L1-PROTOCOL.md has no sidecar. Only random20-sets.sha256 exists, and its 3 entries recompute OK (a3e43672…, e4853b32…, 5112738a…).
- L1-PROTOCOL (judge triage protocol): None of substance. criterion_sha_present=false is correct: there is no L1-PROTOCOL.md.sha256. Date 2026-10-06 is correct (L1-PROTOCOL.md:1; QUEUE.md:750). Every cited line (11, 12, 13, 20, 26, 27, 28) holds the quoted number.
- GEMMATHINK: Issue 'Slice requests sha (01e6955d…) … recorded only in QUEUE.md:829' is incomplete: it is also in QUEUE.md:826 (freeze entry, 'requests sha 01e6955d…'). It is true that GEMMATHINK.md never records it. GEMMATHINK.md:20 gives only the full…
- GEMMATHINK: Issue 'CLOSED.md row R19 labels it closed citing CI upper +0.003' needs context: CLOSED.md:8 sets the convention that a row is 'closed' when the CI upper bound is below the MDE (+0.03), so R19 follows its own rule. The arm's own verdict is…
- GEMMATHINK: Primary delta CI upper '+0.003' is a rounding of 0.0025 (aggregates/paired_gap-GvsT-2seed.json raw ci95 [-0.057, 0.0025]). It is quoted the same way everywhere, so this is not an error, only a note.
- GEMMATHINK: Every other field was confirmed: status closed (verdict NO), primary_delta, n (51 judged / 58 generated, slice 20), seeds 42+43, judge (Opus judge.v1 N=4 L2; Haiku 5.5-low L1 on the slice and full s42), sets (V-para plus v0.1 smoke), date …
- K3-ON-CUT2: None material. Minor nuance: the record calls the 1 vitest failure 'expected', but k3-criterion.md:36 expected 2 failing assertions in depth.test.ts ('expected to fail the 2 assertions ... that pin retrieveK: 4'), while k3-on-cut2.md:40 re…
- K3-ON-CUT2: Minor: 458.9 - 439.7 = 19.2, the report states 'saved 19.3' (k3-on-cut2.md:21), presumably from unrounded means; the value is quoted correctly.
- TF2-ON-CUT2: None material. All fields (status, primary_delta, n, seeds, judge, sets, date, criterion_sha_present=false) match tf2-on-cut2.md and tf2-criterion.md.
- CUT3-CONFIRM: status 'lever-adopted' is imprecise: this arm is a no-regression confirmation with verdict CONFIRMED (cut3-confirm.md:61; criterion verdict is CONFIRMED vs REGRESSION, cut3-confirm-criterion.md:35). The cut 3 adoption decision is QUEUE.md:…
- CUT3-CONFIRM: primary_delta '+0.032, CI90 [+0.010, +0.062]' is reported, not gated: cut3-confirm-criterion.md:26 'Ratio (reported, not gated)'. The gated outcomes are: no changed item drops ≥ 1.0 (min Δ +0.92, dng-001), unsafe 0/0, V-exact drops < 0.15 …
- CUT3-VGAR-L1: verdict nuance: per the frozen criterion, VG should read 'NOT adopted', not 'PENDING'. cut3-vgar-L1-criterion.md:54 says 'If the file says FAIL, VG is not adopted whatever its L1 result', and arms/vg-REVIEW.md:5 reads 'Verdict: **FAIL**' (…
- CUT3-VGAR-L1: Otherwise the fields check out: Δ +0.029, CI90 [+0.007, +0.058]; 57 items x s44/s45; 16 calls; 53 reused control verdicts; judge.v1-med; v0.1; date 2026-10-04; no .sha256 sibling.

## A.8 Internal issues inside arm files (728)

- CF: CF.md L0 table still reads bar 1 'Pending reviewer' and bar 2 'Blind set: pending, coordinator' (CF.md:20-21) while data-REVIEW.md (FAIL 84%) and trigger-result.txt (recall 80/100 FAIL) exist; the TL;DR (CF.md:3) was not updated with eithe…
- CF: CF.md:33 says 'trigger-set2 was not opened or scored' but trigger-set2/items.jsonl and README.md exist in the folder (consistent with being frozen unscored, QUEUE l.585).
- CF: Patch cf-on-cut3.vs-0cfd4a77.patch and the scorer pins describe pre-revision commit f57c81fb; WIP revision (driving-side QID fix, government type) on wt/cf b8a2b7e9 is not a candidate and tests were not re-run (CF.md:35).
- CF: Result file does not quote the criterion sha; criterion sha256 file 5c302adf... matches shasum of CF-criterion.md (verified).
- CF: No CLOSED.md row for CF found (grep for arms/cf / country-facts returned nothing), although QUEUE l.586 records 'CF NOT adopted' and l.605 lists CF among exhausted levers.
- CF: Data-review population/plug checks relied on a summarizing fetch; five plug UNCLEARs flagged for recheck (data-REVIEW.md:52).
- CF: L1 never run: no judge numbers exist for CF.
- CHATGATE: Frozen G1 conflates gate routing misses with retrieval/corpus misses (acknowledged in CHATGATE.md:39 and QUEUE l.678 as a coordinator design error); the verdict line is FAIL while the reading is 'the gate is fine' — ambiguous headline for …
- CHATGATE: Kit was boar-crypto + wikivoyage-en (no Wikipedia pack), so G1 mostly measures kit coverage; no follow-up run with the Wikipedia pack recorded in the arm.
- CHATGATE: Criterion sha256 file stores path 'chatgate/CHATGATE-criterion.md'; hash 449c6e17... matches shasum (verified); result cites '449c6e17...' consistently.
- CHATGATE: Per-item rows live outside the arm (boar-eval/runs/kiln/chatgate/chatgate-s44.rows.json, not committed).
- CHATGATE: No CLOSED.md row for CHATGATE (grep returned nothing); QUEUE l.678 says 'No gate fix arm'.
- COMPLETE: The criterion specifies ONE change (instruction swap + max tokens), but the run also removed the user-turn suffix '(Response style: Keep it short: 2-3 sentences...)', declared as an interpretation in COMPLETE.md:40 — a deviation from the l…
- COMPLETE: Criterion sha bff13f1c... and prompt-diff sha 53bdda16... both match shasum of the files (verified).
- COMPLETE: CLOSED.md R8 (CLOSED.md:23) covers COMPLETE and says its date is not stated in the report (CLOSED.md:60), but COMPLETE.md:5 states 2026-10-06 18:33–20:07; COMPLETE.md itself does not cite R8.
- COMPLETE: Confident-wrong breakdown lists '9 new' and '1 left' with net +8 (COMPLETE.md:60-63); consistent with 7 − 1 + 9 = 15, but only readable that way if 'left' means left the list.
- COMPLETE: R450 contexts were picked using the reference answer (upper-bound reader setting, COMPLETE.md:103); 1 seed with noise floor ≈ 0.05.
- CROWDQ: Frozen criterion stage 2 requires the reach check to 'reproduce the replay's 46 ± 3, else stop and report' (CROWDQ-criterion.md:26); P reads 41/180, outside 43–49. The result applies a later QUEUE ruling (15:0x) changing the band to 40 ± 4…
- CROWDQ: SE family alone meets the 'cost confirmed' reading (Δ −0.033 ≤ −0.03, CI high −0.011 < 0) while the pooled reading is 'cost small'; the declared split had no separate decision rule.
- CROWDQ: runs/ now contains Opus judgment files (qa-*-se *.judgments.opus.jsonl dated 20:51–20:56, and an in-progress firstaid .opus.jsonl.lock) written after CROWDQ.md (15:42) which states 0 Opus; per QUEUE l.1062 these belong to the PACKS-L2 burn…
- CROWDQ: S Haiku rows were judged in an earlier session (system label differs) (CROWDQ.md:38).
- CROWDQ: No own CLOSED.md row; CLOSED.md R48 (top-1 pack routing) makes reopening conditional on CROWDQ showing a cost >= 0.03, and QUEUE l.1033 says CROWDQ 'confirms R48', but CROWDQ.md does not cite an R## row.
- CROWDQ: Criterion sha 71603c60... matches shasum (verified) and aggregates/crowdq.json criterion_sha256; JSON pooled/SE/topic numbers match CROWDQ.md.
- CRYPTOFACTS-step1: Criterion sha256 b093b65a…ffc60 verified: shasum matches the .sha256 file (the .sha256 records a workspace-relative path, rnd/research/coordinator/arms/...).
- CRYPTOFACTS-step1: Closed at step 1 (QUEUE l.796 'Line closed at step 1') but no row for CRYPTOFACTS in CLOSED.md.
- CRYPTOFACTS-step1: Verdict is coverage-only; the projected effects are projections, not measurements (stated in the file).
- CRYPTOSEL: No CRYPTOSEL-criterion.sha256 sibling file, so not frozen by the template's definition; the cited sha 6ba3e103… does match shasum of CRYPTOSEL-criterion.md (6ba3e103618e…e469).
- CRYPTOSEL: Patch sha 948493ee… cited in both reports matches shasum of cryptosel-on-cut3.vs-0cfd4a77.patch; gold-facts.json sha e1ca7a4c… matches gold-facts.sha256.
- CRYPTOSEL: Disclosed deviations: gold-facts.json written after the round-1 replay had run on 009; round-2 Abstract-preference rule goes beyond the criterion wording.
- CRYPTOSEL: L0 latency bar (p50 <= 1.2x): L0-round2.txt shows the single-run ratio 1.217 (>1.2); PASS rests on a post-hoc min-of-3 interleaved metric (1.005x).
- CRYPTOSEL: Criterion L1 bar 'paired Δ >= 0' passed with lan-exp-007 noise item included in the changed set.
- CRYPTOSEL: Closed (no revision after L1) but no row for CRYPTOSEL in CLOSED.md; QUEUE l.608 rounds CI to [−0.005, +0.014].
- CRYPTOTRUTH: Criterion sha 767e4d24…1902 verified: matches the .sha256 file and shasum. Patch sha b64b3e08… matches shasum.
- CRYPTOTRUTH: Patch file name 'cryptotruth-on-cut4.vs-0cfd4a77.patch' but the arm is built on cut 6 (coord/detmax, patch 824e0b35…) — naming inconsistency.
- CRYPTOTRUTH: Gate table wording 'FAIL (2 of 3)' is ambiguous (2 probes pass, 1 fails); TL;DR states one probe of three fails.
- CRYPTOTRUTH: Criterion G3 asks for a same-day cut 6 control; control verdicts were reused from the speedpack-l1 run (cut 4-control texts, byte-identical answers) — allowed by the 10-06 single-source rule but the control verdict source is not a cut 6 ru…
- CRYPTOTRUTH: Status: verdict NOT ADOPTED; QUEUE l.702 says 'parked for after the claim (PR phase), with a broadened phrase list as a new freeze'. No row in CLOSED.md.
- CRYPTOTRUTH: Effect rests on 3 items (002, 005, 007); held-out/V-para exposure not examined (UNKNOWN in file).
- CUT4-KVFIX: Criterion sha c4735323… verified (matches .sha256 and shasum); stack patch 1fd5d9a5…, kvfix 27f7e0f3… match shasum.
- CUT4-KVFIX: Gate (2) cannot exercise KVFIX by construction (desktop adapter uses llama-server, shim no-ops saveSession): the desktop PASS is vacuous for KVFIX; gate (3) device result is not reported in this arm directory (still open in cut4-L1.md).
- CUT4-KVFIX: Adopted into cut 4 on gates (1)+(2) as the criterion allows; final cut 4 also includes INSTANT-SUBJ (d51e844c…), which was not in this desktop identity gate (QUEUE l.654).
- CUT4-KVFIX: CUT4.md mixes two 'cut 4 APK' identities: line 53-54 (80925f6a…, tree d631a9de…) and line 60 referring to 'the cut 4 APK 22e22f2c…' (final, tree 6a61670e…); the first is superseded (QUEUE l.651) but the file does not say so.
- CUT4-KVFIX: No CLOSED.md row (adopted levers are excluded by design).
- CUT4-INSTANT-FRAG: Criterion sha c4735323… verified; instantfrag patch 5d3922df… matches shasum.
- CUT4-INSTANT-FRAG: L1 PASS is vacuous (changed set empty); the only evidence of benefit is the warm-up question and unit tests.
- CUT4-INSTANT-FRAG: Lookup set (lookup-set/items.jsonl, sha 72404eea…) was meant to be engineer-blind; the engineer ran it (QUEUE l.637 logs the exposure, set burned for that agent). It lives in the arm dir, not under blind/.
- CUT4-INSTANT-FRAG: Lookup set revealed an uncovered off-topic instant class (Baton Rouge) -> follow-up arm INSTANT-SUBJ (arms/instsubj), adopted into final cut 4.
- CUT4-INSTANT-FRAG: Side effect kept: instant preview event still emitted before the block (UI may flash the fragment).
- CUT5-SPEED: Criterion sha256 ab05007f... matches CUT5SPEED-criterion.sha256 (verified with shasum).
- CUT5-SPEED: G3 as frozen was structurally unable to pass for component 1 (desktop node has no bridge/native-zstd cost); acknowledged in Deviations.
- CUT5-SPEED: G4 guards were tightened after a dev check showed 35 violations, before any desktop run (disclosed); the first run was killed and restarted.
- CUT5-SPEED: Passage identity measured by (title, section, source), not chunk id (deviation).
- CUT5-SPEED: G4 does not simulate the learned detector; KV component (2) covered by unit tests only.
- CUT5-SPEED: Post-verdict device A/B (QUEUE l.699, 0.445x) is confounded and needs ABBA; not recorded in CUT5SPEED.md.
- CUT5-SPEED: Not cited in CLOSED.md.
- CUT5-LITE: Post-hoc arm (declared in criterion line 1) frozen after CUT5-SPEED's results.
- CUT5-LITE: Criterion sha256 e8be61a9... matches CUT5LITE-criterion.sha256 (verified).
- CUT5-LITE: Desktop-identical by construction; KV .nosrc change covered only by unit tests (desktop adapter does not use LlamaEngine.ts); phone gains unmeasured in this arm.
- CUT5-LITE: Passage identity by (title, section, source), not chunk id.
- CUT5-LITE: Criterion has no G3 (numbering G1, G2, G4, G5), intentional carry-over from CUT5-SPEED numbering.
- CUT5-LITE: Not cited in CLOSED.md; later superseded by cut 6/cut 7.
- CUT7: Criterion sha256 2d430a70... matches CUT7-criterion.sha256 (verified); cut7.vs-cut6.patch sha 0eee6a0b... matches its .sha256 file.
- CUT7: Cross-doc: CUT7.md quotes v0.2 held-out headline 0.512 while workspace CLAUDE.md states v0.2 held-out raw 0.519 for cut 6/7.
- CUT7: Criterion UNKNOWN says 107 ms cold load; report says 107–129 / 111–129 ms (G5 measured on MacBook, not mini; g5 cold script reconstructed, deviation 1).
- CUT7: Fire count read blind request files under a scoped blind exception (script-only); exposure logged.
- CUT7: Learned detector not simulated in the deterministic count (upper bound).
- CUT7: CLOSED.md row 9 (FACTS) references cut 7 shipping but no CLOSED row for CUT7 itself; result does not cite a CLOSED row.
- CV: Final verdict (ship gate FAIL, CV KILLED) is not written in any .md in arms/cv; it exists only in QUEUE.md:596 and gate-score.txt. CV.md TL;DR is stale ('accuracy NOT scored').
- CV: CV.md says CV answered 118 of 146 routed (28 abstained); score.txt says CV answered 113, abstained 26 on the 145 scored items (QUEUE l.592 repeats 113/26) - different denominators, not reconciled.
- CV: gold/README.md says 148 scored items (155 - 7 ambiguous), but score.txt scored 145.
- CV: Rev1 breaks the frozen criterion's 80% routing bar by the letter (103/155 = 66.5%), disclosed in CV.md and QUEUE l.594.
- CV: Routing was tuned on the same DEV questions (CV.md:15).
- CV: The 'fresh blind' gate set and key are stored inside arms/cv/ (gate-set/, gate-key/), not under blind/.
- CV: Ship gate's v0.1 EN L1 step was never run (gate FAIL first).
- CV: Criterion sha256 b27a0b58... matches CV-criterion.sha256 (verified).
- CV: Two patch files: run patch 9c4250fa and final/rev1 patch (CV.md lists 455559f6... then rev1 8271ec3b... for the same filename).
- CV: dev-fires.jsonl is empty (0 bytes), consistent with 0/1,328 dev fires.
- CV: No CLOSED.md row for the computed-verdict line (CV/CVS/CVH/CVO) found by grep.
- CVS: Criterion header says frozen 2026-10-05 but CVS-criterion.md / .sha256 file mtimes are 2026-10-04 18:20 (likely timezone; minor).
- CVS: Result files (cvs-L1.md, CVS.md) do not cite the criterion sha; QUEUE l.597 cites 595107c3…, which matches shasum of CVS-criterion.md and the .sha256 file.
- CVS: No standalone gate #3 result .md: the gate #3 PASS verdict is only in gate3-score.txt (labelled 'cut 3 + CV', not CVS) and QUEUE l.600.
- CVS: gate3-score.txt scored 83 of 90 key lines (7 ambiguous) while the criterion requires 120/120 valid; validity count only in QUEUE l.600.
- CVS: Descriptive result on the burned CV gate set (+27.7 pp) appears only in QUEUE l.600, not in arm files.
- CVS: Not listed as a row in CLOSED.md (computed-verdict family absent from the registry) though QUEUE l.604 closes the line.
- CVS: Other files: cvs-on-cut3.vs-0cfd4a77.patch, cvs-dev-replay.mts/.txt, cvs-gate3-timing.txt, gate3-detail.jsonl, gate3-key/ (README, key.jsonl, key.scorer.jsonl), gate3-set/ (README, items.jsonl).
- CVH: Criterion header says frozen 2026-10-05 but file mtimes are 2026-10-04 20:19 (likely timezone; minor).
- CVH: cvh-L1.md does not cite the criterion sha; QUEUE l.602 cites 010b7ed2…, matching shasum and the .sha256 file.
- CVH: Step 2 (fresh blind gate #4) never run by design (stop rule) — criterion step without result.
- CVH: Not listed as a row in CLOSED.md (computed-verdict family absent from the registry).
- CVH: Other files: cvh-on-cut3.vs-0cfd4a77.patch (743 KB).
- CVO: No CVO-criterion.sha256 file: criterion not frozen by the sibling-sha convention; QUEUE l.606 cites 4c37259b…, which matches shasum -a 256 of CVO-criterion.md (4c37259b70a6…).
- CVO: No result .md for Step 2 / gate #4: the FAIL verdict and the +6.0 pp rescored number exist only in QUEUE l.618; gate4-score.txt shows 0.0 pp / CV answered 0 because of a scorer bug (non-'computed-verdict' reason codes counted as abstain).
- CVO: gate4-score.txt prints 'bar >= +10' while CVO-criterion.md sets the bar at +8 pp (scorer default reused from CV/CVS).
- CVO: gate4-detail.jsonl vs gate4-detail-cvoself.jsonl differ on cut3 labels for several items (e.g. cv4-008, cv4-023, cv4-030); the rescoring procedure is documented only in QUEUE.
- CVO: cvo-L1.md title says PASS 'with two flags'; Step 1 baseline choice (same-day control vs stored cut3-confirm) was a post-hoc coordinator ruling (QUEUE l.609).
- CVO: gate #4 seeds and 120/120 validity not written in arm files.
- CVO: Not listed as a row in CLOSED.md.
- CVO: Other files: cvo-on-cut3.vs-0cfd4a77.patch, gate4-detail.jsonl, gate4-detail-cvoself.jsonl, gate4-key/ (README, key.jsonl, key.scorer.jsonl), gate4-set/ (README, items.jsonl), gate4-score.txt.
- DEEPBO2: Criterion text says '204 prompts' for S1 alone (l.17) while the result runs 102 per selector (204 total); QUEUE l.857 notes the criterion's 204 counts both selectors.
- DEEPBO2: Criterion sets USEFUL threshold at +0.015 ≈ 40 % of 'the oracle's +0.038', and the criterion question cites handoff CI +0.027…+0.051 for the oracle gain; DEEPBO2.md table does not report a CI for the oracle vs expected-single +0.038.
- DEEPBO2: Result predates CLOSED.md and does not cite a row; CLOSED.md lists it as R27.
- DEEPBO2: Criterion sha in DEEPBO2.md (c7e2232f…) matches shasum and the .sha256 file.
- DEEPBO2: Other files: aggregates/ (S1.picks.json, S2.picks.json, baselines-summary.json, score-S1/S2/anti-oracle/cites/longer/oracle/s42/s43.json), tools/ (build.py, run-selector.sh, score.mjs, select.py).
- DEEPCOVER: Criterion sha256 e325ab46… matches DEEPCOVER-criterion.sha256 (verified); patch sha 180adac4… matches deepcover.vs-dt512.patch.sha256 (verified).
- DEEPCOVER: Criterion specifies no explicit stop rule for the Opus slice check; the NO verdict after Opus rests on 'gain ≥ +0.03 excluded' plus the correctness drop (the written correctness clause at stage 2 is Haiku-defined, at stage 3 Opus-defined).
- DEEPCOVER: aggregates/L1-rule-CvsH-slice.txt prints '=> NO' for the Haiku slice while the criterion's l1_futility (Haiku Δ > 0) sent it to Opus; the arm correctly continued to Opus, but the rule file label is misleading.
- DEEPCOVER: No row for DEEPCOVER in CLOSED.md (registry built 10-11, before the 10-12 verdict); CLOSED R8/R25 refer to DEEPCOVER as the reopen path; BACKLOG l.49/l.81 record the NO.
- DEEPCOVER: Full v0.2 (dc-C-v02-s42, 110) and V-para s42 (58) generated and left unjudged; V-para s43 never run; verdict strength slice only (n = 20).
- DEEPCOVER: Smoke criterion required cap hit on ≤ 1/3; QUEUE l.923 reports two of three smoke answers at the 300-cap edge (290 tokens) yet PASS (290 < 300, so arguably not a hit).
- DEEPCOV-FB: No frozen criterion file or .sha256 in the directory; the gate rule (≥ 5 enters, 0 emptied) is stated only in the result file.
- DEEPCOV-FB: Directory name deepcovfb vs arm name DEEPCOV-FB used in QUEUE l.914 and CLOSED R32.
- DEEPCOV-FB: CLOSED R32 dates it 10-10/11; QUEUE l.914 and file mtime give 2026-10-10 23:32.
- DEEPCOV-FB: Lexical detector only (deep runs used detector v3b); title-level gold on 39/60; why 6 of 9 gold R2 items miss was not examined.
- DEEPCOV-FB: Other files: replay-base.jsonl, replay-peer.jsonl, aggregates/replay-v01.json, tools/{replay-deep.ts,replay-deep.sh,run-replays.sh,fallback.py}, logs/ (pack.sha256, replay logs, smoke.jsonl), cache/ app dirs.
- DEEPCTX: Criterion sha b9fba1b6… matches DEEPCTX-criterion.sha256 and is cited in the result (verified); patch sha 1335c2c7… matches (verified).
- DEEPCTX: CLOSED R23 labels it closed (CI upper +0.024 < +0.03) while the TL;DR of CLOSED.md also lists DEEPCTX as parked in BACKLOG s3: dual labelling across documents.
- DEEPFULL-F1: Criterion sha c13b5679… matches DEEPFULL-criterion.sha256 and is cited (verified).
- DEEPFULL-F1: F1 answers truncated at cap 200 on 20/20, so the result measures truncation as much as persona.
- DEEPFULL-F2: Result says NO, but CLOSED R25 labels F2 'not detected at MDE 0.08 (20, 1 seed)' because the CI upper +0.048 includes +0.03: status label differs across documents.
- DEEPFULL-F2: Context lever confounded with persona and cap; isolated later by DEEPCTX.
- DEEPFULL-F2: Smoke try 1 ran without --deep-model (infra error before the first token, rerun logged); allowed by the criterion.
- DEEPFULL-F2: Minor rounding: table arm ratios give 0.477−0.489 = −0.012 and 0.325−0.347 = −0.022 vs paired −0.013 / −0.023 written (paired values from unrounded aggregates −0.0126 / −0.0228).
- DEEPHEDGE: Criterion sha256 31d81b13… matches DEEPHEDGE-criterion.sha256 (verified); patch sha f4f775a1… matches deephedge.vs-dt512.patch.sha256.
- DEEPHEDGE: Arithmetic inconsistency at DEEPHEDGE.md:5: '12 of them get the identical 32-word fallback (... LOSSMAP primary hedged 10, off-question 3)' — 10 + 3 = 13, not 12.
- DEEPHEDGE: Wording drift: DEEPHEDGE.md:3 says byte-identical E vs H on 9/11 (+2 instant-path items identical), QUEUE l.952 says 'E = H byte-identical' without the split.
- DEEPHEDGE: Criterion said ≤ 31 ids; 29 generated (overlap of hedged-11 and random20-v02) — consistent but not stated in criterion.
- DEEPHEDGE: Generation 1 failed FAIL-INFRA (missing Q2 model); gen2 is the run reported (QUEUE l.951).
- DEEPHEDGE: Other files present: PATCH.md (read), arm.conf, deephedge-remote-run.sh, deephedge.vs-dt512.patch(+.sha256), hedged11.ids, aggregates/hedge-gate.json, tools/diff-vs-dt512.scratch.test.ts, tools/hedge_gate.py, logs/ (empty), .locks/ (2).
- DEEPHEDGE: CLOSED.md row R40 records this arm; result file itself cites no CLOSED row.
- DEEPITER: Criterion sha256 432fddf9… matches DEEPITER-criterion.sha256 (the .sha256 file carries a repo-relative path); patch shas a83bead8… and ad86e920… match their .sha256 files.
- DEEPITER: Criterion is shared with MP4B (arm M); MP4B's result is in arms/mp4b/, not in this directory.
- DEEPITER: Criterion's stage rules do not specify what an Opus slice result decides (stage 1 near-miss → Opus 'before deciding', verdict defined only on full v0.2 Opus); NO was declared at slice level — verdict strength is slice-only (DEEPITER.md:17).
- DEEPITER: aggregates/L1-rule-slice.txt applies arm.sh's generic wins/p50 PROMOTE/CHEAPER rule ('=> NO'), not the criterion's futility/near-miss rule.
- DEEPITER: Criterion names runner 'arms/deepiter/tools/remote-run.sh' but no tools/ dir exists; runner is deepiter-remote-run.sh at arm root.
- DEEPITER: gen-slice.txt reports deepRouted 19/20 while the result table says 'no deep path on 5' (likely planner-gate exclusions such as health; not explained).
- DEEPITER: Full 110 and V-para stages not run.
- DEEPITER: Other files present: README.md (read), arm.conf, deepiter-remote-run.sh, two patches + .sha256, aggregates/ (9 files: L1/L2 slice json, followups, think, posthoc split, gen-slice, L1-rule-slice), .locks/ (2).
- DEEPNORAG: Criterion sha256 1c78caea… matches DEEPNORAG-criterion.sha256 (sha file records path 'deepnorag/DEEPNORAG-criterion.md').
- DEEPNORAG: Criterion predates CRITERION-TEMPLATE: no ## Power block / MDE; uses signal20-vpara (the 20 weakest 4B items), which the later template forbids ('never signal20') — the slice is selected, so Δ is not an unbiased set estimate.
- DEEPNORAG: Haiku only, one seed, slice 20: CLOSED R33 labels it closed with MDE 0.08; Δ −0.045 is below that slice MDE though CI excludes 0.
- DEEPNORAG: Stage 3 (full 51) not run, as allowed by the criterion.
- DEEPNORAG: Other files present: arm.conf, aggregates/ (L1-NvsH-slice json, L1-rule-slice.txt, chain.log, gen-slice.txt, think-H/N-slice, think-N-smoke), .locks/ (2).
- DEEPPAR: Criterion sha256 98028c0d… matches DEEPPAR-criterion.sha256 and the sha cited in DEEPPAR.md:3.
- DEEPPAR: bmoe binary built from the v0.28.0 tag prints --version 0.27.0 (upstream CMakeLists not bumped) — documented.
- DEEPPAR: Criterion said (c) is written 'only if this one ends NEEDS-L1'; the verdict was FAIL, yet (c) DEEPPAR-L1 was run (FAIL text also says 'until (c) is run', so permitted).
- DEEPPAR: Criterion anticipated (c) as 'judged L1, Haiku 5.5-low paired vs the deep35 desktop traces on the EN slice'; the actual (c) used Opus on R450 gold contexts.
- DEEPPAR: Superseded for planning purposes by DEEPPAR-L1 TRANSFER.
- DEEPPAR: Other files present: items.csv, raw/ (per-item rendered/server/bmoe/csv files, compare.out, run.log, server.log, side-00 files, prompts/, l1/), tools/ (run_deeppar.py, compare.py, run_l1.py, splice.py, analyze_l1.mjs).
- DEEPPAR-L1: Criterion sha256 1d974587… matches DEEPPAR-L1-criterion.sha256 and the sha cited in DEEPPAR-L1.md:3.
- DEEPPAR-L1: Deviation: judge needed --bench bench/v0.1 (bare command would resolve to v0 refs); pins confirmed after the change.
- DEEPPAR-L1: Runner bug: result rows had item id overwritten by session id; re-mapped by request order and verified by prompt-token counts.
- DEEPPAR-L1: bmoe has no min_p (pre-accepted deviation).
- DEEPPAR-L1: Result notes a ≈ 0.04 loss is not excluded by the CI; QUEUE l.808 adds '4 answers byte-identical to A', a figure not in DEEPPAR-L1.md.
- DEEPPAR-L1: CLOSED.md row R16 covers DEEPPAR + DEEPPAR-L1 as 'closed (equivalence shown, not a lever)'.
- DEEPPAR-L1: Files present: bmoe-R450.traces.jsonl, bmoe-R450.judgments.jsonl, bmoe-R450.items.csv, tools/run_l1.py, splice.py, analyze_l1.mjs, raw/l1/.
- DEEPREAD: CLOSED.md R15 labels this family 'not detected at MDE 0.055 (57, 1 seed)' while the frozen verdict is INCONCLUSIVE; record does not cite a CLOSED row itself
- DEEPREAD: Backend deviation: 4B ran on node-llama-cpp (MacBook), deep35 on llama-server (mini); sampler chains differ at temp 0.7, so part of Δ is not separable from the model (documented)
- DEEPREAD: DEEPREAD-criterion.sha256 is a shared file also holding the facts/FACTS-criterion.md hash
- DEEPREAD: Extra judgment files present (deep35-R450.judgments.haiku.jsonl, .sonnet-low.jsonl, .sonnet-med.jsonl) used later for JUDGE-TRIAGE, not described in DEEPREAD.md
- DEEPREAD: Other files: analysis.json, analyze.mjs, build_msgs.mjs, gen_server.py, requests.jsonl, traces, server log, gen-run.log, judge log
- DEEPRERANK: No criterion file (and no .sha256) in the arm directory; the gate (≥ 5 items) is stated only in the result and QUEUE
- DEEPRERANK: QUEUE.md:908 names the k = 6 gold-entering items as 'vit-sci-002, vit-trv-003', but REPLAY-v01.md:27 says k = 6 is vit-sci-002, trv-004 (vit-trv-003 is the k = 4 pair)
- DEEPRERANK: CLOSED.md R30 covers this arm (gate FAIL at step 0) but the result file cites no CLOSED row
- DEEPRERANK: Caveat: 'in top-k' means raw, not kept sources after compressContext/400-token cap; detector lexical vs learned v3b in deep runs
- DEEPRERANK: Other files: aggregates/{replay-v01.json, rerun-ub2048.json}, replay-v01.jsonl, rerun-ub2048.jsonl, fidelity/*.jsonl, logs/*, cache/appdir, tools/{rerank-replay.sh, rerank-replay.ts}
- DEEPROUTE: Descriptive analysis with no verdict rule; CLOSED.md R28 labels the routing family closed, the result file cites no CLOSED row
- DEEPROUTE: All rules in-sample on the same 57 items; R8 formed after seeing R2/R3 (stated in UNKNOWN)
- DEEPROUTE: Other files: analysis-ctl-s44.json, analysis-ctl-s45.json, deeproute-items.csv, deeproute.mjs
- DEEPROUTE-OOS: No frozen criterion (descriptive); script-only read of blind/bench-v02 and blind/V-para cut 6 traces+judgments (exposure logged in QUEUE:812)
- DEEPROUTE-OOS: Not listed as its own row in CLOSED.md (folded into R28 routing family)
- DEEPROUTE-OOS: Script: r2oos.py
- DEEPROUTE-VPARA: No frozen criterion (descriptive); recombined judgments written into blind/V-para/runs-deeproute/ and blind/bench-v02/runs-deeproute/ (script-only)
- DEEPROUTE-VPARA: Floor-adj figures (≈ 0.33, ≈ 0.45) are derived by applying an assumed floor Δ, not measured
- DEEPROUTE-VPARA: The v0.2 addendum is called DEEPROUTE-V02 in QUEUE.md:882 but lives inside DEEPROUTE-VPARA.md
- DEEPROUTE-VPARA: CLAIM-REVIEW note (QUEUE.md:868): random routing of 37 % would capture ≈ 37 % in expectation, so V-para R2 is near chance; result file says '≈ 35–45 %'
- DEEPROUTE-VPARA: Script: hybrid-vpara.py
- DEEPSAMP: Criterion has no '## Power' block (expected_delta/mde) required by the current CRITERION-TEMPLATE
- DEEPSAMP: Slice is signal20-vpara (arm-*.conf SLICE_IDS), which the current template forbids ('never signal20'); may predate that rule
- DEEPSAMP: CLOSED.md R26 labels Q closed and P borderline (CI upper +0.029 vs +0.03); result file cites no CLOSED row
- DEEPSAMP: Other files: aggregates/ (L1-PvsH/QvsH slice JSON, L1-rule-slice.txt, chain-P/Q.log, gen-slice.txt, think-*.json), arm-P.conf, arm-Q.conf, tools/remote-run.sh, .locks/
- DEEPSPEED: Criterion sha256 c2e101d3... matches .sha256 and shasum (verified).
- DEEPSPEED: Extra file UPSTREAM-NOTE-ngram.md: draft upstream bug report for bmoe (not posted; no public posting without r4to OK).
- DEEPSPEED: Other files: items.csv, raw/ (152 files: gen/csv-summary/stderr per item x config, run.log, driver.out), tools/run_deepspeed.py, tools/compare.py.
- DEEPSPEED: Divergence cause (batched verify numerics) is stated as inference, not tested.
- DEEPSPEED: CLOSED.md row R36 cites this arm, but the result file itself cites no CLOSED row.
- DEEPTHINK: Criterion sha 1d988821... and patch sha eb3f464b... match .sha256 files and shasum (verified).
- DEEPTHINK: Wins clause ambiguous: read as wins-vs-ref it is 0 ≥ 3 FAIL, read as head-to-head 31 ≥ 15 pass; promotion rests on the Δ clause (DEEPTHINK.md:24).
- DEEPTHINK: QUEUE.md:820 interim entry (and DEEPTHINK2-criterion.md:3) say '39/58 items hit the 1024 budget', while DEEPTHINK.md:16 reports 36/51 on s42 (7 venue items have no generation, so 39/58 is not reconcilable with the result table).
- DEEPTHINK: Deviation 1: adapter --timeout-ms 600000 vs criterion 'everything else exactly as D' (ratified later).
- DEEPTHINK: No Haiku on T s43; L2 D rows reused from DEEPVPARA.
- DEEPTHINK: Status 'lever-adopted' taken from CLOSED.md TL;DR ('DEEPTHINK 1024 vs none ... adopted'); later superseded in budget by DT512 (512 recommended); never shipped on a device.
- DEEPTHINK: Other files: aggregates/ (10 JSON: L1-TvsD-s42, L2-TvsD-2seed opus + paired_gap, L2 s42, cat-*, think-*), deepthink-on-cut6.patch(+.sha256), tools/{dt.sh,dtcat.py,remote-run.sh,shard_judge.sh}.
- DEEPTHINK-2: Criterion sha 5af5b013... and patch sha e813da6d... match .sha256 files and shasum (verified).
- DEEPTHINK-2: Criterion premise (DEEPTHINK2-criterion.md:3) says '39/58 answers hit the 1024-work budget'; DEEPTHINK.md:16 reports 36/51 for the same s42 run.
- DEEPTHINK-2: Result file labels verdict NO/NOT PROMOTED; CLOSED.md row R22 relabels it 'not detected at MDE 0.06 (51, 1 seed, Haiku)' (status here follows the registry).
- DEEPTHINK-2: Result file cites the adapter sha (da424129...) as required, but the criterion asked the adapter commit 'after 060845f'; adapter commit used is 2cbddfc (consistent, just noted).
- DEEPTHINK-2: tools/l2.sh present but unused (no promotion).
- DEEPTHINK-2: Other files: aggregates/ (L1-T2vsD, L1-T2vsT, cat-haiku T2vsD/T2vsT, think-T2-s42), deepthink2-on-cut6.patch(+.sha256), tools/{dt2.sh,dt2cat.py,l1.sh,l2-scales.sh,l2.sh,paired.mjs,remote-run.sh,shard_judge.sh}.
- DEEPTHINK-V02: Criterion sha 265ea559... matches .sha256 and shasum (verified).
- DEEPTHINK-V02: Reading section says 'head-to-head 55/40' (DEEPTHINKV02.md:22) but the table says 51/19/40 (line 16).
- DEEPTHINK-V02: Reading section says TV floor-adj 0.414 (line 22) vs 0.413 in the table (line 16).
- DEEPTHINK-V02: QUEUE.md:828 headline says 'Δ +0.029 vs +0.03' while the result file's decision number is +0.027 (dedup); +0.029 is the raw 266-row figure.
- DEEPTHINK-V02: Haiku spend 266 over the 240 cap (runner and coordinator both ran l1.sh; 46 duplicate keys).
- DEEPTHINK-V02: Near-miss: Opus on the same s42 ids later gave +0.048 (QUEUE.md:836, :851), prompting the L1-PROTOCOL near-miss rule; the NO stands.
- DEEPTHINK-V02: Result says s43 requests prepared (03522ff5f224), not run; the addendum s43 used requests f219654e (different hash).
- DEEPTHINK-V02: Under CLOSED.md's MDE 0.025 for v0.2 one seed the \|Δ\| 0.027 qualifies as closed, but the arm has no CLOSED.md row.
- DEEPTHINK-V02: Other files: aggregates/ (22 files incl. L1-TVvsD-s42, L1-rule-s42.txt, parametrisation.txt, think-TV-s42/s43, percat-*, paired_gap-*, console logs, s43-chain.log), tools/{dedup.mjs,dtv.sh,l1.sh,l2.sh,paired.mjs,percat.mjs,s43-after-dt512.…
- DEEPTHINK-V02-ADDENDUM1: Addendum sha 92121156... matches .sha256 and shasum (verified); the .sha256 uses a relative filename while the other .sha256 files use absolute paths (cosmetic).
- DEEPTHINK-V02-ADDENDUM1: The one-seed result that gated seed 43 (TV−D CI low > 0) is not written in the .md; it is only in QUEUE.md:836 (+0.048 (+0.022…+0.076)) and aggregates/*-1seed files.
- DEEPTHINK-V02-ADDENDUM1: s43 generation lost to a duplicate launcher and rerun (deviation logged QUEUE.md:838); Opus 440 total = addendum cap 220 + 220 on seed 43.
- DEEPTHINK-V02-ADDENDUM1: Measurement on a burnt/dev set: explicitly not claim evidence.
- DEEPTHINK-V02-ADDENDUM1: No CLOSED.md row (measurement).
- DEEPVPARA: Criterion sha256 503c2a0c… matches the .sha256 file and is cited in the result (verified with shasum).
- DEEPVPARA: Deviation: Haiku cap exceeded (criterion 320/stage; ran 510 + 880) — DEEPVPARA.md:61.
- DEEPVPARA: Promotion rests only on the Δ clause (wins vs reference 0/0 for both arms); stage-2 margin only +0.002 over the +0.03 threshold.
- DEEPVPARA: DEEPVPARA-CATS.md:18 gives v0.2 D 0.567 while DEEPVPARA.md:48 gives 0.568 (rounding/aggregation difference).
- DEEPVPARA: Criterion predates the CRITERION-TEMPLATE: no ## Power block / MDE.
- DEEPVPARA: K s43 not Haiku-judged (DEEPVPARA.md:61); v0.2 K s43 win reads '0/110 (1 tie)'.
- DEEPVPARA: v0.2 is burnt (dev), so v0.2 numbers are not claim numbers (stated in file).
- DEEPWIKI: Criterion sha256 88de2099… matches .sha256 and the result citation (verified).
- DEEPWIKI: Slice uses signal20-vpara (arm.conf SLICE_IDS); the later CRITERION-TEMPLATE says 'never signal20' (random20 sets) — predates the rule but the slice is a selected, not random, subset.
- DEEPWIKI: Criterion has no ## Power block; verdict extends a 20-item Haiku slice (MDE ~0.08 per CLOSED.md) to 'corpus size closed for the deep tier'.
- DEEPWIKI: Criterion example path mentions `--timeout-ms 600000` etc. consistent; arm.conf CONTROLS includes D and K but ladder numbers vs D/K were not reported (stopped at slice, as rule allows).
- DEEPWIKI: Result file does not cite its CLOSED.md row (R29 in CLOSED.md).
- DENSECHUNK-ST: Criterion sha256 24793013… matches .sha256 and the result's prefix citation (verified).
- DENSECHUNK-ST: Criterion G1 example ('OFF 90 → ON ≥ 113') differs from the realised threshold (OFF 67 → ≥ 84); the rule is relative so not a conflict, but the example is stale.
- DENSECHUNK-ST: The same empty-kept statistic was later ruled mis-specified for ST2 (ST2 addendum 1, RULE 26); ST's G2 FAIL also involves empty-kept +2 with gold-in-kept rising, but ST was not re-ruled (in fusion mode raw6 gold did drop 6 → 5, so a genuin…
- DENSECHUNK-ST: Addendum 1 (Haiku replaces local judge) is moot because no judge stage ran.
- DENSECHUNK-ST: Criterion's reopen line cites CLOSED R30 (DEEPRERANK); result file cites no CLOSED row.
- DENSECHUNK-ST: packdense2-only.vs-tk2base.patch has no sibling .sha256 (other patches do).
- DENSECHUNK-ST2: Criterion sha256 6c7b12dd… matches .sha256 and result citation (verified).
- DENSECHUNK-ST2: Step-0 G2 FAILED by the frozen statistic (ST2-GATE.md:1); addendum 1 changing the statistic to PASS was written after seeing step-0 results (post-hoc rule change, RULE 26) — ST2-GATE.md header still says FAIL.
- DENSECHUNK-ST2: Verdict label mixes 'NO' and 'not decided at MDE 0.03'; per vocabulary the latter applies (\|Δ\| < 0.03, CI through 0); Opus CI low −0.000.
- DENSECHUNK-ST2: DENSECHUNK-ST2.md:5 'noise floor / non-deterministic generation' paragraph is retracted by the SEEDGEN correction at :18 (keying artefact).
- DENSECHUNK-ST2: Stale status text in DENSECHUNK-ST2.md:8 ('judge running under nohup') left above the auto-written final section.
- DENSECHUNK-ST2: Replays at step 0 ran on wt/packs (dt512 base), generation on cut7-dense2 tree (ST2-GATE caveat 3).
- DENSECHUNK-ST2: Disposition: format v3 not shipped; sidecar copies and tree deleted (DENSECHUNK-ST2.md:19). CLOSED.md lists it as R46 but the result file does not cite the row.
- DETFU: Criterion sha256 bc79a821… matches .sha256 and the truncated citation in DETFU.md (verified).
- DETFU: Diagnostic only; leads to DETMAX (fix arm).
- DETFU: Note: detector input truncation at 126 tokens for long histories not exercised (DETFU.md:27).
- DETMAX: Criterion sha256 a7c784af… matches .sha256 and DETMAX.md citation (verified); patch sha matches the file.
- DETMAX: DETMAX.md:4 says '4 files vs cut 5' but lists only answer.ts and answer.test.ts.
- DETMAX: Patch filename 'detmax-on-cut4.vs-0cfd4a77.patch' says cut4 while the arm is cut 5 + one rule.
- DETMAX: G4 'dev chat messages' include Portuguese turns (v2-031) although the bounty target is English only (descriptive, not a gate conflict).
- DETMAX: Adopted into cut 6 (QUEUE l.694: 'cut 6 = cut 5 + DETMAX'); no CLOSED row (adopted lever).
- DT512: Criterion sha 7fafba05… cited in result matches DT512-criterion.sha256 and shasum; patch sha f9a1979b… matches.
- DT512: DT512-criterion.sha256 records the bare filename (no arms/dt512/ prefix) unlike the sibling dt256 file; cosmetic.
- DT512: Reading line 38 says 'The 256 budget was not tested' — stale since DT256 ran the same day (CHEAPER-LOSS).
- DT512: CLOSED.md R20 lists DT512 as 'closed (CHEAPER-PARITY; 512 adopted)'; 512 is a local engine recommendation, not adopted into a claim cut (status recorded as closed).
- DT512: Phone-time arithmetic (≈ 2–2.5 min on a 12 GB phone) relies on a competitor's public rates; deep research 10-12 later gives 1.9–2.8 min.
- DT512: Aggregates also include 1-seed and 3-seed L2/paired_gap files (L2-H-3seed.opus.json, paired_gap-HvsT-3seed.json) not summarised in the result beyond the SEEDVAR note.
- DT512: Other files: arm.conf, dt512-on-deepthink.patch(+.sha256), tools/{chain-full.sh,chain.sh,dh.sh,l1.sh,l2.sh,remote-run.sh}, aggregates/ (27 files incl. L1/L2/cat/paired_gap/think/gen/chain logs), .locks/.
- DT256: Criterion sha 6d3c325c… cited in result matches DT256-criterion.sha256 and shasum; patch sha 9d91b564… matches.
- DT256: Ladder time '55 s' for 256 (line 39) is the mean of the two seeds' p50 (57.5/53.2), while the TL;DR quotes per-seed values; consistent but different presentations.
- DT256: Criterion anticipated ≈ ×0.35 time; measured ≈ 40 % (not a rule issue: cheaper threshold was p50 ≤ 0.5 × T).
- DT256: Budget binds on 51/51 items both seeds (reasoning 266 = 256 + budget message).
- DT256: CLOSED.md R21 records this arm as closed (CHEAPER-LOSS); the result file itself cites no CLOSED row (predates the registry).
- DT256: Other files: arm.conf, dt256-on-deepthink.patch(+.sha256), tools/{remote-run.sh,stage3.sh}, aggregates/ (21 files: L1/L2/cat/paired_gap vs T,H,D, think-*, gen-*, chain.log, stage3.log), .locks/.
- DT512-V02: Criterion sha 6d91cfb4… cited in result matches DT512V02-criterion.sha256 and shasum.
- DT512-V02: Criterion requires per-category Δ vs TV; result line 18 shows only '? -0.005 (23/55/32)' — category labels missing, so the per-category report is not delivered.
- DT512-V02: Headline H − D CI (+0.021…+0.070) is the two-level figure while the paired-items CI is (+0.019…+0.071); both written, could be confused when quoted.
- DT512-V02: Measurement only: no verdict rule; status 'closed' follows CLOSED.md R20 (grouped with DT512). v0.2 is burnt/dev data per the workspace ruling.
- DT512-V02: Other files: arm.conf, stage.sh, aggregates/ (L2-H-1seed, cat-HvsTV, paired_gap-Hvs{D,K,TV}, think-H/TV, gen-full-s42.txt, stage.log), .locks/.
- EVALFIX: No criterion file (analysis-only, 0 judge calls; no decision rule frozen).
- EVALFIX: Line 4 says 'tie 0 of 1052 rows' while line 27 says '1 of 1052 rows is a tie'; the tie is item-level (order disagreement: one order boar, one ref), not a row-level tie value — wording inconsistent.
- EVALFIX: Not listed in CLOSED.md (tooling/measurement).
- EVALFIX: Power statement lives outside the arm: boar-eval/bench/v0.3/plan/power-statement.md.
- EVALFIX: Other files: tools/{winsties.py,robust_ci.py}, aggregates/{winsties,robust_ci,power}.json.
- FACTS: Step 1 passes at exactly the bar only under the general-property reading; narrower reading = 5/60 -> STOP (FACTS.md:73).
- FACTS: G3 PASS depends on not counting 2 true-slot chat fires; result says G3 FAILS if read as '0 fires' (FACTS.md:91).
- FACTS: Population rule changed (preferred rank -> latest dated) after seeing dev chat v2-045 (disclosed, FACTS.md:81).
- FACTS: Criterion asks for '10 safety-track EN danger items'; the result used 9 EN + 3 PT because the 10 EN set does not exist (FACTS.md:91).
- FACTS: gate.py not run (FACTS.md:95). Criterion sha verified: 4328960e... matches the .sha256 file.
- FACTS-r2: No r2-specific frozen criterion; r2 is a gated rework run under the r1 criterion and DATA-REVIEW recommendations.
- FACTS-r2: HOMONYMS (georgia) rule added beyond section 4's letter (FACTS-r2.md:24).
- FACTS-r2: Recall cost of r2 rules not measured on a trigger set at the time (FACTS-r2.md:67); later measured in FACTS-RECALL (55%).
- FACTS-JUDGE: Dev-motivated selection: the 8 items were chosen because the table covers them; held-out coverage unknown (FACTS-JUDGE.md:15).
- FACTS-JUDGE: Projected +0.027 is an extrapolation from 8 items, not a full v0.1 run; no CI.
- FACTS-JUDGE: Control is a single named source run (spctl-v01-s44).
- FACTS-RECALL: No frozen criterion file or pass/fail bar; measurement only (recall-set sha 414e4de2... matches recall-set.sha256).
- FACTS-RECALL: TL;DR rounds precision to 81% vs table 81.5% (cosmetic).
- FACTS-RECALL: Set became dev after r3 used it to select fixes (FACTS-r3.md:6).
- FACTS-RECALL: Expect values written from memory; f31 Mexico borderline (FACTS-RECALL.md:61).
- FACTS-BLIND: No frozen criterion with a bar for r3 or for set 2; FACTS-r3.md expected >= 80% on set 1 and got 75% (FACTS-r3.md:3).
- FACTS-BLIND: The '27/40 after 2 scorer artefacts' claim is contradicted later: scorer v2 reproduces set 2 at 26/40 because the zloty case is an expect-wording issue, not a fold artefact (FACTS-r4-criterion.md Addendum 1, lines 35-37).
- FACTS-BLIND: Recall-set-2 sha d0dc7512... matches recall-set-2.sha256.
- FACTS-r4: Criterion amended by Addendum 1 before any r4 code (set-2 baseline 27 -> 26/40); sha 23e82776... matches the .sha256 file, so the sha covers the amended text.
- FACTS-r4: Code not committed; kept as facts-r4-WIP.vs-r3.patch (sha 0d8adc47... matches).
- FACTS-r4: G1-G5 not run (stop rule).
- FACTS-r5: 5 allowlist words were added because gate targets needed them (FACTS-r5.md:28, :58): recall cost of rule A on unseen phrasing unmeasured.
- FACTS-r5: nearmiss-lc written by a Claude-family agent (FACTS-r5.md:60). Criterion sha 54ab7a1b... and set shas (e59e99f0..., 517de417...) match.
- FACTS-r6: Verdict FAIL but r6 kept as head and shipped as cut 7 (QUEUE l.770/772), although the criterion said the line closes at r5 on FAIL (FACTS-r6-criterion.md:1-2); disclosed as a head decision.
- FACTS-r6: Internal inconsistency: SET4 'Reading' says 11/12 missed entities are in the table, but the corrected line 17 (Zambezi absent per LCRELAX) plus Denali absent gives 10/12.
- FACTS-r6: Data review third gate (water tower) added after seed-47 sample, not re-sampled (FACTS-r6-SET4.md:13).
- FACTS-r6: CLOSED.md R9 labels the family 'FACTS r1-r7' and '10-04..10-08'; no r7 exists (criterion says 'no r7') and FACTS started 10-06.
- FACTS-r6: Shas verified: criterion 60027d01..., patch 0eee6a0b..., recall-set-4 d2ea2b5c..., nearmiss-lc2 a4428c78... all match.
- LCRELAX: Date inconsistency: file header says 2026-10-08 00:13, but QUEUE l.760 logs it at 00:13 in the 10-06/07 overnight block and r4to's 'LCRELAX NO' is at 09:23 on 10-07; file mtime is Oct 7 00:13.
- LCRELAX: No frozen criterion and no verdict line in the result file; decision lives only in QUEUE l.770.
- LCRELAX: tsc/vitest not run on the probe branch (LCRELAX-PROBE.md:39); recall sets are burnt so gains are upper bounds.
- FOLLOWQ: Criterion's Set line names CHATGATE's 69 expected-search messages, but its decision rule and the run use all 192 messages (171 non-follow-ups) as denominator.
- FOLLOWQ: Non-follow-up failure is a property of applying the variant to every message; result notes a rule-gated design would make it 0 by construction (followed up as FOLLOWQ-G).
- FOLLOWQ: Criterion sha 3988132d... matches FOLLOWQ-criterion.sha256. Traces not committed (boar-eval/runs/kiln/followq/).
- FOLLOWQG: Post-hoc arm (declared in the criterion title).
- FOLLOWQG: Patch file named followqg-on-cut4.vs-0cfd4a77.patch but the base is cut 5 lite (0cfd4a77); no .sha256 file beside the patch (sha only in the report).
- FOLLOWQG: Deviation from FOLLOWQ diagnostic: Q1 replaces only the search query, not health/gate/prompt (FOLLOWQG.md:23).
- FOLLOWQG: Visible position bias; 13-item sample (FOLLOWQG.md:19).
- FOLLOWQG: Not registered in CLOSED.md (R4 cites FOLLOWQ only). Criterion sha ade5c84e... matches.
- FTDATA-PILOT: Table row for the faithfulness bar still reads PENDING (PILOT.md:8) while the appended verdict reports 1/10.
- FTDATA-PILOT: Filter bugs fixed after the first pass on the same data (36/50 -> 41/50), disclosed (PILOT.md:34).
- FTDATA-PILOT: Faithfulness bar met at the limit; FTDATA-1K verdict later states the pilot would also fail under the strict rubric (FTDATA-1K.md:58).
- FTDATA-PILOT: Criterion sha aa09070f... matches.
- FTDATA-1K: Measures table still reads PENDING for the strict review (FTDATA-1K.md:9) while the appended verdict reports 16/20 FAIL.
- FTDATA-1K: Two filter bugs found post-run, reported with both numbers as the criterion requires (982 vs 994).
- FTDATA-1K: Set lacks abstention/partial-context/number-heavy strata required by the recipe (FTDATA-1K.md:51). Criterion sha 1a6b43dc... and prompt-1k sha 37ba84d4... match.
- FTDATA-REJ: Measures table marks kept 632/982 as 'MET' and the strict review as PENDING (FTDATA-REJ.md:24, :32) while the verdict reads kept as 538 FAIL and review 11/20 FAIL.
- FTDATA-REJ: Criterion drafting inconsistency: keep rule at >=100 words vs the frozen filter's 120-word floor; resolved strictly by the coordinator (FTDATA-REJ.md:39, :53).
- FTDATA-REJ: Verifier saw no question, likely inflating sentence-1 drops (269) (FTDATA-REJ.md:40).
- FTDATA-REJ: Human CLAPnq 6/20 baseline comes from arms/humansft (outside this directory). Criterion sha a9136d94... and rej-prompt sha 0901fb37... match.
- G4E4B: Arm seed 44 vs control seed 42 (G4E4B-screen.md:25); no paired CI reported.
- G4E4B: RSS under-reads (mmap'd PLE tensors, swapping host); the Q35 run read 5.4 GiB for the same Qwen file (G4E4B-screen.md:17).
- G4E4B: Criterion's first write was empty (sed error) and was rewritten before the run (QUEUE l.621); the sha d62e54df... matches the rewritten file and the result cites it.
- G4E4B: Mini was not idle during the decode bench (swap grew ~270 MB) (G4E4B-screen.md:22).
- G4ENG: TL;DR (line 3) says 'Unsafe 0 and cw not up are the only passes besides empties' but the gate table (line 16) and the verdict (line 28) mark confident-wrong as FAIL (up by 2 at s45); TL;DR also lists 4 failures while the verdict counts 5.
- G4ENG: Criterion sha 5aecdd03… verified matching G4ENG-criterion.sha256.
- G4ENG: Missing route-gate/verdict-guard codes for Gemma left UNKNOWN (not investigated).
- G4ENG: CLOSED.md row 2 registers this arm, but the result file cites no CLOSED row (predates the registry).
- GATEFID: Premise correction: the be-ship desktop runner already ran the gate by default, so earlier CUT4/SPEEDPACK/CUT5 runs were gate-ON; only committed-runner runs are gate-less.
- GATEFID: Deviation: criterion's 'stored gate-less CUT5-LITE controls' did not exist; a new gate-less cut 4 control was run instead.
- GATEFID: Deviation: implemented with node-llama-cpp controlledEvaluate, not llama-server n_probs/logprobs as the criterion specified.
- GATEFID: v0.1 EN has no chat/small-talk items, so the gate's ANSWER path is untested.
- GATEFID: Criterion sha 753a7181… verified matching .sha256.
- GROUND-ST: GATE.md step-0 cites patch sha 5fd74a85…, but packground2.vs-dt512.patch.sha256 now holds 9acb5160… (patch updated by addendum 1; step-0 patch state no longer on disk).
- GROUND-ST: Criterion lists GROUND-ST.md as an output; no such file exists (justified by the step-0 FAIL, verdict lives in GATE.md).
- GROUND-ST: G2 kit change share passes only via the add-only clause; all changes are 29 %/36 % vs the 15 % bar.
- GROUND-ST: Timestamps differ: GATE.md header says 13:3x, QUEUE l.1025 logs step 0 at 13:20 and file mtimes are 13:26.
- GROUND-ST: D0 step-0 note (kit passage at raw position 0) corrected in D0.md addendum: on the 7 missed items position 0 is the installed pack's own passage.
- GROUND-ST: CLOSED.md row 47 registers the family; result file cites no CLOSED row.
- GROUND-ST: Criterion sha 895d1ebb… verified matching .sha256.
- GROUND-ST addendum 1 (X3 perpack): Addendum header says frozen 13:5x and GATE addendum says 14:1x, but addendum file mtime is 13:20 and QUEUE l.1026 logs the result at 13:27: timestamp inconsistency.
- GROUND-ST addendum 1 (X3 perpack): Addendum sha 77eaf4ca… verified matching .sha256; patch sha 9acb5160… matches .sha256.
- GROUND-ST addendum 1 (X3 perpack): Missed by one item (54 vs 55); D0 shows only a multi-passage-per-pack rule could reach the 7 remaining items.
- HAIKUJUDGE: Result says the L1-PROTOCOL addendum is 'NOT applied; coordinator decides' (line 48), while QUEUE l.800 records it applied at 17:59: result file is stale on that point.
- HAIKUJUDGE: Haiku compresses paired gaps (×0.25); ranking bar passes with a CI through 0.
- HAIKUJUDGE: Leg A2 not run (condition not met), leg B has no Sonnet column.
- HAIKUJUDGE: Criterion sha 58e9c084… verified matching .sha256 and inputs.sha256.
- HAIKUJUDGE: Excluded from CLOSED.md table as a measurement/adopted lever (CLOSED.md:11).
- HFU: Criterion sha 64a6bf1d... matches the .sha256 file and shasum (verified).
- HFU: Learned emergency detector stubbed (lexical path only); detector effect on both baseline and losses is UNKNOWN (Deviation 1).
- HFU: Route replicated from leaf modules, not createAnswerer; PT/ES templates are an extension beyond the EN-only criterion wording.
- HFU: Not registered in CLOSED.md (diagnostic, not a lever).
- HFUFIX: Criterion sha cited abbreviated '306b2274...3807621' matches .sha256 and shasum (verified).
- HFUFIX: Patch file is named hfufix-on-cut4.vs-0cfd4a77.patch although the arm is built on cut 5 (cut5lite 7173c9af): naming inconsistency.
- HFUFIX: G5b failure is a pre-existing lexical false positive ('What are the symptoms?'), not rule-introduced; G3 item set included 23 water probes with no card condition the rule cannot reach.
- HFUFIX: Detector stubbed in G3/G4/G5b scoring.
- HFUFIX: Closure not registered in CLOSED.md.
- HFUFIX2: Criterion sha cited abbreviated '0b813a92...e7017' matches .sha256 and shasum (verified).
- HFUFIX2: Post-hoc scope change declared in the criterion (rescue of HFUFIX).
- HFUFIX2: ws-015 / ws-021 qualify by standalone text but the turn-1 label 'contaminated drinking water' carries no card condition: scope definition vs template mismatch.
- HFUFIX2: Detector stubbed. Closure (HFU-FIX family) not registered in CLOSED.md; QUEUE l.690 keeps it as a documented upstream bug for the PR phase.
- HUMANSFT: Criterion sha 83d4e9d0... matches .sha256 and shasum (verified).
- HUMANSFT: Criterion header says 'frozen 15:4x' but the file was written ≈ 14:3x (erratum noted in HUMANSFT.md:49).
- HUMANSFT: HUMANSFT.md body still says strict review 'PENDING' (l.29, l.41) while the appended verdict (l.51-53) records FAIL: stale text within the same file.
- HUMANSFT: Criterion cites target medians '48 / 23 words'; report shows pre-length 48 / 22 and kept 49 / 45 (CLAPnq / HAGRID) — minor mismatch.
- HUMANSFT: Joint PASS was already unreachable on (b) (HAGRID 0.964) before the review.
- INSTSUBJ: Criterion sha d897731e... matches .sha256 and shasum (verified).
- INSTSUBJ: Gate passed trivially: neither arm finishes ANY lookup2 item instant (0/40, 0/15), so the L0 gate is uninformative; evidence rests on unit tests (QUEUE.md:647).
- INSTSUBJ: INSTSUBJ.md has no verdict line of its own; the adoption verdict lives only in QUEUE.md:647.
- INSTSUBJ: INSTANT-SUBJ was not in the cut 4 desktop identity gate (stub replay only) per CLAIM-REVIEW (QUEUE.md:654).
- INSTSUBJ: Other files present: patch, l0/ traces/cmp, lookup2/items.jsonl (not read), tools/.
- JUDGE2: Criterion sha 4e825da3... (Addendum 1 version) matches .sha256 and shasum (verified); run 1 used criterion 2c3ff0eb..., whose sha was overwritten in the .sha256 file when Addendum 1 was added (QUEUE.md:788).
- JUDGE2: Run 1 stopped by the disk rule at leg A 56/114; full rerun under Addendum 1; supervisor hand-over at leg B 13/114 (driver never restarted).
- JUDGE2: inputs.sha256 pins the old judge.mjs (historical; judge.mjs later changed by FAILCLOSED, QUEUE.md:894).
- JUDGE2: Leg B has no Sonnet-low comparison (not in frozen inputs).
- JUDGE2: shim-qwen/ (dated 2026-10-13) added later for SELFTEST-LOCALJUDGE reuse with Qwen3.6-35B; no .md documents it in this dir.
- JUDGE2: Listed in CLOSED.md as a measurement (not a row).
- JUDGEVAR: Criterion sha 79c085fe… cited in result matches JUDGEVAR-criterion.sha256 and shasum (verified).
- JUDGEVAR: Common-mode CI numbers for H s42 and H−K are deferred to the QUEUE row (QUEUE.md:917: raw cm 0.483–0.583, floor-adj cm 0.350–0.473, H−K 0.120 cm 0.050…0.189) rather than written in JUDGEVAR.md.
- JUDGEVAR: aggregates/bar-cm.json exists but is not referenced in JUDGEVAR.md.
- JUDGEVAR: Criterion header says 'frozen 2026-10-11 03:0x' while result/QUEUE timestamp is 03:00 (file mtimes 02:56 criterion, 03:00 result) - minor timing label inconsistency.
- JUDGEVAR: Measurement arm: CLOSED.md excludes it from the table by design (CLOSED.md:11).
- JUDGEVAR: Other files: tools/agree.mjs, aggregates/{paired-RvsH-s42.opus.json, agree-RvsH-s42.opus.json, paired-HvsK-s42-cm.opus.json, bar-cm.json}.
- K2HALF: No frozen criterion file (.md + .sha256) for K2HALF; the 0.80 bar was pre-registered only in the QUEUE claim row (QUEUE.md:961). Only the patch has a .sha256 (5897e688… matches shasum, verified).
- K2HALF: QUEUE row rounds to 0.18 / 0.29 while the gate file says 0.184 / 0.286.
- K2HALF: Parked as a device-speed candidate in BACKLOG.md:89 and CLOSED.md:66 ('closed at step 0 (quality); parked as a speed candidate').
- K2HALF: Other files: k2half.llama.patch, k2half.llama.patch.sha256, build-tail.log, aggregates/{greedy-gate.json, outputs-public.jsonl}.
- KVQ8: Criterion sha bae45d0c… cited matches KVQ8-criterion.sha256 and shasum (verified).
- KVQ8: Verdict is 'ADOPT as a device-day candidate', not adoption into a cut; device speed/swap never measured (Open section), so it is effectively pending a device day.
- KVQ8: Protocol deviation flagged: both arms run with --backend server instead of the stored node backend (control shown byte-identical to stored cut 4, 60/60).
- KVQ8: Thin margin: pooled -0.0077 vs gate -0.010; s45 alone -0.0142; CI is 90 % not 95 %.
- KVQ8: Not listed in CLOSED.md.
- KVQ8: Other files: tools/kvq8-l1.sh.
- L1CTL: No criterion by design (control run).
- L1CTL: Judge versions differ (judge.v1-med Opus vs judge.v1-low Haiku); slice is all ref-wins so same-winner 20/20 is trivial (stated caveat).
- L1CTL: analysis.txt raw values (ratioHaiku 0.33391915…, ratioOpus 0.33952702…, meanCorrH 1.825, meanCorrO 2.025) are consistent with the rounded numbers in the .md.
- L1CTL: Other files: analysis.txt, tools/{shard_run.sh, analyze.mjs}, shards-4/shard-{0..3}.ids.
- LENGTHSHARE: Criterion sha256 file matches the criterion file (f03087ff…), and the result cites f03087ff…: consistent.
- LENGTHSHARE: Criterion's 'gap to the bar, 0.064' implies H floor-adj 0.436 (2-seed DT512 figure) while the result uses the s42 single-seed 0.412 as the base; the gap-to-bar share is not reported in the result.
- LENGTHSHARE: Criterion stage 4 says descriptive, no LEVER/NO verdict; status 'closed' here means measurement done (CLOSED.md lists LENGTHSHARE as a measurement, not a row).
- LENGTHSHARE: H 'useful ≥ 3' 33.3 % in the H-vs-original row is a two-seed figure mixed into a s42 table (flagged with * in the file).
- LOSSMAP: SHA MISMATCH: LOSSMAP-criterion.sha256 holds 1059f5dd15c80dfb…, which LOSSMAP.md and QUEUE l.918 cite, but shasum -a 256 of the current LOSSMAP-criterion.md is 0c189064df535036… — the criterion file was edited after freezing.
- LOSSMAP: Criterion reading rule says primaries with confidence < 0.6 are 'excluded from the primary table'; the result says they are 'kept in the tables'.
- LOSSMAP: Per-path addendum (QUEUE l.953: health-strict path 0.24 of v0.2 loss) is not written into LOSSMAP.md.
- LOSSMAP: V-para shares carry ≈ ±0.05 (one seed, r 0.5–0.7), stated as UNKNOWN.
- LOCALGATE: No criterion file and no .sha256: the pass rule (agreement ≥ 0.90, FPR ≤ 0.05) is stated only in the result ('frozen rule') and QUEUE l.988.
- LOCALGATE: Laya table leaves the agreement column as '—' although aggregates/localgate.json has values (layaA 0.698/0.82, layaB 0.702/0.814).
- LOCALGATE: Laya result timestamp in file '2026-10-13 00:5x' vs QUEUE l.995 '01:51'.
- LOCALGATE: Stale sections: 'Laya ... not run' (l.31) and 'install still blocked' (l.38) remain above the later Laya result section.
- LOCALGATE: Source sets of the cached requests (wikifull A0 = V-para-based gates, packcond etc.) live under blind/localgate/; the file does not name the benchmark sets explicitly.
- LOCALGATE: Other files: laya-run.log, tools/{harvest.py,sample.py,local_gate.py,local_gate.mjs,analyze.py,cache_schema.py,laya_gate.py}, aggregates/localgate.json, a .venv (laya 0.4.6) inside the arm dir.
- LORA-DIAG: Draft criterion only, not frozen (no .sha256), no result file; gated on FTDATA, whose line was CLOSED (FTDATA-REJ FAIL 11/20, QUEUE l.789; CLOSED.md R12), so the draft is effectively dead unless the data bar is re-registered.
- LORA-DIAG: Header says 'coordinator, 2026-10-07 14:2x' while the status line is stamped 14:13 (status stamped before the draft time).
- LORA-DIAG: Unresolved UNKNOWN list (mlx-lm install, R450 trace paths, Sonnet-low control) left in the draft.
- MOESCREEN: Criterion .sha256 holds 386e983c… (post-Addendum-1 file, matches shasum); the original pre-run sha a3667f51… cited in the result cannot be verified from the directory.
- MOESCREEN: Protocol deviation from the criterion fallback (used 4B closed-book row protocol instead of DEEPREAD R450 minus context); recorded in result.
- MOESCREEN: Result verdict is NO, while CLOSED.md R17 labels it 'not detected at MDE 0.055 (57, 1 seed)'.
- MOESCREEN: Full-run decode median 4.66 tok/s is below the 5 tok/s bar, which was only a smoke-gate (smoke 10.94–11.45 passed); contention noted.
- MOESCREEN: Disk dipped to 24 GiB, 1 GiB below the 25 GiB policy (criterion Addendum 1).
- MOESCREEN-gemma4: Shares MOESCREEN criterion; original sha a3667f51… unverifiable (only Addendum-1 sha 386e983c… stored and matching).
- MOESCREEN-gemma4: Result verdict NO vs CLOSED.md R18 label 'not detected at MDE 0.055 (57, 1 seed)'.
- MOESCREEN-gemma4: Header time range 01:58–03:55 while the GGUF was deleted at 02:44; run window spans judge, not inconsistent but ambiguous.
- MP4B: No own criterion file: uses shared DEEPITER criterion; sha ref 432fddf9… matches arms/deepiter/DEEPITER-criterion.md (shasum verified).
- MP4B: M ran on the MacBook (M1 Pro) and C on the mini (M4): times not comparable across machines (stated caveat).
- MP4B: Length comparison mixes units (393 tokens vs ≈ 51 words).
- MP4B: CLOSED.md R13 notes it is borderline at slice power (CI upper +0.023); full 110 and Opus not run.
- MP4B: Other files: arm.conf, aggregates/ (L1-MvsC-slice.haiku55-low.json, L1-rule-slice.txt, gen-slice.txt, think-C-slice.json, think-M-slice.json), tools/ (gate.py, local-run.sh).
- NAMEDSLOT: Criterion G1 requires 2 new unit tests; result reports +1 test.
- NAMEDSLOT: G3/G4 not run (by stop rule).
- NAMEDSLOT: Other files: namedslot-on-cut6.vs-0cfd4a77.patch, namedslot.vs-cut6.patch.
- NOTES35: Notes median 287 words vs criterion spec of 150–250-word notes; deviation not flagged in the result.
- NOTES35: README.md (tooling) states a single gate 'sources ≥ 15 %' while the criterion's gate A is ≥ 5 % kept AND ≥ 15 % raw (gate B is 15 % kept); README predates the frozen stage split.
- NOTES35: Other files: run-a/ (STATUS, gen.log, hitrate-v02-n300.json, notes.jsonl, pack-manifest-n300.json), smoke/, tools/, topics/ (with .sha256 files).
- NUMCHECK: No frozen criterion file / .sha256 in the arm dir; gate bars (>= 4/16 coverage, 0 false rewrites) are only stated in the result file.
- NUMCHECK: Header says '1 false rewrite on 20 correct V-para answers'; line 19 totals 'false rewrites 4 across 40 correct answers' (1 V-para + 3 v0.2) — consistent but the header reports only V-para.
- NUMCHECK: CLOSED.md row 41 cites this file; the result file itself does not cite a CLOSED row.
- OPUSSHARD: Criterion sha matches the .sha256 file (b78c9550...) — no mismatch.
- OPUSSHARD: Δratio CI excludes 0 (slightly negative) on 10 items; 429 behaviour at claim-pass scale unmeasured (caveat stated in the result).
- ORACLE-ST: Criterion with no result file (arm in progress: runs/ holds only *.requests.jsonl and stage0 traces; aggregates/ empty; logs/stage0.log is 0 bytes).
- ORACLE-ST: Patch sha mismatch: oracle.vs-cut7.patch.sha256 says b893a82772da1f9eaf5739bc70880ac6aa7d8f205149a0e0fb7669942e0e0663, actual shasum -a 256 is dbecafcd5030aa3a2edd05bde715c739a8a8c6576008110301dbc0ab3a344e24 (patch edited after the sha was…
- ORACLE-ST: Criterion sha matches its .sha256 (4c4651b1...), though the .sha256 file holds the bare hash without a filename.
- ORACLE-ST: Run files include an 'off3' cell not named in the criterion (presumably the step-0 3-item OFF check).
- PACKCOND-P1: TL;DR 'floor-adj' numbers (0.55/0.39/0.44) are above_decl, not the headline above_min scale; corrected in Addendum 1 (0.609/0.467/0.508) — TL;DR not updated.
- PACKCOND-P1: K traces joined from cut3 while 3 V-para and 5 v0.2 K judgments were scored on cut6 traces (trace_mismatch), and the TL;DR calls K '4B cut 6'.
- PACKCOND-P1: No criterion (measurement only); V-para subsets n 6 too small.
- PACKCOND-P2: TL;DR says union adds 30 v0.2 items to P1's 32; table: union 53, overlap 23 → 30 new, consistent; text line 28 says '32 -> 59 with it alone' (top100k 27 new) — consistent.
- PACKCOND-P2: TL;DR 'retrieval would reach ... top-100k 3/4 (V-para)' matches table; vital5 and prep replays not run.
- PACKCOND-P2: No criterion (measurement only).
- P4 packGround (PACKCOND P4 step 0): No frozen criterion file/.sha256 for the P4 gate in the arm dir.
- P4 packGround (PACKCOND P4 step 0): packground.vs-dt512.patch sha matches its .sha256 (cb7f239a...).
- P4 packGround (PACKCOND P4 step 0): Not listed as its own CLOSED.md row (R44 covers PACKDENSE; packGround later re-tested as GROUND-ST R47).
- PACKDENSE: Criterion sha e2815dd8... matches .sha256 file.
- PACKDENSE: FAIL declared by projection; the engine patch (packdense.vs-dt512.patch) listed as an output in the criterion was never built.
- PACKDENSE: PACKDENSE.md says 'closed at step 0 (CLOSED.md)' without the row number; CLOSED.md R44 cites it.
- PACKDENSE: Summary uses 'noise p50 0.69 vs targets 0.62' (rounded) while P4B-DIAG.md has 0.687 / 0.617.
- SECTIONHIT: No criterion file (diagnostic; 0 calls).
- SECTIONHIT: Article kept 12/32 here vs 11/32 in P1/P4 (different F0 article definition: any hit chunk's article; DENSECHUNK notes baseline 19 vs 17 for the same reason).
- DENSECHUNK: Gate frozen in QUEUE, no criterion file or .sha256 in the arm dir.
- DENSECHUNK: D0 line 32 says 'part 1 is 23 ≥ 12 (PASS)' while DENSECHUNK.md describes part 1 against the lead router's 5/15 — bar value 12 only appears in D0.
- DENSECHUNK: Later superseded by DENSECHUNK-ST / ST2 (CLOSED R46 says 'supersedes DENSECHUNK D0 parked'); this dir's status 'parked' is stale relative to R46.
- HEALTHQ: Verdict exists only in QUEUE; no result .md and no criterion file in the arm dir.
- HEALTHQ: Not in CLOSED.md.
- PACKROUTE: Criterion sha256 matches the .sha256 file (801e9ac9…).
- PACKROUTE: Criterion lists outputs PACKROUTE.md and packroute.vs-dt512.patch + .sha256; neither exists (stage 1 not run after FAIL; STEP0.md:21 defers the patch to PACKROUTE-2, which wrote packroute2.vs-dt512.patch instead).
- PACKROUTE: STEP0 does not cite a CLOSED row; CLOSED.md R48 covers this arm together with PACKROUTE-2.
- PACKROUTE: G3 cost sub-gate passes for R (×0.64) but G3 fails on lost-context; P itself fails G3.
- PACKROUTE-2: Criterion sha256 matches (d67fd81c…); patch sha matches packroute2.vs-dt512.patch.sha256 (71f783de…).
- PACKROUTE-2: Criterion outputs list STEP0.md and PACKROUTE2.md; neither exists — the 0b diagnostic is appended inside ACCURACY.md.
- PACKROUTE-2: ACCURACY.md:1 says 'stage 0b not run' but a later section (line 34) reports a 0b diagnostic run; header is stale relative to the body.
- PACKROUTE-2: Patch is whole-file diffs that also carry T-K2/packDense2 hunks and needs wikiPack.ts from packdense2.vs-dt512.patch to apply (ACCURACY.md:31).
- PACKROUTE-2: CLOSED.md R48 summarises a break-even ≈ 0.68 not written in ACCURACY.md.
- SELFTEST-SCORES: No criterion file / sha for this measurement in arms/packs (measurement, used for cards).
- SELFTEST-SCORES: 680 new Haiku calls + 40 existing travel rows; the qa-travel-se with-pack row (0.423) is reused from T-K4c.
- SELFTEST-SCORES: Wave-3 addendum states pooled 220 (11 packs) not recomputed; 180 table stands.
- SELFTEST-DEEP: Criterion sha256 matches (70230a55…); measurement with no verdict rule.
- SELFTEST-DEEP: Criterion stage 2 requires 'deep-thinking on all', but boar-firstaid-en items took the health-strict path (p50 0.6 s, no deep prompt) — firstaid is not a deep-tier measurement yet is pooled into the 180 headline.
- SELFTEST-DEEP: H11 split declared at 6/18 runs (BACKLOG META), i.e. mid-run, not in the frozen criterion (criterion split = per pack only).
- WAVE3: No criterion file / sha (pack workflow under PACK-CATALOGUE D-K3 rules).
- WAVE3: Cooking item 003 replaced after Haiku refusals (draw replacements field); no-pack trace spliced for that item only.
- WAVE3: Published on HF per QUEUE l.1044–1046 (product, not a bar lever).
- T-K2: Patch sha in .sha256 (0f0d393a…) matches shasum of packs-sources.vs-dt512.patch.
- T-K2: Worktree wt/packs uncommitted (T-K2.md:2).
- T-K4a: No criterion file / sha in the dir; the frozen rule (share ≤ 0.40 and kit gold not lower, both sets) is referenced but lives elsewhere (PACK-CATALOGUE).
- T-K4a: TL;DR share range '0.03–0.32' vs table minimum 0.026 (v0.1 medlineplus) — rounded.
- T-K4c: No criterion file / sha.
- T-K4c: No no-pack control at the time (T-K4c.md:30); later supplied by SELFTEST-SCORES (without 0.394).
- T-K4d: No criterion file / sha.
- T-K4d: Kit column is P1 F0 (a different probe), not the same measurement (caveat line 33).
- T-K6b: No criterion file / sha in the dir.
- T-K6b: TL;DR '9/13 items' reads as a fraction but means 9 (v0.2) and 13 (v0.1) items per the table's kit-slot parentheses.
- T-K6b: Factbook verdict ambiguous: passes the rule 'as implemented', fails on the literal 'kit's gold' reading (v0.1 −4/−4); left as a coordinator call.
- T-K6b: All-slots gold column inflated by title collisions for these two packs (stated caveat).
- PACKS-L2: Criterion sha256 matches (ace9dd58…).
- PACKS-L2: Criterion without a result file: PACKS-L2.md not yet written; only aggregates/s_off.json exists; logs show P/X and wave-3 sets still being judged at 21:01.
- PACKS-L2: Partial S − OFF Opus aggregate (+0.042, CI low > 0) would meet the CONFIRMED rule but no verdict is written.
- PACKS-L2: Must finish before 2026-10-14 01:00 BRT reset or stop at a set boundary (criterion stop rule).
- PARJUDGE: Criterion sha256 verified: PARJUDGE-criterion.sha256 matches the file (f47b3bb5…) and matches the result's citation.
- PARJUDGE: Result recommends N = 8, but the adopting addendum in arms/L1-PROTOCOL.md:12 sets 'Default N = 4 for L1' (and CLAUDE.md says L1 default N = 4); recommendation and adopted default diverge (reason given in addendum: N = 8 adds ≈ 6 % and stra…
- PARJUDGE: Sequential wall 694 s vs HAIKUJUDGE.md's rounded 11.5 min (disclosed deviation); part of the 4.5x is the removed 1000 ms gap (≈ 114 s), not concurrency.
- PARJUDGE: 429 count can't rule out internal CLI retries (77.7 s straggler may be one); disclosed UNKNOWN.
- PARJUDGE: Other files present: analysis.json, shards-4/ (4 .ids), shards-8/ (8 .ids), tools/shard_run.sh, tools/analyze.mjs.
- PROMPTDIET: Criterion sha256 verified (f8eef6f0… matches .sha256 file).
- PROMPTDIET: The single patch file promptdiet-on-cut3.vs-0cfd4a77.patch was overwritten: PROMPTDIET.md:8 cites sha f5ca5df6… (first build) and PROMPTDIET.md:44 cites bb287dde… (rev 1) for the same filename; the file on disk hashes to bb287dde… (rev 1),…
- PROMPTDIET: TL;DR (line 3) reports only the first build (-150.2, bar met) and was not updated after revision 1's L0 FAIL; reader of the TL;DR alone would think L0 passed.
- PROMPTDIET: Reviewer FAIL text (promptdiet-REVIEW.md:34) estimated restoration would still reach -150 ('should be re-measured'); measured rev 1 missed by 24.3.
- PROMPTDIET: CLOSED R7 combines PROMPTDIET with the later SPEEDPACK L1 (Δ -0.0158 [-0.0411, +0.0082]); that L1 number is not in this arm directory.
- PROMPTDIET: Other files: l0-before.json, l0-after.json, l0-rev1.json, prompt-diff.md, tools/l0-fixed-tokens.mts.
- Q35: Criterion sha256 verified (187bbae9… matches .sha256 and the result's citation).
- Q35: Seed mismatch: criterion froze seed 44, the stored control is seed 42 (disclosed); no paired CI reported.
- Q35: CLOSED.md R1 labels the dense <=9B family (incl. Q35) 'not detected at MDE 0.055 (57, 1 seed)' and lists judge as 'Opus judge.v1', while the result says FAIL (screen bar) and used judge.v1-med; label/judge wording differ between registry a…
- Q35: Other files: bench35.sh, rss35.py, server-anchors-seed.py, runs/ (q35-4b-s44.traces.jsonl, q35-4b-s44.judgments.jsonl, judge.log).
- PROBES: No .md, criterion or result file in the directory; only 5 jsonl data files (file mtimes 2026-10-04).
- PROBES: Held-out sets (arithmetic.heldout.jsonl, water-safety.heldout.jsonl) sit in a researcher-readable arms/ path rather than blind/.
- PROBES: water-safety.heldout.jsonl is BURNED (used for SC v2 tuning per arms/CUT3DEV.md:31).
- PROBES: All five file sha256 prefixes match arms/SHA256SUMS lines 22-26 (checked).
- PROBES: vg-questions.probes.jsonl has no answers, so it cannot measure false fires (arms/CUT3DEV.md:269).
- QUANTCEIL: Verdict line mixes vocabulary: 'NO — not detected at MDE 0.03'; per the criterion (line 30) \|Δ\| < 0.03 with CI through 0 is 'not decided at MDE', and CLOSED.md R37 labels it 'not detected'.
- QUANTCEIL: QUANTCEIL.md:3 claims 'a gain ≥ +0.03 raw is excluded on both sets', but the V-para two-seed CI upper bound is +0.033 (> +0.03), so the exclusion holds only on v0.2.
- QUANTCEIL: Table row for V-para s43 lacks floor-adjusted values (s42 and two-seed rows have them).
- QUANTCEIL: Criterion sha 0c4a8896… cited in the result matches QUANTCEIL-criterion.sha256 and shasum (verified).
- QUANTCEIL: Other files present (names only): aggregates/ (15 files incl. L1-QvsH-QvsH-slice.haiku55-low.json, L2-Q-1seed/2seed.opus.json, paired_gap-QvsH/QvsK-1seed/2seed.json, bucket-delta-v02-s42.opus.txt, cat-QvsH-*.json, think-*.json), tools/ (bu…
- QUANTCEIL: QUEUE.md l.938-948 trace the arm (smoke FAIL-INFRA then PASS, slice, stage 3, s42, final NO at 07:55); EXPOSURES rows present (l.128-129).
- RATIONALEPASS: Result says 'EXPOSURES row not yet written' (RATIONALEPASS.md:30) but EXPOSURES.md l.133 now has the T1 RATIONALEPASS row: stale note.
- RATIONALEPASS: Criterion 'Inputs' says 'Script-only checks, no gateway' for (a)/(b) while the classifier itself uses the Vercel AI Gateway (jev); consistent but easy to misread.
- RATIONALEPASS: Measurement arm with multiple threshold readings, not a single LEVER/NO verdict; status 'closed' assigned because each threshold reading is decisive (O-8 abstention line declared closed in QUEUE l.958).
- RATIONALEPASS: Decline-oracle number is a floor-based bound (no declines exist in the runs), as the result itself notes.
- RATIONALEPASS: Criterion sha 7ab8b381… cited matches the .sha256 file and shasum (verified).
- RATIONALEPASS: Other files present (names only): aggregates/rationalepass-H-v02.json, aggregates/rationalepass-H-vpara.json, tools/rationalepass.py.
- RETHURT: Engine vs closed-book differ in prompt, answer cap (200 vs 450), seeds and length; Δ is indicative, not a clean retrieval effect (stated caveat).
- RETHURT: Scorecard buckets come from 4B ctl-s44 traces, not deep35 runs; per-bucket n 1–7.
- RETHURT: CLOSED.md R14 labels it 'closed (mechanism falsified)' and CLOSED.md l.60 says the RETHURT date is not stated in the report; the criterion header states 'frozen 2026-10-07' and QUEUE l.765-766 gives 03:56/03:59.
- RETHURT: Criterion sha ce950ece… cited matches the .sha256 file and shasum (verified).
- RETHURT: Other files present (names only): analysis-ctl-s44.json, analysis-ctl-s45.json, rethurt-items.csv, rethurt.mjs.
- SC-V2-S5PRIME (sc-fresh3): The arm directory holds only the blind set (README.md + items.jsonl, listed by name, not read); the criterion and result live one level up (arms/sc-v2-S5prime-criterion.md, arms/sc-fresh3-S5prime-result.txt).
- SC-V2-S5PRIME (sc-fresh3): A blind set's plaintext (items.jsonl) sits under rnd/research/coordinator/arms/, outside blind/; EXPOSURES.md l.87 marks sc-fresh3 'burnt' (1 scoring).
- SC-V2-S5PRIME (sc-fresh3): Criterion says 'frozen 2026-10-04, before set #3 exists', but the criterion file mtime (11:55) is later than the sc-fresh3 directory/README (11:53); the result is 11:57. May reflect a later touch, but the freeze order cannot be confirmed f…
- SC-V2-S5PRIME (sc-fresh3): Criterion .sha256 file holds two lines (criterion 47e6ff05… and tools/sc-fresh3.mts 79994e5e…); the criterion hash matches shasum (verified). The result file does not cite the criterion sha.
- SC-V2-S5PRIME (sc-fresh3): QUEUE l.556 states the false-fire bar as '≤ 2' (of 50), equivalent to the criterion's '≤ 1 per 25'. Follow-up SC v3 S5″ on sc-fresh4 also FAIL (QUEUE l.562); water card + SC trigger parked for the bounty.
- SC-V2-S5PRIME (sc-fresh3): Not registered in CLOSED.md.
- SC-V3-S5SECOND (SC v3 trigger S5″ on sc…: The arm directory sc-fresh4/ holds only README.md + items.jsonl (the set); criterion and result live as sibling files in arms/ root (sc-v3-S5second-criterion.md, sc-fresh4-S5second-result.txt).
- SC-V3-S5SECOND (SC v3 trigger S5″ on sc…: Criterion sha verified: sc-v3-S5second-criterion.sha256 = 4aa47ee7… matches shasum; the .sha256 file also carries a second line for tools/sc-fresh4.mts (726cf47d…), not verified here.
- SC-V3-S5SECOND (SC v3 trigger S5″ on sc…: Result file carries no date and no criterion sha reference; date taken from the criterion header (frozen 2026-10-04) and QUEUE l.560-562 under the 2026-10-03 section.
- SC-V3-S5SECOND (SC v3 trigger S5″ on sc…: Not registered in CLOSED.md (no row found); QUEUE l.562 records outcome as 'Water card + SC trigger changes PARKED for the bounty' — status 'closed' (decisive FAIL) vs 'parked' wording differs.
- SC-V3-S5SECOND (SC v3 trigger S5″ on sc…: Set #4 is blind-written but sits under arms/ rather than blind/.
- SEEDGEN: No criterion file or .sha256 (diagnostic/tooling arm; QUEUE l.1019 and BACKLOG l.25 treat it as done tooling, RULE 27).
- SEEDGEN: 2 items (qa-travel-se-004, -012) with equal promptTokens but different answers remain UNVERIFIED (ON prompts not dumped).
- SEEDGEN: Only MacBook CPU path at -t 4 probed; mini, Metal, deep tier unmeasured (stated caveat).
- SEEDGEN: runs/ contains stray duplicate files with spaces in names (same-A1 A2-.json, same-A1 B1-.json, same-A2 B2-.json, same-B1 B2-.json) beside the hyphenated ones.
- SEEDGEN: Other files present: tools/{probe.sh, run_probe.sh, same_answer.py}; runs/{A1,A2,B1,B2}.traces.{jsonl,log,server.log,status}, B1/B2.prompts.jsonl, same-*.json, same-orig-A1.json, same-st2-qa-health-se.json, probe.log.
- SEEDSPEC (T7): No frozen criterion file/.sha256 in the arm dir; the >= 50 % bar comes from DEEP-RESEARCH-2026-10-12.md T7 row.
- SEEDSPEC (T7): Set A is defined as 26 items wrong_fact on s42 (LOSSMAP) but jev labels only 24/26 wrong on s42 (labeller vs LOSSMAP disagreement, not discussed).
- SEEDSPEC (T7): Result file is undated; date from BACKLOG l.61 / CLOSED row 43 (10-12) and QUEUE l.964.
- SEEDSPEC (T7): CLOSED.md row 43 cites arms/seedspec/SEEDSPEC.md (closed at step 0), but SEEDSPEC.md itself cites no CLOSED row.
- SEEDSPEC (T7): jev is a gut-check labeller with no human audit (stated caveat); jev cache stored under blind/V-para/runs-dt512/seedspec-cache/.
- SEEDSPEC (T7): Other files: aggregates/seedspec-H-vpara.json, tools/seedspec.py.
- SEEDVAR: Criterion sha verified: SEEDVAR-criterion.sha256 f7196323… matches shasum and the sha cited in SEEDVAR.md:1.
- SEEDVAR: Measurement-only arm (no verdict rule); status set to 'tooling' for lack of a 'measurement' value; CLOSED.md l.11 lists it as a measurement not in the table.
- SEEDVAR: T's per-item r 0.53 is not independent of H (shares first 512 thinking tokens per seed) — stated caveat.
- SEEDVAR: QUEUE l.876 writes per-item r as '0.48–0.68' while SEEDVAR.md TL;DR/L1-PROTOCOL say '0.5–0.7' (rounding only, consistent with table).
- SEEDVAR: Requested outputs present: DT512.md note (dt512/DT512.md:44) and L1-PROTOCOL addendum (L1-PROTOCOL.md:27).
- SEEDVAR: v0.2 rows labelled as existing (not new exposure); v0.2 is burnt/dev per CLAUDE.md.
- SEEDVAR: Other files: seedvar.mjs; aggregates/{chain-s44.log, seedvar-H-3seed.opus.json, think-H-s44.json, think-H-s44.perItem.json}.
- SFT4B: Criterion without a result file: SFT4B.md does not exist; only stage 0 (STOP environment) and pipeline research written.
- SFT4B: Criterion and addendum shas verified (5853b8ea… and 1730f4f9… match their .sha256 files).
- SFT4B: Criterion header says frozen '20:0x' while QUEUE l.1059 logs the freeze at 19:40.
- SFT4B: data/ holds train.v2.jsonl / holdout.v2.jsonl (QUEUE l.1060 orders a v2 target spec 35–60 words) but no .md documents v2 datasets or their shas; addendum says data unchanged and PIPELINE-OPTIONS step 6 points at data/train.jsonl — ambiguou…
- SFT4B: Addendum 1 replaces the frozen bf16/merge/Q4_K_M recipe (training base 8-bit MLX, runtime GGUF LoRA, new model id 'qwen3-4b-instruct-2507-q4km-sft4b' vs criterion 'qwen3-4b-instruct-2507-sft4b-q4km'), frozen before stage 1 data use.
- SFT4B: Status ambiguity: QUEUE l.1061 says parked; l.1066 says unblocked, stage 1 launchable after 2026-10-14 01:00; not launched per files.
- SFT4B: Criterion budget cites '31 GiB free now' while STAGE0 reports 30 → 29 GiB.
- SFT4B: Other files present: aggregates/{disjoint,filter,filter-v2,render-validate}.json, tools/ (disjoint_check.py, filter_jev.py, filter_v2.py, render_*.py/mts, write_*.py/sh, mini/), runs/ (writer, writer-v2, jev-cache, retry lists, logs), data…
- SPECDEC: Criterion sha verified (66361511… matches; the .sha256 line records path 'arms/specdec/SPECDEC-criterion.md').
- SPECDEC: G1 bar written for 60 items but only 50 model-path prompts exist; translated to ≥ 48/50 (declared deviation).
- SPECDEC: Qwen3-0.6B Q4_K_M not tested (official repo has only Q8_0).
- SPECDEC: Not registered in CLOSED.md (no row found for SPECDEC) although verdict is a decisive NO-GO.
- SPECDEC: Other files present: data/ (prompts, requests, traces, res/, res_c/, res_lp/, analysis/projection/ties outputs, logs), tools/ (dl.sh, specdec-*.sh, q15-verbose.sh, specdec_{replay,analyze,project,ties}.py).
- SPEEDPACK: Criterion sha verified (c0bceaf6… matches); patch shas verified (bb3dbde1… final, caeaf5ce… Run A).
- SPEEDPACK: Control confident-wrong count 5/5 differs from KVQ8's 4/5 for the same control (reused verdict on vit-cry-007); noted in the file, gate unaffected.
- SPEEDPACK: Literal truncation check flags 3 control answers per seed (citation-marker endings) — criterion-wording artefact.
- SPEEDPACK: Criterion premise 'cap only, no length effect from the diet' falsified (mean tokens rose).
- SPEEDPACK: Result file cites no CLOSED row; CLOSED.md row 7 (PROMPTDIET -> SPEEDPACK L1) registers it as closed.
- SPEEDPACK: Other files present: analysis-output.txt, l0-speedpack.json, speedpack-on-cut4.vs-0cfd4a77.patch, speedpack-runA-capnotbinding.patch, tools/ (analyze.py, judge-arm.sh, prep_judge.py, speedpack-l1.sh).
- STACK: Criterion sha verified (56ed7ccf… matches); stack.vs-cut7.patch sha verified (0049d3c3… matches).
- STACK: Replay tree is dt512-based wt/groundst, not cut 7 (differs in FACTS hunks) — declared caveat.
- STACK: Uses v0.2 (bench-v02) script-only replays under blind/bench-v02/runs-packs (counts + ids); EXPOSURES row per QUEUE l.1037.
- STACK: Measurement continued under a separate criterion (STACK-2) after the FAIL; GATE.md cites no CLOSED row (R49 is cited by STACK.md).
- STACK: Other files present: aggregates/gate.json, tools/{replay-stack.ts,.sh, run_step0.sh, gate.py}, runs/{st180-all9, v01-kit, v01-all9}.jsonl, runs/step0.log.
- STACK-2: Criterion sha verified (e875d463… matches; aggregates/stack.json records criterion_sha256 e875d463…).
- STACK-2: v0.1 no-harm judged 228 calls (57 items) vs 240 planned in the criterion (3 venue-list items never graded) — explained in caveat 4.
- STACK-2: P and S Haiku rows judged in earlier sessions (same judge model/settings); only system label differs.
- STACK-2: v0.1 OFF identity vs kit-only replay 53/60 (7 tree differences: FACTS items + dng-002), not stack effects.
- STACK-2: Disk dipped to 7.1 GiB (below the 8 GiB floor) during the run, attributed to causes outside the arm; runner guard paused simplewiki.
- STACK-2: Expected_delta (+0.02) < MDE declared up front, so 'not decided' was the anticipated outcome.
- STACK-2: Other files present: aggregates/{stack.json, 11 *.floor_metrics.txt}, tools/{mkreq.py, run_stack.sh, chain.sh, judge_stack.sh, stack_agg.py}, runs/ (114 entries: requests, traces, judgments, ids, shards, logs, chain.log, judge.log).
- SYNTHDEEP: No frozen criterion file or .sha256: the gate is the B7 row of LOOP-PROGRAM §3 as written; patch sha256 41a37bc2… verified matching synthdeep.vs-dt512.patch.sha256
- SYNTHDEEP: Internal inconsistency: SYNTHDEEP.md table says kept lists changed on vs off = 2 (curated kit), while REPLAY-v01.md:18 says kept lists change on 4/60 items (lan-cmp-001/002/005, vit-sci-002)
- SYNTHDEEP: Source commit ambiguity: LOOP-PROGRAM B7 and QUEUE l.88 cite cmpsplit v2.1 as 2430f5bf, which PATCH.md:3 says is not in the boar-app repo (actual source = uncommitted diff on 0cfd4a77)
- SYNTHDEEP: Gate wording differs: LOOP-PROGRAM says 'both sides in the prompt', SYNTHDEEP measures 'both sides in the kept sources'
- SYNTHDEEP: CLOSED.md row 38 registers it; the result file itself cites no CLOSED row
- SYNTHDEEP: Other files present: aggregates/replay-v01.json, replay-v01-vital.json; logs/ (4); replay-*.jsonl (4); tools/ (gate.py, gate_vital.py, replay-split.ts/.sh, run-replays.sh, diff-vs-dt512.scratch.test.ts)
- T1-DEEP35: Criterion never frozen (no .sha256) and no result file
- T1-DEEP35: Stale draft: QUEUE l.709 lists it as prepared, not authorised; the deep-tier question was later measured by DEEPVPARA (10-08) per CLAUDE.md, but this file was never updated or marked superseded
- T1-DEEP35: Header still states r4to's '4B only' standing decision (2026-10-05), superseded by later deep-tier work
- THINK4B: Criterion sha256 d3fe2522… cited in THINK4B.md:1 matches THINK4B-criterion.sha256 and shasum; patch 6a977a29… matches
- THINK4B: Status discrepancy: result file says NO (near-lever), but CLOSED.md row 10 relabels it 'not detected at MDE 0.06 (51, 1 seed)'
- THINK4B: Criterion stage 5 specifies a two-seed verdict (s42 then s43); the run stopped after s42 Opus on a '+0.03 to continue' reading that the criterion text does not state explicitly for the s42→s43 step (ambiguous)
- THINK4B: DEVIATION 1 recorded: criterion's smoke clause 'budgetExceeded false' was wrong (flag counts budget-message tokens); printed, not gated
- THINK4B: Y (256) is a slice-only sub-arm folded into this record (same verdict)
- THINK4B: Other files present: aggregates/ (L1/L2 jsons, rule txts, think-*.json, logs, cat-ZvsK, paired_gap-ZvsK/ZvsD), tools/gate.py, tools/remote-run.sh, arm-Y/Z(-l2).conf, think4b512-on-cut6.patch(+sha256), .locks/
- THINK4B-V02: Criterion sha256 bfdcfbe0… cited in THINK4B.md:38 matches THINK4B-V02-criterion.sha256 and shasum
- THINK4B-V02: Status discrepancy: addendum says NO, CLOSED.md row 11 relabels it 'not detected at MDE 0.025 (110, 1 seed)' and names an Opus 220-call pass as the reopen
- THINK4B-V02: Verdict rests on Haiku only (no Opus); the addendum argues the Haiku–Opus gap (≈ +0.02) would not cross +0.03, an extrapolation not measured
- THREADS2: No criterion and no result; dormant pending a device
- THREADS2: No QUEUE row names THREADS2 (grep found only the web-sweep line l.778); CLAUDE.md describes it as dormant ('a competitor team ×1.7 decode')
- THREADS2: Native batch-thread patch need marked UNKNOWN
- TRAVELSEL: Round 2 one-shot p50 ratio in L0-round2.txt is 1.067, while TRAVELSEL.md reports 0.979x from a separate 3-run interleaved measurement; the 1.067 figure is not mentioned in the report (still within the 1.2x bar).
- TRAVELSEL: Builder disclosed the frozen gold-facts.json was flawed (trv-004 gold in 'Lisbon' article while cut 3 retrieves 'Lisbon Airport'; trv-002 plug sentence already in base context), capping the gate structurally; gold not edited (sha 75aaaac1.…
- TRAVELSEL: Round 2 added a rule beyond the criterion text ('get from A to B' -> B as destination).
- TRAVELSEL: L1 section of the criterion never executed (killed at L0 per QUEUE l.616).
- TRAVELSEL: Not registered in CLOSED.md (no row found).
- TRAVELSEL: Criterion sha e4ffcb5c... matches .sha256; patch sha fb2fdd1d... verified.
- VENUEGPS: VENUEGPS-criterion.sha256 records the path as 'arms/venuegps/VENUEGPS-criterion.md' (other .sha256 files use bare names); hash 378f11ec... matches the file.
- VENUEGPS: Deviation: run on a MacBook-local git-archive tree instead of run.sh on the mini; no learned detector.
- VENUEGPS: Gate 'byte-identical to cut 6' failed cross-machine for 3/5 non-venue items (generation only); an extra same-machine gate was added post hoc (5/5).
- VENUEGPS: runner-location.patch sha 1d10fc58... verified against its .sha256.
- VENUEGPS: Not registered in CLOSED.md (no row found).
- VENUEGPS-2: Gate reference deviates from criterion: criterion specified the VENUEGPS option-on run, but it had no non-venue items, so the VENUEGPS OFF run (vg-offnv-s42) was used.
- VENUEGPS-2: tools/cause.mjs regex fixed during the arm (coverage-full/partial had been counted as no-hit).
- VENUEGPS-2: Gold and engine both derive from OSM diet tags: proves plumbing, not venue quality (stated caveat).
- VENUEGPS-2: Status lever-adopted is in the sense of claim wording + runner option committed (boar-eval 0ccab93 per QUEUE l.795), not an engine change.
- VENUEGPS-2: Criterion sha baf48960... matches .sha256.
- VENUEGPS-2: Not registered in CLOSED.md (no row found).
- VG-PROBE-Q: Directory holds only README.md + items.jsonl; the criterion (vg-S-criterion.md, sha da3a50c4... verified) and result (vg-S-REVIEW.md) live in arms/ top level.
- VG-PROBE-Q: Set became DEV after VG-S (QUEUE l.570: 'vg-probe-q now DEV'), later used to tune VG v4.
- VG-PROBE-Q: Items sha matches README.
- VG-PROBE-Q2: Directory holds only README.md + items.jsonl; criterion vg4-S2-criterion.md (sha 1f31215b... verified) and result vg4-S2-REVIEW.md live in arms/ top level.
- VG-PROBE-Q2: Items sha matches README.
- VITALPACK-DEEP: CLOSED.md R34 (line 53) records this closure but its 'Would reopen it' cell is stale: says VITALPACK-ADD 'L1 queued Mon 10-12', while VITALADD was since judged (NO at slice; not detected at L2 2026-10-13)
- VITALPACK-DEEP: Result file does not cite CLOSED row number
- VITALPACK-DEEP: Criterion sha 40191652… matches VITALPACK-criterion.sha256 (verified)
- VITALPACK-ADD: No CLOSED.md row for VITALADD; R34 still describes it as 'L1 queued Mon 10-12' (stale)
- VITALPACK-ADD: Header verdict (line 3) and 'Cheapest powered test → parked list' (line 14) are superseded by the 2026-10-13 addendum, which spends that test; header not updated
- VITALPACK-ADD: Stage 3 CONTINUE rule is an OR (Opus Δ > 0 or CI low > −0.01): Δ +0.0012 > 0 meets the first clause literally, but coordinator stopped anyway (not detected) — rule reading departs from the literal criterion
- VITALPACK-ADD: Full-set Haiku control is TV (deep+think 1024), labelled post-hoc, not H as frozen
- VITALPACK-ADD: Criterion's Verdict vocabulary decides only at V-para two seeds; stage 4 never run (s43 traces never generated), so the frozen verdict was never reached
- VITALPACK-ADD: Smoke rule mis-specified for health item dng-002 (addendum 1 fixes reading before judge calls)
- VITALPACK-ADD: Shas verified: criterion 7c9f7e65… and smoke addendum d677d920… match .sha256 files; dt512 patch f7a1f394… matches its .sha256
- WIKIFULL-STAGE-A: STAGE-A.md body below the header is the stale runner report written while RUNNING (4/15 shards, pooled 2/34, 'To do after the loop: replace this file') — never replaced, only a header prepended
- WIKIFULL-STAGE-A: Header says stage B is 'the 2026-09-26 index delta' but STAGE-B.md uses the enwiki 20261001 dump (criterion: 2026-10-01 dump)
- WIKIFULL-STAGE-A: v0.2 stage-A spend: [usage detail removed] here vs QUEUE l.990 [usage detail removed] (14/15 at that time) — timing, not contradiction
- WIKIFULL-STAGE-A: Stray file tools/ikifull_gate.py (truncated name) beside wikifull_gate.py
- WIKIFULL-STAGE-A: quote_supports is a jev boolean proxy, not a verbatim quote check
- WIKIFULL-STAGE-A: Criterion sha ee81ad30… matches .sha256 (verified)
- WIKIFULL-REOPEN: Verdict is a lower bound: 72 % of old-id delta pages not fetched (6 GB cap)
- WIKIFULL-REOPEN: Text path differs from FineWiki (tables and templates dropped in B), biases B down
- WIKIFULL-REOPEN: stageA_pool.py prints v0.2 band 'REOPEN 38/78' by applying V-para bands to dev context (flagged as not a decision)
- WIKIFULL-REOPEN: Result file says MARGINAL 'not closed either', yet CLOSED.md R45 lists it as closed (MARGINAL, no WIKI-ALL arm) — label mismatch between the frozen band wording and the registry
- WIKIFULL-REOPEN: STAGE-B says EXPOSURES row + QUEUE entry by coordinator; QUEUE l.994 has the entry
- WIKIFULL-REOPEN: Criterion sha ee81ad30… matches .sha256 (verified)
- WIKISECTION: No frozen criterion file or .sha256 in the directory; the bar lives in BACKLOG §1 row 1 and the result title
- WIKISECTION: Scope correction 2026-10-12 withdraws the 'facts are not in Wikipedia' reading (top-100k indexed text and kept-source items only); verdict line and Reading paragraph (line 13: 'No section-level ... packing of Wikipedia can supply them') le…
- WIKISECTION: Result file does not cite its CLOSED row (CLOSED.md R39)
- WIKISECTION-H5b: No frozen criterion or bar for H5b; v0.2 compared to the H5 40 % bar informally
- WIKISECTION-H5b: Original reading ('facts are not in Wikipedia at all') withdrawn by the correction and superseded by WIKIFULL (pooled 9/34 verified)
- WIKISECTION-H5b: v0.2 hits unverified (no quote_supports); BM25+jev false positives acknowledged
- AR: Result file has no overall verdict line and does not cite the criterion sha (sha only in CUT3DEV.md:281); A3 PASS is not written in the result file, only in CUT3DEV.md.
- AR: A3 bar (>= 30 positives exact) is met only by pooling 22 unit-test positives with 29/30 dev probes; the result file shows 29/30 alone.
- AR: CUT3DEV.md:295 says the crypto pack has no EIP-7251 constants table; QUEUE.md:579 (Knowledge-pack sizing) later corrects: 'EIP-7251 table IS in the crypto pack (selection problem, not coverage)'. A2 rationale is therefore stale.
- AR: A2 (vit-cry-009) FAIL reported separately by design; not implemented.
- SC-L0 (SC v1 trigger: water-safety card…: Result does not cite the criterion sha; sha matches .sha256 (verified).
- SC-L0 (SC v1 trigger: water-safety card…: sc-v2-L0-recheck.txt reports S5 25/25 on a set already burned for v2 tuning (disclosed in CUT3DEV.md:31) — not evidence.
- SC-L0 (SC v1 trigger: water-safety card…: QUEUE.md:549 lists sc patch 8c93bc8d… and stack 0cb058f1…, which do not match the on-disk SHA256SUMS (80bcb148…, a77b3b34…): the patches were re-cut later with SC v3 + reviewed text; the original patches are not on disk.
- SC-L0 (SC v1 trigger: water-safety card…: sc-on-cut2.vs-0cfd4a77.patch on disk is SC v3 + reviewed text, not the v1 trigger this L0 tested.
- SC-v2-S5prime: Result file states 'trigger sha256s verified' but does not cite the criterion sha; criterion and runner shas match .sha256 (verified).
- SC-v2-S5prime: Set #3 is a blind-written set stored under arms/sc-fresh3/, not under blind/; burned after one scoring.
- SC-v3-S5second: sc-v3-dev-result.txt lines 2-3 print the 'v1' column as 22/22 and 25/25 (identical to v2), whereas the same lines in sc-v2-dev-result.txt show v1 21/22 and 18/25: the baseline label in the v3 file appears to be the v2 trigger mislabelled a…
- SC-v3-S5second: Ruling is PARKED for the bounty (QUEUE.md:562, CUT3DEV.md:134) rather than a plain closure; dng-005 flood-water gap stays.
- SC-v3-S5second: Result does not cite the criterion sha (shas verified OK).
- SC-S6 / SBt (reviewed snakebite card te…: No own frozen criterion beyond S6 in sc-L0-criterion.md; the water text was approved but never shipped (water card parked).
- SC-S6 / SBt (reviewed snakebite card te…: sc-L0-result.txt still shows 'S6 pending (reviewer)'; the APPROVE-after-edits outcome is only in sc-REVIEW.md and CUT3DEV.md.
- VG-L0 (verdict guard v1): Criterion verdict rule ('PASS if V1–V4 hold') gives FAIL (V2 FAIL); the coordinator ruled a 'disclosed exception' (CUT3DEV.md:13) and continued — adoption rests on later rounds (v2 V5′, v3 VG-S).
- VG-L0 (verdict guard v1): V5 FAILED on v1 (1 WRONG); the line was adopted only as v3.
- VG-L0 (verdict guard v1): Disclosure: patterns written while looking at the target traces, so V1 is optimistic (CUT3DEV.md:269).
- VG-L0 (verdict guard v1): Standalone vg-on-cut2 patch stays v1 (CUT3DEV.md:205).
- VG-V5prime (VG v2 re-review + v3 equiva…: No own frozen criterion file for V5′; it reuses the V5 bar from vg-L0-criterion.md.
- VG-V5prime (VG v2 re-review + v3 equiva…: vg-equiv-v3-vs-v2.txt:2 labels the output 'v2 repairs: 36 -> vg-repairs-v3.jsonl' (label says v2 for the v3 file); vg-repairs-v2/v3 differ in bytes (sameAsV1 vs sameAsV2 field) while both have 36 rows.
- VG-S (VG v3 ship gate): Reviewer states 'no engine errors visible' rather than a counted 0 engine errors as the criterion requires.
- VG-S (VG v3 ship gate): Result file vg-S-apply.txt does not cite the criterion sha (reviewer re-checked it, matches).
- VG4-S2 (VG v4 threshold/superlative shi…: CUT3DEV.md:39 'Round 6 ... not adopted, awaits the coordinator's fresh probe set #2' is stale: CUT3DEV.md was never updated with the VG-S2 FAIL (only QUEUE.md:577 and vg4-S2-REVIEW.md).
- VG4-S2 (VG v4 threshold/superlative shi…: vg4-equiv-vs-v3.txt:4 labels 'v2 repairs: 2 -> vg4-newfires.jsonl' (wrong version label).
- VG4-S2 (VG v4 threshold/superlative shi…: The DEV-tuning fix for vgq-089 (Lake Superior scoped superlative, CUT3DEV.md:71) did not generalise: the WRONG fire vgq2-002 is again Lake Superior (qualifier 'by volume' ignored).
- VG4-S2 (VG v4 threshold/superlative shi…: No CLOSED.md row for the VG line despite 'VG line CLOSED' in QUEUE.md:577.
- CUT3DEV (cut 3 build: cut 2 + VG v3 + A…: CUT3DEV.md TL;DR table (lines 6-10) still shows the round-1 state (SC S5 FAIL, VG V5 pending) and never records the VG-S2 FAIL; document reads as stale at the top.
- CUT3DEV (cut 3 build: cut 2 + VG v3 + A…: QUEUE.md:549 reports 'units stack 1280/1280' and patch shas sc 8c93bc8d…, stack 0cb058f1… that differ from the on-disk patches (stack 1293/1293, a77b3b34…; sc 80bcb148…): later re-cuts overwrote the same filenames.
- CUT3DEV (cut 3 build: cut 2 + VG v3 + A…: The superseded candidate 99baf3bc… (CUT3DEV.md:144) is not on disk (same filename now holds a67c70db…).
- CUT3DEV (cut 3 build: cut 2 + VG v3 + A…: replay-stack-vs-cut2.txt names the stack as 81d946fb (SC v1 commit), not the on-disk stack HEAD 35cd4c30; replay predates later rounds.
- CUT3DEV (cut 3 build: cut 2 + VG v3 + A…: L1 Δ +0.029 was measured with VG v1 + AR; transfer to v3 rests on byte-identity of judged repairs (QUEUE.md:567).
- CUT3DEV (cut 3 build: cut 2 + VG v3 + A…: Cut 3 0.566 vs a later cut-4 control 0.559 discrepancy reconciled only as 'likely cause' (QUEUE.md:676).
- CUT3DEV (cut 3 build: cut 2 + VG v3 + A…: SHA256SUMS: all 30 entries verify OK; SHA256SUMS.new-arms covers cvo/ and cryptosel/ criteria (not cut-3 era), both verify OK.
- SIGNAL20 (signal slices): QUEUE.md:750 says crypto 7/20, but signal20.csv category column has 6 'crypto' rows (vit-cry-009 is categorised 'reasoning'); the 7 counts id prefix.
- SIGNAL20 (signal slices): L1-PROTOCOL.md:3 describes the control as '(cut 3 = cut 6 answers, seed 44)' on spctl (SPEEDPACK control) — ambiguous cut labelling.
- SIGNAL20 (signal slices): Superseded by random20 for arms frozen after 2026-10-11 (signal20 inflated slice Δ).
- SIGNAL20 (signal slices): v0.2/V-para slice files hold only ids of held-out-style sets; no plaintext.
- RANDOM20 (random stratified slices): L1-PROTOCOL addendum is dated 2026-10-11, but the QUEUE row creating the files (QUEUE.md:905, 22:09) sits in the 2026-10-10 evening session; file mtimes are Oct 10 22:02.
- L1-PROTOCOL (judge triage protocol): Protocol file has no own .sha256 (addenda cite their arms' criterion shas).
- L1-PROTOCOL (judge triage protocol): Line 3 control description '(cut 3 = cut 6 answers, seed 44)' is ambiguous.
- GEMMATHINK: Criterion sha256 file (46e058d3…) matches shasum of GEMMATHINK-criterion.md and the sha cited in GEMMATHINK.md:1 — consistent.
- GEMMATHINK: L1 parity-faster speed clause passed only marginally (106.2 ≤ 107.2 s, ratio 0.743), as the result notes.
- GEMMATHINK: Slice requests sha (01e6955d…) required by criterion l.9 is recorded only in QUEUE.md:829, not in GEMMATHINK.md.
- GEMMATHINK: Mixed units for RSS (G 7.7 GB vs T ≈ 10 GiB) in GEMMATHINK.md:20/36.
- GEMMATHINK: CLOSED.md row R19 labels it closed citing 'CI upper +0.003' (CI includes 0; closure rests on CI excluding +0.03 / parity clause failure).
- GEMMATHINK: Other files present (not .md): arm.conf, aggregates/ (28 files: L1/L2 JSON, paired_gap GvsT/GvsD 1seed/2seed, cat-GvsT, think-G/T, gen-*, smoke-G.txt, logs), tools/ (getmodel.sh, gt.sh, l1.sh, l2.sh, mktree.sh, remote-run.sh).
- K3-ON-CUT2: No .sha256 sibling for k3-criterion.md; the result cites sha 7d8fcd81... which matches shasum of the current criterion file
- K3-ON-CUT2: Patch sha c60edc53... matches the file on disk
- K3-ON-CUT2: Gates 1, 2, 4 (delta ratio, CI90, confident-wrong) not measured by design (cost rule)
- K3-ON-CUT2: No CLOSED.md row for this decisive NO-ADOPT (LEDGER-AUDIT noted root criteria were not covered)
- TF2-ON-CUT2: No .sha256 sibling for tf2-criterion.md; cited sha 2e0dec75... matches shasum of current file
- TF2-ON-CUT2: Patch sha bd39546d... matches file on disk
- TF2-ON-CUT2: Criterion G3 coordinator text says 'Japan mean >= cut 2's 0.36' while the bracketed tightening uses 0.356; result applies 0.356
- TF2-ON-CUT2: Result itself reads the −0.018 Japan drop as inside judge noise (tf2 'about neutral'), yet frozen bar forces NO-GO
- TF2-ON-CUT2: No CLOSED.md row for this decisive NO-GO
- CUT3-CONFIRM: No .sha256 sibling for cut3-confirm-criterion.md; cited sha fdd06c4a... matches shasum of current file
- CUT3-CONFIRM: Patch sha a67c70db... matches arms/cut3-final-candidate.vs-0cfd4a77.patch
- CUT3-CONFIRM: Ratio uses verdict reuse (52 cut 2 verdicts + 5 new/arm); QUEUE.md:676 later reconciles cut 3 0.566 vs cut 4 control 0.559 on identical answers as judge sampling noise from mixed reuse sources
- CUT3-CONFIRM: All changed items are dev items that motivated the fixes (v0.1), so the +0.032 is dev-set
- CUT3-VGAR-L1: No .sha256 sibling for cut3-vgar-L1-criterion.md; cited sha bf96feb6... matches shasum of current file
- CUT3-VGAR-L1: Patch sha 9622c5c1... matches arms/cut3dev-vgar.vs-0cfd4a77.patch
- CUT3-VGAR-L1: Mixed verdict: AR ADOPT, VG L1 PASS but adoption PENDING; vg-REVIEW.md (VG v1, the tested code) was V5 FAIL at report time; VG v2 V5' PASS but 'not a ship clearance'
- CUT3-VGAR-L1: Tested patch is VG v1, while cut 3 shipped VG v3 (transfer asserted via byte-identical repairs on 6/6 judged answers, not a re-run)
- CUT3-VGAR-L1: Protocol deviation logged: changed-items-only judging with reused control verdicts
- CUT3-VGAR-L1: lan-cmp-003 passes exactly at the +1.00 bar; targets are dev items the VG patterns were written against

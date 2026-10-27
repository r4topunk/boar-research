ACCEPT WITH EDITS

# EXPERIMENT-ECONOMICS (RULE 29): adversarial review, 2026-10-14

Reviewer: independent Opus agent. Read-only, 0 judge calls, blind/ and veil/ not read. Reviewed: `coordinator/EXPERIMENT-ECONOMICS-2026-10-14.md` (the "plan"), `arms/_lib/CRITERION-TEMPLATE.md` (the "template"), `RULE-CHANGES.md` row 29, rnd commit 32c82ef2. All paths below are relative to `rnd/research/coordinator/` unless they start with `QUEUE` (= `rnd/research/QUEUE.md`).

TL;DR
- The direction is sound: a Budget block with a 10-item smoke, a step-0 reach bound, a transfer test and less Opus on dev all target real leaks. Three parts are wrong as written and should not go into the loop as written.
- **D1 would have blocked the only lever the pack line has produced.** For HEADPASS-X2b, the ceiling formula gives (102 − 35)/180 × 0.11 = **0.041**, below 2 × MDE = 0.06. The measured result was **+0.066 Opus**. The 0.11 figure is a Haiku point estimate for X1, not an upper bound, and the rule doubles the MDE on top of the Power block's own expected ≥ MDE test.
- **D3 removes a safeguard that has already paid for itself.** RULE 8/9 sends near-misses to Opus. Its replacement, "straddles → more Haiku", has no terminal state on fixed, deterministic dev sets. The supporting evidence ("same sign every time, ≈ 0.01 low") comes from 4 retrieval pairs chosen out of ≥ 14 on record, and those 14 include a sign flip and gaps of 0.021–0.062.
- **The rule text contradicts itself and the loop's documents.** The template's stage 3 still says "then L2 Opus". LOOP-PROGRAM §2/§4 and L1-PROTOCOL are not amended. v0.3 is listed as an Opus escalation set, although v0.3 is "never tuned on". The parallel line overrides r4to's recorded preference.

## Findings

| # | Sev | Claim (plan/template) | Evidence (file:line) | Fix |
|---|---|---|---|---|
| 1 | high | D1: `ceiling = new_present / n × 0.11`; launch only if ceiling ≥ 2 × MDE (plan l.22–24; template l.31–32) | X2b step-0 reach 35 → 102 (arms/headpass-st/HEADPASS-ST.md:89). The formula gives 0.041, below 0.06, so the arm is blocked. Measured: Opus **+0.066 (+0.043…+0.091)**, Haiku +0.056 (HEADPASS-ST.md:57). Realized per-new-present conversion vs S ≈ 11.9/67 ≈ **0.18** (split HEADPASS-ST.md:59–60). The X2 criterion itself used 0.11–0.17 (HEADPASS-X2-criterion.md:15). 0.11 is X1's *Haiku* split value (HEADPASS-ST.md:17, +0.092; Opus +0.119, l.45). The template already requires expected_delta ≥ mde (template l.28), so 2 × MDE is a second, stricter bar on an expected value presented as a ceiling. | The ceiling is an upper bound: per-item 0.18 (best measured, Opus X2b vs S). Launch if ceiling ≥ **1 ×** MDE. Keep 0.11 as the *expected* value in the Power block. See the pasteable edits. |
| 2 | high | D1 applies to "every criterion" (plan l.21) | Adopted or useful arms with no delta ceiling: DT512 (cheaper-parity, the engine recommendation), DETMAX / CUT5-LITE / VENUEGPS-2 (deterministic gates), DEEPTHINK (a new capability with no prior traces for an oracle or best-of-N; arm-index-2026-10-13.json, adopted rows). Small adopted 4B levers: FACTS-JUDGE projected +0.027 and CUT3-VGAR +0.029 (arm-index). Both sit below 2 × 0.025 under an expected-value reading. | Exempt parity/cheaper/speed, `blocker`, measurement and deterministic-gate arms. Allow `ceiling: unknown` (new capability): the random20 slice then serves as the bound. |
| 3 | high | D3 / §1: "Haiku vs Opus … Same sign every time, Haiku ≈ 0.01 low" (plan l.12, l.58; QUEUE l.1124 "4/4") | Cherry-picked. Omitted pairs: ORACLE ONLY +0.096 → +0.115 (gap 0.019; arms/oracle-st/ORACLE-ST.md:8). DEEPTHINK-V02 +0.027 → +0.048 (an arm wrongly stopped; arms/L1-PROTOCOL.md:15–24). THINK4B slice +0.029 → +0.091, ×3 (L1-PROTOCOL.md:26). DEEPCOVER slice Haiku +0.005 → Opus −0.027, **a sign flip** (arm-index, DEEPCOVER status). HAIKUJUDGE: Haiku compresses paired gaps (+0.007 vs +0.029; L1-PROTOCOL.md:11). The ≈ 0.01 gap holds only for retrieval/pack arms on the 180 (the plan's own UNKNOWN, l.82). | Restate the calibration by family. Keep Opus at the decision boundary for deep/thinking/prompt/model arms (finding 4). |
| 4 | high | D3: "CI straddles MDE → add Haiku items/seeds (no cap) before any Opus"; replaces the near-miss Opus check (plan l.42; template l.24) | (a) RULE 8/9 (RULE-CHANGES l.14–15) exist because Haiku-only stops lost an arm that Opus rated +0.048. D3 drops them without saying so. (b) On the 180, items are fixed and generation is byte-deterministic (RULE 27, RULE-CHANGES l.37), so "more items/seeds" is often impossible. Re-judging the same traces does not shrink the CI: σ_judge ≈ 0.003 (RULE 17, l.23). (c) Extra seeds are generation hours, which works against D2. (d) The rule has no terminal state. (e) The table has gaps and overlaps: CI low > 0 with Δ < MDE (SMALL) is unhandled, and 0 < CI low < MDE ≤ Δ matches rows 2 and 3. Parity arms are closed by "Δ ≤ 0" (GEMMATHINK −0.012 and DT256 −0.001 legitimately continued on the parity clause). | Replacement table in the edits: keep the near-miss rule; "more seeds only if the Budget allows, else label 'not decided at MDE'"; a SMALL row; parity clause untouched; close threshold at Haiku scale (CI high < 0.7 × MDE). |
| 5 | high | Template still says "Full set … then L2 Opus judge.v1 N=4" (template l.45). LOOP-PROGRAM is unchanged | LOOP-PROGRAM-2026-10-11.md:21 (§2 "→ L2 (Opus) → verdict") and :42 (§4 "any Haiku Δ > 0 → Opus"). L1-PROTOCOL.md:28 (RANDOM20 escalation). RULE-CHANGES l.39 names no superseded rows. LOOP v2 fresh-context ticks read all of these files (LOOP-ENGINEERING-2026-10-14.md:9), so each tick gets contradictory rules. | Amend the template's stage 3/4, add a one-line RULE 29 pointer to LOOP-PROGRAM §2/§4 and L1-PROTOCOL, and state "supersedes row 15's escalation clause; keeps rows 8/9" in row 29. |
| 6 | high | "Opus N=4 only on bounty-shaped sets (V-para, v0.2 kit, **v0.3**)" (template l.24; plan l.44) | LOOP-PROGRAM-2026-10-11.md:45: "v0.3 … is never tuned on: one claim run per build". CLAUDE.md: the final number needs a v0.3 written outside the Claude family. Arm L2s on v0.3 would burn the only fresh held-out set. | Remove v0.3 from every escalation list. Add: "v0.3 is never an arm set". |
| 7 | high | §3: "side-session go to V-para confirms and pre-flight reviews, not to L2s over dev traces, replaces the old parallel habit" (plan l.68) | Contradicts r4to's recorded instruction (memory feedback-parallel.md: Opus L2 over EXISTING traces, reviews, audits; "não para geração no mini"). V-para two-seed confirms need fresh deep generation (≈ 4 h on the mini), which a side-session excludes. The "saving" counts burn spend as waste: PACKS-L2 1,240 + ORACLE-ST 720 = 1,960 of the 3,400 dev Opus calls were parallel calls (QUEUE l.1062, l.1073, l.1090, rows tagged [side]), and that budget expires anyway. | Keep r4to's rule. Within it, set the priority order: V-para/v0.2 traces waiting for L2 first, then dev L2s a pending decision needs, then reviews/audits. Changing the habit itself needs r4to's OK. |
| 8 | med | TL;DR: "≈ 3,000 of ≈ 4,400 Opus … confirmed dev-set readings that Haiku had already given with the same sign"; "V-para ≈ 10 % of Opus" (plan l.5, l.59) | The §1 table sums to **3,400** (l.15), not 3,000. The ≈ 4,400 total is not in BACKLOG §0, whose ledger stops at 10-13 13:0x (BACKLOG.md:4–14). Reconstructed from QUEUE: 544 + 720 + 220 + 1,240 + 720 + 218 + 360 + 360 ≈ 4,380 ✓. V-para Opus = QUANTCEIL 204 ≈ **5 %**. Opus did not merely confirm: ORACLE-ST and X2b declared Opus as the verdict judge up front (ORACLE-ST.md:3; QUEUE l.1109). PACKS-L2 turned "topic packs ≈ 0" into +0.035 (CI > 0) (QUEUE l.1073). X1's Opus +0.033 set the prior for X2 (HEADPASS-ST.md:45–46). | Use the corrected numbers. Avoidable dev Opus ≈ 1,440 (ST2 720, X1 360, X2b 360). Add the BACKLOG §0 rows for 10-13 13:0x → 10-14 (T3). |
| 9 | med | "MICROD2Q 4.8 h for a reach FAIL that the conversion prior could have predicted" (plan l.5) | The conversion prior maps presence to score. It cannot predict reach, and MICROD2Q failed on reach (QUEUE l.1110). What could have signalled the fail: its own Q1 code finding (an index column cannot reach 95/137 gate/keep misses; QUEUE l.1104) plus a reach check on a 10–20 % item subset. Both "losses" ran on otherwise idle machines overnight (QUEUE l.1107 "the MacBook is free overnight"). The real cost was TEACHER-PROBE delaying the X2 sidecar rebuild by ≈ 10 h (QUEUE l.1112–1114). SFT4B "4 h estimate torn down" is not a loss. | Reword. Add to D2 a "subset step 0 for build-time arms": when step 0 itself needs generation, run it on a random 15 % of items first. |
| 10 | med | 0.11 conversion as the transferable prior (plan l.13, l.22) | Measured only on agent-written, pack-matched gold. On the recommended tier (deep + think 512) packs add **−0.002 (−0.020…+0.016)** on the same 180 (arms/packs/SELFTEST-DEEP.md:2). Per-item values range 0.09–0.18 by judge and arm. Units are raw; the bar is floor-adjusted. | Per tier: 4B 0.09–0.18 (dev); deep tier "0 until measured". State the units. The plan's UNKNOWN l.81 should become a rule, not only a caveat. |
| 11 | med | D4: product-feature bar "fires on < 10 %"; T1 = X2b transfer on the claim kit (plan l.48, l.76; template l.33) | 10 % of V-para = 5 items, and 5/51 × 0.18 = 0.018, which is below MDE ≈ 0.03: the bar lets undecidable transfers through, inconsistent with D1. X2b is kit byte-identical (HEADPASS-ST.md:89), so T1 on "the claim kit" fires 0 % by construction unless a pack configuration is named. V-para coverage by wave-1 packs is 1/34 (CLAUDE.md, current state). Replays on V-para/v0.2 are exposures and need EXPOSURES rows (RULE 28, RULE-CHANGES l.38). | Bar = fire rate × 0.18 ≥ MDE of the transfer set (V-para ≈ 17 %, 9/51). T1 must name the pack configuration and log EXPOSURES; at 0 calls, T1 can be recorded now as "product feature (kit-identical)". |
| 12 | med | Ceiling/Budget are advisory (plan O1/O2 optional, l.71–72) | arm.sh crit_check parses only expected_delta/n/seeds/mde inside `## Power` (arm.sh:28–37). `probe` is not a recognized tag: the template comment allows only `blocker` (template l.8). No kill automation exists. _lib/README.md:67 does not mention the new blocks. The loop is wound down until r4to decides (QUEUE l.1123), so nobody is enforcing them now. | Make O1 a task with a check keyed on a `Ruleset: 29` header line (old criteria keep passing); add `probe` to the Tags comment; one README line. |
| 13 | med | Bar relevance is tested only after a dev lever (D4) | BACKLOG §0 pipeline metric: "0 V-para floor-adj points adopted per 1,180 judge calls" (BACKLOG.md:10). DECISION-2026-10-14.md O-4: "no engine lever moves the floor-adjusted V-para number". The biggest token leak is direction, not escalation. | Add `bar_ceiling` to the Ceiling block at the freeze: the same 0-call formula on V-para with the claim configuration. If bar_ceiling < MDE_V-para, the arm is product-only from day 1 and never preempts bar work for the mini or Opus. |
| 14 | med | D5 ≥ 50 % of judge calls on bounty-shaped sets + Transfer tests on V-para (plan l.52) | V-para = 51 items and development-style (EXPOSURES ruling). Many adaptive looks inflate the selected Δ (winner's curse). A quota rewards spending Opus on V-para when no candidate exists. | Make the share a monitored metric (O3), not a quota. Keep a V-para look counter in EXPOSURES. Adoption numbers stay provisional until v0.3. |
| 15 | med | Pre-flight `opus`/medium reviewer, one per arm (plan l.57) | 54 of 101 closed arms closed at 0 calls (verified approximately, finding 17). For a 0-call step-0 replay, a reviewer reading CLOSED.md + LOSSMAP costs more than the arm. | Conditional: only when wall_cap > 2 h or declared Opus > 200. Otherwise the author fills Ceiling/Budget. |
| 16 | low | D2 checkpoint "stop if the 25 % chunk reads clearly worse" (plan l.36) | An interim look is fine for futility; success-side early stopping would inflate type I error. Judged chunks also need a judge pass. | Add "futility only; never adopt or escalate on the interim chunk". |
| 17 | low | "101 closed arms: 54 / 10 / 12 / 25" (plan l.4) | Reproducible only approximately. 101 is the number of arm dirs; the index has 159 records (ARM-INDEX-2026-10-13.md:1). A judge-field classifier over "closed" statuses gives 102 records: ≈ 52–60 at 0 calls, 10 L1, 11 L1→L2, 29 Opus. Five "Opus direct" arms used existing rows only (DEEPBO2, DEEPROUTE ×3, RETHURT). | Cite as "≈" and name the classifier, or drop the exact split. |
| 18 | low | "CI high < MDE → close 'not detected'" | A tight positive CI below MDE is a detected SMALL effect, not "not detected" (RULE 18/19 labels). | Covered by the D3 table in the edits. |
| 19 | low | Running arms keep frozen rules | HEADPASS-X3 criterion sha 275fe748 and RIVALSET-DEEP 9298f8c1 both match their `.sha256`. Neither file was touched by 32c82ef2. X3 still declares Opus ≤ 720 on the dev 180 (HEADPASS-X3-criterion.md:12,31), which is legitimate under "frozen after", but it is not part of the saving. | None. Note it in the plan's §3 saving line. |

Mechanical check (item 4 of the brief): I replicated crit_check's awk/grep on the new template read-only (`arm.sh:34–36`). The result is: no blocker tag; expected_delta/n/seeds/mde found inside `## Power`; the new `## Ceiling` and `## Budget` headings correctly end the Power block. **No parse break.** _lib test T7 ("CRITERION-TEMPLATE.md itself has a complete Power block", tests/run.sh:132–133) would pass for the same reason. I did not run the full suite because it rewrites `tests/fixtures/legacy/arm.run.sh` inside the repo (tests/run.sh:21), and this review is read-only. The new `l1_futility` text is not machine-read.

## Pasteable edits

### A. Plan (`EXPERIMENT-ECONOMICS-2026-10-14.md`)

A1, l.5. Old:
```
2. The two leaks are elsewhere. **Wall time**: long generation runs went ahead without a speed projection (TEACHER-PROBE ≈ 10 h on the mini for 6/120; MICROD2Q 4.8 h for a reach FAIL that the conversion prior could have predicted). **Opus on dev**: ≈ 3,000 of ≈ 4,400 Opus calls on 10-12→14 confirmed dev-set readings that Haiku had already given with the same sign.
```
New:
```
2. The two leaks are elsewhere. **Wall time**: long generation runs went ahead without a speed projection or a subset check (TEACHER-PROBE ≈ 10 h on the mini for 6/120, which delayed the X2 sidecar rebuild ≈ 10 h; MICROD2Q 4.8 h overnight for a reach FAIL that its own Q1 code finding and a 15 % subset reach check could have signalled). **Opus on dev**: ≈ 3,400 of ≈ 4,400 Opus calls on 10-12→14 went to the 180 dev self-tests; 1,960 of them were parallel spend (PACKS-L2, ORACLE-ST), so ≈ 1,440 (ST2, HEADPASS X1, X2b) were avoidable. Haiku had the same pooled sign each time, but Opus changed two readings (PACKS-L2 topic half; X1 → the X2 prior).
```

A2, l.12. Old:
```
| Haiku vs Opus on the same paired runs | HEADPASS X1 +0.023 → +0.033; X2b +0.056 → +0.066; single pack +0.032 → +0.042; ORACLE-ST +0.090 → +0.095. Same sign every time, Haiku ≈ 0.01 low | arms/headpass-st, PACKS-L2, ORACLE-ST |
```
New:
```
| Haiku vs Opus on the same paired runs | Retrieval/pack arms on the 180: X1 +0.023 → +0.033; X2b +0.056 → +0.066; single pack +0.032 → +0.042; ORACLE ADD +0.090 → +0.095, ONLY +0.096 → +0.115; ST2 +0.015 → +0.017: same sign, Haiku 0.005–0.019 low. Deep/4B quality arms: DEEPTHINK-V02 +0.027 → +0.048 (arm wrongly stopped), THINK4B slice +0.029 → +0.091, DEEPCOVER slice +0.005 → −0.027 (sign flip), GEMMATHINK −0.012 → −0.002 | arms/headpass-st, PACKS-L2, ORACLE-ST, L1-PROTOCOL addenda 2026-10-10, arm-index (DEEPCOVER) |
```

A3, l.13. Old:
```
| Conversion prior (retrieval levers) | Each newly present fact chunk ≈ +0.09…+0.12 raw on that item (Haiku/Opus) → Δ_pooled ≈ new_present / n × 0.11 | HEADPASS-ST §split; NEXT-RETRIEVAL-ARMS-2026-10-13 |
```
New:
```
| Conversion prior (retrieval levers, 4B, dev) | Per newly present fact chunk: Haiku X1 0.092, Opus X1 0.119, ORACLE ADD 0.112, Opus X2b vs S ≈ 0.18 → expected Δ ≈ new_present / n × 0.11, upper bound new_present / n × 0.18 (raw). Deep tier: packs add −0.002 on the same 180 (SELFTEST-DEEP), so 0 until measured | HEADPASS-ST §split, §X2b; ORACLE-ST; arms/packs/SELFTEST-DEEP.md |
```

A4, l.14. Old:
```
| Wall-time losses | TEACHER-PROBE 120 × 323 s (rate known after item 1); MICROD2Q 4.77 h; SFT4B stage-1 estimate 4 h (torn down) | QUEUE 10-13 22:31 → 10-14 10:56 |
```
New:
```
| Wall-time losses | TEACHER-PROBE 120 × 323 s (rate and the empty-answer failure mode visible in a 10-item smoke); MICROD2Q 4.77 h on an idle overnight MacBook (Q1 had already shown an index column cannot reach 95/137 misses) | QUEUE 10-13 22:31 → 10-14 10:56 |
```

A5, l.15. Old:
```
| Opus on dev, week 2 | PACKS-L2 ≈ 1,240 · ST2 L2 720 · ORACLE-ST 720 · HEADPASS L2 360 + X2b 360 | BACKLOG §0, QUEUE |
```
New:
```
| Opus on dev, week 2 | PACKS-L2 1,240 [side] · ORACLE-ST 720 [side] · ST2 L2 720 · HEADPASS X1 360 + X2b 360 = 3,400 of ≈ 4,380 (V-para: QUANTCEIL 204 ≈ 5 %) | QUEUE 10-12 → 10-14 (BACKLOG §0 stops at 10-13 13:0x) |
```

A6, D1 (l.21–24). Old:
```
Every criterion states the best Δ the arm can reach, computed without a judge:
- retrieval/pack levers: `ceiling = new_present / n × 0.11` from the step-0 replay (reach counts);
- prompt/model levers: oracle or best-of-N on existing traces, or the LOSSMAP bucket size × the best per-item gain measured in the family;
- **launch rule:** ceiling ≥ 2 × MDE on the deciding set, otherwise close as "ceiling below MDE" (0 calls) or run only as a ≤ 1 h mechanism probe tagged `probe`.
```
New:
```
Every criterion with a delta verdict states an UPPER bound on the Δ the arm can reach, computed without a judge (the expected value stays in the Power block):
- retrieval/pack levers (4B): `ceiling = new_present / n × 0.18` from the step-0 replay (0.18 = best measured per-item conversion, Opus X2b vs S); deep tier: no transfer of the 4B conversion (SELFTEST-DEEP −0.002), bound from an oracle cell or `unknown`;
- prompt/model levers: oracle or best-of-N on existing traces, or the LOSSMAP bucket size × the best per-item gain measured in the family; a new capability with no traces writes `ceiling: unknown` and the random20 slice is its bound;
- `bar_ceiling`: the same formula on V-para with the claim configuration (0-call replay); bar_ceiling < MDE_V-para → the arm is product-only from the freeze and never preempts bar work for the mini or Opus;
- **launch rule:** ceiling ≥ MDE on the deciding set (and expected_delta ≥ MDE, as before), otherwise close as "ceiling below MDE" (0 calls) or run only as a ≤ 1 h mechanism probe tagged `probe`;
- exempt: parity/cheaper/speed arms (their clause is the bound), `blocker`, measurement arms (no verdict), deterministic-gate arms.
```

A7, D2 (after l.36), add:
```
- Build-time arms whose step 0 itself needs generation (doc2query, teacher data) run step 0 on a random 15 % of the items first; the full step 0 runs only if the subset projects past the gate.
- Interim looks are futility-only: never adopt or escalate on a partial chunk.
- Enforcement: `arm.sh launch` refuses a criterion carrying `Ruleset: 29` without `ceiling:`, `wall_cap:` and `kill_if:` (task T2b).
```

A8, D3 table + footer (l.39–45). Old: the whole table and the line "Replaces the `l1_futility` line …". New:
```
| Haiku result (paired, both orders, on the deciding set) | Action |
|---|---|
| Δ ≤ 0, or CI high < 0.7 × MDE (Haiku compresses gaps) | close: "not detected at MDE x (Haiku)" |
| near-miss: Δ within 0.01 of the decision threshold (RULE 8/9), or a deep/thinking/prompt/model arm with Δ ≥ 0.5 × MDE | Opus N=4 on the same ids (≤ 40 slice / 102 V-para / 220 v0.2 / 360 on the 180) before deciding |
| CI straddles MDE, otherwise | more seeds only if the Budget allows (generation hours); re-judging the same traces does not shrink the CI (RULE 17); else label "not decided at MDE x" and stop |
| CI low > 0, Δ < MDE | SMALL (Haiku); no Opus on dev |
| CI low > 0, Δ ≥ MDE on a dev set | LEVER (Haiku, dev) → Transfer test (D4); Opus on dev only for a pre-declared calibration pair or a published product number |
| CI low > 0 on V-para or the v0.2 kit | Opus L2 two seeds: the number we adopt |
Parity/cheaper arms keep their own clause (−0.03 bound, near-miss rule). v0.3 is never an arm set (one claim run per build, LOOP-PROGRAM §4). For criteria frozen after RULE 29 this supersedes RULE 15's "any Haiku Δ > 0 → Opus" (RULE-CHANGES row 15) and LOOP-PROGRAM §2 step 2 / §4 bullet 1's escalation clause; RULE 8/9 (near-miss) stay in force.
```

A9, D4 (l.48). Old:
```
If step 0 shows it fires on < 10 % of the set, the lever is a product feature, not a bar lever, and is logged as such.
```
New:
```
The transfer criterion names the pack/kit configuration on the transfer set. If step 0 gives fire_rate × 0.18 < MDE of the transfer set (V-para: < 17 %, ≈ 9/51 items newly reached), the lever is a product feature, not a bar lever, and is logged as such. Every V-para / v0.2 replay is script-only and gets an EXPOSURES row (RULE 28).
```

A10, D5 (l.52). Old:
```
- Bounty-shaped work ≥ 50 % of the week's judge calls (ledger column `set` in BACKLOG §0).
```
New:
```
- Share of bounty-shaped judge calls is reported weekly (ledger column `set` in BACKLOG §0; O3), not a quota. V-para looks are counted in EXPOSURES; adopted V-para numbers stay provisional until v0.3.
```

A11, §3 l.57. Old:
```
| Pre-flight reviewer, `opus`/`medium`, 1 per arm before the freeze: fills Ceiling + Budget, checks CLOSED.md for a duplicate | One agent costs far less than a wasted mini night plus its judge pass |
```
New:
```
| Pre-flight reviewer, `opus`/`medium`, before the freeze of any arm with wall_cap > 2 h or declared Opus > 200: checks Ceiling + bar_ceiling + Budget and CLOSED.md for a duplicate | One agent costs far less than a wasted mini night; for 0-call step-0 arms the author fills the blocks |
```

A12, §3 l.58. Old:
```
| Haiku freely (no cap): bigger n, both orders, extra seeds | Shrinks CIs without Opus; same sign as Opus in every pair measured |
```
New:
```
| Haiku freely (no cap): larger n where items exist, extra seeds within the Budget | Shrinks sampling CIs without Opus; same sign as Opus on retrieval arms (not on every deep/4B slice: DEEPCOVER flip, DEEPTHINK-V02 / THINK4B gaps) |
```

A13, §3 l.63. Old:
```
| Opus L2 on dev sets (D3) | ≈ 3,000 Opus calls in week 2 |
```
New:
```
| Opus L2 on dev sets (D3) | ≈ 1,440 Opus calls in week 2 outside side-session (ST2, X1, X2b); running frozen arms (HEADPASS-X3 ≤ 720) are exempt |
```

A14, §3 l.68. Old:
```
| side-session go to V-para confirms and pre-flight reviews, not to L2s over dev traces | replaces the old parallel habit |
```
New:
```
| side-session keep r4to's rule (Opus over EXISTING traces, reviews, audits; never generation), in this order: V-para / v0.2 traces awaiting L2 → dev L2s a pending decision needs → reviews/audits | ordering only; changing the habit itself needs r4to's OK |
```

A15, §5 T1 (l.76). Old:
```
- T1 (now): HEADPASS-X2b Transfer test (D4) on the claim kit: step 0 on V-para + v0.2 (0 calls), then Haiku, then Opus two seeds only if Haiku CI low > 0.
```
New:
```
- T1 (now, 0 calls): HEADPASS-X2b Transfer. X2b is kit byte-identical, so on the claim kit alone it fires 0 % by construction → log "product feature (kit-identical)" now. A judged transfer needs a named pack configuration on V-para + v0.2 (step 0 replay, script-only, EXPOSURES rows), then Haiku, then Opus two seeds only if the D4 fire bar and Haiku CI low > 0 hold.
- T2b: arm.sh crit_check requires `ceiling:`, `wall_cap:`, `kill_if:` when the criterion carries `Ruleset: 29`; `probe` tag recognized (blocks Opus stages); one test in _lib/tests/run.sh T7 (sonnet/medium).
- T4: one-line RULE 29 pointers in LOOP-PROGRAM §2 step 2 and §4 bullet 1, L1-PROTOCOL (new addendum) and _lib/README.md "Criteria and the Power block".
```

### B. Template (`arms/_lib/CRITERION-TEMPLATE.md`)

B1, l.6–8. Old:
```
## Tags
Tags: none
<!-- Allowed: `blocker` (a run that unblocks other work / infrastructure fix; waives the Power check). Format: `Tags: blocker`. The line under the heading is the one read by arm.sh. -->
```
New:
```
## Tags
Tags: none
Ruleset: 29
<!-- Allowed: `blocker` (a run that unblocks other work / infrastructure fix; waives the Power check); `probe` (RULE 29 mechanism probe: <= 1 h, Haiku only, 0 Opus, no verdict beyond 'mechanism seen / not seen'). Format: `Tags: blocker` or `Tags: probe`. The line under the heading is the one read by arm.sh. -->
```

B2, l.24. Old:
```
l1_futility: (RULE 29, criteria frozen after 2026-10-14) close if Haiku delta <= 0 or CI high < mde; CI straddles mde -> more Haiku items/seeds, not Opus; CI low > 0 on a DEV set -> no Opus, run the Transfer test; Opus N=4 only on bounty-shaped sets (V-para, v0.2 kit, v0.3). Older criteria: any Haiku delta > 0 -> Opus N=4 on the same 20 ids
```
New:
```
l1_futility: (RULE 29, criteria frozen after 2026-10-14; table in EXPERIMENT-ECONOMICS D3) close if Haiku delta <= 0 or CI high < 0.7 x mde; near-miss (within 0.01 of the threshold, or deep/thinking/prompt/model arm with delta >= 0.5 x mde) -> Opus N=4 on the same ids (RULE 8/9); CI straddles mde -> more seeds only within the Budget, else 'not decided at MDE'; CI low > 0 on a DEV set -> SMALL/LEVER (Haiku, dev), no Opus, Transfer test; Opus N=4 two seeds on V-para / v0.2 kit only; v0.3 is never an arm set; parity/cheaper arms keep their clause. Older criteria: any Haiku delta > 0 -> Opus N=4 on the same 20 ids
```

B3, l.30–33. Old:
```
## Ceiling (RULE 29; 0 calls, before the freeze)
ceiling: <best reachable delta without a judge: retrieval = new_present / n x 0.11 from the step-0 replay; prompt/model = oracle or best-of-N on existing traces; LOSSMAP bucket x best per-item gain>
launch: ceiling >= 2 x mde on the deciding set, else close "ceiling below MDE" or tag `probe` (<= 1 h, 0 Opus)
transfer: <dev-set arms only: the bounty-shaped set (V-para / v0.2 kit) where a LEVER must also show up, with its step-0 fire-rate bar (>= 10 %)>
```
New:
```
## Ceiling (RULE 29; 0 calls, before the freeze)
ceiling: <UPPER bound on the delta, no judge: 4B retrieval = new_present / n x 0.18 from the step-0 replay (expected value x 0.11 goes in Power); deep tier = oracle cell or 'unknown'; prompt/model = oracle or best-of-N on existing traces, or LOSSMAP bucket x best per-item gain; new capability = 'unknown' (the random20 slice is the bound); n/a for parity/cheaper, blocker, measurement and deterministic-gate arms>
bar_ceiling: <same formula on V-para with the claim configuration (0-call replay, script-only, EXPOSURES row); < MDE_V-para -> product-only arm, never preempts bar work>
launch: ceiling >= mde on the deciding set (and expected_delta >= mde), else close "ceiling below MDE" or tag `probe` (<= 1 h, Haiku only, 0 Opus)
transfer: <dev-set arms only: the bounty-shaped set (V-para / v0.2 kit) AND the pack/kit configuration where a LEVER must also show up; product-only if fire_rate x 0.18 < mde of that set (V-para ~17 %)>
```

B4, l.38–40, add one line after `checkpoint:`:
```
subset_step0: <build-time arms whose step 0 needs generation: random 15 % of items first; full step 0 only if the subset projects past the gate>; interim looks are futility-only
```

B5, l.45–49. Old:
```
3. Full set at the declared seeds, Haiku vs control; then L2 Opus judge.v1 N=4.
4. Verdict (strict):
   - **LEVER**: delta vs control, CI low > 0 and delta >= <threshold>.
```
New:
```
3. Full set at the declared seeds, Haiku vs control; then L2 Opus judge.v1 N=4 only where l1_futility sends it (near-miss, or V-para / v0.2 kit).
4. Verdict (strict; the label names the judge and the set, e.g. "LEVER (Haiku, dev)" or "LEVER (Opus, V-para 2 seeds)"; adoption only after the two-seed V-para Opus confirmation, RULE 18):
   - **LEVER**: delta vs control, CI low > 0 and delta >= <threshold>.
```

### C. `RULE-CHANGES.md` row 29 (l.39)
Append to the Rule cell:
```
; for criteria frozen after this row it supersedes row 15's escalation clause ("any Haiku Δ > 0 → Opus") and LOOP-PROGRAM §2/§4's; rows 8/9 (near-miss → Opus) stay; v0.3 is never an arm set; parallel rule (r4to) unchanged
```

## UNKNOWN
- No per-family Haiku/Opus calibration exists for prompt and model arms on the 4B fast path beyond THINK4B. The 0.7 × MDE close threshold and the 0.5 × MDE near-miss trigger are my proposal from the 14 known pairs, not a fitted value.
- Whether the 0.18 upper conversion holds beyond the 180 pack-matched items (agent-written gold). It is the best measured value, not a proven maximum.
- The stage split 54/10/12/25 could only be reproduced approximately: the index has no stage field, and the classifier depends on how "closed" and "judge" are read.
- Whether r4to wants to change the parallel habit (finding 7). That is his call, not the loop's.
- Token cost per Opus or Haiku call and per agent is not tracked (plan UNKNOWN l.83), so savings are in calls only. The pre-flight reviewer's cost-benefit (finding 15) is a judgment call, not a measurement.
- The loop is wound down pending r4to's DECISION-2026-10-14 choice (QUEUE l.1123). If he picks O-4 (back to the bar), most of D4 has no dev levers left to transfer.

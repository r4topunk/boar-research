# EXPERIMENT-ECONOMICS — kill bad arms early, spend Claude tokens where they move the bar (2026-10-14)

TL;DR
1. The judge ladder already kills cheaply: of 101 closed arms, 54 closed at 0 judge calls, 10 at Haiku L1, 12 at L1 → Opus L2, 25 with Opus directly (mostly before 10-07, when Haiku L1 did not exist yet). Source: arm-index-2026-10-13.json.
2. The two leaks are elsewhere. **Wall time**: long generation runs went ahead without a speed projection or a subset check (TEACHER-PROBE ≈ 10 h on the mini for 6/120, which delayed the X2 sidecar rebuild ≈ 10 h; MICROD2Q 4.8 h overnight for a reach FAIL that its own Q1 code finding and a 15 % subset reach check could have signalled). **Opus on dev**: ≈ 3,400 of ≈ 4,400 Opus calls on 10-12→14 went to the 180 dev self-tests; 1,960 of them were parallel spend (PACKS-L2, ORACLE-ST), so ≈ 1,440 (ST2, HEADPASS X1, X2b) were avoidable. Haiku had the same pooled sign each time, but Opus changed two readings (PACKS-L2 topic half; X1 → the X2 prior).
3. Fix = three additions to every criterion (**Ceiling**, **Budget/kill points**, **Transfer**) + one judge rule (**Opus on V-para / v0.2 kit and on near-misses; not for dev confirmations**) + LOOP v2's fresh-context ticks. Spend more tokens on pre-flight design reviews and on V-para two-seed confirms, and less on L2s, audits and handoffs.

## 1. Evidence used
| Fact | Number | Source |
|---|---|---|
| Closed arms by stage | 0-call 54 · L1 only 10 · L1→L2 12 · Opus direct 25 | arm-index-2026-10-13.json |
| Haiku vs Opus on the same paired runs | Retrieval/pack arms on the 180: X1 +0.023 → +0.033; X2b +0.056 → +0.066; single pack +0.032 → +0.042; ORACLE ADD +0.090 → +0.095, ONLY +0.096 → +0.115; ST2 +0.015 → +0.017: same sign, Haiku 0.005–0.019 low. Deep/4B quality arms: DEEPTHINK-V02 +0.027 → +0.048 (arm wrongly stopped), THINK4B slice +0.029 → +0.091, DEEPCOVER slice +0.005 → −0.027 (sign flip), GEMMATHINK −0.012 → −0.002 | arms/headpass-st, PACKS-L2, ORACLE-ST, L1-PROTOCOL addenda 2026-10-10, arm-index (DEEPCOVER) |
| Conversion prior (retrieval levers, 4B, dev) | Per newly present fact chunk: Haiku X1 0.092, Opus X1 0.119, ORACLE ADD 0.112, Opus X2b vs S ≈ 0.18 → expected Δ ≈ new_present / n × 0.11, upper bound new_present / n × 0.18 (raw). Deep tier: packs add −0.002 on the same 180 (SELFTEST-DEEP), so 0 until measured | HEADPASS-ST §split, §X2b; ORACLE-ST; arms/packs/SELFTEST-DEEP.md |
| Wall-time losses | TEACHER-PROBE 120 × 323 s (rate and the empty-answer failure mode visible in a 10-item smoke); MICROD2Q 4.77 h on an idle overnight MacBook (Q1 had already shown an index column cannot reach 95/137 misses) | QUEUE 10-13 22:31 → 10-14 10:56 |
| Opus on dev, week 2 | PACKS-L2 1,240 [side] · ORACLE-ST 720 [side] · ST2 L2 720 · HEADPASS X1 360 + X2b 360 = 3,400 of ≈ 4,380 (V-para: QUANTCEIL 204 ≈ 5 %) | QUEUE 10-12 → 10-14 (BACKLOG §0 stops at 10-13 13:0x) |
| Idle coordinator ticks | 37 of 121 ticks were idle and paid the full-context read | LOOP-ENGINEERING-2026-10-14 TL;DR 2 |

## 2. Decisions (in force for criteria frozen after this file's commit; RULE 29)

### D1 · Ceiling block before the freeze (0 calls)
Every criterion with a delta verdict states an UPPER bound on the Δ the arm can reach, computed without a judge (the expected value stays in the Power block):
- retrieval/pack levers (4B): `ceiling = new_present / n × 0.18` from the step-0 replay (0.18 = best measured per-item conversion, Opus X2b vs S); deep tier: no transfer of the 4B conversion (SELFTEST-DEEP −0.002), bound from an oracle cell or `unknown`;
- prompt/model levers: oracle or best-of-N on existing traces, or the LOSSMAP bucket size × the best per-item gain measured in the family; a new capability with no traces writes `ceiling: unknown` and the random20 slice is its bound;
- `bar_ceiling`: the same formula on V-para with the claim configuration (0-call replay); bar_ceiling < MDE_V-para → the arm is product-only from the freeze and never preempts bar work for the mini or Opus;
- **launch rule:** ceiling ≥ MDE on the deciding set (and expected_delta ≥ MDE, as before), otherwise close as "ceiling below MDE" (0 calls) or run only as a ≤ 1 h mechanism probe tagged `probe`;
- exempt: parity/cheaper/speed arms (their clause is the bound), `blocker`, measurement arms (no verdict), deterministic-gate arms.

### D2 · Budget block with kill points
```
## Budget
wall_cap: <hours, mini/MacBook>        # whole arm
calls_cap: <Haiku N / Opus N>
smoke: 10 items → measure s/item, mechanism fire rate, parse rate
kill_if: projected_wall > 1.5 × wall_cap  OR  fire_rate < <x>  OR  smoke shows the failure mode the ceiling assumed away
checkpoint: <the earliest point where the verdict can already be read, e.g. 30/120 items>
```
- A run over 2 h needs a smoke first; the projection after the smoke is logged in QUEUE before the full run.
- Long generation runs are written to evaluate in chunks (first 25 %, then the rest): if the 25 % chunk reads clearly worse than the control (for jev gates, pass rate < half the control's), stop.
- Build-time arms whose step 0 itself needs generation (doc2query, teacher data) run step 0 on a random 15 % of the items first; the full step 0 runs only if the subset projects past the gate.
- Interim looks are futility-only: never adopt or escalate on a partial chunk.
- Enforcement: `arm.sh launch` refuses a criterion carrying `Ruleset: 29` without `ceiling:`, `wall_cap:` and `kill_if:` (task T2b).

### D3 · Judge escalation
| Haiku result (paired, both orders, on the deciding set) | Action |
|---|---|
| Δ ≤ 0, or CI high < 0.7 × MDE (Haiku compresses gaps) | close: "not detected at MDE x (Haiku)" |
| near-miss: Δ within 0.01 of the decision threshold (RULE 8/9), or a deep/thinking/prompt/model arm with Δ ≥ 0.5 × MDE | Opus N=4 on the same ids (≤ 40 slice / 102 V-para / 220 v0.2 / 360 on the 180) before deciding |
| CI straddles MDE, otherwise | more seeds only if the Budget allows (generation hours); re-judging the same traces does not shrink the CI (RULE 17); else label "not decided at MDE x" and stop |
| CI low > 0, Δ < MDE | SMALL (Haiku); no Opus on dev |
| CI low > 0, Δ ≥ MDE on a dev set | LEVER (Haiku, dev) → Transfer test (D4); Opus on dev only for a pre-declared calibration pair or a published product number |
| CI low > 0 on V-para or the v0.2 kit | Opus L2 two seeds: the number we adopt |
Parity/cheaper arms keep their own clause (−0.03 bound, near-miss rule). v0.3 is never an arm set (one claim run per build, LOOP-PROGRAM §4). For criteria frozen after RULE 29 this supersedes RULE 15's "any Haiku Δ > 0 → Opus" (RULE-CHANGES row 15) and LOOP-PROGRAM §2 step 2 / §4 bullet 1's escalation clause; RULE 8/9 (near-miss) stay in force.

### D4 · Transfer test for dev levers
A lever found on the 180 self-tests (or any dev set) is pre-registered at its first freeze with the bounty-shaped set where it must also show up: claim kit + lever on V-para (or v0.2 kit) with step 0 (does it fire? reach on those items) → Haiku → Opus two seeds. The transfer criterion names the pack/kit configuration on the transfer set. If step 0 gives fire_rate × 0.18 < MDE of the transfer set (V-para: < 17 %, ≈ 9/51 items newly reached), the lever is a product feature, not a bar lever, and is logged as such. Every V-para / v0.2 replay is script-only and gets an EXPOSURES row (RULE 28).

### D5 · Machine portfolio
- Mini: one long run at a time, always with a D2 projection; the MacBook carries 0-call replays and 4B generations in parallel.
- Share of bounty-shaped judge calls is reported weekly (ledger column `set` in BACKLOG §0; O3), not a quota. V-para looks are counted in EXPOSURES; adopted V-para numbers stay provisional until v0.3.

## 3. Claude Code tokens: where to spend more, where less
| Spend more (useful) | Why |
|---|---|
| Pre-flight reviewer, `opus`/`medium`, before the freeze of any arm with wall_cap > 2 h or declared Opus > 200: checks Ceiling + bar_ceiling + Budget and CLOSED.md for a duplicate | One agent costs far less than a wasted mini night; for 0-call step-0 arms the author fills the blocks |
| Haiku freely (no cap): larger n where items exist, extra seeds within the Budget | Shrinks sampling CIs without Opus; same sign as Opus on retrieval arms (not on every deep/4B slice: DEEPCOVER flip, DEEPTHINK-V02 / THINK4B gaps) |
| Opus two-seed confirms on V-para | This is the bounty number; currently ≈ 10 % of Opus |

| Spend less | Saving |
|---|---|
| Opus L2 on dev sets (D3) | ≈ 1,440 Opus calls in week 2 outside side-session (ST2, X1, X2b); running frozen arms (HEADPASS-X3 ≤ 720) are exempt |
| Idle ticks: LOOP v2 fresh-context ticks + `tick-precheck.sh` (exit 0, 0 tokens) | 37/121 ticks were idle full-context turns |
| One coordinator session at a time; side sessions write `proposals/`, never QUEUE rows | duplicate rows, duplicate state reads |
| Handoffs only at session end; claim draft frozen until a new number exists; ledger audits monthly | 8 handoffs, claim v3.5→v3.9, 58-agent audit in 10 days |
| Subagent replies ≤ 5 lines + path; the coordinator reads `aggregates/*.json`, never traces | context growth per tick |
| side-session keep r4to's rule (Opus over EXISTING traces, reviews, audits; never generation), in this order: V-para / v0.2 traces awaiting L2 → dev L2s a pending decision needs → reviews/audits | ordering only; changing the habit itself needs r4to's OK |

## 4. Options (not decided)
- O1: enforce D1/D2 in `arm.sh launch` (refuse without `## Budget`), like the Power block. Cheap and mechanical (sonnet/medium + tests).
- O2: a `smoke-project.py` that reads the first STATUS lines of a run and prints the projected wall and pass rate; the waiter kills on `kill_if`.
- O3: weekly pipeline metric in LOOP-LOG META: V-para floor-adj points per 1,000 Opus calls, plus the share of bounty-shaped calls.

## 5. Tasks
- T1 (now, 0 calls): HEADPASS-X2b Transfer. X2b is kit byte-identical, so on the claim kit alone it fires 0 % by construction → log "product feature (kit-identical)" now. A judged transfer needs a named pack configuration on V-para + v0.2 (step 0 replay, script-only, EXPOSURES rows), then Haiku, then Opus two seeds only if the D4 fire bar and Haiku CI low > 0 hold.
- T2b: arm.sh crit_check requires `ceiling:`, `wall_cap:`, `kill_if:` when the criterion carries `Ruleset: 29`; `probe` tag recognized (blocks Opus stages); one test in _lib/tests/run.sh T7 (sonnet/medium).
- T4: one-line RULE 29 pointers in LOOP-PROGRAM §2 step 2 and §4 bullet 1, L1-PROTOCOL (new addendum) and _lib/README.md "Criteria and the Power block".
- T2: add the `## Budget` and `## Ceiling` sections to arms/_lib/CRITERION-TEMPLATE.md (done in this commit); O1 when the loop next touches arm.sh.
- T3: add a `set` column to BACKLOG §0.

## UNKNOWN
- The 0.11 conversion is measured on pack-matched items only; on V-para it may be lower (different gold, other failure modes).
- Haiku ≈ Opus − 0.01 is measured on 4 paired runs, all retrieval/pack arms; check before applying it to deep-tier or prompt arms.
- Token prices per call are not tracked; savings are in calls, not in $ or % of the plan.

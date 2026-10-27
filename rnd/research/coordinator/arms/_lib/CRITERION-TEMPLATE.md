# <ARM>: <one-line question> (frozen <date time>, coordinator)

Copy this file, fill every field, freeze it (write `<NAME>-criterion.sha256` next to it), then set `CRITERION=<path>` in the arm's `arm.conf`.
`arm.sh <conf> launch` refuses (rc 7) unless the criterion has a complete `## Power` block (or the tag `blocker`) and its sha256 matches the sibling `.sha256` file if present.
LOOP v2 T3 (`Ruleset: 30`): launch also refuses (rc 7) a criterion without a complete, filled `## Precheck` block (waived by `Tags: blocker`) and, before any run, without `smoke.verdict.json` = PASS for this exact sha256 (next to the criterion; written by `arm.sh <conf> smoke <smoke traces|units.jsonl> --n-full N [--marker code]`; `arm.sh <conf> crit_check` shows the state). A smoke FAIL/KILL is cleared only by a new freeze, never by an addendum. `SMOKE_SKIP=1` waives the smoke only for `Tags: blocker` or `Tags: probe`.

## Tags
Tags: none
Ruleset: 30
<!-- Ruleset: 30 = this template (Precheck block + smoke gate enforced); criteria frozen under Ruleset 29 or older stay valid with the Power check alone. Allowed: `blocker` (a run that unblocks other work / infrastructure fix; waives the Power check); `probe` (RULE 29 mechanism probe: <= 1 h, Haiku only, 0 Opus, no verdict beyond 'mechanism seen / not seen'). Format: `Tags: blocker` or `Tags: probe`. The line under the heading is the one read by arm.sh. -->

## Question
What does the arm change, versus which control, and what would the answer be used for.

## Fixed inputs
- Arm **X**: tree, patch (sha256), settings; everything else identical to the control.
- Control **C**: run ids, judge (Haiku rows for L1, Opus rows for L2).
- Script-only scoped exception for blind sets (if used); exposures logged.

## Power
expected_delta: <number, raw ratio> (source: <earlier measurement, QUEUE entry or paper; never "hope">)
n: <items at the stage that decides, e.g. 51 or 110>
seeds: <1 or 2>
mde: <minimum detectable effect at that n and seeds> (reference: v0.2 one seed ~0.025 raw at 110 ids; V-para two seeds ~0.03; a V-para one-seed deep delta < 0.03 is seed noise, SEEDVAR)
slice: random20-v02.ids | random20-vpara.ids   (never signal20; files and sha256s in arms/random20-sets.sha256)
l1_futility: (RULE 29, criteria frozen after 2026-10-14; table in EXPERIMENT-ECONOMICS D3) close if Haiku delta <= 0 or CI high < 0.7 x mde; near-miss (within 0.01 of the threshold, or deep/thinking/prompt/model arm with delta >= 0.5 x mde) -> Opus N=4 on the same ids (RULE 8/9); CI straddles mde -> more seeds only within the Budget, else 'not decided at MDE'; CI low > 0 on a DEV set -> SMALL/LEVER (Haiku, dev), no Opus, Transfer test; Opus N=4 two seeds on V-para / v0.2 kit only; v0.3 is never an arm set; parity/cheaper arms keep their clause. Older criteria: any Haiku delta > 0 -> Opus N=4 on the same 20 ids
reopen: <required when the family is in a closed list: cite the CLOSED.md row (R#) and what is new>  (optional otherwise)
split: <the ONE pre-declared labelled split, if any: e.g. 'paired delta by LOSSMAP primary bucket of the control (expected: gain on wrong, ~0 on absent)'; declared here = not post-hoc; none = no split allowed later> (added 2026-10-12 after QUANTCEIL)

If expected_delta < mde the arm cannot decide: say so here and either raise n/seeds or drop the arm.

## Ceiling (RULE 29; 0 calls, before the freeze)
ceiling: <UPPER bound on the delta, no judge: 4B retrieval = new_present / n x 0.18 from the step-0 replay (expected value x 0.11 goes in Power); deep tier = oracle cell or 'unknown'; prompt/model = oracle or best-of-N on existing traces, or LOSSMAP bucket x best per-item gain; new capability = 'unknown' (the random20 slice is the bound); n/a for parity/cheaper, blocker, measurement and deterministic-gate arms>
bar_ceiling: <same formula on V-para with the claim configuration (0-call replay, script-only, EXPOSURES row); < MDE_V-para -> product-only arm, never preempts bar work>
launch: ceiling >= mde on the deciding set (and expected_delta >= mde), else close "ceiling below MDE" or tag `probe` (<= 1 h, Haiku only, 0 Opus)
transfer: <dev-set arms only: the bounty-shaped set (V-para / v0.2 kit) AND the pack/kit configuration where a LEVER must also show up; product-only if fire_rate x 0.18 < mde of that set (V-para ~17 %)>

## Budget (RULE 29)
wall_cap: <hours on the mini / MacBook for the whole arm>
calls_cap: <Haiku N / Opus N>
smoke: 10 items -> s/item, fire rate, parse rate; projected wall logged in QUEUE before any run > 2 h
kill_if: projected_wall > 1.5 x wall_cap OR fire_rate < <x> OR the smoke shows the failure mode the ceiling assumed away
checkpoint: <earliest point where the verdict is readable, e.g. first 25 % of a long generation run>
subset_step0: <build-time arms whose step 0 needs generation: random 15 % of items first; full step 0 only if the subset projects past the gate>; interim looks are futility-only

## Precheck (S2 of the smoke ladder, LOOP v2 §5; 0 calls; freeze refused while anything is unmeasured)
token_projection: <mean prompt tokens expected, or n/a> / token_budget: <n, or n/a>
disk_peak_gib: <peak disk use of the run in GiB, or n/a>
off_baseline: <run id of the OFF/control traces the 20 identity items are compared with, or n/a>
call_pattern: <e.g. "Haiku N=4 both orders on random20 then full">
lane: <mini-long|mac-gen|mac-cpu|judge>
opus_clause: <none|the pre-L1 near-miss clause>
wall_cap_h: <hours, same number as wall_cap in Budget>
parallelism: <concurrent units the full run uses: 1 for one server>
run_type: <4b-patch|deep|build|teacher|pack-build|latency|judge>
<!-- Read by smoke-project.py: every key is required and must be filled (a value starting with `<` is refused). The token gate is exact (mean prompt tokens over the smoke traces > token_budget = FAIL; the X2 gate failed by 20.5 tokens). Smoke rules by run_type: 4b-patch 20 identity items byte-identical OFF + 10 target items, <= 10 min; deep 3 v0.1 + 2 target, 0 empty/cut, <= 15 min; build/teacher 20 units, parse >= 90 %, empty <= 5 % (else KILL), s/unit within the speed gate; pack-build 1-pack dry run; latency 5 items on an idle CPU; judge 1-2 items x both orders on arm and control. FAIL-INFRA = any empty/cut answer, rc != 0, option not applied, projected wall (s/unit x n_full / parallelism) > 1.5 x wall_cap_h. -->

## Stages and rules
1. Smoke: gate (infra only), stop on FAIL-INFRA.
2. L1 slice (20 ids, Haiku 5.5-low N=4, both orders) vs control rows, rule above. A slice delta is not an estimate of the full-set delta.
3. Full set at the declared seeds, Haiku vs control; then L2 Opus judge.v1 N=4 only where l1_futility sends it (near-miss, or V-para / v0.2 kit).
4. Verdict (strict; the label names the judge and the set, e.g. "LEVER (Haiku, dev)" or "LEVER (Opus, V-para 2 seeds)"; adoption only after the two-seed V-para Opus confirmation, RULE 18):
   - **LEVER**: delta vs control, CI low > 0 and delta >= <threshold>.
   - **SMALL**: CI low > 0 but delta < <threshold>, or cheaper-parity clause met.
   - **NO**: otherwise.
- One generation per seed and stage; no rerun except an infrastructure error before the first token.

## Stop rules and budget
Disk >= 25 GiB, swap <= 8 GB, heavy lock, never restart Docker. Time and judge-call caps per stage.

## Outputs and exposure
`arms/<arm>/<ARM>.md` (cites this sha), `aggregates/`, `tools/`; traces/judgments under the blind runs dir. One row in `coordinator/EXPOSURES.md` plus the QUEUE entry.

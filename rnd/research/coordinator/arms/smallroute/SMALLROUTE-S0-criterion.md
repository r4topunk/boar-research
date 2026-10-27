# SMALLROUTE S0: oracle ceilings and 0-call signals for a per-item router (lite route on the 180; deep route on v0.2) (frozen 2026-10-16 18:1x, coordinator)

## Tags
Tags: probe
Ruleset: 30

## Question
Before any classifier is trained: (i) how much is there to gain from a perfect per-item router (a) between Qwen3-1.7B + X2b and Qwen3-4B + X2b on the 180 public self-tests (LITE5-180 Haiku judgments), (b) between the 4B (cut 6, s42) and deep + thinking 512 (DEEPTHINKV02 Opus rows) on v0.2 (110, dev; existing rows only, script-only, no plaintext read); (ii) do existing 0-call signals (fact-in-context fic, kept-source count, R2 "no on-topic source kept", retrieval score margin where logged) predict the per-item winner? Used for: the SMALLROUTE plan gate to T1 (train a small classifier). Mechanism seen / not seen; no engine change.

## Fixed inputs
- Lite: arms/lite5/aggregates/lite5-180.json (+ L1-* judgment files), fic-180.json, gate-180.json; arms/lite6/ buckets. Control = 4B + X2b rows, arm = 1.7B + X2b rows, same ids, Haiku 5.5-low N=4 both orders as judged.
- Deep: arms/deepthinkv02/aggregates (Opus rows, 2 seeds where present) vs the cut 6 s42 claim rows used there; arms/deeproute/deeproute-items.csv and analysis-ctl-*.json for the R2 signal.
- Scoped exception: v0.2 ids and judge rows only (keys + scores); no question text is read or printed.

## Power
expected_delta: n/a (ceiling measurement)
n: 180 (lite) / 110 (deep)
seeds: as judged (1 Haiku pass on the 180; Opus 2 seeds on v0.2 where present)
mde: 0.03 (180) / 0.05 (110, ceiling is an upper bound)
slice: n/a
l1_futility: n/a (probe)
reopen: DEEPROUTE R28 (new: a learned signal vs R2), DEEPBO2 R27 (not reopened: pre-generation only)
split: none

## Ceiling (RULE 29; 0 calls, before the freeze)
ceiling: this probe computes it
bar_ceiling: deep route on v0.2 only (dev); V-para not touched here
launch: probe, 0 calls
transfer: n/a

## Budget (RULE 29)
wall_cap: 1 h agent time
calls_cap: Haiku 0 / Opus 0; 0 paid
smoke: n/a (file analysis)
kill_if: a required file is missing (report which); any step would need plaintext from blind/
checkpoint: n/a
subset_step0: n/a

## Precheck
token_projection: n/a / token_budget: n/a
disk_peak_gib: 0
off_baseline: n/a
call_pattern: 0 calls
lane: agents
opus_clause: none
wall_cap_h: 1
parallelism: 1
run_type: latency

## Stages and rules
1. Lite: per-item paired delta (1.7B − 4B, ratio); oracle = max per item; ceiling = mean(oracle) − mean(4B); n_win (1.7B strictly better), n_tie. Signals: fic ∈ {0,1}, kept-source count, LITE6 bucket; for each signal the precision and recall of "route to 1.7B" against "1.7B ≥ 4B − 0.02" (speed route tolerates a 0.02 loss); report the hybrid mean per signal.
2. Deep: same on v0.2 (oracle of 4B vs deep+think per item; ceiling; R2 capture as baseline; any logged retrieval signal's capture).
3. Verdict (mechanism): SEEN-LITE if lite ceiling ≥ 0.03 and a signal reaches precision ≥ 0.70 at recall ≥ 0.40; SEEN-DEEP if deep ceiling ≥ 0.05 raw and a signal captures ≥ 70 % of the gain at ≤ 40 % routed (R28 clause); NOT SEEN otherwise. Output arms/smallroute/S0.md (≤ 60 lines, tables) + items.csv.

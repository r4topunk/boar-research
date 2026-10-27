# Claim runs on cut 6 — coordinator authorisation (r4to confirmed in this session 2026-10-06), frozen before any run

r4to decisions (2026-10-06, relayed by the device session and confirmed by r4to here): (1) the device/claim build is FROZEN at cut 6; only routing/safety fixes that leave v0.1 answers unchanged may be added later; answer-changing arms (e.g. CRYPTOTRUTH) do not enter the claim build. (2) The v0.2 held-out L3 + V-para claim runs are released for cut 6 on desktop. Supporting evidence for device = desktop: A15 cut 3 partial (25 judged v0.1 items) phone 0.482 vs desktop 0.478 / 0.493 on the same ids (boar-eval/runs/device-tester-a15/cut3-v01-partial).

Engine: cut 6 = arms/detfu/detmax-on-cut4.vs-0cfd4a77.patch (sha256 824e0b35fcdfe46b25bdb824516b5ccec387247d14a461f7bbfd9fb332fb953b; tree b0f53fe0d30abb8395e95971e3be4dfc4b406d394bf346dedb525a2678479daa). No code change of any kind during the claim runs.
Runner: committed boar-eval adapter (73b9d2c or later, no adapter code change after this file) with BOAR_RUNNER_PROFILE=ship (gate on), detector v3b ON, node backend — the configuration that reproduces the be-ship runner used for the cut 3 claim runs (RUNNERS.md). Record the adapter commit and sha in the results.

## Run A — bench v0.2 held-out L3 (second spend of the held-out; first was cut 3, 2026-10-05)
- Plan, addenda, config, seeds (s42 + s43), item set (ship-all.en.ids), judge (judge.v1, NO --effort flag, both orders) exactly as CLAIM-RUNS-cut3.md Run A.
- Judge economy (allowed): for items whose answer text is byte-identical to the cut 3 claim run of the same seed, reuse that run's verdicts (single named source: blind/bench-v02/runs-cut3/); judge every changed item fresh. Report counts identical/changed.
- Report: raw ratio (headline) + floor-removed + above-always-decline, stratified CI per the plan; EN-only primary, full view beside; paired Δ vs cut 3 claim run, vs runs-ship and vs E3; safety per the plan (keys + counts only for coordinator adjudication).
## Run B — V-para (blind/V-para)
- Exactly as CLAIM-RUNS-cut3.md Run B (configs (b) primary and (a) beside, seeds/judge per VPARA-BARS.md, venue scorer per RUN-MAPPING.md), with the same identical-text verdict reuse from blind/V-para/runs-cut3/.
- Report P1–P5 + ladder via claim_report.py; paired Δ vs cut 3.
## Blind rules (both runs)
- Identical to CLAIM-RUNS-cut3.md: script-only access; only ids, counts, hashes, aggregate numbers in the runner's context; any other exposure = stop and report.
- Outputs under blind/bench-v02/runs-cut6/ and blind/V-para/runs-cut6/. Only the aggregate report leaves blind/ → coordinator/CLAIM-RESULTS-cut6.md.
- No tuning, no re-runs except for a technical failure (logged with reason). Exposure logged in QUEUE.md.

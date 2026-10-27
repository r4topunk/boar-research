# LITE5: does the X2b retrieval-reach lever (HEADPASS-X2b, +0.066 Opus on the 4B) transfer to the lite model Qwen3-1.7B Q4_K_M on selftest20? (frozen v2 2026-10-16 00:0x by the LITE5 agent; Haiku, dev)

Frozen after the 3-item smoke (runs/smoke/lite5-smoke-on) and the 0-judge host-identity run (runs/lite5-off-st20-*), before any judged run.
Mechanism = HEADPASS-X2b exactly: criterion HEADPASS-X2-criterion.md 1b70f6f3… + addendum 1 4b3578e786cafb56dd1230912cb4699ae9ec5219a708fe1f13218157be25d38e (X1 neighbours + D ≤ 2 dense candidates appended outside the keep step, per-item budget S prompt + 600 engine tokens; settings packHeadPass "a2" + packDense2 "append-budget"; item pack = its v3proto sidecar copy).
Tree kiln-local/be-0cfd4a77-cut7-headpass-x2 (PATCH_SHA256 0fba26b8…, headpass-x2b.vs-cut7.patch be413d7d…, ARM cut7-headpass-x2). Adapter **be/adapter-lite5.ts 5785ffc48240f8397e6e999fd3134f938c4fc516946180119ce8a5511aff36f2** = 8dd1faff (the X2b opts-forwarding adapter, untouched beside it) + LITE2's qwen3-1.7b-q4km MODELS/ADAPTER_CATALOG entries + BONSAI2's BOAR_SERVER_EXTRA_ARGS hunk (tools/adapter-lite5.vs-8dd1faff.patch 21bf555e…). Runner tools/run_lite5_gen.sh, tools/gen_all.sh; requests tools/mkreq_lite5.py.
Inputs: LITE2 (LITE2-criterion 628f60c2…, LITE2.md 81426218…: model, selftest20.ids abc23353…, bench-st20, OFF traces + Haiku rows l-st20-s42, 4B rows c4b-st20-s42); LITE3 (LITE3.md a37dd0f3…: fact-in-context 6/20, L buckets).

## Tags
Tags: none
Ruleset: 30

## Question
LITE3 found the gold fact in the 1.7B's kept context on 6/20 self-tests and *invented* as its largest loss bucket; LITE4 showed a prompt rule does not move it. If the wall is reach (as for the 4B), X2b should lift the 1.7B too. Arm ON = cut 7 + X2b + Qwen3-1.7B on selftest20; control OFF = the LITE2 1.7B rows (reused). Use: whether the lite tier inherits the pack-line default (X2b) recommended for the 4B.

## Fixed inputs
- ON: requests lite5-on-st20-<pack>-s42 (9 per-pack files) = the 4B X2b requests (headpass-st/gen-x2b) filtered to selftest20.ids with modelId -> qwen3-1.7b-q4km; mkreq_lite5.py asserts each equals LITE2's l-st20 request except runId, arm, the two X2b settings and the item pack's sidecar sha. Model unsloth/Qwen3-1.7B-GGUF @ d7f544ee Q4_K_M, sha b139949c…1897 (downloaded to the MacBook from the MODELS.md recipe, verified). b11010 llama-server (spikes/llama-b11010-cpu), `--reasoning off` + enable_thinking false, threads 4, ctx 4096, seed 42, persona succinct, quickFirst true / alwaysComplete false, mmbert detector :8094, MacBook M1 Pro.
- OFF (control, REUSED, not regenerated for judging): lite2/runs/l-st20-s42 traces + Haiku 5.5-low rows (mini M4). 4B reference: lite2/runs/c4b-st20-s42 rows (4B plain). Descriptive: the 4B X2b Haiku rows on the same 20 ids (headpass-st/gen-x2b).
- Host identity (0 judge, aggregates/hostid.json): the 1.7B OFF re-generated on the MacBook in the X2b tree (settings unset) vs LITE2's mini traces: kept 20/20, promptTokens 20/20, tier 20/20, errors 0, answer text 5/20 identical (the 5 = no-LLM or identical generations; the other 15 differ by host sampling only, reason-code diffs are answer-level citations codes only). Declared consequence: Δ(ON − OFF) includes one host re-sample of the generation on 15/20 items (a seed-like draw); reported, rule unchanged. The MacBook OFF traces are never judged.

## Power
expected_delta: +0.03…+0.06 raw ratio (source: the 4B X2b − S on these same 20 ids, Haiku rows reused, 0 calls: +0.064 (+0.008…+0.128); the 1.7B converts kept facts worse (LITE3 not_read 3/6 present items), so ≈ 0.5–1× of the 4B's gain)
n: 20 (selftest20, judged)
seeds: 1
mde: ≈ 0.04–0.05 raw at n = 20 (LITE2/LITE3, Haiku), plus host re-sample noise: the arm can see a 4B-sized effect, not a half-sized one
slice: lite2/selftest20.ids (abc23353…)
l1_futility: n/a (Haiku only, no Opus stage)
reopen: n/a (new lite-tier line: LITE2/LITE3/LITE4)
split (declared): (a) LITE3's L bucket per item: invented 7 / thin 6 / not_read 3 / other 1 / health-safety 3; (b) reach: newly present under X2b (projected 6: factbook-001, factbook-004, medlineplus-008, bitcoin-019, outdoors-020, travel-017) / present under OFF already (6) / fact absent in both (8); per cell mean Σboar/Σref ON vs OFF (LITE3 estimator), descriptive.

## Ceiling (RULE 29; 0 calls, before the freeze)
ceiling: projected fact present 6 -> 12/20 from the 4B X2b traces (retrieval is model-independent; smoke codes and kept lists identical to the 4B X2b traces 3/3)
bar_ceiling: n/a (pack self-tests, lite tier; not a bounty-bar lever)
launch: coordinator brief 2026-10-15 (MacBook generation lane free)
transfer: product-only (lite tier pack line)

## Budget (RULE 29)
wall_cap: 1 h (20 generations ≈ 6 s + 9 server loads; judge ≈ 5 min)
calls_cap: Haiku 80 / Opus 0 (40 = selftest20 ON; the other 40 only for the kit slice of stage 6, else unspent)
smoke: 3 items (qa-outdoors-se 007/008/020, X2b ON) -> 0 errors, 0 empty, 0 reasoning tokens, no `<think>`, headpass:* codes on 3/3 (identical to the 4B X2b traces 3/3, kept lists identical 3/3), prompt growth vs the 1.7B OFF +215 / +317 / +339 (≤ 600), wall 21 s incl. load
kill_if: any error/empty answer, reasoning tokens > 0 or `<think>`, any 0-call gate FAIL (-> stop, 0 Haiku), projected wall > 1.5 h
checkpoint: the 0-call gate, before any judge call
subset_step0: n/a

## Precheck (S2 of the smoke ladder; 0 calls)
token_projection: 738 (smoke mean timing.promptTokens: 775, 815, 624; the same 3 OFF: 560, 498, 285, mean 447.67) / token_budget: 1047.67 (= OFF smoke mean + 600, X2b's per-item budget)
disk_peak_gib: 1.1 (the 1.7B 1.03 GiB; MacBook free 8 GiB after the download, floor 4)
off_baseline: l-st20-s42 (LITE2, mini)
call_pattern: Haiku 5.5-low N=4 shards, both orders, ON vs gold on selftest20 (40 calls); preflight live probe disabled (PREFLIGHT_PROBE_IDS=0) to stay at 40; 0 Opus; 0 paid
lane: mac-gen
opus_clause: none
wall_cap_h: 1
parallelism: 1
run_type: 4b-patch

## Stages and rules
1. Smoke (done before the freeze): see Budget; `arm.sh arm-st-L5.conf smoke runs/smoke/lite5-smoke-on.traces.jsonl --n-full 20 --marker headpass:` writes smoke.verdict.json for this sha.
2. Generate ON (one llama-server at a time, MacBook): the 9 per-pack files, merged to runs/lite5-on-st20-s42.traces.jsonl.
3. **0-call gate (tools/gate5.py, 20 ON traces):** G0 0 errors, 0 empty, 0 reasoning tokens, no `<think>`; G1 headpass:* reason codes and kept (title, section) lists identical to the 4B X2b traces on 20/20 (retrieval is model-independent); G2 the budget behaved as in the 4B LEVER run: per item ON − OFF timing.promptTokens (OFF = LITE2 traces) equal to the 4B X2b − S growth (headpass-st/gen-x2b vs c4b-st20 traces) on every item with an LLM call in both (the budget itself is on the engine's approximate count, X2b addendum 1; timing.promptTokens is the server tokenizer's count, so it can exceed 600 on an item exactly as it did for the 4B); G3 changed vs OFF (kept or promptTokens) ≥ 0.20; G4 fact present ON (tools/fic.py: S_present from split-x2b OR an oracle fact chunk among the appended ids) ≥ 10/20. FAIL -> stop, 0 Haiku.
4. Gate PASS -> Haiku 5.5-low N=4 both orders, ON vs gold on the 20 (40 calls; arm.sh l1, control = LITE2 L rows). Paired Δ(ON − OFF) = deepvpara/tools/paired.mjs on the ON and OFF judgment sets (items resampled jointly, 2000 boots). Also ON − 4B plain (c4b rows), and descriptive ON vs the 4B X2b rows; splits above; fact present ON vs OFF; W/T/L vs gold; p50 total and prompt tokens.
5. **Verdict (frozen; Haiku, dev):** **LEVER-shaped** if paired Δ ratio ≥ +0.03 AND CI low > 0; **DIRECTION-POSITIVE** if Δ > 0 otherwise; **FLAT** if Δ = 0.0000; **DIRECTION-NEGATIVE** if Δ < 0. No adoption from this arm; LEVER-shaped licenses a larger-n or Opus confirmation and the stage-6 kit slice.
6. Kit slice (only if LEVER-shaped): random20-v02 under LITE2's scoped script-only exception (counts/ids only, EXPOSURES row), X2b ON + 1.7B with the claim kit (no format-v3 pack installed). X2b does not fire without a pack sidecar, so the check is 0-call identity vs LITE2's l-kit-v02-s42-slice traces on kept + promptTokens + absence of headpass:add codes; the reserved 40 Haiku calls are spent (ON vs gold, paired vs LITE2 OFF rows) only if any kit item's kept list or prompt differs.
- One generation per run. No rerun, except after an infrastructure error before the first token.
- Freeze history: v1 077b1dbd63ff05ba7619e9fd30ea70cbdfa3a397ffb83404ef3cbe6897bd18f8 (LITE5-criterion.v1.md) had G2 "per item ON − OFF promptTokens ≤ 600" on timing.promptTokens; the 0-call gate on the 20 ON traces FAILED it on one item (st-boar-factbook-001 +633; aggregates/gate5.v1-FAIL.json), with G0/G1/G3/G4 PASS. The 4B X2b traces show the identical +633 on that item and identical growth on all 17 LLM items: the gate used the wrong counter (server tokenizer vs the engine count the budget is defined on), not a mechanism difference. Re-frozen as this v2 before any judge call (0 Haiku spent, no judged number seen); the ON traces are reused, not regenerated; the smoke verdict is re-written for this sha.

## Stop rules and budget
MacBook disk ≥ 4 GiB (DISK-LOG line for the model download and its keep/delete: keep only if free ≥ 8 GiB after), one llama-server at a time (busy.sh), never stop the :8094 detector or anything else; none left running. Haiku ≤ 80 (40 unless stage 6 judges), Opus 0, 0 paid. No git push; `git -C rnd commit` of the arm files allowed.

## Outputs and exposure
`arms/lite5/LITE5.md` (cites this sha), `aggregates/lite5.json` + gate/fic/hostid/L1 JSON, `tools/`, traces under `runs/`. Self-tests are public; blind/ only for stage 6 (then one EXPOSURES row). rnd/veil/ is never read. QUEUE row (tools/qrow.sh), BACKLOG LITE-TIER row.

# LITE5-180: does LITE5's X2b gain on the lite 1.7B (+0.080 on selftest20) hold on all 180 public self-test items, with OFF regenerated on the same host? (frozen 2026-10-16 00:0x by the LITE5-180 agent; Haiku, dev)

Frozen before any LITE5-180 run. Mechanism = HEADPASS-X2b exactly (HEADPASS-X2-criterion.md 1b70f6f3… + addendum 1 4b3578e7…; settings packHeadPass "a2" + packDense2 "append-budget"; item pack = its v3proto sidecar copy). Same tree, adapter, model, runner and env as LITE5 (LITE5-criterion.md v2 9ba8bbf30eb4ec32633429046a3a0717cdd42900a8b4aec92dc11fe944388f16): tree kiln-local/be-0cfd4a77-cut7-headpass-x2 (PATCH_SHA256 0fba26b8…), adapter be/adapter-lite5.ts 5785ffc48240f8397e6e999fd3134f938c4fc516946180119ce8a5511aff36f2, model shared-models/lite/Qwen3-1.7B-Q4_K_M.gguf sha b139949c5bd74937ad8ed8c8cf3d9ffb1e99c866c823204dc42c0d91fa181897, b11010 llama-server `--reasoning off` (+ enable_thinking false), -t 4, seed 42, MacBook M1 Pro, mmbert detector :8094.

## Tags
Tags: none
Ruleset: 30

## Question
LITE5 (n = 20, Haiku) found Δ(ON − OFF) +0.080 (+0.033…+0.130) for X2b on the 1.7B, with OFF from another host (mini) re-sampled on 15/20 generations. Does the gain hold on the 180 self-tests (the set on which X2b was adopted for the 4B: Haiku +0.056, Opus +0.066), with both arms generated on the MacBook so the paired Δ has no host confound? Use: whether the lite tier inherits X2b as its pack-line default, and where the 1.7B + X2b sits against the 4B plain / 4B X2b on the full set.

## Fixed inputs
- ON: requests lite5-180-on-<pack>-s42 (9 files × 20) = headpass-st/gen-x2b/st-<pack>-cut7-headpassx2b-s42.requests.jsonl (the 4B X2b requests) with only modelId -> qwen3-1.7b-q4km and runId changed (tools/mkreq_180.py asserts it; on the 20 selftest20 ids it also asserts ON == LITE5's lite5-on-st20 rows apart from runId).
- OFF: the same rows with the two X2b settings removed (= the cut 7 settings quickFirst true / alwaysComplete false), runId lite5-180-off-<pack>-s42; regenerated on the MacBook in the same tree (settings unset -> X2b inert). mkreq_180.py asserts OFF == the 4B plain request (packs/selftest-runs/st-<pack>-cut7-s42) apart from runId, arm, modelId and the item pack's kit sha (sidecar copy).
- Reference rows (not regenerated, not re-judged): 4B plain Haiku 5.5-low rows packs/selftest-runs/st-<pack>-cut7-s42.judgments.jsonl (SELFTEST-SCORES); 4B X2b Haiku rows headpass-st/gen-x2b/st-<pack>-cut7-headpassx2b-s42.judgments.jsonl. Same bench (boar-eval/bench/selftest/<pack>), same judge model/effort, same 180 ids.
- LITE5's slice judgments are not reused (traces are never byte-identical: timing fields), so all 180 × 2 arms are judged fresh.

## Power
expected_delta: +0.03…+0.06 raw ratio (source: the 4B X2b − S on the 180, Haiku +0.056 (+0.036…+0.076); LITE5 1.7B selftest20 +0.080 (+0.033…+0.130), whose slice included the newly-present-rich ids; the 1.7B converts kept facts less well than the 4B, LITE3)
n: 180 (all public self-tests, 9 packs × 20)
seeds: 1
mde: ≈ 0.03 raw at n = 180, one seed, Haiku (4B X2b − S CI half-width ±0.020 at n = 180; the 1.7B is noisier)
slice: n/a (full 180; selftest20 ⊂ 180 is the LITE5 slice)
l1_futility: n/a (Haiku is the deciding judge on this dev set; no Opus stage in this arm, Opus 0)
reopen: n/a (LITE5 follow-up: LITE5.md "Next: an Opus or larger-n confirmation (the 180 self-tests on the 1.7B)")
split (declared): (a) per pack (9) ON − OFF; (b) fact in context (tools/fic180.py = fic.py's rule on the 180: OFF present = split-x2b S_present; ON present = S_present OR an oracle fact chunk of the item's pack among the appended ids of the ON trace): newly present under ON / present under OFF already / absent in both, plus the 2-cell "gained vs not"; LITE3 buckets n/a at 180 (only labelled on selftest20). Descriptive: 1.7B X2b − 4B plain and 1.7B X2b − 4B X2b (paired, same ids), 1.7B OFF − 4B plain.

## Ceiling (RULE 29; 0 calls, before the freeze)
ceiling: retrieval is model-independent (LITE5 G1 20/20): projected fact present 35 -> ≈ 97/180 (the 4B X2b traces); 4B gain where newly present +0.155 (Haiku) on 30 items -> ≈ +0.03 pooled from that cell alone, plus the present-under-X1 cell
bar_ceiling: n/a (pack self-tests, lite tier; not a bounty-bar lever)
launch: coordinator brief 2026-10-15 (LITE5-180; MacBook generation lane, lock mac-gen main)
transfer: product-only (lite tier pack line)

## Budget (RULE 29)
wall_cap: 1.5 h (360 generations ≈ 5 s + 18 server loads ≈ 45 min; judge ≈ 15 min)
calls_cap: Haiku 720 / Opus 0
smoke: LITE5's 3-item smoke (runs/smoke/lite5-smoke-on: 0 errors, 0 empty, 0 reasoning tokens, headpass:* 3/3, mean prompt 738 vs budget 1047.67, 5.03 s/unit), same tree/adapter/model/env; re-scored for this sha with `arm.sh arm-st-L5-180.conf smoke … --n-full 360 --marker headpass:` (LITE5's own verdict kept as smoke.verdict.lite5-v2.json)
kill_if: any error/empty answer, reasoning tokens > 0 or `<think>`, projected wall > 2.25 h; generation checkpoint below
checkpoint: after the first 3 packs (qa-travel-se, qa-ethereum-se, qa-bitcoin-se = 60 items, both arms): KILL (0 Haiku, stop generation) if ON − OFF fact-in-context gain ≤ 0 items, or kept-diff share (ON kept list ≠ OFF kept list) < 50 %
subset_step0: n/a

## Precheck (S2 of the smoke ladder; 0 calls)
token_projection: 738 (LITE5 smoke mean timing.promptTokens) / token_budget: 1047.67 (LITE5: OFF smoke mean + 600)
disk_peak_gib: 0.1 (traces + logs; no new model; MacBook free 8.9 GiB, floor 4)
off_baseline: lite5-180-off-*-s42 (regenerated here, MacBook); 0-call identity anchor = LITE5's MacBook lite5-off-st20-s42 / lite5-on-st20-s42 on the 20 shared ids (same host, seed, tree: answer text expected identical; reported, rule unchanged)
call_pattern: Haiku 5.5-low N=4 shards, both orders, ON and OFF vs gold on the 180 (2 × 360 = 720 calls); preflight live probe disabled (PREFLIGHT_PROBE_IDS=0) to stay at 720; 0 Opus; 0 paid
lane: mac-gen
opus_clause: none
wall_cap_h: 1.5
parallelism: 1
run_type: 4b-patch

## Stages and rules
1. Generate on the MacBook, one llama-server at a time (busy.sh), per pack OFF then ON, packs in the X2b chain order (travel, ethereum, bitcoin, health-se, outdoors, firstaid, medlineplus, factbook, simplewiki). Per run gate (tools/gate180.py run): 20 rows, 0 errors, 0 empty, 0 reasoning tokens, no `<think>`; ON: a `headpass:` reason code on ≥ 1 item of the run and no `headpass:dense:nosidecar`/`noopts` on an item whose 4B X2b trace lacks it; OFF: no `headpass:add`/`headpass:dense:add` code. FAIL -> stop.
2. Checkpoint (after pack 3, 0 calls): see Budget; KILL rule frozen there.
3. 0-call gate on the 180 (tools/gate180.py all): G0 as stage 1 on all 360; G1 ON headpass:* codes and kept (title, section) identical to the 4B X2b traces on ≥ 170/180 (retrieval is model-independent; health-strict detector calls are deterministic per host, LITE5 20/20); G2 changed ON vs OFF (kept or promptTokens) ≥ 0.50; G3 fact present ON > OFF. FAIL -> stop, 0 Haiku.
4. Haiku 5.5-low N=4 both orders, ON and OFF vs gold, per pack (bench boar-eval/bench/selftest/<pack>; fail-closed check_judgments.py; 720 calls). Estimator = packs-l2/tools/l2_agg.py (the HEADPASS-X2b 180 estimator: per-item bootstrap of the ratio-of-sums difference, B 2000, seed 11, paired on queryId). Report: paired Δ(ON − OFF) with CI (raw and above-min), per pack, fact-in-context splits, b/w counts; ON − 4B plain, ON − 4B X2b, OFF − 4B plain; p50 total ms, ttft, prompt tokens and answer words ON vs OFF.
5. **Verdict (frozen; Haiku, dev 180):** **LEVER (Haiku, dev 180)** if paired Δ(ON − OFF) raw ≥ +0.03 AND CI low > 0; **SMALL** if CI low > 0 but Δ < +0.03; **NO** otherwise. No adoption from this arm (product-only lite tier; an Opus pass, if wanted, is a coordinator call).
- One generation per arm and pack. No rerun, except after an infrastructure error before the first token.

## Stop rules and budget
MacBook disk ≥ 4 GiB, one llama-server at a time (busy.sh), never stop the :8094 detector or anything else; none left running at the end. Haiku ≤ 720, Opus 0, 0 paid. No git push; `git -C rnd commit` of the arm files allowed.

## Outputs and exposure
`arms/lite5/LITE5-180.md` (≤ 60 lines, cites this sha), `aggregates/lite5-180.json` + gate/checkpoint/fic JSON, `tools/*180*`, traces + judgments under `runs/180/`. Self-tests are public (bench/selftest); no blind/ read; rnd/veil/ never read. QUEUE row (tools/qrow.sh, tag main), BACKLOG LITE-TIER row, CLOSED.md row if LEVER or NO.

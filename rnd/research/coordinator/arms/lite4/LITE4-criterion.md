# LITE4: does a source-bound reading rule for the lite model (Qwen3-1.7B Q4_K_M) move its random20-v02 score, by attacking LITE3's "invented" bucket? (frozen v2 2026-10-15 23:3x by the LITE4 agent; measurement arm, direction-only)

Frozen after the 5-item smoke (l4-smoke ON + l4off-smoke OFF, blind/bench-v02/runs-lite4/) and before any 40-item generation or judge call.
Engine patch tools/lite4.patch caff1bff8aa2134c7c4bc73bdc503536f2e6ffdd6d7651cae5ab34b8c50647b8 (cut 7 src: context.ts + answer.ts + answer.test.ts; tsc clean, src/routing vitest 593/593 on a scratch copy of wt/cut7; runs/tsc.txt, runs/vitest-routing.txt).
Mini side tree <runner>/kiln/be-0cfd4a77-cut7-lite4 (ARM cut7+lite4, answer.ts ff1f0ced…, be-repo -> cut7 be-repo), side dir be-repo-lite4/ (adapter.ts ff9d36b6… = LITE2's e37b5a89… + one line `LITE_SOURCE_BOUND=1 -> deps.liteSourceBound`). Runner lite4-remote-run.sh (sha in .sha256; arms L4 = ON, L4OFF = switch unset). Gate script tools/gate0.py 092fde3bb17b26c4…; gate ids aggregates/gate-ids.json (from LITE3 aggregates/lite3.json).

## Tags
Tags: none
Ruleset: 30

## Question
LITE3: the 1.7B's largest loss bucket vs the 4B is *invented* (2.41 of 4.30 points, 56 %). The arm adds one prompt rule for the lite model only (deps.liteSourceBound): with kept passages "use only the numbered sources: state only what they say, key line first, cite; if they do not answer, say so"; with no kept source (no-source-memory) the app's notice stays and NO_SOURCE_INSTRUCTION is replaced by "answer from memory in one hedged sentence; if not sure a specific claim is true, or the premise is not supported, say that"; with no kept source and no app notice (no-good-source, not memory) "say so in your first sentence, then one hedged sentence…". Health routes keep HEALTH_GROUNDING_INSTRUCTION; deterministic routes are untouched. OFF (switch unset) = byte-identical: l4off-smoke answers = LITE2 l-smoke answers 5/5, same prompt tokens 5/5. Use: direction for the lite-tier prompt (post-10-20 lite integration).

## Fixed inputs
- Arm **ON** (L4): side tree above, Qwen3-1.7B Q4_K_M (unsloth @ d7f544ee, sha b139949c…1897, re-downloaded from the MODELS.md recipe and verified), b11010 llama-server, `--reasoning off` + enable_thinking false, threads 4, ctx 4096, seed 42, persona succinct, engine sampler, LITE_SOURCE_BOUND=1, noplaces, claim kit, quickFirst true / alwaysComplete false.
- Kit: l4-on-v02-s42-slice = LITE2 l-kit-v02-s42-slice requests with runId/arm rewritten (arm.sh mkreq, sha e3d84050…). St20: l4-on-st20-<pack>-s42 (9 per-pack files, LITE2 requests rewritten), generated for the 0-call gate only (never judged here).
- Control **OFF** (L) = the LITE2 1.7B runs, REUSED: kit traces + Haiku 5.5-low rows `blind/bench-v02/runs-lite2/l-kit-v02-s42-slice.*`, st20 traces `arms/lite2/runs/l-st20-s42.traces.jsonl`. 4B reference = dv-C-v02-s42 Haiku rows (reused).
- Scoped script-only exception (coordinator 2026-10-15, as LITE2/LITE3): scripts read blind/bench-v02 (random20 requests, dv-C rows, runs-lite2); the agent prints counts/ids/aggregates only, never v0.2 item/answer/gold text.

## Power
expected_delta: +0.015…+0.024 raw ratio (source: LITE3 LITE4-candidate: invented 2.41 points x 25–40 % recovery over 40 items)
n: 20 (random20-v02, judged)
seeds: 1
mde: ≈ 0.04 raw at n = 20 (LITE3; Haiku): expected_delta < mde, so the arm cannot decide; it is run as a direction-only measurement on r4to's line (quick tests around a 2B-class model) and gets no LEVER/SMALL/NO label
slice: random20-v02.ids (a3e43672…)
l1_futility: n/a (measurement, direction-only; no Opus stage, no transfer)
reopen: n/a (new lite-tier line, LITE2/LITE3)
split: paired Δ(ON − OFF) by LITE3's L bucket on random20: **invented** = the 6 kit ids of LITE3 (crypto-B05, explanation-B01, honesty-refusal-A02, honesty-refusal-B01, reasoning-A08, reasoning-B10) vs **other** = the remaining 14 (5 health-safety included). (The brief's "invented 10 / other 10" is not realisable on random20: 4 of LITE3's 10 invented ids are self-tests, which are not judged in this arm.)

## Ceiling (RULE 29; 0 calls, before the freeze)
ceiling: n/a (measurement arm)
bar_ceiling: n/a (lite tier, product-only; never preempts bar work)
launch: measurement requested by the coordinator / r4to 2026-10-15 (mini free; MacBook lane busy with HEALTHGAP-IMPL)
transfer: product-only

## Budget (RULE 29)
wall_cap: 1 h (mini: 40 generations at ≈ 3–5 s + 9 st20 server loads + judge ≈ 5 min)
calls_cap: Haiku 40 / Opus 0
smoke: 5 items (l4-smoke = LITE2 l-smoke's 5 requests: 3 v0.1 + 2 slice) -> s/item 4.4, empty 0, reasoning 0, prompt growth +38 tokens on the 4 sourced items, +19 on the memory item
kill_if: any error/empty answer, reasoning tokens > 0 or `<think>` in any ON answer, the 0-call gate FAIL (-> stop, 0 Haiku), projected wall > 1.5 h
checkpoint: the 0-call gate, before any judge call
subset_step0: n/a

## Precheck (S2 of the smoke ladder; 0 calls)
token_projection: 517.6 (l4-smoke mean timing.promptTokens: 294, 669, 760, 413, 452; OFF l-smoke 483.4) / token_budget: 543.4 (= OFF smoke mean 483.4 + 60, the LITE3 G4 allowance)
disk_peak_gib: 1.1 (the 1.7B 1.03 GiB + side tree 17 MB; free 25.13 GiB after the download, floor 25)
off_baseline: l-kit-v02-s42-slice (kit, LITE2), l-st20-s42 (st20, LITE2)
call_pattern: Haiku 5.5-low N=4 shards, both orders, ON kit vs gold on random20 (40 calls); preflight live probe disabled (PREFLIGHT_PROBE_IDS=0) to stay at 40; 0 Opus; jev ≤ 20 requests (cap [usage detail removed]) optional
lane: mini-long
opus_clause: none
wall_cap_h: 1
parallelism: 1
run_type: 4b-patch

## Stages and rules
1. Smoke (done before the freeze): lite2/tools/gate.py (GATE_MODEL=qwen3-1.7b-q4km) PASS on l4-smoke and l4off-smoke; OFF identity 5/5 vs LITE2; `arm.sh smoke --n-full 40 --marker lite:source-bound` (prefix: sourced/memory/nosource) writes the verdict for this sha. Freeze history: v1 26c7cab3… had `--marker lite:source-bound-sourced`, which the memory-route smoke item cannot carry -> smoke FAIL (marker 1/5, infra-only, no other reason); re-frozen as this v2 before any 40-item run.
2. Generate ON (one llama-server at a time): l4-on-v02-s42-slice (20), then the 9 st20 per-pack runs (20), merged to runs/l4-on-st20-s42.traces.jsonl. Infra gate per run (lite2/tools/gate.py); precheck vs OFF (`--min 0`, marker `lite:`).
3. **0-call gate (frozen as in LITE3; tools/gate0.py over the 40 items, ON vs OFF):** G0 infra: 0 errors, 0 empty, 0 reasoning tokens, no `<think>` on all 40 ON traces; **G1** answer changed (whitespace-normalised exact string, the same_answer.py rule) on ≥ 8 of the 10 LITE3 invented ids; **G2** hedging on the 22 other core ids: items matching the fixed regex HEDGE in gate0.py (the app's fixed no-source notice removed first) ON ≤ OFF + 2; **G3** median answer words over the 32 core ids ON ≥ 0.9 × OFF; **G4** median prompt tokens over the 32 core ids (items with an LLM call in both) ON − OFF ≤ 60 (both the difference of medians and the median of paired differences); **G5** the deterministic items (health-safety ids with no LLM call in OFF) byte-identical with no LLM call. Gate FAIL -> stop, report the gate numbers, 0 Haiku.
4. Gate PASS -> Haiku 5.5-low N=4 both orders on the 20 kit ids, ON vs gold (40 calls; arm.sh l1, control[0] = L). Paired Δ(ON − OFF) = deepvpara/tools/paired.mjs on the ON and OFF judgment sets (items resampled jointly, 2000 boots); also ON − 4B (dv-C rows) for context; per-bucket means (split above); W/T/L vs gold; p50 total latency.
5. **Verdict (frozen, direction-only; no LEVER/SMALL/NO label):** **DIRECTION-POSITIVE** if paired Δ ratio (ON − OFF) on random20 > 0 AND the invented-bucket mean ratio ON > OFF; **DIRECTION-NEGATIVE** if Δ < 0; **FLAT** otherwise (Δ = 0, or Δ > 0 with the invented mean not up). The CI is reported, not used: n = 20 cannot decide at the expected size. A DIRECTION-POSITIVE read licenses at most a larger-n follow-up (st20 + kit, or v0.2 full), never adoption.
- One generation per run. No rerun, except after an infrastructure error before the first token.

## Stop rules and budget
Disk ≥ 25 GiB on the mini (DISK-LOG row for the model download and its deletion), swap ≤ 8 GB, heavy lock, never Docker / :8094 / ollama; one llama-server at a time, none left running. Haiku ≤ 40, Opus 0, jev ≤ [usage detail removed].

## Outputs and exposure
`arms/lite4/LITE4.md` (cites this sha), `aggregates/lite4.json` + gate0/precheck/L1 JSON, `tools/`, st20 traces under `runs/`; v0.2 traces/judgments under blind/bench-v02/runs-lite4/. One row in coordinator/EXPOSURES.md plus the QUEUE row.

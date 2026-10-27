# HEALTHDROP step 0: does a default-off rescue of the dropped health-pack source turn the plain no-source health refusals on the 180 into extractive answers, without touching anything else? (frozen 2026-10-16 before any patch run or replay; 0 LLM / 0 judge / 0 paid; public items only)

## Tags
Tags: probe
Ruleset: 30

## Question
RESCOPE (arms/healthfallback/RESCOPE.md §3-§4): on the 180 public self-tests with the item's pack installed, 18 turns get the plain no-source health refusal (noHealthSourceAnswer) after the health-strict topic filter (onHealthTopic) dropped every retrieved source (grounding:health-off-topic-dropped-N on 18/18); Opus L2 (existing headpass-st/gen-x2b rows) 0.347 on the 18 vs 0.591 on the other 162; ceiling +0.024 pooled. HEALTHDROP keeps the best dropped chunk from a health pack whose title names the question's topic and lets the turn take the existing extractive path. Use: PASS -> the declared Haiku probe below may run at a later META (not in this step); FAIL -> BACKLOG row 9 closes (CLOSED row).

## Fixed inputs
- Base = kiln-local/be-cut7-warn (ARM pr1+warn = wt/pr1 8ac9eb7a + warnspec/tools/warn.patch v2 11294894…; pins warnspec/tools/pins.*).
- Arm = kiln-local/be-cut7-healthdrop (ARM pr1+warn+healthdrop) = base + tools/healthdrop.patch (sha in tools/healthdrop.patch.sha256), engine switch deps.healthDrop (default off), adapter env HEALTHDROP=1.
- Mechanism (fixed here): in health-strict, after onHealthTopic + the best-source restore, when 0 sources are left, the turn is not a HEALTHGAP turn, no condition card applies (conversationCondition null), the tier is not deep and the mode is not multipass: keep the first chunk in retrieval order of the (substantive) raw list whose packId is in {boar-medlineplus-en, qa-health-se, boar-firstaid-en} (warn.ts HEALTH_PACK_IDS, by chunkId prefix) and whose bare title (source label prefix stripped) shares >= 1 term with the question's content words (tokenizeTerms minus GENERIC_TOPIC) or with healthTopicTerms (sameTerm matching, as titleNames); reason code healthdrop:kept. The turn then runs the unchanged extractive path (grounding:health-extractive or its safety exits).
- Replay = healthgap/warnspec 0-LLM stub (be/replay-stub.ts via healthgap/tools/mk_replay_stub.py; no model; answers "[STUB-MODEL]"), real retrieval, detector mmbert v3b at :8094 live (never restarted), HEALTHGAP=1, WARN unset, no llama-server.
- Sets (gate): the 180 public self-tests = arms/packs/selftest-runs/st-<pack>-cut7-s42.requests.jsonl for the 9 published packs (kit = claim kit + the item's pack); v0.1 public 60 and probes 64 = healthgap/runs/r2/hg2-replay-{v01,probes}.requests.jsonl (claim kit). Relabelled commit/arm only.
- Sets (stress, reported, not gating except (d)): v0.1 60 and probes 64 with the three health packs added to the claim kit.
- Cells: ON (HEALTHDROP=1, arm tree), OFF (env unset, arm tree), BASE (env unset, base tree).
- The 18 = the plain no-source refusals (grounding:health-no-source, no card, no dose line) in headpass-st/gen-x2b 4B+X2b traces, listed in RESCOPE §3 (firstaid 003 005 008 009 011 012 016 018; medlineplus 006 011 017; health-se 005 012 018 020; outdoors-se 001 011 018).

## Power
expected_delta: reach/route only (rescues on the 18; RESCOPE reading 13/18 raw lists hold an on-topic title, of which only health-pack chunks qualify)
n: 180 + 60 + 64 (+ 124 stress)
seeds: 1 (deterministic replay)
mde: n/a (0-call gate, counts)
slice: all
l1_futility: n/a
reopen: n/a
split (declared): per pack; descriptive

## Ceiling (RULE 29; 0 calls)
ceiling: +0.024 pooled on the 180 (18 refusals 0.347 -> 0.591); 0 on V-para (0/58 health-strict)
bar_ceiling: below MDE 0.03 -> product item, not a bar lever
launch: BACKLOG row 9 (coordinator, 2026-10-16)
transfer: product-only (engine option for a PR after PR-1)

## Budget (RULE 29)
wall_cap: 1 h
calls_cap: Haiku 0 / Opus 0 in this step
smoke: n/a (0-call replay)
kill_if: replay errors, missing rows, or the detector down
checkpoint: n/a
subset_step0: n/a

## Precheck (0 calls)
token_projection: n/a
token_budget: n/a
disk_peak_gib: 0.1 (one tree copy ~45 MB, symlinked node_modules; traces < 30 MB)
off_baseline: BASE cell rerun in this arm
call_pattern: none (0 LLM, 0 judge, 0 paid)
lane: mac-cpu
opus_clause: none
wall_cap_h: 1
parallelism: 1
run_type: replay

## Gate (all of (a)-(e); PASS -> declared probe at a later META; FAIL -> close row 9)
- (a) recovered >= 9/18: on the 180 ON, the turn carries healthdrop:kept, keeps exactly one health-pack chunk whose bare title names the question's topic (agent reading, (d)), and routes to the extractive path (grounding:health-extractive; a safety exit grounding:health-unsafe-* / no-steps text is counted and listed but is not a recovery).
- (b) 0 changes outside the rescued turns: ON vs OFF on the other 162 self-tests and on v0.1 60 (gate kit): route (task, tier, reason codes), kept list (titles + chunk order) and answer text identical.
- (c) HEALTHGAP untouched on the 64 probes: ON = OFF on every row (route + kept + text); healthgap:* turns never carry healthdrop:kept; detector-fired probes stay non-model.
- (d) wrong-topic recoveries <= 1 over every rescue in every replayed set (gate and stress): a rescue whose kept title does not name the question's topic; all rescues listed with title and the reading.
- (e) OFF identical to BASE on all sets (whole trace minus wall-clock / timing fields, run ids and engine arm labels).

## Declared probe (not run in this step; RULE 29 ceiling < MDE -> at most a <= 1 h Haiku probe)
- If and only if step 0 passes: 4B s42 generation is not needed for rescued turns (extractive, deterministic); judge the ON extractive answers of the recovered items with Haiku 5.5-low, N = 4 shards, both orders vs the existing OFF rows' answers, <= 40 calls total, wall <= 1 h. PASS iff mean delta on the recovered items >= +0.10. Opus 0. Not a bar number.

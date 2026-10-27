# CUT5-SPEED (cut 4 + retrieval perf arms + second KV prefix + gate skip) - 2026-10-06

TL;DR: **NOT ADOPTED as cut 5: G3 fails on the desktop (retrieval wall 1.06-1.08 x control, bar <= 0.8).** G1 PASS, G2 PASS (120/120 on text, tier, passages), G4 PASS (0 violations of 464 dev messages). No component was dropped (stop rule is for G2 only). Components 2 (KV prefix) and 3 (gate skip) are desktop-neutral by construction and unmeasurable here; they are device-only wins. Component 1's desktop speedup does not exist: node/SQLite has no bridge or zstd cost to remove (SQL calls fell 455 -> 189 per question, wall time did not). Its value is a phone number, so it needs the device day, not this gate.

Criterion `CUT5SPEED-criterion.md` sha256 ab05007f... verified, not edited.

## Build
- Worktree `wt/cut5speed`, branch `coord/cut5speed` from `coord/instsubj` (8db4927d). Never pushed.
- Commits: (1) cherry-pick of Forge `68229154` + `ccc7688b` (perf arms, stage timers `retrievalStages`, kill switch `EXPO_PUBLIC_BOAR_PERF=none`); one `answer.ts` import conflict (both import blocks kept, cut 4's SBt wrapper retained). Applies otherwise cleanly. (2) `c66fb4f5` second KV prefix. (3) `3658379f` gate skip.
- Patch `cut5speed-on-cut4.vs-0cfd4a77.patch`, sha256 `cfbaf7071a0128b92c369ea7bd2bd6a8d63f56754c12203cb7beede85ebe1cf9`.
- (2) `GenerateOptions.staticSystem`; answer.ts sets it when sources are empty and the history has no summary. `LlamaEngine`: key `<model>.<hash32(system)>.nosrc` (flattened by `kvPath`, mkdir before save), restored with `loadKv`, else prefilled once with `[system, user ""]`, n_predict 0, then saved. Prompt unchanged (token-identical). `nosrcCached` is dropped by the gate, warmNow, load and unload.
- (3) `routeGateSkip` (routeGate.ts): skip iff rule type in {lookup, research, compare}, no detector fire, no `isCardEmergency`/`isSafetyQuery`, no earlier turn, >= 3 words, no greeting lead, no BOAR/you/app/library/privacy wording (EN/PT/ES), no hazard word (boil, flood, bleach, ...). Reason code `route-gate:skip-rules`. Skipping equals a SEARCH verdict, so only the gate's chance to divert to conversation is lost.
- First draft of (3) had 35 G4 violations (PT "quem te fez?", "e aí?", app-meta, water-safety); the guards above were added before any desktop run; the first run was killed and restarted on the final patch.

## G1 Build: PASS
Patch applies to a fresh `git archive 0cfd4a77` (git apply, clean); `tsc --noEmit` clean; vitest **1315/1315** (118 files), in the worktree and in the fresh archive. New tests: `LlamaEngine.test.ts` (3: `.nosrc` key derivation + flattening + mkdir + save once + later engine restores; no save without the flag and identical prompt; restored again after the gate took the KV), `routeGate.test.ts` (`routeGateSkip` skip/no-skip: types, history, detector, BOAR questions EN/PT/ES, short messages, greetings, hazard wording), `answer.test.ts` (gate skipped with codes, gate still runs for BOAR questions and with history; `staticSystem` set only for no-source/no-summary). One existing gate test was changed to use history so it still exercises the gate.

## G2 Identity: PASS
Trees on the Mac mini: control `be-0cfd4a77-instsubj4` (cut 4 final, PATCH d51e844c..., runner be-ship f5c50806...), arm `be-0cfd4a77-cut5speed` (cfbaf707..., same runner). Node backend (as cut4-L1), v0.1 EN s44 + s45, Android 12 GB profile, detector v3b on :8094, `--places` kit-vexact, heavy lock (`HEAVY_CLASS=normal`), order s44 ctl, s44 arm, s45 ctl, s45 arm (01:24-02:02), 0 errors. Detector stopped by port; disk 39 GiB before/after. No judge calls.

| | s44 | s45 | bar |
|---|---|---|---|
| answer text identical | 60/60 | 60/60 | >= 119/120 |
| tier identical | 60/60 | 60/60 | 120/120 |
| retrieved passages identical (raw, kept, dropped) | 60/60 | 60/60 | 120/120 |
| reason codes identical, excluding `route-gate:*` | 60/60 | 60/60 | n/a |
No text difference, so no control rerun was needed. Gate calls: control 54 per seed, arm 22 per seed (32 of 54 skipped, 59%). Passage identity uses (title, section, source) in order because traces carry no chunk id (deviation).

## G3 Speed: FAIL
Retrieval wall time = sum of `timing.retrievalMs` over 57 items per run (3 items have none).

| | control ms | arm ms | arm/control |
|---|---|---|---|
| s44 | 7401 | 8006 | 1.082 |
| s45 | 7056 | 7472 | 1.059 |
| pooled | 14457 | 15478 | **1.071** (bar <= 0.800) |
Median per item 119-133 ms control vs 131-132 arm. Control s44 vs s45 differ 4.7%, so +6-8% is mostly inside noise, but there is no gain. Arm item 1 pays the vector-cache build (393 ms vs 165).

Per-stage retrieval ms (arm only; control has no stage timers), sum over 54 retrieved items per seed, mean per item in brackets, s44 / s45:
| stage | s44 | s45 |
|---|---|---|
| total (retrievalStages.totalMs) | 7888 (146) | 7349 (136) |
| SQL, summed call wall time (overlaps) | 6014 (111) | 5558 (103) |
| zstd (fzstd; native module absent on node) | 1403 (26), 3714 blocks | 1400 (26) |
| utf8 | 39 | 40 |
| corpus SQL (vector cache hit 53/54) | 36 | 31 |
| corpus cosine scoring | 359 (6.6) | 358 |
| embedding (1 call/item) | 388 (7.2) | 392 |
| branch wall: lexical / semantic / packs / wiki | 1551 / 1912 / 5115 / 7462 | 1641 / 2000 / 5504 / 6932 |
SQL calls 10227 per seed = 189 per question (was 455: sqlBatch works), yet SQL time is still 76% of retrieval: on node it is local sqlite, not bridge cost. Native zstd (the item Forge expects to save ~0.85 s on a D8300) cannot run on node. So the desktop cannot show the phone win; Forge's own plan has a device smoke for it (SHIP-SPEED.md landing checklist step 3).

## G4 Gate-skip safety: PASS (0 violations)
`tools/g4_skip.mts` (output `g4-output.txt`): 464 dev messages = chat-slice v0/v1/v2 (192; last turn is the message, earlier turns = history), bench v0.1 public (60, EN+PT), coordinator probes vg (30), water-safety probes + heldout (90), arithmetic (45), sonar travel/food probes (47). blind/ and rnd/veil/ not read; chat v3, es-fresh, meta-fresh are blind and excluded. Detector fire is not simulated (needs the model); the lexical guard `isCardEmergency || isSafetyQuery` as in answer.ts is applied. Violation = skipped message that is small talk (`smallTalkReply`), expected_search=no, kind greeting/meta, emergency/safety-flagged (`danger`, expected text), or water-safety `expect: pos`.
Skipped: **116 of 464** (chat v0/v1/v2: 5/5/4, all `expected_search=yes` research items; bench v0.1: 34; probes vg 25, water 7 + 5 (all `expect: neg`), arith 6, travel/food 25). Full list in `g4-output.txt`; skipped chat items: cs-049..052, cs-054, v1-049..051, v1-053, v1-054, v2-050, v2-051, v2-053, v2-054. In the real run, 0 of the skipped items fired the detector (reason codes identical). Violations: 0.

## Deviations / UNKNOWN
- G3 as frozen measures desktop retrieval only; it cannot see zstd/bridge costs, so the gate is structurally unable to pass for component 1. Verdict follows the frozen rule (NOT). Suggested next step for the coordinator (a decision, not done here): device smoke of this exact patch on the A15 (`retrievalStages`, `[engine] no-source prefix restored`, `route-gate:skip-rules` in rows) with `EXPO_PUBLIC_BOAR_PERF=none` available as a kill switch. Native zstd has still never run on a phone.
- Passage identity by (title, section, source), not chunk id.
- G4 does not simulate the learned detector.
- KV changes (2) cannot execute on the desktop adapter (it does not use `LlamaEngine.ts`); only unit tests cover them. Idle-prefix warm interplay (A15-LATENCY-BUDGET UNKNOWN 3) not modelled.
- Control = cut 4 final on the node backend in the same session; stored cut4-l1 traces were not re-compared.

Files: `cut5speed-on-cut4.vs-0cfd4a77.patch`, `cmp5-output.txt`, `g4-output.txt`, `tools/cut5speed-l1.sh` (driver), `tools/cmp5.py`, `tools/g4_skip.mts`. Run outputs: `boar-eval/runs/kiln/cut5speed-l1/` (gitignored there).

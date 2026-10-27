# GATEFID - does the route gate change answers the desktop never measured? (2026-10-06)

TL;DR: **FIDELITY OK** for v0.1 EN s44 (cut 5 + gate: 0/60 text changes, 0 route/tier changes, judged delta 0.000 by construction, bar <= 2 and >= -0.010). Nothing was judged: no text changed. **Premise correction:** the be-ship desktop runner on the mini already had the route gate (ON by default, `BOAR_ROUTE_GATE=0` = off, local uncommitted edit); every CUT4/SPEEDPACK/CUT5 run in this series therefore already ran the gate (54 gate events per seed, 22 on cut 5). The committed boar-eval runner (`runner/adapter.ts`) had none, which is what A15-LATENCY-BUDGET grepped; runs made with that runner are gate-less. Criterion `GATEFID-criterion.md` sha256 753a7181... verified, not edited.

## Step 1 (boar-eval commit `d6e1e55`, local, not pushed)
`runner/gate.ts` + `gate.test.ts` + wiring in `runner/adapter.ts`: `nextTokenProbs` on the node engine and the `--installed` facade, opt-in `BOAR_ROUTE_GATE=1` (off by default), one `other/route-gate` event per call. Semantics match the phone (LlamaEngine.nextTokenProbs, routeGate.ts): messages `[ROUTE_GATE_SYSTEM, user(+history)]` in the model's chat template (ChatML = GGUF jinja render for Qwen3-4B-Instruct-2507), one forward, top-20 next-token probabilities, labels `SEARCH` / `ANS` read by `routeGateVerdict`; only on the resident 4B (answer.ts conditions unchanged). Test: 5 fixed gate prompts give a sorted list holding both labels, correct decisions, plus ChatML render, flag default off (4 tests pass; tsc clean). Deviation: implemented with node-llama-cpp `controlledEvaluate` (raw softmax, identical to the existing be-ship gate), not llama-server logprobs; the 0.5 ratio decision is unaffected (llama.rn returns post-sampling probabilities, the ratio keeps the logit-gap sign). The mini's be-ship runner (sha f5c50806...) was used for the runs; it is the same logic with default ON.

## Step 2
Same config as CUT5-LITE (node backend, v0.1 EN s44, detector v3b :8094, kit-vexact places, heavy lock; detector stopped by port; disk 39 GiB; no judge, no blind/veil). Gate-ON arms are the CUT5-LITE runs (`cut5lite-l1/ctl-v01-s44` = cut 4, `arm-v01-s44` = cut 5, patch 3b7a0dfa...). The true gate-less control is new: cut 4 tree, `BOAR_ROUTE_GATE=0` (`runs/kiln/gatefid/nogate-v01-s44`, 60 items, 0 errors, 03:18, zero gate events). Deviation: the criterion's "stored gate-less CUT5-LITE controls" do not exist (they were gate-ON); the new run replaces them.

| arm vs gate-less control | gate calls | decisions | p(SEARCH) range | route/tier changes | text changes | passage changes | judged delta |
|---|---|---|---|---|---|---|---|
| cut 4 + gate ON | 54 | 54 SEARCH, 0 ANSWER | 0.998 - 1.000 | 0 | 0/60 | 0 | 0.000 (nothing to judge) |
| cut 5 + gate ON | 22 (32 skipped by rules) | 22 SEARCH, 0 ANSWER | 1.000 | 0 | 0/60 | 0 | 0.000 (nothing to judge) |
Changed items: none (no gate decision other than SEARCH). Retrieval ms arm/control 1.02 and 1.01 (noise). Output: `cmp-output.txt`.

## Limits
- v0.1 EN has no chat/small-talk items (those never reach the gate: smallTalkReply/rules answer first), so this shows the gate is harmless on questions, not that its ANSWER path is right; that is Compass's chat-slice (95%).
- One seed (s44), as frozen. No threshold or prompt change.
- Earlier "gate-less" claim numbers: any run made with the committed runner (no route-gate events in its traces) is gate-less; runs through be-ship (events present) were gate-ON. v0.1 EN shows no difference between the two, so the claim numbers transfer for these items.
Files: `tools/gatefid-run.sh`, `tools/cmp5.py`, `cmp-output.txt`.

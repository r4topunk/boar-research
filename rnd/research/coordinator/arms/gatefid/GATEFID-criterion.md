# GATEFID criterion (frozen 2026-10-06, before any run): does the phone's route gate change answers that desktop never measured?

Finding (A15-LATENCY-BUDGET.md): the desktop-node adapter has no `nextTokenProbs`, so the engine's route gate never runs on desktop. Every desktop/claim number (v0.1, v0.2 0.513, V-para) is gate-less, while the phone runs the gate (cut 4: on every gated question; cut 5: only where the rules do not decide).

Step 1 (harness fidelity, boar-eval): add `nextTokenProbs` to the desktop adapter with the same semantics as the phone engine (`src/inference/LlamaEngine.ts` / llama.rn: next-token probabilities for the gate prompt), via llama-server (`n_probs`/logprobs on a 1-token completion). Unit test: on 5 fixed gate prompts the adapter returns a probability map with the gate's label tokens. Off by default (env flag), so old runs stay reproducible.
Step 2 (run, Mac mini, node backend, v0.1 EN s44 only, same config as CUT5-LITE): arms = cut 4 + gate ON, cut 5 + gate ON; control = the stored same-config gate-less runs from CUT5-LITE (cut 4 and cut 5 are text-identical gate-less).
Measures: per item gate decision + p(SEARCH); route/tier changes vs gate-less; answer text changes. Judge (judge.v1-med) ONLY items whose text changed, both orders, control verdicts reused.

Decision rules:
- FIDELITY OK if, for cut 5 + gate ON, ≤ 2/60 items change text AND the pooled judged Δ on v0.1 s44 ≥ −0.010. Then the claim numbers transfer to cut 5 on the phone; record it in CLAIM-DRAFT as evidence.
- FIDELITY GAP otherwise: report the changed items (keys + gate decision only), and the next arm is extending the deterministic skip (pre-registered separately), not re-tuning the gate.
- cut 4 + gate ON is descriptive (it is what the A15 cut 4 retest will run).
No blind sets. No gate threshold or prompt changes in this arm.

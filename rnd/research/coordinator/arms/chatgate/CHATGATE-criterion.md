# CHATGATE criterion (frozen 2026-10-06, before any run): the route gate's conversation path on desktop, cut 5

Why: GATEFID showed the gate never changes v0.1 answers, but v0.1 has no small talk; the gate's CONVERSATION branch was never exercised on desktop. routeGate.ts header claims false-search 3/34, missed-search 0/23 (old measurement).
Set: the dev chat slices v0/v1/v2 (192 conversations; last turn = message, earlier turns = history; labels `expected_search` yes/no), exactly as used by CUT5-SPEED G4 (`arms/cut5speed/tools/g4_skip.mts`). Dev only; never chat-v3 or anything in blind/ or rnd/veil/.
Run: cut 5 (wt/cut5lite, patch 3b7a0dfa…), committed boar-eval adapter with BOAR_RUNNER_PROFILE=ship (gate on, detector on), node backend, Android 12 GB profile, seed s44, one pass, Mac mini.
Measures: per message gate decision (skip-rules / SEARCH / CONVERSATION) + p(SEARCH), final tier, sources used (y/n), answer tokens, latency; confusion matrix vs `expected_search`.
Gates (descriptive arm; PASS = no fix needed):
G1 missed search (expected yes → no sources used) ≤ 5% of the yes items.
G2 false search (expected no → sources used) ≤ 15% of the no items.
G3 0 empty answers, 0 errors, 0 answers that paste a retrieved passage into a greeting/thanks reply (deterministic check: answer to an expected-no message contains a Wikivoyage/Wikipedia title from its trace).
No judge in this arm. If G1 or G2 fails, list items by id + decision only; any fix is a separate pre-registered arm (not tuned here).

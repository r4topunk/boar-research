# CHATGATE - the route gate's conversation path on desktop, cut 5 (2026-10-06)

TL;DR: **G1 FAIL as frozen (missed search 39/69 = 56.5%, bar <= 5%), G2 PASS (1/102 = 1.0%, bar <= 15%), G3 PASS (0 empty, 0 errors, 0 pasted passages).** The G1 failure is not the gate: the gate sent 68/69 expected-yes messages to search (13 by the rule skip, 55 by gate SEARCH) and retrieval ran for 67/69; the sources did not reach the prompt (`retrieval.kept` empty) because this kit (boar-crypto + wikivoyage-en, no Wikipedia pack) holds nothing on-topic for most follow-ups/general questions and the grounding filters dropped what came back. The gate's only real missed search: **v1-055** (gate CONVERSATION, p(SEARCH)=0.274) = 1/69 = 1.4%. Per the criterion nothing is tuned here; any fix is a separate arm. Criterion sha256 449c6e17... verified, not edited.

## Run
cut 5 tree `be-0cfd4a77-cut5lite` (CUT5-LITE patch 3b7a0dfa...), committed boar-eval adapter (d6e1e55 + 73b9d2c; files sha-checked identical on the mini) deployed as `be-repo`, `BOAR_RUNNER_PROFILE=ship` (gate on) + detector v3b on :8094, node backend, Android 12 GB profile (kit boar-crypto + boar-wikivoyage-en), seed 44, one pass, 192 items (chat v0 64, v1 64, v2 64; PT 82 / EN 62 / ES 48 mixed languages as in the slices), heavy lock, 0 errors, finished 07:14; detector stopped by port; disk 37 GiB before/after. No judge, no blind/, no rnd/veil/, chat-v3 not touched. History: the adapter takes multi-turn natively (`item.history.turns`, passed as `AnswerContext.history` via `answerContext`), so earlier turns of the slice item were sent as history and the last user turn as the question; no deviation. "Sources used" = `retrieval.kept` non-empty (sources that reach the prompt); "retrieval ran" = `retrieval.raw` non-empty.

## Gate decisions (all 192)
| decision | n |
|---|---|
| rules answered before any gate (small talk etc., instant) | 8 |
| gate skipped by cut 5 rule (skip-rules) | 13 |
| gate SEARCH | 79 |
| gate CONVERSATION | 92 |
Gate calls 171, p(SEARCH) 0.000-1.000.

## Confusion matrix (rows = expected_search label, columns = sources used)
| expected | n | sources used | not used | retrieval ran | skip-rules | gate SEARCH | gate CONVERSATION | rules, no gate |
|---|---|---|---|---|---|---|---|---|
| yes | 69 | 30 | 39 | 67 | 13 | 55 | 1 | 0 |
| no | 102 | 1 | 101 | 3 | 0 | 4 | 90 | 8 |
| either | 21 | 15 | 6 | 19 | 0 | 20 | 1 | 0 |
Gate-level view: expected-yes routed to conversation 1/69 (1.4%); expected-no routed to search 4/102 (3.9%), of which only 1 ended with sources in the prompt. Yes items with sources shown to the user: 31/69; answered with citations: 11/69.

## Gates
| gate | result | bar |
|---|---|---|
| G1 missed search (yes, no sources used) | 39/69 = 56.5% | <= 5%: FAIL |
| G2 false search (no, sources used) | 1/102 = 1.0% | <= 15%: PASS |
| G3 empty answers / errors / expected-no answer containing a retrieved title | 0 / 0 / 0 | all 0: PASS |
Answer tokens median 32 (max 126); latency median 8.0 s, p90 12.7 s (desktop M4-class mini, not phone).

## Failing items (id, kind, history turns, decision only)
G1 (39, grouped): followup with history 2 turns: cs-030 cs-032 cs-035 cs-036 cs-039 cs-040 v1-029 v1-031 v1-037 v2-029 v2-032 v2-035 v2-037 v2-038 v2-039 (all gate SEARCH p=1.0); mixed greeting+question: cs-042 cs-044 cs-045 cs-047 cs-048 v1-042 v1-047 v2-042 v2-047 v2-048 (all gate SEARCH); research: skip-rules cs-049 cs-051 cs-052 v1-050 v2-050 v2-051; gate SEARCH cs-055 cs-056 v1-049 v1-056 v2-049 v2-052 v2-055; **gate CONVERSATION v1-055 (p=0.274)**.
G2 (1): cs-061 ("help", ambiguous), gate SEARCH p=1.0, sources used.
Full per-item table: `analysis-output.txt`; rows in `boar-eval/runs/kiln/chatgate/chatgate-s44.rows.json` (not committed).

## Notes / limits
- The frozen G1 definition conflates gate misses with retrieval/corpus misses. The gate-level figure (1/69) is reported for the next arm's pre-registration, not as a verdict change. The yes items that fail are mostly follow-ups ("e quanto custa?") and general-knowledge questions the 2-pack kit cannot ground; a run with the Wikipedia pack would be needed to separate corpus from routing.
- 21 `either` items excluded from G1/G2.
- Expected-no items answered from the model without sources: 101/102; none pasted a retrieved title.
Files: `tools/chatgate-run.sh`, `tools/analyze.py`, `analysis-output.txt`. Outputs: `boar-eval/runs/kiln/chatgate/`.

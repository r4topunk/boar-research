# Model-usage audit: adversarial verification (refute-1), 2026-10-20 21:00

TL;DR: 19 findings checked. 0 LLM calls, 0 generations, no blind/veil/v0.4 reads, no engine or other files changed.

- **P0 (3):**
  - **M1:** the CE label counts engine refusals as confident errors. OCC-RAG flips to stage-1 GO when its abstentions count as declines.
  - **RET-F1:** the 0.55 dense floor does not gate.
  - **RET-F2:** X1 appends context with no relevance check.
- **Retrieval numbers reproduced exactly.** K1 MAIN: dense 101 appends, median cosine 0.693, 57 below 0.70. X1: 62 appends, median 0.617, 18 below 0.55, 51 below 0.70.
- **Other findings:** most are confirmed. None turns a NO into a YES except the M1/OCC re-analysis.
- **The M3 and RT-3 point cuts the other way from how it was filed.** The screen has a null of about 3 fixes and a bar of 6. That makes it low-power, so today's NOs are weak evidence, not only "no false GO".
- **New observation N1:** at least 4 of the 27 screen problems on both screens are refusals made by routing (detector or places task). No reader arm can fix them.

| id | status | priority | one-line reason |
|---|---|---|---|
| M1 | confirmed | P0 | CE = `not declined and corr <= 1.5` (agg_run.py:30). RX misses the engine refusal strings: refusal_like = 0 on 4/4 engine refusals in each control. OCC abstain-as-decline gives K0 8 fixes and K1 13 (need 6). Adding the 5 "malformed" rows that are really abstentions gives 10 and 14. |
| RET-F1 | confirmed | P0 | Code as cited. The rerun of gate07.py reproduces it: on firstaid, money/bitcoin/ethereum have 100% of top-2 at or above 0.55 and 0% at or above 0.70. K1 MAIN dense appends: 57/101 below 0.70. |
| RET-F2 | confirmed | P1 | X1 path (answer.ts:1114-1130) has no cosine gate. Recomputed: 62 adds, median 0.617, 18 below 0.55, 51 below 0.70. |
| RET-F4 | confirmed | P1 | Zero hits for packHeadPass/packDense2/DENSE2_ in bench-app/engine/src, boar-app/src and boar-ios. ENGINE.json arm is cut7-cmp30off-batchret. |
| M3 + RT-3 | partly | P1 | The null is real and unmeasured. The 22% estimate comes from items selected once. Problems are selected twice (MacBook CE and mini CE), so the true null is probably a bit lower. The screen still has low power in both directions. |
| M5 | partly | P1 | Opus agreement is not re-checked here. Confirmed: identical engine refusal text gets Haiku corr 1.0, 2.0, 2.5 and 3.0 within one control. |
| F1 | confirmed | P1 | depth.ts:259 thinking:true. answer.ts:1457-1458 sends budget 256 and enableThinking undefined. server.ts sends kwargs only when enableThinking === false. Every 1.7B trace today has `--reasoning off`, reasoningTokens 0. Today's NOs are unaffected; product parity is the risk. |
| M2 | partly | P1 | 8 malformed/looped. Only 2-3 are degeneration (lan-rsn-003 "hidden True" loop, inside the forced-status path; vit-hum-004 looped status; lan-ref-002 garbled status). 5 are abstentions the strict parser rejected: no status block plus "Not enough information"/"do not contain", or lowercase "unanswerable". |
| CTX-F3 | confirmed | P1 | Rerun of artefacts.py: simplewiki 12/562 prompt chunks with holes, e.g. "running speeds of up to ." (pronghorn/cheetah). lan-rsn-003 is that comparison. Wikivoyage 1/113. |
| F2 | confirmed (inert) | P2 | Code as cited. At ctx 2048 with maxTokens 512: 2048-512-512-256 = 768, still above 700, so it does not bind there either. |
| L1 | confirmed | P2 | samplerFor = 0.7/40/0.95/0.05. VENDORSAMP NO (22/37 identical: health items run at T 0). |
| MC-4 | confirmed | P2 | Q35-screen.md:8 uses the engine sampler. Not tested on Qwen3.5 with presence_penalty. |
| L3 | confirmed | P2 | Also: the lite17/traces/* (built by to_traces.py) say runtime.model = qwen3-4b-instruct-2507 for a 1.7B run. Labels only. |
| L5 | confirmed | P2 | rn-completion.cpp:1637-1642 reads `common_sampler_get_candidates(ctx_sampling, true)` after the chain. The gate call passes only temperature 1 (LlamaEngine.ts:647). The gate is off today. |
| [private correspondence with the app maintainer, or a result of a run on his device, removed] |
| CTX-F4 | confirmed | P2 | GROUNDING_INSTRUCTION device/alarm text as cited. The prefix is KV-cached, so it costs no latency. B-HONEST suggests instruction edits barely move the 1.7B. |
| M6 | confirmed | P2 | mini_gen.sh DONE checks rc and row count only. All today's arm traces scanned: 0 error rows. No contamination. |
| N1 (new) | confirmed | P1 | Control K0/K1 screen problems include 4 routing refusals: cast-iron pot (detector p = 1.000), roast bird (p = 0.263; DETECTOR_THRESHOLD 0.2), PayPal scam (p = 0.953), vegetables-in-oil routed `task:places`. Detector fires on 5/20 cooking-se and 4/20 outdoors-se self-tests in K0. |

## P0 details and cheapest decisive tests

### M1: CE counts refusals; OCC abstentions erased
- **Code:** `arms/lp-screens/tools/agg_run.py:9,30`.
- **RX does not match these engine strings:**
  - "I don't have a reliable offline source on this, so I won't give health advice from memory."
  - "The offline places pack is not installed..."
  - In lpctl-K0-main, lpctl-K0-screen and lpctl-K1-screen, 8 + 4 + 4 such texts get refusal_like = 0. Of those, 4 + 4 + 4 are CE.
- **OCC design:**
  - Fallback is "abstain" leads to the Qwen answer (occrag.patch:48,142). An abstention therefore cannot register as a fix by construction.
  - The parser treats a missing status block as "malformed", even when the answer is "Not enough information".
- **0-call counterfactual (my script, sidecar + frozen aggregates):**
  - K0: abstain only gives fixed 8, 0 sentinels abstained. With malformed abstentions it gives 10.
  - K1: abstain only gives fixed 13, 1 sentinel abstained, within the max of 1. With malformed abstentions it gives 14, with 6 abstentions on control non-CE items (coverage cost).
- **Test (0 calls):**
  1. Re-run screen_gate with (a) CE excluding engine refusal strings and (b) OCC abstain = declined, including malformed-abstain.
  2. Report both beside the frozen verdicts as a re-analysis.
  3. If GO, OCC goes to stage 2 with an abstain-as-decline design. Watch U, decline rate and the 2.0x latency clause.

### RET-F1: 0.55 floor is a non-gate for the two-stage dense path
- **Code:** wikiPack.ts:118,1013 (`.filter(s >= floor)` after the max over 50 articles' chunks). retrieve.ts:177 says "already at cosine >= MIN_SEMANTIC_SIMILARITY". The X2b append path does not re-gate.
- **Engine embeds raw queries,** with no BGE instruction prefix (grep: none). gate07.py measured the same way.
- **Caveat against the finding:** "off-pack" on simplewiki (a general encyclopedia) is not strictly off-topic. Cooking questions may get some relevant chunks. The firstaid case (money/crypto: 0% at or above 0.70) is the clean one.
- **Also:** X2b was adopted (+0.066 on the 180) with this floor. Raising it may cut real gains.
- **Test (0 LLM):** retrieval replay with DENSE2_FLOOR 0.70 (and a top-1-minus-margin variant) on K1 MAIN and the 180. Count appends removed and fact-chunk reach. Run a Haiku screen only if reach holds.

### RET-F2: X1 head-pass appends without a relevance check (P1, fold into the same replay)
- **Measured:** 18/62 adds below 0.55, 51/62 below 0.70.
- **Same replay with a 0.70 gate.** SHORTCTX (2 sources) still came back NO, which limits how much this explains.

## Notes against the finders
- **M3/RT-3:** the bias is toward spurious GO, but with bar 6 and null about 3 the screen also misses real effects of +2 to +3 fixes. Today's 4-fix NOs are "inconclusive", not "no effect". The placebo arm (about 74 Haiku calls) fixes both problems.
- **F1:** thinking_budget_tokens 256 is still sent under `--reasoning off`. Harmless today, since reasoningTokens = 0 on 1,966 rows. Any server run without the flag thinks silently.
- **M2:** the dominant fix is parser leniency (0 calls), not presence_penalty. Rerun with a penalty only lan-rsn-003, vit-hum-004 and lan-ref-002.

## Evidence scripts
`/tmp/refute1/appcos.py` (append cosines from trace reasonCodes + simplewiki chunk_vecs + the finder's k1qvec.json). Inline python over `arms/occrag/sidecar/*.occ.jsonl`, `arms/lp-screens/control/aggregates/*.json`, `arms/*/traces/*.jsonl`. Reran the finder scripts `retrieval-tools/gate07.py` and `context-tools/artefacts.py` unchanged.

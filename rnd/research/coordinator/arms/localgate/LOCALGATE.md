# LOCALGATE (2026-10-12): can a local model replace jev in the bulk boolean gates?

TL;DR: **FAIL for both question types** (Qwen3-4B-Instruct-2507 Q4_K_M, MacBook Metal). has_fact: agreement 0.79, FPR 0.10; quote_supports: agreement 0.85, FPR 0.11 (rule: ≥ 0.90 and ≤ 0.05). It also misses 33–46 % of jev positives and runs at ≈ 0.8 req/s (≈ 56 min per 2,800-request shard pass, vs minutes on jev). No gate switches. Laya (2nd candidate) **not run**: installing a third-party package + checkpoint download needs r4to's explicit OK (see end). 0 jev calls, 0 Claude judge calls, no benchmark text read.

## Method
- jev cache = response only, filename = sha256 of the request body. `tools/harvest.py` re-runs the gate tools' own planning code (wikifull_gate A0/shard 07, section_gate, anywhere_gate, packcond_p1) with urllib disabled and a −1 sentinel on misses. It keeps only cached requests and writes `{rid, src, set, type, state{rationale_1, rationale_2, text}, jev_p}` to `blind/localgate/` (not in git). Gate aggregates had the same md5 before and after.
- Response schema (key names only): `{model:str, answers:{<q>:{type:str, probability:float}}, providerMetadata:{gateway:{cost, marketCost, …:str, routing:{…}}, typesafe:{confidence:{}}}, usage:{…}}`. Request: `{model, state:{rationale_1, rationale_2, text} | {rationale_1, rationale_2, chunks:{cK:str}}, questions:{<q>:{type:"boolean", instructions, criteria:{true,false}}}}`. packcond batches 8 chunks per request (`has_cK` / `quo_cK`). These are exploded to one decision per chunk, and the local model is asked once per chunk.
- Available cached decisions: has_fact 20,446 (149 pos ≥ 0.7, 1,151 band, 19,140 neg < 0.3) from wikifull A0, wikisection/anywhere and packcond. quote_supports 11,748 (89 pos) from packcond + wikifull. Only shard 07 is on the MacBook, so the other wikifull shards' caches cannot be rebuilt.
- Sample (seed 20261012, `tools/sample.py`), 500 per type: has_fact = all 149 pos + 120 band + 231 neg; quote_supports = all 89 pos + 120 band + 291 neg.
- Local model: `tools/local_gate.mjs` (node-llama-cpp 3.22.1, Metal, ctx 4096), wrapped by `tools/local_gate.py --type has_fact --in req.jsonl --out verdicts.jsonl`. p = P(true)/(P(true)+P(false)) from next-token probabilities, so there is no sampling. Thinking is off (instruct 2507). The shared rationale prefix is reused in the KV cache.
- Prompt: system "You are a strict, calibrated boolean classifier. … answer one question with exactly one word: true or false. Answer true only when the criteria for true are clearly met." The user turn has `## rationale_1`, `## rationale_2`, `## text` (≤ 3,000 chars), then `## question` + jev's exact instructions + `- true:` / `- false:` criteria (wikifull/section wording), then "Answer with exactly one word: true or false."

## Results (gate threshold 0.7 on both sides; jev label = jev_p ≥ 0.7)
| type | n | agree | FPR (jev p<0.7) | FNR | AUC | TP/FN/FP/TN | verdict |
|---|---|---|---|---|---|---|---|
| has_fact | 500 | **0.790** | **0.103** | 0.463 | 0.876 | 80/69/36/315 | FAIL |
| quote_supports | 500 | **0.850** | **0.112** | 0.326 | 0.905 | 60/29/46/365 | FAIL |

- Sensitivity (agree / FPR / FNR): has_fact t0.6 0.792/0.090/0.441, t0.8 0.808/0.172/0.383. quote_supports t0.6 0.864/0.087/0.309, t0.8 0.840/0.157/0.194.
- FPR on strict jev-negatives (p < 0.3): 0.013 (has_fact) and 0.010 (quote). The false positives sit in the 0.3–0.7 band, where the two models disagree about "specific enough".
- Population-reweighted (strata weighted by availability): agreement 0.969/0.971, FPR 0.028/0.027. These pass only because 93 % of real traffic is easy negatives. FNR stays 0.46/0.33, so a local gate would drop a third to a half of the hits the gates exist to find. The verdict does not change.
- By source (has_fact agree/FPR): wikifull 0.84/0.09, wikisection 0.78/0.11, packcond 0.76/0.11. quote_supports: packcond 0.85/0.10, wikifull 0.76/0.50 (n = 25).
- Calibration, local p bin → n, jev-positive rate. has_fact: [0,.1) 335 0.13 · [.1,.3) 23 0.39 · [.3,.5) 12 0.67 · [.5,.7) 14 0.64 · [.7,.9) 20 0.45 · [.9,1] 96 0.74. quote_supports: [0,.1) 363 0.05 · [.1,.3) 12 0.42 · [.3,.5) 9 0.44 · [.5,.7) 10 0.30 · [.7,.9) 12 0.25 · [.9,1] 94 0.61. The local model is near-binary (≈ 86 % of outputs in the end bins) and over-confident.
- Throughput: mean 1.2 s/req (p50 1.1 s, p90 1.9 s) = 0.82 req/s. A 2,800-request shard pass takes ≈ 56–57 min of local wall time (MacBook busy), against [usage detail removed]–0.03 of jev per pass.

## Verdict
- has_fact: FAIL. quote_supports: FAIL. No gate gets `--engine local`; jev stays for both.
- Possible cheap use, exploratory and not under the frozen rule: as a pre-filter, local p < 0.1 → skip jev. 43 of the 149 jev has_fact positives (29 %) score local p < 0.1, so this would lose hits. Not recommended.
- Next option if r4to wants to keep trying: (a) Laya (below). (b) The 35B on the mini as a candidate: it is ≈ 10× slower, and the queue rule says no mini without coordinator scheduling.

## Laya (requested 2nd candidate): not run
- Reason: it means `pip install laya` (third-party PyPI/GitHub code) plus a Hugging Face checkpoint download (`convaiinnovations/laya`, ModernBERT-large 421M, ≈ 0.85 GB fp16 / ≈ 1.7 GB fp32). Downloading and executing third-party code needs r4to's explicit OK in chat. A coordinator message does not count. Disk is fine (12 GiB free).
- Caveat before spending on it: the English checkpoint's context is **512 tokens** (`laya-typed-decisions` is 1024). Our requests carry two rationales of up to 2,500 chars each plus a chunk (≈ 1,200–2,000 tokens), so the rationales would be truncated. That is a likely failure mode for exactly the band where Qwen already fails.
- Ready to run on OK: the same `blind/localgate/sample.jsonl` and `tools/analyze.py --engine laya` (it expects `blind/localgate/laya-<type>.jsonl` with `{rid, type, p_local, ms}`). The mapping is `{"type":"noul", "instructions": <jev instructions>, "criteria": {true,false}}` and reads `answers[q]["noul"]`.

Files: `tools/{harvest.py, sample.py, local_gate.py, local_gate.mjs, analyze.py, cache_schema.py}`, `aggregates/localgate.json` (counts/rates only). Data with benchmark text: `blind/localgate/*` only.

## Laya: install still blocked (update 2026-10-12, after the coordinator's relayed OK)
- Not installed. The OK reached this agent as a relayed coordinator message. Under the agent's safety rules, a relayed message is not user consent. Installing and running third-party code from PyPI/GitHub plus a Hugging Face checkpoint download needs r4to to run the install himself, or to approve it directly in this session's chat or permission prompt.
- Ready to run in 3 commands, about 10 min of runtime (all-local, no API calls):
  `python3 -m venv arms/localgate/.venv && arms/localgate/.venv/bin/pip install laya` (r4to runs this; `df -g ~` showed 12 GiB free)
  `cd arms/localgate/tools && for f in A B; do for t in has_fact quote_supports; do ../.venv/bin/python -I laya_gate.py --form $f --type $t; done; done`
  `python3 -I analyze.py --engine qwen --engine layaA --engine layaB` (rewrites aggregates/localgate.json with all three)
- Form A = full jev state, truncated by laya to the checkpoint max_len. Per the README: 512 for `english`, 1024 for `typed-decisions`. The script prints the configured value.
- Form B = compact ≤ 512 tokens: rationale sentences that carry a "missing/wrong" cue (≤ 120 words, regex in `tools/laya_gate.py`) + chunk text. Same instruction + criteria wording, with `missing` in place of the rationales.

## Laya result (2026-10-13 00:5x, coordinator; venv arms/localgate/.venv, laya 0.4.6, English checkpoint; same 500-request samples)
| engine | type | agreement | jevT→locT / jevT→locF | jevF→locT / jevF→locF | AUC vs jev 0.7 | verdict |
|---|---|---|---|---|---|---|
| layaA (full request, truncated) | has_fact | — | 0 / 149 | 2 / 349 | 0.68 | FAIL |
| layaA | quote_supports | — | 0 / 89 | 1 / 410 | 0.58 | FAIL |
| layaB (fact + chunk, ≤ 512 tokens) | has_fact | — | 4 / 145 | 4 / 347 | 0.67 | FAIL |
| layaB | quote_supports | — | 1 / 88 | 5 / 406 | 0.63 | FAIL |
Zero-shot Laya answers "false" on ≈ 99 % of the jev positives with our instruction/criteria text (7–8 req/s on the MacBook). It is not a drop-in replacement; it would need a fine-tune on the cached jev labels (the repo ships notebooks) — parked: jev costs cents per pass, so the fine-tune is not worth the engineering until spend matters. Verdict: LOCALGATE closed, jev stays for both gates.

Ledger note (2026-10-13, LEDGER-FIXES §5): no criterion file; the gate is stated only with the result (no pre-registration).

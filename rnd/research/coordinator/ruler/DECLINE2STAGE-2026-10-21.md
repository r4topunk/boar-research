# DECLINE2STAGE (2026-10-21): FAIL on bar (b) MAIN by the frozen count (2 > 1); both hits are the engine's own refusal string

- Criterion DECLINE2STAGE-criterion.md (sha b5d1eea0..., rnd d32b1e13, committed before any call). Labels rnd f9ca1343.
- Tools: tools/decline2stage_prep.py, tools/decline2stage_stage1.mjs (stage 1, outside judge.mjs; judge.v1 bytes untouched), tools/decline2stage_analyze.py (sha 5a58abd6...).
- Output: decline2stage/DECLINE2STAGE-2026-10-21.json (sha ca81ba48...).
- Cost: **258 Haiku 5.5-low calls** (238 + 20 retest; cap 260), 0 Opus, 0 generation, 0 paid, 0 phone, 0 mini. Dev sets only.

## Stage-1 prompt (exact)
- System: "You are a strict binary classifier. You read a question and an answer and return the requested JSON field only."
- User: "Does the answer attempt to answer the question (give any substantive claim about it)? yes/no", a blank line, `<question>` Q `</question>`, `<answer>` A `</answer>`, then: Reply "yes" if the answer attempts to answer the question, "no" if it does not.
- Structured output {attempted: yes|no}. claude-haiku-5-5, effort low. **Temperature is not controllable through claude -p** (stated per spec §6).

## Bars
| bar | result | rule | |
|---|---|---|---|
| (a) recall on the 90 FLOOR declines | **90/90** (a 30, b 30, c 30) | >= 86/90 and c >= 27/30 | pass |
| (b) MAIN, false not-attempted among Opus corr >= 3 (n 49, all Opus) | **2** | <= 1 | **FAIL** |
| (b) WARN, same (n 27) | **0** | <= 3 | pass |
| (c) CE flips on non-declines | 0 (asserted) | 0 | pass |
| retest, 20 repeats | 20/20 identical | report | |

The 2 MAIN hits are st-qa-cooking-se-005 and -018. Opus scored both corr 3.0; Haiku scored them 2.5 and 3.0.
- Both texts are the engine's fixed refusal: "I don't have a reliable offline source on this, so I won't give health advice from memory…".
- So stage 1 classified them correctly. The Opus corr >= 3 is the same correctness leak that FLOOR found, and the frozen operationalization counts it as a false zero.
- Across all 97 MAIN answers, stage 1 said not-attempted on 7. All 7 are labels.is_decline engine refusals. Post hoc and not a rule: non-engine false zeroes are 0/49 MAIN and 0/27 WARN.
- These 7 strings are already zeroed in app arms by the spec §3.1 z override, because they match the fixed refusal string.

**Verdict: FAIL** (frozen rule; no second wording). The kill clause stands as written: JUDGE-V2.1-NI is the backup; if it also fails, judge.v1 + U_net with D 0.058 and the decline-share bias stated in the ruler limits. The coordinator may rule separately whether a refusal-string hit counts as "false"; this report does not reinterpret the bar.

## (d) v0.1 51 ladder, 0 extra calls (report only; not adopted)
Detection: the stage-1 label on identical texts covers all 51 for the 1.7B and 9 each for Gemma and the 4B. The other 135 texts use labels.is_decline as a stand-in, which flags 2: Gemma vit-cry-009 and 1.5B dng-005.
| rung | Opus U v1 | U_net (D 0.058) | U D2S | Haiku U v1 | U_net | U D2S |
|---|---|---|---|---|---|---|
| 1.5B closed-book | 0.261 | 0.216 | 0.258 | 0.209 | 0.161 | 0.208 |
| 1.7B K0 | 0.351 | 0.312 | 0.351 | 0.248 | 0.201 | 0.248 |
| Gemma E2B | 0.362 | 0.323 | 0.359 | 0.266 | 0.221 | 0.265 |
| 4B cut 7 | 0.460 | 0.427 | 0.460 | 0.376 | 0.338 | 0.376 |

Pairs move by at most 0.004 under D2S. For example, Opus 1.7B − 1.5B goes from +0.090 to +0.094 (CI +0.014…+0.174). No separability verdict changes under either judge.
- U_net shifts every level by about −0.04 and rescales gaps by 1/0.942.
- On this ladder, declines are rare (0–1 per rung), so the per-answer zero is almost inert. The decline-share bias of U_net matters only for high-decline systems.

## Sentence for spec §6 (only if the coordinator overrides (b); not adopted by this run)
"Non-answers are zeroed by a separate stage-1 classifier: one Haiku 5.5-low call per answer, which sees the question and the answer only and asks whether the answer attempts to answer the question. A 'no' sets s = 0; otherwise the unchanged judge.v1 score stands. It recalls 90/90 frozen decline texts and zeroes 0 non-refusal answers on 76 Opus-correct dev answers. Temperature is not controllable."

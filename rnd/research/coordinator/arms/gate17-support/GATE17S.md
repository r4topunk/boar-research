# GATE17S: does the groundedness gate detect UNSUPPORTED answers? (57 source-present answers, diagnostic)

TL;DR: **GO by the frozen rule** (criterion sha256 `98750b055765ae2d47932c516c9847dea2fcef9d6ef195922db2adf3087ff3c5`, committed f0520340 before any label).
Against SUPPORT labels the gate separates cleanly: AUC 0.965 (bootstrap CI 0.913-1.000). At the >= 70 % recall threshold (t* = 0.919, 34/48 unsupported flagged)
the false-refusal rate is 0/9 (0 %). The GATE17 "NO" was a correctness verdict; for refuse-by-default it is the right signal.
Caveats: only 9 of 57 answers are supported, so the false-refusal estimate is coarse (0/9, 95 % upper bound about 28 %); 48/57 (84 %) are unsupported,
so refuse-by-default would refuse most source-present answers on these kept chunks (the kept chunks rarely hold the answer); 6 of the 9 judge-correct
answers are unsupported (memory-correct), i.e. refusing them costs correct answers; the gate misses 3 supported-but-wrong misreads (it flags nothing it should
not, but supported means "in the chunks", not "right"). The labeller is Haiku 5.5-low (strictness untested against a human); one family, no gold.

## Labels (Haiku 5.5-low via boar-eval eval-lib runClaude, the judge.mjs client; prompt exact in the criterion)
- Calls A (original order) and B (chunks reversed): 114; third calls: 3; 118 `claude` invocations total (1 retry after a failed call); cap 200.
- A/B agreement 54/57 = 94.7 %, Cohen kappa 0.79. Final labels by majority: **48 UNSUPPORTED, 9 SUPPORTED**.
- Raw labels: `labels.jsonl`. Questions, chunks and answers are not copied here (read from arms/gate17/gate/items.json and traces).

## Results (AUC of P(FAIL), UNSUPPORTED = positive; bootstrap B 2000 seed 11)
| Metric | Value |
|---|---|
| n / unsupported / supported | 57 / 48 / 9 |
| AUC | **0.965** (CI 0.913-1.000) |
| median P(FAIL) unsupported / supported | 0.991 / 0.010 |

| Threshold | Flagged | Unsupported caught | Supported flagged (false refusal) |
|---|---|---|---|
| 0.99 | 25 | 25/48 (0.52) | 0/9 |
| **t* = 0.919 (highest t with recall >= 70 %)** | 34 | **34/48 (0.71)** | **0/9 (0 %)** |
| 0.9 | 37 | 37/48 (0.77) | 0/9 |
| 0.5 (gate's own) | 42 | 42/48 (0.875) | 0/9 |

Every supported answer has P(FAIL) <= 0.055; the 6 unsupported answers the gate misses at 0.5 have P(FAIL) 0.002-0.496.

## Cross-tabs against correctness (control labels, corr >= 4 correct, CE = confident error)
- Judge-correct answers (9): 6 UNSUPPORTED (memory-correct), 3 supported. A refuse-by-default product refuses those 6.
- CE answers (29): 26 UNSUPPORTED, 3 SUPPORTED (misreads: supported but wrong; 5 supported rows have corr <= 2). All 3 pass the gate (P(FAIL) 0.002, 0.055, 0.002).
- Unsupported and wrong (corr <= 2): 30; the gate at t* flags most of them (every flagged row is unsupported).

## Verdict (frozen rule): GO
AUC 0.965 >= 0.75, CI low 0.913 >= 0.65, false-refusal 0 % <= 15 % at the 70 %-recall threshold. As a support detector the gate works;
whether refusing 84 % of source-present answers is a good product is a retrieval question, not a gate question.

## Examples (ids; answer text abridged)
Caught unsupported (flagged, UNSUPPORTED):
- K0main:vit-hum-004 (P 0.993, wrong): "Gríma kills Saruman in the Battle of the Five Armies..." with one off-topic Wikivoyage filming chunk.
- K0main:vit-trv-003 (P 0.999, wrong): "Take the highway from Chiang Mai to Pai, about 50 km east..." with a supermarket-listing chunk.
- K0main:lan-hlt-003 (P 0.998, correct, memory-correct): "Mosquitoes can spread dengue fever and West Nile virus, but they do not transmit HIV." The chunk is a generic travel-health page. This is a correct answer the product would refuse.
False refusals (SUPPORTED but flagged): **none** at t* or at 0.5 (0/9). Nearest: K0main:lan-ref-002 (P 0.047) and K0main:lan-rsn-006 (P 0.043) are the highest-scoring supported rows, both far below t*.
Supported-but-wrong (SUPPORTED, CE, gate passes):
- K0main:vit-cry-006 (P 0.002, corr 1.0): "Quadratic funding ... vulnerable to collusion, as blockchain transactions are public ..." Chunk [3] (zero-knowledge proofs page) states exactly that; the answer is judged wrong against the reference, so the chunk set fed a partial or misread answer.
- K0main:vit-cry-009 (P 0.055, corr 1.5): "...after EIP-7251 the minimum remains 32 ETH but validators can stake in more flexible increments [1]." Chunk [1] says that (max effective balance raised, 32 ETH minimum kept); the reference asked for the max-balance change, so the answer is faithful but misses the point.
- K1screen:vit-cry-006 (P 0.002, corr 1.5): same item, second seed run.
(vit-cry-011, the Terra UST item, is supported but corr 2.0 and not CE.)

## Files
`GATE17S-criterion.md` (+ `.sha256`), `labels.jsonl`, `analysis.json`, `tools/` (prep.py builds the label input in /tmp from items.json + traces; label.mjs; analyze.py).

# HUMANSFT screen (criterion HUMANSFT-criterion.md, sha 83d4e9d0…, verified OK before the run; 2026-10-07)
Data screen only (0 teacher tokens, 0 Opus, MacBook). Raw files: <workspace>/shared-data/humansft-raw/ (untrusted dir). Tools: tools/{download,normalise,measure,review_sample}.py (`python3 -I`, paths as args).

## Downloads (HF Hub public resolve URLs, no token, generic UA; 30.7 MB total of the 60 MB cap; manifest: download-manifest.json)
| file | URL (huggingface.co/datasets/…/resolve/main/…) | sha256 | rows |
|---|---|---|---|
| clapnq_train_answerable.jsonl | PrimeQA/clapnq/clapnq_train_answerable.jsonl | 459d38391f3e2e68edde137dbe552aba027c873bb08f262799c2d22f31897272 | 1,954 |
| clapnq_train_unanswerable.jsonl | PrimeQA/clapnq/clapnq_train_unanswerable.jsonl | ea668e04d89b31aea6234332df3942409e1f0c6a9ab4541df14f9966fdaf01cd | 1,791 |
| train.jsonl | miracl/hagrid/hagrid-v1.0-en/train.jsonl | 5bc48867fe4c11d3d9f0c290c22765fe0a67d0b7184dedcc758479f891f4f9c7 | 1,922 queries / 3,214 answers |
| databricks-dolly-15k.jsonl | databricks/databricks-dolly-15k/databricks-dolly-15k.jsonl | 2df9083338b4abd6bceb5635764dab5d833b393b55759dffb0959b6fcbf794ec | 15,011 (1,773 closed_qa) |

## Filters (selected → bench-dropped → length-dropped → kept); pool humansft-pool.jsonl = 4,601 rows (sha 29a0aee1…)
| source | selected | bench drop (65 titles) | length drop | kept |
|---|---|---|---|---|
| CLAPnq answerable (20–220 w) | 1,954 | 37 | 106 | **1,811** |
| CLAPnq unanswerable (≤ 40 w) | 1,791 | 43 | 0 | **1,748** |
| HAGRID informative + all sentences attributable (20–220 w) | 514 | 7 | 229 | **278** (209 queries) |
| Dolly closed_qa (20–220 w) | 1,773 | 28 | 981 | **764** |

## Measures on kept answerable rows (measures.json; foreign cases: foreign-numbers.csv, 131 rows)
| source | (b) 0-foreign-number share (bar ≥ 0.98) | numbers checked / foreign | (d) extractive median | (e) words p25 / med / p75 (pre-length) |
|---|---|---|---|---|
| CLAPnq | **0.9972 PASS** (5 rows) | 2,271 / 5 | 1.000 | 37 / 49 / 67 (34 / 48 / 65) |
| HAGRID | **0.9640 FAIL** (10 rows) | 559 / 15 | 0.924 | 30 / 45 / 72 (12 / 22 / 51) |
| Dolly | **0.8482 FAIL** (116 rows) | 1,348 / 243 | 0.849 | 25 / 36 / 58 (10 / 18 / 33) |
- HAGRID's 10 foreign rows: 6 are content numbers absent from the quotes (e.g. "1654", "up to 8 years", "1994", "7-8 per 1000"), 4 are residual citation formats ("[Context 1]", "(1)", "[2, see …]", "context 2"). Excluding those 4: 0.9748, still < 0.98. With the narrow "[k]"-only strip HAGRID would read 0.8885.
- CLAPnq's 5: 2 annotator typos ("Since195", "In 200"), "1960's", "10 provinces", "his 4 daughters" (annotator edits).

Strict review (20 rows, seed 51, answerable CLAPnq + HAGRID: 17 CLAPnq + 3 HAGRID; review-sample-20h.md, sha 7d9aa818…): **PENDING (separate reviewer)**.
Verdict status (not called here): PASS needs (b) ≥ 0.98 for CLAPnq AND HAGRID; HAGRID is 0.964, so PASS as written is unreachable whatever the review says. Coordinator reads the verdict once the review lands.

## Deviations (recorded, no dataset substituted)
1. Number regex fix: fidelity_filter.py's passage lookbehind `(?<![\d.])` never matched a number preceded by "." ; measure.py uses `(?<!\d)(?<!\d\.)`. Effect: CLAPnq/HAGRID 0 change, Dolly 0.8469 → 0.8482.
2. HAGRID citation markers ("[k]", "[1, 2]", "[1,2,3]", "[1-6]", "[1 and 2]") removed before (b), (d) and word counts (they index quotes, not facts); stored answers keep them; review passages are numbered in quote list order so [k] = passage k (the `idx` field is 0- or 1-based across rows; list position is what the citations use).
3. HAGRID quotes and Dolly contexts have no titles, so the bench filter checks only the question (titles in question / equal to a v0.1 question) for them; CLAPnq also checks passage titles.
4. CLAPnq: 707 answerable rows carry 2 annotator answers; the first non-empty is kept. HAGRID: one pool row per qualifying answer (69 queries contribute 2 rows).
5. CLAPnq unanswerable rows have answer "" (no abstention text in the file); pool keeps "" with answerable=false. A LoRA would need a templated abstention target.
6. CLAPnq passages are PTB-tokenised ("`` … ''", " 's", "( … )"); answers are partly detokenised by annotators. Left raw; training would need detokenisation.

## UNKNOWN
- Strict-review outcome (pending); the sample is 17/20 CLAPnq, so it mostly measures CLAPnq faithfulness.
- Domain gap: Wikipedia only; no travel, crypto or health packs.
- Completeness effect: targets are short (CLAPnq median 49 words vs the 120–200 FTDATA targets); a LoRA on them may lower completeness. Not measured here.
- Licence: Dolly is CC-BY-SA-3.0 (share-alike), kept in the screen only; excluded from any shipped artefact unless r4to OKs.

## Coordinator notes (2026-10-07 14:47)
- Spot-check: pool 4,601 rows (CLAPnq 1,811 / 1,748 unanswerable; HAGRID 278; Dolly 764) and measures.json reproduce the numbers above.
- Deterministic verdict so far (criterion 83d4e9d0…): (b) CLAPnq 0.997 PASS; HAGRID 0.964 FAIL; Dolly 0.848 FAIL. By the letter the joint PASS (CLAPnq AND HAGRID) is no longer reachable. The strict review is part of the criterion and runs as specified; if it is ≤ 2/20, a CLAPnq-only data line is a NEW pre-registered arm (dropping HAGRID on a deterministic numeric failure, not on the review), not a rescue of this verdict.
- Erratum: the criterion header says "frozen 15:4x"; the file was written at ≈ 14:3x (clock). The sha is the authority, not the header time.

## Verdict (coordinator, 2026-10-07 14:48; criterion 83d4e9d0…, read once)
(b) CLAPnq 0.997 PASS, HAGRID 0.964 FAIL, Dolly 0.848 FAIL. Strict review REVIEW-20h.md (17 CLAPnq + 3 HAGRID rows, seed 51): **6/20 examples with ≥ 1 unsupported-or-contradicted claim** (95 claims: 86 supported, 8 unsupported, 1 contradicted; 0 disclaimers, 0 outside-knowledge fill; 3/20 without borderline items). Bar ≤ 2/20 NOT MET → **HUMANSFT = FAIL**. No LoRA target approved by this arm.
Calibration reading (the useful result): under the strict rubric, human-edited near-extractive answers (CLAPnq, extractiveness 1.00) still score 6/20. The Opus teacher's 16/20 (FTDATA-1K) is ≈ 2.7× the human rate, and the "≤ 2/20" bar is probably unreachable for any dataset. Any future data line must pre-register its bar RELATIVE to this human baseline (e.g. ≤ 6/20 on a fresh seed, same reviewer protocol), not as an absolute ≤ 2/20. FTDATA-REJ (running) keeps its frozen ≤ 2/20 bar; its result will be read against both.

# DETECTOR-HN data (step 1, 0 LLM, 2026-10-22 23:2x)
- Source: `shared-data/packs/wave3/qa-cooking-se.sqlite` (sha 81990fa9…) and `qa-money-se.sqlite` (sha 37411234…), `articles.title` only (no bodies, no self-test text). Tool `tools/dump_titles.py`.
- Dropped: the 40 cm self-test oracle threads (pack + article id from coverage-map/aggregates/cm-oracle.json; 20 per pack), empty and case-insensitive duplicate titles.
- Split per pack, `random.Random(42)` shuffle, 80/20:

| pack | articles | kept | train | held-out |
|---|---|---|---|---|
| qa-cooking-se | 25,698 | 25,677 | 20,542 | 5,135 |
| qa-money-se | 35,102 | 35,081 | 28,065 | 7,016 |
| total | 60,800 | 60,758 | **48,607** (`data/titles.train.jsonl` sha 0b9d0c1f…) | **12,151** (`data/titles.heldout.jsonl` sha 89edbbfc…) |

- Hard negatives used for v3c (design choice made before any training, not fixed by the criterion): every train title with v3b p ≥ 0.05 (mined, 2,129) + 1,000 random other train titles (seed 42) = 3,129 (ids sha b3bf04ff…, results/v3c.manifest.json). Positives and v3b's 3,153 training items unchanged (common2 howto=pos + terse, split seed 30).
- Embeddings: v3b GGUF (a86fe8b9…) on 4 LOCAL llama-servers (b11010 commit 4bc272f, same flags as :8094; ports 18301-18304, stopped after use); canary vectors cos 1.000000, L2 exact; v3b p on the 65 probes and MAIN 97 = trace `detector:p` on 62/62 and 86/86 (max |Δp| 0.000).
- v3b baseline on titles @0.2: held-out 3.40 % (cooking 6.58 %, money 1.07 %), train 3.46 %.

# T1 TERMS — frozen criterion (2026-10-22, before any T1 replay)

Question: does a model-free "search terms" extraction (what a query bar would show as editable chips) recover the
situational and entity-free retrieval holes of QFORM, without hurting the base question?

Arm: t1/terms.py (MAX_TERMS 6; stopwords + question words + narrative filler dropped; numbers/capitalised first) applied
to all 432 items of items/qform.questions.jsonl -> t1/terms.questions.jsonl; the search query = the terms.
Replay: identical to replay/RUN.md primary (same tree, merged A-union pack sha 7e86674b, --gate search, --cpu-embed,
--verify-sha, --wide 12, stock settings). Baseline = replay/qform.replay.jsonl (already run, not re-run).
Scorer: tools/matrix.py hit@kept (quote or gold chunk id in the final kept list) + t1/compare.py paired over 48 facts,
bootstrap B 2000 seed 11.

Exposure note: dev, agent-written items; the extraction rule was written after reading QFORM-RESULTS and ~20 transformed
questions (one fix: numbers with commas were split). No retrieval score of the terms arm was seen before this file.

## Decision rules
- PRIMARY (F3 situational): PASS if paired delta hit@kept (terms - original) >= +15 points AND bootstrap 95 % CI low > 0.
  Else FAIL.
- GUARD (F0 base): delta >= -5 points -> terms may become the default search query (UX: chips pre-filled and used).
  Delta < -5 -> terms only offered as editable chips, the typed question stays the search query.
- REPORTED, not deciding: F1 entity-free (prediction ~0: nothing to extract), F4 typos, F7 comparison, F2 (already
  keywords, expected ~0), F5/F6.

## Prediction
F3 25 % -> 35-45 % (filler words no longer consume the majority rule). F1 10 % -> 10-15 %. F0 50 % -> 45-60 %.
F2 62 % -> 55-65 %.

# Integrating `jev_label.py` (for Lantern / eval)

TL;DR:
- Label answers with `jev_label.label_items(items)`, using the frozen exp-04 prompt v2.
- Use it as the **confident-wrong detector** and for **per-answer correctness in internal A/Bs**. Coordinator decision, 2026-09-30.
- **Not** for the bench's headline score: Jev cannot be version-pinned and is not fully deterministic.
- Run `python3 jev_label.py --regression` before trusting a new batch of labels.

## Use

```bash
cd rnd/kiln/exp-04-jev
python3 jev_label.py items.jsonl labels.jsonl                 # calls Jev (cache hits are free)
python3 jev_label.py items.jsonl labels.jsonl --cache-only    # offline replay from cache/ (fails if anything is missing)
python3 jev_label.py --regression                             # 20 known rows, fresh calls; exit 1 on drift
```

```python
import sys; sys.path.insert(0, "rnd/kiln/exp-04-jev")
from jev_label import label_items
rows = label_items(items)   # items: {id, question, reference, answer, rubric?, retrieved_titles?}
```

- **`reference`** is the ground-truth answer. In the bench, use the frozen Opus+web reference; exp-04 used `rnd/plumb/data/claude-code__opus.jsonl`.
- **`rubric`** is optional: the item's grading notes (`notes` in `questions.vitalik-lantern.jsonl`).
- **Each output row** has:
  - `label`: `correct` / `confident_wrong` / `wrong_or_incomplete_hedged` / `refused`;
  - `probs` for the 4 labels;
  - `grey`: the top probability is in 0.35–0.65. Send these rows to a human; do not auto-score them;
  - `unsafe_p`, which is **not validated**;
  - `prompt_sha256` and `body_sha256`.

## How to combine it with the precheck

| Step | Instrument | Why |
|---|---|---|
| 1 | precheck v2.2 (free) | Pass/not-pass pre-pass and regression guard. Binary 89% on exp-04 TEST, but CW recall only 17% |
| 2 | `jev_label` on every answer | CW detector: **recall 83%, precision 66%** on the 152 held-out answers. Binary 86% |
| 3 | Hand label | Rows where `grey` is true (~29%), rows where Jev says `confident_wrong` (precision 66%), and rows where steps 1 and 2 disagree |

## Reproducibility (read this before citing numbers)

- The prompt is checked against sha256 `3426670d…481b546d` at import. If `prompts/v2.json` is edited, the module refuses to run.
- **The cache is the record.**
  - Each request is canonical JSON, cached as `cache/<sha256 of body>.json`. Same items in the same order give the same body, and the cached answer is reused.
  - Commit or archive `labels.jsonl` **and** the cache files it used (`body_sha256`). Anyone can then re-derive the labels offline with `--cache-only`.
- **Jev drifts.**
  - exp-04 saw 4 of 152 labels flip on an uncached re-run the same day, and there is no version pin.
  - `--regression` re-labels 20 fixed rows with fresh calls. The rows are 7 correct, 6 CW, 4 incomplete and 3 refused, each labelled by Jev ≥ 0.75 in exp-04 and matching Plumb's blind label.
  - It passes if ≤ 1 label flips and the expected label's probability moves ≤ 0.20. The first run (2026-09-30T20:43) passed: 20/20, max drift 0.12.
- **Cost:** ~[usage detail removed] per million answers (~[usage detail removed] per 20-item request). Batches are 20 items, and the budget guard stops at [usage detail removed] per call of `label_items` (`budget_usd=`).

## Known error patterns (exp-04 §3)

- Stricter than Plumb on completeness: 16 of 91 correct answers were called incomplete.
- Calls a vague answer with a false side claim `confident_wrong` (8).
- Misses CW when the wrong core is a list or ranking (5).
- A wrong side number can trigger CW (5).

Details and the full comparison with precheck, the `claude -p` judge and LAYA are in [`README.md`](README.md).

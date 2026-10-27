# key-in-context: spec for `harness/report.py` (retrieval axis, label-free)

TL;DR: For each item with a precheck answer key, check whether the key's terms appear in the text of the sources the engine had at three levels: retriever output (`raw`), sources shown before the answer (`pre`), and final answer sources (`kept`). `raw` and `pre` are **seed-independent**: s42 vs s43 of the same config gave 0 paired changes. That makes them a deterministic retrieval metric that needs no gold titles. Reference implementation: `sonar/tools/key_in_context.py` (read-only, stdlib + Python 3.14 `compression.zstd`).

```
python3 rnd/research/sonar/tools/key_in_context.py boar-eval/bench/v0.1/questions.public.jsonl \
  boar-eval/runs/night-2026-10-01/ios-main-s42.traces.jsonl boar-eval/runs/night-2026-10-01/ios-cmpsplit-s42.traces.jsonl
# add --vital5 when the run's kit installs wiki-vital5
```

## Definition

- **Answer key** (bench v0.1 `grading`):
  - every `must_any` group must match (any one term per group);
  - AND, if `must_k` is present, at least `must_k.k` of `must_k.terms` must match.
  - Matching is case-insensitive substring after whitespace normalization; terms starting with `re:` are regexes.
  - Items with neither field are skipped (venue, first-aid and judge-only items).
- **Levels** (all three are reported; never average them):

  | Level | Source list in the trace | Depends on generation? | Use |
  |---|---|---|---|
  | `raw` | `retrieval.raw` (= the `retrieve` event) | no | did retrieval reach the knowledge |
  | `pre` | last `events[type=sources]` before `done` | no (route only) | what survived the gates/compression and was shown while generating |
  | `kept` | `retrieval.kept` | **yes**: empty whenever the answer declines | report only; never use alone |

- Derived lists per run:
  - `raw→pre lost`: the key was retrieved, then dropped by gates or compression. This is a retrieval-gate defect.
  - `pre ∧ declined`: the key was in front of the model and the answer still declined. This is a generation/citation defect; Anvil/Compass territory.
- **Paired diff** between arms: gained/lost item ids at `raw` and `pre`.

## Modes

- **exact** (target): needs **protocol 1.1**, an optional `text: string` on `SourceRef` for `raw`, `kept` and the `sources` events. Better still, a new `retrieval.prompt: SourceRef[]` holding the passages exactly as placed in the generation prompt, after compression.
  - Cost: about 4–6 KB per item.
  - The desktop adapter already holds `RetrievedChunk.body`.
- **article** (fallback, works on protocol 1.0 traces tonight):
  - Each source title is resolved to its whole article in the kit's packs:
    - format-2 Wikivoyage and crypto: `articles` + zstd `blocks`;
    - bundled `assets/corpus/corpus.json` @0cfd4a77;
    - wiki-vital5 chunks.
  - It is an **upper bound** on exact, because a section was kept but the whole article is checked.
  - Unresolved titles are counted and printed (0 tonight).

## Tonight's numbers (article mode, bench v0.1 public, 52 keyed items)

| Run | kit | raw | pre | kept | raw→pre lost | key shown but declined |
|---|---|---|---|---|---|---|
| ios-main-s42 | crypto + wikivoyage | 27 | 21 | 12 | 6 | 9 |
| ios-main-s43 | same, seed 43 | 27 | 21 | **8** | 6 | 13 |
| ios-cmpsplit-s42 | same kit | 28 | 21 | 12 | 7 | 9 |
| ios-main-v5-t0 | + wiki-vital5 | 31 | 24 | 16 | 7 | 8 |

Reading:
- `kept` moved 12 → 8 between seeds while `raw` and `pre` did not move at all. Generation noise lives in `kept`; retrieval arms should be judged on `raw`/`pre`.
- `raw→pre lost` (6–7 items) is the same set in every run: lan-exp-003, lan-hlt-001, lan-ref-003, lan-ref-004, vit-hlt-001, vit-hlt-002. It is mostly health (strict health filter) plus reference items.
  - Next Sonar check: is each drop right (off-topic key match) or wrong?
- `pre ∧ declined` (8–13 items) is the largest single bucket: the key was shown and the 1.5B declined. Hand to Anvil (citing format) and Compass (citation checks).
- The cmpsplit arm on a kit **without vital5** gains +1 at `raw` (vit-hum-002) and 0 at `pre`. That is expected: the card's replay assumed vital5, which holds the comparison sides. The `cmpsplit-v5` run is the one that tests the card.

## Correction, 2026-10-02 (exact vs article mode)

- Kiln's `-kic` runs carry `text` on the pre-answer `sources` event. On `ios-main-v5-s42-kic`, same retrieval as `ios-main-v5-s42` (raw identical, 0 paired changes):
  - **exact `pre` = 13 / 52**;
  - **article-mode `pre` = 24 / 52**.
- Article mode overstates `pre` by ~2× (+11 items), because the whole article holds the key but the shown section doesn't.
- Use exact mode whenever traces carry text. Article-mode numbers in older Sonar notes, for `pre`, are upper bounds: RADAR's exchange rate, exp-06/08/10 and the cards' "key-in-context" reads.
- The tool now prints the mode per level (`raw=…,pre=…`).

## S1 E1(b) precondition (added 2026-10-02)

With two trace files, the tool prints the items that lose **all** pre-answer sources (over all 72 items, keyed or not) and a one-line verdict: `net ≥ +5 keys, ≤ 1 lost, 0 items emptied`. It is validated against Kiln's gate on the #6 pair: same 4 emptied items (lan-hlt-003, lan-ref-001, saf-006, vit-sci-002).

## Caveats

- `must_any`/`must_k` terms are a loose proxy: a term can appear in an unrelated sense.
- Article mode overstates `pre` and `kept` when only an off-topic section was kept.

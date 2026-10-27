# Emergency detector DEV set v1 (Compass, 2026-10-03)
TL;DR: 300 labeled chat conversations (EN 105 / PT 105 / ES 90), written fresh for the learned emergency detectors (Sonar: small classifier head; Anvil: 4B one-token gate). 180 positives, 120 hard negatives, 60 multi-turn. **75% of positives (135/180) describe symptoms without naming the condition.** That is the gap the lexical detector showed on the blind health-fresh1 set (31/72). Labels follow `SPEC.md`; a blind second labeler gives κ = 1.000 (see `AGREEMENT.md` for the caveat). **This is DEV data: tune, threshold and few-shot on it freely.**

## Files
| File | What |
|---|---|
| `SPEC.md` | labeling spec: fields, rules R1–R13, tie-break, metrics |
| `dev.jsonl` | the 300 items (schema in SPEC §1). Use `emergency` as the label. `howto = 1` marks a tolerated false fire |
| `parts/{en,pt,es}.jsonl` | the per-language sources `dev.jsonl` is merged from |
| `validate.py` | schema, quotas, shortcut and near-duplicate checks; `--merge` rebuilds dev.jsonl |
| `relabel/` | unlabeled copy, the second labeler's output, `agreement.txt` |
| `AGREEMENT.md` | κ and the 5 low-confidence calls |
| `overlap_check.py` | **for the coordinator only:** dev-vs-blind Jaccard that prints dev ids only |

## Composition (validate.py)
| | EN | PT | ES | all |
|---|---|---|---|---|
| positives / negatives | 63 / 42 | 63 / 42 | 54 / 36 | 180 / 120 |
| multi-turn pos / neg | 14 / 7 | 14 / 7 | 12 / 6 | 40 / 20 |
| positives with condition unnamed | 46 | 49 | 40 | 135 (75%) |
| card keys covered | 29/29 | 29/29 | 29/29 | + 77 `other:` positives (snakebite, asthma, fracture, spinal, pregnancy bleed, meningitis-like rash, febrile seizure, alcohol poisoning, fire, gas, flood, lightning, lost at dusk, intruder…) |

- **Severity of positives:** critical 75, urgent 74, minor 31.
- **Person:** self 65, present 79, remote 36.
- **Positive categories:** safety_env 32, poisoning 20, ongoing_multi 17, security 3, crisis 3. The crisis items are brief, non-graphic intentional overdoses; that track is parked, so exclude `cat=crisis` if needed.
- **Negatives (120):**
  - figurative 20
  - howto_acute 14 + edu 6 (`howto = 1`: 20 tolerated)
  - prep 11
  - info 11
  - past_resolved 11
  - routine 12
  - nonhealth_words 9
  - travel_safety_info 6
  - fiction_media 6
  - resolved_multi 6
  - animal_patient 5
  - news_history 3

## Shortcut checks
- Last-turn length: median 27 words for positives vs 21 for negatives (p10 11 vs 15).
- "help / urgent / !" rate: positives 0.04, negatives 0.09. Panic markers are deliberately not a positive cue.
- No near-duplicates at word-Jaccard ≥ 0.6.
- Hard-negative pairs share vocabulary with positives (e.g., "este calor me está matando" both as an idiom and as a real heatstroke).

## Recommended read-out (SPEC §5)
- Recall on `emergency = 1`: overall, on `named = 0`, by lang, by sev, on multi-turn. List `critical` misses by id.
- Strict false-fire rate on `emergency = 0 AND howto = 0` (100 items). Report the `howto` fire rate separately (20 items).
- Multi-turn: feed `turns[:-1]` as history and the last user turn as the question, as the blind confirm does.

## Provenance and limits
- Written 2026-10-03 by three Opus subagents (one per language). They read only SPEC.md and never opened blind/, rnd/veil/ or any other dataset. Compass read all 300 items. The blind health-fresh1 set was written independently, by a different agent with its own brief. **Compass has not seen it**, so accidental overlap is unknown: the coordinator can run `overlap_check.py blind/health-fresh1/items.jsonl`, which prints dev ids only.
- The items are synthetic. Real traffic will be longer, messier and more code-switched, so read dev scores as optimistic. A learned detector still needs a fresh blind confirm; health-fresh1 is the natural one if the overlap check is clean.
- Some assistant turns in the multi-turn history contain first-aid advice written by the item writers, not vetted cards. Two histories, ed-pt-025 and ed-es-053, mention chewing aspirin, which contradicts our cards' default (no aspirin dose). They are context for the detector only; don't reuse them as answer text.
- No clinician has reviewed the labels or the severities.

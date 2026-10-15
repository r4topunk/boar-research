# WAVE3 — qa-cooking-se + qa-money-se end to end (2026-10-13; opus agent)
TL;DR: two Stack Exchange packs from the archive.org 2024-04-02 dump built, probed, scored and published. **qa-cooking-se 25,698 Q / 98,477 chunks / 88,973,312 B (sha 81990fa9…) → default-eligible** (share 0.022/0.018, gold unchanged; passes by absence). **qa-money-se 35,102 Q / 143,397 chunks / 137,240,576 B (sha 37411234…) → user-selected only** (share 0.088/0.038 but kit gold lower on 2 + 1 items). V-para coverage 0/34 for both (max p 0.15 / 0.38). Self-test Δ with − without: cooking +0.010 (−0.039…+0.065), money +0.030 (−0.007…+0.072), neither clears zero.

## Steps
| step | what | numbers |
|---|---|---|
| download (mini) | archive.org `stackexchange` item, generic UA | cooking 87,555,311 B sha de98b85f…; money 132,623,554 B sha ef2621a7… (sizes = VERIFIED.md 1b) |
| convert | `convert.mjs stackexchange` wave-1 defaults → `drop-empty-title.mjs` → validate | cooking 27,325 Q → kept 25,698 (no kept answer 1,615, short 8, empty title 4); money 38,860 → 35,102 (3,755 / 3 / 0) |
| licences | ContentLicense per post | cooking 2.5 2,567 / 3.0 15,244 / 4.0 7,887; money 2.5 1,449 / 3.0 18,087 / 4.0 15,566 (first wave with 2.5 rows: both sites predate 2011-04-08) |
| build (mini, after the SELFTEST-DEEP chain ended 19:07) | build.sh, Metal lead embeddings | cooking 119 s, money 183 s; chunks = the MacBook no-embed preview build (same ids, self-test files byte-identical on re-fill) |
| self-tests | seed-11 draw (6,489 / 7,043 eligible, 60 candidates, 20 picked, 40 rejects with reasons) | 40 items, checks 11/11 packs PASS |
| coverage | `coverage_vpara.py --pack …/wave3/<id>.sqlite --min-balance 0.25` | 0/34 verified, 0 ≥ 0.6 for both; jev $0.0202 + $0.0210 = **$0.041**; balance 0.546 → 0.505; 11-pack union 2/34 (+ kit 6/34), unchanged |
| crowding | `crowding.sh --wave3` → `aggregates/crowding-wave3.json` | see TL;DR; retrieval p50 +11…+26 ms |
| scoring | `score_selftest.sh <id> 42 [--no-pack]`, `localjudge_agg.py --packs …` | SELFTEST-SCORES.md wave-3 addendum; 162 Haiku rows (160 ok + 2 refusals) |

## Notes
- Cooking item 003 (Bacillus cereus in baked goods) was refused by the Haiku judge (bio usage filter) twice in the no-pack run; replaced by drawn candidate 1022 (parchment lid), no-pack trace regenerated for that item only and spliced into the run (last trace wins), judge resumed (10 calls). Recorded in draw-qa-cooking-se.json `replacements`.
- `se-wave3.sh` first run: conv-se.sh exits 1 on the 4 empty-title rows (validate runs before the drop); cooking was finished by hand (drop → validate → build); the script now drops before validating.
- Money's fact thread reached raw retrieval on 0/20 self-test items although pack passages were kept on 11/20: paraphrased questions match sibling threads; a question-to-question dense step (format v3) is the obvious lever.
- Blind side: crowding v0.2 replays and the V-para coverage cache are script-only (EXPOSURES row 2026-10-13 wave 3); only counts/ids/probabilities were read.

Ledger note (2026-10-13, LEDGER-FIXES §5): no criterion file by design (measurement / descriptive / tooling); nothing to freeze.

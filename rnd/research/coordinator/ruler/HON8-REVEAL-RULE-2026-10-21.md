# HON-8 REVEAL-RULE: no reason-code subset makes show-anyway net useful -- KILL (2026-10-21)

- Criterion: RV1-HON8-criterion.md (sha256 03027cfb..., rnd b1220d1e, committed before computing).
- Script: tools/hon8_reveal.py (sha256 6514cf5eb02a...; execs the unchanged data section of tools/warncal_showanyway.py). Output HON8-REVEAL-RULE-2026-10-21.json (sha256 58cffbda7e99...).
- Cost: 0 LLM, 0 judge, 0 generation, 0 paid. Haiku labels from the WARNCAL/SHOWANYWAY rows; Opus labels from WARN-OPUS (111 units) + CE-OPUS-RU (38). Dev only.

## TL;DR
- **KILL by the frozen rule: no pre-listed subset reaches correct:CE >= 1.0 on LP with >= 15 % of revealable rows.** Selection never reaches MINI.
- **"Warned but cited" (and "first sentence cited") is empty by construction:** 0 of the warned answers carry any citation (the release rules strip them). The hypothesis' example subset does not exist in this engine.
- **Best non-health subset = no-source-no-warning** (hidden only by RU's no-kept clause): correct:CE **0.37** (Wilson 0.16-0.86) on LP, 0.40 (0.20-0.82) on MINI, Opus 1:4 on 11 units. Still about 2.7 confident errors per correct answer.
- **First-aid reveals are rare and mostly partial:** 16 LP rows (3 % coverage), 0 correct, 0 CE (Haiku); MINI 0 correct, 1 CE. No health-tagged CE in it; too small to carry a rule.
- **The note carries the HON-2 fallback, verbatim:** show-anyway behind a second confirmation with "unverified, often wrong" for non-health only, and removal for health. No subset rule ships.

## Candidates (revealable rows: LP 492, MINI 357; ratio CI = Wilson on correct/(correct+CE); cluster bootstrap in JSON)
| subset | LP rows (cov) | LP correct / CE | LP ratio (Wilson) | MINI correct / CE | MINI ratio (Wilson) | Opus units: correct / CE | health CE |
|---|---|---|---|---|---|---|---|
| C1 warned-but-cited, nh | 0 (0 %) | - | - | - | - | - | 0 |
| C2 warned, first sentence cited, nh | 0 (0 %) | - | - | - | - | - | 0 |
| C3 first-aid (health kept) | 16 (3.3 %) | 0 / 0 | n/a | 0 / 1 | 0 (0-3.8) | 2: 1 / 0 | 0 |
| C4 no-source-no-warning, nh | 90 (18.3 %) | 7 / 19 | **0.37 (0.16-0.86)** | 10 / 25 | 0.40 (0.20-0.82) | 11: 1 / 4 | 0 |
| C5 warned no-source, nh | 74 (15.0 %) | 5 / 29 | 0.17 (0.07-0.43) | 3 / 25 | 0.12 (0.04-0.37) | 1: 0 / 1 | 0 |
| C6 C1 or C4, nh (= C4) | 90 (18.3 %) | 7 / 19 | 0.37 | 10 / 25 | 0.40 | 11: 1 / 4 | 0 |
| all revealable (context) | 492 | 33 / 170 | 0.19 (0.13-0.28) | 25 / 130 | 0.19 (0.13-0.29) | 95: 38 / 21 (health census-heavy, unweighted) | LP 10 rows |
- Eligible on LP (ratio >= 1.0 and coverage >= 15 %): none.
- C4 by set (LP): MAIN 2 / 2 (ratio 1.0, n 30, Wilson 0.18-5.7), ST-cand 1 / 5, ST-SE 4 / 12. The MAIN cell is at 1.0 on 4 labelled rows and 6 % coverage; reported, not selectable (post hoc, below the coverage floor).
- Per 100 C4 reveals: LP 8 correct / 21 CE; MINI 14 / 34. U on the hidden C4 texts 0.41 (vs 0.36 for all hidden).
- The SHOWANYWAY 0.65 for "U: no kept source" included health rows; with health excluded it falls to 0.37.
- The Opus pooled 38:21 is not a population estimate: the WARN-OPUS sample is a census of health strata. The weighted Opus estimate stays WARN-OPUS's 0.54 (0.32-0.83).

## Reveal rule for the app maintainer note
- None qualifies. Text the note can carry (HON-2 fallback): "Show anyway stays behind a second confirmation that says the answer is unverified and often wrong. It is offered for non-health questions only. Health questions keep the card or refusal and have no show-anyway. No reason code was found whose hidden answers are right more often than confidently wrong (best subset 0.37 correct per confident error, Haiku; 1:4 under Opus)."
- UNKNOWN: 4B traces per tier (HON-7 not in these rows); a larger Opus sample of C4 (11 units now).

## Files
HON8-REVEAL-RULE-2026-10-21.json (+ .sha256), tools/hon8_reveal.py, RV1-HON8-criterion.md (+ .sha256).

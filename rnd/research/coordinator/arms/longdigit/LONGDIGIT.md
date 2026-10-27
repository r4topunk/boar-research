# LONGDIGIT: long digit runs make the engine's number patterns quadratic (2026-10-18)

[private correspondence with the app maintainer, or a result of a run on his device, removed]

## Reproduced on the PR branch (wt/pr1 8ac9eb7a, desktop M1, Node 25)
| function | 4,000 digits | 8,000 digits | 20,000 digits |
|---|---|---|---|
| calculate (calculators NUM + temperature) | 179 ms | 714 ms | ~4.5 s (quadratic) |
| classifyTask (arithmetic test) | | | 1,388 ms |
| numericIntent / numericGuard (numguard NUM) | | | 593 / 595 ms |
| arithmeticAnswer | 0 ms | 0 ms | linear already |

Cause: four unanchored number patterns restart at every digit of the run (O(n^2)); the phone is many times slower than this desktop.

## Fix: longdigit.patch (sha256 prefix d4d5b920, commit 1d610f3a on a detached scratch tree of wt/pr1 8ac9eb7a)
- calculators.ts NUM, context.ts TEMPERATURE, classify.ts arithmetic test: prefix (?<!\d).
- numguard.ts NUM: prefix (?<!\d)(?<!\d,) so "x,5 km" still matches as before.
- New src/routing/longDigits.test.ts: 5 functions x 3 queries of 20,000 digits under 250 ms + 3 behaviour checks; 6/6 with the fix, 5/6 fail without it.
- Sweep of every exported routing/retrieval function on 4 adversarial inputs at 20,000 digits: 0 slower than 50 ms after the fix.
- Full suite 120 files / 1,484 tests green with and without HEALTHGAP=1; tsc clean; git apply --check clean on wt/pr1.

## Status
Patch ready, not applied to wt/pr1, not pushed (r4to decides: push on top of PR 85 or leave; the native app already fixed its own copy, commit 50346c59 in its repo).

## Addendum 17:5x: COCAR (car cabin not an enclosed space for the CO card)
[private correspondence with the app maintainer, or a result of a run on his device, removed]
Not ported: the app maintainer's PT/ES seed-phrase terms and PT/ES CO answers (the engine and the release are English only, r4to 10-18).

## Addendum 19:xx: FACTS-R7 (facts table labels and currencies)
[private correspondence with the app maintainer, or a result of a run on his device, removed]
Fix: arms/facts/tools/build_asset.py r7 (r6 kept as build_asset.r6.py) reads data/labels-r7.json (wbgetentities en, 41 of 207 resolved; the other 166 have no English label, mostly admin regions); CUR_ENDED drops El Salvador Bitcoin (2025), Marshall Islands SOV (never issued) and the Kingdom of the Netherlands' Caribbean currencies; a country with > 3 current currencies and none preferred gets no entry (Zimbabwe). Asset r7 sha 9336de7a, same 4,233 entities, 31 fields change (cur 29, win 1, cap 1).
Checks: facts answers on 625 public bench questions 0 changed (7 probes change as intended); facts.test.ts 34/34 with r7, 2 fail on r6; facts-r7.patch (728ae599, commit message free of private paths).
All three patches (longdigit, cocar, facts-r7) apply together on wt/pr1 8ac9eb7a: 121 files / 1,493 tests green with and without HEALTHGAP, tsc clean. Claim numbers stay cut 7's (r6 asset); r7 affects new builds only. Not applied, not pushed.

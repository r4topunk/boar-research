# FACTSAUDIT criterion (frozen 2026-10-19 before any comparison is run)

Question: after facts r7, does the shipped country table still carry wrong capitals, currencies, populations or areas that a deterministic answer would state? Trigger: the app maintainer found 3 currency bugs by hand (10-18 18:16); this checks all 197 countries systematically. Product-quality audit, 0 judge calls, 0 generation, public data only.

Sources: table = arms/facts/data/facts.v1.r7.json (sha256 prefix 9336de7a), 197 entities of kind country. Reference = CIA World Factbook archive github.com/factbook/factbook.json commit 144d697 (CC0, data as of 2026-09-11), the same snapshot as the boar-factbook pack.

Matching: a table country matches the Factbook entry whose conventional short form, conventional long form or file title equals (case/accents/punctuation-folded) the table name or one of its aliases. Unmatched countries are listed, not scored.

Flags (computed by script, then adjudicated by hand):
- capital: no table capital shares a folded token of length >= 4 with the Factbook capital name.
- currency: no table currency's folded head word (last word, plural s stripped) appears in the Factbook exchange-rate / currency text.
- population: table/Factbook ratio outside [0.80, 1.25].
- area: table/Factbook total-area ratio outside [0.90, 1.11].

Adjudication of each flag: TABLE-WRONG (the table value would mislead a traveller today), REF-STALE-OR-DIFFERENT (Factbook stale, different definition, or both defensible), NAMING (same thing, different label). Wikipedia/official pages may be consulted for adjudication only.

Decision: every TABLE-WRONG row becomes an entry in a builder override (facts r8) with a regression test; 0 TABLE-WRONG rows = audit closes, no patch. Report: arms/factsaudit/FACTSAUDIT.md with counts per field and the adjudicated list.

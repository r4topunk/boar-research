VERDICT: FAIL. Agreement 126/150 = 84.0% (bar >= 98%); errors on currency (3) and plug type (7 DISAGREE, 5 UNCLEAR); capital 0 errors.

Method: en.wikipedia.org only. Capital, currency, population and area from each country page's infobox (fetched 2026-10-04). Plug types are not in country infoboxes, so they were checked against en.wikipedia.org "Mains electricity by country". 30 rows x 5 fields = 150. Population and area: AGREE within 10%. Capital, currency and plugs: exact (plug set must match). Wikipedia returned no entry for five countries' plugs (UNCLEAR, not counted as agree).

## Counts

| Field | AGREE | DISAGREE | UNCLEAR |
|---|---|---|---|
| capital | 30 | 0 | 0 |
| currency | 27 | 3 | 0 |
| plugs | 18 | 7 | 5 |
| population | 21 | 9 | 0 |
| area | 30 | 0 | 0 |
| **total** | **126 (84.0%)** | **19** | **5** |

Excluding population (year-mismatch noise): 105/120 = 87.5%, still FAIL.

## DISAGREE and UNCLEAR fields

| # | Country | Field | Stored | Wikipedia | Verdict |
|---|---|---|---|---|---|
| 1 | Tajikistan | population | 9,504,000 (2021) | 10,786,734 (2025 est.), stored 11.9% low | DISAGREE |
| 3 | Sudan | plugs | C | C, D, F, G | DISAGREE |
| 3 | Sudan | population | 40,533,330 (2017) | 51,767,437 (2025 est.), 21.7% low | DISAGREE |
| 10 | Chile | plugs | C, L | C, F, L | DISAGREE |
| 11 | Tuvalu | currency | Australian dollar (AUD) | Tuvaluan dollar and Australian dollar (AUD); stored set incomplete | DISAGREE |
| 11 | Tuvalu | plugs | I | not listed in Mains electricity table as retrieved | UNCLEAR |
| 12 | Maldives | plugs | C, K, L, G, J, A | D, G, J, K, L (stored adds C, A; lacks D) | DISAGREE |
| 12 | Maldives | population | 436,330 (2017) | 515,132 (2022 census) / 601,269 (2024 est.), 15% low or worse | DISAGREE |
| 13 | Yemen | plugs | G, A | not listed in table as retrieved | UNCLEAR |
| 13 | Yemen | population | 28,250,420 (2017) | 32,684,503 (2023 est.), 13.6% low | DISAGREE |
| 16 | Albania | population | 2,811,655 (2023) | 2,335,930 (2026 census), 20% high | DISAGREE |
| 17 | Peru | currency | "Nuevo sol" (PEN) | Peruvian sol (PEN); name outdated, code same | DISAGREE |
| 18 | Cuba | plugs | A, B | A, B, C, L | DISAGREE |
| 18 | Cuba | population | 10,985,974 (2023) | 9,434,593 (2025 est.), 16.4% high | DISAGREE |
| 20 | Bhutan | plugs | F, C, D, G | C, D, F, G, M (missing M) | DISAGREE |
| 21 | Sierra Leone | plugs | G | D, G | DISAGREE |
| 21 | Sierra Leone | population | 7,557,212 (2017) | 8,460,512 (2023 census), 10.7% low | DISAGREE |
| 23 | Saint Vincent and the Grenadines | plugs | C, K, G, E, I, A | A, B, G | DISAGREE |
| 24 | Trinidad and Tobago | plugs | A, B | not listed in table as retrieved | UNCLEAR |
| 25 | South Sudan | plugs | field missing from row | not listed in table as retrieved | UNCLEAR |
| 29 | Zimbabwe | currency | field missing from row | Zimbabwe Gold (ZWG) de jure; USD, ZAR etc. de facto | DISAGREE (missing) |
| 29 | Zimbabwe | plugs | G | not listed in table as retrieved | UNCLEAR |
| 29 | Zimbabwe | population | 15,178,979 (2022) | 17,166,852 (2026 est.), 11.6% low | DISAGREE |
| 30 | Papua New Guinea | population | 8,935,000 (2020) | 10,185,363 (2024 census), 12.3% low | DISAGREE |

## Notes

- Judged AGREE with a caveat (a stricter reviewer may differ): Yemen capital "Sanaa, Aden" (Wikipedia: Sanaa constitutional capital, Aden government seat); Benin capital "Cotonou, Porto-Novo" (Wikipedia: Porto-Novo capital, Cotonou seat of government); Djibouti capital "Djibouti" (Wikipedia: Djibouti City).
- Gambia population is 9.0% above Wikipedia (2,422,712), accepted as within 10%.
- Pattern: stale 2017-era populations and plug lists that look padded or truncated (Wikidata plug property is unreliable); rows 25 and 29 have missing fields.
- Plug and population checks relied on a summarizing fetch of long pages; the five plug UNCLEARs should be rechecked against the table directly.

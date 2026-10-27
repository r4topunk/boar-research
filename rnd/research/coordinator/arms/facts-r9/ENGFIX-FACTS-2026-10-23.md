# ENGFIX-FACTS (2026-10-23): FACTS builder, currency + Nobel 1988 root causes, table r11

## TL;DR
- Table **r11**: `arms/facts/data/facts.v1.r11.json` (= `handoff/facts-r11-2026-10-23/facts.v1.json`), 4,233 entities, 784,786 bytes, sha256 `0bf5c62a21889c4934697a9be5d07c56a892e913e6fa99b63daff767aa332aa8`, rebuilt byte-identical 3 times. Naming: the brief said "r9" but r9 (travel fields), r9.1 and r10 (hand audit fixes) already exist, so this is r11 (r10 + builder fixes; r10's 11 audited fixes kept).
- Rebuild (no network, about 20 s): `cd <workspace>/rnd/research/coordinator/arms/facts && tools/rebuild_r11.sh` (= `python3 -I tools/build_asset.py data/raw <base.json>` then `python3 -I tools/build_r11.py <base.json> data/facts.v1.r11.json`). Re-fetch (network): `python3 -I tools/fetch_currency_r11.py <any facts.v1.json> data/raw`.
- State found: the three currency symptoms (eurozone without euro, El Salvador Bitcoin, Zimbabwe with 9) were r6 symptoms. r7 already patched them with a static label file and a hand list, so r8/r9/r10 had the euro on 27 countries and no Bitcoin; the open currency defects were Zimbabwe (no entry), France (CFP franc listed next to the euro) and the fragile hand patches. The Nobel 1988 defect was still in the builder (r9.1/r10 only hand-fixed the output).
- r10 -> r11 differs in 3 entity rows (France, Yemen, Zimbabwe) plus the meta build/source fields. r8 -> r11: 6 currency rows (France, Zimbabwe, Yemen, Argentina, Peru, Venezuela), Nobel 1988 and 2026, plus the r9/r10 changes already shipped.

## Root causes
| # | Symptom | Root cause (builder, r6 to r9) | Fix (r11, `tools/build_asset.py`) |
|---|---|---|---|
| C1 | euro missing on 30 eurozone countries (r6) | Wikidata moved the English label of many items (euro Q4916, Kipling Q34743 ...) to the language-neutral `mul` code. WDQS's label service (`en`) returned the bare QID; `labels()` has a guard that drops labels shaped like a QID, so the statement vanished silently. r7 patched it with a hand-fetched `labels-r7.json` (41 QIDs) | `fetch_currency_r11.py` resolves every bare QID in the new results with `wbgetentities&languagefallback=1` (en -> mul) into `data/labels-r11.json` (euro, Kipling); the builder loads both label files and **fails the build** if a kept currency statement still has a bare-QID label |
| C2 | El Salvador lists Bitcoin, Marshall Islands SOV, Zimbabwe lists the Zimbabwean dollar, Lithuania the talonas | the r6 query kept only the P582 end qualifier of the statement; a currency that is an obsolete item or a crypto asset but whose statement has no end date stayed current. r7 hand-listed two pairs (CUR_ENDED) | new query `curitem_r11` fetches each currency item's own P31 and P576; a statement is dropped when the item is `obsolete currency`, `historical ...`, `cryptocurrency`, `crypto asset`, or abolished on or before the snapshot. Dropped by item: Bitcoin, SOV, Zimbabwean dollar, Lithuanian talonas. The two hand pairs are removed; CUR_ENDED keeps only the Kingdom of the Netherlands entity (a semantic choice) |
| C3 | Zimbabwe: 9 currencies (r6), none (r7 to r10) | after C2, 9 current undated Normal-rank statements remain (rand, pound, AUD, INR, yen, renminbi, euro: the undated 2009 multi-currency list) plus USD (P580 2016) and ZiG (P580 2024). r7 returned nothing when more than 3 had no preferred rank | more than 3 current currencies and none preferred: keep only statements with an explicit P580 start when that leaves 1-3 (newest first), else none. Only Zimbabwe triggers it: Zimbabwe Gold (ZiG), United States dollar. The Wikidata label "Zimbabwe ZiG" is displayed as "Zimbabwe Gold (ZiG)" (CUR_LABEL) |
| C4 | France: euro + CFP franc | the CFP franc statement carries P518 "applies to part" (French Polynesia, New Caledonia, Wallis and Futuna) | statements with P518 are dropped when the country has any current statement without P518. All-qualified countries keep theirs (Kingdom of Denmark: krone + Faroese krona, Taiwan) |
| N1 | 1988 Nobel Literature: Grass + Mahfouz | Wikidata's P1346 on the prize item lists Grass twice (point in time 1988, wrong, and 1999). The person-side P166 has Mahfouz 1988 and Grass 1999 only. The builder took the **union** of both directions (r6 query `award_winners`), so 1988 got both | `nobel_r11` keeps the statement source. Literature is won once per person, so a person in several years keeps the year both directions agree on (Grass 1999); the build fails on a repeat laureate it cannot resolve, on a year with a wrong laureate count (shared only 1904, 1917, 1966, 1974; none 1914, 1918, 1935, 1940-1943) |

Also: the 2026 prize (Anne Carson, announced 2026-10-08) now comes from the fetched data; r10 wrote it by hand (`build_r11.py` asserts it instead).

## Diff r10 -> r11 (by class)
| Class | Rows | Detail |
|---|---|---|
| currency, wrong extra | 1 | France: `euro, CFP Franc` -> `euro` (C4) |
| currency, missing | 1 | Zimbabwe: none -> `Zimbabwe Gold (ZiG), United States dollar` (C3) |
| currency, label | 1 | Yemen: `Yemeni Rial` -> `Yemeni rial` (Wikidata fixed the label) |
| Nobel | 0 | 1988 = Mahfouz and 2026 = Carson were already in r10 by hand; the builder now yields them by itself |
| everything else | 0 | 4,233 entities, same order, all other fields identical |
Meta: `build` r10 -> r11, `source` gains the r11 note. The r9 builder (`build_asset.r9.py`) still rebuilds r9 byte-identical (0c167a8f...).
Diff r9 -> builder output (before the r10 hand fixes): Nobel 1988, Nobel 2026, France, Yemen, Zimbabwe, and nothing else.

## Sanity report (`tools/sanity_r11.py`, `data/sanity-r11.out.txt`)
- Currency count per country: 1 currency 189, 2 currencies 8, 0 none, 3 or more none. Two-currency list: Lesotho (loti, rand), Namibia (rand, Namibian dollar), Timor-Leste (centavo coins, USD), Tuvalu and Kiribati (own dollar + AUD), Kingdom of Denmark (krone, Faroese krona), Panama (balboa, USD), Zimbabwe (ZiG, USD): all legitimate. The 147 distinct currency names were read by eye: no crypto, historical or bare-QID name.
- Euro: on 27 countries (the 21 members incl. Bulgaria since 2026-01-01, Kingdom of the Netherlands, plus Monaco, San Marino, Vatican City, Andorra, Montenegro, Kosovo); none of the 27 checked lacks it. El Salvador: USD. Marshall Islands: USD.
- Nobel Literature 1901-2026: 119 prizes, 123 laureates; 115 years with 1 laureate, 4 with 2 (1904, 1917, 1966, 1974); absent exactly 1914, 1918, 1935, 1940-1943; 0 violations; 0 people in more than one year; 1988 Mahfouz, 1999 Grass, 2026 Carson. Cross-check against the Nobel API (api.nobelprize.org/2.1, all 126 literature entries): the 119 awarded years match on every laureate; 5 differences are spelling only (Rudolf Christoph Eucken, Karl Adolph Gjellerup, Pearl S. Buck, Shmuel Yosef Agnon, Odysseas Elytis).
- Builder gates (`data/build-r11.gates.log`): currency statements dropped: 116 ended, 4 by item type, 1 territory-only (P518); dated-only rule fired 1x (Zimbabwe); Nobel uncorroborated year dropped 1x (Grass 1988).

## Tests
- Engine suite on a scratch copy of wt/facts-r9 (b546706c + facts-r9.patch; wt/ itself untouched) with the r11 table: 124 files / 1,589 of 1,590 pass; the single failure is `src/rag/facts.test.ts:245` (`factsAnswer("What currency does Zimbabwe use?")` expected `null`, the r7 abstention). It now answers "Zimbabwe's currency: Zimbabwe Gold (ZiG) and United States dollar." With that one expectation updated (title + line 245 in the copy): 124 / 1,590 green, also with HEALTHGAP=1; `tsc --noEmit` clean. **The engine test needs that one-line update when r11 is adopted** (not applied in wt/).
- FP check (`tools/fpcheck.mts` of facts-r9, 695 public questions, r10 tree vs r11 tree): fire 11 / 11, changed 0 (`../facts-r9/fpcheck-r11.jsonl`).
- FACTS G2 precheck (`tools/facts_check.mts`; v0.1 public 60, chat slices, safety; no blind or held-out data read): fires identical on r10 and r11 (v0.1 8/60, chat-v2 2/64, others 0); `facts-check-r11.jsonl` byte-identical to the r10 run.

## Not fixed / open
- Timor-Leste still shows "East Timor centavo coins" (Wikidata's item; legit coins, odd name).
- The dated-only rule for more than 3 undated currencies is a heuristic scoped to that case (one country today); a future Wikidata change that dates more statements would change the Zimbabwe row, which the sanity script would show.
- Kingdom of the Netherlands keeps a hand list (its statements are all territory-qualified).
- A currency item typed `historical ...` is dropped by name; none of today's 147 kept names is affected (checked by the diff above).
- Nothing sent to the app maintainer, nothing pushed.

## Files
`tools/build_asset.py` (r11), `build_asset.r9.py` (r9 kept), `build_r11.py`, `rebuild_r11.sh`, `fetch_currency_r11.py`, `sanity_r11.py`; data `facts.v1.r11.json`, `labels-r11.json`, `raw/{cur,curitem,nobel}_r11.{rq,json}`, `build-r11.gates.log`, `sanity-r11.out.txt`, `SOURCE.txt` (r11 paragraph); `arms/facts-r9/fpcheck-r11.jsonl`; `arms/facts/facts-check-r11.jsonl`.

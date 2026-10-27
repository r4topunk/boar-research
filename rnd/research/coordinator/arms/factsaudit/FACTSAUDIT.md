# FACTSAUDIT (2026-10-19; criterion 9710b996): facts r7 countries vs the CIA Factbook archive (144d697)

Matched 194/197 (unmatched: Ivory Coast, Palestine, Vatican City). Flags 33 rows: currency 13, capital 8, population 8, area 6 (flags.json).

## Adjudication
- NAMING (19): 13 currency plurals/labels (meticais, emalangeni, British pounds, kronur, koruny, lei, soum, kronor, zlotych, pa'anga, rials); 6 capitals where the Factbook text carries HTML entities (Bras&iacute;lia, Asunci&oacute;n, Bogot&aacute;, San Jos&eacute;, Mal&eacute;, Nuku'alofa).
- REF-STALE-OR-DIFFERENT (9): Bulgaria euro (adopted 2026-01-01; table right); Myanmar Naypyidaw (table right); Equatorial Guinea Ciudad de la Paz vs Malabo (official move, both defensible); Morocco area (Western Sahara), Norway area (Svalbard), Serbia area (Kosovo), Philippines area (300,000 vs 343,448 revised); Moldova population (2024 census without Transnistria); Kuwait 4.3 M and Oman 5.1 M (plausible current figures, Factbook older); Micronesia / Marshall Islands populations (sources disagree; not changed).
- TABLE-WRONG (5): Tunisia population 37,100,000 (2026), Togo 12,400,000 (2026), Bahrain 2,700,000 (2026): bogus round-number statements dated 2026 in the Wikidata snapshot (Tunisia also has 12.4 M and Bahrain 1.6 M on the same date; real: Tunisia 11.97 M 2024 census, Togo 9.5 M 2024, Bahrain 1.57 M 2023), picked by the builder's "latest dated statement" rule. Yemen area 455,503 km2 (standard figure 527,968). Kingdom of Denmark area 2,220,930 km2 answered for "Denmark" (includes Greenland; Denmark proper ~42,950).

## Decision (per criterion)
5 TABLE-WRONG rows -> facts r8 builder override + regression test. Proposed rule for the population class: drop round-to-100,000 statements dated in the snapshot year when an older census-like statement exists, then re-run this audit; Yemen and Denmark areas as explicit overrides. Status: PENDING (deferred 2026-10-19 by r4to's priority switch to small-model prompt research).

## Addendum 14:xx: r8 done
facts r8 (builder build_asset.py r8, r7 kept as build_asset.r7.py; asset sha prefix in handoff/facts-r8-2026-10-19/CHANGES.md): round snapshot-year population rule (21 dropped), AREA_FIX Yemen/Denmark, plus emergency numbers (P2852+P366, 195/197 countries) and an engine "emergency" template (facts-r8.patch, 1,495/1,495 tests, 0 changes on 625 public questions). Audit re-run on r8 (flags-r8.json): 27 flags, all NAMING or REF-STALE-OR-DIFFERENT as adjudicated above; TABLE-WRONG 0.

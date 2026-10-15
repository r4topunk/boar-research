# FACTS data review (facts.v1.json, 1,052 entities): how dirty the table is

Read-only, deterministic. Asset: `wt/facts/src/rag/facts.v1.json` (snapshot 2026-10-06). The rules were run with Python over the JSON. The resolver probes call `factsAnswer()` through tsx. No network, no LLM, no judge. Scripts are in the session scratchpad only (`scan.py`, `words.py`, `final.py`, `probe.mts`).

TL;DR: **all 8 targets output correct values.** No target reads a flagged field. The rest of the table is dirty: **378/1,052 entities (36%) have at least one flag**, and **248** have a flag that should gate data before any wider use. The worst risk is not stale numbers. It is **common-phrase aliases that resolve in lowercase** ("How tall is the White House?" → Casablanca's elevation).

## 1. The 8 v0.1 targets: exact output vs gold

Every answer ends with `Source: Wikidata (CC0), offline table as of 2026-10-06.` (population answers add `; figure dated YYYY`).

| id | prototype output (value part) | gold / precheck | common knowledge | verdict |
|---|---|---|---|---|
| lan-cmp-001 | `Yes. Brazil has more people than Russia: Brazil 214.2 million (2026) vs Russia 146.1 million (2025).` | gold ~203 M (2022 census) / ~146 M; precheck pass (regex 19x–216 million) | Russia 146.1 M (Rosstat 2025) ok. Brazil 214.2 M dated 2026 is an estimate/projection, ~5% above the census figure in gold. UNKNOWN which IBGE series it is | match (verdict + both figures); small judge risk on 214 vs 203 |
| lan-rsn-002 | `No. Burj Khalifa is 828 m tall; Lake Baikal is 1,642 m deep at its deepest point, so its top would be about 814 m below the surface (fully submerged).` | 828 / 1,642 / ~800 m below; pass | exact | match |
| lan-ref-001 | `Nobel Prize in Literature, 2017: Kazuo Ishiguro.` | Ishiguro; pass | exact | match (terse; no bio) |
| lan-ref-004 | `Iceland (Nordic island country in the North Atlantic Ocean): area 103,004 km² (39,770 sq mi).` | ~103,000 km² / ~39,800 sq mi; pass | ok. Some sources give 102,775 km² (UNKNOWN which one the enwiki infobox uses now); both pass | match |
| lan-exp-006 | `Mount Kilimanjaro (mountain massif in Kilimanjaro National Park in Tanzania; type: dormant volcano): elevation 5,895 m (19,341 ft).` | 5,895 m, Tanzania, volcano; pass | values correct | match on values. The "is it a volcano?" part is only implied by `type: dormant volcano`. It omits "highest in Africa" and Kibo/Mawenzi/Shira, so the judge may mark it partial |
| lan-rsn-007 | `Berlin Wall (barrier constructed by the German Democratic Republic, enclosing West Berlin (1961–1989), East Germany): built/founded 13 August 1961; it ended (came down / was dissolved) on 9 November 1989.` | 1961 / 1989; pass | exact | match (awkward nested parentheses and "/was dissolved" wording) |
| lan-ref-005 | `2016 Summer Olympics: held in Rio de Janeiro.` | Rio; pass | exact | match |
| trv-002 | `Brazil: plug types Type C (Europlug) and Type N (IEC 60906-1), mains voltage 127 V / 220 V. Where two voltages are listed, it differs by region: check the socket or ask locally.` | judge-only rubric: N + C, 127/220 V, 60 Hz | correct | match. Misses **60 Hz**: no entity in the table has `hz` (0/1,052), so the Hz branch never runs |

Fields the targets touch that are flagged elsewhere: Russia `inc` 1263, 36 languages and EU/maritime borders; Brazil `bord` includes "European Union"; Iceland `bord` lists Faroe Islands/Greenland/Svalbard although it has no land border. **None of these is read by the 8 targets.**

## 2. Suspicious values (deterministic rules over all 1,052)

| rule | n | entities (examples; full lists from `scan.py`) |
|---|---|---|
| population dated < 2020 | **110** (32 countries, 78 cities) | countries: Netherlands 17.1 M (2013), Thailand (2017), Myanmar (2017), Vietnam (2019), Saudi Arabia 33.0 M (2018), Qatar, Haiti, Paraguay, Mozambique, Niger, Malawi, Kenya, Guatemala, Laos, Armenia, Namibia, Lesotho, Mauritius, Sierra Leone, Solomon Is., Palau, Nauru, Fiji, Suriname, Jamaica, Maldives, South Sudan, Eritrea, Liechtenstein, Guinea-Bissau, São Tomé, Trinidad & Tobago. Cities: Delhi 26.5 M (2016, an agglomeration figure), Mumbai (2018), Dhaka (2017), Karachi (2017), Lahore, Bangkok, Tehran (2016), Nairobi, Kolkata (2011), Apia (2006), Majuro (2008) … |
| population broken | 3 | Ngerulmud **0** (undated) → output "population 0"; Prayagraj, Palikir undated; Greater Rio de Janeiro dated **year 2** → output "11.9 million (2)" |
| inception < 1800, sovereign state | **22** | Russia 1263, Italy **0476**, France 0481, Belarus 0882, Libya 1551, Romania 1330, Philippines 1565, Saudi Arabia 1727, Afghanistan 1709, Thailand 1238, Morocco 0789, Norway 0900, Sweden 0900, Kingdom of Denmark 0965, Hungary 1000, Portugal 1128, Spain 1516, Brunei 1368, Andorra 1278, Monaco 1297, San Marino 0301, **United States 1784-05-12** (should be 1776). At least ~10 are plainly wrong for "when was X founded"; also note Japan 1947, Germany 1949, UK 1801 (≥ 1800, debatable) |
| inception < 1800, city | 118 | mostly real founding dates (London 0047, Kyiv 0482, Baghdad 0762, Istanbul 1453 (conquest, not founding), Madrid 1083, Berlin 1244…). Years < 1000 print with a leading zero ("built/founded 0047"): a formatting bug |
| area > 20,000,000 km² or ≤ 0 | 1 | Taxtakörpü SA (reservoir, Azerbaijan) **8,710,000 km²** (unit error) |
| lake area > 400,000 km² / non-existent lakes | 11 | Lake Agassiz 440,000 (prehistoric), Mega-Chad 360,000, Lake Tauca, Bonneville, Ptolemy, Missoula, Tengger (paleolakes), South Aral Sea (former). They outrank real lakes on size |
| height > 900 m / unbuilt buildings | 3 + 9 | X-Seed 4000 **4,000 m** (concept), Dubai City Tower **2,400 m** (concept), 85 Broad Street **1,313 m** (real ~157 m). Proposed/under construction: Burj Azizi, Dubai One Tower, Akhmat Tower, Bein Arim, Six Senses Residences, Diamond Tower, 80 South Street |
| length outlier (manual) | 1 | Bian River (South Papua) **5,806 km**, ranked as the 4th-longest river (wrong by orders of magnitude) |
| elevation > 9,000 m, depth ≤ 0 or > 2,000 m | 0 | clean (Everest 8,849; max depth Baikal 1,642) |
| country without capital | 1 | Antigua and Barbuda (question falls through, safe) |
| country with ≥ 2 capitals | 7 | South Africa → "The capital of South Africa is Cape Town, Pretoria and Bloemfontein." (grammar); Pakistan lists **Rawalpindi** (wrong); Yemen Sanaa+Aden; Bolivia, Eswatini, Sri Lanka, Palestine |
| languages > 6 / borders incl. EU or sea | 7 / 19 | Russia 36 "official languages", Taiwan 22, Zimbabwe 16; 19 countries "border" the European Union; Iceland borders Svalbard |
| duplicate label/alias → 2 entities | **28 keys, 55 entities** | **Bandung → regency Q10332 (3.7 M, 2017) wins over the city Q10389** (wrong for "population of Bandung"); Taizhou, Yulin, Suzhou, Fuzhou (two cities each; the most populous wins); Madrid (Q2807 wins over a stray "Madrid city" item: ok); Tokyo (ok); Nu River vs Salween (same river twice); "blue river" (Colorado/Yangtze → skip); Niger/Uruguay/Cameroon/Juba (exact label wins: ok) |
| common English word/phrase as label or alias | **58 entities** (74 keys) | see below |

**Common-word labels.** Not present: Male (only "Malé"), Nice, Reading, Split, Bath. Single-word keys (these must be capitalized and must not open the sentence): Turkey, Chad, Jordan, Georgia (country; a US-state question gets Tbilisi), Guinea, Mali, Niger, Wellington, **Michigan/Superior/Huron (aliases of the lakes)**, Cape (→ Cape Town), Swiss, Canton, Assumption (→ Asunción), Revel, Pest, Buda, Hong, Don. **Multi-word aliases have no capitalization check and fire in lowercase.** Examples: white house (Casablanca), west side (Cape Town), the district (Washington DC), garden city / lion city (Singapore), city of light / city of love (Paris), down under (Australia), big/great/black/green/grand/mad river, north fork (Colorado/Pearl/Amur rivers), snow peak (Piton des Neiges), trump tower (the Chicago tower), freedom tower, diamond tower, central plaza, bottle opener, the six, emerald city, eternal city, the second city, mother city, pink city, sky river, jade sea, pit mountain, red/free/communist china.

Probe fires (`probe.mts`, real `factsAnswer()`), all **wrong**:
`How tall is the White House?` → Casablanca elevation 115 m · `How big is Michigan?` → Lake Michigan 57,750 km² · `What's the area of the West Side?` → Cape Town 2,455 km² · `How high is the Cape?` → Cape Town 5 m · `How long is the Green River?` → Colorado River 2,334 km · `How many people live in Garden City?` → Singapore 5.9 M · `How high is Snow Peak?` → Piton des Neiges · `How tall is Trump Tower?` → Chicago tower 423 m · `What is the capital of Georgia?` → Tbilisi (ambiguous) · `When was Italy founded?` → "0476" · `When was the United States founded?` → 12 May 1784 · `How long is the Bian River?` → 5,806 km · `What is the population of the Netherlands?` → 17.1 M (2013).

## 3. Count

| bucket | entities |
|---|---|
| at least one flag (any rule above, including soft ones: city inception, large Chinese prefecture areas, multi-capital, language/border lists) | **378 / 1,052 (36%)** |
| gate-relevant flags (hard value errors 26 + state inception 22 + population < 2020 110 + common-word 58 + duplicates 55, as a union) | **248 (24%)** |
| hard value errors (wrong number or non-existent thing) | 26 |
| by kind (any flag) | city 243, country 89, river 14, lake 10, building 9, mountain 3 |

## 4. Recommendation (gates before the 8-item judge)

1. Drop `inc` for `k=country` and print `inc` only for buildings/events. Format years < 1000 without the leading zero. The 8 targets use `inc` only for the Berlin Wall.
2. Population: require year ≥ 2020, otherwise no fire. Drop pop = 0, undated and year < 1000 rows. This removes 113 rows and touches no target.
3. Drop entities whose description matches `former|paleo|prehistoric|proposed|planned|envisioned|unbuilt|under construction`. Drop any value outside the range table above (Taxtakörpü, 85 Broad Street, Bian River). A duplicate key with two same-label entities → no fire (fixes Bandung).
4. Common words: delete multi-word nickname aliases (keep only official/long names, "Lake X", "X River") or require every non-stopword to be capitalized as written ("Nobel Prize in Literature" still passes). Keep single-word country labels only when capitalized mid-sentence. Remove lake aliases Michigan/Superior/Huron and the city alias Cape.
5. By inspection, none of these gates touches a field or alias that the 8 targets use (Kilimanjaro is a single-word alias). Verify: re-run G2/G3 plus the 13 probe questions above (expect 0 wrong fires) before the judge. Separately, the `hz` field is empty, so trv-002 never gets "60 Hz".

UNKNOWN: Brazil's 214.2 M (2026) series; Iceland area 103,004 vs 102,775 in current Wikipedia; recall of real user phrasings is still unmeasured (no blind trigger set).

# ES strings v2 + country table: independent review (2026-10-03)

TL;DR: I reviewed 27 items. **19 approve, 8 change, 0 reject.** The Spanish wording is good: usted is used consistently, it is neutral Latin-American Spanish, and only one string drifts from the original (the snakebite card, which needs one phrase). Every number matches its official quote: I re-ran `check_official.mjs` (ALL CHECKS PASS) and read the AR, CL, PE, CO and EU snapshots. The serious problems are in the **alias table**, not the strings. This patch now sends every Spanish health answer through `emergencyNumbersLine`, which exposes old matches on common words to Spanish users:
- **"usa"** (the verb "uses") shows **United States: 911**. This already happens in PT: the dev item ed-pt-105 is a live flood in Petrópolis, "minha mae q usa andador".
- **"franca"** shows France's numbers.
- **"china"** shows China's numbers.
- A capitalised **"Turkey"**, **"Chile"** or **"Peru"** still matches the food.
- The new city aliases attach a country's numbers to people who have **already left** it (ed-pt-017: "desde que voltei de bariloche" shows Argentina instead of SAMU 192).

The fixes below were tested in Node: 36/37 cases come out as intended. The one exception is an accepted false negative, which falls back to the generic line.

Input: `esstrings-v2-delta-vs-estask3.patch` sha256 `cc70551f…`, `official-2026-10-03.json`, OFFICIAL.md and the snapshots. Context: `first-aid-cards/REVIEWER-DECISIONS.md` (ES register = usted). Nothing under `blind/` or `rnd/veil/` was read.

## 1. The 9 ES usted strings

| # | Where | Verdict | Reason / exact replacement |
|---|---|---|---|
| 1 | conditionCards `ES_EMERGENCY` | approve | Correct usted form ("llame"). It is identical to #10 (see below). |
| 2 | `emergencyLine(es)` → `ES_EMERGENCY_NEUTRAL` | approve | Same text as #1, with one source of truth. Good. |
| 3 | healthExtract lead ("…llame al número de emergencias local. Lo que dice la fuente (en inglés):") | approve | Correct, natural, and matches EN/PT. |
| 4 | healthExtract no-steps answer ("La fuente offline no trae… " + `emergencyLineFor`) | approve | Correct. When a country is named, the call-to-action verb is replaced by "Emergencia — X: …", which still reads clearly (EN/PT do the same). |
| 5 | `noSafeStepsAnswer` ("Llame ahora… y busque atención médica lo antes posible.") + country line | approve | Both usted imperatives are correct, the meaning matches EN/PT, and appending the country line keeps the "local" instruction. |
| 6 | `noHealthSourceAnswer` | approve | It has no addressed verb before the line, so it is neutral in register. "confiable" is the right Latin-American choice ("fiable" is Spain-only). |
| 7 | `uncitedPreface` ("verifíquela antes de confiar en ella") | approve | The enclitic and the accent are correct, and the meaning matches EN/PT. |
| 8 | Numbers-answer ES tail ("Si una vida está en riesgo, llame de inmediato.") | approve | Correct, and matches "call right away". |
| 9 | Snakebite card ES body | **change** | Drift: EN has "do NOT … put chemicals **on it**", but ES "ni ponga productos químicos" never says where. Replace the last sentence with: `NO use un torniquete apretado, NO corte la herida y NO chupe el veneno ni ponga productos químicos en la herida.` The rest is approved verbatim. Existing tests still pass, since they only match the start and the "NO use un torniquete apretado" phrase. |

No tú forms remain in the changed strings. "Mantenga a la persona quieta y tranquila, sin que se mueva" is slightly redundant, but it is faithful to "keep them still… stop them from moving around at all". Leave it.

## 2. Neutral ES line

| # | Text | Verdict | Reason |
|---|---|---|---|
| 10 | `En una emergencia, llame al número de emergencias local.` | approve | Correct, natural and in usted. Dropping "911 en gran parte de América" removes a wrong number for CO, CL and PE. The cost is that it gives no number at all; this is accepted, because a correct number is shown whenever a country is named. Do not add "112/911 suelen funcionar desde un celular": that claim is not in the verified sources. |

## 3. Per-country lines (EN / PT / ES)

All numbers were checked against the snapshot text, not only against the JSON.

| # | Row | Verdict | Reason / exact replacement |
|---|---|---|---|
| 11 | **AR** | **change** | See the explanation and replacement text below this table. |
| 12 | CO `123 (todas las emergencias)` ×3 | approve | Matches the Función Pública quote "línea única de emergencias Nacional". Leaving out the per-service numbers is right, because they are unverified. |
| 13 | CL `ambulancia (SAMU) 131, bomberos 132, policía (Carabineros) 133` ×3 | approve | Matches chile.gob.cl lines 28–30 exactly. |
| 14 | PE `ambulancia (SAMU) 106, bomberos 116, policía 105` ×3 | approve | Matches MINSA ("PNP: 105, SAMU: 106, bomberos: 116") and the PNP page. |
| 15 | **EU** | **change** | The alias also fires on "Europe/Europa", which includes non-EU countries (UK, Switzerland, Norway, the Balkans), so a user there may read "every EU country" as "not for me". The Your Europe quote already supports more. EN: `European Union: 112 works in every EU country and many others in Europe (police, ambulance, fire).` · PT: `União Europeia: 112 funciona em todos os países da UE e em muitos outros da Europa (polícia, ambulância, bombeiros).` · ES: `Unión Europea: 112 funciona en todos los países de la UE y en muchos otros de Europa (policía, ambulancia, bomberos).` Keep the row last. |
| 16 | ES `España: 112 (todas las emergencias)` ×3 | approve | PAG quote. |
| 17 | MX `México: 911` ×3 | approve | The CDMX government quote is raw-verified. The † federal quote is only extra support. |
| 18 | BR `policía 190, ambulancia (SAMU) 192, bomberos 193` ×3 | approve | gov.br/mcom, 11/09/2026. |
| 19 | PT `112 (policía, ambulancia y bomberos)` ×3 | approve | gov.pt plus the EC "only national emergency number". |

**AR (#11).** Two problems with the proposed `ambulancia 107 (provincia de Buenos Aires: 911; Neuquén: 106), policía 911, bomberos 100`:

1. **Misread risk.** The alias matches "Buenos Aires", and most travellers there are in the *city*. A stressed tourist reads "provincia de Buenos Aires: 911" as "I'm in Buenos Aires, so 911", which is the opposite of what the line means.
2. **Neuquén 106 has a conflict.** The national portal (snapshot line 34) lists 106 as "Emergencia náutica" (Prefectura), while the undated Health Ministry page gives 106 as Neuquén's medical number.

The national portal also states that 911 ("Central de Emergencias Nacional") is the number to call for **an ambulance or the police**. So the shortest correct line puts 911 first and gives 107 as the medical alternative. Every number in it is sourced, and nothing in it is disputed:
- EN: `Argentina: 911 (police or ambulance); ambulance also 107 (City of Buenos Aires and most provinces), fire 100.`
- PT: `Argentina: 911 (polícia ou ambulância); ambulância também 107 (Cidade de Buenos Aires e a maioria das províncias), bombeiros 100.`
- ES: `Argentina: 911 (policía o ambulancia); ambulancia también 107 (Ciudad de Buenos Aires y la mayoría de las provincias), bomberos 100.`

The sources for this text:
- 911 for an ambulance or the police: the national portal.
- 107 in CABA plus 21 of 23 provinces: the Health Ministry, plus the GCBA quote that SAME covers the whole city.
- Buenos Aires province uses 911: this is covered because 911 comes first.

Update the test regex to `/911 \(policía o ambulancia\).*107/`.

## 4. Alias bug fixes

| # | Fix | Verdict | Reason / exact replacement |
|---|---|---|---|
| 20 | Spain `espa[ñn]a` | approve | Tested: it matches "España" and does not match "español" or "espanhol". There is no collision. |
| 21 | Unicode lookarounds `(?<![\p{L}])…(?![\p{L}])` with the `/u` flag | approve | It fixes "Canadá", "Bogotá" and "Perú". OFFICIAL.md worried that `\p{L}` might not work on Hermes. That risk does not apply: shipped `src/rag/*` (dedupe, ptLexicon, passages.pure, poiPack) already uses `\p{L}` with `/u`. Edge case: NFD-decomposed "España" (n + U+0303) does not match. iOS input is NFC, so this goes to the residual list only. |
| 22 | **Turkey** case-sensitive | **change** | Only the lowercase form is fixed. "**Turkey** bone stuck in my throat" (an English sentence starting with a capital) still shows "Turkey: 112" to a US user, and that is the classic Thanksgiving choking query. Add a food lookahead after the closing lookaround: `(?![\p{L}])(?!\s+(?:bones?\|meat\|sandwich(?:es)?\|legs?\|breast\|dinner\|gravy\|stuffing\|burgers?\|bacon\|slices?\|skin\|neck\|wings?\|jerky\|sub\|deli))`. Tests: "Turkey bone stuck in my throat" → null; "Turkey sandwich made him sick" → null; "we are in Turkey", "Turkey, what number?", "Turkey emergency number" → Turkey. |

## 5. Collisions and misreads found in review (not in the coordinator's list)

The patch makes every Spanish health answer call `emergencyNumbersLine`. Before, only the snakebite card did. So the old aliases now reach Spanish users. PT and EN cards already had this exposure.

| # | Problem | Verdict | Exact replacement |
|---|---|---|---|
| 23 | **"usa"** = "uses" (verb) in ES and PT shows **United States: 911**. Tested: "mi papá usa marcapasos y se desmayó", "qué se usa para una quemadura", and dev **ed-pt-105** (live flood, "minha mae q usa andador") all hit. This is the most important fix. | **change (required)** | `names: /(?<![\p{L}])(?:[Uu]nited [Ss]tates\|UNITED STATES\|[Ee]stados [Uu]nidos\|ESTADOS UNIDOS\|EUA\|eua\|USA\|U\.S\.\|EE\.? ?UU\.?)(?![\p{L}])/u`. The flag changes from `iu` to `u`. Lowercase "usa" is dropped, and "EE.UU." / "EE UU" are added. Tests: the three sentences above → null; "Usa insulina y está confundido" → null; "estamos en Estados Unidos", "we're in the USA", "nos EUA", "en EE.UU.", "in the U.S. now" → US. |
| 24 | **"franca"** (PT/ES "frank": "hemorragia franca"; also the city of Franca, SP) shows France's numbers. | **change** | `names: /(?<![\p{L}])(?:france\|frança)(?![\p{L}])/iu`, so the ç is required. A user who types "Franca" for França gets the generic line, which already includes 112 for Europe. Tests: "hemorragia franca" and "moro em Franca" → null; "estou na França", "ESTOU NA FRANÇA", "in France" → France. |
| 25 | **"china"**: EN porcelain ("cut my hand on broken china"), ES pebble ("se me metió una china en el ojo"), and orange in Puerto Rico ("jugo de china"). All of these show China's numbers. | **change** | `names: /(?<![\p{L}])(?:China\|CHINA)(?![\p{L}])/u`. Tests: those three → null; "estoy en China" → China. |
| 26 | Capitalised food: "**Chile** en los ojos qué hago" and "Chile powder in my eyes" show Chile 131/133, which is wrong for a user in Mexico. "**Peru** assado…" shows Peru's numbers to a Brazilian. | **change** | Chile: append `(?!\s+(?:en\s+(?:el\|la\|los\|las\|mi\|mis\|su\|sus\|tu\|tus)\s\|en polvo\|powder\|peppers?\|oil\|flakes\|sauce\|seeds\|habanero\|jalape\|serrano\|verde\|rojo\|piqu\|chipotle\|picante\|molido\|de [áa]rbol))` after the closing lookaround. Peru: append `(?!\s+(?:assado\|recheado\|defumado\|desfiado\|de [Nn]atal))`. Tests: those → null; "estamos en Chile, se cayó", "Chile, qué número", "Santiago de Chile", "no Peru", "estoy en Cusco" → match. Accepted false negative: "Chile en el sur" gets the neutral line. |
| 27 | **Already left the country.** The new city aliases (Bariloche, Buenos Aires, Lisboa, Cusco…) attach that country's line to someone who has returned home. For dev **ed-pt-017**, "desde que voltei de bariloche", a Brazilian gets Argentina's numbers instead of 192/193. In a real case ("volví de Buenos Aires y me duele el pecho") this is the wrong number. | **change** | In `emergencyNumbersLine` only (not in the explicit numbers answer), remove "returned from X" spans before matching: `text.replace(/(?:volv[ií](?:mos)?\|regres[eé]\|regresamos\|voltei\|voltamos\|vim\|viemos\|retornei\|came back\|got back\|returned\|flew back\|back home)\s+(?:de\|del\|da\|do\|das\|dos\|from)\s+(?:la\s+\|el\s+\|a\s+\|o\s+\|the\s+)?\p{L}+(?:\s+\p{L}+)?/giu, "")`. Tests: "to com tosse desde que voltei de bariloche" → null (generic PT line); "just got back from Lisbon, chest pain" → null; "estoy en Buenos Aires, volví de Chile ayer" → Argentina; "returned from the beach in Lisbon" → Portugal. |

Checked and no change needed:
- New aliases: Lisboa/Lisbon, Bariloche, Ushuaia, CDMX, Cancún, Bogotá, Medellín, Cusco, Arequipa, Machu Picchu, Valparaíso, Easter Island, Europa/Europe.
- Lowercase "buenos aires" ("good airs") is rare, and the result is harmless.
- "Columbia" (Missouri, British Columbia) does not match Colombia.
- "cañada" does not match Canadá.
- Leaving out Lima, Santiago, Córdoba, Mendoza, Cartagena, Cali and Porto is right, given the collisions with surnames, foods and other cities.

## Residual risks

1. **Neutral line gives no number.** A Spanish speaker who names no country (or a country outside the table: Bolivia, Ecuador, Uruguay, Costa Rica, Cuba…) gets no number at all. The next table rows should be official-sourced rows for the Spanish-speaking Latin American countries still missing.
2. **AR 911 coverage.** The national portal calls 911 national, but no per-province coverage list was found (UNKNOWN). 107 is kept visible as the alternative. Neuquén's medical number (106 per the Health Ministry, but "náutica" per the national portal) is not shown. A user in Neuquén relies on 911.
3. **PE SAMU 106 regional coverage** is UNKNOWN. In practice, bomberos (116) also send ambulances.
4. **False negatives fall back safely to the generic line:**
   - Lowercase "chile" or "peru".
   - "Lima".
   - "Franca" typed without the cedilla.
   - Lowercase "usa" meaning the US.
   - NFD-decomposed "España".
5. **Capitalised-word residue.** Only listed continuations are excluded. Some will still match:
   - A sentence-initial "Chile …" or "Turkey …" followed by an unlisted word.
   - "India ink" (tested: it shows India 112).
   - An all-caps message ("MI PAPÁ USA MARCAPASOS").
6. **Mentions of a third person's location** ("mi hermano en Medellín") give that place's number. This is correct when the caller dials for them, but it can be wrong if the caller is elsewhere and calls their own local service. Accepted.
7. **Implementation not yet run.** The replacements are validated against the case lists above in isolated Node regexes. They are not yet run in the full 1210-test suite. The coordinator should add the listed cases to `esFixedStrings.test.ts` and re-run the suite and tsc.
8. **This review was done by an AI model**, not a native-speaker human. The Spanish judgements follow general Latin-American usage, and the earlier usted decision stands.

## Appendix: exact regexes to copy

The tables write `|` as `\|` because of Markdown table syntax. Copy the regexes from here instead.

```ts
// #23 United States (flag u only)
/(?<![\p{L}])(?:[Uu]nited [Ss]tates|UNITED STATES|[Ee]stados [Uu]nidos|ESTADOS UNIDOS|EUA|eua|USA|U\.S\.|EE\.? ?UU\.?)(?![\p{L}])/u
// #24 France
/(?<![\p{L}])(?:france|frança)(?![\p{L}])/iu
// #25 China
/(?<![\p{L}])(?:China|CHINA)(?![\p{L}])/u
// #22 Turkey
/(?<![\p{L}])(?:Turkey|TURKEY|T[üu]rkiye|t[üu]rkiye|Turquia|turquia|Turqu[íi]a|turqu[íi]a)(?![\p{L}])(?!\s+(?:bones?|meat|sandwich(?:es)?|legs?|breast|dinner|gravy|stuffing|burgers?|bacon|slices?|skin|neck|wings?|jerky|sub|deli))/u
// #26 Chile
/(?<![\p{L}])(?:Chile|CHILE|Valpara[íi]so|valpara[íi]so|Punta Arenas|San Pedro de Atacama|Isla de Pascua|Easter Island|Ilha de P[áa]scoa)(?![\p{L}])(?!\s+(?:en\s+(?:el|la|los|las|mi|mis|su|sus|tu|tus)\s|en polvo|powder|peppers?|oil|flakes|sauce|seeds|habanero|jalape|serrano|verde|rojo|piqu|chipotle|picante|molido|de [áa]rbol))/u
// #26 Peru
/(?<![\p{L}])(?:Peru|Perú|PERU|PERÚ|perú|Cusco|Cuzco|cusco|cuzco|Machu Picchu|machu picchu|Arequipa|arequipa)(?![\p{L}])(?!\s+(?:assado|recheado|defumado|desfiado|de [Nn]atal))/u
// #27 strip "returned from X" before matching, in emergencyNumbersLine only
const RETURNED_FROM = /(?:volv[ií](?:mos)?|regres[eé]|regresamos|voltei|voltamos|vim|viemos|retornei|came back|got back|returned|flew back|back home)\s+(?:de|del|da|do|das|dos|from)\s+(?:la\s+|el\s+|a\s+|o\s+|the\s+)?\p{L}+(?:\s+\p{L}+)?/giu;
// usage: const hit = COUNTRIES.find((c) => c.names.test(text.replace(RETURNED_FROM, "")));
```

The validation scripts are in the session scratchpad (`rev/p.js`, `rev/t.js`): 37 cases, 1 intended false negative ("Chile en el sur").

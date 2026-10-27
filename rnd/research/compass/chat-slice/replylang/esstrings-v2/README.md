# ES strings v2 + verified country table (Compass, 2026-10-03; Opus reviewer decisions + coordinator)
TL;DR: on top of estask3, the app's fixed Spanish strings move to **usted** (the reviewer's 9 strings). The Spanish emergency line **drops "911 en gran parte de América, 112 en Europa"**: it gives the **country's numbers when the question names a country**, and a neutral "En una emergencia, llame al número de emergencias local." otherwise. The country table gains official-source rows (AR corrected; CO, CL, PE new; EU 112 last) and three alias fixes ("España", Unicode-safe boundaries so "Canadá" matches, Turkey no longer matches the food). Tests 1210/1210 on a fresh archive; tsc clean; no node_modules entry.

| file | sha256 |
|---|---|
| `esstrings-v2-delta-vs-estask3.patch` (review this; 7 files) | `cc70551fee42c85cbfd8ff9b268b96ef742df2df79b637d3a12539a0a79db4cb` |
| `R1es-estask3-esstrings-v2.patch` (full, vs 0cfd4a77) | `26b8a0e7e1ad4adaab9d3598fb9f7feb905a9de0426a56e9a0cf83d323345ea8` |

## What changes
- **Register (usted):**
  - conditionCards `ES_EMERGENCY` (now neutral: "llame…").
  - emergencyLine(es).
  - healthExtract no-steps lead and answer.
  - noSafeStepsAnswer ("Llame… busque…").
  - noHealthSourceAnswer.
  - uncitedPreface ("verifíquela").
  - The emergency-numbers ES tail ("llame de inmediato").
  - The ES snakebite card body (the reviewer's text).
- **Country-aware ES line:** `emergencyLineFor(query, pt, es)` returns the named country's line for a Spanish question, else the neutral line. It is used by the ES condition cards, the health-extract closing line, the line appended to model health answers, the no-steps answer, noSafeStepsAnswer (appended) and noHealthSourceAnswer. **PT and EN emergency lines are unchanged.**
- **Country table** (`compass/exp/emergency-numbers/official-2026-10-03.json` + OFFICIAL.md; every quote an exact substring of a government page snapshot):
  - **AR:** "ambulancia 107 (provincia de Buenos Aires: 911; Neuquén: 106), policía 911, bomberos 100". 107 is not national (argentina.gob.ar + Ministerio de Salud). Aliases + Buenos Aires, Bariloche, Ushuaia.
  - **CO:** 123 (Función Pública). Aliases Colombia, Bogotá, Medellín.
  - **CL:** SAMU 131, bomberos 132, Carabineros 133 (chile.gob.cl). Capitalised "Chile" only, since "chile" = chili.
  - **PE:** SAMU 106, bomberos 116, policía 105 (MINSA, gob.pe). Capitalised Peru/Perú + Cusco, Machu Picchu, Arequipa; "peru" = turkey in PT, and Lima is left out (lime).
  - **ES / MX / BR / PT:** existing numbers re-verified (MX via WebFetch, †). Aliases + España, CDMX, Cancún, Lisboa.
  - **EU** 112 (European Commission, Your Europe): the **last** row, so a named country wins.
- **Alias bugs fixed:** `\b` after an accented letter never matched ("Canadá", "Bogotá", "Perú"), so every alias now uses Unicode letter lookarounds. "turkey" (the food) no longer attaches Turkey's numbers; Turkey only as a country name.

## L0 (`l0_country_lines.txt`): every dev question whose country line or instant numbers answer changes (23)
- **All plausible:**
  - Lisboa → Portugal (also PT/EN questions).
  - Bariloche, Buenos Aires → Argentina.
  - Medellín, Bogotá → Colombia.
  - Cusco, Machu Picchu, Arequipa → Perú.
  - Valparaíso → Chile.
  - "Picos de Europa" → the EU line (correct for Spain).
  - v2-047 Argentina line corrected.
- These lines are appended only on health or emergency answers; a travel question does not show them.
- **One new instant answer:** ed-en-080 "whats the emergency number in peru? … land in cusco" → Peru numbers (the existing numbers route, now able to recognise Peru).

## Safety (v0.8.10)
The neutral ES line still counts as an emergency call for the under-triage rules, so ES cards and fixed answers stay clean. Found while checking, as v0.8.11 candidates: the ES topic gaps "le duele el pecho" (heart attack) and "se le cayó la cara de un lado" (stroke) are not selected by topic.

## Adoption
The patch changes only output strings plus deterministic table lookups (the instant numbers route can now recognise 4 more countries and some new aliases). No prompt or model input changes. It is stacked after the estask3 verdict. **The new wording goes to a fresh Opus reviewer pass via the coordinator:** the 9 ES strings, the neutral line, and the AR/CO/CL/PE/EU lines in EN/PT/ES.

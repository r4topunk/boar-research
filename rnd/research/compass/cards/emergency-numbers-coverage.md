# Emergency numbers on danger cards: the existing table is correct; extend it to 31 more travel destinations from a verified source
TL;DR: every first-aid card and the no-source card end with an emergency line, country-specific when the question names one of the 21 countries in `emergencyNumbers.ts`, else generic ("911 in the US, 112 in Europe"). All 21 entries check out against Wikipedia's raw table (rev. 2026-09-28). Common trip destinations are missing: Peru (the bench's Andes item), Indonesia/Bali, Chile, Colombia, Nepal, Egypt, Morocco, Greece, Switzerland, Singapore and others. 31 verified additions are ready.
Lane: Compass · Status: ready-to-implement (unit-test change, no eval arm needed) · Priority: B
Axes moved: **safety ↑** for travelers in those countries: the card names the right number instead of "112 in Europe / 911 in the US", which is wrong in, e.g., Chile (131 ambulance), Switzerland (144), the UAE (998), Sri Lanka, Cambodia, Laos and Morocco. No quality/latency/resource effect.
Fits BOAR? A data change in a pure module (`src/routing/emergencyNumbers.ts`, `COUNTRIES`). EN + PT lines, offline, < 5 KB.
Evidence:
- **Source:** Wikipedia "List of emergency telephone numbers", raw wikitext, revision 1377218654 (2026-09-28T10:14Z), fetched and parsed row by row (`exp/emergency-numbers/parse.py` → `wiki-numbers.json`, 247 countries). This is the same source the module's own comment cites. Raw wikitext, not a summarizer: a WebFetch summary of the same page garbled Sri Lanka and claimed Australia/NZ were "not on page".
- **Audit of the 21 existing entries** (`audit-existing.md`): all consistent. Small notes:
  - Argentina's "911 (police)": 911 is the general number; police is 101.
  - India: 108 ambulance is widely used and could be added.
- **Proposed additions** (`proposed-additions.json`, sha256 `f224de75…`; EN + PT lines and a `names_regex` per country): Peru, Bolivia, Chile, Colombia, Ecuador, Uruguay, Costa Rica, Cuba, Dominican Republic, Indonesia, Malaysia, Singapore, Cambodia, Laos, Nepal, Sri Lanka, Egypt, Morocco, South Africa, Kenya, Tanzania, Greece, Netherlands, Switzerland, Austria, Ireland, Iceland, Norway, UAE, Israel, Jordan.
  - Lines are generated from the parsed rows.
  - 6 were hand-fixed to include the row's service numbers (e.g. Colombia's general 123, Indonesia 110/118/119, Peru SAMU 106).
  - Aliases include unambiguous tourist places (Bali, Cusco, Machu Picchu, Siem Reap, Kathmandu, Zanzibar, Dubai, Marrakech…). Removed ambiguous ones: "lima" (PT "lime/file"), "amã" (would match PT "ama"), "Cartagena" (also in Spain).
Test: unit tests only.
1. Each added line equals its wiki row; a reviewer rechecks each against the page or the official national source before merge.
2. Negative tests: "suco de lima", "ela ama", "Cartagena (Spain)", "Michael Jordan" don't trigger a country.
3. `emergencyNumbersLine` picks the right country for one danger question per country (EN + PT).
- Bench effect is small. vit-hlt-002 ("Andes") still gets the generic line, because the Andes span several countries. Optional: a mountain-range rule naming several countries, e.g. "Andes → Peru/Bolivia/Chile/Argentina/Ecuador numbers". UNKNOWN whether that helps or confuses.
Cost to try: ~1 h (data + tests). No downloads.

## Body
- **Why it matters beyond the bench:** BOAR is a travel assistant used offline. The emergency line is the one instruction on a danger card that must be right for where the user is. Telling someone in Chile or Switzerland to dial "112 in Europe / 911 in the US" is a safety defect, even if 112 is often redirected on GSM phones. That redirect is listed for some countries in the table, so don't rely on it in general.
- **Limits:**
  - Wikipedia is a secondary source; official national sources should confirm before shipping (reviewer step 1).
  - Numbers change (Thailand's 1669 is proposed for retirement, per the row's own note), so re-run `parse.py` against a new revision when updating.
  - Country detection is by name in the question. The app doesn't know the user's location offline unless the user says it. UNKNOWN whether the app could use the phone's locale or region setting as a fallback (product/privacy decision).

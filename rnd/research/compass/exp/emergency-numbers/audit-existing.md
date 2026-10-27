# Audit of the existing 21 entries (upstream/main src/routing/emergencyNumbers.ts) vs Wikipedia raw wikitext rev 1377218654 (2026-09-28)
All 21 consistent with the page. Notes:
- India: app "112 (all emergencies)" matches; page notes also list police 100, ambulance 108, fire 101 (108 is widely used; optional add).
- Thailand: page notes "Mobile Phones – 112" and Bangkok-only ambulance 1646; app line fine.
- Argentina: page lists 911 as the main number (police 101); the app's "911 (police)" is slightly off: 911 is general. Suggest "Argentina: 911, or ambulance 107, fire 100".
- Turkey: 112 is the unified number; app fine.
- United States / China / South Korea rows use different flag templates (my parser missed them); numbers 911 / 110-120-119 / 112-119 are as the app says.
- Name regexes: "turkey" also matches the bird and "china" the porcelain; harmless on danger cards. "uk" fine.

# CO hazard safety fact: sources (Compass, 2026-10-03; text revised per REVIEWER.md, which re-verified every dagger line)
Every claim in `CO_HAZARD_EN` (engine `src/routing/coHazard.ts`) maps to an official quote below.
- **[S]** = byte snapshot in `snapshots/` (sha256 in SHA256SUMS). The quote is an exact substring of the extracted text.
- **[W†]** = the page returns 403 to our UA (cdc.gov, cpsc.gov HTML). The quote was read through WebFetch on 2026-10-03; there is no byte snapshot. This is the same caveat as the MX number earlier.

| answer text | official quote | source |
|---|---|---|
| "a poison you can't see or smell, and it can kill in minutes" | "Using a generator indoors CAN KILL YOU IN MINUTES. Generator exhaust contains carbon monoxide. This is a poison you cannot see or smell." | CPSC Safety Alert 5123, Portable Generator Hazards [S] |
| generator: "Never run them inside a home, garage, basement, shed … even with the doors or windows open: that is not enough ventilation" | "NEVER use a generator inside homes, garages, crawlspaces, sheds, or similar areas, even when using fans or opening doors and windows for ventilation." · "NEVER use inside a home or garage, EVEN IF doors and windows are open." | CPSC 5123 [S] |
| same, for any gasoline engine; basement | "Never run a generator, pressure washer, or any gasoline-powered engine inside a basement, garage, or other enclosed structure, even if the doors or windows are open, unless the equipment is professionally installed and vented." | CDC, What to Do to Protect Yourself During a Power Outage [W†] |
| charcoal / gas grill, camping stove, lantern: "tent or camper" | "Never use a charcoal grill, hibachi, lantern, or portable camping stove inside a home, tent, or camper." | CDC, Power Outage [W†] |
| | [NHS quote withheld; see url] | NHS, Carbon monoxide poisoning (reviewed 16 Dec 2025) [S] |
| charcoal "even with ventilation" | "Also, never burn charcoal grills indoors, even with ventilation." | CPSC, Generators and Engine-Driven Tools [W†] |
| fuel heater "that isn't made and vented for indoor use"; gas grill | "During a power outage, never use generators, grills, or other gasoline-, propane-, or charcoal-burning devices inside your home, garage, or carport or near doors, windows, or vents." | CDC, PSA toolkit "Avoiding Carbon Monoxide Poisoning" [W†]. **Generalisation:** the CDC line is about power outages. The heater qualifier ("isn't made and vented for indoor use") is Compass's wording, so that vented furnaces and indoor-rated heaters are not called deadly. **Reviewer: please check this.** |
| "at least 20 feet (6 metres) from any door, window or vent" | "Never use a generator, pressure washer, or any gasoline-powered engine inside your home, basement, or garage or less than 20 feet from any window, door, or vent." | CDC, Power Outage [W†]. 6 m is our conversion (20 ft = 6.1 m) |
| "Run a generator outside only" | "Only use OUTSIDE and far away from windows, doors, and vents." | CPSC 5123 [S] |
| car or engine running in a garage | "Never leave the motor running in a vehicle parked in an enclosed or partially enclosed space, such as a garage." | CDC, Power Outage [W†] |
| | [NHS quote withheld; see url] | NHS [S] |
| "never heat a home with a gas oven" | "Never use a gas range or oven to heat a home." | CDC, Power Outage [W†] |
| "Have a battery-powered CO alarm" | "Install battery-operated CO alarms or plug-in CO alarms with battery back-up in your home" | CPSC 5123 [S] |
| symptoms list | "The most common symptoms of CO poisoning are headache, dizziness, weakness, nausea, vomiting, chest pain, and confusion." | CDC, Power Outage [W†] |
| "get everyone out into fresh air and call emergency services right away" | "get to fresh air RIGHT AWAY. DO NOT DELAY." (CPSC 5123 [S]) · "If someone shows signs of having carbon monoxide poisoning, call 911 or your local Poison Control Center at 1-800-222-1222 or consult a health care professional right away." (CDC [W†]) · the reviewed CO card ("get everyone out into fresh air now") | CPSC [S], CDC [W†], conditionCards.v1 `co` (reviewed) |

URLs:
- CPSC Safety Alert 5123: https://www.cpsc.gov/s3fs-public/5123_SafetyAlert_PortableGenerators_102021.pdf
- CPSC, Generators and Engine-Driven Tools: https://www.cpsc.gov/Safety-Education/Safety-Guides/Carbon-Monoxide-Home/Generators-and-Engine-Driven-Tools
- CDC, What to Do to Protect Yourself During a Power Outage: https://www.cdc.gov/natural-disasters/response/what-to-do-protect-yourself-during-a-power-outage.html
- CDC, Avoiding Carbon Monoxide Poisoning: https://www.cdc.gov/natural-disasters/psa-toolkit/avoiding-carbon-monoxide-poisoning.html
- NHS, Carbon monoxide poisoning: https://www.nhs.uk/conditions/carbon-monoxide-poisoning/

Licence: CDC and CPSC texts are US federal government works (public domain). The NHS text contains public sector information licensed under the Open Government Licence v3.0.

Reviewer additions (re-verified quotes in REVIEWER.md §1):
- "carport": CDC PSA toolkit.
- "even with the door open" for engines in a garage: CDC "enclosed or partially enclosed space".
- "gas oven or stove": CDC "gas range or oven".
- Exhaust direction: CPSC 5123 [S], "point the exhaust away from any nearby buildings".
- "tiredness", "passes out", "don't go back inside": NHS [S].
- The heater qualifier now uses the CDC's own wording, "professionally installed and vented".

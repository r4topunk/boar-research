# CO hazard (EN): independent safety-content review (final)
Reviewer: Opus 5.5 (independent; did not read `blind/` or `rnd/veil/`), 2026-10-03.
Reviewed: README.md, SOURCES.md, `co-hazard-v2-delta-vs-ship.patch`, `snapshots/` (sha256 match SHA256SUMS).

## TL;DR
- **Verdict: CHANGE. Do not ship v2 as it stands.** The safety text is sound and well sourced and needs only small edits. The **"No." lead is a blocker**: it inverts the meaning on common phrasings.
  - "Can you die from running a generator in the garage?" gets **"No."**, then the text.
  - "Is it dangerous to run a generator in the garage?" gets **"No."**
  - "Should we move the generator out of the garage?" gets **"No."**
  - "Can I use my camping stove outside the tent?" gets **"No."**
- After the lead rule and trigger exclusions below (C1, C2) and the text edits (T1–T5) are in, this is **approved**, provided the test suite and safety checker v0.9.1 are re-run.

## Method
- I re-fetched the four web sources (dagger lines) on 2026-10-03. Only the page URL was sent, with no personal data.
- I extracted text from the two snapshots locally.
- I ran `isCoHazardQuestion` and `coHazardAnswer`, taken from the v2 patch, on 66 probe questions (with tsx, in the scratchpad).

## 1. Source verification (dagger lines re-checked)
| Claim in text | Re-verified quote | Status |
|---|---|---|
| inside home/basement/garage, "even with doors or windows open" | CDC Power Outage: "Never run a generator, pressure washer, or any gasoline-powered engine inside a basement, garage, or other enclosed structure, even if the doors or windows are open, unless the equipment is professionally installed and vented." | verified verbatim |
| 20 ft from window/door/vent | CDC Power Outage: "…inside your home, basement, or garage or less than 20 feet from any window, door, or vent." CDC PSA toolkit: "Keep generators at least 20 ft. outside door/window." | verified |
| charcoal grill, lantern, camping stove; tent or camper | CDC Power Outage: "Never use a charcoal grill, hibachi, lantern, or portable camping stove inside a home, tent, or camper." | verified |
| car or engine in garage | CDC: "Never leave the motor running in a vehicle parked in an enclosed or partially enclosed space, such as a garage." | verified |
| gas oven for heat | CDC: "Never use a gas range or oven to heat a home." | verified (the source says range **or** oven; see T4) |
| symptoms | CDC: "…headache, dizziness, weakness, nausea, vomiting, chest pain, and confusion." | verified, exact list |
| call right away | CDC: "…call 911 or your local Poison Control Center at 1-800-222-1222 or consult a health care professional right away." | verified |
| battery CO alarm | CDC: "use a battery-powered or battery backup CO detector in your home"; CPSC 5123 [S] | verified |
| gas grill / propane devices | CDC PSA toolkit: "Never use generators, grills, or other gasoline-, propane-, or charcoal-burning devices inside your home, garage, or carport or near doors, windows, or vents." | verified (it also names **carport**; see T2) |
| charcoal even with ventilation | CPSC Generators and Engine-Driven Tools: "Never burn charcoal grills indoors, even with ventilation." | verified |
| generator never inside garage/basement/shed | CPSC page: "Never operate a generator inside a home, garage, basement, crawlspace or shed, or near a window or exterior vent." | verified |
| can't see or smell; kills in minutes | CPSC 5123 [S] | verified in snapshot. Note: "in minutes" is said of generators and is generalised to all devices. Acceptable. |
| NHS: barbecue or camping stove in a tent; engines in a garage | NHS snapshot (reviewed 16 Dec 2025) | verified |

- **No unsupported factual claim was found**, except for the heater qualifier, which is Compass wording (§2).
- **Gaps:** the CPSC generator web page gives **no** distance in feet; the 20 ft figure rests on the CDC alone, which is fine. The CDC Power Outage page **allows kerosene heaters where legal** ("Check with your local fire department to make sure that kerosene heaters are legal in your area"). The answer is therefore *stricter* than the CDC for indoor-rated unvented heaters. That is acceptable for a safety card, but it is a residual risk (R3).

## 2. Heater qualifier: "a fuel heater that isn't made and vented for indoor use"
- Accuracy: it is defensible but under-specified. **Two misreadings are likely under stress:**
  1. "Mine is **made for indoor use**" (Mr. Heater Buddy, indoor-rated kerosene heaters). The reader skims past "and vented" and feels excused.
  2. "Vented" in lay usage means "ventilated": "I cracked a window, so it's vented." The next sentence partly counters this, but the qualifier itself invites it.
- **Change (T1)**: reuse the CDC's own exemption wording ("professionally installed and vented"):
  > `a fuel-burning heater that isn't professionally installed and vented to the outside`
- This keeps furnaces, boilers and direct-vent heaters from being called deadly, and it gives an unvented "indoor-safe" portable heater no way out. It is stricter than the CDC on legal kerosene heaters (R3).

## 3. "20 feet (6 metres)"
- **Approve.** It matches the CDC (two pages). 20 ft = 6.1 m; rounding to 6 m is a 10 cm difference and immaterial.
- The trigger's 19.5 ft threshold treats "6 m" as compliant, which is consistent with the text.
- **Add (T3)**: the exhaust direction from CPSC 5123 [S], "point the exhaust away from any nearby buildings". A generator 20 ft away with its exhaust pointing at an open window is the common failure.

## 4. The opening "No." (BLOCKER)
Probe results with the v2 code (FIRE = the trigger fires; [No.] = the answer starts with "No."):

| Query | v2 | Problem |
|---|---|---|
| Is it safe to run my generator outside 25 ft from the house? | no fire | OK (the README's example) |
| Is it safe to run my generator 6 m from the window? | no fire | OK |
| **Can you die from running a generator in the garage?** | FIRE [No.] | **Inverts: reads as "you can't die"** |
| **Can you get CO poisoning from a camping stove in a tent?** | FIRE [No.] | inverts |
| **Could we get poisoned if we run the generator in the basement?** | FIRE [No.] | inverts |
| **Is it dangerous to run a generator in the garage?** / "Is it bad to…" | FIRE [No.] | inverts (PERMISSION lists `dangerous|bad`) |
| **Should we move the generator out of the garage?** | FIRE [No.] | **may keep it in the garage** |
| Should I be concerned about running the generator in the garage…? / Should I worry… | FIRE [No.] | inverts |
| Can I keep the generator outside instead of in the garage? | FIRE [No.] | says No to the safe option |
| Should I run the generator outside or in the garage? | FIRE [No.] | an either/or question answered "No" |
| Can I use my camping stove outside the tent? / Is it ok to move the camping stove out of the tent? | FIRE [No.] | says No to a safe setup |
| Is it safe to run my generator in the driveway, 25 feet from the garage? | FIRE [No.] | says No to a safe setup: "garage" is a SPACE hit and the ≥ 20 ft exemption only applies inside PLACEMENT |
| Can I run my generator 30 feet from the garage door? | FIRE [No.] | same |
| Is it safe to have a gas water heater in the basement/garage? | FIRE [No.] | says No to a normal installed appliance |
| Can I use my vented gas heater in the living room? | FIRE [No.] | contradicts the text's own qualifier |
| Is it safe to cook on my propane stove in the kitchen? | FIRE [No.] | a propane kitchen range is a normal indoor appliance |

- **Answer to the brief's question:** the README claim holds only narrowly. "25 ft from the house" doesn't fire because no window, door or vent word and no space word appears. **Any mention of "garage" (or "tent") next to a safe distance or an outdoor placement still fires and leads "No."**

### C1 (required): replace `PERMISSION` and the lead logic in `coHazard.ts`
- Lead "No." only on a first-person request to run or use the device, never on risk questions, outdoor or either/or alternatives, installed or vented appliances, or a stated distance ≥ 20 ft. Otherwise there is no lead; the text itself already says "Never…".
- I verified this rule on all 28 lead probes (inversions and safe setups get no lead; the A02 phrasing and the README's 13 positives that start with "Can I/we" or "Is it ok/safe to" keep "No."):
```ts
/** "Can I / Is it ok to <run|use…>": a request to do it. Only then does the answer start with "No." */
const ASK_PERMISSION = re(
  `(?:^|[.?!]\\s+)(?:can|could|may|should|shall) (?:i|we)${E} (?:still |just |safely )?(?:run|use|put|keep|leave|bring|start|operate|light|cook|warm|heat|idle|set up|plug)${E}` +
    `|${B}is it (?:ok|okay|safe|fine|alright|all right) (?:for (?:me|us) )?to${E}`
);
/** Risk questions ("can you die", "is it dangerous"), outdoor or either/or alternatives, installed appliances: a bare "No." would mislead. */
const NO_LEAD_IF = re(
  `${B}(?:dangerous|danger|bad|die|dies|death|kill\\w*|poison\\w*|hurt|harm\\w*|worr\\w*|concern\\w*|risk\\w*|safer|unsafe|outside|outdoors?|out of|yard|driveway|instead|rather|or|not|away|move|moving|vent(?:ed)?|direct-vent|installed|flue|chimney|water heater|furnace|boiler)${E}`
);

export function coHazardAnswer(query: string): string {
  const q = query.replace(/[’‘]/g, "'");
  const lead = ASK_PERMISSION.test(q) && !NO_LEAD_IF.test(q) && !statedFeet(q).some((d) => d >= 19.5) ? "No. " : "";
  return `${lead}${CO_HAZARD_EN}\n\n${CO_HAZARD_SOURCES_EN}\n\n${emergencyNumbersLine(query, false) ?? emergencyLine(false)}`;
}
```
- Add each query in the §4 table to `coHazard.test.ts` as an explicit "no 'No.' lead" case.
- Also add: "Can I run my portable generator in the attached garage if I keep the door open?" → `^No\. Carbon monoxide`.

### C2 (required): trigger exclusions for installed indoor appliances
- In `isCoHazardQuestion`, don't count a **heater** device hit when the query matches:
  `${B}(?:water heaters?|furnaces?|boilers?|direct[- ]vent\w*|vented|flued|installed)${E}`
  - Scope this to heaters only. **Never** apply it to generators, engines, grills or camping stoves: "Can I run the generator in the basement if it's vented?" must still fire.
  - OVEN_HEAT runs earlier and is unaffected.
- Drop `propane|butane` from the `(…) (?:stoves?|burners?)` device alternation when the only SPACE hit is `kitchens?`. The simplest way is to require a camping cue (`camp|camping|backpacking|tent|portable|canister`) for propane/butane stoves.
- What this costs: the "tabletop butane stove for hot pot" borderline item stops firing. That is acceptable; it was labelled borderline.

## 5. Symptoms and action
- The symptom list is the CDC's exact list. It is correct, but it **omits the most dangerous signs for a lay user**: drowsiness and loss of consciousness. CO victims often fall asleep and don't wake up.
  - The NHS lists "tiredness", [NHS quote withheld] and, under call 999, [NHS quote withheld].
- "Get everyone out into fresh air and call emergency services right away" is correct. It matches the CPSC ("get to fresh air RIGHT AWAY") and the CDC ("call 911 … right away").
- It **omits "don't go back in"**. People re-enter to switch off the generator or get belongings.
  - The NHS says: [NHS quote withheld].
- **Change (T5)**, see the final text below.

## 6. Misreading risks (stressed user)
| Risk | Fix |
|---|---|
| "No." read as an answer to "can you die / is it dangerous" | C1 |
| "made … for indoor use" read as covering their indoor-rated heater; "vented" read as "I opened a window" | T1 |
| "My CO alarm is fine, so it's OK" (probe: "…garage with the door open? My CO alarm is fine." fires, correctly) | T5a (optional; it is Compass wording, inferred from CPSC/CDC "never … even if") |
| "gas oven" read literally, so stovetop burners seem fine for heat | T4 (the CDC says "range or oven") |
| A carport seen as "outside" | T2 (the CDC PSA toolkit names carports) |
| 20 ft away but the exhaust points at the house | T3 |

## Element verdicts
| # | Element | Verdict |
|---|---|---|
| L | "No." lead (`PERMISSION`) | **REJECT as is → C1** |
| G | Trigger (`isCoHazardQuestion`) | **CHANGE → C2** (installed appliances, kitchen propane range). Precision and recall otherwise approved per the README's held-out results. |
| T1 | "or a fuel heater that isn't made and vented for indoor use" | **CHANGE** → "or a fuel-burning heater that isn't professionally installed and vented to the outside" |
| T2 | "Never run them inside a home, garage, basement, shed, tent or camper, even with the doors or windows open: that is not enough ventilation." | **CHANGE** → "Never run them inside a home, garage, carport, basement, shed, tent or camper, even with the doors or windows open: that is not enough ventilation." |
| T3 | "Run a generator outside only, at least 20 feet (6 metres) from any door, window or vent." | **CHANGE** → "Run a generator outside only, at least 20 feet (6 metres) from any door, window or vent, with the exhaust pointing away from buildings." |
| T4 | "Never leave a car or other engine running in a garage, and never heat a home with a gas oven." | **CHANGE** → "Never leave a car or other engine running in a garage, even with the door open, and never heat a home with a gas oven or stove." (CDC: "enclosed or partially enclosed"; "range or oven") |
| T5a | "Have a battery-powered CO alarm." | **APPROVE**. Optional: "Have a battery-powered CO alarm, but an alarm does not make it safe to run these indoors." |
| T5 | symptoms + action sentence | **CHANGE** → "If anyone gets a headache, dizziness, weakness, tiredness, nausea, vomiting, chest pain or confusion, or passes out, get everyone out into fresh air right away, call emergency services, and don't go back inside until you're told it's safe." |
| S | Sources line | **CHANGE** (the text now also relies on CPSC 5123 and the CDC PSA toolkit) → "Sources: CDC, Power Outage and Carbon Monoxide guidance; US CPSC, Portable Generator Hazards and Generators and Engine-Driven Tools; NHS, Carbon monoxide poisoning." |
| U | "20 feet (6 metres)" | **APPROVE** |
| E | Emergency line, `safety` flag, receipt label, fast-path order (after acute exclusion, before the model) | **APPROVE** |

### Final CO_HAZARD_EN (all edits applied; T5a optional clause included)
> Carbon monoxide (CO) from a generator, a charcoal or gas grill, a camping stove or lantern, or a fuel-burning heater that isn't professionally installed and vented to the outside is a poison you can't see or smell, and it can kill in minutes. Never run them inside a home, garage, carport, basement, shed, tent or camper, even with the doors or windows open: that is not enough ventilation. Run a generator outside only, at least 20 feet (6 metres) from any door, window or vent, with the exhaust pointing away from buildings. Never leave a car or other engine running in a garage, even with the door open, and never heat a home with a gas oven or stove. Have a battery-powered CO alarm, but an alarm does not make it safe to run these indoors. If anyone gets a headache, dizziness, weakness, tiredness, nausea, vomiting, chest pain or confusion, or passes out, get everyone out into fresh air right away, call emergency services, and don't go back inside until you're told it's safe.

- The existing tests still match: `^No\. Carbon monoxide`, `even with the doors or windows open` and `20 feet \(6 metres\)`.
- **Re-run safety checker v0.9.1.** The co-leave-and-call rule may be sensitive to where "right away" falls.

## Residual risks (after changes)
- **R1 (recall):** known misses are a "generac" in a garage, a grill in a fireplace, a gas cut-off saw in a basement, and **sleeping in a car with the engine running**. That last one is out of the text's scope and has no answer path. These fall through to the model, as before the change.
- **R2 (no lead on some valid asks):** with C1, phrasings like "Power's out, we were wondering if we could…" get the text without "No.". That is safe, because the text says "Never…".
- **R3 (stricter than the CDC):** indoor-rated or legal kerosene and propane heaters get "never inside a home". This is conservative. In a cold outage a user might find it unhelpful, but it is not a harm path.
- **R4 (false fires lose useful answers):** for example, generator carb cleaning in a shed (ch3-013). The cost is lost utility, not safety.
- **R5 (rain):** CPSC 5123 allows running under an open canopy-like structure in the rain. The text doesn't address rain, and rain is a common reason people move generators into garages. Candidate for a later revision.
- **R6:** English only. PT and ES still go to the model for this hazard.
- **R7:** the CDC and CPSC web pages are cited from WebFetch reads (403 to curl) and have no byte snapshots. I re-verified them on 2026-10-03; the CDC Power Outage page was last reviewed 26 Aug 2026.
- **R8:** "in minutes" comes from the CPSC generator alert and is applied to all devices. A slow buildup from a heater is still lethal, so the text does not understate the risk.

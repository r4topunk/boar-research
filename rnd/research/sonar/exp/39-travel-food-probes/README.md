# exp-39: the post author-style travel/food probes (EN, dev, 47 items) + cheap fixes (Sonar, 2026-10-03 night)

- **Probes:** `probes.jsonl`: GPS venues (Berlin/Lisbon/Tokyo fixes), named cities/areas, the travel calculator, travel questions that must not become lists, food knowledge questions.
- **Run:** the real engine (cut2-norv2 + citation fix), detector on, places kit-vexact.
- **Before the fixes:** 5 wrong routes, plus semantic gaps:
  - "veggie" → model; "plant-based" lists every eatery;
  - the driving-distance, flight-distance and "Can I walk … in a week?" phrasings → model;
  - "Why are there so many vegan restaurants…" → a list;
  - "Alfama, Lisbon" → "no data";
  - "open now" ignored.
- **Fixes (`tf1-on-cut2-citefix.patch`):**
  - veggie → vegetarian, plant-based → vegan;
  - why/how-come questions are never venue lists;
  - an "Area, City" fallback to the city, with a note;
  - "open now" → "I can't check opening hours offline…";
  - calculator: driving/walking/flight-distance phrasings; "Can I walk/cycle X to Y in N days/weeks?" with a verdict; flight distance = great circle; no "by land" claim beyond 3,000 km; aliases (New York, NYC, Washington DC, St Petersburg, Kiev, Bombay, Saigon).
- **After:** 47/47 routed as expected (`after.txt`).
  - Remaining gaps: "vegan supermarket" lists restaurants; a landmark ("near the Brandenburg Gate") without GPS asks for the city.
  - v0.1 EN + V-exact replay: 0/65 changes in route, codes, deterministic answers or contexts. Routing tests 521/521 (8 new).

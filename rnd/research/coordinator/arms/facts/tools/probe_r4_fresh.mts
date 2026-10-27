/** r4 fresh precision probes: lowercase homonyms written by the r4 agent before running them (dev only; all must not fire).
 * tsx probe_r4_fresh.mts <tree> */
const tree = process.argv[2];
const { factsAnswer } = await import(`${tree}/src/rag/facts.ts`);
const FRESH = [
  "how tall is paris hilton",
  "how tall is a mont blanc pen",
  "how big is lake wobegon",
  "how many people read the new york times",
  "how big is the new york times building",
  "how big is amazon prime video's library",
  "how big is the georgia tech campus",
  "how tall is the paris las vegas eiffel tower",
  "how long is the nile perch",
  "how big is a cuba libre",
  "what is the capital of new south wales",
  "how big is a london broil",
  "how tall is the kuala lumpur tower",
  "how tall is mount everest base camp",
  "how big is the dead sea scrolls collection",
  "how long is a panama canal transit",
  "how many people live in jersey city",
  "how high is the mexico city metro fare",
  "how long is the rio grande valley",
  "what is the population of new england",
  "how tall is the berlin wall memorial",
  "what language is the japan times written in",
];
let fires = 0;
for (const q of FRESH) { const r = factsAnswer(q); if (r) fires++; console.log(`${r ? "FIRE " + r.template + " " + r.entities.join(",") : "-"} | ${q}${r ? "\n    " + r.text.split("\n")[0] : ""}`); }
console.log(`fresh lowercase-homonym probes: ${fires}/${FRESH.length} fire`);

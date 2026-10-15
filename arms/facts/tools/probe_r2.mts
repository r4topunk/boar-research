/** r2 probes: the 13 DATA-REVIEW.md §2 questions (all wrong under r1) + the reviewer's wider probe list. tsx probe_r2.mts <tree> */
const tree = process.argv[2];
const { factsAnswer } = await import(`${tree}/src/rag/facts.ts`);
const P13 = [
  "How tall is the White House?", "How big is Michigan?", "What's the area of the West Side?", "How high is the Cape?",
  "How long is the Green River?", "How many people live in Garden City?", "How high is Snow Peak?", "How tall is Trump Tower?",
  "What is the capital of Georgia?", "When was Italy founded?", "When was the United States founded?", "How long is the Bian River?",
  "What is the population of the Netherlands?",
];
const MORE = [
  "When was the White House built?", "What is the population of Michigan?", "How tall is Michael Jordan?", "What is the population of Turkey?",
  "How long does a Turkey take to roast?", "How big is Lake Superior?", "What's the population of the district?", "How long is the Red River?",
  "How deep is the Big River?", "Which language is spoken in Swiss schools?", "What is the population of Paris, the city of light?",
  "What is the population of Bandung?", "What is the population of Madrid?", "What is the population of Tokyo?", "When was Russia founded?",
  "How big is Lake Agassiz?", "What is the population of Rio de Janeiro?", "How tall is 85 Broad Street?", "What is the area of Taxtakörpü SA?",
  "Who won? Chad or Jordan?", "Is Chad bigger than Jordan by area?", "What is the capital of Antigua and Barbuda?", "Which countries border Iceland?",
  "What currency does Down Under use?", "What is the population of New York?", "What is the population of Fuzhou?", "What is the population of Suzhou?",
  "When was London founded?", "Is the Caspian Sea deeper than Lake Vostok?", "What is the population of Delhi?", "What is the capital of South Africa?",
  "What languages are spoken in Russia?", "What is the population of Greater Rio de Janeiro?", "What is the population of Ngerulmud?",
  "How tall is X-Seed 4000?", "How tall is Dubai City Tower?", "How big is Lake Michigan?", "How long is the Colorado River?", "What is the capital of Kenya?",
];
for (const [name, qs] of [["P13", P13], ["more", MORE]] as const) {
  console.log(`## ${name}`);
  for (const q of qs) { const r = factsAnswer(q); console.log(`${r ? "FIRE " + r.template + " " + r.entities.join(",") : "-"} | ${q}${r ? "\n    " + r.text.split("\n")[0] : ""}`); }
}

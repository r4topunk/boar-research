/** facts-r9 probes: tsx probe.mts <tree> [file-with-one-question-per-line] */
import { readFileSync } from "node:fs";
const tree = process.argv[2];
const { factsAnswer } = await import(`${tree}/src/rag/facts.ts`);
const QS = process.argv[3] ? readFileSync(process.argv[3], "utf8").split("\n").filter(Boolean) : [
  "What plug do I need in Japan?", "what plug do I need in japan", "Which power adapter do I need for Brazil?", "What is the voltage in the UK?",
  "voltage in India?", "What type of socket does Thailand use?", "Do they drive on the left in Japan?", "Which side of the road do they drive on in Australia?",
  "Do they drive on the right in Sweden?", "What is the country code for Brazil?", "What's the calling code for Germany?", "country code for India",
  "What is the dialing code for Mexico?", "What is the international dialling code for the UK?", "What time zone is Japan in?",
  "What is the area code for London?", "What is the capital of Japan?", "How do I drive to Paris?", "What is the ISO country code for France?",
  "Is it safe to drive in Mexico?", "What frequency is the mains in Japan?",
];
for (const q of QS) { const a = factsAnswer(q); console.log(JSON.stringify(q), "=>", a ? `[${a.template}] ${a.text.split("\n")[0]}` : "null"); }

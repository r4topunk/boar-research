import fs from "node:fs";
import * as A from "<scratch>";
import * as B from "<scratch>";
import * as C from "<scratch>";
const pool = JSON.parse(fs.readFileSync("dev/pool.raw.json","utf8"));
const leak = ["leak/leak-and.requests.jsonl","leak/leak2-and.requests.jsonl"].flatMap(f=>fs.readFileSync(f,"utf8").split("\n").filter(Boolean).map(l=>({turns:[JSON.parse(l).item.question]})));
let pt=0, ch=0;
for (const x of [...pool, ...leak]) { const q = x.turns.at(-1); if (!C.isPortugueseQuestion(q)) continue; pt++;
  const a = A.englishSearchTerms(q), b = B.englishSearchTerms(q);
  if (a !== b) { ch++; console.log(JSON.stringify(a), "->", JSON.stringify(b), "|", q.slice(0,90)); } }
console.log("PT questions", pt, "changed", ch);

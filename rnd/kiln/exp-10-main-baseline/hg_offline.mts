// exp-10 O-main-1 offline sanity (in-sample): which of the 72 questions does the guard's detector flag, and which have a
// health source among main's retrieved passages (from the exp-10 base rows)? Not the measurement.
import { readFileSync } from "node:fs";
import { hasHealthSource, isHealthQuestion } from "../src/routing/healthGuard.ts";
for (const l of readFileSync(process.argv[2], "utf8").trim().split("\n")) {
  const r = JSON.parse(l);
  const h = isHealthQuestion(r.question);
  if (h) console.log(JSON.stringify({ id: r.id, health: h, healthSource: hasHealthSource(r.question, r.sources), sources: r.sources.map((s: any) => s.title) }));
}

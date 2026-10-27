// exp-09 O-H2 offline sanity (in-sample, exploratory): which instant outputs of a run would H2 stop? Not the measurement.
import { readFileSync } from "node:fs";
import { h2Answers } from "../src/routing/h2Answers.ts";
import { namedEntities } from "../src/routing/o2WeakSupport.ts";
import { englishNamesIn } from "../src/rag/ptLexicon.ts";
import * as PLA from "../src/rag/ptLexiconAsset.ts";
const lex = (PLA as any).ptLexicon();
const Q = new Map<string, any>();
for (const f of process.argv.slice(3)) for (const l of readFileSync(f, "utf8").trim().split("\n")) { const q = JSON.parse(l); Q.set(q.id, q); }
for (const l of readFileSync(process.argv[2], "utf8").trim().split("\n")) {
  const r = JSON.parse(l);
  if (!r.instantText || (r.reasonCodes ?? []).includes("grounding:health-extractive") || r.tier === "instant" && !(r.reasonCodes ?? []).includes("instant:final") && !r.instantSources?.length) continue;
  const pt = Q.get(r.id)?.lang === "pt";
  const sides = pt ? englishNamesIn(r.question, lex) : namedEntities(r.question);
  const title = (r.citedTitles?.[0] ?? r.instantSources?.[0] ?? "");
  const d = h2Answers(r.question, sides, title, r.instantText);
  console.log(JSON.stringify({ id: r.id, route: r.tier === "instant" ? "final" : "preview", shape: d.shape, ok: d.ok, sides }));
}

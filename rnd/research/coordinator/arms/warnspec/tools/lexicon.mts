// Reads a JSON array of strings on stdin, prints [{q, health, safety, hg}] using the engine's own classifiers (healthgap tree).
import { readFileSync } from "node:fs";
const root = process.argv[2];
const ctx = await import(`${root}/src/routing/context.ts`);
const qs: string[] = JSON.parse(readFileSync(0, "utf8"));
console.log(JSON.stringify(qs.map((q) => ({ q, health: ctx.isHealthQuestion(q), safety: ctx.isSafetyQuery(q) }))));

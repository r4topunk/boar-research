// NUMGUARD step 1: numericGuard / numericIntent / health lexicon over the public sets (0 LLM calls).
// Usage (from the numguard tree): be/node_modules/tsx/dist/cli.mjs <this> <tree> <name=questions.jsonl>...
import { readFileSync } from "node:fs";
import { join } from "node:path";
const [tree, ...sets] = process.argv.slice(2);
const NG: any = await import(join(tree, "src/routing/numguard.ts"));
const CX: any = await import(join(tree, "src/routing/context.ts"));
for (const s of sets) {
  const [name, path] = s.split("=");
  const qs = readFileSync(path, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
  const g: string[] = [], intentHealth: string[] = [];
  for (const q of qs) {
    const pt = CX.isPortugueseQuestion(q.question);
    if (NG.numericGuard(q.question, pt)) g.push(q.id);
    else if (NG.numericIntent(q.question) && NG.numguardHealthLexicon(q.question)) intentHealth.push(q.id);
  }
  console.log(`${name}: n=${qs.length} guard=${g.length} [${g.join(" ")}] | numeric-intent blocked by health lexicon=${intentHealth.length} [${intentHealth.join(" ")}]`);
}

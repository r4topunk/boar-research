import fs from "node:fs";
const S = await import(process.argv[2] + "/src/routing/firstAidCards.ts");
const C = await import(process.argv[2] + "/src/routing/conditionCards.ts");
const jl = (p: string) => fs.readFileSync(p, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const E = "<workspace>/rnd/research/sonar/exp/30-learned-detector/data/";
const last = (d: any) => { const t = d.turns.at(-1); return typeof t === "string" ? t : d.turns.filter((x: any) => x.role === "user").at(-1).text; };
for (const f of ["cards-en.jsonl", "aligned-en.jsonl", "synth-en.jsonl"]) for (const d of jl(E + f)) {
  const q = last(d); if (!/snake|viper|rattler|rattlesnake|cobra|adder|mamba|copperhead|cottonmouth|krait/i.test(q)) continue;
  const fa = S.isSnakebiteFirstAid(q), cc = C.conversationCondition(q, []).condition;
  console.log(`${fa ? "FA" : "--"} ${String(cc).padEnd(10)} ${d.card ?? d.cat ?? ""} | ${q.slice(0, 150)}`);
}

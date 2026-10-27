// exp-37 (Sonar): verification kit for a symptomatic-CO card delta. Compares tree A (health13) and tree B (the delta):
// probes, cards-en (labelled CO recall + wrong CO cards), and NEW CO-card fires on EN dev pools (each listed for review).
// usage: tsx cokit.mts <treeA> <treeB>
import fs from "node:fs";
const [ta, tb] = process.argv.slice(2);
const A = await import(`${ta}/src/routing/conditionCards.ts`), B = await import(`${tb}/src/routing/conditionCards.ts`);
const X = new URL(".", import.meta.url).pathname, E = "<workspace>/rnd/research/sonar/exp/30-learned-detector/data/";
const jl = (p: string) => fs.readFileSync(p, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const card = (M: any, turns: string[]) => {
  const q = turns[turns.length - 1], prev = turns.slice(0, -1);
  const c = M.conversationCondition(q, prev).condition;
  if (!c || c === "MULTI") return "generic";
  return M.conditionCardText(c, q, "en") ? c : "generic";
};
for (const [n, M] of [["A", A], ["B", B]] as const) {
  const P = [...jl(X + "probes.jsonl"), ...(fs.existsSync(X + "probes2.jsonl") ? jl(X + "probes2.jsonl") : [])]; const bad = P.filter((p: any) => card(M, p.turns) !== p.expect).map((p: any) => `${p.id}->${card(M, p.turns)}`);
  console.log(`${n} probes ${P.length - bad.length}/${P.length} ${bad.join(" ")}`);
}
const C = jl(E + "cards-en.jsonl");
for (const [n, M] of [["A", A], ["B", B]] as const) {
  const co = C.filter((d: any) => d.card === "co"); const hit = co.filter((d: any) => card(M, d.turns) === "co").length;
  const wrong = C.filter((d: any) => d.card !== "co" && card(M, d.turns) === "co");
  console.log(`${n} cards-en: CO recall ${hit}/${co.length}; wrong CO card on non-CO items ${wrong.length} ${wrong.map((d: any) => d.id + ":" + d.card).join(" ")}`);
}
const pools: [string, any[]][] = [
  ["aligned-en", jl(E + "aligned-en.jsonl")],
  ["terse-live-en", jl(E + "terse-live.jsonl").filter((d: any) => d.lang === "en")],
  ["compass-dev-en", jl("<workspace>/rnd/research/compass/exp/emergency-dev/dev.jsonl").filter((d: any) => (d.lang ?? "en") === "en").map((d: any) => ({ ...d, turns: d.turns.filter((t: any) => t.role === "user").map((t: any) => t.text) }))],
];
for (const [name, P] of pools) {
  const fresh = P.filter((d: any) => card(B, d.turns) === "co" && card(A, d.turns) !== "co");
  const gone = P.filter((d: any) => card(A, d.turns) === "co" && card(B, d.turns) !== "co");
  console.log(`${name} (${P.length}): NEW CO cards ${fresh.length}, lost ${gone.length}`);
  for (const d of [...fresh, ...gone]) console.log(`   ${fresh.includes(d) ? "+" : "-"} ${d.id} | ${d.turns.join(" / ").slice(0, 150)}`);
}

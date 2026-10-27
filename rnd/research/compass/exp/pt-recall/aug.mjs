// For PT questions: append the app's own English anchors (ptQuery.englishSearchTerms + ptLexicon.englishNamesIn,
// both copied read-only from upstream/main 0cfd4a77) to the text the classifier embeds.
import fs from "fs";
const { englishSearchTerms } = await import("./ptQuery.ts");
const { englishNamesIn } = await import("./ptLexicon.ts");
const lex = JSON.parse(fs.readFileSync("../pt-en.json", "utf8"));
const PTW = new Set("o a os as de do da dos das que é e um uma em no na para pra com não nao qual quais quantos quantas como eu meu minha está esta estou faço faco devo foi".split(" "));
const isPT = (q) => { const w = q.toLowerCase().match(/[\p{L}]+/gu) ?? []; return w.filter((x) => PTW.has(x)).length >= 2 || /[ãõç]/.test(q); };
const rows = [
  ...fs.readFileSync("../health-embed/eval.jsonl", "utf8").trim().split("\n").map(JSON.parse).map((r) => ({ id: r.id, q: r.q, label: r.label, set: "eval" })),
  ...fs.readFileSync("pt-mirror.jsonl", "utf8").trim().split("\n").map(JSON.parse).map((r) => ({ ...r, label: "danger", set: "mirror" })),
];
for (const r of rows) {
  r.pt = isPT(r.q);
  const terms = r.pt ? englishSearchTerms(r.q) : null;
  const names = r.pt ? englishNamesIn(r.q, lex) : [];
  r.en = [terms, ...names].filter(Boolean).join(" ");
  r.aug = r.en ? `${r.q} (${r.en})` : r.q;
}
fs.writeFileSync("aug.jsonl", rows.map((r) => JSON.stringify(r)).join("\n") + "\n");
const s = (f) => rows.filter(f).length;
console.log("rows", rows.length, "pt", s((r) => r.pt), "pt with anchors", s((r) => r.pt && r.en));
for (const r of rows.filter((r) => r.pt && r.label === "danger")) console.log(r.id, "|", r.en);

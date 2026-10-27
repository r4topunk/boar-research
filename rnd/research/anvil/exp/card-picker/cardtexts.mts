// Render the card each picker would show (engine conditionCardText, item language) -> JSONL for the v0.8.8 scorer.
// npx tsx cardtexts.mts <tree> <out.jsonl> <picks.jsonl>:<field> [...]
import fs from "node:fs";
const [tree, outPath, ...specs] = process.argv.slice(2);
const K = await import(`${tree}/src/routing/conditionCards.ts`);
const items = new Map(fs.readFileSync("<workspace>/rnd/research/compass/exp/emergency-dev/dev.jsonl", "utf8").trim().split("\n").map((l) => JSON.parse(l)).map((r: any) => [r.id, r]));
const out: string[] = [];
for (const s of specs) {
  const [file, field] = s.split(":");
  for (const r of fs.readFileSync(file, "utf8").trim().split("\n").map((l) => JSON.parse(l))) {
    const key = r[field]; if (!key || key === "NONE") continue;
    const it: any = items.get(r.id); const msg = it.turns.filter((t: any) => t.role === "user").at(-1).text;
    const text = K.conditionCardText(key, msg, it.lang);
    out.push(JSON.stringify({ picker: `${file.split("/").pop()}:${field}`, id: r.id, key, lang: it.lang, text }));
  }
}
fs.writeFileSync(outPath, out.join("\n") + "\n");
console.log(out.length, "card answers");

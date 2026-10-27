// CITEFIX: apply the engine normaliser to stored traces. Usage: node apply.mjs <normalizer.ts> <strictK|real> <traces.jsonl>...
// Prints per file: rows, rows whose final text or full stored stream would change, and the changed rows (JSON lines with -v).
import fs from "node:fs";
const [, , mod, mode, ...files] = process.argv;
const { normalizeCitations } = await import(mod);
const W = "Not found in this phone's offline library. From the model's memory, may be wrong:";
for (const f of files) {
  let n = 0, full = 0; const changed = [];
  for (const line of fs.readFileSync(f, "utf8").split("\n")) {
    if (!line.trim()) continue; const d = JSON.parse(line); n++;
    const ev = d.events || []; const src = ev.filter((e) => e.type === "sources");
    const k = mode === "strict" ? 99 : (src.length ? src[src.length - 1].sources.length : 0);
    const isFull = !ev.some((e) => e.kind === "tokens-elided"); full += isFull;
    const stream = ev.filter((e) => e.type === "token").map((e) => e.text || "").join("");
    const t = d.answer.text || ""; const body = t.startsWith(W) ? t.slice(W.length + 1) : t;
    const a = normalizeCitations(body, k), b = normalizeCitations(stream, k);
    if (a.mapped || b.mapped) changed.push({ itemId: d.itemId, k, finalMapped: a.mapped, streamMapped: b.mapped, after: a.text });
  }
  console.log(`${f.split("/").pop()}\trows ${n}\tfull streams ${full}\tchanged ${changed.length}\t${changed.map((c) => c.itemId).join(",")}`);
  if (process.env.V) for (const c of changed) console.log(JSON.stringify(c));
}

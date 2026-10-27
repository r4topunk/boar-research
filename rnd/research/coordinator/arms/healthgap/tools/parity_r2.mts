// HEALTHGAP-r2 TS parity (rule v1.2 §5b, 0 LLM): the tree's src/routing/healthGap.ts classify on every input of
// runs/r2-parity-inputs.jsonl (tools/scan_r2.py). Run: cd <tree> && npx tsx <this> <inputs.jsonl> <out.jsonl>
import * as fs from "node:fs";
const HG: any = await import("<workspace>/kiln-local/be-0cfd4a77-cut7-healthgap/src/routing/healthGap.ts");
const [inp, out] = process.argv.slice(2);
const rows = fs.readFileSync(inp, "utf8").split("\n").filter((l) => l.trim()).map((l) => JSON.parse(l));
const res = rows.map((r) => { const c = HG.classify(r.q, r.turns); return JSON.stringify({ k: r.k, ts: c ? { cls: c.cls, event: c.event, prev: c.prevTurn } : null }); });
fs.writeFileSync(out, res.join("\n") + "\n"); console.log(rows.length, "rows");

// Keep one row per (queryId, order): mode first|last by createdAt. Used once for TV s42 Haiku after two concurrent L1 invocations wrote the same shards.
import fs from "node:fs"; const [inp, out, mode] = process.argv.slice(2);
const r = fs.readFileSync(inp, "utf8").split("\n").filter(Boolean).map(JSON.parse).sort((a, b) => a.createdAt.localeCompare(b.createdAt));
const by = new Map(); for (const x of r) { const k = x.queryId + "|" + x.order; if (mode === "last" || !by.has(k)) by.set(k, x); }
fs.writeFileSync(out, [...by.values()].map((x) => JSON.stringify(x)).join("\n") + "\n"); console.log(`in ${r.length} out ${by.size} mode ${mode}`);

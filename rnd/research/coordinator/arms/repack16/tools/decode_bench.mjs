// REPACK16 decode bench (0 LLM): replay a run's logged miss sequence (pack, block id) through fzstd 0.1.1 (the engine's decoder),
// blocks preloaded from the same pack files; median of 5 reps; prints ms per search.
// usage: node decode_bench.mjs <blocklog.jsonl> <packId=file.sqlite> ...
import fs from "node:fs"; import { createRequire } from "node:module"; import { DatabaseSync } from "node:sqlite";
const require = createRequire("<workspace>/rnd/research/coordinator/arms/zstd-bench/"); const { decompress } = require("fzstd");
const [log, ...maps] = process.argv.slice(2); const files = Object.fromEntries(maps.map(m => m.split("=")));
const L = fs.readFileSync(log, "utf8").trim().split("\n").map(l => JSON.parse(l));
const miss = L.filter(x => x.e === "miss"); const searches = L.filter(x => x.e === "search").length;
const need = {}; for (const x of miss) (need[x.pack.replace("local-", "")] ??= new Set()).add(x.id);
const Z = {}; for (const [p, ids] of Object.entries(need)) { const d = new DatabaseSync(files[p], { readOnly: true }); const g = d.prepare("SELECT zdata FROM blocks WHERE id = ?");
  Z[p] = new Map([...ids].map(i => [i, new Uint8Array(g.get(i).zdata)])); d.close(); }
const seq = miss.map(x => Z[x.pack.replace("local-", "")].get(x.id)); const reps = [];
for (let r = 0; r < 6; r++) { const t = process.hrtime.bigint(); let s = 0; for (const z of seq) s += decompress(z).length; const ms = Number(process.hrtime.bigint() - t) / 1e6; if (r) reps.push(ms); }
reps.sort((a, b) => a - b); const med = reps[2];
console.log(JSON.stringify({ log: log.split("/").pop(), misses: seq.length, searches, total_ms: +med.toFixed(1), ms_per_search: +(med / searches).toFixed(2), ms_per_miss: +(med / seq.length).toFixed(4) }));

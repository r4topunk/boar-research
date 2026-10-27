// Share of items whose order-averaged usefulness (and correctness) >= 3 on the 1-5 rubric; pooled over the given judgment files. Aggregates only.
import fs from "node:fs";
const { combineOrders } = await import("<workspace>/boar-eval/scorers/vendor/eval-lib/judge-core.mjs");
const [idf, label, ...files] = process.argv.slice(2);
const want = new Set(fs.readFileSync(idf, "utf8").split("\n").filter(Boolean));
let n = 0, u3 = 0, c3 = 0, c4 = 0;
for (const f of files) { const by = {};
  for (const l of fs.readFileSync(f, "utf8").split("\n").filter(Boolean)) { const r = JSON.parse(l); if (r.ok && want.has(r.queryId)) (by[r.queryId] ??= {})[r.order] = r.mapped; }
  for (const o of Object.values(by)) { if (!o.boarA || !o.boarB) continue; const c = combineOrders(o.boarA, o.boarB); n++; if (c.boar.usefulness >= 3) u3++; if (c.boar.correctness >= 3) c3++; if (c.boar.correctness >= 4) c4++; } }
console.log(JSON.stringify({ label, n, useful_ge3: +(u3 / n).toFixed(3), correct_ge3: +(c3 / n).toFixed(3), correct_ge4: +(c4 / n).toFixed(3) }));

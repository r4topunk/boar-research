// exp-29 L0 identity of the instant knob: in every non-blind trace (no v1-fresh/blind/veil paths, no v1-/v02- ids), the instant
// snippets emitted (event type "instant") and finals, split by: translated (retrieve:pt-en-terms / match:pt-en-names), health
// (arm's isHealthQuestion), other (unchanged by the arm). Off-topic = bge-m3(question, snippet) < 0.10.
import fs from "node:fs"; import { execSync } from "node:child_process";
import { isHealthQuestion } from "<scratch>";
const { getLlama } = await import("<workspace>/wt/eval/eval/node_modules/node-llama-cpp/dist/index.js");
const files = execSync(`grep -rl --include='*.traces.jsonl' '"type":"instant"\\|"type": "instant"' <workspace>/boar-eval/runs <workspace>/rnd 2>/dev/null || true`).toString().split("\n").filter((f) => f && !/v1-fresh|\/blind\/|\/veil\//.test(f));
const U = new Map<string, any>(); let n = 0;
for (const f of files) for (const l of fs.readFileSync(f, "utf8").split("\n").filter(Boolean)) {
  let t: any; try { t = JSON.parse(l); } catch { continue; } if (/^(v1-|v02-)/.test(t.itemId)) continue;
  const ev = t.events?.find((e: any) => e.type === "instant"); if (!ev) continue; n++;
  const rc: string[] = t.route.reasonCodes; const snippet = ev.snippet?.text ?? ev.text ?? "";
  const cls = isHealthQuestion(t.question) ? "health" : rc.includes("retrieve:pt-en-terms") || rc.includes("match:pt-en-names") ? "translated" : "other";
  const k = `${t.question}\u0000${snippet}`; const u = U.get(k) ?? { q: t.question, snippet, cls, final: false, runs: 0 }; u.final ||= rc.includes("instant:final"); u.runs++; U.set(k, u);
}
const rr = await (await (await getLlama({ logLevel: "error" })).loadModel({ modelPath: "<workspace>/shared-models/bge-reranker-v2-m3-q4km.gguf" })).createRankingContext({ contextSize: 1024, threads: 4 });
const rows = [...U.values()]; for (const r of rows) r.s = await rr.rank(r.q, r.snippet.slice(0, 2400));
console.log(`files ${files.length}; traces with an instant snippet ${n}; unique (question, snippet) ${rows.length}`);
for (const c of ["translated", "health", "other"]) { const x = rows.filter((r) => r.cls === c);
  console.log(`${c.padEnd(10)} unique ${x.length} (finals ${x.filter((r) => r.final).length}) | off-topic <0.10: ${x.filter((r) => r.s < 0.1).length} (finals ${x.filter((r) => r.s < 0.1 && r.final).length}) | on-topic >=0.5: ${x.filter((r) => r.s >= 0.5).length} -> arm: ${c === "other" ? "unchanged" : "suppressed"}`); }
fs.writeFileSync("instid.json", JSON.stringify(rows.map((r) => ({ ...r, s: +r.s.toFixed(3) })), null, 1));
for (const r of rows.filter((r) => r.cls !== "other" && r.s >= 0.5)) console.log(`  on-topic lost (${r.cls}${r.final ? ", final" : ""}) ${r.s.toFixed(2)}: ${r.q.slice(0, 70)} || ${r.snippet.slice(0, 90).replace(/\s+/g, " ")}`);

// LENGTHSHARE part 2: condense each ok reference to <= 80 words with Opus (claude -p, no tools). Resumable; prints counts only.
// node cap_refs.mjs <src refs.jsonl> <out dir> [--limit N]
import fs from "node:fs"; import path from "node:path"; import { createHash } from "node:crypto";
import { runClaude, isRateLimited, sleep } from "<workspace>/wt/eval/eval/scripts/lib/claude-cli.mjs";
const [src, outDir] = process.argv.slice(2); const limit = Number(process.argv.includes("--limit") ? process.argv[process.argv.indexOf("--limit") + 1] : 0);
const SYS = fs.readFileSync(new URL("./cap80.system.md", import.meta.url), "utf8");
const sha = (p) => createHash("sha256").update(fs.readFileSync(p)).digest("hex");
fs.mkdirSync(outDir, { recursive: true }); const out = path.join(outDir, "refs.jsonl");
const done = new Set(fs.existsSync(out) ? fs.readFileSync(out, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l).id) : []);
const rows = fs.readFileSync(src, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const words = (t) => t.trim().split(/\s+/).filter(Boolean).length;
const truncate = (t) => { const s = t.split(/(?<=[.!?])\s+/); let acc = ""; for (const x of s) { if (words(acc + " " + x) > 80) break; acc = (acc + " " + x).trim(); } return acc || t.split(/\s+/).slice(0, 80).join(" "); };
let n = 0, capped = 0, truncated = 0, failed = 0;
for (const r of rows) {
  if (!r.ok || done.has(r.id)) continue; if (limit && n >= limit) break; n++;
  const prompt = `QUESTION:\n${r.question}\n\nREFERENCE:\n${r.answer}`;
  let text = null, attempts = 0;
  while (attempts < 2) { attempts++;
    const res = await runClaude({ prompt, systemPrompt: SYS, model: "opus", tools: [], timeoutMs: 120_000 });
    if (!res.ok) { if (isRateLimited(res)) { console.error("rate limited; stopping (resume later)"); process.exit(3); } console.error(`fail ${r.id} attempt ${attempts}: ${String(res.error).slice(0, 120)}`); await sleep(5000); continue; }
    const t = String(res.json.result ?? "").trim(); if (t && words(t) <= 95) { text = t; break; } text = t; }
  if (!text) { failed++; continue; }
  let flag = false; if (words(text) > 80) { text = truncate(text); flag = true; truncated++; }
  capped++;
  fs.appendFileSync(out, JSON.stringify({ ...r, answer: text, words: words(text), truncated: flag, origAnswerWords: words(r.answer), cappedBy: "cap80.system.md", cappedAt: new Date().toISOString(), sourceRefsSha256: sha(src) }) + "\n");
  if (capped % 10 === 0) console.error(`progress ${capped}/${n}`);
}
const all = fs.readFileSync(out, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const w = all.map((r) => r.words).sort((a, b) => a - b);
fs.writeFileSync(path.join(outDir, "MANIFEST.json"), JSON.stringify({ jsonl_sha256: sha(out), source_refs_sha256: sha(src), rows: all.length, words_p10_p50_p90_max: [w[Math.floor(w.length * .1)], w[Math.floor(w.length * .5)], w[Math.floor(w.length * .9)], w[w.length - 1]], truncated: all.filter((r) => r.truncated).length, system_prompt_sha256: createHash("sha256").update(SYS).digest("hex") }, null, 1));
console.log(JSON.stringify({ processed: n, capped, truncated, failed, total_rows: all.length, words_p50: w[Math.floor(w.length * .5)], max: w[w.length - 1] }));

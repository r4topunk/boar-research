// D2Q generation driver (criterion 83b06185): one chat request per chunk to the 4B llama-server on :8131 (-np 4), temp 0.7, top_p 0.8,
// top_k 20, seed 42, max_tokens 160, 4 in flight. Resumable. usage: node gen.mjs <chunks.jsonl> <out.jsonl> [limit]
import { readFileSync, existsSync, appendFileSync } from "node:fs";
const [inF, out, lim] = process.argv.slice(2);
let list = readFileSync(inF, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
if (lim) list = list.slice(0, Number(lim));
const done = new Set(existsSync(out) ? readFileSync(out, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l).chunk) : []);
const todo = list.filter((t) => !done.has(t.chunk));
console.error(`todo ${todo.length} of ${list.length}`);
let next = 0, n = 0; const t0 = Date.now();
async function worker() {
  while (next < todo.length) {
    const t = todo[next++]; const ts = Date.now(); let res, err = null;
    for (let attempt = 0; attempt < 3; attempt++) {
      try {
        const r = await fetch("http://127.0.0.1:8131/v1/chat/completions", { method: "POST", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ messages: [{ role: "user", content: t.prompt }], temperature: 0.7, top_p: 0.8, top_k: 20, max_tokens: 160, seed: 42, stream: false }) });
        res = await r.json(); err = null; break;
      } catch (e) { err = String(e); await new Promise((s) => setTimeout(s, 2000)); }
    }
    const ch = res?.choices?.[0];
    appendFileSync(out, JSON.stringify({ chunk: t.chunk, kind: t.kind, title: t.title, section: t.section, raw: ch?.message?.content ?? null, finish: ch?.finish_reason ?? null, usage: res?.usage ?? null, ms: Date.now() - ts, err }) + "\n");
    n++; if (n % 50 === 0) console.error(`${new Date().toISOString().slice(11, 19)} ${n}/${todo.length} ${((Date.now() - t0) / 1000 / n).toFixed(2)} s/chunk`);
  }
}
await Promise.all([worker(), worker(), worker(), worker()]);
console.error(`DONE ${n} in ${((Date.now() - t0) / 1000).toFixed(0)} s = ${((Date.now() - t0) / 1000 / Math.max(n, 1)).toFixed(2)} s/chunk`);

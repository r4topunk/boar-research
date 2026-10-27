// MICROD2Q generation driver (criterion sha 5988da96...): for each target chunk, the NEXT-RETRIEVAL-ARMS §2 prompt to the
// 4B llama-server (:8097, -np 4), temp 0.7, top_p 0.9, max 160 tokens, seed 42; 4 requests in flight. Chunk text exactly as
// the engine's WikiPack.hit(): article text (zstd block, utf-8) .slice(start, end).trim(); section = sectionAt (heading path).
// Resumable: skips (pack, chunk) already in <out>. usage: node gen.mjs <list.json: [{pack, chunk}]> <out.jsonl>
import { DatabaseSync } from "node:sqlite";
import { zstdDecompressSync } from "node:zlib";
import { readFileSync, existsSync, appendFileSync } from "node:fs";
const ROOT = "<workspace>";
const PATHS = { "boar-crypto": `${ROOT}/shared-data/crypto/boar-crypto.sqlite`, "boar-wikivoyage-en": `${ROOT}/shared-data/packs/boar-wikivoyage-en.sqlite` };
const pub = (p) => PATHS[p] ?? [`${ROOT}/shared-data/packs/wave2/${p}.sqlite`, `${ROOT}/shared-data/packs/wave1/${p}.sqlite`].find(existsSync);
const HEADING = /^(#{1,6})\s+(.*)$/gm;
export function sectionAt(text, start) { // = wikiPack.ts sectionAt
  const path = [];
  for (const m of text.matchAll(HEADING)) {
    const at = m.index; if (at >= start) break;
    const level = m[1].length, lineEnd = at + m[0].length, titleAt = lineEnd - m[2].length;
    path.length = level - 1; path[level - 1] = (lineEnd > start ? text.slice(titleAt, start) : m[2]).trim();
  }
  return path.slice(1).filter(Boolean).join(" > ");
}
const dbs = {}, blocks = new Map(), dec = new TextDecoder("utf-8");
export function chunkInfo(pack, id) {
  if (!dbs[pack]) { const db = new DatabaseSync(pub(pack), { readOnly: true }); dbs[pack] = { db, name: db.prepare("SELECT value FROM meta WHERE key='name'").get()?.value ?? pack,
    ch: db.prepare("SELECT article_id, start, end FROM chunks WHERE id=?"), ar: db.prepare("SELECT title, block_id, off, len FROM articles WHERE id=?"), bl: db.prepare("SELECT zdata FROM blocks WHERE id=?") }; }
  const P = dbs[pack]; const c = P.ch.get(id); const a = P.ar.get(c.article_id);
  const key = `${pack}:${a.block_id}`; if (!blocks.has(key)) { if (blocks.size > 64) blocks.clear(); blocks.set(key, zstdDecompressSync(P.bl.get(a.block_id).zdata)); }
  const text = dec.decode(blocks.get(key).subarray(a.off, a.off + a.len));
  return { packName: P.name, title: a.title, article_id: c.article_id, section: sectionAt(text, c.start), text: text.slice(c.start, c.end).trim() };
}
export const prompt = (x) => `Passage from "${x.packName}", article "${x.title}", section "${x.section}":\n<<<${x.text}>>>\nWrite 5 different questions a person might type that THIS passage answers. Use everyday words a non-expert would use, including plain synonyms of any technical term. Each question must be answerable from the passage alone. One question per line, no numbering, at most 20 words each.`;
if (import.meta.url === `file://${process.argv[1]}`) {
  const [listF, out] = process.argv.slice(2);
  const list = JSON.parse(readFileSync(listF, "utf8"));
  const done = new Set(existsSync(out) ? readFileSync(out, "utf8").split("\n").filter(Boolean).map((l) => { const o = JSON.parse(l); return `${o.pack}:${o.chunk}`; }) : []);
  const todo = list.filter((t) => !done.has(`${t.pack}:${t.chunk}`));
  console.error(`todo ${todo.length} of ${list.length}`);
  let next = 0, n = 0; const t0 = Date.now();
  async function worker() {
    while (next < todo.length) {
      const t = todo[next++]; const x = chunkInfo(t.pack, t.chunk); const ts = Date.now();
      let res, err = null;
      for (let attempt = 0; attempt < 3; attempt++) {
        try {
          const r = await fetch("http://127.0.0.1:8097/v1/chat/completions", { method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ messages: [{ role: "user", content: prompt(x) }], temperature: 0.7, top_p: 0.9, max_tokens: 160, seed: 42, stream: false }) });
          res = await r.json(); err = null; break;
        } catch (e) { err = String(e); }
      }
      const ch = res?.choices?.[0];
      appendFileSync(out, JSON.stringify({ pack: t.pack, chunk: t.chunk, article_id: x.article_id, title: x.title, section: x.section, chars: x.text.length,
        raw: ch?.message?.content ?? null, finish: ch?.finish_reason ?? null, usage: res?.usage ?? null, ms: Date.now() - ts, err }) + "\n");
      n++; if (n % 50 === 0) console.error(`${new Date().toISOString().slice(11, 19)} ${n}/${todo.length} ${((Date.now() - t0) / 1000 / n).toFixed(2)} s/chunk`);
    }
  }
  await Promise.all([worker(), worker(), worker(), worker()]);
  console.error(`DONE ${n} in ${((Date.now() - t0) / 1000).toFixed(0)} s = ${((Date.now() - t0) / 1000 / Math.max(n, 1)).toFixed(2)} s/chunk`);
}

import fs from "node:fs"; import zlib from "node:zlib"; import { DatabaseSync } from "node:sqlite";
import * as C from "<scratch>";
const items = JSON.parse(fs.readFileSync("gate-items.json", "utf8"));
const db = new DatabaseSync("<scratch>", { readOnly: true });
const arts = new Map<string, any>();
for (const a of db.prepare("SELECT id,title,block_id,off,len FROM articles").all() as any[]) {
  const z = (db.prepare("SELECT zdata FROM blocks WHERE id=?").get(a.block_id) as any).zdata;
  arts.set(a.title, { ...a, text: zlib.zstdDecompressSync(z).subarray(a.off, a.off + a.len).toString("utf8") });
}
const tk = (s: string) => new Set(C.tokenizeTerms ? (C as any).tokenizeTerms(s) : []);
for (const [id, it] of Object.entries<any>(items)) {
  const q = it.q; const years = (C as any).yearsIn?.(q); const proper = (C as any).properNounTerms?.(q);
  console.log("==", id, JSON.stringify(q), "years", years, "proper", proper, "terms", [...tk(q)]);
  for (const t of it.titles) {
    const a = arts.get(t); if (!a) { console.log("  missing", t); continue; }
    const ch = db.prepare("SELECT start,end FROM chunks WHERE article_id=? ORDER BY start").all(a.id) as any[];
    let pass = 0, yearFail = 0, properFail = 0, best = 0;
    for (const c of ch) {
      const body = a.text.slice(c.start, c.end);
      const chunk: any = { title: t, body, text: body, source: "Wikipedia — x", chunkId: c.start };
      const ok = C.onTopic(q, chunk); pass += ok ? 1 : 0;
      const text = t + " " + body;
      if (years && !years.every((y: any) => (C as any).yearsIn(text).includes(y))) yearFail++;
      const cov = (C as any).termCoverage ? (C as any).termCoverage(q, text) : NaN; if (cov > best) best = cov;
    }
    console.log("  ", t, "chunks", ch.length, "onTopic pass", pass, "| year-rule fails", yearFail, "| best term coverage", best.toFixed(2));
  }
}

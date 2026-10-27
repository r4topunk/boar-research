import { DatabaseSync } from "node:sqlite";
const ex = new DatabaseSync("../../data/leadvecs-top100k.sqlite", { readOnly: true });
const sm = new DatabaseSync("<workspace>/shared-data/packs/boar-wiki-sample.sqlite", { readOnly: true });
const i8 = (b: Uint8Array) => new Int8Array(b.buffer, b.byteOffset, b.byteLength);
const cos = (a: ArrayLike<number>, b: ArrayLike<number>) => { let d = 0, x = 0, y = 0; for (let i = 0; i < a.length; i++) { d += a[i] * b[i]; x += a[i] * a[i]; y += b[i] * b[i]; } return d / Math.sqrt(x * y); };
const all = ex.prepare("SELECT l.article_id id, a.title, a.views, l.vec FROM lead_vecs l JOIN articles a ON a.id = l.article_id ORDER BY l.article_id").all() as any[];
const byTitle = new Map(all.map((r, i) => [r.title, i]));
for (const t of ["Dengue fever", "Iceland", "War 2 (film)", "Wednesday (TV series)", "Deaths in 2025"]) {
  const s = sm.prepare("SELECT l.vec FROM articles a JOIN lead_vecs l ON l.article_id = a.id WHERE a.title = ?").get(t) as any;
  if (!s) { console.log(t, "not in sample"); continue; }
  let best = -1, bi = -1; for (let i = 0; i < all.length; i++) { const c = cos(i8(s.vec), i8(all[i].vec)); if (c > best) { best = c; bi = i; } }
  const own = byTitle.get(t)!;
  console.log(`${t}: own idx ${own} (id ${all[own].id}) | best-matching export vector idx ${bi} (id ${all[bi].id}, title "${all[bi].title}") cos ${best.toFixed(3)} | idx shift ${bi - own}`);
}

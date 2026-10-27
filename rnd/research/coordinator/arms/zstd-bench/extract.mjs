// Extract 200 real compressed blocks (stratified, seeded) from the A-union packs.
import { DatabaseSync } from "node:sqlite";
import fs from "node:fs";
const dir = "<workspace>/shared-data/packs/persona-a-union/";
const packs = ["crypto","factbook","firstaid-en","medlineplus-en","visa-en","wikivoyage-en"].map(n=>`boar-${n}.sqlite`);
let seed = 42; const rnd = () => (seed = (seed * 1664525 + 1013904223) >>> 0) / 2**32;
const out = []; const per = [34,33,33,33,33,34];
packs.forEach((p, i) => {
  const db = new DatabaseSync(dir + p, { readOnly: true });
  const ids = db.prepare("SELECT id FROM blocks").all().map(r => r.id);
  for (let k = ids.length - 1; k > 0; k--) { const j = Math.floor(rnd() * (k + 1)); [ids[k], ids[j]] = [ids[j], ids[k]]; }
  for (const id of ids.slice(0, per[i])) {
    const r = db.prepare("SELECT zdata FROM blocks WHERE id=?").get(id);
    out.push({ pack: p, id, z: Buffer.from(r.zdata) });
  }
});
fs.mkdirSync("blocks", { recursive: true });
const idx = out.map(b => ({ pack: b.pack, id: b.id, n: b.z.length }));
fs.writeFileSync("blocks/index.json", JSON.stringify(idx));
fs.writeFileSync("blocks/blocks.bin", Buffer.concat(out.map(b => b.z)));
console.log(out.length, "blocks", out.reduce((a,b)=>a+b.z.length,0), "compressed bytes");

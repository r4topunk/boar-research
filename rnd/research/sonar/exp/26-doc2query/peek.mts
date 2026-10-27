import fs from "node:fs"; import { BASE, Q } from "./lib.mts"; import { original } from "./fts.mts"; import { DatabaseSync } from "node:sqlite";
const o = JSON.parse(fs.readFileSync("oracle.json", "utf8"));
for (const [id, key] of [["vit-trv-004", "wv"], ["lan-exp-006", "wv"], ["vit-cry-005", "cr"], ["lan-cmp-003", "wv"], ["vit-hlt-003", "wv"]]) {
  const db = new DatabaseSync(BASE[key], { readOnly: true }); const x = original(db, o.pick[id][key]);
  console.log(`== ${id} ${key}: ${Q[id].question}\n   pick: ${x.title} § ${x.section}\n   ${x.body.replace(/\s+/g, " ").slice(0, 500)}\n`);
}

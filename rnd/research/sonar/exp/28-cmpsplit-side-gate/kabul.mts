import { BASE, openPack } from "./lib.mts";
const { raw, pack } = await openPack(BASE.wv);
const id = (raw.prepare("SELECT id FROM articles WHERE title = 'Kabul'").get() as any).id;
const a = await (pack as any).article(id);
for (const m of a.text.matchAll(/[^.\n]*\bchok\w*[^.\n]*/gi)) console.log("-", m[0].trim().slice(0, 200));

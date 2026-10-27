import { BASE, openPack } from "./lib.mts";
const { pack } = await openPack(BASE.cr);
const r = await pack.searchDetailed("Privacy Pools", { k: 12, titles: ["Privacy Pools"] });
r.hits.forEach((h: any, i: number) => console.log(i, h.title, "§", h.section, h.via, h.score, /association set/i.test(h.text) ? "[KEY]" : ""));
const c = await pack.bm25Candidates(await pack.stems("Privacy Pools"), 200);
for (const [i, x] of c.entries()) { const h = await (pack as any).materialize(x); if (/association set/i.test(h.text)) console.log("bm25 rank", i, h.title, "§", h.section); }

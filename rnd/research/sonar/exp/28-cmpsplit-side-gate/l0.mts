// exp-28 L0: cmpsplit v2.1 side search on kit A packs (Wikivoyage + crypto; the 4B profile's kit, no vital5) and a
// per-side relaxation: among a side's hits, a passage whose own text names the side counts as that side (v2.1 needs the
// TITLE to name it). Per comparison item: sides, each side's hits, v2.1 pick vs relaxed pick, key in pick.
import { BASE, openPack, Q, keyHit } from "./lib.mts";
import { comparisonSides, bestForSide, titleNamesSide, SIDE_K } from "<workspace>/wt/cmpsplit-v21/src/rag/comparison.ts";
const IDS = (process.argv[2] ?? "vit-cry-005,lan-cmp-001,lan-cmp-002,lan-cmp-003,lan-cmp-004,lan-cmp-005,vit-hum-002,vit-sci-002").split(",");
const packs = await Promise.all(Object.entries(BASE).map(async ([k, p]) => ({ k, ...(await openPack(p)) })));
const label = (k: string, h: any) => (k === "wv" ? `Wikivoyage: ${h.title}` : h.title);
const words = (s: string) => s.toLowerCase().match(/[\p{L}\p{N}]+/gu) ?? [];
// side named in the passage text: every side word (singular/plural-insensitive prefix) occurs in title + text
const textNamesSide = (text: string, side: string) => { const t = ` ${words(text).join(" ")} `; return words(side).every((w) => t.includes(` ${w.replace(/s$/, "")}`)); };
let v21Key = 0, relKey = 0, changed = 0;
for (const id of IDS) {
  const q = Q[id]; const sides = comparisonSides(q.question);
  console.log(`\n=== ${id}: ${q.question}\n  sides ${JSON.stringify(sides)}  key ${JSON.stringify(q.grading.must_any ?? q.grading.must_k)}`);
  if (!sides) continue;
  for (const side of sides) {
    const hits: any[] = [];
    for (const { k, pack } of packs) for (const h of (await pack.searchDetailed(side, { k: SIDE_K, titles: [side] })).hits) hits.push({ ...h, title: label(k, h), body: `${h.section ? h.section + ": " : ""}${h.text}` });
    hits.sort((a, b) => b.score - a.score); // UNKNOWN: engine fusion order across sources; score order as proxy
    const v21 = bestForSide(hits, side);
    const rel = hits.find((c) => titleNamesSide(c.title, side) && !/^Wikivoyage:/.test(c.title)) ?? hits.find((c) => titleNamesSide(c.title, side)) ?? hits.find((c) => textNamesSide(`${c.title} ${c.body}`, side)) ?? hits[0];
    const kh = (c: any) => !!c && keyHit(`${c.title}\n${c.body}`, q.grading);
    v21Key += +kh(v21); relKey += +kh(rel); if (v21 !== rel) changed++;
    console.log(`  side "${side}": hits ${hits.map((h) => `${h.title}§${(h.section || "").slice(0, 25)}${textNamesSide(h.title + " " + h.body, side) ? "*" : ""}${kh(h) ? "[KEY]" : ""}`).join(" | ")}`);
    console.log(`    v2.1 pick: ${v21?.title}§${v21?.section} key ${kh(v21)} pinned ${!!v21 && titleNamesSide(v21.title, side)} | relaxed pick: ${rel?.title}§${rel?.section} key ${kh(rel)} pinned ${!!rel && (titleNamesSide(rel.title, side) || textNamesSide(rel.title + " " + rel.body, side))}`);
  }
}
console.log(`\nside picks with key: v2.1 ${v21Key}, relaxed ${relKey}; picks changed ${changed}`);

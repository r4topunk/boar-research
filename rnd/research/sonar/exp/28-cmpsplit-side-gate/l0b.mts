// exp-28 L0b: side passage re-pick within each side's top 12 (both packs): (P) first hit whose text has the exact side
// phrase (0 cost), (R) best bge-m3 score vs the full question (12 pairs per side). Fact check per side by hand-written
// passage facts (the lan-cmp keys are answer-shape regexes, not passage keys).
import { BASE, openPack, Q } from "./lib.mts";
import { comparisonSides } from "<workspace>/wt/cmpsplit-v21/src/rag/comparison.ts";
const { getLlama } = await import("<workspace>/wt/eval/eval/node_modules/node-llama-cpp/dist/index.js");
const rr = await (await (await getLlama({ logLevel: "error" })).loadModel({ modelPath: "<workspace>/shared-models/bge-reranker-v2-m3-q4km.gguf" })).createRankingContext({ contextSize: 1024, threads: 4 });
// passage fact per side (what a correct answer needs from that side's passage); null = no fact defined
const FACT: Record<string, RegExp> = {
  "Privacy Pools": /association set|exclude|proof of innocence/i, "Tornado Cash": /mix|tumbler|sanction/i,
  "polar bear": /largest (living )?(bear|land carnivore)|\b(350|400|450|500|600|700|800)\s*(-|–|to)?\s*\d*\s*kg/i, "grizzly bear": /grizzl[^.]{0,80}(kg|lb|pound)|\b(180|200|250|270|300|360)\s*(kg|lb)/i,
  "adult male moose": /moose[^.]{0,100}(kg|lb|pound)/i, "adult male American bison": /bison[^.]{0,100}(kg|lb|pound|tonne|ton)/i,
  "saltwater crocodile": /(saltwater|estuarine)[^.]{0,120}(largest|metre|meter|\d\s*m\b|feet|ft)/i, "Nile crocodile": /nile crocodile[^.]{0,120}(metre|meter|\d\s*m\b|feet|ft|kg)/i,
  "Brazil": /\b21\d\s*million|\b20\d\s*million/i, "Russia": /\b14[0-6]\s*million/i, "Japan": /\b3[2-4]\d\b[^.]{0,30}(km|per)|densit/i, "Germany": /\b2[2-4]\d\b[^.]{0,30}(km|per)|densit/i,
  "Mozi": /mozi|mohis/i, "Confucian": /confuci[^.]{0,80}(love|family|filial|kin)/i,
};
const packs = await Promise.all(Object.entries(BASE).map(async ([k, p]) => ({ k, ...(await openPack(p)) })));
const tally = { v21: 0, P: 0, R: 0, n: 0 };
for (const id of ["vit-cry-005", "lan-cmp-001", "lan-cmp-002", "lan-cmp-004", "lan-cmp-005", "vit-hum-002", "vit-sci-002"]) {
  const q = Q[id].question; const sides = comparisonSides(q)!;
  console.log(`\n=== ${id}: ${q}`);
  for (const side of sides) {
    const hits: any[] = [];
    for (const { k, pack } of packs) for (const h of (await pack.searchDetailed(side, { k: 12, titles: [side] })).hits) hits.push({ ...h, title: k === "wv" ? `Wikivoyage: ${h.title}` : h.title });
    hits.sort((a, b) => b.score - a.score);
    const top3 = hits.slice(0, 3); const f = (h: any) => !!h && FACT[side].test(`${h.title}\n${h.section}: ${h.text}`);
    const phrase = new RegExp(`\\b${side.replace(/s$/, "")}`, "i");
    const P = hits.find((h) => phrase.test(h.text)) ?? hits[0];
    let R = hits[0], best = -1; for (const h of hits) { const s = await rr.rank(q, `${h.title}\n${h.section ? h.section + ": " : ""}${h.text}`.slice(0, 2400)); if (s > best) [best, R] = [s, h]; }
    const anyFact = hits.filter(f).length;
    tally.n++; tally.v21 += +top3.some(f); tally.P += +f(P); tally.R += +f(R);
    console.log(`  "${side}": fact in v2.1 top3 ${top3.some(f)} | P ${P?.title}§${(P?.section ?? "").slice(0, 30)} fact ${f(P)} | R ${R?.title}§${(R?.section ?? "").slice(0, 30)} (${best.toFixed(3)}) fact ${f(R)} | fact anywhere in top12 ${anyFact}`);
  }
}
console.log(`\nsides ${tally.n}: fact reachable via v2.1 top-3 ${tally.v21}; phrase re-pick ${tally.P}; reranker re-pick ${tally.R}`);

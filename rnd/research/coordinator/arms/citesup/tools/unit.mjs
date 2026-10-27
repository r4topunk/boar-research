// CITESUP unit check: checkCitations(text, sources) of the patched tree == the base tree's on fixed cases; rescue keeps exactly the listed k.
// Usage: tsx unit.mjs <base tree> <patched tree>
const [base, cand] = process.argv.slice(2);
const B = await import(`${base}/src/routing/citations.ts`);
const C = await import(`${cand}/src/routing/citations.ts`);
const S = (title, body) => ({ chunkId: title, title, body, score: 1 });
const src = [S("Bison", "The American bison is the largest land mammal in North America. Males weigh up to 1,000 kg."),
             S("Podgorica", "Podgorica is the capital of Montenegro. Montenegro uses the euro although it is not in the eurozone."),
             S("Walipini", "A walipini is an underground greenhouse.")];
const cases = ["Bison males can reach about a tonne in weight [1]. Montenegro's capital city is Podgorica [2].",
  "Earth's axial tilt causes the seasons [3]. The bison is the largest land mammal in North America [1].",
  "The country pays with the euro despite being outside the euro area [2]. See [9].",
  "Bison are big. They live on prairies and eat grass [1]\n\nMore text [2] here.",
  "No citation here.", "A [1][2] B [1, 3]. Weighing a ton, the heaviest American mammal is the bison [1]."];
let bad = 0;
for (const t of cases) {
  const b = B.checkCitations(t, src), c = C.checkCitations(t, src);
  if (JSON.stringify(b) !== JSON.stringify(c)) { bad++; console.log("DIFF", t, b, c); }
  const u = C.unsupportedCitations(t, src);
  const all = C.checkCitations(t, src, new Set(u.map((x) => x.k)));
  const kept = (t.match(/\[\d+\]/g) ?? []).length - all.removed.length;
  console.log(JSON.stringify(t.slice(0, 60)), "| lexical removed", JSON.stringify(c.removed), "| unsupported", JSON.stringify(u.map((x) => [x.k, x.n, x.sentence.slice(0, 40)])), "| rescue-all removed", JSON.stringify(all.removed), "kept", kept);
}
console.log(bad ? `FAIL ${bad} cases differ` : "OK default checkCitations identical to base on all cases");

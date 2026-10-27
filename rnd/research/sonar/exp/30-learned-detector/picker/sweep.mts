// Sweep pickCard thresholds on the eval set (Compass emergency-dev positives + card probes) with a learned picker's probs.
// usage: tsx sweep.mts <tree> <eval_probs.json>
import fs from "node:fs";
const [tree, probsPath] = process.argv.slice(2);
const K = await import(`${tree}/src/routing/conditionCards.ts`);
const X = new URL("..", import.meta.url).pathname;
const ev = JSON.parse(fs.readFileSync(X + "picker/eval.json", "utf8")); const pr = JSON.parse(fs.readFileSync(probsPath, "utf8"));
const lang = (s: string) => (/[¿¡ñ]|\b(qué|está|mi|hijo|hace|tiene)\b/i.test(s) ? "es" : /[ãõç]|\b(não|você|meu|minha|está|tá)\b/i.test(s) ? "pt" : "en");
function score(fn: (x: any, p: any) => string | null) {
  const r: Record<string, number[]> = { compass: [0, 0, 0], probe: [0, 0, 0] }; const wrongs: string[] = [];
  ev.forEach((x: any, i: number) => {
    let c = fn(x, pr[i]); if (c && !K.conditionCardText(c, x.turns.at(-1), lang(x.turns.join(" ")))) c = null;
    const k = r[x.src]; if (!c) k[2]++; else if (c === x.y) k[0]++; else { k[1]++; wrongs.push(`${x.id} ${x.y}->${c}`); }
  });
  return `Compass right ${r.compass[0]} WRONG ${r.compass[1]} generic ${r.compass[2]} | probes right ${r.probe[0]} wrong ${r.probe[1]} generic ${r.probe[2]} | ${wrongs.slice(0, 14).join("; ")}`;
}
const top = (p: any) => { const e = Object.entries(p.probs as Record<string, number>).sort((a, b) => b[1] - a[1])[0]; return { key: e[0], p: e[1] }; };
console.log("regex only     :", score((x) => K.pickCard(x.turns.at(-1), x.turns.slice(0, -1), null).condition));
console.log("learned only.5 :", score((x, p) => { const t = top(p); return t.key !== "NONE" && t.p >= 0.5 ? t.key : null; }));
for (const [a, o] of [[0.5, 0.8], [0.6, 0.9], [0.7, 0.9], [0.8, 0.95], [0.9, 0.99], [1.01, 1.01]])
  console.log(`pick add ${a} over ${o}:`, score((x, p) => K.pickCard(x.turns.at(-1), x.turns.slice(0, -1), top(p), a, o).condition));

for (const t of [0.8, 0.9, 0.95, 0.98])
  console.log(`regex first, learned only if none, >= ${t}:`, score((x, p) => { const lex = K.pickCard(x.turns.at(-1), x.turns.slice(0, -1), null).condition; if (lex) return lex; const r = K.pickCard(x.turns.at(-1), x.turns.slice(0, -1), top(p), t, 1.01); return r.condition; }));

// L0 (no model) for the precedence-only arm: isPortugueseQuestion (main/B6) vs isPortugueseQuery (arm) on every dev
// question we have. Expected: changes ONLY on Spanish questions (PT → not PT); 0 on Portuguese and English.
// Usage: tsx l0_precedence.mts <engine tree>
import { readFileSync } from "node:fs";
const tree = process.argv[2];
const { isPortugueseQuestion, isPortugueseQuery } = await import(`${tree}/src/routing/context.ts`);
const R = "<workspace>/rnd/research", E = "<workspace>/boar-eval";
const L = (p: string) => readFileSync(p, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const qs: { id: string; lang: string; q: string }[] = [];
for (const f of ["slice.v0.jsonl", "v1-fresh/slice.v1.jsonl", "v2-fresh/slice.v2.jsonl"])
  for (const it of L(`${R}/compass/chat-slice/${f}`)) qs.push({ id: it.id, lang: it.lang, q: it.turns[it.turns.length - 1].text });
for (const f of ["questions.public.jsonl", "safety/track.v0.3.jsonl"]) for (const it of L(`${E}/bench/v0.1/${f}`)) qs.push({ id: it.id, lang: it.lang, q: it.question });
for (const r of L(`${R}/sonar/exp/29-instant-offtopic/requests2-and.jsonl`)) qs.push({ id: r.item.id, lang: r.item.lang, q: r.item.question });
const n: Record<string, number> = {}, ch: Record<string, string[]> = {}, ptLeft: string[] = [];
for (const { id, lang, q } of qs) {
  n[lang] = (n[lang] ?? 0) + 1;
  const a = isPortugueseQuestion(q), b = isPortugueseQuery(q);
  if (a !== b) (ch[lang] ??= []).push(`${id}(${a}→${b})`);
  if (lang === "es" && b) ptLeft.push(id);
}
console.log("questions per lang:", JSON.stringify(n));
for (const lang of Object.keys(n)) console.log(`  ${lang}: changes ${(ch[lang] ?? []).length} ${(ch[lang] ?? []).join(" ")}`);
console.log(`ES questions still treated as PT by the arm: ${ptLeft.length} ${ptLeft.join(" ")}`);

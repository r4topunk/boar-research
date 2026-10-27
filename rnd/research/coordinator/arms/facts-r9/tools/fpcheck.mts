/** facts-r9 FP check (criterion a4fd8b92): every public question through factsAnswer on the r8 and r9 trees.
 * Usage: tsx fpcheck.mts <r8 tree> <r9 tree> <out.jsonl>. Sets: boar-eval/bench v0.1 public, rivalset, selftest/*, slices/* (no blind). */
import { readFileSync, writeFileSync, readdirSync, existsSync } from "node:fs";
const [r8t, r9t, out] = process.argv.slice(2);
const B = "<workspace>/boar-eval/bench";
const A = (await import(`${r8t}/src/rag/facts.ts`)).factsAnswer;
const C = (await import(`${r9t}/src/rag/facts.ts`)).factsAnswer;
const jl = (p: string) => readFileSync(p, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const files = [`${B}/v0.1/questions.public.jsonl`, `${B}/rivalset/questions.jsonl`];
for (const d of ["selftest", "slices"]) for (const s of readdirSync(`${B}/${d}`)) if (existsSync(`${B}/${d}/${s}/questions.jsonl`)) files.push(`${B}/${d}/${s}/questions.jsonl`);
files.push(`${B}/slices/chat-fu-v1/chats.jsonl`, `${B}/slices/citation-pt/citation-pt.jsonl`);
const rows: any[] = [];
const seen = new Set<string>();
for (const f of files) for (const r of jl(f)) {
  const qs: string[] = r.question ? [r.question] : (r.turns ?? []).filter((t: any) => t.role !== "assistant").map((t: any) => t.text ?? t.content ?? t.question);
  for (const q of qs) { if (!q || seen.has(q)) continue; seen.add(q); rows.push({ set: f.replace(B + "/", ""), id: r.id, q }); }
}
let fire8 = 0, fire9 = 0, changed = 0, newT = 0;
const res = rows.map((r) => {
  const a = A(r.q), c = C(r.q);
  if (a) fire8++; if (c) fire9++;
  const ch = (a?.text ?? null) !== (c?.text ?? null);
  if (ch) changed++;
  if (c && (c.template === "driving" || c.template === "calling")) newT++;
  return { ...r, r8: a ? `[${a.template}] ${a.text}` : null, r9: c ? `[${c.template}] ${c.text}` : null, changed: ch };
});
writeFileSync(out, res.map((r) => JSON.stringify(r)).join("\n") + "\n");
console.log(`files ${files.length} questions ${rows.length} fire r8 ${fire8} fire r9 ${fire9} changed ${changed} r9-new-templates ${newT}`);
for (const r of res.filter((r) => r.changed)) console.log("CHANGED", r.set, r.id, JSON.stringify(r.q), "\n  r8:", r.r8?.split("\n")[0], "\n  r9:", r.r9?.split("\n")[0]);

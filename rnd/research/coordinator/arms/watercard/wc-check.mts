// usage: tsx wc-check.mts <engine-tree> <boar root>
import fs from "node:fs";
import path from "node:path";
const [tree, B] = process.argv.slice(2);
const R = path.join(tree, "src/routing");
const W = await import(path.join(R, "waterSafety.ts"));
const F = await import(path.join(R, "firstAidCards.ts"));
const CO = await import(path.join(R, "coHazard.ts"));
const { isPortugueseQuestion, isSpanishQuestion } = await import(path.join(R, "context.ts"));
function card(q: string): string {
  if (F.isSnakebiteFirstAid(q)) return "snakebite";
  const en = !isPortugueseQuestion(q) && !isSpanishQuestion(q);
  if (en && CO.isCoHazardQuestion(q)) return "co";
  if (en && W.isWaterSafetyQuestion(q)) return "water";
  return "none";
}
const jl = (p: string) => fs.readFileSync(p, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const A = path.join(B, "rnd/research/coordinator/arms");
const out: string[] = [];
// (a) old trigger sets (all dev/burnt now)
for (const f of ["probes/water-safety.probes.jsonl", "probes/water-safety.heldout.jsonl"]) {
  const it = jl(path.join(A, f));
  const pos = it.filter((d: any) => d.expect === "pos"), neg = it.filter((d: any) => d.expect !== "pos");
  const hit = pos.filter((d: any) => card(d.text) === "water"), ff = neg.filter((d: any) => card(d.text) === "water");
  out.push(`(a) ${f}: water recall ${hit.length}/${pos.length}; water false fires ${ff.length}/${neg.length}; misses: ${pos.filter((d: any) => card(d.text) !== "water").map((d: any) => d.id).join(" ") || "-"}; ff: ${ff.map((d: any) => d.id).join(" ") || "-"}`);
}
for (const f of ["sc-fresh3/items.jsonl", "sc-fresh4/items.jsonl"]) {
  const it = jl(path.join(A, f));
  const pos = it.filter((d: any) => d.expect_card === "water"), others = it.filter((d: any) => d.expect_card !== "water");
  const neg = it.filter((d: any) => d.expect_card === "none");
  const hit = pos.filter((d: any) => card(d.text) === "water");
  const ff = others.filter((d: any) => card(d.text) === "water");
  const anyFF = neg.filter((d: any) => card(d.text) !== "none");
  out.push(`(a) ${f}: water recall ${hit.length}/${pos.length} (${((100 * hit.length) / pos.length).toFixed(0)} %); water card on non-water items ${ff.length}/${others.length} (${ff.map((d: any) => d.id).join(" ") || "-"}); any card on expect=none ${anyFF.length}/${neg.length} (${anyFF.map((d: any) => `${d.id}->${card(d.text)}`).join(" ") || "-"}); water misses: ${pos.filter((d: any) => card(d.text) !== "water").map((d: any) => `${d.id}: ${d.text}`).join(" | ")}`);
}
// (b) public sets: every water fire
function texts(o: any, acc: string[] = [], key = ""): string[] {
  if (typeof o === "string") { if (["question", "text", "query", "q", "prompt", "user"].includes(key)) acc.push(o); return acc; }
  if (Array.isArray(o)) { for (const x of o) texts(x, acc, key); return acc; }
  if (o && typeof o === "object") {
    if ((o.role === "user") && typeof o.content === "string") acc.push(o.content);
    for (const [k, v] of Object.entries(o)) if (!["rubric", "gold", "reference", "answer", "refs", "notes", "note"].includes(k)) texts(v, acc, k);
  }
  return acc;
}
const pub: string[] = [path.join(B, "boar-eval/bench/v0.1/questions.public.jsonl")];
for (const d of fs.readdirSync(path.join(B, "boar-eval/bench/slices"))) for (const f of fs.readdirSync(path.join(B, "boar-eval/bench/slices", d))) if (f.endsWith(".jsonl")) pub.push(path.join(B, "boar-eval/bench/slices", d, f));
for (const d of fs.readdirSync(path.join(B, "boar-eval/bench/selftest"))) { const p = path.join(B, "boar-eval/bench/selftest", d, "questions.jsonl"); if (fs.existsSync(p)) pub.push(p); }
let total = 0, fires = 0;
for (const p of pub) {
  const msgs = [...new Set(jl(p).flatMap((d: any) => texts(d).map((t) => `${d.id ?? d.session_id ?? d.chat_id ?? "?"}\t${t}`)))];
  let n = 0;
  for (const m of msgs) { const t = m.split("\t")[1]; total++; if (card(t) === "water") { fires++; n++; out.push(`(b) FIRE ${path.relative(B, p)} ${m}`); } }
  out.push(`(b) ${path.relative(B, p)}: ${n}/${msgs.length} messages fire`);
}
out.push(`(b) total public messages ${total}, water fires ${fires}`);
// (c) safepack
for (const d of jl(path.join(B, "boar-eval/bench/selftest/safepack/questions.jsonl"))) out.push(`(c) ${d.id} [${d.category}] ${card(d.question)}: ${d.question}`);
console.log(out.join("\n"));

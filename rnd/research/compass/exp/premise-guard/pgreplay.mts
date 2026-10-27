import fs from "node:fs";
import path from "node:path";
const G = await import(process.argv[2] + "/src/routing/premiseGuard.ts");
const jl = (p: string) => fs.readFileSync(p, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
// Only non-blind items: v0.1 public, the V-exact slice, the compass chat slices.
const allowed = new Set<string>();
for (const f of ["<workspace>/boar-eval/bench/v0.1/questions.public.jsonl", "<workspace>/rnd/research/compass/exp/bounty-eval/bench-vslice/questions.jsonl"]) for (const r of jl(f)) allowed.add(r.id);
const R = "<workspace>/boar-eval/runs";
const dirs = ["night-2026-10-01", "kiln/vexact", "kiln/vexact-cut2", "kiln/rv2-l1", "kiln/chat-slice-base-s42", "kiln/bigpack-l1"];
const files: string[] = [];
const walk = (d: string) => { if (!fs.existsSync(d)) return; for (const e of fs.readdirSync(d, { withFileTypes: true })) { const p = path.join(d, e.name); if (e.isDirectory()) walk(p); else if (p.endsWith(".traces.jsonl")) files.push(p); } };
for (const d of dirs) walk(path.join(R, d));
let n = 0, uncited = 0, fires = 0;
const out: string[] = [];
for (const f of files) {
  for (const t of jl(f)) {
    if (!allowed.has(t.itemId) && !/^c[sv]|^v[12]-/.test(t.itemId)) continue;
    if (!/4b/i.test(t.runtime?.model ?? "")) continue;
    const a0 = typeof t.answer === "string" ? t.answer : t.answer?.text ?? ""; const a = a0.replace(/^This answer is not from an offline source on this phone; check it before relying on it\.\s*/, "");
    const codes: string[] = t.route?.reasonCodes ?? [];
    const task = (codes.find((c) => c.startsWith("task:")) ?? "").slice(5);
    n++;
    if (!a || /\[\d+\]/.test(a) || !["lookup", "research", "compare", "extract"].includes(task) || codes.some((c) => c.includes("health"))) continue;
    uncited++;
    const r = G.premiseGuard(t.question, a); if (r) { fires++; out.push(`${r.action.toUpperCase()} ${path.relative(R, f)} ${t.itemId} | Q: ${t.question} | A: ${a.replace(/\s+/g, " ").slice(0, 200)}`); }
  }
}
out.push(`4B traces on allowed items ${n}; uncited knowledge answers ${uncited}; guard fires ${fires}`);
fs.writeFileSync(process.argv[3], out.join("\n") + "\n"); console.log(out.slice(-40).join("\n"));

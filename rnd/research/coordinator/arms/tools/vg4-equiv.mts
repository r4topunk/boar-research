// VG v4 vs v3 offline equivalence on every stored answer used for the VG L0 + any cut3-vgar L1 traces present.
// usage: tsx vg-equiv.mts <v1-tree> <v2-tree>   (writes arms/vg4-newfires.jsonl and arms/vg4-equiv-vs-v3.txt)
import fs from "node:fs";
import path from "node:path";
const [t1, t2] = process.argv.slice(2);
const V1 = (await import(path.join(t1, "src/routing/verdictGuard.ts"))).verdictGuard;
const V2 = (await import(path.join(t2, "src/routing/verdictGuard.ts"))).verdictGuard;
const B = "<workspace>", A = path.join(B, "rnd/research/coordinator/arms");
const jl = (p: string) => fs.readFileSync(p, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const EN = new Set(jl(`${B}/boar-eval/bench/v0.1/questions.public.jsonl`).filter((q: any) => q.lang === "en").map((q: any) => q.id));
const PREFACE = "This answer is not from an offline source on this phone; check it before relying on it.";
const NOT_MODEL = /answer:|grounding:health|instant:final|places|calculator|grounding:current-event|small-talk|safety-fact/;
const runs: [string, string][] = [
  ["cut2-s44", "boar-eval/runs/kiln/overnight/traces/ov-cut2-v01-s44.traces.jsonl"], ["cut2-s45", "boar-eval/runs/kiln/overnight/traces/ov-cut2-v01-s45.traces.jsonl"],
  ["cut2-s46", "boar-eval/runs/kiln/overnight/traces/ov-cut2-v01-s46.traces.jsonl"], ["cut2-s47", "boar-eval/runs/kiln/overnight/traces/ov-cut2-v01-s47.traces.jsonl"],
  ["A-s42", "boar-eval/runs/kiln/bigpack-l1/bigpack-A-s42.v01.traces.jsonl"], ["A-s43", "boar-eval/runs/kiln/rv2-l1/rv2l1-A-s43.v01.traces.jsonl"],
  ["E0-s42", "boar-eval/runs/night-2026-10-01/and-qwen-s42.traces.jsonl"], ["E0-s43", "boar-eval/runs/night-2026-10-01/and-qwen-s43.traces.jsonl"],
  ["E0-s44", "boar-eval/runs/and-qwen-s44/and-qwen-s44.traces.jsonl"], ["RV2-s42", "boar-eval/runs/kiln/rv2-l1/rv2l1-R-s42.v01.traces.jsonl"],
  ["RV2-s43", "boar-eval/runs/kiln/rv2-l1/rv2l1-R-s43.v01.traces.jsonl"], ["CB", "rnd/research/anvil/exp/outofkit/runs/srv-qwen3-4b.traces.jsonl"],
];
const L1 = `${B}/boar-eval/runs/kiln/cut3-vgar-l1`;
for (const f of fs.existsSync(L1) ? fs.readdirSync(L1).filter((f) => f.endsWith(".traces.jsonl")) : []) runs.push([`L1:${f.replace(".traces.jsonl", "")}`, path.relative(B, path.join(L1, f))]);
const chat: string[] = [];
const walk = (d: string) => { for (const e of fs.readdirSync(d, { withFileTypes: true })) { const p = path.join(d, e.name); if (e.isDirectory()) { if (!/blind/i.test(e.name)) walk(p); } else if (e.name.endsWith("traces.jsonl")) chat.push(p); } };
for (const d of ["v1-fresh/runs", "v2-fresh/runs"]) walk(path.join(B, "rnd/research/compass/chat-slice", d));
for (const f of chat) runs.push([`chat:${path.basename(path.dirname(f))}`, path.relative(B, f)]);

// For an L1 VG-arm trace the stored answer is already VG-processed; compare v1/v2 on the same text anyway (v1 must be a no-op
// on its own output only if idempotent, so we report flags as seen).
let n = 0, same = 0; const diffs: string[] = [], repairs: any[] = [];
for (const [name, rel] of runs) {
  const p = path.join(B, rel);
  if (!fs.existsSync(p)) continue;
  for (const r of jl(p)) {
    if (!name.startsWith("chat:") && !EN.has(r.itemId)) continue;
    const text = r.answer?.text ?? "";
    if (!text || (r.route?.reasonCodes?.length && NOT_MODEL.test(r.route.reasonCodes.join(" ")))) continue;
    let body = text, pre = "";
    if (body.startsWith(PREFACE)) { pre = PREFACE + "\n\n"; body = body.slice(PREFACE.length).replace(/^\s+/, ""); }
    const a = V1(r.question, body), b = V2(r.question, body);
    n++;
    const ka = a ? `${a.kind}|${a.text}` : "null", kb = b ? `${b.kind}|${b.text}` : "null";
    if (ka === kb) same++;
    else diffs.push(`${name} ${r.itemId}: v3 ${a ? a.kind : "no flag"} -> v4 ${b ? b.kind : "no flag"}${a && b ? " (text differs)" : ""}`);
    if (b && ka !== kb) repairs.push({ run: name, itemId: r.itemId, kind: b.kind, question: r.question, before: text, after: pre + b.text, sameAsV3: ka === kb });
  }
}
fs.writeFileSync(path.join(A, "vg4-newfires.jsonl"), repairs.map((r) => JSON.stringify(r)).join("\n") + "\n");
const rep = [`VG v4 vs v3 on ${n} stored EN model answers (${runs.length} files incl. chat dev and any cut3-vgar L1 traces present): identical ${same}, differ ${diffs.length}`, ...diffs.map((d) => "  " + d), `v2 repairs: ${repairs.length} -> vg4-newfires.jsonl`, `L1 files included: ${runs.filter(([nm]) => nm.startsWith("L1:")).map(([nm]) => nm).join(", ") || "none"}`];
fs.writeFileSync(path.join(A, "vg4-equiv-vs-v3.txt"), rep.join("\n") + "\n");
console.log(rep.join("\n"));

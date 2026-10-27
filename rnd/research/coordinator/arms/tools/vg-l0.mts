// VG L0 (criterion arms/vg-L0-criterion.md): run verdictGuard offline on stored 4B v0.1 EN answers + EN chat dev traces.
// usage: tsx vg-l0.mts <engine-tree>   (writes arms/vg-repairs.jsonl, prints the tables)
import fs from "node:fs";
import path from "node:path";
const tree = process.argv[2];
const { verdictGuard } = await import(path.join(tree, "src/routing/verdictGuard.ts"));
const B = "<workspace>";
const OUT = path.join(B, "rnd/research/coordinator/arms");
const jl = (p: string) => fs.readFileSync(p, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const EN = new Set(jl(`${B}/boar-eval/bench/v0.1/questions.public.jsonl`).filter((q: any) => q.lang === "en").map((q: any) => q.id));
const PREFACE = "This answer is not from an offline source on this phone; check it before relying on it.";
const NOT_MODEL = /answer:|grounding:health|instant:final|places|calculator|grounding:current-event|small-talk|safety-fact/;
const runs: [string, string][] = [
  ["cut2-s44", "boar-eval/runs/kiln/overnight/traces/ov-cut2-v01-s44.traces.jsonl"],
  ["cut2-s45", "boar-eval/runs/kiln/overnight/traces/ov-cut2-v01-s45.traces.jsonl"],
  ["cut2-s46", "boar-eval/runs/kiln/overnight/traces/ov-cut2-v01-s46.traces.jsonl"],
  ["cut2-s47", "boar-eval/runs/kiln/overnight/traces/ov-cut2-v01-s47.traces.jsonl"],
  ["A-s42", "boar-eval/runs/kiln/bigpack-l1/bigpack-A-s42.v01.traces.jsonl"],
  ["A-s43", "boar-eval/runs/kiln/rv2-l1/rv2l1-A-s43.v01.traces.jsonl"],
  ["E0-s42", "boar-eval/runs/night-2026-10-01/and-qwen-s42.traces.jsonl"],
  ["E0-s43", "boar-eval/runs/night-2026-10-01/and-qwen-s43.traces.jsonl"],
  ["E0-s44", "boar-eval/runs/and-qwen-s44/and-qwen-s44.traces.jsonl"],
  ["RV2-s42", "boar-eval/runs/kiln/rv2-l1/rv2l1-R-s42.v01.traces.jsonl"],
  ["RV2-s43", "boar-eval/runs/kiln/rv2-l1/rv2l1-R-s43.v01.traces.jsonl"],
  ["CB", "rnd/research/anvil/exp/outofkit/runs/srv-qwen3-4b.traces.jsonl"],
];
const TARGETS = ["lan-ref-003", "vit-sci-002", "lan-cmp-003"];
const GUARDS = ["lan-cmp-001", "lan-cmp-002", "lan-cmp-004", "lan-cmp-005", "lan-rsn-002", "lan-rsn-004", "lan-rsn-006", "lan-ref-002", "lan-ref-004"];

function apply(q: string, text: string) {
  let body = text, pre = "";
  if (body.startsWith(PREFACE)) { pre = PREFACE + "\n\n"; body = body.slice(PREFACE.length).replace(/^\s+/, ""); }
  const r = verdictGuard(q, body);
  return r ? { kind: r.kind, after: pre + r.text } : null;
}

const repairs: any[] = [];
const table: string[] = ["| run | targets flagged | guard flags | other flags |", "|---|---|---|---|"];
const targetHits: Record<string, number> = Object.fromEntries(TARGETS.map((t) => [t, 0]));
let v2 = true, v3 = true;
for (const [name, rel] of runs) {
  const rows = jl(path.join(B, rel)).filter((r: any) => EN.has(r.itemId));
  const flagged: string[] = [];
  for (const r of rows) {
    const text = r.answer?.text ?? "";
    const codes = (r.route?.reasonCodes ?? []).join(" ");
    if (!text || (r.route?.reasonCodes?.length && NOT_MODEL.test(codes))) continue;
    const res = apply(r.question, text);
    if (!res) continue;
    flagged.push(r.itemId);
    repairs.push({ run: name, itemId: r.itemId, kind: res.kind, question: r.question, before: text, after: res.after });
  }
  const t = flagged.filter((i) => TARGETS.includes(i));
  const g = flagged.filter((i) => GUARDS.includes(i));
  const o = flagged.filter((i) => !TARGETS.includes(i) && !GUARDS.includes(i));
  if (name.startsWith("cut2")) for (const i of t) targetHits[i]++;
  if (g.length) v2 = false;
  if (o.length > 1) v3 = false;
  table.push(`| ${name} (${rows.length}) | ${t.join(", ") || "—"} | ${g.join(", ") || "0"} | ${o.join(", ") || "0"} |`);
}
const v1 = TARGETS.every((t) => targetHits[t] >= 3);

// V4: stored EN chat dev answers (never *-blind) and the question gate on Sonar's EN dev pools.
const chatFiles: string[] = [];
const walk = (d: string) => { for (const e of fs.readdirSync(d, { withFileTypes: true })) { const p = path.join(d, e.name); if (e.isDirectory()) { if (!/blind/i.test(e.name)) walk(p); } else if (e.name.endsWith("traces.jsonl")) chatFiles.push(p); } };
for (const d of ["v1-fresh/runs", "v2-fresh/runs"]) walk(path.join(B, "rnd/research/compass/chat-slice", d));
const chatSlice = new Map<string, string>();
for (const f of ["slice.v0.jsonl", "v1-fresh/slice.v1.jsonl", "v2-fresh/slice.v2.jsonl"]) for (const d of jl(path.join(B, "rnd/research/compass/chat-slice", f))) chatSlice.set(d.id, d.lang);
let chatN = 0; const chatFires: string[] = [];
for (const f of chatFiles) for (const r of jl(f)) {
  if ((chatSlice.get(r.itemId) ?? r.lang ?? "en") !== "en" || !r.answer?.text) continue;
  chatN++;
  const res = apply(r.question, r.answer.text);
  if (res) chatFires.push(`${path.basename(path.dirname(f))}:${r.itemId}`);
}
const v4 = chatFires.length === 0;
// Question gate only (an answer that would let the check run at all: a Yes/No verdict + facts, or a which-form verdict).
const E = `${B}/rnd/research/sonar/exp/30-learned-detector/data/`;
const pools: [string, string[]][] = [
  ["aligned-en", jl(E + "aligned-en.jsonl").map((d: any) => d.turns[d.turns.length - 1])],
  ["terse-live-en", jl(E + "terse-live.jsonl").filter((d: any) => d.lang === "en").map((d: any) => d.turns[d.turns.length - 1])],
  ["compass-dev-en", jl(`${B}/rnd/research/compass/exp/emergency-dev/dev.jsonl`).filter((d: any) => (d.lang ?? "en") === "en").map((d: any) => d.turns.filter((t: any) => t.role === "user").at(-1).text)],
];
// Probe answers that would trip each check if the question gate passes: what a gate hit costs is one check per answer.
const PROBES = ["No, it did not happen before 1970. The first time was in 1969.", "Germany is bigger than Japan. Germany has 10 people, while Japan has 20 people.", "No country is bigger than India. India is the seventh-largest country."];
const gate: string[] = [];
let poolN = 0;
for (const [name, qs] of pools) {
  let hits = 0;
  for (const q of qs) { poolN++; if (PROBES.some((p) => verdictGuard(q, p))) { hits++; gate.push(`${name}: ${q.slice(0, 100)}`); } }
  table.push(`| pool ${name} (${qs.length}) | question-gate hits ${hits} | | |`);
}
fs.writeFileSync(path.join(OUT, "vg-repairs.jsonl"), repairs.map((r) => JSON.stringify(r)).join("\n") + "\n");
console.log(table.join("\n"));
console.log(`\ncut2 target seeds flagged: ${TARGETS.map((t) => `${t} ${targetHits[t]}/4`).join(", ")}`);
console.log(`chat dev EN stored answers: ${chatN} in ${chatFiles.length} files, fires ${chatFires.length} ${chatFires.join(" ")}`);
console.log(`dev pools question gate: ${gate.length}/${poolN}${gate.length ? "\n  " + gate.join("\n  ") : ""}`);
console.log(`\nV1 ${v1 ? "PASS" : "FAIL"} · V2 ${v2 ? "PASS" : "FAIL"} · V3 ${v3 ? "PASS" : "FAIL"} · V4 ${v4 ? "PASS" : "FAIL"} · repairs ${repairs.length}`);

// SC v2 trigger dev checks (coordinator follow-up 2026-10-04). usage: tsx sc-l0-v2.mts <tree-v2> <tree-v1(sc commit)> <baseline-cut2>
import fs from "node:fs";
import path from "node:path";
const [t2, t1, t0] = process.argv.slice(2);
const imp = async (t: string, f: string) => import(path.join(t, "src/routing", f));
const W2 = await imp(t2, "waterSafety.ts"), W1 = await imp(t1, "waterSafety.ts");
const F2 = await imp(t2, "firstAidCards.ts"), F0 = await imp(t0, "firstAidCards.ts");
const C2 = await imp(t2, "conditionCards.ts"), C0 = await imp(t0, "conditionCards.ts");
const B = "<workspace>", A = path.join(B, "rnd/research/coordinator/arms");
const jl = (p: string) => fs.readFileSync(p, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const turns = (d: any): string[] => (d.turns ?? []).map((t: any) => (typeof t === "string" ? t : t.role === "user" ? t.text : null)).filter(Boolean);
const last = (d: any) => turns(d).at(-1) ?? d.text ?? d.question ?? "";
const E = `${B}/rnd/research/sonar/exp/30-learned-detector/data/`;
const chat: string[] = [];
for (const f of ["slice.v0.jsonl", "v1-fresh/slice.v1.jsonl", "v2-fresh/slice.v2.jsonl"]) for (const d of jl(`${B}/rnd/research/compass/chat-slice/${f}`)) if (d.lang === "en") chat.push(last(d));
const co = (f: string) => jl(`${B}/rnd/research/compass/exp/co-hazard/${f}`).map(last);
const v01 = jl(`${B}/boar-eval/bench/v0.1/questions.public.jsonl`).filter((q: any) => q.lang === "en");
const pools: [string, string[]][] = [
  ["aligned-en", jl(E + "aligned-en.jsonl").map(last)],
  ["terse-live-en", jl(E + "terse-live.jsonl").filter((d: any) => d.lang === "en").map(last)],
  ["compass-dev-en", jl(`${B}/rnd/research/compass/exp/emergency-dev/dev.jsonl`).filter((d: any) => (d.lang ?? "en") === "en").map(last)],
  ["co-lookalike-dev", co("lookalike.dev.jsonl")], ["co-lookalike-heldout", co("lookalike.heldout.jsonl")], ["co-lookalike-heldout3", co("lookalike.heldout3.jsonl")],
  ["chat-slice-en", chat], ["v0.1-en minus dng-005", v01.filter((q: any) => q.id !== "dng-005").map((q: any) => q.question)],
];
const out: string[] = [];
// Water: dev pools must stay 0 (1,703).
let wf: string[] = [], n = 0;
for (const [name, qs] of pools) { n += qs.length; wf.push(...qs.filter((q) => q && W2.isWaterSafetyQuestion(q)).map((q) => `${name}: ${q.slice(0, 140)}`)); }
out.push(`W-FF water v2 false fires on dev pools: ${wf.length}/${n}${wf.length ? "\n    " + wf.join("\n    ") : ""}`);
const score = (f: string, label: string) => {
  const P = jl(`${A}/probes/${f}`); const pos = P.filter((p: any) => p.expect === "pos"), neg = P.filter((p: any) => p.expect === "neg");
  const r = (W: any) => `${pos.filter((p: any) => W.isWaterSafetyQuestion(p.text)).length}/${pos.length} recall, ${neg.filter((p: any) => W.isWaterSafetyQuestion(p.text)).length}/${neg.length} FF`;
  out.push(`${label}: v1 ${r(W1)} -> v2 ${r(W2)}`);
};
score("water-safety.probes.jsonl", "W-dev paraphrases (DEV, used for tuning)");
score("water-safety.heldout.jsonl", "W-S5 set (BURNED: used for v2 tuning)");
out.push(`dng-005 v2 fires: ${W2.isWaterSafetyQuestion(v01.find((q: any) => q.id === "dng-005").question)}`);

// Snakebite: every message in pools + emergency-dev (all languages) + Sonar cards/synth EN: before (cut 2) vs v2.
const ed = jl(`${B}/rnd/research/compass/exp/emergency-dev/dev.jsonl`);
const extra: [string, any[]][] = [["emergency-dev-all", ed], ["cards-en", jl(E + "cards-en.jsonl")], ["synth-en", jl(E + "synth-en.jsonl")], ["cards-pt", jl(E + "cards-pt.jsonl")], ["cards-es", jl(E + "cards-es.jsonl")], ["aligned-pt", jl(E + "aligned-pt.jsonl")], ["aligned-es", jl(E + "aligned-es.jsonl")]];
const msgs: [string, string, string[], any][] = [];
for (const [name, qs] of pools) for (const q of qs) msgs.push([name, q, [], null]);
for (const [name, ds] of extra) for (const d of ds) msgs.push([name, last(d), turns(d).slice(0, -1), d]);
let lostFA = 0, lostCond = 0; const newFA: string[] = [], condChanged: string[] = [];
for (const [name, q, prev, d] of msgs) {
  if (!q) continue;
  const a = F0.isSnakebiteFirstAid(q), b = F2.isSnakebiteFirstAid(q);
  if (a && !b) lostFA++;
  if (!a && b) newFA.push(`${name}${d?.card ? `[label ${d.card}]` : d?.cat ? `[${d.cat}]` : ""}: ${q.slice(0, 130)}`);
  const ca = C0.conversationCondition(q, prev).condition, cb = C2.conversationCondition(q, prev).condition;
  if (ca === "snakebite" && cb !== "snakebite") lostCond++;
  if (ca !== cb) condChanged.push(`${name}${d?.card ? `[label ${d.card}]` : d?.cat ? `[${d.cat}]` : ""}: ${ca} -> ${cb} | ${q.slice(0, 120)}`);
}
out.push(`SB existing positives lost: fast path ${lostFA}, condition ${lostCond} (of ${msgs.length} messages)`);
out.push(`SB new fast-path fires ${newFA.length}:\n    ${newFA.join("\n    ")}`);
out.push(`SB condition changes ${condChanged.length}:\n    ${condChanged.join("\n    ")}`);
console.log(out.join("\n"));

// WARN-DET analysis (0 LLM): per v0.2 item, the warn tree's own healthReasons / isModelGenerated over the stub route replay
// (live detector), H at p thresholds 0.05 and 0.02, the layer table. SCRIPT-ONLY on blind: writes ids, labels, p and flags; no text.
// Usage: tsx warndet.mts <tree> <traces.jsonl> <out rows.jsonl> <out agg.json>
import { readFileSync, writeFileSync } from "node:fs";
const [tree, tracesP, rowsOut, aggOut] = process.argv.slice(2);
const WN: any = await import(`${tree}/src/routing/warn.ts`);
const CX: any = await import(`${tree}/src/routing/context.ts`);
const jl = (p: string) => readFileSync(p, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const Q = new Map(jl("<private held-out dir>").map((q: any) => [q.id, q]));
const rows: any[] = [];
for (const t of jl(tracesP)) {
  const q: any = Q.get(t.itemId); const done = t.events.filter((e: any) => e.type === "done").at(-1);
  const codes: string[] = done?.receipt?.reasonCodes ?? t.route.reasonCodes;
  const pc = codes.find((c) => c.startsWith("detector:p=")); const p = pc ? Number(pc.slice(11)) : null;
  const kept = t.retrieval.kept.map((k: any) => ({ source: k.source, chunkId: k.chunkId }));
  const reasons: string[] = WN.healthReasons({ query: t.question, codes, kept });
  const other = reasons.filter((r) => !r.startsWith("detector:p>="));
  const M = WN.isModelGenerated({ modelId: done?.receipt?.modelId, codes, outcome: t.route.outcome, text: t.answer.text ?? "" });
  const label = q.category === "health" ? "P" : q.danger === true || q.danger === "True" ? "D" : "N";
  const layer = M ? "model" : (codes.find((c) => /^(answer:|grounding:health-|grounding:fa-card|healthgap:|instant:final)/.test(c) || c.includes("declined")) ?? `modelId:${done?.receipt?.modelId}`);
  rows.push({ id: t.itemId, label, health18: label !== "N", category: q.category, p, fire: codes.includes("detector:fire"),
    p05: (p ?? 0) >= 0.05, p02: (p ?? 0) >= 0.02, healthgap: codes.filter((c) => c.startsWith("healthgap:")), groundingHealth: codes.filter((c) => c.startsWith("grounding:health-")),
    isSafety: CX.isSafetyQuery(t.question), warnLex: reasons.includes("lexicon:warn"), healthPack: reasons.includes("source:health-pack"),
    H05: reasons.length > 0, H02: other.length > 0 || (p ?? 0) >= 0.02, Hnodet: other.filter((r) => r !== "detector:fire").length > 0,
    M, layer, warnEvent: t.events.find((e: any) => e.kind === "warn")?.tier ?? null, doneWarn: done?.warn ?? null, reasons });
}
writeFileSync(rowsOut, rows.map((r) => JSON.stringify(r)).join("\n") + "\n");
const H = rows.filter((r) => r.health18), N = rows.filter((r) => !r.health18);
const cnt = (rs: any[], k: string) => rs.filter((r) => r[k]).length;
const sig: Record<string, any> = {};
for (const k of ["fire", "p05", "p02", "Hnodet", "H05", "H02", "warnLex", "isSafety"]) sig[k] = { recall: `${cnt(H, k)}/18`, fp: `${cnt(N, k)}/92`, P8: cnt(rows.filter((r) => r.label === "P"), k), D10: cnt(rows.filter((r) => r.label === "D"), k), miss: H.filter((r) => !r[k]).map((r) => r.id), fpIds: N.filter((r) => r[k]).map((r) => r.id) };
const qs = (a: number[]) => { const s = [...a].sort((x, y) => x - y); const at = (f: number) => s[Math.min(s.length - 1, Math.floor(f * (s.length - 1)))]; return { min: s[0], q25: at(0.25), med: at(0.5), q75: at(0.75), q90: at(0.9), max: s.at(-1) }; };
const layers: Record<string, any> = {};
for (const r of H) { const k = r.layer; layers[k] = layers[k] ?? { n: 0, H05: 0, H02: 0, ids: [] }; layers[k].n++; layers[k].H05 += r.H05; layers[k].H02 += r.H02; layers[k].ids.push(r.id); }
const agg = { n: rows.length, pMissing: rows.filter((r) => r.p === null).length, sig, pQuant: { health18: qs(H.map((r) => r.p ?? 0)), nonhealth92: qs(N.map((r) => r.p ?? 0)) },
  health18P: H.map((r) => `${r.id}:${r.p}`), nonhealthTop: N.map((r) => r.p ?? 0).sort((a, b) => b - a).slice(0, 8),
  layers, warn18: { M: cnt(H, "M"), warn05: H.filter((r) => r.M && r.H05).length, warn02: H.filter((r) => r.M && r.H02).length, warnEvent: H.filter((r) => r.warnEvent).length },
  warn92: { M: cnt(N, "M"), warn05: N.filter((r) => r.M && r.H05).length, warn02: N.filter((r) => r.M && r.H02).length, warnEvent: N.filter((r) => r.warnEvent).length },
  eventVsRule: rows.filter((r) => !!r.warnEvent !== (r.M && r.H05)).map((r) => r.id), healthPackFires: cnt(rows, "healthPack") };
writeFileSync(aggOut, JSON.stringify(agg, null, 1)); console.log(JSON.stringify(agg, null, 1));

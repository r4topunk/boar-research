// WARNSPEC-PATCH: final tiers with generation skipped (0 LLM). Route, codes and kept sources from the ON stub replay (this tree's
// engine, live detector); answer text and cited from the existing generation traces (aggregates/feats.jsonl, 4B probes / v0.1);
// the tier from the tree's own src/routing/warn.ts. Usage: tsx replay_tier.mts <tree> <arm dir>  -> JSON on stdout
import { readFileSync } from "node:fs";
const [tree, arm] = process.argv.slice(2);
const { warnOf, streamStartTier, settleTier } = await import(`${tree}/src/routing/warn.ts`);
const jl = (p: string) => readFileSync(p, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l));
const feats = jl(`${arm}/aggregates/feats.jsonl`);
const W = JSON.parse(readFileSync(`${arm}/aggregates/warnspec.json`, "utf8")).rows;
const out: any = {};
for (const [s, set] of [["probes", "probes64"], ["v01", "v01"]] as const) {
  const on = jl(`${arm}/runs/warn-${s}-on.traces.jsonl`);
  const rows: any[] = [];
  for (const t of on) {
    const f = feats.find((x: any) => x.model === "4B" && x.set === set && x.id === t.itemId);
    const exp = W.find((x: any) => x.model === "4B" && x.set === set && x.id === t.itemId).tier;
    const done = t.events.filter((e: any) => e.type === "done").at(-1);
    const generated = t.events.some((e: any) => e.type === "other" && e.kind === "generation");
    const start = t.events.find((e: any) => e.kind === "warn")?.tier ?? null;
    // A generated turn takes the trace's answer; a deterministic one (no generation in the replay) keeps the replay's own text.
    const final = warnOf({
      query: t.question, codes: t.route.reasonCodes, modelId: done.receipt.modelId, outcome: t.route.outcome,
      text: generated ? f.text : t.answer.text, kept: t.retrieval.kept.map((k: any) => ({ source: k.source })), cited: generated ? f.cited : done.cited ?? [],
    });
    const tier = settleTier(start, final);
    rows.push({ id: t.itemId, generated, start, final, tier, expect: exp, ok: tier === exp, startOk: start === (exp ? streamStartTier(exp === "no-source" ? 0 : 1) : null) });
  }
  out[s] = { n: rows.length, warn: rows.filter((r) => r.tier).map((r) => `${r.id}:${r.tier}`), bad: rows.filter((r) => !r.ok || !r.startOk) };
}
console.log(JSON.stringify(out, null, 1));

// NUMGUARD-r3 route replay (from route_replay_r2.mts): on_acts = fire && guard && a calculator answers (the only way r3 changes an
// answer); code_only = fire && guard && no calculator (numguard:no-calculator is added, the refusal text is unchanged).
// NUMGUARD step 3: 0-LLM route replay. Per question: the learned detector (same client as be/adapter.ts: mmbert head over
// llama-server :8094 /embedding, detectorText with no history), numericGuard, and whether NUMGUARD=1 changes the turn
// (acts = fire && guard; answer.ts changes nothing else). OFF never acts (the patch's only branch is env-gated).
// Usage (cwd = numguard tree): be/node_modules/tsx/dist/cli.mjs route_replay.mts <tree> <out.jsonl> <name=questions.jsonl>...
import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
const [tree, out, ...sets] = process.argv.slice(2);
const EH: any = await import(join(tree, "src/routing/emergencyHead.ts"));
const NG: any = await import(join(tree, "src/routing/numguard.ts"));
const CX: any = await import(join(tree, "src/routing/context.ts"));
const CA: any = await import(join(tree, "src/routing/calculators.ts"));
const TR: any = await import(join(tree, "src/routing/travelDistance.ts"));
const head = JSON.parse(readFileSync(process.env.BOAR_DETECTOR_HEAD!, "utf8"));
const url = process.env.BOAR_DETECTOR_URL ?? "http://127.0.0.1:8094";
const thr = EH.DETECTOR_THRESHOLD;
const post = async (path: string, body: any) => {
  const r = await fetch(`${url}${path}`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) });
  if (!r.ok) throw new Error(`detector ${path} ${r.status}`);
  return r.json() as any;
};
const embed = async (content: string): Promise<number[]> => { const j = await post("/embedding", { content, embd_normalize: -1 }); const e = Array.isArray(j) ? j[0].embedding : j.embedding; return Array.isArray(e[0]) ? e[0] : e; };
const countTokens = async (content: string) => (await post("/tokenize", { content, add_special: false })).tokens.length;
if (head.kind !== "mmbert-cls") throw new Error("expected the mmbert head");
const rows: any[] = [];
for (const s of sets) {
  const [set, path] = s.split("=");
  for (const q of readFileSync(path, "utf8").split("\n").filter(Boolean).map((l) => JSON.parse(l))) {
    const text = await EH.detectorText([], q.question, countTokens);
    const p = EH.mmbertProbability(head, await embed(text));
    const pt = CX.isPortugueseQuestion(q.question), fire = p >= thr, guard = NG.numericGuard(q.question, pt);
    const calculator = CA.calculate(q.question, pt)?.kind ?? (pt || CX.isSpanishQuestion(q.question) ? null : TR.travelDistanceAnswer(q.question) ? "travel" : null);
    rows.push({ set, id: q.id, p: Number(p.toFixed(3)), fire, guard, health_lexicon: NG.numguardHealthLexicon(q.question), calculator, off_acts: false, on_acts: fire && guard && calculator !== null, code_only: fire && guard && calculator === null });
  }
}
writeFileSync(out, rows.map((r) => JSON.stringify(r)).join("\n") + "\n");
const by = new Map<string, any[]>(); for (const r of rows) by.set(r.set, [...(by.get(r.set) ?? []), r]);
for (const [set, rs] of by) console.log(`${set}: n=${rs.length} fire=${rs.filter((r) => r.fire).length} guard=${rs.filter((r) => r.guard).length} on_acts=${rs.filter((r) => r.on_acts).length} [${rs.filter((r) => r.on_acts).map((r) => `${r.id}(p=${r.p},${r.calculator})`).join(" ")}] code_only=${rs.filter((r) => r.code_only).length} [${rs.filter((r) => r.code_only).map((r) => r.id).join(" ")}]`);
console.log(`threshold ${thr}; total n=${rows.length} on_acts=${rows.filter((r) => r.on_acts).length} code_only=${rows.filter((r) => r.code_only).length}`);
